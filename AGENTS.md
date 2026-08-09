# AGENTS.md

This file provides guidance for AI coding agents working on the nf-docs project.

## Project Overview

nf-docs is a CLI tool that generates API documentation for Nextflow pipelines by querying the
Nextflow Language Server (LSP) and extracting information from `nextflow_schema.json`,
`nextflow.config`, `meta.yml`, and `README.md`. Output formats: HTML, JSON, YAML, Markdown.

## Build & Development

### Installation

```bash
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest                                                    # all tests
pytest -v                                                 # verbose
pytest tests/test_models.py                               # single file
pytest tests/test_models.py::TestProcess                  # single class
pytest tests/test_models.py::TestProcess::test_creation   # single test
pytest --cov=nf_docs --cov-report=term-missing            # with coverage
```

### Linting & Formatting

```bash
ruff check src/ tests/            # lint
ruff check --fix src/ tests/      # lint + autofix
ruff format src/ tests/           # format
ty check src/                     # type checking (NOT mypy)
prek run --all-files              # all hooks (ruff, ty, prettier, tailwind) — pre-commit also works
```

Prek is preferred over pre-commit; both consume the same `.pre-commit-config.yaml`.

### Rebuilding Tailwind CSS

If you modify `src/nf_docs/templates/html.html` or `build-assets/input.css`, rebuild the committed
CSS at `src/nf_docs/templates/tailwind.css`:

```bash
cd build-assets && npm install && npm run build   # first time
cd build-assets && npm run build                  # subsequent
```

The pre-commit hook does this automatically. The generated CSS is committed so end users don't need
Node.

### Running the CLI

```bash
nf-docs generate . -f html -o ./nf-docs/    # HTML output (also: json, yaml, markdown)
nf-docs generate . -f html --no-cache        # skip cache
nf-docs generate . -f html -v                # debug logging
```

## Code Style Guidelines

### General Rules

- **Line length**: 100 characters (enforced by ruff)
- **Python version**: 3.10+ (use native union types, builtin generics)
- **Type hints**: Required on all function signatures
- **Docstrings**: Required on all public modules, classes, and functions (Google style)

### Type Hints

- Builtin generics: `list[str]`, `dict[str, Any]`, `tuple[int, str]`
- Union syntax: `X | None` (never `Optional[X]`)
- Import `Any` from `typing` when needed
- Use `TYPE_CHECKING` guard for circular imports

### Imports

Sorted by ruff isort rules. Order: stdlib, third-party, local. Separate each group with a blank
line:

```python
import logging
from pathlib import Path
from typing import Any

from jinja2 import Environment

from nf_docs.models import Pipeline, Process
```

### Naming Conventions

- **Modules**: `snake_case` (`lsp_client.py`, `git_utils.py`)
- **Classes**: `PascalCase` (`PipelineExtractor`, `LSPClient`)
- **Functions/methods**: `snake_case` (`parse_hover_content`, `get_entry_workflow`)
- **Private methods**: `_prefix` (`_extract_from_lsp`, `_parse_symbol_name`)
- **Constants**: `UPPER_SNAKE_CASE` (`LANGUAGE_SERVER_JAR`, `NEXTFLOW_URL`)
- **Tests**: `TestXxx` classes, `test_xxx` methods

### Data Models

Use `@dataclass` for all models (never pydantic/attrs). Every model should have a `to_dict()`
method:

```python
@dataclass
class Example:
    """Brief description."""

    name: str
    description: str = ""
    items: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {"name": self.name, "description": self.description, "items": self.items}
```

### Error Handling

Each module defines its own exception class (e.g., `ExtractionError`, `LSPError`,
`SchemaParseError`, `ConfigParseError`). Use specific exceptions, log recoverable issues as
warnings:

```python
logger = logging.getLogger(__name__)

try:
    result = some_operation()
except SpecificError as e:
    logger.warning(f"Operation failed: {e}")
    return None
```

The CLI layer catches domain exceptions and shows user-friendly messages via `rich`.

### Logging

- Define `logger = logging.getLogger(__name__)` at module level
- Use f-strings in log calls: `logger.info(f"Parsed {count} parameters")`
- **debug**: Internal state, LSP communication, cache details
- **info**: User-relevant progress ("Parsed config with N parameters")
- **warning**: Recoverable issues ("Failed to parse schema")
- **error**: Failures that affect output

### Testing

Tests use pytest with class-based organization. Shared fixtures in `conftest.py` include
`sample_schema`, `sample_pipeline`, `sample_nextflow_file`, etc.

```python
class TestProcess:
    """Tests for Process model."""

    def test_creation(self):
        process = Process(name="FASTQC", docstring="QC tool")
        assert process.name == "FASTQC"

    def test_to_dict(self):
        result = Process(name="TEST").to_dict()
        assert result["name"] == "TEST"
```

Use `unittest.mock.patch` to mock LSP and external calls:

```python
with patch.object(PipelineExtractor, "_extract_from_lsp"):
    extractor = PipelineExtractor(workspace_path=sample_pipeline)
    pipeline = extractor.extract()
```

Async test mode is `auto` (via `asyncio_mode = "auto"` in pyproject.toml).

## File Organization

```
src/nf_docs/
├── __init__.py          # Version, public API re-exports (__all__)
├── api.py               # High-level library API: extract() / render() / generate()
├── cache.py             # XDG-compliant caching with content hashing
├── cli.py               # CLI entry point (rich-click)
├── output.py            # Source/output path policy shared by the CLI and api.py (leaf module)
├── config.py            # User config from ~/.config/nf-docs/config.yaml
├── config_parser.py     # Parse nextflow.config via `nextflow config -flat`
├── extractor.py         # Main extraction orchestration
├── generation_info.py   # Generation metadata (version, timestamp)
├── git_utils.py         # Git info for source URLs
├── lsp_client.py        # JSON-RPC over stdio to Nextflow Language Server
├── meta_parser.py       # nf-core meta.yml parser
├── models.py            # Data models (all @dataclass)
├── nextflow_env.py      # Isolated NXF_HOME for clean Nextflow runs
├── nf_parser.py         # Parse process/workflow hover content from LSP
├── progress.py          # Callback-based progress reporting
├── schema_parser.py     # nextflow_schema.json parser
├── tailwind.py          # Tailwind CSS build utility + CLI
├── renderers/
│   ├── __init__.py      # get_renderer() factory
│   ├── base.py          # BaseRenderer ABC
│   ├── html.py          # HTML renderer (Jinja2 + Tailwind)
│   ├── json.py          # JSON renderer
│   ├── markdown.py      # Markdown renderer (multi-file)
│   └── yaml.py          # YAML renderer
└── templates/
    ├── html.html        # Jinja2 HTML template
    └── tailwind.css     # Pre-built Tailwind CSS
```

## Architecture Notes

- **LSP Integration**: JSON-RPC over stdio. Symbol names are prefixed (`"process FASTQC"`,
  `"workflow MAIN"`). Hover results have a signature block then `---` then Groovydoc. Workspace must
  be indexed via `didChangeConfiguration` before queries work.
- **Caching**: Stored in `~/.cache/nf-docs/`, keyed by pipeline path, package version, and SHA256
  content hash of all `.nf` + config + schema + README files.
- **Rendering**: Strategy pattern via `BaseRenderer` ABC with `render()`, `render_to_file()`,
  `render_to_directory()`. Factory function `get_renderer(format)` returns the appropriate renderer.
  HTML uses a single Jinja2 template with inline CSS (Tailwind) and JavaScript for search. Adding a
  new output format means updating `RENDERERS` in `renderers/__init__.py`,
  `SINGLE_FILE_OUTPUT_POLICY` and (if it writes a directory) `DIRECTORY_FORMATS` in `output.py`, the
  CLI's `--format` choices, and tests. Format aliases live only in `output.FORMAT_ALIASES`;
  `get_renderer()` resolves through `normalize_format()` so there is one alias table.
- **Config parsing**: `config_parser.py` shells out to `nextflow config -flat`. `nextflow_env.py`
  sets an isolated `NXF_HOME` so this doesn't pollute the user's Nextflow state.
- **Two entry points**: `cli.py` (rich-click) and `api.py` (library). All source/output path and
  format decisions live in `output.py`, and `cli.py` extracts via `api.extract()`, so the two stay
  in sync by construction rather than by discipline. Keep console output and `sys.exit()` in
  `cli.py` only — core modules log via `logging` and raise exceptions. The CLI reads the user's
  `~/.config/nf-docs/config.yaml` and passes it to `PipelineExtractor(config=...)`; `api.py` uses
  `NfDocsConfig()` defaults so library calls are reproducible. There is deliberately no global
  config accessor — inject an `NfDocsConfig` instead of reintroducing ambient state.
- **Public API**: everything in `nf_docs.__all__` plus `nf_docs.models`. Adding to it is a
  commitment — update `docs/python-api.md` and `tests/test_api.py` alongside. `__init__.py`
  re-exports eagerly, which costs ~170 ms on `import nf_docs` (it pulls in jinja2, httpx and
  friends). That's deliberate: a plain import list is worth more than the startup time for a tool
  that spends seconds waiting on the Language Server. Don't make it lazy.
- **Pre-commit hook entry**: `.pre-commit-hooks.yaml` exposes the CLI as the `nf-docs` hook with
  default `args: [., --format, html]`, triggered by changes to `.nf`, `nextflow.config`,
  `nextflow_schema.json`, `meta.yml`, or README files. Guarded by `tests/test_pre_commit_hooks.py`.

## Test pipelines

Useful real-world targets for manual testing:

- [nextflow-io/rnaseq-nf](https://github.com/nextflow-io/rnaseq-nf) — simple, good for first checks
- [nf-core/fetchngs](https://github.com/nf-core/fetchngs) — small but real
- [nf-core/rnaseq](https://github.com/nf-core/rnaseq) — complex, stress test
