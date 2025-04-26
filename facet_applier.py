import re
from openai_client import OpenAIClient
from pos_tagging import extract_keywords

def _clean_tag_part(part):
    """Clean tag keys or values by removing leading/trailing punctuation."""
    return re.sub(r'^[^\w]+|[^\w]+$', '', part.strip())

def apply_facets_to_products(products, facets):
    """Apply user-defined facets to a list of products."""
    labeled_products = []
    openai_client = OpenAIClient()

    for product in products:
        applied_facets = {}

        for facet_name, facet_info in facets.items():
            allowed_values = facet_info.get("allowed_values", [])
            multi_valued = facet_info.get("multi_valued", False)
            required = facet_info.get("required", False)
            default_value = facet_info.get("default_value", None)

            # Try matching from tags
            matched_values = match_tags(product, facet_name, allowed_values)

            # Try matching from OpenAI
            if not matched_values and allowed_values:
                product_text = build_product_text(product)
                gpt_response = openai_client.classify_facet_value(
                    product_text=product_text,
                    facet_name=facet_name,
                    candidate_values=allowed_values,
                    multi_valued=multi_valued,
                    required_response=(required and (default_value is None)),
                    vendor=product.get("vendor", "Unknown Vendor"),
                )
                if gpt_response and gpt_response.lower() != "none":
                    matched_values = [v.strip() for v in gpt_response.split(",") if v.strip() and v.strip().lower() != "none"]

            # Fallback to default if required
            if not matched_values and required:
                matched_values = [default_value] if default_value else []

            if matched_values:
                applied_facets[facet_name] = matched_values

        labeled_products.append({
            "id": product.get("id"),
            "title": product.get("title"),
            "facets": applied_facets
        })

    return labeled_products

def match_tags(product, facet_name, allowed_values):
    """Check if any tags match the facet."""
    tags = product.get("tags", [])
    matches = []
    for tag in tags:
        if ':' in tag:
            key, value = tag.split(':', 1)
            key = _clean_tag_part(key)
            value = _clean_tag_part(value)
            if key.lower() == facet_name.lower() and value in allowed_values:
                matches.append(value)
        else:
            value = _clean_tag_part(tag)
            if value in allowed_values:
                matches.append(value)
    return matches

def build_product_text(product):
    """Combine various product fields for LLM input."""
    parts = []
    if product.get('vendor'):
        parts.append(f"We are categorizing products from {product.get('vendor')}.")

    parts.append(f"Title: {product.get('title', '')}")
    description_keywords = extract_keywords(product.get('body_html', ''))
    parts.append(f"Description Keywords: {', '.join(description_keywords)}")

    if isinstance(product.get('options'), list):
        option_strings = []
        for opt in product['options']:
            if isinstance(opt, dict):
                name = opt.get("name", "")
                values = opt.get("values", [])
                if isinstance(values, list):
                    values_text = ", ".join(values)
                    option_strings.append(f"{name}: {values_text}")
        if option_strings:
            parts.append(f"Options: {'; '.join(option_strings)}")

    if product.get('price_range'):
        price_range = product['price_range']
        parts.append(f"Price Range: ${price_range.get('min_price', '')} - ${price_range.get('max_price', '')}")

    if product.get('handle'):
        parts.append(f"Handle: {product['handle']}")

    if product.get('product_type'):
        parts.append(f"Product Type: {product['product_type']}")

    tags = product.get("tags", [])
    if tags:
        parts.append(f"Tags: {', '.join(tags)}")

    return "\n".join(parts)