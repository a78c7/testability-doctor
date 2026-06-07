# Quickstart

## Run the CLI

```bash
python3 testability_doctor.py analyze --path examples/node-package-lock
```

Expected result: `good_for_agent` with exit code `0`.

## Get JSON

```bash
python3 testability_doctor.py analyze --path examples/node-no-lockfile --format json
```

Expected result: `manual_setup_needed` with exit code `1`.

## Write a report

```bash
python3 testability_doctor.py analyze --path examples/python-pytest --output examples/sample-report.md
```

## Create a config

```bash
python3 testability_doctor.py init-config --output testability-doctor.config.json
```

## Package a release

```bash
bash package-release.sh
```

The release package is written to `dist/testability-doctor-0.1.0.zip`.
