# Quickstart

Follow these steps to run the RNA-seq pipeline on your workstation or a compute node.

1. Install the base environment:
   ```bash
   mamba env create -f environment.yml
   conda activate sra-rnaseq
   ```
2. Update `config/samples.csv` with the SRA accessions you wish to process. Ensure each row has a unique `sample_id`, a `condition`, and an `sra_run` accession.
3. Edit `config/params.yaml` to match your compute resources (e.g., number of threads) and verify the reference file paths.
4. Populate `config/genome/reference.fa`, `config/genome/reference.gtf`, and build a Salmon index under `config/genome/index/` following the instructions in `config/genome/README.md`.
5. Launch the workflow:
   ```bash
   snakemake --cores 8
   ```

## Adding New SRA Runs

To include additional SRA accessions:
1. Append new rows to `config/samples.csv` for each run, specifying the appropriate condition.
2. Re-run `snakemake --cores 8`. Snakemake detects which outputs are missing and only processes the new samples.

For larger additions, consider using `scripts/fetch_sra_metadata.py` to generate a starter sample sheet from a BioProject accession, then refine the `condition` labels manually.
