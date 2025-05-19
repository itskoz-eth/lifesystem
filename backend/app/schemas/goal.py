from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Import the Enum from SQLAlchemy models
from app.models.enhanced_models import GoalStatus

# Properties to receive via API on creation
class GoalBase(BaseModel):
    name: str
    description: Optional[str] = None
    target_date: Optional[datetime] = None
    status: Optional[GoalStatus] = GoalStatus.NOT_STARTED
    parent_id: Optional[int] = None

# Properties to receive via API on creation
class GoalCreate(GoalBase):
    pass

# Properties to receive via API on update
class GoalUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_date: Optional[datetime] = None
    status: Optional[GoalStatus] = None
    parent_id: Optional[int] = None # Allow updating parent_id, or removing it (setting to None)

# Properties shared by models stored in DB
class GoalInDBBase(GoalBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True # Replaces orm_mode = True in Pydantic v2

# Additional properties to return to client
class Goal(GoalInDBBase):
    # We can add relationships here later if needed, e.g.:
    # sub_goals: List['Goal'] = [] # Forward reference for self-referencing model
    # values: List[Value] = [] # Assuming a Value schema exists
    pass

# If using forward references for self-referencing (like sub_goals)
# or circular dependencies, update_forward_refs() might be needed at the end of the file.
# For Pydantic v2, it's often handled automatically or by type adapter annotations.
# Goal.model_rebuild() # Pydantic v2 way to rebuild model if forward refs were used 