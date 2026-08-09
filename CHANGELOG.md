# Changelog

## Unreleased

### Added

- Supported Python API for using nf-docs as a library: `nf_docs.extract()`, `nf_docs.render()` and
  `nf_docs.generate()`, alongside a wider set of exports from the top-level `nf_docs` namespace
- `py.typed` marker so type hints reach downstream users
- `PipelineExtractor` accepts a `config=` argument, so callers can supply an `NfDocsConfig` instead
  of relying on the global instance
- New "Python API" documentation page
- Every `NfDocsConfig` option now takes effect. `ignore_input_prefixes`, `include_hidden_params`,
  `max_readme_length` and `exclude_patterns` were documented but never consulted; `default_format`
  was ignored in favour of a hardcoded `html`
- Restored the `nf-docs config` command (`--path`, `--show-example`, `--init`), which had been
  removed by accident along with the config wiring

### Fixed

- `strip_readme_badges` is consulted again when parsing a README. It was wired up when the option
  was introduced, then dropped by an unrelated revert in the same release
- A parameter excluded by `include_hidden_params` or `ignore_input_prefixes` no longer reappears in
  the Configuration section
- A config option set to the wrong type falls back to its default with a warning, rather than
  failing somewhere downstream. `default_format: 3` used to be an uncaught `AttributeError`,
  `max_readme_length: "lots"` silently dropped the README, and `exclude_patterns: "tests"` sent the
  language server one exclusion per character
- `NfDocsConfig.from_dict()` copies its list defaults, so mutating a returned config no longer
  changes `DEFAULT_CONFIG` for every later caller
- `default_format` is excluded from the extraction cache key. It only picks the CLI's output format,
  so changing it no longer evicts every cached pipeline
- The extraction cache is now keyed on the configuration as well as the pipeline contents.
  Previously a CLI run (which loads `~/.config/nf-docs/config.yaml`) and a library call (which uses
  defaults) shared a cache entry for the same unchanged pipeline and returned each other's results
- A config file containing valid YAML of the wrong shape (e.g. a top-level list) falls back to
  defaults with a warning instead of raising
- `nf_docs.extract()` and `nf_docs.generate()` raise `ValueError` for a path that doesn't exist,
  rather than returning an empty `Pipeline` named after the missing directory

### Changed

- `include_hidden_params` now defaults to `true`, matching the behaviour nf-docs has always had of
  showing hidden schema parameters. Set it to `false` to leave them out
- Output path policy (format aliases, single-module detection, default filenames) moved from
  `cli.py` into a new `nf_docs.output` module so the CLI and the Python API share one implementation
- Library callers now get `NfDocsConfig()` defaults rather than the user's
  `~/.config/nf-docs/config.yaml`, which the CLI continues to read. This keeps programmatic use
  reproducible.

## [Version 0.4.0](https://github.com/ewels/nf-docs/releases/tag/v0.4.0) - 2026-05-29

### Added

- Parse typed process outputs from the Nextflow Language Server
  [#12](https://github.com/ewels/nf-docs/pull/12)

### Changed

- Pin GitHub Actions to commit SHAs and harden workflows against zizmor findings
  [#10](https://github.com/ewels/nf-docs/pull/10)

## [Version 0.3.0](https://github.com/ewels/nf-docs/releases/tag/v0.3.0) - 2026-05-20

- Single-process docs if run on an individual module [#9](https://github.com/ewels/nf-docs/pull/9)
- Reusable pre-commit hook manifest so pipelines can regenerate docs on commit
  [#8](https://github.com/ewels/nf-docs/pull/8)

## [Version 0.2.1](https://github.com/ewels/nf-docs/releases/tag/v0.2.1) - 2026-03-23

### Fixed

- Configure additional files for PyPI package distribution
  ([#6](https://github.com/ewels/nf-docs/pull/6))
- Fix ty typecheck errors with explicit dict type annotations
  ([#7](https://github.com/ewels/nf-docs/pull/7))

## [Version 0.2.0](https://github.com/ewels/nf-docs/releases/tag/v0.2.0) - 2026-03-04

### Added

- New **table** output format (`-f table`) with terraform-docs-style Markdown tables and marker
  injection for embedding generated docs into existing README files
- Template-based selective section rendering for the table format, allowing users to choose which
  sections to include
- Groovydoc `@param` and `@return` tag descriptions are now applied to process inputs and outputs
- Support for Nextflow typed syntax (`val(x)`, `path(x)`, `tuple val(x), path(y)`, etc.) when
  parsing process inputs and outputs
- Enriched bare typed outputs from `.nf` source files with proper type and name extraction
- Pattern restriction display in HTML parameter cards
- nf-fgsv added as an example pipeline, with YAML and table example outputs for all pipelines

### Fixed

- Parameters not displaying in HTML output due to README heading ID collisions with parameter IDs
- Parsing of bare typed outputs and `?` nullable type from LSP hover content
- Use a valid GitHub markdown admonition type in README

## [Version 0.1.0](https://github.com/ewels/nf-docs/releases/tag/v0.1.0) - 2026-02-20

Initial release of `nf-docs`.

### Added

- `nf-docs generate` command to extract and render pipeline documentation in HTML, JSON, YAML, and
  Markdown formats
- `nf-docs inspect` command for a dry-run summary of what nf-docs finds in a pipeline
- `nf-docs download-lsp` and `nf-docs clear-cache` utility commands
- Extraction of pipeline inputs from `nextflow_schema.json` and config parameters from
  `nextflow.config`
- Process, workflow, and function documentation via the Nextflow Language Server (LSP), including
  Groovydoc docstrings and typed I/O declarations
- nf-core `meta.yml` support for enriched module and subworkflow documentation
- Git-aware source code deep links for GitHub, GitLab, and Bitbucket
- XDG-compliant caching keyed by content hash and package version, with automatic invalidation
- User config file at `~/.config/nf-docs/config.yaml` for persistent defaults
