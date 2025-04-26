import yaml

class ConfigLoaderError(Exception):
    pass

def load_facet_config(config_path):
    """Load and validate the facet config from a YAML file."""
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    if "facets" not in config:
        raise ConfigLoaderError("Config file must have a 'facets' section.")

    facets = config["facets"]
    if not isinstance(facets, dict):
        raise ConfigLoaderError("'facets' section must be a dictionary.")

    validated_facets = {}

    for facet_name, facet_info in facets.items():
        if not isinstance(facet_info, dict):
            raise ConfigLoaderError(f"Facet '{facet_name}' must map to a dictionary.")
        
        allowed_values = facet_info.get("allowed_values", None)
        multi_valued = facet_info.get("multi_valued", False)
        required = facet_info.get("required", False)
        default_value = facet_info.get("default_value", None)

        if allowed_values is None or not isinstance(allowed_values, list):
            raise ConfigLoaderError(f"'allowed_values' for facet '{facet_name}' must be a list.")
        if isinstance(allowed_values, list) and len(allowed_values) == 0:
            raise ConfigLoaderError(f"'allowed_values' for facet '{facet_name}' cannot be an empty list.")
        if not isinstance(multi_valued, bool):
            raise ConfigLoaderError(f"'multi_valued' for facet '{facet_name}' must be a boolean.")
        if not isinstance(required, bool):
            raise ConfigLoaderError(f"'required' for facet '{facet_name}' must be a boolean.")
        if default_value is not None and not isinstance(default_value, str):
            raise ConfigLoaderError(f"'default_value' for facet '{facet_name}' must be a string or null.")
        
        validated_facets[facet_name] = {
            "allowed_values": allowed_values,
            "multi_valued": multi_valued,
            "required": required,
            "default_value": default_value
        }

    return validated_facets


if __name__ == "__main__":
    # Example usage
    try:
        config = load_facet_config("input_examples/example_config.yaml")
        print("Loaded facet config:", config)
    except ConfigLoaderError as e:
        print("Error loading facet config:", e)