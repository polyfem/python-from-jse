# Generator Tool Paths

This file explains the paths used by the standalone `python-from-jse` tools.
Project-specific wrappers should document their own paths outside this repo.

## Main Rule

`python-from-jse` should stay generic. It owns the generator logic, generic
examples, dummy config examples, validators, and default local generated output.
Project schemas should come from the consuming project, not from this generator
repo.

A consuming project should own its packaged output path and project-specific
generator config. Pass those paths through `tools/generate_with_overrides.py`
instead of hard-coding project paths inside the generator.

Generated files are artifacts. Do not edit them by hand.

## Standalone `python-from-jse`

Run from the `python-from-jse` repo root:

```powershell
python tools\regenerate_and_test.py
```

This uses the generic example config:

- schema input: `examples/basic_generation/input-spec.json`
- optional overrides: `examples/basic_generation/generator_overrides.json`
- generated output: `generated/`

The default generated files are:

- `generated/generated_class.py`
- `generated/generated_api.py`
- `generated/class_tree_manifest.json`
- `generated/generated_api_manifest.json`
- `generated/schema_patch_report.json`

This output is useful for generator development and tests. It is not packaged
output for any consuming project.

For a custom standalone schema:

```powershell
python tools\generate_with_overrides.py `
  --schema-file path\to\input-spec.json `
  --overrides path\to\generator_overrides.json `
  --output-file generated\generated_class.py `
  --api-output-file generated\generated_api.py `
  --manifest-dir generated
```

## Adapting Another Project

Create a small wrapper in the consuming project. The wrapper should define the
project paths once and pass them to `generate_with_overrides.py`.

Common arguments to set from the consuming project:

| Argument | Purpose |
| --- | --- |
| `--schema-file` | input schema/spec file |
| `--include-spec-dir` | extra directory for linked include specs |
| `--output-file` | generated schema-faithful classes |
| `--api-output-file` | generated convenience API |
| `--manifest-dir` | generated manifests and reports |
| `--overrides` | optional schema patches and API config |
| `--api-aliases` | optional public API alias config |
| `--relationships` | optional builder relationship config |
| `--model-entry` | optional model-builder entry name |

Use `--api-aliases`, `--relationships`, and `--model-entry` only if the project
needs those features.

If another library also uses this JSON-spec dialect, keep its schema in that
library's source/config repo and point the consuming project's wrapper at that
schema.

## Checks

Standalone generator check, run from `python-from-jse`:

```powershell
python tools\regenerate_and_test.py
```

For another project, at minimum compile the generated Python files and run any
project-specific import or parity tests that depend on the generated API.
