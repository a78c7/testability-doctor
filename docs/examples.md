# Examples

## `examples/node-package-lock`

Expected: `good_for_agent`

Reason: Node project with `package.json`, `package-lock.json`, and test-related scripts.

## `examples/node-no-lockfile`

Expected: `manual_setup_needed`

Reason: Node project has a test script but no lockfile.

## `examples/python-pytest`

Expected: `good_for_agent`

Reason: Python project has pytest config and a `tests/` directory.

## `examples/go-module`

Expected: `good_for_agent`

Reason: Go module with `go.mod` and `*_test.go`.

## `examples/rust-cargo`

Expected: `good_for_agent`

Reason: Rust project with Cargo files and an inline `#[test]`.

## `examples/swift-unsupported`

Expected: `avoid`

Reason: Swift package is treated as unsupported for default Docker-style validation unless config overrides it.

## `examples/external-env`

Expected: `avoid`

Reason: README describes real device, cloud account, and credential-like setup requirements.
