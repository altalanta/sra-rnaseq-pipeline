import logging
from pathlib import Path
from typing import Dict

import pandas as pd


def get_logger(name: str = "sra-rnaseq") -> logging.Logger:
    """Configure and return a module-level logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


def ensure_dir(path: Path) -> None:
    """Create a directory (and parents) if it does not exist."""
    path.mkdir(parents=True, exist_ok=True)


def read_sample_sheet(path: Path) -> pd.DataFrame:
    """Load the sample sheet and validate mandatory columns."""
    df = pd.read_csv(path)
    required = {"sample_id", "condition", "sra_run"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in {path}: {', '.join(sorted(missing))}")
    return df


def sample_to_run_map(df: pd.DataFrame) -> Dict[str, str]:
    """Return mapping from sample identifier to SRA run accession."""
    return dict(zip(df["sample_id"], df["sra_run"], strict=True))


def parse_bool(value: str) -> bool:
    """Interpret a string as a boolean flag."""
    true_values = {"true", "1", "yes", "y"}
    false_values = {"false", "0", "no", "n"}
    lowered = value.strip().lower()
    if lowered in true_values:
        return True
    if lowered in false_values:
        return False
    raise ValueError(f"Cannot parse boolean from {value!r}")
