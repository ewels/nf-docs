"""
Output renderers for nf-docs.

This package contains renderers for different output formats:
- JSON: Structured data, machine-readable
- YAML: Structured data, human-friendly
- Markdown: Documentation files
- HTML: Self-contained static site
 Table: Compact Markdown tables (terraform-docs style)
"""

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
    "get_renderer",
]


def get_renderer(format: str) -> type[BaseRenderer]:
    """
    Get the renderer class for a given format.

    Args:
        format: Output format (json, yaml, markdown, html)

    Returns:
        Renderer class

    Raises:
        ValueError: If format is not supported
    """
    renderers = {
        "json": JSONRenderer,
        "yaml": YAMLRenderer,
        "markdown": MarkdownRenderer,
        "md": MarkdownRenderer,
        "html": HTMLRenderer,
        "table": TableRenderer,
    }

    format_lower = format.lower()
    if format_lower not in renderers:
        supported = ", ".join(sorted(set(renderers.keys())))
        raise ValueError(f"Unsupported format: {format}. Supported formats: {supported}")

    return renderers[format_lower]
