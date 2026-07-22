# python-from-jse

`python-from-jse` is a generic JSON-spec-to-Python generator.

It reads a JSON schema-like spec and emits:

- `generated/generated_class.py`: schema-faithful Python config classes
- `generated/generated_api.py`: user-facing factory helpers
- `generated/*_manifest.json`: manifests used by validators and optional
  project integrations
- `generated/schema_patch_report.json`: applied schema patch diagnostics

The generator repo should define supported generation behavior, dummy/example
config shapes, validators, and tests. Project-specific schemas and Python API
policy belong in the consuming project.

## Standalone Usage

Run the default generic example from this directory:

```powershell
python tools\regenerate_and_test.py
```

This command:

1. reads `examples/basic_generation/input-spec.json`;
2. applies `examples/basic_generation/generator_overrides.json`;
3. writes generated artifacts under `generated/`;
4. compiles the generated Python files;
5. runs the generator unit test suite.

For a custom schema:

```powershell
python tools\generate_with_overrides.py `
  --schema-file path\to\input-spec.json `
  --include-spec-dir path\to\linked-specs `
  --overrides path\to\generator_overrides.json `
  --output-file generated\generated_class.py `
  --api-output-file generated\generated_api.py `
  --manifest-dir generated
```

`--overrides` is optional. If omitted, the generator uses the schema directly.
`--include-spec-dir` is also optional and is only needed when the input spec
references include files that live outside the schema file's directory.

## Standalone Repo Readiness

The repo is ready to be checked as a standalone generator project when this
command works from the repo root:

```powershell
python tools\regenerate_and_test.py
```

The GitHub Actions workflow at `.github/workflows/ci.yml` runs the same command
on push and pull requests. That check proves the generator can use the dummy
schema in `examples/basic_generation/` to regenerate `generated/`, compile the
generated Python files, and run the test suite without any consuming project
checkout.

Packaging metadata can be added later, after the source layout is intentionally
converted into an installable Python package. Until then, this repo should be
treated as a runnable generator/tool repo rather than a pip-published package.

## Optional Project Config

Some projects need extra config around the generated API. These inputs are
optional and are only used when passed explicitly:

```powershell
python tools\generate_with_overrides.py `
  --schema-file path\to\input-spec.json `
  --api-aliases path\to\api_aliases.json `
  --relationships path\to\id_relationships.json
```

The supported example shapes live in:

- `examples/config_capabilities/api_aliases.example.json`
- `examples/config_capabilities/schema_patches.example.json`
- `examples/config_capabilities/id_relationships.example.json`

Validator modules can be run directly after generating manifests:

```powershell
python -m validators.api_aliases
python -m validators.id_relationships
```

By default these validators use the generic example config and `generated/`
manifests. Consuming projects should pass their own config and manifest paths.

## Generated Files

Generated files are build artifacts. Do not edit them by hand:

- `generated/generated_class.py`
- `generated/generated_api.py`
- `generated/*_manifest.json`
- `generated/schema_patch_report.json`

If generated output is wrong, update the input spec, overrides, config examples,
or generator logic, then regenerate.

For a direct map of standalone and custom-project tool paths, see
`tools/README.md`.

## Project Integration

Consuming projects should keep their schema files, package output paths, and
public API policy outside this generator repo. The usual pattern is:

1. keep the real schema in the backend or project repo that owns it;
2. keep project-specific overrides/config in the consuming project;
3. add a small project wrapper that calls `tools/generate_with_overrides.py`
   with explicit paths;
4. document those project paths in the consuming project.

The generator repo only needs the dummy/example schema under
`examples/basic_generation/` so its own tests can run without any consuming
project checkout.

## Folder Map

```text
examples/       Generic runnable examples and dummy config capability examples.
generator/      Generator core and generic helper code.
tools/          Generation and verification workflow CLI entry points.
validators/     Reusable validation logic imported by tools and tests.
tests/          Generator, generated API, builder, and validator tests.
doc/            Local design notes and handoff documents.
```

## Test Map

- `tests/test_generator_units.py`: tree construction and generated-class
  behavior.
- `tests/test_generated_api.py`: generated API factories, naming, aliases, and
  manifests.
- `tests/test_generator_runner.py`: schema patches and generation entry points.
- `tests/test_generator_examples.py`: generic examples remain runnable and
  separate from project-specific config.
- `tests/test_model_builder.py`: model/builder behavior with explicit
  relationship maps.
- `tests/test_validators.py`: validation for generic example config against
  generated manifests.
- `tests/test_id_relationship_rules.py`: loading and structure rules for the
  generic id relationship example.
- `tests/test_regenerate_and_test.py`: the standalone regeneration and test
  workflow.
- `tests/test_full_spec_smoke.py`: optional full-spec smoke coverage. It should
  not define standalone defaults; the standalone workflow uses
  `examples/basic_generation/`.
