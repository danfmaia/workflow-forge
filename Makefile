.PHONY: setup clean test run-backend run-frontend install-frontend format lint run-demo init-db create-env update-env test-api test-workflow clean-backend setup-backend dev-backend dev-frontend docker-build docker-up docker-down setup-and-run activate

# Environment variables
BACKEND_DIR=backend
FRONTEND_DIR=frontend
CONDA_ENV_NAME=workflow-forge
PYTHON=python

setup-backend: clean-backend create-env init-db

create-env:
	cd $(BACKEND_DIR) && conda env create -f environment.yml

update-env:
	cd $(BACKEND_DIR) && conda env update -f environment.yml --prune

install-frontend:
	cd $(FRONTEND_DIR) && npm install

init-db:
	cd $(BACKEND_DIR) && $(PYTHON) -c "from app.database import init_db; import asyncio; asyncio.run(init_db())"

run-backend:
	cd $(BACKEND_DIR) && $(PYTHON) -m app.main

run-demo:
	cd $(BACKEND_DIR) && $(PYTHON) demo.py

run-frontend:
	cd $(FRONTEND_DIR) && npm run dev

test-backend:
	cd $(BACKEND_DIR) && pytest

test-api:
	cd $(BACKEND_DIR) && pytest -xvs tests/api/test_workflows_api.py

test-workflow:
	cd $(BACKEND_DIR) && pytest -xvs tests/workflow/test_orchestrator.py

format:
	cd $(BACKEND_DIR) && black . && isort .

lint:
	cd $(BACKEND_DIR) && flake8 .

clean-backend:
	cd $(BACKEND_DIR) && conda env remove -n $(CONDA_ENV_NAME) || true
	find $(BACKEND_DIR) -type d -name "__pycache__" -exec rm -rf {} +
	find $(BACKEND_DIR) -type f -name "*.pyc" -delete
	find $(BACKEND_DIR) -type f -name "*.db" -delete

clean: clean-backend
	# Add frontend cleaning when needed

# Development shortcuts
dev-backend: update-env run-backend
dev-frontend: install-frontend run-frontend
setup-and-run: setup-backend run-backend

# Docker commands
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

# Activate environment (run this first)
# You need to source this command: source make activate
activate:
	conda activate $(CONDA_ENV_NAME) 