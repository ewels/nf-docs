"""Tests for the high-level Python API (nf_docs.api)."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

import nf_docs
from nf_docs.api import extract, generate, render, render_pages
from nf_docs.config import NfDocsConfig
from nf_docs.extractor import PipelineExtractor
from nf_docs.models import ConfigParam, Pipeline, PipelineMetadata, Process
from nf_docs.output import (
    looks_like_module,
    normalize_format,
    resolve_source,
)


@pytest.fixture
def module_dir(tmp_path: Path) -> Path:
    """A directory holding a module-style main.nf (process, no workflow)."""
    module = tmp_path / "modules" / "mytool"
    module.mkdir(parents=True)
    (module / "main.nf").write_text(
        "process MYTOOL {\n    input:\n    path reads\n\n    script:\n    '''\n    mytool\n    '''\n}\n"
    )
    return module


@pytest.fixture
def rendered_pipeline() -> Pipeline:
    """A small Pipeline model that needs no extraction."""
    return Pipeline(
        metadata=PipelineMetadata(name="Test Pipeline", description="A test"),
        processes=[Process(name="FASTQC", docstring="Quality control")],
    )


class TestNormalizeFormat:
    """Tests for format alias normalization."""

    def test_md_alias(self) -> None:
        assert normalize_format("md") == "markdown"

    def test_case_insensitive(self) -> None:
        assert normalize_format("HTML") == "html"

    def test_passthrough(self) -> None:
        assert normalize_format("json") == "json"


class TestResolveSource:
    """Tests for single-file vs pipeline source resolution."""

    def test_pipeline_directory(self, sample_pipeline: Path) -> None:
        resolved, single_file = resolve_source(sample_pipeline)
        assert resolved == sample_pipeline
        assert single_file is False

    def test_nf_file(self, sample_pipeline: Path) -> None:
        resolved, single_file = resolve_source(sample_pipeline / "main.nf")
        assert resolved == sample_pipeline / "main.nf"
        assert single_file is True

    def test_module_directory_autodetected(self, module_dir: Path) -> None:
        """A bare module dir resolves to its main.nf in single-file mode."""
        resolved, single_file = resolve_source(module_dir)
        assert resolved == module_dir / "main.nf"
        assert single_file is True

    def test_non_nf_file_rejected(self, tmp_path: Path) -> None:
        other = tmp_path / "notes.txt"
        other.write_text("hello")
        with pytest.raises(ValueError, match="must be a .nf file"):
            resolve_source(other)

    def test_looks_like_module(self, module_dir: Path, sample_pipeline: Path) -> None:
        assert looks_like_module(module_dir / "main.nf") is True
        # The sample pipeline's main.nf defines a workflow, so it isn't a module
        assert looks_like_module(sample_pipeline / "main.nf") is False


class TestExtract:
    """Tests for nf_docs.extract()."""

    def test_extract_directory(self, sample_pipeline: Path) -> None:
        with patch.object(PipelineExtractor, "_extract_from_lsp"):
            pipeline = extract(sample_pipeline)
        assert isinstance(pipeline, Pipeline)
        assert pipeline.inputs

    def test_extract_single_file(self, sample_pipeline: Path) -> None:
        with patch.object(PipelineExtractor, "_extract_from_lsp"):
            pipeline = extract(sample_pipeline / "main.nf")
        assert isinstance(pipeline, Pipeline)

    def test_rejects_non_nf_file(self, tmp_path: Path) -> None:
        other = tmp_path / "notes.txt"
        other.write_text("hello")
        with pytest.raises(ValueError):
            extract(other)

    def test_rejects_missing_path(self, tmp_path: Path) -> None:
        """A typo'd path must raise, not return an empty Pipeline named after it."""
        with pytest.raises(ValueError, match="does not exist"):
            extract(tmp_path / "no_such_pipeline")

    def test_cache_is_keyed_on_config(self, sample_pipeline: Path) -> None:
        """
        Two configs must not share a cache entry.

        Without the config in the cache key a CLI run (user config) and a
        library call (defaults) return each other's results for an unchanged
        pipeline.
        """
        params = (PipelineMetadata(), [ConfigParam(name="genomes.mm10")])
        with patch.object(PipelineExtractor, "_extract_from_lsp"):
            with patch("nf_docs.extractor.parse_config", return_value=params):
                # Caching left ON deliberately - that is the thing under test.
                permissive = extract(
                    sample_pipeline, config=NfDocsConfig(ignore_config_prefixes=[])
                )
                restrictive = extract(
                    sample_pipeline, config=NfDocsConfig(ignore_config_prefixes=["genomes."])
                )
        assert [p.name for p in permissive.config_params] == ["genomes.mm10"]
        assert [p.name for p in restrictive.config_params] == []

    def test_config_is_injected(self, sample_pipeline: Path) -> None:
        """A passed config reaches the extractor rather than the global one."""
        config = NfDocsConfig(ignore_config_prefixes=["params."])
        with patch("nf_docs.api.PipelineExtractor") as mock_cls:
            extract(sample_pipeline, config=config)
        assert mock_cls.call_args.kwargs["config"] is config

    def test_defaults_are_hermetic(self, sample_pipeline: Path) -> None:
        """Without a config argument, defaults are used - not the user's file."""
        assert PipelineExtractor(workspace_path=sample_pipeline).config == NfDocsConfig()

    def test_config_filters_config_params(self, sample_pipeline: Path) -> None:
        """The injected config actually affects the extracted result."""
        with patch.object(PipelineExtractor, "_extract_from_lsp"):
            with patch(
                "nf_docs.extractor.parse_config",
                return_value=(PipelineMetadata(), [ConfigParam(name="genomes.hg38")]),
            ):
                default = extract(sample_pipeline, use_cache=False)
                permissive = extract(
                    sample_pipeline,
                    use_cache=False,
                    config=NfDocsConfig(ignore_config_prefixes=[]),
                )
        assert [p.name for p in default.config_params] == []
        assert [p.name for p in permissive.config_params] == ["genomes.hg38"]

    def test_progress_callback_is_called(self, sample_pipeline: Path) -> None:
        updates = []
        with patch.object(PipelineExtractor, "_extract_from_lsp"):
            extract(sample_pipeline, use_cache=False, progress_callback=updates.append)
        assert updates
        assert all(hasattr(u, "phase") for u in updates)


class TestRender:
    """Tests for nf_docs.render()."""

    @pytest.mark.parametrize("output_format", ["json", "yaml", "markdown", "html", "table"])
    def test_all_formats(self, rendered_pipeline: Pipeline, output_format: str) -> None:
        result = render(rendered_pipeline, output_format)
        assert isinstance(result, str)
        assert result

    def test_md_alias(self, rendered_pipeline: Pipeline) -> None:
        assert render(rendered_pipeline, "md") == render(rendered_pipeline, "markdown")

    def test_json_is_parseable(self, rendered_pipeline: Pipeline) -> None:
        data = json.loads(render(rendered_pipeline, "json"))
        assert data["pipeline"]["name"] == "Test Pipeline"

    def test_title_override(self, rendered_pipeline: Pipeline) -> None:
        assert "Custom Title" in render(rendered_pipeline, "markdown", title="Custom Title")

    def test_renderer_kwargs_are_passed(self, rendered_pipeline: Pipeline) -> None:
        compact = render(rendered_pipeline, "json", indent=0)
        spaced = render(rendered_pipeline, "json", indent=8)
        assert len(spaced) > len(compact)

    def test_single_file_mode(self, rendered_pipeline: Pipeline) -> None:
        result = render(rendered_pipeline, "markdown", single_file=True)
        assert isinstance(result, str)
        assert result

    def test_unsupported_format(self, rendered_pipeline: Pipeline) -> None:
        with pytest.raises(ValueError, match="Unsupported format"):
            render(rendered_pipeline, "pdf")


class TestRenderPages:
    """Tests for nf_docs.render_pages()."""

    def test_default_format_matches_render(self, rendered_pipeline: Pipeline) -> None:
        """html, like render() and generate() - not markdown."""
        assert set(render_pages(rendered_pipeline, use_tailwind=False)) == {"index.html"}

    def test_markdown_returns_one_entry_per_page(self, rendered_pipeline: Pipeline) -> None:
        pages = render_pages(rendered_pipeline, "markdown")
        assert set(pages) == {"index.md", "inputs.md", "processes.md"}

    @pytest.mark.parametrize("output_format", ["html", "markdown", "table", "json", "yaml"])
    def test_all_formats(self, rendered_pipeline: Pipeline, output_format: str) -> None:
        kwargs = {"use_tailwind": False} if output_format == "html" else {}
        pages = render_pages(rendered_pipeline, output_format, **kwargs)
        assert pages
        assert all(isinstance(name, str) and content for name, content in pages.items())

    def test_md_alias(self, rendered_pipeline: Pipeline) -> None:
        assert render_pages(rendered_pipeline, "md") == render_pages(rendered_pipeline, "markdown")

    def test_title_override(self, rendered_pipeline: Pipeline) -> None:
        pages = render_pages(rendered_pipeline, "markdown", title="Renamed")
        assert "# Renamed" in pages["index.md"]

    def test_renderer_kwargs_are_passed(self, rendered_pipeline: Pipeline) -> None:
        pages = render_pages(rendered_pipeline, "json", indent=4)
        assert '\n    "pipeline"' in next(iter(pages.values()))

    def test_unsupported_format(self, rendered_pipeline: Pipeline) -> None:
        with pytest.raises(ValueError, match="Unsupported format"):
            render_pages(rendered_pipeline, "pdf")

    def test_matches_what_generate_writes(self, sample_pipeline: Path, tmp_path: Path) -> None:
        """
        The consumer-facing promise: render_pages() replaces generating into a
        throwaway directory and reading the files back.
        """
        out = tmp_path / "docs"
        with patch.object(PipelineExtractor, "_extract_from_lsp"):
            pipeline = extract(sample_pipeline)
            created = generate(
                sample_pipeline,
                output_format="markdown",
                output=out,
                include_generation_info=False,
            )

        pages = render_pages(pipeline, "markdown", include_generation_info=False)

        assert {p.name for p in created} == set(pages)
        for path in created:
            assert path.read_text(encoding="utf-8") == pages[path.name]


class TestReproducibleOutput:
    """include_generation_info=False reaches the renderers through the facade."""

    def test_the_flag_reaches_the_renderer(
        self, rendered_pipeline: Pipeline, advancing_clock
    ) -> None:
        """
        The facade only has to thread the flag through to the renderer.
        Per-format byte identity is covered at the renderer level, in
        tests/test_renderers.py::TestReproducibleOutput.
        """
        assert render(rendered_pipeline, "markdown", include_generation_info=False) == render(
            rendered_pipeline, "markdown", include_generation_info=False
        )
        assert render_pages(
            rendered_pipeline, "markdown", include_generation_info=False
        ) == render_pages(rendered_pipeline, "markdown", include_generation_info=False)

    def test_generate_writes_identical_bytes(
        self, sample_pipeline: Path, tmp_path: Path, advancing_clock
    ) -> None:
        """The actual requirement: two builds produce the same files on disk."""
        with patch.object(PipelineExtractor, "_extract_from_lsp"):
            first = generate(
                sample_pipeline,
                output_format="markdown",
                output=tmp_path / "first",
                include_generation_info=False,
            )
            second = generate(
                sample_pipeline,
                output_format="markdown",
                output=tmp_path / "second",
                include_generation_info=False,
            )

        assert [p.name for p in first] == [p.name for p in second]
        for a, b in zip(first, second, strict=True):
            assert a.read_bytes() == b.read_bytes()

    def test_single_file_output_is_reproducible(self, module_dir: Path, advancing_clock) -> None:
        """Single-module output goes through render_single_file(), not render()."""
        with patch.object(PipelineExtractor, "_extract_from_lsp"):
            pipeline = extract(module_dir)

        kwargs = {"single_file": True, "use_tailwind": False, "include_generation_info": False}
        assert render(pipeline, "html", **kwargs) == render(pipeline, "html", **kwargs)


class TestGenerate:
    """Tests for nf_docs.generate()."""

    def test_returns_written_paths(self, sample_pipeline: Path, tmp_path: Path) -> None:
        out = tmp_path / "site"
        with patch.object(PipelineExtractor, "_extract_from_lsp"):
            created = generate(sample_pipeline, output_format="html", output=out)
        assert created
        assert all(p.exists() for p in created)

    def test_json_to_explicit_file(self, sample_pipeline: Path, tmp_path: Path) -> None:
        target = tmp_path / "api.json"
        with patch.object(PipelineExtractor, "_extract_from_lsp"):
            created = generate(sample_pipeline, output_format="json", output=target)
        assert created == [target]
        assert json.loads(target.read_text())

    def test_json_default_location(self, sample_pipeline: Path) -> None:
        """Without an output, json lands in <pipeline>/docs/pipeline.json."""
        with patch.object(PipelineExtractor, "_extract_from_lsp"):
            created = generate(sample_pipeline, output_format="json")
        assert created == [sample_pipeline / "docs" / "pipeline.json"]
        assert created[0].exists()

    def test_markdown_default_directory(self, sample_pipeline: Path) -> None:
        with patch.object(PipelineExtractor, "_extract_from_lsp"):
            created = generate(sample_pipeline, output_format="markdown")
        assert created
        assert all(p.is_relative_to(sample_pipeline / "docs") for p in created)

    def test_single_file_writes_readme(self, module_dir: Path) -> None:
        """A module gets a README.md next to its main.nf."""
        with patch.object(PipelineExtractor, "_extract_from_lsp"):
            created = generate(module_dir, output_format="md")
        assert created == [module_dir / "README.md"]
        assert created[0].exists()

    def test_single_file_json_writes_a_file(self, module_dir: Path) -> None:
        """Unlike the CLI, generate() writes json to disk rather than stdout."""
        with patch.object(PipelineExtractor, "_extract_from_lsp"):
            created = generate(module_dir, output_format="json")
        assert created == [module_dir / "main.json"]
        assert created[0].exists()

    def test_title_reaches_output(self, sample_pipeline: Path, tmp_path: Path) -> None:
        with patch.object(PipelineExtractor, "_extract_from_lsp"):
            created = generate(
                sample_pipeline,
                output_format="markdown",
                output=tmp_path / "docs",
                title="My Custom Pipeline",
            )
        assert any("My Custom Pipeline" in p.read_text() for p in created)


class TestPublicSurface:
    """The names promised in nf_docs.__all__ must resolve."""

    def test_all_names_resolve(self) -> None:
        missing = [name for name in nf_docs.__all__ if not hasattr(nf_docs, name)]
        assert missing == []

    def test_facade_is_exported(self) -> None:
        assert nf_docs.extract is extract
        assert nf_docs.render is render
        assert nf_docs.render_pages is render_pages
        assert nf_docs.generate is generate

    def test_py_typed_marker_ships(self) -> None:
        assert (Path(nf_docs.__file__).parent / "py.typed").exists()
