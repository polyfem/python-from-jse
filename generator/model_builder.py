import json
import re
import uuid
from pathlib import Path

from id_relationships import (
    consumer_root_sections,
    load_id_relationships,
    relationships_by_builder_api,
)
from selection_refs import SelectionPool


_MISSING = object()
DEFAULT_MODEL_ENTRY = "generated_api.model"
DEFAULT_CLASS_TREE_MANIFEST_PATH = (
    Path(__file__).resolve().parents[1]
    / "generated"
    / "class_tree_manifest.json"
)
_SELECTION_BASE_CLASS_PATHS = {
    "surface": "Root.Geometry.Mesh.Surface_selection",
    "point": "Root.Geometry.Mesh.Point_selection",
}
_SKIPPED_SELECTION_RULE_CLASS_NAMES = {"Item", "List", "ValueWithUnit"}


class ModelBuilder:
    def __init__(
        self,
        api_module,
        *,
        relationships=None,
        selection_pool=None,
        selection_helper_rules=None,
    ):
        self._api = api_module
        self._selection_pool = selection_pool or SelectionPool()
        if relationships is None:
            relationships = load_api_adjacent_relationships(api_module)
        if relationships is None:
            relationships = load_id_relationships(statuses={"required"})
        relationships = list(relationships)
        self._relationships_by_api = relationships_by_builder_api(relationships)
        self._config_consumer_sections = consumer_root_sections(relationships)
        if selection_helper_rules is None:
            class_tree_manifest_path = api_adjacent_manifest_path(
                api_module,
                "class_tree_manifest.json",
            )
            selection_helper_rules = load_selection_helper_rules(
                class_tree_manifest_path,
            )
        self._selection_helper_rules = dict(selection_helper_rules)
        self._geometry = []
        self._mesh_by_uuid = {}
        self._consumer_lists = {}
        self._selection_backend_id_by_signature = {}

    def mesh(self, **kwargs):
        values = dict(kwargs)
        mesh_uuid = str(uuid.uuid4())
        volume_ref = self._selection_pool.allocate(
            "volume",
            backend_id=values.get("volume_selection"),
            mesh_uuid=mesh_uuid,
        )
        values["volume_selection"] = volume_ref.backend_id
        mesh_object = self._api.mesh(**values)
        self._geometry.append(mesh_object)
        self._mesh_by_uuid[mesh_uuid] = mesh_object
        return BodyHandle(self, mesh_uuid, volume_ref)

    def geometry(self):
        return [_payload_dict(item) for item in self._geometry]

    def materials(self):
        return self._consumer_root_section("materials")

    def initial_conditions(self):
        return self._consumer_root_section("initial_conditions")

    def space(self):
        return self._consumer_root_section("space")

    def boundary_conditions(self, **kwargs):
        section = dict(kwargs)
        for key, items in self._consumer_section(("boundary_conditions",)).items():
            if key in section and section[key]:
                if not isinstance(section[key], list):
                    raise ValueError(
                        "boundary_conditions.%s already has a non-list value" % key
                    )
                section[key] = list(section[key]) + list(items)
            else:
                section[key] = list(items)
        return section

    def config(self, **kwargs):
        values = dict(kwargs)
        rhs = values.pop("rhs", _MISSING)

        if "geometry" not in values:
            values["geometry"] = self.geometry()

        explicit_boundary = values.pop("boundary_conditions", _MISSING)
        if explicit_boundary is _MISSING:
            boundary_kwargs = {}
        elif explicit_boundary is None:
            boundary_kwargs = {}
        else:
            boundary_kwargs = _payload_dict(explicit_boundary)

        if rhs is not _MISSING:
            if "rhs" in boundary_kwargs:
                raise TypeError(
                    "Use either rhs=... or boundary_conditions with rhs, not both"
            )
            boundary_kwargs["rhs"] = rhs

        for section in self._config_consumer_sections:
            if section == "boundary_conditions":
                continue
            if section in values:
                continue
            payload = self._consumer_root_section(section)
            if payload:
                values[section] = payload

        boundary_conditions = self.boundary_conditions(**boundary_kwargs)
        if (
            boundary_conditions
            or explicit_boundary is not _MISSING
            or rhs is not _MISSING
        ):
            values["boundary_conditions"] = boundary_conditions

        return self._api.config(**values)

    def _add_surface_selection(self, mesh_uuid, payload, *, append=True):
        return self._add_geometry_selection(
            mesh_uuid,
            namespace="surface",
            geometry_field="surface_selection",
            payload=payload,
            append=append,
        )

    def _add_point_selection(self, mesh_uuid, payload):
        return self._add_geometry_selection(
            mesh_uuid,
            namespace="point",
            geometry_field="point_selection",
            payload=payload,
            append=True,
        )

    def _add_geometry_selection(
        self,
        mesh_uuid,
        *,
        namespace,
        geometry_field,
        payload,
        append,
    ):
        values = dict(payload)
        backend_id = values.pop("id", None)
        signature = _selection_signature(namespace, values)
        if backend_id is None and signature in self._selection_backend_id_by_signature:
            backend_id = self._selection_backend_id_by_signature[signature]
        selection_ref = self._selection_pool.allocate(
            namespace,
            backend_id=backend_id,
            mesh_uuid=mesh_uuid,
        )
        self._selection_backend_id_by_signature.setdefault(
            signature,
            selection_ref.backend_id,
        )

        if append:
            geometry_payload = {"id": selection_ref.backend_id}
            geometry_payload.update(values)
        else:
            geometry_payload = selection_ref.backend_id

        self._set_mesh_selection_field(
            mesh_uuid,
            geometry_field,
            geometry_payload,
            append=append,
        )
        return SelectionHandle(self, selection_ref)

    def _set_mesh_selection_field(self, mesh_uuid, field, payload, *, append):
        mesh_object = self._mesh_by_uuid[mesh_uuid]
        current = _payload_dict(mesh_object).get(field)

        if append:
            if current is None or current == []:
                next_value = [_copy_payload(payload)]
            elif isinstance(current, list):
                next_value = list(current) + [_copy_payload(payload)]
            else:
                raise ValueError("cannot append %s to existing non-list value" % field)
        else:
            if current is not None and current != []:
                raise ValueError("%s already exists for this mesh" % field)
            next_value = payload

        _set_payload_field(mesh_object, field, next_value)

    def bind(self, builder_api, selection_ref, value):
        relationship = self._relationship_for(builder_api)
        if relationship["namespace"] != selection_ref.namespace:
            raise ValueError(
                "%s expects %s selection, got %s"
                % (builder_api, relationship["namespace"], selection_ref.namespace)
            )

        consumer_path, id_field = _parse_list_item_consumer(relationship["consumer"])
        payload = _payload_dict(value)
        payload[id_field] = selection_ref.backend_id
        items = self._consumer_lists.setdefault(consumer_path, [])
        if payload not in items:
            items.append(payload)
        return payload

    def _relationship_for(self, builder_api):
        relationship = self._relationships_by_api.get(builder_api)
        if relationship is None:
            raise ValueError("missing ID relationship for builder API %r" % builder_api)
        return relationship

    def has_builder_api(self, builder_api):
        return builder_api in self._relationships_by_api

    def has_selection_helper(self, method_name):
        return method_name in self._selection_helper_rules

    def add_selection_with_helper(self, mesh_uuid, method_name, payload):
        rule = self._selection_helper_rules[method_name]
        _validate_selection_helper_payload(method_name, payload, rule["allowed_fields"])
        return self._add_geometry_selection(
            mesh_uuid,
            namespace=rule["namespace"],
            geometry_field=rule["geometry_field"],
            payload=payload,
            append=True,
        )

    def _consumer_section(self, section_path):
        section = {}
        prefix_len = len(section_path)
        for consumer_path, items in self._consumer_lists.items():
            if (
                len(consumer_path) == prefix_len + 1
                and consumer_path[:prefix_len] == section_path
            ):
                section[consumer_path[-1]] = list(items)
        return section

    def _consumer_root_section(self, section):
        section_path = (section,)
        if section_path in self._consumer_lists:
            return list(self._consumer_lists[section_path])
        return self._consumer_section(section_path)


class BodyHandle:
    def __init__(self, model, mesh_uuid, volume_ref):
        self._model = model
        self.mesh_uuid = mesh_uuid
        self.volume_ref = volume_ref

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)

        builder_api = "body.%s" % name
        if not self._model.has_builder_api(builder_api):
            selection_helper = self._dynamic_selection_helper(name)
            if selection_helper is not None:
                return selection_helper
            raise AttributeError(
                "%s has no configured builder API %r"
                % (self.__class__.__name__, builder_api)
            )

        def bind_value(*args, **kwargs):
            value = _bind_payload_from_call(builder_api, args, kwargs)
            self._model.bind(builder_api, self.volume_ref, value)
            return self

        bind_value.__name__ = name
        return bind_value

    def _dynamic_selection_helper(self, name):
        if not self._model.has_selection_helper(name):
            return None

        def add_selection(*args, **kwargs):
            if args:
                raise TypeError("%s accepts keyword fields only" % name)
            return self._model.add_selection_with_helper(
                self.mesh_uuid,
                name,
                kwargs,
            )

        add_selection.__name__ = name
        return add_selection

    def surface_all(self, *, id=None):
        payload = {"id": id} if id is not None else {}
        return self._model._add_surface_selection(
            self.mesh_uuid,
            payload,
            append=False,
        )


class SelectionHandle:
    def __init__(self, model, selection_ref):
        self._model = model
        self.selection_ref = selection_ref

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)

        builder_api = "%s.%s" % (self.selection_ref.namespace, name)
        if not self._model.has_builder_api(builder_api):
            raise AttributeError(
                "%s has no configured builder API %r"
                % (self.__class__.__name__, builder_api)
            )

        def bind_value(*args, **kwargs):
            value = _bind_payload_from_call(builder_api, args, kwargs)
            self._model.bind(builder_api, self.selection_ref, value)
            return self

        bind_value.__name__ = name
        return bind_value


def _parse_list_item_consumer(consumer):
    parts = consumer.split(".")
    if len(parts) < 2 or parts[-1] != "id":
        raise ValueError("unsupported ID consumer path: %r" % consumer)

    list_path = []
    for part in parts[:-1]:
        if part.endswith("[*]"):
            list_path.append(part[:-3])
        else:
            list_path.append(part)

    return tuple(list_path), parts[-1]


def _bind_payload_from_call(builder_api, args, kwargs):
    if len(args) > 1:
        raise TypeError("%s accepts at most one payload object" % builder_api)
    if args and kwargs:
        raise TypeError(
            "%s accepts either a payload object or keyword fields, not both"
            % builder_api
        )
    if args:
        return args[0]
    if kwargs:
        return kwargs
    raise TypeError("%s requires a payload object or keyword fields" % builder_api)


def _payload_dict(value):
    if isinstance(value, dict):
        return dict(value)
    if hasattr(value, "as_dict"):
        payload = value.as_dict()
        if not isinstance(payload, dict):
            raise TypeError("as_dict() must return a dict")
        return dict(payload)
    raise TypeError("expected dict or generated object with as_dict()")


def _copy_payload(value):
    if isinstance(value, dict):
        return dict(value)
    if isinstance(value, list):
        return [_copy_payload(item) for item in value]
    return value


def _selection_signature(namespace, values):
    return (
        namespace,
        tuple(
            (key, _freeze_value(value))
            for key, value in sorted(values.items())
        ),
    )


def _freeze_value(value):
    if isinstance(value, dict):
        return tuple(
            (key, _freeze_value(child))
            for key, child in sorted(value.items())
        )
    if isinstance(value, list):
        return tuple(_freeze_value(child) for child in value)
    return value


def _set_payload_field(value, field, field_value):
    if isinstance(value, dict):
        value[field] = field_value
        return
    if hasattr(value, field):
        setattr(value, field, field_value)
        return
    raise TypeError("expected dict or generated object with %s field" % field)


def load_selection_helper_rules(path=None):
    manifest_path = Path(path) if path is not None else DEFAULT_CLASS_TREE_MANIFEST_PATH
    with manifest_path.open(encoding="utf-8") as f:
        return selection_helper_rules_from_manifest(json.load(f))


def api_adjacent_manifest_path(api_module, filename):
    module_file = getattr(api_module, "__file__", None)
    if not module_file:
        return None

    path = Path(module_file).resolve().parent / filename
    return path if path.exists() else None


def load_api_adjacent_relationships(api_module):
    manifest_path = api_adjacent_manifest_path(
        api_module,
        "builder_api_manifest.json",
    )
    if manifest_path is None:
        return None

    with manifest_path.open(encoding="utf-8") as f:
        manifest = json.load(f)

    relationships = []
    for item in manifest.get("relationships", []):
        relationship = dict(item)
        relationship.setdefault("status", "required")
        relationships.append(relationship)
    return relationships


def write_builder_api_manifest(
    relationships_path,
    class_tree_manifest_path,
    output_path,
    model_entry=DEFAULT_MODEL_ENTRY,
):
    relationships = load_id_relationships(relationships_path, statuses={"required"})
    with Path(class_tree_manifest_path).open(encoding="utf-8") as f:
        class_tree_manifest = json.load(f)

    manifest = builder_api_manifest_from_inputs(
        relationships,
        class_tree_manifest,
        model_entry=model_entry,
    )
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")
    return manifest


def builder_api_manifest_from_inputs(
    relationships,
    class_tree_manifest,
    model_entry=DEFAULT_MODEL_ENTRY,
):
    relationships = list(relationships)
    relationships_by_builder_api(relationships)

    body_methods = []
    selection_methods = {}
    relationship_entries = []

    for relationship in relationships:
        builder_api = relationship["builder_api"]
        scope, method = _split_builder_api(builder_api)
        if scope == "body":
            body_methods.append(method)
        else:
            selection_methods.setdefault(scope, []).append(method)
        relationship_entries.append(
            {
                "builder_api": builder_api,
                "namespace": relationship["namespace"],
                "producer": relationship["producer"],
                "consumer": relationship["consumer"],
            }
        )

    selection_helpers = {}
    for method_name, rule in selection_helper_rules_from_manifest(
        class_tree_manifest
    ).items():
        selection_helpers.setdefault(rule["namespace"], []).append(method_name)

    return {
        "version": 1,
        "model_entry": model_entry,
        "body_methods": sorted(body_methods),
        "selection_methods": _sorted_values(selection_methods),
        "selection_helpers": _sorted_values(selection_helpers),
        "config_auto_sections": sorted(consumer_root_sections(relationships)),
        "relationships": sorted(
            relationship_entries,
            key=lambda item: item["builder_api"],
        ),
    }


def selection_helper_rules_from_manifest(manifest):
    params_by_class_path = {
        entry["class_path"]: tuple(entry.get("params", []))
        for entry in manifest
        if isinstance(entry, dict) and entry.get("class_path")
    }
    result = {}
    for namespace, base_class_path in _SELECTION_BASE_CLASS_PATHS.items():
        geometry_field = "%s_selection" % namespace
        for rule_path in _selection_rule_class_paths(
            params_by_class_path,
            base_class_path,
        ):
            allowed_fields = params_by_class_path[rule_path]
            if "id" not in allowed_fields:
                continue
            rule_name = _class_leaf_to_helper_name(rule_path.rsplit(".", 1)[-1])
            method_name = "%s_%s" % (namespace, rule_name)
            result[method_name] = {
                "namespace": namespace,
                "geometry_field": geometry_field,
                "allowed_fields": allowed_fields,
            }
    return result


def _selection_rule_class_paths(params_by_class_path, base_class_path):
    for child_path in _direct_child_class_paths(params_by_class_path, base_class_path):
        child_name = child_path.rsplit(".", 1)[-1]
        if child_name == "List":
            for list_child_path in _direct_child_class_paths(
                params_by_class_path,
                child_path,
            ):
                list_child_name = list_child_path.rsplit(".", 1)[-1]
                if list_child_name not in _SKIPPED_SELECTION_RULE_CLASS_NAMES:
                    yield list_child_path
        elif child_name not in _SKIPPED_SELECTION_RULE_CLASS_NAMES:
            yield child_path


def _direct_child_class_paths(params_by_class_path, parent_class_path):
    prefix = parent_class_path + "."
    result = []
    for class_path in params_by_class_path:
        if not class_path.startswith(prefix):
            continue
        remainder = class_path[len(prefix):]
        if "." not in remainder:
            result.append(class_path)
    return result


def _class_leaf_to_helper_name(class_leaf):
    name = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", class_leaf)
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    return name.lower()


def _validate_selection_helper_payload(method_name, payload, allowed_fields):
    allowed = set(allowed_fields)
    unknown = sorted(set(payload) - allowed)
    if unknown:
        raise TypeError(
            "%s got unsupported field(s): %s"
            % (method_name, ", ".join(unknown))
        )


def _split_builder_api(builder_api):
    parts = builder_api.split(".", 1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError("unsupported builder API name: %r" % builder_api)
    return parts[0], parts[1]


def _sorted_values(mapping):
    return {
        key: sorted(values)
        for key, values in sorted(mapping.items())
    }
