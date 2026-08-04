"""Evidence-locked reporting contract."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping


class ReportingContractError(ValueError):
    """Raised when a report alters locked output or exceeds permitted scope."""


@dataclass(frozen=True)
class LockedPrediction:
    patient_id: str
    horizon_months: int
    survival_probability: float
    risk_probability: float
    triage: str
    calibration_status: str
    modalities: tuple[str, ...]
    abstained: bool
    abstention_reasons: tuple[str, ...] = ()


def render_locked_report(prediction: LockedPrediction) -> dict[str, Any]:
    if prediction.abstained:
        narrative = "No unqualified risk report is available; abstention reasons: " + ", ".join(prediction.abstention_reasons)
        triage = "abstain"
    else:
        narrative = (
            f"At {prediction.horizon_months} months, locked survival probability is "
            f"{prediction.survival_probability:.6f} and locked risk probability is "
            f"{prediction.risk_probability:.6f}; triage is {prediction.triage}."
        )
        triage = prediction.triage
    report = asdict(prediction)
    report["triage"] = triage
    report["modalities"] = list(prediction.modalities)
    report["narrative"] = narrative
    report.pop("abstention_reasons", None)
    validate_locked_report(report, prediction)
    return report


def validate_locked_report(report: Mapping[str, Any], prediction: LockedPrediction) -> None:
    required = {
        "patient_id",
        "horizon_months",
        "survival_probability",
        "risk_probability",
        "triage",
        "calibration_status",
        "modalities",
        "abstained",
        "narrative",
    }
    if set(report) != required:
        raise ReportingContractError("report keys must exactly match the locked schema")
    if report["patient_id"] != prediction.patient_id or report["horizon_months"] != prediction.horizon_months:
        raise ReportingContractError("patient or horizon differs from locked output")
    for key in ("survival_probability", "risk_probability"):
        if abs(float(report[key]) - float(getattr(prediction, key))) > 1e-12:
            raise ReportingContractError(f"{key} differs from locked output")
    expected_triage = "abstain" if prediction.abstained else prediction.triage
    if report["triage"] != expected_triage or bool(report["abstained"]) != prediction.abstained:
        raise ReportingContractError("triage or abstention differs from locked output")
    if report["calibration_status"] != prediction.calibration_status:
        raise ReportingContractError("calibration status differs from locked output")
    if tuple(report["modalities"]) != prediction.modalities:
        raise ReportingContractError("modalities differ from locked output")

    narrative = str(report["narrative"]).lower()
    forbidden = (
        "caused by",
        "guaranteed",
        "will survive",
        "treatment should",
        "recommend treatment",
        "proves",
    )
    if any(term in narrative for term in forbidden):
        raise ReportingContractError("narrative contains a prohibited causal, certainty or treatment claim")

