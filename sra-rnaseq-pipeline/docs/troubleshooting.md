# Troubleshooting Guide

## Low Disk Space During `fasterq-dump`
- `fasterq-dump` writes temporary uncompressed FASTQ files that can be 2–3× larger than the final `.fastq.gz`.
- Point the `TMPDIR` environment variable to a volume with ample space:
  ```bash
  export TMPDIR=/path/to/scratch
  snakemake --cores 8
  ```
- Alternatively, run `prefetch` beforehand to download `.sra` files to a dedicated drive and supply `--temp` to `fasterq-dump`.

## SRA Toolkit SSL or Prefetch Errors
- SSL problems often stem from outdated certificates. Update the SRA Toolkit configuration with:
  ```bash
  vdb-config --interactive
  ```
  and enable system certificates.
- For strict network environments, download `.sra` files manually using a browser and place them in the SRA data directory reported by `vdb-config --list`.

## Salmon Index Path Mismatch
- If Snakemake reports `Salmon index directory not found`, verify the path in `config/params.yaml`:
  ```yaml
  genome:
    salmon_index: "config/genome/index"
  ```
- Confirm the directory contains Salmon index files (`hash.bin`, `info.json`, etc.).
- Rebuild the index if the FASTA or GTF changed. Mixing mismatched references introduces quantification biases and misaligned gene IDs.
