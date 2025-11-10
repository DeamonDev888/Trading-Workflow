"""
[OK] Data Aggregator for NOVAQUOTE Claude Code Agents
Built with love by Deamon Dev [ROCKET]

Ce module gère la récupération, l'agrégation et la validation
des données provenant des sub-agents Claude Code.
"""

import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from termcolor import safe_cprint
except ImportError:
    # Fallback if termcolor is not available
    def safe_cprint(text, color=None, attrs=None):
        print(text)

def safe_safe_cprint(text, color):
    """Safe print that handles Unicode encoding issues"""
    try:
        safe_cprint(text, color)
    except UnicodeEncodeError:
        # Remove emojis and special characters for compatibility
        clean_text = text.encode('ascii', 'ignore').decode('ascii')
        print(clean_text)


@dataclass
class AgentData:
    """Structure des données d'un agent"""

    agent_name: str
    timestamp: str
    raw_response: str
    parsed_data: Dict[str, Any]
    confidence: float
    convergence: bool
    iterations: int
    execution_time: float
    success: bool
    error: Optional[str] = None
    validation_status: str = "PENDING"  # PENDING, VALID, INVALID, WARNING
    reliability_score: float = 0.0  # 0.0 - 1.0
    quality_metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class AggregationResult:
    """Résultat de l'agrégation complète"""

    aggregation_id: str
    timestamp: str
    agents_data: List[AgentData]
    consensus: Dict[str, Any]
    final_decision: str
    confidence_score: float
    reliability_score: float
    validation_results: Dict[str, Any]
    warnings: List[str]
    errors: List[str]
    metadata: Dict[str, Any]


class DataAggregator:
    """
    Gestionnaire de l'agrégation et validation des données
    des sub-agents Claude Code
    """

    def __init__(self, project_path: Optional[str] = None):
        self.project_path = (
            Path(project_path) if project_path else Path(__file__).parent.parent.parent
        )
        self.data_dir = self.project_path / "data" / "aggregator"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Historique des agrégations
        self.aggregation_history: List[AggregationResult] = []

        # Métriques de fiabilité
        self.reliability_metrics = {
            "total_aggregations": 0,
            "successful_aggregations": 0,
            "failed_aggregations": 0,
            "average_confidence": 0.0,
            "average_reliability": 0.0,
            "agent_success_rates": {},
            "validation_failure_rate": 0.0,
        }

        safe_safe_cprint("[OK] Data Aggregator initialized", "green")

    def aggregate_agent_data(
        self,
        agent_results: Dict[str, Dict[str, Any]],
        context_data: Optional[Dict[str, Any]] = None,
    ) -> AggregationResult:
        """
        Agrège les données de tous les agents

        Args:
            agent_results: Dictionnaire {agent_name: result_dict}
            context_data: Données de contexte (marché, portfolio, etc.)

        Returns:
            AggregationResult avec toutes les données agrégées
        """
        aggregation_id = f"agg_{int(time.time())}"
        timestamp = datetime.now().isoformat()

        safe_safe_cprint(f"\n[AGGREGATOR] Starting aggregation {aggregation_id}", "cyan")
        safe_safe_cprint(f"[AGGREGATOR] Processing {len(agent_results)} agents", "cyan")

        # 1. Convertir les résultats en AgentData
        agents_data = []
        for agent_name, result in agent_results.items():
            agent_data = self._convert_to_agent_data(agent_name, result)
            agents_data.append(agent_data)
            safe_safe_cprint(
                f"  - {agent_name}: confidence={agent_data.confidence:.2f}, "
                f"converged={agent_data.convergence}",
                "white",
            )

        # 2. Valider chaque agent
        for agent_data in agents_data:
            agent_data = self._validate_agent_data(agent_data)

        # 3. Calculer le consensus
        consensus = self._calculate_consensus(agents_data)

        # 4. Calculer la décision finale
        final_decision = self._determine_final_decision(consensus, agents_data)

        # 5. Calculer les scores globaux
        confidence_score = self._calculate_confidence_score(agents_data)
        reliability_score = self._calculate_reliability_score(agents_data)

        # 6. Valider le système global
        validation_results = self._validate_system(agents_data, consensus, context_data)

        # 7. Collecter warnings et erreurs
        warnings, errors = self._collect_warnings_errors(agents_data, validation_results)

        # 8. Créer le résultat
        result = AggregationResult(
            aggregation_id=aggregation_id,
            timestamp=timestamp,
            agents_data=agents_data,
            consensus=consensus,
            final_decision=final_decision,
            confidence_score=confidence_score,
            reliability_score=reliability_score,
            validation_results=validation_results,
            warnings=warnings,
            errors=errors,
            metadata={
                "context_data": context_data,
                "num_agents": len(agents_data),
                "successful_agents": sum(1 for a in agents_data if a.success),
                "avg_execution_time": sum(a.execution_time for a in agents_data) / len(agents_data),
            },
        )

        # 9. Sauvegarder
        self._save_aggregation_result(result)

        # 10. Mettre à jour l'historique et les métriques
        self._update_metrics(result)

        # 11. Afficher le résumé
        self._print_aggregation_summary(result)

        return result

    def _convert_to_agent_data(self, agent_name: str, result: Dict[str, Any]) -> AgentData:
        """Convertit un résultat d'agent en AgentData"""
        return AgentData(
            agent_name=agent_name,
            timestamp=result.get("timestamp", datetime.now().isoformat()),
            raw_response=str(result.get("result", "")),
            parsed_data=result.get("result", {}),
            confidence=result.get("confidence", 0.0),
            convergence=result.get("converged", False),
            iterations=result.get("iterations", 1),
            execution_time=result.get("execution_time", 0.0),
            success=result.get("success", False),
            error=result.get("error"),
        )

    def _validate_agent_data(self, agent_data: AgentData) -> AgentData:
        """Valide les données d'un agent"""
        validations = []

        # 1. Vérifier le succès
        if not agent_data.success:
            agent_data.validation_status = "INVALID"
            validations.append("Agent execution failed")
            return agent_data

        # 2. Vérifier la confiance
        if agent_data.confidence < 0.3:
            agent_data.validation_status = "WARNING"
            validations.append("Low confidence score")
        elif agent_data.confidence < 0.6:
            agent_data.validation_status = "WARNING"
            validations.append("Medium confidence score")
        else:
            agent_data.validation_status = "VALID"

        # 3. Vérifier la convergence
        if not agent_data.convergence and agent_data.confidence < 0.7:
            agent_data.validation_status = "WARNING"
            validations.append("No convergence with low confidence")

        # 4. Vérifier l'exécution
        if agent_data.execution_time > 120:  # Plus de 2 minutes
            agent_data.validation_status = "WARNING"
            validations.append("Slow execution")

        # 5. Vérifier les itérations
        if agent_data.iterations > 5:
            agent_data.validation_status = "WARNING"
            validations.append("Too many iterations")

        # 6. Calculer le score de fiabilité
        agent_data.reliability_score = self._calculate_agent_reliability(agent_data)

        # 7. Calculer les métriques de qualité
        agent_data.quality_metrics = {
            "confidence": agent_data.confidence,
            "convergence": 1.0 if agent_data.convergence else 0.0,
            "execution_speed": 1.0 - min(1.0, agent_data.execution_time / 120),
            "stability": min(1.0, agent_data.iterations / 3.0),
        }

        return agent_data

    def _calculate_agent_reliability(self, agent_data: AgentData) -> float:
        """Calcule le score de fiabilité d'un agent (0.0 - 1.0)"""
        if not agent_data.success:
            return 0.0

        score = 0.0

        # Confiance (40%)
        score += agent_data.confidence * 0.4

        # Convergence (30%)
        if agent_data.convergence:
            score += 0.3
        else:
            score += agent_data.confidence * 0.3

        # Vitesse d'exécution (15%)
        speed_score = max(0.0, 1.0 - (agent_data.execution_time / 120))
        score += speed_score * 0.15

        # Stabilité (nombre d'itérations raisonnable) (15%)
        stability_score = max(0.0, 1.0 - abs(agent_data.iterations - 3) / 3)
        score += stability_score * 0.15

        return min(1.0, score)

    def _calculate_consensus(self, agents_data: List[AgentData]) -> Dict[str, Any]:
        """Calcule le consensus entre les agents"""
        if not agents_data:
            return {"decision": "HOLD", "confidence": 0.0, "agreements": []}

        # Collecter les décisions
        decisions = {}
        confidences = []
        agreements = []

        for agent_data in agents_data:
            if not agent_data.success:
                continue

            # Extraire la décision du parsed_data
            decision = self._extract_decision(agent_data)
            if decision:
                decisions[agent_data.agent_name] = {
                    "decision": decision,
                    "confidence": agent_data.confidence,
                    "reliability": agent_data.reliability_score,
                }
                confidences.append(agent_data.confidence)

        # Calculer le consensus
        if not decisions:
            return {
                "decision": "HOLD",
                "confidence": 0.0,
                "agreements": [],
                "reason": "No valid decisions",
            }

        # Compter les décisions
        decision_counts = {}
        for agent_name, data in decisions.items():
            dec = data["decision"]
            weight = data["confidence"] * data["reliability"]
            decision_counts[dec] = decision_counts.get(dec, 0) + weight

        # Trouver la décision majoritaire
        best_decision = max(decision_counts.items(), key=lambda x: x[1])
        final_decision = best_decision[0]
        final_confidence = best_decision[1] / sum(decision_counts.values())

        # Construire la liste des accords
        for agent_name, data in decisions.items():
            agreements.append(
                {
                    "agent": agent_name,
                    "decision": data["decision"],
                    "matches_final": data["decision"] == final_decision,
                    "confidence": data["confidence"],
                    "reliability": data["reliability"],
                }
            )

        return {
            "decision": final_decision,
            "confidence": final_confidence,
            "agreements": agreements,
            "total_weighted_votes": sum(decision_counts.values()),
            "decision_breakdown": decision_counts,
        }

    def _extract_decision(self, agent_data: AgentData) -> Optional[str]:
        """Extrait la décision du parsed_data de l'agent"""
        data = agent_data.parsed_data

        # Chercher dans différentes structures possibles
        if isinstance(data, dict):
            if "decision" in data:
                return data["decision"].upper()
            if "recommendation" in data:
                return data["recommendation"].upper()
            if "action" in data:
                return data["action"].upper()

        # Chercher dans le raw_response
        text = agent_data.raw_response.upper()
        if "BUY" in text or "SELL" in text or "HOLD" in text:
            if "BUY" in text and text.count("BUY") > text.count("SELL"):
                return "BUY"
            elif "SELL" in text and text.count("SELL") > text.count("BUY"):
                return "SELL"
            else:
                return "HOLD"

        return None

    def _determine_final_decision(
        self, consensus: Dict[str, Any], agents_data: List[AgentData]
    ) -> str:
        """Détermine la décision finale"""
        # Si on a un consensus clair
        if consensus.get("confidence", 0) > 0.7:
            return consensus["decision"]

        # Sinon, décision conservative
        return "HOLD"

    def _calculate_confidence_score(self, agents_data: List[AgentData]) -> float:
        """Calcule le score de confiance global"""
        if not agents_data:
            return 0.0

        valid_agents = [a for a in agents_data if a.success]
        if not valid_agents:
            return 0.0

        # Moyenne pondérée par la fiabilité
        total_weight = sum(a.reliability_score for a in valid_agents)
        if total_weight == 0:
            return 0.0

        weighted_sum = sum(a.confidence * a.reliability_score for a in valid_agents)
        return weighted_sum / total_weight

    def _calculate_reliability_score(self, agents_data: List[AgentData]) -> float:
        """Calcule le score de fiabilité global"""
        if not agents_data:
            return 0.0

        valid_agents = [a for a in agents_data if a.success]
        if not valid_agents:
            return 0.0

        return sum(a.reliability_score for a in valid_agents) / len(valid_agents)

    def _validate_system(
        self,
        agents_data: List[AgentData],
        consensus: Dict[str, Any],
        context_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Valide le système global"""
        validation_results = {
            "overall_status": "VALID",
            "checks": [],
            "warnings": [],
            "critical_issues": [],
        }

        # 1. Vérifier le nombre d'agents
        num_successful = sum(1 for a in agents_data if a.success)
        if num_successful < 2:
            validation_results["critical_issues"].append("Less than 2 agents successful")
            validation_results["overall_status"] = "INVALID"

        # 2. Vérifier la dispersion des confiances
        confidences = [a.confidence for a in agents_data if a.success]
        if confidences:
            avg_conf = sum(confidences) / len(confidences)
            if avg_conf < 0.5:
                validation_results["warnings"].append("Low average confidence")

        # 3. Vérifier l'accord des agents
        agreements = consensus.get("agreements", [])
        if agreements:
            matches = sum(1 for a in agreements if a["matches_final"])
            agreement_rate = matches / len(agreements)
            if agreement_rate < 0.5:
                validation_results["warnings"].append("Low agreement rate between agents")

        # 4. Vérifier la cohérence temporelle
        timestamps = [datetime.fromisoformat(a.timestamp) for a in agents_data if a.success]
        if len(timestamps) > 1:
            time_diffs = [(max(timestamps) - min(timestamps)).total_seconds() for _ in timestamps]
            max_time_diff = max(time_diffs)
            if max_time_diff > 300:  # Plus de 5 minutes
                validation_results["warnings"].append("Large time dispersion between agents")

        # 5. Vérifier les données de contexte
        if context_data:
            required_fields = ["symbol", "price"]
            missing_fields = [f for f in required_fields if f not in context_data]
            if missing_fields:
                validation_results["warnings"].append(f"Missing context fields: {missing_fields}")

        return validation_results

    def _collect_warnings_errors(
        self, agents_data: List[AgentData], validation_results: Dict[str, Any]
    ) -> Tuple[List[str], List[str]]:
        """Collecte tous les warnings et erreurs"""
        warnings = []
        errors = []

        # Depuis les agents
        for agent_data in agents_data:
            if agent_data.validation_status == "WARNING":
                warnings.append(f"{agent_data.agent_name}: {agent_data.validation_status}")
            if agent_data.validation_status == "INVALID":
                errors.append(f"{agent_data.agent_name}: {agent_data.validation_status}")
            if agent_data.error:
                errors.append(f"{agent_data.agent_name}: {agent_data.error}")

        # Depuis la validation système
        warnings.extend(validation_results.get("warnings", []))
        errors.extend(validation_results.get("critical_issues", []))

        return warnings, errors

    def _save_aggregation_result(self, result: AggregationResult):
        """Sauvegarde le résultat d'agrégation"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"aggregation_{result.aggregation_id}_{timestamp}.json"
        filepath = self.data_dir / filename

        # Convertir en dict pour sérialisation
        result_dict = {
            "aggregation_id": result.aggregation_id,
            "timestamp": result.timestamp,
            "agents_data": [
                {
                    "agent_name": a.agent_name,
                    "timestamp": a.timestamp,
                    "raw_response": a.raw_response,
                    "parsed_data": a.parsed_data,
                    "confidence": a.confidence,
                    "convergence": a.convergence,
                    "iterations": a.iterations,
                    "execution_time": a.execution_time,
                    "success": a.success,
                    "error": a.error,
                    "validation_status": a.validation_status,
                    "reliability_score": a.reliability_score,
                    "quality_metrics": a.quality_metrics,
                }
                for a in result.agents_data
            ],
            "consensus": result.consensus,
            "final_decision": result.final_decision,
            "confidence_score": result.confidence_score,
            "reliability_score": result.reliability_score,
            "validation_results": result.validation_results,
            "warnings": result.warnings,
            "errors": result.errors,
            "metadata": result.metadata,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(result_dict, f, indent=2, ensure_ascii=False)

        safe_safe_cprint(f"[AGGREGATOR] Saved: {filepath}", "green")

    def _update_metrics(self, result: AggregationResult):
        """Met à jour les métriques de fiabilité"""
        self.aggregation_history.append(result)

        self.reliability_metrics["total_aggregations"] += 1

        if result.errors:
            self.reliability_metrics["failed_aggregations"] += 1
        else:
            self.reliability_metrics["successful_aggregations"] += 1

        # Moyennes mobiles
        total = self.reliability_metrics["total_aggregations"]
        self.reliability_metrics["average_confidence"] = (
            self.reliability_metrics["average_confidence"] * (total - 1) + result.confidence_score
        ) / total
        self.reliability_metrics["average_reliability"] = (
            self.reliability_metrics["average_reliability"] * (total - 1) + result.reliability_score
        ) / total

        # Taux de succès par agent
        for agent_data in result.agents_data:
            agent_name = agent_data.agent_name
            if agent_name not in self.reliability_metrics["agent_success_rates"]:
                self.reliability_metrics["agent_success_rates"][agent_name] = {
                    "total": 0,
                    "successful": 0,
                }
            self.reliability_metrics["agent_success_rates"][agent_name]["total"] += 1
            if agent_data.success:
                self.reliability_metrics["agent_success_rates"][agent_name]["successful"] += 1

        # Taux d'échec de validation
        if result.validation_results.get("critical_issues"):
            self.reliability_metrics["validation_failure_rate"] = (
                self.reliability_metrics["validation_failure_rate"] * (total - 1) + 1
            ) / total
        else:
            self.reliability_metrics["validation_failure_rate"] = (
                self.reliability_metrics["validation_failure_rate"] * (total - 1)
            ) / total

    def _print_aggregation_summary(self, result: AggregationResult):
        """Affiche un résumé de l'agrégation"""
        print("\n" + "=" * 70)
        safe_cprint("  AGGREGATION SUMMARY", "cyan", attrs=["bold"])
        print("=" * 70)

        safe_cprint(f"\n  ID: {result.aggregation_id}", "white")
        safe_cprint(f"  Timestamp: {result.timestamp}", "white")

        safe_cprint(
            f"\n  Agents: {len(result.agents_data)} total, "
            f"{sum(1 for a in result.agents_data if a.success)} successful",
            "cyan",
        )

        safe_cprint(f"\n  Final Decision: {result.final_decision}", "green", attrs=["bold"])
        safe_cprint(f"  Confidence Score: {result.confidence_score:.2f}", "cyan")
        safe_cprint(f"  Reliability Score: {result.reliability_score:.2f}", "cyan")

        consensus = result.consensus
        safe_cprint(
            f"\n  Consensus: {consensus.get('decision', 'N/A')} "
            f"(confidence: {consensus.get('confidence', 0.0):.2f})",
            "white",
        )

        # Statut de validation
        validation = result.validation_results
        if validation.get("critical_issues"):
            safe_cprint(
                f"\n  Status: INVALID ({len(validation['critical_issues'])} critical issues)",
                "red",
            )
        elif validation.get("warnings"):
            safe_cprint(
                f"\n  Status: WARNING ({len(validation['warnings'])} warnings)",
                "yellow",
            )
        else:
            safe_cprint(f"\n  Status: VALID", "green")

        # Avertissements et erreurs
        if result.warnings:
            safe_cprint(f"\n  Warnings: {len(result.warnings)}", "yellow")
            for warning in result.warnings[:3]:  # Afficher max 3
                safe_cprint(f"    - {warning}", "yellow")

        if result.errors:
            safe_cprint(f"\n  Errors: {len(result.errors)}", "red")
            for error in result.errors[:3]:  # Afficher max 3
                safe_cprint(f"    - {error}", "red")

        print("\n" + "=" * 70)

    def get_reliability_report(self) -> Dict[str, Any]:
        """Génère un rapport de fiabilité complet"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": self.reliability_metrics,
            "recent_aggregations": [
                {
                    "id": a.aggregation_id,
                    "timestamp": a.timestamp,
                    "final_decision": a.final_decision,
                    "confidence_score": a.confidence_score,
                    "reliability_score": a.reliability_score,
                    "has_errors": len(a.errors) > 0,
                }
                for a in self.aggregation_history[-10:]  # 10 dernières
            ],
            "agent_reliability": {},
        }

        # Statistiques par agent
        for agent_name, stats in self.reliability_metrics["agent_success_rates"].items():
            if stats["total"] > 0:
                success_rate = stats["successful"] / stats["total"]
                report["agent_reliability"][agent_name] = {
                    "total_calls": stats["total"],
                    "successful_calls": stats["successful"],
                    "success_rate": success_rate,
                }

        return report

    def is_system_reliable(self, threshold: float = 0.7) -> bool:
        """Vérifie si le système est fiable"""
        # Critères de fiabilité
        metrics = self.reliability_metrics

        # 1. Taux de succès global > threshold
        if metrics["total_aggregations"] == 0:
            return False

        success_rate = metrics["successful_aggregations"] / metrics["total_aggregations"]
        if success_rate < threshold:
            return False

        # 2. Confiance moyenne > threshold
        if metrics["average_confidence"] < threshold:
            return False

        # 3. Fiabilité moyenne > threshold
        if metrics["average_reliability"] < threshold:
            return False

        # 4. Taux d'échec de validation < 0.3
        if metrics["validation_failure_rate"] > 0.3:
            return False

        # 5. Tous les agents ont un taux de succès > 0.5
        for stats in metrics["agent_success_rates"].values():
            if stats["total"] > 0:
                if stats["successful"] / stats["total"] < 0.5:
                    return False

        return True

    def get_agent_status(self) -> Dict[str, Any]:
        """Retourne le statut détaillé de chaque agent"""
        status = {}
        for agent_name, stats in self.reliability_metrics["agent_success_rates"].items():
            if stats["total"] > 0:
                success_rate = stats["successful"] / stats["total"]
                if success_rate >= 0.8:
                    health = "HEALTHY"
                elif success_rate >= 0.6:
                    health = "DEGRADED"
                else:
                    health = "UNHEALTHY"

                status[agent_name] = {
                    "health": health,
                    "success_rate": success_rate,
                    "total_calls": stats["total"],
                    "successful_calls": stats["successful"],
                }

        return status


# Test du module
if __name__ == "__main__":
    aggregator = DataAggregator()

    # Test avec des données simulées
    test_results = {
        "claude-strategy-advisor": {
            "success": True,
            "confidence": 0.85,
            "converged": True,
            "iterations": 3,
            "execution_time": 45.2,
            "result": {"decision": "BUY", "reasoning": "Strong signal"},
            "timestamp": datetime.now().isoformat(),
        },
        "claude-risk-advisor": {
            "success": True,
            "confidence": 0.78,
            "converged": True,
            "iterations": 2,
            "execution_time": 38.7,
            "result": {"decision": "BUY", "risk_level": "LOW"},
            "timestamp": datetime.now().isoformat(),
        },
        "claude-funding-advisor": {
            "success": True,
            "confidence": 0.82,
            "converged": True,
            "iterations": 3,
            "execution_time": 42.1,
            "result": {"decision": "HOLD", "funding_rate": 0.0001},
            "timestamp": datetime.now().isoformat(),
        },
    }

    context = {"symbol": "BTC-USD", "price": 50000}

    result = aggregator.aggregate_agent_data(test_results, context)

    print("\n" + "=" * 70)
    safe_cprint("  RELIABILITY CHECK", "cyan", attrs=["bold"])
    print("=" * 70)

    reliable = aggregator.is_system_reliable()
    safe_cprint(f"\n  System Reliable: {reliable}", "green" if reliable else "red")

    if reliable:
        safe_cprint("  The system is operating reliably", "green")
    else:
        safe_cprint("  The system has reliability issues - review the report", "yellow")

    report = aggregator.get_reliability_report()
    print(f"\n  Average Confidence: {report['summary']['average_confidence']:.2f}")
    print(f"  Average Reliability: {report['summary']['average_reliability']:.2f}")
    print(
        f"  Success Rate: {report['summary']['successful_aggregations']}/{report['summary']['total_aggregations']}"
    )

    print("\n" + "=" * 70)
