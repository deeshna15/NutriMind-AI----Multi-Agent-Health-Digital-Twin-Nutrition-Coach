from typing import Dict, Any
import numpy as np
from sklearn.linear_model import LinearRegression

class PredictionAgent:
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Uses Machine Learning (Linear Regression) to build a Digital Twin forecast.
        Predicts weight and health score 30 days into the future based on historical data.
        """
        # Simulated historical data for MVP (Days 1 to 30)
        # X is days, Y_weight is weight in kg, Y_score is health score
        X = np.array([[1], [5], [10], [15], [20], [25], [30]])
        
        # User started at 80kg, losing weight gradually
        Y_weight = np.array([80.0, 79.5, 79.0, 78.4, 78.1, 77.8, 77.5])
        
        # Health score has been improving from 70 to 85
        Y_score = np.array([70, 72, 75, 78, 80, 83, 85])

        # Train ML models
        weight_model = LinearRegression().fit(X, Y_weight)
        score_model = LinearRegression().fit(X, Y_score)

        # Predict 30 days from now (Day 60)
        future_day = np.array([[60]])
        
        future_weight = weight_model.predict(future_day)
        future_score = score_model.predict(future_day)

        # Provide detailed scenario simulation
        baseline_weight = round(future_weight[0], 1)
        optimized_weight = round(future_weight[0] - 1.5, 1) # Assuming a 1.5kg difference if optimized
        
        state["weight_forecast"] = baseline_weight
        state["health_score_forecast"] = int(future_score[0])
        
        state["digital_twin_scenarios"] = {
            "baseline": {
                "description": "If you continue your current diet and activity patterns for 30 days:",
                "projected_weight": f"{baseline_weight} kg",
                "projected_score": f"{int(future_score[0])} / 100",
                "risk_warning": "Cholesterol risk may elevate slightly if saturated fat remains high."
            },
            "optimized": {
                "description": "If you increase protein intake by 20% and reduce sodium by 15%:",
                "projected_weight": f"{optimized_weight} kg",
                "projected_score": f"{min(int(future_score[0]) + 12, 100)} / 100",
                "benefit": "Muscle gain (+1.8 kg) and improved cardiovascular health."
            }
        }
        
        return state
