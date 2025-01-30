import pytest
from datetime import datetime
from app.agents.intelligence.memory_store import (
    MemoryStore,
    ExperimentMemory,
    ExperimentOutcome
)
from app.agents.intelligence.experiment_planner import ExperimentPlanner

@pytest.fixture
def memory_store():
    """Initialize memory store with some test data"""
    store = MemoryStore()
    
    # Add successful experiment
    store.add_experiment(ExperimentMemory(
        experiment_id="exp1",
        timestamp=datetime.now(),
        experiment_type="network_failure",
        target_component="user-service",
        parameters={
            "failure_type": "latency",
            "latency_ms": 1000,
            "duration": "30s"
        },
        outcome=ExperimentOutcome.SUCCESS,
        metrics={
            "error_rate": 0.1,
            "latency_p99": 1200
        },
        learnings=[
            "Service handled latency well",
            "No cascade failures observed"
        ],
        affected_components=["user-service", "auth-service"],
        duration="30s",
        risk_level="medium"
    ))
    
    # Add failed experiment
    store.add_experiment(ExperimentMemory(
        experiment_id="exp2",
        timestamp=datetime.now(),
        experiment_type="network_failure",
        target_component="user-service",
        parameters={
            "failure_type": "latency",
            "latency_ms": 5000,
            "duration": "60s"
        },
        outcome=ExperimentOutcome.FAILURE,
        metrics={
            "error_rate": 0.8,
            "latency_p99": 6000
        },
        learnings=[
            "Latency too high caused cascading failures",
            "Circuit breaker didn't trigger fast enough"
        ],
        affected_components=["user-service", "auth-service", "order-service"],
        duration="60s",
        risk_level="high"
    ))
    
    return store

@pytest.fixture
def experiment_planner(memory_store):
    """Initialize experiment planner"""
    return ExperimentPlanner(memory_store)

@pytest.fixture
def system_analysis():
    """Sample system analysis"""
    return {
        "components": [
            {
                "name": "user-service",
                "type": "service",
                "properties": {
                    "language": "python",
                    "framework": "fastapi",
                    "monitoring": True
                }
            },
            {
                "name": "auth-service",
                "type": "service",
                "properties": {
                    "language": "node",
                    "framework": "express",
                    "monitoring": True
                }
            }
        ],
        "critical_components": ["user-service"],
        "relationships": [
            {
                "from": "user-service",
                "to": "auth-service",
                "type": "http"
            }
        ]
    }

def test_memory_store_similar_experiments(memory_store):
    """Test finding similar experiments"""
    new_experiment = {
        "type": "network_failure",
        "parameters": {
            "target_component": "user-service",
            "failure_type": "latency",
            "latency_ms": 2000
        }
    }
    
    similar = memory_store.get_similar_experiments(new_experiment)
    assert len(similar) == 2
    assert similar[0].experiment_id in ["exp1", "exp2"]

def test_memory_store_risk_profile(memory_store):
    """Test building risk profiles"""
    profile = memory_store.get_component_risk_profile("user-service")
    
    assert "success_rate" in profile
    assert "risk_score" in profile
    assert "safe_parameter_ranges" in profile
    assert "failure_patterns" in profile
    
    # Check success rate calculation
    assert profile["success_rate"] == 0.5  # 1 success, 1 failure

def test_experiment_planner_enhancement(experiment_planner, system_analysis):
    """Test experiment enhancement"""
    experiment = {
        "type": "network_failure",
        "parameters": {
            "target_component": "user-service",
            "failure_type": "latency",
            "latency_ms": 4000,
            "duration": "45s"
        }
    }
    
    enhanced = experiment_planner.enhance_experiment(experiment, system_analysis)
    
    # Should have adjusted parameters based on history
    assert enhanced["parameters"]["latency_ms"] <= 4000  # Should be reduced
    assert "safety_checks" in enhanced
    assert "monitoring" in enhanced

def test_experiment_planner_risk_calculation(experiment_planner, system_analysis):
    """Test risk calculation"""
    experiment = {
        "type": "network_failure",
        "parameters": {
            "target_component": "user-service",
            "failure_type": "latency",
            "latency_ms": 3000,
            "duration": "40s"
        },
        "affected_components": ["user-service", "auth-service"]
    }
    
    risk = experiment_planner.calculate_experiment_risk(experiment, system_analysis)
    
    assert "total_risk" in risk
    assert "base_risk" in risk
    assert "impact_risk" in risk
    assert "parameter_risk" in risk
    assert "duration_risk" in risk
    
    # Risk should be higher because user-service is critical
    assert risk["impact_risk"] > 0.5

def test_safety_measures_addition(experiment_planner, system_analysis):
    """Test safety measures are properly added"""
    experiment = {
        "type": "network_failure",
        "parameters": {
            "target_component": "user-service",
            "failure_type": "latency",
            "latency_ms": 2000
        }
    }
    
    enhanced = experiment_planner.enhance_experiment(experiment, system_analysis)
    
    # Check safety checks
    assert "safety_checks" in enhanced
    safety_checks = [check["name"] for check in enhanced["safety_checks"]]
    assert "monitoring" in safety_checks
    assert "rollback" in safety_checks
    assert "timeout" in safety_checks

def test_monitoring_configuration(experiment_planner, system_analysis):
    """Test monitoring configuration is properly added"""
    experiment = {
        "type": "network_failure",
        "parameters": {
            "target_component": "user-service",
            "failure_type": "latency",
            "latency_ms": 2000
        }
    }
    
    enhanced = experiment_planner.enhance_experiment(experiment, system_analysis)
    
    # Check monitoring configuration
    assert "monitoring" in enhanced
    assert "metrics" in enhanced["monitoring"]
    metrics = enhanced["monitoring"]["metrics"]
    
    # Should have basic metrics
    assert "cpu_usage" in metrics
    assert "memory_usage" in metrics
    assert "error_rate" in metrics
    assert "latency" in metrics

def test_duration_optimization(experiment_planner, system_analysis):
    """Test experiment duration is optimized"""
    experiment = {
        "type": "network_failure",
        "parameters": {
            "target_component": "user-service",
            "failure_type": "latency",
            "latency_ms": 2000
        },
        "duration": "90s"  # Too long based on history
    }
    
    enhanced = experiment_planner.enhance_experiment(experiment, system_analysis)
    
    # Duration should be reduced based on successful experiments
    assert int(enhanced["duration"].rstrip("s")) <= 60  # Should be reduced to safer duration

def test_parameter_adjustment(experiment_planner, system_analysis):
    """Test parameters are adjusted based on history"""
    experiment = {
        "type": "network_failure",
        "parameters": {
            "target_component": "user-service",
            "failure_type": "latency",
            "latency_ms": 6000  # Too high based on history
        }
    }
    
    enhanced = experiment_planner.enhance_experiment(experiment, system_analysis)
    
    # Latency should be reduced based on failed experiment history
    assert enhanced["parameters"]["latency_ms"] < 6000
