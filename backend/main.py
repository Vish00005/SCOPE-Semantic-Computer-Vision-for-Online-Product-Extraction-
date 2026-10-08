from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from models import ExtractedProduct, SearchResponse
import io
import cv2
import numpy as np

app = FastAPI(title="Product Analyzer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok"}

@app.post("/api/analyze", response_model=ExtractedProduct)
async def analyze_image(file: UploadFile = File(...)):
    # Read image
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    from ocr import extract_text
    from extractor import extract_product_details

    # Run OCR + NLP pipeline
    ocr_result = extract_text(img)
    extracted = extract_product_details(ocr_result["raw_text"], ocr_result.get("largest_text", ""))
    
    return extracted

@app.post("/api/search", response_model=SearchResponse)
async def search_products(product: ExtractedProduct):
    from scraper import search_amazon, search_flipkart
    from recommender import rank_and_recommend
    
    query_parts = []
    if product.brand: query_parts.append(product.brand)
    if product.product_name: query_parts.append(product.product_name)
    if product.quantity: query_parts.append(product.quantity)
    
    query = " ".join(query_parts) if query_parts else "Product"
    
    all_results = search_amazon(query) + search_flipkart(query)
    top_results, similar = rank_and_recommend(query, all_results)
    import urllib.parse
    amazon_url = f"https://www.amazon.in/s?k={urllib.parse.quote_plus(query)}"
    flipkart_url = f"https://www.flipkart.com/search?q={urllib.parse.quote_plus(query)}"
    
    return SearchResponse(
        results=top_results,
        similar_products=similar,
        search_urls={"amazon": amazon_url, "flipkart": flipkart_url}
    )
