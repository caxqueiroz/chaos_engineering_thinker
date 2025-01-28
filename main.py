from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
import uuid
from datetime import datetime
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import Graph
import chromadb

app = FastAPI(title="ChaosThinker", description="An AI-powered system analysis tool")

# Global session storage
sessions = {}

class Document(BaseModel):
    content: str
    doc_type: str  # network_topology, tech_stack, network_ips, databases, infrastructure
    metadata: Dict = {}

class Session(BaseModel):
    id: str
    created_at: datetime
    documents: List[Document] = []

class Query(BaseModel):
    session_id: str
    question: str

# Initialize Ollama embeddings and vector store
embeddings = OllamaEmbeddings(model="llama2")
vector_store = Chroma(
    persist_directory="./data/vectorstore",
    embedding_function=embeddings
)

def get_or_create_session(session_id: Optional[str] = None) -> Session:
    if session_id and session_id in sessions:
        return sessions[session_id]
    new_session_id = session_id or str(uuid.uuid4())
    sessions[new_session_id] = Session(
        id=new_session_id,
        created_at=datetime.now(),
        documents=[]
    )
    return sessions[new_session_id]

@app.post("/sessions")
async def create_session():
    session = get_or_create_session()
    return {"session_id": session.id}

@app.post("/sessions/{session_id}/documents")
async def add_document(session_id: str, document: Document):
    session = get_or_create_session(session_id)
    session.documents.append(document)
    
    # Add document to vector store with metadata
    vector_store.add_texts(
        texts=[document.content],
        metadatas=[{
            "doc_type": document.doc_type,
            "session_id": session_id,
            **document.metadata
        }]
    )
    
    return {"status": "success", "document_count": len(session.documents)}

def create_analysis_graph():
    llm = ChatOllama(model="llama2")
    
    # Define the analysis workflow
    def retrieve_context(question: str, session_id: str):
        results = vector_store.similarity_search(
            question,
            k=5,
            filter={"session_id": session_id}
        )
        return "\n".join([doc.page_content for doc in results])
    
    def analyze(context: str, question: str):
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert system analyst. Using the provided context about the system, "
                      "answer the user's question thoroughly and accurately."),
            ("user", "Context: {context}\n\nQuestion: {question}")
        ])
        
        chain = prompt | llm
        return chain.invoke({"context": context, "question": question})
    
    workflow = Graph()
    workflow.add_node("retrieve", retrieve_context)
    workflow.add_node("analyze", analyze)
    
    workflow.add_edge("retrieve", "analyze")
    return workflow

@app.post("/sessions/{session_id}/query")
async def query_system(session_id: str, query: Query):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    workflow = create_analysis_graph()
    
    # Execute the analysis workflow
    result = workflow.invoke({
        "question": query.question,
        "session_id": session_id
    })
    
    return {"result": result}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
