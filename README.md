<div align="center">

# nf-docs

**Generate beautiful API documentation for Nextflow pipelines**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)

![nf-docs demo](https://raw.githubusercontent.com/ewels/nf-docs/main/docs/images/demo.gif)

**[Full documentation →](https://ewels.github.io/nf-docs)**

Choose from 4 different output formats:

</div>

<table width="100%">
<tr>
<td width="33%">
<h3 align="center">HTML</h3>
<ul><li>Single-file output</li><li>Share anywhere, even offline</li><li>Full-text search built in</li></ul><hr>
</td>
<td width="33%">
<h3 align="center">Markdown</h3>
<ul><li>Multiple files or tables by section</li><li>Perfect for static site generators</li></ul><hr>
</td>
<td width="33%">
<h3 align="center">JSON / YAML</h3>
<ul><li>Machine-readable output</li><li>Build custom integrations</li><li>CI/CD friendly</li></ul><hr>
</td>
</tr>
</table>

## What is nf-docs?

<!-- prettier-ignore-start -->
> [!IMPORTANT]
> This is not an official Nextflow project. It's a fun side-project by
> [Phil Ewels](https://github.com/ewels). Please use at your own risk :)
<!-- prettier-ignore-end -->

Information is pulled from multiple sources to construct the docs (each only if available):

- **README.md** - Pipeline overview and description
- **nextflow.config** - Runtime configuration defaults
- **nextflow_schema.json** - Typed input parameters with descriptions and validation rules
- **Language Server** - Processes, workflows, functions with their Groovydoc comments
- **meta.yml** - nf-core module metadata (tools, keywords, authors)

The documentation for workflows, processes and functions is relatively unique. `nf-docs` extracts
this from your Nextflow pipelines by querying the
[Nextflow Language Server](https://github.com/nextflow-io/language-server). It produces structured
API documentation similar to Sphinx for Python or Javadoc for Java.

## Examples and docs

See https://ewels.github.io/nf-docs

## Quick Start

With [`uv`](https://docs.astral.sh/uv/):

```bash
uvx nf-docs generate ./my_pipeline
```

With `pip`:

```bash
# Install
pip install nf-docs

# Generate HTML documentation
nf-docs generate ./my_pipeline
```

With [Bioconda](https://bioconda.github.io/) (requires
[channel setup](https://bioconda.github.io/)):

```bash
pixi global install nf-docs
# or
conda install nf-docs
```

That's it! Open `docs/index.html` in your browser.

### Document a single module

Pass a single `.nf` file to generate a focused, module-style README:

```bash
nf-docs generate modules/mytool/subtools/main.nf --format md
```

By default this writes `README.md` next to `main.nf`. Use `--output` to pick a different path, or
`--format json` / `--format yaml` to print structured output to stdout instead.

## Prek / pre-commit hook

`nf-docs` can generate pipeline documentation automatically before each commit using
[Prek](https://prek.j178.dev/) or [pre-commit](https://pre-commit.com/):

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

The hook defaults to `nf-docs generate . --format html`, which writes HTML output to `docs/`.
Override `args` in your `.pre-commit-config.yaml` to use another format or output path:

```yaml
repos:
  - repo: https://github.com/ewels/nf-docs
    rev: v0.2.1
    hooks:
      - id: nf-docs
        args: [., --format, markdown, --output, docs/api]
```

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, testing, and contribution guidelines.

## License

Apache 2.0 - see [LICENSE](LICENSE) for details.
