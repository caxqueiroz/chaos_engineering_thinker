from abc import ABC, abstractmethod
from typing import Dict, Any, List

class DocumentAnalyzer(ABC):
    """Base class for document analyzers."""
    
    @abstractmethod
    async def analyze(self, content: bytes, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze document content and return structured information."""
        pass
    
    @abstractmethod
    def supported_formats(self) -> List[str]:
        """Return list of supported file formats."""
        pass
