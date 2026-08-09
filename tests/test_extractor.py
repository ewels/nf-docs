"""Tests for the pipeline extractor."""

import json
from pathlib import Path
from unittest.mock import patch

from nf_docs.cache import PipelineCache
from nf_docs.config import NfDocsConfig
from nf_docs.extractor import PipelineExtractor, find_pipeline_root
from nf_docs.models import ConfigParam, Pipeline, PipelineMetadata


class TestPipelineExtractor:
    def test_extract_schema_inputs(self, sample_pipeline: Path):
        """Test that schema inputs are extracted."""
        with patch.object(PipelineExtractor, "_extract_from_lsp"):
            extractor = PipelineExtractor(workspace_path=sample_pipeline)
            pipeline = extractor.extract()

            # Check inputs from schema
            input_names = {inp.name for inp in pipeline.inputs}
            assert "input" in input_names
            assert "outdir" in input_names
            assert "genome" in input_names

    def test_extract_metadata_from_schema(self, sample_pipeline: Path):
        """Test that metadata is extracted from schema."""
        with patch.object(PipelineExtractor, "_extract_from_lsp"):
            extractor = PipelineExtractor(workspace_path=sample_pipeline)
            pipeline = extractor.extract()

            # Schema title takes priority
            assert pipeline.metadata.name == "Test Pipeline"

    def test_extract_readme_description(self, sample_pipeline: Path):
        """Test that README description is extracted when schema has none."""
        with patch.object(PipelineExtractor, "_extract_from_lsp"):
            extractor = PipelineExtractor(workspace_path=sample_pipeline)
            pipeline = extractor.extract()

            # Schema description takes priority
            assert pipeline.metadata.description is not None


class TestFindPipelineRoot:
    def test_finds_nextflow_config(self, tmp_path: Path):
        """Walks up to the directory containing nextflow.config."""
        (tmp_path / "nextflow.config").write_text("")
        nested = tmp_path / "modules" / "tool" / "main.nf"
        nested.parent.mkdir(parents=True)
        nested.write_text("")

        assert find_pipeline_root(nested) == tmp_path.resolve()

    def test_finds_git_dir(self, tmp_path: Path):
        """Walks up to the directory containing .git."""
        (tmp_path / ".git").mkdir()
        nested = tmp_path / "subdir" / "main.nf"
        nested.parent.mkdir()
        nested.write_text("")

        assert find_pipeline_root(nested) == tmp_path.resolve()

    def test_falls_back_to_parent(self, tmp_path: Path):
        """Falls back to the file's parent when no marker is found."""
        nf_file = tmp_path / "lonely.nf"
        nf_file.write_text("")

        # tmp_path has no nextflow.config or .git, so we fall back to parent.
        result = find_pipeline_root(nf_file)
        # Either tmp_path itself or one of its ancestors that happens to
        # contain a .git (test runner working dir). We just assert the file
        # is inside the returned root.
        assert nf_file.resolve().is_relative_to(result)


class TestSingleFileMode:
    def test_target_file_skips_pipeline_level_extractors(self, sample_pipeline: Path):
        """In single-file mode, schema / config / README are NOT parsed."""
        target = sample_pipeline / "main.nf"

        with patch.object(PipelineExtractor, "_extract_from_lsp") as mock_lsp:
            extractor = PipelineExtractor(
                workspace_path=sample_pipeline,
                target_file=target,
                use_cache=False,
            )
            pipeline = extractor.extract()

            # LSP extraction still runs
            mock_lsp.assert_called_once()

            # Schema-derived inputs should NOT be present
            assert pipeline.inputs == []
            # Config-derived params should NOT be present
            assert pipeline.config_params == []
            # README content should NOT be loaded
            assert pipeline.metadata.readme_content == ""
            # Pipeline name is NOT inferred from workspace dir in this mode
            assert pipeline.metadata.name == ""

    def test_target_file_restricts_lsp_scan(self, tmp_path: Path):
        """_extract_from_lsp scans only the target file, not the whole workspace."""
        (tmp_path / "nextflow.config").write_text("")
        target = tmp_path / "modules" / "tool" / "main.nf"
        target.parent.mkdir(parents=True)
        target.write_text("process FOO {}\n")
        # Other .nf files in workspace that should be IGNORED in single-file mode
        (tmp_path / "other.nf").write_text("process BAR {}\n")

        seen_files: list[Path] = []

        def fake_extract_file_symbols(self, client, file_path, pipeline, git_info=None):
            seen_files.append(file_path)

        # Patch the inner LSPClient so we don't actually start the server.
        with (
            patch("nf_docs.extractor.LSPClient") as mock_lsp_cls,
            patch.object(
                PipelineExtractor,
                "_extract_file_symbols",
                fake_extract_file_symbols,
            ),
        ):
            mock_lsp_cls.return_value.__enter__.return_value.get_workspace_symbols.return_value = []

            extractor = PipelineExtractor(
                workspace_path=tmp_path,
                target_file=target,
                use_cache=False,
            )
            extractor.extract()

        # Only the target file was processed
        assert seen_files == [target.resolve()]

    def test_target_file_uses_per_file_cache_key(self, tmp_path: Path):
        """Single-file mode caches per-target-file, not per-workspace."""
        target_a = tmp_path / "a" / "main.nf"
        target_b = tmp_path / "b" / "main.nf"
        target_a.parent.mkdir()
        target_b.parent.mkdir()
        target_a.write_text("process A {}\n")
        target_b.write_text("process B {}\n")

        cache = PipelineCache(cache_dir=tmp_path / ".cache")
        # Different target files inside the same workspace must produce
        # different cache paths so module results don't collide.
        path_a = cache._get_cache_path(tmp_path, target_file=target_a)
        path_b = cache._get_cache_path(tmp_path, target_file=target_b)
        path_pipeline = cache._get_cache_path(tmp_path)

        assert path_a != path_b
        assert path_a != path_pipeline
        assert "_mod_" in path_a.name
        assert "_mod_" not in path_pipeline.name

    def test_target_file_cache_invalidates_on_content_change(self, tmp_path: Path):
        """Editing the target file changes its cache key."""
        target = tmp_path / "main.nf"
        target.write_text("process FASTQC {}\n")

        cache = PipelineCache(cache_dir=tmp_path / ".cache")
        before = cache._get_cache_path(tmp_path, target_file=target)
        target.write_text("process BWA {}\n")
        after = cache._get_cache_path(tmp_path, target_file=target)
        assert before != after


class TestReadmeExtraction:
    def test_extract_simple_readme(self, tmp_path: Path):
        """Test extraction from a simple README."""
        readme = tmp_path / "README.md"
        readme.write_text("# My Pipeline\n\nThis is a test pipeline.\n")

        with patch.object(PipelineExtractor, "_extract_from_lsp"):
            extractor = PipelineExtractor(workspace_path=tmp_path)
            pipeline = extractor.extract()

            # README content goes into readme_content field (not description)
            assert "test pipeline" in pipeline.metadata.readme_content.lower()

    def test_extract_readme_with_badges(self, tmp_path: Path):
        """Test extraction skips badge lines."""
        readme = tmp_path / "README.md"
        readme.write_text(
            "# My Pipeline\n\n"
            "[![Build Status](https://example.com/badge.svg)](https://example.com)\n"
            "![Coverage](https://example.com/coverage.svg)\n\n"
            "This is the actual description.\n"
        )

        with patch.object(PipelineExtractor, "_extract_from_lsp"):
            extractor = PipelineExtractor(workspace_path=tmp_path)
            pipeline = extractor.extract()

            # README content goes into readme_content field (not description)
            assert "actual description" in pipeline.metadata.readme_content.lower()
            assert "badge" not in pipeline.metadata.readme_content.lower()

    def test_no_readme(self, tmp_path: Path):
        """Test extraction when no README exists."""
        with patch.object(PipelineExtractor, "_extract_from_lsp"):
            extractor = PipelineExtractor(workspace_path=tmp_path)
            pipeline = extractor.extract()

            # Should use directory name as fallback
            assert pipeline.metadata.name == tmp_path.name


class TestMetadataMerging:
    def test_schema_takes_priority(self, sample_pipeline: Path):
        """Test that schema metadata takes priority over config."""
        with patch.object(PipelineExtractor, "_extract_from_lsp"):
            extractor = PipelineExtractor(workspace_path=sample_pipeline)
            pipeline = extractor.extract()

            # Schema has "Test Pipeline" as title
            assert pipeline.metadata.name == "Test Pipeline"


class TestInputGroups:
    def test_inputs_grouped_correctly(self, sample_pipeline: Path):
        """Test that inputs are grouped by their schema group."""
        with patch.object(PipelineExtractor, "_extract_from_lsp"):
            extractor = PipelineExtractor(workspace_path=sample_pipeline)
            pipeline = extractor.extract()

            groups = pipeline.get_input_groups()
            assert "Input/output options" in groups
            assert "Reference genome options" in groups


class TestConfigOptions:
    """
    Each NfDocsConfig option changes what comes out of extraction.

    These assert both settings of every option, so they fail whether an option
    stops being consulted or starts being applied backwards.
    """

    def _write_schema(self, workspace: Path) -> None:
        """Write a schema with one hidden parameter and one prefixed parameter."""
        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "Test Pipeline",
            "$defs": {
                "options": {
                    "title": "Options",
                    "type": "object",
                    "properties": {
                        "input": {"type": "string", "description": "Samplesheet"},
                        "tracedir": {
                            "type": "string",
                            "description": "Trace directory",
                            "hidden": True,
                        },
                        "internal_debug": {"type": "boolean", "description": "Debug"},
                    },
                }
            },
        }
        (workspace / "nextflow_schema.json").write_text(json.dumps(schema))

    def _extract(self, workspace: Path, config: NfDocsConfig) -> Pipeline:
        """Extract from ``workspace`` with the LSP and cache out of the way."""
        with patch.object(PipelineExtractor, "_extract_from_lsp"):
            extractor = PipelineExtractor(workspace_path=workspace, config=config, use_cache=False)
            return extractor.extract()

    def test_include_hidden_params_keeps_hidden_by_default(self, tmp_path: Path):
        """Hidden schema parameters are included unless the option says otherwise."""
        self._write_schema(tmp_path)

        pipeline = self._extract(tmp_path, NfDocsConfig())

        assert "tracedir" in {inp.name for inp in pipeline.inputs}

    def test_include_hidden_params_false_drops_hidden(self, tmp_path: Path):
        """Setting include_hidden_params to False removes hidden parameters."""
        self._write_schema(tmp_path)

        pipeline = self._extract(tmp_path, NfDocsConfig(include_hidden_params=False))

        input_names = {inp.name for inp in pipeline.inputs}
        assert "tracedir" not in input_names
        # Visible parameters are untouched
        assert "input" in input_names

    def test_ignore_input_prefixes_drops_matching_params(self, tmp_path: Path):
        """Inputs matching ignore_input_prefixes are excluded."""
        self._write_schema(tmp_path)

        kept = self._extract(tmp_path, NfDocsConfig())
        assert "internal_debug" in {inp.name for inp in kept.inputs}

        dropped = self._extract(tmp_path, NfDocsConfig(ignore_input_prefixes=["internal_"]))
        input_names = {inp.name for inp in dropped.inputs}
        assert "internal_debug" not in input_names
        assert "input" in input_names

    def test_filtered_inputs_do_not_reappear_as_config_params(self, tmp_path: Path):
        """A parameter hidden from the inputs section isn't shown as a config param."""
        self._write_schema(tmp_path)
        config_params = [ConfigParam(name="tracedir", default="./trace")]

        with patch(
            "nf_docs.extractor.parse_config", return_value=(PipelineMetadata(), config_params)
        ):
            pipeline = self._extract(tmp_path, NfDocsConfig(include_hidden_params=False))

        assert "tracedir" not in {p.name for p in pipeline.config_params}

    def test_ignore_config_prefixes_drops_matching_params(self, tmp_path: Path):
        """Config params matching ignore_config_prefixes are excluded."""
        config_params = [
            ConfigParam(name="genomes.GRCh38.fasta", default="ref.fa"),
            ConfigParam(name="max_cpus", default=16),
        ]

        with patch(
            "nf_docs.extractor.parse_config", return_value=(PipelineMetadata(), config_params)
        ):
            kept = self._extract(tmp_path, NfDocsConfig(ignore_config_prefixes=[]))
            dropped = self._extract(tmp_path, NfDocsConfig(ignore_config_prefixes=["genomes."]))

        assert "genomes.GRCh38.fasta" in {p.name for p in kept.config_params}
        dropped_names = {p.name for p in dropped.config_params}
        assert "genomes.GRCh38.fasta" not in dropped_names
        assert "max_cpus" in dropped_names

    def test_strip_readme_badges_false_keeps_badges(self, tmp_path: Path):
        """Badge lines survive when strip_readme_badges is turned off."""
        (tmp_path / "README.md").write_text(
            "# My Pipeline\n\n"
            "[![Build Status](https://example.com/badge.svg)](https://example.com)\n\n"
            "This is the actual description.\n"
        )

        stripped = self._extract(tmp_path, NfDocsConfig())
        kept = self._extract(tmp_path, NfDocsConfig(strip_readme_badges=False))

        assert "badge" not in stripped.metadata.readme_content.lower()
        assert "badge" in kept.metadata.readme_content.lower()
        # Either way the prose is preserved - stripping must not eat the body
        assert "actual description" in stripped.metadata.readme_content.lower()
        assert "actual description" in kept.metadata.readme_content.lower()

    def test_max_readme_length_truncates_at_a_line_break(self, tmp_path: Path):
        """README content is trimmed to the configured length, on a line boundary."""
        body = "\n".join(f"Line {i} of the readme." for i in range(50))
        (tmp_path / "README.md").write_text(f"# My Pipeline\n\n{body}\n")

        full = self._extract(tmp_path, NfDocsConfig()).metadata.readme_content
        truncated = self._extract(tmp_path, NfDocsConfig(max_readme_length=100))
        content = truncated.metadata.readme_content

        assert len(full) > 100
        assert len(content) <= 100
        assert full.startswith(content)
        # Cut on a line boundary, so no line is left half-written
        assert full[len(content)] == "\n"

    def test_exclude_patterns_reach_the_language_server(self, tmp_path: Path):
        """Configured exclude patterns are passed through to the LSP client."""
        (tmp_path / "main.nf").write_text("process FOO {}\n")

        with patch("nf_docs.extractor.LSPClient") as mock_lsp_cls:
            mock_lsp_cls.return_value.__enter__.return_value.get_workspace_symbols.return_value = []
            extractor = PipelineExtractor(
                workspace_path=tmp_path,
                config=NfDocsConfig(exclude_patterns=["testdata"]),
                use_cache=False,
            )
            extractor.extract()

        assert mock_lsp_cls.call_args.kwargs["exclude_patterns"] == ["testdata"]


class TestSymbolNameParsing:
    """Test parsing of Nextflow LSP symbol names."""

    def test_parse_process_name(self, tmp_path: Path):
        """Test parsing process symbol names."""
        extractor = PipelineExtractor(workspace_path=tmp_path)

        symbol_type, name = extractor._parse_symbol_name("process FASTQC")
        assert symbol_type == "process"
        assert name == "FASTQC"

    def test_parse_workflow_name(self, tmp_path: Path):
        """Test parsing workflow symbol names."""
        extractor = PipelineExtractor(workspace_path=tmp_path)

        symbol_type, name = extractor._parse_symbol_name("workflow PIPELINE")
        assert symbol_type == "workflow"
        assert name == "PIPELINE"

    def test_parse_entry_workflow(self, tmp_path: Path):
        """Test parsing entry workflow symbol name."""
        extractor = PipelineExtractor(workspace_path=tmp_path)

        symbol_type, name = extractor._parse_symbol_name("workflow <entry>")
        assert symbol_type == "workflow"
        assert name == ""

    def test_parse_function_name(self, tmp_path: Path):
        """Test parsing function symbol names."""
        extractor = PipelineExtractor(workspace_path=tmp_path)

        symbol_type, name = extractor._parse_symbol_name("function myHelper")
        assert symbol_type == "function"
        assert name == "myHelper"

    def test_parse_enum_name(self, tmp_path: Path):
        """Test parsing enum symbol names."""
        extractor = PipelineExtractor(workspace_path=tmp_path)

        symbol_type, name = extractor._parse_symbol_name("enum MyEnum")
        assert symbol_type == "enum"
        assert name == "MyEnum"

    def test_parse_unknown_name(self, tmp_path: Path):
        """Test parsing names without known prefix."""
        extractor = PipelineExtractor(workspace_path=tmp_path)

        symbol_type, name = extractor._parse_symbol_name("something_else")
        assert symbol_type == "unknown"
        assert name == "something_else"

    def test_parse_empty_name(self, tmp_path: Path):
        """Test parsing empty name."""
        extractor = PipelineExtractor(workspace_path=tmp_path)

        symbol_type, name = extractor._parse_symbol_name("")
        assert symbol_type == "unknown"
        assert name == ""


class TestGroovydocParsing:
    """Tests for Groovydoc parsing from source files."""

    def test_parse_groovydoc_at_param_return(self):
        """Parse standard @param and @return tags."""
        from nf_docs.extractor import _parse_groovydoc_comment

        comment = """
         * Align reads to reference genome.
         *
         * @param meta  Map containing sample information
         * @param bam   Input BAM file
         * @return txt  Tuple of meta and output text file
         * @return bam  Tuple of meta and output BAM file
        """
        docstring, params = _parse_groovydoc_comment(comment)
        assert docstring == "Align reads to reference genome."
        assert params["meta"] == "Map containing sample information"
        assert params["bam"] == "Input BAM file"
        assert params["_return_txt"] == "Tuple of meta and output text file"
        assert params["_return_bam"] == "Tuple of meta and output BAM file"

    def test_parse_groovydoc_bullet_format(self):
        """Parse Inputs:/Outputs: bullet-list format."""
        from nf_docs.extractor import _parse_groovydoc_comment

        comment = """
         * Detect structural variants.
         *
         * Inputs:
         *   - - meta: Map of sample info
         *     - bam: Input BAM file
         * Outputs:
         *   - - meta: Map of sample info
         *     - txt: SvPileup breakpoint output
        """
        docstring, params = _parse_groovydoc_comment(comment)
        assert docstring == "Detect structural variants."
        assert params["meta"] == "Map of sample info"
        assert params["bam"] == "Input BAM file"
        assert params["_return_txt"] == "SvPileup breakpoint output"

    def test_parse_groovydoc_from_source_with_intervening_code(self):
        """Groovydoc with code between */ and process declaration."""
        from nf_docs.extractor import _parse_groovydoc_from_source

        source = """\
/**
 * Detect SVs from BAM.
 *
 * @param meta  Sample metadata
 * @param bam   Input BAM
 * @return txt  Output text file
 */
nextflow.preview.types = true
process SV_PILEUP {
    input:
    (meta, bam): Tuple<?, Path>

    output:
    txt
    bam
}
"""
        docstring, params = _parse_groovydoc_from_source(source, "SV_PILEUP")
        assert "Detect SVs from BAM" in docstring
        assert params["meta"] == "Sample metadata"
        assert params["bam"] == "Input BAM"
        assert params["_return_txt"] == "Output text file"

    def test_parse_groovydoc_from_source_not_found(self):
        """Returns empty when process not found in source."""
        from nf_docs.extractor import _parse_groovydoc_from_source

        docstring, params = _parse_groovydoc_from_source(
            "process OTHER { script: '' }\n", "MISSING"
        )
        assert docstring == ""
        assert params == {}

    def test_find_param_description_simple(self):
        """Match a simple input name to param docs."""
        from nf_docs.extractor import _find_param_description

        param_docs = {"reads": "FASTQ input files", "genome": "Reference genome"}
        assert _find_param_description("reads", param_docs) == "FASTQ input files"

    def test_find_param_description_tuple(self):
        """Match tuple component names to param docs."""
        from nf_docs.extractor import _find_param_description

        param_docs = {
            "meta": "Sample metadata map",
            "bam": "Input BAM file",
        }
        desc = _find_param_description("val(meta), path(bam)", param_docs)
        assert "meta" in desc
        assert "Sample metadata map" in desc
        assert "bam" in desc
        assert "Input BAM file" in desc

    def test_find_param_description_no_match(self):
        """Returns empty when no param docs match."""
        from nf_docs.extractor import _find_param_description

        assert _find_param_description("unknown", {"meta": "desc"}) == ""
        assert _find_param_description("val(x)", {"meta": "desc"}) == ""
        assert _find_param_description("reads", {}) == ""
