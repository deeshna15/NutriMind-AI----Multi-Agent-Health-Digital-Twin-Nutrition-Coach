from fastapi import FastAPI  # pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware  # pyrefly: ignore [missing-import]
import os
from dotenv import load_dotenv  # pyrefly: ignore [missing-import]

load_dotenv()

try:
    from .database import engine, Base, SessionLocal
    from .models import UserProfile, FoodHistory, HealthScore
    from .api import tools_router, workflow_router, graph_router, voice_router
except ImportError:
    from database import engine, Base, SessionLocal  # pyrefly: ignore [missing-import]
    from models import UserProfile, FoodHistory, HealthScore  # pyrefly: ignore [missing-import]
    from api import tools_router, workflow_router, graph_router, voice_router  # pyrefly: ignore [missing-import]

# Recreate DB tables on startup for development schema migration
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="NutriMind AI API")

@app.on_event("startup")
def seed_database():
    db = SessionLocal()
    user = db.query(UserProfile).filter(UserProfile.id == 1).first()
    if not user:
        new_user = UserProfile(
            name="Demo User",
            age=25,
            weight=70.5,
            height=175.0,
            activity_level="Moderately Active",
            goal="weight loss",
            diet_type="veg",
            allergies=["Peanuts"],
            memory_blob={"favorite_foods": ["Pizza", "Ice Cream"], "weekly_patterns": ["Friday junk food cravings"], "budget": "medium"}
        )
        db.add(new_user)
        db.commit()
    db.close()

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tools_router.router, prefix="/api/tools", tags=["MCP Tools"])
app.include_router(workflow_router.router, prefix="/api/workflow", tags=["Workflow"])
app.include_router(graph_router.router, prefix="/api/graph", tags=["Knowledge Graph"])
app.include_router(voice_router.router, prefix="/api/voice", tags=["Voice Assistant"])

@app.get("/")
def read_root():
    return {"message": "Welcome to NutriMind AI"}
