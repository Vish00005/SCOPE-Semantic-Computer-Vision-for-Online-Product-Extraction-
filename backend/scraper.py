import requests
from bs4 import BeautifulSoup
import urllib.parse
from typing import List
from models import SearchResult

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

def search_amazon(query: str) -> List[SearchResult]:
    url = f"https://www.amazon.in/s?k={urllib.parse.quote_plus(query)}"
    results = []
    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        items = soup.find_all('div', {'data-component-type': 's-search-result'})
        
        count = 0
        for item in items:
            if count >= 5:
                break
                
            # Skip sponsored products
            if item.find(class_='puis-sponsored-label-text') or item.find(class_='s-sponsored-label-text'):
                continue
                
            title_elem = item.find('h2')
            if not title_elem:
                continue
            title = title_elem.text.strip()
            
            # Find the main product link in the item block
            link_elem = item.find('a', class_='a-link-normal s-no-outline') or item.find('a', class_='a-link-normal')
            link = url
            if link_elem and 'href' in link_elem.attrs:
                href = link_elem['href']
                link = href if href.startswith('http') else f"https://www.amazon.in{href}"
            
            price_elem = item.find('span', {'class': 'a-price-whole'})
            price = price_elem.text.strip() if price_elem else "N/A"
            
            rating_elem = item.find('span', {'class': 'a-icon-alt'})
            rating = rating_elem.text.strip() if rating_elem else "N/A"
            
            img_elem = item.find('img', {'class': 's-image'})
            img_url = img_elem['src'] if img_elem else ""
            
            results.append(SearchResult(
                title=title, price=price, rating=rating,
                image_url=img_url, product_link=link, store="Amazon"
            ))
            count += 1
    except Exception as e:
        print(f"Amazon scraping failed: {e}")
        # Graceful fallback: return a single item directing to the search page
        results.append(SearchResult(
            title=f"Search for {query} on Amazon",
            price="N/A", rating="N/A", image_url="",
            product_link=url, store="Amazon"
        ))
    return results

def search_flipkart(query: str) -> List[SearchResult]:
    url = f"https://www.flipkart.com/search?q={urllib.parse.quote_plus(query)}"
    results = []
    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # User provided class name
        items = soup.find_all('div', {'class': 'RGLWAk'})
        if not items:
            items = soup.find_all('div', {'class': 'slAVV4'}) or soup.find_all('div', {'class': '_1AtVbE'})
            
        for item in items[:5]:
            link_elem = item.find('a')
            if not link_elem or 'href' not in link_elem.attrs:
                continue
                
            href = link_elem['href']
            link = href if href.startswith('http') else f"https://www.flipkart.com{href}"
            
            img_elem = item.find('img')
            title = img_elem['alt'] if img_elem and 'alt' in img_elem.attrs else link_elem.text.strip()
            if not title or len(title) < 3:
                 title = "Flipkart Product"
                 
            img_url = img_elem['src'] if img_elem else ""
            
            # Find price by looking for the rupee symbol
            price_elem = item.find(string=lambda text: text and '₹' in text)
            price = price_elem.strip() if price_elem else "N/A"
            
            # Find rating by looking for the star symbol
            rating_elem = item.find(string=lambda text: text and '★' in text)
            rating = rating_elem.strip() if rating_elem else "N/A"
            
            results.append(SearchResult(
                title=title, price=price, rating=rating,
                image_url=img_url, product_link=link, store="Flipkart"
            ))
    except Exception as e:
        print(f"Flipkart scraping failed: {e}")
        results.append(SearchResult(
            title=f"Search for {query} on Flipkart",
            price="N/A", rating="N/A", image_url="",
            product_link=url, store="Flipkart"
        ))
    return results
