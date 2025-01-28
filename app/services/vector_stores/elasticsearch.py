from typing import List, Dict, Any, Optional
from llama_index import Document, VectorStoreIndex, ServiceContext
from llama_index.schema import BaseNode
from llama_index.vector_stores.elasticsearch import ElasticsearchStore
from elasticsearch import Elasticsearch
from .base import BaseVectorStore

class ElasticsearchVectorStore(BaseVectorStore):
    def __init__(
        self,
        service_context: ServiceContext,
        hosts: List[str],
        index_prefix: str = "chaos_thinker",
        es_config: Optional[Dict[str, Any]] = None
    ):
        super().__init__(service_context)
        self.index_prefix = index_prefix
        self.es_config = es_config or {}
        
        # Initialize Elasticsearch client
        self.es_client = Elasticsearch(hosts=hosts, **self.es_config)
        self.vector_stores: Dict[str, ElasticsearchStore] = {}
    
    def _get_vector_store(self, doc_type: str) -> ElasticsearchStore:
        """Get or create Elasticsearch vector store for document type"""
        if doc_type not in self.vector_stores:
            index_name = f"{self.index_prefix}_{doc_type}"
            self.vector_stores[doc_type] = ElasticsearchStore(
                es_client=self.es_client,
                index_name=index_name,
                embedding_dimension=384  # Adjust based on your embedding model
            )
        return self.vector_stores[doc_type]
    
    def add_documents(self, documents: List[Document], doc_type: str) -> None:
        """Add documents to Elasticsearch"""
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
        """Search for documents in Elasticsearch"""
        if doc_type not in self.indices:
            return []
        
        query_engine = self.indices[doc_type].as_query_engine(
            similarity_top_k=k,
            filters=filters
        )
        response = query_engine.query(query)
        return response.source_nodes
    
    def persist(self) -> None:
        """No explicit persistence needed for Elasticsearch"""
        pass
    
    def load(self) -> None:
        """Load indices from Elasticsearch"""
        # Get all indices with our prefix
        indices = self.es_client.indices.get(index=f"{self.index_prefix}_*")
        
        for index_name in indices:
            doc_type = index_name.replace(f"{self.index_prefix}_", "")
            vector_store = self._get_vector_store(doc_type)
            
            self.indices[doc_type] = VectorStoreIndex.from_documents(
                [],  # Empty list as we're loading from Elasticsearch
                service_context=self.service_context,
                vector_store=vector_store
            )
