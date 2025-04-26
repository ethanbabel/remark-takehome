import spacy
from bs4 import BeautifulSoup

def strip_html(text):
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text(separator=" ", strip=True)


# Load the spaCy model (English, optimized for Mac if you installed 'spacy[apple]')
nlp = spacy.load("en_core_web_sm")

def extract_keywords(text):
    """
    Extracts key tokens (nouns, proper nouns, adjectives) from the input text.
    
    Args:
        text (str): The product description.

    Returns:
        List[str]: List of extracted keywords.
    """
    # Remove HTML tags
    text = strip_html(text)

    doc = nlp(text)
    
    # We’ll select important parts of speech (nouns, proper nouns, adjectives)
    keywords = [
        token.text for token in doc 
        if token.pos_ in {"NOUN", "PROPN", "ADJ"} and not token.is_punct and not token.is_space and not token.is_stop and token.is_alpha
    ]

    # Remove duplicates 
    keywords = list(set(keywords))

    return keywords

if __name__ == "__main__":
    # Example usage
    product_description = "Experience the ultimate comfort with our premium Italian leather sofa, featuring modern design and adjustable headrests."
    
    keywords = extract_keywords(product_description)
    print("Extracted Keywords:", keywords)