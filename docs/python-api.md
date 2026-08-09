# Python API

`nf-docs` is a CLI tool first, but it's also a normal Python package. Import it when you need
something the CLI doesn't cover: feeding pipeline data into your own tooling, or rendering docs as
part of a site build.

```bash
pip install nf-docs
```

The requirements are the same as for the CLI: Java for the Nextflow Language Server, and optionally
Nextflow itself for parsing `nextflow.config`.

## Three functions

Three functions cover most of it:

| Function     | Does                                                    | Returns      |
| ------------ | ------------------------------------------------------- | ------------ |
| `extract()`  | Reads a pipeline (or a single module) into a data model | `Pipeline`   |
| `render()`   | Turns a `Pipeline` into a string in a given format      | `str`        |
| `generate()` | Both of the above, then writes the result to disk       | `list[Path]` |

```python
import nf_docs

pipeline = nf_docs.extract("./my_pipeline")
markdown = nf_docs.render(pipeline, "markdown")
files = nf_docs.generate("./my_pipeline", output_format="html", output="site/")
```

Unlike the CLI, these never print to the console and never exit the process. They return values and
raise exceptions.

## Reading pipeline data

`extract()` gives you a [`Pipeline`](#the-pipeline-model) object. Use it when you want the data
rather than the documentation.

```python
import nf_docs

pipeline = nf_docs.extract("./my_pipeline")

print(pipeline.metadata.name, pipeline.metadata.version)

for process in pipeline.processes:
    print(f"{process.name}: {process.docstring}")

# Required parameters that have no default
for param in pipeline.inputs:
    if param.required and param.default is None:
        print(f"{param.name} ({param.type}) - {param.description}")
```

Every model has a `to_dict()`, so handing the whole thing to another tool is one call:

```python
import json

with open("pipeline-api.json", "w") as fh:
    json.dump(pipeline.to_dict(), fh, indent=2)
```

## Rendering into an existing build

`render()` returns a string. That's usually what you want when another tool owns the output
directory, such as a static site generator.

```python
from pathlib import Path
import nf_docs

pipeline = nf_docs.extract("./my_pipeline")

Path("src/content/docs/api.md").write_text(
    "---\ntitle: Pipeline API\n---\n\n" + nf_docs.render(pipeline, "markdown")
)
```

Renderer-specific options pass straight through:

```python
nf_docs.render(pipeline, "json", indent=4)
nf_docs.render(pipeline, "yaml", default_flow_style=True)
nf_docs.render(pipeline, "html", use_tailwind=False)
nf_docs.render(pipeline, "markdown", title="My Pipeline")
```

Pass `single_file=True` for the focused single-document form used for modules, rather than the full
pipeline layout.

## Writing files

`generate()` is the equivalent of `nf-docs generate`. It returns the paths it wrote:

```python
import nf_docs

for path in nf_docs.generate("./my_pipeline", output_format="html", output="site/"):
    print(f"wrote {path}")
```

Omit `output` and it follows the same conventions as the CLI: `<pipeline>/docs/` for a whole
pipeline, and a file alongside the source when documenting a single module.

!!! note

    `generate()` always writes files, even for `json` and `yaml`. Streaming those to stdout is a
    command-line convenience rather than part of the API. Use `extract()` and `render()` if you
    want a string.

## Documenting a single module

Pass a path to a `.nf` file to document just that file. nf-docs also auto-detects a directory
holding a module-style `main.nf` (process definitions, no workflow, no pipeline config), so both of
these do the same thing:

```python
nf_docs.generate("modules/mytool/main.nf", output_format="md")
nf_docs.generate("modules/mytool", output_format="md")
```

Both write `modules/mytool/README.md`.

To document every module in a repository:

```python
from pathlib import Path
import nf_docs

for main_nf in Path("modules").rglob("main.nf"):
    nf_docs.generate(main_nf, output_format="md")
```

!!! warning

    Each call starts its own Language Server process, so a loop like this is slow. Documenting a
    whole pipeline in one `extract()` call is much faster than documenting its modules one by one.

## Progress reporting

Extraction can take a while, because the Language Server has to start and index the workspace. Pass
a `progress_callback` to drive your own progress display. It receives
[`ProgressUpdate`](#progress-updates) objects.

```python
import nf_docs

def show(update: nf_docs.ProgressUpdate) -> None:
    if update.has_progress:
        print(f"{update.message} [{update.current}/{update.total}] {update.detail or ''}")
    else:
        print(update.message)

pipeline = nf_docs.extract("./my_pipeline", progress_callback=show)
```

`rich` ships with nf-docs, so a progress bar costs no extra dependency. Passing `None` for
`completed` or `total` leaves those values alone, so the same callback handles both the countable
and indeterminate phases:

```python
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn

import nf_docs

with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
) as progress:
    task = progress.add_task("Starting...", total=None)

    def show(update: nf_docs.ProgressUpdate) -> None:
        progress.update(
            task,
            description=update.message,
            completed=update.current,
            total=update.total,
        )

    pipeline = nf_docs.extract("./my_pipeline", progress_callback=show)
```

`update.phase` is an `ExtractionPhase` member if you want to react to specific stages
(`LSP_INDEXING`, `PARSING_SCHEMA`, `COMPLETE`, and so on).

## Configuration

The CLI reads `~/.config/nf-docs/config.yaml`. The Python API deliberately does not: a library call
inside someone else's build script shouldn't change behaviour based on whoever happens to be running
it. Library calls use the defaults unless you pass a config explicitly:

```python
import nf_docs

# Defaults - reproducible regardless of the user's config file
nf_docs.extract("./my_pipeline")

# Opt in to the user's config file
nf_docs.extract("./my_pipeline", config=nf_docs.load_config())

# Or set options directly
config = nf_docs.NfDocsConfig(ignore_config_prefixes=["genomes.", "test."])
nf_docs.extract("./my_pipeline", config=config)
```

The fields:

| Field                     | Default        | Effect                                                                          |
| ------------------------- | -------------- | ------------------------------------------------------------------------------- |
| `ignore_config_prefixes`  | `["genomes."]` | Drops matching parameters from the Configuration section                        |
| `ignore_input_prefixes`   | `[]`           | Drops matching parameters from the Parameters section                           |
| `include_hidden_params`   | `True`         | Set `False` to leave out parameters marked `hidden` in `nextflow_schema.json`   |
| `max_readme_length`       | `0`            | Trims README source text to this many characters, on a line boundary. `0` = no limit |
| `strip_readme_badges`     | `True`         | Set `False` to keep the badge lines below a README's title                      |
| `exclude_patterns`        | `[]`           | Extra paths the Language Server skips when indexing the workspace               |
| `default_format`          | `"html"`       | CLI only — the format `nf-docs generate` uses without `-f/--format`             |

A parameter dropped by `include_hidden_params` or `ignore_input_prefixes` doesn't reappear under
Configuration; it's left out of the documentation entirely.

`exclude_patterns` is added to the exclusions nf-docs always sends (`.git`, `.nf-test`, `work`)
rather than replacing them.

`max_readme_length` caps the README source text. Local images are converted to base64 data URIs
*after* the cut, so `readme_content` can still be large if the kept portion contains images.

A value of the wrong type falls back to that option's default with a warning, so a typo in
`config.yaml` won't surface as an error part-way through extraction.

## Caching

nf-docs caches extraction results in `~/.cache/nf-docs/`, keyed by pipeline path, nf-docs version, a
hash of the pipeline's files, and the configuration used. The config is part of the key so a CLI run
and a library call on the same pipeline don't return each other's results. The cache is on by
default, matching the CLI:

```python
nf_docs.extract("./my_pipeline", use_cache=False)     # ignore the cache entirely
nf_docs.extract("./my_pipeline", force_refresh=True)  # re-extract, then update the cache

from pathlib import Path

from nf_docs import PipelineCache

PipelineCache().clear(Path("./my_pipeline"))  # one pipeline; takes a Path
PipelineCache().clear()  # everything
```

## Errors

The API raises rather than exiting. The exceptions worth catching:

| Exception         | Raised when                                                                                   |
| ----------------- | --------------------------------------------------------------------------------------------- |
| `ValueError`      | A path that doesn't exist, an unsupported format, or a non-`.nf` file passed as a single file |
| `LSPError`        | The Language Server can't be found, downloaded, started or queried                            |
| `ExtractionError` | Extraction failed                                                                             |

```python
import nf_docs

try:
    pipeline = nf_docs.extract("./my_pipeline")
except nf_docs.LSPError as e:
    print(f"Language Server problem: {e}")
except nf_docs.ExtractionError as e:
    print(f"Could not extract: {e}")
```

A missing or unparseable individual source (no schema, a broken `nextflow.config`) logs a warning
and carries on rather than raising. Nothing reaches the console by default. Attach a handler to the
`nf_docs` logger to see these:

```python
import logging

logging.getLogger("nf_docs").addHandler(logging.StreamHandler())
logging.getLogger("nf_docs").setLevel(logging.INFO)
```

## The Pipeline model

Everything is a plain `@dataclass`, so `to_dict()`, `dataclasses.asdict()` and ordinary attribute
access all work.

| Attribute       | Type                  | Contents                                      |
| --------------- | --------------------- | --------------------------------------------- |
| `metadata`      | `PipelineMetadata`    | Name, description, version, authors, README   |
| `inputs`        | `list[PipelineInput]` | Typed parameters from `nextflow_schema.json`  |
| `config_params` | `list[ConfigParam]`   | Defaults from `nextflow.config`               |
| `workflows`     | `list[Workflow]`      | Workflows with inputs, outputs and docstrings |
| `processes`     | `list[Process]`       | Processes with inputs, outputs and docstrings |
| `functions`     | `list[Function]`      | Functions with parameters and return values   |

Some helpers:

```python
pipeline.has_content()                  # did we find anything at all?
pipeline.get_entry_workflow()           # the entry workflow, or None
pipeline.get_process_by_name("FASTQC")  # a Process, or None
pipeline.get_input_groups()             # inputs grouped by schema section
pipeline.to_dict()                      # JSON-compatible dict
```

## Progress updates

`ProgressUpdate` objects carry:

| Attribute      | Type              | Meaning                                     |
| -------------- | ----------------- | ------------------------------------------- |
| `phase`        | `ExtractionPhase` | Which stage of extraction this is           |
| `message`      | `str`             | Human-readable description                  |
| `current`      | `int \| None`     | Items done, when countable                  |
| `total`        | `int \| None`     | Items in total, when countable              |
| `detail`       | `str \| None`     | Extra context, usually the current filename |
| `has_progress` | `bool`            | Whether `current`/`total` are both set      |
| `percent`      | `float \| None`   | Progress as a percentage, when countable    |

## Lower-level pieces

The three functions above wrap classes you can use directly if you need more control:

```python
from nf_docs import PipelineExtractor, get_renderer

extractor = PipelineExtractor(
    workspace_path="./my_pipeline",
    target_file="./my_pipeline/modules/mytool/main.nf",  # single-file mode
    language_server_jar="/path/to/language-server-all.jar",
    nextflow_path="/usr/local/bin/nextflow",
)
pipeline = extractor.extract()

renderer = get_renderer("markdown")(title="My Pipeline")
files = renderer.render_to_directory(pipeline, "docs/")
```

Subclass `BaseRenderer` to add your own output format, implementing `render()` and
`render_to_directory()`.

## What's public

Anything re-exported from the top-level `nf_docs` namespace, plus the models in `nf_docs.models`, is
the supported API. Everything else may change without notice: underscore-prefixed helpers, the
Language Server client internals, the parser modules.

`nf-docs` is pre-1.0, so the public API may still change between minor releases. Pin a version if
that matters to you.
