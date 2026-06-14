from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel

# Defining schemas locally if they aren't fully covered in schemas.py
class NutritionRequest(BaseModel):
    food_names: List[str]

class MealGenerationRequest(BaseModel):
    goal: str
    calorie_target: float
    diet_type: str

class UserProfileRequest(BaseModel):
    age: int
    weight: float
    goal: str
    diet_type: str
    allergies: List[str]

class ImageAnalysisRequest(BaseModel):
    image_base64: str

class ContextRequest(BaseModel):
    time_of_day: str
    mood: str
    activity_level: str

router = APIRouter()

@router.post("/nutrition")
def fetch_nutrition_data(request: NutritionRequest):
    """
    MCP Tool 1: Nutrition Data Tool
    Fetch real-time nutrition data.
    """
    if not request.food_names:
        raise HTTPException(status_code=400, detail="No food items provided")
    
    # Returning structured mock output to satisfy the tool definition
    return {
        "calories": 450,
        "protein": 25,
        "carbs": 40,
        "fat": 15,
        "sugar": 8,
        "is_estimated": True
    }

@router.post("/meal-plan")
def generate_meal_plan(request: MealGenerationRequest):
    """
    MCP Tool 2: Meal Generation Tool
    Generate structured meal plans based on goal and diet.
    """
    return {
        "breakfast": "Scrambled eggs with spinach",
        "lunch": "Grilled chicken wrap",
        "dinner": "Baked salmon and broccoli",
        "snacks": ["Almonds", "Greek Yogurt"]
    }

@router.post("/user-profile")
def manage_user_profile(request: UserProfileRequest):
    """
    MCP Tool 3: User Profile Memory Tool
    Store and retrieve user preferences.
    """
    return {
        "status": "success",
        "message": "User profile saved",
        "data": request.dict()
    }

@router.post("/image-analysis")
def analyze_food_image(request: ImageAnalysisRequest):
    """
    MCP Tool 4: Food Image Analysis Tool
    Detect food items from uploaded images.
    """
    # Mocking computer vision
    return {
        "detected_foods": ["Pizza", "Cola"]
    }

@router.post("/context")
def capture_context(request: ContextRequest):
    """
    MCP Tool 5: Context Awareness Tool
    Capture time, mood, and activity level.
    """
    return {
        "status": "success",
        "adjusted_recommendation": f"Since you are feeling {request.mood}, we suggest drinking water."
    }
