import os
import httpx  # pyrefly: ignore [missing-import]
import json
from typing import Dict, Any

class NutritionAgent:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.edamam_app_id = os.getenv("EDAMAM_APP_ID")
        self.edamam_app_key = os.getenv("EDAMAM_APP_KEY")
        self.thresholds = {
            "calories": 800.0,
            "carbs": 100.0,
            "fat": 30.0,
            "sugar": 15.0,
            "sodium": 1000.0
        }

    def process(self, food_text: str, state: Dict[str, Any], image_base64: str = None) -> Dict[str, Any]:
        """
        Classifies food using Ollama (llava for images, llama3.2 for text),
        runs threshold warnings, and logs nutritional variables.
        """
        food_items = []
        portion = "1 serving"
        
        # 1. Visually identify items (if image uploaded) using Llava
        if image_base64:
            vision_prompt = """
            Analyze the following food image carefully.
            Identify ONLY the individual items that are CLEARLY VISIBLE in the picture.
            CRITICAL HINTS TO PREVENT HALLUCINATION:
            - Do not guess or assume ingredients that you cannot see.
            - Do not hallucinate meat (such as chicken or beef) if it is a vegetarian meal (e.g. plain rice, beans, or bread).
            - Only list items you are 100% visually certain of.
            
            Return ONLY a JSON object with this exact structure:
            {
                "food_items": ["item1", "item2"],
                "portion_estimation": "e.g. 1 plate, 1 bowl, 2 pieces"
            }
            """
            try:
                payload = {
                    "model": "llava",
                    "prompt": vision_prompt,
                    "images": [image_base64],
                    "stream": False,
                    "format": "json"
                }
                response = httpx.post(self.ollama_url, json=payload, timeout=None)
                if response.status_code == 200:
                    data = response.json()
                    response_text = data.get("response", "{}")
                    parsed_vision = json.loads(response_text)
                    food_items = parsed_vision.get("food_items", [])
                    portion = parsed_vision.get("portion_estimation", "1 serving")
            except Exception as e:
                print(f"Ollama Vision (Llava) Error: {e}")
                food_items = ["Unknown Food Item"]
        
        # 2. Get the search query text (either visual list or text input)
        search_query = ", ".join(food_items) if image_base64 else food_text
        if not search_query:
            search_query = "Unknown meal"

        # 3. Try Edamam API for verified data first (if query is simple and credentials exist)
        edamam_worked = False
        nutrition_data = {}
        if self.edamam_app_id and self.edamam_app_key and not image_base64:
            try:
                response = httpx.get(
                    "https://api.edamam.com/api/nutrition-data",
                    params={"app_id": self.edamam_app_id, "app_key": self.edamam_app_key, "ingr": search_query},
                    timeout=5.0
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("calories", 0) > 0:
                        nutrients = data.get("totalNutrients", {})
                        nutrition_data = {
                            "calories": float(data.get("calories", 0.0)),
                            "protein": float(nutrients.get("PROCNT", {}).get("quantity", 0.0)),
                            "carbs": float(nutrients.get("CHOCDF", {}).get("quantity", 0.0)),
                            "fat": float(nutrients.get("FAT", {}).get("quantity", 0.0)),
                            "sugar": float(nutrients.get("SUGAR", {}).get("quantity", 0.0)),
                            "sodium": float(nutrients.get("NA", {}).get("quantity", 0.0)),
                            "is_estimated": False
                        }
                        food_items = [search_query]
                        edamam_worked = True
            except Exception as e:
                print(f"Edamam API Error: {e}")

        # Fetch RAG guidelines
        from agents.rag_agent import RAGAgent
        try:
            rag_agent = RAGAgent()
            retrieved_doc = rag_agent.retrieve_guidelines(search_query)
        except Exception as e:
            print(f"Failed to fetch RAG guidelines: {e}")
            retrieved_doc = "- No specific guideline found."

        # Fetch weekly patterns and habit nudge
        from datetime import datetime
        weekly_patterns = {
            "Friday": "User often orders junk food or fast food in the evening.",
            "Sunday": "User skips breakfast."
        }
        current_day = datetime.now().strftime("%A")
        habit_nudge = ""
        if current_day in weekly_patterns:
            pattern = weekly_patterns[current_day]
            habit_nudge = f"Pattern Detected: {pattern} Suggestion: Prepare healthy alternatives in advance to beat the craving!"
        
        # Build simulated deficiency history
        user_history = [
            {"day": "Monday", "calories": 1400, "protein": 40, "iron_intake": "low", "vitamin_d": "low"},
            {"day": "Tuesday", "calories": 1500, "protein": 45, "iron_intake": "low", "vitamin_d": "medium"},
            {"day": "Wednesday", "calories": 1300, "protein": 38, "iron_intake": "very low", "vitamin_d": "low"},
            {"day": "Thursday", "calories": 1450, "protein": 50, "iron_intake": "low", "vitamin_d": "low"}
        ]
        history_str = json.dumps(user_history)

        # 4. Fallback/Primary for general text: Ask Llama 3.2 to estimate nutrition values
        if not edamam_worked:
            estimate_prompt = f"""
            You are NutriMind, an expert AI nutritionist, health coach, and digital twin analyzer.
            Analyze the following food item(s): "{search_query}" with portion size "{portion}".
            
            Here is the user's health context:
            - Daily Calorie Goal: 2000 kcal (Calories Consumed So Far: 1450 kcal)
            - Allergies: Peanuts
            - Budget: Medium ($60/week)
            - Today's Habit Nudge: {habit_nudge}
            
            Analyze the user's food intake history to predict micronutrient deficiency risks (e.g. Iron, Vitamin D, Protein, Fiber) based on this historical log:
            {history_str}
            
            Here are the official nutritional guidelines matching the foods consumed:
            {retrieved_doc}
            
            Perform a complete evaluation. Outline:
            1. Cumulative nutritional values (calories, protein, carbs, fat, sugar, sodium).
            2. Swaps/recommendations.
            3. Long-term metabolic/disease risk factors if the meal exceeds the guidelines.
            4. A warm, supportive coaching tip/response based on their meal, goal, and habit nudge.
            5. Predicted deficiency risks and recommended foods to address them.
            
            Return ONLY a JSON object with this exact structure:
            {{
                "food_items": ["item1", "item2"],
                "nutrition": {{
                    "calories": 0.0,
                    "protein": 0.0,
                    "carbs": 0.0,
                    "fat": 0.0,
                    "sugar": 0.0,
                    "sodium": 0.0
                }},
                "disease_risk_analysis": ["risk1", "risk2"],
                "recommendations": ["swap1", "swap2"],
                "rag_answer": {{
                    "answer": "Your grounded response detailing values and risk factors based strictly on the guidelines",
                    "source": "The specific guidelines you matched"
                }},
                "habit_insights": ["Your warm coaching tips/nudges"],
                "deficiency_risks": ["Risk1", "Risk2"],
                "deficiency_recommendations": ["Food1", "Food2"]
            }}
            """
            try:
                payload = {
                    "model": "llama3.2",
                    "prompt": estimate_prompt,
                    "stream": False,
                    "format": "json"
                }
                response = httpx.post(self.ollama_url, json=payload, timeout=None)
                if response.status_code == 200:
                    data = response.json()
                    response_text = data.get("response", "{}")
                    parsed_llm = json.loads(response_text)
                    
                    if not food_items:
                        food_items = parsed_llm.get("food_items", [search_query])
                    
                    nut = parsed_llm.get("nutrition", {})
                    nutrition_data = {
                        "calories": float(nut.get("calories", 400.0)),
                        "protein": float(nut.get("protein", 15.0)),
                        "carbs": float(nut.get("carbs", 50.0)),
                        "fat": float(nut.get("fat", 12.0)),
                        "sugar": float(nut.get("sugar", 5.0)),
                        "sodium": float(nut.get("sodium", 400.0)),
                        "is_estimated": True
                    }
                    state["disease_risk_analysis"] = parsed_llm.get("disease_risk_analysis", [])
                    state["recommendations"] = parsed_llm.get("recommendations", [])
                    
                    # Store consolidated values for RAG, Habit, and Deficiency agents
                    state["rag_answer"] = parsed_llm.get("rag_answer", {})
                    state["habit_insights"] = parsed_llm.get("habit_insights", [])
                    state["deficiency_risks"] = parsed_llm.get("deficiency_risks", [])
                    state["deficiency_recommendations"] = parsed_llm.get("deficiency_recommendations", [])
                    
                    # Append RAG grounded risks into the state's disease risks
                    rag_ans_text = state["rag_answer"].get("answer", "")
                    if rag_ans_text:
                        state["disease_risk_analysis"].append(f"RAG Grounded Warning: {rag_ans_text[:120]}...")
                        
                    edamam_worked = True
            except Exception as e:
                print(f"Ollama Llama3.2 Estimation Error: {e}")
                raise Exception(f"Ollama Llama3.2 Estimation Error: {e}") from e

        # Ensure we don't proceed with missing/unresolved nutrition data
        if not edamam_worked:
            raise Exception("Nutrition estimation failed. Neither Edamam nor Ollama is available.")

        # Commit to state
        state["food_items"] = food_items
        state["portion_estimation"] = portion
        state["nutrition"] = nutrition_data

        # Enforce Programmatic Nutrient Thresholds
        warnings = []
        is_exceeded = False
        exceeded_count = 0

        cals = state["nutrition"]["calories"]
        carbs = state["nutrition"]["carbs"]
        fat = state["nutrition"]["fat"]
        sugar = state["nutrition"]["sugar"]
        sodium = state["nutrition"]["sodium"]

        if cals > self.thresholds["calories"]:
            warnings.append(f"Calorie threshold exceeded ({cals:.0f} kcal > {self.thresholds['calories']:.0f} kcal)")
            is_exceeded = True
            exceeded_count += 1
        if carbs > self.thresholds["carbs"]:
            warnings.append(f"Carbs threshold exceeded ({carbs:.0f}g > {self.thresholds['carbs']:.0f}g)")
            is_exceeded = True
            exceeded_count += 1
        if fat > self.thresholds["fat"]:
            warnings.append(f"Fat threshold exceeded ({fat:.0f}g > {self.thresholds['fat']:.0f}g)")
            is_exceeded = True
            exceeded_count += 1
        if sugar > self.thresholds["sugar"]:
            warnings.append(f"Sugar threshold exceeded ({sugar:.0f}g > {self.thresholds['sugar']:.0f}g)")
            is_exceeded = True
            exceeded_count += 1
        if sodium > self.thresholds["sodium"]:
            warnings.append(f"Sodium threshold exceeded ({sodium:.0f}mg > {self.thresholds['sodium']:.0f}mg)")
            is_exceeded = True
            exceeded_count += 1

        state["warnings"] = warnings
        state["is_exceeded"] = is_exceeded

        # Calculate daily risk level
        if exceeded_count == 0:
            state["risk_level"] = "LOW"
        elif exceeded_count <= 2:
            state["risk_level"] = "MEDIUM"
        else:
            state["risk_level"] = "HIGH"

        return state
