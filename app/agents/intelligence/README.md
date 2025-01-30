# Intelligent Chaos Engineering Agent

This package implements an intelligent agent system for chaos engineering, combining service-based efficiency with AI-driven decision making.

## Core Components

### 1. Memory Store (`memory_store.py`)

The memory store manages the agent's experiences and learnings:

- **Experiment Memory**: Stores detailed information about past experiments
  - Outcomes and metrics
  - Parameters and configurations
  - Learnings and observations
  - Affected components

- **Component Knowledge**: Builds knowledge about system components
  - Success rates
  - Safe parameter ranges
  - Failure patterns
  - Risk profiles

- **Relationship Knowledge**: Tracks component relationships
  - Dependency strengths
  - Impact patterns
  - Cascade effects

### 2. Experiment Planner (`experiment_planner.py`)

The experiment planner uses historical knowledge to enhance experiments:

- **Parameter Optimization**
  - Adjusts parameters based on past successes
  - Avoids known failure patterns
  - Stays within safe ranges

- **Risk Assessment**
  - Calculates comprehensive risk scores
  - Considers component criticality
  - Evaluates potential impacts
  - Assesses parameter risks

- **Safety Enhancement**
  - Adds appropriate safety checks
  - Configures monitoring
  - Optimizes experiment duration
  - Prevents known issues

## Key Features

### 1. Intelligent Learning
- Learns from experiment outcomes
- Builds component risk profiles
- Identifies safe parameter ranges
- Recognizes failure patterns

### 2. Risk Management
- Multi-factor risk assessment
- Component-specific risk profiles
- Impact analysis
- Parameter validation

### 3. Safety First
- Automated safety checks
- Monitoring configuration
- Duration optimization
- Rollback procedures

### 4. Adaptability
- Learns from new experiments
- Updates risk profiles
- Adjusts parameters
- Enhances safety measures

## Usage Example

```python
from app.agents.intelligence.memory_store import MemoryStore, ExperimentMemory
from app.agents.intelligence.experiment_planner import ExperimentPlanner

# Initialize components
memory_store = MemoryStore()
planner = ExperimentPlanner(memory_store)

# Define experiment
experiment = {
    "type": "network_failure",
    "parameters": {
        "target_component": "user-service",
        "failure_type": "latency",
        "latency_ms": 2000
    }
}

# Enhance with intelligence
enhanced = planner.enhance_experiment(experiment, system_analysis)

# Calculate risk
risk = planner.calculate_experiment_risk(enhanced, system_analysis)

# Store outcome
memory_store.add_experiment(ExperimentMemory(
    experiment_id="exp1",
    timestamp=datetime.now(),
    experiment_type=enhanced["type"],
    target_component=enhanced["parameters"]["target_component"],
    parameters=enhanced["parameters"],
    outcome=ExperimentOutcome.SUCCESS,
    metrics={"error_rate": 0.1},
    learnings=["Service handled latency well"],
    affected_components=["user-service"],
    duration=enhanced["duration"],
    risk_level="medium"
))
```

## Testing

Run the tests with:
```bash
pytest tests/test_agent_intelligence.py -v
```

The tests cover:
- Memory store functionality
- Experiment enhancement
- Risk calculation
- Safety measure addition
- Parameter optimization
- Duration adjustment
- Monitoring configuration

## Extension

### Adding New Intelligence Features

1. Memory Store Extensions:
```python
class MemoryStore:
    def add_custom_knowledge(self, knowledge_type: str, data: Dict[str, Any]):
        # Add custom knowledge types
        pass
        
    def get_custom_knowledge(self, knowledge_type: str) -> Dict[str, Any]:
        # Retrieve custom knowledge
        pass
```

2. Experiment Planner Extensions:
```python
class ExperimentPlanner:
    def add_custom_enhancement(self, name: str, enhance_fn: Callable):
        # Add custom enhancement logic
        pass
        
    def add_custom_risk_factor(self, name: str, risk_fn: Callable):
        # Add custom risk calculation
        pass
```

### Adding New Experiment Types

1. Update ExperimentOutcome enum:
```python
class ExperimentOutcome(Enum):
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    UNSAFE = "unsafe"
    INTERRUPTED = "interrupted"
    CUSTOM_OUTCOME = "custom_outcome"  # Add new outcomes
```

2. Add type-specific logic:
```python
class ExperimentPlanner:
    def _enhance_custom_experiment(self, experiment: Dict[str, Any]) -> Dict[str, Any]:
        # Add custom experiment enhancement logic
        pass
```

## Best Practices

1. Memory Management
   - Regularly clean up old experiments
   - Prioritize recent outcomes
   - Archive historical data

2. Risk Assessment
   - Start with conservative limits
   - Gradually increase complexity
   - Monitor impact carefully

3. Safety Measures
   - Always include monitoring
   - Define clear rollback procedures
   - Set reasonable timeouts

4. Learning Process
   - Document all outcomes
   - Analyze failure patterns
   - Update knowledge base
