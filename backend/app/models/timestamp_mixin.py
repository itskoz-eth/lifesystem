from sqlalchemy import Column, DateTime
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime

class TimestampMixin:
    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=datetime.utcnow)
    
    @declared_attr
    def updated_at(cls):
        return Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 