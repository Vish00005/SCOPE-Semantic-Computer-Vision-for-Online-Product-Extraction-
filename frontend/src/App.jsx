import React, { useState, useRef } from 'react';

function App() {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [product, setProduct] = useState(null);
  const [searchResults, setSearchResults] = useState(null);
  const [searching, setSearching] = useState(false);
  const videoRef = useRef(null);
  const [useCamera, setUseCamera] = useState(false);
  
  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImage(file);
      setPreview(URL.createObjectURL(file));
      setUseCamera(false);
    }
  };

  const startCamera = async () => {
    setUseCamera(true);
    setImage(null);
    setPreview(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (err) {
      console.error("Error accessing camera:", err);
      alert("Could not access camera.");
    }
  };

  const captureCamera = () => {
    if (!videoRef.current) return;
    const canvas = document.createElement("canvas");
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
    
    canvas.toBlob((blob) => {
      const file = new File([blob], "camera_capture.jpg", { type: "image/jpeg" });
      setImage(file);
      setPreview(URL.createObjectURL(file));
      setUseCamera(false);
      // stop stream
      const stream = videoRef.current.srcObject;
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    }, 'image/jpeg');
  };

  const analyzeImage = async () => {
    if (!image) return;
    setAnalyzing(true);
    setProduct(null);
    setSearchResults(null);
    
    const formData = new FormData();
    formData.append('file', image);
    
    try {
      // Connect to backend running on port 8000
      const res = await fetch('http://localhost:8000/api/analyze', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      setProduct(data);
      // Automatically proceed to search
      await searchProductsData(data);
    } catch (err) {
      console.error("Error analyzing image:", err);
      alert("Error analyzing image.");
      setAnalyzing(false);
    }
  };

  const searchProductsData = async (productData) => {
    setAnalyzing(false);
    setSearching(true);
    
    try {
      const res = await fetch('http://localhost:8000/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(productData),
      });
      const data = await res.json();
      setSearchResults(data);
    } catch (err) {
      console.error("Error searching products:", err);
      alert("Error searching products.");
    } finally {
      setSearching(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <header className="max-w-4xl mx-auto mb-8 text-center">
        <h1 className="text-4xl font-bold text-blue-600 mb-2">Product Analyzer</h1>
        <p className="text-gray-600">Scan product packaging to find deals online!</p>
      </header>

      <main className="max-w-4xl mx-auto bg-white rounded-xl shadow-md p-6">
        {/* INPUT SECTION */}
        {!product && !analyzing && (
          <div className="flex flex-col items-center gap-6">
            <div className="flex gap-4">
              <label className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg cursor-pointer transition">
                Upload Image
                <input type="file" accept="image/*" className="hidden" onChange={handleFileUpload} />
              </label>
              <button 
                onClick={startCamera}
                className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg transition">
                Use Camera
              </button>
            </div>

            {useCamera && (
              <div className="flex flex-col items-center">
                <video ref={videoRef} autoPlay playsInline className="max-w-full rounded-lg mb-4 bg-black"></video>
                <button onClick={captureCamera} className="bg-red-500 text-white px-6 py-2 rounded-lg">Capture</button>
              </div>
            )}

            {preview && !useCamera && (
              <div className="flex flex-col items-center">
                <img src={preview} alt="Preview" className="max-w-sm rounded-lg mb-4 shadow-sm" />
                <button onClick={analyzeImage} className="bg-indigo-600 hover:bg-indigo-700 text-white px-8 py-3 rounded-lg font-semibold w-full text-lg shadow-md transition">
                  Analyze Product
                </button>
              </div>
            )}
          </div>
        )}

        {/* LOADING STATE */}
        {analyzing && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
            <p className="text-xl text-gray-600">Extracting product details with NLP...</p>
          </div>
        )}



        {/* SEARCH LOADING */}
        {searching && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-green-500 mx-auto mb-4"></div>
            <p className="text-xl text-gray-600">Scraping Amazon & Flipkart...</p>
          </div>
        )}

        {/* RESULTS PAGE */}
        {searchResults && (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold">Results</h2>
              <button onClick={() => { setProduct(null); setSearchResults(null); setPreview(null); setImage(null); }} className="bg-gray-200 hover:bg-gray-300 px-4 py-2 rounded-lg">Start Over</button>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-5 mb-8 text-sm">
              <h3 className="font-bold text-blue-800 mb-2">Scan Analysis</h3>
              <p className="mb-3"><span className="font-semibold text-blue-900">Raw OCR Text: </span><span className="text-gray-700 font-mono text-xs bg-white px-2 py-1 rounded border inline-block mt-1 w-full overflow-hidden break-words">{product?.raw_text || "No text detected."}</span></p>
              <div className="grid grid-cols-2 gap-2 text-blue-900 mb-3">
                <p><span className="font-semibold">Brand:</span> {product?.brand || "N/A"}</p>
                <p><span className="font-semibold">Product:</span> {product?.product_name || "N/A"}</p>
                <p><span className="font-semibold">Quantity:</span> {product?.quantity || "N/A"}</p>
                <p><span className="font-semibold">Price:</span> {product?.price || "N/A"}</p>
              </div>
              {searchResults?.search_urls && (
                <div className="mt-3 pt-3 border-t border-blue-200">
                  <p className="font-semibold text-blue-900 mb-1">Generated Search Links:</p>
                  <ul className="list-disc pl-5">
                    <li><a href={searchResults.search_urls.amazon} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline">Amazon Search</a></li>
                    <li><a href={searchResults.search_urls.flipkart} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline">Flipkart Search</a></li>
                  </ul>
                </div>
              )}
            </div>

            <div className="mb-8">
              <h3 className="text-xl font-bold text-gray-800 border-b pb-2 mb-4">Best Matches</h3>
              <div className="grid grid-cols-1 gap-4">
                {searchResults.results.map((item, idx) => (
                  <a key={idx} href={item.product_link} target="_blank" rel="noreferrer" className="flex flex-col sm:flex-row bg-white border rounded-lg shadow-sm hover:shadow-md transition p-4 gap-4 items-center">
                    {item.image_url && <img src={item.image_url} alt={item.title} className="w-32 h-32 object-contain" />}
                    <div className="flex-1">
                      <h4 className="font-semibold text-lg text-blue-600 line-clamp-2">{item.title}</h4>
                      <p className="text-2xl font-bold text-gray-800 mt-2">{item.price}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded">{item.rating}</span>
                        <span className="text-sm text-gray-500">{item.store}</span>
                      </div>
                    </div>
                  </a>
                ))}
                {searchResults.results.length === 0 && <p className="text-gray-500 italic">No exact matches found.</p>}
              </div>
            </div>

            <div>
              <h3 className="text-xl font-bold text-gray-800 border-b pb-2 mb-4">Similar Products</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
                {searchResults.similar_products.map((item, idx) => (
                  <a key={idx} href={item.product_link} target="_blank" rel="noreferrer" className="bg-white border rounded-lg shadow-sm hover:shadow-md transition p-4 flex flex-col h-full">
                    {item.image_url && <img src={item.image_url} alt={item.title} className="w-full h-40 object-contain mb-4" />}
                    <h4 className="font-semibold text-sm text-gray-800 line-clamp-3 mb-2 flex-1">{item.title}</h4>
                    <div className="mt-auto">
                      <p className="text-lg font-bold text-gray-800">{item.price}</p>
                      <p className="text-xs text-gray-500 mt-1">{item.store}</p>
                    </div>
                  </a>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
