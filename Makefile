.PHONY: test test-coverage clean deploy-k8s build-image create-kind-cluster delete-kind-cluster kind-load-image deploy-kind list-kind-clusters select-kind-cluster diagrams install-plantuml

# Variables
PYTHON := python3
KIND_CLUSTER_NAME := chaos-thinker
KIND := kind
PIP := pip3
IMAGE_NAME := chaos-engineering-thinker
IMAGE_TAG := latest
DOCKER_REGISTRY := # Add your registry here
KUBECTL := kubectl
K8S_NAMESPACE := default
PYTHONPATH := $(shell pwd)

# PlantUML
PLANTUML_VERSION := 1.2024.1
PLANTUML_JAR := plantuml.jar
PLANTUML_URL := https://github.com/plantuml/plantuml/releases/download/v$(PLANTUML_VERSION)/plantuml-$(PLANTUML_VERSION).jar
PLANTUML := java -jar $(PLANTUML_JAR)
DIAGRAMS_DIR := docs

# Development setup
install: install-plantuml
	$(PIP) install -r requirements.txt

# Install PlantUML
install-plantuml:
	@echo "Checking for PlantUML..."
	@if [ ! -f "$(PLANTUML_JAR)" ]; then \
		echo "Downloading PlantUML..." && \
		curl -L $(PLANTUML_URL) -o $(PLANTUML_JAR); \
	fi

# Generate diagrams
diagrams: install-plantuml
	@echo "Generating diagrams..."
	@for file in $(DIAGRAMS_DIR)/*.puml; do \
		echo "Processing $$file..." && \
		$(PLANTUML) -tpng $$file; \
	done
	@echo "Diagrams generated in $(DIAGRAMS_DIR)/"

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

# Kind cluster management
list-kind-clusters:
	@echo "Available Kind clusters:"
	@$(KIND) get clusters

select-kind-cluster:
	@if [ -z "$(CLUSTER)" ]; then \
		echo "Error: Please specify a cluster name using CLUSTER=<name>"; \
		exit 1; \
	fi
	@if ! $(KIND) get clusters | grep -q $(CLUSTER); then \
		echo "Error: Cluster '$(CLUSTER)' not found"; \
		exit 1; \
	fi
	$(KIND) export kubeconfig --name $(CLUSTER)
	@echo "Switched to Kind cluster: $(CLUSTER)"
	$(KUBECTL) cluster-info

# Kind cluster management
create-kind-cluster:
	@if ! $(KIND) get clusters | grep -q $(KIND_CLUSTER_NAME); then \
		echo "Creating Kind cluster $(KIND_CLUSTER_NAME)..." && \
		$(KIND) create cluster --name $(KIND_CLUSTER_NAME); \
	else \
		echo "Kind cluster $(KIND_CLUSTER_NAME) already exists."; \
	fi

delete-kind-cluster:
	@if $(KIND) get clusters | grep -q $(KIND_CLUSTER_NAME); then \
		echo "Deleting Kind cluster $(KIND_CLUSTER_NAME)..." && \
		$(KIND) delete cluster --name $(KIND_CLUSTER_NAME); \
	else \
		echo "Kind cluster $(KIND_CLUSTER_NAME) does not exist."; \
	fi

kind-load-image: build-image
	$(KIND) load docker-image $(IMAGE_NAME):$(IMAGE_TAG) --name $(KIND_CLUSTER_NAME)

deploy-kind: create-kind-cluster kind-load-image
	$(KUBECTL) apply -f k8s/ -n $(K8S_NAMESPACE)

# Help target
help:
	@echo "Available targets:"
	@echo "  install            : Install Python dependencies"
	@echo "  test              : Run tests"
	@echo "  test-coverage     : Run tests with coverage report"
	@echo "  clean             : Remove Python cache and build artifacts"
	@echo "  build-image       : Build Docker image"
	@echo "  deploy-k8s        : Deploy to Kubernetes"
	@echo "  create-kind-cluster: Create a Kind Kubernetes cluster"
	@echo "  delete-kind-cluster: Delete the Kind Kubernetes cluster"
	@echo "  kind-load-image   : Load Docker image into Kind cluster"
	@echo "  deploy-kind       : Deploy to Kind cluster (creates cluster if needed)"
	@echo "  list-kind-clusters : List all available Kind clusters"
	@echo "  select-kind-cluster: Select a Kind cluster (usage: make select-kind-cluster CLUSTER=<name>)"
