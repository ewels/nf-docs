"""
Configuration management for nf-docs.

Loads user configuration from XDG_CONFIG_HOME/nf-docs/config.yaml
(default: ~/.config/nf-docs/config.yaml).

The configuration file is optional - nf-docs works with sensible defaults
if no config file exists.
"""

import hashlib
import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

# Default configuration values
DEFAULT_CONFIG: dict[str, Any] = {
    # Prefixes for config parameters to ignore (e.g., "genomes." for nf-core)
    "ignore_config_prefixes": ["genomes."],
    # Prefixes for config parameters to ignore in inputs
    "ignore_input_prefixes": [],
    # Whether to include hidden parameters in documentation
    "include_hidden_params": False,
    # Default output format
    "default_format": "html",
    # Maximum README length (in characters) to include. 0 = no limit
    "max_readme_length": 0,
    # Whether to strip badge lines from the top of README files
    "strip_readme_badges": True,
    # Patterns for files to exclude from LSP analysis
    "exclude_patterns": [],
}


def get_xdg_config_home() -> Path:
    """Get the XDG config directory."""
    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config:
        return Path(xdg_config)
    return Path.home() / ".config"


def get_config_path() -> Path:
    """Get the path to the nf-docs config file."""
    return get_xdg_config_home() / "nf-docs" / "config.yaml"


@dataclass
class NfDocsConfig:
    """
    Configuration for nf-docs.

    Attributes:
        ignore_config_prefixes: List of prefixes for config parameters to ignore.
            Parameters starting with any of these prefixes will be excluded from
            the Configuration section. Default: ["genomes."] (for nf-core pipelines).
        ignore_input_prefixes: List of prefixes for input parameters to ignore.
            Parameters starting with any of these prefixes will be excluded from
            the Parameters section. Default: [].
        include_hidden_params: Whether to include parameters marked as hidden
            in the nextflow_schema.json. Default: False.
        default_format: Default output format when not specified. Default: "html".
        max_readme_length: Maximum README content length to include (0 = no limit).
            Default: 0.
        strip_readme_badges: Whether to strip badge lines (images/links at the top)
            from README files. Default: True.
        exclude_patterns: Glob patterns for files to exclude from LSP analysis.
            Default: [].
    """

    ignore_config_prefixes: list[str] = field(default_factory=lambda: ["genomes."])
    ignore_input_prefixes: list[str] = field(default_factory=list)
    include_hidden_params: bool = False
    default_format: str = "html"
    max_readme_length: int = 0
    strip_readme_badges: bool = True
    exclude_patterns: list[str] = field(default_factory=list)

    def should_ignore_config_param(self, param_name: str) -> bool:
        """Check if a config parameter should be ignored based on its name."""
        for prefix in self.ignore_config_prefixes:
            if param_name.startswith(prefix):
                return True
        return False

    def should_ignore_input_param(self, param_name: str) -> bool:
        """Check if an input parameter should be ignored based on its name."""
        for prefix in self.ignore_input_prefixes:
            if param_name.startswith(prefix):
                return True
        return False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "NfDocsConfig":
        """Create a config from a dictionary, using defaults for missing values."""
        return cls(
            ignore_config_prefixes=data.get(
                "ignore_config_prefixes", DEFAULT_CONFIG["ignore_config_prefixes"]
            ),
            ignore_input_prefixes=data.get(
                "ignore_input_prefixes", DEFAULT_CONFIG["ignore_input_prefixes"]
            ),
            include_hidden_params=data.get(
                "include_hidden_params", DEFAULT_CONFIG["include_hidden_params"]
            ),
            default_format=data.get("default_format", DEFAULT_CONFIG["default_format"]),
            max_readme_length=data.get("max_readme_length", DEFAULT_CONFIG["max_readme_length"]),
            strip_readme_badges=data.get(
                "strip_readme_badges", DEFAULT_CONFIG["strip_readme_badges"]
            ),
            exclude_patterns=data.get("exclude_patterns", DEFAULT_CONFIG["exclude_patterns"]),
        )

    def cache_key(self) -> str:
        """
        Stable short hash of this configuration.

        Extraction results depend on the config in use, so the cache key has to
        include it. Without this, a CLI run (which loads the user's config file)
        and a library call (which uses defaults) would share a cache entry on
        the same unchanged pipeline and return each other's results.

        Returns:
            A hex digest suitable for use in a cache filename.
        """
        payload = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    def to_dict(self) -> dict[str, Any]:
        """Convert config to a dictionary."""
        return {
            "ignore_config_prefixes": self.ignore_config_prefixes,
            "ignore_input_prefixes": self.ignore_input_prefixes,
            "include_hidden_params": self.include_hidden_params,
            "default_format": self.default_format,
            "max_readme_length": self.max_readme_length,
            "strip_readme_badges": self.strip_readme_badges,
            "exclude_patterns": self.exclude_patterns,
        }


def load_config(config_path: Path | None = None) -> NfDocsConfig:
    """
    Load configuration from file.

    Args:
        config_path: Optional custom path to config file. If not provided,
            uses the default XDG config path.

    Returns:
        NfDocsConfig with values from file or defaults if file doesn't exist.
    """
    if config_path is None:
        config_path = get_config_path()

    if not config_path.exists():
        logger.debug(f"No config file at {config_path}, using defaults")
        return NfDocsConfig()

    try:
        with open(config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        if not isinstance(data, dict):
            # Valid YAML, wrong shape (e.g. a top-level list). Treat it the same
            # as unparseable rather than letting an AttributeError escape.
            logger.warning(
                f"Config file {config_path} must contain a mapping of settings, "
                f"got {type(data).__name__}. Using defaults."
            )
            return NfDocsConfig()

        logger.debug(f"Loaded config from {config_path}")
        return NfDocsConfig.from_dict(data)

    except yaml.YAMLError as e:
        logger.warning(f"Invalid YAML in config file {config_path}: {e}")
        return NfDocsConfig()
    except OSError as e:
        logger.warning(f"Failed to read config from {config_path}: {e}")
        return NfDocsConfig()


def get_example_config() -> str:
    """
    Get an example configuration file with comments.

    Returns:
        YAML string with example configuration and documentation.
    """
    return """\
# nf-docs configuration file
# Location: ~/.config/nf-docs/config.yaml (or $XDG_CONFIG_HOME/nf-docs/config.yaml)
#
# All settings are optional - nf-docs uses sensible defaults if this file
# doesn't exist or if specific settings are omitted.

# Prefixes for configuration parameters to ignore in the "Configuration" section.
# Parameters starting with any of these prefixes will be excluded.
# This is useful for nf-core pipelines which have many "genomes." parameters
# that are typically not relevant for end-user documentation.
# Default: ["genomes."]
ignore_config_prefixes:
  - "genomes."

# Prefixes for input parameters to ignore in the "Parameters" section.
# Parameters starting with any of these prefixes will be excluded.
# Default: []
ignore_input_prefixes: []

# Whether to include parameters marked as "hidden" in nextflow_schema.json.
# Hidden parameters are typically advanced options not needed by most users.
# Default: false
include_hidden_params: false

# Default output format when -f/--format is not specified.
# Options: html, json, yaml, markdown, md
# Default: html
default_format: html

# Maximum length of README content to include (in characters).
# Set to 0 for no limit.
# Default: 0
max_readme_length: 0

# Whether to strip badge lines from the top of README files.
# Badges are typically image links ([![...], ![...]) that appear after the title.
# Set to false to include badges in the documentation.
# Default: true
strip_readme_badges: true

# Glob patterns for files to exclude from LSP analysis.
# Useful for excluding test files, examples, etc.
# Default: []
exclude_patterns: []
#  - "tests/**/*.nf"
#  - "examples/**/*.nf"
"""
