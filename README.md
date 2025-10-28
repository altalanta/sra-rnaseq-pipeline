# SRA RNA-seq Pipeline

The `sra-rnaseq-pipeline` repository provides an end-to-end Snakemake workflow for quantifying transcript expression from public RNA sequencing experiments deposited in the NCBI Sequence Read Archive (SRA). It targets differential expression studies, guiding users from raw accession numbers through quality control, quasi-mapping quantification with Salmon, and summary reporting suitable for downstream statistical analysis.

## Pipeline Stages
- Download SRA runs with `fasterq-dump` and compress to FASTQ
- Trim adapters and low-quality bases with `fastp`
- Assess read quality with `fastqc`
- Quantify transcript abundance using Salmon quasi-mapping
- Merge transcript-level counts into a single matrix
- Summarize QC metrics and aggregate reports with MultiQC

## Quickstart
1. `mamba env create -f environment.yml`
2. `conda activate sra-rnaseq`
3. Edit `config/samples.csv`
4. Edit `config/params.yaml`
5. `snakemake --cores 8`

## Sample Sheet Format
`config/samples.csv` must be a comma-separated table with the headers `sample_id`, `condition`, and `sra_run`. Each row represents one biological sample mapped to a single SRA run accession (single-end sequencing by default). Conditions distinguish biological groups for downstream differential expression (e.g., WT, KO). Ensure every `sample_id` is unique; if you have multiple runs per sample, list each run on a separate line and adjust the workflow to merge at the FASTQ level.

Example:
```
sample_id,condition,sra_run
WT_1,WT,SRR0000001
WT_2,WT,SRR0000002
KO_1,KO,SRR0000003
KO_2,KO,SRR0000004
```

## Reference and Index Preparation
1. Download the appropriate reference transcriptome FASTA (`reference.fa`) and gene annotation GTF (`reference.gtf`) for your organism and experimental question.
2. Place both files under `config/genome/`.
3. Build a Salmon transcriptome index:
   ```bash
   salmon index -t config/genome/reference.fa -i config/genome/index --gencode
   ```
4. Confirm the paths in `config/params.yaml` match the files you provided.

The repository ships empty placeholders for `reference.fa` and `reference.gtf` to illustrate expected filenames. Replace them with actual data before running the workflow. Use consistent genome builds and annotation versions across projects to preserve reproducibility.

## How the Workflow Operates
Configuration is handled through `config/params.yaml`. Snakemake loads sample metadata from `config/samples.csv`, resolves SRA run IDs, and triggers the following steps:

1. **Download** – `fasterq-dump` retrieves reads for each SRR accession, logging progress in `results/raw_fastq/`.
2. **QC and Trimming** – `fastp` removes adapters and short reads (threshold configurable) and produces trimmed FASTQs under `results/qc/`.
3. **Quality Reporting** – `fastqc` inspects both raw and trimmed reads; MultiQC aggregates all QC outputs.
4. **Quantification** – `salmon quant` runs in quasi-mapping mode using the provided transcriptome index.
5. **Counts Aggregation** – `scripts/make_counts_matrix.py` collates Salmon quantifications into `results/counts/expression_matrix.tsv`.
6. **Reporting** – `scripts/summarize_qc.py` and `multiqc` generate visual summaries and consolidated reports.

## Extending to Paired-End Data
The default rules assume single-end sequencing. To support paired-end reads, modify:
- `config/samples.csv` to include separate columns for R1/R2 FASTQs or multiple SRR entries per sample.
- `workflow/rules/download.smk` to pass `--split-files` to `fasterq-dump`.
- `workflow/rules/qc.smk` and `workflow/rules/align_quant.smk` to reference both mate files when running `fastp` and Salmon.

## Citing the Tools
Please cite the software that powers this workflow in publications:
- NCBI SRA Toolkit – Leinonen et al., Nucleic Acids Res. 2011.
- `fastp` – Chen et al., Bioinformatics 2018.
- `FastQC` – Andrews, Babraham Bioinformatics.
- `Salmon` – Patro et al., Nat. Methods 2017.
- `MultiQC` – Ewels et al., Bioinformatics 2016.
- `Snakemake` – Mölder et al., Nat. Biotechnol. 2021.

Refer to each tool’s documentation for specific citation formats.
