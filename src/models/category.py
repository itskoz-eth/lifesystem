from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
from .timestamp_mixin import TimestampMixin

class Category(Base, TimestampMixin):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    color = Column(String, default="#CCCCCC")  # Default light gray color
    
    # Relationships
    # goals = relationship('Goal', back_populates='category') # Removed
    # values = relationship('Value', back_populates='category') # Removed
    # habits = relationship('Habit', back_populates='category') # Removed
    
    def __repr__(self):
        return f"<Category(name='{self.name}')>" 