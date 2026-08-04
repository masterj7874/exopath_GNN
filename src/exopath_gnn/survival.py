"""Discrete-time censoring-aware survival utilities."""

from __future__ import annotations

import math
from typing import Sequence


def sigmoid(value: float) -> float:
    if value >= 0:
        exponent = math.exp(-value)
        return 1.0 / (1.0 + exponent)
    exponent = math.exp(value)
    return exponent / (1.0 + exponent)


def hazards_from_logits(logits: Sequence[float]) -> tuple[float, ...]:
    return tuple(sigmoid(float(value)) for value in logits)


def survival_from_hazards(hazards: Sequence[float]) -> tuple[float, ...]:
    survival: list[float] = []
    probability = 1.0
    for hazard in hazards:
        value = float(hazard)
        if not 0.0 <= value <= 1.0:
            raise ValueError("hazards must lie in [0, 1]")
        probability *= 1.0 - value
        survival.append(probability)
    return tuple(survival)


def discrete_time_nll(
    logits: Sequence[float],
    terminal_interval: int,
    event_observed: bool,
) -> float:
    """Negative log likelihood for an event or end-of-interval censoring."""

    hazards = hazards_from_logits(logits)
    if terminal_interval < 0 or terminal_interval >= len(hazards):
        raise IndexError("terminal_interval is outside the modeled horizon")
    epsilon = 1e-12
    log_likelihood = 0.0
    stop = terminal_interval if event_observed else terminal_interval + 1
    for hazard in hazards[:stop]:
        log_likelihood += math.log(max(1.0 - hazard, epsilon))
    if event_observed:
        log_likelihood += math.log(max(hazards[terminal_interval], epsilon))
    return -log_likelihood


def brier_score(predicted_event_risk: Sequence[float], observed: Sequence[int]) -> float:
    if len(predicted_event_risk) != len(observed) or not observed:
        raise ValueError("prediction and outcome vectors must have equal non-zero length")
    return sum((float(risk) - int(outcome)) ** 2 for risk, outcome in zip(predicted_event_risk, observed)) / len(observed)


def apply_temperature(logits: Sequence[float], temperature: float) -> tuple[float, ...]:
    if temperature <= 0:
        raise ValueError("temperature must be positive")
    return tuple(float(value) / temperature for value in logits)

