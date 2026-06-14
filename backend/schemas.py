from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- Tool Request/Response Schemas ---
class NutritionRequest(BaseModel):
    food_names: List[str]

class NutritionInfo(BaseModel):
    calories: float
    protein: float
    carbs: float
    fat: float
    sugar: float
    sodium: float = 0.0
    is_estimated: bool = False

class MealGenerationRequest(BaseModel):
    goal: str
    calorie_target: float
    diet_type: str

class UserProfileSchema(BaseModel):
    id: Optional[int] = None
    name: str
    age: int
    weight: float
    goal: str
    diet_type: str
    allergies: List[str]
    current_streak: Optional[int] = 0
    highest_streak: Optional[int] = 0

    class Config:
        from_attributes = True

# --- Agent & Workflow Schemas ---
class AgentResponse(BaseModel):
    food_items: List[str] = []
    portion_estimation: str = ""
    disease_risk_analysis: List[str] = []
    deficiency_risks: List[str] = []
    deficiency_recommendations: List[str] = []
    detected_ingredients: List[str] = []
    possible_meals: List[Dict[str, str]] = []
    weight_forecast: float = 0.0
    health_score_forecast: float = 0.0
    nutrition: NutritionInfo = NutritionInfo(calories=0, protein=0, carbs=0, fat=0, sugar=0, sodium=0)
    health_score: float = 0.0
    health_explanation: str = ""
    recommendations: List[str] = []
    meal_plan: Dict[str, Any] = {}
    rag_answer: Dict[str, Any] = {}
    grocery_list: List[Dict[str, Any]] = []
    habit_insights: List[str] = []
    warnings: List[str] = []
    is_exceeded: bool = False
    risk_level: str = "LOW"

class WorkflowRequest(BaseModel):
    user_id: int
    input_text: Optional[str] = None
    input_image_base64: Optional[str] = None
    context: Dict[str, str] = {} # e.g., {"time_of_day": "morning", "mood": "tired"}
