from pydantic import BaseModel
from typing import List, Optional

class ExtractedProduct(BaseModel):
    brand: Optional[str] = None
    product_name: Optional[str] = None
    quantity: Optional[str] = None
    price: Optional[str] = None
    category: Optional[str] = None
    raw_text: Optional[str] = None
    confidence_scores: dict = {}

class SearchResult(BaseModel):
    title: str
    price: str
    rating: str
    image_url: str
    product_link: str
    store: str

class SearchResponse(BaseModel):
    results: List[SearchResult]
    similar_products: List[SearchResult]
    search_urls: dict = {}
