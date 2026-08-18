"""Tests for the generation CLI, default paths, and config-file handling.

These tests cover the standalone default schema, schema patch inputs, optional
project config, and generated package import behavior.
"""

import contextlib
import importlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests.generator_test_helpers import (
    PROJECT_ROOT,
    RUNNER_PATH,
    import_generator,
    import_runner,
    module_from_generated_text,
)


class GeneratorRunnerTests(unittest.TestCase):
    def test_default_paths_target_standalone_example_and_generated_dir(self):
        generator = import_generator("json_to_tree_default_standalone_outputs")

        self.assertEqual(
            PROJECT_ROOT / "examples" / "basic_generation" / "input-spec.json",
            generator.DEFAULT_SCHEMA_FILE,
        )
        self.assertEqual(
            PROJECT_ROOT / "generated" / "generated_class.py",
            generator.DEFAULT_OUTPUT_FILE,
        )
        self.assertEqual(
            PROJECT_ROOT / "generated" / "generated_api.py",
            generator.DEFAULT_API_OUTPUT_FILE,
        )

    def test_generated_api_imports_generated_class_as_package_sibling(self):
        generator = import_generator("json_to_tree_package_import")
        root = generator.build_tree([
            {"pointer": "/", "type": "object", "optional": ["contact"]},
            {"pointer": "/contact", "type": "object", "optional": ["enabled"]},
            {"pointer": "/contact/enabled", "type": "bool", "default": False},
        ])

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            package_root = tmp_path / "polyfempy"
            generated_dir = package_root / "generated_api"
            generator_dir = tmp_path / "python-from-jse" / "generator"
            generated_dir.mkdir(parents=True)
            generator_dir.mkdir(parents=True)
            (package_root / "__init__.py").write_text("", encoding="utf-8")
            (generated_dir / "__init__.py").write_text("", encoding="utf-8")
            (generator_dir / "model_builder.py").write_text(
                "class ModelBuilder:\n"
                "    def __init__(self, api_module):\n"
                "        self.api_module = api_module\n",
                encoding="utf-8",
            )
            (generated_dir / "generated_class.py").write_text(
                generator.generated_class_text(root),
                encoding="utf-8",
            )
            (generated_dir / "generated_api.py").write_text(
                generator.generated_api_text(root),
                encoding="utf-8",
            )

            sys.path.insert(0, str(tmp_path))
            try:
                module = importlib.import_module("polyfempy.generated_api.generated_api")
            finally:
                sys.path.remove(str(tmp_path))
                for name in list(sys.modules):
                    if name.startswith("polyfempy"):
                        sys.modules.pop(name, None)

        self.assertEqual({"contact": {"enabled": True}}, module.config(contact={"enabled": True}).as_dict())

    def test_generated_api_loads_model_builder_without_bare_imports(self):
        generator = import_generator("json_to_tree_pylance_model_builder")
        root = generator.build_tree([
            {"pointer": "/", "type": "object", "optional": ["geometry"]},
            {"pointer": "/geometry", "type": "object"},
        ])

        text = generator.generated_api_text(root)

        self.assertIn("import importlib.util", text)
        self.assertIn("spec_from_file_location", text)
        self.assertIn("model_builder.py", text)
        self.assertNotIn("from model_builder import", text)
        self.assertNotIn("sys.path.insert", text)

    def test_schema_patch_add_field_updates_class_tree_and_report(self):
        generator = import_generator("json_to_tree_schema_patch")
        schema = [
            {"pointer": "/", "type": "object", "optional": ["contact"]},
            {"pointer": "/contact", "type": "object"},
        ]
        overrides = {
            "version": 1,
            "schema_patches": [
                {
                    "id": "contact_temperature",
                    "op": "add_field",
                    "target": "/contact",
                    "name": "temperature",
                    "schema": {
                        "type": "float",
                        "default": 300.0,
                    },
                }
            ],
        }

        patched_schema, report = generator.apply_schema_patches(schema, overrides)
        root = generator.build_tree(patched_schema)
        generated_module = module_from_generated_text(generator.generated_class_text(root))

        self.assertEqual(
            [
                {
                    "id": "contact_temperature",
                    "op": "add_field",
                    "pointer": "/contact/temperature",
                    "status": "applied",
                }
            ],
            report,
        )
        self.assertEqual({}, generated_module.Root.Contact().as_dict())
        self.assertEqual(
            {"temperature": 310.0},
            generated_module.Root.Contact(temperature=310.0).as_dict(),
        )

    def test_schema_patch_add_field_updates_existing_optional_parent(self):
        generator = import_generator("json_to_tree_schema_patch_existing_parent")
        schema = [
            {"pointer": "/", "type": "object", "optional": ["contact"]},
            {"pointer": "/contact", "type": "object", "optional": ["enabled"]},
            {"pointer": "/contact/enabled", "type": "bool", "default": False},
        ]
        overrides = {
            "version": 1,
            "schema_patches": [
                {
                    "id": "contact_temperature",
                    "op": "add_field",
                    "target": "/contact",
                    "name": "temperature",
                    "schema": {
                        "type": "float",
                        "default": 300.0,
                    },
                }
            ],
        }

        patched_schema, _report = generator.apply_schema_patches(schema, overrides)
        root = generator.build_tree(patched_schema)
        generated_module = module_from_generated_text(generator.generated_class_text(root))

        self.assertEqual(
            {"temperature": 310.0},
            generated_module.Root.Contact(temperature=310.0).as_dict(),
        )

    def test_generate_works_without_generator_overrides_file(self):
        generator = import_generator("json_to_tree_no_overrides_generate")
        schema = [
            {"pointer": "/", "type": "object", "optional": ["contact"]},
            {"pointer": "/contact", "type": "object", "optional": ["enabled"]},
            {"pointer": "/contact/enabled", "type": "bool", "default": False},
        ]

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            schema_path = tmp_path / "input.json"
            class_path = tmp_path / "generated_class.py"
            api_path = tmp_path / "generated_api.py"
            schema_path.write_text(json.dumps(schema), encoding="utf-8")

            generator.generate(
                schema_file=schema_path,
                output_file=class_path,
                api_output_file=api_path,
                generator_overrides_file=None,
                manifest_dir=tmp_path,
            )

            self.assertTrue(class_path.exists())
            self.assertTrue(api_path.exists())
            self.assertTrue((tmp_path / "class_tree_manifest.json").exists())
            self.assertTrue((tmp_path / "generated_api_manifest.json").exists())
            self.assertTrue((tmp_path / "schema_patch_report.json").exists())

    def test_generate_with_overrides_runner_applies_override_file(self):
        schema = [
            {"pointer": "/", "type": "object", "optional": ["contact"]},
            {"pointer": "/contact", "type": "object"},
        ]
        overrides = {
            "version": 1,
            "schema_patches": [
                {
                    "id": "contact_temperature",
                    "op": "add_field",
                    "target": "/contact",
                    "name": "temperature",
                    "schema": {"type": "float", "default": 300.0},
                }
            ],
        }

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            schema_path = tmp_path / "input.json"
            overrides_path = tmp_path / "generator_overrides.json"
            class_path = tmp_path / "generated_class.py"
            api_path = tmp_path / "generated_api.py"
            schema_path.write_text(json.dumps(schema), encoding="utf-8")
            overrides_path.write_text(json.dumps(overrides), encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(RUNNER_PATH),
                    "--schema-file",
                    str(schema_path),
                    "--output-file",
                    str(class_path),
                    "--api-output-file",
                    str(api_path),
                    "--manifest-dir",
                    str(tmp_path),
                    "--overrides",
                    str(overrides_path),
                    "--skip-id-relationship-check",
                    "--skip-api-aliases",
                    "--skip-api-alias-check",
                ],
                cwd=PROJECT_ROOT,
                text=True,
                capture_output=True,
            )

            self.assertEqual("", result.stderr)
            self.assertEqual(0, result.returncode)
            self.assertIn("Generated", result.stdout)
            self.assertTrue(class_path.exists())
            self.assertTrue(api_path.exists())
            report = json.loads((tmp_path / "schema_patch_report.json").read_text(encoding="utf-8"))
            self.assertEqual("applied", report[0]["status"])

    def test_generate_with_overrides_runner_defaults_to_standalone_generation(self):
        runner = import_runner("generate_with_overrides_runner_standalone")

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            output_file = tmp_path / "generated_class.py"
            api_output_file = tmp_path / "generated_api.py"
            manifest_dir = tmp_path / "manifests"
            with mock.patch.object(runner, "generate") as generate_mock:
                with mock.patch.object(runner, "write_builder_api_manifest") as builder_manifest_mock:
                    with mock.patch.object(runner, "check_id_relationship_files", return_value=[]) as check_mock:
                        with mock.patch.object(runner, "check_api_aliases_files", return_value=[]) as alias_check_mock:
                            with contextlib.redirect_stdout(io.StringIO()):
                                result = runner.main([
                                    "--schema-file",
                                    str(tmp_path / "input.json"),
                                    "--output-file",
                                    str(output_file),
                                    "--api-output-file",
                                    str(api_output_file),
                                    "--manifest-dir",
                                    str(manifest_dir),
                                ])

        self.assertEqual(0, result)
        generate_mock.assert_called_once()
        builder_manifest_mock.assert_not_called()
        check_mock.assert_not_called()
        alias_check_mock.assert_not_called()

    def test_generate_with_overrides_help_describes_standalone_schema_default(self):
        runner = import_runner("generate_with_overrides_runner_help")

        stdout = io.StringIO()
        with self.assertRaises(SystemExit) as raised:
            with contextlib.redirect_stdout(stdout):
                runner.parse_args(["--help"])

        self.assertEqual(0, raised.exception.code)
        help_text = stdout.getvalue().replace("\\", "/")
        self.assertIn(
            "examples/basic_generation/input-spec.json",
            help_text,
        )
        self.assertNotIn("Defaults to json-specs/input-spec.json", help_text)

    def test_generate_with_overrides_runner_checks_optional_project_config(self):
        runner = import_runner("generate_with_overrides_runner_check")

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            output_file = tmp_path / "generated_class.py"
            api_output_file = tmp_path / "generated_api.py"
            manifest_dir = tmp_path / "manifests"
            relationships_path = tmp_path / "relationships.json"
            aliases_path = tmp_path / "api_aliases.json"
            aliases_path.write_text('{"api_aliases": []}', encoding="utf-8")
            with mock.patch.object(runner, "generate") as generate_mock:
                with mock.patch.object(runner, "write_builder_api_manifest") as builder_manifest_mock:
                    with mock.patch.object(runner, "check_id_relationship_files", return_value=[]) as check_mock:
                        with mock.patch.object(runner, "check_api_aliases_files", return_value=[]) as alias_check_mock:
                            with contextlib.redirect_stdout(io.StringIO()):
                                result = runner.main([
                                    "--schema-file",
                                    str(tmp_path / "input.json"),
                                    "--output-file",
                                    str(output_file),
                                    "--api-output-file",
                                    str(api_output_file),
                                    "--manifest-dir",
                                    str(manifest_dir),
                                    "--relationships",
                                    str(relationships_path),
                                    "--api-aliases",
                                    str(aliases_path),
                                ])

        self.assertEqual(0, result)
        generate_mock.assert_called_once()
        builder_manifest_mock.assert_called_once_with(
            relationships_path,
            manifest_dir / "class_tree_manifest.json",
            manifest_dir / "builder_api_manifest.json",
            model_entry=runner.DEFAULT_MODEL_ENTRY,
        )
        check_mock.assert_called_once_with(
            relationships_path,
            manifest_dir / "class_tree_manifest.json",
            manifest_dir / "generated_api_manifest.json",
        )
        alias_check_mock.assert_called_once_with(
            aliases_path,
            manifest_dir / "generated_api_manifest.json",
        )

    def test_generate_with_overrides_runner_forwards_include_spec_dirs(self):
        runner = import_runner("generate_with_overrides_runner_include_dirs")

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            include_dir = tmp_path / "dependency-specs"
            include_dir.mkdir()
            output_file = tmp_path / "generated_class.py"
            api_output_file = tmp_path / "generated_api.py"
            manifest_dir = tmp_path / "manifests"
            with mock.patch.object(runner, "generate") as generate_mock:
                with contextlib.redirect_stdout(io.StringIO()):
                    result = runner.main([
                        "--schema-file",
                        str(tmp_path / "input.json"),
                        "--include-spec-dir",
                        str(include_dir),
                        "--output-file",
                        str(output_file),
                        "--api-output-file",
                        str(api_output_file),
                        "--manifest-dir",
                        str(manifest_dir),
                    ])

        self.assertEqual(0, result)
        self.assertEqual([include_dir], generate_mock.call_args.kwargs["include_spec_dirs"])

    def test_generate_with_overrides_runner_fails_when_id_relationship_check_fails(self):
        runner = import_runner("generate_with_overrides_runner_check_failure")

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / "api_aliases.json").write_text(
                '{"api_aliases": []}',
                encoding="utf-8",
            )
            with mock.patch.object(runner, "generate"):
                with mock.patch.object(runner, "write_builder_api_manifest"):
                    with mock.patch.object(
                        runner,
                        "check_id_relationship_files",
                        return_value=["consumer path not found"],
                    ):
                        stdout = io.StringIO()
                        with contextlib.redirect_stdout(stdout):
                            result = runner.main([
                                "--schema-file",
                                str(tmp_path / "input.json"),
                                "--output-file",
                                str(tmp_path / "generated_class.py"),
                                "--api-output-file",
                                str(tmp_path / "generated_api.py"),
                                "--manifest-dir",
                                str(tmp_path / "manifests"),
                                "--relationships",
                                str(tmp_path / "relationships.json"),
                            ])

        self.assertEqual(1, result)
        self.assertIn("FAILED: id relationship validation found issues", stdout.getvalue())
        self.assertIn("consumer path not found", stdout.getvalue())

    def test_generate_with_overrides_runner_fails_when_api_alias_check_fails(self):
        runner = import_runner("generate_with_overrides_runner_alias_check_failure")

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / "api_aliases.json").write_text(
                '{"api_aliases": []}',
                encoding="utf-8",
            )
            with mock.patch.object(runner, "generate"):
                with mock.patch.object(runner, "write_builder_api_manifest"):
                    with mock.patch.object(runner, "check_id_relationship_files", return_value=[]):
                        with mock.patch.object(
                            runner,
                            "check_api_aliases_files",
                            return_value=["alias_name mismatch"],
                        ):
                            stdout = io.StringIO()
                            with contextlib.redirect_stdout(stdout):
                                result = runner.main([
                                    "--schema-file",
                                    str(tmp_path / "input.json"),
                                    "--output-file",
                                    str(tmp_path / "generated_class.py"),
                                    "--api-output-file",
                                    str(tmp_path / "generated_api.py"),
                                    "--manifest-dir",
                                    str(tmp_path / "manifests"),
                                    "--api-aliases",
                                    str(tmp_path / "api_aliases.json"),
                                ])

        self.assertEqual(1, result)
        self.assertIn("FAILED: api aliases validation found issues", stdout.getvalue())
        self.assertIn("alias_name mismatch", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
