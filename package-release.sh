#!/usr/bin/env bash
set -u

VERSION="0.1.0"
ZIP_PATH="dist/testability-doctor-${VERSION}.zip"

run() {
  echo "+ $*"
  "$@"
}

expect_exit() {
  local expected="$1"
  shift
  echo "+ $* # expected exit ${expected}"
  set +e
  "$@"
  local actual="$?"
  set -e
  if [ "$actual" -ne "$expected" ]; then
    echo "Expected exit ${expected}, got ${actual}: $*" >&2
    exit 1
  fi
}

set -e

run python3 -m unittest discover -s tests
expect_exit 0 python3 testability_doctor.py analyze --path examples/node-package-lock
expect_exit 1 python3 testability_doctor.py analyze --path examples/node-no-lockfile --format json
expect_exit 0 python3 testability_doctor.py analyze --path examples/python-pytest --output examples/sample-report.md
expect_exit 2 python3 testability_doctor.py analyze --path examples/external-env
run python3 testability_doctor.py init-config --output examples/generated-config.json

mkdir -p dist
rm -f "$ZIP_PATH"

FILES=(
  README.md
  QUICKSTART.md
  CHANGELOG.md
  LICENSE
  PRODUCT_REPORT.md
  OPEN_SOURCE_READY_REPORT.md
  GITHUB_OPEN_SOURCE_REPORT.md
  SECURITY.md
  CONTRIBUTING.md
  CODE_OF_CONDUCT.md
  testability_doctor.py
  testability-doctor.config.example.json
  pyproject.toml
  .github
  docs
  examples
  tests
  package-release.sh
)

if command -v zip >/dev/null 2>&1; then
  zip -qr "$ZIP_PATH" "${FILES[@]}" \
    -x "*.git*" "*.env*" "*node_modules*" "*__pycache__*" "*state.json*" "*cookies*" "*keychain*" "*token*" "*credential*" "*.secret"
else
  python3 - "$ZIP_PATH" "${FILES[@]}" <<'PY'
import os
import sys
import zipfile
from pathlib import Path

zip_path = Path(sys.argv[1])
inputs = [Path(arg) for arg in sys.argv[2:]]
excluded = (".git", ".env", "node_modules", "__pycache__", "state.json", "cookies", "keychain", "token", "credential", ".secret")

def include(path):
    lowered = str(path).lower()
    return not any(part in lowered for part in excluded)

with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
    for item in inputs:
        if item.is_dir():
            for root, dirs, files in os.walk(item):
                dirs[:] = [d for d in dirs if include(Path(root) / d)]
                for name in files:
                    path = Path(root) / name
                    if include(path):
                        archive.write(path, path.as_posix())
        elif item.exists() and include(item):
            archive.write(item, item.as_posix())
PY
fi

echo "Created $ZIP_PATH"
