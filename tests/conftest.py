"""Pytest configuration and fixtures."""

import json
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolate_xdg_dirs(tmp_path_factory, monkeypatch) -> None:
    """
    Point XDG cache and config at throwaway directories for every test.

    Without this, any test that extracts with caching left entries in the
    developer's real ``~/.cache/nf-docs/`` - and because the Language Server is
    mocked out in tests, those entries are empty results that a later real run
    could pick up. It also keeps anything reaching ``load_config()`` independent
    of whether the person running the suite has a real config file.
    """
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path_factory.mktemp("xdg_cache")))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path_factory.mktemp("xdg_config")))


@pytest.fixture
def sample_schema() -> dict:
    """Sample nextflow_schema.json content."""
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Test Pipeline",
        "description": "A test pipeline for unit tests",
        "$defs": {
            "input_output_options": {
                "title": "Input/output options",
                "type": "object",
                "properties": {
                    "input": {
                        "type": "string",
                        "format": "file-path",
                        "description": "Path to input samplesheet",
                        "help_text": "The samplesheet should contain sample IDs and file paths.",
                    },
                    "outdir": {
                        "type": "string",
                        "format": "directory-path",
                        "description": "Output directory",
                        "default": "./results",
                    },
                },
                "required": ["input"],
            },
            "reference_options": {
                "title": "Reference genome options",
                "type": "object",
                "properties": {
                    "genome": {
                        "type": "string",
                        "description": "Reference genome ID",
                        "enum": ["GRCh37", "GRCh38", "GRCm38"],
                    },
                    "fasta": {
                        "type": "string",
                        "format": "file-path",
                        "description": "Path to FASTA file",
                    },
                },
            },
        },
    }


@pytest.fixture
def sample_schema_file(tmp_path: Path, sample_schema: dict) -> Path:
    """Create a sample schema file."""
    schema_file = tmp_path / "nextflow_schema.json"
    schema_file.write_text(json.dumps(sample_schema, indent=2))
    return schema_file


@pytest.fixture
def sample_nextflow_file() -> str:
    """Sample Nextflow file content."""
    return '''
/**
 * Align reads to reference genome using BWA MEM.
 *
 * @param reads Tuple of sample ID and fastq files
 * @param index BWA index files
 * @return Tuple of sample ID and BAM file
 */
process BWA_MEM {
    container 'biocontainers/bwa:0.7.17'
    cpus 8
    memory '16.GB'

    input:
    tuple val(sample_id), path(reads)
    path index

    output:
    tuple val(sample_id), path("*.bam"), emit: bam

    script:
    """
    bwa mem -t ${task.cpus} ${index}/*.fa ${reads} | samtools view -bS - > ${sample_id}.bam
    """
}

/**
 * Run FastQC quality control.
 */
process FASTQC {
    input:
    tuple val(sample_id), path(reads)

    output:
    path "*.html", emit: html
    path "*.zip", emit: zip

    script:
    """
    fastqc ${reads}
    """
}

/**
 * Main analysis workflow.
 *
 * @param input_ch Input channel with samples
 */
workflow ANALYSIS {
    take:
    input_ch

    main:
    FASTQC(input_ch)
    BWA_MEM(input_ch, params.index)

    emit:
    bam = BWA_MEM.out.bam
    qc = FASTQC.out.html
}

workflow {
    Channel.fromPath(params.input) | ANALYSIS
}
'''


@pytest.fixture
def sample_config_file() -> str:
    """Sample nextflow.config content."""
    return """
manifest {
    name = 'test-pipeline'
    version = '1.0.0'
    description = 'A test pipeline'
    author = 'Test Author'
    homePage = 'https://example.com'
}

params {
    input = null
    outdir = './results'
    genome = 'GRCh38'
    max_cpus = 16
    max_memory = '128.GB'
    max_time = '24.h'
}

process {
    cpus = 2
    memory = '4.GB'
}
"""


@pytest.fixture
def sample_pipeline(
    tmp_path: Path, sample_schema: dict, sample_nextflow_file: str, sample_config_file: str
) -> Path:
    """Create a sample pipeline directory."""
    # Create schema
    schema_file = tmp_path / "nextflow_schema.json"
    schema_file.write_text(json.dumps(sample_schema, indent=2))

    # Create main.nf
    main_file = tmp_path / "main.nf"
    main_file.write_text(sample_nextflow_file)

    # Create config
    config_file = tmp_path / "nextflow.config"
    config_file.write_text(sample_config_file)

    # Create README
    readme_file = tmp_path / "README.md"
    readme_file.write_text("# Test Pipeline\n\nThis is a test pipeline for nf-docs.\n")

    return tmp_path
