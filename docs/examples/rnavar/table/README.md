<!-- BEGIN_NF_DOCS -->
# nf-core/rnavar

**Version:** 1.3.0dev · GATK4 RNA variant calling pipeline

## Inputs

### Input/output options

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| `--input` | Path to comma-separated file containing information about the samples in the experiment. | `string` | n/a | yes |
| `--outdir` | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. | `string` | n/a | yes |
| `--tools` | Specify which additional tools RNAvar should use. Values can be 'seq2hla', 'bcfann', 'snpeff', 'vep' or 'merge'. If you specify 'merge', the pipeline runs both snpeff and VEP annotation. | `string` | n/a | no |
| `--save_merged_fastq` | Save FastQ files after merging re-sequenced libraries in the results directory. | `boolean` | n/a | no |

### Preprocessing of alignment

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| `--extract_umi` | Specify whether to remove UMIs from the reads with UMI-tools extract. | `boolean` | n/a | no |
| `--umitools_extract_method` | UMI pattern to use. Can be either 'string' (default) or 'regex'. | `string` | `string` | no |
| `--umitools_bc_pattern` | The UMI barcode pattern to use e.g. 'NNNNNN' indicates that the first 6 nucleotides of the read are from the UMI. | `string` | n/a | no |
| `--umitools_bc_pattern2` | The UMI barcode pattern to use if the UMI is located in read 2. | `string` | n/a | no |
| `--umitools_umi_separator` | The character that separates the UMI in the read name. Most likely a colon if you skipped the extraction with UMI-tools and used other software. | `string` | n/a | no |

### Alignment options

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| `--aligner` | Specifies the alignment algorithm to use. | `string` | `star` | yes |
| `--star_index` | Path to STAR index folder or compressed file (tar.gz) | `string` | n/a | no |
| `--star_twopass` | Enable STAR 2-pass mapping mode. | `boolean` | `True` | no |
| `--star_ignore_sjdbgtf` | Do not use GTF file during STAR index building step | `boolean` | n/a | no |
| `--star_max_memory_bamsort` | Option to limit RAM when sorting BAM file. Value to be specified in bytes. If 0, will be set to the genome index size. | `integer` | `0` | no |
| `--star_bins_bamsort` | Specifies the number of genome bins for coordinate-sorting | `integer` | `50` | no |
| `--star_max_collapsed_junc` | Specifies the maximum number of collapsed junctions | `integer` | `1000000` | no |
| `--star_max_intron_size` | Specifies the maximum intron size | `integer` | n/a | no |
| `--seq_center` | Sequencing center information to be added to read group of BAM files. | `string` | n/a | no |
| `--seq_platform` | Specify the sequencing platform used | `string` | `illumina` | yes |
| `--save_unaligned` | Where possible, save unaligned reads from aligner to the results directory. | `boolean` | n/a | no |
| `--save_align_intermeds` | Save the intermediate BAM files from the alignment step. | `boolean` | n/a | no |
| `--bam_csi_index` | Create a CSI index for BAM files instead of the traditional BAI index. This will be required for genomes with larger chromosome sizes. | `boolean` | n/a | no |

### Postprocessing of alignment

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| `--remove_duplicates` | Specify whether to remove duplicates from the BAM during Picard MarkDuplicates step. | `boolean` | n/a | no |

### Variant calling

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| `--gatk_hc_call_conf` | The minimum phred-scaled confidence threshold at which variants should be called. | `integer` | `20` | no |
| `--generate_gvcf` | Enable generation of GVCFs by sample additionnaly to the VCFs. | `boolean` | n/a | no |
| `--gatk_interval_scatter_count` | Number of times the gene interval list to be split in order to run GATK haplotype caller in parallel | `integer` | `25` | no |
| `--no_intervals` | Do not use gene interval file during variant calling | `boolean` | n/a | no |

### Variant filtering

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| `--gatk_vf_qd_filter` | Value to be used for the QualByDepth (QD) filter | `number` | `2` | no |
| `--gatk_vf_fs_filter` | Value to be used for the FisherStrand (FS) filter | `number` | `30` | no |
| `--gatk_vf_window_size` | The window size (in bases) in which to evaluate clustered SNPs. | `integer` | `35` | no |
| `--gatk_vf_cluster_size` | The number of SNPs which make up a cluster. Must be at least 2. | `integer` | `3` | no |

### Variant Annotation

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| `--vep_cache` | Path to VEP cache. | `string` | `s3://annotation-cache/vep_cache/` | no |
| `--snpeff_cache` | Path to snpEff cache. | `string` | `s3://annotation-cache/snpeff_cache/` | no |
| `--vep_include_fasta` | Allow usage of fasta file for annotation with VEP | `boolean` | n/a | no |
| `--vep_dbnsfp` | Enable the use of the VEP dbNSFP plugin. | `boolean` | n/a | no |
| `--dbnsfp` | Path to dbNSFP processed file. | `string` | n/a | no |
| `--dbnsfp_tbi` | Path to dbNSFP tabix indexed file. | `string` | n/a | no |
| `--dbnsfp_consequence` | Consequence to annotate with | `string` | n/a | no |
| `--dbnsfp_fields` | Fields to annotate with | `string` | `rs_dbSNP,HGVSc_VEP,HGVSp_VEP,1000Gp3_EAS_AF,1000Gp3_AMR_AF,LRT_score,GERP++_RS,gnomAD_exomes_AF` | no |
| `--vep_loftee` | Enable the use of the VEP LOFTEE plugin. | `boolean` | n/a | no |
| `--vep_spliceai` | Enable the use of the VEP SpliceAI plugin. | `boolean` | n/a | no |
| `--spliceai_snv` | Path to spliceai raw scores snv file. | `string` | n/a | no |
| `--spliceai_snv_tbi` | Path to spliceai raw scores snv tabix indexed file. | `string` | n/a | no |
| `--spliceai_indel` | Path to spliceai raw scores indel file. | `string` | n/a | no |
| `--spliceai_indel_tbi` | Path to spliceai raw scores indel tabix indexed file. | `string` | n/a | no |
| `--vep_spliceregion` | Enable the use of the VEP SpliceRegion plugin. | `boolean` | n/a | no |
| `--vep_custom_args` | Add an extra custom argument to VEP. | `string` | `--everything --filter_common --per_gene --total_length --offline --format vcf` | no |
| `--outdir_cache` | The output directory where the cache will be saved. You have to use absolute paths to storage on Cloud infrastructure. | `string` | n/a | no |
| `--vep_out_format` | VEP output-file format. | `string` | `vcf` | no |
| `--bcftools_annotations` | A vcf file containing custom annotations to be used with bcftools annotate. Needs to be bgzipped. | `string` | n/a | no |
| `--bcftools_annotations_tbi` | Index file for `bcftools_annotations` | `string` | n/a | no |
| `--bcftools_columns` | Optional text file with list of columns to use from `bcftools_annotations`, one name per row | `string` | n/a | no |
| `--bcftools_header_lines` | Text file with the header lines of `bcftools_annotations` | `string` | n/a | no |

### Pipeline stage options

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| `--skip_baserecalibration` | Skip the process of base recalibration steps i.e., GATK BaseRecalibrator and GATK ApplyBQSR. | `boolean` | n/a | no |
| `--skip_intervallisttools` | Skip the process of preparing interval lists for the GATK variant calling step | `boolean` | n/a | no |
| `--skip_variantfiltration` | Skip variant filtering of GATK | `boolean` | n/a | no |
| `--skip_variantannotation` | Skip variant annotation | `boolean` | n/a | no |
| `--skip_multiqc` | Skip MultiQC reports | `boolean` | n/a | no |
| `--skip_exon_bed_check` | Skip the check of the exon bed | `boolean` | n/a | no |

### General reference genome options

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| `--igenomes_base` | The base path to the igenomes reference files | `string` | `s3://ngi-igenomes/igenomes/` | no |
| `--igenomes_ignore` | Do not load the iGenomes reference config. | `boolean` | n/a | no |
| `--save_reference` | Save built references. | `boolean` | n/a | no |
| `--download_cache` | Download annotation cache. | `boolean` | n/a | no |

### Reference genome options

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| `--genome` | Name of iGenomes reference. | `string` | `GRCh38` | no |
| `--fasta` | Path to FASTA genome file. | `string` | n/a | no |
| `--dict` | Path to FASTA dictionary file. | `string` | n/a | no |
| `--fasta_fai` | Path to FASTA reference index. | `string` | n/a | no |
| `--gtf` | Path to GTF annotation file. | `string` | n/a | no |
| `--gff` | Path to GFF3 annotation file. | `string` | n/a | no |
| `--exon_bed` | Path to BED file containing exon intervals. This will be created from the GTF file if not specified. | `string` | n/a | no |
| `--read_length` | Read length | `number` | `150` | no |
| `--known_indels` | Path to known indels file. | `string` | n/a | no |
| `--known_indels_tbi` | Path to known indels file index. | `string` | n/a | no |
| `--dbsnp` | Path to dbsnp file. | `string` | n/a | no |
| `--dbsnp_tbi` | Path to dbsnp index. | `string` | n/a | no |
| `--snpeff_db` | snpEff DB version. | `string` | n/a | no |
| `--vep_genome` | VEP genome. | `string` | n/a | no |
| `--vep_species` | VEP species. | `string` | n/a | no |
| `--vep_cache_version` | VEP cache version. | `integer` | n/a | no |
| `--feature_type` | Type of feature to parse from annotation file | `string` | `exon` | no |

### Institutional config options

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| `--custom_config_version` | Git commit id for Institutional configs. | `string` | `master` | no |
| `--custom_config_base` | Base directory for Institutional configs. | `string` | `https://raw.githubusercontent.com/nf-core/configs/master` | no |
| `--config_profile_name` | Institutional config name. | `string` | n/a | no |
| `--config_profile_description` | Institutional config description. | `string` | n/a | no |
| `--config_profile_contact` | Institutional config contact information. | `string` | n/a | no |
| `--config_profile_url` | Institutional config URL link. | `string` | n/a | no |

### Generic options

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| `--version` | Display version and exit. | `boolean` | n/a | no |
| `--publish_dir_mode` | Method used to save pipeline results to output directory. | `string` | `copy` | no |
| `--email` | Email address for completion summary. | `string` | n/a | no |
| `--email_on_fail` | Email address for completion summary, only when pipeline fails. | `string` | n/a | no |
| `--plaintext_email` | Send plain-text email instead of HTML. | `boolean` | n/a | no |
| `--max_multiqc_email_size` | File size limit when attaching MultiQC reports to summary emails. | `string` | `25.MB` | no |
| `--monochrome_logs` | Do not use coloured log outputs. | `boolean` | n/a | no |
| `--hook_url` | Incoming hook URL for messaging service | `string` | n/a | no |
| `--multiqc_config` | Custom config file to supply to MultiQC. | `string` | n/a | no |
| `--multiqc_logo` | Custom logo file to supply to MultiQC. File name must also be set in the MultiQC config file | `string` | n/a | no |
| `--multiqc_methods_description` | Custom MultiQC yaml file containing HTML including a methods description. | `string` | n/a | no |
| `--multiqc_title` | MultiQC report title. Printed as page header, used for filename if not otherwise specified. | `string` | n/a | no |
| `--validate_params` | Boolean whether to validate parameters against the schema at runtime | `boolean` | `True` | no |
| `--modules_testdata_base_path` | Base URL or local path to location of pipeline test dataset files | `string` | `https://raw.githubusercontent.com/nf-core/test-datasets/modules/data/` | no |
| `--pipelines_testdata_base_path` | Base URL or local path to location of pipeline test dataset files | `string` | `https://raw.githubusercontent.com/nf-core/test-datasets/rnavar/data/` | no |
| `--trace_report_suffix` | Suffix to add to the trace report filename. Default is the date and time in the format yyyy-MM-dd_HH-mm-ss. | `string` | n/a | no |
| `--help` | Display the help message. | `boolean` | n/a | no |
| `--help_full` | Display the full detailed help message. | `boolean` | n/a | no |
| `--show_hidden` | Display hidden parameters in the help message (only works when --help or --help_full are provided). | `boolean` | n/a | no |

## Workflows

| Name | Description | Entry |
|------|-------------|:-----:|
| `NFCORE_RNAVAR` | n/a | no |
| *(entry)* | n/a | yes |
| `RNAVAR` | Main workflow for RNA variant calling analysis. This workflow performs end-to-end RNA-seq variant calling including: - Quality control with FastQC - Read alignment with STAR - Duplicate marking with Picard - Split N CIGAR reads for RNA-seq data - Base quality score recalibration (BQSR) - Variant calling with GATK HaplotypeCaller - Variant filtering - Variant annotation with SnpEff and VEP - HLA typing with seq2HLA (optional) The workflow supports multiple input types including FASTQ, BAM, CRAM, and VCF files. | no |
| `BAM_STATS_SAMTOOLS` | Produces comprehensive statistics from SAM/BAM/CRAM file | no |
| `FASTQ_ALIGN_STAR` | Align reads to a reference genome using bowtie2 then sort with samtools | no |
| `VCF_ANNOTATE_SNPEFF` | Perform annotation with snpEff and bgzip + tabix index the resulting VCF file | no |
| `VCF_ANNOTATE_ENSEMBLVEP` | Perform annotation with ensemblvep and bgzip + tabix index the resulting VCF file | no |
| `BAM_MARKDUPLICATES_PICARD` | Picard MarkDuplicates, index BAM file and run samtools stats, flagstat and idxstats | no |
| `BAM_SORT_STATS_SAMTOOLS` | Sort SAM/BAM/CRAM file | no |
| `PREPARE_ALIGNMENT` | n/a | no |
| `SPLITNCIGAR` | Split reads that contain N CIGAR operations for RNA-seq variant calling. This subworkflow handles the GATK SplitNCigarReads step which is essential for RNA-seq variant calling. It splits reads that span introns (N in CIGAR) and reassigns mapping qualities to meet GATK requirements. The workflow processes BAM files in parallel across genomic intervals, then merges and indexes the results for efficient downstream processing. | no |
| `RECALIBRATE` | Apply base quality score recalibration (BQSR) to BAM files. This subworkflow applies the BQSR model generated by GATK BaseRecalibrator to adjust base quality scores in BAM files. Recalibrated quality scores improve the accuracy of variant calling by correcting systematic errors in the original quality scores assigned by the sequencing machine. Optionally generates alignment statistics using samtools stats for QC. | no |
| `DOWNLOAD_CACHE_SNPEFF_VEP` | n/a | no |
| `PIPELINE_INITIALISATION` | Initialize the nf-core/rnavar pipeline. Performs all setup tasks required before running the main workflow: - Display version information if requested - Validate parameters against the schema - Check Conda channel configuration - Parse and validate the input samplesheet - Generate parameter summary for logging | no |
| `PIPELINE_COMPLETION` | Handle pipeline completion tasks. Executes cleanup and notification tasks when the pipeline finishes: - Send completion email with run summary - Generate completion summary to stdout - Send notifications to messaging platforms (Slack, Teams, etc.) - Log error messages for failed runs | no |
| `ANNOTATION_CACHE_INITIALISATION` | n/a | no |
| `PREPARE_GENOME` | n/a | no |
| `VCF_ANNOTATE_ALL` | Annotate variants using multiple annotation tools. This subworkflow provides flexible variant annotation using one or more tools: - **SnpEff**: Functional annotation and effect prediction - **VEP (Ensembl Variant Effect Predictor)**: Comprehensive variant annotation - **BCFtools annotate**: Add custom annotations from external files - **Merge**: Combined SnpEff + VEP annotation The tools to use are specified via the `tools` parameter as a comma-separated list (e.g., "snpeff,vep" or "merge"). | no |

### `NFCORE_RNAVAR` Inputs

| Name | Description |
|------|-------------|
| `samplesheet` | n/a |
| `align` | n/a |

### `NFCORE_RNAVAR` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |
| `?` | n/a |

### `RNAVAR` Inputs

| Name | Description |
|------|-------------|
| `input` | n/a |
| `bcftools_annotations` | n/a |
| `bcftools_annotations_tbi` | n/a |
| `bcftools_columns` | n/a |
| `bcftools_header_lines` | n/a |
| `dbsnp` | n/a |
| `dbsnp_tbi` | n/a |
| `dict` | n/a |
| `exon_bed` | n/a |
| `fasta` | n/a |
| `fasta_fai` | n/a |
| `gtf` | n/a |
| `known_sites` | n/a |
| `known_sites_tbi` | n/a |
| `star_index` | n/a |
| `snpeff_cache` | n/a |
| `snpeff_db` | n/a |
| `vep_genome` | n/a |
| `vep_species` | n/a |
| `vep_cache_version` | n/a |
| `vep_include_fasta` | n/a |
| `vep_cache` | n/a |
| `vep_extra_files` | n/a |
| `seq_center` | n/a |
| `seq_platform` | n/a |
| `aligner` | n/a |
| `bam_csi_index` | n/a |
| `extract_umi` | n/a |
| `generate_gvcf` | n/a |
| `skip_multiqc` | n/a |
| `skip_baserecalibration` | n/a |
| `skip_intervallisttools` | n/a |
| `skip_variantannotation` | n/a |
| `skip_variantfiltration` | n/a |
| `star_ignore_sjdbgtf` | n/a |
| `tools` | n/a |

### `RNAVAR` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |
| `?` | n/a |

### `BAM_STATS_SAMTOOLS` Inputs

| Name | Description |
|------|-------------|
| `ch_bam_bai` | The input channel containing the BAM/CRAM and it's index Structure: [ val(meta), path(bam), path(bai) ] |
| `ch_fasta` | Reference genome fasta file Structure: [ path(fasta) ] |

### `BAM_STATS_SAMTOOLS` Outputs

| Name | Description |
|------|-------------|
| `stats` | File containing samtools stats output Structure: [ val(meta), path(stats) ] |
| `flagstat` | File containing samtools flagstat output Structure: [ val(meta), path(flagstat) ] |
| `idxstats` | File containing samtools idxstats output Structure: [ val(meta), path(idxstats)] |
| `versions` | Files containing software versions Structure: [ path(versions.yml) ] |

### `FASTQ_ALIGN_STAR` Inputs

| Name | Description |
|------|-------------|
| `ch_reads` | List of input FastQ files of size 1 and 2 for single-end and paired-end data, respectively. Structure: [ val(meta), [ path(reads) ] ] |
| `ch_index` | STAR genome index |
| `ch_gtf` | GTF file used to set the splice junctions with the --sjdbGTFfile flag |
| `val_star_ignore_sjdbgtf` | If true the --sjdbGTFfile flag is set |
| `val_seq_platform` | Sequencing platform to be added to the bam header using the --outSAMattrRGline flag |
| `val_seq_center` | Sequencing center to be added to the bam header using the --outSAMattrRGline flag |
| `ch_fasta` | Reference genome fasta file |
| `ch_transcripts_fasta` | Optional reference genome fasta file |

### `FASTQ_ALIGN_STAR` Outputs

| Name | Description |
|------|-------------|
| `orig_bam` | Output BAM file containing read alignments Structure: [ val(meta), path(bam) ] |
| `log_final` | STAR final log file Structure: [ val(meta), path(log_final) ] |
| `log_out` | STAR log out file Structure: [ val(meta), path(log_out) ] |
| `log_progress` | STAR log progress file Structure: [ val(meta), path(log_progress) ] |
| `bam_sorted` | Sorted BAM file of read alignments (optional) Structure: [ val(meta), path(bam) ] |
| `orig_bam_transcript` | Output BAM file of transcriptome alignment (optional) Structure: [ val(meta), path(bam) ] |
| `fastq` | Unmapped FastQ files (optional) Structure: [ val(meta), path(fastq) ] |
| `tab` | STAR output tab file(s) (optional) Structure: [ val(meta), path(tab) ] |
| `bam` | BAM file ordered by samtools Structure: [ val(meta), path(bam) ] |
| `bai` | BAI index of the ordered BAM file Structure: [ val(meta), path(bai) ] |
| `stats` | File containing samtools stats output Structure: [ val(meta), path(stats) ] |
| `flagstat` | File containing samtools flagstat output Structure: [ val(meta), path(flagstat) ] |
| `idxstats` | File containing samtools idxstats output Structure: [ val(meta), path(idxstats) ] |
| `bam_transcript` | Transcriptome-level BAM file ordered by samtools  (optional) Structure: [ val(meta), path(bam) ] |
| `bai_transcript` | Transcriptome-level BAI index of the ordered BAM file (optional) Structure: [ val(meta), path(bai) ] |
| `stats_transcript` | Transcriptome-level file containing samtools stats output (optional) Structure: [ val(meta), path(stats) ] |
| `flagstat_transcript` | Transcriptome-level file containing samtools flagstat output (optional) Structure: [ val(meta), path(flagstat) ] |
| `idxstats_transcript` | Transcriptome-level file containing samtools idxstats output (optional) Structure: [ val(meta), path(idxstats) ] |
| `versions` | File containing software versions |

### `VCF_ANNOTATE_SNPEFF` Inputs

| Name | Description |
|------|-------------|
| `ch_vcf` | vcf file Structure: [ val(meta), path(vcf) ] |
| `val_snpeff_db` | db version to use |
| `ch_snpeff_cache` | path to root cache folder for snpEff (optional) Structure: [ path(cache) ] |

### `VCF_ANNOTATE_SNPEFF` Outputs

| Name | Description |
|------|-------------|
| `vcf_tbi` | Compressed vcf file + tabix index Structure: [ val(meta), path(vcf), path(tbi) ] |
| `reports` | html reports Structure: [ path(html) ] |
| `summary` | html reports Structure: [ path(csv) ] |
| `genes_txt` | html reports Structure: [ path(txt) ] |
| `versions` | Files containing software versions Structure: [ path(versions.yml) ] |

### `VCF_ANNOTATE_ENSEMBLVEP` Inputs

| Name | Description |
|------|-------------|
| `ch_vcf` | vcf file to annotate Structure: [ val(meta), path(vcf), [path(custom_file1), path(custom_file2)... (optional)] ] |
| `ch_fasta` | Reference genome fasta file (optional) Structure: [ val(meta2), path(fasta) ] |
| `val_genome` | genome to use |
| `val_species` | species to use |
| `val_cache_version` | cache version to use |
| `ch_cache` | the root cache folder for ensemblvep (optional) Structure: [ val(meta3), path(cache) ] |
| `ch_extra_files` | any extra files needed by plugins for ensemblvep (optional) Structure: [ path(file1), path(file2)... ] |

### `VCF_ANNOTATE_ENSEMBLVEP` Outputs

| Name | Description |
|------|-------------|
| `vcf_tbi` | Compressed vcf file + tabix index Structure: [ val(meta), path(vcf), path(tbi) ] |
| `json` | json file Structure: [ val(meta), path(json) ] |
| `tab` | tab file Structure: [ val(meta), path(tab) ] |
| `reports` | html reports |
| `versions` | File containing software versions |

### `BAM_MARKDUPLICATES_PICARD` Inputs

| Name | Description |
|------|-------------|
| `ch_reads` | Sequence reads in BAM/CRAM/SAM format Structure: [ val(meta), path(reads) ] |
| `ch_fasta` | Reference genome fasta file required for CRAM input Structure: [ path(fasta) ] |
| `ch_fasta` | Index of the reference genome fasta file Structure: [ path(fai) ] |

### `BAM_MARKDUPLICATES_PICARD` Outputs

| Name | Description |
|------|-------------|
| `bam` | processed BAM/SAM file Structure: [ val(meta), path(bam) ] |
| `bai` | BAM/SAM samtools index Structure: [ val(meta), path(bai) ] |
| `cram` | processed CRAM file Structure: [ val(meta), path(cram) ] |
| `crai` | CRAM samtools index Structure: [ val(meta), path(crai) ] |
| `csi` | CSI samtools index Structure: [ val(meta), path(csi) ] |
| `stats` | File containing samtools stats output Structure: [ val(meta), path(stats) ] |
| `flagstat` | File containing samtools flagstat output Structure: [ val(meta), path(flagstat) ] |
| `idxstats` | File containing samtools idxstats output Structure: [ val(meta), path(idxstats) ] |
| `versions` | Files containing software versions Structure: [ path(versions.yml) ] |

### `BAM_SORT_STATS_SAMTOOLS` Inputs

| Name | Description |
|------|-------------|
| `meta` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `bam` | BAM/CRAM/SAM file |
| `fasta` | Reference genome fasta file |

### `BAM_SORT_STATS_SAMTOOLS` Outputs

| Name | Description |
|------|-------------|
| `meta` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `bam` | Sorted BAM/CRAM/SAM file |
| `bai` | BAM/CRAM/SAM index file |
| `crai` | BAM/CRAM/SAM index file |
| `stats` | File containing samtools stats output |
| `flagstat` | File containing samtools flagstat output |
| `idxstats` | File containing samtools idxstats output |
| `versions` | File containing software versions |

### `PREPARE_ALIGNMENT` Inputs

| Name | Description |
|------|-------------|
| `cram` | n/a |
| `bam` | n/a |

### `PREPARE_ALIGNMENT` Outputs

| Name | Description |
|------|-------------|
| `bam` | n/a |
| `versions` | n/a |

### `SPLITNCIGAR` Inputs

| Name | Description |
|------|-------------|
| `bam` | n/a |
| `fasta` | n/a |
| `fai` | n/a |
| `dict` | n/a |
| `intervals` | n/a |

### `SPLITNCIGAR` Outputs

| Name | Description |
|------|-------------|
| `bam_bai` | n/a |
| `versions` | n/a |

### `RECALIBRATE` Inputs

| Name | Description |
|------|-------------|
| `skip_samtools` | n/a |
| `bam` | n/a |
| `dict` | n/a |
| `fai` | n/a |
| `fasta` | n/a |

### `RECALIBRATE` Outputs

| Name | Description |
|------|-------------|
| `bam` | n/a |
| `qc` | n/a |
| `versions` | n/a |

### `DOWNLOAD_CACHE_SNPEFF_VEP` Inputs

| Name | Description |
|------|-------------|
| `ensemblvep_info` | n/a |
| `snpeff_info` | n/a |

### `DOWNLOAD_CACHE_SNPEFF_VEP` Outputs

| Name | Description |
|------|-------------|
| `ensemblvep_cache` | n/a |
| `snpeff_cache` | n/a |

### `PIPELINE_INITIALISATION` Inputs

| Name | Description |
|------|-------------|
| `version` | n/a |
| `validate_params` | n/a |
| `nextflow_cli_args` | n/a |
| `outdir` | n/a |
| `input` | n/a |
| `help` | n/a |
| `help_full` | n/a |
| `show_hidden` | n/a |

### `PIPELINE_INITIALISATION` Outputs

| Name | Description |
|------|-------------|
| `samplesheet` | n/a |
| `align` | n/a |
| `versions` | n/a |

### `PIPELINE_COMPLETION` Inputs

| Name | Description |
|------|-------------|
| `email` | n/a |
| `email_on_fail` | n/a |
| `plaintext_email` | n/a |
| `outdir` | n/a |
| `monochrome_logs` | n/a |
| `hook_url` | n/a |
| `multiqc_report` | n/a |

### `PIPELINE_COMPLETION` Outputs

| Name | Description |
|------|-------------|
| `<none>` | n/a |

### `ANNOTATION_CACHE_INITIALISATION` Inputs

| Name | Description |
|------|-------------|
| `snpeff_enabled` | n/a |
| `snpeff_cache` | n/a |
| `snpeff_db` | n/a |
| `vep_enabled` | n/a |
| `vep_cache` | n/a |
| `vep_species` | n/a |
| `vep_cache_version` | n/a |
| `vep_genome` | n/a |
| `vep_custom_args` | n/a |
| `help_message` | n/a |

### `ANNOTATION_CACHE_INITIALISATION` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |
| `?` | n/a |

### `PREPARE_GENOME` Inputs

| Name | Description |
|------|-------------|
| `bcftools_annotations` | n/a |
| `bcftools_annotations_tbi` | n/a |
| `dbsnp` | n/a |
| `dbsnp_tbi` | n/a |
| `dict` | n/a |
| `exon_bed` | n/a |
| `fasta` | n/a |
| `fasta_fai` | n/a |
| `gff` | n/a |
| `gtf` | n/a |
| `known_indels` | n/a |
| `known_indels_tbi` | n/a |
| `star_index` | n/a |
| `feature_type` | n/a |
| `skip_exon_bed_check` | n/a |
| `align` | n/a |

### `PREPARE_GENOME` Outputs

| Name | Description |
|------|-------------|
| `bcfann` | n/a |
| `bcfann_tbi` | n/a |
| `dbsnp` | n/a |
| `dbsnp_tbi` | n/a |
| `dict` | n/a |
| `exon_bed` | n/a |
| `fasta` | n/a |
| `fasta_fai` | n/a |
| `gtf` | n/a |
| `known_indels` | n/a |
| `known_indels_tbi` | n/a |
| `known_sites` | n/a |
| `known_sites_tbi` | n/a |
| `star_index` | n/a |
| `versions` | n/a |

### `VCF_ANNOTATE_ALL` Inputs

| Name | Description |
|------|-------------|
| `vcf` | n/a |
| `fasta` | n/a |
| `tools` | n/a |
| `snpeff_db` | n/a |
| `snpeff_cache` | n/a |
| `vep_genome` | n/a |
| `vep_species` | n/a |
| `vep_cache_version` | n/a |
| `vep_cache` | n/a |
| `vep_extra_files` | n/a |
| `bcftools_annotations` | n/a |
| `bcftools_annotations_index` | n/a |
| `bcftools_columns` | n/a |
| `bcftools_header_lines` | n/a |

### `VCF_ANNOTATE_ALL` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |

## Processes

| Name | Description |
|------|-------------|
| `MULTIQC` | Aggregate results from bioinformatics analyses across many samples into a single report |
| `UNTAR` | Extract files from tar, tar.gz, tar.bz2, tar.xz archives |
| `MOSDEPTH` | Calculates genome-wide sequencing coverage. |
| `SEQ2HLA` | Precision HLA typing and expression from RNA-seq data using seq2HLA |
| `FASTQC` | Run FastQC on sequenced reads |
| `GFFREAD` | Validate, filter, convert and perform various other operations on GFF files |
| `GUNZIP` | Compresses and decompresses files. |
| `GATK4_COMBINEGVCFS` | Combine per-sample gVCF files produced by HaplotypeCaller into a multi-sample gVCF file |
| `GATK4_INDEXFEATUREFILE` | Creates an index for a feature file, e.g. VCF or BED file. |
| `GATK4_VARIANTFILTRATION` | Filter variants |
| `GATK4_CREATESEQUENCEDICTIONARY` | Creates a sequence dictionary for a reference sequence |
| `GATK4_SPLITNCIGARREADS` | Splits reads that contain Ns in their cigar string |
| `GATK4_HAPLOTYPECALLER` | Call germline SNPs and indels via local re-assembly of haplotypes |
| `GATK4_INTERVALLISTTOOLS` | Splits the interval list file into unique, equally-sized interval files and place it under a directory |
| `GATK4_BASERECALIBRATOR` | Generate recalibration table for Base Quality Score Recalibration (BQSR) |
| `GATK4_APPLYBQSR` | Apply base quality score recalibration (BQSR) to a bam file |
| `GATK4_BEDTOINTERVALLIST` | Creates an interval list from a bed file and a reference dict |
| `GATK4_MERGEVCFS` | Merges several vcf files |
| `UMITOOLS_EXTRACT` | Extracts UMI barcode from a read and add it to the read name, leaving any sample barcode in place |
| `SAMTOOLS_SORT` | Sort SAM/BAM/CRAM file |
| `SAMTOOLS_MERGE` | Merge BAM or CRAM file |
| `SAMTOOLS_IDXSTATS` | Reports alignment summary statistics for a BAM/CRAM/SAM file |
| `SAMTOOLS_FAIDX` | Index FASTA file, and optionally generate a file of chromosome sizes |
| `SAMTOOLS_INDEX` | Index SAM/BAM/CRAM file |
| `SAMTOOLS_FLAGSTAT` | Counts the number of alignments in a BAM/CRAM/SAM file for each FLAG type |
| `SAMTOOLS_STATS` | Produces comprehensive statistics from SAM/BAM/CRAM file |
| `SAMTOOLS_CONVERT` | convert and then index CRAM -> BAM or BAM -> CRAM file |
| `BEDTOOLS_SORT` | Sorts a feature file by chromosome and other criteria. |
| `BEDTOOLS_MERGE` | combines overlapping or “book-ended” features in an interval file into a single feature which spans all of the combined features. |
| `STAR_GENOMEGENERATE` | Create index for STAR |
| `STAR_ALIGN` | Align reads to a reference genome using STAR |
| `STAR_INDEXVERSION` | Get the minimal allowed index version from STAR |
| `SNPEFF_SNPEFF` | Genetic variant annotation and functional effect prediction toolbox |
| `SNPEFF_DOWNLOAD` | Genetic variant annotation and functional effect prediction toolbox |
| `ENSEMBLVEP_VEP` | Ensembl Variant Effect Predictor (VEP). The output-file-format is controlled through `task.ext.args`. |
| `ENSEMBLVEP_DOWNLOAD` | Ensembl Variant Effect Predictor (VEP). The cache downloading options are controlled through `task.ext.args`. |
| `BCFTOOLS_ANNOTATE` | Add or remove annotations. |
| `PICARD_MARKDUPLICATES` | Locate and tag duplicate reads in a BAM file |
| `TABIX_TABIX` | create tabix index from a sorted bgzip tab-delimited genome file |
| `TABIX_BGZIPTABIX` | bgzip a sorted tab-delimited genome file and then create tabix index |
| `CAT_FASTQ` | Concatenates fastq files |
| `REMOVE_UNKNOWN_REGIONS` | n/a |
| `GTF2BED` | Convert GTF annotation file to BED format. Extracts genomic features (exons, transcripts, or genes) from a GTF file and outputs them in BED format for use with interval-based tools. The output BED file uses 0-based coordinates (BED standard) converted from the 1-based GTF coordinates. |

### `MULTIQC` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `report` | `-` | n/a | n/a |
| `data` | `-` | n/a | n/a |
| `plots` | `-` | n/a | n/a |

### `UNTAR` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `archive` | `file` | File to be untarred |

### `UNTAR` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `untar` | `map` | `*/` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |

### `MOSDEPTH` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `bam` | `file` | Input BAM/CRAM file |
| `bai` | `file` | Index for BAM/CRAM file |
| `bed` | `file` | BED file with intersected intervals |
| `meta2` | `map` | Groovy Map containing bed information e.g. [ id:'test' ] |
| `fasta` | `file` | Reference genome FASTA file |

### `MOSDEPTH` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `global_txt` | `file` | `*.{global.dist.txt}` | Text file with global cumulative coverage distribution |
| `summary_txt` | `file` | `*.{summary.txt}` | Text file with summary mean depths per chromosome and regions |
| `regions_txt` | `file` | `*.{region.dist.txt}` | Text file with region cumulative coverage distribution |
| `per_base_d4` | `file` | `*.{per-base.d4}` | D4 file with per-base coverage |
| `per_base_bed` | `file` | `*.{per-base.bed.gz}` | BED file with per-base coverage |
| `per_base_csi` | `file` | `*.{per-base.bed.gz.csi}` | Index file for BED file with per-base coverage |
| `regions_bed` | `file` | `*.{regions.bed.gz}` | BED file with per-region coverage |
| `regions_csi` | `file` | `*.{regions.bed.gz.csi}` | Index file for BED file with per-region coverage |
| `quantized_bed` | `file` | `*.{quantized.bed.gz}` | BED file with binned coverage |
| `quantized_csi` | `file` | `*.{quantized.bed.gz.csi}` | Index file for BED file with binned coverage |
| `thresholds_bed` | `file` | `*.{thresholds.bed.gz}` | BED file with the number of bases in each region that are covered at or above each threshold |
| `thresholds_csi` | `file` | `*.{thresholds.bed.gz.csi}` | Index file for BED file with threshold coverage |

### `SEQ2HLA` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. `[ id:'sample1', single_end:false ]` |
| `reads` | `file` | Paired-end FASTQ files for RNA-seq data |

### `SEQ2HLA` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `class1_genotype_2d` | `file` | `*ClassI-class.HLAgenotype2digits` | HLA Class I 2-digit genotype results |
| `class2_genotype_2d` | `file` | `*ClassII.HLAgenotype2digits` | HLA Class II 2-digit genotype results |
| `class1_genotype_4d` | `file` | `*ClassI-class.HLAgenotype4digits` | HLA Class I 4-digit genotype results |
| `class2_genotype_4d` | `file` | `*ClassII.HLAgenotype4digits` | HLA Class II 4-digit genotype results |
| `class1_bowtielog` | `file` | `*ClassI-class.bowtielog` | HLA Class I Bowtie alignment log |
| `class2_bowtielog` | `file` | `*ClassII.bowtielog` | HLA Class II Bowtie alignment log |
| `class1_expression` | `file` | `*ClassI-class.expression` | HLA Class I expression results |
| `class2_expression` | `file` | `*ClassII.expression` | HLA Class II expression results |
| `class1_nonclass_genotype_2d` | `file` | `*ClassI-nonclass.HLAgenotype2digits` | HLA Class I non-classical 2-digit genotype results |
| `ambiguity` | `file` | `*.ambiguity` | HLA typing ambiguity results |
| `class1_nonclass_genotype_4d` | `file` | `*ClassI-nonclass.HLAgenotype4digits` | HLA Class I non-classical 4-digit genotype results |
| `class1_nonclass_bowtielog` | `file` | `*ClassI-nonclass.bowtielog` | HLA Class I non-classical Bowtie alignment log |
| `class1_nonclass_expression` | `file` | `*ClassI-nonclass.expression` | HLA Class I non-classical expression results |

### `FASTQC` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `reads` | `file` | List of input FastQ files of size 1 and 2 for single-end and paired-end data, respectively. |

### `FASTQC` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `html` | `file` | `*_{fastqc.html}` | FastQC report |
| `zip` | `file` | `*_{fastqc.zip}` | FastQC report archive |

### `GFFREAD` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing meta data e.g. [ id:'test' ] |
| `gff` | `file` | A reference file in either the GFF3, GFF2 or GTF format. |

### `GFFREAD` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `gtf` | `file` | `*.{gtf}` | GTF file resulting from the conversion of the GFF input file if '-T' argument is present |
| `gffread_gff` | `file` | `*.gff3` | GFF3 file resulting from the conversion of the GFF input file if '-T' argument is absent |
| `gffread_fasta` | `file` | `*.fasta` | Fasta file produced when either of '-w', '-x', '-y' parameters is present |

### `GUNZIP` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Optional groovy Map containing meta information e.g. [ id:'test', single_end:false ] |
| `archive` | `file` | File to be compressed/uncompressed |

### `GUNZIP` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `gunzip` | `file` | `*.*` | Compressed/uncompressed file |

### `GATK4_COMBINEGVCFS` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test' ] |
| `vcf` | `file` | Compressed VCF files |
| `vcf_idx` | `file` | VCF Index file |

### `GATK4_COMBINEGVCFS` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `combined_gvcf` | `file` | `*.combined.g.vcf.gz` | Compressed Combined GVCF file |

### `GATK4_INDEXFEATUREFILE` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `feature_file` | `file` | VCF/BED file |

### `GATK4_INDEXFEATUREFILE` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `index` | `file` | `*.{tbi,idx}` | Index for VCF/BED file |

### `GATK4_VARIANTFILTRATION` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test'] |
| `vcf` | `list` | List of VCF(.gz) files |
| `tbi` | `list` | List of VCF file indexes |
| `meta2` | `map` | Groovy Map containing reference information e.g. [ id:'genome' ] |
| `fasta` | `file` | Fasta file of reference genome |
| `meta3` | `map` | Groovy Map containing reference information e.g. [ id:'genome' ] |
| `fai` | `file` | Index of fasta file |
| `meta4` | `map` | Groovy Map containing reference information e.g. [ id:'genome' ] |
| `dict` | `file` | Sequence dictionary of fastea file |
| `meta5` | `map` | Groovy Map containing reference information e.g. [ id:'genome' ] |
| `gzi` | `file` | Genome index file only needed when the genome file was compressed with the BGZF algorithm. |

### `GATK4_VARIANTFILTRATION` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `vcf` | `file` | `*.vcf.gz` | Compressed VCF file |
| `tbi` | `file` | `*.vcf.gz.tbi` | Index of VCF file |

### `GATK4_CREATESEQUENCEDICTIONARY` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing reference information e.g. [ id:'genome' ] |
| `fasta` | `file` | Input fasta file |

### `GATK4_CREATESEQUENCEDICTIONARY` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `dict` | `file` | `*.{dict}` | gatk dictionary file |

### `GATK4_SPLITNCIGARREADS` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test'] |
| `bam` | `list` | BAM/SAM/CRAM file containing reads |
| `bai` | `list` | BAI/SAI/CRAI index file (optional) |
| `intervals` | `file` | Bed file with the genomic regions included in the library (optional) |
| `meta2` | `map` | Groovy Map containing reference information e.g. [ id:'reference' ] |
| `fasta` | `file` | The reference fasta file |
| `meta3` | `map` | Groovy Map containing reference information e.g. [ id:'reference' ] |
| `fai` | `file` | Index of reference fasta file |
| `meta4` | `map` | Groovy Map containing reference information e.g. [ id:'reference' ] |
| `dict` | `file` | GATK sequence dictionary |

### `GATK4_SPLITNCIGARREADS` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `bam` | `file` | `*.{bam,sam,cram}` | Output file with split reads (BAM/SAM/CRAM) |

### `GATK4_HAPLOTYPECALLER` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `input` | `file` | BAM/CRAM file from alignment |
| `input_index` | `file` | BAI/CRAI file from alignment |
| `intervals` | `file` | Bed file with the genomic regions included in the library (optional) |
| `dragstr_model` | `file` | Text file containing the DragSTR model of the used BAM/CRAM file (optional) |
| `meta2` | `map` | Groovy Map containing reference information e.g. [ id:'test_reference' ] |
| `fasta` | `file` | The reference fasta file |
| `meta3` | `map` | Groovy Map containing reference information e.g. [ id:'test_reference' ] |
| `fai` | `file` | Index of reference fasta file |
| `meta4` | `map` | Groovy Map containing reference information e.g. [ id:'test_reference' ] |
| `dict` | `file` | GATK sequence dictionary |
| `meta5` | `map` | Groovy Map containing dbsnp information e.g. [ id:'test_dbsnp' ] |
| `dbsnp` | `file` | VCF file containing known sites (optional) |
| `meta6` | `map` | Groovy Map containing dbsnp information e.g. [ id:'test_dbsnp' ] |
| `dbsnp_tbi` | `file` | VCF index of dbsnp (optional) |

### `GATK4_HAPLOTYPECALLER` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `vcf` | `file` | `*.vcf.gz` | Compressed VCF file |
| `tbi` | `file` | `*.vcf.gz.tbi` | Index of VCF file |
| `bam` | `file` | `*.realigned.bam` | Assembled haplotypes and locally realigned reads |

### `GATK4_INTERVALLISTTOOLS` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `intervals` | `file` | Interval file |

### `GATK4_INTERVALLISTTOOLS` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `interval_list` | `file` | `*.interval_list` | Interval list files |

### `GATK4_BASERECALIBRATOR` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `input` | `file` | BAM/CRAM file from alignment |
| `input_index` | `file` | BAI/CRAI file from alignment |
| `intervals` | `file` | Bed file with the genomic regions included in the library (optional) |
| `meta2` | `map` | Groovy Map containing reference information e.g. [ id:'genome'] |
| `fasta` | `file` | The reference fasta file |
| `meta3` | `map` | Groovy Map containing reference information e.g. [ id:'genome'] |
| `fai` | `file` | Index of reference fasta file |
| `meta4` | `map` | Groovy Map containing reference information e.g. [ id:'genome'] |
| `dict` | `file` | GATK sequence dictionary |
| `meta5` | `map` | Groovy Map containing reference information e.g. [ id:'genome'] |
| `known_sites` | `file` | VCF files with known sites for indels / snps |
| `meta6` | `map` | Groovy Map containing reference information e.g. [ id:'genome'] |
| `known_sites_tbi` | `file` | Tabix index of the known_sites |

### `GATK4_BASERECALIBRATOR` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `table` | `file` | `*.{table}` | Recalibration table from BaseRecalibrator |

### `GATK4_APPLYBQSR` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `input` | `file` | BAM/CRAM file from alignment |
| `input_index` | `file` | BAI/CRAI file from alignment |
| `bqsr_table` | `file` | Recalibration table from gatk4_baserecalibrator |
| `intervals` | `file` | Bed file with the genomic regions included in the library (optional) |

### `GATK4_APPLYBQSR` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `bam` | `file` | `${prefix}.bam` | Recalibrated BAM file |
| `bai` | `file` | `${prefix}*bai` | Recalibrated BAM index file |
| `cram` | `file` | `${prefix}.cram` | Recalibrated CRAM file |

### `GATK4_BEDTOINTERVALLIST` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test'] |
| `bed` | `file` | Input bed file |
| `meta2` | `map` | Groovy Map containing reference information e.g. [ id:'genome' ] |
| `dict` | `file` | Sequence dictionary |

### `GATK4_BEDTOINTERVALLIST` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `interval_list` | `file` | `*.interval_list` | gatk interval list file |

### `GATK4_MERGEVCFS` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test'] |
| `vcf` | `list` | Two or more VCF files |
| `meta2` | `map` | Groovy Map containing reference information e.g. [ id:'genome'] |
| `dict` | `file` | Optional Sequence Dictionary as input |

### `GATK4_MERGEVCFS` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `vcf` | `file` | `*.vcf.gz` | merged vcf file |
| `tbi` | `file` | `*.tbi` | index files for the merged vcf files |

### `UMITOOLS_EXTRACT` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `reads` | `list` | List of input FASTQ files whose UMIs will be extracted. |

### `UMITOOLS_EXTRACT` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `reads` | `file` | `*.{fastq.gz}` | Extracted FASTQ files. \| For single-end reads, pattern is \${prefix}.umi_extract.fastq.gz. \| For paired-end reads, pattern is \${prefix}.umi_extract_{1,2}.fastq.gz. |
| `log` | `file` | `*.{log}` | Logfile for umi_tools |

### `SAMTOOLS_SORT` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `bam` | `file` | BAM/CRAM/SAM file(s) |
| `meta2` | `map` | Groovy Map containing reference information e.g. [ id:'genome' ] |
| `fasta` | `file` | Reference genome FASTA file |

### `SAMTOOLS_SORT` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `bam` | `file` | `*.{bam}` | Sorted BAM file |
| `cram` | `file` | `*.{cram}` | Sorted CRAM file |
| `sam` | `file` | `*.{sam}` | Sorted SAM file |
| `crai` | `file` | `*.crai` | CRAM index file (optional) |
| `csi` | `file` | `*.csi` | BAM index file (optional) |
| `bai` | `file` | `*.bai` | BAM index file (optional) |

### `SAMTOOLS_MERGE` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `input_files` | `file` | BAM/CRAM file |
| `meta2` | `map` | Groovy Map containing reference information e.g. [ id:'genome' ] |
| `fasta` | `file` | Reference file the CRAM was created with (optional) |
| `meta3` | `map` | Groovy Map containing reference information e.g. [ id:'genome' ] |
| `fai` | `file` | Index of the reference file the CRAM was created with (optional) |
| `meta4` | `map` | Groovy Map containing reference information e.g. [ id:'genome' ] |
| `gzi` | `file` | Index of the compressed reference file the CRAM was created with (optional) |

### `SAMTOOLS_MERGE` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `bam` | `file` | `*.{bam}` | BAM file |
| `cram` | `file` | `*.{cram}` | CRAM file |
| `csi` | `file` | `*.csi` | BAM index file (optional) |
| `crai` | `file` | `*.crai` | CRAM index file (optional) |

### `SAMTOOLS_IDXSTATS` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `bam` | `file` | BAM/CRAM/SAM file |
| `bai` | `file` | Index for BAM/CRAM/SAM file |

### `SAMTOOLS_IDXSTATS` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `idxstats` | `file` | `*.{idxstats}` | File containing samtools idxstats output |

### `SAMTOOLS_FAIDX` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing reference information e.g. [ id:'test' ] |
| `fasta` | `file` | FASTA file |
| `meta2` | `map` | Groovy Map containing reference information e.g. [ id:'test' ] |
| `fai` | `file` | FASTA index file |

### `SAMTOOLS_FAIDX` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `fa` | `file` | `*.{fa}` | FASTA file |
| `sizes` | `file` | `*.{sizes}` | File containing chromosome lengths |
| `fai` | `file` | `*.{fai}` | FASTA index file |
| `gzi` | `file` | `*.gzi` | Optional gzip index file for compressed inputs |

### `SAMTOOLS_INDEX` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `input` | `file` | input file |

### `SAMTOOLS_INDEX` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `bai` | `file` | `*.{bai,crai,sai}` | BAM/CRAM/SAM index file |
| `csi` | `file` | `*.{csi}` | CSI index file |
| `crai` | `file` | `*.{bai,crai,sai}` | BAM/CRAM/SAM index file |

### `SAMTOOLS_FLAGSTAT` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `bam` | `file` | BAM/CRAM/SAM file |
| `bai` | `file` | Index for BAM/CRAM/SAM file |

### `SAMTOOLS_FLAGSTAT` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `flagstat` | `file` | `*.{flagstat}` | File containing samtools flagstat output |

### `SAMTOOLS_STATS` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `input` | `file` | BAM/CRAM file from alignment |
| `input_index` | `file` | BAI/CRAI file from alignment |
| `meta2` | `map` | Groovy Map containing reference information e.g. [ id:'genome' ] |
| `fasta` | `file` | Reference file the CRAM was created with (optional) |

### `SAMTOOLS_STATS` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `stats` | `file` | `*.{stats}` | File containing samtools stats output |

### `SAMTOOLS_CONVERT` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `input` | `file` | BAM/CRAM file |
| `index` | `file` | BAM/CRAM index file |
| `meta2` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `fasta` | `file` | Reference file to create the CRAM file |
| `meta3` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `fai` | `file` | Reference index file to create the CRAM file |

### `SAMTOOLS_CONVERT` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `bam` | `file` | `*{.bam}` | filtered/converted BAM file |
| `cram` | `file` | `*{cram}` | filtered/converted CRAM file |
| `bai` | `file` | `*{.bai}` | filtered/converted BAM index |
| `crai` | `file` | `*{.crai}` | filtered/converted CRAM index |

### `BEDTOOLS_SORT` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `intervals` | `file` | BED/BEDGRAPH |

### `BEDTOOLS_SORT` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `sorted` | `file` | `*.${extension}` | Sorted output file |

### `BEDTOOLS_MERGE` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `bed` | `file` | Input BED file |

### `BEDTOOLS_MERGE` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `bed` | `file` | `*.{bed}` | Overlapped bed file with combined features |

### `STAR_GENOMEGENERATE` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `fasta` | `file` | Fasta file of the reference genome |
| `meta2` | `map` | Groovy Map containing reference information e.g. [ id:'test' ] |
| `gtf` | `file` | GTF file of the reference genome |

### `STAR_GENOMEGENERATE` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `index` | `directory` | `star` | Folder containing the star index files |

### `STAR_ALIGN` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `reads` | `file` | List of input FastQ files of size 1 and 2 for single-end and paired-end data, respectively. |
| `meta2` | `map` | Groovy Map containing reference information e.g. [ id:'test' ] |
| `index` | `directory` | STAR genome index |
| `meta3` | `map` | Groovy Map containing reference information e.g. [ id:'test' ] |
| `gtf` | `file` | Annotation GTF file |

### `STAR_ALIGN` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `log_final` | `file` | `*Log.final.out` | STAR final log file |
| `log_out` | `file` | `*Log.out` | STAR lot out file |
| `log_progress` | `file` | `*Log.progress.out` | STAR log progress file |
| `bam` | `file` | `*.{bam}` | Output BAM file containing read alignments |
| `bam_sorted` | `file` | `*sortedByCoord.out.bam` | Sorted BAM file of read alignments (optional) |
| `bam_sorted_aligned` | `file` | `*.Aligned.sortedByCoord.out.bam` | Sorted BAM file of read alignments (optional) |
| `bam_transcript` | `file` | `*toTranscriptome.out.bam` | Output BAM file of transcriptome alignment (optional) |
| `bam_unsorted` | `file` | `*Aligned.unsort.out.bam` | Unsorted BAM file of read alignments (optional) |
| `fastq` | `file` | `*fastq.gz` | Unmapped FastQ files (optional) |
| `tab` | `file` | `*.tab` | STAR output tab file(s) (optional) |
| `spl_junc_tab` | `file` | `*.SJ.out.tab` | STAR output splice junction tab file |
| `read_per_gene_tab` | `file` | `*.ReadsPerGene.out.tab` | STAR output read per gene tab file |
| `junction` | `file` | `*.out.junction` | STAR chimeric junction output file (optional) |
| `sam` | `file` | `*.out.sam` | STAR output SAM file(s) (optional) |
| `wig` | `file` | `*.wig` | STAR output wiggle format file(s) (optional) |
| `bedgraph` | `file` | `*.bg` | STAR output bedGraph format file(s) (optional) |

### `STAR_INDEXVERSION` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `index_version` | `-` | n/a | n/a |

### `SNPEFF_SNPEFF` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `vcf` | `file` | vcf to annotate |
| `meta2` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `cache` | `file` | path to snpEff cache (optional) |

### `SNPEFF_SNPEFF` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `vcf` | `file` | `*.ann.vcf` | annotated vcf |
| `report` | `string` | `*.csv` | The process The tool name snpEff report csv file |
| `summary_html` | `string` | `*.html` | The process The tool name snpEff summary statistics in html file |
| `genes_txt` | `string` | `*.genes.txt` | The process The tool name txt (tab separated) file having counts of the number of variants affecting each transcript and gene |

### `SNPEFF_DOWNLOAD` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `snpeff_db` | `string` | SnpEff database name |

### `SNPEFF_DOWNLOAD` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `cache` | `file` | n/a | snpEff cache |

### `ENSEMBLVEP_VEP` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `vcf` | `file` | vcf to annotate |
| `custom_extra_files` | `file` | extra sample-specific files to be used with the `--custom` flag to be configured with ext.args (optional) |
| `meta2` | `map` | Groovy Map containing fasta reference information e.g. [ id:'test' ] |
| `fasta` | `file` | reference FASTA file (optional) |

### `ENSEMBLVEP_VEP` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `vcf` | `file` | `*.vcf.gz` | annotated vcf (optional) |
| `tbi` | `file` | `*.vcf.gz.tbi` | annotated vcf index (optional) |
| `tab` | `file` | `*.ann.tab.gz` | tab file with annotated variants (optional) |
| `json` | `file` | `*.ann.json.gz` | json file with annotated variants (optional) |
| `report` | `string` | `*.html` | The process The tool name VEP report file |

### `ENSEMBLVEP_DOWNLOAD` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `assembly` | `string` | Genome assembly |
| `species` | `string` | Specie |
| `cache_version` | `string` | cache version |

### `ENSEMBLVEP_DOWNLOAD` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `cache` | `file` | `*` | cache |

### `BCFTOOLS_ANNOTATE` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `input` | `file` | Query VCF or BCF file, can be either uncompressed or compressed |
| `index` | `file` | Index of the query VCF or BCF file |
| `annotations` | `file` | Bgzip-compressed file with annotations |
| `annotations_index` | `file` | Index of the annotations file |

### `BCFTOOLS_ANNOTATE` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `vcf` | `file` | `*{vcf,vcf.gz,bcf,bcf.gz}` | Compressed annotated VCF file |
| `tbi` | `file` | `*.tbi` | Alternative VCF file index |
| `csi` | `file` | `*.csi` | Default VCF file index |

### `PICARD_MARKDUPLICATES` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `reads` | `file` | Sequence reads file, can be SAM/BAM/CRAM format |
| `meta2` | `map` | Groovy Map containing reference information e.g. [ id:'genome' ] |
| `fasta` | `file` | Reference genome fasta file, required for CRAM input |
| `meta3` | `map` | Groovy Map containing reference information e.g. [ id:'genome' ] |
| `fai` | `file` | Reference genome fasta index |

### `PICARD_MARKDUPLICATES` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `bam` | `file` | `*.{bam}` | BAM file with duplicate reads marked/removed |
| `bai` | `file` | `*.{bai}` | An optional BAM index file. If desired, --CREATE_INDEX must be passed as a flag |
| `cram` | `file` | `*.{cram}` | Output CRAM file |
| `metrics` | `file` | `*.{metrics.txt}` | Duplicate metrics file generated by picard |

### `TABIX_TABIX` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `tab` | `file` | TAB-delimited genome position file compressed with bgzip |

### `TABIX_TABIX` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `index` | `file` | `*.{tbi,csi}` | Tabix index file (either tbi or csi) |

### `TABIX_BGZIPTABIX` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `input` | `file` | Sorted tab-delimited genome file |

### `TABIX_BGZIPTABIX` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `gz_index` | `file` | `*.gz, *.{tbi,csi}` | bgzipped tab-delimited genome file Tabix index file (either tbi or csi) |

### `CAT_FASTQ` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `reads` | `file` | List of input FastQ files to be concatenated. |

### `CAT_FASTQ` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `reads` | `file` | `*.{merged.fastq.gz}` | Merged fastq file |

### `REMOVE_UNKNOWN_REGIONS` Inputs

| Name | Type | Description |
|------|------|-------------|
| `val(meta), path(bed)` | `tuple` | n/a |
| `val(meta2), path(dict)` | `tuple` | n/a |

### `REMOVE_UNKNOWN_REGIONS` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path('*.bed')` | `tuple` | `bed` | n/a |

### `GTF2BED` Inputs

| Name | Type | Description |
|------|------|-------------|
| `val(meta), path(gtf)` | `tuple` | n/a |

### `GTF2BED` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path('*.bed')` | `tuple` | `bed` | n/a |

## Functions

| Name | Parameters | Returns | Description |
|------|------------|---------|-------------|
| `paramsSummaryMultiqc` | `summary_params` | n/a | n/a |
| `validateInputParameters` | n/a | n/a | Validate pipeline input parameters. Checks that all required parameters are provided and valid. Currently validates that the specified genome exists in the config. |
| `validateInputSamplesheet` | `input` | n/a | Validate and parse input samplesheet entries. Ensures that multiple runs of the same sample have consistent sequencing type (all single-end or all paired-end). |
| `checkSamplesAfterGrouping` | `input` | n/a | Validate samples after grouping by sample ID. Performs consistency checks on grouped sample data: - Ensures only one BAM/CRAM file per sample - Prevents mixing of FASTQ and BAM/CRAM inputs - Validates consistent single-end/paired-end status - Properly interleaves paired-end FASTQ files |
| `genomeExistsError` | n/a | n/a | Check if the specified genome exists in the configuration. Throws an error with a helpful message listing available genomes if the specified genome key is not found in the config. |
| `toolCitationText` | n/a | n/a | n/a |
| `toolBibliographyText` | n/a | n/a | n/a |
| `methodsDescriptionText` | `mqc_methods_yaml` | n/a | n/a |
| `isCloudUrl` | `cache_url` | n/a | n/a |
| `isCompatibleStarIndex` | `index_version`, `minimal_index_version` | n/a | n/a |
| `convertVersionToList` | `version` | n/a | n/a |

---

*This pipeline was built with [Nextflow](https://nextflow.io).
Documentation generated by [nf-docs](https://github.com/ewels/nf-docs) v0.2.0 on 2026-03-03 22:40:54 UTC.*

<!-- END_NF_DOCS -->
