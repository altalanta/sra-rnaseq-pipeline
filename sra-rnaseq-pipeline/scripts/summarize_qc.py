#!/usr/bin/env python3
"""Create QC summary plots from Salmon quantifications."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from utils import ensure_dir, get_logger, parse_bool, read_sample_sheet


logger = get_logger("summarize_qc")


def library_size_barplot(counts_df: pd.DataFrame, out_path: Path) -> None:
    num_reads_cols = [col for col in counts_df.columns if col.endswith("_NumReads")]
    if not num_reads_cols:
        raise ValueError("Counts matrix does not contain *_NumReads columns required for library size plot.")

    library_sizes = counts_df[num_reads_cols].sum(axis=0)
    samples = [col.replace("_NumReads", "") for col in num_reads_cols]

    plt.figure(figsize=(10, 4))
    plt.bar(samples, library_sizes.values)
    plt.ylabel("Total mapped reads")
    plt.xlabel("Sample")
    plt.title("Library Size per Sample")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    logger.info("Saved library size barplot to %s", out_path)


def pca_scatter_plot(counts_df: pd.DataFrame, out_path: Path, sample_order: list[str]) -> None:
    tpm_cols = [col for col in counts_df.columns if col.endswith("_TPM")]
    if not tpm_cols:
        raise ValueError("Counts matrix does not contain *_TPM columns required for PCA.")

    matrix = counts_df[tpm_cols].transpose()
    matrix.index = [col.replace("_TPM", "") for col in tpm_cols]
    matrix = matrix.loc[sample_order]

    log_expr = np.log1p(matrix.to_numpy())
    centered = log_expr - log_expr.mean(axis=0, keepdims=True)
    u, s, _ = np.linalg.svd(centered, full_m=False)
    scores = u[:, :2] * s[:2]

    plt.figure(figsize=(6, 6))
    plt.scatter(scores[:, 0], scores[:, 1])
    for idx, sample in enumerate(matrix.index):
        plt.text(scores[idx, 0], scores[idx, 1], sample, ha="center", va="bottom")
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.title("PCA of log1p(TPM)")
    plt.axhline(0, color="lightgray", linewidth=0.5)
    plt.axvline(0, color="lightgray", linewidth=0.5)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    logger.info("Saved PCA plot to %s", out_path)


def placeholder_pca(out_path: Path) -> None:
    plt.figure(figsize=(6, 4))
    plt.text(0.5, 0.5, "PCA disabled (see config)", ha="center", va="center", fontsize=12)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    logger.info("PCA disabled; wrote placeholder to %s", out_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate QC summary plots from quantification results.")
    parser.add_argument("--samples", required=True, help="Path to config/samples.csv")
    parser.add_argument("--quant", required=True, help="Merged counts matrix TSV")
    parser.add_argument("--outdir", required=True, help="Directory for plots")
    parser.add_argument("--make_pca", default="true", help="Whether to compute PCA (true/false)")
    args = parser.parse_args()

    sample_df = read_sample_sheet(Path(args.samples))
    counts_df = pd.read_csv(args.quant, sep="\t")
    out_dir = Path(args.outdir)
    ensure_dir(out_dir)

    library_plot = out_dir / "library_sizes.png"
    library_size_barplot(counts_df, library_plot)

    pca_plot = out_dir / "pca.png"
    if parse_bool(str(args.make_pca)):
        pca_scatter_plot(counts_df, pca_plot, sample_df["sample_id"].tolist())
    else:
        placeholder_pca(pca_plot)


if __name__ == "__main__":
    main()
