from typing import List, Dict, Any, Optional
from llama_index import Document, VectorStoreIndex, ServiceContext
from llama_index.schema import BaseNode
from .base import BaseVectorStore

class InMemoryVectorStore(BaseVectorStore):
    def __init__(self, service_context: ServiceContext):
        super().__init__(service_context)
    
    def add_documents(self, documents: List[Document], doc_type: str) -> None:
        """Add documents to in-memory vector store"""
        if doc_type not in self.indices:
            self.indices[doc_type] = VectorStoreIndex.from_documents(
                documents,
                service_context=self.service_context
            )
        else:
            self.indices[doc_type].insert_nodes(documents)
    
    def search(self, query: str, doc_type: str, filters: Optional[Dict] = None, k: int = 5) -> List[BaseNode]:
        """Search for documents in memory"""
        if doc_type not in self.indices:
            return []
        
        query_engine = self.indices[doc_type].as_query_engine(
            similarity_top_k=k,
            filters=filters
        )
        response = query_engine.query(query)
        return response.source_nodes
    
    def persist(self) -> None:
        """No persistence for in-memory store"""
        pass
    
    def load(self) -> None:
        """No loading for in-memory store"""
        pass
