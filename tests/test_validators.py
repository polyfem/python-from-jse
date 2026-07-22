import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests.generator_test_helpers import PROJECT_ROOT, import_generator
from validators import api_aliases, id_relationships


EXAMPLES_DIR = PROJECT_ROOT / "examples"
BASIC_GENERATION_DIR = EXAMPLES_DIR / "basic_generation"
CONFIG_CAPABILITIES_DIR = EXAMPLES_DIR / "config_capabilities"
ALIASES_PATH = CONFIG_CAPABILITIES_DIR / "api_aliases.example.json"
RELATIONSHIPS_PATH = CONFIG_CAPABILITIES_DIR / "id_relationships.example.json"
GENERATED_DIR = PROJECT_ROOT / "generated"
CLASS_TREE_MANIFEST_PATH = GENERATED_DIR / "class_tree_manifest.json"
GENERATED_API_MANIFEST_PATH = GENERATED_DIR / "generated_api_manifest.json"


def load_json(path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def generate_example_manifests(tmp_path):
    generator = import_generator("json_to_tree_validator_example_manifests")
    generator.generate(
        schema_file=BASIC_GENERATION_DIR / "input-spec.json",
        output_file=tmp_path / "generated_class.py",
        api_output_file=tmp_path / "generated_api.py",
        generator_overrides_file=BASIC_GENERATION_DIR / "generator_overrides.json",
        manifest_dir=tmp_path,
    )
    return (
        load_json(tmp_path / "class_tree_manifest.json"),
        load_json(tmp_path / "generated_api_manifest.json"),
    )


class ApiAliasesValidatorTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        tmp_path = Path(self.tmpdir.name)
        _class_manifest, self.api_manifest = generate_example_manifests(tmp_path)
        self.api_aliases = load_json(ALIASES_PATH)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_default_aliases_path_uses_generic_example_config(self):
        self.assertEqual(ALIASES_PATH, api_aliases.DEFAULT_ALIASES_PATH)

    def test_default_generated_manifest_path_uses_standalone_generated_dir(self):
        self.assertEqual(
            GENERATED_API_MANIFEST_PATH,
            api_aliases.DEFAULT_GENERATED_API_MANIFEST_PATH,
        )

    def test_default_api_aliases_match_generated_api_manifest(self):
        issues = api_aliases.validate_api_aliases_against_manifest(
            self.api_aliases,
            self.api_manifest,
        )

        self.assertEqual([], issues)

    def test_default_api_aliases_file_only_contains_generator_input(self):
        self.assertEqual({"api_aliases"}, set(self.api_aliases))

    def test_unknown_alias_class_path_is_reported(self):
        config = dict(self.api_aliases)
        config["api_aliases"] = [dict(item) for item in self.api_aliases["api_aliases"]]
        config["api_aliases"][0] = dict(config["api_aliases"][0])
        config["api_aliases"][0]["aliases"] = [
            dict(item) for item in config["api_aliases"][0]["aliases"]
        ]
        config["api_aliases"][0]["aliases"][0]["alias_class_path"] = (
            "Root.Scene.Items.DoesNotExist"
        )

        issues = api_aliases.validate_api_aliases_against_manifest(
            config,
            self.api_manifest,
        )

        self.assertTrue(
            any("alias_class_path not found" in issue for issue in issues),
            issues,
        )

    def test_alias_name_must_match_current_generated_api_name(self):
        config = dict(self.api_aliases)
        config["api_aliases"] = [dict(item) for item in self.api_aliases["api_aliases"]]
        config["api_aliases"][0] = dict(config["api_aliases"][0])
        config["api_aliases"][0]["aliases"] = [
            dict(item) for item in config["api_aliases"][0]["aliases"]
        ]
        config["api_aliases"][0]["aliases"][0]["alias_name"] = "stale_alias_name"

        issues = api_aliases.validate_api_aliases_against_manifest(
            config,
            self.api_manifest,
        )

        self.assertTrue(
            any("alias_name mismatch" in issue for issue in issues),
            issues,
        )

    def test_main_reports_success(self):
        with (
            mock.patch.object(api_aliases, "check_files", return_value=[]),
            mock.patch.object(api_aliases, "load_json", return_value={"api_aliases": [1, 2]}),
        ):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                result = api_aliases.main([])

        self.assertEqual(0, result)
        self.assertIn("OK: 2 api alias item(s)", stdout.getvalue())

    def test_main_reports_validation_failure(self):
        with mock.patch.object(api_aliases, "check_files", return_value=["bad alias"]):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                result = api_aliases.main([])

        self.assertEqual(1, result)
        self.assertIn("FAILED: api aliases validation found issues", stdout.getvalue())
        self.assertIn("bad alias", stdout.getvalue())


class IdRelationshipsValidatorTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        tmp_path = Path(self.tmpdir.name)
        self.class_manifest, self.api_manifest = generate_example_manifests(tmp_path)
        self.relationships = load_json(RELATIONSHIPS_PATH)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_default_relationships_path_uses_generic_example_config(self):
        self.assertEqual(
            RELATIONSHIPS_PATH,
            id_relationships.DEFAULT_RELATIONSHIPS_PATH,
        )

    def test_default_generated_manifest_paths_use_standalone_generated_dir(self):
        self.assertEqual(
            CLASS_TREE_MANIFEST_PATH,
            id_relationships.DEFAULT_CLASS_TREE_MANIFEST_PATH,
        )
        self.assertEqual(
            GENERATED_API_MANIFEST_PATH,
            id_relationships.DEFAULT_GENERATED_API_MANIFEST_PATH,
        )

    def test_default_relationships_match_generated_manifests(self):
        issues = id_relationships.validate_relationships_against_manifests(
            self.relationships,
            self.class_manifest,
            self.api_manifest,
        )

        self.assertEqual([], issues)

    def test_invalid_consumer_path_is_reported(self):
        relationships = [dict(item) for item in self.relationships]
        relationships[0]["consumer"] = "output.missing_id"

        issues = id_relationships.validate_relationships_against_manifests(
            relationships,
            self.class_manifest,
            self.api_manifest,
        )

        self.assertTrue(
            any(
                "consumer" in issue and "output.missing_id" in issue
                for issue in issues
            ),
            issues,
        )

    def test_main_reports_success(self):
        with (
            mock.patch.object(id_relationships, "check_files", return_value=[]),
            mock.patch.object(id_relationships, "load_json", return_value=[1, 2, 3]),
        ):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                result = id_relationships.main([])

        self.assertEqual(0, result)
        self.assertIn("OK: 3 id relationship(s)", stdout.getvalue())

    def test_main_reports_validation_failure(self):
        with mock.patch.object(id_relationships, "check_files", return_value=["bad relationship"]):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                result = id_relationships.main([])

        self.assertEqual(1, result)
        self.assertIn("FAILED: id relationship validation found issues", stdout.getvalue())
        self.assertIn("bad relationship", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
