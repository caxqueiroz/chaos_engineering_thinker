from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Document(Base):
    __tablename__ = 'documents'
    
    id = Column(String, primary_key=True)  # This will be the file path
    file_hash = Column(String, nullable=False)
    content = Column(Text, nullable=True)  # Extracted content
    original_filename = Column(String, nullable=False)
    session_id = Column(String, nullable=False)
    doc_type = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(Text, nullable=True)  # JSON string of metadata

class DatabaseManager:
    def __init__(self, db_path: str = 'sqlite:///./data/documents.db'):
        self.engine = create_engine(db_path)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def save_document(self, doc_data: dict):
        session = self.Session()
        try:
            doc = Document(**doc_data)
            session.add(doc)
            session.commit()
        finally:
            session.close()
    
    def get_document(self, file_path: str):
        session = self.Session()
        try:
            return session.query(Document).filter(Document.id == file_path).first()
        finally:
            session.close()
