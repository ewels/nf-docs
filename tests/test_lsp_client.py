"""Tests for the Nextflow Language Server client."""

from nf_docs.lsp_client import DEFAULT_LSP_EXCLUDES, build_exclude_list


class TestBuildExcludeList:
    """Tests for build_exclude_list."""

    def test_defaults_when_nothing_configured(self):
        """With no user patterns we send exactly the built-in exclusions."""
        assert build_exclude_list() == DEFAULT_LSP_EXCLUDES
        assert build_exclude_list([]) == DEFAULT_LSP_EXCLUDES

    def test_user_patterns_are_appended(self):
        """User patterns are added to the built-ins rather than replacing them."""
        result = build_exclude_list(["testdata", "examples"])

        assert result[: len(DEFAULT_LSP_EXCLUDES)] == DEFAULT_LSP_EXCLUDES
        assert result[len(DEFAULT_LSP_EXCLUDES) :] == ["testdata", "examples"]

    def test_duplicates_are_dropped(self):
        """Repeating a built-in doesn't duplicate it."""
        result = build_exclude_list(["work", "testdata", "testdata"])

        assert result.count("work") == 1
        assert result.count("testdata") == 1

    def test_never_empty(self):
        """
        The list must stay non-empty.

        The language server only initialises a workspace when the configuration
        it receives differs from its defaults, so an empty exclude list means no
        indexing at all.
        """
        assert build_exclude_list([]) != []
        assert build_exclude_list([""]) != []
