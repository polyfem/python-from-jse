# Class Generation from JSON Specification

This repository contains the implementation developed for a master's thesis on **specification-driven configuration generation**. The system converts a JSON-based specification into a **strongly typed Python configuration interface**, allowing users to construct valid configurations programmatically and serialize them into JSON.

Instead of manually writing JSON configuration files and validating them afterward, this approach generates Python classes that enforce structure and constraints during configuration construction.

---

# Overview

The generator reads a JSON specification describing configuration variables, their hierarchy, and associated constraints. From this specification it:

1. Builds an **intermediate tree representation** of the configuration structure.
2. Generates **Python classes** that mirror the hierarchy of the specification.
3. Provides a **typed authoring interface** for constructing configurations.
4. Serializes the resulting configuration objects into **JSON-compatible dictionaries**.

Validation occurs during assignment through generated setters and helper utilities, ensuring that type and constraint violations are detected early.

---

**Files**

- **Untitled-1.json**  
  Example JSON specification used as input to the generator.

- **JsonToTreeClass.py**  
  Main script responsible for:
  - parsing the specification
  - constructing the intermediate tree
  - generating Python classes

- **generated_class.py**  
  Output file containing the generated configuration classes.

---

# Generating Classes

To generate classes from the specification:

### 1. Modify the specification

Edit the example file:
Untitled-1.json


or replace it with another compatible specification.

### 2. Run the generator

```bash
python JsonToTreeClass.py
```
### 3. Generated output

After execution, the generated Python classes will be written to:
```bash
generated_class.py
```
This file is automatically overwritten each time the generator runs.

---

# Using the Generated Classes

Once classes are generated, they can be used as a configuration authoring interface.

Example usage:
```bash
from generated_class import Root

# Create root configuration
root = Root(string1="hello")

# Incrementally populate nested values
root.geometry.nested = 8

# Optional: check for missing required fields
root.check_required()

# Convert to JSON-compatible dictionary
data = root.as_dict()
```
The resulting dictionary can then be serialized using any JSON library.

---

# Validation Behavior

The generated interface performs validation when values are assigned.

This includes checks such as:

- Type validation

- Numeric range constraints

- Enumerated value checks

- File extension checks (when defined)

Errors are reported at the point of assignment, helping users detect invalid configurations early.

---

# Notes on Extending the System

## Hierarchy Ordering

The generator assumes that the specification is incremental with respect to hierarchy.

This means:

- A parent node must appear before its children in the specification file.

If this ordering is violated, the generator raises a hierarchy-order error.

## Adding New Types or Rules

If new types or validation rules are required, the following components must be extended consistently:

- specification parser

- node representation

- class generation logic

Unsupported type identifiers are rejected with a clear error message listing the supported types.
