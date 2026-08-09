"""Tests for output renderers."""

import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest
import yaml

import nf_docs
from nf_docs.models import (
    ConfigParam,
    Function,
    Pipeline,
    PipelineInput,
    PipelineMetadata,
    Process,
    ProcessInput,
    ProcessOutput,
    Workflow,
)
from nf_docs.output import (
    FORMAT_ALIASES,
    SINGLE_FILE_OUTPUT_POLICY,
    supported_formats,
)
from nf_docs.renderers import (
    RENDERERS,
    BaseRenderer,
    HTMLRenderer,
    JSONRenderer,
    MarkdownRenderer,
    TableRenderer,
    YAMLRenderer,
    get_renderer,
)
from nf_docs.renderers.table import (
    AVAILABLE_SECTIONS,
    BEGIN_MARKER,
    END_MARKER,
    extract_template,
    inject_into_content,
)


@pytest.fixture
def sample_pipeline() -> Pipeline:
    """Create a sample pipeline for testing renderers."""
    return Pipeline(
        metadata=PipelineMetadata(
            name="test-pipeline",
            description="A test pipeline",
            version="1.0.0",
            authors=["Test Author"],
        ),
        inputs=[
            PipelineInput(
                name="input",
                type="string",
                description="Input file path",
                required=True,
                group="Input/output",
            ),
            PipelineInput(
                name="outdir",
                type="string",
                description="Output directory",
                default="./results",
                group="Input/output",
            ),
        ],
        workflows=[
            Workflow(
                name="MAIN",
                docstring="Main workflow",
                file="main.nf",
                line=10,
                is_entry=True,
                calls=["PROCESS_A", "PROCESS_B"],
            ),
        ],
        processes=[
            Process(
                name="PROCESS_A",
                docstring="First process",
                file="main.nf",
                line=20,
                inputs=[ProcessInput(name="input_file", type="path")],
                outputs=[ProcessOutput(name="*.txt", type="path", emit="output")],
                directives={"cpus": 2, "memory": "4.GB"},
            ),
            Process(
                name="PROCESS_B",
                docstring="Second process",
                file="main.nf",
                line=40,
            ),
        ],
    )


class TestGetRenderer:
    def test_get_json_renderer(self):
        renderer_class = get_renderer("json")
        assert renderer_class == JSONRenderer

    def test_get_yaml_renderer(self):
        renderer_class = get_renderer("yaml")
        assert renderer_class == YAMLRenderer

    def test_get_markdown_renderer(self):
        renderer_class = get_renderer("markdown")
        assert renderer_class == MarkdownRenderer

    def test_get_md_renderer(self):
        renderer_class = get_renderer("md")
        assert renderer_class == MarkdownRenderer

    def test_get_html_renderer(self):
        renderer_class = get_renderer("html")
        assert renderer_class == HTMLRenderer

    def test_invalid_format(self):
        with pytest.raises(ValueError, match="Unsupported format"):
            get_renderer("invalid")

    def test_get_table_renderer(self):
        renderer_class = get_renderer("table")
        assert renderer_class == TableRenderer


class TestJSONRenderer:
    def test_render(self, sample_pipeline: Pipeline):
        renderer = JSONRenderer()
        output = renderer.render(sample_pipeline)

        # Should be valid JSON
        data = json.loads(output)

        assert data["pipeline"]["name"] == "test-pipeline"
        assert len(data["inputs"]) == 2
        assert len(data["processes"]) == 2

    def test_render_with_custom_title(self, sample_pipeline: Pipeline):
        renderer = JSONRenderer(title="Custom Title")
        output = renderer.render(sample_pipeline)

        data = json.loads(output)
        assert data["pipeline"]["name"] == "Custom Title"

    def test_render_to_directory(self, sample_pipeline: Pipeline, tmp_path: Path):
        renderer = JSONRenderer()
        files = renderer.render_to_directory(sample_pipeline, tmp_path)

        assert len(files) == 1
        assert files[0].exists()
        assert files[0].suffix == ".json"

        # Verify content
        data = json.loads(files[0].read_text())
        assert data["pipeline"]["name"] == "test-pipeline"


class TestYAMLRenderer:
    def test_render(self, sample_pipeline: Pipeline):
        renderer = YAMLRenderer()
        output = renderer.render(sample_pipeline)

        # Should be valid YAML
        data = yaml.safe_load(output)

        assert data["pipeline"]["name"] == "test-pipeline"
        assert len(data["inputs"]) == 2

    def test_render_to_directory(self, sample_pipeline: Pipeline, tmp_path: Path):
        renderer = YAMLRenderer()
        files = renderer.render_to_directory(sample_pipeline, tmp_path)

        assert len(files) == 1
        assert files[0].suffix == ".yaml"


class TestMarkdownRenderer:
    def test_render_index(self, sample_pipeline: Pipeline):
        renderer = MarkdownRenderer()
        output = renderer.render(sample_pipeline)

        # Check for key sections
        assert "# test-pipeline" in output
        assert "Version:" in output
        assert "A test pipeline" in output

    def test_render_inputs(self, sample_pipeline: Pipeline):
        renderer = MarkdownRenderer()
        output = renderer.render(sample_pipeline)

        # Check inputs are documented
        assert "--input" in output
        assert "--outdir" in output
        assert "Required" in output

    def test_render_processes(self, sample_pipeline: Pipeline):
        renderer = MarkdownRenderer()
        output = renderer.render(sample_pipeline)

        # Check processes are documented
        assert "PROCESS_A" in output
        assert "PROCESS_B" in output
        assert "First process" in output

    def test_render_to_directory(self, sample_pipeline: Pipeline, tmp_path: Path):
        renderer = MarkdownRenderer()
        files = renderer.render_to_directory(sample_pipeline, tmp_path)

        # Should create multiple files
        assert len(files) >= 3  # At least index, inputs, processes

        # Check expected files exist
        file_names = {f.name for f in files}
        assert "index.md" in file_names
        assert "inputs.md" in file_names
        assert "processes.md" in file_names

    def test_render_workflows_with_calls(self, sample_pipeline: Pipeline):
        renderer = MarkdownRenderer()
        output = renderer.render(sample_pipeline)

        # Check workflow calls are linked
        assert "PROCESS_A" in output
        assert "processes.md#" in output  # Link to process

    def test_custom_title(self, sample_pipeline: Pipeline):
        renderer = MarkdownRenderer(title="My Custom Title")
        output = renderer.render(sample_pipeline)

        assert "# My Custom Title" in output

    def test_render_single_file_module(self):
        """Single-file output for a module should be focused on the process."""
        pipeline = Pipeline(
            processes=[
                Process(
                    name="FASTQC",
                    docstring="Run FastQC",
                    file="modules/fastqc/main.nf",
                    line=10,
                    inputs=[ProcessInput(name="reads", type="path")],
                    outputs=[ProcessOutput(name="*.html", type="path", emit="html")],
                )
            ],
        )

        output = MarkdownRenderer().render_single_file(pipeline)

        # Top-level heading uses the single symbol's name
        assert output.splitlines()[0] == "# FASTQC"
        # Symbol body is present
        assert "## FASTQC" in output
        assert "Run FastQC" in output
        # No multi-file wrappers / pipeline-level sections
        assert "# Processes" not in output
        assert "# Pipeline Inputs" not in output
        assert "inputs.md" not in output
        assert "processes.md" not in output
        # Markdown-Extra {#anchor} attribute syntax is stripped — renderers
        # without attr_list (GitHub, etc.) would show it as literal text.
        assert "{#" not in output
        # No project-attribution footer in single-file mode; the README is
        # meant to be embedded in a docs site with its own footer.
        assert "was built with" not in output

    def test_render_single_file_uses_meta_description(self):
        """When a single symbol has a meta.yml description, surface it under the heading."""
        process = Process(
            name="FASTQC",
            file="modules/fastqc/main.nf",
            line=10,
        )
        process.meta_description = "FastQC gives a quick overview of read quality."
        pipeline = Pipeline(processes=[process])

        output = MarkdownRenderer().render_single_file(pipeline)
        assert "FastQC gives a quick overview of read quality." in output

    def test_render_single_file_empty(self):
        """A file with no symbols still produces sensible output."""
        output = MarkdownRenderer().render_single_file(Pipeline())
        assert "# Documentation" in output
        assert "No processes, workflows, or functions" in output

    def test_html_render_single_file(self):
        """HTML single-file output collapses to a single-page layout."""
        pipeline = Pipeline(
            processes=[
                Process(
                    name="FASTQC",
                    docstring="Run FastQC",
                    file="modules/fastqc/main.nf",
                    line=3,
                )
            ],
        )

        # use_tailwind=False keeps the test fast and avoids the tailwind subprocess.
        output = HTMLRenderer(use_tailwind=False).render_single_file(pipeline)

        # Navbar + main heading both use "Module: FASTQC"
        assert "Module: FASTQC" in output
        assert "<title>Module: FASTQC</title>" in output
        # Footer wording flipped from "Pipeline built with" to "Module built with"
        assert "Module built with" in output
        assert "Pipeline built with" not in output
        # Sidebars are not rendered (their CSS rules remain, but the elements don't)
        assert 'id="left-nav"' not in output
        assert 'id="right-nav"' not in output
        assert 'id="mobile-menu-btn"' not in output
        # The processes section is shown (no `hidden` class on it)
        assert 'id="processes" class="section">' in output
        # Pipeline-level sections are not rendered in single-file mode
        assert 'id="search-results"' not in output
        assert 'id="inputs"' not in output
        assert 'id="config"' not in output
        assert 'id="overview"' not in output

    def test_html_subworkflow_label(self):
        """Single-workflow files use a 'Subworkflow:' label."""
        from nf_docs.models import Workflow as WorkflowModel

        pipeline = Pipeline(
            workflows=[
                WorkflowModel(
                    name="ALIGN_READS",
                    file="subworkflows/align_reads/main.nf",
                    line=1,
                )
            ],
        )
        output = HTMLRenderer(use_tailwind=False).render_single_file(pipeline)
        assert "Subworkflow: ALIGN_READS" in output
        assert "Module: ALIGN_READS" not in output


class TestHTMLRenderer:
    def test_render(self, sample_pipeline: Pipeline):
        renderer = HTMLRenderer(use_tailwind=False)
        output = renderer.render(sample_pipeline)

        # Should be valid HTML (lowercase doctype is valid HTML5)
        assert "<!doctype html>" in output.lower()
        assert "<html" in output
        assert "</html>" in output

    def test_render_contains_content(self, sample_pipeline: Pipeline):
        renderer = HTMLRenderer(use_tailwind=False)
        output = renderer.render(sample_pipeline)

        # Check content is present
        assert "test-pipeline" in output
        assert "PROCESS_A" in output
        assert "PROCESS_B" in output
        assert "--input" in output

    def test_render_contains_navigation(self, sample_pipeline: Pipeline):
        renderer = HTMLRenderer(use_tailwind=False)
        output = renderer.render(sample_pipeline)

        # Check navigation elements (using Tailwind classes now)
        assert "<aside" in output
        assert "<nav" in output
        assert "Overview" in output
        assert "Inputs" in output
        assert "Processes" in output

    def test_render_self_contained(self, sample_pipeline: Pipeline):
        renderer = HTMLRenderer(use_tailwind=False)
        output = renderer.render(sample_pipeline)

        # Should include inline CSS and JS
        assert "<style>" in output
        assert "</style>" in output
        assert "<script>" in output
        assert "</script>" in output

    def test_render_to_directory(self, sample_pipeline: Pipeline, tmp_path: Path):
        renderer = HTMLRenderer(use_tailwind=False)
        files = renderer.render_to_directory(sample_pipeline, tmp_path)

        # Should create single HTML file
        assert len(files) == 1
        assert files[0].name == "index.html"
        assert files[0].exists()


class TestTableRenderer:
    def test_render(self, sample_pipeline: Pipeline):
        renderer = TableRenderer()
        output = renderer.render(sample_pipeline)

        # Should contain key sections
        assert "# test-pipeline" in output
        assert "Version:** 1.0.0" in output
        assert "A test pipeline" in output

    def test_render_inputs_table(self, sample_pipeline: Pipeline):
        renderer = TableRenderer()
        output = renderer.render(sample_pipeline)

        # Check inputs table structure
        assert "## Inputs" in output
        assert "| Name | Description | Type | Default | Required |" in output
        assert "`--input`" in output
        assert "`--outdir`" in output
        assert "| yes |" in output  # input is required
        assert "| no |" in output  # outdir is not required

    def test_render_inputs_grouped(self, sample_pipeline: Pipeline):
        renderer = TableRenderer()
        output = renderer.render(sample_pipeline)

        # Both inputs share a group
        assert "### Input/output" in output

    def test_render_processes_table(self, sample_pipeline: Pipeline):
        renderer = TableRenderer()
        output = renderer.render(sample_pipeline)

        # Check processes section
        assert "## Processes" in output
        assert "`PROCESS_A`" in output
        assert "`PROCESS_B`" in output
        assert "First process" in output

    def test_render_process_io(self, sample_pipeline: Pipeline):
        renderer = TableRenderer()
        output = renderer.render(sample_pipeline)

        # PROCESS_A has inputs and outputs
        assert "### `PROCESS_A` Inputs" in output
        assert "`input_file`" in output
        assert "### `PROCESS_A` Outputs" in output

    def test_render_workflows_table(self, sample_pipeline: Pipeline):
        renderer = TableRenderer()
        output = renderer.render(sample_pipeline)

        # Check workflows section
        assert "## Workflows" in output
        assert "| Name | Description | Entry |" in output
        assert "`MAIN`" in output
        assert "| yes |" in output  # entry workflow

    def test_render_workflow_calls(self, sample_pipeline: Pipeline):
        renderer = TableRenderer()
        output = renderer.render(sample_pipeline)

        # MAIN workflow calls PROCESS_A and PROCESS_B
        assert "`MAIN` calls:** `PROCESS_A`, `PROCESS_B`" in output

    def test_render_to_directory(self, sample_pipeline: Pipeline, tmp_path: Path):
        renderer = TableRenderer()
        files = renderer.render_to_directory(sample_pipeline, tmp_path)

        # Should create single file
        assert len(files) == 1
        assert files[0].name == "README.md"
        assert files[0].exists()

        # Verify content
        content = files[0].read_text()
        assert "# test-pipeline" in content
        assert "## Inputs" in content

    def test_custom_title(self, sample_pipeline: Pipeline):
        renderer = TableRenderer(title="My Custom Title")
        output = renderer.render(sample_pipeline)

        assert "# My Custom Title" in output

    def test_cell_sanitization(self):
        renderer = TableRenderer()
        assert renderer._cell(None) == "n/a"
        assert renderer._cell("") == "n/a"
        assert renderer._cell("hello\nworld") == "hello world"
        assert renderer._cell("foo|bar") == "foo\\|bar"


class TestRendererWithEmptyPipeline:
    def test_json_empty(self):
        pipeline = Pipeline()
        renderer = JSONRenderer()
        output = renderer.render(pipeline)

        data = json.loads(output)
        assert data["inputs"] == []
        assert data["processes"] == []

    def test_markdown_empty(self):
        pipeline = Pipeline()
        renderer = MarkdownRenderer()
        output = renderer.render(pipeline)

        # Should still produce valid markdown
        assert "#" in output

    def test_html_empty(self):
        pipeline = Pipeline()
        renderer = HTMLRenderer(use_tailwind=False)
        output = renderer.render(pipeline)

        # Should still produce valid HTML (lowercase doctype is valid HTML5)
        assert "<!doctype html>" in output.lower()

    def test_table_empty(self):
        pipeline = Pipeline()
        renderer = TableRenderer()
        output = renderer.render(pipeline)

        # Should still produce valid markdown with just a title
        assert "#" in output
        # Should not include empty sections
        assert "## Inputs" not in output
        assert "## Processes" not in output


class TestMarkerInjection:
    """Tests for marker-based injection into existing files."""

    def test_inject_replaces_between_markers(self):
        existing = (
            "# My Project\n"
            "Some intro text.\n"
            f"{BEGIN_MARKER}\n"
            "old generated content\n"
            f"{END_MARKER}\n"
            "Footer text.\n"
        )
        result = inject_into_content(existing, "new generated content")

        assert result is not None
        assert "# My Project" in result
        assert "Some intro text." in result
        assert "new generated content" in result
        assert "Footer text." in result
        assert "old generated content" not in result

    def test_inject_no_markers_returns_none(self):
        result = inject_into_content("# My Project\nNo markers here.\n", "new")

        assert result is None

    def test_inject_only_begin_marker_returns_none(self):
        existing = f"# My Project\n{BEGIN_MARKER}\nsome content\n"
        result = inject_into_content(existing, "new")

        assert result is None

    def test_inject_only_end_marker_returns_none(self):
        existing = f"# My Project\nsome content\n{END_MARKER}\n"
        result = inject_into_content(existing, "new")

        assert result is None

    def test_inject_end_before_begin_returns_none(self):
        existing = f"{END_MARKER}\nsome content\n{BEGIN_MARKER}\n"
        result = inject_into_content(existing, "new")

        assert result is None

    def test_inject_preserves_surrounding_content(self):
        before = "line1\nline2\nline3"
        after = "line4\nline5\nline6"
        existing = f"{before}\n{BEGIN_MARKER}\nold\n{END_MARKER}\n{after}"
        result = inject_into_content(existing, "replaced")

        assert result is not None
        assert result.startswith(before)
        assert result.endswith(after)
        assert "replaced" in result

    def test_inject_markers_preserved_in_output(self):
        existing = f"{BEGIN_MARKER}\nold\n{END_MARKER}"
        result = inject_into_content(existing, "new")

        assert result is not None
        assert BEGIN_MARKER in result
        assert END_MARKER in result

    def test_render_to_directory_injects_into_existing_file(
        self, sample_pipeline: Pipeline, tmp_path: Path
    ):
        readme = tmp_path / "README.md"
        readme.write_text(
            f"# Existing Header\n"
            f"Keep this intro.\n"
            f"{BEGIN_MARKER}\n"
            f"old docs\n"
            f"{END_MARKER}\n"
            f"Keep this footer.\n"
        )

        renderer = TableRenderer()
        files = renderer.render_to_directory(sample_pipeline, tmp_path)

        content = readme.read_text()
        assert "# Existing Header" in content
        assert "Keep this intro." in content
        assert "Keep this footer." in content
        assert "old docs" not in content
        assert BEGIN_MARKER in content
        assert END_MARKER in content
        assert "## Inputs" in content
        assert len(files) == 1

    def test_render_to_directory_wraps_with_markers_new_file(
        self, sample_pipeline: Pipeline, tmp_path: Path
    ):
        renderer = TableRenderer()
        files = renderer.render_to_directory(sample_pipeline, tmp_path)

        content = (tmp_path / "README.md").read_text()
        assert content.startswith(BEGIN_MARKER)
        assert END_MARKER in content
        assert "## Inputs" in content
        assert len(files) == 1

    def test_render_to_directory_overwrites_file_without_markers(
        self, sample_pipeline: Pipeline, tmp_path: Path
    ):
        readme = tmp_path / "README.md"
        readme.write_text("# Old content without markers\n")

        renderer = TableRenderer()
        files = renderer.render_to_directory(sample_pipeline, tmp_path)

        content = readme.read_text()
        assert "# Old content without markers" not in content
        assert content.startswith(BEGIN_MARKER)
        assert END_MARKER in content
        assert "## Inputs" in content
        assert len(files) == 1


class TestTemplateRendering:
    """Tests for template-based selective section rendering."""

    def test_extract_template_with_tags(self):
        existing = (
            f"# Intro\n{BEGIN_MARKER}\n{{{{ inputs }}}}\n{{{{ config }}}}\n{END_MARKER}\nFooter\n"
        )
        result = extract_template(existing)

        assert result is not None
        assert "{{ inputs }}" in result
        assert "{{ config }}" in result

    def test_extract_template_no_tags_returns_none(self):
        existing = f"{BEGIN_MARKER}\njust some plain text\n{END_MARKER}\n"
        result = extract_template(existing)

        assert result is None

    def test_extract_template_no_markers_returns_none(self):
        result = extract_template("# No markers here")

        assert result is None

    def test_extract_template_empty_markers_returns_none(self):
        existing = f"{BEGIN_MARKER}\n{END_MARKER}"
        result = extract_template(existing)

        assert result is None

    def test_available_sections_complete(self):
        assert AVAILABLE_SECTIONS == {
            "header",
            "inputs",
            "config",
            "workflows",
            "processes",
            "functions",
        }

    def test_render_from_template_selective(self, sample_pipeline: Pipeline):
        renderer = TableRenderer()
        template = "\n{{ inputs }}\n"
        result = renderer.render_from_template(sample_pipeline, template)

        assert "## Inputs" in result
        assert "## Workflows" not in result
        assert "## Processes" not in result
        assert "## Functions" not in result
        assert "## Configuration" not in result

    def test_render_from_template_multiple_sections(self, sample_pipeline: Pipeline):
        renderer = TableRenderer()
        template = "\n{{ inputs }}\n\n{{ processes }}\n"
        result = renderer.render_from_template(sample_pipeline, template)

        assert "## Inputs" in result
        assert "## Processes" in result
        assert "## Workflows" not in result
        assert "## Functions" not in result

    def test_render_from_template_preserves_custom_text(self, sample_pipeline: Pipeline):
        renderer = TableRenderer()
        template = "\n## My Custom Section\n\nSome text.\n\n{{ inputs }}\n"
        result = renderer.render_from_template(sample_pipeline, template)

        assert "## My Custom Section" in result
        assert "Some text." in result
        assert "## Inputs" in result

    def test_render_from_template_unrecognised_tag_preserved(self, sample_pipeline: Pipeline):
        renderer = TableRenderer()
        template = "\n{{ inputs }}\n\n{{ unknown_tag }}\n"
        result = renderer.render_from_template(sample_pipeline, template)

        assert "## Inputs" in result
        assert "{{ unknown_tag }}" in result

    def test_render_from_template_case_insensitive(self, sample_pipeline: Pipeline):
        renderer = TableRenderer()
        template = "\n{{ INPUTS }}\n"
        result = renderer.render_from_template(sample_pipeline, template)

        assert "## Inputs" in result

    def test_render_from_template_whitespace_in_tag(self, sample_pipeline: Pipeline):
        renderer = TableRenderer()
        template = "\n{{  inputs  }}\n"
        result = renderer.render_from_template(sample_pipeline, template)

        assert "## Inputs" in result

    def test_render_to_directory_uses_template(self, sample_pipeline: Pipeline, tmp_path: Path):
        readme = tmp_path / "README.md"
        readme.write_text(
            f"# My Pipeline\n{BEGIN_MARKER}\n{{{{ inputs }}}}\n{END_MARKER}\nOther content.\n"
        )

        renderer = TableRenderer()
        renderer.render_to_directory(sample_pipeline, tmp_path)

        content = readme.read_text()
        assert "# My Pipeline" in content
        assert "Other content." in content
        assert "## Inputs" in content
        assert "## Workflows" not in content
        assert "## Processes" not in content
        assert BEGIN_MARKER in content
        assert END_MARKER in content

    def test_render_to_directory_empty_markers_renders_all(
        self, sample_pipeline: Pipeline, tmp_path: Path
    ):
        """Empty markers (no template tags) should render everything."""
        readme = tmp_path / "README.md"
        readme.write_text(f"# My Pipeline\n{BEGIN_MARKER}\n{END_MARKER}\nFooter.\n")

        renderer = TableRenderer()
        renderer.render_to_directory(sample_pipeline, tmp_path)

        content = readme.read_text()
        assert "## Inputs" in content
        assert "## Processes" in content
        assert "Footer." in content


class TestFormatRegistryConsistency:
    def test_renderers_and_output_policy_cover_the_same_formats(self):
        """
        Every renderable format needs an output policy, and vice versa.

        `output.py` is a leaf module, so `config.py` validates a config file's
        default_format against SINGLE_FILE_OUTPUT_POLICY rather than importing
        the renderers. That is only sound while the two agree.
        """
        assert set(RENDERERS) == set(SINGLE_FILE_OUTPUT_POLICY)

    def test_supported_formats_covers_every_renderer_and_alias(self):
        """The name list offered to users matches what get_renderer() accepts."""
        assert set(supported_formats()) == {*RENDERERS, *FORMAT_ALIASES}


def _renderer(output_format: str, **kwargs) -> BaseRenderer:
    """Build a renderer, keeping HTML off the Tailwind build for test speed."""
    if output_format == "html":
        kwargs.setdefault("use_tailwind", False)
    return RENDERERS[output_format](**kwargs)


class _AdvancingClock:
    """
    A ``datetime`` stand-in whose ``now()`` moves a second forward every call.

    Real runs of the test suite finish inside the same wall-clock second, so
    without this the timestamped output would compare equal by accident and the
    reproducibility tests would pass whatever ``include_generation_info`` did.
    """

    def __init__(self) -> None:
        self.calls = 0

    def now(self, tz=None) -> datetime:
        self.calls += 1
        return datetime(2024, 1, 1, 12, 0, 0, tzinfo=tz) + timedelta(seconds=self.calls)


@pytest.fixture
def advancing_clock(monkeypatch) -> _AdvancingClock:
    """Make every generation timestamp differ from the last one."""
    clock = _AdvancingClock()
    monkeypatch.setattr("nf_docs.generation_info.datetime", clock)
    return clock


class TestRenderPages:
    """Tests for render_pages(), the in-memory form of render_to_directory()."""

    def test_markdown_returns_a_page_per_file(self, sample_pipeline: Pipeline):
        pages = MarkdownRenderer().render_pages(sample_pipeline)

        # The sample pipeline has no config params and no functions, so those
        # two pages are absent - the key set depends on the pipeline.
        assert set(pages) == {"index.md", "inputs.md", "workflows.md", "processes.md"}
        assert pages["index.md"].startswith("# test-pipeline")
        assert "PROCESS_A" in pages["processes.md"]

    def test_markdown_omits_pages_with_no_content(self):
        pages = MarkdownRenderer().render_pages(Pipeline())

        assert set(pages) == {"index.md", "inputs.md"}

    def test_markdown_includes_optional_pages_when_populated(self, sample_pipeline: Pipeline):
        sample_pipeline.config_params = [ConfigParam(name="foo", type="string", default="bar")]
        sample_pipeline.functions = [Function(name="helper", docstring="A helper")]

        pages = MarkdownRenderer().render_pages(sample_pipeline)

        assert set(pages) == {
            "index.md",
            "inputs.md",
            "config.md",
            "workflows.md",
            "processes.md",
            "functions.md",
        }
        assert "foo" in pages["config.md"]
        assert "helper" in pages["functions.md"]

    def test_html_returns_index(self, sample_pipeline: Pipeline):
        pages = HTMLRenderer(use_tailwind=False).render_pages(sample_pipeline)

        assert set(pages) == {"index.html"}
        assert "<!doctype html>" in pages["index.html"].lower()

    def test_json_filename_follows_the_pipeline_name(self, sample_pipeline: Pipeline):
        pages = JSONRenderer().render_pages(sample_pipeline)

        assert set(pages) == {"test-pipeline-api.json"}
        assert json.loads(pages["test-pipeline-api.json"])["pipeline"]["name"] == "test-pipeline"

    def test_yaml_filename_follows_the_pipeline_name(self, sample_pipeline: Pipeline):
        pages = YAMLRenderer().render_pages(sample_pipeline)

        assert set(pages) == {"test-pipeline-api.yaml"}
        assert (
            yaml.safe_load(pages["test-pipeline-api.yaml"])["pipeline"]["name"] == "test-pipeline"
        )

    def test_data_filenames_sanitise_the_pipeline_name(self):
        pipeline = Pipeline(metadata=PipelineMetadata(name="nf-core/rnaseq"))

        assert set(JSONRenderer().render_pages(pipeline)) == {"nf-core_rnaseq-api.json"}

    def test_data_filenames_fall_back_when_unnamed(self):
        assert set(YAMLRenderer().render_pages(Pipeline())) == {"pipeline-api.yaml"}

    def test_table_wraps_in_markers(self, sample_pipeline: Pipeline):
        pages = TableRenderer().render_pages(sample_pipeline)

        assert set(pages) == {"README.md"}
        assert pages["README.md"].startswith(BEGIN_MARKER)
        assert pages["README.md"].rstrip().endswith(END_MARKER)

    @pytest.mark.parametrize("output_format", sorted(RENDERERS))
    def test_pages_are_exactly_what_render_to_directory_writes(
        self, sample_pipeline: Pipeline, tmp_path: Path, output_format: str
    ):
        """
        The whole point of render_pages(): consumers should be able to drop the
        write-to-a-temp-dir-and-read-it-back round trip without changing what
        they get. Generation info is off so the two calls can't disagree on the
        timestamp.
        """
        renderer = _renderer(output_format, include_generation_info=False)

        pages = renderer.render_pages(sample_pipeline)
        files = renderer.render_to_directory(sample_pipeline, tmp_path)

        assert [f.name for f in files] == list(pages)
        for file_path in files:
            assert file_path.read_text(encoding="utf-8") == pages[file_path.name]

    def test_table_directory_output_diverges_when_injecting(
        self, sample_pipeline: Pipeline, tmp_path: Path
    ):
        """
        The documented exception: injecting into an existing README depends on
        what is already on disk, so render_pages() can't express it.
        """
        readme = tmp_path / "README.md"
        readme.write_text(f"# Kept heading\n\n{BEGIN_MARKER}\n{END_MARKER}\n", encoding="utf-8")
        renderer = TableRenderer(include_generation_info=False)

        renderer.render_to_directory(sample_pipeline, tmp_path)

        written = readme.read_text(encoding="utf-8")
        assert "# Kept heading" in written
        assert written != renderer.render_pages(sample_pipeline)["README.md"]


class TestReproducibleOutput:
    """``include_generation_info=False`` must make output byte-identical."""

    @pytest.mark.parametrize("output_format", sorted(RENDERERS))
    def test_render_is_byte_identical(
        self, sample_pipeline: Pipeline, output_format: str, advancing_clock: _AdvancingClock
    ):
        first = _renderer(output_format, include_generation_info=False).render(sample_pipeline)
        second = _renderer(output_format, include_generation_info=False).render(sample_pipeline)

        assert first.encode("utf-8") == second.encode("utf-8")

    @pytest.mark.parametrize("output_format", sorted(RENDERERS))
    def test_render_pages_is_byte_identical(
        self, sample_pipeline: Pipeline, output_format: str, advancing_clock: _AdvancingClock
    ):
        first = _renderer(output_format, include_generation_info=False).render_pages(
            sample_pipeline
        )
        second = _renderer(output_format, include_generation_info=False).render_pages(
            sample_pipeline
        )

        assert {k: v.encode("utf-8") for k, v in first.items()} == {
            k: v.encode("utf-8") for k, v in second.items()
        }

    @pytest.mark.parametrize("output_format", ["markdown", "table", "json", "html"])
    def test_default_output_varies_between_runs(
        self, sample_pipeline: Pipeline, output_format: str, advancing_clock: _AdvancingClock
    ):
        """The guard for the tests above: without the flag, output does change."""
        first = _renderer(output_format).render(sample_pipeline)
        second = _renderer(output_format).render(sample_pipeline)

        assert first != second

    def test_yaml_is_reproducible_either_way(
        self, sample_pipeline: Pipeline, advancing_clock: _AdvancingClock
    ):
        """YAML embeds no generation metadata, so the flag is a no-op for it."""
        assert YAMLRenderer().render(sample_pipeline) == YAMLRenderer(
            include_generation_info=False
        ).render(sample_pipeline)

    def test_markdown_drops_the_footer(self, sample_pipeline: Pipeline):
        output = MarkdownRenderer(include_generation_info=False).render(sample_pipeline)

        assert "Documentation generated by" not in output
        # The documentation itself is untouched
        assert "PROCESS_A" in output

    def test_markdown_pages_drop_the_footer(self, sample_pipeline: Pipeline):
        pages = MarkdownRenderer(include_generation_info=False).render_pages(sample_pipeline)

        assert all("Documentation generated by" not in page for page in pages.values())

    def test_table_drops_the_footer(self, sample_pipeline: Pipeline):
        output = TableRenderer(include_generation_info=False).render(sample_pipeline)

        assert "Documentation generated by" not in output
        assert "## Processes" in output

    def test_table_template_output_drops_the_footer(self, sample_pipeline: Pipeline):
        output = TableRenderer(include_generation_info=False).render_from_template(
            sample_pipeline, "{{ header }}\n\n{{ processes }}"
        )

        assert "Documentation generated by" not in output
        assert "## Processes" in output

    def test_json_drops_the_generated_by_key(self, sample_pipeline: Pipeline):
        data = json.loads(JSONRenderer(include_generation_info=False).render(sample_pipeline))

        assert "generated_by" not in data
        assert data["pipeline"]["name"] == "test-pipeline"

    def test_json_keeps_the_generated_by_key_by_default(self, sample_pipeline: Pipeline):
        data = json.loads(JSONRenderer().render(sample_pipeline))

        assert "generated_at" in data["generated_by"]

    def test_html_drops_only_the_timestamp(self, sample_pipeline: Pipeline):
        output = HTMLRenderer(use_tailwind=False, include_generation_info=False).render(
            sample_pipeline
        )

        # The timestamp is the only part that moves between runs
        assert " UTC" not in output
        # The attribution and the version are the same every run, so they stay
        assert "Documentation generated by" in output
        assert f"v{nf_docs.__version__}" in output
        assert "built with" in output
        assert "https://nextflow.io" in output

    def test_html_keeps_the_timestamp_by_default(self, sample_pipeline: Pipeline):
        output = HTMLRenderer(use_tailwind=False).render(sample_pipeline)

        assert "Documentation generated by" in output
        assert " UTC" in output

    def test_generation_info_is_on_by_default(self):
        assert MarkdownRenderer().include_generation_info is True
        assert JSONRenderer().include_generation_info is True
        assert HTMLRenderer(use_tailwind=False).include_generation_info is True
        assert YAMLRenderer().include_generation_info is True
        assert TableRenderer().include_generation_info is True

    def test_flag_composes_with_other_renderer_options(self, sample_pipeline: Pipeline):
        """It's keyword-only, so it can't collide with the positional options."""
        renderer = JSONRenderer("Custom Title", 4, include_generation_info=False)
        output = renderer.render(sample_pipeline)

        assert json.loads(output)["pipeline"]["name"] == "Custom Title"
        assert "generated_by" not in output
        assert '\n    "pipeline"' in output
