from fastapi import FastAPI

# Import Base and engine from the app.database module
# Base will be used by the engine to create tables
from app.database import engine
# Although Base is initialized within app.models and used by app.database,
# it needs to be known here if we were to directly reference models.models.Base.metadata for create_all
# However, we can just import the models module to ensure all models are loaded 
# before create_all is called via the engine that already knows about Base.
from app import models # Ensures models are loaded
from app.api.endpoints import goals, values # Import the values router

# Create database tables if they don't exist
# This uses the Base imported and used within app.database and app.models
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Life System API",
    description="API for managing goals, habits, values, and reflections.",
    version="0.1.0"
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Life System API"}

# Include API routers
app.include_router(goals.router, prefix="/api/v1/goals", tags=["Goals"])
app.include_router(values.router, prefix="/api/v1/values", tags=["Values"])

# Future API routers will be included here
# e.g., from app.api.endpoints import habits
# app.include_router(habits.router, prefix="/api/v1/habits", tags=["Habits"]) 