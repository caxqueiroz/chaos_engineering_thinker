from datetime import datetime
import uuid
from typing import Optional, Dict, Any
from app.models.schemas import Session
from app.services.document_processor import DocumentProcessor
from app.services.vector_store import VectorStoreService

class SessionService:
    def __init__(self, vector_store: VectorStoreService):
        self.sessions: Dict[str, Session] = {}
        self.document_processor = DocumentProcessor()
        self.vector_store = vector_store
    
    def get_or_create_session(self, session_id: Optional[str] = None) -> Session:
        if session_id and session_id in self.sessions:
            return self.sessions[session_id]
            
        new_session_id = session_id or str(uuid.uuid4())
        self.sessions[new_session_id] = Session(
            id=new_session_id,
            created_at=datetime.now(),
            documents=[]
        )
        return self.sessions[new_session_id]
    
    def process_and_store_document(self, session_id: str, file_content: bytes, filename: str, doc_type: str) -> Dict[str, Any]:
        """Process uploaded document, store it, and add to LlamaIndex"""
        # Get or create session
        session = self.get_or_create_session(session_id)
        
        try:
            # Process and save document
            file_path, metadata = self.document_processor.save_document(
                content=file_content,
                filename=filename,
                doc_type=doc_type
            )
            
            # Add session information to metadata
            metadata['session_id'] = session_id
            
            # Add to LlamaIndex
            self.vector_store.add_document(
                file_path=file_path,
                doc_type=doc_type,
                metadata=metadata
            )
            
            # Update session with document info
            session.documents.append({
                'filename': filename,
                'doc_type': doc_type,
                'file_path': file_path,
                'upload_time': metadata['upload_time'],
                'metadata': metadata
            })
            
            return {
                'status': 'success',
                'file_path': file_path,
                'metadata': metadata,
                'document_count': len(session.documents)
            }
            
        except Exception as e:
            raise Exception(f"Error processing document: {str(e)}")
