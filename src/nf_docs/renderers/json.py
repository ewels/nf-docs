"""
JSON renderer for nf-docs.

Outputs pipeline documentation as structured JSON data.
"""

import json

from nf_docs.generation_info import get_generation_info
from nf_docs.models import Pipeline
from nf_docs.renderers.base import BaseRenderer


class JSONRenderer(BaseRenderer):
    """
    Render pipeline documentation as JSON.

    This format is machine-readable and suitable for:
    - Integration with other tools
    - Custom post-processing
    - API responses
    """

    def __init__(
        self,
        title: str | None = None,
        indent: int = 2,
        *,
        include_generation_info: bool = True,
    ):
        """
        Initialize the JSON renderer.

        Args:
            title: Optional custom title (included in output)
            indent: JSON indentation level (default: 2)
            include_generation_info: Whether to include the ``generated_by``
                key, which carries a timestamp
        """
        super().__init__(title, include_generation_info=include_generation_info)
        self.indent = indent

    def render(self, pipeline: Pipeline) -> str:
        """
        Render the pipeline to JSON.

        Args:
            pipeline: The Pipeline model to render

        Returns:
            JSON string
        """
        data = pipeline.to_dict()

        # Add custom title if provided
        if self.title:
            data["pipeline"]["name"] = self.title

        # Add generation metadata
        if self.include_generation_info:
            data["generated_by"] = get_generation_info()

        return json.dumps(data, indent=self.indent, ensure_ascii=False)

    def render_pages(self, pipeline: Pipeline) -> dict[str, str]:
        """
        Render the pipeline as a single ``<pipeline name>-api.json`` file.

        Args:
            pipeline: The Pipeline model to render

        Returns:
            Mapping with one entry: the JSON file name and its content
        """
        return {self._api_filename(pipeline, "json"): self.render(pipeline)}
