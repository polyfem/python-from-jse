"""Helpers for applying user-facing generated API aliases."""


def expand_api_aliases(
    api_aliases,
    paths_by_name,
    generated_name_by_class_path,
    validate_api_function_name,
):
    """Expand api_aliases config into generator override entries."""
    custom_api_names = []
    skip_auto_generated_api_names = []

    for index, item in enumerate(api_aliases):
        if not isinstance(item, dict):
            raise ValueError(f"api_aliases[{index}] must be an object")

        main_class_path = item.get("main_class_path")
        if main_class_path not in paths_by_name:
            raise ValueError(f"api_aliases[{index}] references unknown main_class_path: {main_class_path!r}")

        main_api_name = validate_api_function_name(item.get("main_api_name"))
        main_generated_name = generated_name_by_class_path[main_class_path]
        requested_generated_name = item.get("api_generated_name")
        if requested_generated_name is not None and requested_generated_name != main_generated_name:
            raise ValueError(
                "api_aliases api_generated_name mismatch: "
                f"{requested_generated_name!r} != {main_generated_name!r}"
            )

        if main_api_name != main_generated_name:
            custom_api_names.append({
                "class_path": main_class_path,
                "api_custom_name": main_api_name,
                "_kind": "api_alias",
                "_source": "api_aliases",
            })

        aliases = item.get("aliases", [])
        if not isinstance(aliases, list):
            raise ValueError(f"api_aliases[{index}].aliases must be a list")

        for alias_index, alias in enumerate(aliases):
            if not isinstance(alias, dict):
                raise ValueError(
                    f"api_aliases[{index}].aliases[{alias_index}] must be an object"
                )

            alias_class_path = alias.get("alias_class_path")
            if alias_class_path not in paths_by_name:
                raise ValueError(
                    "api_aliases alias references unknown alias_class_path: "
                    f"{alias_class_path!r}"
                )

            alias_name = validate_api_function_name(alias.get("alias_name"))
            alias_generated_name = generated_name_by_class_path[alias_class_path]
            if alias_name != alias_generated_name:
                raise ValueError(
                    "api_aliases alias_name mismatch: "
                    f"{alias_name!r} != {alias_generated_name!r}"
                )

            if alias.get("hide", False):
                skip_auto_generated_api_names.append({
                    "class_path": alias_class_path,
                    "api_generated_name": alias_name,
                    "_source": "api_aliases",
                })

    return custom_api_names, skip_auto_generated_api_names
