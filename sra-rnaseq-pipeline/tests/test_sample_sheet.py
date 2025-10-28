from pathlib import Path

import pandas as pd
import pytest


REQUIRED_COLUMNS = ["sample_id", "condition", "sra_run"]


@pytest.mark.parametrize(
    "csv_path",
    [
        Path("config/samples.csv"),
        Path("tests/tiny_dataset/samples_small.csv"),
    ],
)
def test_sample_sheet_columns(csv_path: Path) -> None:
    df = pd.read_csv(csv_path)
    for column in REQUIRED_COLUMNS:
        assert column in df.columns, f"Missing required column: {column}"
        assert df[column].notna().all(), f"Column {column} contains empty values"
        assert (df[column].astype(str).str.len() > 0).all(), f"Column {column} has blank strings"
