"""Tests for the Nextflow code parser."""

from nf_docs.nf_parser import (
    ParsedInput,
    ParsedOutput,
    _parse_named_output,
    _parse_single_input,
    _parse_single_output,
    _typed_to_qualifier,
    enrich_outputs_from_source,
    parse_process_hover,
    parse_workflow_hover,
)


class TestParseSingleInput:
    """Tests for _parse_single_input."""

    def test_empty_line(self):
        assert _parse_single_input("") is None
        assert _parse_single_input("   ") is None

    def test_simple_val(self):
        result = _parse_single_input("val(x)")
        assert result == ParsedInput(name="x", type="val")

    def test_simple_path(self):
        result = _parse_single_input("path(reads)")
        assert result == ParsedInput(name="reads", type="path")

    def test_simple_env(self):
        result = _parse_single_input("env(MY_VAR)")
        assert result == ParsedInput(name="MY_VAR", type="env")

    def test_simple_file(self):
        result = _parse_single_input("file(data)")
        assert result == ParsedInput(name="data", type="file")

    def test_stdin(self):
        result = _parse_single_input("stdin")
        assert result == ParsedInput(name="stdin", type="stdin")

    def test_path_with_pattern(self):
        result = _parse_single_input("path '*.txt'")
        assert result == ParsedInput(name="*.txt", type="path")

    def test_tuple_traditional(self):
        result = _parse_single_input("tuple val(meta), path(reads)")
        assert result is not None
        assert result.type == "tuple"
        assert result.name == "val(meta), path(reads)"

    def test_tuple_multiple_paths(self):
        result = _parse_single_input("tuple val(meta), path(reads), path(index)")
        assert result is not None
        assert result.type == "tuple"
        assert result.name == "val(meta), path(reads), path(index)"

    # Typed input syntax tests

    def test_typed_tuple_two_elements(self):
        """Typed tuple: (meta, bam): Tuple<Map, Path>"""
        result = _parse_single_input("(meta, bam): Tuple<Map, Path>")
        assert result is not None
        assert result.type == "tuple"
        assert result.name == "val(meta), path(bam)"
        assert result.qualifier == "Tuple<Map, Path>"

    def test_typed_tuple_three_elements(self):
        """Typed tuple: (meta, bam, txt): Tuple<Map, Path, Path>"""
        result = _parse_single_input("(meta, bam, txt): Tuple<Map, Path, Path>")
        assert result is not None
        assert result.type == "tuple"
        assert result.name == "val(meta), path(bam), path(txt)"
        assert result.qualifier == "Tuple<Map, Path, Path>"

    def test_typed_tuple_all_vals(self):
        """Typed tuple with all value types."""
        result = _parse_single_input("(name, count): Tuple<String, Integer>")
        assert result is not None
        assert result.type == "tuple"
        assert result.name == "val(name), val(count)"
        assert result.qualifier == "Tuple<String, Integer>"

    def test_typed_simple_integer(self):
        """Simple typed input: x: Integer"""
        result = _parse_single_input("x: Integer")
        assert result is not None
        assert result.type == "val"
        assert result.name == "x"
        assert result.qualifier == "Integer"

    def test_typed_simple_path(self):
        """Simple typed input: bam: Path"""
        result = _parse_single_input("bam: Path")
        assert result is not None
        assert result.type == "path"
        assert result.name == "bam"
        assert result.qualifier == "Path"

    def test_typed_simple_string(self):
        """Simple typed input: name: String"""
        result = _parse_single_input("name: String")
        assert result is not None
        assert result.type == "val"
        assert result.name == "name"
        assert result.qualifier == "String"

    def test_typed_simple_map(self):
        """Simple typed input: meta: Map"""
        result = _parse_single_input("meta: Map")
        assert result is not None
        assert result.type == "val"
        assert result.name == "meta"
        assert result.qualifier == "Map"

    def test_typed_simple_file(self):
        """Simple typed input: data: File"""
        result = _parse_single_input("data: File")
        assert result is not None
        assert result.type == "path"
        assert result.name == "data"
        assert result.qualifier == "File"

    def test_typed_tuple_with_question_mark_type(self):
        """Typed tuple with ? (unresolved) type from LSP: (meta, bam): Tuple<?, Path>"""
        result = _parse_single_input("(meta, bam): Tuple<?, Path>")
        assert result is not None
        assert result.type == "tuple"
        assert result.name == "val(meta), path(bam)"
        assert result.qualifier == "Tuple<?, Path>"

    def test_typed_tuple_three_with_question_mark(self):
        """Typed 3-tuple with ? type: (meta, bam, txt): Tuple<?, Path, Path>"""
        result = _parse_single_input("(meta, bam, txt): Tuple<?, Path, Path>")
        assert result is not None
        assert result.type == "tuple"
        assert result.name == "val(meta), path(bam), path(txt)"
        assert result.qualifier == "Tuple<?, Path, Path>"

    def test_each_qualifier_not_mismatched_as_typed(self):
        """Traditional 'each' qualifier must not be parsed as typed input."""
        # 'each' followed by a colon-like pattern should not match typed simple
        result = _parse_single_input("each val(x)")
        # 'each val(x)' is not currently handled - should return None rather than misparsing
        assert result is None

    def test_typed_tuple_mismatched_counts(self):
        """Typed tuple with more names than types falls back to val() for extras."""
        result = _parse_single_input("(a, b, c): Tuple<Map, Path>")
        assert result is not None
        assert result.type == "tuple"
        # 'a' -> val(a), 'b' -> path(b), 'c' -> val(c) (fallback)
        assert result.name == "val(a), path(b), val(c)"
        assert result.qualifier == "Tuple<Map, Path>"


class TestTypedToQualifier:
    """Tests for _typed_to_qualifier."""

    def test_path_type(self):
        assert _typed_to_qualifier("Path") == "path"

    def test_file_type(self):
        assert _typed_to_qualifier("File") == "path"

    def test_map_type(self):
        assert _typed_to_qualifier("Map") == "val"

    def test_integer_type(self):
        assert _typed_to_qualifier("Integer") == "val"

    def test_string_type(self):
        assert _typed_to_qualifier("String") == "val"

    def test_boolean_type(self):
        assert _typed_to_qualifier("Boolean") == "val"


class TestParseSingleOutput:
    """Tests for _parse_single_output."""

    def test_empty_line(self):
        assert _parse_single_output("") is None
        assert _parse_single_output("   ") is None

    def test_simple_path_with_emit(self):
        result = _parse_single_output('path "versions.yml", emit: versions')
        assert result is not None
        assert result.type == "path"
        assert result.name == "versions.yml"
        assert result.emit == "versions"

    def test_tuple_with_emit(self):
        result = _parse_single_output('tuple val(meta), path("*.html"), emit: html')
        assert result is not None
        assert result.type == "tuple"
        assert result.name == 'val(meta), path("*.html")'
        assert result.emit == "html"

    def test_stdout(self):
        result = _parse_single_output("stdout")
        assert result is not None
        assert result.type == "stdout"

    def test_optional_output(self):
        result = _parse_single_output('path "*.log", emit: log, optional: true')
        assert result is not None
        assert result.optional is True

    # Named assignment output tests (typed syntax)

    def test_named_tuple_output(self):
        """Named assignment: txt = tuple(meta, file("*_svpileup.txt"))"""
        result = _parse_single_output('txt = tuple(meta, file("*_svpileup.txt"))')
        assert result is not None
        assert result.type == "tuple"
        assert result.emit == "txt"
        assert 'file("*_svpileup.txt")' in result.name

    def test_named_tuple_with_two_files(self):
        """Named assignment: bam = tuple(meta, file("*_sorted.bam"))"""
        result = _parse_single_output('bam = tuple(meta, file("*_sorted.bam"))')
        assert result is not None
        assert result.type == "tuple"
        assert result.emit == "bam"

    def test_named_simple_file(self):
        """Named assignment: report = file("*.html")"""
        result = _parse_single_output('report = file("*.html")')
        assert result is not None
        assert result.type == "file"
        assert result.name == "*.html"
        assert result.emit == "report"

    def test_named_simple_path(self):
        """Named assignment: versions = path("versions.yml")"""
        result = _parse_single_output('versions = path("versions.yml")')
        assert result is not None
        assert result.type == "path"
        assert result.name == "versions.yml"
        assert result.emit == "versions"

    def test_named_val(self):
        """Named assignment: count = val(total)"""
        result = _parse_single_output("count = val(total)")
        assert result is not None
        assert result.type == "val"
        assert result.name == "total"
        assert result.emit == "count"

    def test_bare_emit_name(self):
        """Bare identifier output from typed syntax LSP hover (e.g. just 'txt')."""
        result = _parse_single_output("txt")
        assert result is not None
        assert result.name == "txt"
        assert result.emit == "txt"
        assert result.type == ""

    def test_bare_emit_name_bam(self):
        """Bare identifier output: bam."""
        result = _parse_single_output("bam")
        assert result is not None
        assert result.name == "bam"
        assert result.emit == "bam"

    def test_bare_emit_name_bedpe(self):
        """Bare identifier output: bedpe."""
        result = _parse_single_output("bedpe")
        assert result is not None
        assert result.name == "bedpe"
        assert result.emit == "bedpe"

    def test_topic_publish_skipped(self):
        """Topic publish lines should be skipped."""
        assert _parse_single_output(">> 'sample_outputs'") is None
        assert _parse_single_output('>> "my_topic"') is None


class TestParseNamedOutput:
    """Tests for _parse_named_output."""

    def test_tuple_with_file(self):
        result = _parse_named_output("txt", 'tuple(meta, file("*_svpileup.txt"))')
        assert result.type == "tuple"
        assert result.emit == "txt"
        assert "file" in result.name

    def test_tuple_with_multiple_components(self):
        result = _parse_named_output("out", 'tuple(meta, file("*.bam"), file("*.bai"))')
        assert result.type == "tuple"
        assert result.emit == "out"

    def test_tuple_plain_names(self):
        result = _parse_named_output("result", "tuple(meta, data)")
        assert result.type == "tuple"
        assert result.emit == "result"
        assert result.name == "val(meta), val(data)"

    def test_simple_file(self):
        result = _parse_named_output("report", 'file("report.html")')
        assert result.type == "file"
        assert result.emit == "report"
        assert result.name == "report.html"

    def test_simple_path(self):
        result = _parse_named_output("versions", 'path("versions.yml")')
        assert result.type == "path"
        assert result.emit == "versions"
        assert result.name == "versions.yml"

    def test_fallback(self):
        result = _parse_named_output("x", "some_expression")
        assert result.type == "val"
        assert result.emit == "x"
        assert result.name == "some_expression"


class TestParseProcessHover:
    """Tests for parse_process_hover."""

    def test_traditional_process(self):
        """Parse a traditional DSL2 process definition."""
        hover = """```nextflow
process FASTQC {
  input:
  tuple val(meta), path(reads)

  output:
  tuple val(meta), path("*.html"), emit: html
  path "versions.yml", emit: versions
}
```"""
        result = parse_process_hover(hover)
        assert result is not None
        assert result.name == "FASTQC"
        assert len(result.inputs) == 1
        assert result.inputs[0].type == "tuple"
        assert len(result.outputs) == 2
        assert result.outputs[0].emit == "html"
        assert result.outputs[1].emit == "versions"

    def test_typed_process(self):
        """Parse a typed process definition (Nextflow typed syntax)."""
        hover = """```nextflow
process SV_PILEUP {
  input:
  (meta, bam): Tuple<Map, Path>

  output:
  txt = tuple(meta, file("*_svpileup.txt"))
  bam = tuple(meta, file("*_svpileup.bam"))
}
```"""
        result = parse_process_hover(hover)
        assert result is not None
        assert result.name == "SV_PILEUP"
        assert len(result.inputs) == 1
        assert result.inputs[0].type == "tuple"
        assert result.inputs[0].name == "val(meta), path(bam)"
        assert result.inputs[0].qualifier == "Tuple<Map, Path>"
        assert len(result.outputs) == 2
        assert result.outputs[0].emit == "txt"
        assert result.outputs[0].type == "tuple"
        assert result.outputs[1].emit == "bam"
        assert result.outputs[1].type == "tuple"

    def test_typed_process_three_inputs(self):
        """Parse typed process with 3-element tuple input."""
        hover = """```nextflow
process AGGREGATE {
  input:
  (meta, bam, txt): Tuple<Map, Path, Path>

  output:
  txt = tuple(meta, file("*_aggregate.txt"))
}
```"""
        result = parse_process_hover(hover)
        assert result is not None
        assert result.name == "AGGREGATE"
        assert len(result.inputs) == 1
        assert result.inputs[0].name == "val(meta), path(bam), path(txt)"
        assert len(result.outputs) == 1
        assert result.outputs[0].emit == "txt"

    def test_typed_process_with_topic_section(self):
        """Topic section should not interfere with output parsing."""
        hover = """```nextflow
process MY_PROC {
  input:
  (meta, bam): Tuple<Map, Path>

  output:
  txt = tuple(meta, file("*.txt"))

  topic:
  >> 'sample_outputs'
}
```"""
        result = parse_process_hover(hover)
        assert result is not None
        assert len(result.inputs) == 1
        assert len(result.outputs) == 1
        assert result.outputs[0].emit == "txt"

    def test_mixed_typed_and_traditional_outputs(self):
        """Process with both named assignment and traditional output syntax."""
        hover = """```nextflow
process MIXED {
  input:
  val(x)

  output:
  txt = file("output.txt")
  path "versions.yml", emit: versions
}
```"""
        result = parse_process_hover(hover)
        assert result is not None
        assert len(result.outputs) == 2
        assert result.outputs[0].emit == "txt"
        assert result.outputs[0].type == "file"
        assert result.outputs[1].emit == "versions"

    def test_typed_simple_inputs(self):
        """Process with simple typed inputs."""
        hover = """```nextflow
process SIMPLE_TYPED {
  input:
  x: Integer
  bam: Path

  output:
  result = val(x)
}
```"""
        result = parse_process_hover(hover)
        assert result is not None
        assert len(result.inputs) == 2
        assert result.inputs[0].name == "x"
        assert result.inputs[0].type == "val"
        assert result.inputs[0].qualifier == "Integer"
        assert result.inputs[1].name == "bam"
        assert result.inputs[1].type == "path"
        assert result.inputs[1].qualifier == "Path"

    def test_no_code_block(self):
        """Handle hover text without code fences."""
        result = parse_process_hover("just some text")
        assert result is None

    def test_empty_process(self):
        """Process with no inputs or outputs."""
        hover = """```nextflow
process EMPTY {
  script:
  echo "hello"
}
```"""
        result = parse_process_hover(hover)
        assert result is not None
        assert result.name == "EMPTY"
        assert len(result.inputs) == 0
        assert len(result.outputs) == 0

    def test_topic_in_output_block_skipped(self):
        """Topic publish lines within output block should be skipped."""
        hover = """```nextflow
process WITH_TOPIC {
  output:
  txt = file("out.txt")
  >> 'my_topic'
}
```"""
        result = parse_process_hover(hover)
        assert result is not None
        # Only the file output, not the topic line
        assert len(result.outputs) == 1
        assert result.outputs[0].emit == "txt"

    def test_typed_process_with_bare_outputs(self):
        """Real LSP hover for a typed process with bare emit names as outputs."""
        hover = """```nextflow
process SV_PILEUP {
  input:
  (meta, bam): Tuple<?, Path>

  output:
  txt
  bam
}
```"""
        result = parse_process_hover(hover)
        assert result is not None
        assert result.name == "SV_PILEUP"
        # Input: typed tuple with ? type
        assert len(result.inputs) == 1
        assert result.inputs[0].type == "tuple"
        assert result.inputs[0].name == "val(meta), path(bam)"
        assert result.inputs[0].qualifier == "Tuple<?, Path>"
        # Outputs: bare emit names
        assert len(result.outputs) == 2
        assert result.outputs[0].name == "txt"
        assert result.outputs[0].emit == "txt"
        assert result.outputs[1].name == "bam"
        assert result.outputs[1].emit == "bam"

    def test_typed_process_three_inputs_bare_output(self):
        """Real LSP hover for typed process with 3-element tuple and bare output."""
        hover = """```nextflow
process AGGREGATE_SV_PILEUP {
  input:
  (meta, bam, txt): Tuple<?, Path, Path>

  output:
  txt
}
```"""
        result = parse_process_hover(hover)
        assert result is not None
        assert len(result.inputs) == 1
        assert result.inputs[0].name == "val(meta), path(bam), path(txt)"
        assert len(result.outputs) == 1
        assert result.outputs[0].emit == "txt"


class TestParseWorkflowHover:
    """Tests for parse_workflow_hover."""

    def test_workflow_with_takes_and_emits(self):
        hover = """```nextflow
workflow MAIN {
  take:
  reads
  genome

  emit:
  bam = aligned
  vcf = variants
}
```"""
        result = parse_workflow_hover(hover)
        assert result is not None
        assert result.name == "MAIN"
        assert result.takes == ["reads", "genome"]
        assert result.emits == ["bam", "vcf"]

    def test_empty_workflow(self):
        hover = """```nextflow
workflow EMPTY {
}
```"""
        result = parse_workflow_hover(hover)
        assert result is not None
        assert result.name == "EMPTY"
        assert result.takes == []
        assert result.emits == []


class TestEnrichOutputsFromSource:
    """Tests for enriching bare outputs with data from .nf source files."""

    SV_PILEUP_SOURCE = """\
process SV_PILEUP {
    container "community.wave.seqera.io/library/fgsv:0.2.1"

    input:
    (meta, bam): Tuple<?, Path>

    output:
    txt = tuple(meta, file("*_svpileup.txt"))
    bam = tuple(meta, file("*_svpileup.bam"))

    topic:
    tuple(meta, file("*_svpileup.txt")) >> 'sample_outputs'

    script:
    def prefix = "${meta.id}"
    \"""
    fgsv SvPileup --input ${bam} --output ${prefix}_svpileup
    \"""
}
"""

    def test_bare_outputs_enriched(self):
        """Bare emit names are replaced with full declarations from source."""
        bare_outputs = [
            ParsedOutput(name="txt", type="", emit="txt"),
            ParsedOutput(name="bam", type="", emit="bam"),
        ]
        result = enrich_outputs_from_source(bare_outputs, self.SV_PILEUP_SOURCE, "SV_PILEUP")

        assert len(result) == 2
        assert result[0].emit == "txt"
        assert result[0].type == "tuple"
        assert "file(" in result[0].name
        assert result[1].emit == "bam"
        assert result[1].type == "tuple"
        assert "file(" in result[1].name

    def test_already_qualified_outputs_not_changed(self):
        """Outputs that already have a type are left untouched."""
        qualified_outputs = [
            ParsedOutput(name="val(meta), path(*.html)", type="tuple", emit="html"),
        ]
        result = enrich_outputs_from_source(qualified_outputs, self.SV_PILEUP_SOURCE, "SV_PILEUP")

        assert len(result) == 1
        assert result[0] is qualified_outputs[0]  # same object, unchanged

    def test_process_not_found_returns_originals(self):
        """If the process name isn't in the source, return outputs unchanged."""
        bare_outputs = [ParsedOutput(name="txt", type="", emit="txt")]
        result = enrich_outputs_from_source(
            bare_outputs, "process OTHER_PROC {\n  output:\n  x = val(1)\n}\n", "SV_PILEUP"
        )
        assert result is bare_outputs

    def test_partial_match_enriches_only_matching(self):
        """Only bare outputs whose emit matches a source declaration are enriched."""
        outputs = [
            ParsedOutput(name="txt", type="", emit="txt"),
            ParsedOutput(name="unknown", type="", emit="unknown"),
        ]
        result = enrich_outputs_from_source(outputs, self.SV_PILEUP_SOURCE, "SV_PILEUP")

        assert result[0].type == "tuple"  # enriched
        assert result[0].emit == "txt"
        assert result[1].type == ""  # not found in source, unchanged
        assert result[1].emit == "unknown"

    def test_simple_named_output(self):
        """Named simple output: versions = path("versions.yml")."""
        source = (
            'process SIMPLE {\n  output:\n  versions = path("versions.yml")\n\n  script:\n  ""\n}\n'
        )

        bare_outputs = [ParsedOutput(name="versions", type="", emit="versions")]
        result = enrich_outputs_from_source(bare_outputs, source, "SIMPLE")

        assert result[0].emit == "versions"
        assert result[0].type == "path"
        assert result[0].name == "versions.yml"
