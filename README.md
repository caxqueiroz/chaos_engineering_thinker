# ChaosThinker

ChaosThinker is an AI-powered system analysis tool that helps users understand and analyze their application infrastructure using natural language queries. It uses FastAPI for the REST API, LangGraph for workflow management, and Ollama for LLM capabilities.

## Prerequisites

- Python 3.8+
- Ollama installed and running locally with the llama2 model
- Virtual environment (recommended)

## Installation

1. Clone the repository
2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Make sure Ollama is running with the deepseek-r1:70b model:
```bash
ollama run --model deepseek-r1:70b
```

2. Start the FastAPI server:
```bash
python app/main.py
```

The server will start at http://localhost:8000

## API Usage

### 1. Create a Session
```bash
curl -X POST http://localhost:8000/sessions
```

### 2. Add Documents
```bash
curl -X POST http://localhost:8000/sessions/{session_id}/documents \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Our application uses a microservices architecture...",
    "doc_type": "tech_stack",
    "metadata": {"service": "main-app"}
  }'
```

Document types:
- network_topology
- tech_stack
- network_ips
- databases
- infrastructure

### 3. Query the System
```bash
curl -X POST http://localhost:8000/sessions/{session_id}/query \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id",
    "question": "What are the potential points of failure in our current architecture?"
  }'
```

## Features

- Session-based document management
- Vector store-based document storage using Chroma
- LangGraph-powered analysis workflow
- Integration with Ollama LLM
- Support for various infrastructure document types

## Architecture Overview

### Core Components
```text
├── app/
│   ├── services/                # Core service implementations
│   │   ├── vector_store.py       - Vector store management
│   │   ├── document_processor/  - Analysis pipelines
│   │   └── vector_stores/       - Embedding storage
│   └── agents/
│       └── intelligence/       # AI-driven experimentation
│           ├── experiment_planner.py
│           ├── experiment_predictor.py
│           └── memory_store.py
```

### Technical Stack
```python
# Key Dependencies
chaostoolkit    # Chaos engineering toolkit
langchain       # LLM integration
pydantic        # Data validation
chromadb        # Vector storage
python-kubernetes # K8s integration
```

### Infrastructure
```text
├── openshift/                 # Cloud-native deployment
│   ├── deployment.yaml        # K8s config
│   └── deploy.sh              # CI/CD automation
└── Dockerfile                 # Containerization
```

## Architecture

Below is the high-level architecture diagram of the ChaosThinker system:

![Architecture Diagram](docs/images/architecture.png)

The architecture consists of several key components:
- **API Layer**: Handles all external requests and routes them to appropriate handlers
- **Agents**: Intelligent components that perform specific tasks:
  - Chaos Agent: Manages chaos engineering operations
  - Experiment Designer: Designs and validates experiments
  - Intelligence components for planning and prediction
- **Services**: Core functionality implementations:
  - Document Analysis: Processes and analyzes various document types
  - Experiment Generation: Creates and manages experiments
  - Storage: Handles data persistence
  - Vector Stores: Manages document embeddings and similarity search
- **Guardrails**: Ensures system safety and input validation
- **Models**: Defines data schemas and structures

## Flow
1. Session Creation:
  Users start by creating a session via /api/sessions
  This gives them a unique session ID to track their analysis
2. Document Upload:
  - Users can upload various types of system documentation via /api/sessions/{session_id}/documents
  - Supported document types include:
      - Network topology
      - Tech stack information
      - Network IPs
      - Databases
      - Infrastructure
  - Each document is processed and stored for analysis
3. System Analysis:
  - Users can query their system via /api/sessions/{session_id}/query
  - They can ask questions about their system architecture
  - The system analyzes the uploaded documents and provides detailed answers
  - Responses include both the answer and the sources used to generate it
4. Experiment Generation:
  - Users can request chaos engineering experiments via /api/sessions/{session_id}/experiments
  - They specify their platform (Kubernetes or Docker) and any configuration
  - The system generates experiments of various types:
    - Network failures
    - Latency injection
    - Resource exhaustion
    - Process failures
    - Dependency failures
  - Each experiment includes:
    - A clear description and hypothesis
    - Success criteria
    - Safety validation results
    - Implementation code
    - Deployment, rollback, and validation steps
5. Safety Measures:
  - All experiments go through safety validation
  - Risk levels are assigned (LOW, MEDIUM, HIGH, CRITICAL)
  - Safety checks provide detailed feedback including:
    - Violations
    - Warnings
    - Recommendations
  - The system essentially acts as an AI-powered assistant that helps users:
    - Understand their system architecture through document analysis
    - Generate safe and relevant chaos engineering experiments
    - Implement and validate these experiments in their environment
  - All interactions are done through a REST API, making it easy to integrate with existing tools and workflows.