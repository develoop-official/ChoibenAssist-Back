# ChoibenAssist AI Backend - Makefile
# Python環境セットアップと開発タスクの自動化

# Variables
PYTHON = python3
VENV = .venv
VENV_BIN = $(VENV)/bin
PIP = $(VENV_BIN)/pip
PYTHON_VENV = $(VENV_BIN)/python
PROJECT_NAME = ChoibenAssist-Back

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE = \033[1;34m
GREEN = \033[1;32m
YELLOW = \033[1;33m
RED = \033[1;31m
NC = \033[0m # No Color

.PHONY: help
help: ## Show this help message
	@echo "$(BLUE)$(PROJECT_NAME) - Makefile Commands$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# ============================================================================
# Setup Commands
# ============================================================================

.PHONY: setup
setup: ## Complete project setup (recommended for first time)
	@echo "$(BLUE)Setting up $(PROJECT_NAME)...$(NC)"
	$(MAKE) venv
	$(MAKE) install-deps
	$(MAKE) setup-env
	$(MAKE) verify-setup
	@echo "$(GREEN)✅ Setup complete! Run 'make run' to start the server.$(NC)"

.PHONY: venv
venv: ## Create Python virtual environment
	@echo "$(BLUE)Creating virtual environment...$(NC)"
	@if [ ! -d "$(VENV)" ]; then \
		$(PYTHON) -m venv $(VENV); \
		echo "$(GREEN)✅ Virtual environment created at $(VENV)$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  Virtual environment already exists$(NC)"; \
	fi

.PHONY: install-deps
install-deps: venv ## Install all dependencies
	@echo "$(BLUE)Installing dependencies...$(NC)"
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install --no-cache-dir -r requirements.txt
	$(PIP) install --no-cache-dir -r requirements-dev.txt
	@echo "$(GREEN)✅ Dependencies installed$(NC)"

.PHONY: setup-env
setup-env: ## Setup environment variables file
	@echo "$(BLUE)Setting up environment variables...$(NC)"
	@if [ ! -f ".env" ]; then \
		cp .env.example .env; \
		echo "$(GREEN)✅ .env file created from .env.example$(NC)"; \
		echo "$(YELLOW)⚠️  Please edit .env file with your actual values$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  .env file already exists$(NC)"; \
	fi

.PHONY: verify-setup
verify-setup: ## Verify that setup is correct
	@echo "$(BLUE)Verifying setup...$(NC)"
	@$(PYTHON_VENV) --version
	@$(PIP) --version
	@if [ -f ".env" ]; then \
		echo "$(GREEN)✅ Environment file exists$(NC)"; \
	else \
		echo "$(RED)❌ Environment file missing$(NC)"; \
	fi
	@echo "$(GREEN)✅ Setup verification complete$(NC)"

# ============================================================================
# Development Commands
# ============================================================================

.PHONY: run
run: ## Start the development server
	@echo "$(BLUE)Starting development server...$(NC)"
	$(PYTHON_VENV) run.py

.PHONY: run-reload
run-reload: ## Start the development server with auto-reload
	@echo "$(BLUE)Starting development server with auto-reload...$(NC)"
	$(VENV_BIN)/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

.PHONY: shell
shell: ## Activate virtual environment shell
	@echo "$(BLUE)Activating virtual environment...$(NC)"
	@echo "Run: source $(VENV_BIN)/activate"

# ============================================================================
# Code Quality Commands
# ============================================================================

.PHONY: format
format: ## Format code with black and isort
	@echo "$(BLUE)Formatting code...$(NC)"
	$(VENV_BIN)/black app/ tests/
	$(VENV_BIN)/isort app/ tests/
	@echo "$(GREEN)✅ Code formatted$(NC)"

.PHONY: lint
lint: ## Run linting with flake8
	@echo "$(BLUE)Running linter...$(NC)"
	$(VENV_BIN)/flake8 app/ tests/
	@echo "$(GREEN)✅ Linting complete$(NC)"

.PHONY: typecheck
typecheck: ## Run type checking with mypy
	@echo "$(BLUE)Running type check...$(NC)"
	$(VENV_BIN)/mypy app/
	@echo "$(GREEN)✅ Type checking complete$(NC)"

.PHONY: quality
quality: format lint typecheck ## Run all code quality checks
	@echo "$(GREEN)✅ All code quality checks passed$(NC)"

# ============================================================================
# Testing Commands
# ============================================================================

.PHONY: test
test: ## Run tests
	@echo "$(BLUE)Running tests...$(NC)"
	$(VENV_BIN)/pytest

.PHONY: test-verbose
test-verbose: ## Run tests with verbose output
	@echo "$(BLUE)Running tests with verbose output...$(NC)"
	$(VENV_BIN)/pytest -v

.PHONY: test-coverage
test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	$(VENV_BIN)/pytest --cov=app --cov-report=html --cov-report=term
	@echo "$(GREEN)✅ Coverage report generated in htmlcov/$(NC)"

.PHONY: test-watch
test-watch: ## Run tests in watch mode
	@echo "$(BLUE)Running tests in watch mode...$(NC)"
	$(VENV_BIN)/pytest-watch

.PHONY: test-gemini
test-gemini: ## Test Gemini service with real API
	@echo "$(BLUE)Testing Gemini service...$(NC)"
	$(PYTHON_VENV) scripts/test_gemini.py

# ============================================================================
# Docker Commands
# ============================================================================

.PHONY: docker-build
docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	docker build -t choibenassist-backend .
	@echo "$(GREEN)✅ Docker image built$(NC)"

.PHONY: docker-run
docker-run: ## Run application with Docker
	@echo "$(BLUE)Starting application with Docker...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✅ Application started at http://localhost:8000$(NC)"

.PHONY: docker-dev
docker-dev: ## Run application in development mode with Docker
	@echo "$(BLUE)Starting development server with Docker...$(NC)"
	docker-compose -f docker-compose.dev.yml up -d
	@echo "$(GREEN)✅ Development server started at http://localhost:8000$(NC)"

.PHONY: docker-stop
docker-stop: ## Stop Docker containers
	@echo "$(BLUE)Stopping Docker containers...$(NC)"
	docker-compose down
	docker-compose -f docker-compose.dev.yml down || true
	@echo "$(GREEN)✅ Docker containers stopped$(NC)"

.PHONY: docker-logs
docker-logs: ## Show Docker container logs
	@echo "$(BLUE)Showing Docker logs...$(NC)"
	docker-compose logs -f

.PHONY: docker-test
docker-test: ## Run tests in Docker container
	@echo "$(BLUE)Running tests in Docker...$(NC)"
	docker run --rm choibenassist-backend pytest tests/ -v
	@echo "$(GREEN)✅ Docker tests completed$(NC)"

.PHONY: docker-shell
docker-shell: ## Get shell access to Docker container
	@echo "$(BLUE)Accessing Docker container shell...$(NC)"
	docker exec -it choibenassist-backend /bin/bash

.PHONY: docker-clean
docker-clean: ## Clean Docker images and containers
	@echo "$(BLUE)Cleaning Docker resources...$(NC)"
	docker system prune -f
	@echo "$(GREEN)✅ Docker cleanup completed$(NC)"

# ============================================================================
# Database/API Commands
# ============================================================================

.PHONY: check-health
check-health: ## Check API health endpoint
	@echo "$(BLUE)Checking API health...$(NC)"
	@curl -s http://127.0.0.1:8000/api/health || echo "$(RED)❌ Server not running$(NC)"

.PHONY: docs
docs: ## Open API documentation
	@echo "$(BLUE)Opening API documentation...$(NC)"
	@open http://127.0.0.1:8000/docs || echo "$(YELLOW)Visit: http://127.0.0.1:8000/docs$(NC)"

# ============================================================================
# Cleanup Commands
# ============================================================================

.PHONY: clean
clean: ## Clean cache files and temporary files
	@echo "$(BLUE)Cleaning cache files...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	@echo "$(GREEN)✅ Cache files cleaned$(NC)"

.PHONY: clean-venv
clean-venv: ## Remove virtual environment
	@echo "$(BLUE)Removing virtual environment...$(NC)"
	rm -rf $(VENV)
	@echo "$(GREEN)✅ Virtual environment removed$(NC)"

.PHONY: reset
reset: clean clean-venv ## Complete reset (clean + remove venv)
	@echo "$(GREEN)✅ Complete reset done$(NC)"

# ============================================================================
# Production Commands
# ============================================================================

.PHONY: install-prod
install-prod: venv ## Install production dependencies only
	@echo "$(BLUE)Installing production dependencies...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✅ Production dependencies installed$(NC)"

.PHONY: run-prod
run-prod: ## Run with production settings
	@echo "$(BLUE)Starting production server...$(NC)"
	$(VENV_BIN)/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

# ============================================================================
# Utility Commands
# ============================================================================

.PHONY: requirements
requirements: ## Generate requirements.txt from current environment
	@echo "$(BLUE)Generating requirements.txt...$(NC)"
	$(PIP) freeze > requirements.txt
	@echo "$(GREEN)✅ requirements.txt updated$(NC)"

.PHONY: info
info: ## Show project information
	@echo "$(BLUE)Project Information:$(NC)"
	@echo "  Project: $(PROJECT_NAME)"
	@echo "  Python: $(PYTHON)"
	@echo "  Virtual Environment: $(VENV)"
	@echo "  Current directory: $(PWD)"
	@if [ -d "$(VENV)" ]; then \
		echo "  Venv Status: $(GREEN)✅ Active$(NC)"; \
		$(PYTHON_VENV) --version; \
	else \
		echo "  Venv Status: $(RED)❌ Not found$(NC)"; \
	fi

.PHONY: update
update: ## Update all dependencies
	@echo "$(BLUE)Updating dependencies...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade -r requirements.txt
	$(PIP) install --upgrade -r requirements-dev.txt
	@echo "$(GREEN)✅ Dependencies updated$(NC)"
