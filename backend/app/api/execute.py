from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel

from app.workflow.orchestrator import WorkflowOrchestrator

router = APIRouter()
orchestrator = WorkflowOrchestrator()


class ExecuteRequest(BaseModel):
    """Request model for workflow execution."""
    workflow_id: str
    input_data: Dict[str, Any]


@router.post("/")
async def execute_workflow(request: ExecuteRequest):
    """Execute a workflow with the given input data."""
    try:
        result = await orchestrator.execute_workflow(
            workflow_id=request.workflow_id,
            input_data=request.input_data
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Workflow execution failed: {str(e)}"
        )


@router.post("/test")
async def test_workflow():
    """Test workflow execution with sample data."""
    test_data = {
        "workflow_id": "test-workflow",
        "input_data": {
            "query": "Analyze customer feedback trends",
            "context": "E-commerce customer reviews dataset",
            "constraints": {
                "time_period": "last_month",
                "min_confidence": 0.8
            }
        }
    }
    return await execute_workflow(ExecuteRequest(**test_data))
