from typing import List, Dict, Any, Optional
from llama_index import Document, VectorStoreIndex, ServiceContext
from llama_index.schema import BaseNode
from llama_index.vector_stores import ChromaVectorStore
import chromadb
from .base import BaseVectorStore

class InMemoryVectorStore(BaseVectorStore):
    def __init__(self, service_context: ServiceContext):
        super().__init__(service_context)
        
        # Initialize Chroma client in-memory
        self.chroma_client = chromadb.Client()
        self.vector_stores: Dict[str, ChromaVectorStore] = {}
    
    def _get_vector_store(self, doc_type: str) -> ChromaVectorStore:
        """Get or create Chroma vector store for document type"""
        if doc_type not in self.vector_stores:
            # Create collection for document type
            collection = self.chroma_client.create_collection(
                name=f"collection_{doc_type}",
                metadata={"doc_type": doc_type}
            )
            
            # Create vector store
            self.vector_stores[doc_type] = ChromaVectorStore(
                chroma_collection=collection
            )
            
            # Create index
            self.indices[doc_type] = VectorStoreIndex.from_documents(
                [],  # Empty list as we're creating a new index
                service_context=self.service_context,
                vector_store=self.vector_stores[doc_type]
            )
        
        return self.vector_stores[doc_type]
    
    def add_documents(self, documents: List[Document], doc_type: str) -> None:
        """Add documents to in-memory Chroma vector store"""
        vector_store = self._get_vector_store(doc_type)
        
        if doc_type not in self.indices:
            self.indices[doc_type] = VectorStoreIndex.from_documents(
                documents,
                service_context=self.service_context,
                vector_store=vector_store
            )
        else:
            self.indices[doc_type].insert_nodes(documents)
    
    def search(self, query: str, doc_type: str, filters: Optional[Dict] = None, k: int = 5) -> List[BaseNode]:
        """Search for documents in Chroma"""
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
