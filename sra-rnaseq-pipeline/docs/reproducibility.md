# Reproducibility Notes

- **Reference Data**: Record the exact genome build and annotation release you use. For example, note "Ensembl GRCh38 release 110 FASTA/GTF" in your lab notebook or version-control metadata.
- **Transcriptome Index**: Salmon indices are tied to the FASTA sequence and Salmon version. Rebuild the index if either changes, and store the index metadata (`info.json`) alongside your project.
- **Annotation Consistency**: Switching to a different annotation (e.g., RefSeq vs. Ensembl) alters transcript and gene identifiers. Do not compare quantification outputs generated from different annotations without explicit remapping.
- **Software Environment**: The provided `environment.yml` pins primary dependencies. Export an exact environment snapshot after installation:
  ```bash
  conda activate sra-rnaseq
  conda env export --from-history > env.lock.yml
  ```
  Commit the lockfile to track precise package versions.
- **Randomness Control**: Salmon uses deterministic algorithms given fixed inputs, so no additional random seeds are required. Ensure thread counts remain constant if you benchmark performance.
- **Data Provenance**: Keep a copy of `config/samples.csv` for every analysis state. When updating the sample sheet, save the prior version so you can reproduce earlier results.
