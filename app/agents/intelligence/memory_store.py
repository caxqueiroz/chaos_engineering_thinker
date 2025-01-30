from typing import Dict, Any, List, Optional
import json
from datetime import datetime
import numpy as np
from dataclasses import dataclass
from enum import Enum

class ExperimentOutcome(Enum):
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    UNSAFE = "unsafe"
    INTERRUPTED = "interrupted"

@dataclass
class ExperimentMemory:
    experiment_id: str
    timestamp: datetime
    experiment_type: str
    target_component: str
    parameters: Dict[str, Any]
    outcome: ExperimentOutcome
    metrics: Dict[str, float]
    learnings: List[str]
    affected_components: List[str]
    duration: str
    risk_level: str

class MemoryStore:
    """Stores and manages agent's memories and learnings."""
    
    def __init__(self):
        self.experiments: List[ExperimentMemory] = []
        self.component_knowledge: Dict[str, Dict[str, Any]] = {}
        self.relationship_knowledge: Dict[str, Dict[str, float]] = {}
        self.risk_profiles: Dict[str, Dict[str, float]] = {}
        
    def add_experiment(self, memory: ExperimentMemory) -> None:
        """Add new experiment memory"""
        self.experiments.append(memory)
        self._update_knowledge(memory)
        
    def get_similar_experiments(
        self,
        experiment: Dict[str, Any],
        threshold: float = 0.7
    ) -> List[ExperimentMemory]:
        """Find similar experiments from memory"""
        similar = []
        for mem in self.experiments:
            similarity = self._calculate_similarity(experiment, mem)
            if similarity >= threshold:
                similar.append(mem)
        return similar
    
    def get_component_risk_profile(self, component: str) -> Dict[str, float]:
        """Get risk profile for a component"""
        if component not in self.risk_profiles:
            self._build_risk_profile(component)
            # Initialize with default profile if no data
            if component not in self.risk_profiles:
                self.risk_profiles[component] = {
                    "success_rate": 0.5,  # Neutral success rate
                    "avg_impact": 1.0,    # Assume high impact
                    "risk_score": 0.5,    # Neutral risk
                    "safe_parameter_ranges": {},
                    "failure_patterns": []
                }
        return self.risk_profiles[component]
    
    def get_component_relationships(self, component: str) -> Dict[str, float]:
        """Get relationship strengths with other components"""
        return self.relationship_knowledge.get(component, {})
    
    def _update_knowledge(self, memory: ExperimentMemory) -> None:
        """Update knowledge base with new experiment data"""
        # Update component knowledge
        if memory.target_component not in self.component_knowledge:
            self.component_knowledge[memory.target_component] = {
                "experiments": 0,
                "success_rate": 0.0,
                "avg_duration": 0.0,
                "failure_patterns": [],
                "safe_parameters": {},
                "risky_parameters": {}
            }
            
        comp_knowledge = self.component_knowledge[memory.target_component]
        comp_knowledge["experiments"] += 1
        
        # Update success rate
        if memory.outcome in [ExperimentOutcome.SUCCESS, ExperimentOutcome.PARTIAL_SUCCESS]:
            comp_knowledge["safe_parameters"].update(memory.parameters)
        else:
            comp_knowledge["risky_parameters"].update(memory.parameters)
            
        # Update relationship knowledge
        for affected in memory.affected_components:
            if memory.target_component not in self.relationship_knowledge:
                self.relationship_knowledge[memory.target_component] = {}
            rel = self.relationship_knowledge[memory.target_component]
            rel[affected] = rel.get(affected, 0) + 1
            
        # Update risk profile
        self._build_risk_profile(memory.target_component)
    
    def _build_risk_profile(self, component: str) -> None:
        """Build risk profile for a component"""
        if component not in self.component_knowledge:
            return
            
        comp_knowledge = self.component_knowledge[component]
        experiments = [
            exp for exp in self.experiments
            if exp.target_component == component
        ]
        
        if not experiments:
            return
            
        # Calculate risk metrics
        success_rate = len([
            exp for exp in experiments
            if exp.outcome in [ExperimentOutcome.SUCCESS, ExperimentOutcome.PARTIAL_SUCCESS]
        ]) / len(experiments)
        
        avg_impact = np.mean([
            len(exp.affected_components) for exp in experiments
        ])
        
        risk_score = (1 - success_rate) * avg_impact
        
        self.risk_profiles[component] = {
            "success_rate": success_rate,
            "avg_impact": avg_impact,
            "risk_score": risk_score,
            "safe_parameter_ranges": self._calculate_safe_ranges(experiments),
            "failure_patterns": self._identify_failure_patterns(experiments)
        }
    
    def _calculate_safe_ranges(
        self,
        experiments: List[ExperimentMemory]
    ) -> Dict[str, Dict[str, float]]:
        """Calculate safe parameter ranges from successful experiments"""
        successful = [
            exp for exp in experiments
            if exp.outcome in [ExperimentOutcome.SUCCESS, ExperimentOutcome.PARTIAL_SUCCESS]
        ]
        
        if not successful:
            return {}
            
        ranges = {}
        for exp in successful:
            for param, value in exp.parameters.items():
                if param not in ranges:
                    ranges[param] = {"min": float('inf'), "max": float('-inf')}
                if isinstance(value, (int, float)):
                    ranges[param]["min"] = min(ranges[param]["min"], value)
                    ranges[param]["max"] = max(ranges[param]["max"], value)
                    
        return ranges
    
    def _identify_failure_patterns(
        self,
        experiments: List[ExperimentMemory]
    ) -> List[Dict[str, Any]]:
        """Identify common patterns in failed experiments"""
        failed = [
            exp for exp in experiments
            if exp.outcome in [ExperimentOutcome.FAILURE, ExperimentOutcome.UNSAFE]
        ]
        
        if not failed:
            return []
            
        patterns = []
        for exp in failed:
            pattern = {
                "type": exp.experiment_type,
                "parameters": exp.parameters,
                "affected_components": exp.affected_components,
                "duration": exp.duration
            }
            if pattern not in patterns:
                patterns.append(pattern)
                
        return patterns
    
    def _calculate_similarity(
        self,
        experiment: Dict[str, Any],
        memory: ExperimentMemory
    ) -> float:
        """Calculate similarity between new experiment and memory"""
        # Type similarity
        type_sim = 1.0 if experiment["type"] == memory.experiment_type else 0.0
        
        # Target similarity
        target_sim = 1.0 if experiment["parameters"]["target_component"] == memory.target_component else 0.0
        
        # Parameter similarity
        param_sim = 0.0
        if isinstance(experiment["parameters"], dict):
            common_params = set(experiment["parameters"].keys()) & set(memory.parameters.keys())
            if common_params:
                param_sim = len(common_params) / len(set(experiment["parameters"].keys()) | set(memory.parameters.keys()))
                
        # Component similarity
        comp_sim = 0.0
        if "affected_components" in experiment and memory.affected_components:
            common_comps = set(experiment["affected_components"]) & set(memory.affected_components)
            if common_comps:
                comp_sim = len(common_comps) / len(set(experiment["affected_components"]) | set(memory.affected_components))
                
        # Weighted similarity
        weights = [0.3, 0.3, 0.2, 0.2]  # Adjust weights based on importance
        return sum([
            weights[0] * type_sim,
            weights[1] * target_sim,
            weights[2] * param_sim,
            weights[3] * comp_sim
        ])
