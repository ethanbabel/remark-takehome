from openai_client import OpenAIClient
import pos_tagging
import random

def suggest_new_facets(products, existing_facets):
    """
    Suggest entirely new facets based on product data.
    """
    openai_client = OpenAIClient()

    company_name = products[0].get("vendor", "Unknown Company")

    # Extract keywords from product descriptions
    all_keywords = []
    for product in products:
        body_html = product.get("body_html", "")
        all_keywords.extend(pos_tagging.extract_keywords(body_html))

    # Randomly sample keywords to avoid exceeding token limits
    all_keywords = random.sample(all_keywords, min(300, len(all_keywords)))

    keywords_str = " ".join(all_keywords)

    # Use OpenAI to suggest new facets
    gpt_response = openai_client.suggest_new_facets(keywords_str, existing_facets, company_name)

    if not gpt_response or gpt_response.lower() == "none":
        return []

    # Parse GPT response into a dictionary of facets and their allowed values
    suggested_facets = {}
    for line in gpt_response.split("\n"):
        if ":" in line:
            facet, values = line.split(":", 1)
            facet = facet.strip()
            values = [v.strip() for v in values.split(",") if v.strip()]
            suggested_facets[facet] = values

    return suggested_facets