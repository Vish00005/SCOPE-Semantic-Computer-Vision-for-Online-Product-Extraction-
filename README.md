# Product Analyzer

A web application that uses Optical Character Recognition (OCR) and Natural Language Processing (NLP) to extract product details from images and find deals online. Built as an NLP course project.

## Features
- **Image Input**: Upload a product image or capture via webcam.
- **OCR Pipeline**: Preprocesses image and extracts text using EasyOCR.
- **NLP Extraction**: Extracts brand, product name, quantity, and price using spaCy (NER), rapidfuzz (Fuzzy matching), and Regex.
- **Web Scraping**: Searches Amazon and Flipkart for matches and extracts results using BeautifulSoup.
- **Recommendation Engine**: Ranks scraped results based on cosine similarity with `sentence-transformers` (`all-MiniLM-L6-v2`).

## Tech Stack
- **Backend**: FastAPI, EasyOCR, spaCy, Sentence Transformers, BeautifulSoup
- **Frontend**: React (Vite), Tailwind CSS

## Setup Instructions

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Download the spaCy English model:
   ```bash
   python -m spacy download en_core_web_sm
   ```
5. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

## NLP Techniques Used
- **EasyOCR**: Used for initial text extraction from images. Deep learning based OCR that performs well on complex backgrounds.
- **spaCy (NER)**: Named Entity Recognition is used as a fallback to identify ORG entities (Brands).
- **Fuzzy String Matching (rapidfuzz)**: Used to match OCR text against a list of known brands. OCR often makes slight spelling mistakes, which fuzzy matching handles elegantly.
- **Regular Expressions (Regex)**: Precise pattern matching for extracting standard formats like prices (₹/Rs) and quantities (kg/L/ml).
- **Sentence Embeddings (Sentence Transformers)**: Used to compute cosine similarity between the extracted product name and the scraped search results. This ensures that the most semantically similar products are ranked highest and recommended as similar items, overcoming differences in wording (e.g. "Maggi Noodles" vs "Maggi 2-Minute Instant Noodles").
