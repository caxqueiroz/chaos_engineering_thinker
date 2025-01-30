from typing import Dict, Any, List, Optional
from .base import Agent
from app.services.experiment_generation.generator import ExperimentGenerator
from app.services.experiment_generation.code_generator import ExperimentCodeGenerator
from app.services.validation.safety_validator import SafetyValidator
from app.services.analysis import AnalysisService
from app.services.llama_store import LlamaStoreService

class ChaosAgent(Agent):
    """
    An intelligent agent that combines both high-level decision making and low-level services.
    
    This hybrid approach:
    1. Uses services for specific tasks (generation, validation, etc.)
    2. Adds intelligent orchestration and decision making
    3. Maintains state and context across operations
    4. Can learn from past experiments and outcomes
    """
    
    def __init__(
        self,
        llama_store: Optional[LlamaStoreService] = None,
        experiment_generator: Optional[ExperimentGenerator] = None,
        code_generator: Optional[ExperimentCodeGenerator] = None,
        safety_validator: Optional[SafetyValidator] = None,
        analysis_service: Optional[AnalysisService] = None
    ):
        super().__init__(
            name="Chaos Engineering Agent",
            description="Intelligent agent for designing and running chaos experiments"
        )
        
        # Initialize services
        self.llama_store = llama_store or LlamaStoreService()
        self.experiment_generator = experiment_generator or ExperimentGenerator()
        self.code_generator = code_generator or ExperimentCodeGenerator()
        self.safety_validator = safety_validator or SafetyValidator()
        self.analysis_service = analysis_service or AnalysisService(self.llama_store)
        
        # Agent state
        self.experiment_history: List[Dict[str, Any]] = []
        self.system_knowledge: Dict[str, Any] = {}
        self.risk_tolerance: float = 0.7  # Default risk tolerance
        
    async def analyze_system(self, session_id: str, question: str) -> Dict[str, Any]:
        """Analyze the system using both services and agent intelligence"""
        # Get base analysis from service
        analysis = await self.analysis_service.analyze_system(session_id, question)
        
        # Enhance with agent's accumulated knowledge
        if session_id in self.system_knowledge:
            analysis["historical_context"] = self.system_knowledge[session_id]
            analysis["previous_experiments"] = [
                exp for exp in self.experiment_history 
                if exp["session_id"] == session_id
            ]
        
        return analysis
        
    async def design_experiment(
        self,
        system_analysis: Dict[str, Any],
        constraints: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Design experiments using both services and agent intelligence"""
        # Generate base experiments
        experiments = await self.experiment_generator.generate_experiments(system_analysis)
        
        # Apply agent intelligence
        enhanced_experiments = []
        for exp in experiments:
            # Check experiment history
            similar_experiments = self._find_similar_experiments(exp)
            
            # Adjust based on historical outcomes
            if similar_experiments:
                exp = self._enhance_experiment_from_history(exp, similar_experiments)
            
            # Apply custom constraints
            if constraints:
                exp = self._apply_constraints(exp, constraints)
            
            enhanced_experiments.append(exp)
        
        return enhanced_experiments
    
    async def validate_experiment(
        self,
        experiment: Dict[str, Any],
        system_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate experiments with both service checks and agent intelligence"""
        # Get base validation
        validation = self.safety_validator.validate_experiment(experiment, system_analysis)
        
        # Enhance with agent intelligence
        validation["agent_assessment"] = {
            "historical_safety": self._assess_historical_safety(experiment),
            "complexity_score": self._calculate_complexity(experiment),
            "risk_factors": self._identify_risk_factors(experiment, system_analysis),
            "recommended_precautions": self._suggest_precautions(experiment)
        }
        
        # Adjust final safety decision
        validation["is_safe"] = (
            validation["is_safe"] and 
            validation["agent_assessment"]["historical_safety"] >= self.risk_tolerance
        )
        
        return validation
    
    async def generate_implementation(
        self,
        experiment: Dict[str, Any],
        platform: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate implementation with both service code and agent enhancements"""
        # Get base implementation
        implementation = await self.code_generator.generate_code(
            experiment=experiment,
            platform=platform,
            config=config
        )
        
        # Enhance with agent intelligence
        implementation["monitoring_setup"] = self._generate_monitoring_code(experiment)
        implementation["safety_checks"] = self._generate_safety_checks(experiment)
        implementation["rollback_procedures"] = self._enhance_rollback_procedures(
            implementation["rollback_steps"]
        )
        
        return implementation
    
    def _find_similar_experiments(self, experiment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find similar experiments from history"""
        return [
            hist_exp for hist_exp in self.experiment_history
            if self._calculate_similarity(experiment, hist_exp) > 0.8
        ]
    
    def _enhance_experiment_from_history(
        self,
        experiment: Dict[str, Any],
        similar_experiments: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Enhance experiment based on historical outcomes"""
        for hist_exp in similar_experiments:
            if hist_exp.get("outcome", {}).get("success", False):
                # Copy successful parameters
                experiment["parameters"].update(hist_exp["parameters"])
            else:
                # Avoid failed parameters
                experiment["safety_checks"].extend(hist_exp.get("failure_learnings", []))
        
        return experiment
    
    def _assess_historical_safety(self, experiment: Dict[str, Any]) -> float:
        """Assess safety based on historical data"""
        similar_experiments = self._find_similar_experiments(experiment)
        if not similar_experiments:
            return 0.5  # Neutral score for new experiments
            
        success_rate = sum(
            1 for exp in similar_experiments
            if exp.get("outcome", {}).get("success", False)
        ) / len(similar_experiments)
        
        return success_rate
    
    def _calculate_complexity(self, experiment: Dict[str, Any]) -> float:
        """Calculate experiment complexity score"""
        factors = [
            len(experiment.get("parameters", {})),
            len(experiment.get("affected_components", [])),
            experiment.get("duration", "30s").rstrip("s"),
            len(experiment.get("safety_checks", []))
        ]
        return sum(float(f) for f in factors) / len(factors) / 10  # Normalize to 0-1
    
    def _identify_risk_factors(
        self,
        experiment: Dict[str, Any],
        system_analysis: Dict[str, Any]
    ) -> List[str]:
        """Identify potential risk factors"""
        risks = []
        
        # Check component criticality
        target = experiment["parameters"].get("target_component")
        if target in system_analysis.get("critical_components", []):
            risks.append(f"Target {target} is a critical component")
            
        # Check experiment duration
        duration = int(experiment.get("duration", "30s").rstrip("s"))
        if duration > 60:
            risks.append(f"Long duration ({duration}s) increases risk")
            
        # Check affected components
        affected = experiment.get("affected_components", [])
        if len(affected) > 2:
            risks.append(f"Multiple components ({len(affected)}) affected")
            
        return risks
    
    def _suggest_precautions(self, experiment: Dict[str, Any]) -> List[str]:
        """Suggest additional safety precautions"""
        precautions = []
        
        # Basic precautions
        precautions.append("Enable enhanced monitoring before experiment")
        precautions.append("Prepare rollback procedures")
        
        # Specific precautions based on experiment type
        if experiment["type"] == "network_failure":
            precautions.append("Ensure backup communication channel")
        elif experiment["type"] == "resource_exhaustion":
            precautions.append("Set up resource quotas and limits")
            
        return precautions
    
    def _apply_constraints(
        self,
        experiment: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply custom constraints to experiment"""
        # Time constraints
        if "max_duration" in constraints:
            current_duration = int(experiment["duration"].rstrip("s"))
            max_duration = int(constraints["max_duration"].rstrip("s"))
            if current_duration > max_duration:
                experiment["duration"] = f"{max_duration}s"
                
        # Component constraints
        if "excluded_components" in constraints:
            if experiment["parameters"]["target_component"] in constraints["excluded_components"]:
                experiment["parameters"]["target_component"] = self._find_alternative_component(
                    experiment,
                    constraints["excluded_components"]
                )
                
        return experiment
    
    def _find_alternative_component(
        self,
        experiment: Dict[str, Any],
        excluded: List[str]
    ) -> str:
        """Find alternative component for experiment"""
        # Implementation would depend on system analysis
        # Return a suitable alternative component not in excluded list
        return "alternative-component"  # Placeholder
