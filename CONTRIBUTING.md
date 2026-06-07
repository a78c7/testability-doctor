# Contributing

## Detector Changes

When adding or changing detection behavior:

- add or update a focused `unittest` case
- explain the expected recommendation
- document new config fields
- avoid dependency installation or external calls
- keep static analysis deterministic

## Pull Requests

Use the pull request template. In particular, answer whether the change adds dependency installation, external calls, or secret reading.

## Local Checks

```bash
python3 -m unittest discover -s tests
bash package-release.sh
```
