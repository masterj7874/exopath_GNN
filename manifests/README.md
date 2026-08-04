# Split manifests

`synthetic_example_split.csv` illustrates the release format using generated
patient identifiers only. It contains no real cohort identifiers.

Required columns are:

- `patient_id`: a study-local pseudonymous identifier;
- `cohort`: the frozen cohort label;
- `site`: the site label used for held-out checks;
- `split`: one of `train`, `tuning`, `calibration`, or `external`;
- `assignment_sha256`: digest of the seed, patient identifier and assignment.

All slides, tiles, repeated samples and linked records for one patient must map
to the same split. External-cohort patients must never appear in a development
split.

