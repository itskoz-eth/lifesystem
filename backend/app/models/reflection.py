from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
from .timestamp_mixin import TimestampMixin

class GoalReflection(Base):
    __tablename__ = 'goal_reflections'
    
    id = Column(Integer, primary_key=True)
    goal_id = Column(Integer, ForeignKey('goals.id', ondelete='CASCADE'))
    reflection_date = Column(DateTime, nullable=False)
    content = Column(Text, nullable=False)
    
    # Relationships
    goal = relationship("Goal", back_populates="reflections")

class ValueReflection(Base, TimestampMixin):
    __tablename__ = 'value_reflections'
    
    id = Column(Integer, primary_key=True)
    value_id = Column(Integer, ForeignKey('values.id', ondelete='CASCADE'))
    reflection_date = Column(DateTime, nullable=False)
    content = Column(Text, nullable=False)
    
    # Relationships
    value = relationship("Value", back_populates="reflections")
    
    def __repr__(self):
        return f"<ValueReflection(value_id={self.value_id}, date='{self.reflection_date}')>" 