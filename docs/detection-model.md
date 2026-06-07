# Detection Model

Testability Doctor uses static repository signals. It does not install dependencies or execute package-manager commands.

## Stack Detection

The detector recognizes:

- Node: `package.json`
- Python: `pyproject.toml`, `requirements.txt`, `setup.py`, `setup.cfg`, `pytest.ini`, `tox.ini`
- Go: `go.mod`
- Rust: `Cargo.toml`
- Swift: `Package.swift`
- Java: `pom.xml`, `build.gradle`, `build.gradle.kts`
- Docs: `README.md`, `docs/`, `*.md`, `*.mdx`, `*.rst`
- Unknown: no recognized stack or docs signal

## Package Managers

Node lockfiles map to npm, pnpm, or yarn. Python signals map to pip, poetry, or uv. Go, Rust, and Swift map to their standard package ecosystems.

## Lockfiles

Recognized lockfiles:

- `package-lock.json`
- `pnpm-lock.yaml`
- `yarn.lock`
- `poetry.lock`
- `uv.lock`
- `Cargo.lock`
- `go.sum`
- `Package.resolved`

## Test Commands

The detector extracts likely test commands from package scripts and stack markers:

- Node: `test`, `lint`, `typecheck`, `build` scripts
- Python: pytest config, `tests/`, `test_*.py`, or unittest-style files
- Go: `go test ./...`
- Rust: `cargo test`
- Swift: `swift test`

## External Environment Signals

Text files are scanned for practical blockers such as device requirements, cloud account dependencies, browser extension store validation, manual-only validation, Xcode requirements, and emulator requirements. Common sensitive paths are skipped.
