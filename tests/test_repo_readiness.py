"""Repository-level readiness checks for the standalone generator repo.

These tests keep CI, packaging metadata, ignored artifacts, README guidance,
and local fixture ownership aligned with the standalone-repo contract.
"""

import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class StandaloneRepoReadinessTests(unittest.TestCase):
    def test_ci_runs_standalone_dummy_generation_workflow(self):
        workflow = (
            PROJECT_ROOT / ".github" / "workflows" / "ci.yml"
        ).read_text(encoding="utf-8")

        self.assertIn("push:", workflow)
        self.assertIn("pull_request:", workflow)
        self.assertIn("strategy:", workflow)
        self.assertIn("fail-fast: false", workflow)
        for runner in ("ubuntu-latest", "macos-latest", "windows-latest"):
            with self.subTest(runner=runner):
                self.assertIn(runner, workflow)
        for python_version in ('"3.10"', '"3.11"', '"3.12"'):
            with self.subTest(python_version=python_version):
                self.assertIn(python_version, workflow)
        self.assertIn("actions/checkout@v4", workflow)
        self.assertIn("actions/setup-python@v5", workflow)
        self.assertIn("python-version: ${{ matrix.python-version }}", workflow)
        self.assertIn("python -m pip install -e .", workflow)
        self.assertIn("python-from-jse-generate --help", workflow)
        self.assertIn("python tools/regenerate_and_test.py", workflow)

    def test_gitignore_keeps_generated_and_local_artifacts_out_of_git(self):
        gitignore = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8")

        required_patterns = [
            "doc/",
            "generated/",
            "__pycache__/",
            "**/__pycache__/",
            ".pytest_cache/",
            ".ruff_cache/",
            ".venv/",
            "build/",
            "dist/",
            "*.egg-info/",
        ]
        for pattern in required_patterns:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, gitignore)

    def test_readme_describes_standalone_repo_readiness_boundary(self):
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("## Testing", readme)
        self.assertIn("## Standalone Repo Readiness", readme)
        self.assertIn(".github/workflows/ci.yml", readme)
        self.assertIn("tests/README.md", readme)
        self.assertIn("python tools/regenerate_and_test.py", readme)
        self.assertIn("python tools\\regenerate_and_test.py", readme)
        self.assertIn("Python 3.10, 3.11, and 3.12", readme)
        for runner_name in ("Ubuntu", "macOS", "Windows"):
            with self.subTest(runner_name=runner_name):
                self.assertIn(runner_name, readme)
        self.assertIn("python-from-jse-generate --help", readme)
        self.assertIn("python -m pip install -e .", readme)

    def test_pyproject_declares_installable_generator_package(self):
        pyproject = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")

        self.assertIn('[build-system]', pyproject)
        self.assertIn('build-backend = "setuptools.build_meta"', pyproject)
        self.assertIn('[project]', pyproject)
        self.assertIn('name = "python-from-jse"', pyproject)
        self.assertIn('requires-python = ">=3.10"', pyproject)
        self.assertIn('[project.scripts]', pyproject)
        self.assertIn(
            'python-from-jse-generate = "tools.generate_with_overrides:main"',
            pyproject,
        )
        self.assertIn(
            'include = ["generator*", "validators*", "tools*", "examples*"]',
            pyproject,
        )

    def test_standalone_include_fixtures_are_inside_repo(self):
        fixture_dir = PROJECT_ROOT / "tests" / "fixtures" / "specs"

        self.assertTrue(fixture_dir.is_dir())
        self.assertTrue(fixture_dir.is_relative_to(PROJECT_ROOT))
        self.assertTrue((fixture_dir / "value-no.json").is_file())
        self.assertTrue((fixture_dir / "value1.json").is_file())
        self.assertTrue((fixture_dir / "boundary-condition.json").is_file())

    def test_tests_readme_documents_test_groups_and_skip_policy(self):
        tests_readme = (PROJECT_ROOT / "tests" / "README.md").read_text(
            encoding="utf-8",
        )

        for heading in (
            "## Main Commands",
            "## Test Groups",
            "## Skip Policy",
            "## Adding Tests",
        ):
            with self.subTest(heading=heading):
                self.assertIn(heading, tests_readme)
        for test_file in (
            "test_generator_units.py",
            "test_generator_runner.py",
            "test_regenerate_and_test.py",
            "test_generated_api.py",
            "test_model_builder.py",
            "test_validators.py",
            "test_id_relationship_rules.py",
            "test_repo_readiness.py",
            "test_generator_examples.py",
            "test_full_spec_smoke.py",
        ):
            with self.subTest(test_file=test_file):
                self.assertIn(test_file, tests_readme)
        self.assertIn("python tools/regenerate_and_test.py", tests_readme)
        self.assertIn("python -m unittest discover -s tests", tests_readme)
        self.assertIn("POLYFEM_SPEC_DIR", tests_readme)


if __name__ == "__main__":
    unittest.main()
