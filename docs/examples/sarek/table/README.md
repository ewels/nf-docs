<!-- BEGIN_NF_DOCS -->
# nf-core/sarek

**Version:** 3.7.1 · An open-source analysis pipeline to detect germline or somatic variants from whole genome or targeted sequencing

## Inputs

### Input/output options

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| `--input` | Path to comma-separated file containing information about the samples in the experiment. | `string` | n/a | no |
| `--input_restart` | Automatic retrieval for restart | `string` | n/a | no |
| `--step` | Starting step | `string` | `mapping` | yes |
| `--outdir` | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. | `string` | n/a | yes |

### Main options

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| `--split_fastq` | Specify how many reads each split of a FastQ file contains. Set 0 to turn off splitting at all. | `integer` | `50000000` | no |
| `--nucleotides_per_second` | Estimate interval size. | `integer` | `200000` | no |
| `--intervals` | Path to target bed file in case of whole exome or targeted sequencing or intervals file. | `string` | n/a | no |
| `--no_intervals` | Disable usage of intervals. | `boolean` | n/a | no |
| `--wes` | Enable when exome or panel data is provided. | `boolean` | n/a | no |
| `--tools` | Tools to use for contamination removal, duplicate marking, variant calling and/or for annotation. | `string` | n/a | no |
| `--skip_tools` | Disable specified tools. | `string` | n/a | no |

### FASTQ Preprocessing

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| `--trim_fastq` | Run FastP for read trimming | `boolean` | n/a | no |
| `--clip_r1` | Remove bp from the 5' end of read 1 | `integer` | `0` | no |
| `--clip_r2` | Remove bp from the 5' end of read 2 | `integer` | `0` | no |
| `--three_prime_clip_r1` | Remove bp from the 3' end of read 1 | `integer` | `0` | no |
| `--three_prime_clip_r2` | Remove bp from the 3' end of read 2 | `integer` | `0` | no |
| `--trim_nextseq` | Removing poly-G tails. | `boolean` | n/a | no |
| `--length_required` | Minimum length of reads to keep | `integer` | `15` | no |
| `--save_trimmed` | Save trimmed FastQ file intermediates. | `boolean` | n/a | no |
| `--save_split_fastqs` | If set, publishes split FASTQ files. Intended for testing purposes. | `boolean` | n/a | no |

### Unique Molecular Identifiers

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| `--umi_read_structure` | Specify UMI read structure for fgbio UMI consensus read generation | `string` | n/a | no |
| `--group_by_umi_strategy` | Default strategy for fgbio UMI-based consensus read generation | `string` | `Adjacency` | no |
| `--umi_in_read_header` | Move UMIs from fastq read headers to a tag prior to deduplication. | `boolean` | n/a | no |
| `--umi_location` | Location of the UMI(s) to be extracted with fastp. | `string` | n/a | no |
| `--umi_length` | Length of the UMI(s) in the read. | `integer` | n/a | no |
| `--umi_base_skip` | Number of bases to skip after the UMI(s) in the read when extracting with fastp. | `integer` | n/a | no |
| `--umi_tag` | Tag detailing where UMIs are present inside the bam/cram file (e.g. RX). | `string` | n/a | no |
| `--bbsplit_fasta_list` | Path to comma-separated file containing a list of reference genomes to filter reads against with BBSplit. You have to also explicitly set `--tools bbsplit` if you want to use BBSplit. | `string` | n/a | no |
| `--bbsplit_index` | Path to directory or tar.gz archive for pre-built BBSplit index. | `string` | n/a | no |
| `--save_bbsplit_reads` | If this option is specified, FastQ files split by reference will be saved in the results directory. | `boolean` | n/a | no |

### Preprocessing

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| `--aligner` | Specify aligner to be used to map reads to reference genome. | `string` | `bwa-mem` | no |
| `--save_mapped` | Save mapped files. | `boolean` | n/a | no |
| `--save_output_as_bam` | Saves output from mapping (if `--save_mapped`), Markduplicates & Baserecalibration as BAM file instead of CRAM | `boolean` | n/a | no |
| `--use_gatk_spark` | Enable usage of GATK Spark implementation for duplicate marking and/or base quality score recalibration | `string` | n/a | no |
| `--markduplicates_pixel_distance` | n/a | `integer` | n/a | no |
| `--sentieon_consensus` | Generate consensus reads with Sentieon dedup rather than choosing one best read. | `boolean` | n/a | no |

### Variant Calling

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| `--only_paired_variant_calling` | If true, skips germline variant calling for matched normal to tumor sample. Normal samples without matched tumor will still be processed through germline variant calling tools. | `boolean` | n/a | no |
| `--ascat_min_base_qual` | Overwrite Ascat min base quality required for a read to be counted. | `integer` | `20` | no |
| `--ascat_min_counts` | Overwrite Ascat minimum depth required in the normal for a SNP to be considered. | `integer` | `10` | no |
| `--ascat_min_map_qual` | Overwrite Ascat min mapping quality required for a read to be counted. | `integer` | `35` | no |
| `--ascat_ploidy` | Overwrite ASCAT ploidy. | `number` | n/a | no |
| `--ascat_purity` | Overwrite ASCAT purity. | `number` | n/a | no |
| `--cf_chrom_len` | Specify a custom chromosome length file. | `string` | n/a | no |
| `--cf_coeff` | Overwrite Control-FREEC coefficientOfVariation | `number` | `0.05` | no |
| `--cf_contamination_adjustment` | Overwrite Control-FREEC contaminationAdjustement | `boolean` | n/a | no |
| `--cf_contamination` | Design known contamination value for Control-FREEC | `integer` | `0` | no |
| `--cf_minqual` | Minimal sequencing quality for a position to be considered in BAF analysis. | `integer` | `0` | no |
| `--cf_mincov` | Minimal read coverage for a position to be considered in BAF analysis. | `integer` | `0` | no |
| `--cf_ploidy` | Genome ploidy used by ControlFREEC | `string` | `2` | no |
| `--cf_window` | Overwrite Control-FREEC window size. | `number` | n/a | no |
| `--cnvkit_reference` | Copy-number reference for CNVkit | `string` | n/a | no |
| `--freebayes_filter` | Filtering expression for vcflib/vcffilter | `string` | `30` | no |
| `--joint_germline` | Turn on the joint germline variant calling for GATK haplotypecaller | `boolean` | n/a | no |
| `--joint_mutect2` | Runs Mutect2 in joint (multi-sample) mode for better concordance among variant calls of tumor samples from the same patient. Mutect2 outputs will be stored in a subfolder named with patient ID under `variant_calling/mutect2/` folder. Only a single normal sample per patient is allowed. Tumor-only mode is also supported. | `boolean` | n/a | no |
| `--ignore_soft_clipped_bases` | Do not analyze soft clipped bases in the reads for GATK Mutect2. | `boolean` | n/a | no |
| `--pon` | Panel-of-normals VCF (bgzipped) for GATK Mutect2 | `string` | n/a | no |
| `--pon_tbi` | Index of PON panel-of-normals VCF. | `string` | n/a | no |
| `--sentieon_haplotyper_emit_mode` | Option for selecting output and emit-mode of Sentieon's Haplotyper. | `string` | `variant` | no |
| `--sentieon_dnascope_emit_mode` | Option for selecting output and emit-mode of Sentieon's Dnascope. | `string` | `variant` | no |
| `--sentieon_dnascope_pcr_indel_model` | Option for selecting the PCR indel model used by Sentieon Dnascope. | `string` | `CONSERVATIVE` | no |
| `--gatk_pcr_indel_model` | n/a | `string` | `CONSERVATIVE` | no |

### Post variant calling

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| `--filter_vcfs` | Enable filtering of VCFs with bcftools view | `boolean` | n/a | no |
| `--bcftools_filter_criteria` | Filter criteria. Uses bcftools view filter options. To customize, follow instructions here: https://samtools.github.io/bcftools/bcftools.html#view | `string` | `-f PASS,.` | no |
| `--normalize_vcfs` | Option for normalization of vcf-files. | `boolean` | n/a | no |
| `--snv_consensus_calling` | Enable consensus calling of multiple VCF files from one sample | `boolean` | n/a | no |
| `--consensus_min_count` | Minimum number of variant callers calling a variant for consensus results | `integer` | `2` | no |
| `--concatenate_vcfs` | Option for concatenating germline vcf-files. | `boolean` | n/a | no |
| `--varlociraptor_chunk_size` | Number of chunks to split the vcf-files for varlociraptor. Minimum 1, indicates no splitting | `integer` | `15` | no |
| `--varlociraptor_scenario_tumor_only` | Yte compatible scenario file for tumor only samples. Defaults to assets/varlociraptor_tumor_only.yte.yaml | `string` | n/a | no |
| `--varlociraptor_scenario_somatic` | Yte compatible scenario file for somatic samples. Defaults to assets/varlociraptor_somatic.yte.yaml | `string` | n/a | no |
| `--varlociraptor_scenario_germline` | Yte compatible scenario file for germline samples. Defaults to assets/varlociraptor_germline.yte.yaml | `string` | n/a | no |

### Annotation

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
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
| `--vep_version` | Should reflect the VEP version used in the container. | `string` | `111.0-0` | no |
| `--outdir_cache` | The output directory where the cache will be saved. You have to use absolute paths to storage on Cloud infrastructure. | `string` | n/a | no |
| `--vep_out_format` | VEP output-file format. | `string` | `vcf` | no |
| `--bcftools_annotations` | A vcf file containing custom annotations to be used with bcftools annotate. Needs to be bgzipped. | `string` | n/a | no |
| `--bcftools_annotations_tbi` | Index file for `bcftools_annotations` | `string` | n/a | no |
| `--bcftools_columns` | Optional text file with list of columns to use from `bcftools_annotations`, one name per row | `string` | n/a | no |
| `--bcftools_header_lines` | Text file with the header lines of `bcftools_annotations` | `string` | n/a | no |

### General reference genome options

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| `--igenomes_base` | The base path to the igenomes reference files | `string` | `s3://ngi-igenomes/igenomes/` | no |
| `--igenomes_ignore` | Do not load the iGenomes reference config. | `boolean` | n/a | no |
| `--save_reference` | Save built references. | `boolean` | n/a | no |
| `--build_only_index` | Only built references. | `boolean` | n/a | no |
| `--download_cache` | Download annotation cache. | `boolean` | n/a | no |

### Reference genome options

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| `--genome` | Name of iGenomes reference. | `string` | `GATK.GRCh38` | no |
| `--ascat_genome` | ASCAT genome. | `string` | n/a | no |
| `--ascat_alleles` | Path to ASCAT allele zip file. | `string` | n/a | no |
| `--ascat_loci` | Path to ASCAT loci zip file. | `string` | n/a | no |
| `--ascat_loci_gc` | Path to ASCAT GC content correction file. | `string` | n/a | no |
| `--ascat_loci_rt` | Path to ASCAT RT (replictiming) correction file. | `string` | n/a | no |
| `--bwa` | Path to BWA mem indices. | `string` | n/a | no |
| `--bwamem2` | Path to bwa-mem2 mem indices. | `string` | n/a | no |
| `--chr_dir` | Path to chromosomes folder used with ControLFREEC. | `string` | n/a | no |
| `--dbsnp` | Path to dbsnp file. | `string` | n/a | no |
| `--dbsnp_tbi` | Path to dbsnp index. | `string` | n/a | no |
| `--dbsnp_vqsr` | Label string for VariantRecalibration (haplotypecaller joint variant calling).  If you use AWS iGenomes, this has already been set for you appropriately. | `string` | n/a | no |
| `--dict` | Path to FASTA dictionary file. | `string` | n/a | no |
| `--dragmap` | Path to dragmap indices. | `string` | n/a | no |
| `--fasta` | Path to FASTA genome file. | `string` | n/a | no |
| `--fasta_fai` | Path to FASTA reference index. | `string` | n/a | no |
| `--germline_resource` | Path to GATK Mutect2 Germline Resource File. | `string` | n/a | no |
| `--germline_resource_tbi` | Path to GATK Mutect2 Germline Resource Index. | `string` | n/a | no |
| `--known_indels` | Path to known indels file. | `string` | n/a | no |
| `--known_indels_tbi` | Path to known indels file index. | `string` | n/a | no |
| `--known_indels_vqsr` | Label string for VariantRecalibration (haplotypecaller joint variant calling). If you use AWS iGenomes, this has already been set for you appropriately. | `string` | n/a | no |
| `--known_snps` | Path to known snps file. | `string` | n/a | no |
| `--known_snps_tbi` | Path to known snps file snps. | `string` | n/a | no |
| `--known_snps_vqsr` | Label string for VariantRecalibration (haplotypecaller joint variant calling).If you use AWS iGenomes, this has already been set for you appropriately. | `string` | n/a | no |
| `--mappability` | Path to Control-FREEC mappability file. | `string` | n/a | no |
| `--msisensor2_models` | Path to models folder used with MSIsensor2. | `string` | n/a | no |
| `--msisensor2_scan` | Path to scan file used with MSIsensor2. | `string` | n/a | no |
| `--msisensorpro_scan` | Path to scan file used with MSIsensorPro. | `string` | n/a | no |
| `--ngscheckmate_bed` | Path to SNP bed file for sample checking with NGSCheckMate | `string` | n/a | no |
| `--sentieon_dnascope_model` | Machine learning model for Sentieon Dnascope. | `string` | n/a | no |
| `--snpeff_cache` | Path to snpEff cache. | `string` | `s3://annotation-cache/snpeff_cache/` | no |
| `--snpeff_db` | snpEff DB version. | `string` | n/a | no |
| `--vep_cache` | Path to VEP cache. | `string` | `s3://annotation-cache/vep_cache/` | no |
| `--vep_cache_version` | VEP cache version. | `string` | n/a | no |
| `--vep_genome` | VEP genome. | `string` | n/a | no |
| `--vep_species` | VEP species. | `string` | n/a | no |

### Institutional config options

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| `--custom_config_version` | Git commit id for Institutional configs. | `string` | `master` | no |
| `--custom_config_base` | Base directory for Institutional configs. | `string` | `https://raw.githubusercontent.com/nf-core/configs/master` | no |
| `--config_profile_name` | Institutional config name. | `string` | n/a | no |
| `--config_profile_description` | Institutional config description. | `string` | n/a | no |
| `--config_profile_contact` | Institutional config contact information. | `string` | n/a | no |
| `--config_profile_url` | Institutional config URL link. | `string` | n/a | no |
| `--test_data_base` | Base path / URL for data used in the test profiles | `string` | `https://raw.githubusercontent.com/nf-core/test-datasets/sarek3` | no |
| `--modules_testdata_base_path` | Base path / URL for data used in the modules | `string` | n/a | no |
| `--seq_center` | Sequencing center information to be added to read group (CN field). | `string` | n/a | no |
| `--seq_platform` | Sequencing platform information to be added to read group (PL field). | `string` | `ILLUMINA` | no |

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
| `--multiqc_title` | MultiQC report title. Printed as page header, used for filename if not otherwise specified. | `string` | n/a | no |
| `--multiqc_config` | Custom config file to supply to MultiQC. | `string` | n/a | no |
| `--multiqc_logo` | Custom logo file to supply to MultiQC. File name must also be set in the MultiQC config file | `string` | n/a | no |
| `--multiqc_methods_description` | Custom MultiQC yaml file containing HTML including a methods description. | `string` | n/a | no |
| `--validate_params` | Boolean whether to validate parameters against the schema at runtime | `boolean` | `True` | no |
| `--pipelines_testdata_base_path` | Base URL or local path to location of pipeline test dataset files | `string` | `https://raw.githubusercontent.com/nf-core/test-datasets/` | no |
| `--trace_report_suffix` | Suffix to add to the trace report filename. Default is the date and time in the format yyyy-MM-dd_HH-mm-ss. | `string` | n/a | no |
| `--help` | Display the help message. | `boolean` | n/a | no |
| `--help_full` | Display the full detailed help message. | `boolean` | n/a | no |
| `--show_hidden` | Display hidden parameters in the help message (only works when --help or --help_full are provided). | `boolean` | n/a | no |

## Workflows

| Name | Description | Entry |
|------|-------------|:-----:|
| `NFCORE_SAREK` | n/a | no |
| *(entry)* | n/a | yes |
| `SAREK` | n/a | no |
| `BAM_NGSCHECKMATE` | Take a set of bam files and run NGSCheckMate to determine whether samples match with each other, using a set of SNPs. | no |
| `UTILS_NFCORE_PIPELINE` | Subworkflow with utility functions specific to the nf-core pipeline template | no |
| `UTILS_NEXTFLOW_PIPELINE` | Subworkflow with functionality that may be useful for any Nextflow pipeline | no |
| `VCF_ANNOTATE_SNPEFF` | Perform annotation with snpEff and bgzip + tabix index the resulting VCF file | no |
| `UTILS_NFSCHEMA_PLUGIN` | Run nf-schema to validate parameters and create a summary of changed parameters | no |
| `VCF_ANNOTATE_ENSEMBLVEP` | Perform annotation with ensemblvep and bgzip + tabix index the resulting VCF file | no |
| `BAM_VARIANT_CALLING_SOMATIC_MUTECT2` | Perform variant calling on a paired tumor normal set of samples using mutect2 tumor normal mode. f1r2 output of mutect2 is run through learnreadorientationmodel to get the artifact priors. Run the input bam files through getpileupsummarries and then calculatecontamination to get the contamination and segmentation tables. Filter the mutect2 output vcf using filtermutectcalls, artifact priors and the contamination & segmentation tables for additional filtering. | no |
| `SAMPLESHEET_TO_CHANNEL` | n/a | no |
| `CHANNEL_VARIANT_CALLING_CREATE_CSV` | n/a | no |
| `BAM_VARIANT_CALLING_TUMOR_ONLY_LOFREQ` | n/a | no |
| `BAM_VARIANT_CALLING_TUMOR_ONLY_MUTECT2` | Perform variant calling on a single tumor sample using mutect2 tumor only mode. Run the input bam file through getpileupsummarries and then calculatecontaminationto get the contamination and segmentation tables. Filter the mutect2 output vcf using filtermutectcalls and the contamination & segmentation tables for additional filtering. | no |
| `BAM_JOINT_CALLING_GERMLINE_SENTIEON` | n/a | no |
| `VCF_QC_BCFTOOLS_VCFTOOLS` | n/a | no |
| `BAM_VARIANT_CALLING_SENTIEON_DNASCOPE` | n/a | no |
| `BAM_VARIANT_CALLING_SOMATIC_MUSE` | n/a | no |
| `BAM_VARIANT_CALLING_FREEBAYES` | n/a | no |
| `CHANNEL_BASERECALIBRATOR_CREATE_CSV` | n/a | no |
| `BAM_VARIANT_CALLING_SOMATIC_MANTA` | n/a | no |
| `BAM_VARIANT_CALLING_TUMOR_ONLY_ALL` | n/a | no |
| `PREPARE_REFERENCE_CNVKIT` | n/a | no |
| `CONCATENATE_GERMLINE_VCFS` | n/a | no |
| `BAM_VARIANT_CALLING_TUMOR_ONLY_CONTROLFREEC` | n/a | no |
| `BAM_VARIANT_CALLING_TUMOR_ONLY_MANTA` | n/a | no |
| `BAM_VARIANT_CALLING_SOMATIC_ALL` | n/a | no |
| `BAM_MARKDUPLICATES_SPARK` | n/a | no |
| `BAM_APPLYBQSR_SPARK` | n/a | no |
| `BAM_VARIANT_CALLING_SOMATIC_STRELKA` | n/a | no |
| `CHANNEL_MARKDUPLICATES_CREATE_CSV` | n/a | no |
| `BAM_VARIANT_CALLING_DEEPVARIANT` | n/a | no |
| `VCF_VARLOCIRAPTOR_SINGLE` | n/a | no |
| `CRAM_QC_MOSDEPTH_SAMTOOLS` | n/a | no |
| `DOWNLOAD_CACHE_SNPEFF_VEP` | n/a | no |
| `FASTQ_PREPROCESS_GATK` | n/a | no |
| `BAM_MERGE_INDEX_SAMTOOLS` | n/a | no |
| `FASTQ_PREPROCESS_PARABRICKS` | n/a | no |
| `VCF_VARIANT_FILTERING_GATK` | n/a | no |
| `BAM_CONVERT_SAMTOOLS` | n/a | no |
| `BAM_SENTIEON_DEDUP` | n/a | no |
| `BAM_VARIANT_CALLING_SOMATIC_TIDDIT` | n/a | no |
| `CHANNEL_ALIGN_CREATE_CSV` | n/a | no |
| `BAM_MARKDUPLICATES` | n/a | no |
| `CRAM_MERGE_INDEX_SAMTOOLS` | n/a | no |
| `ANNOTATION_CACHE_INITIALISATION` | n/a | no |
| `BAM_VARIANT_CALLING_SENTIEON_HAPLOTYPER` | n/a | no |
| `BAM_VARIANT_CALLING_SINGLE_TIDDIT` | n/a | no |
| `BAM_VARIANT_CALLING_CNVKIT` | n/a | no |
| `CRAM_SAMPLEQC` | n/a | no |
| `CONSENSUS` | n/a | no |
| `BAM_VARIANT_CALLING_INDEXCOV` | n/a | no |
| `FASTQ_CREATE_UMI_CONSENSUS_FGBIO` | n/a | no |
| `BAM_VARIANT_CALLING_MPILEUP` | n/a | no |
| `BAM_VARIANT_CALLING_SINGLE_STRELKA` | n/a | no |
| `POST_VARIANTCALLING` | n/a | no |
| `VCF_VARLOCIRAPTOR_SOMATIC` | n/a | no |
| `BAM_VARIANT_CALLING_GERMLINE_MANTA` | n/a | no |
| `BAM_APPLYBQSR` | n/a | no |
| `BAM_VARIANT_CALLING_SOMATIC_TNSCOPE` | n/a | no |
| `NORMALIZE_VCFS` | n/a | no |
| `BAM_VARIANT_CALLING_TUMOR_ONLY_TNSCOPE` | Perform variant calling on a single tumor sample using mutect2 tumor only mode. Run the input bam file through getpileupsummarries and then calculatecontaminationto get the contamination and segmentation tables. Filter the mutect2 output vcf using filtermutectcalls and the contamination & segmentation tables for additional filtering. | no |
| `BAM_VARIANT_CALLING_HAPLOTYPECALLER` | n/a | no |
| `PIPELINE_INITIALISATION` | n/a | no |
| `PIPELINE_COMPLETION` | n/a | no |
| `PREPARE_GENOME` | n/a | no |
| `BAM_VARIANT_CALLING_SOMATIC_CONTROLFREEC` | n/a | no |
| `BAM_BASERECALIBRATOR_SPARK` | n/a | no |
| `BAM_BASERECALIBRATOR` | n/a | no |
| `BAM_JOINT_CALLING_GERMLINE_GATK` | n/a | no |
| `CHANNEL_APPLYBQSR_CREATE_CSV` | n/a | no |
| `FASTQ_ALIGN` | n/a | no |
| `BAM_VARIANT_CALLING_GERMLINE_ALL` | n/a | no |
| `VCF_ANNOTATE_ALL` | n/a | no |
| `BAM_VARIANT_CALLING_SOMATIC_ASCAT` | n/a | no |

### `NFCORE_SAREK` Inputs

| Name | Description |
|------|-------------|
| `samplesheet` | n/a |

### `NFCORE_SAREK` Outputs

| Name | Description |
|------|-------------|
| `multiqc_report` | n/a |

### `SAREK` Inputs

| Name | Description |
|------|-------------|
| `input_sample` | n/a |
| `aligner` | n/a |
| `skip_tools` | n/a |
| `step` | n/a |
| `tools` | n/a |
| `ascat_alleles` | n/a |
| `ascat_loci` | n/a |
| `ascat_loci_gc` | n/a |
| `ascat_loci_rt` | n/a |
| `bbsplit_index` | n/a |
| `bcftools_annotations` | n/a |
| `bcftools_annotations_tbi` | n/a |
| `bcftools_columns` | n/a |
| `bcftools_header_lines` | n/a |
| `cf_chrom_len` | n/a |
| `chr_files` | n/a |
| `cnvkit_reference` | n/a |
| `dbsnp` | n/a |
| `dbsnp_tbi` | n/a |
| `dbsnp_vqsr` | n/a |
| `dict` | n/a |
| `fasta` | n/a |
| `fasta_fai` | n/a |
| `germline_resource` | n/a |
| `germline_resource_tbi` | n/a |
| `index_alignment` | n/a |
| `intervals_and_num_intervals` | n/a |
| `intervals_bed_combined` | n/a |
| `intervals_bed_combined_for_variant_calling` | n/a |
| `intervals_bed_gz_tbi_and_num_intervals` | n/a |
| `intervals_bed_gz_tbi_combined` | n/a |
| `intervals_for_preprocessing` | n/a |
| `known_indels_vqsr` | n/a |
| `known_sites_indels` | n/a |
| `known_sites_indels_tbi` | n/a |
| `known_sites_snps` | n/a |
| `known_sites_snps_tbi` | n/a |
| `known_snps_vqsr` | n/a |
| `mappability` | n/a |
| `msisensor2_models` | n/a |
| `msisensorpro_scan` | n/a |
| `ngscheckmate_bed` | n/a |
| `pon` | n/a |
| `pon_tbi` | n/a |
| `sentieon_dnascope_model` | n/a |
| `varlociraptor_scenario_germline` | n/a |
| `varlociraptor_scenario_somatic` | n/a |
| `varlociraptor_scenario_tumor_only` | n/a |
| `snpeff_cache` | n/a |
| `snpeff_db` | n/a |
| `vep_cache` | n/a |
| `vep_cache_version` | n/a |
| `vep_extra_files` | n/a |
| `vep_fasta` | n/a |
| `vep_genome` | n/a |
| `vep_species` | n/a |
| `versions` | n/a |

### `SAREK` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |
| `?` | n/a |

### `BAM_NGSCHECKMATE` Inputs

| Name | Description |
|------|-------------|
| `meta1` | Groovy Map containing sample information e.g. [ id:'test' ] |
| `bam` | BAM files for each sample |
| `meta2` | Groovy Map containing bed file information e.g. [ id:'sarscov2' ] |
| `snp_bed` | BED file containing the SNPs to analyse. NGSCheckMate provides some default ones for hg19/hg38. |
| `meta3` | Groovy Map containing reference genome meta information e.g. [ id:'sarscov2' ] |
| `fasta` | fasta file for the genome |

### `BAM_NGSCHECKMATE` Outputs

| Name | Description |
|------|-------------|
| `pdf` | A pdf containing a dendrogram showing how the samples match up |
| `corr_matrix` | A text file containing the correlation matrix between each sample |
| `matched` | A txt file containing only the samples that match with each other |
| `all` | A txt file containing all the sample comparisons, whether they match or not |
| `vcf` | vcf files for each sample giving the SNP calls |
| `versions` | File containing software versions |

### `UTILS_NFCORE_PIPELINE` Inputs

| Name | Description |
|------|-------------|
| `nextflow_cli_args` | Nextflow CLI positional arguments |

### `UTILS_NFCORE_PIPELINE` Outputs

| Name | Description |
|------|-------------|
| `success` | Dummy output to indicate success |

### `UTILS_NEXTFLOW_PIPELINE` Inputs

| Name | Description |
|------|-------------|
| `print_version` | Print the version of the pipeline and exit |
| `dump_parameters` | Dump the parameters of the pipeline to a JSON file |
| `output_directory` | Path to output dir to write JSON file to. |
| `check_conda_channel` | Check if the conda channel priority is correct. |

### `UTILS_NEXTFLOW_PIPELINE` Outputs

| Name | Description |
|------|-------------|
| `dummy_emit` | Dummy emit to make nf-core subworkflows lint happy |

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

### `UTILS_NFSCHEMA_PLUGIN` Inputs

| Name | Description |
|------|-------------|
| `input_workflow` | The workflow object of the used pipeline. This object contains meta data used to create the params summary log |
| `validate_params` | Validate the parameters and error if invalid. |
| `parameters_schema` | Path to the parameters JSON schema. This has to be the same as the schema given to the `validation.parametersSchema` config option. When this input is empty it will automatically use the configured schema or "${projectDir}/nextflow_schema.json" as default. The schema should not be given in this way for meta pipelines. |

### `UTILS_NFSCHEMA_PLUGIN` Outputs

| Name | Description |
|------|-------------|
| `dummy_emit` | Dummy emit to make nf-core subworkflows lint happy |

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

### `BAM_VARIANT_CALLING_SOMATIC_MUTECT2` Inputs

| Name | Description |
|------|-------------|
| `meta` | Groovy Map containing sample information e.g. [ id:'test' ] |
| `input` | list containing the tumor and normal BAM files, in that order, also able to take CRAM as an input |
| `input_index` | list containing the tumor and normal BAM file indexes, in that order, also able to take CRAM index as an input |
| `which_norm` | optional list of sample headers contained in the normal sample input file. |
| `fasta` | The reference fasta file |
| `fai` | Index of reference fasta file |
| `dict` | GATK sequence dictionary |
| `germline_resource` | Population vcf of germline sequencing, containing allele fractions. |
| `germline_resource_tbi` | Index file for the germline resource. |
| `panel_of_normals` | vcf file to be used as a panel of normals. |
| `panel_of_normals_tbi` | Index for the panel of normals. |
| `interval_file` | File containing intervals. |

### `BAM_VARIANT_CALLING_SOMATIC_MUTECT2` Outputs

| Name | Description |
|------|-------------|
| `versions` | File containing software versions |
| `mutect2_vcf` | Compressed vcf file to be used for variant_calling. |
| `mutect2_tbi` | Indexes of the mutect2_vcf file |
| `mutect2_stats` | Stats files for the mutect2 vcf |
| `mutect2_f1r2` | file containing information to be passed to LearnReadOrientationModel. |
| `artifact_priors` | file containing artifact-priors to be used by filtermutectcalls. |
| `pileup_table_tumor` | File containing the tumor pileup summary table, kept separate as calculatecontamination needs them individually specified. |
| `pileup_table_normal` | File containing the normal pileup summary table, kept separate as calculatecontamination needs them individually specified. |
| `contamination_table` | File containing the contamination table. |
| `segmentation_table` | Output table containing segmentation of tumor minor allele fractions. |
| `filtered_vcf` | file containing filtered mutect2 calls. |
| `filtered_tbi` | tbi file that pairs with filtered vcf. |
| `filtered_stats` | file containing statistics of the filtermutectcalls run. |

### `SAMPLESHEET_TO_CHANNEL` Inputs

| Name | Description |
|------|-------------|
| `ch_from_samplesheet` | n/a |
| `aligner` | n/a |
| `ascat_alleles` | n/a |
| `ascat_loci` | n/a |
| `ascat_loci_gc` | n/a |
| `ascat_loci_rt` | n/a |
| `bcftools_annotations` | n/a |
| `bcftools_annotations_tbi` | n/a |
| `bcftools_columns` | n/a |
| `bcftools_header_lines` | n/a |
| `build_only_index` | n/a |
| `dbsnp` | n/a |
| `fasta` | n/a |
| `germline_resource` | n/a |
| `intervals` | n/a |
| `joint_germline` | n/a |
| `joint_mutect2` | n/a |
| `known_indels` | n/a |
| `known_snps` | n/a |
| `no_intervals` | n/a |
| `pon` | n/a |
| `sentieon_dnascope_emit_mode` | n/a |
| `sentieon_haplotyper_emit_mode` | n/a |
| `seq_center` | n/a |
| `seq_platform` | n/a |
| `skip_tools` | n/a |
| `snpeff_cache` | n/a |
| `snpeff_db` | n/a |
| `step` | n/a |
| `tools` | n/a |
| `umi_length` | n/a |
| `umi_location` | n/a |
| `umi_in_read_header` | n/a |
| `umi_read_structure` | n/a |
| `wes` | n/a |

### `SAMPLESHEET_TO_CHANNEL` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |

### `CHANNEL_VARIANT_CALLING_CREATE_CSV` Inputs

| Name | Description |
|------|-------------|
| `vcf_to_annotate` | n/a |
| `outdir` | n/a |

### `CHANNEL_VARIANT_CALLING_CREATE_CSV` Outputs

| Name | Description |
|------|-------------|
| `<none>` | n/a |

### `BAM_VARIANT_CALLING_TUMOR_ONLY_LOFREQ` Inputs

| Name | Description |
|------|-------------|
| `input` | n/a |
| `fasta` | n/a |
| `fai` | n/a |
| `intervals` | n/a |
| `dict` | n/a |

### `BAM_VARIANT_CALLING_TUMOR_ONLY_LOFREQ` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |

### `BAM_VARIANT_CALLING_TUMOR_ONLY_MUTECT2` Inputs

| Name | Description |
|------|-------------|
| `meta` | Groovy Map containing sample information e.g. [ id:'test' ] |
| `input` | list containing one BAM file, also able to take CRAM as an input |
| `input_index` | list containing one BAM file indexe, also able to take CRAM index as an input |
| `fasta` | The reference fasta file |
| `fai` | Index of reference fasta file |
| `dict` | GATK sequence dictionary |
| `germline_resource` | Population vcf of germline sequencing, containing allele fractions. |
| `germline_resource_tbi` | Index file for the germline resource. |
| `panel_of_normals` | vcf file to be used as a panel of normals. |
| `panel_of_normals_tbi` | Index for the panel of normals. |
| `interval_file` | File containing intervals. |

### `BAM_VARIANT_CALLING_TUMOR_ONLY_MUTECT2` Outputs

| Name | Description |
|------|-------------|
| `versions` | File containing software versions |
| `mutect2_vcf` | Compressed vcf file to be used for variant_calling. |
| `mutect2_tbi` | Indexes of the mutect2_vcf file |
| `mutect2_stats` | Stats files for the mutect2 vcf |
| `pileup_table` | File containing the pileup summary table. |
| `contamination_table` | File containing the contamination table. |
| `segmentation_table` | Output table containing segmentation of tumor minor allele fractions. |
| `filtered_vcf` | file containing filtered mutect2 calls. |
| `filtered_tbi` | tbi file that pairs with filtered vcf. |
| `filtered_stats` | file containing statistics of the filtermutectcalls run. |

### `BAM_JOINT_CALLING_GERMLINE_SENTIEON` Inputs

| Name | Description |
|------|-------------|
| `input` | n/a |
| `fasta` | n/a |
| `fai` | n/a |
| `dict` | n/a |
| `dbsnp` | n/a |
| `dbsnp_tbi` | n/a |
| `dbsnp_vqsr` | n/a |
| `resource_indels_vcf` | n/a |
| `resource_indels_tbi` | n/a |
| `known_indels_vqsr` | n/a |
| `resource_snps_vcf` | n/a |
| `resource_snps_tbi` | n/a |
| `known_snps_vqsr` | n/a |
| `variant_caller` | n/a |

### `BAM_JOINT_CALLING_GERMLINE_SENTIEON` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |

### `VCF_QC_BCFTOOLS_VCFTOOLS` Inputs

| Name | Description |
|------|-------------|
| `vcf` | n/a |
| `target_bed` | n/a |

### `VCF_QC_BCFTOOLS_VCFTOOLS` Outputs

| Name | Description |
|------|-------------|
| `bcftools_stats` | n/a |
| `vcftools_tstv_counts` | n/a |
| `vcftools_tstv_qual` | n/a |
| `vcftools_filter_summary` | n/a |
| `?` | n/a |

### `BAM_VARIANT_CALLING_SENTIEON_DNASCOPE` Inputs

| Name | Description |
|------|-------------|
| `cram` | n/a |
| `fasta` | n/a |
| `fasta_fai` | n/a |
| `dict` | n/a |
| `dbsnp` | n/a |
| `dbsnp_tbi` | n/a |
| `dbsnp_vqsr` | n/a |
| `intervals` | n/a |
| `joint_germline` | n/a |
| `sentieon_dnascope_emit_mode` | n/a |
| `sentieon_dnascope_pcr_indel_model` | n/a |
| `sentieon_dnascope_model` | n/a |

### `BAM_VARIANT_CALLING_SENTIEON_DNASCOPE` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |

### `BAM_VARIANT_CALLING_SOMATIC_MUSE` Inputs

| Name | Description |
|------|-------------|
| `bam_normal` | n/a |
| `bam_tumor` | n/a |
| `fasta` | n/a |
| `dbsnp` | n/a |

### `BAM_VARIANT_CALLING_SOMATIC_MUSE` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |

### `BAM_VARIANT_CALLING_FREEBAYES` Inputs

| Name | Description |
|------|-------------|
| `ch_cram` | n/a |
| `ch_dict` | n/a |
| `ch_fasta` | n/a |
| `ch_fasta_fai` | n/a |
| `ch_intervals` | n/a |

### `BAM_VARIANT_CALLING_FREEBAYES` Outputs

| Name | Description |
|------|-------------|
| `vcf_unfiltered` | n/a |
| `vcf` | n/a |
| `tbi` | n/a |
| `?` | n/a |

### `CHANNEL_BASERECALIBRATOR_CREATE_CSV` Inputs

| Name | Description |
|------|-------------|
| `cram_table_bqsr` | n/a |
| `tools` | n/a |
| `skip_tools` | n/a |
| `outdir` | n/a |
| `save_output_as_bam` | n/a |

### `CHANNEL_BASERECALIBRATOR_CREATE_CSV` Outputs

| Name | Description |
|------|-------------|
| `<none>` | n/a |

### `BAM_VARIANT_CALLING_SOMATIC_MANTA` Inputs

| Name | Description |
|------|-------------|
| `cram` | n/a |
| `fasta` | n/a |
| `fasta_fai` | n/a |
| `intervals` | n/a |

### `BAM_VARIANT_CALLING_SOMATIC_MANTA` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |

### `BAM_VARIANT_CALLING_TUMOR_ONLY_ALL` Inputs

| Name | Description |
|------|-------------|
| `tools` | n/a |
| `bam` | n/a |
| `cram` | n/a |
| `bwa` | n/a |
| `cf_chrom_len` | n/a |
| `chr_files` | n/a |
| `cnvkit_reference` | n/a |
| `dbsnp` | n/a |
| `dbsnp_tbi` | n/a |
| `dict` | n/a |
| `fasta` | n/a |
| `fasta_fai` | n/a |
| `germline_resource` | n/a |
| `germline_resource_tbi` | n/a |
| `intervals` | n/a |
| `intervals_bed_gz_tbi` | n/a |
| `intervals_bed_combined` | n/a |
| `intervals_bed_gz_tbi_combined` | n/a |
| `mappability` | n/a |
| `msisensor2_models` | n/a |
| `panel_of_normals` | n/a |
| `panel_of_normals_tbi` | n/a |
| `joint_mutect2` | n/a |
| `wes` | n/a |

### `BAM_VARIANT_CALLING_TUMOR_ONLY_ALL` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |

### `PREPARE_REFERENCE_CNVKIT` Inputs

| Name | Description |
|------|-------------|
| `fasta` | n/a |
| `intervals_bed_combined` | n/a |

### `PREPARE_REFERENCE_CNVKIT` Outputs

| Name | Description |
|------|-------------|
| `cnvkit_reference` | n/a |
| `?` | n/a |

### `CONCATENATE_GERMLINE_VCFS` Inputs

| Name | Description |
|------|-------------|
| `vcfs` | n/a |

### `CONCATENATE_GERMLINE_VCFS` Outputs

| Name | Description |
|------|-------------|
| `vcfs` | n/a |
| `tbis` | n/a |
| `?` | n/a |

### `BAM_VARIANT_CALLING_TUMOR_ONLY_CONTROLFREEC` Inputs

| Name | Description |
|------|-------------|
| `controlfreec_input` | n/a |
| `fasta` | n/a |
| `fasta_fai` | n/a |
| `dbsnp` | n/a |
| `dbsnp_tbi` | n/a |
| `chr_files` | n/a |
| `mappability` | n/a |
| `intervals_bed` | n/a |

### `BAM_VARIANT_CALLING_TUMOR_ONLY_CONTROLFREEC` Outputs

| Name | Description |
|------|-------------|
| `versions` | n/a |

### `BAM_VARIANT_CALLING_TUMOR_ONLY_MANTA` Inputs

| Name | Description |
|------|-------------|
| `cram` | n/a |
| `fasta` | n/a |
| `fasta_fai` | n/a |
| `intervals` | n/a |

### `BAM_VARIANT_CALLING_TUMOR_ONLY_MANTA` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |

### `BAM_VARIANT_CALLING_SOMATIC_ALL` Inputs

| Name | Description |
|------|-------------|
| `tools` | n/a |
| `bam` | n/a |
| `cram` | n/a |
| `bwa` | n/a |
| `cf_chrom_len` | n/a |
| `chr_files` | n/a |
| `dbsnp` | n/a |
| `dbsnp_tbi` | n/a |
| `dict` | n/a |
| `fasta` | n/a |
| `fasta_fai` | n/a |
| `germline_resource` | n/a |
| `germline_resource_tbi` | n/a |
| `intervals` | n/a |
| `intervals_bed_gz_tbi` | n/a |
| `intervals_bed_combined` | n/a |
| `intervals_bed_gz_tbi_combined` | n/a |
| `mappability` | n/a |
| `msisensorpro_scan` | n/a |
| `panel_of_normals` | n/a |
| `panel_of_normals_tbi` | n/a |
| `allele_files` | n/a |
| `loci_files` | n/a |
| `gc_file` | n/a |
| `rt_file` | n/a |
| `joint_mutect2` | n/a |
| `wes` | n/a |

### `BAM_VARIANT_CALLING_SOMATIC_ALL` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |

### `BAM_MARKDUPLICATES_SPARK` Inputs

| Name | Description |
|------|-------------|
| `bam` | n/a |
| `dict` | n/a |
| `fasta` | n/a |
| `fasta_fai` | n/a |
| `intervals_bed_combined` | n/a |

### `BAM_MARKDUPLICATES_SPARK` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |

### `BAM_APPLYBQSR_SPARK` Inputs

| Name | Description |
|------|-------------|
| `cram` | n/a |
| `dict` | n/a |
| `fasta` | n/a |
| `fasta_fai` | n/a |
| `intervals` | n/a |

### `BAM_APPLYBQSR_SPARK` Outputs

| Name | Description |
|------|-------------|
| `bam` | n/a |
| `cram` | n/a |
| `?` | n/a |

### `BAM_VARIANT_CALLING_SOMATIC_STRELKA` Inputs

| Name | Description |
|------|-------------|
| `cram` | n/a |
| `dict` | n/a |
| `fasta` | n/a |
| `fasta_fai` | n/a |
| `intervals` | n/a |

### `BAM_VARIANT_CALLING_SOMATIC_STRELKA` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |

### `CHANNEL_MARKDUPLICATES_CREATE_CSV` Inputs

| Name | Description |
|------|-------------|
| `cram_markduplicates` | n/a |
| `csv_subfolder` | n/a |
| `outdir` | n/a |
| `save_output_as_bam` | n/a |

### `CHANNEL_MARKDUPLICATES_CREATE_CSV` Outputs

| Name | Description |
|------|-------------|
| `<none>` | n/a |

### `BAM_VARIANT_CALLING_DEEPVARIANT` Inputs

| Name | Description |
|------|-------------|
| `cram` | n/a |
| `dict` | n/a |
| `fasta` | n/a |
| `fasta_fai` | n/a |
| `intervals` | n/a |

### `BAM_VARIANT_CALLING_DEEPVARIANT` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |

### `VCF_VARLOCIRAPTOR_SINGLE` Inputs

| Name | Description |
|------|-------------|
| `ch_cram` | n/a |
| `ch_fasta` | n/a |
| `ch_fasta_fai` | n/a |
| `ch_scenario` | n/a |
| `ch_vcf` | n/a |
| `val_num_chunks` | n/a |
| `val_sampletype` | n/a |

### `VCF_VARLOCIRAPTOR_SINGLE` Outputs

| Name | Description |
|------|-------------|
| `vcf` | n/a |
| `tbi` | n/a |
| `versions` | n/a |

### `CRAM_QC_MOSDEPTH_SAMTOOLS` Inputs

| Name | Description |
|------|-------------|
| `cram` | n/a |
| `fasta` | n/a |
| `intervals` | n/a |

### `CRAM_QC_MOSDEPTH_SAMTOOLS` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |
| `?` | n/a |

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
| `?` | n/a |

### `FASTQ_PREPROCESS_GATK` Inputs

| Name | Description |
|------|-------------|
| `input_fastq` | n/a |
| `input_sample` | n/a |
| `dict` | n/a |
| `fasta` | n/a |
| `fasta_fai` | n/a |
| `index_alignment` | n/a |
| `intervals_and_num_intervals` | n/a |
| `intervals_for_preprocessing` | n/a |
| `known_sites_indels` | n/a |
| `known_sites_indels_tbi` | n/a |
| `bbsplit_index` | n/a |

### `FASTQ_PREPROCESS_GATK` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |

### `BAM_MERGE_INDEX_SAMTOOLS` Inputs

| Name | Description |
|------|-------------|
| `bam` | n/a |

### `BAM_MERGE_INDEX_SAMTOOLS` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |
| `?` | n/a |

### `FASTQ_PREPROCESS_PARABRICKS` Inputs

| Name | Description |
|------|-------------|
| `ch_reads` | n/a |
| `ch_fasta` | n/a |
| `ch_index` | n/a |
| `ch_interval_file` | n/a |
| `ch_known_sites` | n/a |
| `val_output_fmt` | n/a |

### `FASTQ_PREPROCESS_PARABRICKS` Outputs

| Name | Description |
|------|-------------|
| `cram` | n/a |
| `versions` | n/a |
| `reports` | n/a |

### `VCF_VARIANT_FILTERING_GATK` Inputs

| Name | Description |
|------|-------------|
| `vcf` | n/a |
| `fasta` | n/a |
| `fasta_fai` | n/a |
| `dict` | n/a |
| `intervals_bed_combined` | n/a |
| `known_sites` | n/a |
| `known_sites_tbi` | n/a |

### `VCF_VARIANT_FILTERING_GATK` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |

### `BAM_CONVERT_SAMTOOLS` Inputs

| Name | Description |
|------|-------------|
| `input` | n/a |
| `fasta` | n/a |
| `fasta_fai` | n/a |
| `interleaved` | n/a |

### `BAM_CONVERT_SAMTOOLS` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |
| `?` | n/a |

### `BAM_SENTIEON_DEDUP` Inputs

| Name | Description |
|------|-------------|
| `bam` | n/a |
| `bai` | n/a |
| `fasta` | n/a |
| `fasta_fai` | n/a |
| `intervals_bed_combined` | n/a |

### `BAM_SENTIEON_DEDUP` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |

### `BAM_VARIANT_CALLING_SOMATIC_TIDDIT` Inputs

| Name | Description |
|------|-------------|
| `cram_normal` | n/a |
| `cram_tumor` | n/a |
| `fasta` | n/a |
| `bwa` | n/a |

### `BAM_VARIANT_CALLING_SOMATIC_TIDDIT` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |

### `CHANNEL_ALIGN_CREATE_CSV` Inputs

| Name | Description |
|------|-------------|
| `bam_indexed` | n/a |
| `outdir` | n/a |
| `save_output_as_bam` | n/a |

### `CHANNEL_ALIGN_CREATE_CSV` Outputs

| Name | Description |
|------|-------------|
| `<none>` | n/a |

### `BAM_MARKDUPLICATES` Inputs

| Name | Description |
|------|-------------|
| `bam` | n/a |
| `fasta` | n/a |
| `fasta_fai` | n/a |
| `intervals_bed_combined` | n/a |

### `BAM_MARKDUPLICATES` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |

### `CRAM_MERGE_INDEX_SAMTOOLS` Inputs

| Name | Description |
|------|-------------|
| `cram` | n/a |
| `fasta` | n/a |
| `fasta_fai` | n/a |

### `CRAM_MERGE_INDEX_SAMTOOLS` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |
| `?` | n/a |

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

### `BAM_VARIANT_CALLING_SENTIEON_HAPLOTYPER` Inputs

| Name | Description |
|------|-------------|
| `cram` | n/a |
| `fasta` | n/a |
| `fasta_fai` | n/a |
| `dict` | n/a |
| `dbsnp` | n/a |
| `dbsnp_tbi` | n/a |
| `dbsnp_vqsr` | n/a |
| `intervals` | n/a |
| `joint_germline` | n/a |
| `sentieon_haplotyper_emit_mode` | n/a |

### `BAM_VARIANT_CALLING_SENTIEON_HAPLOTYPER` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |

### `BAM_VARIANT_CALLING_SINGLE_TIDDIT` Inputs

| Name | Description |
|------|-------------|
| `cram` | n/a |
| `fasta` | n/a |
| `bwa` | n/a |

### `BAM_VARIANT_CALLING_SINGLE_TIDDIT` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |

### `BAM_VARIANT_CALLING_CNVKIT` Inputs

| Name | Description |
|------|-------------|
| `cram` | n/a |
| `fasta` | n/a |
| `fasta_fai` | n/a |
| `targets` | n/a |
| `reference` | n/a |

### `BAM_VARIANT_CALLING_CNVKIT` Outputs

| Name | Description |
|------|-------------|
| `cnv_calls_raw` | n/a |
| `cnv_calls_export` | n/a |
| `?` | n/a |

### `CRAM_SAMPLEQC` Inputs

| Name | Description |
|------|-------------|
| `cram` | n/a |
| `ngscheckmate_bed` | n/a |
| `fasta` | n/a |
| `skip_baserecalibration` | n/a |
| `intervals_for_preprocessing` | n/a |

### `CRAM_SAMPLEQC` Outputs

| Name | Description |
|------|-------------|
| `corr_matrix` | n/a |
| `matched` | n/a |
| `all` | n/a |
| `vcf` | n/a |
| `pdf` | n/a |
| `?` | n/a |
| `?` | n/a |

### `CONSENSUS` Inputs

| Name | Description |
|------|-------------|
| `vcfs` | n/a |

### `CONSENSUS` Outputs

| Name | Description |
|------|-------------|
| `versions` | n/a |
| `vcfs` | n/a |
| `tbis` | n/a |

### `BAM_VARIANT_CALLING_INDEXCOV` Inputs

| Name | Description |
|------|-------------|
| `cram` | n/a |
| `fasta` | n/a |
| `fasta_fai` | n/a |

### `BAM_VARIANT_CALLING_INDEXCOV` Outputs

| Name | Description |
|------|-------------|
| `out_indexcov` | n/a |
| `?` | n/a |

### `FASTQ_CREATE_UMI_CONSENSUS_FGBIO` Inputs

| Name | Description |
|------|-------------|
| `reads` | n/a |
| `fasta` | n/a |
| `fai` | n/a |
| `map_index` | n/a |
| `groupreadsbyumi_strategy` | n/a |

### `FASTQ_CREATE_UMI_CONSENSUS_FGBIO` Outputs

| Name | Description |
|------|-------------|
| `umibam` | n/a |
| `groupbam` | n/a |
| `consensusbam` | n/a |
| `versions` | n/a |

### `BAM_VARIANT_CALLING_MPILEUP` Inputs

| Name | Description |
|------|-------------|
| `cram` | n/a |
| `dict` | n/a |
| `fasta` | n/a |
| `intervals` | n/a |

### `BAM_VARIANT_CALLING_MPILEUP` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |

### `BAM_VARIANT_CALLING_SINGLE_STRELKA` Inputs

| Name | Description |
|------|-------------|
| `cram` | n/a |
| `dict` | n/a |
| `fasta` | n/a |
| `fasta_fai` | n/a |
| `intervals` | n/a |

### `BAM_VARIANT_CALLING_SINGLE_STRELKA` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |

### `POST_VARIANTCALLING` Inputs

| Name | Description |
|------|-------------|
| `tools` | n/a |
| `cram_germline` | n/a |
| `germline_vcfs` | n/a |
| `germline_tbis` | n/a |
| `cram_tumor_only` | n/a |
| `tumor_only_vcfs` | n/a |
| `tumor_only_tbis` | n/a |
| `cram_somatic` | n/a |
| `somatic_vcfs` | n/a |
| `somatic_tbis` | n/a |
| `fasta` | n/a |
| `fai` | n/a |
| `concatenate_vcfs` | n/a |
| `filter_vcfs` | n/a |
| `snv_consensus_calling` | n/a |
| `normalize_vcfs` | n/a |
| `varlociraptor_chunk_size` | n/a |
| `varlociraptor_scenario_germline` | n/a |
| `varlociraptor_scenario_somatic` | n/a |
| `varlociraptor_scenario_tumor_only` | n/a |

### `POST_VARIANTCALLING` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |

### `VCF_VARLOCIRAPTOR_SOMATIC` Inputs

| Name | Description |
|------|-------------|
| `ch_cram` | n/a |
| `ch_fasta` | n/a |
| `ch_fasta_fai` | n/a |
| `ch_scenario` | n/a |
| `ch_somatic_vcf` | n/a |
| `ch_germline_vcf` | n/a |
| `val_num_chunks` | n/a |

### `VCF_VARLOCIRAPTOR_SOMATIC` Outputs

| Name | Description |
|------|-------------|
| `vcf` | n/a |
| `tbi` | n/a |
| `versions` | n/a |

### `BAM_VARIANT_CALLING_GERMLINE_MANTA` Inputs

| Name | Description |
|------|-------------|
| `cram` | n/a |
| `fasta` | n/a |
| `fasta_fai` | n/a |
| `intervals` | n/a |

### `BAM_VARIANT_CALLING_GERMLINE_MANTA` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |

### `BAM_APPLYBQSR` Inputs

| Name | Description |
|------|-------------|
| `cram` | n/a |
| `dict` | n/a |
| `fasta` | n/a |
| `fasta_fai` | n/a |
| `intervals` | n/a |

### `BAM_APPLYBQSR` Outputs

| Name | Description |
|------|-------------|
| `bam` | n/a |
| `cram` | n/a |
| `?` | n/a |

### `BAM_VARIANT_CALLING_SOMATIC_TNSCOPE` Inputs

| Name | Description |
|------|-------------|
| `input` | n/a |
| `fasta` | n/a |
| `fai` | n/a |
| `dict` | n/a |
| `germline_resource` | n/a |
| `germline_resource_tbi` | n/a |
| `panel_of_normals` | n/a |
| `panel_of_normals_tbi` | n/a |
| `intervals` | n/a |

### `BAM_VARIANT_CALLING_SOMATIC_TNSCOPE` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |

### `NORMALIZE_VCFS` Inputs

| Name | Description |
|------|-------------|
| `vcfs` | n/a |
| `fasta` | n/a |

### `NORMALIZE_VCFS` Outputs

| Name | Description |
|------|-------------|
| `vcfs` | n/a |
| `tbis` | n/a |
| `?` | n/a |

### `BAM_VARIANT_CALLING_TUMOR_ONLY_TNSCOPE` Inputs

| Name | Description |
|------|-------------|
| `meta` | Groovy Map containing sample information e.g. [ id:'test' ] |
| `input` | list containing one BAM file, also able to take CRAM as an input |
| `input_index` | list containing one BAM file indexe, also able to take CRAM index as an input |
| `fasta` | The reference fasta file |
| `fai` | Index of reference fasta file |
| `dict` | GATK sequence dictionary |
| `germline_resource` | Population vcf of germline sequencing, containing allele fractions. |
| `germline_resource_tbi` | Index file for the germline resource. |
| `panel_of_normals` | vcf file to be used as a panel of normals. |
| `panel_of_normals_tbi` | Index for the panel of normals. |
| `interval_file` | File containing intervals. |

### `BAM_VARIANT_CALLING_TUMOR_ONLY_TNSCOPE` Outputs

| Name | Description |
|------|-------------|
| `versions` | File containing software versions |
| `mutect2_vcf` | Compressed vcf file to be used for variant_calling. |
| `mutect2_tbi` | Indexes of the mutect2_vcf file |
| `mutect2_stats` | Stats files for the mutect2 vcf |
| `pileup_table` | File containing the pileup summary table. |
| `contamination_table` | File containing the contamination table. |
| `segmentation_table` | Output table containing segmentation of tumor minor allele fractions. |
| `filtered_vcf` | file containing filtered mutect2 calls. |
| `filtered_tbi` | tbi file that pairs with filtered vcf. |
| `filtered_stats` | file containing statistics of the filtermutectcalls run. |

### `BAM_VARIANT_CALLING_HAPLOTYPECALLER` Inputs

| Name | Description |
|------|-------------|
| `cram` | n/a |
| `fasta` | n/a |
| `fasta_fai` | n/a |
| `dict` | n/a |
| `dbsnp` | n/a |
| `dbsnp_tbi` | n/a |
| `intervals` | n/a |

### `BAM_VARIANT_CALLING_HAPLOTYPECALLER` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |

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
| `?` | n/a |

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

### `PREPARE_GENOME` Inputs

| Name | Description |
|------|-------------|
| `ascat_alleles_in` | n/a |
| `ascat_loci_in` | n/a |
| `ascat_loci_gc_in` | n/a |
| `ascat_loci_rt_in` | n/a |
| `bbsplit_fasta_list_in` | n/a |
| `bbsplit_index_in` | n/a |
| `bcftools_annotations_in` | n/a |
| `bcftools_annotations_tbi_in` | n/a |
| `bwa_in` | n/a |
| `bwamem2_in` | n/a |
| `chr_dir_in` | n/a |
| `dbsnp_in` | n/a |
| `dbsnp_tbi_in` | n/a |
| `dict_in` | n/a |
| `dragmap_in` | n/a |
| `fasta_in` | n/a |
| `fasta_fai_in` | n/a |
| `germline_resource_in` | n/a |
| `germline_resource_tbi_in` | n/a |
| `known_indels_in` | n/a |
| `known_indels_tbi_in` | n/a |
| `known_snps_in` | n/a |
| `known_snps_tbi_in` | n/a |
| `msisensor2_models_in` | n/a |
| `msisensorpro_scan_in` | n/a |
| `pon_in` | n/a |
| `pon_tbi_in` | n/a |
| `aligner` | n/a |
| `step` | n/a |
| `tools` | n/a |
| `vep_include_fasta` | n/a |

### `PREPARE_GENOME` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |

### `BAM_VARIANT_CALLING_SOMATIC_CONTROLFREEC` Inputs

| Name | Description |
|------|-------------|
| `controlfreec_input` | n/a |
| `fasta` | n/a |
| `fasta_fai` | n/a |
| `dbsnp` | n/a |
| `dbsnp_tbi` | n/a |
| `chr_files` | n/a |
| `mappability` | n/a |
| `intervals_bed` | n/a |

### `BAM_VARIANT_CALLING_SOMATIC_CONTROLFREEC` Outputs

| Name | Description |
|------|-------------|
| `versions` | n/a |

### `BAM_BASERECALIBRATOR_SPARK` Inputs

| Name | Description |
|------|-------------|
| `cram` | n/a |
| `dict` | n/a |
| `fasta` | n/a |
| `fasta_fai` | n/a |
| `intervals` | n/a |
| `known_sites` | n/a |
| `known_sites_tbi` | n/a |

### `BAM_BASERECALIBRATOR_SPARK` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |
| `?` | n/a |

### `BAM_BASERECALIBRATOR` Inputs

| Name | Description |
|------|-------------|
| `cram` | n/a |
| `dict` | n/a |
| `fasta` | n/a |
| `fasta_fai` | n/a |
| `intervals` | n/a |
| `known_sites` | n/a |
| `known_sites_tbi` | n/a |

### `BAM_BASERECALIBRATOR` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |
| `?` | n/a |

### `BAM_JOINT_CALLING_GERMLINE_GATK` Inputs

| Name | Description |
|------|-------------|
| `input` | n/a |
| `fasta` | n/a |
| `fai` | n/a |
| `dict` | n/a |
| `dbsnp` | n/a |
| `dbsnp_tbi` | n/a |
| `dbsnp_vqsr` | n/a |
| `resource_indels_vcf` | n/a |
| `resource_indels_tbi` | n/a |
| `known_indels_vqsr` | n/a |
| `resource_snps_vcf` | n/a |
| `resource_snps_tbi` | n/a |
| `known_snps_vqsr` | n/a |

### `BAM_JOINT_CALLING_GERMLINE_GATK` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |

### `CHANNEL_APPLYBQSR_CREATE_CSV` Inputs

| Name | Description |
|------|-------------|
| `cram_recalibrated_index` | n/a |
| `outdir` | n/a |
| `save_output_as_bam` | n/a |

### `CHANNEL_APPLYBQSR_CREATE_CSV` Outputs

| Name | Description |
|------|-------------|
| `<none>` | n/a |

### `FASTQ_ALIGN` Inputs

| Name | Description |
|------|-------------|
| `reads` | n/a |
| `index` | n/a |
| `sort` | n/a |
| `fasta` | n/a |
| `fasta_fai` | n/a |

### `FASTQ_ALIGN` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |

### `BAM_VARIANT_CALLING_GERMLINE_ALL` Inputs

| Name | Description |
|------|-------------|
| `tools` | n/a |
| `skip_tools` | n/a |
| `bam` | n/a |
| `cram` | n/a |
| `bwa` | n/a |
| `cnvkit_reference` | n/a |
| `dbsnp` | n/a |
| `dbsnp_tbi` | n/a |
| `dbsnp_vqsr` | n/a |
| `dict` | n/a |
| `fasta` | n/a |
| `fasta_fai` | n/a |
| `intervals` | n/a |
| `intervals_bed_combined` | n/a |
| `intervals_bed_gz_tbi_combined` | n/a |
| `intervals_bed_combined_haplotypec` | n/a |
| `intervals_bed_gz_tbi` | n/a |
| `known_indels_vqsr` | n/a |
| `known_sites_indels` | n/a |
| `known_sites_indels_tbi` | n/a |
| `known_sites_snps` | n/a |
| `known_sites_snps_tbi` | n/a |
| `known_snps_vqsr` | n/a |
| `joint_germline` | n/a |
| `skip_haplotypecaller_filter` | n/a |
| `sentieon_haplotyper_emit_mode` | n/a |
| `sentieon_dnascope_emit_mode` | n/a |
| `sentieon_dnascope_pcr_indel_model` | n/a |
| `sentieon_dnascope_model` | n/a |

### `BAM_VARIANT_CALLING_GERMLINE_ALL` Outputs

| Name | Description |
|------|-------------|
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |
| `?` | n/a |

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
| `?` | n/a |

### `BAM_VARIANT_CALLING_SOMATIC_ASCAT` Inputs

| Name | Description |
|------|-------------|
| `cram_pair` | n/a |
| `allele_files` | n/a |
| `loci_files` | n/a |
| `intervals_bed` | n/a |
| `fasta` | n/a |
| `gc_file` | n/a |
| `rt_file` | n/a |

### `BAM_VARIANT_CALLING_SOMATIC_ASCAT` Outputs

| Name | Description |
|------|-------------|
| `versions` | n/a |

## Processes

| Name | Description |
|------|-------------|
| `MULTIQC` | Aggregate results from bioinformatics analyses across many samples into a single report |
| `UNTAR` | Extract files. |
| `MOSDEPTH` | Calculates genome-wide sequencing coverage. |
| `VCFTOOLS` | A set of tools written in Perl and C++ for working with VCF files |
| `UNZIP` | Unzip ZIP archive files |
| `YTE` | A YAML template engine with Python expressions |
| `GAWK` | If you are like many computer users, you would frequently like to make changes in various text files wherever certain patterns appear, or extract data from parts of certain lines while discarding the rest. The job is easy with awk, especially the GNU implementation gawk. |
| `FASTQC` | Run FastQC on sequenced reads |
| `ASCAT` | copy number profiles of tumour cells. |
| `FREEBAYES` | A haplotype-based variant detector |
| `FASTP` | Perform adapter/quality trimming on sequencing reads |
| `GUNZIP` | Compresses and decompresses files. |
| `SPRING_DECOMPRESS` | Fast, efficient, lossless decompression of FASTQ files. |
| `LOFREQ_CALLPARALLEL` | It predicts variants using multiple processors |
| `GATK4_INTERVALLISTTOBED` | Converts an Picard IntervalList file to a BED file. |
| `GATK4_CALCULATECONTAMINATION` | Calculates the fraction of reads from cross-sample contamination based on summary tables from getpileupsummaries. Output to be used with filtermutectcalls. |
| `GATK4_FILTERMUTECTCALLS` | Filters the raw output of mutect2, can optionally use outputs of calculatecontamination and learnreadorientationmodel to improve filtering. |
| `GATK4_APPLYVQSR` | Apply a score cutoff to filter variants based on a recalibration table. AplyVQSR performs the second pass in a two-stage process called Variant Quality Score Recalibration (VQSR). Specifically, it applies filtering to the input variants based on the recalibration table produced in the first step by VariantRecalibrator and a target sensitivity value. |
| `GATK4_GENOMICSDBIMPORT` | merge GVCFs from multiple samples. For use in joint genotyping or somatic panel of normal creation. |
| `GATK4_LEARNREADORIENTATIONMODEL` | Uses f1r2 counts collected during mutect2 to Learn the prior probability of read orientation artifacts |
| `GATK4_VARIANTRECALIBRATOR` | Build a recalibration model to score variant quality for filtering purposes. It is highly recommended to follow GATK best practices when using this module, the gaussian mixture model requires a large number of samples to be used for the tool to produce optimal results. For example, 30 samples for exome data. For more details see https://gatk.broadinstitute.org/hc/en-us/articles/4402736812443-Which-training-sets-arguments-should-I-use-for-running-VQSR- |
| `GATK4_GATHERBQSRREPORTS` | Gathers scattered BQSR recalibration reports into a single file |
| `GATK4_GETPILEUPSUMMARIES` | Summarizes counts of reads that support reference, alternate and other alleles for given sites. Results can be used with CalculateContamination. Requires a common germline variant sites file, such as from gnomAD. |
| `GATK4_GENOTYPEGVCFS` | Perform joint genotyping on one or more samples pre-called with HaplotypeCaller. |
| `GATK4_CREATESEQUENCEDICTIONARY` | Creates a sequence dictionary for a reference sequence |
| `GATK4_GATHERPILEUPSUMMARIES` | write your description here |
| `GATK4_ESTIMATELIBRARYCOMPLEXITY` | Estimates the numbers of unique molecules in a sequencing library. |
| `GATK4_HAPLOTYPECALLER` | Call germline SNPs and indels via local re-assembly of haplotypes |
| `GATK4_CNNSCOREVARIANTS` | Apply a Convolutional Neural Net to filter annotated variants |
| `GATK4_BASERECALIBRATOR` | Generate recalibration table for Base Quality Score Recalibration (BQSR) |
| `GATK4_APPLYBQSR` | Apply base quality score recalibration (BQSR) to a bam file |
| `GATK4_MERGEVCFS` | Merges several vcf files |
| `GATK4_FILTERVARIANTTRANCHES` | Apply tranche filtering |
| `GATK4_MARKDUPLICATES` | This tool locates and tags duplicate reads in a BAM or SAM file, where duplicate reads are defined as originating from a single fragment of DNA. |
| `GATK4_MUTECT2` | Call somatic SNVs and indels via local assembly of haplotypes. |
| `GATK4_MERGEMUTECTSTATS` | Merges mutect2 stats generated on different intervals/regions |
| `GATK4SPARK_BASERECALIBRATOR` | Generate recalibration table for Base Quality Score Recalibration (BQSR) |
| `GATK4SPARK_APPLYBQSR` | Apply base quality score recalibration (BQSR) to a bam file |
| `GATK4SPARK_MARKDUPLICATES` | This tool locates and tags duplicate reads in a BAM or SAM file, where duplicate reads are defined as originating from a single fragment of DNA. |
| `DEEPVARIANT_RUNDEEPVARIANT` | DeepVariant is an analysis pipeline that uses a deep neural network to call genetic variants from next-generation DNA sequencing data |
| `SENTIEON_GVCFTYPER` | Perform joint genotyping on one or more samples pre-called with Sentieon's Haplotyper. |
| `SENTIEON_TNSCOPE` | TNscope algorithm performs somatic variant calling on the tumor-normal matched pair or the tumor only data, using a Haplotyper algorithm. |
| `SENTIEON_DNAMODELAPPLY` | modifies the input VCF file by adding the MLrejected FILTER to the variants |
| `SENTIEON_BWAMEM` | Performs fastq alignment to a fasta reference using Sentieon's BWA MEM |
| `SENTIEON_APPLYVARCAL` | Apply a score cutoff to filter variants based on a recalibration table. Sentieon's Aplyvarcal performs the second pass in a two-stage process called Variant Quality Score Recalibration (VQSR). Specifically, it applies filtering to the input variants based on the recalibration table produced in the previous step VarCal and a target sensitivity value. https://support.sentieon.com/manual/usages/general/#applyvarcal-algorithm |
| `SENTIEON_VARCAL` | Module for Sentieons VarCal. The VarCal algorithm calculates the Variant Quality Score Recalibration (VQSR). VarCal builds a recalibration model for scoring variant quality. https://support.sentieon.com/manual/usages/general/#varcal-algorithm |
| `SENTIEON_DNASCOPE` | DNAscope algorithm performs an improved version of Haplotype variant calling. |
| `SENTIEON_HAPLOTYPER` | Runs Sentieon's haplotyper for germline variant calling. |
| `SENTIEON_DEDUP` | Runs the sentieon tool LocusCollector followed by Dedup. LocusCollector collects read information that is used by Dedup which in turn marks or removes duplicate reads. |
| `SAMTOOLS_BAM2FQ` | The module uses bam2fq method from samtools to convert a SAM, BAM or CRAM file to FASTQ format |
| `SAMTOOLS_MERGE` | Merge BAM or CRAM file |
| `SAMTOOLS_MPILEUP` | BAM |
| `SAMTOOLS_FAIDX` | Index FASTA file, and optionally generate a file of chromosome sizes |
| `SAMTOOLS_VIEW` | filter/convert SAM/BAM/CRAM file |
| `SAMTOOLS_INDEX` | Index SAM/BAM/CRAM file |
| `SAMTOOLS_COLLATEFASTQ` | The module uses collate and then fastq methods from samtools to convert a SAM, BAM or CRAM file to FASTQ format |
| `SAMTOOLS_STATS` | Produces comprehensive statistics from SAM/BAM/CRAM file |
| `SAMTOOLS_CONVERT` | convert and then index CRAM -> BAM or BAM -> CRAM file |
| `VCFLIB_VCFFILTER` | Command line tools for parsing and manipulating VCF files. |
| `BBMAP_BBSPLIT` | Split sequencing reads by mapping them to multiple references simultaneously |
| `MSISENSOR2_MSI` | msisensor2 detection of MSI regions. |
| `CONTROLFREEC_FREEC2BED` | Plot Freec output |
| `CONTROLFREEC_MAKEGRAPH2` | Plot Freec output |
| `CONTROLFREEC_FREEC2CIRCOS` | Format Freec output to circos input format |
| `CONTROLFREEC_FREEC` | Copy number and genotype annotation from whole genome and whole exome sequencing data |
| `CONTROLFREEC_ASSESSSIGNIFICANCE` | Add both Wilcoxon test and Kolmogorov-Smirnov test p-values to each CNV output of FREEC |
| `GOLEFT_INDEXCOV` | Quickly estimate coverage from a whole-genome bam or cram index. A bam index has 16KB resolution so that's what this gives, but it provides what appears to be a high-quality coverage estimate in seconds per genome. |
| `DRAGMAP_ALIGN` | Performs fastq alignment to a reference using DRAGMAP |
| `DRAGMAP_HASHTABLE` | Create DRAGEN hashtable for reference genome |
| `STRELKA_GERMLINE` | Strelka2 is a fast and accurate small variant caller optimized for analysis of germline variation |
| `STRELKA_SOMATIC` | Strelka2 is a fast and accurate small variant caller optimized for analysis of germline variation in small cohorts and somatic variation in tumor/normal sample pairs |
| `BWA_INDEX` | Create BWA index for reference genome |
| `BWA_MEM` | Performs fastq alignment to a fasta reference using BWA |
| `SNPEFF_SNPEFF` | Genetic variant annotation and functional effect prediction toolbox |
| `SNPEFF_DOWNLOAD` | Genetic variant annotation and functional effect prediction toolbox |
| `NGSCHECKMATE_NCM` | Determining whether sequencing data comes from the same individual by using SNP matching. Designed for humans on vcf or bam files. |
| `ENSEMBLVEP_VEP` | Ensembl Variant Effect Predictor (VEP). The output-file-format is controlled through `task.ext.args`. |
| `ENSEMBLVEP_DOWNLOAD` | Ensembl Variant Effect Predictor (VEP). The cache downloading options are controlled through `task.ext.args`. |
| `VARLOCIRAPTOR_CALLVARIANTS` | Call variants for a given scenario specified with the varlociraptor calling grammar, preprocessed by varlociraptor preprocessing |
| `VARLOCIRAPTOR_PREPROCESS` | Obtains per-sample observations for the actual calling process with varlociraptor calls |
| `VARLOCIRAPTOR_ESTIMATEALIGNMENTPROPERTIES` | In order to judge about candidate indel and structural variants, Varlociraptor needs to know about certain properties of the underlying sequencing experiment in combination with the used read aligner. |
| `CNVKIT_GENEMETRICS` | Copy number variant detection from high-throughput sequencing data |
| `CNVKIT_CALL` | Given segmented log2 ratio estimates (.cns), derive each segment’s absolute integer copy number |
| `CNVKIT_BATCH` | Copy number variant detection from high-throughput sequencing data |
| `CNVKIT_ANTITARGET` | Derive off-target (“antitarget”) bins from target regions. |
| `CNVKIT_EXPORT` | Convert copy number ratio tables (.cnr files) or segments (.cns) to another format. |
| `CNVKIT_REFERENCE` | Compile a coverage reference from the given files (normal samples). |
| `RBT_VCFSPLIT` | A tool for splitting VCF/BCF files into N equal chunks, including BND support |
| `FGBIO_FASTQTOBAM` | Using the fgbio tools, converts FASTQ files sequenced into unaligned BAM or CRAM files possibly moving the UMI barcode into the RX field of the reads |
| `FGBIO_COPYUMIFROMREADNAME` | Copies the UMI at the end of a bam files read name to the RX tag. |
| `FGBIO_CALLMOLECULARCONSENSUSREADS` | Calls consensus sequences from reads with the same unique molecular tag. |
| `FGBIO_GROUPREADSBYUMI` | Groups reads together that appear to have come from the same original molecule. Reads are grouped by template, and then templates are sorted by the 5’ mapping positions of the reads from the template, used from earliest mapping position to latest. Reads that have the same end positions are then sub-grouped by UMI sequence. (!) Note: the MQ tag is required on reads with mapped mates (!) This can be added using samblaster with the optional argument --addMateTags. |
| `BWAMEM2_INDEX` | Create BWA-mem2 index for reference genome |
| `BWAMEM2_MEM` | Performs fastq alignment to a fasta reference using BWA |
| `MANTA_TUMORONLY` | Manta calls structural variants (SVs) and indels from mapped paired-end sequencing reads. It is optimized for analysis of germline variation in small sets of individuals and somatic variation in tumor/normal sample pairs. |
| `MANTA_GERMLINE` | Manta calls structural variants (SVs) and indels from mapped paired-end sequencing reads. It is optimized for analysis of germline variation in small sets of individuals and somatic variation in tumor/normal sample pairs. |
| `MANTA_SOMATIC` | Manta calls structural variants (SVs) and indels from mapped paired-end sequencing reads. It is optimized for analysis of germline variation in small sets of individuals and somatic variation in tumor/normal sample pairs. |
| `BCFTOOLS_CONCAT` | Concatenate VCF files |
| `BCFTOOLS_SORT` | Sorts VCF files |
| `BCFTOOLS_MERGE` | Merge VCF files |
| `BCFTOOLS_MPILEUP` | Compresses VCF files |
| `BCFTOOLS_ANNOTATE` | Add or remove annotations. |
| `BCFTOOLS_NORM` | Normalize VCF file |
| `BCFTOOLS_VIEW` | View, subset and filter VCF or BCF files by position and filtering expression. Convert between VCF and BCF |
| `BCFTOOLS_STATS` | Generates stats from VCF files |
| `BCFTOOLS_ISEC` | Apply set operations to VCF files |
| `MSISENSORPRO_SCAN` | MSIsensor-pro evaluates Microsatellite Instability (MSI) for cancer patients with next generation sequencing data. It accepts the whole genome sequencing, whole exome sequencing and target region (panel) sequencing data as input |
| `MSISENSORPRO_MSISOMATIC` | MSIsensor-pro evaluates Microsatellite Instability (MSI) for cancer patients with next generation sequencing data. It accepts the whole genome sequencing, whole exome sequencing and target region (panel) sequencing data as input |
| `MUSE_SUMP` | Computes tier-based cutoffs from a sample-specific error model which is generated by muse/call and reports the finalized variants |
| `MUSE_CALL` | pre-filtering and calculating position-specific summary statistics using the Markov substitution model |
| `PARABRICKS_FQ2BAM` | NVIDIA Clara Parabricks GPU-accelerated alignment, sorting, BQSR calculation, and duplicate marking. Note this nf-core module requires files to be copied into the working directory and not symlinked. |
| `SVDB_MERGE` | The merge module merges structural variants within one or more vcf files. |
| `TIDDIT_SV` | Identify chromosomal rearrangements. |
| `TABIX_TABIX` | create tabix index from a sorted bgzip tab-delimited genome file |
| `TABIX_BGZIPTABIX` | bgzip a sorted tab-delimited genome file and then create tabix index |
| `CAT_CAT` | A module for concatenation of gzipped or uncompressed files |
| `CAT_FASTQ` | Concatenates fastq files |
| `CREATE_INTERVALS_BED` | n/a |
| `ADD_INFO_TO_VCF` | n/a |
| `SAMTOOLS_REINDEX_BAM` | The aim of this process is to re-index the bam file without the duplicate, supplementary, unmapped etc, for goleft/indexcov It creates a BAM containing only a header (so indexcov can get the sample name) and a BAM index were low quality reads, supplementary etc, have been removed |

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
| `archive` | `file` | File to be untar |

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

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path('*.global.dist.txt')` | `tuple` | `global_txt` | n/a |
| `val(meta), path('*.summary.txt')` | `tuple` | `summary_txt` | n/a |
| `val(meta), path('*.region.dist.txt')` | `tuple` | `regions_txt` | n/a |
| `val(meta), path('*.per-base.d4')` | `tuple` | `per_base_d4` | n/a |
| `val(meta), path('*.per-base.bed.gz')` | `tuple` | `per_base_bed` | n/a |
| `val(meta), path('*.per-base.bed.gz.csi')` | `tuple` | `per_base_csi` | n/a |
| `val(meta), path('*.regions.bed.gz')` | `tuple` | `regions_bed` | n/a |
| `val(meta), path('*.regions.bed.gz.csi')` | `tuple` | `regions_csi` | n/a |
| `val(meta), path('*.quantized.bed.gz')` | `tuple` | `quantized_bed` | n/a |
| `val(meta), path('*.quantized.bed.gz.csi')` | `tuple` | `quantized_csi` | n/a |
| `val(meta), path('*.thresholds.bed.gz')` | `tuple` | `thresholds_bed` | n/a |
| `val(meta), path('*.thresholds.bed.gz.csi')` | `tuple` | `thresholds_csi` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

### `VCFTOOLS` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `variant_file` | `file` | variant input file which can be vcf, vcf.gz, or bcf format. |
| `bed` | `file` | bed file which can be used with different arguments in vcftools (optional) |
| `diff_variant_file` | `file` | secondary variant file which can be used with the 'diff' suite of tools (optional) |

### `VCFTOOLS` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*.vcf")` | `tuple` | `vcf` | n/a |
| `val(meta), path("*.bcf")` | `tuple` | `bcf` | n/a |
| `val(meta), path("*.frq")` | `tuple` | `frq` | n/a |
| `val(meta), path("*.frq.count")` | `tuple` | `frq_count` | n/a |
| `val(meta), path("*.idepth")` | `tuple` | `idepth` | n/a |
| `val(meta), path("*.ldepth")` | `tuple` | `ldepth` | n/a |
| `val(meta), path("*.ldepth.mean")` | `tuple` | `ldepth_mean` | n/a |
| `val(meta), path("*.gdepth")` | `tuple` | `gdepth` | n/a |
| `val(meta), path("*.hap.ld")` | `tuple` | `hap_ld` | n/a |
| `val(meta), path("*.geno.ld")` | `tuple` | `geno_ld` | n/a |
| `val(meta), path("*.geno.chisq")` | `tuple` | `geno_chisq` | n/a |
| `val(meta), path("*.list.hap.ld")` | `tuple` | `list_hap_ld` | n/a |
| `val(meta), path("*.list.geno.ld")` | `tuple` | `list_geno_ld` | n/a |
| `val(meta), path("*.interchrom.hap.ld")` | `tuple` | `interchrom_hap_ld` | n/a |
| `val(meta), path("*.interchrom.geno.ld")` | `tuple` | `interchrom_geno_ld` | n/a |
| `val(meta), path("*.TsTv")` | `tuple` | `tstv` | n/a |
| `val(meta), path("*.TsTv.summary")` | `tuple` | `tstv_summary` | n/a |
| `val(meta), path("*.TsTv.count")` | `tuple` | `tstv_count` | n/a |
| `val(meta), path("*.TsTv.qual")` | `tuple` | `tstv_qual` | n/a |
| `val(meta), path("*.FILTER.summary")` | `tuple` | `filter_summary` | n/a |
| `val(meta), path("*.sites.pi")` | `tuple` | `sites_pi` | n/a |
| `val(meta), path("*.windowed.pi")` | `tuple` | `windowed_pi` | n/a |
| `val(meta), path("*.weir.fst")` | `tuple` | `weir_fst` | n/a |
| `val(meta), path("*.het")` | `tuple` | `heterozygosity` | n/a |
| `val(meta), path("*.hwe")` | `tuple` | `hwe` | n/a |
| `val(meta), path("*.Tajima.D")` | `tuple` | `tajima_d` | n/a |
| `val(meta), path("*.ifreqburden")` | `tuple` | `freq_burden` | n/a |
| `val(meta), path("*.LROH")` | `tuple` | `lroh` | n/a |
| `val(meta), path("*.relatedness")` | `tuple` | `relatedness` | n/a |
| `val(meta), path("*.relatedness2")` | `tuple` | `relatedness2` | n/a |
| `val(meta), path("*.lqual")` | `tuple` | `lqual` | n/a |
| `val(meta), path("*.imiss")` | `tuple` | `missing_individual` | n/a |
| `val(meta), path("*.lmiss")` | `tuple` | `missing_site` | n/a |
| `val(meta), path("*.snpden")` | `tuple` | `snp_density` | n/a |
| `val(meta), path("*.kept.sites")` | `tuple` | `kept_sites` | n/a |
| `val(meta), path("*.removed.sites")` | `tuple` | `removed_sites` | n/a |
| `val(meta), path("*.singletons")` | `tuple` | `singeltons` | n/a |
| `val(meta), path("*.indel.hist")` | `tuple` | `indel_hist` | n/a |
| `val(meta), path("*.hapcount")` | `tuple` | `hapcount` | n/a |
| `val(meta), path("*.mendel")` | `tuple` | `mendel` | n/a |
| `val(meta), path("*.FORMAT")` | `tuple` | `format` | n/a |
| `val(meta), path("*.INFO")` | `tuple` | `info` | n/a |
| `val(meta), path("*.012")` | `tuple` | `genotypes_matrix` | n/a |
| `val(meta), path("*.012.indv")` | `tuple` | `genotypes_matrix_individual` | n/a |
| `val(meta), path("*.012.pos")` | `tuple` | `genotypes_matrix_position` | n/a |
| `val(meta), path("*.impute.hap")` | `tuple` | `impute_hap` | n/a |
| `val(meta), path("*.impute.hap.legend")` | `tuple` | `impute_hap_legend` | n/a |
| `val(meta), path("*.impute.hap.indv")` | `tuple` | `impute_hap_indv` | n/a |
| `val(meta), path("*.ldhat.sites")` | `tuple` | `ldhat_sites` | n/a |
| `val(meta), path("*.ldhat.locs")` | `tuple` | `ldhat_locs` | n/a |
| `val(meta), path("*.BEAGLE.GL")` | `tuple` | `beagle_gl` | n/a |
| `val(meta), path("*.BEAGLE.PL")` | `tuple` | `beagle_pl` | n/a |
| `val(meta), path("*.ped")` | `tuple` | `ped` | n/a |
| `val(meta), path("*.map")` | `tuple` | `map_` | n/a |
| `val(meta), path("*.tped")` | `tuple` | `tped` | n/a |
| `val(meta), path("*.tfam")` | `tuple` | `tfam` | n/a |
| `val(meta), path("*.diff.sites_in_files")` | `tuple` | `diff_sites_in_files` | n/a |
| `val(meta), path("*.diff.indv_in_files")` | `tuple` | `diff_indv_in_files` | n/a |
| `val(meta), path("*.diff.sites")` | `tuple` | `diff_sites` | n/a |
| `val(meta), path("*.diff.indv")` | `tuple` | `diff_indv` | n/a |
| `val(meta), path("*.diff.discordance.matrix")` | `tuple` | `diff_discd_matrix` | n/a |
| `val(meta), path("*.diff.switch")` | `tuple` | `diff_switch_error` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

### `UNZIP` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `archive` | `file` | ZIP file |

### `UNZIP` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `unzipped_archive` | `directory` | `${archive.baseName}/` | Directory contents of the unzipped archive |

### `YTE` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. `[ id:'template1' ]` |
| `template` | `file` | YTE template |
| `map_file` | `file` | YAML file containing a map to be used in the template |
| `map` | `map` | Groovy Map containing mapping information to be used in the template e.g. `[ key: value ]` with key being a wildcard in the template |

### `YTE` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `rendered` | `file` | `*.yaml` | Rendered YAML file |

### `GAWK` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `input` | `file` | The input file - Specify the logic that needs to be executed on this file on the `ext.args2` or in the program file. If the files have a `.gz` extension, they will be unzipped using `zcat`. |
| `program_file` | `file` | Optional file containing logic for awk to execute. If you don't wish to use a file, you can use `ext.args2` to specify the logic. |
| `disable_redirect_output` | `boolean` | Disable the redirection of awk output to a given file. This is useful if you want to use awk's built-in redirect to write files instead of the shell's redirect. |

### `GAWK` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta)` | `tuple` | n/a | n/a |

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

### `ASCAT` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `input_normal` | `file` | BAM/CRAM file, must adhere to chr1, chr2, ...chrX notation For modifying chromosome notation in bam files please follow https://josephcckuo.wordpress.com/2016/11/17/modify-chromosome-notation-in-bam-file/. |
| `index_normal` | `file` | index for normal_bam/cram |
| `input_tumor` | `file` | BAM/CRAM file, must adhere to chr1, chr2, ...chrX notation |
| `index_tumor` | `file` | index for tumor_bam/cram |
| `allele_files` | `file` | allele files for ASCAT WGS. Can be downloaded here https://github.com/VanLoo-lab/ascat/tree/master/ReferenceFiles/WGS |
| `loci_files` | `file` | loci files for ASCAT WGS. Loci files without chromosome notation can be downloaded here https://github.com/VanLoo-lab/ascat/tree/master/ReferenceFiles/WGS Make sure the chromosome notation matches the bam/cram input files. To add the chromosome notation to loci files (hg19/hg38) if necessary, you can run this command `if [[ $(samtools view <your_bam_file.bam> \| head -n1 \| cut -f3)\" == *\"chr\"* ]]; then for i in {1..22} X; do sed -i 's/^/chr/' G1000_loci_hg19_chr_${i}.txt; done; fi` |
| `bed_file` | `file` | Bed file for ASCAT WES (optional, but recommended for WES) |
| `fasta` | `file` | Reference fasta file (optional) |
| `gc_file` | `file` | GC correction file (optional) - Used to do logR correction of the tumour sample(s) with genomic GC content |
| `rt_file` | `file` | replication timing correction file (optional, provide only in combination with gc_file) |

### `ASCAT` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*alleleFrequencies_chr*.txt")` | `tuple` | `allelefreqs` | n/a |
| `val(meta), path("*BAF.txt")` | `tuple` | `bafs` | n/a |
| `val(meta), path("*cnvs.txt")` | `tuple` | `cnvs` | n/a |
| `val(meta), path("*LogR.txt")` | `tuple` | `logrs` | n/a |
| `val(meta), path("*metrics.txt")` | `tuple` | `metrics` | n/a |
| `val(meta), path("*png")` | `tuple` | `png` | n/a |
| `val(meta), path("*purityploidy.txt")` | `tuple` | `purityploidy` | n/a |
| `val(meta), path("*segments.txt")` | `tuple` | `segments` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

### `FREEBAYES` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `input_1` | `file` | BAM/CRAM/SAM file |
| `input_1_index` | `file` | BAM/CRAM/SAM index file |
| `input_2` | `file` | BAM/CRAM/SAM file |
| `input_2_index` | `file` | BAM/CRAM/SAM index file |
| `target_bed` | `file` | Optional - Limit analysis to targets listed in this BED-format FILE. |
| `meta2` | `map` | Groovy Map containing reference information. e.g. [ id:'test_reference' ] |
| `fasta` | `file` | reference fasta file |
| `meta3` | `map` | Groovy Map containing reference information. e.g. [ id:'test_reference' ] |
| `fasta_fai` | `file` | reference fasta file index |
| `meta4` | `map` | Groovy Map containing meta information for the samples file. e.g. [ id:'test_samples' ] |
| `samples` | `file` | Optional - Limit analysis to samples listed (one per line) in the FILE. |
| `meta5` | `map` | Groovy Map containing meta information for the populations file. e.g. [ id:'test_populations' ] |
| `populations` | `file` | Optional - Each line of FILE should list a sample and a population which it is part of. |
| `meta6` | `map` | Groovy Map containing meta information for the cnv file. e.g. [ id:'test_cnv' ] |
| `cnv` | `file` | A copy number map BED file, which has either a sample-level ploidy: sample_name copy_number or a region-specific format: seq_name start end sample_name copy_number |

### `FREEBAYES` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `vcf` | `file` | `*.vcf.gz` | Compressed VCF file |

### `FASTP` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information. Use 'single_end: true' to specify single ended or interleaved FASTQs. Use 'single_end: false' for paired-end reads. e.g. [ id:'test', single_end:false ] |
| `reads` | `file` | List of input FastQ files of size 1 and 2 for single-end and paired-end data, respectively. If you wish to run interleaved paired-end data,  supply as single-end data but with `--interleaved_in` in your `modules.conf`'s `ext.args` for the module. |
| `adapter_fasta` | `file` | File in FASTA format containing possible adapters to remove. |
| `discard_trimmed_pass` | `boolean` | Specify true to not write any reads that pass trimming thresholds. This can be used to use fastp for the output report only. |
| `save_trimmed_fail` | `boolean` | Specify true to save files that failed to pass trimming thresholds ending in `*.fail.fastq.gz` |
| `save_merged` | `boolean` | Specify true to save all merged reads to a file ending in `*.merged.fastq.gz` |

### `FASTP` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path('*.fastp.fastq.gz')` | `tuple` | `reads` | n/a |
| `val(meta), path('*.json')` | `tuple` | `json` | n/a |
| `val(meta), path('*.html')` | `tuple` | `html` | n/a |
| `val(meta), path('*.log')` | `tuple` | `log` | n/a |
| `val(meta), path('*.fail.fastq.gz')` | `tuple` | `reads_fail` | n/a |
| `val(meta), path('*.merged.fastq.gz')` | `tuple` | `reads_merged` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

### `GUNZIP` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Optional groovy Map containing meta information e.g. [ id:'test', single_end:false ] |
| `archive` | `file` | File to be compressed/uncompressed |

### `GUNZIP` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta)` | `tuple` | n/a | n/a |

### `SPRING_DECOMPRESS` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `spring` | `file` | Spring file to decompress. |
| `write_one_fastq_gz` | `boolean` | Controls whether spring should write one fastq.gz file with reads from both directions or two fastq.gz files with reads from distinct directions |

### `SPRING_DECOMPRESS` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*.fastq.gz")` | `tuple` | `fastq` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

### `LOFREQ_CALLPARALLEL` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test' ] |
| `bam` | `file` | Tumor sample sorted BAM file |
| `bai` | `file` | BAM index file |
| `intervals` | `file` | BED file containing target regions for variant calling |
| `meta2` | `map` | Groovy Map containing sample information about the reference fasta e.g. [ id:'reference' ] |
| `fasta` | `file` | Reference genome FASTA file |
| `meta3` | `map` | Groovy Map containing sample information about the reference fasta fai e.g. [ id:'reference' ] |
| `fai` | `file` | Reference genome FASTA index file |

### `LOFREQ_CALLPARALLEL` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*.vcf.gz")` | `tuple` | `vcf` | n/a |
| `val(meta), path("*.vcf.gz.tbi")` | `tuple` | `tbi` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

### `GATK4_INTERVALLISTTOBED` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `intervals` | `file` | IntervalList file |

### `GATK4_INTERVALLISTTOBED` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta)` | `tuple` | n/a | n/a |

### `GATK4_CALCULATECONTAMINATION` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test' ] |
| `pileup` | `file` | File containing the pileups summary table of a tumor sample to be used to calculate contamination. |
| `matched` | `file` | File containing the pileups summary table of a normal sample that matches with the tumor sample specified in pileup argument. This is an optional input. |

### `GATK4_CALCULATECONTAMINATION` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path('*.contamination.table')` | `tuple` | `contamination` | n/a |
| `val(meta), path('*.segmentation.table')` | `tuple` | `segmentation` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

### `GATK4_FILTERMUTECTCALLS` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test' ] |
| `vcf` | `file` | compressed vcf file of mutect2calls |
| `vcf_tbi` | `file` | Tabix index of vcf file |
| `stats` | `file` | Stats file that pairs with output vcf file |
| `orientationbias` | `file` | files containing artifact priors for input vcf. Optional input. |
| `segmentation` | `file` | tables containing segmentation information for input vcf. Optional input. |
| `table` | `file` | table(s) containing contamination data for input vcf. Optional input, takes priority over estimate. |
| `estimate` | `float` | estimation of contamination value as a double. Optional input, will only be used if table is not specified. |
| `meta2` | `map` | Groovy Map containing reference information e.g. [ id:'genome' ] |
| `fasta` | `file` | The reference fasta file |
| `meta3` | `map` | Groovy Map containing reference information e.g. [ id:'genome' ] |
| `fai` | `file` | Index of reference fasta file |
| `meta4` | `map` | Groovy Map containing reference information e.g. [ id:'genome' ] |
| `dict` | `file` | GATK sequence dictionary |

### `GATK4_FILTERMUTECTCALLS` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*.vcf.gz")` | `tuple` | `vcf` | n/a |
| `val(meta), path("*.vcf.gz.tbi")` | `tuple` | `tbi` | n/a |
| `val(meta), path("*.filteringStats.tsv")` | `tuple` | `stats` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

### `GATK4_APPLYVQSR` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test'] |
| `vcf` | `file` | VCF file to be recalibrated, this should be the same file as used for the first stage VariantRecalibrator. |
| `vcf_tbi` | `file` | tabix index for the input vcf file. |
| `recal` | `file` | Recalibration file produced when the input vcf was run through VariantRecalibrator in stage 1. |
| `recal_index` | `file` | Index file for the recalibration file. |
| `tranches` | `file` | Tranches file produced when the input vcf was run through VariantRecalibrator in stage 1. |
| `fasta` | `file` | The reference fasta file |
| `fai` | `file` | Index of reference fasta file |
| `dict` | `file` | GATK sequence dictionary |

### `GATK4_APPLYVQSR` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*.vcf.gz")` | `tuple` | `vcf` | n/a |
| `val(meta), path("*.tbi")` | `tuple` | `tbi` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

### `GATK4_GENOMICSDBIMPORT` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test'] |
| `vcf` | `list` | either a list of vcf files to be used to create or update a genomicsdb, or a file that contains a map to vcf files to be used. |
| `tbi` | `list` | list of tbi files that match with the input vcf files |
| `interval_file` | `file` | file containing the intervals to be used when creating the genomicsdb |
| `interval_value` | `string` | if an intervals file has not been specified, the value entered here will be used as an interval via the "-L" argument |
| `wspace` | `file` | path to an existing genomicsdb to be used in update db mode or get intervals mode. This WILL NOT specify name of a new genomicsdb in create db mode. |
| `run_intlist` | `boolean` | Specify whether to run get interval list mode, this option cannot be specified at the same time as run_updatewspace. |
| `run_updatewspace` | `boolean` | Specify whether to run update genomicsdb mode, this option takes priority over run_intlist. |
| `input_map` | `boolean` | Specify whether the vcf input is providing a list of vcf file(s) or a single file containing a map of paths to vcf files to be used to create or update a genomicsdb. |

### `GATK4_GENOMICSDBIMPORT` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta)` | `tuple` | n/a | n/a |

### `GATK4_LEARNREADORIENTATIONMODEL` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test' ] |
| `f1r2` | `list` | list of f1r2 files to be used as input. |

### `GATK4_LEARNREADORIENTATIONMODEL` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*.tar.gz")` | `tuple` | `artifactprior` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

### `GATK4_VARIANTRECALIBRATOR` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test' ] |
| `vcf` | `file` | input vcf file containing the variants to be recalibrated |
| `tbi` | `file` | tbi file matching with -vcf |
| `resource_vcf` | `file` | all resource vcf files that are used with the corresponding '--resource' label |
| `resource_tbi` | `file` | all resource tbi files that are used with the corresponding '--resource' label |
| `labels` | `string` | necessary arguments for GATK VariantRecalibrator. Specified to directly match the resources provided. More information can be found at https://gatk.broadinstitute.org/hc/en-us/articles/5358906115227-VariantRecalibrator |
| `fasta` | `file` | The reference fasta file |
| `fai` | `file` | Index of reference fasta file |
| `dict` | `file` | GATK sequence dictionary |

### `GATK4_VARIANTRECALIBRATOR` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*.recal")` | `tuple` | `recal` | n/a |
| `val(meta), path("*.idx")` | `tuple` | `idx` | n/a |
| `val(meta), path("*.tranches")` | `tuple` | `tranches` | n/a |
| `val(meta), path("*plots.R")` | `tuple` | `plots` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

### `GATK4_GATHERBQSRREPORTS` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `table` | `file` | File(s) containing BQSR table(s) |

### `GATK4_GATHERBQSRREPORTS` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*.table")` | `tuple` | `table` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

### `GATK4_GETPILEUPSUMMARIES` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test' ] |
| `input` | `file` | BAM/CRAM file to be summarised. |
| `index` | `file` | Index file for the input BAM/CRAM file. |
| `intervals` | `file` | File containing specified sites to be used for the summary. If this option is not specified, variants file is used instead automatically. |
| `meta2` | `map` | Groovy Map containing reference information e.g. [ id:'genome' ] |
| `fasta` | `file` | The reference fasta file |
| `meta3` | `map` | Groovy Map containing reference information e.g. [ id:'genome' ] |
| `fai` | `file` | Index of reference fasta file |
| `meta4` | `map` | Groovy Map containing reference information e.g. [ id:'genome' ] |
| `dict` | `file` | GATK sequence dictionary |
| `variants` | `file` | Population vcf of germline sequencing, containing allele fractions. Is also used as sites file if no separate sites file is specified. |
| `variants_tbi` | `file` | Index file for the germline resource. |

### `GATK4_GETPILEUPSUMMARIES` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path('*.pileups.table')` | `tuple` | `table` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

### `GATK4_GENOTYPEGVCFS` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `input` | `file` | gVCF(.gz) file or a GenomicsDB |
| `gvcf_index` | `file` | index of gvcf file, or empty when providing GenomicsDB |
| `intervals` | `file` | Interval file with the genomic regions included in the library (optional) |
| `intervals_index` | `file` | Interval index file (optional) |
| `meta2` | `map` | Groovy Map containing fasta information e.g. [ id:'test' ] |
| `fasta` | `file` | Reference fasta file |
| `meta3` | `map` | Groovy Map containing fai information e.g. [ id:'test' ] |
| `fai` | `file` | Reference fasta index file |
| `meta4` | `map` | Groovy Map containing dict information e.g. [ id:'test' ] |
| `dict` | `file` | Reference fasta sequence dict file |
| `meta5` | `map` | Groovy Map containing dbsnp information e.g. [ id:'test' ] |
| `dbsnp` | `file` | dbSNP VCF file |
| `meta6` | `map` | Groovy Map containing dbsnp tbi information e.g. [ id:'test' ] |
| `dbsnp_tbi` | `file` | dbSNP VCF index file |

### `GATK4_GENOTYPEGVCFS` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*.vcf.gz")` | `tuple` | `vcf` | n/a |
| `val(meta), path("*.tbi")` | `tuple` | `tbi` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

### `GATK4_CREATESEQUENCEDICTIONARY` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing reference information e.g. [ id:'genome' ] |
| `fasta` | `file` | Input fasta file |

### `GATK4_CREATESEQUENCEDICTIONARY` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `dict` | `file` | `*.{dict}` | gatk dictionary file |

### `GATK4_GATHERPILEUPSUMMARIES` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `pileup` | `file` | Pileup files from gatk4/getpileupsummaries |
| `dict` | `file` | dictionary |

### `GATK4_GATHERPILEUPSUMMARIES` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*.pileups.table")` | `tuple` | `table` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

### `GATK4_ESTIMATELIBRARYCOMPLEXITY` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `input` | `file` | BAM/CRAM/SAM file |
| `fasta` | `file` | The reference fasta file |
| `fai` | `file` | Index of reference fasta file |
| `dict` | `file` | GATK sequence dictionary |

### `GATK4_ESTIMATELIBRARYCOMPLEXITY` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path('*.metrics')` | `tuple` | `metrics` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

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

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*.vcf.gz")` | `tuple` | `vcf` | n/a |
| `val(meta), path("*.tbi")` | `tuple` | `tbi` | n/a |
| `val(meta), path("*.realigned.bam")` | `tuple` | `bam` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

### `GATK4_CNNSCOREVARIANTS` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `vcf` | `file` | VCF file |
| `tbi` | `file` | VCF index file |
| `aligned_input` | `file` | BAM/CRAM file from alignment (optional) |
| `intervals` | `file` | Bed file with the genomic regions included in the library (optional) |
| `fasta` | `file` | The reference fasta file |
| `fai` | `file` | Index of reference fasta file |
| `dict` | `file` | GATK sequence dictionary |
| `architecture` | `file` | Neural Net architecture configuration json file (optional) |
| `weights` | `file` | Keras model HD5 file with neural net weights. (optional) |

### `GATK4_CNNSCOREVARIANTS` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*cnn.vcf.gz")` | `tuple` | `vcf` | n/a |
| `val(meta), path("*cnn.vcf.gz.tbi")` | `tuple` | `tbi` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

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
| `known_sites` | `file` | VCF files with known sites for indels / snps (optional) |
| `meta6` | `map` | Groovy Map containing reference information e.g. [ id:'genome'] |
| `known_sites_tbi` | `file` | Tabix index of the known_sites (optional) |

### `GATK4_BASERECALIBRATOR` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*.table")` | `tuple` | `table` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

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

### `GATK4_MERGEVCFS` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test'] |
| `vcf` | `list` | Two or more VCF files |
| `meta2` | `map` | Groovy Map containing reference information e.g. [ id:'genome'] |
| `dict` | `file` | Optional Sequence Dictionary as input |

### `GATK4_MERGEVCFS` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path('*.vcf.gz')` | `tuple` | `vcf` | n/a |
| `val(meta), path("*.tbi")` | `tuple` | `tbi` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

### `GATK4_FILTERVARIANTTRANCHES` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `vcf` | `file` | a VCF file containing variants, must have info key:CNN_2D |
| `tbi` | `file` | tbi file matching with -vcf |
| `intervals` | `file` | Intervals |
| `resources` | `list` | resource A VCF containing known SNP and or INDEL sites. Can be supplied as many times as necessary |
| `resources_index` | `list` | Index of resource VCF containing known SNP and or INDEL sites. Can be supplied as many times as necessary |
| `fasta` | `file` | The reference fasta file |
| `fai` | `file` | Index of reference fasta file |
| `dict` | `file` | GATK sequence dictionary |

### `GATK4_FILTERVARIANTTRANCHES` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*.vcf.gz")` | `tuple` | `vcf` | n/a |
| `val(meta), path("*.vcf.gz.tbi")` | `tuple` | `tbi` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

### `GATK4_MARKDUPLICATES` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `bam` | `file` | Sorted BAM file |
| `fasta` | `file` | Fasta file |
| `fasta_fai` | `file` | Fasta index file |

### `GATK4_MARKDUPLICATES` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*cram")` | `tuple` | `cram` | n/a |
| `val(meta), path("*bam")` | `tuple` | `bam` | n/a |
| `val(meta), path("*.crai")` | `tuple` | `crai` | n/a |
| `val(meta), path("*.bai")` | `tuple` | `bai` | n/a |
| `val(meta), path("*.metrics")` | `tuple` | `metrics` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

### `GATK4_MUTECT2` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test'] |
| `input` | `list` | list of BAM files, also able to take CRAM as an input |
| `input_index` | `list` | list of BAM file indexes, also able to take CRAM indexes as an input |
| `intervals` | `file` | Specify region the tools is run on. |
| `meta2` | `map` | Groovy Map containing reference information e.g. [ id:'genome' ] |
| `fasta` | `file` | The reference fasta file |
| `meta3` | `map` | Groovy Map containing reference information e.g. [ id:'genome' ] |
| `fai` | `file` | Index of reference fasta file |
| `meta4` | `map` | Groovy Map containing reference information e.g. [ id:'genome' ] |
| `dict` | `file` | GATK sequence dictionary |
| `germline_resource` | `file` | Population vcf of germline sequencing, containing allele fractions. |
| `germline_resource_tbi` | `file` | Index file for the germline resource. |
| `panel_of_normals` | `file` | vcf file to be used as a panel of normals. |
| `panel_of_normals_tbi` | `file` | Index for the panel of normals. |

### `GATK4_MUTECT2` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*.vcf.gz")` | `tuple` | `vcf` | n/a |
| `val(meta), path("*.tbi")` | `tuple` | `tbi` | n/a |
| `val(meta), path("*.stats")` | `tuple` | `stats` | n/a |
| `val(meta), path("*.f1r2.tar.gz")` | `tuple` | `f1r2` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

### `GATK4_MERGEMUTECTSTATS` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `stats` | `file` | Stats file |

### `GATK4_MERGEMUTECTSTATS` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*.vcf.gz.stats")` | `tuple` | `stats` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

### `GATK4SPARK_BASERECALIBRATOR` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `input` | `file` | BAM/CRAM file from alignment |
| `input_index` | `file` | BAI/CRAI file from alignment |
| `intervals` | `file` | Bed file with the genomic regions included in the library (optional) |
| `fasta` | `file` | The reference fasta file |
| `fai` | `file` | Index of reference fasta file |
| `dict` | `file` | GATK sequence dictionary |
| `known_sites` | `file` | VCF files with known sites for indels / snps (optional) |
| `known_sites_tbi` | `file` | Tabix index of the known_sites (optional) |

### `GATK4SPARK_BASERECALIBRATOR` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*.table")` | `tuple` | `table` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

### `GATK4SPARK_APPLYBQSR` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `input` | `file` | BAM/CRAM file from alignment |
| `input_index` | `file` | BAI/CRAI file from alignment |
| `bqsr_table` | `file` | Recalibration table from gatk4_baserecalibrator |
| `intervals` | `file` | Bed file with the genomic regions included in the library (optional) |

### `GATK4SPARK_APPLYBQSR` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `bam` | `file` | `${prefix}.bam` | Recalibrated BAM file |
| `bai` | `file` | `${prefix}*bai` | Recalibrated BAM index file |
| `cram` | `file` | `${prefix}.cram` | Recalibrated CRAM file |

### `GATK4SPARK_MARKDUPLICATES` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `bam` | `file` | Sorted BAM file |
| `fasta` | `file` | The reference fasta file |
| `fasta_fai` | `file` | Index of reference fasta file |
| `dict` | `file` | GATK sequence dictionary |

### `GATK4SPARK_MARKDUPLICATES` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta)` | `tuple` | n/a | n/a |

### `DEEPVARIANT_RUNDEEPVARIANT` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `input` | `file` | BAM/CRAM file |
| `index` | `file` | Index of BAM/CRAM file |
| `intervals` | `file` | file containing intervals |
| `meta2` | `map` | Groovy Map containing reference information e.g. [ id:'genome' ] |
| `fasta` | `file` | The reference fasta file |
| `meta3` | `map` | Groovy Map containing reference information e.g. [ id:'genome' ] |
| `fai` | `file` | Index of reference fasta file |
| `meta4` | `map` | Groovy Map containing reference information e.g. [ id:'genome' ] |
| `gzi` | `file` | GZI index of reference fasta file |
| `meta5` | `map` | Groovy Map containing reference information e.g. [ id:'genome' ] |
| `par_bed` | `file` | BED file containing PAR regions |

### `DEEPVARIANT_RUNDEEPVARIANT` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `vcf` | `file` | `*.vcf.gz` | Compressed VCF file |
| `vcf_index` | `file` | `*.vcf.gz.{tbi,csi}` | Tabix index file of compressed VCF |
| `gvcf` | `file` | `*.g.vcf.gz` | Compressed GVCF file |
| `gvcf_index` | `file` | `*.g.vcf.gz.{tbi,csi}` | Tabix index file of compressed GVCF |

### `SENTIEON_GVCFTYPER` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `gvcfs` | `file` | gVCF(.gz) file |
| `tbis` | `file` | index of gvcf file |
| `intervals` | `file` | Interval file with the genomic regions included in the library (optional) |
| `meta1` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `fasta` | `file` | Reference fasta file |
| `meta2` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `fai` | `file` | Reference fasta index file |
| `meta3` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `dbsnp` | `file` | dbSNP VCF file |
| `meta4` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `dbsnp_tbi` | `file` | dbSNP VCF index file |

### `SENTIEON_GVCFTYPER` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `vcf_gz` | `file` | `*.vcf.gz` | VCF file |
| `vcf_gz_tbi` | `file` | `*.vcf.gz.tbi` | VCF index file |

### `SENTIEON_TNSCOPE` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information. e.g. [ id:'test' ] |
| `input` | `file` | One or more BAM or CRAM files. |
| `input_index` | `file` | Indices for the input files |
| `intervals` | `file` | bed or interval_list file containing interval in the reference that will be used in the analysis. Only recommended for large WGS data, else the overhead may not be worth the additional parallelisation. |
| `meta2` | `map` | Groovy Map containing reference information. e.g. [ id:'test' ] |
| `fasta` | `file` | Genome fasta file |
| `meta3` | `map` | Groovy Map containing reference information. e.g. [ id:'test' ] |
| `fai` | `file` | Index of the genome fasta file |
| `meta4` | `map` | Groovy Map containing reference information. e.g. [ id:'test' ] |
| `dbsnp` | `file` | Single Nucleotide Polymorphism database (dbSNP) file |
| `meta5` | `map` | Groovy Map containing reference information. e.g. [ id:'test' ] |
| `dbsnp_tbi` | `file` | Index of the Single Nucleotide Polymorphism database (dbSNP) file |
| `meta6` | `map` | Groovy Map containing reference information. e.g. [ id:'test' ] |
| `pon` | `file` | Single Nucleotide Polymorphism database (dbSNP) file |
| `meta7` | `map` | Groovy Map containing reference information. e.g. [ id:'test' ] |
| `pon_tbi` | `file` | Index of the Single Nucleotide Polymorphism database (dbSNP) file |
| `meta8` | `map` | Groovy Map containing reference information. e.g. [ id:'test' ] |
| `cosmic` | `file` | Catalogue of Somatic Mutations in Cancer (COSMIC) VCF file. |
| `meta9` | `map` | Groovy Map containing reference information. e.g. [ id:'test' ] |
| `cosmic_tbi` | `file` | Index of the Catalogue of Somatic Mutations in Cancer (COSMIC) VCF file. |

### `SENTIEON_TNSCOPE` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `vcf` | `file` | `*.{vcf.gz}` | VCF file |
| `index` | `file` | `*.vcf.gz.tbi` | Index of the VCF file |

### `SENTIEON_DNAMODELAPPLY` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. `[ id:'test', single_end:false ]` |
| `vcf` | `file` | INPUT VCF file |
| `idx` | `file` | Index of the input VCF file |
| `meta2` | `map` | Groovy Map containing reference information e.g. `[ id:'test' ]` |
| `fasta` | `file` | Genome fasta file |
| `meta3` | `map` | Groovy Map containing reference information e.g. `[ id:'test' ]` |
| `fai` | `file` | Index of the genome fasta file |
| `meta4` | `map` | Groovy Map containing reference information e.g. `[ id:'test' ]` |
| `ml_model` | `file` | machine learning model file |

### `SENTIEON_DNAMODELAPPLY` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `vcf` | `file` | `*.{vcf,vcf.gz}` | INPUT VCF file |
| `tbi` | `file` | `*.{tbi}` | Index of the input VCF file |

### `SENTIEON_BWAMEM` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing reference information. e.g. [ id:'test', single_end:false ] |
| `reads` | `file` | Genome fastq files (single-end or paired-end) |
| `meta2` | `map` | Groovy Map containing reference information. e.g. [ id:'test', single_end:false ] |
| `index` | `file` | BWA genome index files |
| `meta3` | `map` | Groovy Map containing reference information. e.g. [ id:'test', single_end:false ] |
| `fasta` | `file` | Genome fasta file |
| `meta4` | `map` | Groovy Map containing reference information. e.g. [ id:'test', single_end:false ] |
| `fasta_fai` | `file` | The index of the FASTA reference. |

### `SENTIEON_BWAMEM` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `bam_and_bai` | `file` | `*.{bam,bai}, *.{bam,bai}` | BAM file with corresponding index. BAM file with corresponding index. |

### `SENTIEON_APPLYVARCAL` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test'] |
| `vcf` | `file` | VCF file to be recalibrated, this should be the same file as used for the first stage VariantRecalibrator. |
| `vcf_tbi` | `file` | tabix index for the input vcf file. |
| `recal` | `file` | Recalibration file produced when the input vcf was run through VariantRecalibrator in stage 1. |
| `recal_index` | `file` | Index file for the recalibration file. |
| `tranches` | `file` | Tranches file produced when the input vcf was run through VariantRecalibrator in stage 1. |
| `meta2` | `map` | Groovy Map containing sample information e.g. [ id:'test'] |
| `fasta` | `file` | The reference fasta file |
| `meta3` | `map` | Groovy Map containing sample information e.g. [ id:'test'] |
| `fai` | `file` | Index of reference fasta file |

### `SENTIEON_APPLYVARCAL` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `vcf` | `file` | `*.vcf.gz` | compressed vcf file containing the recalibrated variants. |
| `tbi` | `file` | `*vcf.gz.tbi` | Index of recalibrated vcf file. |

### `SENTIEON_VARCAL` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test' ] |
| `vcf` | `file` | input vcf file containing the variants to be recalibrated |
| `tbi` | `file` | tbi file matching with -vcf |

### `SENTIEON_VARCAL` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `recal` | `file` | `*.recal` | Output recal file used by ApplyVQSR |
| `idx` | `file` | `*.idx` | Index file for the recal output file |
| `tranches` | `file` | `*.tranches` | Output tranches file used by ApplyVQSR |
| `plots` | `file` | `*plots.R` | Optional output rscript file to aid in visualization of the input data and learned model. |

### `SENTIEON_DNASCOPE` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information. e.g. [ id:'test', single_end:false ] |
| `bam` | `file` | BAM file. |
| `bai` | `file` | BAI file |
| `intervals` | `file` | bed or interval_list file containing interval in the reference that will be used in the analysis |
| `meta2` | `map` | Groovy Map containing meta information for fasta. |
| `fasta` | `file` | Genome fasta file |
| `meta3` | `map` | Groovy Map containing meta information for fasta index. |
| `fai` | `file` | Index of the genome fasta file |
| `meta4` | `map` | Groovy Map containing meta information for dbsnp. |
| `dbsnp` | `file` | Single Nucleotide Polymorphism database (dbSNP) file |
| `meta5` | `map` | Groovy Map containing meta information for dbsnp_tbi. |
| `dbsnp_tbi` | `file` | Index of the Single Nucleotide Polymorphism database (dbSNP) file |
| `meta6` | `map` | Groovy Map containing meta information for machine learning model for Dnascope. |
| `ml_model` | `file` | machine learning model file |

### `SENTIEON_DNASCOPE` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `vcf` | `file` | `*.unfiltered.vcf.gz` | Compressed VCF file |
| `vcf_tbi` | `file` | `*.unfiltered.vcf.gz.tbi` | Index of VCF file |
| `gvcf` | `file` | `*.g.vcf.gz` | Compressed GVCF file |
| `gvcf_tbi` | `file` | `*.g.vcf.gz.tbi` | Index of GVCF file |

### `SENTIEON_HAPLOTYPER` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing reference information. e.g. [ id:'test', single_end:false ] |
| `input` | `file` | BAM/CRAM file from alignment |
| `input_index` | `file` | BAI/CRAI file from alignment |
| `intervals` | `file` | Bed file with the genomic regions included in the library (optional) |
| `recal_table` | `file` | Recalibration table from sentieon/qualcal (optional) |
| `meta2` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `fasta` | `file` | Genome fasta file |
| `meta3` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `fai` | `file` | The index of the FASTA reference. |
| `meta4` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `dbsnp` | `file` | VCF file containing known sites (optional) |
| `meta5` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `dbsnp_tbi` | `file` | VCF index of dbsnp (optional) |

### `SENTIEON_HAPLOTYPER` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `vcf` | `file` | `*.unfiltered.vcf.gz` | Compressed VCF file |
| `vcf_tbi` | `file` | `*.unfiltered.vcf.gz.tbi` | Index of VCF file |
| `gvcf` | `file` | `*.g.vcf.gz` | Compressed GVCF file |
| `gvcf_tbi` | `file` | `*.g.vcf.gz.tbi` | Index of GVCF file |

### `SENTIEON_DEDUP` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing reference information. e.g. [ id:'test', single_end:false ] |
| `bam` | `file` | BAM file. |
| `bai` | `file` | BAI file |
| `meta2` | `map` | Groovy Map containing reference information. e.g. [ id:'test', single_end:false ] |
| `fasta` | `file` | Genome fasta file |
| `meta3` | `map` | Groovy Map containing reference information. e.g. [ id:'test', single_end:false ] |
| `fasta_fai` | `file` | The index of the FASTA reference. |

### `SENTIEON_DEDUP` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `cram` | `file` | `*.cram` | CRAM file |
| `crai` | `file` | `*.crai` | CRAM index file |
| `bam` | `file` | `*.bam` | BAM file. |
| `bai` | `file` | `*.bai` | BAI file |
| `score` | `file` | `*.score` | The score file indicates which reads LocusCollector finds are likely duplicates. |
| `metrics` | `file` | `*.metrics` | Output file containing Dedup metrics incl. histogram data. |
| `metrics_multiqc_tsv` | `file` | `*.metrics.multiqc.tsv` | Output tsv-file containing Dedup metrics excl. histogram data. |

### `SAMTOOLS_BAM2FQ` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `inputbam` | `file` | BAM/CRAM/SAM file |
| `split` | `boolean` | TRUE/FALSE value to indicate if reads should be separated into /1, /2 and if present other, or singleton. Note: choosing TRUE will generate 4 different files. Choosing FALSE will produce a single file, which will be interleaved in case the input contains paired reads. |

### `SAMTOOLS_BAM2FQ` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*.fq.gz")` | `tuple` | `reads` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

### `SAMTOOLS_MERGE` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `input_files` | `file` | BAM/CRAM file |
| `meta2` | `map` | Groovy Map containing reference information e.g. [ id:'genome' ] |
| `fasta` | `file` | Reference file the CRAM was created with (optional) |
| `meta3` | `map` | Groovy Map containing reference information e.g. [ id:'genome' ] |
| `fai` | `file` | Index of the reference file the CRAM was created with (optional) |

### `SAMTOOLS_MERGE` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta)` | `tuple` | n/a | n/a |

### `SAMTOOLS_MPILEUP` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test' ] |
| `input` | `file` | BAM/CRAM/SAM file |
| `intervals` | `file` | Interval FILE |
| `meta2` | `map` | Groovy Map containing sample information e.g. [ id:'test' ] |
| `fasta` | `file` | FASTA reference file |

### `SAMTOOLS_MPILEUP` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*.mpileup.gz")` | `tuple` | `mpileup` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

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

### `SAMTOOLS_VIEW` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `input` | `file` | BAM/CRAM/SAM file |
| `index` | `file` | BAM.BAI/BAM.CSI/CRAM.CRAI file (optional) |
| `meta2` | `map` | Groovy Map containing reference information e.g. [ id:'test' ] |
| `fasta` | `file` | Reference file the CRAM was created with (optional) |
| `qname` | `file` | Optional file with read names to output only select alignments |
| `index_format` | `string` | Index format, used together with ext.args = '--write-index' |

### `SAMTOOLS_VIEW` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta)` | `tuple` | n/a | n/a |

### `SAMTOOLS_INDEX` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `input` | `file` | input file |

### `SAMTOOLS_INDEX` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*.bai")` | `tuple` | `bai` | n/a |
| `val(meta), path("*.csi")` | `tuple` | `csi` | n/a |
| `val(meta), path("*.crai")` | `tuple` | `crai` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

### `SAMTOOLS_COLLATEFASTQ` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `input` | `file` | BAM/CRAM/SAM file |
| `meta2` | `map` | Groovy Map containing reference information e.g. [ id:'test' ] |
| `fasta` | `file` | Reference genome fasta file |
| `interleave` | `boolean` | If true, the output is a single interleaved paired-end FASTQ If false, the output split paired-end FASTQ |

### `SAMTOOLS_COLLATEFASTQ` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta)` | `tuple` | n/a | n/a |

### `SAMTOOLS_STATS` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `input` | `file` | BAM/CRAM file from alignment |
| `input_index` | `file` | BAI/CRAI file from alignment |
| `meta2` | `map` | Groovy Map containing reference information e.g. [ id:'genome' ] |
| `fasta` | `file` | Reference file the CRAM was created with (optional) |

### `SAMTOOLS_STATS` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*.stats")` | `tuple` | `stats` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

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

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*.bam")` | `tuple` | `bam` | n/a |
| `val(meta), path("*.cram")` | `tuple` | `cram` | n/a |
| `val(meta), path("*.bai")` | `tuple` | `bai` | n/a |
| `val(meta), path("*.crai")` | `tuple` | `crai` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

### `VCFLIB_VCFFILTER` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test_sample_1' ] |
| `vcf` | `file` | VCF file |
| `tbi` | `file` | Index file |

### `VCFLIB_VCFFILTER` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `vcf` | `file` | `*.{vcf.gz}` | Filtered VCF file |

### `BBMAP_BBSPLIT` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `reads` | `file` | List of input FastQ files of size 1 and 2 for single-end and paired-end data, respectively. |
| `other_ref_names` | `list` | List of other reference ids apart from the primary |
| `other_ref_paths` | `list` | Path to other references paths corresponding to "other_ref_names" |

### `BBMAP_BBSPLIT` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `index` | `-` | n/a | n/a |
| `primary_fastq` | `file` | `*primary*fastq.gz` | Output reads that map to the primary reference |
| `all_fastq` | `file` | `*fastq.gz` | All reads mapping to any of the references |
| `stats` | `file` | `*.txt` | Tab-delimited text file containing mapping statistics |
| `log` | `file` | `*.log` | Log file |

### `MSISENSOR2_MSI` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `tumor_bam` | `file` | BAM/CRAM/SAM file |
| `tumor_bam_index` | `file` | BAM/CRAM/SAM index file |
| `meta2` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `models` | `file` | Folder of MSISensor2 models (available from Github or as a product of msisensor2/scan) |

### `MSISENSOR2_MSI` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `msi` | `file` | n/a | MSI classifications as a text file |
| `distribution` | `file` | n/a | Read count distributions of MSI regions |
| `somatic` | `file` | n/a | Somatic MSI regions detected. |

### `CONTROLFREEC_FREEC2BED` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `ratio` | `file` | ratio file generated by FREEC |

### `CONTROLFREEC_FREEC2BED` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `bed` | `file` | `*.bed` | Bed file |

### `CONTROLFREEC_MAKEGRAPH2` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `ratio` | `file` | ratio file generated by FREEC |
| `baf` | `file` | .BAF file generated by FREEC |

### `CONTROLFREEC_MAKEGRAPH2` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `png_baf` | `file` | `*_BAF.png` | Image of BAF plot |
| `png_ratio_log2` | `file` | `*_ratio.log2.png` | Image of ratio log2 plot |
| `png_ratio` | `file` | `*_ratio.png` | Image of ratio plot |

### `CONTROLFREEC_FREEC2CIRCOS` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `ratio` | `file` | ratio file generated by FREEC |

### `CONTROLFREEC_FREEC2CIRCOS` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `circos` | `file` | `*.circos.txt` | Txt file |

### `CONTROLFREEC_FREEC` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `mpileup_normal` | `file` | miniPileup file |
| `mpileup_tumor` | `file` | miniPileup file |
| `cpn_normal` | `file` | Raw copy number profiles (optional) |
| `cpn_tumor` | `file` | Raw copy number profiles (optional) |
| `minipileup_normal` | `file` | miniPileup file from previous run (optional) |
| `minipileup_tumor` | `file` | miniPileup file from previous run (optional) |

### `CONTROLFREEC_FREEC` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `bedgraph` | `file` | `.bedgraph` | Bedgraph format for the UCSC genome browser |
| `control_cpn` | `file` | `*_control.cpn` | files with raw copy number profiles |
| `sample_cpn` | `file` | `*_sample.cpn` | files with raw copy number profiles |
| `gcprofile_cpn` | `file` | `GC_profile.*.cpn` | file with GC-content profile. |
| `BAF` | `file` | `*_BAF.txt` | file B-allele frequencies for each possibly heterozygous SNP position |
| `CNV` | `file` | `*_CNVs` | file with coordinates of predicted copy number alterations. |
| `info` | `file` | `*_info.txt` | parsable file with information about FREEC run |
| `ratio` | `file` | `*_ratio.txt` | file with ratios and predicted copy number alterations for each window |
| `config` | `file` | `config.txt` | Config file used to run Control-FREEC |

### `CONTROLFREEC_ASSESSSIGNIFICANCE` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `cnvs` | `file` | _CNVs file generated by FREEC |
| `ratio` | `file` | ratio file generated by FREEC |

### `CONTROLFREEC_ASSESSSIGNIFICANCE` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `p_value_txt` | `file` | `*.p.value.txt` | CNV file containing p_values for each call |

### `GOLEFT_INDEXCOV` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false] |
| `bams` | `file` | Sorted BAM/CRAM/SAM files |
| `indexes` | `file` | BAI/CRAI files |
| `meta2` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false] |
| `fai` | `file` | FASTA index |

### `GOLEFT_INDEXCOV` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta)` | `tuple` | n/a | n/a |

### `DRAGMAP_ALIGN` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `reads` | `file` | List of input FastQ files of size 1 and 2 for single-end and paired-end data, respectively. |
| `meta2` | `map` | Groovy Map containing reference information e.g. [ id:'test', single_end:false ] |
| `hashmap` | `file` | DRAGMAP hash table |
| `meta3` | `map` | Groovy Map containing reference information e.g. [ id:'genome'] |
| `fasta` | `file` | Genome fasta reference files |
| `sort_bam` | `boolean` | Sort the BAM file |

### `DRAGMAP_ALIGN` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*.sam")` | `tuple` | `sam` | n/a |
| `val(meta), path("*.bam")` | `tuple` | `bam` | n/a |
| `val(meta), path("*.cram")` | `tuple` | `cram` | n/a |
| `val(meta), path("*.crai")` | `tuple` | `crai` | n/a |
| `val(meta), path("*.csi")` | `tuple` | `csi` | n/a |
| `val(meta), path('*.log')` | `tuple` | `log` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

### `DRAGMAP_HASHTABLE` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing reference information e.g. [ id:'test', single_end:false ] |
| `fasta` | `file` | Input genome fasta file |

### `DRAGMAP_HASHTABLE` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `hashmap` | `file` | `*.{cmp,.bin,.txt}` | DRAGMAP hash table |

### `STRELKA_GERMLINE` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test'] |
| `input` | `file` | BAM/CRAM file |
| `input_index` | `file` | BAM/CRAI index file |
| `target_bed` | `file` | BED file containing target regions for variant calling |
| `target_bed_index` | `file` | Index for BED file containing target regions for variant calling |

### `STRELKA_GERMLINE` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `vcf` | `file` | `*.{vcf.gz}` | gzipped germline variant file |
| `vcf_tbi` | `file` | `*.vcf.gz.tbi` | index file for the vcf file |
| `genome_vcf` | `file` | `*_genome.vcf.gz` | variant records and compressed non-variant blocks |
| `genome_vcf_tbi` | `file` | `*_genome.vcf.gz.tbi` | index file for the genome_vcf file |

### `STRELKA_SOMATIC` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `input_normal` | `file` | BAM/CRAM/SAM file |
| `input_index_normal` | `file` | BAM/CRAM/SAM index file |
| `input_tumor` | `file` | BAM/CRAM/SAM file |
| `input_index_tumor` | `file` | BAM/CRAM/SAM index file |
| `manta_candidate_small_indels` | `file` | VCF.gz file |
| `manta_candidate_small_indels_tbi` | `file` | VCF.gz index file |
| `target_bed` | `file` | BED file containing target regions for variant calling |
| `target_bed_index` | `file` | Index for BED file containing target regions for variant calling |

### `STRELKA_SOMATIC` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `vcf_indels` | `file` | `*.{vcf.gz}` | Gzipped VCF file containing variants |
| `vcf_indels_tbi` | `file` | `*.{vcf.gz.tbi}` | Index for gzipped VCF file containing variants |
| `vcf_snvs` | `file` | `*.{vcf.gz}` | Gzipped VCF file containing variants |
| `vcf_snvs_tbi` | `file` | `*.{vcf.gz.tbi}` | Index for gzipped VCF file containing variants |

### `BWA_INDEX` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing reference information. e.g. [ id:'test', single_end:false ] |
| `fasta` | `file` | Input genome fasta file |

### `BWA_INDEX` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `index` | `map` | `*.{amb,ann,bwt,pac,sa}` | Groovy Map containing reference information. e.g. [ id:'test', single_end:false ] |

### `BWA_MEM` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `reads` | `file` | List of input FastQ files of size 1 and 2 for single-end and paired-end data, respectively. |
| `meta2` | `map` | Groovy Map containing reference information. e.g. [ id:'test', single_end:false ] |
| `index` | `file` | BWA genome index files |
| `meta3` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `fasta` | `file` | Reference genome in FASTA format |
| `sort_bam` | `boolean` | use samtools sort (true) or samtools view (false) |

### `BWA_MEM` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*.bam")` | `tuple` | `bam` | n/a |
| `val(meta), path("*.cram")` | `tuple` | `cram` | n/a |
| `val(meta), path("*.csi")` | `tuple` | `csi` | n/a |
| `val(meta), path("*.crai")` | `tuple` | `crai` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

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
| `report` | `file` | `*.csv` | snpEff report csv file |
| `summary_html` | `file` | `*.html` | snpEff summary statistics in html file |
| `genes_txt` | `file` | `*.genes.txt` | txt (tab separated) file having counts of the number of variants affecting each transcript and gene |

### `SNPEFF_DOWNLOAD` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `snpeff_db` | `string` | SnpEff database name |

### `SNPEFF_DOWNLOAD` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `cache` | `file` | n/a | snpEff cache |

### `NGSCHECKMATE_NCM` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test'] |
| `files` | `file` | VCF or BAM files for each sample, in a merged channel (possibly gzipped). BAM files require an index too. |
| `meta2` | `map` | Groovy Map containing SNP information e.g. [ id:'test' ] |
| `snp_bed` | `file` | BED file containing the SNPs to analyse |
| `meta3` | `map` | Groovy Map containing reference fasta index information e.g. [ id:'test' ] |
| `fasta` | `file` | fasta file for the genome, only used in the bam mode |

### `NGSCHECKMATE_NCM` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*_corr_matrix.txt")` | `tuple` | `corr_matrix` | n/a |
| `val(meta), path("*_matched.txt")` | `tuple` | `matched` | n/a |
| `val(meta), path("*_all.txt")` | `tuple` | `all` | n/a |
| `val(meta), path("*.pdf")` | `tuple` | `pdf` | n/a |
| `val(meta), path("*.vcf")` | `tuple` | `vcf` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

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
| `report` | `-` | n/a | n/a |

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

### `VARLOCIRAPTOR_CALLVARIANTS` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `vcfs` | `file` | Sorted VCF/BCF file containing sample observations, Can also be a list of files |

### `VARLOCIRAPTOR_CALLVARIANTS` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `bcf` | `file` | `*.bcf` | BCF file containing sample observations |

### `VARLOCIRAPTOR_PREPROCESS` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `bam` | `file` | Sorted BAM/CRAM/SAM file |
| `bai` | `file` | Index of the BAM/CRAM/SAM file |
| `candidates` | `file` | Sorted BCF/VCF file |
| `alignment_json` | `file` | File containing alignment properties obtained with varlociraptor/estimatealignmentproperties |
| `meta2` | `map` | Groovy Map containing reference information e.g. [ id:'test', single_end:false ] |
| `fasta` | `file` | Reference fasta file |
| `meta3` | `map` | Groovy Map containing reference index information e.g. [ id:'test', single_end:false ] |
| `fai` | `file` | Index for reference fasta file (must be with samtools index) |

### `VARLOCIRAPTOR_PREPROCESS` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `bcf` | `file` | `*.bcf` | BCF file containing sample observations |

### `VARLOCIRAPTOR_ESTIMATEALIGNMENTPROPERTIES` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `bam` | `file` | Sorted BAM/CRAM/SAM file |
| `bai` | `file` | Index of sorted BAM/CRAM/SAM file |
| `meta2` | `map` | Groovy Map containing reference information e.g. [ id:'test', single_end:false ] |
| `fasta` | `file` | Reference fasta file |
| `meta3` | `map` | Groovy Map containing reference index information e.g. [ id:'test', single_end:false ] |
| `fai` | `file` | Index for reference fasta file (must be with samtools index) |

### `VARLOCIRAPTOR_ESTIMATEALIGNMENTPROPERTIES` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `alignment_properties_json` | `file` | `*.alignment-properties.json` | File containing alignment properties |

### `CNVKIT_GENEMETRICS` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `cnr` | `file` | CNR file |
| `cns` | `file` | CNS file [Optional] |

### `CNVKIT_GENEMETRICS` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*.tsv")` | `tuple` | `tsv` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

### `CNVKIT_CALL` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `cns` | `file` | CNVKit CNS file. |
| `vcf` | `file` | Germline VCF file for BAF. |

### `CNVKIT_CALL` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*.cns")` | `tuple` | `cns` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

### `CNVKIT_BATCH` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `tumor` | `file` | Input tumour sample bam file (or cram) |
| `normal` | `file` | Input normal sample bam file (or cram) |
| `meta2` | `map` | Groovy Map containing reference information e.g. [ id:'test' ] |
| `fasta` | `file` | Input reference genome fasta file (only needed for cram_input and/or when normal_samples are provided) |
| `meta3` | `map` | Groovy Map containing reference information e.g. [ id:'test' ] |
| `fasta_fai` | `file` | Input reference genome fasta index (optional, but recommended for cram_input) |
| `meta4` | `map` | Groovy Map containing information about target file e.g. [ id:'test' ] |
| `targets` | `file` | Input target bed file |
| `meta5` | `map` | Groovy Map containing information about reference file e.g. [ id:'test' ] |
| `reference` | `file` | Input reference cnn-file (only for germline and tumor-only running) |
| `panel_of_normals` | `file` | Input panel of normals file |

### `CNVKIT_BATCH` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*.bed")` | `tuple` | `bed` | n/a |
| `val(meta), path("*.cnn")` | `tuple` | `cnn` | n/a |
| `val(meta), path("*.cnr")` | `tuple` | `cnr` | n/a |
| `val(meta), path("*.cns")` | `tuple` | `cns` | n/a |
| `val(meta), path("*.pdf")` | `tuple` | `pdf` | n/a |
| `val(meta), path("*.png")` | `tuple` | `png` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

### `CNVKIT_ANTITARGET` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `targets` | `file` | File containing genomic regions |

### `CNVKIT_ANTITARGET` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*.bed")` | `tuple` | `bed` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

### `CNVKIT_EXPORT` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `cns` | `file` | CNVKit CNS file. |

### `CNVKIT_EXPORT` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta)` | `tuple` | n/a | n/a |

### `CNVKIT_REFERENCE` Inputs

| Name | Type | Description |
|------|------|-------------|
| `fasta` | `file` | File containing reference genome |
| `targets` | `file` | File containing genomic regions |
| `antitargets` | `file` | File containing off-target genomic regions |

### `CNVKIT_REFERENCE` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `*.cnn` | `path` | `cnn` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

### `RBT_VCFSPLIT` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. `[ id:'sample1' ]` |
| `vcf` | `file` | VCF file with variants to be split |

### `RBT_VCFSPLIT` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `bcfchunks` | `file` | `*.bcf` | Chunks of the input VCF file, split into `numchunks` equal parts. |

### `FGBIO_FASTQTOBAM` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `reads` | `file` | pair of reads to be converted into BAM file |

### `FGBIO_FASTQTOBAM` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*.bam")` | `tuple` | `bam` | n/a |
| `val(meta), path("*.cram")` | `tuple` | `cram` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

### `FGBIO_COPYUMIFROMREADNAME` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. `[ id:'sample1' ]` |
| `bam` | `file` | Sorted BAM/CRAM/SAM file |
| `bai` | `file` | Index for bam file |

### `FGBIO_COPYUMIFROMREADNAME` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `bam` | `file` | `*.{bam}` | Sorted BAM file |
| `bai` | `file` | `*.{bai}` | Index for bam file |

### `FGBIO_CALLMOLECULARCONSENSUSREADS` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false, collapse:false ] |
| `grouped_bam` | `file` | The input SAM or BAM file, grouped by UMIs |
| `min_reads` | `integer` | Minimum number of original reads to build each consensus read. |
| `min_baseq` | `integer` | Ignore bases in raw reads that have Q below this value. |

### `FGBIO_CALLMOLECULARCONSENSUSREADS` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*.bam")` | `tuple` | `bam` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

### `FGBIO_GROUPREADSBYUMI` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `bam` | `file` | BAM file. Note: the MQ tag is required on reads with mapped mates (!) |
| `strategy` | `string` | Required argument: defines the UMI assignment strategy. Must be chosen among: Identity, Edit, Adjacency, Paired. |

### `FGBIO_GROUPREADSBYUMI` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*.bam")` | `tuple` | `bam` | n/a |
| `val(meta), path("*histogram.txt")` | `tuple` | `histogram` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

### `BWAMEM2_INDEX` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `fasta` | `file` | Input genome fasta file |

### `BWAMEM2_INDEX` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `index` | `file` | `*.{0123,amb,ann,bwt.2bit.64,pac}` | BWA genome index files |

### `BWAMEM2_MEM` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `reads` | `file` | List of input FastQ files of size 1 and 2 for single-end and paired-end data, respectively. |
| `meta2` | `map` | Groovy Map containing reference/index information e.g. [ id:'test' ] |
| `index` | `file` | BWA genome index files |
| `meta3` | `map` | Groovy Map containing reference information e.g. [ id:'genome' ] |
| `fasta` | `file` | Reference genome in FASTA format |
| `sort_bam` | `boolean` | use samtools sort (true) or samtools view (false) |

### `BWAMEM2_MEM` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*.sam")` | `tuple` | `sam` | n/a |
| `val(meta), path("*.bam")` | `tuple` | `bam` | n/a |
| `val(meta), path("*.cram")` | `tuple` | `cram` | n/a |
| `val(meta), path("*.crai")` | `tuple` | `crai` | n/a |
| `val(meta), path("*.csi")` | `tuple` | `csi` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

### `MANTA_TUMORONLY` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `input` | `file` | BAM/CRAM/SAM file |
| `input_index` | `file` | BAM/CRAM/SAM index file |
| `target_bed` | `file` | BED file containing target regions for variant calling |
| `target_bed_tbi` | `file` | Index for BED file containing target regions for variant calling |
| `meta2` | `map` | Groovy Map containing reference information e.g. [ id:'genome' ] |
| `fasta` | `file` | Genome reference FASTA file |
| `meta3` | `map` | Groovy Map containing reference information e.g. [ id:'genome' ] |
| `fai` | `file` | Genome reference FASTA index file |

### `MANTA_TUMORONLY` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `candidate_small_indels_vcf` | `file` | `*.{vcf.gz}` | Gzipped VCF file containing variants |
| `candidate_small_indels_vcf_tbi` | `file` | `*.{vcf.gz.tbi}` | Index for gzipped VCF file containing variants |
| `candidate_sv_vcf` | `file` | `*.{vcf.gz}` | Gzipped VCF file containing variants |
| `candidate_sv_vcf_tbi` | `file` | `*.{vcf.gz.tbi}` | Index for gzipped VCF file containing variants |
| `tumor_sv_vcf` | `file` | `*.{vcf.gz}` | Gzipped VCF file containing variants |
| `tumor_sv_vcf_tbi` | `file` | `*.{vcf.gz.tbi}` | Index for gzipped VCF file containing variants |

### `MANTA_GERMLINE` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `input` | `file` | BAM/CRAM/SAM file. For joint calling use a list of files. |
| `index` | `file` | BAM/CRAM/SAM index file. For joint calling use a list of files. |
| `target_bed` | `file` | BED file containing target regions for variant calling |
| `target_bed_tbi` | `file` | Index for BED file containing target regions for variant calling |
| `meta2` | `map` | Groovy Map containing reference information e.g. [ id:'genome' ] |
| `fasta` | `file` | Genome reference FASTA file |
| `meta3` | `map` | Groovy Map containing reference information e.g. [ id:'genome' ] |
| `fai` | `file` | Genome reference FASTA index file |

### `MANTA_GERMLINE` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `candidate_small_indels_vcf` | `file` | `*.{vcf.gz}` | Gzipped VCF file containing variants |
| `candidate_small_indels_vcf_tbi` | `file` | `*.{vcf.gz.tbi}` | Index for gzipped VCF file containing variants |
| `candidate_sv_vcf` | `file` | `*.{vcf.gz}` | Gzipped VCF file containing variants |
| `candidate_sv_vcf_tbi` | `file` | `*.{vcf.gz.tbi}` | Index for gzipped VCF file containing variants |
| `diploid_sv_vcf` | `file` | `*.{vcf.gz}` | Gzipped VCF file containing variants |
| `diploid_sv_vcf_tbi` | `file` | `*.{vcf.gz.tbi}` | Index for gzipped VCF file containing variants |

### `MANTA_SOMATIC` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `input_normal` | `file` | BAM/CRAM/SAM file |
| `input_index_normal` | `file` | BAM/CRAM/SAM index file |
| `input_tumor` | `file` | BAM/CRAM/SAM file |
| `input_index_tumor` | `file` | BAM/CRAM/SAM index file |
| `target_bed` | `file` | BED file containing target regions for variant calling |
| `target_bed_tbi` | `file` | Index for BED file containing target regions for variant calling |
| `meta2` | `map` | Groovy Map containing reference information e.g. [ id:'genome' ] |
| `fasta` | `file` | Genome reference FASTA file |
| `meta3` | `map` | Groovy Map containing reference information e.g. [ id:'genome' ] |
| `fai` | `file` | Genome reference FASTA index file |

### `MANTA_SOMATIC` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `candidate_small_indels_vcf` | `file` | `*.{vcf.gz}` | Gzipped VCF file containing variants |
| `candidate_small_indels_vcf_tbi` | `file` | `*.{vcf.gz.tbi}` | Index for gzipped VCF file containing variants |
| `candidate_sv_vcf` | `file` | `*.{vcf.gz}` | Gzipped VCF file containing variants |
| `candidate_sv_vcf_tbi` | `file` | `*.{vcf.gz.tbi}` | Index for gzipped VCF file containing variants |
| `diploid_sv_vcf` | `file` | `*.{vcf.gz}` | Gzipped VCF file containing variants |
| `diploid_sv_vcf_tbi` | `file` | `*.{vcf.gz.tbi}` | Index for gzipped VCF file containing variants |
| `somatic_sv_vcf` | `file` | `*.{vcf.gz}` | Gzipped VCF file containing variants |
| `somatic_sv_vcf_tbi` | `file` | `*.{vcf.gz.tbi}` | Index for gzipped VCF file containing variants |

### `BCFTOOLS_CONCAT` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `vcfs` | `list` | List containing 2 or more vcf files e.g. [ 'file1.vcf', 'file2.vcf' ] |
| `tbi` | `list` | List containing 2 or more index files (optional) e.g. [ 'file1.tbi', 'file2.tbi' ] |

### `BCFTOOLS_CONCAT` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta)` | `tuple` | n/a | n/a |

### `BCFTOOLS_SORT` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `vcf` | `file` | The VCF/BCF file to be sorted |

### `BCFTOOLS_SORT` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta)` | `tuple` | n/a | n/a |

### `BCFTOOLS_MERGE` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `vcfs` | `file` | List containing 2 or more vcf files e.g. [ 'file1.vcf', 'file2.vcf' ] |
| `tbis` | `file` | List containing the tbi index files corresponding to the vcfs input files e.g. [ 'file1.vcf.tbi', 'file2.vcf.tbi' ] |
| `meta2` | `map` | Groovy Map containing reference information e.g. [ id:'genome' ] |
| `fasta` | `file` | (Optional) The fasta reference file (only necessary for the `--gvcf FILE` parameter) |
| `meta3` | `map` | Groovy Map containing reference information e.g. [ id:'genome' ] |
| `fai` | `file` | (Optional) The fasta reference file index (only necessary for the `--gvcf FILE` parameter) |
| `meta4` | `map` | Groovy Map containing bed information e.g. [ id:'genome' ] |
| `bed` | `file` | (Optional) The bed regions to merge on |

### `BCFTOOLS_MERGE` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `vcf` | `file` | `*.{vcf,vcf.gz,bcf,bcf.gz}` | merged output file |
| `index` | `file` | `*.{csi,tbi}` | index of merged output |

### `BCFTOOLS_MPILEUP` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `bam` | `file` | Input BAM file |
| `intervals` | `file` | Input intervals file. A file (commonly '.bed') containing regions to subset |
| `meta2` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `fasta` | `file` | FASTA reference file |
| `save_mpileup` | `boolean` | Save mpileup file generated by bcftools mpileup |

### `BCFTOOLS_MPILEUP` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*vcf.gz")` | `tuple` | `vcf` | n/a |
| `val(meta), path("*vcf.gz.tbi")` | `tuple` | `tbi` | n/a |
| `val(meta), path("*stats.txt")` | `tuple` | `stats` | n/a |
| `val(meta), path("*.mpileup.gz")` | `tuple` | `mpileup` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

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

### `BCFTOOLS_NORM` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `vcf` | `file` | The vcf file to be normalized e.g. 'file1.vcf' |
| `tbi` | `file` | An optional index of the VCF file (for when the VCF is compressed) |
| `meta2` | `map` | Groovy Map containing reference information e.g. [ id:'genome' ] |
| `fasta` | `file` | FASTA reference file |

### `BCFTOOLS_NORM` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta)` | `tuple` | n/a | n/a |

### `BCFTOOLS_VIEW` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `vcf` | `file` | The vcf file to be inspected. e.g. 'file.vcf' |
| `index` | `file` | The tab index for the VCF file to be inspected. e.g. 'file.tbi' |

### `BCFTOOLS_VIEW` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `vcf` | `file` | `*.{vcf,vcf.gz,bcf,bcf.gz}` | VCF normalized output file |
| `tbi` | `file` | `*.tbi` | Alternative VCF file index |
| `csi` | `file` | `*.csi` | Default VCF file index |

### `BCFTOOLS_STATS` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `vcf` | `file` | VCF input file |
| `tbi` | `file` | The tab index for the VCF file to be inspected. Optional: only required when parameter regions is chosen. |
| `meta2` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `regions` | `file` | Optionally, restrict the operation to regions listed in this file. (VCF, BED or tab-delimited) |
| `meta3` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `targets` | `file` | Optionally, restrict the operation to regions listed in this file (doesn't rely upon tbi index files) |
| `meta4` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `samples` | `file` | Optional, file of sample names to be included or excluded. e.g. 'file.tsv' |
| `meta5` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `exons` | `file` | Tab-delimited file with exons for indel frameshifts (chr,beg,end; 1-based, inclusive, optionally bgzip compressed). e.g. 'exons.tsv.gz' |
| `meta6` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `fasta` | `file` | Faidx indexed reference sequence file to determine INDEL context. e.g. 'reference.fa' |

### `BCFTOOLS_STATS` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*stats.txt")` | `tuple` | `stats` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

### `BCFTOOLS_ISEC` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `vcfs` | `list` | List containing 2 or more vcf/bcf files. These must be compressed and have an associated index. e.g. [ 'file1.vcf.gz', 'file2.vcf' ] |
| `tbis` | `list` | List containing the tbi index files corresponding to the vcf/bcf input files e.g. [ 'file1.vcf.tbi', 'file2.vcf.tbi' ] |

### `BCFTOOLS_ISEC` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `results` | `directory` | `${prefix}` | Folder containing the set operations results perform on the vcf files |

### `MSISENSORPRO_SCAN` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `fasta` | `file` | Reference genome |

### `MSISENSORPRO_SCAN` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `list` | `file` | `*.{list}` | File containing microsatellite list |

### `MSISENSORPRO_MSISOMATIC` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `normal` | `file` | BAM/CRAM/SAM file |
| `normal_index` | `file` | BAM/CRAM/SAM index file |
| `tumor` | `file` | BAM/CRAM/SAM file |
| `tumor_index` | `file` | BAM/CRAM/SAM index file |
| `intervals` | `file` | bed file containing interval information, optional |
| `meta2` | `map` | Groovy Map containing genome information e.g. [ id:'genome' ] |
| `fasta` | `file` | Reference genome |

### `MSISENSORPRO_MSISOMATIC` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `output_report` | `file` | n/a | File containing final report with all detected microsatellites, unstable somatic microsatellites, msi score |
| `output_dis` | `file` | n/a | File containing distribution results |
| `output_germline` | `file` | n/a | File containing germline results |
| `output_somatic` | `file` | n/a | File containing somatic results |

### `MUSE_SUMP` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. `[ id:'sample1', single_end:false ]` |
| `muse_call_txt` | `file` | single input file generated by 'MuSE call' |
| `meta2` | `map` | Groovy Map containing reference information. e.g. `[ id:'test' ]` |
| `ref_vcf` | `file` | dbSNP vcf file that should be bgzip compressed, tabix indexed and based on the same reference genome used in 'MuSE call' |
| `ref_vcf_tbi` | `file` | Tabix index for the dbSNP vcf file |

### `MUSE_SUMP` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `vcf` | `map` | `*.vcf.gz` | bgzipped vcf file with called variants |
| `tbi` | `map` | `*.vcf.gz.tbi` | tabix index of bgzipped vcf file with called variants |

### `MUSE_CALL` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. `[ id:'sample1' ]` |
| `tumor_bam` | `file` | Sorted tumor BAM file |
| `tumor_bai` | `file` | Index file for the tumor BAM file |
| `normal_bam` | `file` | Sorted matched normal BAM file |
| `normal_bai` | `file` | Index file for the normal BAM file |
| `meta2` | `map` | Groovy Map containing reference information. e.g. `[ id:'test' ]` |
| `reference` | `file` | reference genome file |

### `MUSE_CALL` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `txt` | `file` | `*.MuSE.txt` | position-specific summary statistics |

### `PARABRICKS_FQ2BAM` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `reads` | `file` | fastq.gz files |
| `meta2` | `map` | Groovy Map containing fasta information |
| `fasta` | `file` | reference fasta file - must be unzipped |
| `meta3` | `map` | Groovy Map containing index information |
| `index` | `file` | reference BWA index |
| `meta4` | `map` | Groovy Map containing index information |
| `interval_file` | `file` | (optional) file(s) containing genomic intervals for use in base quality score recalibration (BQSR) |
| `meta5` | `map` | Groovy Map containing known sites information |
| `known_sites` | `file` | (optional) known sites file(s) for calculating BQSR. markdups must be true to perform BQSR. |

### `PARABRICKS_FQ2BAM` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `bam` | `file` | `*.bam` | Sorted BAM file |
| `bai` | `file` | `*.bai` | index corresponding to sorted BAM file |
| `cram` | `file` | `*.cram` | Sorted CRAM file |
| `crai` | `file` | `*.crai` | index corresponding to sorted CRAM file |
| `bqsr_table` | `file` | `*.table` | (optional) table from base quality score recalibration calculation, to be used with parabricks/applybqsr |
| `qc_metrics` | `directory` | `*_qc_metrics` | (optional) optional directory of qc metrics |
| `duplicate_metrics` | `file` | `*.duplicate-metrics.txt` | (optional) metrics calculated from marking duplicates in the bam file |
| `compatible_versions` | `-` | n/a | n/a |

### `SVDB_MERGE` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test' ] |
| `vcfs` | `list` | One or more VCF files. The order and number of files should correspond to the order and number of tags in the `priority` input channel. |
| `input_priority` | `list` | Prioritize the input VCF files according to this list, e.g ['tiddit','cnvnator']. The order and number of tags should correspond to the order and number of VCFs in the `vcfs` input channel. |
| `sort_inputs` | `boolean` | Should the input files be sorted by name. The priority tag will be sorted together with it's corresponding VCF file. |

### `SVDB_MERGE` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta)` | `tuple` | n/a | n/a |

### `TIDDIT_SV` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `input` | `file` | BAM/CRAM file |
| `input_index` | `file` | BAM/CRAM index file |
| `meta2` | `map` | Groovy Map containing sample information e.g. `[ id:'test_fasta']` |
| `fasta` | `file` | Input FASTA file |
| `meta3` | `map` | Groovy Map containing sample information from bwa index e.g. `[ id:'test_bwa-index' ]` |
| `bwa_index` | `file` | BWA genome index files |

### `TIDDIT_SV` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*.vcf")` | `tuple` | `vcf` | n/a |
| `val(meta), path("*.ploidies.tab")` | `tuple` | `ploidy` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

### `TABIX_TABIX` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `tab` | `file` | TAB-delimited genome position file compressed with bgzip |

### `TABIX_TABIX` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `tbi` | `file` | `*.{tbi}` | tabix index file |
| `csi` | `file` | `*.{csi}` | coordinate sorted index file |

### `TABIX_BGZIPTABIX` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `input` | `file` | Sorted tab-delimited genome file |

### `TABIX_BGZIPTABIX` Outputs

| Name | Type | Pattern | Description |
|------|------|---------|-------------|
| `gz_tbi` | `file` | `*.gz, *.tbi` | bgzipped tab-delimited genome file tabix index file |
| `gz_csi` | `file` | `*.gz, *.csi` | bgzipped tab-delimited genome file csi index file |

### `CAT_CAT` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `files_in` | `file` | List of compressed / uncompressed files |

### `CAT_CAT` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta)` | `tuple` | n/a | n/a |

### `CAT_FASTQ` Inputs

| Name | Type | Description |
|------|------|-------------|
| `meta` | `map` | Groovy Map containing sample information e.g. [ id:'test', single_end:false ] |
| `reads` | `file` | List of input FastQ files to be concatenated. |

### `CAT_FASTQ` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*.merged.fastq.gz")` | `tuple` | `reads` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

### `CREATE_INTERVALS_BED` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `*.bed` | `path` | `bed` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

### `ADD_INFO_TO_VCF` Inputs

| Name | Type | Description |
|------|------|-------------|
| `val(meta), path(vcf_gz)` | `tuple` | n/a |

### `ADD_INFO_TO_VCF` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta), path("*.added_info.vcf")` | `tuple` | `vcf` | n/a |
| `versions.yml` | `path` | `versions` | n/a |

### `SAMTOOLS_REINDEX_BAM` Inputs

| Name | Type | Description |
|------|------|-------------|
| `val(meta), path(input), path(input_index)` | `tuple` | n/a |
| `val(meta2), path(fasta)` | `tuple` | n/a |
| `val(meta3), path(fai)` | `tuple` | n/a |

### `SAMTOOLS_REINDEX_BAM` Outputs

| Name | Type | Emit | Description |
|------|------|------|-------------|
| `val(meta)` | `tuple` | n/a | n/a |

## Functions

| Name | Parameters | Returns | Description |
|------|------------|---------|-------------|
| `getGenomeAttribute` | `attribute` | n/a | n/a |
| `getFileSuffix` | `filename` | n/a | n/a |
| `addReadgroupToMeta` | `meta`, `files` | n/a | n/a |
| `flowcellLaneFromFastq` | `path` | n/a | n/a |
| `readFirstLineOfFastq` | `path` | n/a | n/a |
| `checkConfigProvided` | n/a | n/a | n/a |
| `checkProfileProvided` | `nextflow_cli_args` | n/a | n/a |
| `getWorkflowVersion` | n/a | n/a | n/a |
| `processVersionsFromYAML` | `yaml_file` | n/a | n/a |
| `workflowVersionToYAML` | n/a | n/a | n/a |
| `softwareVersionsToYAML` | `ch_versions` | n/a | n/a |
| `paramsSummaryMultiqc` | `summary_params` | n/a | n/a |
| `logColours` | `monochrome_logs` | n/a | n/a |
| `getSingleReport` | `multiqc_reports` | n/a | n/a |
| `completionEmail` | `summary_params`, `email`, `email_on_fail`, `plaintext_email`, `outdir`, `monochrome_logs`, `multiqc_report` | n/a | n/a |
| `completionSummary` | `monochrome_logs` | n/a | n/a |
| `imNotification` | `summary_params`, `hook_url` | n/a | n/a |
| `dumpParametersToJSON` | `outdir` | n/a | n/a |
| `checkCondaChannels` | n/a | n/a | n/a |
| `isCloudUrl` | `cache_url` | n/a | n/a |
| `validateInputParameters` | n/a | n/a | n/a |
| `genomeExistsError` | n/a | n/a | n/a |
| `sparkAndBam` | n/a | n/a | n/a |
| `toolCitationText` | n/a | n/a | n/a |
| `toolBibliographyText` | n/a | n/a | n/a |
| `methodsDescriptionText` | `mqc_methods_yaml` | n/a | n/a |
| `retrieveInput` | `need_input`, `step`, `outdir` | n/a | n/a |

---

*This pipeline was built with [Nextflow](https://nextflow.io).
Documentation generated by [nf-docs](https://github.com/ewels/nf-docs) v0.2.0 on 2026-03-03 22:40:55 UTC.*

<!-- END_NF_DOCS -->
