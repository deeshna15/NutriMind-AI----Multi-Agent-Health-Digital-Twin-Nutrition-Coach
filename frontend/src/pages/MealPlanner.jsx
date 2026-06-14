import { useState, useEffect } from 'react';
import { Calendar as CalendarIcon, Clock, Flame, ChevronRight, Edit2 } from 'lucide-react';
import axios from 'axios';

export default function MealPlanner() {
  const [mealPlan, setMealPlan] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // In a real app we would call the /api/tools/meal-generation directly 
    // or trigger a specific workflow. We'll use workflow with an empty request
    // that defaults to generating a plan.
    const fetchPlan = async () => {
      try {
        const response = await axios.post('http://127.0.0.1:8000/api/workflow/meals', {
          user_id: 1,
          input_text: "plan my meals"
        });
        setMealPlan(response.data.meal_plan);
      } catch (error) {
        console.error("Error fetching meal plan", error);
      } finally {
        setLoading(false);
      }
    };
    fetchPlan();
  }, []);

  if (loading) {
    return (
      <div className="flex-1 h-screen flex flex-col items-center justify-center text-slate-400">
        <Flame className="animate-pulse mb-4 text-amber-500" size={48} />
        <p className="font-semibold text-lg animate-pulse">Generating your personalized plan...</p>
      </div>
    );
  }

  const mealTypes = [
    { type: 'breakfast', icon: '☀️', color: 'from-amber-100 to-orange-50', text: 'text-amber-800' },
    { type: 'lunch', icon: '🌤️', color: 'from-blue-50 to-cyan-50', text: 'text-blue-800' },
    { type: 'snacks', icon: '🍎', color: 'from-emerald-50 to-teal-50', text: 'text-emerald-800' },
    { type: 'dinner', icon: '🌙', color: 'from-indigo-50 to-purple-50', text: 'text-indigo-800' },
  ];

  return (
    <div className="p-4 sm:p-8 max-w-5xl mx-auto animate-in fade-in duration-500 pb-32 sm:pb-8">
      <header className="mb-8 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-800 flex items-center gap-3">
            <CalendarIcon className="text-emerald-500" /> Today's Plan
          </h1>
          <p className="text-slate-500 mt-2">Dynamically generated based on your health profile.</p>
        </div>
        <button className="flex items-center gap-2 bg-white border border-slate-200 text-slate-700 px-4 py-2 rounded-xl font-semibold hover:bg-slate-50 transition-colors shadow-sm text-sm">
          <Edit2 size={16} /> Customize Plan
        </button>
      </header>

      {mealPlan?.replanning_note && (
        <div className="bg-amber-50 border border-amber-200 p-4 rounded-xl mb-6 text-amber-800 flex items-start gap-3 shadow-sm">
          <Flame className="shrink-0 mt-0.5 text-amber-500" size={20} />
          <p className="font-semibold text-sm leading-relaxed">{mealPlan.replanning_note}</p>
        </div>
      )}

      {mealPlan && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {mealTypes.map(({ type, icon, color, text }) => (
            <div key={type} className={`bg-gradient-to-br ${color} p-6 rounded-3xl border border-white shadow-sm hover:shadow-md transition-shadow group relative overflow-hidden`}>
              <div className="absolute -right-6 -top-6 text-6xl opacity-10 group-hover:scale-110 transition-transform">{icon}</div>
              
              <div className="flex justify-between items-start mb-4 relative z-10">
                <h3 className={`text-xl font-bold capitalize ${text} flex items-center gap-2`}>
                  <span className="text-2xl bg-white/50 w-10 h-10 rounded-full flex items-center justify-center shadow-sm backdrop-blur-sm">{icon}</span> {type}
                </h3>
              </div>
              
              <div className="bg-white/60 backdrop-blur-md rounded-2xl p-4 shadow-sm border border-white/50 relative z-10">
                <p className="font-semibold text-slate-800">
                  {Array.isArray(mealPlan[type]) ? mealPlan[type].join(", ") : mealPlan[type]}
                </p>
                <div className="mt-3 flex items-center gap-4 text-xs font-bold text-slate-500 uppercase tracking-wider">
                  <span className="flex items-center gap-1"><Clock size={14} /> {type === 'breakfast' ? '8:00 AM' : type === 'lunch' ? '1:00 PM' : type === 'snacks' ? '4:00 PM' : '7:30 PM'}</span>
                  <span className="flex items-center gap-1"><Flame size={14} className="text-amber-500" /> ~450 kcal</span>
                </div>
              </div>
              
              <button className={`mt-4 w-full py-3 rounded-xl bg-white/50 hover:bg-white/80 font-bold text-sm flex justify-between items-center px-4 transition-colors ${text} shadow-sm backdrop-blur-sm`}>
                <span>View Recipe</span>
                <ChevronRight size={18} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
