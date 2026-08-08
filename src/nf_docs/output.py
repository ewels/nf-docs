"""
Output resolution policy shared by the CLI and the Python API.

This module holds the decisions about *where* rendered documentation goes and
*what shape* it takes: format aliases, whether a path should be documented as a
single module file or as a whole pipeline, and the default filenames used when
the caller doesn't specify an output path.

It deliberately contains no console output and no process exits so that both
``nf_docs.cli`` and ``nf_docs.api`` can share the same behaviour.
"""

import re
from pathlib import Path

from nf_docs.models import Pipeline
from nf_docs.renderers.base import BaseRenderer

# Format aliases accepted on input, mapped to their canonical renderer name.
FORMAT_ALIASES: dict[str, str] = {"md": "markdown"}

# Single-file output policy per format:
#   default_name: the filename to use when the user passes no output path (or
#       passes a directory). ``None`` means "stream to stdout instead".
#   dir_ext: when streaming-default formats are forced to a file via an output
#       directory, use ``{source_stem}.{dir_ext}``.
SINGLE_FILE_OUTPUT_POLICY: dict[str, tuple[str | None, str]] = {
    "markdown": ("README.md", "md"),
    "html": ("index.html", "html"),
    "json": (None, "json"),
    "yaml": (None, "yaml"),
    "table": (None, "txt"),
}

# Formats that render as a directory of files rather than a single document.
DIRECTORY_FORMATS: frozenset[str] = frozenset({"markdown", "html", "table"})


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


def resolve_single_file_output(
    renderer: BaseRenderer,
    pipeline: Pipeline,
    source_file: Path,
    output_format: str,
    output_path: Path | None,
) -> tuple[Path | None, str]:
    """
    For single-file mode, decide where to write and produce the rendered string.

    Args:
        renderer: The renderer to produce content with
        pipeline: The Pipeline model to render
        source_file: The ``.nf`` file being documented
        output_format: Canonical format name
        output_path: Explicit output path, or ``None`` for the default

    Returns:
        A tuple of ``(output_file, rendered_content)``. ``output_file`` is
        ``None`` when the content should go to stdout (json/yaml/table without
        an explicit output path).
    """
    rendered = renderer.render_single_file(pipeline)
    default_name, dir_ext = SINGLE_FILE_OUTPUT_POLICY.get(output_format, (None, output_format))

    if output_path is not None:
        # User-specified path always wins. Treat directories as "put a default
        # filename in here" so `-o some_dir/` still works.
        if output_path.is_dir():
            filename = default_name or f"{source_file.stem}.{dir_ext}"
            return output_path / filename, rendered
        return output_path, rendered

    if default_name is not None:
        return source_file.parent / default_name, rendered
    # json / yaml / table → stdout
    return None, rendered
