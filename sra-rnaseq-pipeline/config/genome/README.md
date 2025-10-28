# Genome Resource Instructions

Provide organism-specific reference data before running the workflow:

1. Download the transcriptome FASTA (matching transcripts to be quantified) and place it at `config/genome/reference.fa`.
2. Download the corresponding gene annotation GTF and store it at `config/genome/reference.gtf`.
3. Build a Salmon transcriptome index using the FASTA:
   ```bash
   salmon index -t config/genome/reference.fa -i config/genome/index --gencode
   ```
4. Confirm all paths in `config/params.yaml` match the files above.

Use reference releases that align with your experimental design (e.g., Ensembl release, RefSeq build). Document the version in `docs/reproducibility.md` so analyses can be repeated exactly.
