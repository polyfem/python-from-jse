"""Regenerate outputs, compile key files, and run the full unit test suite."""

import argparse
from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def workflow_commands():
    return [
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
    ]


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Regenerate generated outputs and run verification checks.",
    )
    parser.parse_args(argv)

    for command in workflow_commands():
        print("+ " + " ".join(command), flush=True)
        result = subprocess.run(command, cwd=PROJECT_ROOT)
        if result.returncode != 0:
            return result.returncode

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
