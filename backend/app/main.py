import logging
import uuid
import os
import psutil
import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# First import config to avoid circular imports
from app.config import config

# Then import other modules that might depend on config
from app.database import init_db, get_db, db
from app.workflow.orchestrator import WorkflowOrchestrator
from app.api import workflows, agents, execute, metrics
from app.auth import api as auth_api

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.logging.level),
    format=config.logging.format
)
logger = logging.getLogger(__name__)

# Import API routers

# Lifespan context manager for startup/shutdown events


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events for the application."""
    # Log startup information
    logger.info(
        f"Starting WorkflowForge API in {config.environment} environment")

    # Initialize the database
    logger.info("Initializing database...")
    await init_db()

    # Create healthcheck file to indicate the API is running
    healthcheck_file = os.path.join(
        os.path.dirname(__file__), '..', '.healthcheck')
    with open(healthcheck_file, 'w') as f:
        f.write(datetime.now().isoformat())

    yield

    # Cleanup on shutdown
    logger.info("Shutting down WorkflowForge API")

    # Remove healthcheck file
    if os.path.exists(healthcheck_file):
        os.remove(healthcheck_file)


# Create FastAPI application
app = FastAPI(
    title="WorkflowForge API",
    description="Multi-agent workflow orchestration system",
    version="0.1.0",
    lifespan=lifespan,
    debug=config.api.debug
)

# Add CORS middleware with configuration from config
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors.allowed_origins,
    allow_credentials=config.cors.allow_credentials,
    allow_methods=config.cors.allow_methods,
    allow_headers=config.cors.allow_headers,
    max_age=config.cors.max_age,
)

# Log CORS configuration
logger.info(
    f"CORS configuration: allowed origins = {config.cors.allowed_origins}")

# Rate limiting middleware
if config.rate_limit.enabled:
    class RateLimitMiddleware:
        def __init__(
            self,
            app,
            calls_per_minute: int = 60,
            window_size: int = 60
        ):
            self.app = app
            self.calls_per_minute = calls_per_minute
            self.window_size = window_size  # Window size in seconds
            self.request_counts = {}
            logger.info(
                f"Rate limiting enabled: {calls_per_minute} requests per minute")

        async def __call__(self, request: Request, call_next):
            # Get client IP
            client_ip = request.client.host
            current_time = time.time()

            # Clean up old entries
            self._cleanup_old_requests(current_time)

            # Check if rate limit exceeded
            if self._is_rate_limited(client_ip, current_time):
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Rate limit exceeded. Please try again later."}
                )

            # Process the request
            return await call_next(request)

        def _cleanup_old_requests(self, current_time: float):
            """Remove requests older than the window size."""
            cutoff_time = current_time - self.window_size
            for ip in list(self.request_counts.keys()):
                self.request_counts[ip] = [
                    timestamp for timestamp in self.request_counts[ip]
                    if timestamp > cutoff_time
                ]
                if not self.request_counts[ip]:
                    del self.request_counts[ip]

        def _is_rate_limited(self, client_ip: str, current_time: float) -> bool:
            """Check if the client IP has exceeded the rate limit."""
            if client_ip not in self.request_counts:
                self.request_counts[client_ip] = []

            self.request_counts[client_ip].append(current_time)

            # Check if rate limit exceeded
            return len(self.request_counts[client_ip]) > self.calls_per_minute

    # Add rate limiting middleware
    app.add_middleware(
        RateLimitMiddleware,
        calls_per_minute=config.rate_limit.per_minute,
        window_size=config.rate_limit.window_size
    )


# Define request and response models
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
app.include_router(auth_api.router)


@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "name": "WorkflowForge API",
        "version": "0.1.0",
        "status": "operational",
        "environment": config.environment,
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
    # Generate a unique ID for the workflow
    workflow_id = str(uuid.uuid4())

    # Log workflow creation
    logger.info(f"Creating workflow {workflow_id}: {request.name}")

    try:
        # Store workflow in database
        await db.execute(
            """
            INSERT INTO workflows 
            (id, name, description, status, created_at, updated_at) 
            VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
            """,
            (workflow_id, request.name, request.description, "pending")
        )

        # Execute the workflow
        orchestrator = WorkflowOrchestrator(use_mock=config.workflow.use_mock)
        result = await orchestrator.execute_workflow(workflow_id, request.input_data)

        # Update workflow status in database
        await db.execute(
            """
            UPDATE workflows 
            SET status = ?, result = ?, updated_at = datetime('now')
            WHERE id = ?
            """,
            (result["status"], json.dumps(
                result.get("result", {})), workflow_id)
        )

        # Return the workflow response
        return {
            "workflow_id": workflow_id,
            "name": request.name,
            "description": request.description,
            "status": result["status"],
            "result": result.get("result"),
            "error": result.get("error"),
            "history": result.get("history", [])
        }

    except Exception as e:
        logger.error(f"Error creating workflow: {str(e)}")

        # Update workflow status to error
        await db.execute(
            """
            UPDATE workflows 
            SET status = ?, error = ?, updated_at = datetime('now')
            WHERE id = ?
            """,
            ("error", str(e), workflow_id)
        )

        # Return error response
        return {
            "workflow_id": workflow_id,
            "name": request.name,
            "description": request.description,
            "status": "error",
            "result": None,
            "error": str(e),
            "history": []
        }


@app.get("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str):
    """Get a specific workflow by ID."""
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
        "workflow_id": workflow["id"],
        "name": workflow["name"],
        "description": workflow["description"],
        "status": workflow["status"],
        "result": result,
        "error": workflow.get("error"),
        "history": []  # We don't store history in the database yet
    }


@app.get("/metrics")
async def get_metrics():
    """Get overall system metrics."""
    # Get workflow execution metrics
    total_executions = await db.fetch_val(
        "SELECT COUNT(*) FROM workflow_executions"
    ) or 0

    # Get average execution time
    avg_execution_time = await db.fetch_val(
        "SELECT AVG(execution_time) FROM workflow_executions"
    ) or 0

    # Get system metrics
    memory = psutil.virtual_memory()

    return {
        "total_executions": total_executions,
        "avg_execution_time": round(float(avg_execution_time), 2),
        "system_stats": {
            "memory_usage": memory.percent,
            "cpu_usage": psutil.cpu_percent(interval=0.1),
            "timestamp": datetime.now().isoformat()
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": config.environment,
        "database": "connected"  # Would add an actual check in production
    }

# Add this section to run the app with uvicorn if the file is executed directly
if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on {config.api.host}:{config.api.port}")
    uvicorn.run(
        "app.main:app",
        host=config.api.host,
        port=config.api.port,
        reload=config.api.reload,
        workers=config.api.workers
    )
