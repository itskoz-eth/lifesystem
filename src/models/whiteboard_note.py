from sqlalchemy import Column, Integer, Text, DateTime, Date
from sqlalchemy.sql import func
from .base import Base # Assuming Base is in models/base.py or models/__init__.py
from .timestamp_mixin import TimestampMixin # Assuming TimestampMixin is available
from datetime import date # Import date

class DatedNote(Base, TimestampMixin):
    __tablename__ = 'dated_notes'

    id = Column(Integer, primary_key=True) # Standard primary key
    content = Column(Text, nullable=True) # The actual note content
    note_date = Column(Date, nullable=False) # Date for the note

    # created_at and updated_at are inherited from TimestampMixin

    def __repr__(self):
        return f"<DatedNote(id={self.id}, date='{self.note_date}', updated_at='{self.updated_at}')>" 