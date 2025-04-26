from openai_client import OpenAIClient
import pos_tagging  # Make sure pos_tagging is imported
import random


def suggest_new_facet_values(products, facet_name, existing_values):
    """Suggest up to 2 new facet values based on catalog analysis."""
    openai_client = OpenAIClient()

    company_name = products[0].get("vendor", "Unknown Company")

    all_keywords = []

    for product in products:
        body_html = product.get("body_html", "")
        all_keywords.extend(pos_tagging.extract_keywords(body_html))


    # Randomly select keywords
    all_keywords = random.sample(all_keywords, min(300, len(all_keywords)))

    keywords_str = " ".join(all_keywords)

    gpt_response = openai_client.suggest_facet_values(keywords_str, facet_name, existing_values, company_name)

    if not gpt_response or gpt_response.lower() == "none":
        return []

    suggested_values = [v.strip() for v in gpt_response.split(",") if v.strip()]
    return suggested_values[:5]
