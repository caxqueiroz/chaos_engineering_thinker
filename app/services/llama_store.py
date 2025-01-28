from typing import List, Dict, Any, Optional
from llama_index import (
    SimpleDirectoryReader,
    ServiceContext,
    load_index_from_storage,
)
from llama_index.node_parser import SimpleNodeParser
from llama_index.schema import Document, ImageDocument
from llama_index.query_engine import RouterQueryEngine
from llama_index.tools import QueryEngineTool
from llama_index.llms import Ollama
from .vector_stores.base import BaseVectorStore, VectorStoreType
from .vector_stores.in_memory import InMemoryVectorStore
from .vector_stores.local import LocalVectorStore
from .vector_stores.elasticsearch import ElasticsearchVectorStore
import os

class LlamaStoreService:
    def __init__(
        self,
        store_type: VectorStoreType = VectorStoreType.LOCAL,
        persist_directory: str = "./data/llamaindex",
        es_hosts: Optional[List[str]] = None,
        es_config: Optional[Dict[str, Any]] = None
    ):
        self.llm = Ollama(model="llama2")
        self.service_context = ServiceContext.from_defaults(
            llm=self.llm,
            embed_model="local"
        )
        
        # Initialize vector store based on type
        if store_type == VectorStoreType.IN_MEMORY:
            self.vector_store = InMemoryVectorStore(self.service_context)
        elif store_type == VectorStoreType.LOCAL:
            self.vector_store = LocalVectorStore(
                self.service_context,
                persist_dir=persist_directory
            )
        elif store_type == VectorStoreType.ELASTICSEARCH:
            if not es_hosts:
                raise ValueError("Elasticsearch hosts must be provided for Elasticsearch vector store")
            self.vector_store = ElasticsearchVectorStore(
                self.service_context,
                hosts=es_hosts,
                es_config=es_config
            )
        
        # Load existing data
        self.vector_store.load()
    
    def add_document(self, file_path: str, doc_type: str, metadata: Optional[Dict] = None) -> None:
        """Add a document to the appropriate index"""
        # Load document based on type
        if doc_type == "network_topology":
            documents = SimpleDirectoryReader(
                input_files=[file_path],
                filename_as_id=True,
                image_parser=True
            ).load_data()
        else:
            documents = SimpleDirectoryReader(
                input_files=[file_path],
                filename_as_id=True
            ).load_data()
        
        # Add metadata
        for doc in documents:
            doc.metadata.update(metadata or {})
        
        # Add to vector store
        self.vector_store.add_documents(documents, doc_type)
    
    def create_query_engine(self, session_id: str) -> RouterQueryEngine:
        """Create a router query engine that can handle different types of queries"""
        query_engine_tools = []
        
        # Create query engine for each document type
        for doc_type in self.vector_store.indices.keys():
            # Create query engine with metadata filter for session
            query_engine = self.vector_store.indices[doc_type].as_query_engine(
                filters={"session_id": session_id}
            )
            
            # Add description based on document type
            descriptions = {
                "network_topology": "Query network topology information and infrastructure connections",
                "tech_stack": "Query information about the technology stack and components",
                "network_ips": "Query network IP addresses and configurations",
                "databases": "Query database configurations and relationships",
                "infrastructure": "Query infrastructure setup and dependencies"
            }
            
            tool = QueryEngineTool.from_defaults(
                query_engine=query_engine,
                description=descriptions.get(doc_type, ""),
            )
            query_engine_tools.append(tool)
        
        # Create router query engine
        router_query_engine = RouterQueryEngine(
            query_engine_tools=query_engine_tools,
            service_context=self.service_context,
            select_multi=True  # Allow querying multiple indices if needed
        )
        
        return router_query_engine
