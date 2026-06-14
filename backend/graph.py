from langgraph.graph import StateGraph, END  # pyrefly: ignore [missing-import]
from typing import TypedDict, Dict, Any, List
from schemas import AgentResponse
from agents.nutrition_agent import NutritionAgent
from agents.health_agent import HealthAgent
from agents.meal_agent import MealAgent
from agents.grocery_agent import GroceryAgent
from agents.habit_agent import HabitAgent
from agents.deficiency_agent import DeficiencyAgent
from agents.pantry_agent import PantryAgent
from agents.rag_agent import RAGAgent

# We will use the AgentResponse dict as our state
class WorkflowState(TypedDict):
    state: Dict[str, Any]
    user_id: int
    input_text: str
    input_image_base64: str
    context: Dict[str, str]

def nutrition_node(data: WorkflowState):
    agent = NutritionAgent()
    new_state = agent.process(data.get("input_text", "") or "", data["state"], image_base64=data.get("input_image_base64"))
    return {"state": new_state}

def rag_node(data: WorkflowState):
    agent = RAGAgent()
    food_items = data["state"].get("food_items", [])
    query = f"nutritional guidelines, values, and risks for: {', '.join(food_items)}"
    new_state = agent.process(query, data["state"])
    return {"state": new_state}

def health_node(data: WorkflowState):
    agent = HealthAgent()
    new_state = agent.process(data["state"])
    return {"state": new_state}

def habit_node(data: WorkflowState):
    agent = HabitAgent()
    new_state = agent.process(data["state"], data.get("context", {}), input_text=data.get("input_text", ""))
    return {"state": new_state}

def deficiency_node(data: WorkflowState):
    agent = DeficiencyAgent()
    new_state = agent.process(data["state"])
    return {"state": new_state}

def meal_node(data: WorkflowState):
    agent = MealAgent()
    new_state = agent.process(data["state"], data["user_id"])
    return {"state": new_state}

def grocery_node(data: WorkflowState):
    agent = GroceryAgent()
    new_state = agent.process(data["state"])
    return {"state": new_state}

def pantry_node(data: WorkflowState):
    agent = PantryAgent()
    new_state = agent.process(data["state"], data.get("input_image_base64", ""))
    return {"state": new_state}

# --- Analyze Graph (Scanner & Chat) ---
analyze_graph = StateGraph(WorkflowState)
analyze_graph.add_node("nutrition", nutrition_node)
analyze_graph.add_node("rag", rag_node)
analyze_graph.add_node("health", health_node)
analyze_graph.add_node("habit", habit_node)
analyze_graph.add_node("deficiency", deficiency_node)

analyze_graph.set_entry_point("nutrition")
analyze_graph.add_edge("nutrition", "rag")
analyze_graph.add_edge("rag", "health")
analyze_graph.add_edge("health", "habit")
analyze_graph.add_edge("habit", "deficiency")
analyze_graph.add_edge("deficiency", END)
analyze_app = analyze_graph.compile()

# --- Meal Plan Graph ---
meal_graph = StateGraph(WorkflowState)
meal_graph.add_node("meal", meal_node)
meal_graph.set_entry_point("meal")
meal_graph.add_edge("meal", END)
meal_app = meal_graph.compile()

# --- Grocery Graph ---
grocery_graph = StateGraph(WorkflowState)
grocery_graph.add_node("meal", meal_node)
grocery_graph.add_node("grocery", grocery_node)
grocery_graph.set_entry_point("meal")
grocery_graph.add_edge("meal", "grocery")
grocery_graph.add_edge("grocery", END)
grocery_app = grocery_graph.compile()

# --- Pantry Graph ---
pantry_graph = StateGraph(WorkflowState)
pantry_graph.add_node("pantry", pantry_node)
pantry_graph.set_entry_point("pantry")
pantry_graph.add_edge("pantry", END)
pantry_app = pantry_graph.compile()
