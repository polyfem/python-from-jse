import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from generator.id_relationships import (
    relationships_by_builder_api,
    validate_id_relationships,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GENERATED_DIR = PROJECT_ROOT / "generated"
DEFAULT_RELATIONSHIPS_PATH = (
    PROJECT_ROOT
    / "examples"
    / "config_capabilities"
    / "id_relationships.example.json"
)
DEFAULT_CLASS_TREE_MANIFEST_PATH = DEFAULT_GENERATED_DIR / "class_tree_manifest.json"
DEFAULT_GENERATED_API_MANIFEST_PATH = DEFAULT_GENERATED_DIR / "generated_api_manifest.json"


@dataclass
class PathMatch:
    exists: bool
    terminal_class_paths: set


class ClassTreeIndex:
    def __init__(self, manifest):
        self.params_by_class_path = {
            entry["class_path"]: set(entry.get("params", []))
            for entry in manifest
            if isinstance(entry, dict) and entry.get("class_path")
        }
        self.children_by_parent = {}
        for class_path in self.params_by_class_path:
            if "." not in class_path:
                continue
            parent = class_path.rsplit(".", 1)[0]
            self.children_by_parent.setdefault(parent, []).append(class_path)

    def resolve_path(self, relationship_path):
        candidates = {"Root"}
        segments = _split_relationship_path(relationship_path)

        for index, (segment, is_array) in enumerate(segments):
            is_last = index == len(segments) - 1
            next_candidates = set()
            terminal_matches = set()

            for class_path in candidates:
                params = self.params_by_class_path.get(class_path, set())
                if segment == "*":
                    matching_children = self.children_by_parent.get(class_path, [])
                    next_candidates.update(matching_children)
                    if is_last:
                        terminal_matches.update(
                            child
                            for child in matching_children
                            if self.params_by_class_path.get(child)
                        )
                    continue

                if segment not in params:
                    continue

                if is_last:
                    terminal_matches.add(class_path)
                else:
                    next_candidates.update(
                        self._matching_children_for_param(class_path, segment)
                    )

            if is_last:
                return PathMatch(bool(terminal_matches), terminal_matches)

            if not next_candidates:
                return PathMatch(False, set())

            if is_array:
                next_candidates = self._expand_array_candidates(next_candidates)
            candidates = next_candidates

        return PathMatch(False, set())

    def _matching_children_for_param(self, class_path, param):
        result = []
        for child in self.children_by_parent.get(class_path, []):
            leaf = child.rsplit(".", 1)[-1]
            if param in _leaf_param_candidates(leaf):
                result.append(child)
        return result

    def _expand_array_candidates(self, class_paths):
        expanded = set(class_paths)
        for class_path in class_paths:
            prefix = class_path + "."
            for candidate in self.params_by_class_path:
                if candidate.startswith(prefix):
                    expanded.add(candidate)
        return expanded


def load_json(path):
    with Path(path).open(encoding="utf-8") as f:
        return json.load(f)


def validate_relationships_against_manifests(
    relationships,
    class_tree_manifest,
    generated_api_manifest,
):
    issues = []

    try:
        relationships = validate_id_relationships(relationships)
    except ValueError as exc:
        return [f"id_relationships.json structure error: {exc}"]

    try:
        relationships_by_builder_api(relationships)
    except ValueError as exc:
        issues.append(str(exc))

    class_tree = ClassTreeIndex(class_tree_manifest)
    api_class_paths = _manifest_class_paths(generated_api_manifest)

    for relationship in relationships:
        builder_api = relationship["builder_api"]
        for field in ("producer", "consumer"):
            relationship_path = relationship[field]
            match = class_tree.resolve_path(relationship_path)
            if not match.exists:
                issues.append(
                    "%s path not found in class_tree_manifest for %s: %s"
                    % (field, builder_api, relationship_path)
                )
                continue

            if not match.terminal_class_paths.intersection(api_class_paths):
                issues.append(
                    "%s path exists in class_tree_manifest but is not exported "
                    "in generated_api_manifest for %s: %s"
                    % (field, builder_api, relationship_path)
                )

    issues.extend(_check_surface_point_boundary_parity(relationships))
    return issues


def check_files(
    relationships_path=DEFAULT_RELATIONSHIPS_PATH,
    class_tree_manifest_path=DEFAULT_CLASS_TREE_MANIFEST_PATH,
    generated_api_manifest_path=DEFAULT_GENERATED_API_MANIFEST_PATH,
):
    return validate_relationships_against_manifests(
        load_json(relationships_path),
        load_json(class_tree_manifest_path),
        load_json(generated_api_manifest_path),
    )


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Validate id_relationships.json against generated manifests."
    )
    parser.add_argument(
        "--relationships",
        default=DEFAULT_RELATIONSHIPS_PATH,
        type=Path,
        help="Path to id_relationships JSON config.",
    )
    parser.add_argument(
        "--class-tree-manifest",
        default=DEFAULT_CLASS_TREE_MANIFEST_PATH,
        type=Path,
        help="Path to class_tree_manifest.json.",
    )
    parser.add_argument(
        "--generated-api-manifest",
        default=DEFAULT_GENERATED_API_MANIFEST_PATH,
        type=Path,
        help="Path to generated_api_manifest.json.",
    )
    args = parser.parse_args(argv)

    issues = check_files(
        args.relationships,
        args.class_tree_manifest,
        args.generated_api_manifest,
    )
    if issues:
        print("FAILED: id relationship validation found issues:")
        for issue in issues:
            print(f"- {issue}")
        return 1

    relationship_count = len(load_json(args.relationships))
    print(
        "OK: %d id relationship(s) match generated manifests."
        % relationship_count
    )
    return 0


def _manifest_class_paths(manifest):
    return {
        entry["class_path"]
        for entry in manifest
        if isinstance(entry, dict) and entry.get("class_path")
    }


def _split_relationship_path(path):
    result = []
    for raw_segment in path.split("."):
        is_array = raw_segment.endswith("[*]")
        segment = raw_segment[:-3] if is_array else raw_segment
        result.append((segment, is_array))
    return result


def _leaf_param_candidates(class_leaf):
    candidates = {class_leaf}
    if class_leaf:
        candidates.add(class_leaf[0].lower() + class_leaf[1:])
    return candidates


def _check_surface_point_boundary_parity(relationships):
    surface = _boundary_relationships_by_api_suffix(relationships, "surface")
    point = _boundary_relationships_by_api_suffix(relationships, "point")
    issues = []

    for api_suffix in sorted(set(surface) ^ set(point)):
        issues.append(
            "surface/point boundary relationship mismatch for %s: "
            "surface=%s point=%s"
            % (api_suffix, surface.get(api_suffix), point.get(api_suffix))
        )

    for api_suffix in sorted(set(surface).intersection(point)):
        if surface[api_suffix] != point[api_suffix]:
            issues.append(
                "surface/point boundary relationship mismatch for %s: "
                "surface=%s point=%s"
                % (api_suffix, surface[api_suffix], point[api_suffix])
            )

    return issues


def _boundary_relationships_by_api_suffix(relationships, namespace):
    prefix = namespace + "."
    result = {}
    for relationship in relationships:
        if relationship["namespace"] != namespace:
            continue
        if not relationship["consumer"].startswith("boundary_conditions."):
            continue
        builder_api = relationship["builder_api"]
        if not builder_api.startswith(prefix):
            continue
        result[builder_api[len(prefix):]] = relationship["consumer"]
    return result


if __name__ == "__main__":
    raise SystemExit(main())
