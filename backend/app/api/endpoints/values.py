from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app import schemas
from app import crud # This will now give access to crud.crud_value
from app.database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Value, status_code=status.HTTP_201_CREATED)
def create_value(value: schemas.ValueCreate, db: Session = Depends(get_db)):
    return crud.crud_value.create_value(db=db, value=value)

@router.get("/{value_id}", response_model=schemas.Value)
def read_value(value_id: int, db: Session = Depends(get_db)):
    db_value = crud.crud_value.get_value(db, value_id=value_id)
    if db_value is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Value not found")
    return db_value

@router.get("/", response_model=List[schemas.Value])
def read_values(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    values = crud.crud_value.get_values(db, skip=skip, limit=limit)
    return values

@router.put("/{value_id}", response_model=schemas.Value)
def update_value(
    value_id: int, value: schemas.ValueUpdate, db: Session = Depends(get_db)
):
    db_value = crud.crud_value.get_value(db, value_id=value_id)
    if db_value is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Value not found")
    updated_value = crud.crud_value.update_value(db=db, value_id=value_id, value_update=value)
    return updated_value

@router.delete("/{value_id}", response_model=schemas.Value)
def delete_value(value_id: int, db: Session = Depends(get_db)):
    db_value = crud.crud_value.get_value(db, value_id=value_id)
    if db_value is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Value not found")
    deleted_value = crud.crud_value.delete_value(db=db, value_id=value_id)
    return deleted_value 