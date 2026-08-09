"""
Markdown renderer for nf-docs.

Outputs pipeline documentation as a set of Markdown files suitable for
static site generators like MkDocs, Docusaurus, or GitHub Pages.
"""

import re

from nf_docs.models import Function, Pipeline, PipelineInput, Process, Workflow
from nf_docs.renderers.base import BaseRenderer


class MarkdownRenderer(BaseRenderer):
    """
    Render pipeline documentation as Markdown files.

    Output structure:
    - index.md: Pipeline overview
    - inputs.md: Workflow inputs and schema parameters
    - config.md: Non-input parameters (if any)
    - workflows.md: All workflows with descriptions
    - processes.md: All processes with full documentation
    - functions.md: Helper functions (if any)
    """

    def render(self, pipeline: Pipeline) -> str:
        """
        Render the pipeline to a single Markdown string.

        This concatenates all sections for formats that need a single output.

        Args:
            pipeline: The Pipeline model to render

        Returns:
            Combined Markdown string
        """
        sections = []

        sections.append(self._render_index(pipeline))
        sections.append(self._render_inputs(pipeline))

        if pipeline.config_params:
            sections.append(self._render_config(pipeline))

        if pipeline.workflows:
            sections.append(self._render_workflows(pipeline))

        if pipeline.processes:
            sections.append(self._render_processes(pipeline))

        if pipeline.functions:
            sections.append(self._render_functions(pipeline))

        content = "\n\n---\n\n".join(sections)

        # Add footer
        content += self._markdown_footer()

        return content

    def render_pages(self, pipeline: Pipeline) -> dict[str, str]:
        """
        Render the pipeline as one Markdown string per page.

        ``index.md`` and ``inputs.md`` are always present. The other four pages
        only appear when the pipeline has something to put in them, so don't
        assume a fixed set of keys.

        Args:
            pipeline: The Pipeline model to render

        Returns:
            Mapping of file name to Markdown content, in page order
        """
        pages: dict[str, str] = {
            # index.md - Pipeline overview
            "index.md": self._render_index(pipeline),
            # inputs.md - Workflow inputs and schema parameters
            "inputs.md": self._render_inputs(pipeline),
        }

        # config.md - Non-input parameters (only if they exist)
        if pipeline.config_params:
            pages["config.md"] = self._render_config(pipeline)

        # workflows.md - All workflows
        if pipeline.workflows:
            pages["workflows.md"] = self._render_workflows(pipeline)

        # processes.md - All processes
        if pipeline.processes:
            pages["processes.md"] = self._render_processes(pipeline)

        # functions.md - Helper functions (only if they exist)
        if pipeline.functions:
            pages["functions.md"] = self._render_functions(pipeline)

        footer = self._markdown_footer()
        return {name: content + footer for name, content in pages.items()}

    def render_single_file(self, pipeline: Pipeline) -> str:
        """
        Render documentation for a single ``.nf`` source file as a focused
        module/subworkflow README.

        Skips the pipeline overview, inputs, and config sections — and the
        multi-file ``# Processes`` / ``# Workflows`` / ``# Functions`` wrappers
        with their cross-file TOCs — so the result is suitable as a drop-in
        ``README.md`` next to the source file.
        """
        symbols: list[Process | Workflow | Function] = [
            *pipeline.processes,
            *pipeline.workflows,
            *pipeline.functions,
        ]

        # Choose a top-level title: meta.yml name, single-symbol name, or generic.
        title = self.title
        if not title and len(symbols) == 1:
            sym = symbols[0]
            title = getattr(sym, "name", "") or "Documentation"
        if not title:
            title = "Documentation"

        lines: list[str] = [f"# {title}", ""]

        # If the file has exactly one symbol with a meta.yml description, surface
        # it directly under the top heading so the README reads naturally.
        if len(symbols) == 1:
            meta_desc = getattr(symbols[0], "meta_description", None)
            if meta_desc:
                lines.append(meta_desc)
                lines.append("")

        body: list[str] = []
        for process in pipeline.processes:
            body.extend(self._render_process(process))
        for workflow in pipeline.workflows:
            body.extend(self._render_workflow(workflow, pipeline))
        for func in pipeline.functions:
            body.extend(self._render_function(func))

        if not body:
            lines.append("*No processes, workflows, or functions found in this file.*")
        else:
            lines.extend(body)

        # Strip Markdown-Extra ``{#anchor}`` attribute syntax — there are no
        # cross-file links to anchor to in single-file output, and renderers
        # without the ``attr_list`` extension (GitHub, etc.) show the braces
        # as literal text. Slug-based anchors are auto-generated downstream.
        rendered = re.sub(r"\s*\{#[^}]+\}\s*$", "", "\n".join(lines), flags=re.MULTILINE)

        return rendered.rstrip() + "\n"

    def _render_function(self, func: Function) -> list[str]:
        """Render a single function block (used by both multi- and single-file output)."""
        lines: list[str] = []
        anchor = self._make_anchor(func.name)
        lines.append(f"## {func.name} {{#{anchor}}}")
        lines.append("")

        if func.file:
            lines.append(f"*Defined in `{func.file}:{func.line}`*")
            lines.append("")

        params_str = ", ".join(p.name for p in func.params)
        lines.append(f"```groovy\ndef {func.name}({params_str})\n```")
        lines.append("")

        if func.docstring:
            lines.append(func.docstring)
            lines.append("")

        if func.params:
            lines.append("### Parameters")
            lines.append("")
            lines.append("| Name | Description | Default |")
            lines.append("|------|-------------|---------|")
            for param in func.params:
                default = f"`{param.default}`" if param.default is not None else "-"
                lines.append(f"| `{param.name}` | {param.description or '-'} | {default} |")
            lines.append("")

        if func.return_description:
            lines.append("### Returns")
            lines.append("")
            lines.append(func.return_description)
            lines.append("")

        return lines

    def _render_index(self, pipeline: Pipeline) -> str:
        """Render the index/overview page."""
        title = self.get_title(pipeline)
        lines = [f"# {title}"]

        # Version badge
        if pipeline.metadata.version:
            lines.append(f"\n**Version:** {pipeline.metadata.version}")

        # Description
        if pipeline.metadata.description:
            lines.append(f"\n{pipeline.metadata.description}")

        # Quick links
        lines.append("\n## Documentation")
        lines.append("")
        lines.append("- [Pipeline Inputs](inputs.md) - Input parameters and options")

        if pipeline.config_params:
            lines.append("- [Configuration](config.md) - Configuration parameters")

        if pipeline.workflows:
            lines.append("- [Workflows](workflows.md) - Pipeline workflows")

        if pipeline.processes:
            lines.append("- [Processes](processes.md) - Process definitions")

        if pipeline.functions:
            lines.append("- [Functions](functions.md) - Helper functions")

        # Pipeline summary
        lines.append("\n## Summary")
        lines.append("")
        lines.append(f"- **Inputs:** {len(pipeline.inputs)} parameters")
        if pipeline.config_params:
            lines.append(f"- **Config params:** {len(pipeline.config_params)}")
        lines.append(f"- **Workflows:** {len(pipeline.workflows)}")
        lines.append(f"- **Processes:** {len(pipeline.processes)}")
        if pipeline.functions:
            lines.append(f"- **Functions:** {len(pipeline.functions)}")

        # Authors
        if pipeline.metadata.authors:
            lines.append("\n## Authors")
            lines.append("")
            for author in pipeline.metadata.authors:
                lines.append(f"- {author}")

        # Links
        links = []
        if pipeline.metadata.homepage:
            links.append(f"- [Homepage]({pipeline.metadata.homepage})")
        if pipeline.metadata.repository:
            links.append(f"- [Repository]({pipeline.metadata.repository})")

        if links:
            lines.append("\n## Links")
            lines.append("")
            lines.extend(links)

        return "\n".join(lines)

    def _render_inputs(self, pipeline: Pipeline) -> str:
        """Render the inputs page."""
        lines = ["# Pipeline Inputs"]
        lines.append("")
        lines.append("This page documents all input parameters for the pipeline.")

        if not pipeline.inputs:
            lines.append("\n*No input parameters defined.*")
            return "\n".join(lines)

        # Group inputs by their group
        groups = pipeline.get_input_groups()

        for group_name, inputs in groups.items():
            lines.append(f"\n## {group_name}")
            lines.append("")

            for inp in inputs:
                lines.extend(self._render_input_param(inp))
                lines.append("")

        return "\n".join(lines)

    def _render_input_param(self, inp: PipelineInput) -> list[str]:
        """Render a single input parameter."""
        lines = []

        # Parameter name with anchor
        anchor = self._make_anchor(inp.name)
        lines.append(f"### `--{inp.name}` {{#{anchor}}}")
        lines.append("")

        # Type and requirement badges
        badges = []
        badges.append(f"**Type:** `{inp.type}`")

        if inp.required:
            badges.append("**Required**")
        else:
            badges.append("*Optional*")

        if inp.format:
            badges.append(f"**Format:** `{inp.format}`")

        lines.append(" | ".join(badges))
        lines.append("")

        # Description
        if inp.description:
            lines.append(inp.description)
            lines.append("")

        # Help text (extended description)
        if inp.help_text:
            lines.append(f"> {inp.help_text}")
            lines.append("")

        # Default value
        if inp.default is not None:
            lines.append(f"**Default:** `{inp.default}`")
            lines.append("")

        # Enum values
        if inp.enum:
            lines.append("**Allowed values:**")
            for value in inp.enum:
                lines.append(f"- `{value}`")
            lines.append("")

        # Pattern
        if inp.pattern:
            lines.append(f"**Pattern:** `{inp.pattern}`")
            lines.append("")

        return lines

    def _render_config(self, pipeline: Pipeline) -> str:
        """Render the configuration page."""
        lines = ["# Configuration Parameters"]
        lines.append("")
        lines.append(
            "These are additional configuration parameters that are not primary pipeline inputs."
        )
        lines.append("")

        for param in pipeline.config_params:
            lines.append(f"### `{param.name}`")
            lines.append("")

            lines.append(f"**Type:** `{param.type}`")
            lines.append("")

            if param.description:
                lines.append(param.description)
                lines.append("")

            if param.default is not None:
                lines.append(f"**Default:** `{param.default}`")
                lines.append("")

        return "\n".join(lines)

    def _render_workflows(self, pipeline: Pipeline) -> str:
        """Render the workflows page."""
        lines = ["# Workflows"]
        lines.append("")
        lines.append("This page documents all workflows in the pipeline.")

        if not pipeline.workflows:
            lines.append("\n*No workflows defined.*")
            return "\n".join(lines)

        # Table of contents
        lines.append("\n## Contents")
        lines.append("")
        for workflow in pipeline.workflows:
            name = workflow.name or "(entry)"
            anchor = self._make_anchor(workflow.name or "entry")
            entry_badge = " *(entry point)*" if workflow.is_entry else ""
            lines.append(f"- [{name}](#{anchor}){entry_badge}")

        # Workflow details
        for workflow in pipeline.workflows:
            lines.append("")
            lines.extend(self._render_workflow(workflow, pipeline))

        return "\n".join(lines)

    def _render_workflow(self, workflow: Workflow, pipeline: Pipeline) -> list[str]:
        """Render a single workflow."""
        lines = []

        name = workflow.name or "(entry)"
        anchor = self._make_anchor(workflow.name or "entry")
        lines.append(f"## {name} {{#{anchor}}}")
        lines.append("")

        # Entry badge
        if workflow.is_entry:
            lines.append("**Entry workflow**")
            lines.append("")

        # Source location
        if workflow.file:
            lines.append(f"*Defined in `{workflow.file}:{workflow.line}`*")
            lines.append("")

        # Keywords (from meta.yml)
        if workflow.meta_keywords:
            keywords_str = ", ".join(f"`{kw}`" for kw in workflow.meta_keywords)
            lines.append(f"**Keywords:** {keywords_str}")
            lines.append("")

        # meta.yml description
        if workflow.meta_description:
            lines.append(workflow.meta_description)
            lines.append("")

        # Code documentation (Groovydoc) - show if present and different
        if workflow.docstring and workflow.docstring != workflow.meta_description:
            if workflow.meta_description:
                lines.append("### Code Documentation")
                lines.append("")
            lines.append(workflow.docstring)
            lines.append("")

        # Components (from meta.yml)
        if workflow.meta_components:
            lines.append("### Components")
            lines.append("")
            lines.append("This workflow uses the following modules/subworkflows:")
            lines.append("")
            for comp in workflow.meta_components:
                lines.append(f"- `{comp}`")
            lines.append("")

        # Inputs (take) - prefer meta.yml if available
        if workflow.meta_inputs or workflow.inputs:
            lines.append("### Inputs")
            lines.append("")
            lines.append("| Name | Description |")
            lines.append("|------|-------------|")
            if workflow.meta_inputs:
                for inp in workflow.meta_inputs:
                    desc = inp.get("description", "-").replace("\n", " ").strip() or "-"
                    lines.append(f"| `{inp.get('name', '')}` | {desc} |")
            else:
                for inp in workflow.inputs:
                    lines.append(f"| `{inp.name}` | {inp.description or '-'} |")
            lines.append("")

        # Outputs (emit) - prefer meta.yml if available
        if workflow.meta_outputs or workflow.outputs:
            lines.append("### Outputs")
            lines.append("")
            lines.append("| Name | Description |")
            lines.append("|------|-------------|")
            if workflow.meta_outputs:
                for out in workflow.meta_outputs:
                    desc = out.get("description", "-").replace("\n", " ").strip() or "-"
                    lines.append(f"| `{out.get('name', '')}` | {desc} |")
            else:
                for out in workflow.outputs:
                    lines.append(f"| `{out.name}` | {out.description or '-'} |")
            lines.append("")

        # Process calls
        if workflow.calls:
            lines.append("### Calls")
            lines.append("")
            lines.append("This workflow calls the following processes/workflows:")
            lines.append("")
            for call_name in workflow.calls:
                # Link to process if it exists
                process = pipeline.get_process_by_name(call_name)
                if process:
                    anchor = self._make_anchor(call_name)
                    lines.append(f"- [`{call_name}`](processes.md#{anchor})")
                else:
                    # Check if it's a workflow
                    wf = pipeline.get_workflow_by_name(call_name)
                    if wf:
                        anchor = self._make_anchor(call_name)
                        lines.append(f"- [`{call_name}`](#{anchor}) *(workflow)*")
                    else:
                        lines.append(f"- `{call_name}`")
            lines.append("")

        # Authors/Maintainers (from meta.yml)
        if workflow.meta_authors or workflow.meta_maintainers:
            if workflow.meta_authors:
                authors_linked = [
                    f"[{a}](https://github.com/{a[1:]})" if a.startswith("@") else a
                    for a in workflow.meta_authors
                ]
                lines.append(f"**Authors:** {', '.join(authors_linked)}")
            if workflow.meta_maintainers:
                maintainers_linked = [
                    f"[{m}](https://github.com/{m[1:]})" if m.startswith("@") else m
                    for m in workflow.meta_maintainers
                ]
                lines.append(f"**Maintainers:** {', '.join(maintainers_linked)}")
            lines.append("")

        return lines

    def _render_processes(self, pipeline: Pipeline) -> str:
        """Render the processes page."""
        lines = ["# Processes"]
        lines.append("")
        lines.append("This page documents all processes in the pipeline.")

        if not pipeline.processes:
            lines.append("\n*No processes defined.*")
            return "\n".join(lines)

        # Table of contents
        lines.append("\n## Contents")
        lines.append("")
        for process in pipeline.processes:
            anchor = self._make_anchor(process.name)
            lines.append(f"- [{process.name}](#{anchor})")

        # Process details
        for process in pipeline.processes:
            lines.append("")
            lines.extend(self._render_process(process))

        return "\n".join(lines)

    def _render_process(self, process: Process) -> list[str]:
        """Render a single process."""
        lines = []

        anchor = self._make_anchor(process.name)
        lines.append(f"## {process.name} {{#{anchor}}}")
        lines.append("")

        # Source location
        if process.file:
            lines.append(f"*Defined in `{process.file}:{process.line}`*")
            lines.append("")

        # Keywords (from meta.yml)
        if process.meta_keywords:
            keywords_str = ", ".join(f"`{kw}`" for kw in process.meta_keywords)
            lines.append(f"**Keywords:** {keywords_str}")
            lines.append("")

        # meta.yml description
        if process.meta_description:
            lines.append(process.meta_description)
            lines.append("")

        # Code documentation (Groovydoc) - show if present and different
        if process.docstring and process.docstring != process.meta_description:
            if process.meta_description:
                lines.append("### Code Documentation")
                lines.append("")
            lines.append(process.docstring)
            lines.append("")

        # Tools (from meta.yml)
        if process.meta_tools:
            lines.append("### Tools")
            lines.append("")
            for tool in process.meta_tools:
                tool_name = tool.get("name", "Unknown")
                # Link tool name to homepage or documentation
                if tool.get("homepage"):
                    lines.append(f"#### [{tool_name}]({tool['homepage']})")
                elif tool.get("documentation"):
                    lines.append(f"#### [{tool_name}]({tool['documentation']})")
                else:
                    lines.append(f"#### {tool_name}")
                lines.append("")
                if tool.get("description"):
                    lines.append(tool["description"])
                    lines.append("")
                tool_links = []
                if tool.get("homepage"):
                    tool_links.append(f"[Homepage]({tool['homepage']})")
                if tool.get("documentation"):
                    tool_links.append(f"[Documentation]({tool['documentation']})")
                # Link biotools identifiers to bio.tools
                identifier = tool.get("identifier", "")
                if identifier.startswith("biotools:"):
                    biotools_id = identifier.replace("biotools:", "")
                    tool_links.append(f"[{identifier}](https://bio.tools/{biotools_id})")
                elif identifier:
                    tool_links.append(f"ID: `{identifier}`")
                if tool.get("licence"):
                    tool_links.append(f"License: {', '.join(tool['licence'])}")
                if tool_links:
                    lines.append(" | ".join(tool_links))
                    lines.append("")

        # Inputs - prefer meta.yml if available
        if process.meta_inputs or process.inputs:
            lines.append("### Inputs")
            lines.append("")
            lines.append("| Name | Type | Description |")
            lines.append("|------|------|-------------|")
            if process.meta_inputs:
                for inp in process.meta_inputs:
                    desc = inp.get("description", "-").replace("\n", " ").strip() or "-"
                    lines.append(f"| `{inp.get('name', '')}` | `{inp.get('type', '-')}` | {desc} |")
            else:
                for inp in process.inputs:
                    lines.append(f"| `{inp.name}` | `{inp.type}` | {inp.description or '-'} |")
            lines.append("")

        # Outputs - prefer meta.yml if available
        if process.meta_outputs or process.outputs:
            lines.append("### Outputs")
            lines.append("")
            if process.meta_outputs:
                lines.append("| Name | Type | Pattern | Description |")
                lines.append("|------|------|---------|-------------|")
                for out in process.meta_outputs:
                    desc = out.get("description", "-").replace("\n", " ").strip() or "-"
                    pattern = out.get("pattern", "-") or "-"
                    lines.append(
                        f"| `{out.get('name', '')}` | `{out.get('type', '-')}` | `{pattern}` | {desc} |"
                    )
            else:
                lines.append("| Name | Type | Emit | Description |")
                lines.append("|------|------|------|-------------|")
                for out in process.outputs:
                    emit = f"`{out.emit}`" if out.emit else "-"
                    lines.append(
                        f"| `{out.name}` | `{out.type}` | {emit} | {out.description or '-'} |"
                    )
            lines.append("")

        # Directives
        if process.directives:
            lines.append("### Directives")
            lines.append("")
            lines.append("| Directive | Value |")
            lines.append("|-----------|-------|")
            for name, value in process.directives.items():
                lines.append(f"| `{name}` | `{value}` |")
            lines.append("")

        # Authors/Maintainers (from meta.yml)
        if process.meta_authors or process.meta_maintainers:
            if process.meta_authors:
                authors_linked = [
                    f"[{a}](https://github.com/{a[1:]})" if a.startswith("@") else a
                    for a in process.meta_authors
                ]
                lines.append(f"**Authors:** {', '.join(authors_linked)}")
            if process.meta_maintainers:
                maintainers_linked = [
                    f"[{m}](https://github.com/{m[1:]})" if m.startswith("@") else m
                    for m in process.meta_maintainers
                ]
                lines.append(f"**Maintainers:** {', '.join(maintainers_linked)}")
            lines.append("")

        return lines

    def _render_functions(self, pipeline: Pipeline) -> str:
        """Render the functions page."""
        lines = ["# Functions"]
        lines.append("")
        lines.append("This page documents helper functions defined in the pipeline.")

        if not pipeline.functions:
            lines.append("\n*No functions defined.*")
            return "\n".join(lines)

        # Table of contents
        lines.append("\n## Contents")
        lines.append("")
        for func in pipeline.functions:
            anchor = self._make_anchor(func.name)
            lines.append(f"- [{func.name}](#{anchor})")

        # Function details
        for func in pipeline.functions:
            lines.append("")
            lines.extend(self._render_function(func))

        return "\n".join(lines)

    def _make_anchor(self, text: str) -> str:
        """Create a valid anchor ID from text."""
        # Convert to lowercase and replace spaces/special chars with hyphens
        anchor = text.lower()
        anchor = "".join(c if c.isalnum() else "-" for c in anchor)
        anchor = "-".join(filter(None, anchor.split("-")))  # Remove multiple hyphens
        return anchor or "unnamed"
