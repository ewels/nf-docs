"""
YAML renderer for nf-docs.

Outputs pipeline documentation as structured YAML data.
"""

import yaml

from nf_docs.models import Pipeline
from nf_docs.renderers.base import BaseRenderer


class YAMLRenderer(BaseRenderer):
    """
    Render pipeline documentation as YAML.

    This format is human-readable and suitable for:
    - Configuration files
    - Manual editing
    - Integration with YAML-based tools
    """

    def __init__(
        self,
        title: str | None = None,
        default_flow_style: bool = False,
        *,
        include_generation_info: bool = True,
    ):
        """
        Initialize the YAML renderer.

        Args:
            title: Optional custom title (included in output)
            default_flow_style: Use flow style for sequences/mappings
            include_generation_info: Accepted for consistency with the other
                renderers. YAML output carries no generation metadata, so it is
                already reproducible either way.
        """
        super().__init__(title, include_generation_info=include_generation_info)
        self.default_flow_style = default_flow_style

    def render(self, pipeline: Pipeline) -> str:
        """
        Render the pipeline to YAML.

        Args:
            pipeline: The Pipeline model to render

        Returns:
            YAML string
        """
        data = pipeline.to_dict()

        # Add custom title if provided
        if self.title:
            data["pipeline"]["name"] = self.title

        return yaml.dump(
            data,
            default_flow_style=self.default_flow_style,
            allow_unicode=True,
            sort_keys=False,
            width=100,
        )

    def render_pages(self, pipeline: Pipeline) -> dict[str, str]:
        """
        Render the pipeline as a single ``<pipeline name>-api.yaml`` file.

        Args:
            pipeline: The Pipeline model to render

        Returns:
            Mapping with one entry: the YAML file name and its content
        """
        return {self._api_filename(pipeline, "yaml"): self.render(pipeline)}
