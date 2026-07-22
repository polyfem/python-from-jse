import contextlib
import importlib.util
import io
import sys
import unittest
from pathlib import Path
from unittest import mock


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = PROJECT_ROOT / "tools" / "regenerate_and_test.py"


def import_workflow(module_name="regenerate_and_test_for_test"):
    spec = importlib.util.spec_from_file_location(module_name, WORKFLOW_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RegenerateAndTestWorkflowTests(unittest.TestCase):
    def test_workflow_runs_generation_compile_and_unittest_steps(self):
        workflow = import_workflow()

        with mock.patch.object(workflow.subprocess, "run") as run_mock:
            run_mock.return_value = mock.Mock(returncode=0)

            with contextlib.redirect_stdout(io.StringIO()):
                result = workflow.main([])

        self.assertEqual(0, result)
        commands = [call.args[0] for call in run_mock.call_args_list]
        self.assertEqual(
            [
                [
                    sys.executable,
                    "tools\\generate_with_overrides.py",
                    "--overrides",
                    "examples\\basic_generation\\generator_overrides.json",
                ],
                [
                    sys.executable,
                    "-m",
                    "py_compile",
                    "generator\\JsonToTreeClass.py",
                    "generated\\generated_class.py",
                    "generated\\generated_api.py",
                ],
                [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
            ],
            commands,
        )
        self.assertTrue(all(call.kwargs["cwd"] == PROJECT_ROOT for call in run_mock.call_args_list))

    def test_workflow_stops_on_first_failed_step(self):
        workflow = import_workflow()

        with mock.patch.object(workflow.subprocess, "run") as run_mock:
            run_mock.return_value = mock.Mock(returncode=7)

            with contextlib.redirect_stdout(io.StringIO()):
                result = workflow.main([])

        self.assertEqual(7, result)
        self.assertEqual(1, run_mock.call_count)


if __name__ == "__main__":
    unittest.main()
