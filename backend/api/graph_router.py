from fastapi import APIRouter

router = APIRouter()

@router.get("/recommendation-graph")
async def get_recommendation_graph():
    """
    Returns the user's data as a semantic Knowledge Graph for UI rendering.
    User -> Goal -> Meals -> Nutrients -> Deficiencies
    """
    graph_data = {
        "nodes": [
            {"id": "User", "label": "User (ID: 1)", "group": "person"},
            {"id": "Goal", "label": "Weight Loss", "group": "goal"},
            {"id": "Breakfast", "label": "Oatmeal", "group": "meal"},
            {"id": "Lunch", "label": "Quinoa Salad", "group": "meal"},
            {"id": "Dinner", "label": "Lentil Soup", "group": "meal"},
            {"id": "Nutrient_Protein", "label": "Protein (High)", "group": "nutrient"},
            {"id": "Deficiency_Iron", "label": "Low Iron Risk", "group": "deficiency"},
            {"id": "Recommendation", "label": "Eat Spinach", "group": "recommendation"}
        ],
        "links": [
            {"source": "User", "target": "Goal"},
            {"source": "Goal", "target": "Breakfast"},
            {"source": "Goal", "target": "Lunch"},
            {"source": "Goal", "target": "Dinner"},
            {"source": "Lunch", "target": "Nutrient_Protein"},
            {"source": "User", "target": "Deficiency_Iron"},
            {"source": "Deficiency_Iron", "target": "Recommendation"}
        ]
    }
    
    return graph_data
