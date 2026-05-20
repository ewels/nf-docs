"""
Table renderer for nf-docs.

Outputs pipeline documentation as compact Markdown tables inspired by
terraform-docs.  Each section is a ``## Heading`` followed by one or more
dense Markdown tables — no prose, no per-item sub-sections, just scannable
reference data.  Supports marker-based injection into existing README files
with optional ``{{ section }}`` template tags for selective rendering.
"""

import re
from pathlib import Path

from nf_docs.generation_info import get_markdown_footer
from nf_docs.models import Pipeline, PipelineInput, Process, Workflow
from nf_docs.renderers.base import BaseRenderer

BEGIN_MARKER = "<!-- BEGIN_NF_DOCS -->"
END_MARKER = "<!-- END_NF_DOCS -->"

AVAILABLE_SECTIONS = frozenset(
    {"header", "inputs", "config", "workflows", "processes", "functions"}
)

_TAG_PATTERN = re.compile(r"\{\{\s*(\w+)\s*\}\}")


def _find_markers(text: str) -> tuple[int, int] | None:
    """Return ``(begin_idx, end_idx)`` of the doc markers, or ``None``."""
    begin_idx = text.find(BEGIN_MARKER)
    end_idx = text.find(END_MARKER)
    if begin_idx == -1 or end_idx == -1 or end_idx <= begin_idx:
        return None
    return begin_idx, end_idx


def inject_into_content(existing: str, new_content: str) -> str | None:
    """
    Replace text between ``BEGIN_NF_DOCS`` and ``END_NF_DOCS`` markers.

    Args:
        existing: The full text of the file that may contain markers.
        new_content: The rendered documentation to inject.

    Returns:
        The updated text with *new_content* between the markers, or ``None``
        if the markers were not found.
    """
    pos = _find_markers(existing)
    if pos is None:
        return None
    begin_idx, end_idx = pos

    before = existing[: begin_idx + len(BEGIN_MARKER)]
    after = existing[end_idx:]
    return f"{before}\n{new_content}\n{after}"


def extract_template(existing: str) -> str | None:
    """
    Extract the template content between markers, if template tags are present.

    Args:
        existing: The full text of the file that may contain markers.

    Returns:
        The template string if ``{{ section }}`` tags are found between markers,
        or ``None`` if no markers or no template tags.
    """
    pos = _find_markers(existing)
    if pos is None:
        return None
    begin_idx, end_idx = pos

    template = existing[begin_idx + len(BEGIN_MARKER) : end_idx]
    if _TAG_PATTERN.search(template):
        return template
    return None


class TableRenderer(BaseRenderer):
    """
    Render pipeline documentation as compact Markdown tables.

    Modelled on the ``terraform-docs markdown table`` output format:
    a single document with heading-per-section and a dense table underneath.
    """

    # ------------------------------------------------------------------
    # Public API (BaseRenderer contract)
    # ------------------------------------------------------------------

    def render(self, pipeline: Pipeline) -> str:
        """
        Render the full pipeline as a single Markdown string of tables.

        Args:
            pipeline: The Pipeline model to render.

        Returns:
            Markdown string with all sections rendered as tables.
        """
        sections: list[str] = []

        sections.append(self._render_header(pipeline))

        if pipeline.inputs:
            sections.append(self._render_inputs(pipeline))

        if pipeline.config_params:
            sections.append(self._render_config(pipeline))

        if pipeline.workflows:
            sections.append(self._render_workflows(pipeline))

        if pipeline.processes:
            sections.append(self._render_processes(pipeline))

        if pipeline.functions:
            sections.append(self._render_functions(pipeline))

        content = "\n\n".join(sections)
        content += "\n\n" + get_markdown_footer()
        return content

    def render_from_template(self, pipeline: Pipeline, template: str) -> str:
        """
        Render pipeline using a template with ``{{ section }}`` placeholders.

        Each recognised tag (e.g. ``{{ inputs }}``, ``{{ workflows }}``) is
        replaced with the rendered content for that section.  Text surrounding
        the tags is preserved, allowing users to add custom headings or notes.
        Unrecognised tags are left as-is.

        Args:
            pipeline: The Pipeline model to render.
            template: A string containing ``{{ section }}`` placeholders.

        Returns:
            Markdown string with placeholders replaced by rendered sections.
        """
        # Only render sections that are actually referenced in the template.
        referenced = {m.lower() for m in _TAG_PATTERN.findall(template)}
        section_renderers: dict[str, str] = {}
        if "header" in referenced:
            section_renderers["header"] = self._render_header(pipeline)
        if "inputs" in referenced:
            section_renderers["inputs"] = self._render_inputs(pipeline) if pipeline.inputs else ""
        if "config" in referenced:
            section_renderers["config"] = (
                self._render_config(pipeline) if pipeline.config_params else ""
            )
        if "workflows" in referenced:
            section_renderers["workflows"] = (
                self._render_workflows(pipeline) if pipeline.workflows else ""
            )
        if "processes" in referenced:
            section_renderers["processes"] = (
                self._render_processes(pipeline) if pipeline.processes else ""
            )
        if "functions" in referenced:
            section_renderers["functions"] = (
                self._render_functions(pipeline) if pipeline.functions else ""
            )

        def _replace_tag(match: re.Match[str]) -> str:
            tag = match.group(1).lower()
            if tag in section_renderers:
                return section_renderers[tag]
            return match.group(0)  # Leave unrecognised tags as-is

        content = _TAG_PATTERN.sub(_replace_tag, template)
        # Collapse runs of 3+ blank lines into 2
        content = re.sub(r"\n{3,}", "\n\n", content).strip()
        content += "\n\n" + get_markdown_footer()
        return content

    def render_to_directory(self, pipeline: Pipeline, output_dir: str | Path) -> list[Path]:
        """Write table documentation to a single file inside *output_dir*.
        If the README.md already exists and contains ``<!-- BEGIN_NF_DOCS -->`` /
        ``<!-- END_NF_DOCS -->`` markers, the generated content is injected between
        them.  When the markers contain ``{{ section }}`` template tags, only the
        requested sections are rendered.
        Args:
            pipeline: The Pipeline model to render.
            output_dir: Target directory (created if absent).
        Returns:
            List containing the single created/updated file path.
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        out_file = output_path / "README.md"
        try:
            existing = out_file.read_text(encoding="utf-8")
        except FileNotFoundError:
            existing = None
        if existing is not None:
            template = extract_template(existing)
            if template is not None:
                content = self.render_from_template(pipeline, template)
            else:
                content = self.render(pipeline)
            injected = inject_into_content(existing, content)
            if injected is not None:
                out_file.write_text(injected, encoding="utf-8")
                return [out_file]
        # No existing file or no markers — write with markers
        content = self.render(pipeline)
        wrapped = f"{BEGIN_MARKER}\n{content}\n{END_MARKER}\n"
        out_file.write_text(wrapped, encoding="utf-8")
        return [out_file]

    # ------------------------------------------------------------------
    # Header
    # ------------------------------------------------------------------

    def _render_header(self, pipeline: Pipeline) -> str:
        """Render the top-level title and one-line summary."""
        title = self.get_title(pipeline)
        lines: list[str] = [f"# {title}"]

        parts: list[str] = []
        if pipeline.metadata.version:
            parts.append(f"**Version:** {pipeline.metadata.version}")
        if pipeline.metadata.description:
            parts.append(pipeline.metadata.description)
        if parts:
            lines.append("")
            lines.append(" · ".join(parts))

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Inputs
    # ------------------------------------------------------------------

    def _render_inputs(self, pipeline: Pipeline) -> str:
        """Render pipeline inputs as grouped tables."""
        lines: list[str] = ["## Inputs"]

        groups = pipeline.get_input_groups()
        for group_name, inputs in groups.items():
            lines.append("")
            lines.append(f"### {group_name}")
            lines.append("")
            lines.append("| Name | Description | Type | Default | Required |")
            lines.append("|------|-------------|------|---------|:--------:|")
            for inp in inputs:
                lines.append(self._input_row(inp))

        return "\n".join(lines)

    def _input_row(self, inp: PipelineInput) -> str:
        """Format a single input parameter as a table row."""
        name = f"`--{inp.name}`"
        desc = self._cell(inp.description)
        type_ = f"`{inp.type}`" if inp.type else "n/a"
        default = f"`{inp.default}`" if inp.default is not None else "n/a"
        required = "yes" if inp.required else "no"
        return f"| {name} | {desc} | {type_} | {default} | {required} |"

    # ------------------------------------------------------------------
    # Config parameters
    # ------------------------------------------------------------------

    def _render_config(self, pipeline: Pipeline) -> str:
        """Render non-input configuration parameters."""
        lines: list[str] = [
            "## Configuration",
            "",
            "| Name | Type | Default | Description |",
            "|------|------|---------|-------------|",
        ]
        for param in pipeline.config_params:
            name = f"`{param.name}`"
            type_ = f"`{param.type}`" if param.type else "n/a"
            default = f"`{param.default}`" if param.default is not None else "n/a"
            desc = self._cell(param.description)
            lines.append(f"| {name} | {type_} | {default} | {desc} |")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Workflows
    # ------------------------------------------------------------------

    def _render_workflows(self, pipeline: Pipeline) -> str:
        """Render workflows as a summary table plus per-workflow I/O tables."""
        lines: list[str] = [
            "## Workflows",
            "",
            "| Name | Description | Entry |",
            "|------|-------------|:-----:|",
        ]
        for wf in pipeline.workflows:
            lines.append(self._workflow_row(wf))

        # Per-workflow detail: inputs / outputs (only when present)
        for wf in pipeline.workflows:
            detail = self._workflow_detail(wf, pipeline)
            if detail:
                lines.append("")
                lines.append(detail)

        return "\n".join(lines)

    def _workflow_row(self, wf: Workflow) -> str:
        """Format a single workflow as a summary table row."""
        name = f"`{wf.name}`" if wf.name else "*(entry)*"
        desc = self._cell(wf.meta_description or wf.docstring)
        entry = "yes" if wf.is_entry else "no"
        return f"| {name} | {desc} | {entry} |"

    def _workflow_detail(self, wf: Workflow, pipeline: Pipeline) -> str:
        """Render per-workflow inputs, outputs, and calls if present."""
        name = wf.name or "entry"
        sections: list[str] = []

        # Inputs
        if wf.meta_inputs or wf.inputs:
            rows: list[str] = [
                f"### `{name}` Inputs",
                "",
                "| Name | Description |",
                "|------|-------------|",
            ]
            if wf.meta_inputs:
                for inp in wf.meta_inputs:
                    n = f"`{inp.get('name', '')}`"
                    d = self._cell(inp.get("description"))
                    rows.append(f"| {n} | {d} |")
            else:
                for inp in wf.inputs:
                    rows.append(f"| `{inp.name}` | {self._cell(inp.description)} |")
            sections.append("\n".join(rows))

        # Outputs
        if wf.meta_outputs or wf.outputs:
            rows = [
                f"### `{name}` Outputs",
                "",
                "| Name | Description |",
                "|------|-------------|",
            ]
            if wf.meta_outputs:
                for out in wf.meta_outputs:
                    n = f"`{out.get('name', '')}`"
                    d = self._cell(out.get("description"))
                    rows.append(f"| {n} | {d} |")
            else:
                for out in wf.outputs:
                    rows.append(f"| `{out.name}` | {self._cell(out.description)} |")
            sections.append("\n".join(rows))

        # Calls
        if wf.calls:
            call_names = ", ".join(f"`{c}`" for c in wf.calls)
            sections.append(f"**`{name}` calls:** {call_names}")

        return "\n\n".join(sections)

    # ------------------------------------------------------------------
    # Processes
    # ------------------------------------------------------------------

    def _render_processes(self, pipeline: Pipeline) -> str:
        """Render processes as a summary table plus per-process I/O tables."""
        lines: list[str] = [
            "## Processes",
            "",
            "| Name | Description |",
            "|------|-------------|",
        ]
        for proc in pipeline.processes:
            lines.append(self._process_row(proc))

        # Per-process detail: inputs / outputs
        for proc in pipeline.processes:
            detail = self._process_detail(proc)
            if detail:
                lines.append("")
                lines.append(detail)

        return "\n".join(lines)

    def _process_row(self, proc: Process) -> str:
        """Format a single process as a summary table row."""
        name = f"`{proc.name}`"
        desc = self._cell(proc.meta_description or proc.docstring)
        return f"| {name} | {desc} |"

    def _process_detail(self, proc: Process) -> str:
        """Render per-process inputs and outputs if present."""
        sections: list[str] = []

        # Inputs
        if proc.meta_inputs or proc.inputs:
            rows: list[str] = [
                f"### `{proc.name}` Inputs",
                "",
                "| Name | Type | Description |",
                "|------|------|-------------|",
            ]
            if proc.meta_inputs:
                for inp in proc.meta_inputs:
                    n = f"`{inp.get('name', '')}`"
                    t = f"`{inp.get('type', '-')}`"
                    d = self._cell(inp.get("description"))
                    rows.append(f"| {n} | {t} | {d} |")
            else:
                for inp in proc.inputs:
                    rows.append(f"| `{inp.name}` | `{inp.type}` | {self._cell(inp.description)} |")
            sections.append("\n".join(rows))

        # Outputs
        if proc.meta_outputs or proc.outputs:
            if proc.meta_outputs:
                rows = [
                    f"### `{proc.name}` Outputs",
                    "",
                    "| Name | Type | Pattern | Description |",
                    "|------|------|---------|-------------|",
                ]
                for out in proc.meta_outputs:
                    n = f"`{out.get('name', '')}`"
                    t = f"`{out.get('type', '-')}`"
                    p = f"`{out.get('pattern', '-')}`" if out.get("pattern") else "n/a"
                    d = self._cell(out.get("description"))
                    rows.append(f"| {n} | {t} | {p} | {d} |")
            else:
                rows = [
                    f"### `{proc.name}` Outputs",
                    "",
                    "| Name | Type | Emit | Description |",
                    "|------|------|------|-------------|",
                ]
                for out in proc.outputs:
                    emit = f"`{out.emit}`" if out.emit else "n/a"
                    rows.append(
                        f"| `{out.name}` | `{out.type}` | {emit} | {self._cell(out.description)} |"
                    )
            sections.append("\n".join(rows))

        return "\n\n".join(sections)

    # ------------------------------------------------------------------
    # Functions
    # ------------------------------------------------------------------

    def _render_functions(self, pipeline: Pipeline) -> str:
        """Render functions as a summary table."""
        lines: list[str] = [
            "## Functions",
            "",
            "| Name | Parameters | Returns | Description |",
            "|------|------------|---------|-------------|",
        ]
        for func in pipeline.functions:
            name = f"`{func.name}`"
            params = ", ".join(f"`{p.name}`" for p in func.params) if func.params else "n/a"
            returns = self._cell(func.return_description)
            desc = self._cell(func.docstring)
            lines.append(f"| {name} | {params} | {returns} | {desc} |")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _cell(value: str | None) -> str:
        """Sanitise a value for use inside a Markdown table cell."""
        if not value:
            return "n/a"
        # Collapse newlines and pipes that would break the table
        return value.replace("\n", " ").replace("|", "\\|").strip()
