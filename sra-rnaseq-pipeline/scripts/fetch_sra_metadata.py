#!/usr/bin/env python3
"""Fetch SRA run metadata for a BioProject and write a sample sheet."""

from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional

import io
import json

import pandas as pd

from utils import ensure_dir, get_logger


logger = get_logger("fetch_sra_metadata")


def fetch_with_pysradb(bioproject: str) -> Optional[pd.DataFrame]:
    try:
        from pysradb import SRAweb
    except ImportError:
        logger.info("pysradb is not installed; falling back to NCBI E-utilities")
        return None

    logger.info("Querying pysradb for BioProject %s", bioproject)
    try:
        db = SRAweb()
        df = db.sra_metadata(bioproject, detailed=True)
    except Exception as exc:  # noqa: BLE001
        logger.warning("pysradb lookup failed: %s", exc)
        return None

    if df is None or df.empty:
        logger.warning("pysradb returned no runs for %s", bioproject)
        return None

    columns = []
    if "sample_accession" in df.columns:
        columns.append(df["sample_accession"])
    elif "run_accession" in df.columns:
        columns.append(df["run_accession"])
    run_series = df.get("run_accession")
    if run_series is None:
        logger.warning("pysradb response missing run_accession column")
        return None

    output = pd.DataFrame(
        {
            "sample_id": df.get("sample_alias", run_series).fillna(run_series),
            "condition": df.get("sample_attribute", pd.Series(["NA"] * len(df))).fillna("NA"),
            "sra_run": run_series,
        }
    )
    return output.drop_duplicates("sra_run")


def fetch_with_eutils(bioproject: str) -> Optional[pd.DataFrame]:
    logger.info("Querying NCBI E-utilities for BioProject %s", bioproject)
    esearch_params = {
        "db": "sra",
        "term": bioproject,
        "retmode": "json",
    }
    esearch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    query = urllib.parse.urlencode(esearch_params)
    try:
        with urllib.request.urlopen(esearch_url + "?" + query) as response:
            esearch_data = response.read().decode()
    except urllib.error.URLError as exc:
        logger.error("Network error during esearch: %s", exc)
        return None

    try:
        data = json.loads(esearch_data)
        idlist = data["esearchresult"]["idlist"]
    except (KeyError, json.JSONDecodeError) as exc:
        logger.error("Unexpected esearch response for %s: %s", bioproject, exc)
        return None

    if not idlist:
        logger.warning("No SRA run identifiers found for %s", bioproject)
        return None

    efetch_params = {
        "db": "sra",
        "retmode": "text",
        "rettype": "runinfo",
        "id": ",".join(idlist),
    }
    efetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    try:
        with urllib.request.urlopen(efetch_url + "?" + urllib.parse.urlencode(efetch_params)) as response:
            csv_text = response.read().decode()
    except urllib.error.URLError as exc:
        logger.error("Network error during efetch: %s", exc)
        return None

    if not csv_text.strip():
        logger.warning("Empty runinfo returned for %s", bioproject)
        return None

    df = pd.read_csv(io.StringIO(csv_text))
    if df.empty or "Run" not in df.columns:
        logger.warning("Runinfo did not include run accessions for %s", bioproject)
        return None

    sample_alias = df.get("Sample_Name", df.get("BioSample", df["Run"]))
    output = pd.DataFrame(
        {
            "sample_id": sample_alias.fillna(df["Run"]),
            "condition": pd.Series(["NA"] * len(df)),
            "sra_run": df["Run"],
        }
    )
    return output.drop_duplicates("sra_run")


def write_sample_sheet(df: pd.DataFrame, out_path: Path) -> None:
    ensure_dir(out_path.parent)
    df.to_csv(out_path, index=False)
    logger.info("Wrote %d rows to %s", len(df), out_path)


def print_example_and_exit(out_path: Path) -> None:
    example = "sample_id,condition,sra_run\nSampleA,NA,SRR0000001\nSampleB,NA,SRR0000002\n"
    sys.stderr.write(
        "Unable to retrieve metadata from NCBI. Check your network connection or install pysradb.\n"
        "Create the sample sheet manually using the following structure:\n"
        f"{example}"
        f"Expected output location: {out_path}\n"
    )
    sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate config/samples.csv from an NCBI BioProject accession.")
    parser.add_argument("--bioproject", required=True, help="BioProject accession, e.g., PRJNA123456")
    parser.add_argument("--out", required=True, help="Destination CSV path (e.g., config/samples.csv)")
    args = parser.parse_args()

    out_path = Path(args.out)

    df = fetch_with_pysradb(args.bioproject)
    if df is None:
        df = fetch_with_eutils(args.bioproject)

    if df is None or df.empty:
        print_example_and_exit(out_path)

    df = df.drop_duplicates("sra_run").sort_values("sample_id")
    write_sample_sheet(df, out_path)


if __name__ == "__main__":
    main()
