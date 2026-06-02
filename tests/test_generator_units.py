import importlib.util
import types
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GENERATOR_PATH = PROJECT_ROOT / "generator" / "JsonToTreeClass.py"
GENERATED_PATH = PROJECT_ROOT / "generated" / "generated_class.py"


def import_generator(module_name):
    spec = importlib.util.spec_from_file_location(module_name, GENERATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def module_from_generated_text(text):
    module = types.ModuleType("generated_for_test")
    exec(compile(text, "generated_for_test.py", "exec"), module.__dict__)
    return module


class GeneratorUnitTests(unittest.TestCase):
    def test_import_does_not_regenerate_output(self):
        before = GENERATED_PATH.stat().st_mtime_ns

        import_generator("json_to_tree_import_guard")

        self.assertEqual(before, GENERATED_PATH.stat().st_mtime_ns)

    def test_entry_type_name_accepts_current_and_legacy_keys(self):
        generator = import_generator("json_to_tree_type_name")

        self.assertEqual("Mesh", generator.entry_type_name({"type_name": "Mesh"}))
        self.assertEqual("mesh", generator.entry_type_name({"#type_name": "mesh"}))
        self.assertIsNone(generator.entry_type_name({"type": "object"}))

    def test_type_name_defaults_limit_discriminator_enum(self):
        generator = import_generator("json_to_tree_type_defaults")
        node = generator.JsonToTreeClass("MooneyRivlin")
        node.type = "object"
        node.type_name = "MooneyRivlin"
        node.add_required("type")
        type_node = node.get_required("type")
        type_node.type = "string"
        type_node.add_optional("NeoHookean")
        type_node.add_optional("MooneyRivlin")

        generator.apply_type_name_defaults(node)

        self.assertEqual("MooneyRivlin", type_node.default)
        self.assertEqual(["MooneyRivlin"], list(type_node._optional))

    def test_prune_variant_fields_keeps_only_declared_variant_fields(self):
        generator = import_generator("json_to_tree_prune_fields")
        node = generator.JsonToTreeClass("MooneyRivlin")
        node.type = "object"
        node.type_name = "MooneyRivlin"
        node.variant_fields = ["type", "c1", "c2", "k", "id", "rho"]
        for field in ("type", "c1", "c2", "k"):
            node.add_required(field)
        for field in ("id", "rho", "models", "E"):
            node.add_optional(field)

        generator.prune_variant_fields(node)

        self.assertEqual(["type", "c1", "c2", "k"], list(node._required))
        self.assertEqual(["id", "rho"], list(node._optional))

    def test_polymorphic_primitives_use_python_types(self):
        generator = import_generator("json_to_tree_primitive_mapping")
        node = generator.JsonToTreeClass("c1")
        node.type = "polymorphic"
        node.add_optional("float")
        node.add_optional("string")
        node.add_optional("object3")

        generated = node.class_generator("C1")

        self.assertIn("class_check(value, [float, str, self.Object3])", generated)
        self.assertNotIn("self.String", generated)

    def test_build_tree_applies_type_name_variant_rules(self):
        generator = import_generator("json_to_tree_build_tree")
        root = generator.build_tree([
            {
                "pointer": "/",
                "type": "object",
                "optional": ["materials"],
            },
            {
                "pointer": "/materials",
                "type": "list",
            },
            {
                "pointer": "/materials/*",
                "type": "object",
                "type_name": "MooneyRivlin",
                "required": ["type", "c1", "c2", "k"],
                "optional": ["id", "rho"],
            },
            {
                "pointer": "/materials/*/type",
                "type": "string",
                "options": ["NeoHookean", "MooneyRivlin"],
            },
            {
                "pointer": "/materials/*/c1",
                "type": "float",
            },
            {
                "pointer": "/materials/*/c2",
                "type": "float",
            },
            {
                "pointer": "/materials/*/k",
                "type": "float",
            },
            {
                "pointer": "/materials/*/rho",
                "type": "float",
            },
            {
                "pointer": "/materials/*/models",
                "type": "list",
            },
        ])

        materials = root.get_optional("materials")
        material = materials.get_optional("MooneyRivlin")
        type_node = material.get_required("type")

        self.assertEqual("MooneyRivlin", material.type_name)
        self.assertEqual(["type", "c1", "c2", "k"], list(material._required))
        self.assertEqual(["id", "rho"], list(material._optional))
        self.assertEqual("MooneyRivlin", type_node.default)
        self.assertEqual(["MooneyRivlin"], list(type_node._optional))

    def test_parameter_unions_are_inlined_in_variant_classes(self):
        generator = import_generator("json_to_tree_inline_parameters")
        root = generator.build_tree([
            {
                "pointer": "/",
                "type": "object",
                "optional": ["materials"],
            },
            {
                "pointer": "/materials",
                "type": "list",
            },
            {
                "pointer": "/materials/*",
                "type": "object",
                "type_name": "MooneyRivlin",
                "required": ["type", "c1", "k"],
                "optional": ["id", "rho"],
            },
            {
                "pointer": "/materials/*/type",
                "type": "string",
                "options": ["NeoHookean", "MooneyRivlin"],
            },
            {
                "pointer": "/materials/*/c1",
                "type": "include",
                "spec_file": "value-no.json",
            },
            {
                "pointer": "/materials/*/k",
                "type": "include",
                "spec_file": "value-no.json",
            },
            {
                "pointer": "/materials/*/id",
                "type": "int",
                "default": 0,
            },
            {
                "pointer": "/materials/*/id",
                "type": "list",
            },
            {
                "pointer": "/materials/*/id/*",
                "type": "int",
            },
            {
                "pointer": "/materials/*/rho",
                "type": "include",
                "spec_file": "value1.json",
            },
        ])
        generated = generator.generated_class_text(root)
        mooney_block = generated[
            generated.index("        class MooneyRivlin(object):"):
        ]

        self.assertNotIn("class C1(object):", mooney_block)
        self.assertNotIn("class K(object):", mooney_block)
        self.assertNotIn("class Id(object):", mooney_block)
        self.assertNotIn("class Rho(object):", mooney_block)

        generated_module = module_from_generated_text(generated)
        material = generated_module.Root.Materials.MooneyRivlin(
            c1=1.0,
            k={"value": 3.0, "unit": "Pa"},
            id=[1, 2],
            rho="density_expr",
        )

        self.assertEqual(
            {
                "type": "MooneyRivlin",
                "c1": 1.0,
                "k": {"value": 3.0, "unit": "Pa"},
                "id": [1, 2],
                "rho": "density_expr",
            },
            material.as_dict(),
        )


if __name__ == "__main__":
    unittest.main()
