import { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import axios from 'axios';
import { Activity, Flame, Droplets, Target, TrendingUp, Award, AlertTriangle, CheckCircle, Calendar, Plus, ChefHat, Info } from 'lucide-react';

const COLORS = ['#10b981', '#f1f5f9']; // Emerald and Slate
const MACRO_COLORS = {
  Protein: '#3b82f6', // Blue
  Carbs: '#f59e0b', // Amber
  Fat: '#ef4444', // Red
  Sugar: '#ec4899' // Pink
};

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);

  const fetchDashboard = async (dateStr) => {
    setLoading(true);
    try {
      const response = await axios.get('http://127.0.0.1:8000/api/workflow/dashboard', {
        params: { date_str: dateStr }
      });
      setData(response.data);
    } catch (error) {
      console.error("Error fetching dashboard data", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard(selectedDate);
  }, [selectedDate]);

  if (loading && !data) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen text-slate-500 bg-slate-50">
        <Activity className="animate-spin text-emerald-500 mb-4" size={48} />
        <p className="font-semibold text-lg">Loading your personalized dashboard...</p>
      </div>
    );
  }

  const {
    healthScore,
    streak,
    macroData,
    weeklyTrends,
    calories,
    sugar = 0,
    sodium = 0,
    insight,
    weightForecast,
    healthScoreForecast,
    riskLevel = "LOW",
    warnings = [],
    mealsToday = []
  } = data || {};

  const scoreData = [
    { name: 'Score', value: healthScore || 85 },
    { name: 'Remaining', value: 100 - (healthScore || 85) }
  ];

  // Dynamic pantry suggestions based on today's dietary status
  const getBalancingPantrySuggestions = () => {
    if (riskLevel === "HIGH") {
      return [
        {
          name: "Detox Spin-Tofu Bowl",
          description: "Made from Spinach, Tofu, and Lemon in your pantry. Extremely low in calories (180 kcal) and sodium (80mg), but high in plant-based proteins (+15g) to offset the day's high calorie/sodium intakes.",
          time: "10 mins"
        },
        {
          name: "Garlic Herb Grilled Chicken & Asparagus",
          description: "Made from Chicken breast, Garlic, and Asparagus in your pantry. Zero-carb, low-sodium dish that focuses on muscle repair and helps restore daily target values.",
          time: "15 mins"
        }
      ];
    } else if (riskLevel === "MEDIUM") {
      return [
        {
          name: "Lentil Soup with Mixed Veggies",
          description: "Made from Lentils, Tomatoes, and Onions. Heart-healthy and rich in fiber (+12g) to stabilize glycemic index and control cholesterol.",
          time: "20 mins"
        }
      ];
    } else {
      return [
        {
          name: "Berry Oatmeal Bowl",
          description: "Made from Oats, Walnuts, and Honey in your pantry. Sustained energy release with omega-3 fatty acids for optimal breakfast performance.",
          time: "5 mins"
        }
      ];
    }
  };

  const pantrySuggestions = getBalancingPantrySuggestions();

  return (
    <div className="p-4 sm:p-8 max-w-6xl mx-auto space-y-8 animate-in fade-in duration-500">
      
      {/* Upper Header Row */}
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white p-6 rounded-3xl shadow-sm border border-slate-100">
        <div>
          <h1 className="text-3xl font-black text-slate-800">Hello, User! 👋</h1>
          <p className="text-slate-500 mt-1 font-medium">Tracking and optimizing your digital twin health metrics.</p>
        </div>
        
        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          {/* Calendar Picker */}
          <div className="flex items-center gap-2 bg-slate-100 px-4 py-2.5 rounded-full border border-slate-200 text-slate-700 font-bold w-full sm:w-auto">
            <Calendar size={18} className="text-slate-500" />
            <input 
              type="date" 
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="bg-transparent outline-none text-sm font-semibold cursor-pointer"
            />
          </div>
          
          <div className="flex items-center gap-2 bg-amber-100 text-amber-800 px-4 py-2.5 rounded-full font-black text-sm w-full sm:w-auto justify-center">
            <Flame size={18} className="text-amber-600 animate-bounce" />
            <span>{streak} Day Streak!</span>
          </div>
        </div>
      </header>

      {/* Health Risk Alert Banner */}
      <div className={`p-5 rounded-3xl border flex flex-col md:flex-row gap-4 items-start md:items-center justify-between shadow-sm transition-colors duration-300 ${
        riskLevel === "HIGH" ? "bg-rose-50 border-rose-200 text-rose-900" :
        riskLevel === "MEDIUM" ? "bg-amber-50 border-amber-200 text-amber-950" :
        "bg-emerald-50 border-emerald-200 text-emerald-950"
      }`}>
        <div className="flex items-start gap-4">
          <div className={`p-3 rounded-2xl flex-shrink-0 ${
            riskLevel === "HIGH" ? "bg-rose-500 text-white" :
            riskLevel === "MEDIUM" ? "bg-amber-500 text-white" :
            "bg-emerald-500 text-white"
          }`}>
            <AlertTriangle size={24} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-lg uppercase tracking-wider">Health Risk Level: {riskLevel}</span>
              {riskLevel === "LOW" && <span className="bg-emerald-200 text-emerald-800 text-xs px-2 py-0.5 rounded-full font-bold">Optimal</span>}
            </div>
            <p className="text-sm font-medium mt-1 leading-relaxed">
              {riskLevel === "HIGH" 
                ? "Multiple nutritional thresholds have been exceeded. Review warnings below and consume compensating pantry suggestions to balance your day."
                : riskLevel === "MEDIUM"
                ? "A threshold alert is active. Try incorporating fiber-rich vegetables and plenty of water."
                : "Your calorie and chemical nutrient intake are currently balanced within safe ranges."
              }
            </p>
          </div>
        </div>
        {warnings.length > 0 && (
          <div className="flex flex-col gap-1 w-full md:w-auto bg-white/60 p-3.5 rounded-2xl border border-black/5">
            <span className="text-xs font-bold uppercase tracking-wider opacity-70 mb-1">Active Warnings:</span>
            {warnings.map((w, i) => (
              <span key={i} className="text-xs font-bold flex items-center gap-1.5 text-slate-800">
                <span className="w-1.5 h-1.5 rounded-full bg-rose-500 flex-shrink-0"></span> {w}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Primary Dashboard Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Health Score Gauge */}
        <div className="bg-white rounded-3xl p-6 shadow-sm border border-slate-100 flex flex-col items-center justify-center relative overflow-hidden group">
          <div className="absolute top-0 left-0 w-full h-1.5 bg-gradient-to-r from-emerald-400 to-teal-500"></div>
          <h3 className="text-lg font-bold text-slate-700 mb-4 w-full flex items-center gap-2">
            <Activity className="text-emerald-500" /> Health Score
          </h3>
          <div className="h-44 w-full relative">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={scoreData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  startAngle={90}
                  endAngle={-270}
                  dataKey="value"
                  stroke="none"
                  cornerRadius={10}
                >
                  <Cell key="score" fill={riskLevel === "HIGH" ? '#f43f5e' : riskLevel === "MEDIUM" ? '#f59e0b' : '#10b981'} />
                  <Cell key="remaining" fill="#f1f5f9" />
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
              <span className="text-4xl font-black text-slate-800">{healthScore}</span>
              <span className="text-xs text-slate-500 font-bold uppercase">/ 100</span>
            </div>
          </div>
          <p className="text-center text-xs font-semibold text-slate-600 mt-2 bg-slate-50 p-3 rounded-xl w-full border border-slate-100">
            "{insight}"
          </p>
        </div>

        {/* Macros Bar Chart */}
        <div className="bg-white rounded-3xl p-6 shadow-sm border border-slate-100">
          <h3 className="text-lg font-bold text-slate-700 mb-4 flex items-center gap-2">
            <Target className="text-blue-500" /> Macros Tracker
          </h3>
          <div className="h-44 w-full">
            {macroData && macroData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={macroData} layout="vertical" margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
                  <XAxis type="number" hide />
                  <YAxis dataKey="name" type="category" width={60} axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12, fontWeight: 700}} />
                  <Tooltip cursor={{fill: '#f8fafc'}} contentStyle={{borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}} />
                  <Bar dataKey="value" radius={[0, 8, 8, 0]} barSize={18}>
                    {macroData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={MACRO_COLORS[entry.name] || '#10b981'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-400 font-semibold text-sm">No macro log data today.</div>
            )}
          </div>
        </div>

        {/* Dynamic Critical Targets Card */}
        <div className="flex flex-col gap-4">
          <div className="bg-white rounded-3xl p-5 shadow-sm border border-slate-100 flex-1">
             <h3 className="text-xs font-extrabold text-slate-400 uppercase tracking-wider mb-2">Calories consumed</h3>
             <div className="flex items-end gap-1">
               <span className="text-3xl font-black text-slate-800">{calories.toLocaleString()}</span>
               <span className="text-slate-500 font-bold mb-1">/ 2,000 kcal</span>
             </div>
             <div className="w-full bg-slate-100 h-2.5 rounded-full mt-3 overflow-hidden">
               <div 
                 className={`h-full rounded-full transition-all duration-300 ${calories > 2000 ? "bg-rose-500" : "bg-amber-500"}`} 
                 style={{ width: `${Math.min(100, (calories / 2000) * 100)}%` }}
               ></div>
             </div>
          </div>
          
          <div className="bg-white rounded-3xl p-5 shadow-sm border border-slate-100 flex-1">
             <h3 className="text-xs font-extrabold text-slate-400 uppercase tracking-wider mb-2">Sodium Intake</h3>
             <div className="flex items-end gap-1">
               <span className="text-3xl font-black text-slate-800">{sodium.toLocaleString()}</span>
               <span className="text-slate-500 font-bold mb-1">/ 2,000 mg</span>
             </div>
             <div className="w-full bg-slate-100 h-2.5 rounded-full mt-3 overflow-hidden">
               <div 
                 className={`h-full rounded-full transition-all duration-300 ${sodium > 1500 ? "bg-rose-500" : "bg-blue-500"}`} 
                 style={{ width: `${Math.min(100, (sodium / 2000) * 100)}%` }}
               ></div>
             </div>
          </div>
        </div>
      </div>

      {/* Logged Meals & Pantry Recommendations Block */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Today's Meals Logger Tracker */}
        <div className="bg-white rounded-3xl p-6 shadow-sm border border-slate-100 flex flex-col">
          <h3 className="text-xl font-bold text-slate-800 mb-4 flex items-center gap-2">
            <Plus className="text-emerald-500" /> Logged Food Intake
          </h3>
          <div className="flex-1 space-y-4 max-h-[350px] overflow-y-auto pr-2">
            {mealsToday.length > 0 ? (
              mealsToday.map((meal, index) => (
                <div key={index} className="p-4 bg-slate-50 rounded-2xl border border-slate-100 flex justify-between items-start gap-4 hover:border-slate-200 transition-colors">
                  <div className="space-y-1">
                    <h4 className="font-extrabold text-slate-800 text-md capitalize">{meal.food_items.join(", ")}</h4>
                    <p className="text-xs text-slate-400 font-bold">{meal.timestamp}</p>
                    <div className="flex flex-wrap gap-1.5 mt-2">
                      <span className="bg-blue-50 text-blue-700 text-[10px] font-bold px-2 py-0.5 rounded-full">P: {meal.protein}g</span>
                      <span className="bg-amber-50 text-amber-700 text-[10px] font-bold px-2 py-0.5 rounded-full">C: {meal.carbs}g</span>
                      <span className="bg-rose-50 text-rose-700 text-[10px] font-bold px-2 py-0.5 rounded-full">F: {meal.fat}g</span>
                      <span className="bg-purple-50 text-purple-700 text-[10px] font-bold px-2 py-0.5 rounded-full">Na: {meal.sodium}mg</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-lg font-black text-slate-800">{meal.calories} kcal</span>
                    {meal.warnings.length > 0 && (
                      <div className="mt-1">
                        <span className="bg-rose-100 text-rose-700 text-[10px] font-black px-2 py-0.5 rounded-full uppercase border border-rose-200 flex items-center gap-1 justify-end">
                          ⚠️ Warning
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              ))
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-slate-400 p-8 text-center bg-slate-50/50 rounded-2xl border-2 border-dashed border-slate-200">
                <Info size={32} className="mb-2 text-slate-300" />
                <p className="font-bold text-slate-500">No meals logged for this date</p>
                <p className="text-xs mt-1">Upload meal pictures on the Scanner page to keep tracking your food.</p>
              </div>
            )}
          </div>
        </div>

        {/* Suggested Balancing Meals from User's Pantry */}
        <div className="bg-white rounded-3xl p-6 shadow-sm border border-slate-100 flex flex-col">
          <h3 className="text-xl font-bold text-slate-800 mb-4 flex items-center gap-2">
            <ChefHat className="text-purple-500" /> Suggested Balancing Meals (From Pantry)
          </h3>
          <div className="flex-1 space-y-4">
            {pantrySuggestions.map((sug, i) => (
              <div key={i} className="p-4 bg-gradient-to-br from-indigo-50/50 to-purple-50/50 rounded-2xl border border-indigo-50 flex gap-4 hover:border-indigo-100 transition-colors">
                <div className="bg-indigo-100 text-indigo-700 w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0">
                  <ChefHat size={22} />
                </div>
                <div className="space-y-1">
                  <div className="flex justify-between items-center">
                    <h4 className="font-extrabold text-slate-800 text-md">{sug.name}</h4>
                    <span className="text-xs bg-indigo-100 text-indigo-800 font-bold px-2 py-0.5 rounded-full">{sug.time}</span>
                  </div>
                  <p className="text-slate-600 text-xs font-semibold leading-relaxed mt-1">{sug.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* Forecast Block */}
      <div className="bg-gradient-to-br from-indigo-900 to-slate-900 rounded-3xl p-8 text-white shadow-xl flex flex-col md:flex-row gap-8 items-center justify-between relative overflow-hidden">
        <div className="absolute right-0 bottom-0 top-0 w-1/3 opacity-10 bg-radial-gradient from-white to-transparent pointer-events-none"></div>
        <div className="space-y-2">
          <h3 className="text-2xl font-black flex items-center gap-2">
            <TrendingUp size={24} className="text-indigo-400" /> Digital Twin: 30-Day ML Projection
          </h3>
          <p className="text-indigo-100 text-sm max-w-lg leading-relaxed font-medium">
            Based on your cumulative daily diet and consistency, our machine learning regression forecasts the long-term trend of your physical weight and score profile.
          </p>
        </div>
        <div className="grid grid-cols-2 gap-4 w-full md:w-auto flex-shrink-0">
          <div className="bg-white/10 backdrop-blur-md p-5 rounded-2xl border border-white/10 text-center">
            <span className="text-xs text-indigo-200 font-bold uppercase tracking-wider block mb-1">Predicted Weight</span>
            <span className="text-3xl font-black">{weightForecast || 76.5} <span className="text-lg font-bold text-indigo-200">kg</span></span>
          </div>
          <div className="bg-white/10 backdrop-blur-md p-5 rounded-2xl border border-white/10 text-center">
            <span className="text-xs text-indigo-200 font-bold uppercase tracking-wider block mb-1">Predicted Health Score</span>
            <span className="text-3xl font-black">{healthScoreForecast || 89} <span className="text-lg font-bold text-indigo-200">/100</span></span>
          </div>
        </div>
      </div>

    </div>
  );
}
