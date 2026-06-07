#!/usr/bin/env python3
"""Static repository testability checker for AI coding agents."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


VERSION = "0.1.0"

DEFAULT_CONFIG: Dict[str, Any] = {
    "max_repo_size_mb": 500,
    "max_files_scan": 5000,
    "treat_swift_as_unsupported_in_docker": True,
    "require_lockfile_for_node_code_tasks": True,
    "allow_docs_only_without_tests": True,
    "external_environment_keywords": [],
    "custom_test_command_hints": [],
    "fail_on_unknown_stack": False,
    "large_repo_warning_mb": 100,
    "monorepo_warning_package_count": 4,
}

DEFAULT_EXTERNAL_KEYWORDS = [
    "real device",
    "hardware",
    "vnc",
    "browser extension store",
    "google apps script",
    "github pages settings",
    "cloud account",
    "api key",
    "admin account",
    "paid saas",
    "production credentials",
    "manual-only validation",
    "mobile device",
    "simulator required",
    "xcode required",
    "android emulator",
]

IGNORED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    "target",
    "build",
    "dist",
    ".next",
    ".turbo",
    "coverage",
    "cookies",
    "keychain",
}

SENSITIVE_NAMES = {
    ".env",
    "state.json",
    "cookies",
    "keychain",
}

TEXT_EXTENSIONS = {
    ".md",
    ".mdx",
    ".rst",
    ".txt",
    ".json",
    ".toml",
    ".ini",
    ".cfg",
    ".yaml",
    ".yml",
    ".py",
    ".js",
    ".ts",
    ".go",
    ".rs",
    ".swift",
}

CODE_MARKERS = {
    "node": ["package.json"],
    "python": ["pyproject.toml", "requirements.txt", "setup.py", "setup.cfg", "pytest.ini", "tox.ini"],
    "go": ["go.mod"],
    "rust": ["Cargo.toml"],
    "swift": ["Package.swift"],
    "java": ["pom.xml", "build.gradle", "build.gradle.kts", "settings.gradle"],
}

LOCKFILES = {
    "package-lock.json": "npm",
    "pnpm-lock.yaml": "pnpm",
    "yarn.lock": "yarn",
    "poetry.lock": "poetry",
    "uv.lock": "uv",
    "Cargo.lock": "cargo",
    "go.sum": "go",
    "Package.resolved": "swift-package",
}

RECOMMENDATION_EXIT_CODES = {
    "good_for_agent": 0,
    "docs_only": 1,
    "manual_setup_needed": 1,
    "avoid": 2,
}


def load_config(config_path: Optional[Path]) -> Dict[str, Any]:
    config = dict(DEFAULT_CONFIG)
    if config_path:
        with config_path.open("r", encoding="utf-8") as handle:
            loaded = json.load(handle)
        if not isinstance(loaded, dict):
            raise ValueError("Config file must contain a JSON object.")
        config.update(loaded)
    return config


def write_config(output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(DEFAULT_CONFIG, handle, indent=2)
        handle.write("\n")


def is_sensitive_path(path: Path) -> bool:
    lowered_parts = {part.lower() for part in path.parts}
    if lowered_parts.intersection(SENSITIVE_NAMES):
        return True
    lowered_name = path.name.lower()
    return any(token in lowered_name for token in ("token", "credential", "secret"))


def should_skip_dir(dirname: str) -> bool:
    return dirname in IGNORED_DIRS or dirname.lower() in IGNORED_DIRS


def collect_files(root: Path, max_files: int) -> Tuple[List[Path], int, int, bool]:
    files: List[Path] = []
    total_size = 0
    total_count = 0
    truncated = False

    for current_root, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if not should_skip_dir(d)]
        current = Path(current_root)
        for name in names:
            path = current / name
            if is_sensitive_path(path.relative_to(root)):
                continue
            total_count += 1
            try:
                total_size += path.stat().st_size
            except OSError:
                continue
            if len(files) < max_files:
                files.append(path)
            else:
                truncated = True

    return files, total_count, total_size, truncated


def rel_names(root: Path, files: Sequence[Path]) -> List[str]:
    return [str(path.relative_to(root)).replace(os.sep, "/") for path in files]


def has_file(names: Sequence[str], filename: str) -> bool:
    return filename in names


def has_basename(names: Sequence[str], basename: str) -> bool:
    return any(name.rsplit("/", 1)[-1] == basename for name in names)


def has_dir(root: Path, dirname: str) -> bool:
    return (root / dirname).is_dir()


def read_text(path: Path, max_bytes: int = 200_000) -> str:
    try:
        if path.stat().st_size > max_bytes:
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def load_json_file(path: Path) -> Dict[str, Any]:
    try:
        loaded = json.loads(read_text(path))
    except json.JSONDecodeError:
        return {}
    return loaded if isinstance(loaded, dict) else {}


def detect_stacks(root: Path, names: Sequence[str]) -> List[str]:
    stacks: List[str] = []
    for stack, markers in CODE_MARKERS.items():
        if any(has_file(names, marker) or has_basename(names, marker) for marker in markers):
            stacks.append(stack)

    docs_present = detect_docs(root, names)
    if docs_present and not stacks:
        stacks.append("docs")

    return stacks or ["unknown"]


def detect_docs(root: Path, names: Sequence[str]) -> bool:
    if has_file(names, "README.md") or has_basename(names, "README.md") or has_dir(root, "docs"):
        return True
    return any(Path(name).suffix.lower() in {".md", ".mdx", ".rst"} for name in names)


def detect_package_managers(root: Path, names: Sequence[str], stacks: Sequence[str]) -> List[str]:
    managers: List[str] = []

    if "node" in stacks:
        node_managers = []
        for lock_name, manager in (
            ("package-lock.json", "npm"),
            ("pnpm-lock.yaml", "pnpm"),
            ("yarn.lock", "yarn"),
        ):
            if has_basename(names, lock_name):
                node_managers.append(manager)
        managers.extend(node_managers or ["unknown"])

    if "python" in stacks:
        python_managers = []
        if has_basename(names, "poetry.lock") or pyproject_has(root / "pyproject.toml", "[tool.poetry"):
            python_managers.append("poetry")
        if has_basename(names, "uv.lock"):
            python_managers.append("uv")
        if has_basename(names, "requirements.txt") or (root / "pyproject.toml").exists():
            python_managers.append("pip")
        managers.extend(sorted(set(python_managers)) or ["unknown"])

    if "go" in stacks:
        managers.append("go")
    if "rust" in stacks:
        managers.append("cargo")
    if "swift" in stacks:
        managers.append("swift-package")
    if "java" in stacks:
        managers.append("unknown")

    unique: List[str] = []
    for manager in managers:
        if manager not in unique:
            unique.append(manager)
    return unique or ["none"]


def pyproject_has(path: Path, needle: str) -> bool:
    if not path.exists():
        return False
    return needle.lower() in read_text(path).lower()


def detect_lockfiles(names: Sequence[str]) -> List[str]:
    found = []
    for lock_name in LOCKFILES:
        if has_basename(names, lock_name):
            found.append(lock_name)
    return found


def package_json_scripts(path: Path) -> Dict[str, str]:
    data = load_json_file(path)
    scripts = data.get("scripts", {})
    if not isinstance(scripts, dict):
        return {}
    return {str(key): str(value) for key, value in scripts.items()}


def detect_test_commands(root: Path, files: Sequence[Path], names: Sequence[str], stacks: Sequence[str], config: Dict[str, Any]) -> List[str]:
    commands: List[str] = []

    if "node" in stacks:
        for package_path in sorted(root.glob("**/package.json")):
            if any(should_skip_dir(part) for part in package_path.relative_to(root).parts):
                continue
            scripts = package_json_scripts(package_path)
            for script_name in ("test", "lint", "typecheck", "build"):
                if script_name in scripts:
                    prefix = "" if package_path.parent == root else f"cd {package_path.parent.relative_to(root)} && "
                    commands.append(f"{prefix}npm run {script_name}")

    if "python" in stacks:
        has_pytest_config = (
            has_basename(names, "pytest.ini")
            or pyproject_has(root / "pyproject.toml", "[tool.pytest")
            or pyproject_has(root / "pyproject.toml", "pytest")
        )
        has_tests_dir = any("/tests/" in f"/{name}/" or name.startswith("tests/") for name in names)
        has_test_files = any(Path(name).name.startswith("test_") and Path(name).suffix == ".py" for name in names)
        if has_pytest_config or has_tests_dir or has_test_files:
            commands.append("python -m pytest")
        if any(Path(name).name.endswith("_test.py") for name in names):
            commands.append("python -m unittest discover")

    if "go" in stacks:
        if has_basename(names, "go.mod") or any(name.endswith("_test.go") for name in names):
            commands.append("go test ./...")

    if "rust" in stacks:
        cargo_toml = root / "Cargo.toml"
        has_rust_tests = any("/tests/" in f"/{name}/" for name in names)
        for path in files:
            if path.suffix == ".rs" and "#[test]" in read_text(path):
                has_rust_tests = True
                break
        if cargo_toml.exists() or has_rust_tests:
            commands.append("cargo test")

    if "swift" in stacks and has_basename(names, "Package.swift"):
        commands.append("swift test")

    for hint in config.get("custom_test_command_hints", []):
        if isinstance(hint, str) and hint.strip():
            commands.append(hint.strip())

    unique: List[str] = []
    for command in commands:
        if command not in unique:
            unique.append(command)
    return unique


def detect_external_environment(root: Path, files: Sequence[Path], config: Dict[str, Any]) -> List[str]:
    keywords = [kw.lower() for kw in DEFAULT_EXTERNAL_KEYWORDS]
    for keyword in config.get("external_environment_keywords", []):
        if isinstance(keyword, str) and keyword.strip():
            keywords.append(keyword.lower())

    matches: List[str] = []
    negation_re = re.compile(r"\b(does not|do not|without|never|no|not|required: no)\b")

    for path in files:
        relative = path.relative_to(root)
        if path.suffix.lower() not in TEXT_EXTENSIONS or is_sensitive_path(relative):
            continue
        text = read_text(path)
        if not text:
            continue
        for line in text.splitlines():
            lowered = line.lower()
            for keyword in keywords:
                if keyword in lowered:
                    if negation_re.search(lowered):
                        continue
                    label = f"{keyword} ({relative})"
                    if label not in matches:
                        matches.append(label)
    return matches


def estimate_package_count(root: Path, names: Sequence[str]) -> int:
    package_markers = {
        "package.json",
        "pyproject.toml",
        "Cargo.toml",
        "go.mod",
        "Package.swift",
        "pom.xml",
        "build.gradle",
        "build.gradle.kts",
    }
    return sum(1 for name in names if Path(name).name in package_markers)


def detect_generated_files(root: Path, names: Sequence[str]) -> bool:
    generated_markers = ("generated", "dist/", "build/", ".next/", "coverage/")
    return any(any(marker in name for marker in generated_markers) for name in names)


def docker_suitability(stacks: Sequence[str], risk_flags: Sequence[str], config: Dict[str, Any]) -> str:
    if "external environment required" in risk_flags:
        return "not suitable without manual environment setup"
    if "swift" in stacks and config.get("treat_swift_as_unsupported_in_docker", True):
        return "unsupported by default for Docker-style agent validation"
    if "unsupported stack" in risk_flags or "no clear test path" in risk_flags:
        return "weak"
    return "likely suitable for static preflight and local test planning"


def missing_commands(stacks: Sequence[str], test_commands: Sequence[str]) -> List[str]:
    expected = []
    if "node" in stacks:
        for command in ("test", "lint", "typecheck", "build"):
            if not any(command in found for found in test_commands):
                expected.append(f"node:{command}")
    if "python" in stacks and not any("pytest" in found or "unittest" in found for found in test_commands):
        expected.append("python:test")
    if "go" in stacks and not any("go test" in found for found in test_commands):
        expected.append("go:test")
    if "rust" in stacks and not any("cargo test" in found for found in test_commands):
        expected.append("rust:test")
    if "swift" in stacks and not any("swift test" in found for found in test_commands):
        expected.append("swift:test")
    return expected


def choose_recommendation(
    stacks: Sequence[str],
    package_managers: Sequence[str],
    lockfiles: Sequence[str],
    test_commands: Sequence[str],
    risk_flags: Sequence[str],
    docs_present: bool,
    config: Dict[str, Any],
) -> str:
    risk_set = set(risk_flags)
    recognized_code_stack = any(stack in {"node", "python", "go", "rust", "swift", "java"} for stack in stacks)

    if "repo too large" in risk_set or "external environment required" in risk_set:
        return "avoid"
    if "swift" in stacks and config.get("treat_swift_as_unsupported_in_docker", True):
        return "avoid"
    if "unknown" in stacks and config.get("fail_on_unknown_stack", False):
        return "avoid"
    if "unknown" in stacks and not docs_present:
        return "avoid"
    if not recognized_code_stack and docs_present and config.get("allow_docs_only_without_tests", True):
        return "docs_only"
    if "no clear test path" in risk_set:
        if docs_present and config.get("allow_docs_only_without_tests", True):
            return "docs_only"
        return "avoid"
    if "unsupported stack" in risk_set:
        return "avoid"
    if any(flag in risk_set for flag in ("no lockfile", "monorepo", "unknown package manager", "multiple package managers", "no package manager")):
        return "manual_setup_needed"
    if recognized_code_stack and test_commands:
        return "good_for_agent"
    if docs_present and config.get("allow_docs_only_without_tests", True):
        return "docs_only"
    return "avoid"


def confidence_for(recommendation: str, risk_flags: Sequence[str]) -> float:
    base = {
        "good_for_agent": 0.88,
        "docs_only": 0.72,
        "manual_setup_needed": 0.66,
        "avoid": 0.78,
    }[recommendation]
    penalty = min(0.25, 0.03 * len(risk_flags))
    return round(max(0.35, base - penalty), 2)


def analyze_repository(
    path: Path,
    config: Dict[str, Any],
    max_files_scan: Optional[int] = None,
    repo_size_limit_mb: Optional[int] = None,
) -> Dict[str, Any]:
    root = path.resolve()
    if not root.exists() or not root.is_dir():
        raise FileNotFoundError(f"Repository path does not exist or is not a directory: {root}")

    effective_max_files = int(max_files_scan or config.get("max_files_scan", DEFAULT_CONFIG["max_files_scan"]))
    effective_size_limit_mb = int(repo_size_limit_mb or config.get("max_repo_size_mb", DEFAULT_CONFIG["max_repo_size_mb"]))

    files, total_count, total_size, truncated = collect_files(root, effective_max_files)
    names = rel_names(root, files)
    stacks = detect_stacks(root, names)
    docs_present = detect_docs(root, names)
    package_managers = detect_package_managers(root, names, stacks)
    lockfiles = detect_lockfiles(names)
    test_commands = detect_test_commands(root, files, names, stacks, config)
    external_matches = detect_external_environment(root, files, config)
    package_count = estimate_package_count(root, names)
    repo_size_mb = round(total_size / (1024 * 1024), 2)

    risk_flags: List[str] = []
    if "unknown" in stacks:
        risk_flags.append("unsupported stack")
    if repo_size_mb > effective_size_limit_mb:
        risk_flags.append("repo too large")
    elif repo_size_mb > float(config.get("large_repo_warning_mb", DEFAULT_CONFIG["large_repo_warning_mb"])):
        risk_flags.append("large repo")
    if external_matches:
        risk_flags.append("external environment required")
    if "node" in stacks and config.get("require_lockfile_for_node_code_tasks", True):
        if not any(lock in lockfiles for lock in ("package-lock.json", "pnpm-lock.yaml", "yarn.lock")):
            risk_flags.append("no lockfile")
    if not test_commands and any(stack not in {"docs", "unknown"} for stack in stacks):
        risk_flags.append("no test command")
        risk_flags.append("no clear test path")
    if package_count >= int(config.get("monorepo_warning_package_count", DEFAULT_CONFIG["monorepo_warning_package_count"])):
        risk_flags.append("monorepo")
    if package_managers == ["none"]:
        risk_flags.append("no package manager")
    if "unknown" in package_managers and any(stack not in {"docs", "unknown"} for stack in stacks):
        risk_flags.append("unknown package manager")
    known_managers = [manager for manager in package_managers if manager not in {"none", "unknown"}]
    if len(known_managers) > 1:
        risk_flags.append("multiple package managers")
    if detect_generated_files(root, names):
        risk_flags.append("generated files")
    if truncated or total_count > effective_max_files:
        risk_flags.append("file scan limit reached")
    if (root / ".github" / "workflows").is_dir() and not any(stack not in {"docs", "unknown"} for stack in stacks):
        risk_flags.append("workflow-only repo")

    # Preserve order while deduplicating.
    risk_flags = list(dict.fromkeys(risk_flags))

    recommendation = choose_recommendation(
        stacks,
        package_managers,
        lockfiles,
        test_commands,
        risk_flags,
        docs_present,
        config,
    )
    exit_code = RECOMMENDATION_EXIT_CODES[recommendation]

    suggested_next_steps = suggested_steps(recommendation, risk_flags, stacks)
    missing = missing_commands(stacks, test_commands)

    result = {
        "recommendation": recommendation,
        "exit_code": exit_code,
        "confidence": confidence_for(recommendation, risk_flags),
        "repository": {
            "path": str(root),
            "detected_stack": stacks[0],
            "detected_stacks": stacks,
            "package_manager": package_managers[0],
            "package_managers": package_managers,
            "lockfile": lockfiles[0] if lockfiles else None,
            "lockfiles": lockfiles,
            "repo_size_estimate_mb": repo_size_mb,
            "file_count_estimate": total_count,
            "files_scanned": len(files),
            "scan_truncated": truncated,
        },
        "testability": {
            "test_commands_found": test_commands,
            "missing_commands": missing,
            "docker_suitability": docker_suitability(stacks, risk_flags, config),
            "static_only_note": "No dependency install, build, test, Docker, API, or upload command was executed.",
            "external_environment_matches": external_matches,
        },
        "risk_flags": risk_flags,
        "suggested_next_steps": suggested_next_steps,
    }
    return result


def suggested_steps(recommendation: str, risk_flags: Sequence[str], stacks: Sequence[str]) -> List[str]:
    steps: List[str] = []
    if recommendation == "good_for_agent":
        steps.append("Run the discovered test commands in an isolated environment before modifying code.")
        steps.append("Give the AI agent the lockfile, test command, and expected edit scope.")
    elif recommendation == "docs_only":
        steps.append("Limit AI work to documentation, examples, or comments unless a test path is added.")
        steps.append("Add a minimal automated test command before requesting code changes.")
    elif recommendation == "manual_setup_needed":
        steps.append("Document dependency setup and required test commands before assigning agent work.")
        steps.append("Add or refresh lockfiles where possible.")
    else:
        steps.append("Avoid autonomous code changes until the external setup or test path is clarified.")
        steps.append("Ask a human maintainer for validation requirements.")

    if "external environment required" in risk_flags:
        steps.append("Replace manual environment requirements with mocks, fixtures, or a documented local sandbox.")
    if "swift" in stacks:
        steps.append("For Swift repositories, document Xcode, simulator, and device requirements explicitly.")
    if "monorepo" in risk_flags:
        steps.append("Analyze the specific package path instead of the entire monorepo.")
    return steps


def markdown_report(result: Dict[str, Any]) -> str:
    repo = result["repository"]
    testability = result["testability"]

    lines = [
        "# Testability Doctor Report",
        "",
        "## Result",
        "",
        f"- recommendation: {result['recommendation']}",
        f"- exit code: {result['exit_code']}",
        f"- confidence: {result['confidence']}",
        "",
        "## Repository",
        "",
        f"- path: {repo['path']}",
        f"- detected stack: {', '.join(repo['detected_stacks'])}",
        f"- package manager: {', '.join(repo['package_managers'])}",
        f"- lockfile: {', '.join(repo['lockfiles']) if repo['lockfiles'] else 'none'}",
        f"- repo size estimate: {repo['repo_size_estimate_mb']} MB",
        f"- file count estimate: {repo['file_count_estimate']}",
        f"- files scanned: {repo['files_scanned']}",
        "",
        "## Testability",
        "",
        f"- test commands found: {', '.join(testability['test_commands_found']) if testability['test_commands_found'] else 'none'}",
        f"- missing commands: {', '.join(testability['missing_commands']) if testability['missing_commands'] else 'none'}",
        f"- Docker suitability: {testability['docker_suitability']}",
        f"- static-only note: {testability['static_only_note']}",
        "",
        "## Risk Flags",
        "",
    ]
    if result["risk_flags"]:
        lines.extend(f"- {flag}" for flag in result["risk_flags"])
    else:
        lines.append("- none")
    lines.extend(["", "## Suggested Next Steps", ""])
    lines.extend(f"- {step}" for step in result["suggested_next_steps"])
    lines.append("")
    return "\n".join(lines)


def write_output(content: str, output_path: Optional[Path]) -> None:
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
    else:
        print(content, end="")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="testability-doctor",
        description="Check whether a repository is practical for AI coding agents to modify and test.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze = subparsers.add_parser("analyze", help="Analyze a repository with static checks.")
    analyze.add_argument("--path", required=True, help="Repository path to analyze.")
    analyze.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Output format.")
    analyze.add_argument("--output", help="Write output to this path instead of stdout.")
    analyze.add_argument("--config", help="Optional JSON config path.")
    analyze.add_argument("--max-files-scan", type=int, default=None, help="Maximum number of files to inspect.")
    analyze.add_argument("--repo-size-limit-mb", type=int, default=None, help="Maximum allowed repository size in MB.")

    init_config = subparsers.add_parser("init-config", help="Write a default config file.")
    init_config.add_argument("--output", default="testability-doctor.config.json", help="Config output path.")

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "init-config":
        write_config(Path(args.output))
        print(f"Wrote config: {args.output}")
        return 0

    if args.command == "analyze":
        try:
            config = load_config(Path(args.config) if args.config else None)
            result = analyze_repository(
                Path(args.path),
                config,
                max_files_scan=args.max_files_scan,
                repo_size_limit_mb=args.repo_size_limit_mb,
            )
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"testability-doctor: {exc}", file=sys.stderr)
            return 2

        if args.format == "json":
            content = json.dumps(result, indent=2) + "\n"
        else:
            content = markdown_report(result)
        write_output(content, Path(args.output) if args.output else None)
        return int(result["exit_code"])

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
