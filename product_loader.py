import json
import re
from shopify_client import ShopifyClient

class ProductLoaderError(Exception):
    pass

def check_raw_data(raw_data):
    """Validate the raw data structure for products."""
    if not isinstance(raw_data, list):
        raise ProductLoaderError("Product data must be a list.")
    for product in raw_data:
        if not isinstance(product, dict):
            raise ProductLoaderError("Each product must be a dictionary.")
        if 'id' not in product or 'title' not in product:
            raise ProductLoaderError("Each product must have 'id' and 'title'.")
    return raw_data

def load_products_from_file(filepath):
    """Load and validate products from a local JSON file."""
    try:
        with open(filepath, 'r') as f:
            raw_data = json.load(f)
            return raw_data
    except Exception as e:
        raise ProductLoaderError(f"Error loading product file: {e}")

def normalize_product(product):
    """Extract selected fields and normalize a single product."""
    normalized = {}

    fields = ["id", "title", "body_html", "vendor", "options", "handle", "product_type", "tags"]
    for field in fields:
        value = product.get(field)
        if value:
            normalized[field] = value

    # Handle price extraction
    variants = product.get("variants", [])
    if variants and isinstance(variants, list):
        prices = []
        for variant in variants:
            price = variant.get("price")
            if price:
                try:
                    prices.append(float(price))
                except ValueError:
                    continue
        if prices:
            normalized["price_range"] = {
                "min_price": min(prices),
                "max_price": max(prices)
            }

    # Handle images
    images = product.get("images", [])
    if images and isinstance(images, list):
        srcs = [img.get("src") for img in images if img.get("src")]
        if srcs:
            normalized["images"] = srcs

    return normalized

def get_products_from_file(filepath):
    raw_data = load_products_from_file(filepath)
    try:
        check_raw_data(raw_data)
    except ProductLoaderError as e:
        raise ProductLoaderError(f"Invalid product data: {e}")
    return [normalize_product(p) for p in raw_data]

def get_products_from_shopify(store_url):
    client = ShopifyClient(store_url)
    raw_data = client.fetch_all_products()
    try:
        check_raw_data(raw_data)
    except ProductLoaderError as e:
        raise ProductLoaderError(f"Invalid product data from Shopify: {e}")
    return [normalize_product(p) for p in raw_data] 
