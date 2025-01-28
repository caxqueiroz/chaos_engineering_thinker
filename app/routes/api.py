from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from app.models.schemas import Query, DocumentType, AnalysisResponse
from app.services.session import SessionService
from app.services.llama_store import LlamaStoreService
from app.services.analysis import AnalysisService
from app.guardrails.input_validation import query_validator
from typing import Optional

router = APIRouter()

# Initialize services
llama_store = LlamaStoreService()
session_service = SessionService(llama_store)
analysis_service = AnalysisService(llama_store)

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
    
    # Validate and sanitize query using guardrails
    validated_query, errors = query_validator.validate_query(query.question)
    if errors:
        raise HTTPException(status_code=400, detail={"errors": errors})
    
    try:
        # Analyze system
        result = analysis_service.analyze_system(
            session_id=session_id,
            question=validated_query
        )
        
        return AnalysisResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    session = session_service.get_or_create_session(session_id)
    return session
