import subprocess
import sys
from pathlib import Path

import pandas as pd


def _write_quant(path: Path, sample_name: str) -> None:
    content = "\n".join(
        [
            "Name\tLength\tEffectiveLength\tTPM\tNumReads",
            f"ENST0001\t1000\t800\t{10 if sample_name.endswith('1') else 20}\t{50 if sample_name.endswith('1') else 60}",
            f"ENST0002\t900\t700\t{5 if sample_name.endswith('1') else 15}\t{25 if sample_name.endswith('1') else 35}",
        ]
    )
    path.write_text(content)


def test_make_counts_matrix(tmp_path: Path) -> None:
    quant_dir = tmp_path / "results" / "quant"
    (quant_dir / "Sample1").mkdir(parents=True)
    (quant_dir / "Sample2").mkdir(parents=True)

    _write_quant(quant_dir / "Sample1" / "quant.sf", "Sample1")
    _write_quant(quant_dir / "Sample2" / "quant.sf", "Sample2")

    output_path = tmp_path / "results" / "counts" / "expression_matrix.tsv"
    output_path.parent.mkdir(parents=True)

    subprocess.check_call(
        [
            sys.executable,
            "scripts/make_counts_matrix.py",
            "--quant_dir",
            str(quant_dir),
            "--out",
            str(output_path),
        ]
    )

    assert output_path.exists()
    df = pd.read_csv(output_path, sep="\t")
    expected_columns = {"transcript_id", "Sample1_TPM", "Sample1_NumReads", "Sample2_TPM", "Sample2_NumReads"}
    assert expected_columns.issubset(df.columns)
    assert set(df["transcript_id"]) == {"ENST0001", "ENST0002"}
