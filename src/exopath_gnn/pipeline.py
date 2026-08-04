"""End-to-end synthetic protocol dry run."""

from __future__ import annotations

import json
from pathlib import Path

from .benchmark import angle_encoded_protocol_logits, assert_budget_matched, classical_logits
from .config import load_config
from .provenance import write_provenance
from .reporting import LockedPrediction, render_locked_report
from .shift import abstention_reasons, standardized_mean_distance
from .splits import assign_patient_splits, write_manifest
from .survival import discrete_time_nll, hazards_from_logits, survival_from_hazards
from .synthetic import generate_synthetic_patients


def run_protocol_demo(
    output_dir: str | Path,
    config_path: str | Path,
    schema_path: str | Path,
) -> dict:
    config = load_config(config_path)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    seed = int(config["seed"])
    patients = generate_synthetic_patients(seed=seed)
    records = [
        {
            "patient_id": patient.patient_id,
            "cohort": patient.cohort,
            "cohort_role": patient.cohort_role,
            "site": patient.site,
        }
        for patient in patients
    ]
    manifest = assign_patient_splits(records, config["development_split"], seed)
    write_manifest(output / "split_manifest.csv", manifest)

    feature_dim = len(patients[0].features)
    intervals = len(config["endpoint"]["interval_end_months"])
    weights = [
        [((row + 1) * (column + 2) % 7 - 3) / 10.0 for column in range(feature_dim)]
        for row in range(intervals)
    ]
    bias = [-0.8 + 0.2 * row for row in range(intervals)]
    assert_budget_matched(weights, bias, weights, bias)

    development_features = [list(patient.features) for patient in patients if patient.cohort_role == "development"]
    external_features = [list(patient.features) for patient in patients if patient.cohort_role == "external"]
    shift_score = standardized_mean_distance(development_features, external_features)
    predictions_path = output / "locked_predictions.jsonl"
    total_nll = 0.0
    angle_checksum = 0.0
    abstained = 0
    first_report = None
    with predictions_path.open("w", encoding="utf-8") as handle:
        for patient in patients:
            logits = classical_logits(patient.features, weights, bias)
            angle_checksum += sum(angle_encoded_protocol_logits(patient.features, weights, bias))
            total_nll += discrete_time_nll(logits, patient.event_interval, patient.event_observed)
            survival = survival_from_hazards(hazards_from_logits(logits))
            risk = 1.0 - survival[-1]
            triage = "low" if risk < 0.33 else "intermediate" if risk < 0.67 else "high"
            reasons = abstention_reasons(
                shift_score if patient.cohort_role == "external" else 0.0,
                patient.modality_mask,
                float(config["abstention"]["max_standardized_shift"]),
                float(config["abstention"]["max_missing_modality_rate"]),
            )
            locked = LockedPrediction(
                patient_id=patient.patient_id,
                horizon_months=int(config["endpoint"]["horizons_months"][-1]),
                survival_probability=survival[-1],
                risk_probability=risk,
                triage=triage,
                calibration_status="development_only",
                modalities=tuple(name for name, available in patient.modality_mask.items() if available),
                abstained=bool(reasons),
                abstention_reasons=reasons,
            )
            report = render_locked_report(locked)
            if first_report is None:
                first_report = report
            abstained += int(locked.abstained)
            handle.write(json.dumps(report, sort_keys=True) + "\n")

    summary = {
        "status": "synthetic_contract_test_only",
        "patient_count": len(patients),
        "split_counts": {name: sum(row["split"] == name for row in manifest) for name in ("train", "tuning", "calibration", "external")},
        "mean_negative_log_likelihood": total_nll / len(patients),
        "external_shift_score": shift_score,
        "abstained_count": abstained,
        "angle_protocol_checksum": angle_checksum,
        "first_locked_report": first_report,
        "interpretation": "Software contract test only; not a clinical performance result.",
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_provenance(
        output / "provenance.json",
        seed,
        [config_path, schema_path],
        "python scripts/run_protocol_demo.py",
    )
    return summary

