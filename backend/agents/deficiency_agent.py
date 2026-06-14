from typing import Dict, Any, List
import httpx  # pyrefly: ignore [missing-import]
import json

class DeficiencyAgent:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"

    def process(self, state: Dict[str, Any], user_history: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyzes historical food data to predict micronutrient deficiencies.
        """
        if "deficiency_risks" in state and state["deficiency_risks"]:
            return state

        if not user_history:
            user_history = [
                {"day": "Monday", "calories": 1400, "protein": 40, "iron_intake": "low", "vitamin_d": "low"},
                {"day": "Tuesday", "calories": 1500, "protein": 45, "iron_intake": "low", "vitamin_d": "medium"},
                {"day": "Wednesday", "calories": 1300, "protein": 38, "iron_intake": "very low", "vitamin_d": "low"},
                {"day": "Thursday", "calories": 1450, "protein": 50, "iron_intake": "low", "vitamin_d": "low"}
            ]

        history_str = json.dumps(user_history)

        prompt = f"""
        You are an expert AI Nutritionist. Analyze the following food history summary:
        {history_str}

        Detect any possible long-term nutritional deficiencies based on these patterns (e.g., Protein, Iron, Vitamin D, Fiber).
        Return ONLY a JSON object with this exact structure:
        {{
            "deficiency_risks": ["Low Iron", "Low Protein"],
            "recommended_foods": ["Spinach", "Lentils", "Eggs", "Fish"]
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
                state["deficiency_risks"] = parsed_data.get("deficiency_risks", [])
                state["deficiency_recommendations"] = parsed_data.get("recommended_foods", [])
                return state
        except Exception as e:
            print(f"DeficiencyAgent LLM Error: {e}")
            raise Exception(f"DeficiencyAgent LLM Error: {e}") from e
