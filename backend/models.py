from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey  # pyrefly: ignore [missing-import]

from sqlalchemy.sql import func  # pyrefly: ignore [missing-import]
try:
    from .database import Base
except ImportError:
    from database import Base  # pyrefly: ignore [missing-import]

class UserProfile(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)
    weight = Column(Float)
    height = Column(Float) # in cm
    activity_level = Column(String) # Sedentary, Lightly Active, Moderately Active, Very Active
    goal = Column(String) # weight loss, maintenance, weight gain
    diet_type = Column(String) # veg, non-veg, keto, etc.
    allergies = Column(JSON) # list of allergies
    current_streak = Column(Integer, default=0)
    highest_streak = Column(Integer, default=0)
    memory_blob = Column(JSON, default={"favorite_foods": [], "weekly_patterns": [], "budget": "medium"}) # Agent Memory

class FoodHistory(Base):
    __tablename__ = "food_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    food_items = Column(JSON) # list of foods
    calories = Column(Float)
    protein = Column(Float)
    carbs = Column(Float)
    fat = Column(Float)
    sugar = Column(Float)
    sodium = Column(Float, default=0.0)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class HealthScore(Base):
    __tablename__ = "health_scores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    score = Column(Float)
    reason = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
