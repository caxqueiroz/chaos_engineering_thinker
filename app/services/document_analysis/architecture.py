from typing import Dict, Any, List
import spacy
import re
from .base import DocumentAnalyzer

class ArchitectureDocumentAnalyzer(DocumentAnalyzer):
    """Analyzes architecture documents to extract system information."""
    
    def __init__(self):
        # Load SpaCy model for NLP
        self.nlp = spacy.load("en_core_web_sm")
        
        # Common architecture component keywords
        self.component_keywords = {
            'service': ['service', 'microservice', 'api', 'endpoint'],
            'database': ['database', 'db', 'storage', 'cache', 'redis', 'mongodb'],
            'queue': ['queue', 'kafka', 'rabbitmq', 'message broker'],
            'loadbalancer': ['load balancer', 'proxy', 'nginx', 'haproxy'],
            'security': ['firewall', 'authentication', 'authorization', 'ssl']
        }
    
    def supported_formats(self) -> List[str]:
        return ['txt', 'md', 'pdf']
    
    async def analyze(self, content: bytes, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze architecture documents to extract system components and relationships.
        
        Args:
            content: Document content in bytes
            metadata: Document metadata
            
        Returns:
            Dictionary containing:
                - components: List of system components and their details
                - relationships: Component relationships and dependencies
                - constraints: System constraints and requirements
                - failure_modes: Potential failure modes
                - scalability_points: Scalability considerations
        """
        # Convert bytes to text
        text = content.decode('utf-8')
        
        # Process text with SpaCy
        doc = self.nlp(text)
        
        # Extract information
        components = self._extract_components(doc)
        relationships = self._extract_relationships(doc)
        constraints = self._extract_constraints(doc)
        failure_modes = self._identify_failure_modes(doc)
        scalability = self._extract_scalability_info(doc)
        
        return {
            "components": components,
            "relationships": relationships,
            "constraints": constraints,
            "failure_modes": failure_modes,
            "scalability_points": scalability
        }
    
    def _extract_components(self, doc) -> List[Dict[str, Any]]:
        """Extract system components and their properties."""
        components = []
        
        for sent in doc.sents:
            for chunk in sent.noun_chunks:
                # Check if chunk contains component keywords
                component_type = self._identify_component_type(chunk.text)
                if component_type:
                    # Extract properties from surrounding context
                    properties = self._extract_component_properties(chunk, sent)
                    
                    components.append({
                        "name": chunk.text,
                        "type": component_type,
                        "properties": properties,
                        "sentence_context": sent.text
                    })
        
        return components
    
    def _identify_component_type(self, text: str) -> str:
        """Identify the type of component based on keywords."""
        text_lower = text.lower()
        for comp_type, keywords in self.component_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return comp_type
        return None
    
    def _extract_component_properties(self, chunk, sentence) -> Dict[str, Any]:
        """Extract properties of a component from its context."""
        properties = {}
        
        # Look for numbers (possibly indicating capacity, instances, etc.)
        numbers = re.findall(r'\d+', sentence.text)
        if numbers:
            properties['numeric_values'] = numbers
            
        # Look for technical specifications
        tech_specs = re.findall(r'\d+[GgMmKk][Bb]|\d+%|\d+ms', sentence.text)
        if tech_specs:
            properties['technical_specs'] = tech_specs
            
        # Extract adjectives describing the component
        for token in sentence:
            if token.pos_ == 'ADJ' and token.head == chunk.root:
                properties.setdefault('attributes', []).append(token.text)
                
        return properties
    
    def _extract_relationships(self, doc) -> List[Dict[str, Any]]:
        """Extract relationships between components."""
        relationships = []
        
        relationship_patterns = [
            'connects to', 'depends on', 'uses', 'calls',
            'communicates with', 'sends data to', 'receives data from'
        ]
        
        for sent in doc.sents:
            for pattern in relationship_patterns:
                if pattern in sent.text.lower():
                    # Find components in the sentence
                    components = self._find_components_in_sent(sent)
                    if len(components) >= 2:
                        relationships.append({
                            "from": components[0],
                            "to": components[1],
                            "type": pattern,
                            "description": sent.text
                        })
        
        return relationships
    
    def _extract_constraints(self, doc) -> List[Dict[str, Any]]:
        """Extract system constraints and requirements."""
        constraints = []
        
        constraint_keywords = [
            'must', 'should', 'requires', 'needs to',
            'latency', 'throughput', 'availability'
        ]
        
        for sent in doc.sents:
            if any(keyword in sent.text.lower() for keyword in constraint_keywords):
                constraints.append({
                    "description": sent.text,
                    "type": self._identify_constraint_type(sent),
                    "metrics": self._extract_metrics(sent)
                })
                
        return constraints
    
    def _identify_failure_modes(self, doc) -> List[Dict[str, Any]]:
        """Identify potential failure modes from the documentation."""
        failure_modes = []
        
        failure_keywords = [
            'fail', 'error', 'crash', 'timeout', 'unavailable',
            'bottleneck', 'overload', 'latency'
        ]
        
        for sent in doc.sents:
            if any(keyword in sent.text.lower() for keyword in failure_keywords):
                # Find mentioned components
                components = self._find_components_in_sent(sent)
                
                failure_modes.append({
                    "description": sent.text,
                    "affected_components": components,
                    "type": self._classify_failure_type(sent),
                    "potential_impact": self._assess_failure_impact(sent)
                })
                
        return failure_modes
    
    def _extract_scalability_info(self, doc) -> List[Dict[str, Any]]:
        """Extract information about system scalability."""
        scalability_points = []
        
        scalability_keywords = [
            'scale', 'growth', 'capacity', 'throughput',
            'concurrent', 'parallel', 'distributed'
        ]
        
        for sent in doc.sents:
            if any(keyword in sent.text.lower() for keyword in scalability_keywords):
                components = self._find_components_in_sent(sent)
                
                scalability_points.append({
                    "description": sent.text,
                    "components": components,
                    "scaling_type": self._identify_scaling_type(sent),
                    "metrics": self._extract_metrics(sent)
                })
                
        return scalability_points
    
    def _find_components_in_sent(self, sent) -> List[str]:
        """Find component names in a sentence."""
        components = []
        for chunk in sent.noun_chunks:
            if self._identify_component_type(chunk.text):
                components.append(chunk.text)
        return components
    
    def _identify_constraint_type(self, sent) -> str:
        """Identify the type of constraint."""
        text = sent.text.lower()
        if any(word in text for word in ['latency', 'response time', 'speed']):
            return 'performance'
        elif any(word in text for word in ['available', 'uptime', 'sla']):
            return 'availability'
        elif any(word in text for word in ['throughput', 'capacity', 'requests']):
            return 'capacity'
        return 'general'
    
    def _extract_metrics(self, sent) -> Dict[str, Any]:
        """Extract metrics and numbers from text."""
        metrics = {}
        
        # Extract numbers with units
        patterns = {
            'time': r'\d+\s*(?:ms|seconds?|minutes?|hours?)',
            'percentage': r'\d+%',
            'requests': r'\d+\s*(?:requests?|req\/s|tps)',
            'size': r'\d+\s*(?:[GgMmKk][Bb]|bytes?)'
        }
        
        for metric_type, pattern in patterns.items():
            matches = re.findall(pattern, sent.text)
            if matches:
                metrics[metric_type] = matches
                
        return metrics
    
    def _classify_failure_type(self, sent) -> str:
        """Classify the type of failure mentioned."""
        text = sent.text.lower()
        if 'timeout' in text:
            return 'timeout'
        elif any(word in text for word in ['crash', 'down']):
            return 'crash'
        elif 'memory' in text:
            return 'resource_exhaustion'
        elif 'network' in text:
            return 'network'
        return 'general'
    
    def _assess_failure_impact(self, sent) -> Dict[str, Any]:
        """Assess the potential impact of a failure."""
        text = sent.text.lower()
        impact = {
            "severity": self._determine_severity(text),
            "scope": self._determine_scope(text),
            "recovery": self._determine_recovery(text)
        }
        return impact
    
    def _determine_severity(self, text: str) -> str:
        """Determine the severity of a failure."""
        if any(word in text for word in ['critical', 'severe', 'major']):
            return 'high'
        elif any(word in text for word in ['moderate', 'significant']):
            return 'medium'
        return 'low'
    
    def _determine_scope(self, text: str) -> str:
        """Determine the scope of impact."""
        if 'system' in text:
            return 'system-wide'
        elif 'service' in text:
            return 'service-level'
        return 'component-level'
    
    def _determine_recovery(self, text: str) -> str:
        """Determine recovery characteristics."""
        if 'automatic' in text or 'self-heal' in text:
            return 'automatic'
        elif 'manual' in text:
            return 'manual'
        return 'unknown'
    
    def _identify_scaling_type(self, sent) -> str:
        """Identify the type of scaling mentioned."""
        text = sent.text.lower()
        if 'horizontal' in text:
            return 'horizontal'
        elif 'vertical' in text:
            return 'vertical'
        elif 'auto' in text:
            return 'auto'
        return 'general'
