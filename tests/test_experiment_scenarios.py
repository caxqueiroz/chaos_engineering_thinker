import pytest
from app.services.experiment_generation.generator import ExperimentGenerator
from app.services.experiment_generation.code_generator import ExperimentCodeGenerator
from app.services.validation.safety_validator import SafetyValidator

@pytest.fixture
def microservices_system():
    """Complex microservices system for testing"""
    return {
        "components": [
            {
                "name": "api-gateway",
                "type": "service",
                "properties": {
                    "language": "go",
                    "framework": "gin",
                    "monitoring": True,
                    "circuit_breaker": True,
                    "retry": True,
                    "autoscaling": True
                }
            },
            {
                "name": "user-service",
                "type": "service",
                "properties": {
                    "language": "python",
                    "framework": "fastapi",
                    "monitoring": True,
                    "circuit_breaker": True,
                    "retry": True,
                    "cache": True
                }
            },
            {
                "name": "order-service",
                "type": "service",
                "properties": {
                    "language": "java",
                    "framework": "spring-boot",
                    "monitoring": True,
                    "circuit_breaker": True,
                    "retry": True,
                    "cache": True
                }
            },
            {
                "name": "payment-service",
                "type": "service",
                "properties": {
                    "language": "node",
                    "framework": "express",
                    "monitoring": True,
                    "circuit_breaker": True,
                    "retry": True
                }
            },
            {
                "name": "user-db",
                "type": "database",
                "properties": {
                    "type": "postgresql",
                    "version": "13",
                    "monitoring": True,
                    "backup": True,
                    "ha": True
                }
            },
            {
                "name": "order-db",
                "type": "database",
                "properties": {
                    "type": "mongodb",
                    "version": "5",
                    "monitoring": True,
                    "backup": True,
                    "ha": True
                }
            },
            {
                "name": "redis-cache",
                "type": "cache",
                "properties": {
                    "type": "redis",
                    "version": "6",
                    "monitoring": True,
                    "ha": True
                }
            },
            {
                "name": "rabbitmq",
                "type": "queue",
                "properties": {
                    "type": "rabbitmq",
                    "version": "3",
                    "monitoring": True,
                    "ha": True
                }
            }
        ],
        "relationships": [
            {
                "from": "api-gateway",
                "to": "user-service",
                "type": "http",
                "properties": {
                    "protocol": "http",
                    "timeout": "5s",
                    "retry": True
                }
            },
            {
                "from": "api-gateway",
                "to": "order-service",
                "type": "http",
                "properties": {
                    "protocol": "http",
                    "timeout": "5s",
                    "retry": True
                }
            },
            {
                "from": "order-service",
                "to": "payment-service",
                "type": "http",
                "properties": {
                    "protocol": "http",
                    "timeout": "10s",
                    "retry": True,
                    "circuit_breaker": True
                }
            },
            {
                "from": "user-service",
                "to": "user-db",
                "type": "database",
                "properties": {
                    "protocol": "postgresql",
                    "timeout": "30s",
                    "pool_size": 10
                }
            },
            {
                "from": "order-service",
                "to": "order-db",
                "type": "database",
                "properties": {
                    "protocol": "mongodb",
                    "timeout": "30s",
                    "pool_size": 20
                }
            },
            {
                "from": "user-service",
                "to": "redis-cache",
                "type": "cache",
                "properties": {
                    "protocol": "redis",
                    "timeout": "1s"
                }
            },
            {
                "from": "order-service",
                "to": "rabbitmq",
                "type": "queue",
                "properties": {
                    "protocol": "amqp",
                    "timeout": "5s"
                }
            }
        ]
    }

@pytest.fixture
def kubernetes_config():
    """Kubernetes configuration for testing"""
    return {
        "kubernetes": {
            "namespace": "production",
            "labels": {
                "environment": "prod",
                "team": "platform"
            },
            "annotations": {
                "prometheus.io/scrape": "true"
            }
        }
    }

@pytest.mark.asyncio
async def test_api_gateway_scenarios(
    experiment_generator,
    code_generator,
    safety_validator,
    microservices_system,
    kubernetes_config
):
    """Test API Gateway failure scenarios"""
    experiments = await experiment_generator.generate_experiments(microservices_system)
    
    # Find API Gateway experiments
    api_experiments = [
        exp for exp in experiments
        if exp["parameters"]["target_component"] == "api-gateway"
    ]
    
    assert len(api_experiments) > 0
    
    for exp in api_experiments:
        validation = safety_validator.validate_experiment(exp, microservices_system)
        
        if validation["is_safe"]:
            code = await code_generator.generate_code(
                experiment=exp,
                platform="kubernetes",
                config=kubernetes_config
            )
            
            assert "apiVersion: chaos-mesh.org/v1alpha1" in code["code"]
            assert "metadata:" in code["code"]
            assert "namespace: production" in code["code"]

@pytest.mark.asyncio
async def test_database_failure_scenarios(
    experiment_generator,
    code_generator,
    safety_validator,
    microservices_system,
    kubernetes_config
):
    """Test database failure scenarios"""
    experiments = await experiment_generator.generate_experiments(microservices_system)
    
    # Find database experiments
    db_experiments = [
        exp for exp in experiments
        if exp["parameters"]["target_component"] in ["user-db", "order-db"]
    ]
    
    assert len(db_experiments) > 0
    
    for exp in db_experiments:
        validation = safety_validator.validate_experiment(exp, microservices_system)
        
        # Database experiments should require extra safety checks
        if "backup" not in exp.get("safety_checks", []):
            assert not validation["is_safe"]
            assert any(
                "backup" in v["description"].lower()
                for v in validation["violations"]
            )

@pytest.mark.asyncio
async def test_cache_failure_scenarios(
    experiment_generator,
    code_generator,
    safety_validator,
    microservices_system
):
    """Test cache failure scenarios"""
    experiments = await experiment_generator.generate_experiments(microservices_system)
    
    # Find cache experiments
    cache_experiments = [
        exp for exp in experiments
        if exp["parameters"]["target_component"] == "redis-cache"
    ]
    
    assert len(cache_experiments) > 0
    
    for exp in cache_experiments:
        validation = safety_validator.validate_experiment(exp, microservices_system)
        
        # Cache experiments should be relatively safe
        assert validation["is_safe"]
        assert validation["risk_level"] in ["low", "medium"]

@pytest.mark.asyncio
async def test_message_queue_scenarios(
    experiment_generator,
    code_generator,
    safety_validator,
    microservices_system
):
    """Test message queue failure scenarios"""
    experiments = await experiment_generator.generate_experiments(microservices_system)
    
    # Find queue experiments
    queue_experiments = [
        exp for exp in experiments
        if exp["parameters"]["target_component"] == "rabbitmq"
    ]
    
    assert len(queue_experiments) > 0
    
    for exp in queue_experiments:
        validation = safety_validator.validate_experiment(exp, microservices_system)
        
        if validation["is_safe"]:
            # Ensure message queue experiments have proper monitoring
            assert any(
                "monitoring" in check["name"].lower()
                for check in exp.get("safety_checks", [])
            )

@pytest.mark.asyncio
async def test_cross_component_scenarios(
    experiment_generator,
    code_generator,
    safety_validator,
    microservices_system
):
    """Test scenarios affecting multiple components"""
    experiments = await experiment_generator.generate_experiments(microservices_system)
    
    # Find cross-component experiments
    cross_experiments = [
        exp for exp in experiments
        if len(exp["parameters"].get("affected_components", [])) > 1
    ]
    
    assert len(cross_experiments) > 0
    
    for exp in cross_experiments:
        validation = safety_validator.validate_experiment(exp, microservices_system)
        
        # Cross-component experiments should be high risk
        if validation["is_safe"]:
            assert validation["risk_level"] in ["high"]
            
        # Should have rollback procedures
        assert "rollback_procedure" in exp
        assert len(exp["rollback_procedure"]["steps"]) > 0

@pytest.mark.asyncio
async def test_resource_exhaustion_scenarios(
    experiment_generator,
    code_generator,
    safety_validator,
    microservices_system
):
    """Test resource exhaustion scenarios"""
    experiments = await experiment_generator.generate_experiments(microservices_system)
    
    # Find resource experiments
    resource_experiments = [
        exp for exp in experiments
        if exp["type"] == "resource_exhaustion"
    ]
    
    assert len(resource_experiments) > 0
    
    for exp in resource_experiments:
        validation = safety_validator.validate_experiment(exp, microservices_system)
        
        # Resource experiments should have limits
        if validation["is_safe"]:
            assert "resource_limits" in exp["parameters"]
            assert float(exp["parameters"]["resource_limits"]["cpu"]) <= 0.8
            assert float(exp["parameters"]["resource_limits"]["memory"]) <= 0.8

@pytest.mark.asyncio
async def test_network_partition_scenarios(
    experiment_generator,
    code_generator,
    safety_validator,
    microservices_system
):
    """Test network partition scenarios"""
    experiments = await experiment_generator.generate_experiments(microservices_system)
    
    # Find network partition experiments
    partition_experiments = [
        exp for exp in experiments
        if exp["type"] == "network_failure"
        and exp["parameters"].get("failure_type") == "partition"
    ]
    
    assert len(partition_experiments) > 0
    
    for exp in partition_experiments:
        validation = safety_validator.validate_experiment(exp, microservices_system)
        
        # Network partitions should affect multiple components
        assert len(exp["parameters"].get("affected_components", [])) > 1
        
        if validation["is_safe"]:
            # Should have monitoring for both sides of partition
            assert all(
                comp["properties"].get("monitoring", False)
                for comp in microservices_system["components"]
                if comp["name"] in exp["parameters"]["affected_components"]
            )
