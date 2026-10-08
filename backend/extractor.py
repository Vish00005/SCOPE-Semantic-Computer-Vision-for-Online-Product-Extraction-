import re
import spacy
from rapidfuzz import process, fuzz
from models import ExtractedProduct

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

KNOWN_BRANDS = ["Maggi", "Amul", "Britannia", "Parle", "Nestle", "Haldiram's", "Lays", "Kurkure", "Dabur", "Himalaya", "Patanjali", "Tata", "ITC", "Unilever", "P&G", "Colgate", "Oreo", "Cadbury", "Dove"]
CATEGORIES = ["Food", "Beverage", "Personal Care", "Electronics", "Household"]

def  (text: str, largest_text: str = "") -> tuple[str, float]:
    """Extract brand using font size heuristic, fuzzy matching, and SpaCy NER."""
    # If the user's requested heuristic found a large piece of text, use it as the brand
    if largest_text and len(largest_text) > 1:
        # If it happens to be a known brand, high confidence, otherwise 0.9
        best_match = process.extractOne(largest_text, KNOWN_BRANDS, scorer=fuzz.partial_ratio)
        if best_match and best_match[1] > 80:
            return best_match[0], 0.99
        return largest_text.title(), 0.90

    # Try fuzzy matching first for best results with known brands
    best_match = process.extractOne(text, KNOWN_BRANDS, scorer=fuzz.partial_ratio)
    if best_match and best_match[1] > 80:
        return best_match[0], best_match[1] / 100.0
    
    # Fallback to SpaCy NER
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "ORG":
            return ent.text, 0.6
            
    return None, 0.0

def extract_quantity(text: str) -> tuple[str, float]:
    """Extract quantity using Regex."""
    pattern = r'\b(\d+(?:\.\d+)?\s*(?:kg|g|gm|ml|l|liter|litres|pack of \d+))\b'
    matches = re.findall(pattern, text, re.IGNORECASE)
    if matches:
        return matches[0], 0.9
    return None, 0.0

def extract_price(text: str) -> tuple[str, float]:
    """Extract price (MRP) using Regex."""
    pattern = r'(?:₹|Rs\.?|MRP)\s*(\d+(?:\.\d{1,2})?)'
    matches = re.findall(pattern, text, re.IGNORECASE)
    if matches:
        return matches[0], 0.9
    return None, 0.0

def extract_product_details(raw_text: str, largest_text: str = "") -> ExtractedProduct:
    """Parse raw OCR text into structured product fields."""
    clean_text = re.sub(r'\s+', ' ', raw_text).strip()
    
    brand, brand_conf = extract_brand(clean_text, largest_text)
    quantity, qty_conf = extract_quantity(clean_text)
    price, price_conf = extract_price(clean_text)
    
    # Heuristic for product name: the first few words excluding the brand
    # Real implementations might use more advanced keyword extraction
    product_name = None
    if clean_text:
        words = clean_text.split()
        if brand and brand in clean_text:
            # Try to grab words near the brand
            name_parts = [w for w in words[:5] if w.lower() not in brand.lower()]
            product_name = " ".join(name_parts)
        else:
            product_name = " ".join(words[:4])
            
    # Dummy category assignment for now
    category = "Food" if "g" in (quantity or "") or "kg" in (quantity or "") else "Household"
    
    return ExtractedProduct(
        brand=brand,
        product_name=product_name,
        quantity=quantity,
        price=price,
        category=category,
        raw_text=raw_text,
        confidence_scores={
            "brand": brand_conf,
            "quantity": qty_conf,
            "price": price_conf
        }
    )
