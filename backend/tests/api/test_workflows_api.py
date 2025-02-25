import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from contextlib import asynccontextmanager
import asyncio

# Create a mock orchestrator before importing app
mock_orchestrator = AsyncMock()
mock_orchestrator.execute_workflow = AsyncMock(
    return_value={"status": "completed", "result": {"key": "value"}, "history": []})

# Patch the orchestrator
with patch('app.workflow.orchestrator.WorkflowOrchestrator', return_value=mock_orchestrator):
    from app.main import app
    from app.database import init_db

# Initialize the database before running tests


@pytest.fixture(scope="session", autouse=True)
def initialize_db():
    """Initialize the database before running tests."""
    asyncio.run(init_db())


client = TestClient(app)


def test_list_workflow_templates():
    """Test that the workflow templates endpoint returns the expected data."""
    response = client.get("/workflows/templates")

    assert response.status_code == 200
    templates = response.json()

    assert isinstance(templates, list)
    assert len(templates) > 0

    # Check the structure of each template
    for template in templates:
        assert "id" in template
        assert "name" in template
        assert "description" in template
        assert "steps" in template
        assert isinstance(template["steps"], list)


def test_root_endpoint():
    """Test that the root endpoint returns the expected API information."""
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()

    assert "name" in data
    assert "version" in data
    assert "status" in data
    assert "docs_url" in data
    assert data["name"] == "WorkflowForge API"


def test_get_workflows():
    """Test that the GET /workflows endpoint returns a list of workflows."""
    # Add mock implementation of get_db as a context manager
    class MockDB:
        async def fetch_all(self, query, *args, **kwargs):
            return [
                {"id": "123", "name": "Test Workflow",
                    "description": "A test workflow"}
            ]

    # Create a mock of the get_db function that works as an async context manager
    @asynccontextmanager
    async def mock_get_db():
        yield MockDB()

    # Patch the get_db function
    with patch("app.main.get_db", return_value=mock_get_db()):
        response = client.get("/workflows")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) > 0


def test_create_workflow():
    """Test that the POST /workflows endpoint creates a new workflow."""
    workflow_data = {
        "name": "Test Workflow",
        "description": "A test workflow",
        "input_data": {
            "query": "Analyze customer feedback trends",
            "context": "E-commerce customer reviews dataset",
            "constraints": {
                "time_period": "last_month",
                "min_confidence": 0.8
            }
        }
    }
    response = client.post("/workflows", json=workflow_data)
    if response.status_code != 201:
        print(f"Response content: {response.content}")
    assert response.status_code == 201
    result = response.json()
    assert result["name"] == workflow_data["name"]
    assert result["description"] == workflow_data["description"]
    assert "workflow_id" in result


def test_get_agents():
    """Test that the GET /agents endpoint returns a list of available agents."""
    response = client.get("/agents")
    assert response.status_code == 200
    agents = response.json()
    assert isinstance(agents, list)
    # Check for required agent types
    agent_names = [agent["name"] for agent in agents]
    required_agents = ["Researcher", "Processor", "Approver", "Optimizer"]
    for agent in required_agents:
        assert agent in agent_names


@pytest.mark.asyncio
async def test_execute_workflow():
    """Test that the POST /execute endpoint executes a workflow."""
    # This requires mocking the orchestrator, which we've done at the top of the file
    workflow_data = {
        "workflow_id": "test-id",
        "input_data": {
            "document": "Test document",
            "parameters": {"param1": "value1"}
        }
    }

    response = client.post("/execute", json=workflow_data)
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "completed"


def test_get_metrics():
    """Test that the GET /metrics endpoint returns workflow metrics."""
    response = client.get("/metrics")
    assert response.status_code == 200
    metrics = response.json()
    assert isinstance(metrics, dict)
    assert "total_executions" in metrics
    assert "avg_execution_time" in metrics
    assert "system_stats" in metrics
    assert "memory_usage" in metrics["system_stats"]
    assert "cpu_usage" in metrics["system_stats"]
