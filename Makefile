# Database configuration
export PG_HOST=localhost
export PG_PORT=5432
export PG_USER=root
export PG_PASSWORD=example
export PG_DB=postgres

# Default target
.DEFAULT_GOAL := help

# Phony targets
.PHONY: server setup db down lint test env help clean install format check

# Run the API server
server:
	@echo "Starting API server..."
	@poetry run python api.py

# Generate test data
setup: db
	@echo "Waiting for database to be ready..."
	@sleep 3
	@echo "Generating test data..."
	@poetry run python generate_test_data.py

# Start database container
db:
	@echo "Starting PostgreSQL database..."
	@docker compose up -d
	@echo "Database started on $(PG_HOST):$(PG_PORT)"

# Stop and remove database container
down:
	@echo "Stopping database..."
	@docker compose down -v

# Run linting checks
lint:
	@echo "Running linting checks..."
	@poetry run flake8 api.py
	@poetry run mypy api.py
	@poetry run black --check api.py
	@poetry run isort --check-only api.py

# Run tests
test:
	@echo "Running tests..."
	@poetry run pytest -v

# Install dependencies
install:
	@echo "Installing dependencies..."
	@poetry install

# Run all checks (lint + test)
check: lint test
	@echo "All checks passed!"

# Clean up generated files
clean:
	@echo "Cleaning up..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@rm -rf .pytest_cache
	@rm -rf .coverage
	@rm -rf htmlcov
	@rm -rf .mypy_cache

# Help target
help:
	@echo "Available targets:"
	@echo "  make server      - Run the API server"
	@echo "  make setup       - Start database and generate test data"
	@echo "  make db          - Start PostgreSQL database container"
	@echo "  make down        - Stop and remove database container"
	@echo "  make test        - Run tests"
	@echo "  make test-cov    - Run tests with coverage report"
	@echo "  make lint        - Run linting checks (flake8, mypy, black, isort)"
	@echo "  make format      - Auto-format code with black and isort"
	@echo "  make check       - Run all checks (lint + test)"
	@echo "  make clean       - Clean up generated files"
	@echo "  make install     - Install dependencies with poetry"
	@echo "  make env         - Show environment variables"
	@echo "  make help        - Show this help message"