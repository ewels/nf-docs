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
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from nf_docs.output import is_supported_format, supported_formats

logger = logging.getLogger(__name__)

# Default configuration values
DEFAULT_CONFIG: dict[str, Any] = {
    # Prefixes for config parameters to ignore (e.g., "genomes." for nf-core)
    "ignore_config_prefixes": ["genomes."],
    # Prefixes for config parameters to ignore in inputs
    "ignore_input_prefixes": [],
    # Whether to include hidden parameters in documentation
    "include_hidden_params": True,
    # Default output format for the CLI
    "default_format": "html",
    # Maximum README length (in characters) to include. 0 = no limit
    "max_readme_length": 0,
    # Whether to strip badge lines from the top of README files
    "strip_readme_badges": True,
    # Extra paths for the Language Server to skip when indexing the workspace
    "exclude_patterns": [],
}

# Expected shape of each option, derived from the default it ships with so the
# two can't drift. ``list`` means "list of strings". An option defaulting to
# None would need stating explicitly here; none currently does.
_FIELD_TYPES: dict[str, type] = {key: type(value) for key, value in DEFAULT_CONFIG.items()}

# Options that don't affect extraction, and so stay out of the cache key.
_CLI_ONLY_FIELDS = frozenset({"default_format"})

# Options whose value has to be one of a known set, beyond just having the right
# type, paired with what to tell the user when it isn't. Checked in from_dict so
# every option is validated in one place.
_FIELD_VALUE_CHECKS: dict[str, tuple[Callable[[Any], bool], str]] = {
    "default_format": (is_supported_format, f"one of {', '.join(supported_formats())}"),
}


def _requirement(key: str) -> str:
    """Describe what an option accepts, completing "should be ..." in a warning."""
    if key in _FIELD_VALUE_CHECKS:
        return _FIELD_VALUE_CHECKS[key][1]
    return "a list of strings" if _FIELD_TYPES[key] is list else _FIELD_TYPES[key].__name__


def _is_valid(key: str, value: Any) -> bool:
    """
    Check a config value against the type, and domain, its option expects.

    Every option is consulted during extraction or by the CLI, so a bad value
    would otherwise reach real code and fail there instead of at the boundary.
    """
    expected = _FIELD_TYPES[key]
    if expected is list:
        if not (isinstance(value, list) and all(isinstance(item, str) for item in value)):
            return False
    elif expected is int and isinstance(value, bool):
        return False  # bool subclasses int, but `max_readme_length: true` is a mistake
    elif not isinstance(value, expected):
        return False
    check = _FIELD_VALUE_CHECKS.get(key)
    return check[0](value) if check else True


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
            in the nextflow_schema.json. Default: True.
        default_format: Default output format for the ``nf-docs generate`` command
            when ``-f/--format`` is not given. Only the CLI reads this; the Python
            API takes its format as an argument. Default: "html".
        max_readme_length: Maximum length of README *source text* to include, in
            characters (0 = no limit). Local images are embedded as base64 after
            the cut, so the stored content can be larger than this. Default: 0.
        strip_readme_badges: Whether to strip badge lines (images/links at the top)
            from README files. Default: True.
        exclude_patterns: Extra paths for the Language Server to skip when indexing
            the workspace, added to the built-in exclusions rather than replacing
            them. Default: [].
    """

    ignore_config_prefixes: list[str] = field(default_factory=lambda: ["genomes."])
    ignore_input_prefixes: list[str] = field(default_factory=list)
    include_hidden_params: bool = True
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
        """
        Create a config from a dictionary, using defaults for missing values.

        A value of the wrong type falls back to the default with a warning, so a
        typo in ``config.yaml`` can't surface as a traceback from the middle of
        extraction. Unknown keys are ignored.

        Args:
            data: Parsed contents of a config file

        Returns:
            The configuration to use.
        """
        values: dict[str, Any] = {}
        for key, default in DEFAULT_CONFIG.items():
            if key in data:
                if _is_valid(key, data[key]):
                    values[key] = data[key]
                    continue
                logger.warning(
                    f"Config option {key!r} should be {_requirement(key)}, "
                    f"got {data[key]!r}. Using the default: {default!r}"
                )
            # Copy, so the caller can't mutate DEFAULT_CONFIG through the result.
            values[key] = list(default) if isinstance(default, list) else default
        return cls(**values)

    def cache_key(self) -> str:
        """
        Stable short hash of the options that shape extraction.

        Extraction results depend on the config in use, so the cache key has to
        include it. Without this, a CLI run (which loads the user's config file)
        and a library call (which uses defaults) would share a cache entry on
        the same unchanged pipeline and return each other's results.

        ``default_format`` is left out: it only picks the CLI's output format,
        so including it would evict every cached extraction - each one a full
        Language Server run - to change a presentation default.

        Returns:
            A hex digest suitable for use in a cache filename.
        """
        extraction_options = {
            key: value for key, value in self.to_dict().items() if key not in _CLI_ONLY_FIELDS
        }
        payload = json.dumps(extraction_options, sort_keys=True)
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
# Set to false to leave them out of the documentation entirely.
# Default: true
include_hidden_params: true

# Default output format for `nf-docs generate` when -f/--format is not specified.
# Options: html, json, yaml, markdown (or md), table
# Default: html
default_format: html

# Maximum length of README source text to include, in characters.
# The cut happens before local images are embedded as base64, so this limits
# how much of the README is kept, not the size of the stored result.
# Set to 0 for no limit.
# Default: 0
max_readme_length: 0

# Whether to strip badge lines from the top of README files.
# Badges are typically image links ([![...], ![...]) that appear after the title.
# Set to false to include badges in the documentation.
# Default: true
strip_readme_badges: true

# Extra paths for the Nextflow Language Server to skip when indexing.
# Useful for excluding test data, examples, etc. These are added to the paths
# nf-docs always excludes (.git, .nf-test, work) rather than replacing them.
# Entries are passed through to the language server's `nextflow.files.exclude`
# setting, so directory names are the safest thing to put here.
# Uncomment and edit to set some. Default: none.
#
# exclude_patterns:
#   - "tests"
#   - "examples"
"""
