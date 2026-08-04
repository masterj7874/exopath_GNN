from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from exopath_gnn.pipeline import run_protocol_demo


class PipelineTests(unittest.TestCase):
    def test_synthetic_protocol_demo_writes_auditable_outputs(self) -> None:
        output = ROOT / "artifacts" / "test-pipeline"
        output.mkdir(parents=True, exist_ok=True)
        summary = run_protocol_demo(
            output,
            ROOT / "config" / "default.json",
            ROOT / "schemas" / "typed_graph_schema.json",
        )
        self.assertEqual(summary["status"], "synthetic_contract_test_only")
        self.assertEqual(summary["patient_count"], 60)
        self.assertEqual(summary["split_counts"]["external"], 12)
        for filename in ("split_manifest.csv", "locked_predictions.jsonl", "summary.json", "provenance.json"):
            self.assertTrue((output / filename).is_file())
        provenance = json.loads((output / "provenance.json").read_text(encoding="utf-8"))
        self.assertEqual(provenance["status"], "synthetic_contract_test_only")
        self.assertEqual(len(provenance["frozen_files"]), 2)


if __name__ == "__main__":
    unittest.main()
