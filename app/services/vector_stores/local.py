from typing import List, Dict, Any, Optional
import os
from llama_index import Document, VectorStoreIndex, ServiceContext, StorageContext
from llama_index.schema import BaseNode
from llama_index.storage.docstore import SimpleDocumentStore
from llama_index.storage.index_store import SimpleIndexStore
from llama_index.vector_stores import SimpleVectorStore
from .base import BaseVectorStore

class LocalVectorStore(BaseVectorStore):
    def __init__(self, service_context: ServiceContext, persist_dir: str = "./data/vector_store"):
        super().__init__(service_context)
        self.persist_dir = persist_dir
        self.storage_contexts: Dict[str, StorageContext] = {}
        
        # Create persist directory if it doesn't exist
        os.makedirs(persist_dir, exist_ok=True)
    
    def _get_storage_context(self, doc_type: str) -> StorageContext:
        """Get or create storage context for document type"""
        if doc_type not in self.storage_contexts:
            type_dir = os.path.join(self.persist_dir, doc_type)
            os.makedirs(type_dir, exist_ok=True)
            
            self.storage_contexts[doc_type] = StorageContext.from_defaults(
                docstore=SimpleDocumentStore.from_persist_dir(persist_dir=type_dir),
                index_store=SimpleIndexStore.from_persist_dir(persist_dir=type_dir),
                vector_store=SimpleVectorStore.from_persist_dir(persist_dir=type_dir)
            )
        
        return self.storage_contexts[doc_type]
    
    def add_documents(self, documents: List[Document], doc_type: str) -> None:
        """Add documents to local vector store"""
        storage_context = self._get_storage_context(doc_type)
        
        if doc_type not in self.indices:
            self.indices[doc_type] = VectorStoreIndex.from_documents(
                documents,
                service_context=self.service_context,
                storage_context=storage_context
            )
        else:
            self.indices[doc_type].insert_nodes(documents)
        
        self.persist()
    
    def search(self, query: str, doc_type: str, filters: Optional[Dict] = None, k: int = 5) -> List[BaseNode]:
        """Search for documents in local storage"""
        if doc_type not in self.indices:
            return []
        
        query_engine = self.indices[doc_type].as_query_engine(
            similarity_top_k=k,
            filters=filters
        )
        response = query_engine.query(query)
        return response.source_nodes
    
    def persist(self) -> None:
        """Persist indices to disk"""
        for doc_type, index in self.indices.items():
            index.storage_context.persist(persist_dir=os.path.join(self.persist_dir, doc_type))
    
    def load(self) -> None:
        """Load indices from disk"""
        if not os.path.exists(self.persist_dir):
            return
        
        for doc_type in os.listdir(self.persist_dir):
            type_dir = os.path.join(self.persist_dir, doc_type)
            if os.path.isdir(type_dir):
                storage_context = self._get_storage_context(doc_type)
                self.indices[doc_type] = VectorStoreIndex.from_documents(
                    [],  # Empty list as we're loading from storage
                    service_context=self.service_context,
                    storage_context=storage_context
                )
