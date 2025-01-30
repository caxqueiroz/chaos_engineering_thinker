from typing import Dict, Any, List
from .experiment_designer import ExperimentDesignerAgent
from .experiment_validator import ExperimentValidatorAgent
from .implementation_agent import ImplementationAgent
from .outcome_validator import OutcomeValidatorAgent
from app.services.document_processor import DocumentProcessor

class AgentOrchestrator:
    """Orchestrates the workflow between different agents."""
    
    def __init__(self):
        # Initialize document processor to be shared among agents
        self.document_processor = DocumentProcessor()
        
        # Initialize agents with shared document processor
        self.designer = ExperimentDesignerAgent(self.document_processor)
        self.validator = ExperimentValidatorAgent(self.document_processor)
        self.implementer = ImplementationAgent(self.document_processor)
        self.outcome_validator = OutcomeValidatorAgent(self.document_processor)
        
        # Keep track of processed documents
        self.processed_documents = {}
    
    async def process_document(self, document_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a new document through all relevant agents.
        
        Args:
            document_path: Path to the document
            metadata: Document metadata including type and purpose
        """
        results = {}
        
        # Process document with each agent
        for agent in [self.designer, self.validator, self.implementer, self.outcome_validator]:
            agent_results = await agent.process_document(document_path, metadata)
            results[agent.name] = agent_results
            
        # Store processed document results
        self.processed_documents[document_path] = results
        return results
    
    async def ask_question(self, question: str, agent_name: str = None) -> Dict[str, Any]:
        """
        Ask a question to a specific agent or all agents.
        
        Args:
            question: The question from the chaos engineer
            agent_name: Optional name of specific agent to query
        """
        context = {
            "processed_documents": self.processed_documents,
            "previous_results": {}  # Add any previous results needed
        }
        
        if agent_name:
            # Query specific agent
            agent = self._get_agent_by_name(agent_name)
            if not agent:
                raise ValueError(f"Unknown agent: {agent_name}")
            return await agent.answer_question(question, context)
        
        # Query all agents
        results = {}
        for agent in [self.designer, self.validator, self.implementer, self.outcome_validator]:
            agent_response = await agent.answer_question(question, context)
            results[agent.name] = agent_response
        return results
    
    def _get_agent_by_name(self, name: str):
        """Get agent instance by name."""
        agents = {
            self.designer.name: self.designer,
            self.validator.name: self.validator,
            self.implementer.name: self.implementer,
            self.outcome_validator.name: self.outcome_validator
        }
        return agents.get(name)
    
    async def run_workflow(self, initial_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the complete workflow of designing, validating, implementing,
        and analyzing chaos engineering experiments.
        
        Args:
            initial_context: Dictionary containing:
                - documents: List of documents to process
                - questions: List of questions from the chaos engineer
                - system_constraints: System constraints and requirements
            
        Returns:
            Dictionary containing the complete workflow results
        """
        # Process all documents first
        for doc in initial_context.get('documents', []):
            await self.process_document(doc['path'], doc['metadata'])
            
        # Update context with processed documents
        context = {
            "processed_documents": self.processed_documents,
            "engineer_questions": initial_context.get('questions', []),
            "system_constraints": initial_context.get('system_constraints', {})
        }
        
        # Run the regular workflow
        design_results = await self.designer.process(context)
        
        validation_context = {
            **context,
            "proposed_experiments": design_results["experiment_proposals"]
        }
        validation_results = await self.validator.process(validation_context)
        
        implementation_context = {
            **context,
            "validated_experiments": validation_results["validated_experiments"]
        }
        implementation_results = await self.implementer.process(implementation_context)
        
        outcome_context = {
            **context,
            "experiment_results": implementation_results.get("execution_results", {}),
            "expected_outcomes": design_results.get("expected_outcomes", {})
        }
        outcome_results = await self.outcome_validator.process(outcome_context)
        
        return {
            "document_analysis": self.processed_documents,
            "design_phase": design_results,
            "validation_phase": validation_results,
            "implementation_phase": implementation_results,
            "outcome_phase": outcome_results
        }
