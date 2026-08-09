"""
Output renderers for nf-docs.

This package contains renderers for different output formats:
- JSON: Structured data, machine-readable
- YAML: Structured data, human-friendly
- Markdown: Documentation files
- HTML: Self-contained static site
 Table: Compact Markdown tables (terraform-docs style)
"""

from nf_docs.output import normalize_format, supported_formats
from nf_docs.renderers.base import BaseRenderer
from nf_docs.renderers.html import HTMLRenderer
from nf_docs.renderers.json import JSONRenderer
from nf_docs.renderers.markdown import MarkdownRenderer
from nf_docs.renderers.table import TableRenderer
from nf_docs.renderers.yaml import YAMLRenderer

__all__ = [
    "BaseRenderer",
    "TableRenderer",
    "JSONRenderer",
    "YAMLRenderer",
    "MarkdownRenderer",
    "HTMLRenderer",
    "RENDERERS",
    "get_renderer",
]


# Canonical format name -> renderer class. Aliases (e.g. "md") are resolved by
# ``nf_docs.output.normalize_format`` before lookup, so they live in one place.
RENDERERS: dict[str, type[BaseRenderer]] = {
    "json": JSONRenderer,
    "yaml": YAMLRenderer,
    "markdown": MarkdownRenderer,
    "html": HTMLRenderer,
    "table": TableRenderer,
}


def get_renderer(format: str) -> type[BaseRenderer]:
    """
    Get the renderer class for a given format.

    Args:
        format: Output format (json, yaml, markdown/md, html, table)

    Returns:
        Renderer class

    Raises:
        ValueError: If format is not supported
    """
    canonical = normalize_format(format)
    if canonical not in RENDERERS:
        supported = ", ".join(supported_formats())
        raise ValueError(f"Unsupported format: {format}. Supported formats: {supported}")

    return RENDERERS[canonical]
