from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from schemas import WorkflowRequest, AgentResponse
from graph import analyze_app, meal_app, grocery_app, pantry_app
from agents.prediction_agent import PredictionAgent
from database import SessionLocal
from models import FoodHistory, HealthScore
from datetime import datetime, date

router = APIRouter()

@router.post("/analyze", response_model=AgentResponse)
async def analyze_food(request: WorkflowRequest):
    """Analyze food from text or image using LangGraph."""
    state = AgentResponse().dict()
    food_text = request.input_text
    image_base64 = request.input_image_base64

    if not food_text and not image_base64:
        return state

    inputs = {
        "state": state,
        "user_id": request.user_id,
        "input_text": food_text,
        "input_image_base64": image_base64,
        "context": request.context
    }
    
    # Run the LangGraph state machine
    result = analyze_app.invoke(inputs)
    final_state = result["state"]

    # Save to Database
    db = SessionLocal()
    try:
        nutrition = final_state.get("nutrition", {})
        food_history = FoodHistory(
            user_id=request.user_id,
            food_items=final_state.get("food_items", []),
            calories=float(nutrition.get("calories", 0.0)),
            protein=float(nutrition.get("protein", 0.0)),
            carbs=float(nutrition.get("carbs", 0.0)),
            fat=float(nutrition.get("fat", 0.0)),
            sugar=float(nutrition.get("sugar", 0.0)),
            sodium=float(nutrition.get("sodium", 0.0))
        )
        db.add(food_history)
        
        health_score_val = final_state.get("health_score", 0)
        if health_score_val > 0:
            health_score_record = HealthScore(
                user_id=request.user_id,
                score=health_score_val,
                reason="Scanned Meal: " + ", ".join(final_state.get("food_items", []))
            )
            db.add(health_score_record)
            
        db.commit()
    except Exception as e:
        print(f"Error saving to DB: {e}")
        db.rollback()
    finally:
        db.close()

    return final_state

@router.post("/meals", response_model=AgentResponse)
async def generate_meals(request: WorkflowRequest):
    """Generate a dynamic 1-day meal plan using LangGraph."""
    state = AgentResponse().dict()
    inputs = {
        "state": state,
        "user_id": request.user_id,
        "input_text": request.input_text,
        "input_image_base64": None,
        "context": request.context
    }
    result = meal_app.invoke(inputs)
    return result["state"]

@router.post("/grocery", response_model=AgentResponse)
async def generate_grocery(request: WorkflowRequest):
    """Generate a meal plan and parse it into a grocery list using LangGraph."""
    state = AgentResponse().dict()
    inputs = {
        "state": state,
        "user_id": request.user_id,
        "input_text": request.input_text,
        "input_image_base64": None,
        "context": request.context
    }
    result = grocery_app.invoke(inputs)
    return result["state"]

@router.post("/pantry", response_model=AgentResponse)
async def analyze_pantry(request: WorkflowRequest):
    """Use Pantry Vision AI to generate recipes."""
    state = AgentResponse().dict()
    inputs = {
        "state": state,
        "user_id": request.user_id,
        "input_text": "",
        "input_image_base64": request.input_image_base64,
        "context": request.context
    }
    result = pantry_app.invoke(inputs)
    return result["state"]

@router.get("/daily-history")
async def get_daily_history(user_id: int = 1, date_str: Optional[str] = None):
    """Retrieve food items and accumulated stats for a specific day."""
    db = SessionLocal()
    try:
        query_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Expected YYYY-MM-DD")
        
    try:
        foods = db.query(FoodHistory).filter(FoodHistory.user_id == user_id).all()
        day_foods = [f for f in foods if f.timestamp.date() == query_date]
        
        result_meals = []
        for f in day_foods:
            # Check thresholds for each meal to determine warnings
            warnings = []
            if f.calories > 800:
                warnings.append("High Calories")
            if f.sugar > 15:
                warnings.append("High Sugar")
            if f.sodium > 1000:
                warnings.append("High Sodium")
                
            result_meals.append({
                "id": f.id,
                "food_items": f.food_items,
                "calories": f.calories,
                "protein": f.protein,
                "carbs": f.carbs,
                "fat": f.fat,
                "sugar": f.sugar,
                "sodium": f.sodium,
                "timestamp": f.timestamp.isoformat(),
                "warnings": warnings
            })
        return result_meals
    finally:
        db.close()

@router.get("/dashboard")
async def get_dashboard(date_str: Optional[str] = None):
    # Use PredictionAgent for Digital Twin Forecasting
    agent = PredictionAgent()
    state = agent.process({})

    db = SessionLocal()
    user_id = 1 # Seeded demo user
    
    try:
        query_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()
    except ValueError:
        query_date = date.today()
        
    # Query food history for user
    foods = db.query(FoodHistory).filter(FoodHistory.user_id == user_id).all()
    # Filter in python by target date
    day_foods = [f for f in foods if f.timestamp.date() == query_date]
    
    total_cals = sum(f.calories for f in day_foods) if day_foods else 0.0
    total_protein = sum(f.protein for f in day_foods) if day_foods else 0.0
    total_carbs = sum(f.carbs for f in day_foods) if day_foods else 0.0
    total_fat = sum(f.fat for f in day_foods) if day_foods else 0.0
    total_sugar = sum(f.sugar for f in day_foods) if day_foods else 0.0
    total_sodium = sum(f.sodium for f in day_foods) if day_foods else 0.0
    
    # Calculate Warnings & Risk Level for today
    warnings = []
    exceeded_count = 0
    
    # Track which meals caused which warnings
    meals_today_list = []
    for f in day_foods:
        meal_warnings = []
        if f.calories > 800:
            meal_warnings.append(f"Calorie threshold exceeded ({f.calories:.0f} kcal > 800 kcal)")
            exceeded_count += 1
        if f.sugar > 15:
            meal_warnings.append(f"Sugar threshold exceeded ({f.sugar:.0f}g > 15g)")
            exceeded_count += 1
        if f.sodium > 1000:
            meal_warnings.append(f"Sodium threshold exceeded ({f.sodium:.0f}mg > 1000mg)")
            exceeded_count += 1
            
        warnings.extend(meal_warnings)
        
        meals_today_list.append({
            "food_items": f.food_items,
            "calories": f.calories,
            "protein": f.protein,
            "carbs": f.carbs,
            "fat": f.fat,
            "sugar": f.sugar,
            "sodium": f.sodium,
            "timestamp": f.timestamp.strftime("%I:%M %p"),
            "warnings": meal_warnings
        })

    # Unique warnings list
    unique_warnings = list(set(warnings))
    
    if exceeded_count == 0:
        risk_level = "LOW"
    elif exceeded_count <= 2:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    # Get latest score for today or general
    latest_score = db.query(HealthScore).filter(HealthScore.user_id == user_id).order_by(HealthScore.timestamp.desc()).first()
    score = latest_score.score if latest_score else 85
    
    db.close()

    insight_msg = "Dynamic Data Connected! Keep scanning foods to see this change."
    if risk_level == "HIGH":
        insight_msg = "⚠️ High risk alerts active today! Try searching your pantry for balancing meals."
    elif risk_level == "MEDIUM":
        insight_msg = "⚠️ Moderation advised. Keep an eye on sugar/sodium levels."

    return {
        "healthScore": score,
        "streak": 12,
        "macroData": [
            { "name": "Protein", "value": total_protein, "fill": "#3b82f6" },
            { "name": "Carbs", "value": total_carbs, "fill": "#f59e0b" },
            { "name": "Fat", "value": total_fat, "fill": "#ef4444" },
            { "name": "Sugar", "value": total_sugar, "fill": "#ec4899" }
        ],
        "weeklyTrends": [
            { "day": "Mon", "score": 70 },
            { "day": "Tue", "score": 72 },
            { "day": "Wed", "score": 75 },
            { "day": "Thu", "score": 74 },
            { "day": "Fri", "score": 80 },
            { "day": "Sat", "score": 82 },
            { "day": "Sun", "score": score }
        ],
        "calories": total_cals,
        "sugar": total_sugar,
        "sodium": total_sodium,
        "insight": insight_msg,
        "weightForecast": state.get("weight_forecast", []),
        "healthScoreForecast": state.get("health_score_forecast", []),
        "riskLevel": risk_level,
        "warnings": unique_warnings,
        "mealsToday": meals_today_list
    }
