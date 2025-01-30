# Chaos Engineering Services

This package contains the core services for generating, validating, and implementing chaos engineering experiments.

## Components

### 1. Experiment Generator (`generator.py`)
Generates chaos engineering experiments based on system analysis. Features:
- Identifies critical components and relationships
- Generates both single-component and cross-component experiments
- Uses templates for different experiment types
- Leverages LLM for detailed experiment specifications

Supported experiment types:
- Network Failure
- Latency Injection
- Resource Exhaustion
- Process Failure
- Dependency Failure

### 2. Code Generator (`code_generator.py`)
Generates implementation code for chaos experiments. Features:
- Supports multiple platforms (Kubernetes, Docker)
- Provides deployment and rollback steps
- Uses templates for common scenarios
- Falls back to LLM for custom scenarios

Supported platforms:
- Kubernetes (using Chaos Mesh)
- Docker (using tc, stress-ng)

### 3. Safety Validator (`../validation/safety_validator.py`)
Validates experiments for safety and provides recommendations. Features:
- Multiple safety rule categories
- Risk level assessment
- Detailed violation reporting
- Actionable recommendations

Safety checks include:
- Rollback procedures
- Monitoring requirements
- Timeouts and circuit breakers
- Resource limits
- Fallback mechanisms

## Usage Example

```python
from app.services.experiment_generation.generator import ExperimentGenerator
from app.services.experiment_generation.code_generator import ExperimentCodeGenerator
from app.services.validation.safety_validator import SafetyValidator

# Initialize components
generator = ExperimentGenerator()
code_generator = ExperimentCodeGenerator()
validator = SafetyValidator()

# Generate experiments
experiments = await generator.generate_experiments(system_analysis)

# Process each experiment
for experiment in experiments:
    # Validate safety
    validation = validator.validate_experiment(experiment, system_analysis)
    
    if validation["is_safe"]:
        # Generate implementation code
        code = await code_generator.generate_code(
            experiment=experiment,
            platform="kubernetes",
            config={"kubernetes": k8s_config}
        )
```

## Adding New Components

### Adding New Experiment Types
1. Add the type to `ExperimentType` enum in `app/models/schemas.py`
2. Add a template to `ExperimentGenerator.experiment_templates`
3. Update `_select_experiment_templates` logic if needed

### Adding New Platforms
1. Add the platform to `Platform` enum in `app/models/schemas.py`
2. Add templates to `ExperimentCodeGenerator.platform_templates`
3. Implement platform-specific code generation logic

### Adding New Safety Rules
1. Add rules to `SafetyValidator.safety_rules`
2. Implement the validator function
3. Update risk level calculation if needed

## Testing
Run the tests with:
```bash
pytest tests/test_experiment_generation.py -v
```
