from pydantic import BaseModel
from typing import Optional
from datetime import datetime # Although not directly used in Value, good practice for schema files

# Properties to receive via API on creation
class ValueBase(BaseModel):
    name: str
    description: Optional[str] = None

# Properties to receive via API on creation
class ValueCreate(ValueBase):
    pass

# Properties to receive via API on update
class ValueUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

# Properties shared by models stored in DB
class ValueInDBBase(ValueBase):
    id: int
    # Assuming Value model might not have created_at/updated_at directly
    # If it inherits TimestampMixin, these would be present
    # created_at: datetime 
    # updated_at: datetime

    class Config:
        from_attributes = True

# Additional properties to return to client
class Value(ValueInDBBase):
    pass 