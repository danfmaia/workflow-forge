from typing import Dict, Any, Optional
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, Graph
from pydantic import BaseModel


class AgentState(BaseModel):
    """Represents the current state of an agent's workflow."""
    messages: list[HumanMessage | AIMessage] = []
    current_step: str = "start"
    metadata: Dict[str, Any] = {}
    error: Optional[str] = None


class BaseAgent:
    """Base class for all workflow agents."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self._state = AgentState()

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return results."""
        raise NotImplementedError

    def get_state(self) -> AgentState:
        """Get current agent state."""
        return self._state

    def update_state(self, new_state: Dict[str, Any]):
        """Update agent state with new data."""
        for key, value in new_state.items():
            if hasattr(self._state, key):
                setattr(self._state, key, value)

    def reset(self):
        """Reset agent state."""
        self._state = AgentState()

    @property
    def config(self) -> Dict[str, Any]:
        """Get agent configuration."""
        return {
            "name": self.name,
            "description": self.description,
            "current_state": self._state.dict()
        }
