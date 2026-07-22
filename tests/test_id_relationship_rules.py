import importlib.util
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_RELATIONSHIPS = (
    PROJECT_ROOT
    / "examples"
    / "config_capabilities"
    / "id_relationships.example.json"
)
RELATIONSHIP_MODULE_PATH = PROJECT_ROOT / "generator" / "id_relationships.py"


def import_id_relationships(module_name="id_relationships_for_test"):
    spec = importlib.util.spec_from_file_location(module_name, RELATIONSHIP_MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class IdRelationshipRulesTests(unittest.TestCase):
    def test_default_relationships_file_uses_generic_example_config(self):
        relationships_module = import_id_relationships()

        self.assertEqual(
            EXAMPLE_RELATIONSHIPS,
            relationships_module.DEFAULT_RELATIONSHIPS_FILE,
        )

    def test_default_relationships_include_generic_item_output_binding(self):
        relationships_module = import_id_relationships()

        relationships = relationships_module.load_id_relationships()

        self.assertEqual(
            [
                {
                    "namespace": "volume",
                    "producer": "scene.items[*].id",
                    "consumer": "output.selected_item_id",
                    "builder_api": "entity.output",
                    "status": "required",
                }
            ],
            relationships,
        )

    def test_relationships_by_builder_api_finds_generic_consumer(self):
        relationships_module = import_id_relationships()

        relationships = relationships_module.load_id_relationships()
        by_api = relationships_module.relationships_by_builder_api(relationships)

        self.assertEqual("output.selected_item_id", by_api["entity.output"]["consumer"])
        self.assertEqual("scene.items[*].id", by_api["entity.output"]["producer"])

    def test_consumer_root_sections_are_derived_from_relationship_map(self):
        relationships_module = import_id_relationships()

        relationships = relationships_module.load_id_relationships(statuses={"required"})

        self.assertEqual(["output"], relationships_module.consumer_root_sections(relationships))

    def test_validator_rejects_missing_required_field(self):
        relationships_module = import_id_relationships()

        with self.assertRaisesRegex(ValueError, "relationship 0.*consumer"):
            relationships_module.validate_id_relationships([
                {
                    "namespace": "volume",
                    "producer": "scene.items[*].id",
                    "builder_api": "entity.output",
                    "status": "required",
                }
            ])

    def test_load_can_filter_to_required_relationships(self):
        relationships_module = import_id_relationships()

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "relationships.json"
            path.write_text(
                """
[
  {
    "namespace": "volume",
    "producer": "scene.items[*].id",
    "consumer": "output.selected_item_id",
    "builder_api": "entity.output",
    "status": "required"
  },
  {
    "namespace": "surface",
    "producer": "scene.items[*].surface_id",
    "consumer": "output.selected_surface_id",
    "builder_api": "surface.output",
    "status": "supported_later"
  }
]
""".strip(),
                encoding="utf-8",
            )

            required = relationships_module.load_id_relationships(
                path,
                statuses={"required"},
            )

        self.assertEqual(1, len(required))
        self.assertEqual("entity.output", required[0]["builder_api"])


if __name__ == "__main__":
    unittest.main()
