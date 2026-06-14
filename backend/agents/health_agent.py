from typing import Dict, Any

class HealthAgent:
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compute a Smart Health Score using a weighted formula,
        penalizing based on active nutrient threshold warnings.
        Health Score = 0.25 Nutrition + 0.20 Activity + 0.15 Sleep + 0.15 Hydration + 0.25 Consistency
        """
        nutrition = state.get("nutrition", {})
        warnings = state.get("warnings", [])
        is_exceeded = state.get("is_exceeded", False)
        
        def safe_float(val):
            try:
                return float(val) if val is not None else 0.0
            except (ValueError, TypeError):
                return 0.0

        calories = safe_float(nutrition.get("calories", 0))
        sugar = safe_float(nutrition.get("sugar", 0))
        protein = safe_float(nutrition.get("protein", 0))
        sodium = safe_float(nutrition.get("sodium", 0))

        # Calculate base Nutrition Score
        nutrition_score = 100
        explanation = []

        if calories > 800:
            nutrition_score -= 20
            explanation.append("High calorie single intake.")
        elif calories < 200:
            nutrition_score -= 10
            
        if sugar > 15:
            nutrition_score -= 25
            explanation.append(f"High sugar content ({sugar:.0f}g).")
            
        if sodium > 1000:
            nutrition_score -= 25
            explanation.append(f"High sodium level ({sodium:.0f}mg).")

        if protein >= 20:
            nutrition_score += 10
            explanation.append("Excellent protein amount.")
            
        nutrition_score = max(0, min(100, nutrition_score))
        
        # Simulate other factors (In production, these come from wearable integrations / DB)
        activity_score = 80
        sleep_score = 75
        hydration_score = 90
        consistency_score = 85
        
        # Weighted Health Formula
        final_score = (0.25 * nutrition_score) + (0.20 * activity_score) + (0.15 * sleep_score) + (0.15 * hydration_score) + (0.25 * consistency_score)
        
        # Apply additional warning penalties
        if is_exceeded:
            final_score -= (len(warnings) * 8.0)
            
        final_score = max(0, min(100, final_score))
        
        state["health_score"] = round(final_score)
        
        # Prepend warnings to explanation
        if warnings:
            state["health_explanation"] = "⚠️ Warning: " + " | ".join(warnings) + ". " + " ".join(explanation)
        else:
            state["health_explanation"] = " ".join(explanation) if explanation else "Balanced nutrition detected."
        
        return state
