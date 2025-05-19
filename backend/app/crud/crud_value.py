from sqlalchemy.orm import Session
from typing import List, Optional

from app import models
from app import schemas

def get_value(db: Session, value_id: int) -> Optional[models.Value]:
    return db.query(models.Value).filter(models.Value.id == value_id).first()

def get_values(
    db: Session, skip: int = 0, limit: int = 100
) -> List[models.Value]:
    return db.query(models.Value).offset(skip).limit(limit).all()

def create_value(db: Session, value: schemas.ValueCreate) -> models.Value:
    db_value = models.Value(
        name=value.name,
        description=value.description
    )
    db.add(db_value)
    db.commit()
    db.refresh(db_value)
    return db_value

def update_value(
    db: Session, value_id: int, value_update: schemas.ValueUpdate
) -> Optional[models.Value]:
    db_value = get_value(db, value_id=value_id)
    if not db_value:
        return None

    update_data = value_update.model_dump(exclude_unset=True)
    for key, val in update_data.items(): # Changed 'value' to 'val' to avoid conflict
        setattr(db_value, key, val)
    
    db.add(db_value)
    db.commit()
    db.refresh(db_value)
    return db_value

def delete_value(db: Session, value_id: int) -> Optional[models.Value]:
    db_value = get_value(db, value_id=value_id)
    if not db_value:
        return None
    db.delete(db_value)
    db.commit()
    return db_value 