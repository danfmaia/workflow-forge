import pytest
from app.agents.researcher import ResearcherAgent


@pytest.mark.asyncio
async def test_researcher_agent_initialization():
    """Test that the researcher agent initializes correctly with the right properties."""
    agent = ResearcherAgent()

    assert agent.name == "Researcher"
    assert "Gathers and analyzes information" in agent.description
    assert hasattr(agent, "process")
    assert hasattr(agent, "research_history")
    assert isinstance(agent.research_history, list)


@pytest.mark.asyncio
async def test_researcher_agent_process():
    """Test that the researcher agent can process input data."""
    agent = ResearcherAgent()

    input_data = {
        "query": "What are the trends in AI adoption?",
        "context": "Business intelligence report",
        "constraints": {"max_results": 5}
    }

    result = await agent.process(input_data)

    # Verify the result structure
    assert "findings" in result
    assert "sources" in result
    assert "confidence" in result

    # Verify that the state is updated correctly
    state = agent.get_state()
    assert state.current_step == "complete"
    assert len(state.messages) == 2  # One input, one output

    # Verify that research history is updated
    assert len(agent.research_history) == 1
    assert agent.research_history[0] == input_data


@pytest.mark.asyncio
async def test_researcher_agent_reset():
    """Test that the researcher agent can be reset."""
    agent = ResearcherAgent()

    # Process some data to change the state
    input_data = {"query": "Test query"}
    await agent.process(input_data)

    # Reset the agent
    agent.reset()

    # Verify the state is reset
    state = agent.get_state()
    assert state.current_step == "start"
    assert len(state.messages) == 0
    assert state.metadata == {}

    # Research history should still exist (not part of the state)
    assert len(agent.research_history) == 1
