"""Tests for the configuration system."""

from pathlib import Path

import pytest

from nf_docs.config import (
    DEFAULT_CONFIG,
    NfDocsConfig,
    get_config_path,
    get_example_config,
    get_xdg_config_home,
    load_config,
)


class TestGetXdgConfigHome:
    """Tests for get_xdg_config_home function."""

    def test_default_config_home(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test default config home when XDG_CONFIG_HOME is not set."""
        monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
        result = get_xdg_config_home()
        assert result == Path.home() / ".config"

    def test_custom_config_home(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        """Test custom config home from XDG_CONFIG_HOME."""
        custom_config = tmp_path / "custom_config"
        monkeypatch.setenv("XDG_CONFIG_HOME", str(custom_config))
        result = get_xdg_config_home()
        assert result == custom_config


class TestGetConfigPath:
    """Tests for get_config_path function."""

    def test_config_path(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        """Test config path construction."""
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
        result = get_config_path()
        assert result == tmp_path / "nf-docs" / "config.yaml"


class TestNfDocsConfig:
    """Tests for NfDocsConfig class."""

    def test_default_values(self) -> None:
        """Test that default values are set correctly."""
        config = NfDocsConfig()
        assert config.ignore_config_prefixes == ["genomes."]
        assert config.ignore_input_prefixes == []
        assert config.include_hidden_params is True
        assert config.default_format == "html"
        assert config.max_readme_length == 0
        assert config.strip_readme_badges is True
        assert config.exclude_patterns == []

    def test_should_ignore_config_param(self) -> None:
        """Test should_ignore_config_param method."""
        config = NfDocsConfig(ignore_config_prefixes=["genomes.", "test."])

        # Should ignore
        assert config.should_ignore_config_param("genomes.hg38") is True
        assert config.should_ignore_config_param("genomes.") is True
        assert config.should_ignore_config_param("test.foo") is True

        # Should not ignore
        assert config.should_ignore_config_param("input") is False
        assert config.should_ignore_config_param("outdir") is False
        assert config.should_ignore_config_param("genome") is False  # No dot

    def test_should_ignore_input_param(self) -> None:
        """Test should_ignore_input_param method."""
        config = NfDocsConfig(ignore_input_prefixes=["internal.", "debug."])

        # Should ignore
        assert config.should_ignore_input_param("internal.setting") is True
        assert config.should_ignore_input_param("debug.verbose") is True

        # Should not ignore
        assert config.should_ignore_input_param("input") is False
        assert config.should_ignore_input_param("internal") is False  # No dot

    def test_from_dict_full(self) -> None:
        """Test from_dict with all values specified."""
        data = {
            "ignore_config_prefixes": ["custom."],
            "ignore_input_prefixes": ["private."],
            "include_hidden_params": False,
            "default_format": "json",
            "max_readme_length": 5000,
            "strip_readme_badges": False,
            "exclude_patterns": ["tests/**/*.nf"],
        }
        config = NfDocsConfig.from_dict(data)

        assert config.ignore_config_prefixes == ["custom."]
        assert config.ignore_input_prefixes == ["private."]
        assert config.include_hidden_params is False
        assert config.default_format == "json"
        assert config.max_readme_length == 5000
        assert config.strip_readme_badges is False
        assert config.exclude_patterns == ["tests/**/*.nf"]

    def test_from_dict_partial(self) -> None:
        """Test from_dict with only some values specified."""
        data = {
            "include_hidden_params": False,
            "default_format": "yaml",
        }
        config = NfDocsConfig.from_dict(data)

        # Specified values
        assert config.include_hidden_params is False
        assert config.default_format == "yaml"

        # Default values
        assert config.ignore_config_prefixes == DEFAULT_CONFIG["ignore_config_prefixes"]

    def test_from_dict_empty(self) -> None:
        """Test from_dict with empty dict uses all defaults."""
        config = NfDocsConfig.from_dict({})

        assert config.ignore_config_prefixes == DEFAULT_CONFIG["ignore_config_prefixes"]
        assert config.include_hidden_params == DEFAULT_CONFIG["include_hidden_params"]
        assert config.default_format == DEFAULT_CONFIG["default_format"]

    def test_to_dict(self) -> None:
        """Test to_dict conversion."""
        config = NfDocsConfig(
            ignore_config_prefixes=["foo."],
            include_hidden_params=False,
            default_format="markdown",
        )
        result = config.to_dict()

        assert result["ignore_config_prefixes"] == ["foo."]
        assert result["include_hidden_params"] is False
        assert result["default_format"] == "markdown"
        assert "ignore_input_prefixes" in result
        assert "max_readme_length" in result
        assert "strip_readme_badges" in result
        assert "exclude_patterns" in result


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_default_when_file_missing(self, tmp_path: Path) -> None:
        """Test that defaults are used when config file doesn't exist."""
        config = load_config(tmp_path / "nonexistent" / "config.yaml")

        assert config.ignore_config_prefixes == ["genomes."]
        assert config.include_hidden_params is True

    @pytest.mark.parametrize(
        "contents",
        ["- ignore_config_prefixes\n- genomes.\n", "just a string\n", "42\n"],
        ids=["list", "string", "number"],
    )
    def test_load_default_when_yaml_is_not_a_mapping(self, tmp_path: Path, contents: str) -> None:
        """Valid YAML of the wrong shape falls back to defaults, it doesn't raise."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(contents)

        config = load_config(config_file)

        assert config == NfDocsConfig()

    def test_load_from_file(self, tmp_path: Path) -> None:
        """Test loading config from a valid YAML file."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            """\
ignore_config_prefixes:
  - "custom."
  - "other."
include_hidden_params: false
default_format: json
"""
        )

        config = load_config(config_file)

        assert config.ignore_config_prefixes == ["custom.", "other."]
        assert config.include_hidden_params is False
        assert config.default_format == "json"
        # Non-specified values should use defaults
        assert config.strip_readme_badges is True

    def test_load_empty_file(self, tmp_path: Path) -> None:
        """Test loading config from an empty YAML file."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("")

        config = load_config(config_file)

        # Should use all defaults
        assert config.ignore_config_prefixes == ["genomes."]
        assert config.include_hidden_params is True

    def test_load_invalid_yaml(self, tmp_path: Path) -> None:
        """Test that invalid YAML returns defaults with warning."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("invalid: yaml: content: [[[")

        config = load_config(config_file)

        # Should use defaults on error
        assert config.ignore_config_prefixes == ["genomes."]
        assert config.include_hidden_params is True


class TestGetExampleConfig:
    """Tests for get_example_config function."""

    def test_returns_valid_yaml(self) -> None:
        """Test that example config is valid YAML."""
        import yaml

        example = get_example_config()
        data = yaml.safe_load(example)

        assert isinstance(data, dict)
        assert "ignore_config_prefixes" in data
        assert "include_hidden_params" in data
        assert "default_format" in data

    def test_contains_comments(self) -> None:
        """Test that example config contains helpful comments."""
        example = get_example_config()

        assert "# nf-docs configuration file" in example
        assert "# Default:" in example
        assert "~/.config/nf-docs/config.yaml" in example

    def test_documents_all_options(self) -> None:
        """Test that example config documents all available options."""
        example = get_example_config()

        for key in DEFAULT_CONFIG.keys():
            assert key in example, f"Option '{key}' not documented in example config"
