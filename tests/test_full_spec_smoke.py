"""Optional smoke tests against the external PolyFEM full spec.

These tests run only when PolyFEM's full schema and linked spec files are
available. The default standalone CI path is allowed to skip them.
"""

import contextlib
import io
import json
import unittest
from pathlib import Path

from tests.generator_test_helpers import (
    FULL_SPEC_SCHEMA_FILE,
    POLYFEM_INCLUDE_SPEC_DIRS,
    import_generator,
    import_runner,
    module_from_generated_api_text,
    module_from_generated_text,
    polyfem_linked_specs_available,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
POLYFEM_ALIASES_PATH = PROJECT_ROOT.parent / "generator-config" / "api_aliases.json"
POLYFEM_RELATIONSHIPS_PATH = (
    PROJECT_ROOT.parent / "generator-config" / "id_relationships.json"
)


@unittest.skipUnless(
    FULL_SPEC_SCHEMA_FILE.exists() and polyfem_linked_specs_available(),
    "PolyFEM full spec or linked solver specs are not present",
)
class FullSpecSmokeTests(unittest.TestCase):
    def test_generated_api_wraps_contact_json_like_shapes_from_full_spec(self):
        generator = import_generator("json_to_tree_generated_api_contact_shapes")
        with open(FULL_SPEC_SCHEMA_FILE, encoding="utf-8") as f:
            root = generator.build_tree(
                json.load(f),
                spec_dir=FULL_SPEC_SCHEMA_FILE.parent,
                include_dirs=POLYFEM_INCLUDE_SPEC_DIRS,
            )
        generated_module = module_from_generated_text(generator.generated_class_text(root))
        api_module = module_from_generated_api_text(
            generator.generated_api_text(root),
            generated_module.Root,
        )

        cfg = api_module.config(
            geometry=[
                {
                    "mesh": "../../../meshes/3D/simple/cube.msh",
                    "transformation": {
                        "translation": [0, 0, 0],
                        "scale": 0.2,
                    },
                    "volume_selection": 1,
                },
                {
                    "type": "mesh_array",
                    "mesh": "../../../meshes/3D/simple/cube.msh",
                    "array": {
                        "offset": 1.01,
                        "relative": True,
                        "size": [4, 4, 4],
                    },
                    "transformation": {
                        "scale": 0.25,
                        "translation": [-0.375, 0, -0.375],
                    },
                },
            ],
            materials={
                "type": "NeoHookean",
                "E": 100000,
                "nu": 0.4,
                "rho": 1000,
            },
            time={
                "tend": 5,
                "time_steps": 200,
            },
            boundary_conditions={
                "rhs": [0, 9.81, 0],
            },
            output={
                "paraview": {
                    "file_name": "5-cubes.pvd",
                    "options": {
                        "velocity": True,
                        "acceleration": True,
                    },
                },
            },
            solver={
                "nonlinear": {
                    "Newton": {"force_psd_projection": True},
                    "x_delta_tol": 0.01,
                },
            },
        )

        payload = cfg.as_dict()
        self.assertEqual("mesh", payload["geometry"][0]["type"])
        self.assertEqual([0.0, 0.0, 0.0], payload["geometry"][0]["transformation"]["translation"])
        self.assertEqual([0.2], payload["geometry"][0]["transformation"]["scale"])
        self.assertEqual("mesh_array", payload["geometry"][1]["type"])
        self.assertEqual({"offset": 1.01, "relative": True, "size": [4, 4, 4]}, payload["geometry"][1]["array"])
        self.assertEqual("NeoHookean", payload["materials"][0]["type"])
        self.assertEqual(200, payload["time"]["time_steps"])
        self.assertTrue(payload["output"]["paraview"]["options"]["velocity"])
        self.assertTrue(payload["solver"]["nonlinear"]["Newton"]["force_psd_projection"])

    @unittest.skipUnless(
        POLYFEM_ALIASES_PATH.exists() and POLYFEM_RELATIONSHIPS_PATH.exists(),
        "PolyFEM generator config is not present",
    )
    def test_generated_api_smokes_new_elastic_materials_from_full_spec(self):
        generator = import_generator("json_to_tree_generated_api_elastic_material_smoke")
        runner = import_runner("generate_with_overrides_elastic_material_smoke")
        with open(FULL_SPEC_SCHEMA_FILE, encoding="utf-8") as f:
            root = generator.build_tree(
                json.load(f),
                spec_dir=FULL_SPEC_SCHEMA_FILE.parent,
                include_dirs=POLYFEM_INCLUDE_SPEC_DIRS,
            )
        overrides = runner.merged_generator_overrides(api_aliases_path=POLYFEM_ALIASES_PATH)
        generated_module = module_from_generated_text(generator.generated_class_text(root))
        api_module = module_from_generated_api_text(
            generator.generated_api_text(root, generator_overrides=overrides),
            generated_module.Root,
        )

        expected_active = {
            "type": "ActiveFiber",
            "activation": 1.0,
            "Tmax": 2.0,
            "fiber_direction": [1.0, 0.0, 0.0],
        }
        expected_thermo = {
            "type": "ThermoElasticity",
            "displacement_space_id": 0,
            "temperature_space_id": 1,
            "elastic_material": {
                "type": "LinearElasticity",
                "E": 10.0,
                "nu": 0.3,
            },
            "alpha": 1.0,
            "T0": 0.0,
        }

        active = api_module.active_fiber(
            activation=1.0,
            Tmax=2.0,
            fiber_direction=[1.0, 0.0, 0.0],
        )
        thermo = api_module.thermo_elasticity(
            displacement_space_id=0,
            temperature_space_id=1,
            elastic_material={
                "type": "LinearElasticity",
                "E": 10.0,
                "nu": 0.3,
            },
            alpha=1.0,
            T0=0.0,
        )

        self.assertEqual(expected_active, active.as_dict())
        self.assertEqual(expected_thermo, thermo.as_dict())
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            active.check_required()
            thermo.check_required()
        self.assertEqual("", stdout.getvalue())

        with POLYFEM_RELATIONSHIPS_PATH.open(encoding="utf-8") as f:
            relationships = json.load(f)
        model = api_module.model(relationships=relationships)
        body = model.mesh(mesh="box.msh", volume_selection=7)
        body.material(api_module.active_fiber(
            activation=1.0,
            Tmax=2.0,
            fiber_direction=[1.0, 0.0, 0.0],
        ))

        payload = model.config().as_dict()
        self.assertEqual(
            [{"mesh": "box.msh", "type": "mesh", "volume_selection": 7}],
            payload["geometry"],
        )
        self.assertEqual(
            [
                {
                    "type": "ActiveFiber",
                    "activation": 1.0,
                    "id": 7,
                    "Tmax": 2.0,
                    "fiber_direction": [1.0, 0.0, 0.0],
                }
            ],
            payload["materials"],
        )

        models = api_module.material_models(items=[expected_active, expected_thermo])

        self.assertEqual([expected_active, expected_thermo], models.as_dict())

    def test_generated_api_shortcuts_from_full_spec(self):
        generator = import_generator("json_to_tree_generated_api_shortcuts")
        with open(FULL_SPEC_SCHEMA_FILE, encoding="utf-8") as f:
            root = generator.build_tree(
                json.load(f),
                spec_dir=FULL_SPEC_SCHEMA_FILE.parent,
                include_dirs=POLYFEM_INCLUDE_SPEC_DIRS,
            )
        generated_module = module_from_generated_text(generator.generated_class_text(root))
        api_module = module_from_generated_api_text(
            generator.generated_api_text(root),
            generated_module.Root,
        )

        cfg = api_module.config(
            geometry=[
                api_module.mesh(
                    mesh="../assets/impact/triangular_lattice.msh",
                    volume_selection=1,
                    surface_selection=api_module.surface_axis(
                        id=1,
                        axis=-2,
                        position=0.0001,
                    ),
                ),
            ],
            boundary_conditions=api_module.boundary_conditions(
                dirichlet=[
                    api_module.dirichlet(id=1, value=[0.0, 0.0]),
                ],
                rhs=[0.0, 980.0],
            ),
            output=api_module.output(
                paraview=api_module.output_paraview(
                    file_name="results.pvd",
                    options={"velocity": True},
                ),
            ),
        )

        payload = cfg.as_dict()
        self.assertEqual(1, payload["boundary_conditions"]["dirichlet_boundary"][0]["id"])
        self.assertEqual(
            [0.0, 0.0],
            payload["boundary_conditions"]["dirichlet_boundary"][0]["value"],
        )
        self.assertEqual(
            {"id": 1, "axis": -2, "position": 0.0001},
            payload["geometry"][0]["surface_selection"],
        )
        self.assertEqual("results.pvd", payload["output"]["paraview"]["file_name"])
        self.assertTrue(payload["output"]["paraview"]["options"]["velocity"])

    def test_generated_api_config_expands_flat_time_contact_shortcuts(self):
        generator = import_generator("json_to_tree_generated_api_config_shortcuts")
        with open(FULL_SPEC_SCHEMA_FILE, encoding="utf-8") as f:
            root = generator.build_tree(
                json.load(f),
                spec_dir=FULL_SPEC_SCHEMA_FILE.parent,
                include_dirs=POLYFEM_INCLUDE_SPEC_DIRS,
            )
        generated_module = module_from_generated_text(generator.generated_class_text(root))
        api_module = module_from_generated_api_text(
            generator.generated_api_text(root),
            generated_module.Root,
        )

        cfg = api_module.config(
            geometry=[
                api_module.mesh(mesh="../assets/impact/triangular_lattice.msh"),
            ],
            time_tend=0.004,
            time_dt=2e-05,
            contact_enabled=True,
            contact_dhat=6.92820323e-05,
        )

        payload = cfg.as_dict()
        self.assertEqual(0.004, payload["time"]["tend"])
        self.assertEqual(2e-05, payload["time"]["dt"])
        self.assertTrue(payload["contact"]["enabled"])
        self.assertEqual(6.92820323e-05, payload["contact"]["dhat"])

    def test_generated_api_config_rejects_flat_shortcut_when_section_is_explicit(self):
        generator = import_generator("json_to_tree_generated_api_config_shortcut_conflict")
        with open(FULL_SPEC_SCHEMA_FILE, encoding="utf-8") as f:
            root = generator.build_tree(
                json.load(f),
                spec_dir=FULL_SPEC_SCHEMA_FILE.parent,
                include_dirs=POLYFEM_INCLUDE_SPEC_DIRS,
            )
        generated_module = module_from_generated_text(generator.generated_class_text(root))
        api_module = module_from_generated_api_text(
            generator.generated_api_text(root),
            generated_module.Root,
        )

        with self.assertRaisesRegex(TypeError, "time"):
            api_module.config(
                time=api_module.object1(tend=0.004, dt=2e-05),
                time_tend=0.004,
            )


if __name__ == "__main__":
    unittest.main()
