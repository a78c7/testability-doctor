# Testability Doctor

Testability Doctor is a CLI that checks whether a repository is practical for AI coding agents to modify and test.

It is built for Codex, Claude Code, Cursor, and other AI coding agents that need a quick static preflight before changing code.

## What is Testability Doctor?

Testability Doctor looks at repository structure, package manager signals, lockfiles, test commands, docs, and external-environment hints. It returns a recommendation:

- `good_for_agent`: the repo has a clear stack, test path, and low setup risk.
- `manual_setup_needed`: the repo may be workable, but setup or dependency state is unclear.
- `docs_only`: documentation changes are likely safe, while code changes need more testability.
- `avoid`: autonomous code changes are likely risky without human setup.

## Why AI agents need testability checks

AI coding agents work best when they can make a small change, run a deterministic test command, and inspect the result. Many repositories are not shaped that way. Some lack lockfiles, hide test commands, require devices or cloud accounts, or depend on manual validation. Testability Doctor identifies those conditions before agent time is spent on an unsafe or untestable task.

## Installation

Run from source:

```bash
python3 testability_doctor.py --version
```

Install as a local package:

```bash
python3 -m pip install .
testability-doctor --version
```

The tool has no runtime dependencies outside the Python standard library.

## CLI usage

Analyze a repository and print Markdown:

```bash
python3 testability_doctor.py analyze --path examples/node-package-lock
```

Analyze and print JSON:

```bash
python3 testability_doctor.py analyze --path examples/node-no-lockfile --format json
```

Write a report:

```bash
python3 testability_doctor.py analyze --path examples/python-pytest --output examples/sample-report.md
```

Write a default config:

```bash
python3 testability_doctor.py init-config
```

Use a config file:

```bash
python3 testability_doctor.py analyze --path /path/to/repo --config testability-doctor.config.example.json
```

## Example reports

Markdown output includes:

- result, recommendation, exit code, and confidence
- detected stack, package manager, lockfiles, size, and file count
- discovered test commands and missing commands
- Docker suitability note
- risk flags and suggested next steps

JSON output follows this shape:

```json
{
  "recommendation": "good_for_agent",
  "exit_code": 0,
  "confidence": 0.88,
  "repository": {},
  "testability": {},
  "risk_flags": [],
  "suggested_next_steps": []
}
```

## Recommendation meanings

`good_for_agent` means a coding agent can probably make and test ordinary code changes after normal review.

`manual_setup_needed` means a human should clarify setup, lockfiles, package boundaries, or package manager state before the agent starts.

`docs_only` means docs changes are reasonable, but code changes need a clearer automated test path.

`avoid` means the repo depends on external setup, unsupported validation, unclear tests, or environment requirements that make autonomous changes risky.

Exit codes:

- `0`: `good_for_agent`
- `1`: `warning`, `manual_setup_needed`, or `docs_only`
- `2`: `avoid`

## How to use with Codex / Claude Code / Cursor

Run Testability Doctor before asking an agent to edit a candidate repository:

```bash
python3 testability_doctor.py analyze --path /path/to/candidate --format json
```

Then give the agent:

- the recommendation
- the detected test commands
- the risk flags
- the intended edit scope

For `manual_setup_needed`, ask the agent to inspect and propose setup clarifications before changing code. For `avoid`, keep the task with a human until validation is made local and deterministic.

## How it relates to AgentGate

[AgentGate](https://github.com/a78c7/agentgate) focuses on gating agent work and review boundaries. Testability Doctor runs earlier: it checks whether a repo appears testable enough to send into an agent workflow at all.

## How it relates to BountyLens

[BountyLens](https://github.com/a78c7/bountylens) helps inspect bounty opportunities. Testability Doctor can evaluate the repository behind a bounty before an agent attempts implementation.

## Safety model

Testability Doctor is static by default. It does not install dependencies, build projects, run package-manager commands, call external services, upload files, or read cookies, keychains, state stores, or credential folders. It skips common sensitive paths and only reads ordinary repository text files for static hints.

## What it does not do

- It does not prove that tests pass.
- It does not run Docker.
- It does not install dependencies.
- It does not call external APIs.
- It does not replace human review.
- It does not certify security.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Detector changes should include focused unit tests and explain the safety impact.

## License

MIT License. See [LICENSE](LICENSE).
