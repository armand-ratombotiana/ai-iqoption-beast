.PHONY: help install dev test lint format clean run docker-build docker-run

help:
	@echo "IQOption AI Trading Bot - Available Commands:"
	@echo ""
	@echo "  make install       - Install production dependencies"
	@echo "  make dev           - Install development dependencies"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Run linting"
	@echo "  make format        - Format code with black"
	@echo "  make clean         - Clean build artifacts"
	@echo "  make run           - Run development server"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-run    - Run Docker container"
	@echo ""

install:
	pip install -r requirements.txt

dev:
	pip install -r requirements.txt
	pip install -e ".[dev]"

test:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term

lint:
	flake8 src/ tests/
	mypy src/

format:
	black src/ tests/ scripts/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf __pycache__
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

run:
	python app.py

docker-build:
	docker build -t iqoption-trading-bot:latest -f docker/Dockerfile .

docker-run:
	docker-compose -f docker/docker-compose.yml up

docker-stop:
	docker-compose -f docker/docker-compose.yml down
