import pytest
from datetime import datetime
from app.agents.intelligence.memory_store import (
    MemoryStore,
    ExperimentMemory,
    ExperimentOutcome
)
from app.agents.intelligence.experiment_planner import ExperimentPlanner
from app.agents.intelligence.experiment_predictor import ExperimentPredictor
from app.agents.intelligence.experiment_templates import (
    ExperimentTemplateFactory,
    ExperimentType
)

@pytest.fixture
def populated_memory_store():
    """Create memory store with diverse experiment history"""
    store = MemoryStore()
    
    # Add successful network experiments
    for i in range(5):
        store.add_experiment(ExperimentMemory(
            experiment_id=f"net_success_{i}",
            timestamp=datetime.now(),
            experiment_type="network_failure",
            target_component="api-gateway",
            parameters={
                "failure_type": "latency",
                "latency_ms": 1000 + i * 200
            },
            outcome=ExperimentOutcome.SUCCESS,
            metrics={"error_rate": 0.1},
            learnings=["Latency handled well"],
            affected_components=["api-gateway", "auth-service"],
            duration="30s",
            risk_level="medium"
        ))
        
    # Add failed network experiments
    for i in range(3):
        store.add_experiment(ExperimentMemory(
            experiment_id=f"net_fail_{i}",
            timestamp=datetime.now(),
            experiment_type="network_failure",
            target_component="api-gateway",
            parameters={
                "failure_type": "latency",
                "latency_ms": 4000 + i * 1000
            },
            outcome=ExperimentOutcome.FAILURE,
            metrics={"error_rate": 0.8},
            learnings=["Latency too high"],
            affected_components=["api-gateway", "auth-service", "user-service"],
            duration="45s",
            risk_level="high"
        ))
        
    # Add resource exhaustion experiments
    for i in range(4):
        store.add_experiment(ExperimentMemory(
            experiment_id=f"resource_{i}",
            timestamp=datetime.now(),
            experiment_type="resource_exhaustion",
            target_component="user-service",
            parameters={
                "resource_type": "cpu",
                "utilization_percentage": 80 + i * 5
            },
            outcome=ExperimentOutcome.SUCCESS if i < 2 else ExperimentOutcome.FAILURE,
            metrics={"cpu_usage": 80 + i * 5},
            learnings=["CPU threshold identified"],
            affected_components=["user-service"],
            duration="30s",
            risk_level="medium"
        ))
        
    return store

@pytest.fixture
def system_analysis():
    """Sample system analysis"""
    return {
        "components": [
            {
                "name": "api-gateway",
                "type": "service",
                "properties": {
                    "language": "python",
                    "framework": "fastapi"
                }
            },
            {
                "name": "auth-service",
                "type": "service",
                "properties": {
                    "language": "node",
                    "framework": "express"
                }
            },
            {
                "name": "user-service",
                "type": "service",
                "properties": {
                    "language": "python",
                    "framework": "django"
                }
            }
        ],
        "critical_components": ["api-gateway", "auth-service"],
        "relationships": [
            {
                "from": "api-gateway",
                "to": "auth-service",
                "type": "http"
            },
            {
                "from": "auth-service",
                "to": "user-service",
                "type": "http"
            }
        ]
    }

@pytest.fixture
def trained_predictor(populated_memory_store):
    predictor = ExperimentPredictor(populated_memory_store)
    predictor.train_model()
    return predictor

def test_end_to_end_experiment_flow(populated_memory_store, system_analysis, trained_predictor):
    """Test complete experiment flow with intelligence"""
    # Initialize components
    planner = ExperimentPlanner(populated_memory_store)
    
    # Create experiment from template
    template = ExperimentTemplateFactory.create_template(ExperimentType.NETWORK_FAILURE)
    experiment = template.to_dict()
    experiment["parameters"].update({
        "target_component": "api-gateway",
        "failure_type": "latency",
        "latency_ms": 3000
    })
    
    # Get prediction
    prediction = trained_predictor.predict_outcome(experiment, system_analysis)
    assert "predicted_outcome" in prediction
    assert "success_probability" in prediction
    
    # Get improvement suggestions
    suggestions = trained_predictor.suggest_improvements(experiment, system_analysis)
    assert len(suggestions) > 0
    
    # Apply suggestions
    if suggestions:
        for suggestion in suggestions:
            if suggestion["type"] == "parameter_adjustment":
                experiment["parameters"][suggestion["parameter"]] = suggestion["suggested_value"]
            elif suggestion["type"] == "duration_adjustment":
                experiment["duration"] = suggestion["suggested_duration"]
    
    # Enhance experiment
    enhanced = planner.enhance_experiment(experiment, system_analysis)
    
    # Validate enhanced experiment
    assert "safety_checks" in enhanced
    assert "monitoring" in enhanced
    assert len(enhanced["safety_checks"]) > 0

def test_template_integration(populated_memory_store, system_analysis, trained_predictor):
    """Test template integration with intelligence"""
    planner = ExperimentPlanner(populated_memory_store)
    
    # Test each template type
    for exp_type in ExperimentType:
        template = ExperimentTemplateFactory.create_template(exp_type)
        experiment = template.to_dict()
        
        # Set basic parameters
        experiment["parameters"]["target_component"] = "api-gateway"
        
        # Enhance with intelligence
        enhanced = planner.enhance_experiment(experiment, system_analysis)
        
        # Validate
        assert "safety_checks" in enhanced
        assert len(enhanced["safety_checks"]) >= len(template.safety_checks)
        assert "monitoring" in enhanced
        
        # Predict outcome
        prediction = trained_predictor.predict_outcome(enhanced, system_analysis)
        assert "predicted_outcome" in prediction
        assert "success_probability" in prediction

def test_learning_integration(populated_memory_store, system_analysis):
    """Test learning and adaptation"""
    predictor = ExperimentPredictor(populated_memory_store)
    predictor.train_model()
    
    # Create similar experiments with different parameters
    base_experiment = {
        "type": "network_failure",
        "parameters": {
            "target_component": "api-gateway",
            "failure_type": "latency",
            "latency_ms": 2000
        }
    }
    
    # Get initial prediction
    initial_pred = predictor.predict_outcome(base_experiment, system_analysis)
    
    # Add new successful experiment
    populated_memory_store.add_experiment(ExperimentMemory(
        experiment_id="new_success",
        timestamp=datetime.now(),
        experiment_type="network_failure",
        target_component="api-gateway",
        parameters={
            "failure_type": "latency",
            "latency_ms": 2000
        },
        outcome=ExperimentOutcome.SUCCESS,
        metrics={"error_rate": 0.1},
        learnings=["New success pattern"],
        affected_components=["api-gateway"],
        duration="30s",
        risk_level="low"
    ))
    
    # Retrain and predict
    predictor.train_model()
    new_pred = predictor.predict_outcome(base_experiment, system_analysis)
    
    # Should have adapted to new success
    assert new_pred["success_probability"] >= initial_pred["success_probability"]

def test_risk_assessment_integration(populated_memory_store, system_analysis, trained_predictor):
    """Test integrated risk assessment"""
    planner = ExperimentPlanner(populated_memory_store)
    
    # Create high-risk experiment
    risky_experiment = {
        "type": "network_failure",
        "parameters": {
            "target_component": "api-gateway",
            "failure_type": "latency",
            "latency_ms": 5000
        },
        "affected_components": ["api-gateway", "auth-service", "user-service"],
        "duration": "60s"
    }
    
    # Get risk assessment
    risks = planner.calculate_experiment_risk(risky_experiment, system_analysis)
    prediction = trained_predictor.predict_outcome(risky_experiment, system_analysis)
    
    assert "risk_level" in risks
    assert risks["risk_level"] in ["low", "medium", "high"]
    assert len(risks["risk_factors"]) > 0
    assert "predicted_outcome" in prediction

def test_monitoring_integration(populated_memory_store, system_analysis):
    """Test monitoring configuration integration"""
    planner = ExperimentPlanner(populated_memory_store)
    
    # Test different component types
    for component in system_analysis["components"]:
        experiment = {
            "type": "network_failure",
            "parameters": {
                "target_component": component["name"],
                "failure_type": "latency",
                "latency_ms": 1000
            }
        }
        
        enhanced = planner.enhance_experiment(experiment, system_analysis)
        
        # Should have monitoring config
        assert "monitoring" in enhanced
        assert "metrics" in enhanced["monitoring"]
        
        # Should have basic metrics
        basic_metrics = ["cpu_usage", "memory_usage", "error_rate", "latency"]
        for metric in basic_metrics:
            assert metric in enhanced["monitoring"]["metrics"]

def test_template_validation(populated_memory_store):
    """Test template parameter validation"""
    factory = ExperimentTemplateFactory()
    
    # Test valid parameters
    template = factory.create_template(ExperimentType.NETWORK_FAILURE)
    valid_params = {
        "failure_type": "latency",
        "target_component": "api-gateway",
        "latency_ms": 1000
    }
    
    errors = factory.validate_parameters(template, valid_params)
    assert len(errors) == 0
    
    # Test invalid parameters
    invalid_params = {
        "failure_type": "invalid",
        "target_component": "api-gateway",
        "latency_ms": 10000  # Too high
    }
    
    errors = factory.validate_parameters(template, invalid_params)
    assert len(errors) > 0
