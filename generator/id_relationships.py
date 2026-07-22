import json
from pathlib import Path


DEFAULT_RELATIONSHIPS_FILE = (
    Path(__file__).resolve().parents[1]
    / "examples"
    / "config_capabilities"
    / "id_relationships.example.json"
)
REQUIRED_RELATIONSHIP_FIELDS = (
    "namespace",
    "producer",
    "consumer",
    "builder_api",
    "status",
)
ALLOWED_NAMESPACES = {"volume", "surface", "point", "curve"}
ALLOWED_STATUSES = {"required", "supported_later"}


def validate_id_relationships(relationships):
    if not isinstance(relationships, list):
        raise ValueError("id relationships must be a list")

    validated = []
    for index, relationship in enumerate(relationships):
        if not isinstance(relationship, dict):
            raise ValueError(f"id relationship {index} must be an object")

        missing = [
            field
            for field in REQUIRED_RELATIONSHIP_FIELDS
            if field not in relationship
        ]
        if missing:
            raise ValueError(
                "id relationship %d missing required field(s): %s"
                % (index, ", ".join(missing))
            )

        item = dict(relationship)
        for field in REQUIRED_RELATIONSHIP_FIELDS:
            value = item[field]
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    "id relationship %d field %s must be a non-empty string"
                    % (index, field)
                )
            item[field] = value.strip()

        if item["namespace"] not in ALLOWED_NAMESPACES:
            raise ValueError(
                "id relationship %d has unsupported namespace: %r"
                % (index, item["namespace"])
            )
        if item["status"] not in ALLOWED_STATUSES:
            raise ValueError(
                "id relationship %d has unsupported status: %r"
                % (index, item["status"])
            )

        validated.append(item)

    return validated


def load_id_relationships(path=None, *, statuses=None):
    relationships_path = Path(path) if path is not None else DEFAULT_RELATIONSHIPS_FILE
    with relationships_path.open(encoding="utf-8") as f:
        relationships = validate_id_relationships(json.load(f))

    if statuses is None:
        return relationships

    allowed = set(statuses)
    return [
        relationship
        for relationship in relationships
        if relationship["status"] in allowed
    ]


def relationships_by_builder_api(relationships):
    result = {}
    for relationship in validate_id_relationships(relationships):
        builder_api = relationship["builder_api"]
        if builder_api in result:
            raise ValueError(
                "duplicate id relationship builder_api: %r" % builder_api
            )
        result[builder_api] = relationship
    return result


def consumer_root_sections(relationships):
    result = []
    seen = set()
    for relationship in validate_id_relationships(relationships):
        section = _path_root(relationship["consumer"])
        if section not in seen:
            seen.add(section)
            result.append(section)
    return result


def _path_root(path):
    root = path.split(".", 1)[0]
    if root.endswith("[*]"):
        root = root[:-3]
    if not root:
        raise ValueError("unsupported empty relationship path root: %r" % path)
    return root






# {
#     "body.material": {
#         "namespace": "volume",
#         "consumer": "materials[*].id",
#         ...
#     },
#     "body.velocity": {
#         "namespace": "volume",
#         "consumer": "initial_conditions.velocity[*].id",
#         ...
#     }
# }
