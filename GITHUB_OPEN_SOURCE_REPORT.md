# GitHub Open Source Report

## Repo URL

https://github.com/a78c7/testability-doctor

## Release URL

https://github.com/a78c7/testability-doctor/releases/tag/v0.1.0

## Commit Hash

Initial release and `v0.1.0` tag commit:

```text
8b0196e853a523e7d7722bc37c2ca5dad0cd3ae1
```

## Tag

`v0.1.0`

## Tests Result

Local tests:

```text
python3 -m unittest discover -s tests
Ran 14 tests
OK
```

Package script:

```text
bash package-release.sh
Created dist/testability-doctor-0.1.0.zip
```

## GitHub Actions Status

Workflow: `test`

```text
main push: completed / success
tag push: completed / success
```

Runs:

- https://github.com/a78c7/testability-doctor/actions/runs/27088883462
- https://github.com/a78c7/testability-doctor/actions/runs/27088887545

## Package Asset

Uploaded asset:

```text
name: testability-doctor-0.1.0.zip
size: 30014 bytes
state: uploaded
digest: sha256:c03fdc2da99a23ca5337023af9776a1969eacefc339261828703bd009f460e47
url: https://github.com/a78c7/testability-doctor/releases/download/v0.1.0/testability-doctor-0.1.0.zip
```

## Security Scan Result

Local sensitive filename scan found no matches outside ignored `.git` paths.

Zip asset scan before upload:

```text
.git: 0
.env: 0
node_modules: 0
__pycache__: 0
state.json: 0
cookies: 0
keychain: 0
token: 0
credential: 0
.secret: 0
```

Safety boundaries confirmed:

- No dependency installation was used to evaluate examples.
- No external paid services were called.
- No KYC, payment, withdrawal, tax, or sponsorship setup was performed.
- No GitHub Sponsors setup was enabled.
- Existing `codex-bounty-hunter`, `bountylens`, and `agentgate` project directories were not modified.

## Related Links

- AgentGate: https://github.com/a78c7/agentgate
- BountyLens: https://github.com/a78c7/bountylens

## Next Steps

- Manually inspect the GitHub repository landing page.
- Confirm release notes render as intended.
- Optionally replace the placeholder MIT license author name.
- Optionally add screenshots or terminal GIFs later.
