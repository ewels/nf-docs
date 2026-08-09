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
"""

try:
    from importlib.metadata import version

    __version__ = version("nf-docs")
except Exception:
    __version__ = "unknown"

from nf_docs.api import extract, generate, render, render_pages
from nf_docs.cache import PipelineCache
from nf_docs.config import NfDocsConfig, load_config
from nf_docs.extractor import ExtractionError, PipelineExtractor, find_pipeline_root
from nf_docs.lsp_client import LSPError
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

__all__ = [
    "__version__",
    # High-level API
    "extract",
    "render",
    "render_pages",
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
