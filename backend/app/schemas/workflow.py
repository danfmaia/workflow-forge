"""Pydantic models for workflow data validation."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime


class WorkflowBase(BaseModel):
    name: str
    description: Optional[str] = None
    config: Dict[str, Any]
    is_active: bool = True


class WorkflowCreate(BaseModel):
    """Model for creating a new workflow."""
    name: str
    description: str
    input_data: Dict[str, Any]


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
    """Model for listing workflows."""
    id: str
    name: str
    description: str
    status: str
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class WorkflowResponse(BaseModel):
    """Response model for workflow execution."""
    workflow_id: str
    name: str
    description: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    history: List[Dict[str, Any]] = []


class WorkflowDetail(BaseModel):
    """Detailed workflow model."""
    id: str
    name: str
    description: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class WorkflowTemplate(BaseModel):
    """Model for workflow templates."""
    id: str
    name: str
    description: str
    steps: List[str]
