"""
Base renderer class for nf-docs output formats.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TextIO

from nf_docs.models import Pipeline


class BaseRenderer(ABC):
    """
    Abstract base class for output renderers.

    Renderers convert a Pipeline model into a specific output format.
    """

    def __init__(self, title: str | None = None):
        """
        Initialize the renderer.

        Args:
            title: Optional custom title for the documentation
        """
        self.title = title

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

    @abstractmethod
    def render_to_directory(self, pipeline: Pipeline, output_dir: str | Path) -> list[Path]:
        """
        Render the pipeline to a directory structure.

        Some formats (like Markdown) produce multiple files.

        Args:
            pipeline: The Pipeline model to render
            output_dir: Output directory path

        Returns:
            List of created file paths
        """
        pass
