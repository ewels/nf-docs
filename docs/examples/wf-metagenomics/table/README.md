<!-- BEGIN_NF_DOCS -->
# epi2me-labs/wf-metagenomics

**Version:** v2.14.2 · Taxonomic classification of metagenomic sequencing data.

## Inputs

### Other

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| `--aws_image_prefix` | n/a | `string` | n/a | no |
| `--aws_queue` | n/a | `string` | n/a | no |
| `--monochrome_logs` | n/a | `boolean` | n/a | no |
| `--validate_params` | n/a | `boolean` | `True` | no |
| `--show_hidden_params` | n/a | `boolean` | n/a | no |

### Input Options

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| `--fastq` | FASTQ files to use in the analysis. | `string` | n/a | no |
| `--bam` | BAM or unaligned BAM (uBAM) files to use in the analysis. | `string` | n/a | no |
| `--classifier` | Kraken2 or Minimap2 workflow to be used for classification of reads. | `string` | `kraken2` | no |
| `--analyse_unclassified` | Analyse unclassified reads from input directory. By default the workflow will not process reads in the unclassified directory. | `boolean` | `False` | no |
| `--exclude_host` | A FASTA or MMI file of the host reference. Reads that align with this reference will be excluded from the analysis. | `string` | n/a | no |

### Sample Options

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| `--sample_sheet` | A CSV file used to map barcodes to sample aliases. The sample sheet can be provided when the input data is a directory containing sub-directories with FASTQ files. | `string` | n/a | no |
| `--sample` | A single sample name for non-multiplexed data. Permissible if passing a single .fastq(.gz) file or directory of .fastq(.gz) files. | `string` | n/a | no |

### Reference Options

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| `--database_set` | Sets the reference, databases and taxonomy datasets that will be used for classifying reads. Choices: ['ncbi_16s_18s','ncbi_16s_18s_28s_ITS', 'SILVA_138_1', 'Greengenes2_plus', 'Standard-8', 'PlusPF-8', 'PlusPFP-8']. Memory requirement will be slightly higher than the size of the database. Standard-8, PlusPF-8 and PlusPFP-8 databases require more than 8GB and are only available in the kraken2 approach. | `string` | `Standard-8` | no |
| `--store_dir` | Where to store initial download of database. | `string` | `store_dir` | no |
| `--database` | Not required but can be used to specifically override Kraken2 database [.tar.gz or Directory]. | `string` | n/a | no |
| `--taxonomy` | Not required but can be used to specifically override taxonomy database. Change the default to use a different taxonomy file  [.tar.gz or directory]. | `string` | n/a | no |
| `--reference` | Override the FASTA reference file selected by the database_set parameter. It can be a FASTA format reference sequence collection or a minimap2 MMI format index. | `string` | n/a | no |
| `--ref2taxid` | Not required but can be used to specify a  ref2taxid mapping. Format is .tsv (refname  taxid), no header row. | `string` | n/a | no |
| `--taxonomic_rank` | Returns results at the taxonomic rank chosen. In the Kraken2 pipeline: set the level that Bracken will estimate abundance at. Default: S (species). Other possible options are P (phylum), C (class), O (order), F (family), and G (genus). | `string` | `S` | no |

### Kraken2 Options

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| `--bracken_length` | Set the length value Bracken will use | `integer` | n/a | no |
| `--bracken_threshold` | Set the minimum read threshold Bracken will use to consider a taxon | `integer` | `10` | no |
| `--kraken2_memory_mapping` | Avoids loading database into RAM | `boolean` | `False` | no |
| `--kraken2_confidence` | Kraken2 Confidence score threshold. Default: 0.0. Valid interval: 0-1 | `number` | `0.0` | no |

### Minimap2 Options

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| `--minimap2filter` | Filter output of minimap2 by taxids inc. child nodes, E.g. "9606,1404" | `string` | n/a | no |
| `--minimap2exclude` | Invert minimap2filter and exclude the given taxids instead | `boolean` | `False` | no |
| `--keep_bam` | Copy bam files into the output directory. | `boolean` | `False` | no |
| `--minimap2_by_reference` | Add a table with the mean sequencing depth per reference, standard deviation and coefficient of variation. It adds a scatterplot of the sequencing depth vs. the coverage and a heatmap showing the depth per percentile to the report | `boolean` | `False` | no |
| `--min_percent_identity` | Minimum percentage of identity with the matched reference to define a sequence as classified; sequences with a value lower than this are defined as unclassified. | `number` | `90` | no |
| `--min_ref_coverage` | Minimum coverage value to define a sequence as classified; sequences with a coverage value lower than this are defined as unclassified. Use this option if you expect reads whose lengths are similar to the references' lengths. | `number` | `0` | no |

### Antimicrobial Resistance Options

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| `--amr` | Scan reads for antimicrobial resistance or virulence genes | `boolean` | `False` | no |
| `--amr_db` | Database of antimicrobial resistance or virulence genes to use. | `string` | `resfinder` | no |
| `--amr_minid` | Threshold of required identity to report a match between a gene in the database and fastq reads. Valid interval: 0-100 | `integer` | `80` | no |
| `--amr_mincov` | Minimum coverage (breadth-of) threshold required to report a match between a gene in the database and fastq reads. Valid interval: 0-100. | `integer` | `80` | no |

### Report Options

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| `--abundance_threshold` | Remove those taxa whose abundance is equal or lower than the chosen value. | `number` | `0` | no |
| `--n_taxa_barplot` | Number of most abundant taxa to be displayed in the barplot. The rest of taxa will be grouped under the "Other" category. | `integer` | `9` | no |

### Output Options

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| `--out_dir` | Directory for output of all user-facing files. | `string` | `output` | no |
| `--igv` | Enable IGV visualisation in the EPI2ME Desktop Application by creating the required files. This will cause the workflow to emit the BAM files as well. If using a custom reference, this must be a FASTA file and not a minimap2 MMI format index. | `boolean` | `False` | no |
| `--include_read_assignments` | A per sample TSV file that indicates the taxonomy assigned to each sequence. | `boolean` | `False` | no |
| `--output_unclassified` | Output a FASTQ of the unclassified reads. | `boolean` | `False` | no |

### Advanced Options

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| `--min_len` | Specify read length lower limit. | `integer` | `0` | no |
| `--min_read_qual` | Specify read quality lower limit. | `number` | n/a | no |
| `--max_len` | Specify read length upper limit | `integer` | n/a | no |
| `--threads` | Maximum number of CPU threads to use in each parallel workflow task. | `integer` | `4` | no |

### Miscellaneous Options

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| `--disable_ping` | Enable to prevent sending a workflow ping. | `boolean` | `False` | no |
| `--help` | n/a | `boolean` | `False` | no |
| `--version` | Display version and exit. | `boolean` | `False` | no |

## Configuration

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `database_sets.ncbi_16s_18s.reference` | `string` | `s3://ont-open-data/workflow-databases/wf-metagenomics-dbs/ncbi_16s_18s/ncbi_targeted_loci_16s_18s.fna` | n/a |
| `database_sets.ncbi_16s_18s.database` | `string` | `s3://ont-open-data/workflow-databases/wf-metagenomics-dbs/ncbi_16s_18s/ncbi_targeted_loci_kraken2.tar.gz` | n/a |
| `database_sets.ncbi_16s_18s.ref2taxid` | `string` | `s3://ont-open-data/workflow-databases/wf-metagenomics-dbs/ncbi_16s_18s/ref2taxid.targloci.tsv` | n/a |
| `database_sets.ncbi_16s_18s.taxonomy` | `string` | `s3://ont-open-data/workflow-databases/wf-metagenomics-dbs/ncbi_16s_18s/new_taxdump_2025-01-01.zip` | n/a |
| `database_sets.ncbi_16s_18s_28s_ITS.reference` | `string` | `s3://ont-open-data/workflow-databases/wf-metagenomics-dbs/ncbi_16s_18s_28s_ITS/ncbi_16s_18s_28s_ITS.fna` | n/a |
| `database_sets.ncbi_16s_18s_28s_ITS.database` | `string` | `s3://ont-open-data/workflow-databases/wf-metagenomics-dbs/ncbi_16s_18s_28s_ITS/ncbi_16s_18s_28s_ITS_kraken2.tar.gz` | n/a |
| `database_sets.ncbi_16s_18s_28s_ITS.ref2taxid` | `string` | `s3://ont-open-data/workflow-databases/wf-metagenomics-dbs/ncbi_16s_18s_28s_ITS/ref2taxid.ncbi_16s_18s_28s_ITS.tsv` | n/a |
| `database_sets.ncbi_16s_18s_28s_ITS.taxonomy` | `string` | `s3://ont-open-data/workflow-databases/wf-metagenomics-dbs/ncbi_16s_18s_28s_ITS/new_taxdump_2025-01-01.zip` | n/a |
| `database_sets.SILVA_138_1.reference` | `string` | `s3://ont-open-data/workflow-databases/wf-metagenomics-dbs/SILVA_138_1/silva.fna` | n/a |
| `database_sets.SILVA_138_1.database` | `string` | `s3://ont-open-data/workflow-databases/wf-metagenomics-dbs/SILVA_138_1/kraken2.tar.gz` | n/a |
| `database_sets.SILVA_138_1.ref2taxid` | `string` | `s3://ont-open-data/workflow-databases/wf-metagenomics-dbs/SILVA_138_1/seqid2taxid.map` | n/a |
| `database_sets.SILVA_138_1.taxonomy` | `string` | `s3://ont-open-data/workflow-databases/wf-metagenomics-dbs/SILVA_138_1/taxonomy.tar.gz` | n/a |
| `database_sets.Greengenes2_plus.reference` | `string` | `s3://ont-open-data/workflow-databases/wf-metagenomics-dbs/Greengenes2_plus/sequences_mm2format.fasta` | n/a |
| `database_sets.Greengenes2_plus.database` | `string` | `s3://ont-open-data/workflow-databases/wf-metagenomics-dbs/Greengenes2_plus/kraken2.tar.gz` | n/a |
| `database_sets.Greengenes2_plus.ref2taxid` | `string` | `s3://ont-open-data/workflow-databases/wf-metagenomics-dbs/Greengenes2_plus/sequences_mm2format.taxid.map` | n/a |
| `database_sets.Greengenes2_plus.taxonomy` | `string` | `s3://ont-open-data/workflow-databases/wf-metagenomics-dbs/Greengenes2_plus/taxdump.tar.gz` | n/a |
| `schema_ignore_params` | `string` | `show_hidden_params,validate_params,monochrome_logs,aws_queue,aws_image_prefix,database_sets,wf` | n/a |
| `wf.example_cmd` | `array` | `["--fastq \\'wf-metagenomics-demo/test_data\\'"]` | n/a |
| `wf.agent` | `string` | n/a | n/a |
| `wf.container_sha` | `string` | `sha38db033c15c74ae7cac3c609fdfe2c8d2a53ef6f` | n/a |
| `wf.common_sha` | `string` | `shafdd79f8e4a6faad77513c36f623693977b92b08e` | n/a |
| `wf.container_sha_amr` | `string` | `shad8ebf2fc3b15d43612df71170bdd4d8669fe1731` | n/a |

## Workflows

| Name | Description | Entry |
|------|-------------|:-----:|
| *(entry)* | n/a | yes |
| `minimap_pipeline` | n/a | no |
| `kraken_pipeline` | n/a | no |
| `run_common` | n/a | no |
| `run_amr` | n/a | no |

### `minimap_pipeline` Inputs

| Name | Description |
|------|-------------|
| `samples` | n/a |
| `reference` | n/a |
| `ref2taxid` | n/a |
| `taxonomy` | n/a |
| `taxonomic_rank` | n/a |
| `common_minimap2_opts` | n/a |
| `output_igv` | n/a |

### `minimap_pipeline` Outputs

| Name | Description |
|------|-------------|
| `abundance_table` | n/a |
| `lineages` | n/a |
| `alignment_reports` | n/a |
| `metadata_after_taxonomy` | n/a |

### `kraken_pipeline` Inputs

| Name | Description |
|------|-------------|
| `samples` | n/a |
| `taxonomy` | n/a |
| `database` | n/a |
| `bracken_length` | n/a |
| `taxonomic_rank` | n/a |

### `kraken_pipeline` Outputs

| Name | Description |
|------|-------------|
| `abundance_table` | n/a |
| `lineages` | n/a |
| `metadata_after_taxonomy` | n/a |

### `run_common` Inputs

| Name | Description |
|------|-------------|
| `samples` | n/a |
| `host_reference` | n/a |
| `common_minimap2_opts` | n/a |

### `run_common` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |

### `run_amr` Inputs

| Name | Description |
|------|-------------|
| `input` | n/a |
| `amr_db` | n/a |
| `amr_minid` | n/a |
| `amr_mincov` | n/a |

### `run_amr` Outputs

| Name | Description |
|------|-------------|
| `reports` | n/a |

## Processes

| Name | Description |
|------|-------------|
| `minimap` | n/a |
| `minimapTaxonomy` | n/a |
| `extractMinimap2Reads` | n/a |
| `getAlignmentStats` | n/a |
| `run_kraken2` | n/a |
| `run_bracken` | n/a |
| `output_kraken2_read_assignments` | n/a |
| `exclude_host_reads` | n/a |
| `fastcat` | n/a |
| `checkBamHeaders` | n/a |
| `validateIndex` | n/a |
| `mergeBams` | n/a |
| `catSortBams` | n/a |
| `sortBam` | n/a |
| `bamstats` | n/a |
| `move_or_compress_fq_file` | n/a |
| `split_fq_file` | n/a |
| `validate_sample_sheet` | Python script for validating a sample sheet. The script will write messages to STDOUT if the sample sheet is invalid. In case there are no issues, no message is emitted. The sample sheet will be published to the output dir. |
| `samtools_index` | n/a |
| `getParams` | n/a |
| `configure_igv` | n/a |
| `abricate` | n/a |
| `abricate_json` | n/a |
| `filter_references` | n/a |
| `abricateVersion` | n/a |
| `getVersions` | n/a |
| `getVersionsCommon` | n/a |
| `createAbundanceTables` | n/a |
| `publishReads` | n/a |
| `publish` | n/a |
| `makeReport` | n/a |

### `minimap` Inputs

| Name | Type | Description |
|------|------|-------------|
| `val(meta), path(concat_seqs), path(stats)` | `tuple` | n/a |

### `minimap` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta)` | `tuple` | n/a | n/a |

### `minimapTaxonomy` Inputs

| Name | Type | Description |
|------|------|-------------|
| `val(meta), path(assignments)` | `tuple` | n/a |

### `minimapTaxonomy` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta)` | `tuple` | n/a | n/a |

### `extractMinimap2Reads` Inputs

| Name | Type | Description |
|------|------|-------------|
| `val(meta), path("alignment.bam"), path("alignment.bai"), path("bamstats"), val(n_unmapped)` | `tuple` | n/a |

### `extractMinimap2Reads` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta)` | `tuple` | n/a | n/a |

### `getAlignmentStats` Inputs

| Name | Type | Description |
|------|------|-------------|
| `val(meta), path("input.bam"), path("input.bam.bai"), path("bamstats")` | `tuple` | n/a |

### `getAlignmentStats` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `${meta.alias` | `path` | n/a | n/a |

### `run_kraken2` Inputs

| Name | Type | Description |
|------|------|-------------|
| `val(meta), path("reads.fq.gz"), path(fastq_stats)` | `tuple` | n/a |

### `run_kraken2` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta)` | `tuple` | n/a | n/a |

### `run_bracken` Inputs

| Name | Type | Description |
|------|------|-------------|
| `val(meta), path("kraken2.report"), path("kraken2.assignments.tsv")` | `tuple` | n/a |
| `bracken_length.txt` | `path` | n/a |

### `run_bracken` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta)` | `tuple` | n/a | n/a |

### `output_kraken2_read_assignments` Inputs

| Name | Type | Description |
|------|------|-------------|
| `val(meta)` | `tuple` | n/a |

### `output_kraken2_read_assignments` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*_lineages.kraken2.assignments.tsv")` | `tuple` | n/a | n/a |

### `exclude_host_reads` Inputs

| Name | Type | Description |
|------|------|-------------|
| `val(meta), path(concat_seqs), path(fastcat_stats)` | `tuple` | n/a |

### `exclude_host_reads` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*.unmapped.fastq.gz"), path("stats_unmapped"), env(n_seqs_passed_host_depletion)` | `tuple` | `fastq` | n/a |
| `val(meta), path("*.host.bam"), path("*.host.bam.bai")` | `tuple` | `host_bam` | n/a |
| `val(meta), path("*.unmapped.bam"), path("*.unmapped.bam.bai")` | `tuple` | `no_host_bam` | n/a |

### `fastcat` Inputs

| Name | Type | Description |
|------|------|-------------|
| `val(meta), path(input_src, stageAs: "input_src")` | `tuple` | n/a |

### `fastcat` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("fastq_chunks/*.fastq.gz"), path("fastcat_stats")` | `tuple` | n/a | n/a |

### `checkBamHeaders` Inputs

| Name | Type | Description |
|------|------|-------------|
| `val(meta), path("input_dir/reads*.bam")` | `tuple` | n/a |

### `checkBamHeaders` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("input_dir/reads*.bam", includeInputs: true), env(IS_UNALIGNED), env(MIXED_HEADERS), env(IS_SORTED)` | `tuple` | n/a | n/a |

### `validateIndex` Inputs

| Name | Type | Description |
|------|------|-------------|
| `val(meta), path("reads.bam"), path("reads.bam.bai")` | `tuple` | n/a |

### `validateIndex` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("reads.bam", includeInputs: true), path("reads.bam.bai", includeInputs: true), env(HAS_VALID_INDEX)` | `tuple` | n/a | n/a |

### `mergeBams` Inputs

| Name | Type | Description |
|------|------|-------------|
| `val(meta), path("input_bams/reads*.bam")` | `tuple` | n/a |

### `mergeBams` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("reads.bam"), path("reads.bam.bai")` | `tuple` | n/a | n/a |

### `catSortBams` Inputs

| Name | Type | Description |
|------|------|-------------|
| `val(meta), path("input_bams/reads*.bam")` | `tuple` | n/a |

### `catSortBams` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("reads.bam"), path("reads.bam.bai")` | `tuple` | n/a | n/a |

### `sortBam` Inputs

| Name | Type | Description |
|------|------|-------------|
| `val(meta), path("reads.bam")` | `tuple` | n/a |

### `sortBam` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("reads.sorted.bam"), path("reads.sorted.bam.bai")` | `tuple` | n/a | n/a |

### `bamstats` Inputs

| Name | Type | Description |
|------|------|-------------|
| `val(meta), path("reads.bam"), path("reads.bam.bai")` | `tuple` | n/a |

### `bamstats` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("reads.bam"), path("reads.bam.bai"), path("bamstats_results")` | `tuple` | n/a | n/a |

### `move_or_compress_fq_file` Inputs

| Name | Type | Description |
|------|------|-------------|
| `val(meta), path(input)` | `tuple` | n/a |

### `move_or_compress_fq_file` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("seqs.fastq.gz")` | `tuple` | n/a | n/a |

### `split_fq_file` Inputs

| Name | Type | Description |
|------|------|-------------|
| `val(meta), path(input)` | `tuple` | n/a |

### `split_fq_file` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("fastq_chunks/*.fastq.gz")` | `tuple` | n/a | n/a |

### `validate_sample_sheet` Inputs

| Name | Type | Description |
|------|------|-------------|
| `sample_sheet.csv` | `path` | n/a |

### `validate_sample_sheet` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `path("sample_sheet.csv")` | `tuple` | n/a | n/a |

### `samtools_index` Inputs

| Name | Type | Description |
|------|------|-------------|
| `val(meta), path("reads.bam")` | `tuple` | n/a |

### `samtools_index` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("reads.bam"), path("reads.bam.bai")` | `tuple` | n/a | n/a |

### `getParams` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `params.json` | `path` | n/a | n/a |

### `configure_igv` Inputs

| Name | Type | Description |
|------|------|-------------|
| `file-names.txt` | `path` | n/a |

### `configure_igv` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `igv.json` | `path` | n/a | n/a |

### `abricate` Inputs

| Name | Type | Description |
|------|------|-------------|
| `val(meta), path("input_reads.fastq.gz"), path("stats/")` | `tuple` | n/a |

### `abricate` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta)` | `tuple` | n/a | n/a |

### `abricate_json` Inputs

| Name | Type | Description |
|------|------|-------------|
| `val(meta)` | `tuple` | n/a |

### `abricate_json` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta)` | `tuple` | n/a | n/a |

### `filter_references` Inputs

| Name | Type | Description |
|------|------|-------------|
| `bam_flagstats/*` | `path` | n/a |

### `filter_references` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `path("reduced_reference.fasta.gz"), path("reduced_reference.fasta.gz.fai"), path("reduced_reference.fasta.gz.gzi")` | `tuple` | n/a | n/a |

### `abricateVersion` Inputs

| Name | Type | Description |
|------|------|-------------|
| `input_versions.txt` | `path` | n/a |

### `abricateVersion` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `versions.txt` | `path` | n/a | n/a |

### `getVersions` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `versions.txt` | `path` | n/a | n/a |

### `getVersionsCommon` Inputs

| Name | Type | Description |
|------|------|-------------|
| `versions.txt` | `path` | n/a |

### `getVersionsCommon` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `versions_all.txt` | `path` | n/a | n/a |

### `createAbundanceTables` Inputs

| Name | Type | Description |
|------|------|-------------|
| `lineages/*` | `path` | n/a |

### `createAbundanceTables` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `abundance_table_*.tsv` | `path` | `abundance_tsv` | n/a |

### `publishReads` Inputs

| Name | Type | Description |
|------|------|-------------|
| `val(meta), path("reads.fq.gz"), path("ids.txt")` | `tuple` | n/a |

### `publishReads` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `${meta.alias` | `path` | n/a | n/a |

### `publish` Inputs

| Name | Type | Description |
|------|------|-------------|
| `path(fname), val(dirname)` | `tuple` | n/a |

### `publish` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `fname` | `path` | n/a | n/a |

### `makeReport` Inputs

| Name | Type | Description |
|------|------|-------------|
| `abundance_table.tsv` | `path` | n/a |
| `alignment_stats/*` | `path` | n/a |
| `lineages/*` | `path` | n/a |
| `versions/*` | `path` | n/a |
| `params.json` | `path` | n/a |
| `amr/*` | `path` | n/a |

### `makeReport` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `${report_name` | `path` | n/a | n/a |

## Functions

| Name | Parameters | Returns | Description |
|------|------------|---------|-------------|
| `is_target_file` | `file`, `extensions` | n/a | Check if a file ends with one of the target extensions. |
| `is_excluded` | `p`, `margs` | n/a | Check if a file path is flagged for exclusion. |
| `add_run_IDs_and_basecall_models_to_meta` | `ch`, `allow_multiple_basecall_models` | n/a | Take a channel of the shape `[meta, reads, path-to-stats-dir \| null]` (or `[meta, [reads, index], path-to-stats-dir \| null]` in the case of XAM) and extract the run IDs and basecall model, from the `run_ids` and `basecaller` files in the stats directory, into the metamap. If the path to the stats dir is `null`, add an empty list. |
| `add_number_of_reads_to_meta` | `ch`, `input_type_format` | n/a | Take a channel of the shape `[meta, reads, path-to-stats-dir \| null]` and do the following: - For `fastcat`, extract the number of reads from the `n_seqs` file. - For `bamstats`, extract the number of primary alignments and unmapped reads from the `bamstats.flagstat.tsv` file. Then, add add these metrics to the meta map. If the path to the stats dir is `null`, set the values to 0 when adding them. If not set to 'fastq', input is assumed to be 'bam'. |
| `fastq_ingress` | `arguments` | n/a | Take a map of input arguments, find valid FASTQ inputs, and return a channel with elements of `[metamap, seqs.fastq.gz \| null, path-to-fastcat-stats \| null]`. The second item is `null` for sample sheet entries without a matching barcode directory. The last item is `null` if `fastcat` was not run (it is only run on directories containing more than one FASTQ file or when `stats: true`). - "input": path to either: (i) input FASTQ file, (ii) top-level directory containing FASTQ files, (iii) directory containing sub-directories which contain FASTQ files - "sample": string to name single sample - "sample_sheet": path to CSV sample sheet - "analyse_unclassified": boolean. Whether to ingress unclassified (failed to demux) reads - "analyse_fail": boolean. Whether to ingress any sequence files contained in `*_fail` directories. - "stats": boolean whether to write the `fastcat` stats - "fastcat_extra_args": string with extra arguments to pass to `fastcat` - "required_sample_types": list of zero or more required sample types expected to be present in the sample sheet - "per_read_stats": boolean. If true, output a bgzipped TSV containing a summary of each read to fastcat_stats/per-read-stats.tsv.gz. - "fastq_chunk": null or a number of reads to place into chunked FASTQ files - "allow_multiple_basecall_models": emit data of samples that had more than one basecall model; if this is `false`, such samples will be emitted as `[meta, null, null]` The first element is a map with metadata, the second is the path to the `.fastq.gz` file with the (potentially concatenated) sequences and the third is the path to the directory with the `fastcat` statistics. The second element is `null` for sample sheet entries for which no corresponding barcode directory was found. The third element is `null` if `fastcat` was not run. |
| `xam_ingress` | `arguments` | n/a | Take a map of input arguments, find valid (u)BAM inputs, and return a channel with elements of `[metamap, reads.bam \| null, path-to-bamstats-results \| null]`. The second item is `null` for sample sheet entries without a matching barcode directory or samples containing only uBAM files when `keep_unaligned` is `false`. The last item is `null` if `bamstats` was not run (it is only run when `stats: true`). - "input": path to either: (i) input (u)BAM file, (ii) top-level directory containing (u)BAM files, (iii) directory containing sub-directories which contain (u)BAM files - "sample": string to name single sample - "sample_sheet": path to CSV sample sheet - "analyse_unclassified": boolean. Whether to ingress unclassified (failed to demux) reads - "analyse_fail": boolean. Whether to ingress any sequence files contained in `*_fail` directories. - "stats": boolean whether to run `bamstats` - "keep_unaligned": boolean whether to include uBAM files - "return_fastq": boolean whether to convert to FASTQ (this will always run `fastcat`) - "fastcat_extra_args": string with extra arguments to pass to `fastcat` - "required_sample_types": list of zero or more required sample types expected to be present in the sample sheet - "per_read_stats": boolean. If true, output a bgzipped TSV containing a summary - "fastq_chunk": null or a number of reads to place into chunked FASTQ files - "allow_multiple_basecall_models": boolean. If true, emit data of samples that had more than one basecall model; if this is `false`, such samples will be emitted as `[meta, null, null]` The first element is a map with metadata, the second is the path to the `.bam` file with the (potentially merged) sequences and the third is the path to the directory with the `bamstats` statistics. The second element is `null` for sample sheet entries for which no corresponding barcode directory was found and for samples with only uBAM files when `keep_unaligned: false`. The third element is `null` if `bamstats` was not run. |
| `parse_arguments` | `func_name`, `arguments`, `extra_kwargs` | n/a | Parse input arguments for `fastq_ingress` or `xam_ingress`. for details) the argument-parsing to be tailored to a particular ingress function) |
| `get_valid_inputs` | `margs`, `extensions` | n/a | Find valid inputs based on the target extensions and return a branched channel with branches `missing`, `files` and `dir`, which are of the shape `[metamap, input_path \| null]` (with `input_path` pointing to a target file or a directory containing target files, respectively). `missing` contains sample sheet entries for which no corresponding barcodes were found. Checks whether the input is a single target file, a top-level directory with target files, or a directory containing sub-directories (usually barcodes) with target files. |
| `create_metamap` | `arguments` | n/a | Create a map that contains at least these keys: `[alias, barcode, type]`. `alias` is required, `barcode` and `type` are filled with default values if missing. Additional entries are allowed. |
| `get_target_files_in_dir` | `dir`, `extensions`, `margs`, `recursive` | n/a | Get all target files below this directory. |
| `get_sample_sheet` | `sample_sheet`, `required_sample_types` | n/a | Check the sample sheet and return a channel with its rows if it is valid. in the sample sheet |

---

*This pipeline was built with [Nextflow](https://nextflow.io).
Documentation generated by [nf-docs](https://github.com/ewels/nf-docs) v0.2.0 on 2026-03-03 22:40:56 UTC.*

<!-- END_NF_DOCS -->
