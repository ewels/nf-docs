"""
Data models for the nf-docs internal schema.

These models represent the unified internal representation of Nextflow
pipeline documentation, collected from the Language Server, nextflow_schema.json,
nextflow.config, and meta.yml files.
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from nf_docs.meta_parser import ModuleMeta, SubworkflowMeta


@dataclass
class ProcessInput:
    """Represents an input declaration in a Nextflow process."""

    name: str
    type: str  # val, path, tuple, env, stdin
    description: str = ""
    qualifier: str = ""  # Additional type qualifiers

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "qualifier": self.qualifier,
        }


@dataclass
class ProcessOutput:
    """Represents an output declaration in a Nextflow process."""

    name: str
    type: str  # val, path, tuple, env, stdout
    description: str = ""
    emit: str = ""  # Named output emit identifier

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "emit": self.emit,
        }


@dataclass
class Process:
    """Represents a Nextflow process with full documentation."""

    name: str
    docstring: str = ""  # Documentation from code comments (Groovydoc)
    file: str = ""
    line: int = 0
    end_line: int = 0  # End line of the process definition
    inputs: list[ProcessInput] = field(default_factory=list)
    outputs: list[ProcessOutput] = field(default_factory=list)
    directives: dict[str, Any] = field(default_factory=dict)
    script: str = ""  # Script content (optional)
    source_url: str = ""  # URL to view source in remote repository
    nfcore_module_url: str = ""  # URL to nf-core module docs (if applicable)

    # meta.yml fields (for nf-core modules)
    meta_description: str = ""  # Description from meta.yml
    meta_keywords: list[str] = field(default_factory=list)
    meta_tools: list[dict[str, Any]] = field(default_factory=list)  # Tool info from meta.yml
    meta_inputs: list[dict[str, Any]] = field(default_factory=list)  # Input descriptions
    meta_outputs: list[dict[str, Any]] = field(default_factory=list)  # Output descriptions
    meta_authors: list[str] = field(default_factory=list)
    meta_maintainers: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result: dict[str, Any] = {
            "name": self.name,
            "docstring": self.docstring,
            "file": self.file,
            "line": self.line,
            "end_line": self.end_line,
            "inputs": [i.to_dict() for i in self.inputs],
            "outputs": [o.to_dict() for o in self.outputs],
            "directives": self.directives,
        }
        if self.source_url:
            result["source_url"] = self.source_url
        if self.nfcore_module_url:
            result["nfcore_module_url"] = self.nfcore_module_url
        # Include meta.yml data if present
        if self.meta_description:
            result["meta_description"] = self.meta_description
        if self.meta_keywords:
            result["meta_keywords"] = self.meta_keywords
        if self.meta_tools:
            result["meta_tools"] = self.meta_tools
        if self.meta_inputs:
            result["meta_inputs"] = self.meta_inputs
        if self.meta_outputs:
            result["meta_outputs"] = self.meta_outputs
        if self.meta_authors:
            result["meta_authors"] = self.meta_authors
        if self.meta_maintainers:
            result["meta_maintainers"] = self.meta_maintainers
        return result

    def has_meta(self) -> bool:
        """Check if this process has meta.yml documentation."""
        return bool(self.meta_description or self.meta_tools or self.meta_inputs)

    def apply_module_meta(self, meta: "ModuleMeta") -> None:
        """Apply metadata from a parsed ModuleMeta object."""
        self.meta_description = meta.description
        self.meta_keywords = meta.keywords
        self.meta_tools = [t.to_dict() for t in meta.tools]
        self.meta_inputs = [i.to_dict() for i in meta.inputs]
        self.meta_outputs = [o.to_dict() for o in meta.outputs]
        self.meta_authors = meta.authors
        self.meta_maintainers = meta.maintainers


@dataclass
class WorkflowInput:
    """Represents an input (take) in a Nextflow workflow."""

    name: str
    type: str = ""
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "type": self.type,
            "description": self.description,
        }


@dataclass
class WorkflowOutput:
    """Represents an output (emit) in a Nextflow workflow."""

    name: str
    type: str = ""
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "type": self.type,
            "description": self.description,
        }


@dataclass
class Workflow:
    """Represents a Nextflow workflow with documentation."""

    name: str
    docstring: str = ""  # Documentation from code comments (Groovydoc)
    file: str = ""
    line: int = 0
    end_line: int = 0  # End line of the workflow definition
    inputs: list[WorkflowInput] = field(default_factory=list)
    outputs: list[WorkflowOutput] = field(default_factory=list)
    calls: list[str] = field(default_factory=list)  # Process/workflow names called
    is_entry: bool = False  # Is this the entry workflow?
    source_url: str = ""  # URL to view source in remote repository

    # meta.yml fields (for nf-core subworkflows)
    meta_description: str = ""  # Description from meta.yml
    meta_keywords: list[str] = field(default_factory=list)
    meta_components: list[str] = field(default_factory=list)  # Modules/subworkflows used
    meta_inputs: list[dict[str, Any]] = field(default_factory=list)  # Input descriptions
    meta_outputs: list[dict[str, Any]] = field(default_factory=list)  # Output descriptions
    meta_authors: list[str] = field(default_factory=list)
    meta_maintainers: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "name": self.name,
            "docstring": self.docstring,
            "file": self.file,
            "line": self.line,
            "end_line": self.end_line,
            "inputs": [i.to_dict() for i in self.inputs],
            "outputs": [o.to_dict() for o in self.outputs],
            "calls": self.calls,
            "is_entry": self.is_entry,
        }
        if self.source_url:
            result["source_url"] = self.source_url
        # Include meta.yml data if present
        if self.meta_description:
            result["meta_description"] = self.meta_description
        if self.meta_keywords:
            result["meta_keywords"] = self.meta_keywords
        if self.meta_components:
            result["meta_components"] = self.meta_components
        if self.meta_inputs:
            result["meta_inputs"] = self.meta_inputs
        if self.meta_outputs:
            result["meta_outputs"] = self.meta_outputs
        if self.meta_authors:
            result["meta_authors"] = self.meta_authors
        if self.meta_maintainers:
            result["meta_maintainers"] = self.meta_maintainers
        return result

    def has_meta(self) -> bool:
        """Check if this workflow has meta.yml documentation."""
        return bool(self.meta_description or self.meta_components or self.meta_inputs)

    def apply_subworkflow_meta(self, meta: "SubworkflowMeta") -> None:
        """Apply metadata from a parsed SubworkflowMeta object."""
        self.meta_description = meta.description
        self.meta_keywords = meta.keywords
        self.meta_components = meta.components
        self.meta_inputs = [i.to_dict() for i in meta.inputs]
        self.meta_outputs = [o.to_dict() for o in meta.outputs]
        self.meta_authors = meta.authors
        self.meta_maintainers = meta.maintainers


@dataclass
class FunctionParam:
    """Represents a parameter in a Nextflow function."""

    name: str
    type: str = ""
    description: str = ""
    default: Any = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "name": self.name,
            "type": self.type,
            "description": self.description,
        }
        if self.default is not None:
            result["default"] = self.default
        return result


@dataclass
class Function:
    """Represents a Nextflow function with documentation."""

    name: str
    docstring: str = ""
    file: str = ""
    line: int = 0
    end_line: int = 0  # End line of the function definition
    params: list[FunctionParam] = field(default_factory=list)
    return_type: str = ""
    return_description: str = ""
    source_url: str = ""  # URL to view source in remote repository

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "name": self.name,
            "docstring": self.docstring,
            "file": self.file,
            "line": self.line,
            "end_line": self.end_line,
            "params": [p.to_dict() for p in self.params],
            "return_type": self.return_type,
            "return_description": self.return_description,
        }
        if self.source_url:
            result["source_url"] = self.source_url
        return result


@dataclass
class PipelineInput:
    """
    Represents a pipeline input parameter.

    These come from nextflow_schema.json and represent typed inputs
    that users provide when running the pipeline.
    """

    name: str
    type: str  # string, integer, number, boolean, object
    description: str = ""
    help_text: str = ""  # Extended help from schema
    required: bool = False
    default: Any = None
    format: str = ""  # e.g., file-path, directory-path
    pattern: str = ""  # Validation pattern
    enum: list[str] = field(default_factory=list)  # Allowed values
    group: str = ""  # Group/section in schema
    hidden: bool = False  # Hidden from help
    fa_icon: str = ""  # Font Awesome icon

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result: dict[str, Any] = {
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "required": self.required,
        }
        if self.help_text:
            result["help_text"] = self.help_text
        if self.default is not None:
            result["default"] = self.default
        if self.format:
            result["format"] = self.format
        if self.pattern:
            result["pattern"] = self.pattern
        if self.enum:
            result["enum"] = self.enum
        if self.group:
            result["group"] = self.group
        if self.hidden:
            result["hidden"] = self.hidden
        if self.fa_icon:
            result["fa_icon"] = self.fa_icon
        return result


@dataclass
class ConfigParam:
    """
    Represents a configuration parameter from nextflow.config.

    These are params that may not be in the schema (e.g., executor settings,
    resource defaults, or legacy params).
    """

    name: str
    type: str = "string"  # Inferred type
    description: str = ""
    default: Any = None
    source: str = ""  # Which config file it came from

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "name": self.name,
            "type": self.type,
        }
        if self.description:
            result["description"] = self.description
        if self.default is not None:
            result["default"] = self.default
        if self.source:
            result["source"] = self.source
        return result


@dataclass
class PipelineMetadata:
    """Metadata about the pipeline."""

    name: str = ""
    description: str = ""
    version: str = ""
    homepage: str = ""
    repository: str = ""
    authors: list[str] = field(default_factory=list)
    license: str = ""
    readme_content: str = ""  # Full README content (after first h1)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result: dict[str, Any] = {"name": self.name}
        if self.description:
            result["description"] = self.description
        if self.version:
            result["version"] = self.version
        if self.homepage:
            result["homepage"] = self.homepage
        if self.repository:
            result["repository"] = self.repository
        if self.authors:
            result["authors"] = self.authors
        if self.license:
            result["license"] = self.license
        if self.readme_content:
            result["readme_content"] = self.readme_content
        return result


@dataclass
class Pipeline:
    """
    Complete pipeline documentation model.

    This is the unified internal schema that combines information from:
    - Language Server (processes, workflows, functions)
    - nextflow_schema.json (input parameters)
    - nextflow.config (config parameters)
    - README.md (description)
    """

    metadata: PipelineMetadata = field(default_factory=PipelineMetadata)
    inputs: list[PipelineInput] = field(default_factory=list)
    config_params: list[ConfigParam] = field(default_factory=list)
    workflows: list[Workflow] = field(default_factory=list)
    processes: list[Process] = field(default_factory=list)
    functions: list[Function] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation for JSON/YAML output."""
        return {
            "pipeline": self.metadata.to_dict(),
            "inputs": [i.to_dict() for i in self.inputs],
            "config_params": [c.to_dict() for c in self.config_params],
            "workflows": [w.to_dict() for w in self.workflows],
            "processes": [p.to_dict() for p in self.processes],
            "functions": [f.to_dict() for f in self.functions],
        }

    def get_input_groups(self) -> dict[str, list[PipelineInput]]:
        """Get inputs organized by group."""
        groups: dict[str, list[PipelineInput]] = {}
        for inp in self.inputs:
            group = inp.group or "Other"
            if group not in groups:
                groups[group] = []
            groups[group].append(inp)
        return groups

    def get_process_by_name(self, name: str) -> Process | None:
        """Find a process by name."""
        for process in self.processes:
            if process.name == name:
                return process
        return None

    def get_workflow_by_name(self, name: str) -> Workflow | None:
        """Find a workflow by name."""
        for workflow in self.workflows:
            if workflow.name == name:
                return workflow
        return None

    def get_entry_workflow(self) -> Workflow | None:
        """Get the entry (main) workflow."""
        for workflow in self.workflows:
            if workflow.is_entry:
                return workflow
        # If no explicit entry, look for common names
        for name in ["main", "MAIN", "entry", "ENTRY", ""]:
            wf = self.get_workflow_by_name(name)
            if wf:
                return wf
        # Return first workflow if none marked as entry
        return self.workflows[0] if self.workflows else None

    def has_content(self) -> bool:
        """Check if the pipeline has any meaningful content to document.

        Returns True if there are any inputs, config params, workflows,
        processes, or functions extracted.
        """
        return bool(
            self.inputs or self.config_params or self.workflows or self.processes or self.functions
        )
