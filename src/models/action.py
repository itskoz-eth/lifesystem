from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, Enum
from sqlalchemy.orm import relationship
from . import Base, TimestampMixin
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
    status = Column(Enum(ActionStatus), default=ActionStatus.NOT_STARTED)
    goal_id = Column(Integer, ForeignKey('goals.id'))
    
    # Relationships
    goal = relationship('Goal', back_populates='actions')
    
    def __repr__(self):
        return f"<Action(name='{self.name}', status='{self.status.value}')>" 