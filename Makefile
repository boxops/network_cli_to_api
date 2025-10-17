# Makefile for Network API Gateway

.PHONY: help install dev test coverage clean run docker-build docker-run format lint

help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make dev          - Install dev dependencies"
	@echo "  make test         - Run tests"
	@echo "  make coverage     - Run tests with coverage"
	@echo "  make run          - Run the application"
	@echo "  make format       - Format code with black"
	@echo "  make lint         - Run linters"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run   - Run Docker container"
	@echo "  make clean        - Clean up temporary files"

install:
	pip install -r requirements.txt

dev: install
	pip install pytest pytest-asyncio pytest-cov black flake8 mypy

test:
	pytest -v

coverage:
	pytest --cov=app --cov-report=html --cov-report=term

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

format:
	black app/ tests/

lint:
	flake8 app/ tests/
	mypy app/

docker-build:
	docker build -t network-api-gateway .

docker-run:
	docker-compose up -d

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache .coverage htmlcov dist build

.DEFAULT_GOAL := help
