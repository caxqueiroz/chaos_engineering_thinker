# Chaos Assistant

ChaosThinker is an AI-powered system analysis tool that helps users understand and analyze their application infrastructure using natural language queries. It uses FastAPI for the REST API, LangGraph for workflow management, and Ollama for LLM capabilities.

## Prerequisites

- Python 3.8+
- Access to a LLM model. Currently, the system uses Ollama for LLM capabilities.
- Ollama server running with the deepseek-r1:70b model
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
- XLSX
- PDF
- DOCX

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
- Vector store-based document storage using In-memory, local or elasticsearch
- LangGraph-powered analysis workflow
- Integration with Ollama LLM and other LLMs
- Support for various document types

## Architecture Overview

### Core Components
```text
├── app/
│   ├── api/                   # FastAPI service and routes
│   │   └── routes/           # API endpoint definitions
│   ├── services/             # Core service implementations
│   │   ├── document_processor.py   # Document analysis and processing
│   │   ├── content_extractors/     # File type-specific extractors
│   │   │   ├── pdf_extractor.py
│   │   │   ├── docx_extractor.py
│   │   │   └── xlsx_extractor.py
│   │   ├── diagram_analysis/      # Technical diagram processing
│   │   │   ├── detector.py
│   │   │   └── analyzers/
│   │   └── vector_stores/        # Vector storage implementations
│   │       ├── elasticsearch.py
│   │       ├── local.py
│   │       └── in_memory.py
│   ├── agents/               # Intelligent agents
│   │   ├── chaos_agent.py
│   │   ├── experiment_designer.py
│   │   └── orchestrator.py
│   ├── intelligence/        # AI-driven experimentation
│   │   ├── experiment_planner.py
│   │   ├── experiment_predictor.py
│   │   ├── memory_store.py
│   │   └── templates.py
│   └── guardrails/          # Validation and safety checks
       ├── input_validator.py
       ├── safety_validator.py
       └── risk_analyzer.py
```

### Technical Stack
```python
# Core Dependencies
fastapi         # API framework
pydantic        # Data validation
langchain       # LLM orchestration
chaostoolkit    # Chaos engineering toolkit

# Document Processing
PyPDF2          # PDF processing
python-docx     # DOCX processing
openpyxl        # XLSX processing
Pillow          # Image processing

# Storage & Search
elasticsearch   # Vector store and search
psycopg2        # PostgreSQL client
s3fs            # S3 storage integration

# AI & ML
openai          # LLM integration
numpy           # Numerical computations
scikit-learn    # ML utilities

# Infrastructure
python-kubernetes  # K8s integration
uvicorn            # ASGI server
```

### Infrastructure
```text
├── k8s/                    # Kubernetes deployment
│   ├── deployment.yaml     # K8s manifests
│   ├── service.yaml        # Service definitions
│   └── configmap.yaml      # Configuration
├── docs/                   # Documentation
│   ├── architecture.puml   # System architecture in PlantUML
│   └── architecture.png    # Generated architecture diagram
└── Dockerfile             # Containerization
```

## Architecture

Below is the high-level architecture diagram of the ChaosThinker system:

![Architecture Diagram](docs/Chaos%20Engineering%20Thinker%20Architecture.png)

The architecture consists of several key components:

- **API Layer**: FastAPI service handling external requests and routing

- **Intelligent Agents**:
  - Chaos Agent: Orchestrates chaos engineering operations
  - Experiment Designer: Creates and validates experiments
  - Orchestrator: Coordinates agent activities
  - Intelligence Core: Planning, prediction, and memory components

- **Document Processing**:
  - Content Extractors: Handle PDF, DOCX, and XLSX files
  - Technical Diagram Analysis: Detect and analyze technical diagrams
  - Diagram-to-Text Conversion: Generate descriptive text from diagrams

- **Experiment Generation**:
  - Code Generator: Creates experiment implementations
  - Template Engine: Manages experiment templates
  - Generator: Coordinates experiment creation

- **Storage Layer**:
  - Document Storage: Local and S3 storage options
  - Vector Stores: Elasticsearch for vector search
  - PostgreSQL: Document metadata and experiment history

- **Guardrails & Validation**:
  - Input Validation: Request validation
  - Safety Validation: Security checks
  - Risk Analysis: Experiment safety assessment
  - Experiment Validation: Ensures experiment validity

- **LLM Integration**:
  - OpenAI Service: Powers intelligent operations
  - Prompt Templates: Structured LLM interactions

## System Flow

### 1. Document Processing Pipeline

#### Document Upload and Processing
- Users upload documents via `/api/documents/upload`
- Supported document types:
  - PDF: Technical documentation, architecture diagrams
  - DOCX: System specifications, design documents
  - XLSX: Configuration data, system inventories
- Each document goes through:
  1. Content Extraction based on file type
  2. Technical Diagram Detection and Analysis
  3. Text and Metadata Extraction
  4. Vector Embedding Generation

#### Technical Diagram Processing
- Automatic detection of diagram types:
  - Network Topology Diagrams
  - Class Diagrams
  - Sequence Diagrams
  - Data Schema Diagrams
- For each diagram:
  1. Image extraction and preprocessing
  2. Diagram type classification
  3. Specialized analysis based on type
  4. Generation of descriptive text for LLM reasoning

### 2. Knowledge Base Construction

#### Storage Layer Integration
- Document Storage:
  - Raw files stored in Local Storage or S3
  - Extracted text and metadata in PostgreSQL
- Vector Storage:
  - Document embeddings in Elasticsearch
  - Fast similarity search capabilities
  - Metadata indexing for filtered searches

#### Intelligent Processing
- LLM Integration:
  - Diagram-to-text conversion
  - Technical content understanding
  - Context-aware responses
- Knowledge Graph Construction:
  - Entity extraction from documents
  - Relationship mapping
  - System topology understanding

### 3. Experiment Design and Generation

#### Analysis Phase
- System Understanding:
  - Document analysis for system components
  - Architecture pattern recognition
  - Dependency mapping
- Risk Assessment:
  - Component criticality analysis
  - Failure impact prediction
  - Safety boundary identification

#### Experiment Creation
- Intelligent Design:
  - Context-aware experiment planning
  - Safety-first approach
  - Resource consideration
- Validation Pipeline:
  1. Input validation for safety
  2. Risk level assessment
  3. Safety checks and guardrails
  4. Experiment validation

### 4. Safety and Validation

#### Multi-layer Validation
- Input Validation:
  - Request format and content validation
  - Parameter bounds checking
  - Resource limit validation

#### Safety Checks
- Risk Analysis:
  - Component impact assessment
  - Blast radius calculation
  - Recovery path validation
- Safety Guardrails:
  - Automatic safety boundary enforcement
  - Resource protection mechanisms
  - Critical service preservation

### 5. API Integration

- RESTful API Endpoints:
  - `/api/documents/*`: Document management
  - `/api/analysis/*`: System analysis
  - `/api/experiments/*`: Experiment operations
  - `/api/safety/*`: Safety validations

- Asynchronous Operations:
  - Long-running process handling
  - Progress tracking
  - Status notifications

- Integration Features:
  - OpenAPI documentation
  - Authentication and authorization
  - Rate limiting and quotas
  - Detailed error reporting
