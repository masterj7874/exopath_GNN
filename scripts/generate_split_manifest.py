"""Generate a patient-level split manifest from a governance-approved CSV."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from exopath_gnn.splits import assign_patient_splits, write_manifest  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv", help="CSV with patient_id, cohort, cohort_role and site columns")
    parser.add_argument("output_csv")
    parser.add_argument("--config", default=str(ROOT / "config" / "default.json"))
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    with Path(args.input_csv).open("r", encoding="utf-8", newline="") as handle:
        records = list(csv.DictReader(handle))
    manifest = assign_patient_splits(records, config["development_split"], int(config["seed"]))
    write_manifest(args.output_csv, manifest)
    print(f"Wrote {len(manifest)} patient assignments to {args.output_csv}")


if __name__ == "__main__":
    main()

