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

1. Make sure Ollama is running with the llama2 model:
```bash
ollama run llama2
```

2. Start the FastAPI server:
```bash
python main.py
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
