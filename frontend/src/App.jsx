import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Home, Camera, MessageSquare, Utensils, ShoppingCart, ChefHat } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import Scanner from './pages/Scanner';
import Chat from './pages/Chat';
import MealPlanner from './pages/MealPlanner';
import GroceryList from './pages/GroceryList';
import Pantry from './pages/Pantry';

function Navigation() {
  const location = useLocation();
  const navItems = [
    { path: '/', icon: Home, label: 'Dashboard' },
    { path: '/scanner', icon: Camera, label: 'Scanner' },
    { path: '/pantry', icon: ChefHat, label: 'Pantry' },
    { path: '/chat', icon: MessageSquare, label: 'AI Chat' },
    { path: '/meals', icon: Utensils, label: 'Meals' },
    { path: '/grocery', icon: ShoppingCart, label: 'Grocery' },
  ];

  return (
    <nav className="fixed bottom-0 w-full bg-white border-t border-gray-200 pb-safe sm:relative sm:w-64 sm:h-screen sm:border-r sm:border-t-0 flex-shrink-0 z-50">
      <div className="flex sm:flex-col h-16 sm:h-full justify-around sm:justify-start sm:p-4">
        <div className="hidden sm:flex items-center gap-2 mb-8 p-2">
          <div className="w-8 h-8 rounded-full bg-emerald-500 flex items-center justify-center text-white font-bold">N</div>
          <span className="text-xl font-bold bg-gradient-to-r from-emerald-500 to-teal-600 bg-clip-text text-transparent">NutriMind</span>
        </div>
        {navItems.map(({ path, icon: Icon, label }) => {
          const isActive = location.pathname === path;
          return (
            <Link
              key={path}
              to={path}
              className={`flex flex-col sm:flex-row items-center sm:gap-3 p-2 sm:p-3 sm:mb-2 rounded-xl transition-all ${
                isActive 
                  ? 'text-emerald-600 bg-emerald-50 sm:bg-emerald-50/50' 
                  : 'text-gray-500 hover:text-emerald-600 hover:bg-gray-50'
              }`}
            >
              <Icon size={24} className={isActive ? "scale-110 transition-transform" : ""} />
              <span className="text-[10px] sm:text-base font-medium mt-1 sm:mt-0">{label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}

export default function App() {
  return (
    <Router>
      <div className="flex flex-col min-h-screen bg-slate-50">
        {/* Global Meal Logging Reminder Banner */}
        <div className="bg-gradient-to-r from-amber-500 to-orange-600 text-white px-4 py-2.5 text-center text-xs sm:text-sm font-bold shadow-sm flex items-center justify-center gap-2 z-50 animate-pulse">
          <span>📸 Track Daily Nutrition: Snap a photo of your food whenever you consume to balance your diet!</span>
        </div>
        <div className="flex flex-col sm:flex-row flex-1">
          <Navigation />
          <main className="flex-1 pb-20 sm:pb-0 overflow-y-auto">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/scanner" element={<Scanner />} />
              <Route path="/pantry" element={<Pantry />} />
              <Route path="/chat" element={<Chat />} />
              <Route path="/meals" element={<MealPlanner />} />
              <Route path="/grocery" element={<GroceryList />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}
