"""Tests for the CLI interface."""

from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from nf_docs.cli import generate, inspect, main
from nf_docs.extractor import PipelineExtractor


@pytest.fixture
def runner():
    """Create a CLI runner."""
    return CliRunner()


class TestMainCommand:
    def test_help(self, runner: CliRunner):
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Generate API documentation" in result.output

    def test_version(self, runner: CliRunner):
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "nf-docs" in result.output


class TestGenerateCommand:
    def test_generate_help(self, runner: CliRunner):
        result = runner.invoke(generate, ["--help"])
        assert result.exit_code == 0
        assert "Generate documentation" in result.output

    def test_generate_json(self, runner: CliRunner, sample_pipeline: Path):
        with patch.object(PipelineExtractor, "_extract_from_lsp"):
            result = runner.invoke(generate, [str(sample_pipeline), "--format", "json"])
        assert result.exit_code == 0
        # Output should be JSON
        assert '"pipeline"' in result.output

    def test_generate_yaml(self, runner: CliRunner, sample_pipeline: Path):
        with patch.object(PipelineExtractor, "_extract_from_lsp"):
            result = runner.invoke(generate, [str(sample_pipeline), "--format", "yaml"])
        assert result.exit_code == 0
        # Output should be YAML
        assert "pipeline:" in result.output

    def test_generate_markdown_to_directory(
        self, runner: CliRunner, sample_pipeline: Path, tmp_path: Path
    ):
        output_dir = tmp_path / "docs"
        with patch.object(PipelineExtractor, "_extract_from_lsp"):
            result = runner.invoke(
                generate,
                [str(sample_pipeline), "--format", "markdown", "--output", str(output_dir)],
            )
        assert result.exit_code == 0
        assert output_dir.exists()
        assert (output_dir / "index.md").exists()

    def test_generate_html_to_directory(
        self, runner: CliRunner, sample_pipeline: Path, tmp_path: Path
    ):
        output_dir = tmp_path / "site"
        with patch.object(PipelineExtractor, "_extract_from_lsp"):
            result = runner.invoke(
                generate,
                [str(sample_pipeline), "--format", "html", "--output", str(output_dir)],
            )
        assert result.exit_code == 0
        assert output_dir.exists()
        assert (output_dir / "index.html").exists()

    def test_generate_with_custom_title(self, runner: CliRunner, sample_pipeline: Path):
        with patch.object(PipelineExtractor, "_extract_from_lsp"):
            result = runner.invoke(
                generate,
                [str(sample_pipeline), "--format", "json", "--title", "My Custom Title"],
            )
        assert result.exit_code == 0
        assert "My Custom Title" in result.output

    def test_generate_nonexistent_path(self, runner: CliRunner):
        result = runner.invoke(generate, ["/nonexistent/path", "--format", "json"])
        assert result.exit_code != 0

    def test_generate_verbose(self, runner: CliRunner, sample_pipeline: Path):
        with patch.object(PipelineExtractor, "_extract_from_lsp"):
            result = runner.invoke(
                generate,
                [str(sample_pipeline), "--format", "json", "--verbose"],
            )
        assert result.exit_code == 0


class TestGenerateSingleFile:
    """Tests for single-file generation mode (issue #5)."""

    @pytest.fixture
    def single_nf_file(self, tmp_path: Path) -> Path:
        """A module-style .nf file inside a tiny "pipeline" workspace."""
        (tmp_path / "nextflow.config").write_text("")
        module_dir = tmp_path / "modules" / "fastqc"
        module_dir.mkdir(parents=True)
        nf_file = module_dir / "main.nf"
        nf_file.write_text("process FASTQC {\n  script:\n  '''\n  fastqc\n  '''\n}\n")
        return nf_file

    @staticmethod
    def _fake_lsp(populate_with):
        """Build an _extract_from_lsp replacement that injects fake content."""

        def _inner(self, pipeline, git_info=None):
            for item in populate_with(self):
                pipeline.processes.append(item)

        return _inner

    @staticmethod
    def _static_process():
        from nf_docs.models import Process

        return [
            Process(
                name="FASTQC",
                docstring="Run FastQC",
                file="modules/fastqc/main.nf",
                line=1,
            )
        ]

    def test_markdown_writes_sibling_readme(self, runner: CliRunner, single_nf_file: Path):
        with patch.object(
            PipelineExtractor,
            "_extract_from_lsp",
            self._fake_lsp(lambda self: TestGenerateSingleFile._static_process()),
        ):
            result = runner.invoke(generate, [str(single_nf_file), "--format", "md"])
        assert result.exit_code == 0, result.output
        readme = single_nf_file.parent / "README.md"
        assert readme.exists()
        text = readme.read_text()
        assert "FASTQC" in text
        # Module-focused: no pipeline-level wrappers
        assert "# Processes" not in text
        assert "# Pipeline Inputs" not in text

    def test_markdown_with_output_flag(
        self, runner: CliRunner, single_nf_file: Path, tmp_path: Path
    ):
        out_path = tmp_path / "custom.md"
        with patch.object(
            PipelineExtractor,
            "_extract_from_lsp",
            self._fake_lsp(lambda self: TestGenerateSingleFile._static_process()),
        ):
            result = runner.invoke(
                generate,
                [str(single_nf_file), "--format", "md", "--output", str(out_path)],
            )
        assert result.exit_code == 0, result.output
        assert out_path.exists()
        # Sibling README should NOT have been written when -o was specified
        assert not (single_nf_file.parent / "README.md").exists()

    def test_json_to_stdout(self, runner: CliRunner, single_nf_file: Path):
        with patch.object(
            PipelineExtractor,
            "_extract_from_lsp",
            self._fake_lsp(lambda self: TestGenerateSingleFile._static_process()),
        ):
            result = runner.invoke(generate, [str(single_nf_file), "--format", "json"])
        assert result.exit_code == 0, result.output
        assert '"FASTQC"' in result.output
        # No sibling files created
        assert not (single_nf_file.parent / "README.md").exists()

    def test_rejects_non_nf_file(self, runner: CliRunner, tmp_path: Path):
        bad = tmp_path / "not_nextflow.txt"
        bad.write_text("hi")
        result = runner.invoke(generate, [str(bad), "--format", "md"])
        assert result.exit_code != 0
        assert ".nf" in result.output

    def test_auto_detects_module_directory(self, runner: CliRunner, tmp_path: Path):
        """Pointing at a module directory (main.nf + no pipeline config) auto-switches."""
        module_dir = tmp_path / "fastqc"
        module_dir.mkdir()
        (module_dir / "main.nf").write_text("process FASTQC {\n  script:\n  ''' '''\n}\n")
        # NB: no meta.yml, no nextflow.config — the heuristic should still fire.

        with patch.object(
            PipelineExtractor,
            "_extract_from_lsp",
            self._fake_lsp(lambda self: TestGenerateSingleFile._static_process()),
        ):
            result = runner.invoke(generate, [str(module_dir), "--format", "md"])
        assert result.exit_code == 0, result.output
        # Sibling README written next to main.nf — proves single-file mode
        assert (module_dir / "README.md").exists()
        # And the multi-file docs/ dir was NOT created
        assert not (module_dir / "docs").exists()

    def test_skips_auto_detect_for_pipeline_directory(self, runner: CliRunner, tmp_path: Path):
        """A directory with nextflow.config keeps the multi-file directory mode."""
        (tmp_path / "main.nf").write_text("workflow { }\n")
        (tmp_path / "nextflow.config").write_text("")

        with patch.object(
            PipelineExtractor,
            "_extract_from_lsp",
            self._fake_lsp(lambda self: TestGenerateSingleFile._static_process()),
        ):
            result = runner.invoke(
                generate,
                [str(tmp_path), "--format", "md", "--output", str(tmp_path / "docs")],
            )
        assert result.exit_code == 0, result.output
        # Multi-file output: index.md is created
        assert (tmp_path / "docs" / "index.md").exists()
        assert "Generating single module documentation" not in result.output

    def test_skips_auto_detect_when_main_nf_has_workflow(self, runner: CliRunner, tmp_path: Path):
        """main.nf with a workflow block is not auto-treated as a single module."""
        (tmp_path / "main.nf").write_text("workflow { }\n")
        # No nextflow.config, but the workflow block disqualifies the module heuristic.

        with patch.object(
            PipelineExtractor,
            "_extract_from_lsp",
            self._fake_lsp(lambda self: TestGenerateSingleFile._static_process()),
        ):
            result = runner.invoke(
                generate,
                [str(tmp_path), "--format", "md", "--output", str(tmp_path / "docs")],
            )
        assert result.exit_code == 0, result.output
        # Falls through to directory mode → multi-file output
        assert (tmp_path / "docs" / "index.md").exists()
        assert "Generating single module documentation" not in result.output


class TestInspectCommand:
    def test_inspect_help(self, runner: CliRunner):
        result = runner.invoke(inspect, ["--help"])
        assert result.exit_code == 0
        assert "Inspect" in result.output

    def test_inspect_pipeline(self, runner: CliRunner, sample_pipeline: Path):
        with patch.object(PipelineExtractor, "_extract_from_lsp"):
            result = runner.invoke(inspect, [str(sample_pipeline)])
        assert result.exit_code == 0
        # Should show summary
        assert "Pipeline:" in result.output

    def test_inspect_empty_directory(self, runner: CliRunner, tmp_path: Path):
        with patch.object(PipelineExtractor, "_extract_from_lsp"):
            result = runner.invoke(inspect, [str(tmp_path)])
        assert result.exit_code == 0

    def test_inspect_verbose(self, runner: CliRunner, sample_pipeline: Path):
        with patch.object(PipelineExtractor, "_extract_from_lsp"):
            result = runner.invoke(inspect, [str(sample_pipeline), "--verbose"])
        assert result.exit_code == 0
