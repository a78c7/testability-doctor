import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

import testability_doctor as doctor


def write(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class TestTestabilityDoctor(unittest.TestCase):
    def analyze(self, root: Path, **config_overrides):
        config = dict(doctor.DEFAULT_CONFIG)
        config.update(config_overrides)
        return doctor.analyze_repository(root, config)

    def test_node_with_package_lock_is_good_for_agent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "package.json", '{"scripts":{"test":"node test.js"}}')
            write(root / "package-lock.json", '{"lockfileVersion": 3}')

            result = self.analyze(root)

        self.assertEqual(result["recommendation"], "good_for_agent")
        self.assertEqual(result["exit_code"], 0)

    def test_node_without_lockfile_needs_manual_setup(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "package.json", '{"scripts":{"test":"node test.js"}}')

            result = self.analyze(root)

        self.assertEqual(result["recommendation"], "manual_setup_needed")
        self.assertIn("no lockfile", result["risk_flags"])

    def test_python_pytest_is_good_for_agent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "pyproject.toml", '[project]\nname = "demo"\n[tool.pytest.ini_options]\ntestpaths = ["tests"]\n')
            write(root / "tests" / "test_sample.py", "def test_sample():\n    assert True\n")

            result = self.analyze(root)

        self.assertEqual(result["recommendation"], "good_for_agent")
        self.assertIn("python -m pytest", result["testability"]["test_commands_found"])

    def test_go_module_is_good_for_agent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "go.mod", "module example.com/demo\n\ngo 1.22\n")
            write(root / "main_test.go", "package main\n\nfunc TestSample(t *testing.T) {}\n")

            result = self.analyze(root)

        self.assertEqual(result["recommendation"], "good_for_agent")
        self.assertIn("go test ./...", result["testability"]["test_commands_found"])

    def test_rust_cargo_is_good_or_manual(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "Cargo.toml", '[package]\nname = "demo"\nversion = "0.1.0"\nedition = "2021"\n')
            write(root / "Cargo.lock", "# placeholder\n")
            write(root / "src" / "lib.rs", "#[test]\nfn it_works() { assert_eq!(2 + 2, 4); }\n")

            result = self.analyze(root)

        self.assertIn(result["recommendation"], {"good_for_agent", "manual_setup_needed"})
        self.assertIn("cargo test", result["testability"]["test_commands_found"])

    def test_swift_defaults_to_avoid(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "Package.swift", "// swift-tools-version: 5.9\n")

            result = self.analyze(root)

        self.assertEqual(result["recommendation"], "avoid")

    def test_unknown_empty_repo_is_avoid(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            result = self.analyze(root)

        self.assertEqual(result["recommendation"], "avoid")

    def test_external_environment_keyword_is_avoid(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "README.md", "Requires a real device, API key, and cloud account for validation.\n")

            result = self.analyze(root)

        self.assertEqual(result["recommendation"], "avoid")
        self.assertIn("external environment required", result["risk_flags"])

    def test_json_output_is_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "package.json", '{"scripts":{"test":"node test.js"}}')
            write(root / "package-lock.json", '{"lockfileVersion": 3}')
            buffer = io.StringIO()

            with contextlib.redirect_stdout(buffer):
                exit_code = doctor.main(["analyze", "--path", str(root), "--format", "json"])

        data = json.loads(buffer.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(data["recommendation"], "good_for_agent")

    def test_markdown_output_contains_recommendation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "README.md", "# Docs\n")
            buffer = io.StringIO()

            with contextlib.redirect_stdout(buffer):
                exit_code = doctor.main(["analyze", "--path", str(root)])

        self.assertEqual(exit_code, 1)
        self.assertIn("recommendation: docs_only", buffer.getvalue())

    def test_init_config_writes_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "config.json"
            buffer = io.StringIO()

            with contextlib.redirect_stdout(buffer):
                exit_code = doctor.main(["init-config", "--output", str(output)])

            config = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 0)
        self.assertEqual(config["max_repo_size_mb"], 500)

    def test_docs_only_repo_returns_docs_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "README.md", "# Documentation\n")
            write(root / "docs" / "guide.md", "Guide\n")

            result = self.analyze(root)

        self.assertEqual(result["recommendation"], "docs_only")

    def test_monorepo_warning_works(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for index in range(4):
                package = root / f"pkg{index}"
                write(package / "package.json", '{"scripts":{"test":"node test.js"}}')
                write(package / "package-lock.json", '{"lockfileVersion": 3}')

            result = self.analyze(root)

        self.assertIn("monorepo", result["risk_flags"])
        self.assertEqual(result["recommendation"], "manual_setup_needed")

    def test_config_override_works(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "Package.swift", "// swift-tools-version: 5.9\n")

            result = self.analyze(root, treat_swift_as_unsupported_in_docker=False)

        self.assertNotEqual(result["recommendation"], "avoid")


if __name__ == "__main__":
    unittest.main()
