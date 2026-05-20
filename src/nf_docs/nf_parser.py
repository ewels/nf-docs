"""
Nextflow code parser for extracting structured information.

Parses Nextflow process/workflow definitions from LSP hover content
to extract inputs, outputs, and other metadata.
"""

import logging
import re
from dataclasses import dataclass, field

# Traditional Nextflow input qualifiers that should not be treated as typed variable names.
# Used to prevent false matches like "each: sample" being parsed as typed input "each" of type "sample".
_TRADITIONAL_QUALIFIERS = frozenset({"val", "path", "file", "env", "stdin", "tuple", "each"})

# Key prefix used in param_docs dicts to distinguish @return entries from @param entries.
RETURN_KEY_PREFIX = "_return_"
RETURN_KEY_UNNAMED = "_return"

# Regexes for extracting input/output sections from a process body.
# The terminators cover every Nextflow process section keyword.
_INPUT_SECTION_RE = re.compile(
    r"input:\s*(.*?)(?:output:|topic:|script:|shell:|exec:|\})", re.DOTALL
)
_OUTPUT_SECTION_RE = re.compile(
    r"output:\s*(.*?)(?:topic:|script:|shell:|exec:|when:|\})", re.DOTALL
)

logger = logging.getLogger(__name__)


@dataclass
class ParsedInput:
    """A parsed input declaration."""

    name: str
    type: str  # val, path, tuple, env, stdin, file
    qualifier: str = ""  # Additional info like stageAs, arity


@dataclass
class ParsedOutput:
    """A parsed output declaration."""

    name: str
    type: str  # val, path, tuple, env, stdout, file
    emit: str = ""
    optional: bool = False


@dataclass
class ParsedProcess:
    """Parsed process information from code."""

    name: str
    inputs: list[ParsedInput] = field(default_factory=list)
    outputs: list[ParsedOutput] = field(default_factory=list)


@dataclass
class ParsedWorkflow:
    """Parsed workflow information from code."""

    name: str
    takes: list[str] = field(default_factory=list)  # Input channel names
    emits: list[str] = field(default_factory=list)  # Output channel names


def parse_process_hover(hover_text: str) -> ParsedProcess | None:
    """
    Parse a process definition from LSP hover content.

    The hover content looks like:
    ```nextflow
    process FASTQC {
      input:
      tuple val(meta), path(reads)

      output:
      tuple val(meta), path("*.html"), emit: html
      tuple val(meta), path("*.zip"), emit: zip
      path "versions.yml", emit: versions
    }
    ```

    Args:
        hover_text: The hover content from LSP

    Returns:
        ParsedProcess with extracted inputs/outputs, or None if parsing fails
    """
    # Extract code from markdown code block
    code_match = re.search(r"```(?:nextflow|groovy)?\s*\n?(.*?)```", hover_text, re.DOTALL)
    if code_match:
        code = code_match.group(1)
    else:
        code = hover_text

    # Extract process name
    name_match = re.search(r"process\s+(\w+)\s*\{", code)
    if not name_match:
        return None

    process = ParsedProcess(name=name_match.group(1))

    # Extract input section
    input_match = _INPUT_SECTION_RE.search(code)
    if input_match:
        input_block = input_match.group(1)
        process.inputs = _parse_input_declarations(input_block)

    # Extract output section
    output_match = _OUTPUT_SECTION_RE.search(code)
    if output_match:
        output_block = output_match.group(1)
        process.outputs = _parse_output_declarations(output_block)

    return process


def _parse_input_declarations(block: str) -> list[ParsedInput]:
    """Parse input declarations from an input block."""
    inputs = []

    # Split by lines and parse each declaration
    lines = block.strip().split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        parsed = _parse_single_input(line)
        if parsed:
            inputs.append(parsed)

    return inputs


def _parse_single_input(line: str) -> ParsedInput | None:
    """Parse a single input declaration line.

    Handles both traditional DSL2 syntax and typed syntax:
      - Traditional: ``tuple val(meta), path(reads)``
      - Typed tuple: ``(meta, bam): Tuple<Map, Path>``
      - Typed simple: ``x: Integer``, ``bam: Path``
    """
    line = line.strip()
    if not line:
        return None

    # Handle typed destructured tuple: (meta, bam): Tuple<Map, Path>
    typed_tuple_match = re.match(r"\(([^)]+)\)\s*:\s*Tuple\s*<([^>]+)>", line)
    if typed_tuple_match:
        names_str = typed_tuple_match.group(1)
        types_str = typed_tuple_match.group(2)
        names = [n.strip() for n in names_str.split(",")]
        types = [t.strip() for t in types_str.split(",")]
        # Build descriptive components pairing names with their types
        parts = []
        for i, name in enumerate(names):
            if i < len(types):
                type_name = types[i]
                # Map Nextflow types to traditional qualifiers for display
                qualifier = _typed_to_qualifier(type_name)
                parts.append(f"{qualifier}({name})")
            else:
                parts.append(f"val({name})")
        return ParsedInput(
            name=", ".join(parts),
            type="tuple",
            qualifier=f"Tuple<{types_str}>",
        )

    # Handle typed simple input: x: Integer, bam: Path
    # Exclude traditional Nextflow qualifiers that could false-match (e.g. "each: sample")
    typed_simple_match = re.match(r"(\w+)\s*:\s*(\w+)$", line)
    if typed_simple_match and typed_simple_match.group(1) not in _TRADITIONAL_QUALIFIERS:
        name = typed_simple_match.group(1)
        type_name = typed_simple_match.group(2)
        qualifier = _typed_to_qualifier(type_name)
        return ParsedInput(name=name, type=qualifier, qualifier=type_name)

    # Handle tuple inputs: tuple val(meta), path(reads)
    if line.startswith("tuple"):
        # Extract components
        components = re.findall(r"(val|path|file|env)\s*\(([^)]+)\)", line)
        if components:
            # Create a descriptive name from components
            parts = []
            for comp_type, comp_name in components:
                parts.append(f"{comp_type}({comp_name})")
            name = ", ".join(parts)
            return ParsedInput(name=name, type="tuple")

    # Handle simple inputs: val(x), path(x), file(x), env(x), stdin
    simple_match = re.match(r"(val|path|file|env)\s*\(([^)]+)\)", line)
    if simple_match:
        input_type = simple_match.group(1)
        name = simple_match.group(2).strip().strip("'\"")
        return ParsedInput(name=name, type=input_type)

    # Handle stdin
    if line == "stdin" or line.startswith("stdin "):
        return ParsedInput(name="stdin", type="stdin")

    # Handle path with pattern: path '*.txt'
    path_pattern = re.match(r"path\s+['\"]([^'\"]+)['\"]", line)
    if path_pattern:
        return ParsedInput(name=path_pattern.group(1), type="path")

    return None


def _typed_to_qualifier(type_name: str) -> str:
    """Map a Nextflow type annotation to a traditional qualifier name.

    The Nextflow LSP may represent unknown or unresolved types as ``?``.

    Args:
        type_name: The type annotation (e.g. ``Path``, ``Map``, ``Integer``, ``?``).

    Returns:
        The corresponding traditional qualifier (``val``, ``path``, etc.).
    """
    path_types = {"Path", "File"}
    if type_name in path_types:
        return "path"
    # Everything else maps to val (Map, Integer, String, Boolean, ?, etc.)
    return "val"


def _parse_output_declarations(block: str) -> list[ParsedOutput]:
    """Parse output declarations from an output block."""
    outputs = []

    # Split by lines and parse each declaration
    lines = block.strip().split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        parsed = _parse_single_output(line)
        if parsed:
            outputs.append(parsed)

    return outputs


def _parse_single_output(line: str) -> ParsedOutput | None:
    """Parse a single output declaration line.

    Handles both traditional DSL2 syntax and typed/named assignment syntax:
      - Traditional: ``tuple val(meta), path("*.html"), emit: html``
      - Named assignment: ``txt = tuple(meta, file("*_svpileup.txt"))``
      - Named simple: ``bam = file("*.bam")``
      - Topic publish: ``>> 'topic_name'``
    """
    line = line.strip()
    if not line:
        return None

    # Skip topic publish lines: >> 'topic_name'
    if line.startswith(">>"):
        return None

    # Handle named assignment outputs: name = tuple(meta, file("*_svpileup.txt"))
    # or: name = file("*.bam"), name = val(something)
    named_match = re.match(r"(\w+)\s*=\s*(.+)", line)
    if named_match:
        emit_name = named_match.group(1)
        rhs = named_match.group(2).strip()
        return _parse_named_output(emit_name, rhs)

    # Extract emit name if present
    emit_match = re.search(r"emit:\s*(\w+)", line)
    emit_name = emit_match.group(1) if emit_match else ""

    # Extract optional flag
    optional = "optional:" in line or "optional :" in line

    # Handle tuple outputs: tuple val(meta), path("*.html"), emit: html
    if line.startswith("tuple"):
        components = re.findall(r"(val|path|file|env)\s*\(([^)]+)\)", line)
        if components:
            parts = []
            for comp_type, comp_name in components:
                parts.append(f"{comp_type}({comp_name})")
            name = ", ".join(parts)
            return ParsedOutput(name=name, type="tuple", emit=emit_name, optional=optional)

    # Handle simple outputs: path "versions.yml", emit: versions
    simple_match = re.match(r"(val|path|file|env|stdout)\s*\(?([^),]*)\)?", line)
    if simple_match:
        output_type = simple_match.group(1)
        name = (
            simple_match.group(2).strip().strip("'\"()") if simple_match.group(2) else output_type
        )
        return ParsedOutput(name=name, type=output_type, emit=emit_name, optional=optional)

    # Handle bare emit names from typed outputs (LSP returns just the name, e.g. "txt", "bam")
    bare_name_match = re.match(r"(\w+)$", line)
    if bare_name_match:
        name = bare_name_match.group(1)
        return ParsedOutput(name=name, type="", emit=name)

    return None


def _parse_tuple_components(inner: str) -> list[str]:
    """Parse the components inside a ``tuple(...)`` expression.

    Handles mixed content where some elements are qualified
    (``file("...")``, ``val(x)``, ``path("...")``) and others are bare
    names (``meta``, ``bam``).  Bare names are wrapped as ``val(name)``.

    Args:
        inner: The content inside the outer ``tuple()`` parentheses,
            e.g. ``'meta, file("*_svpileup.txt")'``.

    Returns:
        List of formatted component strings like ``["val(meta)", "file(\\"*_svpileup.txt\\")"]``.
    """
    parts: list[str] = []
    # Match qualified components and their positions
    qualifier_re = re.compile(r"(val|path|file|env)\s*\(([^)]+)\)")
    last_end = 0

    for m in qualifier_re.finditer(inner):
        # Any text between the last match end and this match start may contain bare names
        gap = inner[last_end : m.start()]
        for bare in re.findall(r"\b(\w+)\b", gap):
            parts.append(f"val({bare})")
        parts.append(f"{m.group(1)}({m.group(2)})")
        last_end = m.end()

    # Handle any trailing bare names after the last qualified component
    gap = inner[last_end:]
    for bare in re.findall(r"\b(\w+)\b", gap):
        parts.append(f"val({bare})")

    # Fallback: if nothing was parsed, split by comma and wrap as val()
    if not parts:
        names = [n.strip() for n in inner.split(",")]
        parts = [f"val({n})" for n in names if n]

    return parts


def _parse_named_output(emit_name: str, rhs: str) -> ParsedOutput:
    """Parse the right-hand side of a named output assignment.

    Handles patterns like:
      - ``tuple(meta, file("*_svpileup.txt"))``
      - ``file("*.bam")``
      - ``val(something)``
      - ``path("versions.yml")``

    Args:
        emit_name: The variable name (used as the emit name).
        rhs: The right-hand side expression after ``=``.

    Returns:
        A ParsedOutput with the emit name and parsed type/components.
    """
    rhs = rhs.strip()

    # Handle tuple(...): tuple(meta, file("*_svpileup.txt"))
    tuple_match = re.match(r"tuple\s*\((.+)\)\s*$", rhs)
    if tuple_match:
        inner = tuple_match.group(1)
        parts = _parse_tuple_components(inner)
        name = ", ".join(parts)
        return ParsedOutput(name=name, type="tuple", emit=emit_name)

    # Handle simple: file("*.bam"), path("versions.yml"), val(x)
    simple_match = re.match(r"(val|path|file|env|stdout)\s*\(([^)]*)\)", rhs)
    if simple_match:
        output_type = simple_match.group(1)
        name = simple_match.group(2).strip().strip("'\"") if simple_match.group(2) else output_type
        return ParsedOutput(name=name, type=output_type, emit=emit_name)

    # Fallback: treat entire rhs as the name
    return ParsedOutput(name=rhs, type="val", emit=emit_name)


def parse_workflow_hover(hover_text: str) -> ParsedWorkflow | None:
    """
    Parse a workflow definition from LSP hover content.

    Args:
        hover_text: The hover content from LSP

    Returns:
        ParsedWorkflow with extracted takes/emits, or None if parsing fails
    """
    # Extract code from markdown code block
    code_match = re.search(r"```(?:nextflow|groovy)?\s*\n?(.*?)```", hover_text, re.DOTALL)
    if code_match:
        code = code_match.group(1)
    else:
        code = hover_text

    # Extract workflow name (may be empty for entry workflow)
    name_match = re.search(r"workflow\s+(\w+)?\s*\{", code)
    if not name_match:
        return None

    name = name_match.group(1) or ""
    workflow = ParsedWorkflow(name=name)

    # Extract take section
    take_match = re.search(r"take:\s*(.*?)(?:main:|emit:|\})", code, re.DOTALL)
    if take_match:
        take_block = take_match.group(1)
        for line in take_block.strip().split("\n"):
            line = line.strip()
            if line and not line.startswith("//"):
                workflow.takes.append(line)

    # Extract emit section
    emit_match = re.search(r"emit:\s*(.*?)(?:\}|$)", code, re.DOTALL)
    if emit_match:
        emit_block = emit_match.group(1)
        for line in emit_block.strip().split("\n"):
            line = line.strip()
            if line and not line.startswith("//"):
                # Handle "name = channel" or just "name"
                if "=" in line:
                    emit_name = line.split("=")[0].strip()
                else:
                    emit_name = line
                workflow.emits.append(emit_name)

    return workflow


def is_code_block(text: str) -> bool:
    """Check if text appears to be a code block rather than documentation."""
    # If it contains code fences, it's code
    if "```" in text:
        return True

    # If it starts with process/workflow/def keywords, it's code
    stripped = text.strip()
    if re.match(r"^(process|workflow|def)\s+\w+", stripped):
        return True

    # If it contains typical code patterns
    code_patterns = [
        r"\binput:\s*$",
        r"\boutput:\s*$",
        r"\bscript:\s*$",
        r"\btuple\s+val\(",
        r"\bpath\s*\(",
        r"\bval\s*\(",
    ]
    for pattern in code_patterns:
        if re.search(pattern, text, re.MULTILINE):
            return True

    return False


def enrich_outputs_from_source(
    outputs: list[ParsedOutput],
    source: str,
    process_name: str,
) -> list[ParsedOutput]:
    """Enrich bare-name outputs with full declarations parsed from ``.nf`` source text.

    When the Nextflow LSP returns bare emit names for typed process outputs
    (e.g. ``txt``, ``bam`` instead of ``txt = tuple(meta, file("*.txt"))``),
    this function parses the source text to find the named-assignment
    output declarations and provide full type and component information.

    If a bare output's emit name matches a named assignment in the source, the
    bare output is replaced with the richer parsed version.  Outputs that are
    already fully qualified (have a non-empty ``type``) are left untouched.

    Args:
        outputs: The outputs parsed from the LSP hover (may contain bare names).
        source: The ``.nf`` source file contents.
        process_name: Name of the process to locate in the source.

    Returns:
        A new list of ``ParsedOutput`` objects, enriched where possible.
    """
    # Only enrich if there are bare outputs (type is empty)
    if not any(not o.type for o in outputs):
        return outputs

    # Find the process block in source
    proc_pattern = re.compile(rf"process\s+{re.escape(process_name)}\s*\{{", re.MULTILINE)
    proc_match = proc_pattern.search(source)
    if not proc_match:
        logger.debug(f"Could not find process {process_name} in source")
        return outputs

    # Extract the process body (find matching closing brace)
    proc_start = proc_match.start()
    brace_depth = 0
    proc_body = ""
    for i in range(proc_match.end() - 1, len(source)):
        if source[i] == "{":
            brace_depth += 1
        elif source[i] == "}":
            brace_depth -= 1
            if brace_depth == 0:
                proc_body = source[proc_start : i + 1]
                break

    if not proc_body:
        return outputs

    # Extract the output section from the source process body
    output_match = _OUTPUT_SECTION_RE.search(proc_body)
    if not output_match:
        return outputs

    # Parse the source output declarations
    source_outputs = _parse_output_declarations(output_match.group(1))

    # Build a lookup by emit name
    source_by_emit: dict[str, ParsedOutput] = {}
    for out in source_outputs:
        if out.emit:
            source_by_emit[out.emit] = out

    # Replace bare outputs with enriched versions
    enriched = []
    for out in outputs:
        if not out.type and out.emit in source_by_emit:
            enriched.append(source_by_emit[out.emit])
        else:
            enriched.append(out)

    return enriched
