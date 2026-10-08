import cv2
import numpy as np
import easyocr

# Initialize EasyOCR reader once
reader = easyocr.Reader(['en'], gpu=False)

def preprocess_image(img: np.ndarray) -> np.ndarray:
    """Preprocess the image to improve OCR accuracy."""
    # Resize image if too small or too large
    h, w = img.shape[:2]
    # Simple resize if needed, otherwise skip
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Denoise
    denoised = cv2.fastNlMeansDenoising(gray, h=10, searchWindowSize=21, templateWindowSize=7)
    
    # Contrast enhancement (CLAHE)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(denoised)
    
    return enhanced

def extract_text(img: np.ndarray) -> dict:
    """Run EasyOCR on the image and return the concatenated text and the largest text."""
    processed = preprocess_image(img)
    results = reader.readtext(processed, detail=1)
    
    if not results:
        return {"raw_text": "", "largest_text": ""}
        
    raw_text = " ".join([res[1] for res in results])
    
    # Calculate height for each bbox and find the largest
    # bbox format: [[top-left], [top-right], [bottom-right], [bottom-left]]
    max_height = 0
    largest_text = ""
    for bbox, text, prob in results:
        # height is approximately bottom-left Y minus top-left Y
        height = abs(bbox[3][1] - bbox[0][1])
        if height > max_height:
            max_height = height
            largest_text = text
            
    return {"raw_text": raw_text, "largest_text": largest_text}
