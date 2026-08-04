"""Distribution-shift, missingness and abstention checks."""

from __future__ import annotations

import math
from typing import Mapping, Sequence


def standardized_mean_distance(
    reference: Sequence[Sequence[float]],
    candidate: Sequence[Sequence[float]],
) -> float:
    if not reference or not candidate:
        raise ValueError("reference and candidate rows are required")
    dimension = len(reference[0])
    if dimension == 0 or any(len(row) != dimension for row in (*reference, *candidate)):
        raise ValueError("all rows must share a non-zero feature dimension")
    distances: list[float] = []
    for index in range(dimension):
        ref_values = [float(row[index]) for row in reference]
        cand_values = [float(row[index]) for row in candidate]
        ref_mean = sum(ref_values) / len(ref_values)
        cand_mean = sum(cand_values) / len(cand_values)
        variance = sum((value - ref_mean) ** 2 for value in ref_values) / len(ref_values)
        scale = max(math.sqrt(variance), 1e-8)
        distances.append(abs(cand_mean - ref_mean) / scale)
    return sum(distances) / len(distances)


def missing_modality_rate(mask: Mapping[str, bool]) -> float:
    if not mask:
        return 1.0
    missing = sum(1 for available in mask.values() if not bool(available))
    return missing / len(mask)


def abstention_reasons(
    shift_score: float,
    modality_mask: Mapping[str, bool],
    max_shift: float,
    max_missing_rate: float,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if shift_score > max_shift:
        reasons.append("representation_shift_exceeds_frozen_threshold")
    if missing_modality_rate(modality_mask) > max_missing_rate:
        reasons.append("missing_modality_rate_exceeds_frozen_threshold")
    return tuple(reasons)

