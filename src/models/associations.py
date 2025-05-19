from sqlalchemy import Table, Column, Integer, ForeignKey
from .base import Base

# Association table for Goal-Value many-to-many relationship
goal_value = Table('goal_value', Base.metadata,
    Column('goal_id', Integer, ForeignKey('goals.id', ondelete='CASCADE'), primary_key=True),
    Column('value_id', Integer, ForeignKey('values.id', ondelete='CASCADE'), primary_key=True)
) 