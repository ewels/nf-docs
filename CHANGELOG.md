# Changelog

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
