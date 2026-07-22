import unittest

from tests.generator_test_helpers import (
    POLYFEM_SPEC_DIR,
    import_generator,
    module_from_generated_api_text,
    module_from_generated_text,
)


class GeneratedApiTests(unittest.TestCase):
    def test_generated_api_factories_match_direct_root_construction(self):
        generator = import_generator("json_to_tree_generated_api")
        root = generator.build_tree([
            {
                "pointer": "/",
                "type": "object",
                "required": ["geometry", "materials"],
                "optional": ["time"],
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
                "optional": ["volume_selection"],
            },
            {
                "pointer": "/geometry/*/type",
                "type": "string",
                "options": ["mesh"],
            },
            {
                "pointer": "/geometry/*/mesh",
                "type": "string",
            },
            {
                "pointer": "/geometry/*/volume_selection",
                "type": "int",
            },
            {
                "pointer": "/materials",
                "type": "list",
            },
            {
                "pointer": "/materials/*",
                "type": "object",
                "type_name": "NeoHookean",
                "required": ["type", "E", "nu"],
                "optional": ["id"],
            },
            {
                "pointer": "/materials/*/type",
                "type": "string",
                "options": ["NeoHookean"],
            },
            {
                "pointer": "/materials/*/E",
                "type": "include",
                "spec_file": "value-no.json",
            },
            {
                "pointer": "/materials/*/nu",
                "type": "float",
            },
            {
                "pointer": "/materials/*/id",
                "type": "int",
            },
            {
                "pointer": "/time",
                "type": "object",
                "type_name": "TendDt",
                "required": ["tend", "dt"],
            },
            {
                "pointer": "/time/tend",
                "type": "float",
            },
            {
                "pointer": "/time/dt",
                "type": "float",
            },
        ], spec_dir=POLYFEM_SPEC_DIR)
        generated_module = module_from_generated_text(generator.generated_class_text(root))
        api_module = module_from_generated_api_text(
            generator.generated_api_text(root),
            generated_module.Root,
        )

        direct = generated_module.Root(
            geometry=generated_module.Root.Geometry(
                items=[
                    generated_module.Root.Geometry.Mesh(
                        mesh="beam.msh",
                        volume_selection=1,
                    )
                ]
            ),
            materials=generated_module.Root.Materials(
                items=[
                    generated_module.Root.Materials.NeoHookean(
                        id=1,
                        E=generated_module.Root.Materials.NeoHookean.E.Object3(
                            value=20.0,
                            unit="MPa",
                        ),
                        nu=0.45,
                    )
                ]
            ),
            time=generated_module.Root.Time(
                generated_module.Root.Time.TendDt(tend=0.02, dt=0.01)
            ),
        )

        via_api = api_module.config(
            geometry=[
                api_module.mesh(mesh="beam.msh", volume_selection=1),
            ],
            materials=[
                api_module.neo_hookean(
                    id=1,
                    E=api_module.unit(20.0, "MPa"),
                    nu=0.45,
                ),
            ],
            time=api_module.tend_dt(tend=0.02, dt=0.01),
        )

        self.assertEqual(direct.as_dict(), via_api.as_dict())

    def test_generated_api_exposes_model_builder_factory(self):
        generator = import_generator("json_to_tree_generated_api_model_builder")
        root = generator.build_tree([
            {
                "pointer": "/",
                "type": "object",
                "required": ["geometry", "materials"],
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
                "optional": ["volume_selection"],
            },
            {
                "pointer": "/geometry/*/type",
                "type": "string",
                "options": ["mesh"],
            },
            {
                "pointer": "/geometry/*/mesh",
                "type": "string",
            },
            {
                "pointer": "/geometry/*/volume_selection",
                "type": "int",
            },
            {
                "pointer": "/materials",
                "type": "list",
            },
            {
                "pointer": "/materials/*",
                "type": "object",
                "type_name": "NeoHookean",
                "required": ["type", "E", "nu"],
                "optional": ["id"],
            },
            {
                "pointer": "/materials/*/type",
                "type": "string",
                "options": ["NeoHookean"],
            },
            {
                "pointer": "/materials/*/E",
                "type": "float",
            },
            {
                "pointer": "/materials/*/nu",
                "type": "float",
            },
            {
                "pointer": "/materials/*/id",
                "type": "int",
            },
        ])
        generated_module = module_from_generated_text(generator.generated_class_text(root))
        api_module = module_from_generated_api_text(
            generator.generated_api_text(root),
            generated_module.Root,
        )

        relationships = [
            {
                "namespace": "volume",
                "producer": "geometry[*].volume_selection",
                "consumer": "materials[*].id",
                "builder_api": "body.material",
                "status": "required",
            }
        ]
        model = api_module.model(relationships=relationships)
        body = model.mesh(mesh="beam.msh")
        body.material(api_module.neo_hookean(E=20.0, nu=0.45))

        cfg = api_module.config(
            geometry=model.geometry(),
            materials=model.materials(),
        )

        self.assertIs(model.__class__, api_module.ModelBuilder)
        self.assertEqual(1, cfg.as_dict()["geometry"][0]["volume_selection"])
        self.assertEqual(1, cfg.as_dict()["materials"][0]["id"])
        self.assertNotIn("uuid", repr(cfg.as_dict()))

    def test_generated_api_prefers_short_name_for_shallow_collision(self):
        generator = import_generator("json_to_tree_generated_api_names")
        names = generator.generated_api_name_map([
            (["Root"], None),
            (["Root", "Materials", "NeoHookean"], None),
            (["Root", "Materials", "MaterialSum", "Models", "NeoHookean"], None),
        ])

        self.assertEqual(
            "neo_hookean",
            names[("Root", "Materials", "NeoHookean")],
        )
        self.assertEqual(
            "models_neo_hookean",
            names[("Root", "Materials", "MaterialSum", "Models", "NeoHookean")],
        )

    def test_generated_api_custom_name_and_skip_generated_name(self):
        generator = import_generator("json_to_tree_api_overrides")
        root = generator.build_tree([
            {"pointer": "/", "type": "object", "optional": ["materials"]},
            {"pointer": "/materials", "type": "object", "optional": ["MooneyRivlin", "materialSum"]},
            {"pointer": "/materials/MooneyRivlin", "type": "object", "optional": ["c1"]},
            {"pointer": "/materials/MooneyRivlin/c1", "type": "float"},
            {"pointer": "/materials/materialSum", "type": "object", "optional": ["models"]},
            {"pointer": "/materials/materialSum/models", "type": "object", "optional": ["MooneyRivlin"]},
            {"pointer": "/materials/materialSum/models/MooneyRivlin", "type": "object", "optional": ["c1"]},
            {"pointer": "/materials/materialSum/models/MooneyRivlin/c1", "type": "float"},
        ])
        overrides = {
            "version": 1,
            "custom_api_names": [
                {
                    "class_path": "Root.Materials.MaterialSum.Models.MooneyRivlin",
                    "api_custom_name": "material_sum_mooney_rivlin",
                }
            ],
            "skip_auto_generated_api_names": [
                {
                    "class_path": "Root.Materials.MaterialSum.Models.MooneyRivlin",
                    "api_generated_name": "models_mooney_rivlin",
                }
            ],
        }
        generated_module = module_from_generated_text(generator.generated_class_text(root))
        api_module = module_from_generated_api_text(
            generator.generated_api_text(root, generator_overrides=overrides),
            generated_module.Root,
        )

        self.assertTrue(hasattr(api_module, "material_sum_mooney_rivlin"))
        self.assertFalse(hasattr(api_module, "models_mooney_rivlin"))
        self.assertEqual(
            generated_module.Root.Materials.MaterialSum.Models.MooneyRivlin(c1=2.0).as_dict(),
            api_module.material_sum_mooney_rivlin(c1=2.0).as_dict(),
        )

    def test_generated_api_aliases_export_main_name_and_hide_generated_alias(self):
        generator = import_generator("json_to_tree_api_aliases")
        root = generator.build_tree([
            {"pointer": "/", "type": "object", "optional": ["materials"]},
            {"pointer": "/materials", "type": "object", "optional": ["MooneyRivlin", "materialSum"]},
            {"pointer": "/materials/MooneyRivlin", "type": "object", "optional": ["c1"]},
            {"pointer": "/materials/MooneyRivlin/c1", "type": "float"},
            {"pointer": "/materials/materialSum", "type": "object", "optional": ["models"]},
            {"pointer": "/materials/materialSum/models", "type": "object", "optional": ["MooneyRivlin"]},
            {"pointer": "/materials/materialSum/models/MooneyRivlin", "type": "object", "optional": ["c1"]},
            {"pointer": "/materials/materialSum/models/MooneyRivlin/c1", "type": "float"},
        ])
        overrides = {
            "version": 1,
            "api_aliases": [
                {
                    "main_api_name": "material_models",
                    "main_class_path": "Root.Materials.MaterialSum.Models",
                    "api_generated_name": "models",
                    "aliases": [
                        {
                            "alias_name": "models",
                            "alias_class_path": "Root.Materials.MaterialSum.Models",
                            "hide": True,
                        }
                    ],
                },
                {
                    "main_api_name": "mooney_rivlin",
                    "main_class_path": "Root.Materials.MooneyRivlin",
                    "aliases": [
                        {
                            "alias_name": "models_mooney_rivlin",
                            "alias_class_path": "Root.Materials.MaterialSum.Models.MooneyRivlin",
                            "hide": True,
                        }
                    ],
                },
            ],
        }
        generated_module = module_from_generated_text(generator.generated_class_text(root))
        api_module = module_from_generated_api_text(
            generator.generated_api_text(root, generator_overrides=overrides),
            generated_module.Root,
        )

        self.assertTrue(hasattr(api_module, "material_models"))
        self.assertTrue(hasattr(api_module, "mooney_rivlin"))
        self.assertFalse(hasattr(api_module, "models"))
        self.assertFalse(hasattr(api_module, "models_mooney_rivlin"))
        nested_model = generated_module.Root.Materials.MaterialSum.Models.MooneyRivlin(c1=2.0)
        self.assertEqual(
            generated_module.Root.Materials.MaterialSum.Models(MooneyRivlin=nested_model).as_dict(),
            api_module.material_models(MooneyRivlin=nested_model).as_dict(),
        )
        self.assertEqual(
            generated_module.Root.Materials.MooneyRivlin(c1=3.0).as_dict(),
            api_module.mooney_rivlin(c1=3.0).as_dict(),
        )

    def test_generated_api_manifest_records_api_alias_entries(self):
        generator = import_generator("json_to_tree_api_alias_manifest")
        root = generator.build_tree([
            {"pointer": "/", "type": "object", "optional": ["materials"]},
            {"pointer": "/materials", "type": "object", "optional": ["materialSum"]},
            {"pointer": "/materials/materialSum", "type": "object", "optional": ["models"]},
            {"pointer": "/materials/materialSum/models", "type": "object", "optional": []},
        ])
        overrides = {
            "version": 1,
            "api_aliases": [
                {
                    "main_api_name": "material_models",
                    "main_class_path": "Root.Materials.MaterialSum.Models",
                    "api_generated_name": "models",
                    "aliases": [
                        {
                            "alias_name": "models",
                            "alias_class_path": "Root.Materials.MaterialSum.Models",
                            "hide": True,
                        }
                    ],
                }
            ],
        }

        manifest = generator.generated_api_manifest(root, generator_overrides=overrides)
        target_entries = [
            entry for entry in manifest
            if entry["class_path"] == "Root.Materials.MaterialSum.Models"
        ]

        self.assertIn(
            {
                "class_path": "Root.Materials.MaterialSum.Models",
                "api_generated_name": "models",
                "api_custom_name": None,
                "kind": "auto",
                "source": "generator",
                "exported": False,
                "params": [],
            },
            target_entries,
        )
        self.assertIn(
            {
                "class_path": "Root.Materials.MaterialSum.Models",
                "api_generated_name": "models",
                "api_custom_name": "material_models",
                "kind": "api_alias",
                "source": "api_aliases",
                "exported": True,
                "params": [],
            },
            target_entries,
        )

    def test_generated_api_manifest_records_custom_and_skipped_names(self):
        generator = import_generator("json_to_tree_api_manifest")
        root = generator.build_tree([
            {"pointer": "/", "type": "object", "optional": ["materials"]},
            {"pointer": "/materials", "type": "object", "optional": ["MooneyRivlin", "materialSum"]},
            {"pointer": "/materials/MooneyRivlin", "type": "object", "optional": ["c1"]},
            {"pointer": "/materials/MooneyRivlin/c1", "type": "float"},
            {"pointer": "/materials/materialSum", "type": "object", "optional": ["models"]},
            {"pointer": "/materials/materialSum/models", "type": "object", "optional": ["MooneyRivlin"]},
            {"pointer": "/materials/materialSum/models/MooneyRivlin", "type": "object", "optional": ["c1"]},
            {"pointer": "/materials/materialSum/models/MooneyRivlin/c1", "type": "float"},
        ])
        overrides = {
            "version": 1,
            "custom_api_names": [
                {
                    "class_path": "Root.Materials.MaterialSum.Models.MooneyRivlin",
                    "api_custom_name": "material_sum_mooney_rivlin",
                }
            ],
            "skip_auto_generated_api_names": [
                {
                    "class_path": "Root.Materials.MaterialSum.Models.MooneyRivlin",
                    "api_generated_name": "models_mooney_rivlin",
                }
            ],
        }

        manifest = generator.generated_api_manifest(root, generator_overrides=overrides)
        target_entries = [
            entry for entry in manifest
            if entry["class_path"] == "Root.Materials.MaterialSum.Models.MooneyRivlin"
        ]

        self.assertIn(
            {
                "class_path": "Root.Materials.MaterialSum.Models.MooneyRivlin",
                "api_generated_name": "models_mooney_rivlin",
                "api_custom_name": None,
                "kind": "auto",
                "source": "generator",
                "exported": False,
                "params": ["c1"],
            },
            target_entries,
        )
        self.assertIn(
            {
                "class_path": "Root.Materials.MaterialSum.Models.MooneyRivlin",
                "api_generated_name": "models_mooney_rivlin",
                "api_custom_name": "material_sum_mooney_rivlin",
                "kind": "custom_api_name",
                "source": "api_config",
                "exported": True,
                "params": ["c1"],
            },
            target_entries,
        )

    def test_generated_api_skip_unknown_generated_name_fails(self):
        generator = import_generator("json_to_tree_api_skip_validation")
        root = generator.build_tree([
            {"pointer": "/", "type": "object", "optional": ["materials"]},
            {"pointer": "/materials", "type": "object", "optional": ["MooneyRivlin"]},
            {"pointer": "/materials/MooneyRivlin", "type": "object", "optional": ["c1"]},
            {"pointer": "/materials/MooneyRivlin/c1", "type": "float"},
        ])

        with self.assertRaisesRegex(ValueError, "api_generated_name"):
            generator.generated_api_manifest(
                root,
                generator_overrides={
                    "version": 1,
                    "skip_auto_generated_api_names": [
                        {
                            "class_path": "Root.Materials.MooneyRivlin",
                            "api_generated_name": "not_the_generated_name",
                        }
                    ],
                },
            )

    def test_generated_api_config_uses_builtin_list_when_factory_is_named_list(self):
        generator = import_generator("json_to_tree_generated_api_builtin_list")
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
                "type_name": "List",
                "required": ["type"],
            },
            {
                "pointer": "/geometry/*/type",
                "type": "string",
                "options": ["list"],
            },
        ])
        generated_module = module_from_generated_text(generator.generated_class_text(root))
        api_module = module_from_generated_api_text(
            generator.generated_api_text(root),
            generated_module.Root,
        )

        cfg = api_module.config(geometry=[api_module.list()])

        self.assertEqual({"geometry": [{"type": "List"}]}, cfg.as_dict())


if __name__ == "__main__":
    unittest.main()
