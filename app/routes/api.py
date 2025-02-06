from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from app.models.schemas import Query, DocumentType, AnalysisResponse, ExperimentRequest, ExperimentResponse
from app.services.session import SessionService
from app.services.vector_store import VectorStoreService
from app.services.analysis import AnalysisService
from app.services.experiment_generation.generator import ExperimentGenerator
from app.services.experiment_generation.code_generator import ExperimentCodeGenerator
from app.services.validation.safety_validator import SafetyValidator
from app.guardrails.input_validation import query_validator
from typing import Optional, List

router = APIRouter()

# Initialize services
vector_store = VectorStoreService()
session_service = SessionService(vector_store)
analysis_service = AnalysisService(vector_store)
experiment_generator = ExperimentGenerator()
code_generator = ExperimentCodeGenerator()
safety_validator = SafetyValidator()

@router.post("/sessions")
async def create_session():
    session = session_service.get_or_create_session()
    return {"session_id": session.id}

@router.post("/sessions/{session_id}/documents")
async def add_document(
    session_id: str,
    file: UploadFile = File(...),
    doc_type: DocumentType = Form(...),
):
    # Validate document type
    if not isinstance(doc_type, DocumentType):
        raise HTTPException(status_code=400, detail=f"Invalid document type. Must be one of: {', '.join([t.value for t in DocumentType])}")
    
    try:
        # Read file content
        content = await file.read()
        
        # Process and store document
        result = session_service.process_and_store_document(
            session_id=session_id,
            file_content=content,
            filename=file.filename,
            doc_type=doc_type.value
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/sessions/{session_id}/query", response_model=AnalysisResponse)
async def query_system(session_id: str, query: Query):
    # Check if session exists
    if session_id not in session_service.sessions:
        raise HTTPException(status_code=404, detail="Session not found")
        
    try:
        # Validate query
        validated_query = query_validator(query.query)
        
        # Get analysis results
        results = await analysis_service.analyze_query(
            session_id=session_id,
            query=validated_query
        )
        
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/sessions/{session_id}/experiments", response_model=List[ExperimentResponse])
async def generate_experiments(session_id: str, request: ExperimentRequest):
    """Generate chaos engineering experiments based on system analysis."""
    # Check if session exists
    if session_id not in session_service.sessions:
        raise HTTPException(status_code=404, detail="Session not found")
        
    try:
        # Get system analysis from session
        system_analysis = session_service.get_system_analysis(session_id)
        
        # Generate experiments
        experiments = await experiment_generator.generate_experiments(system_analysis)
        
        # Validate experiments
        validated_experiments = []
        for exp in experiments:
            validation = safety_validator.validate_experiment(exp, system_analysis)
            if validation["is_safe"]:
                # Generate implementation code
                code = await code_generator.generate_code(
                    experiment=exp,
                    platform=request.platform,
                    config=request.platform_config
                )
                validated_experiments.append({
                    **exp,
                    "validation": validation,
                    "implementation": code
                })
                
        return validated_experiments
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session details."""
    if session_id not in session_service.sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return session_service.sessions[session_id]
