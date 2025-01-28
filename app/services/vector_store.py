from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain.docstore.document import Document as LangchainDocument
from typing import List, Dict, Any

class VectorStoreService:
    def __init__(self, persist_directory: str = "./data/vectorstore"):
        self.embeddings = OllamaEmbeddings(model="llama2")
        self.vector_store = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings
        )
    
    def add_documents(self, documents: List[LangchainDocument]):
        """Add document chunks to the vector store"""
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        
        self.vector_store.add_texts(
            texts=texts,
            metadatas=metadatas
        )
        self.vector_store.persist()
    
    def similarity_search(self, query: str, session_id: str, k: int = 5) -> List[LangchainDocument]:
        """Search for similar documents"""
        return self.vector_store.similarity_search(
            query,
            k=k,
            filter={"session_id": session_id}
        )
