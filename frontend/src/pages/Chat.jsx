import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2 } from 'lucide-react';
import axios from 'axios';

export default function Chat() {
  const [messages, setMessages] = useState([
    { role: 'ai', text: "Hi! I'm NutriMind. What did you eat today, or what are you planning to eat?" }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: userMessage }]);
    setIsLoading(true);

    try {
      const response = await axios.post('http://127.0.0.1:8000/api/workflow/analyze', {
        user_id: 1,
        input_text: userMessage,
        context: { mood: "neutral", time_of_day: "evening" }
      });
      
      const data = response.data;
      let aiResponse = `I see you had ${data.food_items.join(", ")}. `;
      aiResponse += `That's about ${data.nutrition.calories} calories${data.nutrition.is_estimated ? ' (estimated)' : ''}. `;
      aiResponse += `\n\nHealth Note: ${data.health_explanation}`;
      
      if (data.recommendations && data.recommendations.length > 0) {
         aiResponse += `\n\nTip: ${data.recommendations[0]}`;
      }

      setMessages(prev => [...prev, { role: 'ai', text: aiResponse }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'ai', text: "Sorry, I couldn't process that right now. Please try again." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen sm:h-auto sm:min-h-screen bg-slate-50 relative overflow-hidden">
      {/* Header */}
      <div className="absolute top-0 w-full bg-white/80 backdrop-blur-md border-b border-slate-200 p-4 z-10">
        <div className="max-w-3xl mx-auto flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-white shadow-sm">
            <Bot size={24} />
          </div>
          <div>
            <h1 className="font-bold text-slate-800 text-lg">NutriCoach</h1>
            <p className="text-xs text-emerald-600 font-medium flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span> Online
            </p>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 pt-24 pb-24 sm:pb-32 w-full max-w-3xl mx-auto space-y-6">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-2`}>
            <div className={`flex gap-3 max-w-[85%] ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
              <div className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center text-white shadow-sm ${msg.role === 'user' ? 'bg-slate-800' : 'bg-gradient-to-br from-emerald-400 to-teal-500'}`}>
                {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
              </div>
              <div className={`p-4 rounded-2xl text-sm leading-relaxed ${
                msg.role === 'user' 
                  ? 'bg-slate-800 text-white rounded-tr-sm' 
                  : 'bg-white text-slate-700 shadow-sm border border-slate-100 rounded-tl-sm whitespace-pre-wrap'
              }`}>
                {msg.text}
              </div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="flex gap-3 max-w-[85%]">
              <div className="w-8 h-8 rounded-full flex-shrink-0 bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center text-white shadow-sm">
                <Bot size={16} />
              </div>
              <div className="p-4 rounded-2xl bg-white shadow-sm border border-slate-100 rounded-tl-sm flex items-center gap-2">
                <div className="w-2 h-2 bg-emerald-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="fixed sm:absolute bottom-16 sm:bottom-0 w-full sm:w-[calc(100%-16rem)] p-4 bg-gradient-to-t from-slate-50 via-slate-50/90 to-transparent z-10 left-0 sm:left-64">
        <form onSubmit={handleSend} className="max-w-3xl mx-auto relative group">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your meal or ask for advice..."
            className="w-full bg-white border-2 border-slate-200 focus:border-emerald-500 text-slate-800 rounded-full pl-6 pr-14 py-4 outline-none transition-all shadow-sm focus:shadow-md text-sm font-medium placeholder:text-slate-400"
            disabled={isLoading}
          />
          <button 
            type="submit" 
            disabled={isLoading || !input.trim()}
            className="absolute right-2 top-2 bottom-2 aspect-square rounded-full bg-emerald-500 text-white flex items-center justify-center hover:bg-emerald-600 disabled:opacity-50 disabled:hover:bg-emerald-500 transition-colors group-focus-within:bg-emerald-600"
          >
            {isLoading ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} className="-ml-0.5" />}
          </button>
        </form>
      </div>
    </div>
  );
}
