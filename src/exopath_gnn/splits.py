"""Deterministic patient-level partitioning."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path
from typing import Iterable, Mapping


class SplitError(ValueError):
    """Raised when patient isolation cannot be guaranteed."""


def _uniform(patient_id: str, seed: int) -> float:
    digest = hashlib.sha256(f"{seed}|{patient_id}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") / float(2**64)


def assignment_digest(patient_id: str, split: str, seed: int) -> str:
    return hashlib.sha256(f"{seed}|{patient_id}|{split}".encode("utf-8")).hexdigest()


def assign_patient_splits(
    records: Iterable[Mapping[str, str]],
    proportions: Mapping[str, float],
    seed: int,
) -> list[dict[str, str]]:
    """Assign one row per patient; records marked external bypass development splits."""

    rows = [dict(record) for record in records]
    patient_ids = [row["patient_id"] for row in rows]
    if len(patient_ids) != len(set(patient_ids)):
        raise SplitError("input must contain exactly one row per patient")

    ordered = ["train", "tuning", "calibration"]
    if set(proportions) != set(ordered):
        raise SplitError("proportions must define train, tuning and calibration")
    total = sum(float(proportions[name]) for name in ordered)
    if abs(total - 1.0) > 1e-9:
        raise SplitError("development proportions must sum to one")

    cumulative: list[tuple[str, float]] = []
    running = 0.0
    for name in ordered:
        running += float(proportions[name])
        cumulative.append((name, running))

    manifest: list[dict[str, str]] = []
    for row in sorted(rows, key=lambda item: item["patient_id"]):
        if row.get("cohort_role") == "external":
            split = "external"
        else:
            value = _uniform(row["patient_id"], seed)
            split = next(name for name, threshold in cumulative if value < threshold)
        manifest.append(
            {
                "patient_id": row["patient_id"],
                "cohort": row.get("cohort", "[UNSPECIFIED]"),
                "site": row.get("site", "[UNSPECIFIED]"),
                "split": split,
                "assignment_sha256": assignment_digest(row["patient_id"], split, seed),
            }
        )
    assert_patient_isolation(manifest)
    return manifest


def assert_patient_isolation(manifest: Iterable[Mapping[str, str]]) -> None:
    seen: dict[str, str] = {}
    for row in manifest:
        patient_id = row["patient_id"]
        split = row["split"]
        if patient_id in seen and seen[patient_id] != split:
            raise SplitError(f"patient {patient_id!r} occurs in multiple splits")
        seen[patient_id] = split


def write_manifest(path: str | Path, manifest: Iterable[Mapping[str, str]]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["patient_id", "cohort", "site", "split", "assignment_sha256"]
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(manifest)

