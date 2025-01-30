from typing import Dict, Any, List, Optional
import numpy as np
from datetime import datetime, timedelta
from .memory_store import MemoryStore, ExperimentOutcome
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib

class ExperimentPredictor:
    """Predicts experiment outcomes and suggests improvements using ML."""
    
    def __init__(self, memory_store: MemoryStore):
        self.memory_store = memory_store
        self.classifier = RandomForestClassifier(n_estimators=100)
        self.scaler = StandardScaler()
        self.feature_names = [
            "latency_ms", "duration_s", "component_risk",
            "affected_count", "critical_count", "time_of_day"
        ]
        
    def train_model(self) -> None:
        """Train the prediction model on historical data"""
        X, y = self._prepare_training_data()
        if len(X) > 0:
            self.scaler.fit_transform(X)  # Fit and transform in one step
            self.classifier.fit(X, y)
        else:
            # If no data, initialize with dummy data to avoid NotFittedError
            dummy_X = np.array([[0] * len(self.feature_names)])
            self.scaler.fit(dummy_X)
            self.classifier.fit(dummy_X, [0])
            
    def predict_outcome(
        self,
        experiment: Dict[str, Any],
        system_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predict experiment outcome and success probability"""
        features = self._extract_features(experiment, system_analysis)
        features_scaled = self.scaler.transform([features])
        
        # Get prediction and probabilities
        prediction = self.classifier.predict(features_scaled)[0]
        probabilities = self.classifier.predict_proba(features_scaled)[0]
        
        return {
            "predicted_outcome": prediction,
            "success_probability": probabilities[1],
            "confidence": max(probabilities),
            "contributing_factors": self._analyze_feature_importance(features)
        }
        
    def suggest_improvements(
        self,
        experiment: Dict[str, Any],
        system_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Suggest improvements for experiment parameters"""
        suggestions = []
        
        # Get current prediction
        current_prediction = self.predict_outcome(experiment, system_analysis)
        
        # If success probability is low, suggest parameter adjustments
        if current_prediction["success_probability"] < 0.7:
            # Suggest parameter adjustments based on historical data
            if "latency_ms" in experiment["parameters"]:
                suggestions.append({
                    "type": "parameter_adjustment",
                    "parameter": "latency_ms",
                    "current_value": experiment["parameters"]["latency_ms"],
                    "suggested_value": min(experiment["parameters"]["latency_ms"], 2000),
                    "reason": "High latency values increase failure risk"
                })
            
            # Suggest shorter duration if it's too long
            if "duration" in experiment and experiment["duration"].endswith("s"):
                duration_sec = int(experiment["duration"].rstrip("s"))
                if duration_sec > 30:
                    suggestions.append({
                        "type": "duration_adjustment",
                        "current_duration": experiment["duration"],
                        "suggested_duration": "30s",
                        "reason": "Long experiment duration increases system impact"
                    })
        
        # Always suggest at least one improvement
        if not suggestions:
            suggestions.append({
                "type": "monitoring_adjustment",
                "suggestion": "Add detailed monitoring for the target component",
                "reason": "Improved monitoring helps catch issues early"
            })
            
        return suggestions
        
    def analyze_trends(self) -> Dict[str, Any]:
        """Analyze experiment success trends"""
        experiments = self.memory_store.experiments
        if not experiments:
            return {}
            
        # Time-based analysis
        time_success = self._analyze_time_patterns(experiments)
        
        # Component analysis
        component_success = self._analyze_component_patterns(experiments)
        
        # Parameter trends
        parameter_trends = self._analyze_parameter_trends(experiments)
        
        return {
            "time_patterns": time_success,
            "component_patterns": component_success,
            "parameter_trends": parameter_trends,
            "overall_success_rate": self._calculate_overall_success_rate(experiments)
        }
        
    def _prepare_training_data(self) -> tuple:
        """Prepare training data from experiment history"""
        X = []
        y = []
        
        for exp in self.memory_store.experiments:
            try:
                features = [
                    exp.parameters.get("latency_ms", 0),
                    int(exp.duration.rstrip("s")),
                    self.memory_store.get_component_risk_profile(
                        exp.target_component
                    ).get("risk_score", 0.5),
                    len(exp.affected_components),
                    len([c for c in exp.affected_components if c in exp.learnings]),
                    exp.timestamp.hour + exp.timestamp.minute / 60.0
                ]
                
                outcome = 1 if exp.outcome in [
                    ExperimentOutcome.SUCCESS,
                    ExperimentOutcome.PARTIAL_SUCCESS
                ] else 0
                
                X.append(features)
                y.append(outcome)
            except (KeyError, AttributeError):
                continue
                
        return np.array(X), np.array(y)
        
    def _extract_features(
        self,
        experiment: Dict[str, Any],
        system_analysis: Dict[str, Any]
    ) -> List[float]:
        """Extract numerical features from experiment"""
        features = []
        
        # Parameter values
        params = experiment["parameters"]
        if "latency_ms" in params:
            features.append(float(params["latency_ms"]))
        else:
            features.append(0.0)
            
        # Duration in seconds
        duration = experiment.get("duration", "30s")
        features.append(float(duration.rstrip("s")))
        
        # Component risk
        target = params.get("target_component", "")
        risk_profile = self.memory_store.get_component_risk_profile(target)
        features.append(float(risk_profile["risk_score"]))
        
        # Failure type encoding
        failure_type = params.get("failure_type", "")
        features.append(1.0 if failure_type == "latency" else 0.0)
        features.append(1.0 if failure_type == "error" else 0.0)
        
        # Component relationships
        relationships = self.memory_store.get_component_relationships(target)
        features.append(float(len(relationships)))
        
        return features
        
    def _analyze_feature_importance(self, features: List[float]) -> List[Dict[str, Any]]:
        """Analyze which features contributed most to the prediction"""
        importances = self.classifier.feature_importances_
        feature_importance = []
        
        for name, importance, value in zip(self.feature_names, importances, features):
            feature_importance.append({
                "feature": name,
                "importance": importance,
                "value": value
            })
            
        return sorted(
            feature_importance,
            key=lambda x: x["importance"],
            reverse=True
        )
        
    def _find_best_time(
        self,
        experiment: Dict[str, Any],
        system_analysis: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Find best time of day to run experiment"""
        best_prob = 0
        best_time = None
        base_features = self._extract_features(experiment, system_analysis)
        
        for hour in range(24):
            for minute in [0, 30]:
                features = base_features.copy()
                features[-1] = hour + minute / 60.0
                features_scaled = self.scaler.transform([features])
                prob = self.classifier.predict_proba(features_scaled)[0][1]
                
                if prob > best_prob:
                    best_prob = prob
                    best_time = datetime.now().replace(
                        hour=hour,
                        minute=minute,
                        second=0,
                        microsecond=0
                    )
                    
        if best_time and best_prob > self.predict_outcome(
            experiment,
            system_analysis
        )["success_probability"]:
            return {
                "time": best_time,
                "improvement": best_prob - self.predict_outcome(
                    experiment,
                    system_analysis
                )["success_probability"]
            }
        return None
        
    def _analyze_time_patterns(self, experiments: List[Any]) -> Dict[str, Any]:
        """Analyze success patterns by time of day"""
        hour_success = {h: {"success": 0, "total": 0} for h in range(24)}
        
        for exp in experiments:
            hour = exp.timestamp.hour
            hour_success[hour]["total"] += 1
            if exp.outcome in [ExperimentOutcome.SUCCESS, ExperimentOutcome.PARTIAL_SUCCESS]:
                hour_success[hour]["success"] += 1
                
        return {
            hour: {
                "success_rate": data["success"] / data["total"] if data["total"] > 0 else 0,
                "total_experiments": data["total"]
            }
            for hour, data in hour_success.items()
        }
        
    def _analyze_component_patterns(self, experiments: List[Any]) -> Dict[str, Any]:
        """Analyze success patterns by component"""
        component_success = {}
        
        for exp in experiments:
            if exp.target_component not in component_success:
                component_success[exp.target_component] = {"success": 0, "total": 0}
                
            component_success[exp.target_component]["total"] += 1
            if exp.outcome in [ExperimentOutcome.SUCCESS, ExperimentOutcome.PARTIAL_SUCCESS]:
                component_success[exp.target_component]["success"] += 1
                
        return {
            component: {
                "success_rate": data["success"] / data["total"] if data["total"] > 0 else 0,
                "total_experiments": data["total"]
            }
            for component, data in component_success.items()
        }
        
    def _analyze_parameter_trends(self, experiments: List[Any]) -> Dict[str, Any]:
        """Analyze success patterns by parameter values"""
        parameter_ranges = {}
        
        for exp in experiments:
            for param, value in exp.parameters.items():
                if isinstance(value, (int, float)):
                    if param not in parameter_ranges:
                        parameter_ranges[param] = {
                            "successful": [],
                            "failed": []
                        }
                        
                    if exp.outcome in [ExperimentOutcome.SUCCESS, ExperimentOutcome.PARTIAL_SUCCESS]:
                        parameter_ranges[param]["successful"].append(value)
                    else:
                        parameter_ranges[param]["failed"].append(value)
                        
        return {
            param: {
                "successful_range": {
                    "min": min(data["successful"]) if data["successful"] else None,
                    "max": max(data["successful"]) if data["successful"] else None,
                    "mean": np.mean(data["successful"]) if data["successful"] else None
                },
                "failed_range": {
                    "min": min(data["failed"]) if data["failed"] else None,
                    "max": max(data["failed"]) if data["failed"] else None,
                    "mean": np.mean(data["failed"]) if data["failed"] else None
                }
            }
            for param, data in parameter_ranges.items()
        }
        
    def _calculate_overall_success_rate(self, experiments: List[Any]) -> float:
        """Calculate overall experiment success rate"""
        if not experiments:
            return 0.0
            
        successful = len([
            exp for exp in experiments
            if exp.outcome in [ExperimentOutcome.SUCCESS, ExperimentOutcome.PARTIAL_SUCCESS]
        ])
        
        return successful / len(experiments)
        
    def _copy_with_param(
        self,
        experiment: Dict[str, Any],
        param: str,
        value: Any
    ) -> Dict[str, Any]:
        """Create copy of experiment with modified parameter"""
        exp_copy = experiment.copy()
        exp_copy["parameters"] = experiment["parameters"].copy()
        exp_copy["parameters"][param] = value
        return exp_copy
        
    def save_model(self, path: str) -> None:
        """Save the trained model to disk"""
        joblib.dump({
            'classifier': self.classifier,
            'scaler': self.scaler,
            'feature_names': self.feature_names
        }, path)
        
    def load_model(self, path: str) -> None:
        """Load a trained model from disk"""
        model_data = joblib.load(path)
        self.classifier = model_data['classifier']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
