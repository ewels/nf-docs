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
from nf_docs.extractor import ExtractionError, PipelineExtractor
from nf_docs.lsp_client import LSPError
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
    """
    pass


@main.command()
@click.argument("pipeline_path", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["json", "yaml", "markdown", "md", "html", "table"], case_sensitive=False),
    default="html",
    help="Output format: json, yaml, markdown (or md), html, table (default: html)",
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

    PIPELINE_PATH is the path to the Nextflow pipeline directory.

    Examples:

        # Generate Markdown docs
        nf-docs generate . --format markdown --output docs/

        # Generate JSON to stdout
        nf-docs generate . --format json

        # Generate HTML site with custom title
        nf-docs generate ./my-pipeline --format html -o site/ --title "My Pipeline"
    """
    setup_logging(verbose)

    # Normalize format aliases
    if output_format == "md":
        output_format = "markdown"

    try:
        with ExtractionProgressDisplay(console) as progress_display:
            # Extract documentation
            extractor = PipelineExtractor(
                workspace_path=pipeline_path,
                language_server_jar=language_server,
                nextflow_path=nextflow_path,
                use_cache=True,
                force_refresh=no_cache,
                progress_callback=progress_display.callback,
            )

            pipeline = extractor.extract()

        # Check if any content was found
        if not pipeline.has_content():
            console.print("[yellow]No Nextflow pipeline content found in this directory.[/yellow]")
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

            # Determine output
            if output_path:
                # Write to file/directory
                if output_format in ("markdown", "html", "table"):
                    created_files = renderer.render_to_directory(pipeline, output_path)
                    progress.update(task, description="Rendering complete")
                else:
                    # JSON/YAML - write to single file
                    # If output_path is a directory, use default filename
                    if output_path.is_dir():
                        ext = "json" if output_format == "json" else "yaml"
                        output_file = output_path / f"pipeline.{ext}"
                    else:
                        output_file = output_path
                        output_file.parent.mkdir(parents=True, exist_ok=True)
                    renderer.render_to_file(pipeline, output_file)
                    progress.update(task, description="Rendering complete")
            else:
                # Write to stdout or default directory
                if output_format in ("json", "yaml"):
                    pass  # Will write to stdout after progress
                else:
                    # Write to default directory
                    default_dir = pipeline_path / "docs"
                    created_files = renderer.render_to_directory(pipeline, default_dir)
                    progress.update(task, description="Rendering complete")

        # Output results after progress display is gone
        if output_path:
            if output_format in ("markdown", "html", "table"):
                file_word = "file" if len(created_files) == 1 else "files"
                console.print(
                    f"[green]Created {len(created_files)} {file_word} in {output_path}[/green]"
                )
                for f in created_files:
                    # Show path relative to current directory
                    try:
                        rel_path = f.relative_to(Path.cwd())
                        console.print(f"  - ./{rel_path}")
                    except ValueError:
                        console.print(f"  - {f}")
            else:
                console.print(f"[green]Written to {output_file}[/green]")
        else:
            if output_format in ("json", "yaml"):
                # Write to stdout
                click.echo(renderer.render(pipeline))
            else:
                file_word = "file" if len(created_files) == 1 else "files"
                console.print(
                    f"[green]Created {len(created_files)} {file_word} in {default_dir}[/green]"
                )
                for f in created_files:
                    # Show path relative to current directory
                    try:
                        rel_path = f.relative_to(Path.cwd())
                        console.print(f"  - ./{rel_path}")
                    except ValueError:
                        console.print(f"  - {f}")

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


if __name__ == "__main__":
    main()
