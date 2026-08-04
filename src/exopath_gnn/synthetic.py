"""Deterministic synthetic records for software contract tests only."""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class SyntheticPatient:
    patient_id: str
    cohort: str
    cohort_role: str
    site: str
    features: tuple[float, ...]
    event_interval: int
    event_observed: bool
    modality_mask: dict[str, bool]


def generate_synthetic_patients(
    development_count: int = 48,
    external_count: int = 12,
    seed: int = 20260804,
) -> list[SyntheticPatient]:
    if development_count < 3 or external_count < 1:
        raise ValueError("synthetic run requires development and external patients")
    generator = random.Random(seed)
    patients: list[SyntheticPatient] = []
    modalities = ("wsi", "omics", "clinical", "exposure")
    total = development_count + external_count
    for index in range(total):
        external = index >= development_count
        shift = 0.45 if external else 0.0
        features = tuple(generator.gauss(shift, 1.0) for _ in range(4))
        latent = 0.6 * features[0] - 0.3 * features[1] + 0.2 * features[2] + generator.gauss(0.0, 0.5)
        event_interval = 0 if latent > 0.8 else 1 if latent > 0.0 else 2
        event_observed = generator.random() > 0.25
        mask = {name: generator.random() > (0.12 if name != "clinical" else 0.03) for name in modalities}
        role = "external" if external else "development"
        prefix = "SYN-EXT" if external else "SYN-DEV"
        patients.append(
            SyntheticPatient(
                patient_id=f"{prefix}-{index + 1:04d}",
                cohort="synthetic_external" if external else "synthetic_development",
                cohort_role=role,
                site="synthetic_site_c" if external else ("synthetic_site_a" if index % 2 == 0 else "synthetic_site_b"),
                features=features,
                event_interval=event_interval,
                event_observed=event_observed,
                modality_mask=mask,
            )
        )
    return patients

