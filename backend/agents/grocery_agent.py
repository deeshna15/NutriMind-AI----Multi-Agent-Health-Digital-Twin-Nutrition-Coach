import json
import httpx  # pyrefly: ignore [missing-import]
from typing import Dict, Any

class GroceryAgent:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert meal plan into structured grocery list based on pantry inventory.
        """
        meal_plan = state.get("meal_plan", {})
        
        # Current simulated pantry inventory
        current_inventory = {
            "Eggs": 4,
            "Tomatoes": 2,
            "Apples": 1,
            "Onions": 3,
            "Greek Yogurt": 1
        }

        if meal_plan:
            prompt = f"""
            Given this meal plan:
            {json.dumps(meal_plan)}
            
            And given the user's current pantry inventory:
            {json.dumps(current_inventory)}
            
            Identify the ingredients needed to prepare the breakfast, lunch, dinner, and snacks in the meal plan.
            Calculate what ingredients the user needs to BUY by subtracting what they HAVE (current pantry inventory) from what is REQUIRED.
            If they need a certain ingredient and have a small amount, adjust the amount they need to buy.
            
            Format the shopping list into clear categories (e.g. Produce, Proteins, Grains & Pantry, Dairy & Nuts).
            Return ONLY a JSON array of objects with this exact structure:
            [
              {{"category": "Produce", "items": ["4 Tomatoes (Needed 6 - Have 2)", "Spinach"]}},
              {{"category": "Proteins", "items": ["Chicken breast", "8 Eggs (Needed 12 - Have 4)"]}}
            ]
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
                    text = data.get("response", "[]")
                    parsed_data = json.loads(text)
                    if isinstance(parsed_data, list):
                        state["grocery_list"] = parsed_data
                        return state
            except Exception as e:
                print(f"GroceryAgent Ollama Error: {e}")
                raise Exception(f"GroceryAgent Ollama Error: {e}") from e
