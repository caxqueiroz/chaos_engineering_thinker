from typing import Dict, Any, List
from ollama import AsyncClient

class QuestionAnswerer:
    """Handles question answering using LLM."""
    
    def __init__(self, model: str = "deepseek-r1:70b"):
        self.client = AsyncClient(host='http://localhost:11434')
        self.model = model
        
    async def answer_question(
        self,
        question: str,
        context: Dict[str, Any],
        agent_type: str
    ) -> Dict[str, Any]:
        """
        Answer a question using the LLM with appropriate context and agent-specific prompting.
        
        Args:
            question: The question to answer
            context: Available context including processed documents
            agent_type: Type of agent asking (designer, validator, etc.)
            
        Returns:
            Dictionary containing:
                - answer: The answer to the question
                - supporting_evidence: Evidence from context
                - confidence: Confidence score
                - reasoning: Explanation of the reasoning
        """
        # Prepare prompt based on agent type
        prompt = self._create_prompt(question, context, agent_type)
        
        # Get LLM response
        response = await self._get_llm_response(prompt)
        
        # Extract answer components
        parsed_response = self._parse_response(response)
        
        # Validate answer
        confidence = self._calculate_confidence(parsed_response, context)
        
        return {
            "answer": parsed_response["answer"],
            "supporting_evidence": parsed_response["evidence"],
            "confidence": confidence,
            "reasoning": parsed_response["reasoning"]
        }
    
    def _create_prompt(
        self,
        question: str,
        context: Dict[str, Any],
        agent_type: str
    ) -> str:
        """Create an appropriate prompt based on agent type and context."""
        
        # Base context from processed documents
        doc_context = self._format_document_context(context.get('processed_documents', {}))
        
        # Agent-specific prompting
        agent_prompts = {
            "designer": """As a Chaos Engineering Designer, analyze the following system context and answer the question.
Focus on identifying potential experiment opportunities and system weaknesses.
Consider failure modes, critical paths, and system dependencies in your answer.

System Context:
{context}

Question: {question}

Provide your answer in the following format:
Answer: [Your detailed answer]
Evidence: [List specific evidence from the context]
Reasoning: [Explain your reasoning process]""",

            "validator": """As a Chaos Engineering Validator, analyze the following system context and answer the question.
Focus on safety implications, potential risks, and system constraints.
Consider business requirements and system stability in your answer.

System Context:
{context}

Question: {question}

Provide your answer in the following format:
Answer: [Your detailed answer]
Evidence: [List specific evidence from the context]
Reasoning: [Explain your validation process]""",

            "implementer": """As a Chaos Engineering Implementer, analyze the following system context and answer the question.
Focus on technical implementation details, tools, and practical considerations.
Consider system interfaces, deployment processes, and rollback procedures.

System Context:
{context}

Question: {question}

Provide your answer in the following format:
Answer: [Your detailed answer]
Evidence: [List specific evidence from the context]
Reasoning: [Explain your implementation approach]""",

            "outcome_validator": """As a Chaos Engineering Outcome Validator, analyze the following system context and answer the question.
Focus on metrics, success criteria, and observed behaviors.
Consider expected vs actual results and system resilience indicators.

System Context:
{context}

Question: {question}

Provide your answer in the following format:
Answer: [Your detailed answer]
Evidence: [List specific evidence from the context]
Reasoning: [Explain your analysis process]"""
        }
        
        return agent_prompts[agent_type].format(
            context=doc_context,
            question=question
        )
    
    def _format_document_context(self, processed_documents: Dict[str, Any]) -> str:
        """Format processed documents into a string context."""
        context_parts = []
        
        for doc_path, analysis in processed_documents.items():
            context_parts.append(f"Document: {doc_path}")
            
            # Add components if available
            if 'components' in analysis:
                context_parts.append("Components:")
                for comp in analysis['components']:
                    context_parts.append(f"- {comp['name']} ({comp['type']})")
            
            # Add relationships if available
            if 'relationships' in analysis:
                context_parts.append("Relationships:")
                for rel in analysis['relationships']:
                    context_parts.append(f"- {rel['from']} {rel['type']} {rel['to']}")
            
            # Add constraints if available
            if 'constraints' in analysis:
                context_parts.append("Constraints:")
                for const in analysis['constraints']:
                    context_parts.append(f"- {const['description']}")
        
        return "\n".join(context_parts)
    
    async def _get_llm_response(self, prompt: str) -> str:
        """Get response from LLM."""
        response_text = ""
        async for response in await self.client.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        ):
            if 'message' in response:
                response_text += response['message'].get('content', '')
        
        return response_text
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into structured components."""
        parts = {
            "answer": "",
            "evidence": [],
            "reasoning": ""
        }
        
        # Simple parsing based on format markers
        current_section = None
        for line in response.split('\n'):
            if line.startswith('Answer:'):
                current_section = "answer"
                parts["answer"] = line[7:].strip()
            elif line.startswith('Evidence:'):
                current_section = "evidence"
            elif line.startswith('Reasoning:'):
                current_section = "reasoning"
                parts["reasoning"] = line[10:].strip()
            elif line.strip() and current_section:
                if current_section == "evidence":
                    parts["evidence"].append(line.strip())
                elif current_section == "reasoning":
                    parts["reasoning"] += " " + line.strip()
        
        return parts
    
    def _calculate_confidence(
        self,
        parsed_response: Dict[str, Any],
        context: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for the answer."""
        confidence = 0.0
        
        # Check if evidence is supported by context
        evidence_count = len(parsed_response["evidence"])
        supported_evidence = 0
        
        for evidence in parsed_response["evidence"]:
            if self._evidence_in_context(evidence, context):
                supported_evidence += 1
                
        # Evidence support score (50% of total)
        if evidence_count > 0:
            confidence += 0.5 * (supported_evidence / evidence_count)
            
        # Reasoning completeness score (30% of total)
        if parsed_response["reasoning"]:
            confidence += 0.3
            
        # Answer completeness score (20% of total)
        if len(parsed_response["answer"]) > 50:  # Arbitrary threshold
            confidence += 0.2
            
        return confidence
    
    def _evidence_in_context(self, evidence: str, context: Dict[str, Any]) -> bool:
        """Check if evidence is supported by the context."""
        # Simple text matching for now
        context_text = self._format_document_context(context.get('processed_documents', {}))
        return evidence.lower() in context_text.lower()
