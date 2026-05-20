"""
Caching system for nf-docs pipeline extraction.

Caches the extracted Pipeline model to speed up re-runs when pipeline
files haven't changed.
"""

import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Any

import nf_docs
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

logger = logging.getLogger(__name__)


def get_xdg_cache_home() -> Path:
    """Get the XDG cache directory."""
    xdg_cache = os.environ.get("XDG_CACHE_HOME")
    if xdg_cache:
        return Path(xdg_cache)
    return Path.home() / ".cache"


class PipelineCache:
    """
    Cache for extracted Pipeline models.

    Uses content-based cache invalidation by hashing relevant pipeline files.
    Cache is stored in XDG_CACHE_HOME/nf-docs/ (default ~/.cache/nf-docs/).
    """

    # Files to include in cache key computation
    CACHE_FILES = [
        "*.nf",
        "nextflow_schema.json",
        "nextflow.config",
        "README.md",
        "meta.yml",  # Module/subworkflow metadata files
    ]

    def __init__(self, cache_dir: Path | None = None):
        """
        Initialize the cache.

        Args:
            cache_dir: Custom cache directory (default: $XDG_CACHE_HOME/nf-docs)
        """
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = get_xdg_cache_home() / "nf-docs"

    def _get_workspace_hash(self, workspace: Path) -> str:
        """Get a hash of the workspace path for namespacing."""
        workspace_str = str(workspace.resolve())
        return hashlib.sha256(workspace_str.encode()).hexdigest()[:16]

    def _get_content_hash(self, workspace: Path) -> str:
        """
        Compute a hash of all relevant files in the workspace.

        This hash changes when any pipeline file is modified.
        """
        hasher = hashlib.sha256()

        # Collect all files to hash
        files_to_hash: list[Path] = []

        for pattern in self.CACHE_FILES:
            if "*" in pattern:
                # Glob pattern - find all matching files
                files_to_hash.extend(sorted(workspace.rglob(pattern)))
            else:
                # Specific file
                file_path = workspace / pattern
                if file_path.exists():
                    files_to_hash.append(file_path)

        # Hash each file's content
        for file_path in sorted(files_to_hash):
            try:
                # Include relative path in hash to detect file renames
                rel_path = file_path.relative_to(workspace)
                hasher.update(str(rel_path).encode())

                # Include file content
                content = file_path.read_bytes()
                hasher.update(content)
            except Exception as e:
                logger.debug(f"Could not hash {file_path}: {e}")

        return hasher.hexdigest()[:32]

    def _get_target_file_hash(self, target_file: Path) -> str:
        """
        Hash a single target ``.nf`` file plus its sibling ``meta.yml`` (if any).

        Used for single-file mode so each module/subworkflow inside a workspace
        gets its own cache entry and invalidates independently.
        """
        hasher = hashlib.sha256()
        target = target_file.resolve()
        # Include the absolute path so different files don't collide.
        hasher.update(str(target).encode())
        try:
            hasher.update(target.read_bytes())
        except OSError as e:
            logger.debug(f"Could not hash {target}: {e}")
        meta = target.parent / "meta.yml"
        if meta.exists():
            try:
                hasher.update(b"meta.yml:")
                hasher.update(meta.read_bytes())
            except OSError as e:
                logger.debug(f"Could not hash {meta}: {e}")
        return hasher.hexdigest()[:32]

    def _get_cache_path(self, workspace: Path, target_file: Path | None = None) -> Path:
        """Get the cache file path for a workspace (or a target file within it)."""
        workspace_hash = self._get_workspace_hash(workspace)
        if target_file is not None:
            target_hash = self._get_target_file_hash(target_file)
            return self.cache_dir / f"{nf_docs.__version__}_{workspace_hash}_mod_{target_hash}.json"
        content_hash = self._get_content_hash(workspace)
        # Include version in filename to invalidate old caches when nf-docs is updated
        return self.cache_dir / f"{nf_docs.__version__}_{workspace_hash}_{content_hash}.json"

    def get(self, workspace: Path, target_file: Path | None = None) -> Pipeline | None:
        """
        Get cached Pipeline if valid.

        Args:
            workspace: Path to the pipeline workspace
            target_file: For single-file mode, the .nf file being extracted.
                The cache key becomes per-file so different modules within the
                same workspace don't collide.

        Returns:
            Cached Pipeline if valid, None if cache miss or stale
        """
        cache_path = self._get_cache_path(workspace, target_file)

        if not cache_path.exists():
            logger.debug("Cache miss: no cache file")
            return None

        try:
            data = json.loads(cache_path.read_text(encoding="utf-8"))
            pipeline = self._deserialize_pipeline(data)
            logger.debug(f"Cache hit: loaded from {cache_path.name}")
            logger.info("Using cached extraction results")
            return pipeline
        except Exception as e:
            logger.debug(f"Cache miss: failed to load cache: {e}")
            return None

    def set(
        self,
        workspace: Path,
        pipeline: Pipeline,
        target_file: Path | None = None,
    ) -> None:
        """
        Store Pipeline in cache.

        Args:
            workspace: Path to the pipeline workspace
            pipeline: Pipeline model to cache
            target_file: For single-file mode, the .nf file being extracted.
        """
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        cache_path = self._get_cache_path(workspace, target_file)

        # Clean up old cache files (per-workspace for pipeline mode, per-file
        # for single-file mode — we don't want one module to evict another).
        # ``cache_path`` already encodes the workspace/module hashes, so reuse
        # it rather than recomputing the (potentially file-reading) hashes.
        self._cleanup_old_caches(cache_path)

        try:
            data = self._serialize_pipeline(pipeline)
            cache_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
            logger.debug(f"Cached to {cache_path.name}")
        except Exception as e:
            logger.warning(f"Failed to cache pipeline: {e}")

    def _cleanup_old_caches(self, current_cache_path: Path) -> None:
        """
        Remove obsolete cache files that share a key with ``current_cache_path``.

        The cache filename encodes everything we need:
        ``{version}_{workspace_hash}_{content_hash}.json`` for pipeline mode and
        ``{version}_{workspace_hash}_mod_{target_hash}.json`` for single-file
        mode. We sweep entries that match the same key under any nf-docs
        version, taking care not to evict module entries from a pipeline-mode
        cleanup (or vice versa).
        """
        if not self.cache_dir.exists():
            return

        # Strip the version prefix; what remains identifies the cache key.
        _, _, key_suffix = current_cache_path.name.partition("_")
        is_module_entry = "_mod_" in key_suffix
        if is_module_entry:
            # Sweep entries for THIS module only.
            glob = f"*_{key_suffix}"
        else:
            # Sweep any non-module entry for this workspace.
            workspace_hash = key_suffix.split("_", 1)[0]
            glob = f"*_{workspace_hash}_*.json"

        for cache_file in self.cache_dir.glob(glob):
            if cache_file == current_cache_path:
                continue
            # Pipeline-mode cleanup must not touch module entries.
            if not is_module_entry and "_mod_" in cache_file.name:
                continue
            try:
                cache_file.unlink()
                logger.debug(f"Removed old cache: {cache_file.name}")
            except Exception as e:
                logger.debug(f"Could not remove old cache {cache_file}: {e}")

    def clear(self, workspace: Path | None = None) -> int:
        """
        Clear cache for a workspace or all caches.

        Args:
            workspace: Specific workspace to clear, or None for all

        Returns:
            Number of cache files removed
        """
        if not self.cache_dir.exists():
            return 0

        count = 0

        if workspace:
            # Clear only this workspace's cache (match any version)
            workspace_hash = self._get_workspace_hash(workspace)
            for cache_file in self.cache_dir.glob(f"*_{workspace_hash}_*.json"):
                try:
                    cache_file.unlink()
                    count += 1
                except Exception:
                    pass
        else:
            # Clear all caches
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    cache_file.unlink()
                    count += 1
                except Exception:
                    pass

        logger.info(f"Cleared {count} cache file(s)")
        return count

    def _serialize_pipeline(self, pipeline: Pipeline) -> dict[str, Any]:
        """Serialize a Pipeline to JSON-compatible dict."""
        return pipeline.to_dict()

    def _deserialize_pipeline(self, data: dict[str, Any]) -> Pipeline:
        """Deserialize a Pipeline from JSON dict."""
        # Reconstruct metadata
        pipeline_data = data.get("pipeline", {})
        metadata = PipelineMetadata(
            name=pipeline_data.get("name", ""),
            description=pipeline_data.get("description", ""),
            version=pipeline_data.get("version", ""),
            homepage=pipeline_data.get("homepage", ""),
            repository=pipeline_data.get("repository", ""),
            authors=pipeline_data.get("authors", []),
            license=pipeline_data.get("license", ""),
            readme_content=pipeline_data.get("readme_content", ""),
        )

        # Reconstruct inputs
        inputs = []
        for inp_data in data.get("inputs", []):
            inputs.append(
                PipelineInput(
                    name=inp_data.get("name", ""),
                    type=inp_data.get("type", "string"),
                    description=inp_data.get("description", ""),
                    help_text=inp_data.get("help_text", ""),
                    required=inp_data.get("required", False),
                    default=inp_data.get("default"),
                    format=inp_data.get("format", ""),
                    pattern=inp_data.get("pattern", ""),
                    enum=inp_data.get("enum", []),
                    group=inp_data.get("group", ""),
                    hidden=inp_data.get("hidden", False),
                    fa_icon=inp_data.get("fa_icon", ""),
                )
            )

        # Reconstruct config params
        config_params = []
        for param_data in data.get("config_params", []):
            config_params.append(
                ConfigParam(
                    name=param_data.get("name", ""),
                    type=param_data.get("type", "string"),
                    description=param_data.get("description", ""),
                    default=param_data.get("default"),
                    source=param_data.get("source", ""),
                )
            )

        # Reconstruct workflows
        workflows = []
        for wf_data in data.get("workflows", []):
            wf_inputs = [
                WorkflowInput(
                    name=i.get("name", ""),
                    type=i.get("type", ""),
                    description=i.get("description", ""),
                )
                for i in wf_data.get("inputs", [])
            ]
            wf_outputs = [
                WorkflowOutput(
                    name=o.get("name", ""),
                    type=o.get("type", ""),
                    description=o.get("description", ""),
                )
                for o in wf_data.get("outputs", [])
            ]
            workflows.append(
                Workflow(
                    name=wf_data.get("name", ""),
                    docstring=wf_data.get("docstring", ""),
                    file=wf_data.get("file", ""),
                    line=wf_data.get("line", 0),
                    end_line=wf_data.get("end_line", 0),
                    inputs=wf_inputs,
                    outputs=wf_outputs,
                    calls=wf_data.get("calls", []),
                    is_entry=wf_data.get("is_entry", False),
                    source_url=wf_data.get("source_url", ""),
                    # meta.yml fields
                    meta_description=wf_data.get("meta_description", ""),
                    meta_keywords=wf_data.get("meta_keywords", []),
                    meta_components=wf_data.get("meta_components", []),
                    meta_inputs=wf_data.get("meta_inputs", []),
                    meta_outputs=wf_data.get("meta_outputs", []),
                    meta_authors=wf_data.get("meta_authors", []),
                    meta_maintainers=wf_data.get("meta_maintainers", []),
                )
            )

        # Reconstruct processes
        processes = []
        for proc_data in data.get("processes", []):
            proc_inputs = [
                ProcessInput(
                    name=i.get("name", ""),
                    type=i.get("type", ""),
                    description=i.get("description", ""),
                    qualifier=i.get("qualifier", ""),
                )
                for i in proc_data.get("inputs", [])
            ]
            proc_outputs = [
                ProcessOutput(
                    name=o.get("name", ""),
                    type=o.get("type", ""),
                    description=o.get("description", ""),
                    emit=o.get("emit", ""),
                )
                for o in proc_data.get("outputs", [])
            ]
            processes.append(
                Process(
                    name=proc_data.get("name", ""),
                    docstring=proc_data.get("docstring", ""),
                    file=proc_data.get("file", ""),
                    line=proc_data.get("line", 0),
                    end_line=proc_data.get("end_line", 0),
                    inputs=proc_inputs,
                    outputs=proc_outputs,
                    directives=proc_data.get("directives", {}),
                    source_url=proc_data.get("source_url", ""),
                    nfcore_module_url=proc_data.get("nfcore_module_url", ""),
                    # meta.yml fields
                    meta_description=proc_data.get("meta_description", ""),
                    meta_keywords=proc_data.get("meta_keywords", []),
                    meta_tools=proc_data.get("meta_tools", []),
                    meta_inputs=proc_data.get("meta_inputs", []),
                    meta_outputs=proc_data.get("meta_outputs", []),
                    meta_authors=proc_data.get("meta_authors", []),
                    meta_maintainers=proc_data.get("meta_maintainers", []),
                )
            )

        # Reconstruct functions
        functions = []
        for func_data in data.get("functions", []):
            func_params = [
                FunctionParam(
                    name=p.get("name", ""),
                    type=p.get("type", ""),
                    description=p.get("description", ""),
                    default=p.get("default"),
                )
                for p in func_data.get("params", [])
            ]
            functions.append(
                Function(
                    name=func_data.get("name", ""),
                    docstring=func_data.get("docstring", ""),
                    file=func_data.get("file", ""),
                    line=func_data.get("line", 0),
                    end_line=func_data.get("end_line", 0),
                    params=func_params,
                    return_type=func_data.get("return_type", ""),
                    return_description=func_data.get("return_description", ""),
                    source_url=func_data.get("source_url", ""),
                )
            )

        return Pipeline(
            metadata=metadata,
            inputs=inputs,
            config_params=config_params,
            workflows=workflows,
            processes=processes,
            functions=functions,
        )
