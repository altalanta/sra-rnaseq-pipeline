# Pipeline Overview

The Snakemake workflow consists of modular rules grouped by function. Each rule lists explicit inputs and outputs so new samples trigger only the necessary steps.

## Rules and Data Flow

1. **download_fastq** (`workflow/rules/download.smk`)
   - **Input**: SRA run accession from `config/samples.csv`
   - **Output**: Compressed FASTQ (`results/raw_fastq/{sra_run}.fastq.gz`) plus a log file
   - **Purpose**: Retrieve read data directly from the SRA using `fasterq-dump`.

2. **trim_qc** (`workflow/rules/qc.smk`)
   - **Input**: Raw FASTQ from the download step
   - **Output**: Adapter- and quality-trimmed FASTQ (`results/qc/{sra_run}.trimmed.fastq.gz`)
   - **Purpose**: Remove low-quality bases and short reads using `fastp`.

3. **fastqc_report** (`workflow/rules/qc.smk`)
   - **Input**: Raw and trimmed FASTQs
   - **Output**: `FastQC` HTML/ZIP diagnostics in `results/qc/fastqc/`
   - **Purpose**: Assess per-base quality, GC content, and adapter content before and after trimming.

4. **quantify_expression** (`workflow/rules/align_quant.smk`)
   - **Input**: Trimmed FASTQ, Salmon transcriptome index
   - **Output**: `quant.sf` per sample in `results/quant/{sample_id}/`
   - **Purpose**: Estimate transcript-level abundances with Salmon quasi-mapping (`--gcBias`, `--validateMappings`).

5. **merge_counts** (`workflow/rules/counts.smk`)
   - **Input**: All `quant.sf` files
   - **Output**: `results/counts/expression_matrix.tsv`
   - **Purpose**: Combine TPM and NumReads from Salmon into a single counts matrix for downstream statistics.

6. **multiqc_all** and **summary_plots** (`workflow/rules/report.smk`)
   - **Input**: QC outputs, Salmon results, and the merged counts matrix
   - **Output**: `results/reports/multiqc_report.html` and plots under `results/reports/plots/`
   - **Purpose**: Aggregate QC findings and generate overview figures (library size and PCA).

## Single-End vs. Paired-End

The default configuration treats each SRA run as single-end data. To adapt the pipeline to paired-end sequencing:
- Modify `Workflow/rules/download.smk` to pass `--split-files` to `fasterq-dump` and update outputs to include `_1.fastq.gz` and `_2.fastq.gz`.
- Adjust `trim_qc` to supply both mates to `fastp` (`--in1/--in2` and `--out1/--out2`).
- Update `quantify_expression` to pass `-1`/`-2` inputs to Salmon.

Because Snakemake explicitly lists file patterns, extending to paired-end reads requires only coordinated changes in these rules and the sample sheet format.
