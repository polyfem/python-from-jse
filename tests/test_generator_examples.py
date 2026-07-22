import json
import tempfile
import unittest
from pathlib import Path

from generator.id_relationships import validate_id_relationships
from tests.generator_test_helpers import PROJECT_ROOT, import_generator


EXAMPLES_DIR = PROJECT_ROOT / "examples"
BASIC_GENERATION_DIR = EXAMPLES_DIR / "basic_generation"
CONFIG_CAPABILITIES_DIR = EXAMPLES_DIR / "config_capabilities"


def load_json(path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


class GeneratorExamplesTests(unittest.TestCase):
    def test_basic_generation_example_runs_generator(self):
        generator = import_generator("json_to_tree_basic_example")

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            generator.generate(
                schema_file=BASIC_GENERATION_DIR / "input-spec.json",
                output_file=tmp_path / "generated_class.py",
                api_output_file=tmp_path / "generated_api.py",
                generator_overrides_file=BASIC_GENERATION_DIR / "generator_overrides.json",
                manifest_dir=tmp_path,
            )

            class_manifest = load_json(tmp_path / "class_tree_manifest.json")
            api_manifest = load_json(tmp_path / "generated_api_manifest.json")
            patch_report = load_json(tmp_path / "schema_patch_report.json")

        self.assertEqual(
            [
                {
                    "id": "add_output_format",
                    "op": "add_field",
                    "pointer": "/output/format",
                    "status": "applied",
                }
            ],
            patch_report,
        )
        self.assertIn(
            {
                "class_path": "Root.Output",
                "params": ["directory", "selected_item_id", "format"],
            },
            class_manifest,
        )
        self.assertIn(
            {
                "class_path": "Root.Scene.Items.SceneItem",
                "api_generated_name": "scene_item",
                "api_custom_name": None,
                "kind": "auto",
                "source": "generator",
                "exported": False,
                "params": ["name", "id", "enabled"],
            },
            api_manifest,
        )
        self.assertIn(
            {
                "class_path": "Root.Scene.Items.SceneItem",
                "api_generated_name": "scene_item",
                "api_custom_name": "item_definition",
                "kind": "custom_api_name",
                "source": "api_config",
                "exported": True,
                "params": ["name", "id", "enabled"],
            },
            api_manifest,
        )

    def test_config_capability_examples_are_parseable_and_generic(self):
        aliases = load_json(CONFIG_CAPABILITIES_DIR / "api_aliases.example.json")
        patches = load_json(CONFIG_CAPABILITIES_DIR / "schema_patches.example.json")
        relationships = load_json(
            CONFIG_CAPABILITIES_DIR / "id_relationships.example.json"
        )

        self.assertEqual({"api_aliases"}, set(aliases))
        self.assertIsInstance(aliases["api_aliases"], list)
        self.assertGreater(len(aliases["api_aliases"]), 0)
        self.assertIn("main_api_name", aliases["api_aliases"][0])
        self.assertIn("aliases", aliases["api_aliases"][0])
        self.assertEqual({"schema_patches"}, set(patches))
        self.assertIsInstance(patches["schema_patches"], list)
        self.assertGreater(len(patches["schema_patches"]), 0)
        self.assertEqual("add_field", patches["schema_patches"][0]["op"])
        self.assertEqual("/output", patches["schema_patches"][0]["target"])
        self.assertEqual("format", patches["schema_patches"][0]["name"])
        self.assertIn("schema", patches["schema_patches"][0])
        self.assertEqual(relationships, validate_id_relationships(relationships))

        serialized = json.dumps(
            {
                "api_aliases": aliases,
                "schema_patches": patches,
                "id_relationships": relationships,
            }
        ).lower()
        self.assertNotIn("polyfem", serialized)

    def test_examples_readme_separates_generic_examples_from_project_config(self):
        readme = (EXAMPLES_DIR / "README.md").read_text(encoding="utf-8").lower()

        self.assertIn("basic_generation", readme)
        self.assertIn("config_capabilities", readme)
        self.assertIn("generator-config", readme)
        self.assertIn("project-specific", readme)

    def test_tools_readme_documents_standalone_dummy_generation(self):
        readme = (PROJECT_ROOT / "tools" / "README.md").read_text(encoding="utf-8")
        readme_lower = readme.lower()

        self.assertIn("python tools\\regenerate_and_test.py", readme)
        self.assertIn("examples/basic_generation/input-spec.json", readme)
        self.assertIn("examples/basic_generation/generator_overrides.json", readme)
        self.assertIn("generated/generated_class.py", readme)
        self.assertIn("generated/generated_api.py", readme)
        self.assertIn("--schema-file", readme)
        self.assertIn("--include-spec-dir", readme)
        self.assertNotIn("polyfem integration", readme_lower)
        self.assertNotIn("polyfempy/generated_api", readme_lower)

    def test_project_readme_points_to_tools_readme(self):
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("tools/README.md", readme)
        self.assertNotIn("tools/path-config.md", readme)


if __name__ == "__main__":
    unittest.main()
