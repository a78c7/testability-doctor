# Security Policy

## Scope

Testability Doctor is a static repository inspection CLI. It is designed to avoid side effects while estimating whether a repository is practical for AI coding agents.

## Safety Boundaries

- No dependency installation.
- No project builds.
- No package-manager test execution.
- No external service calls.
- No uploads.
- No credential, cookie, keychain, state store, or secret folder reads.
- No payout, tax, KYC, payment, or sponsorship handling.

## Reporting Issues

Open a GitHub issue with:

- the command you ran
- the expected recommendation
- the actual recommendation
- a minimal repository shape or fixture

Never paste secrets, credential material, cookies, or private account data into an issue.
