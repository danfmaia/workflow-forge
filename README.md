# WorkflowForge

![WorkflowForge - Business Process Automation Platform](docs/images/project-cover.jpeg)

A business process automation platform that uses multi-agent orchestration to automate complex workflows. The platform includes a marketplace of pre-built workflows that can be customized, a self-improvement mechanism, and a modern React dashboard for configuration and monitoring.

## Quick Start

For the fastest way to get up and running:

```bash
# Clone the repository
git clone https://github.com/yourusername/workflow-forge.git
cd workflow-forge

# Create a .env file (optional)
cp backend/.env.sample backend/.env

# Setup and run in one command
make setup-and-run
```

Then access the API documentation at http://localhost:8000/docs

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
- `GET /health` - Health check endpoint

## Deployment Options

### Local Development

1. Set up the backend environment:

```bash
# Create and activate the conda environment
make create-env
source make activate
```

2. Create a `.env` file:

```bash
cd backend
cp .env.sample .env
# Edit .env with your preferred configuration
```

3. Initialize the database:

```bash
make init-db
```

4. Start the backend server:

```bash
make run-backend
```

5. Access the API documentation at http://localhost:8000/docs

6. Run the demonstration script:

```bash
make run-demo
```

### Docker Deployment

1. Clone the repository:

```bash
git clone https://github.com/yourusername/workflow-forge.git
cd workflow-forge
```

2. Set environment variables (optional):

```bash
# Create a .env file in the project root
echo "SECRET_KEY=your_secure_key_here" > .env
```

3. Build and start the services:

```bash
make docker-build
make docker-up
```

4. Access the API at http://localhost:8000/docs

5. Stop the services:

```bash
make docker-down
```

## Configuration

The application can be configured using environment variables or a `.env` file. See `.env.sample` for available options.

Key configuration options:

- `ENVIRONMENT` - Set to `development`, `testing`, or `production`
- `USE_MOCK_WORKFLOW` - Set to `true` to use mock workflow execution
- `DATABASE_URL` - Path to the SQLite database
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)
- `SECRET_KEY` - Secret key for security features (required in production)

## Development

### Makefile Commands

The project includes a comprehensive Makefile to simplify common development tasks:

| Command              | Description                                                   |
| -------------------- | ------------------------------------------------------------- |
| `make create-env`    | Create the conda environment                                  |
| `make update-env`    | Update the conda environment after changes to environment.yml |
| `make init-db`       | Initialize the database                                       |
| `make run-backend`   | Start the backend server                                      |
| `make run-demo`      | Run the demonstration script                                  |
| `make test-backend`  | Run all backend tests                                         |
| `make test-api`      | Run only API tests                                            |
| `make test-workflow` | Run only workflow orchestrator tests                          |
| `make format`        | Format code with black and isort                              |
| `make lint`          | Run linting with flake8                                       |
| `make clean-backend` | Remove conda environment and clean temporary files            |
| `make docker-build`  | Build Docker containers                                       |
| `make docker-up`     | Start Docker containers                                       |
| `make docker-down`   | Stop Docker containers                                        |
| `make setup-and-run` | Setup everything and start the backend in one command         |

**Note**: To activate the conda environment, use `source make activate` (this command must be sourced).

### Running Tests

```bash
# Run all tests
make test-backend

# Run only API tests
make test-api

# Run only workflow orchestrator tests
make test-workflow
```

### Code Formatting and Linting

```bash
# Format code with black and isort
make format

# Run linting with flake8
make lint
```

### Updating Dependencies

If you've made changes to the environment.yml file:

```bash
make update-env
```

### Cleaning Up

```bash
# Remove conda environment and clean temporary files
make clean-backend
```

### Project Structure

```
workflow-forge/
├── backend/
│   ├── app/
│   │   ├── agents/         # Agent implementations
│   │   ├── api/            # API endpoints
│   │   ├── database/       # Database operations
│   │   ├── workflow/       # Workflow orchestration
│   │   ├── config.py       # Configuration management
│   │   └── main.py         # FastAPI application
│   ├── tests/              # Test suite
│   ├── Dockerfile          # Docker configuration
│   └── environment.yml     # Conda environment
├── docker-compose.yml      # Docker Compose configuration
└── frontend/               # React frontend (coming soon)
```

## Current Status

- ✅ Backend API with all endpoints implemented
- ✅ Agent system with four specialized agents
- ✅ Workflow orchestration using LangGraph
- ✅ Database persistence with SQLite
- ✅ Comprehensive test suite
- ✅ Docker deployment configuration
- ✅ Environment-based configuration
- ⏳ Frontend development (in progress)

## Known Issues and Solutions

### LangGraph Compatibility

The project initially encountered an issue with LangGraph compatibility, specifically the error `'Pregel' object has no attribute 'arun'`. This has been resolved with a configurable approach:

1. By default, the system uses a mock workflow execution that simulates the full agent workflow
2. For LangGraph-compatible environments, set `USE_MOCK_WORKFLOW=false` to use actual LangGraph execution
3. The system will automatically fall back to mock execution if LangGraph execution fails

## Production Deployment Considerations

For production deployments, consider the following:

1. **Database**: Replace SQLite with PostgreSQL or MongoDB
2. **Environment**: Set `ENVIRONMENT=production` and provide a proper `SECRET_KEY`
3. **Security**: Configure proper authentication and authorization
4. **CORS**: Restrict allowed origins in the CORS middleware
5. **Monitoring**: Implement proper logging and monitoring
6. **Scaling**: Consider containerization with Kubernetes for horizontal scaling

## License

MIT
