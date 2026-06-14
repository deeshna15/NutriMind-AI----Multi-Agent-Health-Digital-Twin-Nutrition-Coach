import sys
import os
from typing import Dict, Any, List
from datetime import date
import httpx  # pyrefly: ignore [missing-import]
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import SessionLocal  # pyrefly: ignore [missing-import]
from models import UserProfile, FoodHistory  # pyrefly: ignore [missing-import]

class GoalAgent:
    """
    Agent 1: Profile and Goal Analyzer.
    Determines calorie and macronutrient targets based on demographics and specific health goals.
    """
    def determine_targets(self, user: UserProfile) -> Dict[str, Any]:
        weight = user.weight if user.weight else 70.0
        height = user.height if user.height else 175.0
        age = user.age if user.age else 25
        
        # Base BMR (Harris-Benedict equation)
        base_calories = 10 * weight + 6.25 * height - 5 * age + 5
        
        # Activity multipliers
        multiplier = 1.2 # Sedentary
        if user.activity_level == "Lightly Active":
            multiplier = 1.375
        elif user.activity_level == "Moderately Active":
            multiplier = 1.55
        elif user.activity_level == "Very Active":
            multiplier = 1.725
            
        tdee = base_calories * multiplier
        
        # Adjust targets based on Health Goals/Conditions
        goal_lower = user.goal.lower() if user.goal else "maintenance"
        
        targets = {
            "calories": round(tdee),
            "protein": round(weight * 1.2),  # g
            "carbs": round(tdee * 0.5 / 4),  # g
            "fat": round(tdee * 0.25 / 9),   # g
            "sugar": 30.0,                   # g
            "sodium": 2000.0,                # mg
            "focus_description": "General healthy maintenance diet"
        }
        
        if "loss" in goal_lower:
            targets["calories"] = round(tdee - 500)
            targets["protein"] = round(weight * 1.6) # high protein
            targets["carbs"] = round(targets["calories"] * 0.4 / 4)
            targets["fat"] = round(targets["calories"] * 0.25 / 9)
            targets["focus_description"] = "Caloric deficit, high-protein for fat loss while preserving lean mass."
            
        elif "gain" in goal_lower or "muscle" in goal_lower:
            targets["calories"] = round(tdee + 300)
            targets["protein"] = round(weight * 2.0)
            targets["carbs"] = round(targets["calories"] * 0.5 / 4)
            targets["fat"] = round(targets["calories"] * 0.25 / 9)
            targets["focus_description"] = "Caloric surplus, high-protein for muscle hypertrophy."
            
        elif "diabetes" in goal_lower:
            targets["calories"] = round(tdee - 200) # slight deficit
            targets["protein"] = round(weight * 1.4)
            targets["carbs"] = 120.0 # strict carb limit
            targets["fat"] = round(targets["calories"] * 0.3 / 9)
            targets["sugar"] = 15.0 # Low sugar limit
            targets["focus_description"] = "Glycemic control. Strict carbohydrate and sugar limits, high fiber intake."
            
        elif "pcos" in goal_lower:
            targets["calories"] = round(tdee - 200)
            targets["protein"] = round(weight * 1.5)
            targets["carbs"] = 100.0 # Low-glycemic carbs focus
            targets["fat"] = round(targets["calories"] * 0.35 / 9) # Higher healthy fats
            targets["sugar"] = 15.0
            targets["focus_description"] = "Insulin resistance management. Low-glycemic index (GI) foods, low-carb, high healthy fats."
            
        elif "heart" in goal_lower or "cardio" in goal_lower:
            targets["calories"] = round(tdee)
            targets["protein"] = round(weight * 1.2)
            targets["carbs"] = round(tdee * 0.5 / 4)
            targets["fat"] = round(tdee * 0.25 / 9)
            targets["sodium"] = 1300.0 # Heart health low sodium
            targets["sugar"] = 25.0
            targets["focus_description"] = "Cardiovascular support. Low sodium, low saturated fats, high potassium and dietary fiber."

        return targets

class MealDraftingAgent:
    """
    Agent 2: Meal Planner.
    Drafts standard meal recommendations meeting target nutrition goals using Ollama Llama 3.2.
    """
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"

    def draft_meals(self, targets: Dict[str, Any], diet_type: str) -> Dict[str, Any]:
        prompt = f"""
        Draft a high-quality 1-day meal plan matching these target requirements:
        - Target Calories: {targets['calories']} kcal
        - Target Protein: {targets['protein']}g
        - Target Carbs: {targets['carbs']}g
        - Target Fat: {targets['fat']}g
        - Target Sugar: {targets['sugar']}g
        - Target Sodium: {targets['sodium']}mg
        - Diet Type: {diet_type}
        - Focus: {targets['focus_description']}

        Provide a structured, delicious menu including Breakfast, Lunch, Snack, and Dinner.
        Return ONLY a JSON object with this exact structure:
        {{
            "breakfast": "Detailed meal name and summary",
            "lunch": "Detailed meal name and summary",
            "snacks": ["Snack 1 description", "Snack 2 description"],
            "dinner": "Detailed meal name and summary"
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
                return json.loads(text)
        except Exception as e:
            print(f"MealDraftingAgent Ollama Error: {e}")
            raise Exception(f"MealDraftingAgent Ollama Error: {e}") from e

class DietaryBalancingAgent:
    """
    Agent 3: Dynamic Replanning and Dietary Balancer.
    Monitors daily intakes, checks threshold alerts, and rewrites remaining meals using Ollama.
    """
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"

    def balance_and_replan(self, user_id: int, target_cals: float, draft_plan: Dict[str, Any]) -> Dict[str, Any]:
        db = SessionLocal()
        today = date.today()
        
        # Query today's logged meals
        foods_today = db.query(FoodHistory).filter(FoodHistory.user_id == user_id).all()
        foods_today = [f for f in foods_today if f.timestamp.date() == today]
        db.close()

        if not foods_today:
            # No logs today, return draft meal plan directly
            draft_plan["replanning_note"] = "Standard meal plan loaded. No meals logged yet today."
            return draft_plan

        # Calculate totals consumed today
        total_cals = sum(f.calories for f in foods_today)
        total_carbs = sum(f.carbs for f in foods_today)
        total_fat = sum(f.fat for f in foods_today)
        total_sugar = sum(f.sugar for f in foods_today)
        total_sodium = sum(f.sodium for f in foods_today)
        logged_foods = [", ".join(f.food_items) for f in foods_today]

        # Check if thresholds exceeded in today's meals
        has_limit_hit = False
        exceeded_details = []

        for f in foods_today:
            if f.calories > 800:
                exceeded_details.append(f"Calorie threshold hit ({f.calories:.0f} kcal)")
                has_limit_hit = True
            if f.sugar > 15:
                exceeded_details.append(f"Sugar threshold hit ({f.sugar:.0f}g)")
                has_limit_hit = True
            if f.sodium > 1000:
                exceeded_details.append(f"Sodium threshold hit ({f.sodium:.0f}mg)")
                has_limit_hit = True

        remaining_cals = target_cals - total_cals

        # Trigger Dynamic Replanning if threshold was hit or remaining calories are very low
        if has_limit_hit or remaining_cals < 600:
            prompt = f"""
            DYNAMIC REPLANNING AND DIETARY BALANCING INSTRUCTIONS:
            The user has already consumed the following meals today: {", ".join(logged_foods)}.
            Total Nutrients Consumed:
            - Calories: {total_cals:.0f} kcal
            - Carbs: {total_carbs:.0f}g
            - Fat: {total_fat:.0f}g
            - Sugar: {total_sugar:.0f}g
            - Sodium: {total_sodium:.0f}mg

            Nutrient Limits Exceeded: {", ".join(exceeded_details) if exceeded_details else "None directly, but calorie budget is tight."}
            Daily target calorie budget: {target_cals:.0f} kcal.
            Remaining budget: {remaining_cals:.0f} kcal.

            You MUST adjust the remaining meals (Dinner and Snacks) to balance the diet and restore the daily goal.
            - If calories/carbs/fat/sodium were exceeded, make the remaining meals extremely light, such as a fresh garden salad, light steamed vegetables, and/or a lean grilled chicken breast/tofu (very low calorie, low carb, low fat, low sodium, high protein).
            - Keep the remaining calorie counts strictly within the remaining budget: {remaining_cals:.0f} kcal.

            Draft plan was:
            Breakfast: {draft_plan.get('breakfast')}
            Lunch: {draft_plan.get('lunch')}
            Snacks: {draft_plan.get('snacks')}
            Dinner: {draft_plan.get('dinner')}

            Rewrite the remaining plan. Return ONLY a JSON object:
            {{
                "breakfast": "Keep original if consumed, or modify if applicable",
                "lunch": "Keep original if consumed, or modify if applicable",
                "snacks": ["Light balancing snack description", "Water"],
                "dinner": "Modified Dinner: Light Salad, Grilled Chicken (or veggie alternative) to restore goal",
                "replanning_note": "A clear note indicating what exceeded thresholds (e.g. Lunch exceeded calories. Dinner modified to Salad & Grilled Chicken. Daily goal restored.)"
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
                    return json.loads(text)
            except Exception as e:
                print(f"DietaryBalancingAgent Ollama Error: {e}")
                raise Exception(f"DietaryBalancingAgent Ollama Error: {e}") from e

        # No major limits hit, just add standard note
        draft_plan["replanning_note"] = f"Budget track: {total_cals:.0f} kcal consumed, {remaining_cals:.0f} kcal remaining. Eating is on track."
        return draft_plan


class MealAgent:
    """
    Orchestrator for the Multi-Agent Meal Planner.
    """
    def __init__(self):
        self.goal_agent = GoalAgent()
        self.draft_agent = MealDraftingAgent()
        self.balance_agent = DietaryBalancingAgent()

    def process(self, state: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        db = SessionLocal()
        user = db.query(UserProfile).filter(UserProfile.id == user_id).first()
        db.close()
        
        if not user:
            # Fallback mock profile if not seeded
            user = UserProfile(
                age=25,
                weight=70.0,
                height=175.0,
                activity_level="Moderately Active",
                goal="weight loss",
                diet_type="veg"
            )

        # Agent 1: Goals and Targets
        targets = self.goal_agent.determine_targets(user)
        
        # Agent 2: Draft Meals
        draft_plan = self.draft_agent.draft_meals(targets, user.diet_type)
        
        # Agent 3: Dynamic Replanning & Balancing
        final_plan = self.balance_agent.balance_and_replan(user.id, targets["calories"], draft_plan)
        
        state["meal_plan"] = final_plan
        return state
