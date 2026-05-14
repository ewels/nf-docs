"""Tests for the pre-commit hook manifest."""

import re
from pathlib import Path

import yaml


class TestPreCommitHooks:
    """Tests for .pre-commit-hooks.yaml."""

    def test_nf_docs_hook_defaults(self):
        """Test that the nf-docs hook runs the CLI against the repository root."""
        hooks = yaml.safe_load(Path(".pre-commit-hooks.yaml").read_text())

        nf_docs_hook = next(hook for hook in hooks if hook["id"] == "nf-docs")

        assert nf_docs_hook["entry"] == "nf-docs generate"
        assert nf_docs_hook["args"] == [".", "--format", "html"]
        assert nf_docs_hook["pass_filenames"] is False
        assert "nextflow_schema\\.json" in nf_docs_hook["files"]

    def test_nf_docs_hook_file_triggers(self):
        """Test that the nf-docs hook runs for documentation source inputs."""
        hooks = yaml.safe_load(Path(".pre-commit-hooks.yaml").read_text())
        nf_docs_hook = next(hook for hook in hooks if hook["id"] == "nf-docs")
        files_pattern = re.compile(nf_docs_hook["files"])

        assert files_pattern.search("main.nf")
        assert files_pattern.search("modules/fastqc/meta.yml")
        assert files_pattern.search("nextflow_schema.json")
        assert files_pattern.search("README.rst")
        assert not files_pattern.search("docs/index.html")
