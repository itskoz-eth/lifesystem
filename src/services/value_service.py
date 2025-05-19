from sqlalchemy.orm import Session, sessionmaker, joinedload
from typing import List, Optional
from ..models.value import Value
from ..models.category import Category # For potential future use if needed
import logging

logger = logging.getLogger(__name__)

class ValueService:
    def __init__(self, engine):
        """Initializes the service with an SQLAlchemy engine."""
        self.engine = engine
        self.Session = sessionmaker(bind=engine)

    def get_all_values(self) -> List[Value]:
        """Retrieves all values."""
        with self.Session() as session:
            try:
                values = session.query(Value).order_by(Value.name).all()
                return values
            except Exception as e:
                logger.error(f"Error fetching all values: {e}")
                return []

    def get_value(self, value_id: int) -> Optional[Value]:
        """Get a single value by its ID."""
        with self.Session() as session:
            try:
                return session.query(Value).filter(Value.id == value_id).first()
            except Exception as e:
                logger.error(f"Error fetching value with id {value_id}: {e}")
                return None

    # Basic CRUD operations (can be expanded from ValuesView logic if ValuesView is refactored to use this service)
    def create_value(self, name: str, description: Optional[str] = None) -> Optional[Value]:
        with self.Session() as session:
            try:
                new_value = Value(name=name, description=description)
                session.add(new_value)
                session.commit()
                session.refresh(new_value)
                return new_value
            except Exception as e:
                logger.error(f"Error creating value: {e}")
                session.rollback()
                return None

    def update_value(self, value_id: int, name: Optional[str] = None, description: Optional[str] = None) -> Optional[Value]:
        with self.Session() as session:
            try:
                value = session.query(Value).filter(Value.id == value_id).first()
                if not value:
                    return None
                if name is not None:
                    value.name = name
                if description is not None:
                    value.description = description
                session.commit()
                session.refresh(value)
                return value
            except Exception as e:
                logger.error(f"Error updating value {value_id}: {e}")
                session.rollback()
                return None

    def delete_value(self, value_id: int) -> bool:
        with self.Session() as session:
            try:
                value = session.query(Value).filter(Value.id == value_id).first()
                if value:
                    session.delete(value)
                    session.commit()
                    return True
                return False
            except Exception as e:
                logger.error(f"Error deleting value {value_id}: {e}")
                session.rollback()
                return False

    def get_all_categories(self) -> List[Category]:
        """Retrieves all categories."""
        with self.Session() as session:
            try:
                categories = session.query(Category).order_by(Category.name).all()
                return categories
            except Exception as e:
                logger.error(f"Error fetching all categories: {e}")
                return [] 