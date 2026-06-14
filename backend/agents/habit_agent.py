from typing import Dict, Any
import httpx  # pyrefly: ignore [missing-import]
import json

class HabitAgent:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"

    def process(self, state: Dict[str, Any], context: Dict[str, str], input_text: str = "") -> Dict[str, Any]:
        """
        Acts as the Context-Aware AI Nutrition Coach.
        """
        if "habit_insights" in state and state["habit_insights"]:
            return state

        user_query = input_text if input_text else "Give me a brief encouraging tip based on my current meal."
        
        # Simulate fetching memory from UserProfile.memory_blob
        memory = {
            "daily_calorie_goal": 2000,
            "calories_consumed_today": 1450,
            "favorite_foods": ["Ice Cream", "Pizza"],
            "allergies": ["Peanuts"]
        }

        # Simulate retrieving behavioral patterns from memory
        weekly_patterns = {
            "Friday": "User often orders junk food or fast food in the evening.",
            "Sunday": "User skips breakfast."
        }
        
        from datetime import datetime
        current_day = datetime.now().strftime("%A")
        
        habit_nudge = ""
        if current_day in weekly_patterns:
            pattern = weekly_patterns[current_day]
            habit_nudge = f"Pattern Detected: {pattern} Suggestion: Prepare healthy alternatives in advance to beat the craving!"

        prompt = f"""
        You are a highly empathetic and knowledgeable AI Nutrition Coach.
        The user has asked: "{user_query}"
        
        Here is the user's current context:
        - Budget: $60/week
        - Allergies: Peanuts
        - Today's Calorie Goal: 2000 kcal
        - Calories Consumed So Far: 1450 kcal
        - Habit Nudge: {habit_nudge}
        
        Provide a concise, highly personalized response that directly answers their question while adhering to their context. If there is a habit nudge, address it gently.
        Return ONLY a JSON object with this exact structure:
        {{
            "coach_response": "Your conversational answer here"
        }}
        """

        try:
            payload = {
                "model": "llama3.2",
                "prompt": prompt,
                "stream": False,
                "format": "json"
            }
            response = httpx.post(self.ollama_url, json=payload, timeout=None)
            if response.status_code == 200:
                data = response.json()
                text = data.get("response", "{}")
                parsed_data = json.loads(text)
                
                coach_response = parsed_data.get("coach_response", "")
                if coach_response:
                    state["habit_insights"] = [coach_response]
                return state
        except Exception as e:
            print(f"HabitAgent LLM Error: {e}")
            raise Exception(f"HabitAgent LLM Error: {e}") from e
