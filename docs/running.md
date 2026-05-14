# Running nf-docs

## Generate docs

```bash
nf-docs generate PIPELINE_PATH [OPTIONS]
```

| Option              | Description                                                 |
| ------------------- | ----------------------------------------------------------- |
| `--format`, `-f`    | Output format: `html` (default), `markdown`, `json`, `yaml` |
| `--output`, `-o`    | Output file or directory (default: `docs/`)                 |
| `--title`, `-t`     | Custom title                                                |
| `--no-cache`        | Force fresh extraction                                      |
| `--verbose`, `-v`   | Debug output                                                |
| `--language-server` | Path to Language Server JAR                                 |

```bash
# HTML — single shareable file
nf-docs generate . -f html -o site/

# Markdown — for static site generators
nf-docs generate . -f markdown -o docs/

# JSON — pipe to file or other tools
nf-docs generate . -f json > api.json
```

## Pre-commit hook

Use the bundled pre-commit hook to regenerate docs whenever pipeline documentation inputs change:

```yaml
repos:
  - repo: https://github.com/ewels/nf-docs
    rev: v0.2.0
    hooks:
      - id: nf-docs
```

By default, the hook runs:

```bash
nf-docs generate . --format html
```

That writes HTML documentation to `docs/`. To customize the command, replace the hook `args` in your
`.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/ewels/nf-docs
    rev: v0.2.0
    hooks:
      - id: nf-docs
        args: [., --format, markdown, --output, docs/api]
```

The hook is triggered by changes to `*.nf`, `nextflow.config`, `nextflow_schema.json`, `meta.yml`,
and README files.

### Other commands

```bash
# Print a summary without generating full docs
nf-docs inspect /path/to/pipeline

# Pre-download the Language Server JAR
nf-docs download-lsp

# Clear the extraction cache for a specific pipeline
nf-docs clear-cache /path/to/pipeline

# Clear the entire extraction cache
nf-docs clear-cache --all
```

## Caching

nf-docs caches extraction results to avoid re-running the Language Server on every invocation.
Cached data is stored in `~/.cache/nf-docs/` (respects `$XDG_CACHE_HOME`).

The cache is keyed by pipeline path, a SHA-256 hash of all pipeline source files, and the nf-docs
version, so it is automatically invalidated whenever files change or nf-docs is upgraded.

Use `--no-cache` to skip the cache for a single run, or `nf-docs clear-cache` to remove entries
manually.

## Output formats

### HTML

A single self-contained file with everything inlined:

- Three-column responsive layout with full-text search
- Deep linking to every section and item
- Source code links (GitHub, GitLab, Bitbucket)
- nf-core module documentation links
- Dark mode · mobile-friendly

### Markdown

A directory of files, one per section:

```
docs/
├── index.md        # Pipeline overview
├── inputs.md       # Input parameters
├── config.md       # Config parameters
├── workflows.md    # Workflows
├── processes.md    # Processes
└── functions.md    # Functions
```

### JSON / YAML

Structured data for programmatic use, CI/CD pipelines, or custom tooling.
