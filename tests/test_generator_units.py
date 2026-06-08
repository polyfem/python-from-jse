import contextlib
import io
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

    def test_named_object_variants_keep_separate_type_defaults(self):
        generator = import_generator("json_to_tree_named_variant_type_defaults")
        root = generator.build_tree([
            {
                "pointer": "/",
                "type": "object",
                "optional": ["integrator"],
            },
            {
                "pointer": "/integrator",
                "type": "string",
                "default": "ImplicitEuler",
                "options": ["ImplicitEuler", "BDF1", "ImplicitNewmark"],
            },
            {
                "pointer": "/integrator",
                "type": "object",
                "type_name": "ImplicitEuler",
                "required": ["type"],
            },
            {
                "pointer": "/integrator",
                "type": "object",
                "type_name": "BDF",
                "required": ["type"],
                "optional": ["steps"],
            },
            {
                "pointer": "/integrator",
                "type": "object",
                "type_name": "ImplicitNewmark",
                "required": ["type"],
                "optional": ["gamma"],
            },
            {
                "pointer": "/integrator/type",
                "type": "string",
                "options": ["ImplicitEuler", "BDF", "ImplicitNewmark"],
            },
            {
                "pointer": "/integrator/steps",
                "type": "int",
                "default": 1,
            },
            {
                "pointer": "/integrator/gamma",
                "type": "float",
                "default": 0.5,
            },
        ])

        integrator = root.get_optional("integrator")
        implicit_euler_type = integrator.get_optional("ImplicitEuler").get_required("type")
        bdf_type = integrator.get_optional("BDF").get_required("type")
        implicit_newmark_type = integrator.get_optional("ImplicitNewmark").get_required("type")

        self.assertEqual("ImplicitEuler", implicit_euler_type.default)
        self.assertEqual("BDF", bdf_type.default)
        self.assertEqual("ImplicitNewmark", implicit_newmark_type.default)

        generated = generator.generated_class_text(root)
        generated_module = module_from_generated_text(generated)

        self.assertEqual(
            {"type": "ImplicitEuler"},
            generated_module.Root.Integrator.ImplicitEuler().as_dict(),
        )
        self.assertEqual(
            {"type": "BDF", "steps": 1},
            generated_module.Root.Integrator.BDF().as_dict(),
        )
        self.assertEqual(
            {"type": "ImplicitNewmark", "gamma": 0.5},
            generated_module.Root.Integrator.ImplicitNewmark().as_dict(),
        )

    def test_repeated_type_name_variants_use_alternative_required_sets(self):
        generator = import_generator("json_to_tree_repeated_type_name_required_sets")
        root = generator.build_tree([
            {
                "pointer": "/",
                "type": "object",
                "optional": ["material"],
            },
            {
                "pointer": "/material",
                "type": "object",
                "type_name": "LinearElasticity",
                "required": ["type", "E", "nu"],
            },
            {
                "pointer": "/material",
                "type": "object",
                "type_name": "LinearElasticity",
                "required": ["type", "lambda", "mu"],
            },
            {
                "pointer": "/material/type",
                "type": "string",
                "options": ["LinearElasticity"],
            },
            {
                "pointer": "/material/E",
                "type": "float",
            },
            {
                "pointer": "/material/nu",
                "type": "float",
            },
            {
                "pointer": "/material/lambda",
                "type": "float",
            },
            {
                "pointer": "/material/mu",
                "type": "float",
            },
        ])

        generated = generator.generated_class_text(root)
        generated_module = module_from_generated_text(generated)

        young_poisson = generated_module.Root.Material.LinearElasticity(
            E=1.0,
            nu=0.3,
        )
        lame = generated_module.Root.Material.LinearElasticity(
            lambda_=2.0,
            mu=3.0,
        )
        incomplete = generated_module.Root.Material.LinearElasticity(E=1.0)

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            young_poisson.check_required()
            lame.check_required()

        self.assertEqual("", output.getvalue())

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            incomplete.check_required()

        self.assertIn(
            "must satisfy one required field set",
            output.getvalue(),
        )

    def test_required_simple_list_check_required_warns_only_when_empty(self):
        generator = import_generator("json_to_tree_required_simple_list_check")
        root = generator.build_tree([
            {
                "pointer": "/",
                "type": "object",
                "required": ["selection"],
            },
            {
                "pointer": "/selection",
                "type": "object",
                "required": ["box"],
            },
            {
                "pointer": "/selection/box",
                "type": "list",
            },
            {
                "pointer": "/selection/box/*",
                "type": "float",
            },
        ])

        generated = generator.generated_class_text(root)

        self.assertIn(
            'if not self.box:',
            generated,
        )
        self.assertNotIn(
            'if self.box:\n            print("Requiered variable Root.Selection.box does not have value")',
            generated,
        )

    def test_untyped_fields_generate_pass_through_values(self):
        generator = import_generator("json_to_tree_untyped_field")
        root = generator.build_tree([
            {
                "pointer": "/",
                "type": "object",
                "optional": ["box"],
            },
            {
                "pointer": "/box",
                "type": "object",
                "optional": ["threshold"],
            },
        ])

        generated = generator.generated_class_text(root)

        self.assertIn("threshold: object = None", generated)
        self.assertNotIn("threshold: None = None", generated)
        self.assertNotIn("type_check(threshold, None)", generated)
        self.assertNotIn("type_check(value, None)", generated)

        generated_module = module_from_generated_text(generated)
        box = generated_module.Root.Box(threshold=0.25)
        box.threshold = {"expr": "x > 0"}

        self.assertEqual({"threshold": {"expr": "x > 0"}}, box.as_dict())

    def test_simple_list_remove_uses_field_backing_list(self):
        generator = import_generator("json_to_tree_simple_list_remove")
        root = generator.build_tree([
            {
                "pointer": "/",
                "type": "object",
                "optional": ["selection"],
            },
            {
                "pointer": "/selection",
                "type": "object",
                "optional": ["box"],
            },
            {
                "pointer": "/selection/box",
                "type": "list",
            },
            {
                "pointer": "/selection/box/*",
                "type": "float",
            },
        ])

        generated = generator.generated_class_text(root)
        self.assertIn("if item in self._box:", generated)
        self.assertNotIn("if item in self._list:", generated)

        generated_module = module_from_generated_text(generated)
        selection = generated_module.Root.Selection(box=[1.0, 2.0, 3.0])
        selection.box_remove(2.0)

        self.assertEqual({"box": [1.0, 3.0]}, selection.as_dict())

    def test_child_pointer_before_parent_entry_stays_under_parent(self):
        generator = import_generator("json_to_tree_child_before_parent")
        root = generator.build_tree([
            {
                "pointer": "/",
                "type": "object",
                "optional": ["solver"],
            },
            {
                "pointer": "/solver/contact/friction_iterations",
                "type": "int",
                "default": 5,
            },
            {
                "pointer": "/solver",
                "type": "object",
                "optional": ["contact"],
            },
            {
                "pointer": "/solver/contact",
                "type": "object",
                "optional": ["friction_iterations", "enabled"],
            },
            {
                "pointer": "/solver/contact/enabled",
                "type": "bool",
                "default": True,
            },
        ])

        solver = root.get_optional("solver")
        contact = solver.get_optional("contact")
        friction_iterations = contact.get_optional("friction_iterations")

        self.assertEqual("object", solver.type)
        self.assertEqual("object", contact.type)
        self.assertEqual("int", friction_iterations.type)
        self.assertEqual(5, friction_iterations.default)

        generated = generator.generated_class_text(root)
        generated_module = module_from_generated_text(generated)
        contact_config = generated_module.Root.Solver.Contact(
            friction_iterations=7,
            enabled=False,
        )

        self.assertEqual(
            {"friction_iterations": 7, "enabled": False},
            contact_config.as_dict(),
        )

    def test_duplicate_pointer_object_variants_are_preserved(self):
        generator = import_generator("json_to_tree_duplicate_pointer_variants")
        root = generator.build_tree([
            {
                "pointer": "/",
                "type": "object",
                "optional": ["time"],
            },
            {
                "pointer": "/time",
                "type": "object",
                "required": ["tend", "dt"],
                "optional": ["t0"],
                "doc": "Time with end time and time step.",
            },
            {
                "pointer": "/time",
                "type": "object",
                "required": ["time_steps", "dt"],
                "optional": ["t0"],
                "doc": "Time with number of time steps and time step.",
            },
            {
                "pointer": "/time/t0",
                "type": "float",
                "default": 0.0,
            },
            {
                "pointer": "/time/tend",
                "type": "float",
            },
            {
                "pointer": "/time/dt",
                "type": "float",
            },
            {
                "pointer": "/time/time_steps",
                "type": "int",
            },
        ])

        time = root.get_optional("time")

        self.assertEqual("polymorphic", time.type)
        self.assertEqual(["object1", "object2"], list(time._optional))
        self.assertEqual(["tend", "dt"], list(time.get_optional("object1")._required))
        self.assertEqual(
            ["time_steps", "dt"],
            list(time.get_optional("object2")._required),
        )

        generated = generator.generated_class_text(root)
        self.assertIn("class Object1(object):", generated)
        self.assertIn("class Object2(object):", generated)
        self.assertIn("class_check(value, [self.Object1, self.Object2])", generated)

        generated_module = module_from_generated_text(generated)
        time_by_end = generated_module.Root.Time.Object1(tend=1.0, dt=0.1)
        time_by_steps = generated_module.Root.Time.Object2(time_steps=10, dt=0.1)

        self.assertEqual({"tend": 1.0, "dt": 0.1, "t0": 0.0}, time_by_end.as_dict())
        self.assertEqual(
            {"time_steps": 10, "dt": 0.1, "t0": 0.0},
            time_by_steps.as_dict(),
        )

    def test_anonymous_object_variants_keep_declared_fields_only(self):
        generator = import_generator("json_to_tree_anonymous_variant_fields")
        root = generator.build_tree([
            {
                "pointer": "/",
                "type": "object",
                "optional": ["time"],
            },
            {
                "pointer": "/time",
                "type": "object",
                "required": ["tend", "dt"],
                "optional": ["t0"],
            },
            {
                "pointer": "/time",
                "type": "object",
                "required": ["time_steps", "dt"],
                "optional": ["t0"],
            },
            {
                "pointer": "/time",
                "type": "object",
                "required": ["time_steps", "tend"],
                "optional": ["t0"],
            },
            {
                "pointer": "/time/t0",
                "type": "float",
                "default": 0.0,
            },
            {
                "pointer": "/time/tend",
                "type": "float",
            },
            {
                "pointer": "/time/dt",
                "type": "float",
            },
            {
                "pointer": "/time/time_steps",
                "type": "int",
            },
        ])

        time = root.get_optional("time")
        object1 = time.get_optional("object1")
        object2 = time.get_optional("object2")
        object3 = time.get_optional("object3")

        self.assertNotIn("time_steps", object1._required)
        self.assertNotIn("time_steps", object1._optional)
        self.assertNotIn("tend", object2._required)
        self.assertNotIn("tend", object2._optional)
        self.assertNotIn("dt", object3._required)
        self.assertNotIn("dt", object3._optional)

        generated = generator.generated_class_text(root)
        generated_module = module_from_generated_text(generated)

        with self.assertRaises(TypeError):
            generated_module.Root.Time.Object1(
                tend=1.0,
                dt=0.1,
                time_steps=10,
            )

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
        self.assertNotIn("stiffness", rayleigh.get_optional("item")._required)
        self.assertNotIn("stiffness", rayleigh.get_optional("item")._optional)
        self.assertNotIn(
            "stiffness_ratio",
            rayleigh.get_optional("object2")._required,
        )
        self.assertNotIn(
            "stiffness_ratio",
            rayleigh.get_optional("object2")._optional,
        )

        generated = generator.generated_class_text(root)
        self.assertIn("class_check(i, [self.Item, self.Object2])", generated)
        self.assertNotIn("Rayleigh_damping.Item.Object2", generated)

        generated_module = module_from_generated_text(generated)
        with self.assertRaises(TypeError):
            generated_module.Root.Solver.Rayleigh_damping.Item(
                form="elasticity",
                stiffness_ratio=0.25,
                stiffness=2.0,
            )

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

    def test_named_list_variants_do_not_keep_empty_item_placeholder(self):
        generator = import_generator("json_to_tree_named_list_variants")
        root = generator.build_tree([
            {
                "pointer": "/",
                "type": "object",
                "optional": ["geometry"],
            },
            {
                "pointer": "/geometry",
                "type": "list",
            },
            {
                "pointer": "/geometry/*",
                "type": "object",
                "type_name": "Mesh",
                "required": ["type", "mesh"],
            },
            {
                "pointer": "/geometry/*",
                "type": "object",
                "type_name": "Plane",
                "required": ["type", "point"],
            },
            {
                "pointer": "/geometry/*/type",
                "type": "string",
                "options": ["Mesh", "Plane"],
            },
            {
                "pointer": "/geometry/*/mesh",
                "type": "string",
            },
            {
                "pointer": "/geometry/*/point",
                "type": "list",
            },
            {
                "pointer": "/geometry/*/point/*",
                "type": "float",
            },
        ])

        geometry = root.get_optional("geometry")

        self.assertEqual("list", geometry.type)
        self.assertEqual(["item", "Mesh", "Plane"], list(geometry._optional))
        self.assertIsNone(geometry.get_optional("item").type)

        generated = generator.generated_class_text(root)
        self.assertIn("class_check(i, [self.Mesh, self.Plane])", generated)
        self.assertNotIn("class_check(i, [self.Item, self.Mesh", generated)

        generated_module = module_from_generated_text(generated)
        mesh = generated_module.Root.Geometry.Mesh(mesh="mesh.obj")
        plane = generated_module.Root.Geometry.Plane(point=[0.0, 1.0, 2.0])
        geometry = generated_module.Root.Geometry(items=[mesh])

        self.assertEqual({"type": "Mesh", "mesh": "mesh.obj"}, mesh.as_dict())
        self.assertEqual({"type": "Plane", "point": [0.0, 1.0, 2.0]}, plane.as_dict())
        self.assertEqual([{"type": "Mesh", "mesh": "mesh.obj"}], geometry.as_dict())

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
