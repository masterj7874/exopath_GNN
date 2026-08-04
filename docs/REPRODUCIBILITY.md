# Reproducibility contract

The v1.0.1 release verifies software contracts on synthetic data. A real-cohort
analysis is reproducible only after the following items are frozen before any
external-test outcome is inspected:

1. target population, index date, endpoint, censoring rules and horizons;
2. immutable patient and file UUID manifests for every cohort;
3. patient-level train, tuning, calibration and external assignments;
4. every fitted preprocessing object and its training-only provenance;
5. graph schema, relation sources and temporal cut-off checks;
6. comparator identity, feature dimension, parameter count, seeds, tuning
   budget, loss and stopping rule;
7. calibration method, shift threshold and abstention rules;
8. interpreter, libraries, accelerator driver, container digest and hardware;
9. output schema, prompt version and exact locked numerical inputs; and
10. hashes for configuration, manifests, predictions, failures and audit logs.

Run the local contract suite with:

```bash
python -m unittest discover -s tests -v
```

Run the synthetic dry run with:

```bash
python scripts/run_protocol_demo.py --output artifacts/demo
```

The generated `provenance.json` records the seed, platform, Python version and
SHA-256 hashes of the frozen configuration and graph schema.
