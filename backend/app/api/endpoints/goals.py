from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app import schemas
from app import crud
from app.database import get_db # Corrected import for get_db

router = APIRouter()

@router.post("/", response_model=schemas.Goal, status_code=status.HTTP_201_CREATED)
def create_goal(goal: schemas.GoalCreate, db: Session = Depends(get_db)):
    # Optional: Check if parent_id exists if provided
    # if goal.parent_id:
    #     parent_goal = crud.crud_goal.get_goal(db, goal_id=goal.parent_id)
    #     if not parent_goal:
    #         raise HTTPException(status_code=404, detail=f"Parent goal with id {goal.parent_id} not found")
    return crud.crud_goal.create_goal(db=db, goal=goal)

@router.get("/{goal_id}", response_model=schemas.Goal)
def read_goal(goal_id: int, db: Session = Depends(get_db)):
    db_goal = crud.crud_goal.get_goal(db, goal_id=goal_id)
    if db_goal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return db_goal

@router.get("/", response_model=List[schemas.Goal])
def read_goals(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    goals = crud.crud_goal.get_goals(db, skip=skip, limit=limit)
    return goals

@router.put("/{goal_id}", response_model=schemas.Goal)
def update_goal(
    goal_id: int, goal: schemas.GoalUpdate, db: Session = Depends(get_db)
):
    db_goal = crud.crud_goal.get_goal(db, goal_id=goal_id) # Check if goal exists
    if db_goal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    # Optional: Check if new parent_id exists if provided
    # if goal.parent_id:
    #     parent_goal = crud.crud_goal.get_goal(db, goal_id=goal.parent_id)
    #     if not parent_goal:
    #         raise HTTPException(status_code=404, detail=f"New parent goal with id {goal.parent_id} not found")
    updated_goal = crud.crud_goal.update_goal(db=db, goal_id=goal_id, goal_update=goal)
    return updated_goal

@router.delete("/{goal_id}", response_model=schemas.Goal)
def delete_goal(goal_id: int, db: Session = Depends(get_db)):
    db_goal = crud.crud_goal.get_goal(db, goal_id=goal_id) # Check if goal exists
    if db_goal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    deleted_goal = crud.crud_goal.delete_goal(db=db, goal_id=goal_id)
    return deleted_goal 