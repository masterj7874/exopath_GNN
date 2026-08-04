from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from exopath_gnn.config import ConfigurationError, load_config, validate_config
from exopath_gnn.splits import SplitError, assign_patient_splits


class ConfigAndSplitTests(unittest.TestCase):
    def test_release_config_is_valid(self) -> None:
        config = load_config(ROOT / "config" / "default.json")
        self.assertEqual(config["status"], "prospective_protocol")

    def test_config_rejects_assumed_quantum_advantage(self) -> None:
        config = json.loads((ROOT / "config" / "default.json").read_text(encoding="utf-8"))
        config["benchmark"]["quantum_advantage_assumed"] = True
        with self.assertRaises(ConfigurationError):
            validate_config(config)

    def test_assignments_are_deterministic_and_external_isolated(self) -> None:
        records = [
            {"patient_id": f"P-{index}", "cohort": "dev", "cohort_role": "development", "site": "A"}
            for index in range(30)
        ]
        records.append({"patient_id": "E-1", "cohort": "ext", "cohort_role": "external", "site": "B"})
        proportions = {"train": 0.7, "tuning": 0.15, "calibration": 0.15}
        first = assign_patient_splits(records, proportions, 7)
        second = assign_patient_splits(reversed(records), proportions, 7)
        self.assertEqual(first, second)
        external = next(row for row in first if row["patient_id"] == "E-1")
        self.assertEqual(external["split"], "external")

    def test_duplicate_patient_is_rejected(self) -> None:
        records = [
            {"patient_id": "P-1", "cohort_role": "development"},
            {"patient_id": "P-1", "cohort_role": "development"},
        ]
        with self.assertRaises(SplitError):
            assign_patient_splits(records, {"train": 0.7, "tuning": 0.15, "calibration": 0.15}, 1)


if __name__ == "__main__":
    unittest.main()

