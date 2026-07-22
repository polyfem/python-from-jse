import argparse
import json
import keyword
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GENERATED_DIR = PROJECT_ROOT / "generated"
DEFAULT_ALIASES_PATH = (
    PROJECT_ROOT
    / "examples"
    / "config_capabilities"
    / "api_aliases.example.json"
)
DEFAULT_GENERATED_API_MANIFEST_PATH = (
    DEFAULT_GENERATED_DIR / "generated_api_manifest.json"
)


def load_json(path):
    with Path(path).open(encoding="utf-8") as f:
        return json.load(f)


def validate_api_aliases_against_manifest(api_aliases_config, generated_api_manifest):
    issues = []
    manifest = GeneratedApiManifestIndex(generated_api_manifest)

    aliases = api_aliases_config.get("api_aliases")
    if not isinstance(aliases, list):
        return ["api_aliases must be a list"]

    for index, item in enumerate(aliases):
        issues.extend(_validate_alias_item(index, item, manifest))

    return issues


def check_files(
    aliases_path=DEFAULT_ALIASES_PATH,
    generated_api_manifest_path=DEFAULT_GENERATED_API_MANIFEST_PATH,
):
    return validate_api_aliases_against_manifest(
        load_json(aliases_path),
        load_json(generated_api_manifest_path),
    )


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "Validate api aliases config against "
            "generated_api_manifest.json."
        )
    )
    parser.add_argument(
        "--aliases",
        default=DEFAULT_ALIASES_PATH,
        type=Path,
        help="Path to api_aliases JSON config.",
    )
    parser.add_argument(
        "--generated-api-manifest",
        default=DEFAULT_GENERATED_API_MANIFEST_PATH,
        type=Path,
        help="Path to generated_api_manifest.json.",
    )
    args = parser.parse_args(argv)

    issues = check_files(args.aliases, args.generated_api_manifest)
    if issues:
        print("FAILED: api aliases validation found issues:")
        for issue in issues:
            print(f"- {issue}")
        return 1

    alias_count = len(load_json(args.aliases).get("api_aliases", []))
    print("OK: %d api alias item(s) match generated API manifest." % alias_count)
    return 0


class GeneratedApiManifestIndex:
    def __init__(self, manifest):
        self.entries_by_class_path = {
            entry["class_path"]: entry
            for entry in manifest
            if isinstance(entry, dict) and entry.get("class_path")
        }

    def has_class_path(self, class_path):
        return class_path in self.entries_by_class_path

    def entry(self, class_path):
        return self.entries_by_class_path.get(class_path)

    def api_names(self, class_path):
        entry = self.entry(class_path)
        if not entry:
            return set()

        names = set()
        generated_name = entry.get("api_generated_name")
        custom_name = entry.get("api_custom_name")
        if generated_name:
            names.add(generated_name)
        if custom_name:
            names.add(custom_name)
        return names

    def params(self, class_path):
        entry = self.entry(class_path) or {}
        return set(entry.get("params") or [])


def _validate_alias_item(index, item, manifest):
    issues = []
    prefix = "api_aliases[%d]" % index

    if not isinstance(item, dict):
        return [f"{prefix} must be an object"]

    main_api_name = item.get("main_api_name")
    main_class_path = item.get("main_class_path")
    if not _is_python_identifier(main_api_name):
        issues.append(f"{prefix}.main_api_name is not a valid Python identifier")

    if not main_class_path:
        issues.append(f"{prefix}.main_class_path is required")
    elif not manifest.has_class_path(main_class_path):
        issues.append(f"{prefix}.main_class_path not found: {main_class_path}")
    else:
        generated_name = item.get("api_generated_name")
        if generated_name is not None:
            if generated_name not in manifest.api_names(main_class_path):
                issues.append(
                    "%s.api_generated_name mismatch for %s: %s"
                    % (prefix, main_class_path, generated_name)
                )
        elif main_api_name not in manifest.api_names(main_class_path):
            issues.append(
                "%s.main_api_name mismatch for %s: %s"
                % (prefix, main_class_path, main_api_name)
            )

    aliases = item.get("aliases", [])
    if not isinstance(aliases, list):
        issues.append(f"{prefix}.aliases must be a list")
        return issues

    for alias_index, alias in enumerate(aliases):
        issues.extend(
            _validate_alias_entry(
                "%s.aliases[%d]" % (prefix, alias_index),
                alias,
                manifest,
            )
        )

    return issues


def _validate_alias_entry(prefix, alias, manifest):
    issues = []
    if not isinstance(alias, dict):
        return [f"{prefix} must be an object"]

    alias_name = alias.get("alias_name")
    alias_class_path = alias.get("alias_class_path")
    if not _is_python_identifier(alias_name):
        issues.append(f"{prefix}.alias_name is not a valid Python identifier")

    if not alias_class_path:
        issues.append(f"{prefix}.alias_class_path is required")
    elif not manifest.has_class_path(alias_class_path):
        issues.append(f"{prefix}.alias_class_path not found: {alias_class_path}")
    elif alias_name not in manifest.api_names(alias_class_path):
        issues.append(
            "%s.alias_name mismatch for %s: %s"
            % (prefix, alias_class_path, alias_name)
        )

    if not isinstance(alias.get("hide"), bool):
        issues.append(f"{prefix}.hide must be a boolean")
    if not alias.get("reason"):
        issues.append(f"{prefix}.reason is required")

    return issues


def _is_python_identifier(name):
    return isinstance(name, str) and name.isidentifier() and not keyword.iskeyword(name)


if __name__ == "__main__":
    raise SystemExit(main())
