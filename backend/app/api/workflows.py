from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from app.database import Database, db

router = APIRouter()


class WorkflowBase(BaseModel):
    """Base model for workflow data."""
    name: str
    description: Optional[str] = None


class WorkflowCreate(WorkflowBase):
    """Model for creating a workflow."""
    pass


class WorkflowRead(WorkflowBase):
    """Model for reading a workflow."""
    id: str
    status: str
    result: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


@router.get("/templates", response_model=List[dict])
async def list_workflow_templates():
    """List available workflow templates."""
    return [
        {
            "id": "document-processing",
            "name": "Document Processing",
            "description": "Extract and analyze information from documents",
            "steps": ["research", "process", "approve", "optimize"]
        },
        {
            "id": "data-analysis",
            "name": "Data Analysis",
            "description": "Analyze datasets and generate insights",
            "steps": ["research", "process", "approve", "optimize"]
        }
    ]


@router.get("/", response_model=List[WorkflowRead])
async def list_workflows():
    """List all workflows."""
    workflows = await db.fetch_all("SELECT * FROM workflows")
    return [WorkflowRead(**workflow) for workflow in workflows]


@router.get("/{workflow_id}", response_model=WorkflowRead)
async def get_workflow(workflow_id: str):
    """Get a specific workflow by ID."""
    workflow = await db.fetch_one(
        "SELECT * FROM workflows WHERE id = ?",
        (workflow_id,)
    )
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return WorkflowRead(**workflow)
