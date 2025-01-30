.PHONY: test test-coverage clean deploy-k8s build-image

# Variables
PYTHON := python3
PIP := pip3
IMAGE_NAME := chaos-engineering-thinker
IMAGE_TAG := latest
DOCKER_REGISTRY := # Add your registry here
KUBECTL := kubectl
K8S_NAMESPACE := default
PYTHONPATH := $(shell pwd)

# Development setup
install:
	$(PIP) install -r requirements.txt

# Testing
test:
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m pytest tests/ -v

test-coverage:
	pytest tests/ --cov=app --cov-report=term-missing

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +

# Docker
build-image:
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

# Kubernetes deployment
deploy-k8s: build-image
	$(KUBECTL) apply -f k8s/ -n $(K8S_NAMESPACE)

# Help target
help:
	@echo "Available targets:"
	@echo "  install        : Install Python dependencies"
	@echo "  test          : Run tests"
	@echo "  test-coverage : Run tests with coverage report"
	@echo "  clean         : Remove Python cache and build artifacts"
	@echo "  build-image   : Build Docker image"
	@echo "  deploy-k8s    : Deploy to Kubernetes"
