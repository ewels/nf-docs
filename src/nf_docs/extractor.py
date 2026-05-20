"""
Data extraction and merging for Nextflow pipeline documentation.

This module coordinates extraction from all data sources:
- Language Server (processes, workflows, functions)
- nextflow_schema.json (typed input parameters)
- nextflow.config (config parameters)
- README.md (pipeline description)

And merges them into a unified Pipeline model.
"""

import logging
import re
import urllib.request
from pathlib import Path
from typing import Any

from nf_docs.cache import PipelineCache
from nf_docs.config import get_config
from nf_docs.config_parser import parse_config
from nf_docs.git_utils import GitInfo, build_source_url, get_git_info
from nf_docs.lsp_client import LSPClient, SymbolKind, parse_hover_content
from nf_docs.meta_parser import (
    ModuleMeta,
    SubworkflowMeta,
    parse_meta_for_file,
)
from nf_docs.models import (
    Function,
    FunctionParam,
    Pipeline,
    PipelineMetadata,
    Process,
    ProcessInput,
    ProcessOutput,
    Workflow,
    WorkflowInput,
    WorkflowOutput,
)
from nf_docs.nf_parser import (
    RETURN_KEY_PREFIX,
    RETURN_KEY_UNNAMED,
    enrich_outputs_from_source,
    parse_process_hover,
    parse_workflow_hover,
)
from nf_docs.progress import (
    ExtractionPhase,
    ProgressCallbackType,
    ProgressUpdate,
    null_progress,
)
from nf_docs.schema_parser import find_schema_file, parse_schema

logger = logging.getLogger(__name__)

# Cache for nf-core module URL checks to avoid repeated HTTP requests
_nfcore_module_url_cache: dict[str, str | None] = {}


def get_nfcore_module_url(file_path: str) -> str | None:
    """
    Check if a process file is an nf-core module and return its documentation URL.

    Args:
        file_path: Relative path to the process file (e.g., 'modules/nf-core/bbmap/bbsplit/main.nf')

    Returns:
        URL to nf-core module docs if valid, None otherwise
    """
    # Check if the file is in modules/nf-core/
    if not file_path.startswith("modules/nf-core/"):
        return None

    # Extract the module path after modules/nf-core/
    parts = file_path.split("/")
    if len(parts) < 4 or parts[-1] != "main.nf":
        return None

    # Get the module name parts (everything between 'nf-core' and 'main.nf')
    module_parts = parts[2:-1]  # e.g., ['bbmap', 'bbsplit']
    module_name = "_".join(module_parts)  # e.g., 'bbmap_bbsplit'

    # Check cache first
    if module_name in _nfcore_module_url_cache:
        return _nfcore_module_url_cache[module_name]

    # Build the nf-core module URL
    url = f"https://nf-co.re/modules/{module_name}/"

    # Check if the URL is accessible
    try:
        req = urllib.request.Request(url, method="HEAD")
        req.add_header("User-Agent", "nf-docs")
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                _nfcore_module_url_cache[module_name] = url
                logger.debug(f"Found nf-core module: {module_name}")
                return url
    except Exception as e:
        logger.debug(f"nf-core module check failed for {module_name}: {e}")

    _nfcore_module_url_cache[module_name] = None
    return None


class ExtractionError(Exception):
    """Exception raised when data extraction fails."""

    pass


class PipelineExtractor:
    """
    Extracts documentation from a Nextflow pipeline.

    Coordinates extraction from multiple sources and merges them
    into a unified Pipeline model.
    """

    def __init__(
        self,
        workspace_path: str | Path,
        language_server_jar: str | Path | None = None,
        nextflow_path: str = "nextflow",
        use_cache: bool = True,
        force_refresh: bool = False,
        progress_callback: ProgressCallbackType | None = None,
    ):
        """
        Initialize the extractor.

        Args:
            workspace_path: Path to the Nextflow pipeline workspace
            language_server_jar: Path to the language server JAR (optional)
            nextflow_path: Path to the Nextflow executable
            use_cache: Whether to use caching for extraction results
            force_refresh: Force re-extraction even if cache exists (still updates cache)
            progress_callback: Optional callback for progress updates
        """
        self.workspace_path = Path(workspace_path).resolve()
        self.language_server_jar = language_server_jar
        self.nextflow_path = nextflow_path
        self.cache = PipelineCache() if use_cache else None
        self.force_refresh = force_refresh
        self._progress = progress_callback or null_progress

    def extract(self) -> Pipeline:
        """
        Extract all documentation from the pipeline.

        Returns:
            Complete Pipeline model with all extracted information
        """
        # Display path relative to home dir for cleaner output
        try:
            display_path = f"~/{self.workspace_path.relative_to(Path.home())}"
        except ValueError:
            display_path = str(self.workspace_path)
        logger.info(f"Extracting documentation from: {display_path}")

        self._progress(
            ProgressUpdate(
                phase=ExtractionPhase.STARTING,
                message="Starting extraction...",
            )
        )

        # Check cache first (unless force_refresh is set)
        if self.cache and not self.force_refresh:
            self._progress(
                ProgressUpdate(
                    phase=ExtractionPhase.CHECKING_CACHE,
                    message="Checking cache...",
                )
            )
            cached = self.cache.get(self.workspace_path)
            if cached:
                self._progress(
                    ProgressUpdate(
                        phase=ExtractionPhase.COMPLETE,
                        message="Loaded from cache",
                    )
                )
                return cached

        pipeline = Pipeline()

        # Extract from schema (has highest priority for inputs and metadata)
        schema_file = find_schema_file(self.workspace_path)
        if schema_file:
            self._progress(
                ProgressUpdate(
                    phase=ExtractionPhase.PARSING_SCHEMA,
                    message="Parsing schema...",
                    detail=str(schema_file.name),
                )
            )
            logger.debug(f"Found schema file: {schema_file}")
            try:
                schema_metadata, schema_inputs = parse_schema(schema_file)
                pipeline.metadata = schema_metadata
                pipeline.inputs = schema_inputs
            except Exception as e:
                logger.warning(f"Failed to parse schema: {e}")

        # Extract from config
        self._progress(
            ProgressUpdate(
                phase=ExtractionPhase.PARSING_CONFIG,
                message="Parsing config...",
            )
        )
        try:
            config_metadata, config_params = parse_config(self.workspace_path, self.nextflow_path)
            # Merge metadata (schema takes priority)
            pipeline.metadata = self._merge_metadata(pipeline.metadata, config_metadata)
            # Filter config params to exclude those already in inputs and ignored prefixes
            input_names = {inp.name for inp in pipeline.inputs}
            config = get_config()
            pipeline.config_params = [
                p
                for p in config_params
                if p.name not in input_names and not config.should_ignore_config_param(p.name)
            ]
        except Exception as e:
            logger.warning(f"Failed to parse config: {e}")

        # Extract from README (full content after first h1, with base64 images)
        self._progress(
            ProgressUpdate(
                phase=ExtractionPhase.PARSING_README,
                message="Parsing README...",
            )
        )
        readme_content = self._extract_readme_content()
        if readme_content:
            pipeline.metadata.readme_content = readme_content

        # Get git info for repository URL and source links
        git_info = get_git_info(self.workspace_path)
        if git_info and git_info.base_url and not pipeline.metadata.repository:
            pipeline.metadata.repository = git_info.base_url

        # Extract from Language Server (pass git_info for source URLs)
        self._extract_from_lsp(pipeline, git_info)

        # Infer pipeline name from directory if not set
        if not pipeline.metadata.name:
            pipeline.metadata.name = self.workspace_path.name

        self._progress(
            ProgressUpdate(
                phase=ExtractionPhase.FINALIZING,
                message="Finalizing...",
            )
        )

        logger.info(
            f"Extraction complete: {len(pipeline.workflows)} workflows, "
            f"{len(pipeline.processes)} processes, {len(pipeline.functions)} functions"
        )

        # Store in cache
        if self.cache:
            self.cache.set(self.workspace_path, pipeline)

        self._progress(
            ProgressUpdate(
                phase=ExtractionPhase.COMPLETE,
                message="Extraction complete",
                detail=f"{len(pipeline.workflows)} workflows, {len(pipeline.processes)} processes, {len(pipeline.functions)} functions",
            )
        )

        return pipeline

    def _merge_metadata(
        self, primary: PipelineMetadata, secondary: PipelineMetadata
    ) -> PipelineMetadata:
        """Merge metadata, with primary taking precedence."""
        return PipelineMetadata(
            name=primary.name or secondary.name,
            description=primary.description or secondary.description,
            version=primary.version or secondary.version,
            homepage=primary.homepage or secondary.homepage,
            repository=primary.repository or secondary.repository,
            authors=primary.authors or secondary.authors,
            license=primary.license or secondary.license,
        )

    def _extract_readme_content(self) -> str:
        """
        Extract full README content after the first h1 heading.

        Also converts local images to base64 data URIs for portability.
        """
        readme_candidates = [
            self.workspace_path / "README.md",
            self.workspace_path / "readme.md",
            self.workspace_path / "README.rst",
        ]

        for readme_path in readme_candidates:
            if readme_path.exists():
                try:
                    content = readme_path.read_text(encoding="utf-8")
                    parsed_content = self._parse_readme_content(content)
                    # Convert local images to base64
                    return self._convert_images_to_base64(parsed_content, readme_path.parent)
                except Exception as e:
                    logger.debug(f"Failed to read README: {e}")

        return ""

    def _parse_readme_content(self, content: str) -> str:
        """
        Parse README content, returning everything after the first h1 heading.

        Strips the title (markdown # or HTML <h1>) and any badge lines immediately following.
        """
        lines = content.split("\n")
        result_lines: list[str] = []
        found_title = False
        in_html_h1 = False
        skip_badges = True

        for line in lines:
            stripped = line.strip()
            stripped_lower = stripped.lower()

            # Skip everything before/inside the first h1
            if not found_title:
                # Markdown h1
                if stripped.startswith("# "):
                    found_title = True
                    continue
                # HTML <h1> opening tag
                if "<h1" in stripped_lower:
                    in_html_h1 = True
                    # Check if it closes on the same line
                    if "</h1>" in stripped_lower:
                        found_title = True
                        in_html_h1 = False
                    continue
                # Inside HTML h1, look for closing tag
                if in_html_h1:
                    if "</h1>" in stripped_lower:
                        found_title = True
                        in_html_h1 = False
                    continue
                # Still looking for title
                continue

            # Skip badge lines immediately after title
            if skip_badges:
                # Badge patterns: [![...], ![...], [!..., or lines containing "badge"
                if (
                    stripped.startswith("[![")
                    or stripped.startswith("![")
                    or stripped.startswith("[!")
                    or "badge" in stripped_lower
                    or not stripped  # Skip empty lines in badge section
                ):
                    continue
                # First non-badge, non-empty line - stop skipping
                skip_badges = False

            result_lines.append(line)

        return "\n".join(result_lines)

    def _convert_images_to_base64(self, content: str, base_path: Path) -> str:
        """
        Convert local image references to base64 data URIs.

        Handles both markdown image syntax: ![alt](path) and HTML img tags.
        """
        import base64
        import mimetypes

        def get_mime_type(path: str) -> str:
            """Get MIME type for an image file."""
            mime_type, _ = mimetypes.guess_type(path)
            return mime_type or "application/octet-stream"

        def encode_image(image_path: Path) -> str | None:
            """Encode an image file to base64 data URI."""
            if not image_path.exists():
                logger.debug(f"Image not found: {image_path}")
                return None
            try:
                with open(image_path, "rb") as f:
                    data = base64.b64encode(f.read()).decode("utf-8")
                mime_type = get_mime_type(str(image_path))
                return f"data:{mime_type};base64,{data}"
            except Exception as e:
                logger.debug(f"Failed to encode image {image_path}: {e}")
                return None

        def is_local_path(path: str) -> bool:
            """Check if a path is local (not a URL)."""
            return not path.startswith(("http://", "https://", "data:"))

        def resolve_path(path: str) -> Path:
            """Resolve a relative path against the base path."""
            # Handle paths that start with ./
            if path.startswith("./"):
                path = path[2:]
            return base_path / path

        # Replace markdown images: ![alt](path)
        def replace_md_image(match: re.Match) -> str:
            alt = match.group(1)
            path = match.group(2)
            if is_local_path(path):
                image_path = resolve_path(path)
                data_uri = encode_image(image_path)
                if data_uri:
                    return f"![{alt}]({data_uri})"
            return match.group(0)

        content = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replace_md_image, content)

        # Replace HTML img tags: <img src="path" ...>
        def replace_html_image(match: re.Match) -> str:
            full_tag = match.group(0)
            src_match = re.search(r'src=["\']([^"\']+)["\']', full_tag)
            if src_match:
                path = src_match.group(1)
                if is_local_path(path):
                    image_path = resolve_path(path)
                    data_uri = encode_image(image_path)
                    if data_uri:
                        return full_tag.replace(path, data_uri)
            return full_tag

        content = re.sub(r"<img[^>]+>", replace_html_image, content, flags=re.IGNORECASE)

        return content

    def _extract_from_lsp(self, pipeline: Pipeline, git_info: GitInfo | None = None) -> None:
        """Extract processes, workflows, and functions using the Language Server."""
        # Find all Nextflow files
        self._progress(
            ProgressUpdate(
                phase=ExtractionPhase.LSP_SCANNING_FILES,
                message="Scanning for Nextflow files...",
            )
        )
        nf_files = list(self.workspace_path.rglob("*.nf"))
        if not nf_files:
            logger.debug("No .nf files found in workspace")
            return

        logger.info(f"Found {len(nf_files)} Nextflow files")
        # Don't show file count yet - LSP needs to start and index first

        if git_info and git_info.base_url:
            logger.debug(f"Git repository detected: {git_info.base_url}")
        else:
            logger.debug("No git repository detected or unable to build source URLs")

        with LSPClient(
            self.workspace_path,
            server_jar=self.language_server_jar,
            progress_callback=self._progress,
        ) as client:
            # Try workspace symbols first to see what the LSP knows about
            workspace_symbols = client.get_workspace_symbols("")
            logger.debug(f"Workspace symbols: {len(workspace_symbols)}")
            if workspace_symbols:
                logger.debug(f"First few: {workspace_symbols[:3]}")

            for i, nf_file in enumerate(nf_files):
                relative_path = nf_file.relative_to(self.workspace_path)
                self._progress(
                    ProgressUpdate(
                        phase=ExtractionPhase.LSP_EXTRACTING_SYMBOLS,
                        message="Extracting symbols...",
                        current=i + 1,
                        total=len(nf_files),
                        detail=str(relative_path),
                    )
                )
                try:
                    self._extract_file_symbols(client, nf_file, pipeline, git_info)
                except Exception as e:
                    logger.warning(f"Failed to extract from {nf_file}: {e}")

    def _extract_file_symbols(
        self,
        client: LSPClient,
        file_path: Path,
        pipeline: Pipeline,
        git_info: GitInfo | None = None,
    ) -> None:
        """Extract symbols from a single file using LSP."""
        relative_path = file_path.relative_to(self.workspace_path)
        logger.debug(f"Processing: {relative_path}")

        # Parse meta.yml if present (for nf-core modules/subworkflows)
        meta = parse_meta_for_file(file_path, self.workspace_path)
        if meta:
            logger.debug(f"  Found meta.yml: {meta.name}")

        # Open the document
        client.open_document(file_path)

        try:
            # Get document symbols
            symbols = client.get_document_symbols(file_path)
            logger.debug(f"  Found {len(symbols)} symbols")

            for symbol in symbols:
                self._process_symbol(client, file_path, symbol, pipeline, git_info, meta)

        finally:
            client.close_document(file_path)

    def _parse_symbol_name(self, raw_name: str) -> tuple[str, str]:
        """
        Parse a symbol name from the Nextflow LSP.

        The Nextflow LSP returns symbol names with type prefixes like:
        - "process FASTQC"
        - "workflow PIPELINE"
        - "workflow <entry>" (for entry workflow)
        - "function myFunc"
        - "enum MyEnum"

        Args:
            raw_name: The raw symbol name from the LSP

        Returns:
            Tuple of (symbol_type, clean_name) where symbol_type is one of
            "process", "workflow", "function", "enum", or "unknown"
        """
        # Known prefixes from the Nextflow LSP
        prefixes = ["process ", "workflow ", "function ", "enum "]

        for prefix in prefixes:
            if raw_name.startswith(prefix):
                symbol_type = prefix.strip()
                clean_name = raw_name[len(prefix) :]
                # Handle special entry workflow syntax: "workflow <entry>"
                if clean_name == "<entry>":
                    clean_name = ""
                return symbol_type, clean_name

        # No prefix found - return as unknown
        return "unknown", raw_name

    def _process_symbol(
        self,
        client: LSPClient,
        file_path: Path,
        symbol: dict[str, Any],
        pipeline: Pipeline,
        git_info: GitInfo | None = None,
        meta: ModuleMeta | SubworkflowMeta | None = None,
    ) -> None:
        """Process a document symbol and add to pipeline."""
        raw_name = symbol.get("name", "")
        kind = symbol.get("kind")  # May be None for Nextflow symbols
        range_info = symbol.get("range", {})
        selection_range = symbol.get("selectionRange", range_info)

        # Parse the symbol name to extract type and clean name
        symbol_type, name = self._parse_symbol_name(raw_name)

        # Get the line and character for hover
        start = selection_range.get("start", {})
        end = range_info.get("end", {})
        line = start.get("line", 0)
        character = start.get("character", 0)
        end_line = end.get("line", line)

        relative_path = str(file_path.relative_to(self.workspace_path))

        # Build source URL if git info available
        source_url = ""
        if git_info:
            # LSP lines are 0-based, source URLs use 1-based
            source_url = build_source_url(git_info, relative_path, line + 1, end_line + 1) or ""

        # Get hover information - contains signature and documentation
        hover = client.get_hover(file_path, line, character)
        signature, docstring, param_docs = parse_hover_content(hover)

        # Determine what kind of symbol this is based on parsed type or LSP kind
        if symbol_type == "process" or kind == SymbolKind.METHOD:
            process = self._create_process_from_signature(
                name,
                signature,
                docstring,
                relative_path,
                line + 1,
                end_line + 1,
                source_url,
                source_path=file_path,
                param_docs=param_docs,
            )
            if process and not any(p.name == process.name for p in pipeline.processes):
                # Apply meta.yml data if available (for modules)
                if meta and isinstance(meta, ModuleMeta):
                    process.apply_module_meta(meta)
                # Check for nf-core module URL
                nfcore_url = get_nfcore_module_url(relative_path)
                if nfcore_url:
                    process.nfcore_module_url = nfcore_url
                pipeline.processes.append(process)

        elif symbol_type == "workflow" or kind == SymbolKind.CLASS:
            workflow = self._create_workflow_from_signature(
                name, signature, docstring, relative_path, line + 1, end_line + 1, source_url
            )
            if workflow and not any(w.name == workflow.name for w in pipeline.workflows):
                # Entry workflow has empty name (parsed from "<entry>")
                if name == "" or name.lower() in ("main", "entry"):
                    workflow.is_entry = True
                # Apply meta.yml data if available (for subworkflows)
                if meta and isinstance(meta, SubworkflowMeta):
                    workflow.apply_subworkflow_meta(meta)
                pipeline.workflows.append(workflow)

        elif symbol_type == "function" or kind == SymbolKind.FUNCTION:
            function = self._create_function_from_signature(
                name,
                signature,
                docstring,
                param_docs,
                relative_path,
                line + 1,
                end_line + 1,
                source_url,
            )
            if function and not any(f.name == function.name for f in pipeline.functions):
                pipeline.functions.append(function)

        # Process child symbols
        for child in symbol.get("children", []):
            self._process_symbol(client, file_path, child, pipeline, git_info, meta)

    def _create_process_from_signature(
        self,
        name: str,
        signature: str,
        docstring: str,
        file_path: str,
        line: int,
        end_line: int = 0,
        source_url: str = "",
        source_path: Path | None = None,
        param_docs: dict[str, str] | None = None,
    ) -> Process | None:
        """Create a Process by parsing the LSP signature.

        When the LSP hover includes Groovydoc ``@param`` / ``@return`` tags,
        their descriptions are applied to the matching inputs and outputs.
        If the LSP returns no docstring (common with typed Nextflow syntax),
        the Groovydoc is parsed directly from the ``.nf`` source file.
        """
        if param_docs is None:
            param_docs = {}

        # Read the source file once — shared by Groovydoc parsing and output enrichment.
        source_text: str | None = None
        if source_path:
            try:
                source_text = source_path.read_text(encoding="utf-8")
            except OSError as e:
                logger.debug(f"Could not read source file {source_path}: {e}")

        # If the LSP returned no param docs, try to parse them from the source file.
        # The LSP may return the free-text docstring but strip @param/@return tags,
        # or (for typed processes) return no docstring at all.
        if source_text is not None and not param_docs:
            source_docstring, source_params = _parse_groovydoc_from_source(source_text, name)
            if source_params:
                param_docs = source_params
            if not docstring and source_docstring:
                docstring = source_docstring

        process = Process(
            name=name,
            docstring=docstring,
            file=file_path,
            line=line,
            end_line=end_line,
            source_url=source_url,
        )

        # Use the nf_parser to extract inputs/outputs from the signature
        parsed = parse_process_hover(f"```nextflow\n{signature}\n```")
        if parsed:
            # Enrich bare-name outputs from the source file when the LSP
            # only returns emit names (common with typed Nextflow syntax)
            outputs = parsed.outputs
            if source_text is not None and any(not o.type for o in outputs):
                outputs = enrich_outputs_from_source(outputs, source_text, name)

            for inp in parsed.inputs:
                # Look up @param description by matching input component names
                description = _find_param_description(inp.name, param_docs)
                process.inputs.append(
                    ProcessInput(
                        name=inp.name,
                        type=inp.type,
                        qualifier=inp.qualifier,
                        description=description,
                    )
                )
            for out in outputs:
                # Look up @return description by emit name
                description = param_docs.get(f"{RETURN_KEY_PREFIX}{out.emit}", "")
                if not description:
                    description = param_docs.get(RETURN_KEY_UNNAMED, "")
                process.outputs.append(
                    ProcessOutput(
                        name=out.name,
                        type=out.type,
                        emit=out.emit,
                        description=description,
                    )
                )

        return process

    def _create_workflow_from_signature(
        self,
        name: str,
        signature: str,
        docstring: str,
        file_path: str,
        line: int,
        end_line: int = 0,
        source_url: str = "",
    ) -> Workflow | None:
        """Create a Workflow by parsing the LSP signature."""
        workflow = Workflow(
            name=name,
            docstring=docstring,  # Actual Groovydoc documentation
            file=file_path,
            line=line,
            end_line=end_line,
            source_url=source_url,
        )

        # Use the nf_parser to extract takes/emits from the signature
        parsed = parse_workflow_hover(f"```nextflow\n{signature}\n```")
        if parsed:
            for take_name in parsed.takes:
                # Parse "name: Type" format if present
                if ":" in take_name:
                    n, t = take_name.split(":", 1)
                    workflow.inputs.append(WorkflowInput(name=n.strip(), type=t.strip()))
                else:
                    workflow.inputs.append(WorkflowInput(name=take_name))
            for emit_name in parsed.emits:
                # Parse "name: Type" format if present
                if ":" in emit_name:
                    n, t = emit_name.split(":", 1)
                    workflow.outputs.append(WorkflowOutput(name=n.strip(), type=t.strip()))
                else:
                    workflow.outputs.append(WorkflowOutput(name=emit_name))

        return workflow

    def _create_function_from_signature(
        self,
        name: str,
        signature: str,
        docstring: str,
        param_docs: dict[str, str],
        file_path: str,
        line: int,
        end_line: int = 0,
        source_url: str = "",
    ) -> Function | None:
        """Create a Function by parsing the LSP signature."""
        function = Function(
            name=name,
            docstring=docstring,
            file=file_path,
            line=line,
            end_line=end_line,
            source_url=source_url,
            return_description=param_docs.get(RETURN_KEY_UNNAMED, ""),
        )

        # Parse function signature: def name(param1: Type, param2: Type) -> ReturnType
        # or: def name(param1, param2)
        match = re.search(r"def\s+\w+\s*\(([^)]*)\)", signature)
        if match:
            params_str = match.group(1)
            if params_str.strip():
                for param_part in params_str.split(","):
                    param_part = param_part.strip()
                    if ":" in param_part:
                        n, type_str = param_part.split(":", 1)
                        n = n.strip()
                        function.params.append(
                            FunctionParam(
                                name=n,
                                type=type_str.strip(),
                                description=param_docs.get(n, ""),
                            )
                        )
                    else:
                        n = param_part.strip()
                        function.params.append(
                            FunctionParam(
                                name=n,
                                description=param_docs.get(n, ""),
                            )
                        )

        return function


def _find_param_description(input_name: str, param_docs: dict[str, str]) -> str:
    """Find a ``@param`` description that matches a parsed input name.

    Input names may be composite (e.g. ``val(meta), path(bam)``) so we check
    each component name against the ``param_docs`` keys.  For a tuple input
    the descriptions of all matching components are joined.

    Args:
        input_name: The parsed input name (e.g. ``"val(meta), path(bam)"`` or ``"reads"``).
        param_docs: Dict mapping param names to their Groovydoc descriptions.

    Returns:
        The matching description, or an empty string if none found.
    """
    if not param_docs:
        return ""

    # Direct match (simple inputs like "reads")
    if input_name in param_docs:
        return param_docs[input_name]

    # For composite/tuple inputs, extract component names and look them up
    # Matches val(meta), path(bam), file(reads), env(x), etc.
    component_names = re.findall(r"(?:val|path|file|env)\((\w+)\)", input_name)
    if not component_names:
        return ""

    descriptions = []
    for comp_name in component_names:
        if comp_name in param_docs:
            descriptions.append(f"`{comp_name}`: {param_docs[comp_name]}")

    return "; ".join(descriptions) if descriptions else ""


def _parse_groovydoc_from_source(
    source: str,
    process_name: str,
) -> tuple[str, dict[str, str]]:
    """Parse a Groovydoc comment from ``.nf`` source text.

    When the Nextflow LSP does not return a docstring (common with typed
    processes), this function extracts the ``/** ... */`` comment block
    preceding the process definition.

    Supports two documentation styles:

    1. Standard Groovydoc ``@param`` / ``@return`` tags::

        /** @param meta  Sample metadata map
         *  @return txt  Output text file
         */

    2. Bullet-list ``Inputs:`` / ``Outputs:`` sections::

        /** Inputs:
         *   - - meta: sample metadata map
         *     - bam: input BAM file
         *  Outputs:
         *   - - txt: output text file
         */

    Args:
        source: The ``.nf`` source file contents.
        process_name: Name of the process to locate.

    Returns:
        Tuple of ``(docstring, param_docs)`` where *docstring* is the free-text
        description and *param_docs* maps param/return names to descriptions.
        Returns ``("", {})`` if no Groovydoc is found.
    """

    # Find the process declaration, then look backwards for the nearest /** ... */
    proc_pattern = re.compile(
        r"process\s+" + re.escape(process_name) + r"\s*\{",
    )
    proc_match = proc_pattern.search(source)
    if not proc_match:
        return "", {}

    # Search the text before the process for the last /** ... */ comment
    preceding = source[: proc_match.start()]
    # Find all /** ... */ blocks and take the last one (closest to the process)
    comment_matches = list(re.finditer(r"/\*\*(.*?)\*/", preceding, re.DOTALL))
    if not comment_matches:
        return "", {}

    comment_body = comment_matches[-1].group(1)
    return _parse_groovydoc_comment(comment_body)


def _parse_groovydoc_comment(comment_body: str) -> tuple[str, dict[str, str]]:
    """Parse the body of a ``/** ... */`` Groovydoc comment.

    Handles both ``@param``/``@return`` tags and ``Inputs:``/``Outputs:``
    bullet-list sections.

    Args:
        comment_body: The text between ``/**`` and ``*/``.

    Returns:
        Tuple of ``(docstring, param_docs)``.
    """
    lines = comment_body.split("\n")
    doc_lines: list[str] = []
    params: dict[str, str] = {}
    current_section = "description"
    current_param = ""

    for raw_line in lines:
        # Strip leading whitespace and * characters (Groovydoc format)
        line = raw_line.strip()
        if line.startswith("*"):
            line = line[1:].strip()

        if not line:
            if current_section == "description" and doc_lines:
                doc_lines.append("")  # preserve paragraph breaks
            continue

        # --- Standard @param / @return tags ---

        # Check for @param tag
        param_match = re.match(r"@param\s+(\w+)\s*(.*)", line)
        if param_match:
            current_section = "param"
            current_param = param_match.group(1)
            params[current_param] = param_match.group(2).strip()
            continue

        # Check for @return tag (named: @return name desc)
        return_named = re.match(r"@returns?\s+(\w+)\s+(.*)", line)
        if return_named:
            current_section = "return"
            current_param = f"{RETURN_KEY_PREFIX}{return_named.group(1)}"
            params[current_param] = return_named.group(2).strip()
            continue

        # Check for @return tag (unnamed: @return desc)
        return_unnamed = re.match(r"@returns?\s*(.*)", line)
        if return_unnamed:
            current_section = "return"
            current_param = RETURN_KEY_UNNAMED
            params[RETURN_KEY_UNNAMED] = return_unnamed.group(1).strip()
            continue

        # --- Bullet-list Inputs: / Outputs: sections ---

        # Check for section headers
        if re.match(r"Inputs?:", line, re.IGNORECASE):
            current_section = "input_bullets"
            continue
        if re.match(r"Outputs?:", line, re.IGNORECASE):
            current_section = "output_bullets"
            continue

        # Check for bullet items: "- name: description" or "- - name: description"
        bullet_match = re.match(r"-\s*-?\s*(\w+)\s*:\s*(.*)", line)
        if bullet_match and current_section in ("input_bullets", "output_bullets"):
            name = bullet_match.group(1)
            desc = bullet_match.group(2).strip()
            if current_section == "input_bullets":
                current_param = name
                params[name] = desc
            else:
                current_param = f"{RETURN_KEY_PREFIX}{name}"
                params[current_param] = desc
            continue

        # Handle continuation lines
        if current_section == "description":
            # Skip the process name if it's the first line (e.g. "/** SV_PILEUP")
            if not doc_lines and re.match(r"^[A-Z_0-9]+$", line):
                continue
            doc_lines.append(line)
        elif current_section in ("param", "return", "input_bullets", "output_bullets"):
            if current_param and line and not line.startswith("@"):
                params[current_param] += " " + line

    docstring = "\n".join(doc_lines).strip()
    return docstring, params
