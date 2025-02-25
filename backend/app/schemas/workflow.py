from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime


class WorkflowBase(BaseModel):
    name: str
    description: Optional[str] = None
    config: Dict[str, Any]
    is_active: bool = True


class WorkflowCreate(WorkflowBase):
    pass


class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class WorkflowInDB(WorkflowBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Workflow(WorkflowInDB):
    pass


class WorkflowExecutionBase(BaseModel):
    workflow_id: int
    input_data: Dict[str, Any]


class WorkflowExecutionCreate(WorkflowExecutionBase):
    pass


class WorkflowExecutionUpdate(BaseModel):
    output_data: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class WorkflowExecutionInDB(WorkflowExecutionBase):
    id: int
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

    class Config:
        orm_mode = True


class WorkflowExecution(WorkflowExecutionInDB):
    pass


class WorkflowList(BaseModel):
    workflows: List[Workflow]
    count: int
