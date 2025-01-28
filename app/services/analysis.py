from app.services.llama_store import LlamaStoreService
from typing import Dict, Any

class AnalysisService:
    def __init__(self, llama_store: LlamaStoreService):
        self.llama_store = llama_store
    
    def analyze_system(self, session_id: str, question: str) -> Dict[str, Any]:
        """Analyze the system based on the question"""
        # Get the query engine for this session
        query_engine = self.llama_store.create_query_engine(session_id)
        
        # Execute query
        response = query_engine.query(question)
        
        # Process response
        result = {
            "answer": str(response),
            "sources": [
                {
                    "content": source.node.text,
                    "metadata": source.node.metadata
                }
                for source in response.source_nodes
            ] if hasattr(response, 'source_nodes') else []
        }
        
        return result
