"""Base agent module defining the Agent interface and common functionality."""

from typing import Dict, Any, List
from abc import ABC, abstractmethod
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AgentState:
    """Represents the current state of an agent."""

    current_step: str = "start"
    messages: List[Any] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        """Initialize default values for mutable fields."""
        if self.messages is None:
            self.messages = []
        if self.metadata is None:
            self.metadata = {}


class Agent(ABC):
    """Base class for all agents in the system."""

    def __init__(self, name: str, description: str):
        """Initialize the agent with a name and description.

        Args:
            name: The name of the agent
            description: A description of the agent's role and capabilities
        """
        self.name = name
        self.description = description
        self._state = AgentState()
        logger.info(f"Initialized agent: {name}")

    @abstractmethod
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process the current state and return an updated state.

        This is the main method that must be implemented by all agents.

        Args:
            state: The current state dictionary

        Returns:
            The updated state dictionary
        """
        pass

    def update_state(self, updates: Dict[str, Any]) -> None:
        """Update the agent's state with the provided updates.

        Args:
            updates: Dictionary of state updates to apply
        """
        if "current_step" in updates:
            self._state.current_step = updates["current_step"]

        if "messages" in updates:
            self._state.messages = updates["messages"]

        if "metadata" in updates:
            self._state.metadata.update(updates["metadata"])

        logger.debug(f"Updated state for {self.name}: {self._state}")

    def get_state(self) -> AgentState:
        """Get the current state of the agent.

        Returns:
            The current agent state
        """
        return self._state

    def reset(self) -> None:
        """Reset the agent state to its initial values."""
        self._state = AgentState()
        logger.info(f"Reset state for agent: {self.name}")

    @property
    def config(self) -> Dict[str, Any]:
        """Get the agent configuration.

        Returns:
            Dictionary containing agent configuration
        """
        return {
            "name": self.name,
            "description": self.description,
            "current_state": self._state.current_step
        }

    def __repr__(self) -> str:
        """Return a string representation of the agent."""
        return f"{self.__class__.__name__}(name='{self.name}')"
