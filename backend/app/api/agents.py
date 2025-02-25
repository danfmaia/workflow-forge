from fastapi import APIRouter
from typing import List, Dict, Any

from app.agents.researcher import ResearcherAgent
from app.agents.processor import ProcessorAgent
from app.agents.approver import ApproverAgent
from app.agents.optimizer import OptimizerAgent

router = APIRouter()

# Initialize agents
agents = {
    "researcher": ResearcherAgent(),
    "processor": ProcessorAgent(),
    "approver": ApproverAgent(),
    "optimizer": OptimizerAgent()
}


@router.get("/", response_model=List[Dict[str, Any]])
async def list_agents():
    """List all available agents and their capabilities."""
    return [
        {
            "id": agent_id,
            "name": agent.name,
            "description": agent.description,
            "capabilities": [
                "Document analysis" if agent_id == "researcher" else None,
                "Task processing" if agent_id == "processor" else None,
                "Quality validation" if agent_id == "approver" else None,
                "Performance optimization" if agent_id == "optimizer" else None
            ]
        }
        for agent_id, agent in agents.items()
    ]


@router.get("/{agent_id}/config")
async def get_agent_config(agent_id: str):
    """Get configuration for a specific agent."""
    if agent_id not in agents:
        return {"error": "Agent not found"}
    return agents[agent_id].config
