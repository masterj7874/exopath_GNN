"""Budget-matched protocol heads used by the synthetic dry run."""

from __future__ import annotations

import math
from typing import Sequence


def parameter_count(feature_dim: int, intervals: int) -> int:
    if feature_dim <= 0 or intervals <= 0:
        raise ValueError("feature_dim and intervals must be positive")
    return (feature_dim + 1) * intervals


def _validate(weights: Sequence[Sequence[float]], bias: Sequence[float], features: Sequence[float]) -> None:
    if len(weights) != len(bias):
        raise ValueError("one weight row and bias are required per interval")
    if any(len(row) != len(features) for row in weights):
        raise ValueError("weight rows must match the feature dimension")


def classical_logits(
    features: Sequence[float],
    weights: Sequence[Sequence[float]],
    bias: Sequence[float],
) -> tuple[float, ...]:
    _validate(weights, bias, features)
    return tuple(
        sum(float(value) * float(weight) for value, weight in zip(features, row)) + float(offset)
        for row, offset in zip(weights, bias)
    )


def angle_encoded_protocol_logits(
    features: Sequence[float],
    weights: Sequence[Sequence[float]],
    bias: Sequence[float],
) -> tuple[float, ...]:
    """Same-budget local simulator; this is not quantum hardware execution."""

    _validate(weights, bias, features)
    encoded = [math.sin(float(value)) for value in features]
    return tuple(
        sum(value * float(weight) for value, weight in zip(encoded, row)) + float(offset)
        for row, offset in zip(weights, bias)
    )


def assert_budget_matched(
    classical_weights: Sequence[Sequence[float]],
    classical_bias: Sequence[float],
    angle_weights: Sequence[Sequence[float]],
    angle_bias: Sequence[float],
) -> None:
    classical = sum(len(row) for row in classical_weights) + len(classical_bias)
    angle = sum(len(row) for row in angle_weights) + len(angle_bias)
    if classical != angle:
        raise ValueError(f"parameter budgets differ: classical={classical}, angle={angle}")

