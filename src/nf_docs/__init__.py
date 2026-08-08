"""
nf-docs: Generate API documentation for Nextflow pipelines.

This tool queries the Nextflow Language Server to extract docstrings,
type information, and structure from Nextflow pipelines, producing
documentation similar to Sphinx for Python or Javadoc for Java.

As well as the ``nf-docs`` command-line tool, this package is usable as a
library:

    >>> import nf_docs
    >>> pipeline = nf_docs.extract("./my_pipeline")  # doctest: +SKIP
    >>> markdown = nf_docs.render(pipeline, "markdown")  # doctest: +SKIP

The names re-exported here, together with :mod:`nf_docs.models`, are the
supported public API. Anything else - including underscore-prefixed helpers and
the Language Server internals - may change between releases.

Everything except the data models is resolved lazily (PEP 562), so
``import nf_docs`` stays cheap for callers that only want the models or the
version. Touching any other name pulls in its module on first access.
"""

from typing import TYPE_CHECKING, Any

try:
    from importlib.metadata import version

    __version__ = version("nf-docs")
except Exception:
    __version__ = "unknown"

# The models are cheap (dataclasses and stdlib only) and are what most callers
# reach for first, so they stay eager.
from nf_docs.models import (
    ConfigParam,
    Function,
    FunctionParam,
    Pipeline,
    PipelineInput,
    PipelineMetadata,
    Process,
    ProcessInput,
    ProcessOutput,
    Workflow,
    WorkflowInput,
    WorkflowOutput,
)

if TYPE_CHECKING:
    # Imported for type checkers and IDEs only; at runtime __getattr__ below
    # resolves these on first use.
    from nf_docs.api import extract, generate, render
    from nf_docs.cache import PipelineCache
    from nf_docs.config import NfDocsConfig, load_config
    from nf_docs.extractor import ExtractionError, PipelineExtractor, find_pipeline_root
    from nf_docs.lsp_client import LSPError
    from nf_docs.progress import ExtractionPhase, ProgressCallbackType, ProgressUpdate
    from nf_docs.renderers import (
        BaseRenderer,
        HTMLRenderer,
        JSONRenderer,
        MarkdownRenderer,
        TableRenderer,
        YAMLRenderer,
        get_renderer,
    )

# Public name -> module that defines it. Pulling in nf_docs.renderers costs
# jinja2, markdown and pygments; nf_docs.lsp_client costs httpx. Callers that
# only want the models shouldn't pay for either.
_LAZY_EXPORTS: dict[str, str] = {
    "extract": "nf_docs.api",
    "render": "nf_docs.api",
    "generate": "nf_docs.api",
    "PipelineCache": "nf_docs.cache",
    "NfDocsConfig": "nf_docs.config",
    "load_config": "nf_docs.config",
    "ExtractionError": "nf_docs.extractor",
    "PipelineExtractor": "nf_docs.extractor",
    "find_pipeline_root": "nf_docs.extractor",
    "LSPError": "nf_docs.lsp_client",
    "ExtractionPhase": "nf_docs.progress",
    "ProgressCallbackType": "nf_docs.progress",
    "ProgressUpdate": "nf_docs.progress",
    "BaseRenderer": "nf_docs.renderers",
    "HTMLRenderer": "nf_docs.renderers",
    "JSONRenderer": "nf_docs.renderers",
    "MarkdownRenderer": "nf_docs.renderers",
    "TableRenderer": "nf_docs.renderers",
    "YAMLRenderer": "nf_docs.renderers",
    "get_renderer": "nf_docs.renderers",
}


def __getattr__(name: str) -> Any:
    """Resolve a lazily-exported name on first access (PEP 562)."""
    module_name = _LAZY_EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    import importlib

    value = getattr(importlib.import_module(module_name), name)
    globals()[name] = value  # cache, so __getattr__ runs once per name
    return value


def __dir__() -> list[str]:
    """Include the lazy exports in dir() and tab completion."""
    return sorted({*globals(), *_LAZY_EXPORTS})


__all__ = [
    "__version__",
    # High-level API
    "extract",
    "render",
    "generate",
    # Extraction
    "PipelineExtractor",
    "ExtractionError",
    "LSPError",
    "find_pipeline_root",
    "PipelineCache",
    # Configuration
    "NfDocsConfig",
    "load_config",
    # Progress reporting
    "ProgressUpdate",
    "ProgressCallbackType",
    "ExtractionPhase",
    # Rendering
    "get_renderer",
    "BaseRenderer",
    "HTMLRenderer",
    "MarkdownRenderer",
    "TableRenderer",
    "JSONRenderer",
    "YAMLRenderer",
    # Models
    "Pipeline",
    "PipelineMetadata",
    "PipelineInput",
    "ConfigParam",
    "Workflow",
    "Process",
    "Function",
    "FunctionParam",
    "ProcessInput",
    "ProcessOutput",
    "WorkflowInput",
    "WorkflowOutput",
]
