"""Base agent module defining the Agent interface and common functionality."""

from typing import Dict, Any
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


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

    def __repr__(self) -> str:
        """Return a string representation of the agent."""
        return f"{self.__class__.__name__}(name='{self.name}')"
