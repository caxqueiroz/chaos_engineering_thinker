from typing import Dict, Any, List, Optional
from enum import Enum
import json

class ExperimentType(Enum):
    NETWORK_FAILURE = "network_failure"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    STATE_CORRUPTION = "state_corruption"
    PROCESS_FAILURE = "process_failure"
    CLOCK_SKEW = "clock_skew"
    DATA_CORRUPTION = "data_corruption"
    DEPENDENCY_FAILURE = "dependency_failure"
    SCALING_CHAOS = "scaling_chaos"

class ExperimentTemplate:
    """Base class for experiment templates"""
    
    def __init__(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        safety_checks: List[Dict[str, Any]]
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.safety_checks = safety_checks
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "safety_checks": self.safety_checks,
            "type": self.__class__.__name__.lower().replace("template", "")
        }

class NetworkFailureTemplate(ExperimentTemplate):
    def __init__(self):
        super().__init__(
            name="Network Failure",
            description="Simulate various network failure scenarios",
            parameters={
                "failure_type": {
                    "type": "enum",
                    "values": ["latency", "loss", "corruption", "partition"],
                    "default": "latency"
                },
                "target_component": {
                    "type": "string",
                    "description": "Target service/component"
                },
                "latency_ms": {
                    "type": "integer",
                    "min": 100,
                    "max": 5000,
                    "default": 1000
                },
                "packet_loss_percentage": {
                    "type": "float",
                    "min": 0.1,
                    "max": 100.0,
                    "default": 10.0
                },
                "corruption_percentage": {
                    "type": "float",
                    "min": 0.1,
                    "max": 50.0,
                    "default": 5.0
                }
            },
            safety_checks=[
                {
                    "name": "connectivity_check",
                    "description": "Ensure basic connectivity is maintained"
                },
                {
                    "name": "monitoring_check",
                    "description": "Verify monitoring systems are active"
                }
            ]
        )

class ResourceExhaustionTemplate(ExperimentTemplate):
    def __init__(self):
        super().__init__(
            name="Resource Exhaustion",
            description="Simulate resource exhaustion scenarios",
            parameters={
                "resource_type": {
                    "type": "enum",
                    "values": ["cpu", "memory", "disk", "fd", "connection"],
                    "default": "cpu"
                },
                "target_component": {
                    "type": "string",
                    "description": "Target service/component"
                },
                "utilization_percentage": {
                    "type": "float",
                    "min": 50.0,
                    "max": 95.0,
                    "default": 80.0
                },
                "duration": {
                    "type": "string",
                    "pattern": r"^\d+[sm]$",
                    "default": "30s"
                }
            },
            safety_checks=[
                {
                    "name": "resource_monitor",
                    "description": "Monitor resource usage"
                },
                {
                    "name": "system_health",
                    "description": "Check system health metrics"
                }
            ]
        )

class StateCorruptionTemplate(ExperimentTemplate):
    def __init__(self):
        super().__init__(
            name="State Corruption",
            description="Simulate state corruption scenarios",
            parameters={
                "corruption_type": {
                    "type": "enum",
                    "values": ["data", "config", "cache"],
                    "default": "data"
                },
                "target_component": {
                    "type": "string",
                    "description": "Target service/component"
                },
                "corruption_percentage": {
                    "type": "float",
                    "min": 0.1,
                    "max": 10.0,
                    "default": 1.0
                }
            },
            safety_checks=[
                {
                    "name": "backup_check",
                    "description": "Verify backup availability"
                },
                {
                    "name": "state_validation",
                    "description": "Validate state integrity"
                }
            ]
        )

class ProcessFailureTemplate(ExperimentTemplate):
    def __init__(self):
        super().__init__(
            name="Process Failure",
            description="Simulate process failure scenarios",
            parameters={
                "failure_type": {
                    "type": "enum",
                    "values": ["kill", "pause", "crash"],
                    "default": "kill"
                },
                "target_component": {
                    "type": "string",
                    "description": "Target service/component"
                },
                "process_count": {
                    "type": "integer",
                    "min": 1,
                    "max": 5,
                    "default": 1
                }
            },
            safety_checks=[
                {
                    "name": "process_monitor",
                    "description": "Monitor process status"
                },
                {
                    "name": "recovery_check",
                    "description": "Verify recovery mechanisms"
                }
            ]
        )

class ClockSkewTemplate(ExperimentTemplate):
    def __init__(self):
        super().__init__(
            name="Clock Skew",
            description="Simulate clock synchronization issues",
            parameters={
                "skew_type": {
                    "type": "enum",
                    "values": ["drift", "jump", "freeze"],
                    "default": "drift"
                },
                "target_component": {
                    "type": "string",
                    "description": "Target service/component"
                },
                "skew_amount": {
                    "type": "integer",
                    "min": 1,
                    "max": 3600,
                    "default": 60
                }
            },
            safety_checks=[
                {
                    "name": "time_sync_check",
                    "description": "Monitor time synchronization"
                },
                {
                    "name": "dependency_check",
                    "description": "Check time-dependent services"
                }
            ]
        )

class DataCorruptionTemplate(ExperimentTemplate):
    def __init__(self):
        super().__init__(
            name="Data Corruption",
            description="Simulate data corruption scenarios",
            parameters={
                "corruption_type": {
                    "type": "enum",
                    "values": ["random", "targeted", "boundary"],
                    "default": "random"
                },
                "target_component": {
                    "type": "string",
                    "description": "Target service/component"
                },
                "data_type": {
                    "type": "enum",
                    "values": ["user", "transaction", "config"],
                    "default": "transaction"
                },
                "corruption_rate": {
                    "type": "float",
                    "min": 0.1,
                    "max": 5.0,
                    "default": 1.0
                }
            },
            safety_checks=[
                {
                    "name": "data_integrity",
                    "description": "Check data integrity"
                },
                {
                    "name": "backup_validation",
                    "description": "Validate backup data"
                }
            ]
        )

class DependencyFailureTemplate(ExperimentTemplate):
    def __init__(self):
        super().__init__(
            name="Dependency Failure",
            description="Simulate external dependency failures",
            parameters={
                "dependency_type": {
                    "type": "enum",
                    "values": ["database", "cache", "queue", "api"],
                    "default": "database"
                },
                "target_component": {
                    "type": "string",
                    "description": "Target service/component"
                },
                "failure_mode": {
                    "type": "enum",
                    "values": ["timeout", "error", "slow"],
                    "default": "timeout"
                },
                "error_rate": {
                    "type": "float",
                    "min": 10.0,
                    "max": 100.0,
                    "default": 50.0
                }
            },
            safety_checks=[
                {
                    "name": "fallback_check",
                    "description": "Verify fallback mechanisms"
                },
                {
                    "name": "circuit_breaker",
                    "description": "Check circuit breaker status"
                }
            ]
        )

class ScalingChaosTemplate(ExperimentTemplate):
    def __init__(self):
        super().__init__(
            name="Scaling Chaos",
            description="Simulate scaling and load balancing issues",
            parameters={
                "scenario_type": {
                    "type": "enum",
                    "values": ["scale_up", "scale_down", "rebalance"],
                    "default": "scale_up"
                },
                "target_component": {
                    "type": "string",
                    "description": "Target service/component"
                },
                "instance_count": {
                    "type": "integer",
                    "min": 1,
                    "max": 10,
                    "default": 3
                },
                "rate_of_change": {
                    "type": "string",
                    "pattern": r"^\d+[sm]$",
                    "default": "30s"
                }
            },
            safety_checks=[
                {
                    "name": "capacity_check",
                    "description": "Monitor system capacity"
                },
                {
                    "name": "load_balance_check",
                    "description": "Verify load balancing"
                }
            ]
        )

class ExperimentTemplateFactory:
    """Factory for creating experiment templates"""
    
    @staticmethod
    def create_template(experiment_type: ExperimentType) -> ExperimentTemplate:
        templates = {
            ExperimentType.NETWORK_FAILURE: NetworkFailureTemplate,
            ExperimentType.RESOURCE_EXHAUSTION: ResourceExhaustionTemplate,
            ExperimentType.STATE_CORRUPTION: StateCorruptionTemplate,
            ExperimentType.PROCESS_FAILURE: ProcessFailureTemplate,
            ExperimentType.CLOCK_SKEW: ClockSkewTemplate,
            ExperimentType.DATA_CORRUPTION: DataCorruptionTemplate,
            ExperimentType.DEPENDENCY_FAILURE: DependencyFailureTemplate,
            ExperimentType.SCALING_CHAOS: ScalingChaosTemplate
        }
        
        template_class = templates.get(experiment_type)
        if not template_class:
            raise ValueError(f"Unknown experiment type: {experiment_type}")
            
        return template_class()
    
    @staticmethod
    def get_all_templates() -> Dict[str, ExperimentTemplate]:
        """Get all available templates"""
        return {
            exp_type.value: ExperimentTemplateFactory.create_template(exp_type)
            for exp_type in ExperimentType
        }
        
    @staticmethod
    def validate_parameters(
        template: ExperimentTemplate,
        parameters: Dict[str, Any]
    ) -> List[str]:
        """Validate parameters against template"""
        errors = []
        
        for param_name, param_spec in template.parameters.items():
            if param_name not in parameters:
                if "default" not in param_spec:
                    errors.append(f"Missing required parameter: {param_name}")
                continue
                
            value = parameters[param_name]
            
            if param_spec["type"] == "enum":
                if value not in param_spec["values"]:
                    errors.append(
                        f"Invalid value for {param_name}: {value}. "
                        f"Must be one of {param_spec['values']}"
                    )
            elif param_spec["type"] in ["integer", "float"]:
                try:
                    value = float(value)
                    if "min" in param_spec and value < param_spec["min"]:
                        errors.append(
                            f"Value for {param_name} too low: {value}. "
                            f"Minimum is {param_spec['min']}"
                        )
                    if "max" in param_spec and value > param_spec["max"]:
                        errors.append(
                            f"Value for {param_name} too high: {value}. "
                            f"Maximum is {param_spec['max']}"
                        )
                except ValueError:
                    errors.append(f"Invalid number for {param_name}: {value}")
                    
        return errors
