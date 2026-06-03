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

    def test_polymorphic_list_item_object_stays_inside_list_variant(self):
        generator = import_generator("json_to_tree_list_item_variant")
        root = generator.build_tree([
            {
                "pointer": "/",
                "type": "object",
                "optional": ["space"],
            },
            {
                "pointer": "/space",
                "type": "object",
                "optional": ["discr_order"],
            },
            {
                "pointer": "/space/discr_order",
                "type": "int",
            },
            {
                "pointer": "/space/discr_order",
                "type": "file",
            },
            {
                "pointer": "/space/discr_order",
                "type": "list",
            },
            {
                "pointer": "/space/discr_order/*",
                "type": "object",
                "required": ["id", "order"],
            },
            {
                "pointer": "/space/discr_order/*/id",
                "type": "int",
            },
            {
                "pointer": "/space/discr_order/*/id",
                "type": "list",
            },
            {
                "pointer": "/space/discr_order/*/id/*",
                "type": "int",
            },
            {
                "pointer": "/space/discr_order/*/order",
                "type": "int",
            },
        ])

        discr_order = root.get_optional("space").get_optional("discr_order")
        list_variant = discr_order.get_optional("list")

        self.assertNotIn("object4", discr_order._optional)
        self.assertIn("item", list_variant._optional)

        generated = generator.generated_class_text(root)
        self.assertNotIn("class Object4(object):", generated)
        self.assertIn("class List(object):", generated)
        self.assertIn("class Item(object):", generated)
        self.assertIn("class_check(value, [int, str, list, self.List])", generated)

        generated_module = module_from_generated_text(generated)
        entry = generated_module.Root.Space.Discr_order.List.Item(id=[1, 2], order=3)
        space = generated_module.Root.Space(
            discr_order=generated_module.Root.Space.Discr_order.List(items=[entry])
        )

        self.assertEqual(
            {
                "discr_order": [
                    {"id": [1, 2], "order": 3},
                ],
            },
            space.as_dict(),
        )

    def test_list_item_object_and_primitive_variants_stay_at_list_level(self):
        generator = import_generator("json_to_tree_boundary_item_variants")
        root = generator.build_tree([
            {
                "pointer": "/",
                "type": "object",
                "optional": ["boundary_conditions"],
            },
            {
                "pointer": "/boundary_conditions",
                "type": "object",
                "optional": ["dirichlet_boundary"],
            },
            {
                "pointer": "/boundary_conditions/dirichlet_boundary",
                "type": "include",
                "spec_file": "boundary-condition.json",
            },
            {
                "pointer": "/boundary_conditions/dirichlet_boundary/*",
                "type": "object",
                "required": ["id", "value"],
                "optional": ["time_reference"],
                "doc": "Dirichlet boundary condition.",
            },
            {
                "pointer": "/boundary_conditions/dirichlet_boundary/*",
                "type": "string",
                "doc": "Dirichlet boundary condition loaded from a file",
            },
        ])

        dirichlet = root.get_optional("boundary_conditions").get_optional(
            "dirichlet_boundary"
        )
        item = dirichlet.get_optional("item")

        self.assertEqual("list", dirichlet.type)
        self.assertEqual("object", item.type)
        self.assertIn("string", dirichlet._optional)
        self.assertNotIn("object3", item._optional)

        generated = generator.generated_class_text(root)
        self.assertIn("class_check(i, [self.Item, str])", generated)
        self.assertNotIn("Dirichlet_boundary.Item.Object3", generated)

    def test_list_item_object_entries_merge_with_included_item_fields(self):
        generator = import_generator("json_to_tree_boundary_item_merge")
        root = generator.build_tree([
            {
                "pointer": "/",
                "type": "object",
                "optional": ["boundary_conditions"],
            },
            {
                "pointer": "/boundary_conditions",
                "type": "object",
                "optional": ["neumann_boundary"],
            },
            {
                "pointer": "/boundary_conditions/neumann_boundary",
                "type": "include",
                "spec_file": "boundary-condition.json",
            },
            {
                "pointer": "/boundary_conditions/neumann_boundary/*",
                "type": "object",
                "required": ["id", "value"],
                "optional": ["interpolation"],
                "doc": "Neumann boundary condition",
            },
        ])

        neumann = root.get_optional("boundary_conditions").get_optional(
            "neumann_boundary"
        )
        item = neumann.get_optional("item")

        self.assertEqual("list", neumann.type)
        self.assertEqual("object", item.type)
        self.assertEqual(["id", "value"], list(item._required))
        self.assertEqual(["interpolation"], list(item._optional))

        generated = generator.generated_class_text(root)
        self.assertIn("class_check(i, [self.Item])", generated)
        self.assertNotIn("Neumann_boundary.Item.Object3", generated)

    def test_anonymous_object_list_item_variants_stay_at_list_level(self):
        generator = import_generator("json_to_tree_rayleigh_item_variants")
        root = generator.build_tree([
            {
                "pointer": "/",
                "type": "object",
                "optional": ["solver"],
            },
            {
                "pointer": "/solver",
                "type": "object",
                "optional": ["rayleigh_damping"],
            },
            {
                "pointer": "/solver/rayleigh_damping",
                "type": "list",
            },
            {
                "pointer": "/solver/rayleigh_damping/*",
                "type": "object",
                "required": ["form", "stiffness_ratio"],
                "optional": ["lagging_iterations"],
                "doc": "Rayleigh damping with stiffness ratio.",
            },
            {
                "pointer": "/solver/rayleigh_damping/*",
                "type": "object",
                "required": ["form", "stiffness"],
                "optional": ["lagging_iterations"],
                "doc": "Rayleigh damping with stiffness.",
            },
            {
                "pointer": "/solver/rayleigh_damping/*/form",
                "type": "string",
                "options": ["elasticity", "contact"],
            },
            {
                "pointer": "/solver/rayleigh_damping/*/stiffness_ratio",
                "type": "float",
            },
            {
                "pointer": "/solver/rayleigh_damping/*/stiffness",
                "type": "float",
            },
            {
                "pointer": "/solver/rayleigh_damping/*/lagging_iterations",
                "type": "int",
                "default": 1,
            },
        ])

        rayleigh = root.get_optional("solver").get_optional("rayleigh_damping")

        self.assertEqual("list", rayleigh.type)
        self.assertEqual(["item", "object2"], list(rayleigh._optional))
        self.assertEqual("object", rayleigh.get_optional("item").type)
        self.assertEqual("object", rayleigh.get_optional("object2").type)

        generated = generator.generated_class_text(root)
        self.assertIn("class_check(i, [self.Item, self.Object2])", generated)
        self.assertNotIn("Rayleigh_damping.Item.Object2", generated)

        generated_module = module_from_generated_text(generated)
        ratio = generated_module.Root.Solver.Rayleigh_damping.Item(
            form="elasticity",
            stiffness_ratio=0.25,
        )
        stiffness = generated_module.Root.Solver.Rayleigh_damping.Object2(
            form="contact",
            stiffness=2.0,
        )
        rayleigh = generated_module.Root.Solver.Rayleigh_damping(
            items=[ratio, stiffness]
        )

        self.assertEqual(
            [
                {
                    "form": "elasticity",
                    "stiffness_ratio": 0.25,
                    "lagging_iterations": 1,
                },
                {
                    "form": "contact",
                    "stiffness": 2.0,
                    "lagging_iterations": 1,
                },
            ],
            rayleigh.as_dict(),
        )

    def test_included_value_list_items_expand_inline_variants(self):
        generator = import_generator("json_to_tree_value_list_items")
        root = generator.build_tree([
            {
                "pointer": "/",
                "type": "object",
                "optional": ["rhs"],
            },
            {
                "pointer": "/rhs",
                "type": "list",
            },
            {
                "pointer": "/rhs/*",
                "type": "include",
                "spec_file": "value-no.json",
            },
        ])

        rhs = root.get_optional("rhs")

        self.assertEqual("list", rhs.type)
        self.assertEqual(["item", "string"], list(rhs._optional))
        self.assertEqual("polymorphic", rhs.get_optional("item").type)
        self.assertEqual("string", rhs.get_optional("string").type)

        generated = generator.generated_class_text(root)
        self.assertIn("inline_check(i, [float, str], [", generated)
        self.assertNotIn("self.Item", generated)
        self.assertNotIn("class Object3(object):", generated)

        generated_module = module_from_generated_text(generated)
        rhs = generated_module.Root.Rhs(
            items=[1.0, "x + y", {"value": 2.0, "unit": "N"}]
        )
        rhs.add({"value": "load_expr", "unit": "N"})
        rhs.check_required()

        self.assertEqual(
            [
                1.0,
                "x + y",
                {"value": 2.0, "unit": "N"},
                {"value": "load_expr", "unit": "N"},
            ],
            rhs.as_dict(),
        )


if __name__ == "__main__":
    unittest.main()
