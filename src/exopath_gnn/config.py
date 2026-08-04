"""Configuration loading and freeze-time validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ConfigurationError(ValueError):
    """Raised when a protocol configuration violates a frozen contract."""


def load_config(path: str | Path) -> dict[str, Any]:
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_config(config)
    return config


def validate_config(config: dict[str, Any]) -> None:
    required = {
        "protocol_version",
        "seed",
        "status",
        "endpoint",
        "cohorts",
        "development_split",
        "leakage_controls",
        "abstention",
        "benchmark",
        "reporting",
    }
    missing = sorted(required.difference(config))
    if missing:
        raise ConfigurationError(f"missing top-level keys: {', '.join(missing)}")

    if config["status"] != "prospective_protocol":
        raise ConfigurationError("status must remain 'prospective_protocol' until results exist")

    horizons = config["endpoint"].get("horizons_months", [])
    intervals = config["endpoint"].get("interval_end_months", [])
    if not horizons or horizons != sorted(set(horizons)):
        raise ConfigurationError("horizons_months must be unique and increasing")
    if intervals != sorted(set(intervals)) or not set(horizons).issubset(intervals):
        raise ConfigurationError("interval ends must be unique, increasing and cover horizons")

    split = config["development_split"]
    if set(split) != {"train", "tuning", "calibration"}:
        raise ConfigurationError("development splits must be train, tuning and calibration")
    if any(float(value) <= 0 for value in split.values()):
        raise ConfigurationError("development split proportions must be positive")
    if abs(sum(float(value) for value in split.values()) - 1.0) > 1e-9:
        raise ConfigurationError("development split proportions must sum to 1")

    leakage = config["leakage_controls"]
    if leakage.get("partition_unit") != "patient":
        raise ConfigurationError("partition_unit must be patient")
    if leakage.get("fit_preprocessing_on") != "train_only":
        raise ConfigurationError("preprocessing must be fitted on train_only")
    if leakage.get("external_outcomes_opened") != "once_after_freeze":
        raise ConfigurationError("external outcomes must be opened once after freeze")

    benchmark = config["benchmark"]
    if not benchmark.get("same_features") or not benchmark.get("same_parameter_budget"):
        raise ConfigurationError("benchmark branches must share features and parameter budget")
    if benchmark.get("quantum_advantage_assumed"):
        raise ConfigurationError("the protocol must not assume quantum advantage")

    reporting = config["reporting"]
    if reporting.get("numeric_source") != "locked_survival_head":
        raise ConfigurationError("reports must use the locked survival head")
    if reporting.get("allow_treatment_recommendations") or reporting.get("allow_causal_claims"):
        raise ConfigurationError("causal and treatment claims are outside the reporting contract")

