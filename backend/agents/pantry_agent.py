import sys
import os
import json
from typing import Dict, Any, List
from datetime import date
import httpx  # pyrefly: ignore [missing-import]

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import SessionLocal
from models import FoodHistory

class PantryAgent:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"

    def process(self, state: Dict[str, Any], image_base64: str) -> Dict[str, Any]:
        """
        Uses Vision AI (Ollama Llava) to detect pantry/fridge ingredients,
        queries today's food history, and generates recipes designed to balance the user's diet.
        """
        if not image_base64:
            state["detected_ingredients"] = []
            state["possible_meals"] = []
            return state

        # 1. Fetch today's food history
        db = SessionLocal()
        today = date.today()
        # Query for user_id = 1 (seeded demo user)
        foods_today = db.query(FoodHistory).filter(FoodHistory.user_id == 1).all()
        foods_today = [f for f in foods_today if f.timestamp.date() == today]
        db.close()

        # Compile summaries
        logged_meals = []
        total_cals = 0.0
        total_carbs = 0.0
        total_fat = 0.0
        total_sugar = 0.0
        total_sodium = 0.0
        warnings = []

        for f in foods_today:
            logged_meals.extend(f.food_items)
            total_cals += f.calories
            total_carbs += f.carbs
            total_fat += f.fat
            total_sugar += f.sugar
            total_sodium += f.sodium
            
            if f.calories > 800:
                warnings.append("High Calorie single intake")
            if f.sugar > 15:
                warnings.append("High Sugar intake")
            if f.sodium > 1000:
                warnings.append("High Sodium intake")

        diet_status_context = ""
        if foods_today:
            diet_status_context = f"""
            The user has already consumed the following today: {", ".join(logged_meals)}.
            Nutrients consumed so far:
            - Calories: {total_cals:.0f} kcal
            - Carbs: {total_carbs:.0f}g
            - Fat: {total_fat:.0f}g
            - Sugar: {total_sugar:.0f}g
            - Sodium: {total_sodium:.0f}mg
            Threshold alarms triggered: {", ".join(set(warnings)) if warnings else "None"}.
            
            DIETARY BALANCING CRITERIA:
            You must suggest meals that help the user restore their nutritional balance based on what they already ate.
            If they ate a high-calorie, high-fat, or high-sodium meal (like Pizza or fast food), recommend light meals (e.g. low-carb, low-fat, low-sodium, high-fiber, lean protein) that leverage the detected pantry items. Mention how the suggested meal helps balance today's excesses.
            """
        else:
            diet_status_context = "No meals logged yet today. Recommend healthy, balanced general recipes using the pantry items."

        prompt = f"""
        Analyze this image of a pantry, fridge, or kitchen counter.
        1. Identify ONLY the visible ingredients/food items. Do NOT guess or hallucinate items.
        2. Suggest up to 5 meals that can be prepared primarily using these detected ingredients.
        3. For each meal, provide:
           - Meal Name
           - Detailed description and cooking recipe instructions
           - Required ingredients matching the user's pantry
           - How this meal balances their diet today based on their consumption history.

        {diet_status_context}

        Return ONLY a JSON object with this exact structure:
        {{
            "detected_ingredients": ["ingredient1", "ingredient2", "ingredient3"],
            "possible_meals": [
                {{
                    "name": "Meal Name",
                    "description": "Recipe details: Instructions, ingredients matching, and why it balances today's diet."
                }}
            ]
        }}
        """

        try:
            payload = {
                "model": "llava",
                "prompt": prompt,
                "images": [image_base64],
                "stream": False,
                "format": "json"
            }
            response = httpx.post(self.ollama_url, json=payload, timeout=None)
            if response.status_code == 200:
                data = response.json()
                text = data.get("response", "{}")
                parsed_data = json.loads(text)
                
                state["detected_ingredients"] = parsed_data.get("detected_ingredients", [])
                state["possible_meals"] = parsed_data.get("possible_meals", [])
                return state
        except Exception as e:
            print(f"PantryAgent Ollama Vision Error: {e}")
            raise Exception(f"PantryAgent Ollama Vision Error: {e}") from e
