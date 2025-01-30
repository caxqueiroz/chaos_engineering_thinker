from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class DocumentType(str, Enum):
    NETWORK_TOPOLOGY = "network_topology"
    TECH_STACK = "tech_stack"
    NETWORK_IPS = "network_ips"
    DATABASES = "databases"
    INFRASTRUCTURE = "infrastructure"

class ExperimentType(str, Enum):
    NETWORK_FAILURE = "network_failure"
    LATENCY_INJECTION = "latency_injection"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    PROCESS_FAILURE = "process_failure"
    DEPENDENCY_FAILURE = "dependency_failure"

class Platform(str, Enum):
    KUBERNETES = "kubernetes"
    DOCKER = "docker"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

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

class ExperimentParameters(BaseModel):
    target_component: str
    duration: str
    failure_type: Optional[str] = None
    latency_ms: Optional[int] = None
    resource_type: Optional[str] = None
    intensity: Optional[float] = None
    frequency: Optional[str] = None

class SafetyCheck(BaseModel):
    name: str
    description: str
    passed: bool
    details: Optional[str] = None
    recommendation: Optional[str] = None

class ValidationResult(BaseModel):
    is_safe: bool
    risk_level: RiskLevel
    violations: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []
    recommendations: List[Dict[str, Any]] = []

class Implementation(BaseModel):
    code: str
    deployment_steps: List[str]
    rollback_steps: List[str]
    validation_steps: List[str]

class ExperimentRequest(BaseModel):
    platform: Platform
    platform_config: Dict[str, Any]
    constraints: Optional[Dict[str, Any]] = None

class ExperimentResponse(BaseModel):
    name: str
    description: str
    type: ExperimentType
    parameters: ExperimentParameters
    hypothesis: str
    success_criteria: List[str]
    validation: ValidationResult
    implementation: Implementation
