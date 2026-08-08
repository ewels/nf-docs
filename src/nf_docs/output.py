"""
Source and output resolution shared by the CLI and the Python API.

This module answers two questions for both entry points:

- what is being documented (a whole pipeline, or a single ``.nf`` module)
- where the rendered documentation goes on disk

It holds no console output, no process exits, and no rendering. Keeping the
answers here is what stops ``nf_docs.cli`` and ``nf_docs.api`` from drifting
apart. It imports nothing from the rest of the package, so it stays cheap.
"""

import re
from pathlib import Path

# Format aliases accepted on input, mapped to their canonical renderer name.
# ``renderers.get_renderer()`` resolves through this too, so a new alias only
# needs adding here.
FORMAT_ALIASES: dict[str, str] = {"md": "markdown"}

# Per-format single-file output policy:
#   default_name: filename to use when no output path is given. ``None`` means
#       the format has no natural single-file name, so the CLI streams it to
#       stdout instead (see ``resolve_single_file_path``).
#   extension: this format's file extension.
SINGLE_FILE_OUTPUT_POLICY: dict[str, tuple[str | None, str]] = {
    "markdown": ("README.md", "md"),
    "html": ("index.html", "html"),
    "json": (None, "json"),
    "yaml": (None, "yaml"),
    "table": (None, "txt"),
}

# Formats that render as a directory of files rather than a single document.
DIRECTORY_FORMATS: frozenset[str] = frozenset({"markdown", "html", "table"})

# Filename stem used for json/yaml output of a whole pipeline.
DATA_FILE_STEM = "pipeline"

# Directory used when documenting a whole pipeline with no explicit output path.
DEFAULT_OUTPUT_DIR = "docs"


def normalize_format(output_format: str) -> str:
    """
    Normalize a format name to its canonical renderer name.

    Args:
        output_format: Format name, possibly an alias (e.g. ``md``)

    Returns:
        The canonical format name (e.g. ``markdown``)
    """
    lowered = output_format.lower()
    return FORMAT_ALIASES.get(lowered, lowered)


def format_extension(output_format: str) -> str:
    """
    Get the file extension for a canonical format name.

    Args:
        output_format: Canonical format name

    Returns:
        The extension, without a leading dot

    Raises:
        KeyError: If the format has no output policy entry
    """
    return SINGLE_FILE_OUTPUT_POLICY[output_format][1]


def looks_like_module(main_nf: Path) -> bool:
    """
    Heuristic: ``main.nf`` defines at least one ``process`` block and no
    top-level ``workflow`` block — i.e. it's an nf-core-style module rather
    than a pipeline entry point or subworkflow.

    Args:
        main_nf: Path to the ``main.nf`` file to inspect

    Returns:
        ``True`` if the file looks like a standalone module
    """
    try:
        content = main_nf.read_text(encoding="utf-8")
    except OSError:
        return False
    has_process = re.search(r"(?m)^\s*process\b", content) is not None
    has_workflow = re.search(r"(?m)^\s*workflow\b", content) is not None
    return has_process and not has_workflow


def resolve_source(path: str | Path) -> tuple[Path, bool]:
    """
    Decide whether ``path`` should be documented as a single file or a pipeline.

    A ``.nf`` file is always single-file mode. A directory is auto-detected as a
    single module when it holds a ``main.nf`` that defines process(es) and no
    workflow block, and has no pipeline-level config files alongside it.

    Resolving an already-resolved path is a no-op, so callers that pass the
    result back in get the same answer.

    Args:
        path: Path to a Nextflow pipeline directory or a single ``.nf`` file

    Returns:
        Tuple of ``(resolved_path, single_file_mode)``. In single-file mode the
        resolved path points at the ``.nf`` file itself, not its directory.

    Raises:
        ValueError: If ``path`` is a file that isn't a ``.nf`` file
    """
    source = Path(path)

    if source.is_file():
        if source.suffix.lower() != ".nf":
            raise ValueError(f"Single-file input must be a .nf file, got: {source.name}")
        return source, True

    main_nf = source / "main.nf"
    has_pipeline_config = (source / "nextflow.config").is_file() or (
        source / "nextflow_schema.json"
    ).is_file()
    if main_nf.is_file() and not has_pipeline_config and looks_like_module(main_nf):
        return main_nf, True

    return source, False


def streams_by_default(output_format: str) -> bool:
    """
    Whether a format has no natural single-file name, so the CLI streams it to
    stdout when given no output path.

    This is a command-line concern: the Python API always writes a file.

    Args:
        output_format: Canonical format name

    Returns:
        ``True`` if the CLI streams this format rather than writing a file

    Raises:
        KeyError: If the format has no output policy entry
    """
    return SINGLE_FILE_OUTPUT_POLICY[output_format][0] is None


def resolve_single_file_path(
    source_file: Path,
    output_format: str,
    output_path: Path | None,
) -> Path:
    """
    Decide which file a single module's documentation is written to.

    Args:
        source_file: The ``.nf`` file being documented
        output_format: Canonical format name
        output_path: Explicit output path, or ``None`` for the default

    Returns:
        The file to write

    Raises:
        KeyError: If the format has no output policy entry
    """
    default_name, extension = SINGLE_FILE_OUTPUT_POLICY[output_format]
    filename = default_name or f"{source_file.stem}.{extension}"

    if output_path is None:
        return source_file.parent / filename
    # User-specified path always wins. Treat directories as "put a default
    # filename in here" so `-o some_dir/` still works.
    if output_path.is_dir():
        return output_path / filename
    return output_path


def resolve_data_file_path(
    source: Path,
    output_format: str,
    output_path: Path | None,
) -> Path:
    """
    Decide where a whole pipeline's json/yaml output goes.

    Args:
        source: The pipeline directory being documented
        output_format: Canonical format name (``json`` or ``yaml``)
        output_path: Explicit output file or directory, or ``None`` for the
            default of ``<pipeline>/docs/pipeline.<ext>``

    Returns:
        The file to write

    Raises:
        KeyError: If the format has no output policy entry
    """
    filename = f"{DATA_FILE_STEM}.{format_extension(output_format)}"

    if output_path is None:
        return source / DEFAULT_OUTPUT_DIR / filename
    if output_path.is_dir():
        return output_path / filename
    return output_path


def default_output_dir(source: Path) -> Path:
    """Get the default output directory for a whole pipeline."""
    return source / DEFAULT_OUTPUT_DIR
