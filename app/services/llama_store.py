from typing import List, Dict, Any, Optional
from llama_index import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    ServiceContext,
    StorageContext,
    load_index_from_storage,
)
from llama_index.node_parser import SimpleNodeParser
from llama_index.schema import Document, ImageDocument
from llama_index.query_engine import RouterQueryEngine
from llama_index.tools import QueryEngineTool
from llama_index.llms import Ollama
import os

class LlamaStoreService:
    def __init__(self, persist_directory: str = "./data/llamaindex"):
        self.persist_directory = persist_directory
        self.llm = Ollama(model="llama2")
        self.service_context = ServiceContext.from_defaults(
            llm=self.llm,
            embed_model="local"
        )
        
        # Create separate indices for different document types
        self.indices = {}
        self.setup_storage()
        
    def setup_storage(self):
        """Initialize or load existing indices"""
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Document types and their respective directories
        doc_types = ["network_topology", "tech_stack", "network_ips", "databases", "infrastructure"]
        
        for doc_type in doc_types:
            type_dir = os.path.join(self.persist_directory, doc_type)
            os.makedirs(type_dir, exist_ok=True)
            
            try:
                # Try to load existing index
                storage_context = StorageContext.from_defaults(
                    persist_dir=type_dir
                )
                self.indices[doc_type] = load_index_from_storage(
                    storage_context,
                    service_context=self.service_context
                )
            except:
                # Create new index if none exists
                self.indices[doc_type] = VectorStoreIndex(
                    [],
                    service_context=self.service_context
                )
    
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
        
        # Update index
        if doc_type in self.indices:
            self.indices[doc_type] = VectorStoreIndex.from_documents(
                documents,
                service_context=self.service_context,
                storage_context=StorageContext.from_defaults(
                    persist_dir=os.path.join(self.persist_directory, doc_type)
                )
            )
    
    def create_query_engine(self, session_id: str) -> RouterQueryEngine:
        """Create a router query engine that can handle different types of queries"""
        # Create query engine for each document type
        query_engine_tools = []
        
        for doc_type, index in self.indices.items():
            # Create query engine with metadata filter for session
            query_engine = index.as_query_engine(
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
