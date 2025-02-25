import pytest
from app.agents.processor import ProcessorAgent


@pytest.mark.asyncio
async def test_processor_agent_initialization():
    """Test that the processor agent initializes correctly with the right properties."""
    agent = ProcessorAgent()

    assert agent.name == "Processor"
    assert "Executes core workflow" in agent.description
    assert hasattr(agent, "process")
    assert hasattr(agent, "processing_history")
    assert isinstance(agent.processing_history, list)


@pytest.mark.asyncio
async def test_processor_agent_process():
    """Test that the processor agent can process input data."""
    agent = ProcessorAgent()

    input_data = {
        "task": "Analyze customer sentiment",
        "research_findings": {"findings": "Customer reviews dataset analyzed"},
        "parameters": {"threshold": 0.7}
    }

    result = await agent.process(input_data)

    # Verify the result structure
    assert "result" in result
    assert "status" in result
    assert "metrics" in result

    # Verify that the state is updated correctly
    state = agent.get_state()
    assert state.current_step == "complete"
    assert len(state.messages) == 2  # One input, one output

    # Verify that processing history is updated
    assert len(agent.processing_history) == 1
    assert agent.processing_history[0] == input_data


@pytest.mark.asyncio
async def test_processor_agent_config():
    """Test that the processor agent returns the correct configuration."""
    agent = ProcessorAgent()

    config = agent.config

    assert "name" in config
    assert "description" in config
    assert "current_state" in config
    assert config["name"] == "Processor"
