# Python Class Generation from JSON Specification

This repository contains a JSON-specification-driven generator for Python configuration classes. It reads a JSON schema for PolyFEM-style configuration files, builds an intermediate tree representation, and generates a typed Python authoring interface that can validate inputs and serialize back to JSON-compatible dictionaries.

## What The Generator Does

The generator is not a simple one-entry-to-one-class converter. The current pipeline is:

```text
json-specs/input-spec.json
  -> expand_includes()
  -> build_tree()
  -> generated_class_text()
  -> generated/generated_class.py
```

During that process it handles:

- included spec files under `json-specs/`
- repeated pointers and polymorphic values
- list wildcard entries such as `/materials/*`
- `type_name` and legacy `#type_name`
- required and optional child fields
- variant-specific field pruning

The output is a generated Python module containing nested classes such as `Root`, `Root.Time`, `Root.Materials`, and their variants.

## Repository Layout

- `generator/JsonToTreeClass.py`
  - Main generator implementation.
  - Defines schema expansion, tree construction, class generation, and the default CLI entry point.

- `json-specs/input-spec.json`
  - Default top-level input specification.

- `json-specs/*.json`
  - Additional specs included from the top-level schema.

- `generated/generated_class.py`
  - Generated Python classes.
  - This file is overwritten when the generator is run.

- `tests/test_generator_units.py`
  - Unit tests for generator behavior and edge cases.

- `doc/generator-explanation.md`
  - Local detailed explanation document.
  - The `doc/` directory is currently ignored by git.

## Requirements

The project uses the Python standard library only. No external dependencies are required for generation or tests.

Use Python 3.10 or newer if possible. The current code and tests are run with the local Python available in this workspace.

## Generate Classes

From the repository root:

```powershell
python generator\JsonToTreeClass.py
```

By default this reads:

```text
json-specs/input-spec.json
```

and writes:

```text
generated/generated_class.py
```

The output file is regenerated in place.

## Use The Generated Classes

After generation, import `Root` from the generated module and construct configuration objects programmatically.

Example:

```python
from generated.generated_class import Root

config = Root()

config.time = Root.Time(
    Root.Time.TendDt(tend=1.0, dt=0.1)
)

material = Root.Materials.MooneyRivlin(
    c1=1.0,
    c2=1.0,
    k=10.0,
)
config.materials = Root.Materials(items=[material])

config.check_required()
data = config.as_dict()
```

`data` is a JSON-compatible dictionary and can be passed to `json.dump()` or `json.dumps()`.

## Validation Behavior

The generated classes validate values when they are assigned. Current validation includes:

- Python type checks
- class checks for nested generated objects
- enum checks for string `options`
- numeric range checks
- file extension checks
- inline checks for small polymorphic value schemas

`check_required()` recursively reports missing required values by printing messages. It does not currently raise exceptions.

`as_dict()` serializes generated objects back to plain Python dictionaries and lists, dropping fields whose value is `None`.

## Notes On `type_name` And `ObjectN`

The generator supports both `type_name` and legacy `#type_name` through `entry_type_name(entry)`.

When a schema object variant has a stable type name, the generated class uses that readable name:

```python
class Stiffness(object):
    ...
```

The current generator does not add compatibility aliases such as `Object2 = Stiffness` for named variants.

The case that needs attention is:

```python
class Object2(object):
    ...
```

That usually means the schema or generator did not provide a stable readable name for that object variant.

## Skipped Schema Sections

The generator intentionally skips these pointer prefixes:

```python
SKIP_POINTER_PREFIXES = ("/preset_problem", "/tests")
```

Those sections are excluded by design in the current generator.

## Run Checks

Run the unit tests:

```powershell
python -m unittest tests.test_generator_units
```

Compile-check the generator, tests, and generated output:

```powershell
python -m py_compile tests\test_generator_units.py generator\JsonToTreeClass.py generated\generated_class.py
```

Search for generated `ObjectN` classes or aliases:

```powershell
rg -n "class Object[0-9]+\(object\):|Object[0-9]+ =" generated\generated_class.py
```

## Development Notes

When changing the generator, prefer small regression tests in `tests/test_generator_units.py`. A minimal schema in a unit test is usually easier to debug than the full `json-specs/input-spec.json`.

Good areas to test explicitly include:

- include expansion
- child pointers appearing before parent entries
- duplicate pointer variants
- list item variants
- inline value schemas
- `type_name` / `#type_name` behavior
- required field alternatives
- `as_dict()` output shape

Avoid broad refactors unless the generator behavior is already covered by focused tests.
