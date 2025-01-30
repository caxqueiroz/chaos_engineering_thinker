import asyncio
from app.services.experiment_generation.generator import ExperimentGenerator
from app.services.experiment_generation.code_generator import ExperimentCodeGenerator
from app.services.validation.safety_validator import SafetyValidator

async def main():
    # Initialize components
    generator = ExperimentGenerator()
    code_generator = ExperimentCodeGenerator()
    validator = SafetyValidator()
    
    # Example system analysis
    system_analysis = {
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
            }
        ]
    }
    
    # Generate experiments
    print("Generating experiments...")
    experiments = await generator.generate_experiments(system_analysis)
    
    # Example Kubernetes configuration
    k8s_config = {
        "namespace": "default",
        "labels": {
            "app": "user-service",
            "env": "staging"
        }
    }
    
    # Process each experiment
    for experiment in experiments:
        print(f"\nProcessing experiment: {experiment['name']}")
        
        # Validate experiment
        validation = validator.validate_experiment(experiment, system_analysis)
        print(f"Validation result: {'Safe' if validation['is_safe'] else 'Unsafe'}")
        print(f"Risk level: {validation['risk_level']}")
        
        if validation["is_safe"]:
            # Generate implementation code
            implementation = await code_generator.generate_code(
                experiment=experiment,
                platform="kubernetes",
                config={"kubernetes": k8s_config}
            )
            
            print("\nImplementation code:")
            print(implementation["code"])
            
            print("\nDeployment steps:")
            for step in implementation["deployment_steps"]:
                print(f"- {step}")
                
            print("\nRollback steps:")
            for step in implementation["rollback_steps"]:
                print(f"- {step}")
        else:
            print("\nSafety violations:")
            for violation in validation["violations"]:
                print(f"- {violation['description']}: {violation['details']}")
            
            print("\nRecommendations:")
            for rec in validation["recommendations"]:
                print(f"- {rec['recommendation']}")

if __name__ == "__main__":
    asyncio.run(main())
