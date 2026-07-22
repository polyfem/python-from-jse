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
        self.assertIn("windows-latest", workflow)
        self.assertIn("actions/checkout@v4", workflow)
        self.assertIn("actions/setup-python@v5", workflow)
        self.assertIn('python-version: "3.11"', workflow)
        self.assertIn("python tools\\regenerate_and_test.py", workflow)

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

        self.assertIn("## Standalone Repo Readiness", readme)
        self.assertIn(".github/workflows/ci.yml", readme)
        self.assertIn("python tools\\regenerate_and_test.py", readme)
        self.assertIn("Packaging metadata can be added later", readme)


if __name__ == "__main__":
    unittest.main()
