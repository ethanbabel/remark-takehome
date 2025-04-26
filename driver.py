import json
import yaml
from product_loader import get_products_from_shopify, get_products_from_file
from facet_loader import load_facet_config
from facet_applier import apply_facets_to_products
from suggest_facet_values import suggest_new_facet_values
from suggest_new_facets import suggest_new_facets

def run_full_pipeline(store_url, product_file, output_file, user_defined_facets, suggest_facet_values_option, suggest_new_facets_option, limit=None):
    # Load products
    if store_url:
        products = get_products_from_shopify(store_url)
    else:
        products = get_products_from_file(product_file)

# Apply the limit if specified
    if limit is not None:
        print(f"Processing only the first {limit} products out of {len(products)} total products.")
        products = products[:limit]
        
    # Load user-defined facet config
    facets = load_facet_config(user_defined_facets) if user_defined_facets else {}
    # Suggest new facet values if enabled
    if suggest_facet_values_option.lower() in ("yes", "ask"):
        print("Suggesting new facet values...")
        for facet_name, existing_values in facets.items():
            if suggest_facet_values_option.lower() == "ask":
                print(f"Do you want to suggest new values for the facet '{facet_name}'? (y/n)")
                response = input().strip().lower()
                if response != "y":
                    continue

            # Suggest new values
            suggested_values = suggest_new_facet_values(products, facet_name, existing_values["allowed_values"])
            if not suggested_values:
                print(f"No new values suggested for the facet '{facet_name}'.")
                continue
            for value in suggested_values:
                print(f"Do you want to add '{value}' to the allowed values for the facet '{facet_name}'? (y/n)")
                response = input().strip().lower()
                if response == "y":
                    facets[facet_name]["allowed_values"].append(value)

    # Suggest entirely new facets if enabled
    if suggest_new_facets_option.lower() in ("yes", "ask"):
        print("Suggesting new facets...")
        new_facets = suggest_new_facets(products, {facet: config["allowed_values"] for facet, config in facets.items()})
        for facet_name, suggested_values in new_facets.items():
            suggested_values_str = ", ".join(suggested_values)
            if suggest_new_facets_option.lower() == "ask":
                print(f"Do you want to add the new facet '{facet_name}'? (Example values: {suggested_values_str}) (y/n)")
                response = input().strip().lower()
                if response != "y":
                    continue

            # Add the new facet
            facets[facet_name] = {
                "allowed_values": [],
                "multi_valued": False,
                "required": False,
                "default_value": None,
            }

            # Suggest values for the new facet
            for value in suggested_values:
                print(f"Do you want to add '{value}' to the allowed values for the new facet '{facet_name}'? (y/n)")
                response = input().strip().lower()
                if response == "y":
                    facets[facet_name]["allowed_values"].append(value)

            # Allow the user to input their own values
            print(f"Do you want to add your own values for the new facet '{facet_name}'? (y/n)")
            response = input().strip().lower()
            if response == "y":
                while True:
                    print(f"Enter a value for the facet '{facet_name}' (or type 'done' to finish):")
                    custom_value = input().strip()
                    if custom_value.lower() == "done":
                        break
                    facets[facet_name]["allowed_values"].append(custom_value)

            # Force the user to input the other facet config details
            print(f"Should products be allowed multiple values for the new facet '{facet_name}'? (y/n)")
            response = input().strip().lower()
            if response not in ("y", "n"):
                print("Invalid response. Please enter 'y' or 'n'.")
                while response not in ("y", "n"):
                    response = input().strip().lower()
            facets[facet_name]["multi_valued"] = (response == "y")

            print(f"Should the new facet '{facet_name}' be required for all products? (y/n)")
            response = input().strip().lower()
            if response not in ("y", "n"):
                print("Invalid response. Please enter 'y' or 'n'.")
                while response not in ("y", "n"):
                    response = input().strip().lower()
            facets[facet_name]["required"] = (response == "y")

            print(f"Enter a default value for the new facet '{facet_name}' (or type 'none' for no default):")
            response = input().strip()
            if response.lower() == "none":
                facets[facet_name]["default_value"] = None
            else:
                facets[facet_name]["default_value"] = response
    
    # Save the updated facets
    
    with open("output/updated_facets_config.yaml", "w") as f:
        yaml.dump({"facets": facets}, f)
    print("Facets saved to output/updated_facets_config.yaml")

    # Apply facets to products
    print("Applying facets to products...")
    labeled_products = apply_facets_to_products(products, facets)

    # Save labeled products to the output file
    with open(output_file, "w") as f:
        json.dump(labeled_products, f, indent=4)
    print(f"Labeled products saved to {output_file}")


