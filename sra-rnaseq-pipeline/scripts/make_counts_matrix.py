#!/usr/bin/env python3
"""Merge Salmon quantifications into a single table."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict

import pandas as pd

from utils import ensure_dir, get_logger


logger = get_logger("make_counts_matrix")


def gather_quant_files(quant_dir: Path) -> Dict[str, Path]:
    quant_files: Dict[str, Path] = {}
    for sample_dir in quant_dir.glob("*"):
        quant_file = sample_dir / "quant.sf"
        if quant_file.exists():
            quant_files[sample_dir.name] = quant_file
    return quant_files


def load_quant_file(path: Path, sample: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep="\t", usecols=["Name", "TPM", "NumReads"])
    df = df.rename(
        columns={
            "Name": "transcript_id",
            "TPM": f"{sample}_TPM",
            "NumReads": f"{sample}_NumReads",
        }
    )
    return df


def merge_quants(quant_files: Dict[str, Path]) -> pd.DataFrame:
    merged: pd.DataFrame | None = None
    for sample, path in sorted(quant_files.items()):
        df = load_quant_file(path, sample)
        if merged is None:
            merged = df
        else:
            merged = merged.merge(df, on="transcript_id", how="outer")
    if merged is None:
        raise ValueError("No quant.sf files were found in the specified directory.")
    return merged.fillna(0.0)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a combined counts matrix from Salmon outputs.")
    parser.add_argument("--quant_dir", required=True, help="Directory containing per-sample Salmon outputs.")
    parser.add_argument("--out", required=True, help="Destination TSV path.")
    args = parser.parse_args()

    quant_dir = Path(args.quant_dir)
    output_path = Path(args.out)

    quant_files = gather_quant_files(quant_dir)
    if not quant_files:
        raise SystemExit(f"No quant.sf files found under {quant_dir}")

    merged = merge_quants(quant_files)
    ensure_dir(output_path.parent)
    merged.to_csv(output_path, sep="\t", index=False)
    logger.info("Wrote merged counts matrix to %s with %d transcripts", output_path, len(merged))


if __name__ == "__main__":
    main()
