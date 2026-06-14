import { useState } from 'react';
import { Upload, Camera, Loader2, CheckCircle2, ArrowRight, Activity, AlertTriangle } from 'lucide-react';
import axios from 'axios';

export default function Scanner() {
  const [image, setImage] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState(null);

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setImage(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const analyzeFood = async () => {
    if (!image) return;
    setIsAnalyzing(true);
    
    try {
      const base64Data = image.split(',')[1];
      const response = await axios.post('http://127.0.0.1:8000/api/workflow/analyze', {
        user_id: 1,
        input_image_base64: base64Data,
        context: { mood: "hungry", time_of_day: "lunch" }
      });
      
      setResult(response.data);
    } catch (error) {
      console.error("Analysis failed", error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="p-4 sm:p-8 max-w-4xl mx-auto min-h-screen animate-in slide-in-from-bottom-4 duration-500">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-slate-800">Smart Scanner</h1>
        <p className="text-slate-500 mt-2">Snap a photo of your food to instantly get nutritional info and a health score.</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Upload Area */}
        <div className="flex flex-col gap-4">
          <div className="relative group rounded-3xl overflow-hidden border-2 border-dashed border-slate-300 bg-white aspect-square flex flex-col items-center justify-center hover:border-emerald-500 hover:bg-emerald-50 transition-colors cursor-pointer">
            <input 
              type="file" 
              accept="image/*" 
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10" 
              onChange={handleImageUpload}
            />
            {image ? (
              <img src={image} alt="Food preview" className="absolute inset-0 w-full h-full object-cover z-0" />
            ) : (
              <div className="flex flex-col items-center p-6 text-center">
                <div className="w-20 h-20 rounded-full bg-slate-100 flex items-center justify-center mb-4 group-hover:bg-emerald-100 transition-colors">
                  <Camera size={40} className="text-slate-400 group-hover:text-emerald-600 transition-colors" />
                </div>
                <h3 className="text-lg font-semibold text-slate-700">Tap to upload</h3>
                <p className="text-sm text-slate-500 mt-2">or drag and drop your image here</p>
              </div>
            )}
            
            {image && (
              <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity z-0 flex items-center justify-center">
                <p className="text-white font-bold flex items-center gap-2"><Upload size={20} /> Change Image</p>
              </div>
            )}
          </div>
          
          <button 
            onClick={analyzeFood}
            disabled={!image || isAnalyzing}
            className={`py-4 rounded-2xl font-bold text-lg flex items-center justify-center gap-2 transition-all ${
              !image ? 'bg-slate-200 text-slate-400 cursor-not-allowed' :
              isAnalyzing ? 'bg-emerald-500 text-white cursor-wait' : 'bg-emerald-600 hover:bg-emerald-700 text-white shadow-lg hover:shadow-xl hover:-translate-y-1'
            }`}
          >
            {isAnalyzing ? (
              <><Loader2 className="animate-spin" /> Analyzing Nutrients...</>
            ) : (
              <>Analyze Food <ArrowRight /></>
            )}
          </button>
        </div>

        {/* Results Area */}
        <div className="flex flex-col gap-6">
          {result ? (
            <div className="space-y-6 animate-in fade-in zoom-in duration-500">
              
              {/* Warnings Banner */}
              {result.is_exceeded && (
                <div className="bg-rose-50 border border-rose-200 p-4 rounded-2xl text-rose-800 text-xs sm:text-sm font-bold flex items-start gap-3">
                  <AlertTriangle className="text-rose-500 flex-shrink-0" size={20} />
                  <div>
                    <span className="block font-black text-rose-900 uppercase">Threshold Limit Exceeded!</span>
                    <ul className="list-disc pl-4 mt-1 space-y-1">
                      {result.warnings.map((w, idx) => (
                        <li key={idx}>{w}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}

              <div className="bg-white rounded-3xl p-6 shadow-sm border border-slate-100">
                <div className="flex justify-between items-start mb-6">
                  <div>
                    <h3 className="text-xl font-bold text-slate-800 capitalize">{result.food_items.join(", ")}</h3>
                    {result.portion_estimation && (
                      <p className="text-sm text-slate-600 font-medium mt-1">Portion: {result.portion_estimation}</p>
                    )}
                    <p className="text-sm text-slate-500 font-medium flex items-center gap-2 mt-1">
                      Detected Items
                      {result.nutrition.is_estimated && (
                        <span className="bg-amber-100 text-amber-700 text-[10px] uppercase font-bold px-2 py-0.5 rounded-full border border-amber-200">
                          Estimated
                        </span>
                      )}
                    </p>
                  </div>
                  <div className={`w-16 h-16 rounded-2xl flex flex-col items-center justify-center text-white font-bold shadow-lg ${result.health_score > 70 ? 'bg-emerald-500 shadow-emerald-500/30' : result.health_score > 40 ? 'bg-amber-500 shadow-amber-500/30' : 'bg-red-500 shadow-red-500/30'}`}>
                    <span className="text-2xl leading-none">{result.health_score}</span>
                  </div>
                </div>

                <div className="bg-slate-50 rounded-2xl p-4 mb-6">
                  <p className="text-slate-700 text-sm font-medium leading-relaxed">{result.health_explanation}</p>
                </div>

                {/* Macro Grid */}
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-6">
                  {Object.entries(result.nutrition)
                    .filter(([key]) => key !== 'is_estimated')
                    .map(([key, value]) => (
                      <div key={key} className="bg-white border border-slate-200 rounded-xl p-3 flex flex-col items-center justify-center">
                        <span className="text-xs text-slate-500 font-bold uppercase tracking-wider mb-1">{key}</span>
                        <span className="text-lg font-black text-slate-800">{value}{key === 'calories' ? ' kcal' : key === 'sodium' ? 'mg' : 'g'}</span>
                      </div>
                    ))}
                </div>
              </div>

              {result.recommendations && result.recommendations.length > 0 && (
                <div className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-3xl p-6 border border-amber-100">
                  <h3 className="text-lg font-bold text-amber-800 mb-3 flex items-center gap-2">
                    <CheckCircle2 size={20} className="text-amber-500" /> Smart Swaps
                  </h3>
                  <ul className="space-y-3">
                    {result.recommendations.map((rec, i) => (
                      <li key={i} className="flex gap-3 text-amber-900 text-sm font-medium">
                        <span className="mt-0.5 text-amber-500">•</span> {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {result.disease_risk_analysis && result.disease_risk_analysis.length > 0 && (
                <div className="bg-gradient-to-br from-rose-50 to-red-50 rounded-3xl p-6 border border-red-100 mt-6">
                  <h3 className="text-lg font-bold text-rose-800 mb-3 flex items-center gap-2">
                    <Activity size={20} className="text-rose-500" /> Disease Risk Analysis
                  </h3>
                  <ul className="space-y-3">
                    {result.disease_risk_analysis.map((risk, i) => (
                      <li key={i} className="flex gap-3 text-rose-900 text-sm font-medium">
                        <span className="mt-0.5 text-rose-500">⚠</span> {risk}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="h-full border-2 border-dashed border-slate-200 rounded-3xl flex flex-col items-center justify-center text-slate-400 p-8 text-center bg-slate-50/50">
              <Activity size={48} className="mb-4 opacity-50" />
              <p className="text-lg font-semibold text-slate-600">No data yet</p>
              <p className="text-sm mt-2 max-w-[250px]">Upload an image and tap analyze to see the nutritional breakdown and health score.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
