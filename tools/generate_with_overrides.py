"""Run the generated class/API generator with optional maintainer overrides."""

import argparse
import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
GENERATOR_DIR = PROJECT_ROOT / "generator"
if str(GENERATOR_DIR) not in sys.path:
    sys.path.insert(0, str(GENERATOR_DIR))

from generator.JsonToTreeClass import (  # noqa: E402
    DEFAULT_API_OUTPUT_FILE,
    DEFAULT_OUTPUT_FILE,
    DEFAULT_SCHEMA_FILE,
    generate,
    load_generator_overrides,
)
from validators.id_relationships import (  # noqa: E402
    DEFAULT_RELATIONSHIPS_PATH,
    check_files as check_id_relationship_files,
)
from validators.api_aliases import (  # noqa: E402
    DEFAULT_ALIASES_PATH,
    check_files as check_api_aliases_files,
)
from model_builder import DEFAULT_MODEL_ENTRY, write_builder_api_manifest  # noqa: E402


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Generate generated_class.py and generated_api.py with optional maintainer overrides.",
    )
    parser.add_argument(
        "--schema-file",
        default=DEFAULT_SCHEMA_FILE,
        help=(
            "Input JSON schema file. Defaults to "
            f"{DEFAULT_SCHEMA_FILE.relative_to(PROJECT_ROOT).as_posix()}."
        ),
    )
    parser.add_argument(
        "--output-file",
        default=DEFAULT_OUTPUT_FILE,
        help="Output generated_class.py path.",
    )
    parser.add_argument(
        "--api-output-file",
        default=DEFAULT_API_OUTPUT_FILE,
        help="Output generated_api.py path.",
    )
    parser.add_argument(
        "--overrides",
        default=None,
        help="Optional maintainer-authored generator_overrides.json path.",
    )
    parser.add_argument(
        "--include-spec-dir",
        action="append",
        default=[],
        type=Path,
        help=(
            "Additional directory to search for included spec files. "
            "Can be passed more than once."
        ),
    )
    parser.add_argument(
        "--manifest-dir",
        default=None,
        help="Directory for schema/API manifests. Defaults to the generated API directory.",
    )
    parser.add_argument(
        "--relationships",
        default=None,
        type=Path,
        help=(
            "Optional path to id_relationships JSON config. "
            f"Example default: {DEFAULT_RELATIONSHIPS_PATH}"
        ),
    )
    parser.add_argument(
        "--skip-id-relationship-check",
        action="store_true",
        help="Skip validating id_relationships.json against generated manifests.",
    )
    parser.add_argument(
        "--api-aliases",
        dest="api_aliases",
        default=None,
        type=Path,
        help=(
            "Optional path to api_aliases JSON config. "
            f"Example default: {DEFAULT_ALIASES_PATH}"
        ),
    )
    parser.add_argument(
        "--skip-api-aliases",
        action="store_true",
        help="Do not merge api_aliases into the generator overrides.",
    )
    parser.add_argument(
        "--skip-api-alias-check",
        dest="skip_api_alias_check",
        action="store_true",
        help="Skip validating api_aliases against generated manifests.",
    )
    parser.add_argument(
        "--builder-api-manifest",
        default=None,
        type=Path,
        help="Output builder_api_manifest.json path. Defaults to the manifest directory.",
    )
    parser.add_argument(
        "--model-entry",
        default=DEFAULT_MODEL_ENTRY,
        help="Model builder entry name written to builder_api_manifest.json.",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    generator_overrides = merged_generator_overrides(
        args.overrides,
        None if args.skip_api_aliases else args.api_aliases,
    )
    generate(
        schema_file=args.schema_file,
        output_file=args.output_file,
        api_output_file=args.api_output_file,
        manifest_dir=args.manifest_dir,
        generator_overrides=generator_overrides,
        include_spec_dirs=args.include_spec_dir,
    )
    manifest_dir = _manifest_dir(args)
    if args.relationships is not None:
        builder_api_manifest_path = (
            args.builder_api_manifest
            if args.builder_api_manifest is not None
            else manifest_dir / "builder_api_manifest.json"
        )
        write_builder_api_manifest(
            args.relationships,
            manifest_dir / "class_tree_manifest.json",
            builder_api_manifest_path,
            model_entry=args.model_entry,
        )
        print(f"Generated {builder_api_manifest_path}")

    if args.relationships is not None and not args.skip_id_relationship_check:
        issues = check_id_relationship_files(
            args.relationships,
            manifest_dir / "class_tree_manifest.json",
            manifest_dir / "generated_api_manifest.json",
        )
        if issues:
            print("FAILED: id relationship validation found issues:")
            for issue in issues:
                print(f"- {issue}")
            return 1

        print("OK: id relationship check passed.")

    if (
        args.api_aliases is not None
        and not args.skip_api_alias_check
        and not args.skip_api_aliases
    ):
        issues = check_api_aliases_files(
            args.api_aliases,
            manifest_dir / "generated_api_manifest.json",
        )
        if issues:
            print("FAILED: api aliases validation found issues:")
            for issue in issues:
                print(f"- {issue}")
            return 1

        print("OK: api aliases check passed.")

    return 0


def _manifest_dir(args):
    if args.manifest_dir is not None:
        return Path(args.manifest_dir)
    return Path(args.api_output_file).parent


def merged_generator_overrides(overrides_file=None, api_aliases_path=None):
    overrides = load_generator_overrides(overrides_file)
    if api_aliases_path is None:
        return overrides

    aliases = load_api_aliases(api_aliases_path)
    if not aliases:
        return overrides

    merged = dict(overrides)
    merged["api_aliases"] = [
        *merged.get("api_aliases", []),
        *aliases,
    ]
    return merged


def load_api_aliases(path):
    path = Path(path)
    with path.open(encoding="utf-8") as f:
        data = json.load(f)

    aliases = data.get("api_aliases")
    if not isinstance(aliases, list):
        raise ValueError(f"api aliases file must contain an api_aliases list: {path}")
    return aliases


if __name__ == "__main__":
    raise SystemExit(main())
