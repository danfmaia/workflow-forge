from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, Graph
from pydantic import BaseModel

from app.agents.researcher import ResearcherAgent
from app.agents.processor import ProcessorAgent
from app.agents.approver import ApproverAgent
from app.agents.optimizer import OptimizerAgent


class WorkflowState(BaseModel):
    """Represents the current state of a workflow execution."""
    workflow_id: str
    current_step: str = "start"
    data: Dict[str, Any] = {}
    history: List[Dict[str, Any]] = []
    error: Optional[str] = None


class WorkflowOrchestrator:
    """Coordinates the execution of workflow agents."""

    def __init__(self):
        self.researcher = ResearcherAgent()
        self.processor = ProcessorAgent()
        self.approver = ApproverAgent()
        self.optimizer = OptimizerAgent()
        self.graph = self._build_workflow_graph()

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
            # Execute the workflow graph
            final_state = await self.graph.arun(
                initial_state
            )

            return {
                "workflow_id": workflow_id,
                "status": "completed",
                "result": final_state.data,
                "history": final_state.history
            }

        except Exception as e:
            return {
                "workflow_id": workflow_id,
                "status": "error",
                "error": str(e),
                "history": initial_state.history
            }
