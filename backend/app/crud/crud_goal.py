from sqlalchemy.orm import Session
from typing import List, Optional

from app import models
from app import schemas


def get_goal(db: Session, goal_id: int) -> Optional[models.Goal]:
    return db.query(models.Goal).filter(models.Goal.id == goal_id).first()

def get_goals(
    db: Session, skip: int = 0, limit: int = 100
) -> List[models.Goal]:
    return db.query(models.Goal).offset(skip).limit(limit).all()

def create_goal(db: Session, goal: schemas.GoalCreate) -> models.Goal:
    db_goal = models.Goal(
        name=goal.name,
        description=goal.description,
        target_date=goal.target_date,
        status=goal.status,
        parent_id=goal.parent_id
    )
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal

def update_goal(
    db: Session, goal_id: int, goal_update: schemas.GoalUpdate
) -> Optional[models.Goal]:
    db_goal = get_goal(db, goal_id=goal_id)
    if not db_goal:
        return None

    update_data = goal_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_goal, key, value)
    
    db.add(db_goal) # or db.merge(db_goal) if you prefer
    db.commit()
    db.refresh(db_goal)
    return db_goal

def delete_goal(db: Session, goal_id: int) -> Optional[models.Goal]:
    db_goal = get_goal(db, goal_id=goal_id)
    if not db_goal:
        return None
    db.delete(db_goal)
    db.commit()
    return db_goal 