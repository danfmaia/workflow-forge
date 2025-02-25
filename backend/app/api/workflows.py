"""API endpoints for workflow management."""

from fastapi import APIRouter, HTTPException
from app.database import get_db
from app.schemas.workflow import WorkflowList, WorkflowDetail
import json
from typing import List, Dict, Any

router = APIRouter()


@router.get("/", response_model=List[WorkflowList])
async def list_workflows():
    """List all workflows."""
    async with get_db() as db:
        workflows = await db.fetch_all("SELECT * FROM workflows")
        return [
            {
                "id": workflow["id"],
                "name": workflow["name"],
                "description": workflow["description"],
                "status": workflow["status"],
                "created_at": workflow["created_at"],
                "updated_at": workflow["updated_at"]
            }
            for workflow in workflows
        ]


@router.get("/templates", response_model=List[Dict[str, Any]])
async def list_workflow_templates():
    """List all available workflow templates."""
    # Return a list of predefined workflow templates
    return [
        {
            "id": "data-analysis",
            "name": "Data Analysis Workflow",
            "description": "Analyze data sets and generate insights",
            "steps": [
                {"name": "Research", "agent": "Researcher",
                    "description": "Gather relevant data"},
                {"name": "Process", "agent": "Processor",
                    "description": "Process and analyze data"},
                {"name": "Approve", "agent": "Approver",
                    "description": "Validate analysis results"},
                {"name": "Optimize", "agent": "Optimizer",
                    "description": "Suggest improvements"}
            ]
        },
        {
            "id": "content-generation",
            "name": "Content Generation Workflow",
            "description": "Generate and optimize content based on requirements",
            "steps": [
                {"name": "Research", "agent": "Researcher",
                    "description": "Research topic and gather information"},
                {"name": "Process", "agent": "Processor",
                    "description": "Generate initial content draft"},
                {"name": "Approve", "agent": "Approver",
                    "description": "Review and approve content"},
                {"name": "Optimize", "agent": "Optimizer",
                    "description": "Optimize content for engagement"}
            ]
        },
        {
            "id": "customer-support",
            "name": "Customer Support Workflow",
            "description": "Handle customer inquiries and support tickets",
            "steps": [
                {"name": "Research", "agent": "Researcher",
                    "description": "Research customer history and issue"},
                {"name": "Process", "agent": "Processor",
                    "description": "Generate response or solution"},
                {"name": "Approve", "agent": "Approver",
                    "description": "Review and approve response"},
                {"name": "Optimize", "agent": "Optimizer",
                    "description": "Suggest improvements to process"}
            ]
        }
    ]


@router.get("/{workflow_id}", response_model=WorkflowDetail)
async def get_workflow(workflow_id: str):
    """Get a specific workflow by ID."""
    async with get_db() as db:
        workflow = await db.fetch_one(
            "SELECT * FROM workflows WHERE id = ?",
            (workflow_id,)
        )

        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")

        # Parse the result JSON if it exists
        result = None
        if workflow.get("result"):
            try:
                result = json.loads(workflow["result"])
            except json.JSONDecodeError:
                result = {"data": workflow["result"]}

        return {
            "id": workflow["id"],
            "name": workflow["name"],
            "description": workflow["description"],
            "status": workflow["status"],
            "result": result,
            "error": workflow.get("error"),
            "created_at": workflow["created_at"],
            "updated_at": workflow["updated_at"]
        }


@router.delete("/{workflow_id}", status_code=204)
async def delete_workflow(workflow_id: str):
    """Delete a workflow by ID."""
    async with get_db() as db:
        # Check if workflow exists
        workflow = await db.fetch_one(
            "SELECT id FROM workflows WHERE id = ?",
            (workflow_id,)
        )

        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")

        # Delete the workflow
        await db.execute(
            "DELETE FROM workflows WHERE id = ?",
            (workflow_id,)
        )

        return None
