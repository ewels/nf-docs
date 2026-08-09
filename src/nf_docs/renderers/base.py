"""
Base renderer class for nf-docs output formats.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TextIO

from nf_docs.generation_info import get_markdown_footer
from nf_docs.models import Pipeline


class BaseRenderer(ABC):
    """
    Abstract base class for output renderers.

    Renderers convert a Pipeline model into a specific output format.
    """

    def __init__(self, title: str | None = None, *, include_generation_info: bool = True):
        """
        Initialize the renderer.

        Args:
            title: Optional custom title for the documentation
            include_generation_info: Whether to embed generation metadata - the
                nf-docs version and the time of the run - in the output. Set it
                to ``False`` for byte-reproducible output, so that rendering the
                same pipeline twice produces the same bytes.
        """
        self.title = title
        self.include_generation_info = include_generation_info

    @abstractmethod
    def render(self, pipeline: Pipeline) -> str:
        """
        Render the pipeline to a string.

        Args:
            pipeline: The Pipeline model to render

        Returns:
            Rendered output as a string
        """
        pass

    @abstractmethod
    def render_pages(self, pipeline: Pipeline) -> dict[str, str]:
        """
        Render the pipeline to a mapping of file name to file content.

        This is the in-memory equivalent of :meth:`render_to_directory`: the
        keys are the names of the files that method would create, relative to
        the output directory, and the values are what it would write into them.
        Callers that already have somewhere to put the output - a static site
        generator, a build hook, a test - can use this instead of writing to a
        temporary directory and reading the files back.

        Which files appear depends on the pipeline. The Markdown renderer only
        emits ``config.md`` when there are config parameters, for example, so
        don't assume a fixed set of keys.

        Args:
            pipeline: The Pipeline model to render

        Returns:
            Mapping of file name to file content
        """
        pass

    def render_to_file(self, pipeline: Pipeline, output_path: str | Path) -> None:
        """
        Render the pipeline to a file.

        Args:
            pipeline: The Pipeline model to render
            output_path: Path to the output file
        """
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(self.render(pipeline), encoding="utf-8")

    def render_to_stream(self, pipeline: Pipeline, stream: TextIO) -> None:
        """
        Render the pipeline to a stream.

        Args:
            pipeline: The Pipeline model to render
            stream: Output stream to write to
        """
        stream.write(self.render(pipeline))

    def render_single_file(self, pipeline: Pipeline) -> str:
        """
        Render documentation for a single source file (e.g. a module README).

        Default implementation reuses ``render()``. Renderers that benefit from
        a more focused shape (e.g. Markdown) can override this.

        Args:
            pipeline: The Pipeline model to render (will only contain symbols
                from a single ``.nf`` file)

        Returns:
            Rendered output as a string
        """
        return self.render(pipeline)

    def get_title(self, pipeline: Pipeline) -> str:
        """Get the title to use for documentation."""
        if self.title:
            return self.title
        return pipeline.metadata.name or "Pipeline Documentation"

    def render_to_directory(self, pipeline: Pipeline, output_dir: str | Path) -> list[Path]:
        """
        Render the pipeline to a directory structure.

        Writes everything :meth:`render_pages` returns, in the order it returns
        it. Some formats (like Markdown) produce multiple files.

        Args:
            pipeline: The Pipeline model to render
            output_dir: Output directory path

        Returns:
            List of created file paths
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        created_files: list[Path] = []
        for filename, content in self.render_pages(pipeline).items():
            file_path = output_path / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
            created_files.append(file_path)

        return created_files

    def _api_filename(self, pipeline: Pipeline, extension: str) -> str:
        """Build the ``<pipeline name>-api.<extension>`` name used by data formats."""
        name = pipeline.metadata.name or "pipeline"
        clean_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
        return f"{clean_name}-api.{extension}"

    def _markdown_footer(self) -> str:
        """The generation footer for Markdown-flavoured output, or ``""`` if disabled."""
        if not self.include_generation_info:
            return ""
        return "\n\n" + get_markdown_footer()
