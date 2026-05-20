# Running nf-docs

## Generate docs

```bash
nf-docs generate PIPELINE_PATH [OPTIONS]
```

| Option              | Description                                                          |
| ------------------- | -------------------------------------------------------------------- |
| `--format`, `-f`    | Output format: `html` (default), `markdown`, `table`, `json`, `yaml` |
| `--output`, `-o`    | Output file or directory (default: `docs/`)                          |
| `--title`, `-t`     | Custom title                                                         |
| `--no-cache`        | Force fresh extraction                                               |
| `--verbose`, `-v`   | Debug output                                                         |
| `--language-server` | Path to Language Server JAR                                          |

```bash
# HTML — single shareable file
nf-docs generate . -f html -o site/

# Markdown — for static site generators
nf-docs generate . -f markdown -o docs/

# JSON — pipe to file or other tools
nf-docs generate . -f json > api.json

# Table — compact terraform-docs-style tables
nf-docs generate . -f table -o docs/

```

## Prek / pre-commit hook

Use the bundled hook with [Prek](https://prek.j178.dev/) or [pre-commit](https://pre-commit.com/) to
regenerate docs whenever pipeline documentation inputs change.

```yaml
repos:
  - repo: https://github.com/ewels/nf-docs
    rev: v0.2.1
    hooks:
      - id: nf-docs
```

Install the hook into your repo:

```bash
# With Prek (recommended)
prek install

# Or with pre-commit
pre-commit install
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
    rev: v0.2.1
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

### Table

A single `README.md` with compact Markdown tables — inspired by
[terraform-docs](https://github.com/terraform-docs/terraform-docs).

Supports **marker-based injection** into existing README files:

```md
# My Pipeline

Some intro text.

<!-- BEGIN_NF_DOCS -->
<!-- END_NF_DOCS -->

Other content below.
```

Running `nf-docs generate . -f table -o .` will inject the generated tables between the markers,
leaving the rest of the file untouched.

#### Selective sections with template tags

Control which sections appear by adding `{{ section }}` placeholders between the markers:

```md
<!-- BEGIN_NF_DOCS -->

{{ inputs }}

{{ config }}

<!-- END_NF_DOCS -->
```

Available tags: `{{ header }}`, `{{ inputs }}`, `{{ config }}`, `{{ workflows }}`,
`{{ processes }}`, `{{ functions }}`.

If no tags are present, all sections are rendered (the default).

### JSON / YAML

Structured data for programmatic use, CI/CD pipelines, or custom tooling.

See the [examples](examples.md) to get a feel for the structure.
