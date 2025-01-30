from pydantic import BaseModel, Field
from typing import List, Dict, Any
from datetime import datetime
from enum import Enum

class DocumentType(str, Enum):
    NETWORK_TOPOLOGY = "network_topology"
    TECH_STACK = "tech_stack"
    NETWORK_IPS = "network_ips"
    DATABASES = "databases"
    INFRASTRUCTURE = "infrastructure"

class DocumentInfo(BaseModel):
    filename: str
    hash: str
    doc_type: DocumentType
    file_path: str
    upload_time: str
    metadata: Dict[str, Any]

class Session(BaseModel):
    id: str
    created_at: datetime
    documents: List[DocumentInfo] = []

class Query(BaseModel):
    session_id: str
    question: str
    
class AnalysisResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = Field(default_factory=dict)
