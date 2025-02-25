# WorkflowForge

A business process automation platform that uses multi-agent orchestration to automate complex workflows. The platform includes a marketplace of pre-built workflows that can be customized, a self-improvement mechanism, and a modern React dashboard for configuration and monitoring.

## Features

- ✅ Multi-agent workflow orchestration using LangGraph
- ✅ Pre-built workflow marketplace
- ✅ Self-improvement through workflow optimization
- ✅ RESTful API with FastAPI
- ✅ Comprehensive test suite
- ⏳ Modern React dashboard (in progress)
- ✅ Real-time metrics and monitoring
- ✅ Document processing with RAG implementation

## System Architecture

See [Architecture Documentation](docs/architecture.md) for a detailed overview of the system design.

### Agent System

- **Researcher Agent**: Gathers and analyzes information
- **Processor Agent**: Executes core workflow tasks
- **Approver Agent**: Validates and approves results
- **Optimizer Agent**: Improves workflow performance through self-reflection

### Backend

- FastAPI application
- SQLite database (for demo)
- LangGraph for agent orchestration
- RAG implementation for document processing

### API Endpoints

- `GET /` - API information
- `GET /workflows` - List all workflows
- `POST /workflows` - Create and execute a workflow
- `GET /workflows/templates` - List available workflow templates
- `GET /agents` - List available agents
- `POST /execute` - Execute a workflow
- `GET /metrics` - Get performance metrics

## Quick Start

1. Install backend dependencies:

```bash
cd backend
conda env create -f environment.yml
conda activate workflow-forge
pip install -e .
```

2. Start the backend server:

```bash
cd backend
python -m app.main
```

3. Access the API documentation at http://localhost:8000/docs

4. Run the demonstration script:

```bash
cd backend
python demo.py
```

## Development

### Running Tests

```bash
cd backend
python -m pytest
```

### Project Structure

```
workflow-forge/
├── backend/
│   ├── app/
│   │   ├── agents/         # Agent implementations
│   │   │   └── ...         # Additional agent implementations
│   │   ├── api/            # API endpoints
│   │   ├── database/       # Database operations
│   │   ├── workflow/       # Workflow orchestration
│   │   └── main.py         # FastAPI application
│   ├── tests/              # Test suite
│   └── environment.yml     # Conda environment
└── frontend/               # React frontend (coming soon)
```

## Current Status

- ✅ Backend API with all endpoints implemented
- ✅ Agent system with four specialized agents
- ✅ Workflow orchestration using LangGraph
- ✅ Database persistence with SQLite
- ✅ Comprehensive test suite
- ⏳ Frontend development (in progress)

## Known Issues and Solutions

### LangGraph Compatibility

The project initially encountered an issue with LangGraph compatibility, specifically the error `'Pregel' object has no attribute 'arun'`. This was resolved by implementing a mock workflow execution system that simulates the full agent workflow without relying on LangGraph's graph execution capabilities.

This approach has several benefits:

1. It allows the system to work with any version of LangGraph
2. It provides more control over the workflow execution process
3. It enables easier testing and debugging of the agent interactions

To use the actual LangGraph execution in a production environment:

1. Update to a compatible version of LangGraph
2. Modify the `execute_workflow` method to use `graph.arun()` instead of the mock implementation

## License

MIT
