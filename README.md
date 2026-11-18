# python-from-jse

`python-from-jse` is a generic JSON-spec-to-Python generator.

It reads a JSON schema-like spec and emits:

- `generated/generated_class.py`: Python configuration classes that follow the schema
- `generated/generated_api.py`: factory functions for building configurations
- `generated/*_manifest.json`: manifests used by validators and optional
  project integrations
- `generated/schema_patch_report.json`: applied schema patch diagnostics

This repository contains the generator, generic examples, validators, and tests.
Keep project-specific schemas and API settings in the project that uses it.

## Standalone Usage

Install the generator from this repository:

```powershell
python -m pip install -e .
python-from-jse-generate --help
```

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
python-from-jse-generate `
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

## Testing

Run the full standalone check from this repository root:

```bash
python tools/regenerate_and_test.py
```

This is the same command used by CI. It regenerates the generic example
artifacts under `generated/`, compiles `generator/JsonToTreeClass.py` and the
generated Python files, then runs:

```bash
python -m unittest discover -s tests
```

Some optional full-spec smoke tests are skipped unless PolyFEM's full schema and
linked solver specs are available. Those skips are expected for standalone CI;
the generator's default standalone workflow uses only `examples/basic_generation/`.

See [tests/README.md](tests/README.md) for test groups and optional full-spec checks.

## Standalone Repo Readiness

The GitHub Actions workflow at `.github/workflows/ci.yml` runs on Ubuntu,
macOS, and Windows with Python 3.10, 3.11, and 3.12. Each job installs the
package, checks the console command, and runs the standalone check above.
A successful run covers the bundled generic example without a consuming project
checkout. Project-specific schema and API checks belong in the consuming project.
An editable installation does not verify the contents of a release wheel.

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

See [tools/README.md](tools/README.md) for input paths and command options.

## Project Integration

Consuming projects should keep their schema files, package output paths, and
public API policy outside this generator repo. The usual pattern is:

1. keep the real schema in the backend or project repo that owns it;
2. keep project-specific overrides/config in the consuming project;
3. add a small project wrapper that calls `tools/generate_with_overrides.py`
   with explicit paths;
4. run project-specific generated API checks in the consuming project;
5. document those project paths in the consuming project.

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
```

## License

This project is available under the [MIT License](LICENSE).
