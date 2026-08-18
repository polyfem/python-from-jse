# Test Structure

This directory tests the standalone generator repo. The default test path must
not require a consuming project checkout or a PolyFEM source tree.

## Main Commands

Run the full standalone workflow from the repo root:

```bash
python tools/regenerate_and_test.py
```

That command does three things:

1. regenerates generic artifacts from `examples/basic_generation/`;
2. compiles the generator and generated Python files;
3. runs `python -m unittest discover -s tests`.

Run the unit suite directly when you do not need regeneration:

```bash
python -m unittest discover -s tests
```

Check the installable package and console script:

```bash
python -m pip install -e .
python-from-jse-generate --help
```

## Test Groups

| Group | Files | Purpose |
| --- | --- | --- |
| Core generator behavior | `test_generator_units.py` | Tree construction, type variants, required fields, list handling, and generated-class behavior. |
| Generation CLI and paths | `test_generator_runner.py`, `test_regenerate_and_test.py` | Default standalone paths, schema patches, optional config inputs, package import behavior, and the full regeneration workflow. |
| Generated API surface | `test_generated_api.py`, `test_model_builder.py` | Factory helpers, public API naming, manifests, model-builder relationships, selections, and section assembly. |
| Config validators | `test_validators.py`, `test_id_relationship_rules.py` | Validation rules for `api_aliases` and `id_relationships` against generated manifests. |
| Repo readiness and docs | `test_repo_readiness.py`, `test_generator_examples.py` | CI coverage, packaging metadata, ignored artifacts, README guidance, and generic example boundaries. |
| Optional full-spec smoke | `test_full_spec_smoke.py` | Smoke coverage against the real PolyFEM full spec when those external files are available. |

## Skip Policy

Standalone CI is allowed to skip tests that require external PolyFEM full-spec
files. Those tests are guarded by `unittest.skipUnless` in
`test_full_spec_smoke.py` and are not part of the default standalone contract.

If you want to run the optional full-spec smoke tests locally, point these
environment variables at a checkout that contains the real PolyFEM specs:

```bash
POLYFEM_SPEC_DIR=/path/to/polyfem/json-specs
POLYFEM_INCLUDE_SPEC_DIRS=/path/to/linked/specs
python -m unittest tests.test_full_spec_smoke
```

Use the consuming project CI for project-specific schema parity and integration
checks. This repository should only own generic generator behavior and generic
config examples.

## Adding Tests

Add focused tests near the behavior they protect:

- generator parsing/emission changes belong in `test_generator_units.py`;
- CLI, path, and config-file behavior belongs in `test_generator_runner.py`;
- generated API factory behavior belongs in `test_generated_api.py`;
- model-style builder behavior belongs in `test_model_builder.py`;
- repo-level policy, CI, README, or packaging checks belong in
  `test_repo_readiness.py`.
