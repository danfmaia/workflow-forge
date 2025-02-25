"""API endpoints for system metrics."""

from fastapi import APIRouter, HTTPException
from app.database import get_db
import psutil
from datetime import datetime
import logging
from typing import Dict, Any

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/")
async def get_metrics():
    """Get system metrics and workflow statistics."""
    try:
        async with get_db() as db:
            # Get workflow execution metrics
            total_executions = await db.fetch_val(
                "SELECT COUNT(*) FROM workflows"
            ) or 0

            # Get completed workflows
            completed = await db.fetch_val(
                "SELECT COUNT(*) FROM workflows WHERE status = 'completed'"
            ) or 0

            # Get failed workflows
            failed = await db.fetch_val(
                "SELECT COUNT(*) FROM workflows WHERE status = 'error'"
            ) or 0

            # Get system metrics
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=0.1)
            disk = psutil.disk_usage('/')

            return {
                "workflow_metrics": {
                    "total_executions": total_executions,
                    "completed": completed,
                    "failed": failed,
                    "success_rate": (completed / total_executions * 100) if total_executions > 0 else 0
                },
                "system_metrics": {
                    "memory_usage_percent": memory.percent,
                    "cpu_usage_percent": cpu_percent,
                    "disk_usage_percent": disk.percent,
                    "timestamp": datetime.now().isoformat()
                }
            }
    except Exception as e:
        logger.error(f"Error retrieving metrics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve metrics: {str(e)}"
        )


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
