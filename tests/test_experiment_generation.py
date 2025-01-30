import pytest
from app.services.experiment_generation.generator import ExperimentGenerator
from app.services.experiment_generation.code_generator import ExperimentCodeGenerator
from app.services.validation.safety_validator import SafetyValidator
from app.models.schemas import ExperimentType, Platform, RiskLevel

@pytest.fixture
def system_analysis():
    """Sample system analysis for testing"""
    return {
        "components": [
            {
                "name": "user-service",
                "type": "service",
                "properties": {
                    "language": "python",
                    "framework": "fastapi",
                    "monitoring": True,
                    "circuit_breaker": True,
                    "retry": True
                }
            },
            {
                "name": "auth-service",
                "type": "service",
                "properties": {
                    "language": "node",
                    "framework": "express",
                    "monitoring": True,
                    "circuit_breaker": True,
                    "retry": True
                }
            }
        ],
        "relationships": [
            {
                "from": "user-service",
                "to": "auth-service",
                "type": "http",
                "properties": {
                    "protocol": "http",
                    "timeout": "5s",
                    "retry": True
                }
            }
        ]
    }

@pytest.fixture
def experiment_generator():
    """Initialize ExperimentGenerator"""
    return ExperimentGenerator()

@pytest.fixture
def code_generator():
    """Initialize CodeGenerator"""
    return ExperimentCodeGenerator()

@pytest.fixture
def safety_validator():
    """Initialize SafetyValidator"""
    return SafetyValidator()

@pytest.mark.asyncio
async def test_experiment_generation(experiment_generator, system_analysis):
    """Test generating chaos experiments"""
    experiments = await experiment_generator.generate_experiments(system_analysis)
    
    # Verify experiments were generated
    assert len(experiments) > 0
    
    # Verify experiment structure
    for exp in experiments:
        assert "name" in exp
        assert "type" in exp
        assert exp["type"] in [e.value for e in ExperimentType]
        assert "parameters" in exp
        assert "target_component" in exp["parameters"]
        assert exp["parameters"]["target_component"] in ["user-service", "auth-service"]

@pytest.mark.asyncio
async def test_code_generation(code_generator, system_analysis):
    """Test generating implementation code"""
    # Sample experiment
    experiment = {
        "name": "auth-service-latency",
        "type": "latency_injection",
        "parameters": {
            "target_component": "auth-service",
            "latency_ms": 1000,
            "duration": "30s"
        }
    }
    
    # Test Kubernetes code generation
    k8s_config = {
        "namespace": "default",
        "labels": {"app": "auth-service"}
    }
    k8s_code = await code_generator.generate_code(
        experiment=experiment,
        platform="kubernetes",
        config={"kubernetes": k8s_config}
    )
    
    assert k8s_code["code"] is not None
    assert "deployment_steps" in k8s_code
    assert "rollback_steps" in k8s_code
    
    # Test Docker code generation
    docker_config = {
        "container": "auth-service-1"
    }
    docker_code = await code_generator.generate_code(
        experiment=experiment,
        platform="docker",
        config={"docker": docker_config}
    )
    
    assert docker_code["code"] is not None
    assert "deployment_steps" in docker_code
    assert "rollback_steps" in docker_code

def test_safety_validation(safety_validator, system_analysis):
    """Test safety validation"""
    # Safe experiment
    safe_experiment = {
        "name": "auth-service-latency",
        "type": "latency_injection",
        "parameters": {
            "target_component": "auth-service",
            "latency_ms": 1000,
            "duration": "30s"
        },
        "rollback_procedure": {
            "steps": ["Remove latency injection"]
        }
    }
    
    safe_result = safety_validator.validate_experiment(safe_experiment, system_analysis)
    assert safe_result["is_safe"] is True
    assert safe_result["risk_level"] in [r.value for r in RiskLevel]
    
    # Unsafe experiment (no rollback)
    unsafe_experiment = {
        "name": "auth-service-crash",
        "type": "process_failure",
        "parameters": {
            "target_component": "auth-service",
            "failure_type": "crash",
            "duration": "1h"  # Too long
        }
    }
    
    unsafe_result = safety_validator.validate_experiment(unsafe_experiment, system_analysis)
    assert unsafe_result["is_safe"] is False
    assert len(unsafe_result["violations"]) > 0

@pytest.mark.asyncio
async def test_end_to_end_flow(
    experiment_generator,
    code_generator,
    safety_validator,
    system_analysis
):
    """Test the complete flow from generation to validation to implementation"""
    # Generate experiments
    experiments = await experiment_generator.generate_experiments(system_analysis)
    assert len(experiments) > 0
    
    # Process each experiment
    for experiment in experiments:
        # Validate
        validation = safety_validator.validate_experiment(experiment, system_analysis)
        
        if validation["is_safe"]:
            # Generate implementation
            k8s_code = await code_generator.generate_code(
                experiment=experiment,
                platform="kubernetes",
                config={
                    "kubernetes": {
                        "namespace": "default",
                        "labels": {"app": experiment["parameters"]["target_component"]}
                    }
                }
            )
            
            assert k8s_code["code"] is not None
            assert len(k8s_code["deployment_steps"]) > 0
            assert len(k8s_code["rollback_steps"]) > 0
