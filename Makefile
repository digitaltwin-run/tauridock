# Tauri Builder Makefile
# Automation for common tasks

.PHONY: help install test build dev clean docker publish lint format docs

# Variables
PYTHON := python3
PIP := $(PYTHON) -m pip
DOCKER := docker
DOCKER_COMPOSE := docker-compose
PROJECT_NAME := tauri-builder
VERSION := $(shell cat VERSION 2>/dev/null || echo "1.0.0")
PLATFORMS := windows,macos,linux
ARCHITECTURES := x64,arm64

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

# Default target
help: ## Show this help message
	@echo "$(GREEN)Tauri Builder - Available targets:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Usage:$(NC) make [target]"

# Installation targets
install: ## Install all dependencies
	@echo "$(GREEN)Installing Python dependencies...$(NC)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)Installing pre-commit hooks...$(NC)"
	pre-commit install
	@echo "$(GREEN)Installation complete!$(NC)"

install-dev: ## Install development dependencies
	@echo "$(GREEN)Installing development dependencies...$(NC)"
	$(PIP) install -r requirements.txt
	$(PIP) install -e ".[dev]"
	@echo "$(GREEN)Development setup complete!$(NC)"

install-global: ## Install tauri-builder globally
	@echo "$(GREEN)Installing tauri-builder globally...$(NC)"
	$(PIP) install -e .
	@echo "$(GREEN)Global installation complete!$(NC)"
	@echo "You can now use 'tauri-builder' or 'tb' command"

# Testing targets
test: ## Run unit tests
	@echo "$(GREEN)Running unit tests...$(NC)"
	pytest test_tauri_builder.py -v

test-coverage: ## Run tests with coverage report
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	pytest test_tauri_builder.py --cov=tauri_builder --cov-report=html --cov-report=term
	@echo "$(GREEN)Coverage report generated in htmlcov/index.html$(NC)"

test-integration: ## Run integration tests
	@echo "$(GREEN)Running integration tests...$(NC)"
	pytest tests/test_integration.py -v -s

test-all: test test-integration ## Run all tests

# Build targets
build: ## Build for all platforms
	@echo "$(GREEN)Building for all platforms...$(NC)"
	$(PYTHON) tauri-builder.py \
		--dockerfile ./Dockerfile \
		--frontend-port 3000 \
		--mode build \
		--platforms $(PLATFORMS) \
		--arch $(ARCHITECTURES) \
		--optimize

build-windows: ## Build for Windows only
	@echo "$(GREEN)Building for Windows...$(NC)"
	$(PYTHON) tauri-builder.py \
		--dockerfile ./Dockerfile \
		--frontend-port 3000 \
		--mode build \
		--platforms windows \
		--arch x64 \
		--optimize

build-linux: ## Build for Linux only
	@echo "$(GREEN)Building for Linux...$(NC)"
	$(PYTHON) tauri-builder.py \
		--dockerfile ./Dockerfile \
		--frontend-port 3000 \
		--mode build \
		--platforms linux \
		--arch x64,arm64 \
		--optimize

build-macos: ## Build for macOS only
	@echo "$(GREEN)Building for macOS...$(NC)"
	$(PYTHON) tauri-builder.py \
		--dockerfile ./Dockerfile \
		--frontend-port 3000 \
		--mode build \
		--platforms macos \
		--arch x64,arm64 \
		--optimize

# Development targets
dev: ## Run in development mode
	@echo "$(GREEN)Starting development mode...$(NC)"
	$(PYTHON) tauri-builder.py \
		--dockerfile ./Dockerfile \
		--frontend-port 3000 \
		--mode dev \
		--hot-reload \
		--devtools \
		--debug

dev-docker: ## Run development mode with docker-compose
	@echo "$(GREEN)Starting development with Docker Compose...$(NC)"
	MODE=dev $(DOCKER_COMPOSE) up tauri-builder

# Docker targets
docker-build: ## Build Docker image
	@echo "$(GREEN)Building Docker image...$(NC)"
	$(DOCKER) build -t $(PROJECT_NAME):$(VERSION) .
	$(DOCKER) tag $(PROJECT_NAME):$(VERSION) $(PROJECT_NAME):latest

docker-push: ## Push Docker image to registry
	@echo "$(GREEN)Pushing Docker image...$(NC)"
	$(DOCKER) push $(PROJECT_NAME):$(VERSION)
	$(DOCKER) push $(PROJECT_NAME):latest

docker-run: ## Run Docker container
	@echo "$(GREEN)Running Docker container...$(NC)"
	$(DOCKER) run -it --rm \
		-v $(PWD):/app \
		-p 3000:3000 \
		$(PROJECT_NAME):latest

docker-compose-up: ## Start all services with docker-compose
	@echo "$(GREEN)Starting Docker Compose services...$(NC)"
	$(DOCKER_COMPOSE) up -d

docker-compose-down: ## Stop all docker-compose services
	@echo "$(YELLOW)Stopping Docker Compose services...$(NC)"
	$(DOCKER_COMPOSE) down

docker-compose-logs: ## Show docker-compose logs
	$(DOCKER_COMPOSE) logs -f

docker-clean: ## Clean Docker resources
	@echo "$(YELLOW)Cleaning Docker resources...$(NC)"
	$(DOCKER_COMPOSE) down -v
	$(DOCKER) system prune -f

# Publishing targets
publish: ## Publish to GitHub Releases
	@echo "$(GREEN)Publishing to GitHub...$(NC)"
	$(PYTHON) tauri-builder.py \
		--dockerfile ./Dockerfile \
		--frontend-port 3000 \
		--mode publish \
		--github-repo $${GITHUB_REPO} \
		--release-tag v$(VERSION) \
		--release-notes ./CHANGELOG.md

publish-test: ## Publish to GitHub as draft
	@echo "$(GREEN)Publishing draft release...$(NC)"
	$(PYTHON) tauri-builder.py \
		--dockerfile ./Dockerfile \
		--frontend-port 3000 \
		--mode publish \
		--github-repo $${GITHUB_REPO} \
		--release-tag v$(VERSION)-test \
		--draft \
		--prerelease

# Code quality targets
lint: ## Run linters
	@echo "$(GREEN)Running linters...$(NC)"
	flake8 tauri_builder.py test_tauri_builder.py
	pylint tauri_builder.py
	mypy tauri_builder.py

format: ## Format code with black and isort
	@echo "$(GREEN)Formatting code...$(NC)"
	black tauri_builder.py test_tauri_builder.py
	isort tauri_builder.py test_tauri_builder.py

check-format: ## Check code formatting
	@echo "$(GREEN)Checking code format...$(NC)"
	black --check tauri_builder.py test_tauri_builder.py
	isort --check-only tauri_builder.py test_tauri_builder.py

security: ## Run security checks
	@echo "$(GREEN)Running security checks...$(NC)"
	bandit -r tauri_builder.py
	safety check

# Documentation targets
docs: ## Generate documentation
	@echo "$(GREEN)Generating documentation...$(NC)"
	sphinx-build -b html docs/ docs/_build/html
	@echo "$(GREEN)Documentation generated in docs/_build/html/index.html$(NC)"

docs-serve: ## Serve documentation locally
	@echo "$(GREEN)Serving documentation...$(NC)"
	cd docs/_build/html && python -m http.server 8000

# Utility targets
clean: ## Clean build artifacts and cache
	@echo "$(YELLOW)Cleaning build artifacts...$(NC)"
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "$(GREEN)Cleanup complete!$(NC)"

version: ## Show current version
	@echo "$(GREEN)Current version: $(VERSION)$(NC)"

bump-version: ## Bump version (usage: make bump-version VERSION=1.2.3)
	@echo "$(GREEN)Bumping version to $(VERSION)...$(NC)"
	echo $(VERSION) > VERSION
	sed -i 's/version=".*"/version="$(VERSION)"/' setup.py
	sed -i 's/version: .*/version: $(VERSION)/' .tauri-builder.yml
	@echo "$(GREEN)Version bumped to $(VERSION)$(NC)"

stats: ## Show project statistics
	@echo "$(GREEN)Project Statistics:$(NC)"
	@echo "Lines of Python code:"
	@wc -l tauri_builder.py test_tauri_builder.py | tail -1
	@echo ""
	@echo "Number of tests:"
	@pytest --collect-only -q 2>/dev/null | tail -1
	@echo ""
	@echo "Docker image size:"
	@$(DOCKER) images $(PROJECT_NAME):latest --format "table {{.Size}}" | tail -1

# CI/CD targets
ci-setup: ## Setup CI environment
	@echo "$(GREEN)Setting up CI environment...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install -e ".[dev]"

ci-test: ## Run CI tests
	@echo "$(GREEN)Running CI tests...$(NC)"
	pytest test_tauri_builder.py -v --junitxml=test-results.xml

ci-build: ## Run CI build
	@echo "$(GREEN)Running CI build...$(NC)"
	$(PYTHON) tauri-builder.py \
		--dockerfile ./Dockerfile \
		--frontend-port 3000 \
		--mode build \
		--platforms linux \
		--arch x64

# Advanced targets
benchmark: ## Run performance benchmarks
	@echo "$(GREEN)Running benchmarks...$(NC)"
	python -m pytest tests/benchmarks/ -v

profile: ## Profile the application
	@echo "$(GREEN)Profiling application...$(NC)"
	python -m cProfile -o profile.stats tauri-builder.py --help
	python -m pstats profile.stats

validate-config: ## Validate configuration files
	@echo "$(GREEN)Validating configuration...$(NC)"
	yamllint .tauri-builder.yml
	yamllint docker-compose.yml
	@echo "$(GREEN)Configuration valid!$(NC)"

# Monitoring targets
monitoring-up: ## Start monitoring stack
	@echo "$(GREEN)Starting monitoring stack...$(NC)"
	$(DOCKER_COMPOSE) --profile monitoring up -d

monitoring-down: ## Stop monitoring stack
	@echo "$(YELLOW)Stopping monitoring stack...$(NC)"
	$(DOCKER_COMPOSE) --profile monitoring down

# Release targets
release-patch: ## Create patch release
	@$(MAKE) bump-version VERSION=$$(echo $(VERSION) | awk -F. '{print $$1"."$$2"."$$3+1}')
	@$(MAKE) publish

release-minor: ## Create minor release
	@$(MAKE) bump-version VERSION=$$(echo $(VERSION) | awk -F. '{print $$1"."$$2+1".0"}')
	@$(MAKE) publish

release-major: ## Create major release
	@$(MAKE) bump-version VERSION=$$(echo $(VERSION) | awk -F. '{print $$1+1".0.0"}')
	@$(MAKE) publish

# Default target when just running 'make'
.DEFAULT_GOAL := help