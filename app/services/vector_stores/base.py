from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from llama_index import Document, VectorStoreIndex, ServiceContext
from llama_index.schema import BaseNode
from enum import Enum

class VectorStoreType(str, Enum):
    IN_MEMORY = "in_memory"
    LOCAL = "local"
    ELASTICSEARCH = "elasticsearch"

class BaseVectorStore(ABC):
    def __init__(self, service_context: ServiceContext):
        self.service_context = service_context
        self.indices: Dict[str, VectorStoreIndex] = {}
    
    @abstractmethod
    def add_documents(self, documents: List[Document], doc_type: str) -> None:
        """Add documents to the vector store"""
        pass
    
    @abstractmethod
    def search(self, query: str, doc_type: str, filters: Optional[Dict] = None, k: int = 5) -> List[BaseNode]:
        """Search for documents"""
        pass
    
    @abstractmethod
    def persist(self) -> None:
        """Persist the vector store to disk or remote storage"""
        pass
    
    @abstractmethod
    def load(self) -> None:
        """Load the vector store from disk or remote storage"""
        pass
