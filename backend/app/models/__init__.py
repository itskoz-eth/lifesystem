# flake8: noqa
"""
Database models for the Life System application.
"""

from sqlalchemy import create_engine, Column, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime
import os
import logging

# Top-level imports of model modules to help SQLAlchemy resolve relationships
from . import base
from . import timestamp_mixin # Ensure this is a module if Base/TimestampMixin are defined here
from . import associations
from . import value
from . import category
from . import reflection
from . import enhanced_models
from . import whiteboard_note
from . import action # Added action import

logger = logging.getLogger(__name__)

# Base for declarative models (assuming it's defined in .base or here)
# If Base is in base.py, the import above handles it.
# If TimestampMixin is in timestamp_mixin.py, the import above handles it.
Base = base.Base # Or directly declarative_base() if not in base.py
TimestampMixin = timestamp_mixin.TimestampMixin # If it's in its own file


# init_db function will be removed and its functionality moved to app/database.py and main.py
# def init_db():
#     """Initialize the database and create tables."""
#     logger.info("Starting database initialization...")
#     
#     # Import all specific model classes HERE, right before creating tables, 
#     # ensuring they are registered with Base metadata.
#     # These imports rely on the modules already being loaded by the top-level imports.
#     from .value import Value
#     from .category import Category
#     from .reflection import GoalReflection, ValueReflection
#     from .enhanced_models import Goal, Habit, HabitEntry, HabitGoal, FrequencyType, CompletionType, GoalStatus, HabitStatus, GoalCheckIn, GoalHabit
#     from .associations import goal_value # This is likely a Table object, not a class
#     from .whiteboard_note import DatedNote
#     from .action import Action, ActionStatus # Added Action

#     # Ensure data directory exists
#     logger.info("Creating data directory if it doesn't exist...")
#     os.makedirs('data', exist_ok=True) # This path might need adjustment for the backend server
#     
#     # Create database engine
#     logger.info("Creating database engine...")
#     engine = create_engine('sqlite:///data/life_system.db') # This will be handled by database.py
#     
#     # Create all tables
#     logger.info("Creating database tables...")
#     Base.metadata.create_all(engine)
#     logger.info("Database initialization complete!")
#     
#     return engine

# Expose specific models and Base directly from this package
from .value import Value
from .category import Category
from .reflection import GoalReflection, ValueReflection
from .enhanced_models import Goal, Habit, HabitEntry, HabitGoal, FrequencyType, CompletionType, GoalStatus, HabitStatus, GoalCheckIn, GoalHabit
from .associations import goal_value
from .whiteboard_note import DatedNote
from .action import Action, ActionStatus

__all__ = [
    'Base',
    'TimestampMixin',
    # 'init_db', # Removed init_db
    'Value',
    'Category',
    'GoalReflection',
    'ValueReflection',
    'Goal',
    'Habit',
    'HabitEntry',
    'HabitGoal',
    'FrequencyType',
    'CompletionType',
    'GoalStatus',
    'HabitStatus',
    'GoalCheckIn',
    'GoalHabit',
    'goal_value',
    'DatedNote',
    'Action',
    'ActionStatus'
] 