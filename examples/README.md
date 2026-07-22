# Generator Examples

This directory documents generator-owned behavior with generic input names. It
must not contain project-specific configuration for a consuming project.

## basic_generation

`basic_generation/` is a small runnable schema. It demonstrates:

- generating `generated_class.py` and `generated_api.py` from a JSON schema
- adding a field through `schema_patches`
- replacing an auto-generated API function name through `custom_api_names`
- hiding the replaced auto-generated API function through `skip_auto_generated_api_names`

From `python-from-jse/`:

```powershell
python tools/generate_with_overrides.py `
  --schema-file examples/basic_generation/input-spec.json `
  --overrides examples/basic_generation/generator_overrides.json `
  --output-file generated/generated_class.py `
  --api-output-file generated/generated_api.py `
  --manifest-dir generated `
  --skip-id-relationship-check `
  --skip-api-aliases `
  --skip-api-alias-check
```

## config_capabilities

`config_capabilities/` contains dummy config files that show the supported
shape for optional project config:

- `api_aliases.example.json`
- `schema_patches.example.json`
- `id_relationships.example.json`

`schema_patches.example.json` shows the standalone config shape. The same patch
idea is also demonstrated in `basic_generation/generator_overrides.json`, where
it is verified against a concrete schema.

Real project-specific config belongs in the consuming project, for example
`generator-config/` in the top-level Python binding repo. The generator should
only define the supported format and behavior.
