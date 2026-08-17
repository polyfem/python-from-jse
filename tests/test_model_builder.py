import json
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GENERATOR_DIR = PROJECT_ROOT / "generator"
SELECTION_REFS_PATH = GENERATOR_DIR / "selection_refs.py"
MODEL_BUILDER_PATH = GENERATOR_DIR / "model_builder.py"


def import_from_generator(path, module_name):
    sys.path.insert(0, str(GENERATOR_DIR))
    try:
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(GENERATOR_DIR))


class FakeGeneratedApi:
    def config(self, **kwargs):
        return dict(kwargs)

    def mesh(self, **kwargs):
        return dict(kwargs)

    def neo_hookean(self, **kwargs):
        result = {"type": "NeoHookean"}
        result.update(kwargs)
        return result

    def output(self, **kwargs):
        return dict(kwargs)

    def output_paraview(self, **kwargs):
        return dict(kwargs)

    def options(self, **kwargs):
        return dict(kwargs)

    def output_log(self, **kwargs):
        return dict(kwargs)

    def output_advanced(self, **kwargs):
        return dict(kwargs)

    def solver(self, **kwargs):
        return dict(kwargs)

    def linear(self, **kwargs):
        return dict(kwargs)

    def nonlinear(self, **kwargs):
        return dict(kwargs)

    def line_search(self, **kwargs):
        return dict(kwargs)

    def solver_advanced(self, **kwargs):
        return dict(kwargs)


class FakeGeneratedObject:
    def __init__(self, payload):
        self._payload = dict(payload)

    def as_dict(self):
        return dict(self._payload)


POLYFEM_RELATIONSHIPS = [
    {
        "namespace": "volume",
        "producer": "geometry[*].volume_selection",
        "consumer": "materials[*].id",
        "builder_api": "body.material",
        "status": "required",
    },
    {
        "namespace": "volume",
        "producer": "geometry[*].volume_selection",
        "consumer": "initial_conditions.velocity[*].id",
        "builder_api": "body.velocity",
        "status": "required",
    },
    {
        "namespace": "volume",
        "producer": "geometry[*].volume_selection",
        "consumer": "initial_conditions.solution[*].id",
        "builder_api": "body.solution",
        "status": "required",
    },
    {
        "namespace": "volume",
        "producer": "geometry[*].volume_selection",
        "consumer": "initial_conditions.acceleration[*].id",
        "builder_api": "body.acceleration",
        "status": "required",
    },
    {
        "namespace": "volume",
        "producer": "geometry[*].volume_selection",
        "consumer": "space.discr_order[*].id",
        "builder_api": "body.discr_order",
        "status": "required",
    },
    {
        "namespace": "surface",
        "producer": "geometry[*].surface_selection",
        "consumer": "boundary_conditions.dirichlet_boundary[*].id",
        "builder_api": "surface.dirichlet",
        "status": "required",
    },
    {
        "namespace": "surface",
        "producer": "geometry[*].surface_selection",
        "consumer": "boundary_conditions.neumann_boundary[*].id",
        "builder_api": "surface.neumann",
        "status": "required",
    },
    {
        "namespace": "surface",
        "producer": "geometry[*].surface_selection",
        "consumer": "boundary_conditions.normal_aligned_neumann_boundary[*].id",
        "builder_api": "surface.normal_aligned_neumann",
        "status": "required",
    },
    {
        "namespace": "surface",
        "producer": "geometry[*].surface_selection",
        "consumer": "boundary_conditions.pressure_boundary[*].id",
        "builder_api": "surface.pressure",
        "status": "required",
    },
    {
        "namespace": "surface",
        "producer": "geometry[*].surface_selection",
        "consumer": "boundary_conditions.pressure_cavity[*].id",
        "builder_api": "surface.pressure_cavity",
        "status": "required",
    },
    {
        "namespace": "surface",
        "producer": "geometry[*].surface_selection",
        "consumer": "boundary_conditions.obstacle_displacements[*].id",
        "builder_api": "surface.obstacle_displacement",
        "status": "required",
    },
    {
        "namespace": "point",
        "producer": "geometry[*].point_selection",
        "consumer": "boundary_conditions.neumann_boundary[*].id",
        "builder_api": "point.neumann",
        "status": "required",
    },
]
POLYFEM_SELECTION_HELPER_RULES = {
    "surface_axis": {
        "namespace": "surface",
        "geometry_field": "surface_selection",
        "allowed_fields": ("id", "axis", "position"),
    },
    "point_box": {
        "namespace": "point",
        "geometry_field": "point_selection",
        "allowed_fields": ("id", "box"),
    },
}


class SelectionPoolTests(unittest.TestCase):
    def test_selection_pool_allocates_uuid_and_namespace_backend_ids(self):
        refs = import_from_generator(SELECTION_REFS_PATH, "selection_refs_for_test")
        pool = refs.SelectionPool()

        volume = pool.allocate("volume", name="body")
        surface = pool.allocate("surface", name="fixed")
        second_volume = pool.allocate("volume", name="other")

        self.assertEqual("volume", volume.namespace)
        self.assertEqual(1, volume.backend_id)
        self.assertEqual(1, surface.backend_id)
        self.assertEqual(2, second_volume.backend_id)
        self.assertNotEqual(volume.uuid, surface.uuid)


class ModelBuilderTests(unittest.TestCase):
    def test_model_builder_loads_relationships_from_api_adjacent_manifest(self):
        model_builder = import_from_generator(
            MODEL_BUILDER_PATH,
            "model_builder_adjacent_manifest",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            api = FakeGeneratedApi()
            api.__file__ = str(Path(tmpdir) / "generated_api.py")
            (Path(tmpdir) / "builder_api_manifest.json").write_text(
                json.dumps({
                    "version": 1,
                    "model_entry": "polyfem.model",
                    "relationships": [
                        {
                            "namespace": "volume",
                            "producer": "geometry[*].volume_selection",
                            "consumer": "materials[*].id",
                            "builder_api": "body.material",
                        }
                    ],
                }),
                encoding="utf-8",
            )

            model = model_builder.ModelBuilder(api, selection_helper_rules={})
            body = model.mesh(mesh="beam.msh")
            body.material(api.neo_hookean(E=20.0, nu=0.45))

        self.assertEqual(
            [{"type": "NeoHookean", "E": 20.0, "nu": 0.45, "id": 1}],
            model.materials(),
        )

    def test_model_builder_loads_selection_helpers_from_api_adjacent_manifest(self):
        model_builder = import_from_generator(
            MODEL_BUILDER_PATH,
            "model_builder_adjacent_selection_helpers",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            api = FakeGeneratedApi()
            api.__file__ = str(Path(tmpdir) / "generated_api.py")
            generated_dir = Path(tmpdir)
            (generated_dir / "builder_api_manifest.json").write_text(
                json.dumps({
                    "version": 1,
                    "model_entry": "polyfem.model",
                    "relationships": [
                        {
                            "namespace": "surface",
                            "producer": "geometry[*].surface_selection",
                            "consumer": "boundary_conditions.dirichlet_boundary[*].id",
                            "builder_api": "surface.dirichlet",
                        }
                    ],
                }),
                encoding="utf-8",
            )
            (generated_dir / "class_tree_manifest.json").write_text(
                json.dumps([
                    {
                        "class_path": "Root.Geometry.Mesh.Surface_selection",
                        "params": ["axis"],
                    },
                    {
                        "class_path": "Root.Geometry.Mesh.Surface_selection.Axis",
                        "params": ["id", "axis", "position"],
                    },
                ]),
                encoding="utf-8",
            )

            model = model_builder.ModelBuilder(api)
            body = model.mesh(mesh="beam.msh")
            body.surface_axis(axis=1, position=0.5).dirichlet(value=[0, 0])

        self.assertEqual(
            {"dirichlet_boundary": [{"value": [0, 0], "id": 1}]},
            model.boundary_conditions(),
        )

    def test_body_material_uses_relationship_map_and_exports_backend_ids_only(self):
        model_builder = import_from_generator(MODEL_BUILDER_PATH, "model_builder_for_test")
        api = FakeGeneratedApi()
        model = model_builder.ModelBuilder(
            api,
            relationships=POLYFEM_RELATIONSHIPS,
            selection_helper_rules=POLYFEM_SELECTION_HELPER_RULES,
        )

        body = model.mesh(mesh="beam.msh")
        material = api.neo_hookean(E=20.0, nu=0.45)
        body.material(material)

        self.assertEqual(
            [{"mesh": "beam.msh", "volume_selection": 1}],
            model.geometry(),
        )
        self.assertEqual(
            [{"type": "NeoHookean", "E": 20.0, "nu": 0.45, "id": 1}],
            model.materials(),
        )
        self.assertNotIn("uuid", repr(model.geometry()))
        self.assertNotIn("uuid", repr(model.materials()))
        self.assertNotIn("name", repr(model.geometry()))
        self.assertNotIn("name", repr(model.materials()))

    def test_body_methods_are_provided_from_relationship_map(self):
        model_builder = import_from_generator(MODEL_BUILDER_PATH, "model_builder_dynamic_body_api")
        relationships = [
            {
                "namespace": "volume",
                "producer": "geometry[*].volume_selection",
                "consumer": "materials[*].id",
                "builder_api": "body.alt_material",
                "status": "required",
            }
        ]
        model = model_builder.ModelBuilder(FakeGeneratedApi(), relationships=relationships)
        body = model.mesh(mesh="beam.msh")

        body.alt_material({"type": "NeoHookean", "E": 20.0, "nu": 0.45})

        self.assertEqual(
            [{"type": "NeoHookean", "E": 20.0, "nu": 0.45, "id": 1}],
            model.materials(),
        )

    def test_material_binding_does_not_mutate_user_material_object(self):
        model_builder = import_from_generator(MODEL_BUILDER_PATH, "model_builder_no_mutation")
        model = model_builder.ModelBuilder(
            FakeGeneratedApi(),
            relationships=POLYFEM_RELATIONSHIPS,
            selection_helper_rules=POLYFEM_SELECTION_HELPER_RULES,
        )
        body = model.mesh(mesh="beam.msh")
        material = {"type": "NeoHookean", "E": 20.0, "nu": 0.45}

        body.material(material)

        self.assertEqual({"type": "NeoHookean", "E": 20.0, "nu": 0.45}, material)
        self.assertEqual(1, model.materials()[0]["id"])

    def test_material_binding_accepts_generated_object_payload(self):
        model_builder = import_from_generator(MODEL_BUILDER_PATH, "model_builder_generated_object")
        model = model_builder.ModelBuilder(
            FakeGeneratedApi(),
            relationships=POLYFEM_RELATIONSHIPS,
            selection_helper_rules=POLYFEM_SELECTION_HELPER_RULES,
        )
        body = model.mesh(mesh="beam.msh")
        material = FakeGeneratedObject({"type": "NeoHookean", "E": 20.0, "nu": 0.45})

        body.material(material)

        self.assertEqual(
            [{"type": "NeoHookean", "E": 20.0, "nu": 0.45, "id": 1}],
            model.materials(),
        )

    def test_body_velocity_uses_volume_relationship_and_exports_initial_conditions(self):
        model_builder = import_from_generator(MODEL_BUILDER_PATH, "model_builder_velocity")
        relationships = [
            {
                "namespace": "volume",
                "producer": "geometry[*].volume_selection",
                "consumer": "initial_conditions.velocity[*].id",
                "builder_api": "body.velocity",
                "status": "required",
            }
        ]
        model = model_builder.ModelBuilder(FakeGeneratedApi(), relationships=relationships)
        body = model.mesh(mesh="beam.msh")

        body.velocity({"value": [67.0, 0.0]})

        self.assertEqual(
            {"velocity": [{"value": [67.0, 0.0], "id": 1}]},
            model.initial_conditions(),
        )
        self.assertNotIn("uuid", repr(model.initial_conditions()))
        self.assertNotIn("name", repr(model.initial_conditions()))

    def test_default_body_initial_condition_methods_export_volume_ids(self):
        model_builder = import_from_generator(
            MODEL_BUILDER_PATH,
            "model_builder_default_initial_conditions",
        )
        model = model_builder.ModelBuilder(
            FakeGeneratedApi(),
            relationships=POLYFEM_RELATIONSHIPS,
            selection_helper_rules=POLYFEM_SELECTION_HELPER_RULES,
        )
        body = model.mesh(mesh="beam.msh")

        body.solution({"value": [0.0, 0.0]})
        body.velocity({"value": [67.0, 0.0]})
        body.acceleration({"value": [0.0, 0.0]})

        self.assertEqual(
            {
                "solution": [{"value": [0.0, 0.0], "id": 1}],
                "velocity": [{"value": [67.0, 0.0], "id": 1}],
                "acceleration": [{"value": [0.0, 0.0], "id": 1}],
            },
            model.initial_conditions(),
        )

    def test_default_body_discr_order_exports_space_volume_id(self):
        model_builder = import_from_generator(
            MODEL_BUILDER_PATH,
            "model_builder_default_space",
        )
        model = model_builder.ModelBuilder(
            FakeGeneratedApi(),
            relationships=POLYFEM_RELATIONSHIPS,
            selection_helper_rules=POLYFEM_SELECTION_HELPER_RULES,
        )
        model.mesh(mesh="sphere.msh")
        wall = model.mesh(mesh="cube.msh")

        wall.discr_order(order=2)

        self.assertEqual(
            {"discr_order": [{"order": 2, "id": 2}]},
            model.space(),
        )
        self.assertEqual(
            [
                {"mesh": "sphere.msh", "volume_selection": 1},
                {"mesh": "cube.msh", "volume_selection": 2},
            ],
            model.geometry(),
        )

    def test_explicit_volume_selection_is_reused_for_material_id(self):
        model_builder = import_from_generator(MODEL_BUILDER_PATH, "model_builder_explicit_id")
        model = model_builder.ModelBuilder(
            FakeGeneratedApi(),
            relationships=POLYFEM_RELATIONSHIPS,
            selection_helper_rules=POLYFEM_SELECTION_HELPER_RULES,
        )

        body = model.mesh(mesh="beam.msh", volume_selection=7)
        body.material({"type": "NeoHookean", "E": 20.0, "nu": 0.45})
        next_body = model.mesh(mesh="other.msh")

        self.assertEqual(7, model.geometry()[0]["volume_selection"])
        self.assertEqual(7, model.materials()[0]["id"])
        self.assertEqual(8, next_body.volume_ref.backend_id)

    def test_surface_axis_selection_binds_boundary_conditions(self):
        model_builder = import_from_generator(
            MODEL_BUILDER_PATH,
            "model_builder_surface_boundary",
        )
        model = model_builder.ModelBuilder(
            FakeGeneratedApi(),
            relationships=POLYFEM_RELATIONSHIPS,
            selection_helper_rules=POLYFEM_SELECTION_HELPER_RULES,
        )
        wall = model.mesh(mesh="wall.obj")

        fixed = wall.surface_axis(axis=1, position=0.1025)
        loaded = wall.surface_axis(axis=-1, position=-0.1025)
        fixed.dirichlet(value=[0, 0])
        loaded.neumann(value=[0, -10])
        loaded.normal_aligned_neumann(value=5)
        loaded.pressure(value=100)
        loaded.pressure_cavity(value=200)
        loaded.obstacle_displacement(value=[0, 0])

        self.assertEqual(
            [
                {
                    "mesh": "wall.obj",
                    "volume_selection": 1,
                    "surface_selection": [
                        {"id": 1, "axis": 1, "position": 0.1025},
                        {"id": 2, "axis": -1, "position": -0.1025},
                    ],
                }
            ],
            model.geometry(),
        )
        self.assertEqual(
            {
                "dirichlet_boundary": [{"value": [0, 0], "id": 1}],
                "neumann_boundary": [{"value": [0, -10], "id": 2}],
                "normal_aligned_neumann_boundary": [{"value": 5, "id": 2}],
                "pressure_boundary": [{"value": 100, "id": 2}],
                "pressure_cavity": [{"value": 200, "id": 2}],
                "obstacle_displacements": [{"value": [0, 0], "id": 2}],
            },
            model.boundary_conditions(),
        )

    def test_unbound_geometry_mesh_can_create_surface_selection_without_volume_id(self):
        model_builder = import_from_generator(
            MODEL_BUILDER_PATH,
            "model_builder_unbound_geometry_selection",
        )
        model = model_builder.ModelBuilder(
            FakeGeneratedApi(),
            relationships=POLYFEM_RELATIONSHIPS,
            selection_helper_rules=POLYFEM_SELECTION_HELPER_RULES,
        )
        wall = model.geometry_mesh(mesh="wall.obj")

        fixed = wall.surface_all(id=3)
        fixed.dirichlet(value=[0, 0])

        self.assertEqual(
            [
                {
                    "mesh": "wall.obj",
                    "surface_selection": 3,
                }
            ],
            model.geometry(),
        )
        self.assertEqual(
            {
                "dirichlet_boundary": [{"value": [0, 0], "id": 3}],
            },
            model.boundary_conditions(),
        )

    def test_selection_helper_can_preserve_single_object_shape(self):
        model_builder = import_from_generator(
            MODEL_BUILDER_PATH,
            "model_builder_single_object_selection",
        )
        model = model_builder.ModelBuilder(
            FakeGeneratedApi(),
            relationships=POLYFEM_RELATIONSHIPS,
            selection_helper_rules=POLYFEM_SELECTION_HELPER_RULES,
        )
        wall = model.mesh(mesh="wall.obj")

        fixed = wall.surface_axis(
            id=3,
            axis="-y",
            position=1e-05,
            append=False,
        )
        fixed.dirichlet(value=[0, 0])

        self.assertEqual(
            [
                {
                    "mesh": "wall.obj",
                    "volume_selection": 1,
                    "surface_selection": {
                        "id": 3,
                        "axis": "-y",
                        "position": 1e-05,
                    },
                }
            ],
            model.geometry(),
        )
        self.assertEqual(
            {
                "dirichlet_boundary": [{"value": [0, 0], "id": 3}],
            },
            model.boundary_conditions(),
        )

    def test_matching_surface_helpers_share_id_and_dedupe_boundary_binding(self):
        model_builder = import_from_generator(
            MODEL_BUILDER_PATH,
            "model_builder_matching_surface_boundary",
        )
        model = model_builder.ModelBuilder(
            FakeGeneratedApi(),
            relationships=POLYFEM_RELATIONSHIPS,
            selection_helper_rules=POLYFEM_SELECTION_HELPER_RULES,
        )
        ball = model.mesh(mesh="ball.obj")
        wall = model.mesh(mesh="wall.obj")

        ball_fixed = ball.surface_axis(axis=1, position=0.1025)
        wall_fixed = wall.surface_axis(axis=1, position=0.1025)
        ball_fixed.dirichlet(value=[0, 0])
        wall_fixed.dirichlet(value=[0, 0])

        self.assertEqual(
            [
                {
                    "mesh": "ball.obj",
                    "volume_selection": 1,
                    "surface_selection": [
                        {"id": 1, "axis": 1, "position": 0.1025},
                    ],
                },
                {
                    "mesh": "wall.obj",
                    "volume_selection": 2,
                    "surface_selection": [
                        {"id": 1, "axis": 1, "position": 0.1025},
                    ],
                },
            ],
            model.geometry(),
        )
        self.assertEqual(
            {
                "dirichlet_boundary": [{"value": [0, 0], "id": 1}],
            },
            model.boundary_conditions(),
        )

    def test_point_selection_uses_same_boundary_id_pool_as_surface_selection(self):
        model_builder = import_from_generator(
            MODEL_BUILDER_PATH,
            "model_builder_point_boundary",
        )
        model = model_builder.ModelBuilder(
            FakeGeneratedApi(),
            relationships=POLYFEM_RELATIONSHIPS,
            selection_helper_rules=POLYFEM_SELECTION_HELPER_RULES,
        )
        body = model.mesh(mesh="body.obj")

        side = body.surface_axis(axis=1, position=0.5)
        pin = body.point_box(box=[[0.1, 2, -10], [1, 10, 10]])
        side.dirichlet(value=[0, 0])
        pin.neumann(value=[0, -10])

        self.assertEqual(
            [
                {
                    "mesh": "body.obj",
                    "volume_selection": 1,
                    "surface_selection": [
                        {"id": 1, "axis": 1, "position": 0.5},
                    ],
                    "point_selection": [
                        {"id": 2, "box": [[0.1, 2, -10], [1, 10, 10]]},
                    ],
                }
            ],
            model.geometry(),
        )
        self.assertEqual(
            {
                "dirichlet_boundary": [{"value": [0, 0], "id": 1}],
                "neumann_boundary": [{"value": [0, -10], "id": 2}],
            },
            model.boundary_conditions(),
        )

    def test_selection_helpers_are_loaded_from_class_tree_manifest(self):
        model_builder = import_from_generator(
            MODEL_BUILDER_PATH,
            "model_builder_manifest_selection_helpers",
        )
        manifest = [
            {
                "class_path": "Root.Geometry.Mesh.Surface_selection",
                "params": ["ring"],
            },
            {
                "class_path": "Root.Geometry.Mesh.Surface_selection.Ring",
                "params": ["id", "radius", "relative"],
            },
            {
                "class_path": "Root.Geometry.Mesh.Point_selection",
                "params": ["list"],
            },
            {
                "class_path": "Root.Geometry.Mesh.Point_selection.List",
                "params": ["ring"],
            },
            {
                "class_path": "Root.Geometry.Mesh.Point_selection.List.Ring",
                "params": ["id", "radius", "relative"],
            },
        ]
        selection_helper_rules = model_builder.selection_helper_rules_from_manifest(
            manifest
        )
        self.assertEqual(
            "Root.Geometry.Mesh.Surface_selection.Ring",
            selection_helper_rules["surface_ring"]["class_path"],
        )
        self.assertEqual(
            "Root.Geometry.Mesh.Point_selection.List.Ring",
            selection_helper_rules["point_ring"]["class_path"],
        )
        model = model_builder.ModelBuilder(
            FakeGeneratedApi(),
            relationships=POLYFEM_RELATIONSHIPS,
            selection_helper_rules=selection_helper_rules,
        )
        body = model.mesh(mesh="body.obj")

        surface = body.surface_ring(radius=0.01)
        point = body.point_ring(radius=0.02)
        surface.dirichlet(value=[0, 0])
        point.neumann(value=[0, -10])

        self.assertEqual(
            [
                {
                    "mesh": "body.obj",
                    "volume_selection": 1,
                    "surface_selection": [
                        {"id": 1, "radius": 0.01},
                    ],
                    "point_selection": [
                        {"id": 2, "radius": 0.02},
                    ],
                }
            ],
            model.geometry(),
        )
        self.assertEqual(
            {
                "dirichlet_boundary": [{"value": [0, 0], "id": 1}],
                "neumann_boundary": [{"value": [0, -10], "id": 2}],
            },
            model.boundary_conditions(),
        )

    def test_builder_api_manifest_is_generated_from_relationships_and_class_tree(self):
        model_builder = import_from_generator(
            MODEL_BUILDER_PATH,
            "model_builder_api_manifest",
        )
        relationships = [
            {
                "namespace": "volume",
                "producer": "geometry[*].volume_selection",
                "consumer": "materials[*].id",
                "builder_api": "body.material",
                "status": "required",
            },
            {
                "namespace": "surface",
                "producer": "geometry[*].surface_selection",
                "consumer": "boundary_conditions.dirichlet_boundary[*].id",
                "builder_api": "surface.dirichlet",
                "status": "required",
            },
            {
                "namespace": "point",
                "producer": "geometry[*].point_selection",
                "consumer": "boundary_conditions.neumann_boundary[*].id",
                "builder_api": "point.neumann",
                "status": "required",
            },
        ]
        class_tree_manifest = [
            {
                "class_path": "Root.Geometry.Mesh.Surface_selection",
                "params": ["axis"],
            },
            {
                "class_path": "Root.Geometry.Mesh.Surface_selection.Axis",
                "params": ["id", "axis", "position"],
            },
            {
                "class_path": "Root.Geometry.Mesh.Point_selection",
                "params": ["list"],
            },
            {
                "class_path": "Root.Geometry.Mesh.Point_selection.List",
                "params": ["axis"],
            },
            {
                "class_path": "Root.Geometry.Mesh.Point_selection.List.Axis",
                "params": ["id", "axis", "position"],
            },
        ]

        manifest = model_builder.builder_api_manifest_from_inputs(
            relationships,
            class_tree_manifest,
        )

        self.assertEqual("generated_api.model", manifest["model_entry"])
        self.assertEqual(["material"], manifest["body_methods"])
        self.assertEqual(["dirichlet"], manifest["selection_methods"]["surface"])
        self.assertEqual(["neumann"], manifest["selection_methods"]["point"])
        self.assertEqual(["surface_axis"], manifest["selection_helpers"]["surface"])
        self.assertEqual(["point_axis"], manifest["selection_helpers"]["point"])
        self.assertEqual(
            ["boundary_conditions", "materials"],
            manifest["config_auto_sections"],
        )

    def test_builder_api_manifest_accepts_project_model_entry_override(self):
        model_builder = import_from_generator(
            MODEL_BUILDER_PATH,
            "model_builder_api_manifest_entry_override",
        )

        manifest = model_builder.builder_api_manifest_from_inputs(
            [],
            [],
            model_entry="polyfem.model",
        )

        self.assertEqual("polyfem.model", manifest["model_entry"])

    def test_model_config_collects_builder_sections_and_rhs(self):
        model_builder = import_from_generator(
            MODEL_BUILDER_PATH,
            "model_builder_config",
        )
        api = FakeGeneratedApi()
        model = model_builder.ModelBuilder(
            api,
            relationships=POLYFEM_RELATIONSHIPS,
            selection_helper_rules=POLYFEM_SELECTION_HELPER_RULES,
        )
        body = model.mesh(mesh="beam.msh")
        body.material(api.neo_hookean(E=20.0, nu=0.45))
        body.velocity({"value": [67.0, 0.0]})
        body.surface_axis(axis=1, position=0.5).dirichlet(value=[0, 0])

        cfg = model.config(
            rhs=[0, 0],
            time_tend=0.004,
            time_dt=2e-05,
        )

        self.assertEqual(
            [
                {
                    "mesh": "beam.msh",
                    "volume_selection": 1,
                    "surface_selection": [
                        {"id": 1, "axis": 1, "position": 0.5},
                    ],
                }
            ],
            cfg["geometry"],
        )
        self.assertEqual(
            [{"type": "NeoHookean", "E": 20.0, "nu": 0.45, "id": 1}],
            cfg["materials"],
        )
        self.assertEqual(
            {
                "rhs": [0, 0],
                "dirichlet_boundary": [{"value": [0, 0], "id": 1}],
            },
            cfg["boundary_conditions"],
        )
        self.assertEqual(
            {"velocity": [{"value": [67.0, 0.0], "id": 1}]},
            cfg["initial_conditions"],
        )
        self.assertEqual(0.004, cfg["time_tend"])
        self.assertEqual(2e-05, cfg["time_dt"])
        self.assertNotIn("output", cfg)
        self.assertNotIn("solver", cfg)

    def test_model_config_preserves_explicit_solver(self):
        model_builder = import_from_generator(
            MODEL_BUILDER_PATH,
            "model_builder_config_explicit_solver",
        )
        explicit_solver = {"linear": {"solver": "custom"}}
        model = model_builder.ModelBuilder(
            FakeGeneratedApi(),
            relationships=POLYFEM_RELATIONSHIPS,
            selection_helper_rules=POLYFEM_SELECTION_HELPER_RULES,
        )

        cfg = model.config(solver=explicit_solver)

        self.assertIs(explicit_solver, cfg["solver"])

    def test_model_config_preserves_explicit_output(self):
        model_builder = import_from_generator(
            MODEL_BUILDER_PATH,
            "model_builder_config_explicit_output",
        )
        explicit_output = {"json": "custom.json"}
        model = model_builder.ModelBuilder(
            FakeGeneratedApi(),
            relationships=POLYFEM_RELATIONSHIPS,
            selection_helper_rules=POLYFEM_SELECTION_HELPER_RULES,
        )

        cfg = model.config(output=explicit_output)

        self.assertIs(explicit_output, cfg["output"])

    def test_model_config_rejects_rhs_duplicate(self):
        model_builder = import_from_generator(
            MODEL_BUILDER_PATH,
            "model_builder_config_rhs_duplicate",
        )
        model = model_builder.ModelBuilder(
            FakeGeneratedApi(),
            relationships=POLYFEM_RELATIONSHIPS,
            selection_helper_rules=POLYFEM_SELECTION_HELPER_RULES,
        )

        with self.assertRaisesRegex(TypeError, "rhs"):
            model.config(
                rhs=[0, 0],
                boundary_conditions={"rhs": [1, 1]},
            )

    def test_model_config_collects_sections_from_relationship_consumers(self):
        model_builder = import_from_generator(
            MODEL_BUILDER_PATH,
            "model_builder_config_auto_sections",
        )
        relationships = [
            {
                "namespace": "volume",
                "producer": "geometry[*].volume_selection",
                "consumer": "constraints.some_constraint[*].id",
                "builder_api": "body.constraint",
                "status": "required",
            }
        ]
        model = model_builder.ModelBuilder(
            FakeGeneratedApi(),
            relationships=relationships,
        )
        body = model.mesh(mesh="beam.msh")

        body.constraint({"value": "fixed"})
        cfg = model.config()

        self.assertEqual(
            {"some_constraint": [{"value": "fixed", "id": 1}]},
            cfg["constraints"],
        )

    def test_missing_body_material_relationship_reports_clear_error(self):
        model_builder = import_from_generator(MODEL_BUILDER_PATH, "model_builder_missing_map")
        relationships = [
            {
                "namespace": "surface",
                "producer": "geometry[*].surface_selection",
                "consumer": "boundary_conditions.dirichlet_boundary[*].id",
                "builder_api": "surface.dirichlet",
                "status": "required",
            }
        ]
        model = model_builder.ModelBuilder(FakeGeneratedApi(), relationships=relationships)
        body = model.mesh(mesh="beam.msh")

        with self.assertRaisesRegex(AttributeError, "body.material"):
            body.material({"type": "NeoHookean", "E": 20.0, "nu": 0.45})


if __name__ == "__main__":
    unittest.main()
