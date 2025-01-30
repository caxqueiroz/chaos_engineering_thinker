from typing import Dict, Any, List
from ollama import AsyncClient
import json

class ExperimentCodeGenerator:
    """Generates implementation code for chaos engineering experiments."""
    
    def __init__(self, model: str = "deepseek-r1:70b"):
        self.client = AsyncClient(host='http://localhost:11434')
        self.model = model
        
        # Define code templates for different platforms
        self.platform_templates = {
            "kubernetes": {
                "network_failure": """
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: {name}
spec:
  action: {action}
  mode: {mode}
  selector:
    namespaces:
      - {namespace}
    labelSelectors:
      {labels}
  duration: {duration}
""",
                "pod_failure": """
apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata:
  name: {name}
spec:
  action: {action}
  mode: {mode}
  selector:
    namespaces:
      - {namespace}
    labelSelectors:
      {labels}
  duration: {duration}
""",
                "stress": """
apiVersion: chaos-mesh.org/v1alpha1
kind: StressChaos
metadata:
  name: {name}
spec:
  mode: {mode}
  selector:
    namespaces:
      - {namespace}
    labelSelectors:
      {labels}
  stressors:
    {stressors}
  duration: {duration}
"""
            },
            "docker": {
                "network_failure": """
#!/bin/bash
# Network failure simulation for Docker container

CONTAINER="{container}"
DURATION="{duration}"

# Add network delay
docker exec $CONTAINER tc qdisc add dev eth0 root netem delay {delay}ms

# Wait for duration
sleep $DURATION

# Remove network delay
docker exec $CONTAINER tc qdisc del dev eth0 root
""",
                "resource_stress": """
#!/bin/bash
# Resource stress for Docker container

CONTAINER="{container}"
DURATION="{duration}"

# Start stress
docker exec $CONTAINER stress-ng {stress_args}

# Wait for duration
sleep $DURATION

# Stop stress (container will handle cleanup)
docker exec $CONTAINER pkill stress-ng
"""
            }
        }
    
    async def generate_code(
        self,
        experiment: Dict[str, Any],
        platform: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate implementation code for an experiment.
        
        Args:
            experiment: Experiment specification
            platform: Target platform (kubernetes, docker)
            config: Platform-specific configuration
            
        Returns:
            Dictionary containing:
                - code: Generated implementation code
                - deployment_steps: Steps to deploy the experiment
                - rollback_steps: Steps to rollback the experiment
                - validation_steps: Steps to validate the experiment
        """
        # Select appropriate template
        template = self._get_template(experiment, platform)
        if not template:
            return await self._generate_custom_code(experiment, platform, config)
            
        # Generate code from template
        try:
            code = template.format(**self._prepare_template_vars(experiment, config))
        except KeyError as e:
            # Fall back to custom generation if template variables are missing
            return await self._generate_custom_code(experiment, platform, config)
            
        # Generate additional steps
        deployment_steps = self._generate_deployment_steps(experiment, platform)
        rollback_steps = self._generate_rollback_steps(experiment, platform)
        validation_steps = self._generate_validation_steps(experiment, platform)
        
        return {
            "code": code,
            "deployment_steps": deployment_steps,
            "rollback_steps": rollback_steps,
            "validation_steps": validation_steps
        }
    
    def _get_template(self, experiment: Dict[str, Any], platform: str) -> str:
        """Get appropriate template for the experiment type and platform."""
        if platform not in self.platform_templates:
            return None
            
        experiment_type = experiment.get("type", "").lower()
        return self.platform_templates[platform].get(experiment_type)
    
    def _prepare_template_vars(
        self,
        experiment: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare variables for template formatting."""
        vars = {
            "name": experiment.get("name", "chaos-experiment").lower().replace(" ", "-"),
            "duration": experiment.get("parameters", {}).get("duration", "30s"),
            **config
        }
        
        # Add platform-specific variables
        if "kubernetes" in config:
            vars.update({
                "namespace": config["kubernetes"].get("namespace", "default"),
                "labels": self._format_k8s_labels(
                    config["kubernetes"].get("labels", {})
                ),
                "mode": "one" if experiment.get("scope") == "single" else "all"
            })
            
        elif "docker" in config:
            vars.update({
                "container": config["docker"].get("container_id"),
                "delay": experiment.get("parameters", {}).get("latency_ms", 100)
            })
            
        return vars
    
    def _format_k8s_labels(self, labels: Dict[str, str]) -> str:
        """Format Kubernetes label selectors."""
        return "\n".join(
            f"      {k}: {v}"
            for k, v in labels.items()
        )
    
    async def _generate_custom_code(
        self,
        experiment: Dict[str, Any],
        platform: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate custom code using LLM when no template matches."""
        prompt = self._create_code_generation_prompt(experiment, platform, config)
        
        # Get LLM response
        response = await self._get_llm_response(prompt)
        
        # Parse response
        return self._parse_code_response(response)
    
    def _create_code_generation_prompt(
        self,
        experiment: Dict[str, Any],
        platform: str,
        config: Dict[str, Any]
    ) -> str:
        """Create prompt for code generation."""
        return f"""Generate implementation code for the following chaos engineering experiment:

Experiment Specification:
{json.dumps(experiment, indent=2)}

Target Platform: {platform}
Platform Configuration:
{json.dumps(config, indent=2)}

Generate the following:
1. Implementation code
2. Deployment steps
3. Rollback steps
4. Validation steps

Format your response as JSON with the following structure:
{{
    "code": "implementation code here",
    "deployment_steps": ["step 1", "step 2", ...],
    "rollback_steps": ["step 1", "step 2", ...],
    "validation_steps": ["step 1", "step 2", ...]
}}"""
    
    async def _get_llm_response(self, prompt: str) -> str:
        """Get response from LLM."""
        response_text = ""
        async for response in await self.client.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        ):
            if 'message' in response:
                response_text += response['message'].get('content', '')
        return response_text
    
    def _parse_code_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into code components."""
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
                
            json_str = response[json_start:json_end]
            return json.loads(json_str)
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in response: {str(e)}")
    
    def _generate_deployment_steps(
        self,
        experiment: Dict[str, Any],
        platform: str
    ) -> List[str]:
        """Generate steps to deploy the experiment."""
        if platform == "kubernetes":
            return [
                "Verify kubectl access to the cluster",
                f"Apply the chaos manifest: kubectl apply -f {experiment['name']}.yaml",
                "Verify the chaos resource is created",
                "Monitor the experiment status"
            ]
        elif platform == "docker":
            return [
                "Ensure stress-ng is installed in the container",
                "Verify container network access",
                f"Run the chaos script: bash {experiment['name']}.sh",
                "Monitor container metrics"
            ]
        return []
    
    def _generate_rollback_steps(
        self,
        experiment: Dict[str, Any],
        platform: str
    ) -> List[str]:
        """Generate steps to rollback the experiment."""
        if platform == "kubernetes":
            return [
                f"Delete the chaos resource: kubectl delete -f {experiment['name']}.yaml",
                "Verify the chaos resource is removed",
                "Check target pods have recovered"
            ]
        elif platform == "docker":
            return [
                "Stop the chaos script (Ctrl+C)",
                "Verify container network is restored",
                "Check container is functioning normally"
            ]
        return []
    
    def _generate_validation_steps(
        self,
        experiment: Dict[str, Any],
        platform: str
    ) -> List[str]:
        """Generate steps to validate the experiment."""
        common_steps = [
            "Check monitoring dashboards",
            "Verify system metrics are within expected ranges",
            "Confirm no unexpected errors in logs"
        ]
        
        if platform == "kubernetes":
            return [
                "Verify pods are in expected state",
                "Check pod logs for errors",
                *common_steps
            ]
        elif platform == "docker":
            return [
                "Check container status",
                "Verify container logs",
                *common_steps
            ]
        return common_steps
