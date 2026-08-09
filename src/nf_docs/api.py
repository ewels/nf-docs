"""
High-level Python API for nf-docs.

This module is the supported entry point for using nf-docs as a library rather
than a command-line tool. It wraps :class:`~nf_docs.extractor.PipelineExtractor`
and the renderers in three functions:

- :func:`extract` — read a pipeline (or a single module) into a
  :class:`~nf_docs.models.Pipeline` model
- :func:`render` — turn a ``Pipeline`` into a string in a given format
- :func:`generate` — do both and write the result to disk

Unlike the CLI, these functions never print to the console and never exit the
process; they raise exceptions and return values instead.

Example:
    >>> import nf_docs
    >>> pipeline = nf_docs.extract("./my_pipeline")  # doctest: +SKIP
    >>> markdown = nf_docs.render(pipeline, "markdown")  # doctest: +SKIP
"""

from pathlib import Path
from typing import Any

from nf_docs.config import NfDocsConfig
from nf_docs.extractor import PipelineExtractor, find_pipeline_root
from nf_docs.models import Pipeline
from nf_docs.output import (
    DIRECTORY_FORMATS,
    default_output_dir,
    normalize_format,
    resolve_data_file_path,
    resolve_single_file_path,
    resolve_source,
)
from nf_docs.progress import ProgressCallbackType
from nf_docs.renderers import get_renderer

__all__ = ["extract", "render", "generate"]


def _extract_resolved(
    source: Path,
    single_file_mode: bool,
    *,
    config: NfDocsConfig | None = None,
    language_server_jar: str | Path | None = None,
    nextflow_path: str = "nextflow",
    use_cache: bool = True,
    force_refresh: bool = False,
    progress_callback: ProgressCallbackType | None = None,
) -> Pipeline:
    """
    Extract from an already-resolved source, so resolution happens exactly once.

    Args:
        source: Resolved path, as returned by ``resolve_source``
        single_file_mode: Whether ``source`` is a single ``.nf`` file

    Returns:
        The extracted Pipeline model
    """
    extractor = PipelineExtractor(
        workspace_path=find_pipeline_root(source) if single_file_mode else source,
        language_server_jar=language_server_jar,
        nextflow_path=nextflow_path,
        use_cache=use_cache,
        force_refresh=force_refresh,
        progress_callback=progress_callback,
        target_file=source if single_file_mode else None,
        config=config,
    )
    return extractor.extract()


def extract(
    path: str | Path,
    *,
    config: NfDocsConfig | None = None,
    language_server_jar: str | Path | None = None,
    nextflow_path: str = "nextflow",
    use_cache: bool = True,
    force_refresh: bool = False,
    progress_callback: ProgressCallbackType | None = None,
) -> Pipeline:
    """
    Extract documentation from a Nextflow pipeline or a single module file.

    ``path`` may be a pipeline directory or a single ``.nf`` file. A directory
    containing only a module-style ``main.nf`` (process definitions, no
    workflow, no pipeline config) is auto-detected as a single module — the same
    rule the ``nf-docs generate`` command applies.

    Args:
        path: Path to a Nextflow pipeline directory or a single ``.nf`` file
        config: Configuration to use. Defaults to :class:`NfDocsConfig` defaults.
            Unlike the CLI, the user's ``~/.config/nf-docs/config.yaml`` is *not*
            read automatically — pass ``config=load_config()`` to opt in.
        language_server_jar: Path to the Nextflow Language Server JAR. Downloaded
            on demand if not given.
        nextflow_path: Path to the Nextflow executable
        use_cache: Whether to read and write the extraction cache
        force_refresh: Re-extract even when a cache entry exists
        progress_callback: Called with :class:`~nf_docs.progress.ProgressUpdate`
            objects as extraction proceeds

    Returns:
        The extracted :class:`~nf_docs.models.Pipeline` model

    Raises:
        ValueError: If ``path`` is a file that isn't a ``.nf`` file
        ExtractionError: If extraction fails
        LSPError: If the Language Server cannot be started or queried
    """
    source, single_file_mode = resolve_source(path)
    return _extract_resolved(
        source,
        single_file_mode,
        config=config,
        language_server_jar=language_server_jar,
        nextflow_path=nextflow_path,
        use_cache=use_cache,
        force_refresh=force_refresh,
        progress_callback=progress_callback,
    )


def render(
    pipeline: Pipeline,
    output_format: str = "html",
    *,
    title: str | None = None,
    single_file: bool = False,
    **renderer_kwargs: Any,
) -> str:
    """
    Render a Pipeline model to a string.

    Args:
        pipeline: The Pipeline model to render
        output_format: One of ``html``, ``markdown`` (or ``md``), ``table``,
            ``json``, ``yaml``
        title: Custom documentation title. Defaults to the pipeline name.
        single_file: Render the focused single-document form used for modules
            rather than the full pipeline form
        **renderer_kwargs: Extra keyword arguments for the specific renderer,
            e.g. ``use_tailwind`` (HTML), ``indent`` (JSON),
            ``default_flow_style`` (YAML)

    Returns:
        The rendered documentation as a string

    Raises:
        ValueError: If ``output_format`` is not supported
    """
    renderer = get_renderer(normalize_format(output_format))(title=title, **renderer_kwargs)
    if single_file:
        return renderer.render_single_file(pipeline)
    return renderer.render(pipeline)


def generate(
    path: str | Path,
    *,
    output_format: str = "html",
    output: str | Path | None = None,
    title: str | None = None,
    config: NfDocsConfig | None = None,
    language_server_jar: str | Path | None = None,
    nextflow_path: str = "nextflow",
    use_cache: bool = True,
    force_refresh: bool = False,
    progress_callback: ProgressCallbackType | None = None,
    **renderer_kwargs: Any,
) -> list[Path]:
    """
    Extract a pipeline and write its documentation to disk.

    This is the programmatic equivalent of ``nf-docs generate``. Unlike the CLI,
    it always writes files rather than streaming to stdout — use :func:`extract`
    plus :func:`render` if you want the documentation as a string.

    When ``output`` is not given, the defaults mirror the CLI: ``<pipeline>/docs``
    for a whole pipeline, and a file alongside the source (e.g. ``README.md``)
    when documenting a single module.

    Args:
        path: Path to a Nextflow pipeline directory or a single ``.nf`` file
        output_format: One of ``html``, ``markdown`` (or ``md``), ``table``,
            ``json``, ``yaml``
        output: Output file or directory. Defaults to the CLI's conventions.
        title: Custom documentation title
        config, language_server_jar, nextflow_path, use_cache, force_refresh,
            progress_callback: See :func:`extract`.
        **renderer_kwargs: Extra keyword arguments for the specific renderer

    Returns:
        The list of files written, in the order they were created

    Raises:
        ValueError: If ``path`` or ``output_format`` is invalid
        ExtractionError: If extraction fails
        LSPError: If the Language Server cannot be started or queried
    """
    canonical_format = normalize_format(output_format)
    renderer = get_renderer(canonical_format)(title=title, **renderer_kwargs)
    source, single_file_mode = resolve_source(path)
    output_path = Path(output) if output is not None else None

    pipeline = _extract_resolved(
        source,
        single_file_mode,
        config=config,
        language_server_jar=language_server_jar,
        nextflow_path=nextflow_path,
        use_cache=use_cache,
        force_refresh=force_refresh,
        progress_callback=progress_callback,
    )

    if single_file_mode:
        output_file = resolve_single_file_path(source, canonical_format, output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(renderer.render_single_file(pipeline), encoding="utf-8")
        return [output_file]

    if canonical_format in DIRECTORY_FORMATS:
        return renderer.render_to_directory(
            pipeline, output_path if output_path is not None else default_output_dir(source)
        )

    output_file = resolve_data_file_path(source, canonical_format, output_path)
    renderer.render_to_file(pipeline, output_file)
    return [output_file]
