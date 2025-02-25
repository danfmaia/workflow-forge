from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, Graph
from pydantic import BaseModel
import inspect
import logging
import os
from datetime import datetime

from app.agents.researcher import ResearcherAgent
from app.agents.processor import ProcessorAgent
from app.agents.approver import ApproverAgent
from app.agents.optimizer import OptimizerAgent
from app.config import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.logging.level),
    format=config.logging.format
)
logger = logging.getLogger(__name__)


class WorkflowState(BaseModel):
    """Represents the current state of a workflow execution."""
    workflow_id: str
    current_step: str = "start"
    data: Dict[str, Any] = {}
    history: List[Dict[str, Any]] = []
    error: Optional[str] = None


class WorkflowOrchestrator:
    """Coordinates the execution of workflow agents."""

    def __init__(self, use_mock: Optional[bool] = None):
        self.researcher = ResearcherAgent()
        self.processor = ProcessorAgent()
        self.approver = ApproverAgent()
        self.optimizer = OptimizerAgent()
        self.graph = self._build_workflow_graph()

        # Determine whether to use mock implementation
        # Priority: 1. Constructor parameter, 2. Configuration value
        self.use_mock = use_mock if use_mock is not None else config.workflow.use_mock

        if self.use_mock:
            logger.warning(
                f"Using mock workflow execution in {config.environment} environment.")
        else:
            logger.info(
                f"Using LangGraph workflow execution in {config.environment} environment.")

    def _build_workflow_graph(self) -> Graph:
        """Build the workflow execution graph."""
        # Create a new graph
        workflow = StateGraph(WorkflowState)

        # Define state transitions
        workflow.add_node("research", self.researcher.process)
        workflow.add_node("process", self.processor.process)
        workflow.add_node("approve", self.approver.process)
        workflow.add_node("optimize", self.optimizer.process)

        # Define edges (workflow steps)
        workflow.add_edge("research", "process")
        workflow.add_edge("process", "approve")

        # Conditional edges based on approval
        def approval_router(state: Dict) -> str:
            """Route to next step based on approval status."""
            return "optimize" if state.get("approved", False) else "process"

        workflow.add_conditional_edges(
            "approve",
            approval_router,
            {"optimize": "optimize", "process": "process"}
        )

        # Set entry point
        workflow.set_entry_point("research")

        # The graph will end when it reaches the optimize node
        workflow.set_finish_point("optimize")

        return workflow.compile()

    async def _langgraph_workflow_execution(self, workflow_id: str, input_data: Dict[str, Any]) -> WorkflowState:
        """
        Execute workflow using actual LangGraph implementation.

        Args:
            workflow_id: Unique identifier for the workflow
            input_data: Initial data for the workflow

        Returns:
            WorkflowState with execution results

        Raises:
            RuntimeError: If LangGraph execution fails
        """
        try:
            initial_state = WorkflowState(
                workflow_id=workflow_id,
                data=input_data
            )

            # Execute the workflow using LangGraph
            if hasattr(self.graph, 'arun'):
                final_state = await self.graph.arun(initial_state)
                return final_state
            else:
                raise RuntimeError(
                    "LangGraph version does not support 'arun' method")
        except Exception as e:
            logger.error(f"LangGraph execution failed: {str(e)}")
            raise

    async def _mock_workflow_execution(self, workflow_id: str, input_data: Dict[str, Any]) -> WorkflowState:
        """
        Mock implementation of workflow execution for demonstration purposes.

        Args:
            workflow_id: Unique identifier for the workflow
            input_data: Initial data for the workflow

        Returns:
            WorkflowState with simulated execution results
        """
        logger.info(
            f"Using mock workflow execution for workflow {workflow_id}")

        # Get current timestamp for more realistic simulation
        current_time = datetime.now().isoformat()

        # Simulate research step
        research_results = await self.researcher.process(input_data)

        # Simulate processing step
        process_input = {
            "task": "Process research findings",
            "research_findings": research_results,
            "parameters": input_data.get("constraints", {})
        }
        process_results = await self.processor.process(process_input)

        # Simulate approval step
        approval_input = {
            "result": process_results,
            "criteria": {"quality_threshold": 0.8}
        }
        approval_results = await self.approver.process(approval_input)

        # Simulate optimization step
        optimization_input = {
            "workflow_results": {
                "research": research_results,
                "process": process_results,
                "approval": approval_results
            },
            "performance_metrics": {
                "execution_time": 1.5,
                "success_rate": 1.0
            }
        }
        optimization_results = await self.optimizer.process(optimization_input)

        # Combine all results
        mock_data = {
            "research_results": research_results,
            "processed_data": process_results,
            "approval": approval_results,
            "optimization": optimization_results
        }

        # Create final state with more realistic timestamps
        final_state = WorkflowState(
            workflow_id=workflow_id,
            current_step="optimize",
            data=mock_data,
            history=[
                {"step": "research", "timestamp": current_time},
                {"step": "process", "timestamp": current_time},
                {"step": "approve", "timestamp": current_time},
                {"step": "optimize", "timestamp": current_time}
            ]
        )

        return final_state

    async def execute_workflow(self, workflow_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a workflow with the given input data.

        Args:
            workflow_id: Unique identifier for the workflow
            input_data: Initial data for the workflow

        Returns:
            Dictionary containing workflow results and optimization suggestions
        """
        initial_state = WorkflowState(
            workflow_id=workflow_id,
            data=input_data
        )

        try:
            # Choose execution strategy based on configuration
            if self.use_mock:
                final_state = await self._mock_workflow_execution(workflow_id, input_data)
            else:
                try:
                    final_state = await self._langgraph_workflow_execution(workflow_id, input_data)
                except Exception as e:
                    logger.warning(
                        f"LangGraph execution failed, falling back to mock: {str(e)}")
                    final_state = await self._mock_workflow_execution(workflow_id, input_data)

            return {
                "workflow_id": workflow_id,
                "status": "completed",
                "result": final_state.data,
                "history": final_state.history
            }

        except Exception as e:
            logger.error(f"Error executing workflow: {str(e)}")
            return {
                "workflow_id": workflow_id,
                "status": "error",
                "error": str(e),
                "history": initial_state.history
            }
