.PHONY: setup clean test run-backend run-frontend install-backend install-frontend format lint

# Environment variables
BACKEND_DIR=backend
FRONTEND_DIR=frontend
CONDA_ENV_NAME=workflow-forge
PYTHON=python
VENV=$(BACKEND_DIR)/venv

setup-backend: clean-backend create-env install-backend

create-env:
	cd $(BACKEND_DIR) && conda env create -f environment.yml

install-backend:
	cd $(BACKEND_DIR) && pip install -e .

install-frontend:
	cd $(FRONTEND_DIR) && npm install

run-backend:
	cd $(BACKEND_DIR) && $(PYTHON) run.py

run-frontend:
	cd $(FRONTEND_DIR) && npm run dev

test-backend:
	cd $(BACKEND_DIR) && pytest

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
dev-backend: install-backend run-backend
dev-frontend: install-frontend run-frontend

# Activate environment (run this first)
# You need to source this command: source make activate
activate:
	cd $(BACKEND_DIR) && conda activate $(CONDA_ENV_NAME) 