from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, Enum as SAEnum
from sqlalchemy.orm import relationship
from .base import Base
from .timestamp_mixin import TimestampMixin
import enum

class ActionStatus(enum.Enum):
    NOT_STARTED = 'not_started'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

class Action(Base, TimestampMixin):
    __tablename__ = 'actions'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    due_date = Column(Date)
    status = Column(SAEnum(ActionStatus), default=ActionStatus.NOT_STARTED)
    goal_id = Column(Integer, ForeignKey('goals.id'))
    
    # Relationships
    # Assuming Goal model in enhanced_models.py will have an 'actions' relationship added
    goal = relationship('Goal', back_populates='actions') 
    
    def __repr__(self):
        return f"<Action(name='{self.name}', status='{self.status.value}')>" 