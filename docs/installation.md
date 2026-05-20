# Installation

## Requirements

- Python 3.10+
- Java 11+ (for the Nextflow Language Server)
- Nextflow (optional — needed for parsing `nextflow.config`)

## Install

=== ":simple-astral:{ .middle } &nbsp; uv"

    ```bash
    # Run as one-off
    uvx nf-docs ./my-pipeline
    ```

    ```bash
    # Install so "nf-docs" is available globally
    uv tool install nf-docs

    # Run
    nf-docs ./my_pipeline
    ```

=== ":simple-python:{ .middle } &nbsp; pip"

    ```bash
    # Install
    pip install nf-docs

    # Run
    nf-docs ./my_pipeline
    ```

=== ":material-puzzle:{ .middle } &nbsp; Pixi"

    ```bash
    # One-time channel setup
    pixi config set default-channels '["conda-forge", "bioconda"]'

    # Install globally
    pixi global install nf-docs

    # Run
    nf-docs ./my_pipeline
    ```

=== ":simple-anaconda:{ .middle } &nbsp; Conda"

    ```bash
    # One-time channel setup
    conda config --add channels bioconda
    conda config --add channels conda-forge
    conda config --set channel_priority strict

    # Install
    conda install nf-docs

    # Run
    nf-docs ./my_pipeline
    ```

=== ":simple-git:{ .middle } &nbsp; Development"

    ```bash
    # Clone the git repo locally
    git clone https://github.com/ewels/nf-docs

    # Install in 'editable' mode with dev dependencies
    pip install -e ".[dev]"

    # Run
    nf-docs ./my_pipeline
    ```

## Package Links

- [:simple-pypi: PyPI](https://pypi.org/project/nf-docs/)
- [:simple-anaconda: Bioconda](https://bioconda.github.io/recipes/nf-docs/README.html)
- [:simple-github: GitHub Releases](https://github.com/ewels/nf-docs/releases)
