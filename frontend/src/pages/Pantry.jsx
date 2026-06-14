import { useState, useRef } from 'react';
import { Camera as CameraIcon, Upload, Image as ImageIcon, Loader2, ChefHat, ShoppingBasket, Scale } from 'lucide-react';
import axios from 'axios';

export default function Pantry() {
  const [image, setImage] = useState(null);
  const [base64Data, setBase64Data] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const fileInputRef = useRef(null);

  const handleImageCapture = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      const imageUrl = URL.createObjectURL(file);
      setImage(imageUrl);
      
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64String = reader.result.split(',')[1];
        setBase64Data(base64String);
      };
      reader.readAsDataURL(file);
      setResult(null);
    }
  };

  const analyzePantry = async () => {
    if (!base64Data) return;
    
    setAnalyzing(true);
    try {
      const response = await axios.post('http://127.0.0.1:8000/api/workflow/pantry', {
        user_id: 1,
        input_image_base64: base64Data
      });
      setResult(response.data);
    } catch (error) {
      console.error("Error analyzing pantry:", error);
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="h-full flex flex-col p-4 sm:p-8 max-w-5xl mx-auto animate-in fade-in duration-500">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-slate-800 flex items-center gap-3">
          <ChefHat className="text-emerald-500" size={32} />
          Pantry Vision AI
        </h1>
        <p className="text-slate-500 mt-2">Upload a photo of your fridge or pantry, and the AI will identify ingredients and suggest custom meals designed to balance your daily nutrition.</p>
      </header>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-8 min-h-0">
        {/* Left Column: Image Upload */}
        <div className="flex flex-col bg-white rounded-3xl p-6 shadow-sm border border-slate-100">
          {!image ? (
            <div 
              onClick={() => fileInputRef.current?.click()}
              className="flex-1 border-2 border-dashed border-slate-300 rounded-2xl flex flex-col items-center justify-center cursor-pointer hover:border-emerald-500 hover:bg-emerald-50/50 transition-colors group"
            >
              <div className="bg-slate-100 p-4 rounded-full group-hover:bg-emerald-100 group-hover:text-emerald-600 transition-colors text-slate-400 mb-4">
                <ImageIcon size={32} />
              </div>
              <p className="font-semibold text-slate-700">Tap to upload a photo</p>
              <p className="text-sm text-slate-500 mt-1">Fridge, Pantry, or Grocery Haul</p>
            </div>
          ) : (
            <div className="flex flex-col h-full">
              <div className="relative flex-1 rounded-2xl overflow-hidden bg-slate-900 group min-h-[250px]">
                <img src={image} alt="Pantry" className="w-full h-full object-cover" />
                <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                  <button 
                    onClick={() => fileInputRef.current?.click()}
                    className="bg-white/20 backdrop-blur-md text-white px-4 py-2 rounded-full font-medium hover:bg-white/30 transition-colors flex items-center gap-2"
                  >
                    <Upload size={18} /> Retake
                  </button>
                </div>
              </div>
              
              <button 
                onClick={analyzePantry}
                disabled={analyzing}
                className="mt-6 w-full bg-emerald-500 text-white font-bold py-4 rounded-2xl hover:bg-emerald-600 disabled:opacity-50 transition-all shadow-md shadow-emerald-500/20 flex justify-center items-center gap-2"
              >
                {analyzing ? (
                  <><Loader2 className="animate-spin" size={20} /> Analyzing Pantry...</>
                ) : (
                  <><ChefHat size={20} /> Generate Balancing Meals</>
                )}
              </button>
            </div>
          )}
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleImageCapture} 
            accept="image/*" 
            className="hidden" 
          />
        </div>

        {/* Right Column: Results */}
        <div className="bg-white rounded-3xl p-6 shadow-sm border border-slate-100 overflow-y-auto">
          {result ? (
            <div className="space-y-8 animate-in slide-in-from-right-4 duration-500">
              
              {/* Detected Ingredients */}
              {result.detected_ingredients && result.detected_ingredients.length > 0 && (
                <div>
                  <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
                    <ShoppingBasket className="text-blue-500" /> Identified Pantry Items
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {result.detected_ingredients.map((item, i) => (
                      <span key={i} className="bg-blue-50 text-blue-700 px-3 py-1 rounded-full text-xs font-bold border border-blue-100">
                        {item}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Possible Meals */}
              {result.possible_meals && result.possible_meals.length > 0 && (
                <div>
                  <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
                    <ChefHat className="text-emerald-500" /> Suggested Balancing Recipes
                  </h3>
                  <div className="space-y-4">
                    {result.possible_meals.map((meal, i) => (
                      <div key={i} className="bg-slate-50 p-5 rounded-2xl border border-slate-100 space-y-2 relative group hover:border-slate-200 transition-colors">
                        <div className="flex justify-between items-start">
                          <h4 className="font-extrabold text-slate-800 text-md">{meal.name}</h4>
                          <span className="bg-emerald-100 text-emerald-800 text-[10px] font-black uppercase tracking-wider px-2 py-0.5 rounded-full flex items-center gap-1">
                            <Scale size={10} /> Balancing Choice
                          </span>
                        </div>
                        <p className="text-slate-600 text-xs font-semibold leading-relaxed whitespace-pre-wrap">{meal.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="h-full border-2 border-dashed border-slate-200 rounded-3xl flex flex-col items-center justify-center text-slate-400 p-8 text-center bg-slate-50/50">
              <ChefHat size={48} className="mb-4 text-slate-300 animate-pulse" />
              <p className="font-bold text-slate-500">No ingredients analyzed yet</p>
              <p className="text-xs mt-2 max-w-[250px]">Upload a photo of your fridge or pantry to generate custom recipes tailored to balance your daily nutrition.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
