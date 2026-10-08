from sentence_transformers import SentenceTransformer, util
from typing import List
from models import SearchResult

# Load the model once
model = SentenceTransformer('all-MiniLM-L6-v2')

def rank_and_recommend(query: str, results: List[SearchResult]) -> tuple[List[SearchResult], List[SearchResult]]:
    """Rank scraped results by similarity to the query and extract recommendations."""
    if not results:
        return [], []
        
    titles = [r.title for r in results]
    
    # Compute embeddings
    query_emb = model.encode(query, convert_to_tensor=True)
    title_embs = model.encode(titles, convert_to_tensor=True)
    
    # Compute cosine similarities
    cosine_scores = util.cos_sim(query_emb, title_embs)[0]
    
    # Sort results by descending similarity
    scored_results = sorted(zip(results, cosine_scores), key=lambda x: x[1], reverse=True)
    
    top_results = []
    similar_products = []
    seen_stores = set()
    
    for res, score in scored_results:
        # If we haven't seen this store yet, and it's a good match, it's the Best Match for this store
        if res.store not in seen_stores:
            top_results.append(res)
            seen_stores.add(res.store)
        else:
            similar_products.append(res)
            
    return top_results, similar_products
