import os
import openai
from dotenv import load_dotenv

load_dotenv()

class OpenAIClient:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_KEY")
        if openai.api_key is None:
            raise ValueError("OPENAI_KEY not found in environment variables.")

    def classify_facet_value(self, product_text, facet_name, candidate_values, multi_valued, required_response, vendor, model="gpt-4"):
        """Use OpenAI to classify a product into facet value(s)."""
        if not candidate_values:
            raise ValueError("Candidate facet values must be provided.")

        prompt = self._build_assignment_prompt(product_text, facet_name, candidate_values, multi_valued, required_response, vendor)

        try:
            response = openai.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            output = response.choices[0].message.content.strip()
            return output
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return None

    def _build_assignment_prompt(self, product_text, facet_name, candidate_values, multi_valued, required_response, vendor):
        """Internal method to build the prompt text."""
        candidate_list = "\n".join(f"- {value}" for value in candidate_values)
        if multi_valued and not required_response:
            instruction = (
                f"The goal is to classify the above product from {vendor}."
                f" Choose all {facet_name} values from the list below that apply to the product."
                " If none apply, respond with 'None'. Respond only with a comma-separated list of the matching values or 'None'."
            )
        elif not multi_valued and not required_response:
            instruction = (
                f"The goal is to classify the above product from {vendor}."
                f" Choose the single best {facet_name} value from the list below for the product."
                " If none apply, respond with 'None'. Respond only with ONE value or 'None'."
            )
        elif multi_valued and required_response:
            instruction = (
                f"The goal is to classify the above product from {vendor}."
                f" Choose all {facet_name} values from the list below that apply to the product."
                " Respond only with a comma-separated list of the matching values."
            )
        else:
            instruction = (
                f"The goal is to classify the above product from {vendor}."
                f" Choose the single best {facet_name} value from the list below for the product."
                " Respond only with ONE value."
            )

        prompt = (
            f"Product Information:\n{product_text}\n\n"
            f"{instruction}\n"
            f"Candidate {facet_name} values:\n{candidate_list}"
        )

        return prompt

    def suggest_facet_values(self, catalog_snippets, facet_name, existing_values, company_name, model="gpt-4"):
        """Use OpenAI to suggest new facet values not currently listed."""
        prompt = self._build_value_suggestion_prompt(catalog_snippets, facet_name, existing_values, company_name)
        try:
            response = openai.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            output = response.choices[0].message.content.strip()
            return output
        except Exception as e:
            print(f"OpenAI API error (suggest_facet_values): {e}")
            return None

    def _build_value_suggestion_prompt(self, keywords_str, facet_name, existing_values, company_name):
        """Build prompt for suggesting new facet values."""
        existing_list = ", ".join(f"{value}" for value in existing_values)
        if company_name == "Unknown Company":
            company_name = "an unknown company"
        prompt = (
            f"The goal is to suggest new facet values to categorize the product catalog of {company_name}. "
            "Based on the following keywords that appear in product descriptions most often, suggest up to 5 new category values"
            "If less than 5 new facets values make sense, respond with only those that do."
            f" under the facet '{facet_name}' that are clearly applicable and distinct from the existing allowed values. "
            f"Respone with a comma seperated list. If no new values make sense, respond with 'None'.\n"
            f"Existing values for facet '{facet_name}': {existing_list}. \n"
            f"Keywords: {keywords_str}"
        )
        return prompt
    
    def suggest_new_facets(self, keywords_str, existing_facets, company_name, model="gpt-4"):
        """
        Use OpenAI to suggest entirely new facets based on product keywords.
        """
        prompt = self._build_new_facets_with_values_prompt(keywords_str, existing_facets, company_name)
        try:
            response = openai.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )
            output = response.choices[0].message.content.strip()
            return output
        except Exception as e:
            print(f"OpenAI API error (suggest_new_facets): {e}")
            return None
    
    def _build_new_facets_with_values_prompt(self, keywords_str, existing_facets, company_name):
        """
        Build the prompt for suggesting entirely new facets along with their allowed values.
        """
        existing_list = "\n".join(f"{facet}: {', '.join(values)}" for facet, values in existing_facets.items())
        if company_name == "Unknown Company":
            company_name = "an unknown company"
        prompt = (
            f"The goal is to suggest entirely new facets to categorize the product catalog of {company_name}. "
            "For each new facet you recommend, provide a name and a list of allowed values. "
            "Here is an example of an existing facet and its allowed values:\n"
            "Color: Red, Blue, Green\n\n"
            "Here are the existing facets and their allowed values:\n"
            f"{existing_list}\n\n"
            "Based on the following keywords that appear in product descriptions most often, suggest up to 10 new facets, with up to 5 allowed values each, "
            "that are clearly applicable and distinct from the existing facets. For each facet, provide a name and a list of allowed values. "
            "Only suggest new facets that are clearly applicable and distinct from the existing facets. "
            "Respond in the format 'Facet Name: Value1, Value2, etc' on seperated lines without numbering. "
            "If no new facets make sense, respond with 'None'.\n\n"
            "If less than 10 new facets or less than 5 values per facet make sense, respond with only those that do. "
            f"Keywords: {keywords_str}"
        )
        return prompt