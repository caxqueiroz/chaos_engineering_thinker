from typing import Dict, Any, List
from ollama import AsyncClient
import json
import random

class ExperimentGenerator:
    """Generates chaos engineering experiments based on system analysis."""
    
    def __init__(self, model: str = "deepseek-r1:70b"):
        self.client = AsyncClient(host='http://localhost:11434')
        self.model = model
        
        # Define experiment templates
        self.experiment_templates = {
            # Network Failure Experiments
            "network_latency": {
                "type": "network_failure",
                "parameters": {
                    "failure_type": "latency",
                    "latency_ms": lambda: random.randint(100, 2000),
                    "duration": "30s",
                    "jitter_ms": lambda: random.randint(10, 200)
                },
                "safety_checks": [
                    {"name": "monitoring", "description": "Ensure monitoring is enabled"},
                    {"name": "timeout", "description": "Verify timeouts are configured"}
                ]
            },
            "network_partition": {
                "type": "network_failure",
                "parameters": {
                    "failure_type": "partition",
                    "duration": "60s",
                    "direction": lambda: random.choice(["ingress", "egress", "both"])
                },
                "safety_checks": [
                    {"name": "monitoring", "description": "Ensure monitoring is enabled"},
                    {"name": "circuit_breaker", "description": "Verify circuit breakers"}
                ]
            },
            "network_corruption": {
                "type": "network_failure",
                "parameters": {
                    "failure_type": "corruption",
                    "corruption_percentage": lambda: random.randint(1, 10),
                    "duration": "30s"
                },
                "safety_checks": [
                    {"name": "monitoring", "description": "Ensure monitoring is enabled"},
                    {"name": "retry", "description": "Verify retry mechanisms"}
                ]
            },
            "network_bandwidth": {
                "type": "network_failure",
                "parameters": {
                    "failure_type": "bandwidth",
                    "bandwidth_mbps": lambda: random.randint(1, 10),
                    "duration": "60s"
                },
                "safety_checks": [
                    {"name": "monitoring", "description": "Ensure monitoring is enabled"},
                    {"name": "rate_limit", "description": "Verify rate limiting"}
                ]
            },
            
            # Resource Exhaustion Experiments
            "cpu_stress": {
                "type": "resource_exhaustion",
                "parameters": {
                    "resource_type": "cpu",
                    "utilization_percent": lambda: random.randint(70, 90),
                    "duration": "30s",
                    "resource_limits": {
                        "cpu": "0.8",
                        "memory": "0.8"
                    }
                },
                "safety_checks": [
                    {"name": "monitoring", "description": "Ensure monitoring is enabled"},
                    {"name": "resource_limits", "description": "Verify resource limits"}
                ]
            },
            "memory_stress": {
                "type": "resource_exhaustion",
                "parameters": {
                    "resource_type": "memory",
                    "utilization_percent": lambda: random.randint(70, 90),
                    "duration": "30s",
                    "resource_limits": {
                        "cpu": "0.8",
                        "memory": "0.8"
                    }
                },
                "safety_checks": [
                    {"name": "monitoring", "description": "Ensure monitoring is enabled"},
                    {"name": "resource_limits", "description": "Verify resource limits"}
                ]
            },
            "disk_stress": {
                "type": "resource_exhaustion",
                "parameters": {
                    "resource_type": "disk",
                    "utilization_percent": lambda: random.randint(70, 90),
                    "duration": "30s",
                    "io_workers": lambda: random.randint(1, 4)
                },
                "safety_checks": [
                    {"name": "monitoring", "description": "Ensure monitoring is enabled"},
                    {"name": "disk_space", "description": "Verify disk space"}
                ]
            },
            
            # Process Failure Experiments
            "process_kill": {
                "type": "process_failure",
                "parameters": {
                    "failure_type": "kill",
                    "signal": lambda: random.choice(["SIGTERM", "SIGKILL"]),
                    "duration": "10s"
                },
                "safety_checks": [
                    {"name": "monitoring", "description": "Ensure monitoring is enabled"},
                    {"name": "restart_policy", "description": "Verify restart policy"}
                ]
            },
            "process_pause": {
                "type": "process_failure",
                "parameters": {
                    "failure_type": "pause",
                    "duration": "30s"
                },
                "safety_checks": [
                    {"name": "monitoring", "description": "Ensure monitoring is enabled"},
                    {"name": "health_check", "description": "Verify health checks"}
                ]
            },
            
            # State Experiments
            "state_corruption": {
                "type": "state_failure",
                "parameters": {
                    "failure_type": "corruption",
                    "target_type": lambda: random.choice(["disk", "memory"]),
                    "corruption_type": lambda: random.choice(["bit_flip", "null_write"]),
                    "duration": "10s"
                },
                "safety_checks": [
                    {"name": "backup", "description": "Ensure backup exists"},
                    {"name": "monitoring", "description": "Ensure monitoring is enabled"}
                ]
            },
            
            # Clock Experiments
            "clock_skew": {
                "type": "clock_failure",
                "parameters": {
                    "failure_type": "skew",
                    "offset_ms": lambda: random.randint(1000, 10000),
                    "duration": "60s"
                },
                "safety_checks": [
                    {"name": "monitoring", "description": "Ensure monitoring is enabled"},
                    {"name": "ntp", "description": "Verify NTP configuration"}
                ]
            },
            
            # DNS Experiments
            "dns_failure": {
                "type": "dns_failure",
                "parameters": {
                    "failure_type": lambda: random.choice(["error", "delay", "random"]),
                    "duration": "30s",
                    "error_rate": lambda: random.randint(50, 100)
                },
                "safety_checks": [
                    {"name": "monitoring", "description": "Ensure monitoring is enabled"},
                    {"name": "dns_cache", "description": "Verify DNS caching"}
                ]
            },
            
            # Database Experiments
            "db_connection_leak": {
                "type": "database_failure",
                "parameters": {
                    "failure_type": "connection_leak",
                    "leak_rate": lambda: random.randint(1, 5),
                    "duration": "60s"
                },
                "safety_checks": [
                    {"name": "monitoring", "description": "Ensure monitoring is enabled"},
                    {"name": "connection_pool", "description": "Verify connection pooling"}
                ]
            },
            "db_transaction_latency": {
                "type": "database_failure",
                "parameters": {
                    "failure_type": "transaction_latency",
                    "latency_ms": lambda: random.randint(100, 1000),
                    "duration": "30s"
                },
                "safety_checks": [
                    {"name": "monitoring", "description": "Ensure monitoring is enabled"},
                    {"name": "timeout", "description": "Verify transaction timeouts"}
                ]
            },
            
            # Cache Experiments
            "cache_failure": {
                "type": "cache_failure",
                "parameters": {
                    "failure_type": lambda: random.choice(["eviction", "error", "latency"]),
                    "duration": "30s",
                    "error_rate": lambda: random.randint(10, 50)
                },
                "safety_checks": [
                    {"name": "monitoring", "description": "Ensure monitoring is enabled"},
                    {"name": "fallback", "description": "Verify fallback mechanism"}
                ]
            },
            
            # Queue Experiments
            "queue_failure": {
                "type": "queue_failure",
                "parameters": {
                    "failure_type": lambda: random.choice(["delay", "drop", "reorder"]),
                    "duration": "30s",
                    "failure_rate": lambda: random.randint(10, 50)
                },
                "safety_checks": [
                    {"name": "monitoring", "description": "Ensure monitoring is enabled"},
                    {"name": "dlq", "description": "Verify dead letter queue"}
                ]
            }
        }
    
    async def generate_experiments(
        self,
        system_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate chaos engineering experiments based on system analysis.
        
        Args:
            system_analysis: Analysis of system architecture and components
            
        Returns:
            List of generated experiments with details
        """
        experiments = []
        
        # Extract system components and their relationships
        components = self._extract_components(system_analysis)
        relationships = self._extract_relationships(system_analysis)
        
        # Generate experiments for critical components
        critical_components = self._identify_critical_components(
            components,
            relationships
        )
        
        for component in critical_components:
            # Generate component-specific experiments
            component_experiments = await self._generate_component_experiments(
                component,
                system_analysis
            )
            experiments.extend(component_experiments)
            
        # Generate cross-component experiments
        cross_component_experiments = await self._generate_cross_component_experiments(
            critical_components,
            relationships,
            system_analysis
        )
        experiments.extend(cross_component_experiments)
        
        return experiments
    
    def _extract_components(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract components from system analysis."""
        components = []
        
        # Extract from architecture analysis
        for doc_analysis in analysis.values():
            if 'components' in doc_analysis:
                components.extend(doc_analysis['components'])
                
        return components
    
    def _extract_relationships(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract component relationships from system analysis."""
        relationships = []
        
        # Extract from architecture analysis
        for doc_analysis in analysis.values():
            if 'relationships' in doc_analysis:
                relationships.extend(doc_analysis['relationships'])
                
        return relationships
    
    def _identify_critical_components(
        self,
        components: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify critical components based on analysis."""
        critical_components = []
        
        for component in components:
            criticality_score = self._calculate_criticality(
                component,
                relationships
            )
            if criticality_score > 0.7:  # Threshold for critical components
                component['criticality_score'] = criticality_score
                critical_components.append(component)
                
        return critical_components
    
    def _calculate_criticality(
        self,
        component: Dict[str, Any],
        relationships: List[Dict[str, Any]]
    ) -> float:
        """Calculate criticality score for a component."""
        score = 0.0
        
        # Factor 1: Number of dependent components (30%)
        dependent_count = sum(
            1 for r in relationships
            if r['from'] == component['name']
        )
        score += 0.3 * min(dependent_count / 5, 1.0)
        
        # Factor 2: Component type criticality (40%)
        type_scores = {
            'database': 0.9,
            'queue': 0.8,
            'service': 0.7,
            'loadbalancer': 0.6,
            'cache': 0.5
        }
        score += 0.4 * type_scores.get(component['type'], 0.5)
        
        # Factor 3: Technical requirements (30%)
        if 'properties' in component:
            props = component['properties']
            if 'availability' in props or 'sla' in props:
                score += 0.3
            elif 'performance' in props:
                score += 0.2
            else:
                score += 0.1
                
        return score
    
    async def _generate_component_experiments(
        self,
        component: Dict[str, Any],
        system_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate experiments for a specific component."""
        experiments = []
        
        # Select appropriate experiment templates based on component type
        templates = self._select_experiment_templates(component)
        
        for template in templates:
            # Generate experiment using LLM
            experiment = await self._generate_experiment_with_llm(
                template,
                component,
                system_analysis
            )
            if experiment:
                experiments.append(experiment)
                
        return experiments
    
    def _select_experiment_templates(
        self,
        component: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Select appropriate experiment templates for a component."""
        selected = []
        
        component_type = component['type']
        
        # Map component types to relevant experiment types
        type_experiments = {
            'service': [
                'network_latency',
                'network_partition',
                'network_corruption',
                'network_bandwidth',
                'cpu_stress',
                'memory_stress',
                'disk_stress',
                'process_kill',
                'process_pause'
            ],
            'database': [
                'network_latency',
                'network_partition',
                'network_corruption',
                'network_bandwidth',
                'cpu_stress',
                'memory_stress',
                'disk_stress',
                'db_connection_leak',
                'db_transaction_latency'
            ],
            'queue': [
                'network_latency',
                'network_partition',
                'network_corruption',
                'network_bandwidth',
                'cpu_stress',
                'memory_stress',
                'disk_stress',
                'queue_failure'
            ],
            'loadbalancer': [
                'network_latency',
                'network_partition',
                'network_corruption',
                'network_bandwidth',
                'cpu_stress',
                'memory_stress',
                'disk_stress'
            ],
            'cache': [
                'network_latency',
                'network_partition',
                'network_corruption',
                'network_bandwidth',
                'cpu_stress',
                'memory_stress',
                'disk_stress',
                'cache_failure'
            ]
        }
        
        # Get relevant experiment types for this component
        experiment_types = type_experiments.get(component_type, ['network_latency'])
        
        # Add corresponding templates
        for exp_type in experiment_types:
            if exp_type in self.experiment_templates:
                selected.append(self.experiment_templates[exp_type])
                
        return selected
    
    async def _generate_experiment_with_llm(
        self,
        template: Dict[str, Any],
        component: Dict[str, Any],
        system_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate specific experiment details using LLM."""
        
        # Create prompt for experiment generation
        prompt = self._create_experiment_prompt(
            template,
            component,
            system_analysis
        )
        
        # Get LLM response
        response = await self._get_llm_response(prompt)
        
        # Parse and validate response
        try:
            experiment = self._parse_experiment_response(response, template)
            if self._validate_experiment(experiment, component, system_analysis):
                return experiment
        except Exception as e:
            print(f"Error generating experiment: {str(e)}")
            
        return None
    
    def _create_experiment_prompt(
        self,
        template: Dict[str, Any],
        component: Dict[str, Any],
        system_analysis: Dict[str, Any]
    ) -> str:
        """Create prompt for experiment generation."""
        return f"""Generate a chaos engineering experiment using the following template and system information.

Template:
{json.dumps(template, indent=2)}

Target Component:
{json.dumps(component, indent=2)}

System Context:
{json.dumps(system_analysis, indent=2)}

Generate a detailed experiment specification in JSON format with the following structure:
{{
    "name": "Experiment name",
    "description": "Detailed description",
    "hypothesis": "What we expect to learn",
    "parameters": {{
        // Template-specific parameters
    }},
    "safety_checks": [
        // List of specific safety checks
    ],
    "success_criteria": [
        // List of criteria to validate success
    ],
    "rollback_procedure": {{
        // Steps to rollback the experiment
    }}
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
    
    def _parse_experiment_response(
        self,
        response: str,
        template: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse and validate LLM response into experiment specification."""
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
                
            json_str = response[json_start:json_end]
            experiment = json.loads(json_str)
            
            # Validate required fields
            required_fields = [
                'name', 'description', 'hypothesis',
                'parameters', 'safety_checks', 'success_criteria'
            ]
            for field in required_fields:
                if field not in experiment:
                    raise ValueError(f"Missing required field: {field}")
                    
            return experiment
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in response: {str(e)}")
    
    def _validate_experiment(
        self,
        experiment: Dict[str, Any],
        component: Dict[str, Any],
        system_analysis: Dict[str, Any]
    ) -> bool:
        """Validate generated experiment against system constraints."""
        # Check if all required parameters are present
        if not all(
            param in experiment['parameters']
            for param in self.experiment_templates[experiment['type']]['parameters']
        ):
            return False
            
        # Check if safety checks are appropriate
        if not all(
            check in experiment['safety_checks']
            for check in self.experiment_templates[experiment['type']]['safety_checks']
        ):
            return False
            
        # Validate against system constraints
        constraints = self._extract_constraints(system_analysis)
        for constraint in constraints:
            if not self._check_constraint_compliance(experiment, constraint):
                return False
                
        return True
    
    async def _generate_cross_component_experiments(
        self,
        critical_components: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]],
        system_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate experiments that affect multiple components."""
        experiments = []
        
        # Find connected critical components
        for i, comp1 in enumerate(critical_components):
            for comp2 in critical_components[i+1:]:
                if self._are_connected(comp1, comp2, relationships):
                    # Generate experiments for this component pair
                    pair_experiments = await self._generate_pair_experiments(
                        comp1,
                        comp2,
                        system_analysis
                    )
                    experiments.extend(pair_experiments)
                    
        return experiments
    
    def _are_connected(
        self,
        comp1: Dict[str, Any],
        comp2: Dict[str, Any],
        relationships: List[Dict[str, Any]]
    ) -> bool:
        """Check if two components are connected."""
        return any(
            (r['from'] == comp1['name'] and r['to'] == comp2['name']) or
            (r['from'] == comp2['name'] and r['to'] == comp1['name'])
            for r in relationships
        )
    
    async def _generate_pair_experiments(
        self,
        comp1: Dict[str, Any],
        comp2: Dict[str, Any],
        system_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate experiments for a pair of connected components."""
        experiments = []
        
        # Create combined component context
        combined_context = {
            "components": [comp1, comp2],
            "relationship": self._find_relationship(comp1, comp2, system_analysis)
        }
        
        # Generate network partition experiment
        partition_experiment = await self._generate_experiment_with_llm(
            self.experiment_templates['network_partition'],
            combined_context,
            system_analysis
        )
        if partition_experiment:
            experiments.append(partition_experiment)
            
        # Generate latency experiment
        latency_experiment = await self._generate_experiment_with_llm(
            self.experiment_templates['network_latency'],
            combined_context,
            system_analysis
        )
        if latency_experiment:
            experiments.append(latency_experiment)
            
        return experiments
    
    def _find_relationship(
        self,
        comp1: Dict[str, Any],
        comp2: Dict[str, Any],
        system_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Find relationship details between two components."""
        for doc_analysis in system_analysis.values():
            if 'relationships' in doc_analysis:
                for rel in doc_analysis['relationships']:
                    if (
                        (rel['from'] == comp1['name'] and rel['to'] == comp2['name']) or
                        (rel['from'] == comp2['name'] and rel['to'] == comp1['name'])
                    ):
                        return rel
        return {}
