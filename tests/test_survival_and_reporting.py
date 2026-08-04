from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from exopath_gnn.benchmark import assert_budget_matched
from exopath_gnn.reporting import LockedPrediction, ReportingContractError, render_locked_report, validate_locked_report
from exopath_gnn.survival import discrete_time_nll, hazards_from_logits, survival_from_hazards


class SurvivalAndReportingTests(unittest.TestCase):
    def test_survival_is_monotone(self) -> None:
        survival = survival_from_hazards(hazards_from_logits((-1.0, 0.0, 1.0)))
        self.assertGreaterEqual(survival[0], survival[1])
        self.assertGreaterEqual(survival[1], survival[2])
        self.assertTrue(all(0.0 <= value <= 1.0 for value in survival))

    def test_event_and_censoring_likelihoods_are_finite(self) -> None:
        self.assertGreater(discrete_time_nll((-1.0, 0.0, 1.0), 1, True), 0.0)
        self.assertGreater(discrete_time_nll((-1.0, 0.0, 1.0), 1, False), 0.0)

    def test_parameter_budget_mismatch_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            assert_budget_matched([[1.0]], [0.0], [[1.0, 2.0]], [0.0])

    def test_locked_report_rejects_changed_number(self) -> None:
        locked = LockedPrediction("P-1", 60, 0.7, 0.3, "low", "development_only", ("clinical",), False)
        report = render_locked_report(locked)
        report["risk_probability"] = 0.4
        with self.assertRaisesRegex(ReportingContractError, "risk_probability"):
            validate_locked_report(report, locked)

    def test_locked_report_rejects_treatment_language(self) -> None:
        locked = LockedPrediction("P-1", 60, 0.7, 0.3, "low", "development_only", ("clinical",), False)
        report = render_locked_report(locked)
        report["narrative"] = "Treatment should be escalated."
        with self.assertRaises(ReportingContractError):
            validate_locked_report(report, locked)


if __name__ == "__main__":
    unittest.main()

