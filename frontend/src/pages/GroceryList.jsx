import { useState, useEffect } from 'react';
import { ShoppingBag, Check, CheckCircle2, Circle } from 'lucide-react';
import axios from 'axios';

export default function GroceryList() {
  const [groceryList, setGroceryList] = useState([]);
  const [checkedItems, setCheckedItems] = useState(new Set());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchList = async () => {
      try {
        const response = await axios.post('http://127.0.0.1:8000/api/workflow/grocery', {
          user_id: 1,
          input_text: "grocery list"
        });
        setGroceryList(response.data.grocery_list);
      } catch (error) {
        console.error("Error fetching grocery list", error);
      } finally {
        setLoading(false);
      }
    };
    fetchList();
  }, []);

  const toggleItem = (categoryIndex, itemIndex) => {
    const newChecked = new Set(checkedItems);
    const id = `${categoryIndex}-${itemIndex}`;
    if (newChecked.has(id)) {
      newChecked.delete(id);
    } else {
      newChecked.add(id);
    }
    setCheckedItems(newChecked);
  };

  if (loading) {
     return <div className="p-8 text-center text-slate-500">Loading your grocery list...</div>;
  }

  const progress = groceryList.length > 0 
    ? Math.round((checkedItems.size / groceryList.reduce((acc, cat) => acc + cat.items.length, 0)) * 100) 
    : 0;

  return (
    <div className="p-4 sm:p-8 max-w-4xl mx-auto pb-32 sm:pb-8 animate-in slide-in-from-right-4 duration-500">
      <header className="mb-8 bg-emerald-600 text-white p-6 sm:p-8 rounded-3xl shadow-lg shadow-emerald-600/20 relative overflow-hidden">
        <div className="absolute top-0 right-0 p-8 opacity-10">
          <ShoppingBag size={120} />
        </div>
        <div className="relative z-10">
          <h1 className="text-3xl font-black mb-2">Smart Grocery List</h1>
          <p className="text-emerald-100 font-medium mb-6">Auto-generated based on your meal plan.</p>
          
          <div className="bg-emerald-900/20 rounded-2xl p-4 backdrop-blur-sm">
            <div className="flex justify-between text-sm font-bold mb-2 text-emerald-50">
              <span>Shopping Progress</span>
              <span>{progress}%</span>
            </div>
            <div className="w-full bg-emerald-900/40 h-2.5 rounded-full overflow-hidden">
              <div 
                className="bg-white h-full rounded-full transition-all duration-500 ease-out" 
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>
        </div>
      </header>

      <div className="space-y-6">
        {groceryList.map((category, cIdx) => (
          <div key={cIdx} className="bg-white rounded-3xl p-6 shadow-sm border border-slate-100">
            <h3 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2 border-b border-slate-100 pb-3">
              {category.category}
              <span className="bg-slate-100 text-slate-500 text-xs py-1 px-2 rounded-full ml-auto">{category.items.length} items</span>
            </h3>
            <ul className="space-y-1">
              {category.items.map((item, iIdx) => {
                const id = `${cIdx}-${iIdx}`;
                const isChecked = checkedItems.has(id);
                return (
                  <li key={iIdx}>
                    <button 
                      onClick={() => toggleItem(cIdx, iIdx)}
                      className={`w-full flex items-center gap-4 p-3 rounded-xl transition-all ${
                        isChecked ? 'bg-slate-50 text-slate-400' : 'hover:bg-slate-50 text-slate-700'
                      }`}
                    >
                      {isChecked ? (
                        <CheckCircle2 size={24} className="text-emerald-500 flex-shrink-0" />
                      ) : (
                        <Circle size={24} className="text-slate-300 flex-shrink-0 group-hover:text-emerald-500" />
                      )}
                      <span className={`font-medium text-left ${isChecked ? 'line-through text-slate-400' : ''}`}>
                        {item}
                      </span>
                    </button>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}
