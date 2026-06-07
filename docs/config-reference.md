# Config Reference

The default config is available in `testability-doctor.config.example.json`.

## Fields

`max_repo_size_mb`: repository size above this limit returns `avoid`.

`max_files_scan`: maximum number of files to inspect.

`treat_swift_as_unsupported_in_docker`: marks Swift repositories as unsupported for default Docker-style agent validation.

`require_lockfile_for_node_code_tasks`: Node repositories without a lockfile return `manual_setup_needed`.

`allow_docs_only_without_tests`: allows docs-only repositories to return `docs_only`.

`external_environment_keywords`: extra lowercase or mixed-case phrases that should be treated as external environment requirements.

`custom_test_command_hints`: extra test commands to include in reports.

`fail_on_unknown_stack`: unknown repositories return `avoid` even if docs are present.

`large_repo_warning_mb`: size threshold for a warning flag before the hard size limit.

`monorepo_warning_package_count`: package marker count that triggers the monorepo risk flag.

## Example

```json
{
  "max_repo_size_mb": 500,
  "max_files_scan": 5000,
  "treat_swift_as_unsupported_in_docker": true,
  "require_lockfile_for_node_code_tasks": true,
  "allow_docs_only_without_tests": true,
  "external_environment_keywords": ["staging tenant"],
  "custom_test_command_hints": ["make test"],
  "fail_on_unknown_stack": false,
  "large_repo_warning_mb": 100,
  "monorepo_warning_package_count": 4
}
```
