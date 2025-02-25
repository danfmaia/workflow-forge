from fastapi import APIRouter
from typing import Dict, Any
from app.database import db

router = APIRouter()


@router.get("/")
async def get_metrics() -> Dict[str, Any]:
    """Get overall system metrics."""
    # Get workflow statistics
    total_workflows = await db.fetch_val(
        "SELECT COUNT(*) FROM workflows"
    )
    successful_workflows = await db.fetch_val(
        "SELECT COUNT(*) FROM workflows WHERE status = 'completed'"
    )
    failed_workflows = await db.fetch_val(
        "SELECT COUNT(*) FROM workflows WHERE status = 'error'"
    )

    # Calculate success rate
    success_rate = (successful_workflows / total_workflows *
                    100) if total_workflows > 0 else 0

    # Get recent workflows
    recent_workflows = await db.fetch_all(
        """
        SELECT id, name, status, created_at 
        FROM workflows 
        ORDER BY created_at DESC 
        LIMIT 5
        """
    )

    return {
        "workflow_metrics": {
            "total": total_workflows,
            "successful": successful_workflows,
            "failed": failed_workflows,
            "success_rate": round(success_rate, 2)
        },
        "performance_metrics": {
            "average_execution_time": "1.5s",  # TODO: Implement actual timing
            "agent_utilization": {
                "researcher": 85,
                "processor": 90,
                "approver": 75,
                "optimizer": 60
            }
        },
        "recent_workflows": [dict(w) for w in recent_workflows] if recent_workflows else []
    }


@router.get("/agents")
async def get_agent_metrics() -> Dict[str, Any]:
    """Get agent-specific performance metrics."""
    return {
        "researcher": {
            "accuracy": 0.92,
            "average_response_time": "0.8s",
            "queries_processed": 150
        },
        "processor": {
            "throughput": "45 tasks/min",
            "error_rate": 0.03,
            "tasks_completed": 280
        },
        "approver": {
            "approval_rate": 0.85,
            "average_confidence": 0.91,
            "reviews_completed": 200
        },
        "optimizer": {
            "improvement_rate": 0.25,
            "suggestions_implemented": 45,
            "average_optimization": "20%"
        }
    }
