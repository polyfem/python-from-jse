import contextlib
import importlib.util
import os
import types
from pathlib import Path
from unittest import mock


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GENERATOR_PATH = PROJECT_ROOT / "generator" / "JsonToTreeClass.py"
GENERATED_PATH = PROJECT_ROOT / "generated" / "generated_class.py"
RUNNER_PATH = PROJECT_ROOT / "tools" / "generate_with_overrides.py"
FIXTURE_SPEC_DIR = PROJECT_ROOT / "tests" / "fixtures" / "specs"
DEFAULT_POLYFEM_SPEC_DIR = PROJECT_ROOT.parent / "external" / "polyfem" / "json-specs"
POLYFEM_SPEC_DIR = Path(os.environ.get("POLYFEM_SPEC_DIR", DEFAULT_POLYFEM_SPEC_DIR))
FULL_SPEC_SCHEMA_FILE = POLYFEM_SPEC_DIR / "input-spec.json"
DEFAULT_POLYFEM_INCLUDE_SPEC_DIRS = []
POLYFEM_INCLUDE_SPEC_DIRS = [
    Path(path)
    for path in os.environ.get(
        "POLYFEM_INCLUDE_SPEC_DIRS",
        os.pathsep.join(str(path) for path in DEFAULT_POLYFEM_INCLUDE_SPEC_DIRS),
    ).split(os.pathsep)
    if path
]
POLYFEM_LINKED_SPEC_FILES = (
    "linear-solver-spec.json",
    "nonlinear-solver-spec.json",
)


def polyfem_linked_specs_available():
    return all(
        any((include_dir / spec_file).exists() for include_dir in POLYFEM_INCLUDE_SPEC_DIRS)
        for spec_file in POLYFEM_LINKED_SPEC_FILES
    )


def import_generator(module_name):
    spec = importlib.util.spec_from_file_location(module_name, GENERATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def import_runner(module_name):
    spec = importlib.util.spec_from_file_location(module_name, RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def module_from_generated_text(text):
    module = types.ModuleType("generated_for_test")
    exec(compile(text, "generated_for_test.py", "exec"), module.__dict__)
    return module


def module_from_generated_api_text(text, root_class):
    module = types.ModuleType("generated_api_for_test")
    module.__file__ = str(
        PROJECT_ROOT / "generated" / "generated_api_for_test.py"
    )
    module.__package__ = ""
    generated_class = types.ModuleType("generated_class")
    generated_class.Root = root_class
    module.__dict__["Root"] = root_class
    with contextlib.ExitStack() as stack:
        stack.enter_context(mock.patch.dict(
            "sys.modules",
            {"generated_class": generated_class, module.__name__: module},
        ))
        exec(compile(text, "generated_api_for_test.py", "exec"), module.__dict__)
    return module
