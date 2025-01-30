from typing import Dict, Any, List, Optional
from enum import Enum
import re

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SafetyValidator:
    """Validates chaos engineering experiments for safety."""
    
    def __init__(self):
        # Define safety rules
        self.safety_rules = {
            "general": [
                {
                    "name": "has_rollback",
                    "description": "Experiment must have a rollback procedure",
                    "severity": RiskLevel.CRITICAL,
                    "validator": self._validate_rollback
                },
                {
                    "name": "has_monitoring",
                    "description": "System must have monitoring in place",
                    "severity": RiskLevel.HIGH,
                    "validator": self._validate_monitoring
                },
                {
                    "name": "has_timeout",
                    "description": "Experiment must have a timeout",
                    "severity": RiskLevel.HIGH,
                    "validator": self._validate_timeout
                }
            ],
            "network": [
                {
                    "name": "has_fallback",
                    "description": "Service must have fallback mechanisms",
                    "severity": RiskLevel.HIGH,
                    "validator": self._validate_fallback
                },
                {
                    "name": "has_retry",
                    "description": "Service must have retry mechanisms",
                    "severity": RiskLevel.MEDIUM,
                    "validator": self._validate_retry
                }
            ],
            "resource": [
                {
                    "name": "has_limits",
                    "description": "Component must have resource limits",
                    "severity": RiskLevel.HIGH,
                    "validator": self._validate_resource_limits
                },
                {
                    "name": "has_autoscaling",
                    "description": "Service should have autoscaling",
                    "severity": RiskLevel.MEDIUM,
                    "validator": self._validate_autoscaling
                }
            ],
            "dependency": [
                {
                    "name": "has_circuit_breaker",
                    "description": "Service must have circuit breaker",
                    "severity": RiskLevel.HIGH,
                    "validator": self._validate_circuit_breaker
                },
                {
                    "name": "has_cache",
                    "description": "Service should have caching",
                    "severity": RiskLevel.MEDIUM,
                    "validator": self._validate_cache
                }
            ]
        }
    
    def validate_experiment(
        self,
        experiment: Dict[str, Any],
        system_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate a proposed chaos engineering experiment.
        
        Args:
            experiment: The proposed experiment
            system_analysis: Analysis of the system
            
        Returns:
            Dictionary containing:
                - is_safe: Boolean indicating if the experiment is safe
                - risk_level: Overall risk level
                - violations: List of safety violations
                - warnings: List of warnings
                - recommendations: List of safety recommendations
        """
        violations = []
        warnings = []
        recommendations = []
        
        # Apply general safety rules
        self._apply_rules(
            "general",
            experiment,
            system_analysis,
            violations,
            warnings,
            recommendations
        )
        
        # Apply type-specific rules
        experiment_type = self._determine_experiment_type(experiment)
        if experiment_type:
            self._apply_rules(
                experiment_type,
                experiment,
                system_analysis,
                violations,
                warnings,
                recommendations
            )
            
        # Calculate overall risk level
        risk_level = self._calculate_risk_level(violations, warnings)
        
        return {
            "is_safe": len(violations) == 0,
            "risk_level": risk_level.value,
            "violations": violations,
            "warnings": warnings,
            "recommendations": recommendations
        }
    
    def _apply_rules(
        self,
        rule_type: str,
        experiment: Dict[str, Any],
        system_analysis: Dict[str, Any],
        violations: List[Dict[str, Any]],
        warnings: List[Dict[str, Any]],
        recommendations: List[Dict[str, Any]]
    ):
        """Apply a set of safety rules to the experiment."""
        rules = self.safety_rules.get(rule_type, [])
        
        for rule in rules:
            try:
                result = rule["validator"](experiment, system_analysis)
                if not result["passed"]:
                    if rule["severity"] in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                        violations.append({
                            "rule": rule["name"],
                            "description": rule["description"],
                            "details": result["details"]
                        })
                    else:
                        warnings.append({
                            "rule": rule["name"],
                            "description": rule["description"],
                            "details": result["details"]
                        })
                        
                    if "recommendation" in result:
                        recommendations.append({
                            "rule": rule["name"],
                            "recommendation": result["recommendation"]
                        })
            except Exception as e:
                violations.append({
                    "rule": rule["name"],
                    "description": "Error validating rule",
                    "details": str(e)
                })
    
    def _determine_experiment_type(self, experiment: Dict[str, Any]) -> Optional[str]:
        """Determine the type of experiment for rule selection."""
        if "type" in experiment:
            return experiment["type"]
            
        # Infer type from experiment parameters
        if "network_failure" in experiment.get("name", "").lower():
            return "network"
        elif "resource" in experiment.get("name", "").lower():
            return "resource"
        elif "dependency" in experiment.get("name", "").lower():
            return "dependency"
            
        return None
    
    def _calculate_risk_level(
        self,
        violations: List[Dict[str, Any]],
        warnings: List[Dict[str, Any]]
    ) -> RiskLevel:
        """Calculate overall risk level based on violations and warnings."""
        if any(v["rule"] == "has_rollback" for v in violations):
            return RiskLevel.CRITICAL
            
        if len(violations) > 0:
            return RiskLevel.HIGH
            
        if len(warnings) > 2:
            return RiskLevel.MEDIUM
            
        return RiskLevel.LOW
    
    def _validate_rollback(
        self,
        experiment: Dict[str, Any],
        system_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate rollback procedure."""
        if "rollback_procedure" not in experiment:
            return {
                "passed": False,
                "details": "No rollback procedure defined",
                "recommendation": "Define a step-by-step rollback procedure"
            }
            
        rollback = experiment["rollback_procedure"]
        if not isinstance(rollback, dict) or "steps" not in rollback:
            return {
                "passed": False,
                "details": "Rollback procedure must contain steps",
                "recommendation": "Define specific rollback steps"
            }
            
        return {"passed": True}
    
    def _validate_monitoring(
        self,
        experiment: Dict[str, Any],
        system_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate monitoring requirements."""
        # Check if target component has monitoring
        target = experiment.get("parameters", {}).get("target_component")
        if not target:
            return {
                "passed": False,
                "details": "No target component specified"
            }
            
        # Look for monitoring in system analysis
        monitoring_found = False
        for doc in system_analysis.values():
            if "components" in doc:
                for comp in doc["components"]:
                    if comp["name"] == target and "monitoring" in comp.get("properties", {}):
                        monitoring_found = True
                        break
                        
        if not monitoring_found:
            return {
                "passed": False,
                "details": f"No monitoring found for component {target}",
                "recommendation": "Set up monitoring before running the experiment"
            }
            
        return {"passed": True}
    
    def _validate_timeout(
        self,
        experiment: Dict[str, Any],
        system_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate timeout settings."""
        params = experiment.get("parameters", {})
        
        # Check for duration parameter
        if "duration" not in params:
            return {
                "passed": False,
                "details": "No duration specified",
                "recommendation": "Specify a maximum duration for the experiment"
            }
            
        # Validate duration format and value
        duration = params["duration"]
        if not isinstance(duration, (int, str)):
            return {
                "passed": False,
                "details": "Invalid duration format"
            }
            
        # If duration is string, parse it
        if isinstance(duration, str):
            # Parse duration string (e.g., "5m", "1h")
            match = re.match(r"^(\d+)([smh])$", duration)
            if not match:
                return {
                    "passed": False,
                    "details": "Invalid duration format",
                    "recommendation": "Use format: <number><unit> (e.g., 5m, 1h)"
                }
                
            value = int(match.group(1))
            unit = match.group(2)
            
            # Convert to seconds for comparison
            multipliers = {"s": 1, "m": 60, "h": 3600}
            duration_seconds = value * multipliers[unit]
            
            # Check if duration is too long
            if duration_seconds > 3600:  # 1 hour
                return {
                    "passed": False,
                    "details": "Duration too long",
                    "recommendation": "Limit experiment duration to 1 hour"
                }
                
        return {"passed": True}
    
    def _validate_fallback(
        self,
        experiment: Dict[str, Any],
        system_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate fallback mechanisms."""
        target = experiment.get("parameters", {}).get("target_component")
        if not target:
            return {"passed": False, "details": "No target component specified"}
            
        # Check for fallback in system analysis
        for doc in system_analysis.values():
            if "components" in doc:
                for comp in doc["components"]:
                    if comp["name"] == target:
                        props = comp.get("properties", {})
                        if not any(
                            key in props
                            for key in ["fallback", "failover", "backup"]
                        ):
                            return {
                                "passed": False,
                                "details": f"No fallback mechanism found for {target}",
                                "recommendation": "Implement fallback mechanism"
                            }
                            
        return {"passed": True}
    
    def _validate_retry(
        self,
        experiment: Dict[str, Any],
        system_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate retry mechanisms."""
        target = experiment.get("parameters", {}).get("target_component")
        if not target:
            return {"passed": False, "details": "No target component specified"}
            
        # Check for retry in system analysis
        for doc in system_analysis.values():
            if "components" in doc:
                for comp in doc["components"]:
                    if comp["name"] == target:
                        props = comp.get("properties", {})
                        if "retry" not in props:
                            return {
                                "passed": False,
                                "details": f"No retry mechanism found for {target}",
                                "recommendation": "Implement retry mechanism"
                            }
                            
        return {"passed": True}
    
    def _validate_resource_limits(
        self,
        experiment: Dict[str, Any],
        system_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate resource limits."""
        target = experiment.get("parameters", {}).get("target_component")
        if not target:
            return {"passed": False, "details": "No target component specified"}
            
        # Check for resource limits in system analysis
        for doc in system_analysis.values():
            if "components" in doc:
                for comp in doc["components"]:
                    if comp["name"] == target:
                        props = comp.get("properties", {})
                        if not any(
                            key in props
                            for key in ["resource_limits", "cpu_limit", "memory_limit"]
                        ):
                            return {
                                "passed": False,
                                "details": f"No resource limits found for {target}",
                                "recommendation": "Set resource limits"
                            }
                            
        return {"passed": True}
    
    def _validate_autoscaling(
        self,
        experiment: Dict[str, Any],
        system_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate autoscaling configuration."""
        target = experiment.get("parameters", {}).get("target_component")
        if not target:
            return {"passed": False, "details": "No target component specified"}
            
        # Check for autoscaling in system analysis
        for doc in system_analysis.values():
            if "components" in doc:
                for comp in doc["components"]:
                    if comp["name"] == target:
                        props = comp.get("properties", {})
                        if "autoscaling" not in props:
                            return {
                                "passed": False,
                                "details": f"No autoscaling found for {target}",
                                "recommendation": "Configure autoscaling"
                            }
                            
        return {"passed": True}
    
    def _validate_circuit_breaker(
        self,
        experiment: Dict[str, Any],
        system_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate circuit breaker implementation."""
        target = experiment.get("parameters", {}).get("target_component")
        if not target:
            return {"passed": False, "details": "No target component specified"}
            
        # Check for circuit breaker in system analysis
        for doc in system_analysis.values():
            if "components" in doc:
                for comp in doc["components"]:
                    if comp["name"] == target:
                        props = comp.get("properties", {})
                        if "circuit_breaker" not in props:
                            return {
                                "passed": False,
                                "details": f"No circuit breaker found for {target}",
                                "recommendation": "Implement circuit breaker"
                            }
                            
        return {"passed": True}
    
    def _validate_cache(
        self,
        experiment: Dict[str, Any],
        system_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate caching mechanisms."""
        target = experiment.get("parameters", {}).get("target_component")
        if not target:
            return {"passed": False, "details": "No target component specified"}
            
        # Check for caching in system analysis
        for doc in system_analysis.values():
            if "components" in doc:
                for comp in doc["components"]:
                    if comp["name"] == target:
                        props = comp.get("properties", {})
                        if not any(
                            key in props
                            for key in ["cache", "caching", "redis"]
                        ):
                            return {
                                "passed": False,
                                "details": f"No caching mechanism found for {target}",
                                "recommendation": "Implement caching"
                            }
                            
        return {"passed": True}
