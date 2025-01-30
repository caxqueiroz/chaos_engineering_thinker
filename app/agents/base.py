from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from app.services.document_processor import DocumentProcessor

class Agent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(self, name: str, description: str, document_processor: Optional[DocumentProcessor] = None):
        self.name = name
        self.description = description
        self.document_processor = document_processor or DocumentProcessor()
        
    @abstractmethod
    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process the input context and return results."""
        pass
    
    @abstractmethod
    async def validate(self, input_data: Dict[str, Any]) -> bool:
        """Validate the input data before processing."""
        pass
    
    async def process_document(self, document_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Process a document and extract relevant information."""
        # This will be implemented by specific agents based on their needs
        raise NotImplementedError
    
    async def answer_question(self, question: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Answer a question based on the available context."""
        # This will be implemented by specific agents based on their needs
        raise NotImplementedError
