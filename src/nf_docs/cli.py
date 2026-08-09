"""
Command-line interface for nf-docs.

This module provides the CLI entry points for generating Nextflow
pipeline documentation.
"""

import logging
import sys
from pathlib import Path

import rich_click as click
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TextColumn,
)

from nf_docs import __version__
from nf_docs.api import extract as extract_pipeline
from nf_docs.config import (
    DEFAULT_CONFIG,
    NfDocsConfig,
    get_config_path,
    get_example_config,
    load_config,
)
from nf_docs.extractor import ExtractionError, PipelineExtractor
from nf_docs.lsp_client import LSPError
from nf_docs.output import (
    DIRECTORY_FORMATS,
    SUPPORTED_FORMATS,
    default_output_dir,
    normalize_format,
    resolve_data_file_path,
    resolve_single_file_path,
    resolve_source,
    streams_by_default,
)
from nf_docs.progress import ProgressUpdate
from nf_docs.renderers import get_renderer

console = Console()


class ExtractionProgressDisplay:
    """
    Manages the rich progress display for extraction.

    Creates appropriate progress bars based on the extraction phase.
    """

    def __init__(self, console: Console):
        self.console = console
        self._progress: Progress | None = None
        self._task_id: TaskID | None = None
        self._in_bar_mode: bool = False

    def __enter__(self) -> "ExtractionProgressDisplay":
        self._create_spinner_progress()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._progress:
            self._progress.__exit__(exc_type, exc_val, exc_tb)

    def _create_spinner_progress(self) -> None:
        """Create a spinner-based progress display for indeterminate phases."""
        if self._progress:
            self._progress.__exit__(None, None, None)

        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TextColumn("[dim]{task.fields[detail]}[/dim]"),
            console=self.console,
            transient=True,
        )
        self._progress.__enter__()
        self._task_id = self._progress.add_task("Starting...", detail="")
        self._in_bar_mode = False

    def _create_bar_progress(self) -> None:
        """Create a bar-based progress display for determinate phases."""
        if self._progress:
            self._progress.__exit__(None, None, None)

        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
            TextColumn("[dim]{task.fields[detail]}[/dim]"),
            console=self.console,
            transient=True,
        )
        self._progress.__enter__()
        self._task_id = self._progress.add_task("Processing...", total=100, detail="")
        self._in_bar_mode = True

    def update(self, progress_update: ProgressUpdate) -> None:
        """Update the progress display based on the extraction progress."""
        if not self._progress or self._task_id is None:
            return

        message = progress_update.message
        detail = progress_update.detail or ""

        if progress_update.has_progress:
            # Need bar mode for numeric progress
            if not self._in_bar_mode:
                self._create_bar_progress()

            self._progress.update(
                self._task_id,
                description=message,
                completed=progress_update.current,
                total=progress_update.total,
                detail=detail,
            )
        else:
            # Need spinner mode for indeterminate progress
            if self._in_bar_mode:
                self._create_spinner_progress()

            self._progress.update(
                self._task_id,
                description=message,
                detail=detail,
            )

    def callback(self, update: ProgressUpdate) -> None:
        """Callback function for the extractor."""
        self.update(update)


def setup_logging(verbose: bool) -> None:
    """Configure logging based on verbosity."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[RichHandler(console=console, show_time=False, show_path=False)],
    )


@click.group()
@click.version_option(version=__version__, prog_name="nf-docs")
def main() -> None:
    """
    nf-docs: Generate API documentation for Nextflow pipelines.

    This tool extracts documentation from Nextflow pipelines by querying
    the Nextflow Language Server, parsing nextflow_schema.json, and
    analyzing configuration files.

    Examples:

        # Generate Markdown documentation
        nf-docs generate /path/to/pipeline --format markdown --output docs/

        # Generate JSON output
        nf-docs generate . --format json > pipeline-api.json

        # Generate HTML site
        nf-docs generate . --format html --output site/

        # Generate a README for a single module file
        nf-docs generate modules/mytool/subtools/main.nf --format md
    """
    pass


def _display_path(path: Path) -> str:
    """Render ``path`` relative to the current working directory when possible."""
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return str(path)


def _resolve_output_format(output_format: str | None, config: NfDocsConfig) -> str:
    """
    Work out which output format to use.

    An explicit ``-f/--format`` always wins. With no flag we fall back to the
    config file's ``default_format``, warning and using the built-in default if
    that value isn't a format we can render.

    Args:
        output_format: The value of ``-f/--format``, or None if it wasn't given
        config: The user's loaded configuration

    Returns:
        A canonical format name
    """
    if output_format is not None:
        return normalize_format(output_format)

    configured = normalize_format(config.default_format)
    if configured in SUPPORTED_FORMATS:
        return configured

    fallback = normalize_format(DEFAULT_CONFIG["default_format"])
    console.print(
        f"[yellow]Ignoring unknown default_format {config.default_format!r} "
        f"in {get_config_path()}, using {fallback}[/yellow]"
    )
    return fallback


@main.command()
@click.argument("pipeline_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["json", "yaml", "markdown", "md", "html", "table"], case_sensitive=False),
    default=None,
    help=(
        "Output format: json, yaml, markdown (or md), html, table "
        "(default: the config file's default_format, otherwise html)"
    ),
)
@click.option(
    "--output",
    "-o",
    "output_path",
    type=click.Path(path_type=Path),
    help="Output file or directory. If not specified, writes to stdout (for json/yaml) or ./docs/ (for markdown/html)",
)
@click.option(
    "--title",
    "-t",
    help="Custom title for the documentation",
)
@click.option(
    "--language-server",
    "language_server",
    type=click.Path(exists=True, path_type=Path),
    help="Path to the Nextflow Language Server JAR file",
)
@click.option(
    "--nextflow-path",
    default="nextflow",
    help="Path to the Nextflow executable (default: nextflow)",
)
@click.option(
    "--no-cache",
    is_flag=True,
    help="Force re-extraction from pipeline files, ignoring cached results",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output",
)
def generate(
    pipeline_path: Path,
    output_format: str,
    output_path: Path | None,
    title: str | None,
    language_server: Path | None,
    nextflow_path: str,
    no_cache: bool,
    verbose: bool,
) -> None:
    """
    Generate documentation for a Nextflow pipeline.

    PIPELINE_PATH is the path to either a Nextflow pipeline directory or a
    single ``.nf`` file (e.g. a module / subworkflow ``main.nf``).

    Examples:

        # Generate Markdown docs
        nf-docs generate . --format markdown --output docs/

        # Generate JSON to stdout
        nf-docs generate . --format json

        # Generate HTML site with custom title
        nf-docs generate ./my-pipeline --format html -o site/ --title "My Pipeline"

        # Single-file mode: write README.md next to a module's main.nf
        nf-docs generate modules/mytool/subtools/main.nf --format md
    """
    setup_logging(verbose)

    # The CLI honours the user's ~/.config/nf-docs/config.yaml; the Python API
    # deliberately does not (see nf_docs.api.extract).
    user_config = load_config()

    # An explicit --format wins; otherwise fall back to the configured default.
    output_format = _resolve_output_format(output_format, user_config)

    # Decide single-file vs directory mode up front. A directory holding only a
    # module-style main.nf is auto-detected as a single module.
    try:
        pipeline_path, single_file_mode = resolve_source(pipeline_path)
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)

    if single_file_mode:
        logging.getLogger("nf_docs").info("Generating single module documentation")

    try:
        with ExtractionProgressDisplay(console) as progress_display:
            pipeline = extract_pipeline(
                pipeline_path,
                config=user_config,
                language_server_jar=language_server,
                nextflow_path=nextflow_path,
                force_refresh=no_cache,
                progress_callback=progress_display.callback,
            )

        # Check if any content was found
        if not pipeline.has_content():
            if single_file_mode:
                console.print(f"[yellow]No Nextflow content found in {pipeline_path}.[/yellow]")
                console.print(
                    "Ensure the file defines at least one process, workflow, or function."
                )
            else:
                console.print(
                    "[yellow]No Nextflow pipeline content found in this directory.[/yellow]"
                )
                console.print(
                    "Ensure the directory contains Nextflow files (.nf), "
                    "nextflow_schema.json, or nextflow.config."
                )
            sys.exit(1)

        # Rendering phase (quick, use simple spinner)
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task(f"Rendering {output_format}...", total=None)
            renderer_class = get_renderer(output_format)
            renderer = renderer_class(title=title)

            if single_file_mode:
                rendered = renderer.render_single_file(pipeline)
                # Formats with no natural single-file name go to stdout unless
                # the user asked for a specific output path.
                output_file = (
                    None
                    if output_path is None and streams_by_default(output_format)
                    else resolve_single_file_path(pipeline_path, output_format, output_path)
                )
                progress.update(task, description="Rendering complete")
            elif output_path:
                # Write to file/directory
                if output_format in DIRECTORY_FORMATS:
                    created_files = renderer.render_to_directory(pipeline, output_path)
                else:
                    # JSON/YAML - write to a single data file
                    output_file = resolve_data_file_path(pipeline_path, output_format, output_path)
                    renderer.render_to_file(pipeline, output_file)
                progress.update(task, description="Rendering complete")
            else:
                # Write to stdout or default directory
                if output_format in DIRECTORY_FORMATS:
                    default_dir = default_output_dir(pipeline_path)
                    created_files = renderer.render_to_directory(pipeline, default_dir)
                    progress.update(task, description="Rendering complete")
                # json/yaml stream to stdout after the progress display is gone

        # Output results after progress display is gone
        if single_file_mode:
            if output_file is None:
                # Stdout for json/yaml/table when no --output
                click.echo(rendered)
            else:
                output_file.parent.mkdir(parents=True, exist_ok=True)
                output_file.write_text(rendered, encoding="utf-8")
                console.print(
                    f"[green]Created 1 file in {_display_path(output_file.parent)}/[/green]"
                )
                console.print(f"  - {_display_path(output_file)}")
        elif output_path:
            if output_format in DIRECTORY_FORMATS:
                file_word = "file" if len(created_files) == 1 else "files"
                console.print(
                    f"[green]Created {len(created_files)} {file_word} in {output_path}[/green]"
                )
                for f in created_files:
                    console.print(f"  - ./{_display_path(f)}")
            else:
                console.print(f"[green]Written to {output_file}[/green]")
        else:
            if output_format in DIRECTORY_FORMATS:
                file_word = "file" if len(created_files) == 1 else "files"
                console.print(
                    f"[green]Created {len(created_files)} {file_word} in {default_dir}[/green]"
                )
                for f in created_files:
                    console.print(f"  - ./{_display_path(f)}")
            else:
                # Write to stdout
                click.echo(renderer.render(pipeline))

    except LSPError as e:
        console.print(f"[red]Language Server error: {e}[/red]")
        sys.exit(1)
    except ExtractionError as e:
        console.print(f"[red]Extraction error: {e}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if verbose:
            console.print_exception()
        sys.exit(1)


@main.command()
@click.argument("pipeline_path", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output",
)
def inspect(pipeline_path: Path, verbose: bool) -> None:
    """
    Inspect a Nextflow pipeline and show summary information.

    This command shows what nf-docs can extract from the pipeline
    without generating full documentation.

    PIPELINE_PATH is the path to the Nextflow pipeline directory.
    """
    setup_logging(verbose)

    try:
        with ExtractionProgressDisplay(console) as progress_display:
            extractor = PipelineExtractor(
                workspace_path=pipeline_path,
                progress_callback=progress_display.callback,
                config=load_config(),
            )

            pipeline = extractor.extract()

        # Display summary
        console.print()
        console.print(f"[bold]Pipeline:[/bold] {pipeline.metadata.name or pipeline_path.name}")

        if pipeline.metadata.version:
            console.print(f"[bold]Version:[/bold] {pipeline.metadata.version}")

        if pipeline.metadata.description:
            desc = pipeline.metadata.description
            if len(desc) > 100:
                desc = desc[:100] + "..."
            console.print(f"[bold]Description:[/bold] {desc}")

        console.print()
        console.print("[bold]Contents:[/bold]")

        # Show files found
        nf_files = list(pipeline_path.rglob("*.nf"))
        console.print(f"  Nextflow files: {len(nf_files)}")

        # Show schema
        from nf_docs.schema_parser import find_schema_file

        schema_file = find_schema_file(pipeline_path)
        if schema_file:
            console.print(f"  Schema file: {schema_file.relative_to(pipeline_path)}")
        else:
            console.print("  Schema file: [yellow]not found[/yellow]")

        # Show config
        config_file = pipeline_path / "nextflow.config"
        if config_file.exists():
            console.print("  Config file: nextflow.config")
        else:
            console.print("  Config file: [yellow]not found[/yellow]")

        console.print()
        console.print("[bold]Extracted:[/bold]")
        console.print(f"  Input parameters: {len(pipeline.inputs)}")
        console.print(f"  Config parameters: {len(pipeline.config_params)}")
        console.print(f"  Workflows: {len(pipeline.workflows)}")
        console.print(f"  Processes: {len(pipeline.processes)}")
        console.print(f"  Functions: {len(pipeline.functions)}")

        # Show some details
        if pipeline.workflows:
            console.print()
            console.print("[bold]Workflows:[/bold]")
            for wf in pipeline.workflows[:5]:
                name = wf.name or "(entry)"
                entry = " [green](entry)[/green]" if wf.is_entry else ""
                console.print(f"  - {name}{entry}")
            if len(pipeline.workflows) > 5:
                console.print(f"  ... and {len(pipeline.workflows) - 5} more")

        if pipeline.processes:
            console.print()
            console.print("[bold]Processes:[/bold]")
            for proc in pipeline.processes[:5]:
                console.print(f"  - {proc.name}")
            if len(pipeline.processes) > 5:
                console.print(f"  ... and {len(pipeline.processes) - 5} more")

        if pipeline.inputs:
            console.print()
            console.print("[bold]Input groups:[/bold]")
            groups = pipeline.get_input_groups()
            for group, inputs in groups.items():
                console.print(f"  - {group}: {len(inputs)} parameters")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if verbose:
            console.print_exception()
        sys.exit(1)


@main.command()
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Overwrite existing language server JAR",
)
def download_lsp(force: bool) -> None:
    """
    Download the Nextflow Language Server.

    This downloads the language server JAR file to the XDG data directory
    (~/.local/share/nf-docs/ by default) for use with the generate command.
    """
    from nf_docs.lsp_client import LANGUAGE_SERVER_JAR, get_xdg_data_home

    target_dir = get_xdg_data_home() / "nf-docs"
    target_file = target_dir / LANGUAGE_SERVER_JAR

    if target_file.exists() and not force:
        console.print(f"[yellow]Language server already exists at {target_file}[/yellow]")
        console.print("Use --force to re-download")
        return

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Downloading language server...", total=None)

            # Use the LSPClient's download method
            from nf_docs.lsp_client import LSPClient

            client = LSPClient.__new__(LSPClient)
            target_dir.mkdir(parents=True, exist_ok=True)

            if target_file.exists():
                target_file.unlink()

            client._download_language_server(target_file)
            progress.update(task, description="Download complete")

        console.print(f"[green]Downloaded to {target_file}[/green]")

    except Exception as e:
        console.print(f"[red]Download failed: {e}[/red]")
        sys.exit(1)


@main.command()
@click.option(
    "--all",
    "-a",
    "clear_all",
    is_flag=True,
    help="Clear all cached pipelines",
)
@click.argument(
    "pipeline_path",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    required=False,
)
def clear_cache(clear_all: bool, pipeline_path: Path | None) -> None:
    """
    Clear the extraction cache.

    By default, clears cache for a specific pipeline. Use --all to clear
    all cached pipelines.

    Examples:

        # Clear cache for a specific pipeline
        nf-docs clear-cache /path/to/pipeline

        # Clear all cached pipelines
        nf-docs clear-cache --all
    """
    from nf_docs.cache import PipelineCache

    cache = PipelineCache()

    if clear_all:
        cleared = cache.clear()
        console.print(f"[green]Cleared {cleared} cache file(s)[/green]")
    elif pipeline_path:
        cleared = cache.clear(pipeline_path)
        if cleared:
            console.print(f"[green]Cleared {cleared} cache file(s) for {pipeline_path}[/green]")
        else:
            console.print(f"[yellow]No cache found for {pipeline_path}[/yellow]")
    else:
        console.print("[red]Please specify a pipeline path or use --all[/red]")
        raise SystemExit(1)


@main.command()
@click.option(
    "--init",
    "init_config",
    is_flag=True,
    help="Create an example config file at the default location",
)
@click.option(
    "--show-example",
    is_flag=True,
    help="Print an example config file to stdout",
)
@click.option(
    "--path",
    is_flag=True,
    help="Print the config file path",
)
def config(init_config: bool, show_example: bool, path: bool) -> None:
    """
    Show or manage nf-docs configuration.

    Without options, shows the current configuration values.

    Examples:

        # Show current config
        nf-docs config

        # Show config file path
        nf-docs config --path

        # Print example config
        nf-docs config --show-example

        # Create config file with defaults
        nf-docs config --init
    """
    config_path = get_config_path()

    if path:
        console.print(str(config_path))
        return

    if show_example:
        click.echo(get_example_config())
        return

    if init_config:
        if config_path.exists():
            console.print(f"[yellow]Config file already exists at {config_path}[/yellow]")
            console.print("Edit it directly or delete it first to recreate.")
            return

        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(get_example_config(), encoding="utf-8")
        console.print(f"[green]Created config file at {config_path}[/green]")
        return

    # Default: show current config
    console.print(f"[bold]Config file:[/bold] {config_path}")
    if config_path.exists():
        console.print("[dim]  (file exists)[/dim]")
    else:
        console.print("[dim]  (using defaults - file does not exist)[/dim]")

    console.print()
    console.print("[bold]Current settings:[/bold]")

    for key, value in load_config().to_dict().items():
        if isinstance(value, list):
            if value:
                console.print(f"  {key}:")
                for item in value:
                    console.print(f"    - {item}")
            else:
                console.print(f"  {key}: []")
        elif isinstance(value, bool):
            console.print(f"  {key}: {str(value).lower()}")
        else:
            console.print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
