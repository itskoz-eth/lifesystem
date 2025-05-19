from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
from .associations import goal_value

class Value(Base):
    __tablename__ = 'values'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Relationships
    goals = relationship("Goal", secondary=goal_value, back_populates="values")
    reflections = relationship("ValueReflection", back_populates="value")
    
    def __repr__(self):
        return f"<Value(name='{self.name}')>" 