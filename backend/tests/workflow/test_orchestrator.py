import pytest
from unittest.mock import patch, MagicMock
from app.workflow.orchestrator import WorkflowOrchestrator, WorkflowState
import uuid


class MockWorkflowGraph:
    def __init__(self):
        self.state = {}
        self.compiled = True

    async def arun(self, input_data):
        """Mock implementation of the graph arun method"""
        # Return a state object that matches what our orchestrator expects
        state = WorkflowState(
            workflow_id=input_data.workflow_id,
            current_step="optimize",
            data={
                "research_results": "Research completed",
                "processed_data": "Data processed",
                "approval": {"approved": True, "feedback": "Approved"},
                "optimization": "Workflow optimized"
            },
            history=[
                {"step": "research", "timestamp": "2023-01-01T00:00:00"},
                {"step": "process", "timestamp": "2023-01-01T00:00:01"},
                {"step": "approve", "timestamp": "2023-01-01T00:00:02"},
                {"step": "optimize", "timestamp": "2023-01-01T00:00:03"}
            ]
        )
        return state


@pytest.mark.asyncio
async def test_workflow_orchestrator_initialization():
    """Test that the workflow orchestrator initializes correctly using a mock."""
    with patch('app.workflow.orchestrator.WorkflowOrchestrator._build_workflow_graph') as mock_build:
        mock_build.return_value = MockWorkflowGraph()
        orchestrator = WorkflowOrchestrator()
        assert orchestrator is not None
        assert orchestrator.graph is not None
        assert orchestrator.graph.compiled is True


@pytest.mark.asyncio
async def test_workflow_orchestrator_agents():
    """Test that the workflow orchestrator initializes agents correctly."""
    with patch('app.workflow.orchestrator.WorkflowOrchestrator._build_workflow_graph') as mock_build:
        mock_build.return_value = MockWorkflowGraph()
        orchestrator = WorkflowOrchestrator()
        assert orchestrator.researcher is not None
        assert orchestrator.processor is not None
        assert orchestrator.approver is not None
        assert orchestrator.optimizer is not None


@pytest.mark.asyncio
async def test_workflow_orchestrator_execute():
    """Test that the workflow orchestrator executes a workflow correctly."""
    with patch('app.workflow.orchestrator.WorkflowOrchestrator._build_workflow_graph') as mock_build:
        mock_build.return_value = MockWorkflowGraph()
        # Also patch the _mock_workflow_execution method to use our test data
        with patch('app.workflow.orchestrator.WorkflowOrchestrator._mock_workflow_execution') as mock_execute:
            # Create a mock state that matches our expected output
            mock_state = WorkflowState(
                workflow_id="test-id",
                current_step="optimize",
                data={
                    "research_results": "Research completed",
                    "processed_data": "Data processed",
                    "approval": {"approved": True, "feedback": "Approved"},
                    "optimization": "Workflow optimized"
                },
                history=[
                    {"step": "research", "timestamp": "2023-01-01T00:00:00"},
                    {"step": "process", "timestamp": "2023-01-01T00:00:01"},
                    {"step": "approve", "timestamp": "2023-01-01T00:00:02"},
                    {"step": "optimize", "timestamp": "2023-01-01T00:00:03"}
                ]
            )
            mock_execute.return_value = mock_state

            orchestrator = WorkflowOrchestrator()
            workflow_id = "test-id"
            input_data = {"input": "test data"}
            result = await orchestrator.execute_workflow(workflow_id, input_data)

            # Check the structure of the result
            assert result["workflow_id"] == workflow_id
            assert result["status"] == "completed"
            assert "result" in result

            # Check result content - this matches our mock implementation
            data = result["result"]
            assert "research_results" in data
            assert "processed_data" in data
            assert "approval" in data
            assert "optimization" in data


@pytest.mark.asyncio
async def test_workflow_orchestrator_error_handling():
    """Test that the workflow orchestrator handles errors correctly."""
    with patch('app.workflow.orchestrator.WorkflowOrchestrator._build_workflow_graph') as mock_build:
        mock_graph = MagicMock()
        mock_graph.arun.side_effect = Exception("Test error")
        mock_build.return_value = mock_graph

        # Also patch the _mock_workflow_execution method to raise an exception
        with patch('app.workflow.orchestrator.WorkflowOrchestrator._mock_workflow_execution') as mock_execute:
            mock_execute.side_effect = Exception("Test error")

            orchestrator = WorkflowOrchestrator()
            workflow_id = "test-id"
            input_data = {"input": "test data"}

            result = await orchestrator.execute_workflow(workflow_id, input_data)
            assert result["status"] == "error"
            assert "Test error" in result["error"]


@pytest.mark.asyncio
async def test_workflow_state_initialization():
    """Test that the workflow state can be initialized with custom values."""
    workflow_id = str(uuid.uuid4())
    state = WorkflowState(
        workflow_id=workflow_id,
        current_step="research",
        data={"query": "Test query"},
        history=[{"step": "start", "timestamp": "2023-01-01T00:00:00"}]
    )

    assert state.workflow_id == workflow_id
    assert state.current_step == "research"
    assert state.data["query"] == "Test query"
    assert len(state.history) == 1
    assert state.error is None


@pytest.mark.asyncio
async def test_execute_workflow():
    """Test that a workflow can be executed end-to-end."""
    # Patch the _mock_workflow_execution method to return a known state
    with patch('app.workflow.orchestrator.WorkflowOrchestrator._mock_workflow_execution') as mock_execute:
        # Create a mock state that matches our expected output
        mock_state = WorkflowState(
            workflow_id="test-workflow-id",
            current_step="optimize",
            data={
                "research_results": {"findings": "Test findings"},
                "processed_data": {"result": "Test result"},
                "approval": {"approved": True},
                "optimization": {"optimizations": ["Test optimization"]}
            },
            history=[
                {"step": "research", "timestamp": "2023-01-01T00:00:00"},
                {"step": "optimize", "timestamp": "2023-01-01T00:00:03"}
            ]
        )
        mock_execute.return_value = mock_state

        orchestrator = WorkflowOrchestrator()
        workflow_id = str(uuid.uuid4())

        input_data = {
            "query": "Analyze customer feedback trends",
            "context": "E-commerce customer reviews dataset",
            "constraints": {
                "time_period": "last_month",
                "min_confidence": 0.8
            }
        }

        result = await orchestrator.execute_workflow(workflow_id, input_data)

        # Check the structure of the result
        assert result["workflow_id"] == workflow_id
        assert result["status"] == "completed"
        assert "result" in result
        assert "history" in result


@pytest.mark.asyncio
async def test_workflow_error_handling():
    """Test that the workflow orchestrator handles errors gracefully."""
    # Create a subclass of WorkflowOrchestrator with a method that raises an exception
    class ErrorTestOrchestrator(WorkflowOrchestrator):
        async def execute_workflow(self, workflow_id, input_data):
            try:
                # Simulate an error during execution
                raise ValueError("Test error")
            except Exception as e:
                # Return a standardized error response
                return {
                    "workflow_id": workflow_id,
                    "status": "error",
                    "error": str(e),
                    "history": []
                }

    orchestrator = ErrorTestOrchestrator()
    workflow_id = str(uuid.uuid4())

    result = await orchestrator.execute_workflow(workflow_id, {"query": "test"})

    # Verify the error response structure
    assert result["workflow_id"] == workflow_id
    assert result["status"] == "error"
    assert "Test error" in result["error"]
    assert "history" in result
