from typing import List, Dict, Optional
import guardrails as gd
from pydantic import BaseModel, Field
from enum import Enum
from app.models.schemas import Document

# Define allowed document types
class DocumentType(str, Enum):
    NETWORK_TOPOLOGY = "network_topology"
    TECH_STACK = "tech_stack"
    NETWORK_IPS = "network_ips"
    DATABASES = "databases"
    INFRASTRUCTURE = "infrastructure"

# Rail spec for document content validation
document_content_rail = """
<rail version="0.1">
<output>
    <string name="validated_content" format="free-text" description="The validated document content">
        <validator name="length" min="1" max="10000" />
        <validator name="no_harmful_content" />
    </string>
</output>
</rail>
"""

# Rail spec for query validation
query_rail = """
<rail version="0.1">
<output>
    <string name="validated_query" format="free-text" description="The validated and sanitized query">
        <validator name="length" min="1" max="1000" />
        <validator name="no_sql_injection" />
        <validator name="no_harmful_content" />
    </string>
</output>
</rail>
"""

class DocumentValidator:
    def __init__(self):
        self.content_guard = gd.Guard.from_rail_string(document_content_rail)
        
    def validate_document(self, document: Document) -> List[str]:
        errors = []
        
        # Validate document type
        try:
            DocumentType(document.doc_type)
        except ValueError:
            errors.append(f"Invalid document type. Must be one of: {', '.join([t.value for t in DocumentType])}")
        
        # Validate content using guardrails
        try:
            validated = self.content_guard.validate(document.content)
            if validated.validation_passed:
                document.content = validated.validated_content
            else:
                errors.extend(validated.validation_errors)
        except Exception as e:
            errors.append(f"Content validation error: {str(e)}")
        
        # Validate metadata
        if not isinstance(document.metadata, dict):
            errors.append("Metadata must be a dictionary")
            
        return errors

class QueryValidator:
    def __init__(self):
        self.query_guard = gd.Guard.from_rail_string(query_rail)
    
    def validate_query(self, query: str) -> tuple[str, List[str]]:
        try:
            validated = self.query_guard.validate(query)
            if validated.validation_passed:
                return validated.validated_query, []
            return query, validated.validation_errors
        except Exception as e:
            return query, [f"Query validation error: {str(e)}"]

# Initialize validators as singletons
document_validator = DocumentValidator()
query_validator = QueryValidator()
