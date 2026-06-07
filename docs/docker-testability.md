# Docker Testability

Testability Doctor does not run Docker by default.

The CLI answers a narrower question: does the repository look like it could be tested in an isolated agent environment after normal setup?

## Why static only?

Running Docker or package-manager commands can be slow, require network access, or trigger side effects. A static preflight is safer as the first step.

## Signals for Docker suitability

Positive signals:

- recognized stack
- lockfile or simple non-Node project
- clear test command
- no external environment requirement

Negative signals:

- real device or emulator requirements
- cloud account dependencies
- unsupported stack for default container validation
- missing test path
- large or monorepo shape without package focus

Swift is marked unsupported by default for Docker-style validation because many Swift projects depend on Xcode, simulators, or platform-specific tooling.
