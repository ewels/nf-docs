"""Tests for the pipeline extractor."""

from pathlib import Path
from unittest.mock import patch

from nf_docs.extractor import PipelineExtractor


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
