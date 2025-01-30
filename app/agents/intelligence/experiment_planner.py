from typing import Dict, Any, List, Optional
from datetime import datetime
from .memory_store import MemoryStore, ExperimentMemory, ExperimentOutcome
import numpy as np

class ExperimentPlanner:
    """Plans and adapts experiments based on historical data and system knowledge."""
    
    def __init__(self, memory_store: MemoryStore):
        self.memory_store = memory_store
        
    def enhance_experiment(
        self,
        experiment: Dict[str, Any],
        system_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance experiment based on historical knowledge"""
        # Get similar experiments
        similar = self.memory_store.get_similar_experiments(experiment)
        
        # Get component risk profile
        target = experiment["parameters"]["target_component"]
        risk_profile = self.memory_store.get_component_risk_profile(target)
        
        # Enhance experiment
        enhanced = experiment.copy()
        enhanced = self._adjust_parameters(enhanced, similar, risk_profile)
        enhanced = self._add_safety_measures(enhanced, risk_profile)
        enhanced = self._optimize_duration(enhanced, similar)
        enhanced = self._add_monitoring(enhanced, system_analysis)
        
        return enhanced
    
    def calculate_experiment_risk(
        self,
        experiment: Dict[str, Any],
        system_analysis: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate comprehensive risk assessment"""
        target = experiment["parameters"]["target_component"]
        risk_profile = self.memory_store.get_component_risk_profile(target)
        relationships = self.memory_store.get_component_relationships(target)
        
        # Base risk from profile
        base_risk = risk_profile.get("risk_score", 0.5)
        
        # Impact risk based on affected components
        impact_risk = self._calculate_impact_risk(
            experiment.get("affected_components", []),
            relationships,
            system_analysis
        )
        
        # Parameter risk based on historical safe ranges
        param_risk = self._calculate_parameter_risk(
            experiment["parameters"],
            risk_profile.get("safe_parameter_ranges", {})
        )
        
        # Duration risk
        duration_secs = int(experiment.get("duration", "30s").rstrip("s"))
        duration_risk = min(duration_secs / 300, 1.0)  # Max risk at 5 minutes
        
        # Weighted risk score
        weights = [0.3, 0.3, 0.2, 0.2]
        total_risk = sum([
            weights[0] * base_risk,
            weights[1] * impact_risk,
            weights[2] * param_risk,
            weights[3] * duration_risk
        ])
        
        return {
            "total_risk": total_risk,
            "base_risk": base_risk,
            "impact_risk": impact_risk,
            "parameter_risk": param_risk,
            "duration_risk": duration_risk
        }
    
    def _adjust_parameters(
        self,
        experiment: Dict[str, Any],
        similar: List[ExperimentMemory],
        risk_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Adjust experiment parameters based on historical data"""
        if not similar:
            return experiment
            
        # Get successful parameters
        successful_params = {}
        for mem in similar:
            if mem.outcome in [ExperimentOutcome.SUCCESS, ExperimentOutcome.PARTIAL_SUCCESS]:
                for param, value in mem.parameters.items():
                    if param not in successful_params:
                        successful_params[param] = []
                    successful_params[param].append(value)
                    
        # Adjust parameters to safe ranges
        safe_ranges = risk_profile.get("safe_parameter_ranges", {})
        for param, value in experiment["parameters"].items():
            if param in safe_ranges and isinstance(value, (int, float)):
                safe_min = safe_ranges[param]["min"]
                safe_max = safe_ranges[param]["max"]
                if value < safe_min:
                    experiment["parameters"][param] = safe_min
                elif value > safe_max:
                    experiment["parameters"][param] = safe_max
                    
        return experiment
    
    def _add_safety_measures(
        self,
        experiment: Dict[str, Any],
        risk_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add safety measures based on risk profile"""
        if "safety_checks" not in experiment:
            experiment["safety_checks"] = []
            
        # Add basic safety checks
        basic_checks = [
            {"name": "monitoring", "description": "Ensure monitoring is enabled"},
            {"name": "rollback", "description": "Verify rollback procedure"},
            {"name": "timeout", "description": "Set appropriate timeouts"}
        ]
        
        experiment["safety_checks"].extend(basic_checks)
        
        # Add checks based on failure patterns
        for pattern in risk_profile.get("failure_patterns", []):
            check = {
                "name": f"prevent_{pattern['type']}",
                "description": f"Prevent {pattern['type']} failure pattern",
                "parameters": pattern["parameters"]
            }
            if check not in experiment["safety_checks"]:
                experiment["safety_checks"].append(check)
                
        return experiment
    
    def _optimize_duration(
        self,
        experiment: Dict[str, Any],
        similar: List[ExperimentMemory]
    ) -> Dict[str, Any]:
        """Optimize experiment duration based on historical data"""
        if not similar:
            return experiment
            
        # Get durations of successful experiments
        successful_durations = [
            int(mem.duration.rstrip("s"))
            for mem in similar
            if mem.outcome in [ExperimentOutcome.SUCCESS, ExperimentOutcome.PARTIAL_SUCCESS]
        ]
        
        if successful_durations:
            # Use median duration from successful experiments
            optimal_duration = int(np.median(successful_durations))
            current_duration = int(experiment.get("duration", "30s").rstrip("s"))
            
            # Don't increase duration, only decrease if current is higher
            if current_duration > optimal_duration:
                experiment["duration"] = f"{optimal_duration}s"
                
        return experiment
    
    def _add_monitoring(
        self,
        experiment: Dict[str, Any],
        system_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add monitoring configuration based on system analysis"""
        if "monitoring" not in experiment:
            experiment["monitoring"] = {}
            
        # Add basic metrics
        experiment["monitoring"]["metrics"] = [
            "cpu_usage",
            "memory_usage",
            "error_rate",
            "latency"
        ]
        
        # Add component-specific metrics
        target = experiment["parameters"]["target_component"]
        component_info = next(
            (c for c in system_analysis.get("components", [])
            if c["name"] == target),
            None
        )
        
        if component_info:
            if component_info["type"] == "database":
                experiment["monitoring"]["metrics"].extend([
                    "connection_count",
                    "query_latency",
                    "transaction_rate"
                ])
            elif component_info["type"] == "cache":
                experiment["monitoring"]["metrics"].extend([
                    "hit_rate",
                    "eviction_rate",
                    "memory_fragmentation"
                ])
                
        return experiment
    
    def _calculate_impact_risk(
        self,
        affected_components: List[str],
        relationships: Dict[str, float],
        system_analysis: Dict[str, Any]
    ) -> float:
        """Calculate risk based on impact on other components"""
        if not affected_components:
            return 0.0
            
        # Get criticality of affected components
        critical_components = set(system_analysis.get("critical_components", []))
        critical_count = len(set(affected_components) & critical_components)
        
        # Calculate relationship strength
        rel_strength = sum(
            relationships.get(comp, 0)
            for comp in affected_components
        ) / len(affected_components)
        
        # Combine metrics
        impact_risk = (
            0.7 * (critical_count / len(affected_components)) +
            0.3 * rel_strength
        )
        
        return min(impact_risk, 1.0)
    
    def _calculate_parameter_risk(
        self,
        parameters: Dict[str, Any],
        safe_ranges: Dict[str, Dict[str, float]]
    ) -> float:
        """Calculate risk based on parameter values vs safe ranges"""
        if not safe_ranges:
            return 0.5  # Neutral risk for unknown parameters
            
        risks = []
        for param, value in parameters.items():
            if param in safe_ranges and isinstance(value, (int, float)):
                safe_min = safe_ranges[param]["min"]
                safe_max = safe_ranges[param]["max"]
                
                # Calculate how far the value is from safe range
                if value < safe_min:
                    risk = (safe_min - value) / safe_min
                elif value > safe_max:
                    risk = (value - safe_max) / safe_max
                else:
                    risk = 0.0
                    
                risks.append(risk)
                
        return np.mean(risks) if risks else 0.5
