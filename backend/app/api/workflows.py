"""API endpoints for workflow management."""

from fastapi import APIRouter, HTTPException
from app.database import get_db
from app.schemas.workflow import WorkflowList, WorkflowDetail
import json
from typing import List

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
