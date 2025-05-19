from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Float, Enum as SQLAlchemyEnum, Table
from sqlalchemy.orm import relationship, backref
from datetime import datetime
import enum
from .base import Base
from .associations import goal_value # Import the association table
# from .reflection import GoalReflection # Removing this, should be resolved by top-level package imports

# Define Enums needed by Habit model
class FrequencyType(enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    SPECIFIC_DAYS = "specific_days"

class CompletionType(enum.Enum):
    BINARY = "binary"  # Simple yes/no completion
    QUANTITATIVE = "quantitative"  # E.g., run 5 km, read 20 pages
    DURATION = "duration"  # E.g., meditate for 10 minutes

class GoalStatus(enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"

class HabitStatus(enum.Enum): # New Enum for Habit status
    ACTIVE = "active"
    INACTIVE = "inactive"

# Association Table for GoalCheckIn and Habit
goal_check_in_habits_table = Table('goal_check_in_habits',
    Base.metadata,
    Column('goal_check_in_id', Integer, ForeignKey('goal_check_ins.id'), primary_key=True),
    Column('habit_id', Integer, ForeignKey('habits.id'), primary_key=True)
)

class Goal(Base):
    __tablename__ = 'goals'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    target_date = Column(DateTime)
    status = Column(SQLAlchemyEnum(GoalStatus), default=GoalStatus.NOT_STARTED)
    parent_id = Column(Integer, ForeignKey('goals.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent_goal = relationship("Goal", remote_side=[id], back_populates="sub_goals")
    sub_goals = relationship("Goal", back_populates="parent_goal", cascade="all, delete-orphan")
    check_ins = relationship("GoalCheckIn", back_populates="goal", cascade="all, delete-orphan")
    supporting_habits = relationship("Habit", secondary="goal_habits", back_populates="supporting_goals", overlaps="goal, habit")
    values = relationship("Value", secondary=goal_value, back_populates="goals")
    reflections = relationship("GoalReflection", back_populates="goal", cascade="all, delete-orphan")

class GoalCheckIn(Base):
    __tablename__ = 'goal_check_ins'
    
    id = Column(Integer, primary_key=True)
    goal_id = Column(Integer, ForeignKey('goals.id'), nullable=False)
    check_in_date = Column(DateTime, default=datetime.utcnow)
    reflection = Column(String(1000))
    progress_percentage = Column(Float)
    notes = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    goal = relationship("Goal", back_populates="check_ins")
    contributing_habits = relationship("Habit", secondary=goal_check_in_habits_table, back_populates="check_ins_contributed_to")

class GoalHabit(Base):
    __tablename__ = 'goal_habits'
    
    id = Column(Integer, primary_key=True)
    goal_id = Column(Integer, ForeignKey('goals.id'), nullable=False)
    habit_id = Column(Integer, ForeignKey('habits.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    goal = relationship("Goal", overlaps="supporting_habits")
    habit = relationship("Habit", overlaps="supporting_habits")

# Define HabitEntry and HabitGoal models here as well
class HabitEntry(Base):
    __tablename__ = 'habit_entries'

    id = Column(Integer, primary_key=True)
    habit_id = Column(Integer, ForeignKey('habits.id'), nullable=False)
    completion_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed = Column(Boolean, default=False) # Use 'completed' consistently
    value = Column(Float) # Actual value for quantitative/duration types
    notes = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    habit = relationship("Habit", back_populates="entries")

class HabitGoal(Base):
    __tablename__ = 'habit_goals' # Links habits to long-term habit-specific goals/targets

    id = Column(Integer, primary_key=True)
    habit_id = Column(Integer, ForeignKey('habits.id'), nullable=False)
    goal_description = Column(String(255))
    target_date = Column(DateTime)
    target_value = Column(Float) # E.g., achieve a streak of 30 days, run a total of 100km
    current_value = Column(Float, default=0)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    habit = relationship("Habit", back_populates="goals")

# Update Habit model to include relationship with goals
class Habit(Base):
    __tablename__ = 'habits'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    frequency = Column(SQLAlchemyEnum(FrequencyType), nullable=False)
    specific_days_of_week = Column(String(20), nullable=True)  # e.g., "0,1,2,3,4,5,6" for Mon-Sun
    completion_type = Column(SQLAlchemyEnum(CompletionType), nullable=False)
    target_value = Column(Float)
    unit = Column(String(50))
    status = Column(SQLAlchemyEnum(HabitStatus), default=HabitStatus.ACTIVE) # New status field
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    entries = relationship("HabitEntry", back_populates="habit", cascade="all, delete-orphan")
    goals = relationship("HabitGoal", back_populates="habit", cascade="all, delete-orphan")
    supporting_goals = relationship("Goal", secondary="goal_habits", back_populates="supporting_habits", overlaps="goal, habit")
    check_ins_contributed_to = relationship("GoalCheckIn", secondary=goal_check_in_habits_table, back_populates="contributing_habits")

    def __repr__(self):
        return f"<Habit(name='{self.name}', status='{self.status.value}')>" 