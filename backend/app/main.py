from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uuid
import json
import psutil
from contextlib import asynccontextmanager

from app.api import workflows, agents, execute, metrics
from app.database import init_db, get_db
from app.workflow.orchestrator import WorkflowOrchestrator


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for FastAPI app."""
    # Initialize database on startup
    await init_db()
    yield
    # Cleanup on shutdown (if needed)


# Create FastAPI app
app = FastAPI(
    title="WorkflowForge API",
    description="API for WorkflowForge, a business process automation platform using multi-agent orchestration",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only, restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize workflow orchestrator
orchestrator = WorkflowOrchestrator()


class WorkflowRequest(BaseModel):
    """Request model for workflow execution."""
    name: str
    description: str
    input_data: Dict[str, Any]


class WorkflowResponse(BaseModel):
    """Response model for workflow execution."""
    workflow_id: str
    name: str
    description: str
    status: str
    result: Optional[Dict[str, Any]]
    error: Optional[str]
    history: List[Dict[str, Any]]


# Include routers
app.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
app.include_router(agents.router, prefix="/agents", tags=["agents"])
app.include_router(execute.router, prefix="/execute", tags=["execute"])
app.include_router(metrics.router, prefix="/metrics", tags=["metrics"])


@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "name": "WorkflowForge API",
        "version": "0.1.0",
        "status": "operational",
        "docs_url": "/docs"
    }


@app.get("/workflows")
async def list_workflows():
    """List all available workflows."""
    async with get_db() as db:
        workflows = await db.fetch_all("SELECT * FROM workflows")
        return workflows


@app.post("/workflows", response_model=WorkflowResponse, status_code=201)
async def create_workflow(request: WorkflowRequest):
    """Create and execute a new workflow."""
    workflow_id = str(uuid.uuid4())

    try:
        # Execute workflow
        result = await orchestrator.execute_workflow(
            workflow_id=workflow_id,
            input_data=request.input_data
        )

        # Store workflow in database
        async with get_db() as db:
            await db.execute(
                """
                INSERT INTO workflows (id, name, description, status, result)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    workflow_id,
                    request.name,
                    request.description,
                    result["status"],
                    str(result["result"])
                )
            )

        return WorkflowResponse(
            workflow_id=workflow_id,
            name=request.name,
            description=request.description,
            status=result["status"],
            result=result.get("result"),
            error=result.get("error"),
            history=result.get("history", [])
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str):
    """Get workflow execution details."""
    async with get_db() as db:
        workflow = await db.fetch_one(
            "SELECT * FROM workflows WHERE id = ?",
            (workflow_id,)
        )

        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")

        return WorkflowResponse(
            workflow_id=workflow["id"],
            name=workflow["name"],
            description=workflow["description"],
            status=workflow["status"],
            # Note: For demo only, not production safe
            result=eval(workflow["result"]),
            error=workflow.get("error"),
            history=[]  # TODO: Implement history tracking
        )


@app.get("/metrics")
async def get_metrics():
    """Get system metrics and performance data."""
    async with get_db() as db:
        # Get workflow execution metrics from database
        query = """
        SELECT 
            COUNT(*) as total_executions,
            AVG(execution_time) as avg_execution_time
        FROM workflow_executions
        """
        metrics = await db.fetch_one(query)

        # Additional metrics could be calculated here

        return {
            "total_executions": metrics["total_executions"] if metrics else 0,
            "avg_execution_time": metrics["avg_execution_time"] if metrics else 0,
            "system_stats": {
                "memory_usage": psutil.virtual_memory().percent,
                "cpu_usage": psutil.cpu_percent()
            }
        }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
