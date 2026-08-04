# ExoPath-GNN

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21782465.svg)](https://doi.org/10.5281/zenodo.21782465)

Reference implementation and reproducibility scaffold for **“ExoPath-GNN: a
leakage-controlled, shift-aware framework for externally validated
colon-cancer survival triage.”**

## Status and scope

ExoPath-GNN is a **prospective methodological protocol**. This repository does
not contain a trained clinical model, participant-level TCGA, PLCO or PAIP
data, model weights derived from those cohorts, or measured claims of clinical
performance. The included deterministic synthetic example is a software test
of the planned data flow; it is not evidence of discrimination, calibration,
clinical utility, transportability, or quantum advantage.

The release provides:

- deterministic patient-level split manifests with explicit external-cohort
  isolation;
- a versioned typed-graph schema and temporal leakage checks;
- discrete-time censoring-aware survival utilities;
- budget-matched classical and angle-encoded protocol heads;
- shift, missing-modality and abstention checks;
- a locked-output reporting schema that rejects altered numerical claims and
  unsupported causal or treatment language;
- configuration, environment, container and provenance specifications; and
- a standard-library-only synthetic dry run and unit tests.

The angle-encoded head is a local protocol simulator. It is not a quantum
hardware execution and must not be described as demonstrating a quantum
benefit.

## Quick start

Python 3.12 is recommended. The runtime uses only the Python standard library.

```bash
python -m unittest discover -s tests -v
python scripts/run_protocol_demo.py --output artifacts/demo
```

The dry run writes a synthetic split manifest, locked predictions, a summary
and a provenance record. Generated artifacts are excluded from version
control.

## Repository map

```text
config/                 Prespecified protocol configuration
schemas/                Typed graph and locked-report schemas
src/exopath_gnn/        Reference implementation
scripts/                Reproducible command-line entry points
tests/                  Leakage and contract tests
docs/                   Data governance and reproducibility notes
manifests/               Manifest format and synthetic example
container/              Minimal deterministic runtime image
```

## Real-data use

Researchers must obtain TCGA-COAD/READ directly from the NCI Genomic Data
Commons and request PLCO data through the NCI Cancer Data Access System. PAIP
images remain subject to the platform's registration, licence and data-use
terms. This repository neither redistributes nor grants access to any of those
resources. See [docs/DATA_AVAILABILITY.md](docs/DATA_AVAILABILITY.md).

Before any test-set result is opened, users must replace every placeholder in
`config/default.json`, freeze the cohort UUID manifest, endpoint, horizons,
external cohort, comparator, tuning budget, calibration procedure and
abstention thresholds, and archive the resulting configuration and hashes.

## Citation and licence

The exact archived release is available at
[doi:10.5281/zenodo.21782465](https://doi.org/10.5281/zenodo.21782465); the
version-independent concept DOI is
[doi:10.5281/zenodo.21782464](https://doi.org/10.5281/zenodo.21782464).
Citation metadata are provided in `CITATION.cff`. The software is released
under the [MIT License](LICENSE). Dataset licences and cohort governance terms
remain independent of this software licence.
