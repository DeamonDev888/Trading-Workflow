"""
[OK] Reliability Monitor for NOVAQUOTE Claude Code Agents
Built with love by Deamon Dev [ROCKET]

Surveillance continue de la fiabilité du système multi-agents
avec alertes et auto-récupération.
"""

import json
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from termcolor import cprint


class AlertLevel(Enum):
    """Niveaux d'alerte"""

    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"


@dataclass
class ReliabilityAlert:
    """Alerte de fiabilité"""

    level: AlertLevel
    message: str
    timestamp: str
    source: str
    details: Dict[str, Any]
    auto_resolve: bool = False
    resolved: bool = False
    resolution_time: Optional[str] = None


class ReliabilityMonitor:
    """
    Moniteur de fiabilité en temps réel
    Surveille la santé du système et génère des alertes
    """

    def __init__(self, project_path: Optional[str] = None):
        self.project_path = (
            Path(project_path) if project_path else Path(__file__).parent.parent.parent
        )
        self.alerts_dir = self.project_path / "logs" / "reliability"
        self.alerts_dir.mkdir(parents=True, exist_ok=True)

        # Alertes actives
        self.active_alerts: List[ReliabilityAlert] = []

        # Historique des alertes
        self.alert_history: List[ReliabilityAlert] = []

        # Métriques en temps réel
        self.metrics = {
            "uptime_start": datetime.now(),
            "total_checks": 0,
            "failed_checks": 0,
            "alerts_generated": 0,
            "alerts_resolved": 0,
            "system_health_score": 1.0,  # 0.0 - 1.0
            "last_health_check": None,
        }

        # Callbacks d'alerte
        self.alert_callbacks: List[Callable[[ReliabilityAlert], None]] = []

        # Seuils de监控
        self.thresholds = {
            "min_success_rate": 0.7,  # Taux de succès minimum
            "min_confidence": 0.6,  # Confiance minimum moyenne
            "max_execution_time": 120,  # Temps d'exécution maximum (secondes)
            "max_consecutive_failures": 3,  # Échecs consécutifs maximum
            "min_agents_online": 2,  # Agents minimum en ligne
            "health_check_interval": 60,  # Intervalle de vérification (secondes)
        }

        cprint("[OK] Reliability Monitor initialized", "green")

    def add_alert_callback(self, callback: Callable[[ReliabilityAlert], None]):
        """Ajoute un callback pour les alertes"""
        self.alert_callbacks.append(callback)
        cprint(f"[MONITOR] Added alert callback: {callback.__name__}", "cyan")

    def check_system_health(
        self,
        aggregator_data: Optional[Dict[str, Any]] = None,
        agent_status: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Vérification complète de la santé du système

        Args:
            aggregator_data: Données du DataAggregator
            agent_status: Statut des agents

        Returns:
            Rapport de santé complet
        """
        self.metrics["total_checks"] += 1
        self.metrics["last_health_check"] = datetime.now().isoformat()

        health_report = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "HEALTHY",
            "health_score": 1.0,
            "checks": {},
            "alerts": [],
            "recommendations": [],
        }

        # 1. Vérifier les métriques du système
        system_check = self._check_system_metrics(aggregator_data)
        health_report["checks"]["system"] = system_check

        # 2. Vérifier les agents
        agents_check = self._check_agents_health(agent_status)
        health_report["checks"]["agents"] = agents_check

        # 3. Vérifier les performances
        performance_check = self._check_performance(aggregator_data)
        health_report["checks"]["performance"] = performance_check

        # 4. Vérifier la cohérence des données
        consistency_check = self._check_data_consistency(aggregator_data)
        health_report["checks"]["consistency"] = consistency_check

        # 5. Calculer le score global
        health_report["health_score"] = self._calculate_health_score(health_report["checks"])

        # 6. Déterminer le statut global
        if health_report["health_score"] >= 0.8:
            health_report["overall_status"] = "HEALTHY"
        elif health_report["health_score"] >= 0.6:
            health_report["overall_status"] = "DEGRADED"
        elif health_report["health_score"] >= 0.4:
            health_report["overall_status"] = "UNHEALTHY"
        else:
            health_report["overall_status"] = "CRITICAL"

        # 7. Générer des recommandations
        health_report["recommendations"] = self._generate_recommendations(health_report["checks"])

        # 8. Mettre à jour les métriques
        self.metrics["system_health_score"] = health_report["health_score"]
        if health_report["overall_status"] in ["UNHEALTHY", "CRITICAL"]:
            self.metrics["failed_checks"] += 1

        # 9. Sauvegarder le rapport
        self._save_health_report(health_report)

        return health_report

    def _check_system_metrics(self, aggregator_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Vérifie les métriques du système"""
        check_result = {"status": "PASS", "score": 1.0, "details": {}, "warnings": []}

        if not aggregator_data:
            check_result["status"] = "WARNING"
            check_result["score"] = 0.5
            check_result["warnings"].append("No aggregator data available")
            return check_result

        # Vérifier le taux de succès
        total = aggregator_data.get("total_aggregations", 0)
        successful = aggregator_data.get("successful_aggregations", 0)

        if total > 0:
            success_rate = successful / total
            check_result["details"]["success_rate"] = success_rate

            if success_rate < self.thresholds["min_success_rate"]:
                check_result["status"] = "FAIL"
                check_result["score"] = 0.3
                check_result["warnings"].append(f"Success rate too low: {success_rate:.2f}")
            elif success_rate < 0.8:
                check_result["status"] = "WARNING"
                check_result["score"] = 0.7
                check_result["warnings"].append(f"Success rate below optimal: {success_rate:.2f}")

        # Vérifier la confiance moyenne
        avg_confidence = aggregator_data.get("average_confidence", 0.0)
        check_result["details"]["average_confidence"] = avg_confidence

        if avg_confidence < self.thresholds["min_confidence"]:
            check_result["score"] = min(check_result["score"], 0.4)
            check_result["warnings"].append(f"Average confidence low: {avg_confidence:.2f}")

        # Vérifier la fiabilité moyenne
        avg_reliability = aggregator_data.get("average_reliability", 0.0)
        check_result["details"]["average_reliability"] = avg_reliability

        if avg_reliability < 0.6:
            check_result["warnings"].append(f"Average reliability low: {avg_reliability:.2f}")

        return check_result

    def _check_agents_health(self, agent_status: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Vérifie la santé des agents"""
        check_result = {
            "status": "PASS",
            "score": 1.0,
            "details": {"agents": {}},
            "warnings": [],
        }

        if not agent_status:
            check_result["status"] = "WARNING"
            check_result["score"] = 0.5
            check_result["warnings"].append("No agent status data available")
            return check_result

        healthy_agents = 0
        total_agents = len(agent_status)

        for agent_name, status in agent_status.items():
            health = status.get("health", "UNKNOWN")
            success_rate = status.get("success_rate", 0.0)

            agent_info = {
                "health": health,
                "success_rate": success_rate,
                "online": health in ["HEALTHY", "DEGRADED"],
            }

            if health == "HEALTHY":
                healthy_agents += 1
                agent_info["score"] = 1.0
            elif health == "DEGRADED":
                healthy_agents += 1
                agent_info["score"] = 0.7
            else:
                agent_info["score"] = 0.3
                check_result["warnings"].append(f"Agent {agent_name} is {health}")

            check_result["details"]["agents"][agent_name] = agent_info

        # Vérifier le nombre d'agents en ligne
        if healthy_agents < self.thresholds["min_agents_online"]:
            check_result["status"] = "FAIL"
            check_result["score"] = 0.2
            check_result["warnings"].append(
                f"Only {healthy_agents}/{total_agents} agents online (minimum: {self.thresholds['min_agents_online']})"
            )
        elif healthy_agents < total_agents:
            check_result["status"] = "WARNING"
            check_result["score"] = 0.7

        return check_result

    def _check_performance(self, aggregator_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Vérifie les performances"""
        check_result = {"status": "PASS", "score": 1.0, "details": {}, "warnings": []}

        if not aggregator_data:
            return check_result

        # Vérifier le temps d'exécution
        recent_aggregations = aggregator_data.get("recent_aggregations", [])
        if recent_aggregations:
            avg_execution_times = [
                a.get("metadata", {}).get("avg_execution_time", 0)
                for a in recent_aggregations[-5:]  # 5 dernières
            ]
            if avg_execution_times:
                avg_time = sum(avg_execution_times) / len(avg_execution_times)
                check_result["details"]["average_execution_time"] = avg_time

                if avg_time > self.thresholds["max_execution_time"]:
                    check_result["status"] = "WARNING"
                    check_result["score"] = 0.6
                    check_result["warnings"].append(
                        f"Average execution time high: {avg_time:.1f}s (max: {self.thresholds['max_execution_time']}s)"
                    )

        return check_result

    def _check_data_consistency(self, aggregator_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Vérifie la cohérence des données"""
        check_result = {"status": "PASS", "score": 1.0, "details": {}, "warnings": []}

        if not aggregator_data:
            return check_result

        # Vérifier la dispersion des décisions
        recent_decisions = [
            a.get("final_decision") for a in aggregator_data.get("recent_aggregations", [])[-10:]
        ]

        if recent_decisions:
            unique_decisions = set(recent_decisions)
            if len(unique_decisions) > 3:  # Trop de dispersion
                check_result["status"] = "WARNING"
                check_result["score"] = 0.7
                check_result["warnings"].append(
                    f"High decision dispersion: {len(unique_decisions)} different decisions in recent runs"
                )

        return check_result

    def _calculate_health_score(self, checks: Dict[str, Any]) -> float:
        """Calcule le score de santé global"""
        weights = {"system": 0.4, "agents": 0.3, "performance": 0.2, "consistency": 0.1}

        total_weight = 0
        weighted_score = 0

        for check_name, check_data in checks.items():
            if check_name in weights:
                score = check_data.get("score", 0.0)
                weight = weights[check_name]
                weighted_score += score * weight
                total_weight += weight

        return weighted_score / total_weight if total_weight > 0 else 0.0

    def _generate_recommendations(self, checks: Dict[str, Any]) -> List[str]:
        """Génère des recommandations"""
        recommendations = []

        # Recommandations basées sur les vérifications
        if checks.get("system", {}).get("status") == "FAIL":
            recommendations.append("Check system metrics - low success rate detected")
            recommendations.append("Review recent aggregation results for patterns")

        if checks.get("agents", {}).get("status") == "FAIL":
            recommendations.append("Restart unhealthy agents")
            recommendations.append("Check agent configurations and logs")

        agents_check = checks.get("agents", {})
        for agent_name, agent_data in agents_check.get("details", {}).get("agents", {}).items():
            if agent_data.get("health") == "UNHEALTHY":
                recommendations.append(f"Investigate {agent_name} - repeated failures detected")

        if checks.get("performance", {}).get("status") == "WARNING":
            recommendations.append("Optimize agent execution time")
            recommendations.append("Consider reducing iteration counts")

        return recommendations

    def _save_health_report(self, report: Dict[str, Any]):
        """Sauvegarde le rapport de santé"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"health_report_{timestamp}.json"
        filepath = self.alerts_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

    def create_alert(
        self,
        level: AlertLevel,
        message: str,
        source: str,
        details: Optional[Dict[str, Any]] = None,
        auto_resolve: bool = False,
    ) -> ReliabilityAlert:
        """Crée une nouvelle alerte"""
        alert = ReliabilityAlert(
            level=level,
            message=message,
            timestamp=datetime.now().isoformat(),
            source=source,
            details=details or {},
            auto_resolve=auto_resolve,
        )

        self.active_alerts.append(alert)
        self.alert_history.append(alert)
        self.metrics["alerts_generated"] += 1

        # Notifier les callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                cprint(f"[MONITOR] Alert callback failed: {e}", "red")

        # Logger l'alerte
        self._log_alert(alert)

        # Afficher l'alerte
        self._display_alert(alert)

        return alert

    def resolve_alert(self, alert: ReliabilityAlert):
        """Résout une alerte"""
        if alert in self.active_alerts:
            alert.resolved = True
            alert.resolution_time = datetime.now().isoformat()
            self.active_alerts.remove(alert)
            self.metrics["alerts_resolved"] += 1

            cprint(f"[MONITOR] Alert resolved: {alert.message}", "green")

    def _log_alert(self, alert: ReliabilityAlert):
        """Log l'alerte"""
        log_file = self.alerts_dir / f"alerts_{datetime.now().strftime('%Y%m%d')}.log"
        log_entry = {
            "timestamp": alert.timestamp,
            "level": alert.level.value,
            "message": alert.message,
            "source": alert.source,
            "details": alert.details,
        }

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

    def _display_alert(self, alert: ReliabilityAlert):
        """Affiche l'alerte"""
        level_colors = {
            AlertLevel.INFO: "cyan",
            AlertLevel.WARNING: "yellow",
            AlertLevel.CRITICAL: "red",
            AlertLevel.EMERGENCY: "red",
        }

        color = level_colors.get(alert.level, "white")
        cprint(f"\n[ALERT {alert.level.value}] {alert.message}", color, attrs=["bold"])
        cprint(f"  Source: {alert.source}", "white")
        cprint(f"  Time: {alert.timestamp}", "white")
        if alert.details:
            cprint(f"  Details: {json.dumps(alert.details, indent=2)}", "white")

    def get_active_alerts(self) -> List[ReliabilityAlert]:
        """Retourne les alertes actives"""
        return self.active_alerts.copy()

    def get_alert_summary(self) -> Dict[str, Any]:
        """Retourne un résumé des alertes"""
        now = datetime.now()
        last_24h = now - timedelta(hours=24)

        recent_alerts = [
            a for a in self.alert_history if datetime.fromisoformat(a.timestamp) > last_24h
        ]

        return {
            "total_alerts": len(self.alert_history),
            "active_alerts": len(self.active_alerts),
            "last_24h": len(recent_alerts),
            "by_level": {
                level.value: len([a for a in recent_alerts if a.level == level])
                for level in AlertLevel
            },
            "unresolved_critical": len(
                [
                    a
                    for a in self.active_alerts
                    if a.level in [AlertLevel.CRITICAL, AlertLevel.EMERGENCY]
                ]
            ),
        }

    def check_consecutive_failures(self, agent_name: str, failure_count: int) -> bool:
        """Vérifie les échecs consécutifs d'un agent"""
        threshold = self.thresholds["max_consecutive_failures"]

        if failure_count >= threshold:
            self.create_alert(
                AlertLevel.CRITICAL,
                f"Agent {agent_name} has failed {failure_count} consecutive times",
                "reliability_monitor",
                {"agent": agent_name, "failure_count": failure_count},
            )
            return True

        return False

    def get_system_uptime(self) -> float:
        """Retourne l'uptime du système en secondes"""
        return (datetime.now() - self.metrics["uptime_start"]).total_seconds()

    def export_metrics(self, filepath: Optional[Path] = None) -> Path:
        """Exporte les métriques"""
        if not filepath:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = self.alerts_dir / f"metrics_{timestamp}.json"

        metrics_export = {
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": self.get_system_uptime(),
            "metrics": self.metrics,
            "thresholds": self.thresholds,
            "alert_summary": self.get_alert_summary(),
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(metrics_export, f, indent=2, ensure_ascii=False)

        return filepath


# Test du moniteur
if __name__ == "__main__":
    monitor = ReliabilityMonitor()

    # Test d'alertes
    monitor.create_alert(AlertLevel.WARNING, "Test warning alert", "test", {"test_data": "value"})

    # Test de vérification de santé
    mock_aggregator_data = {
        "total_aggregations": 100,
        "successful_aggregations": 85,
        "average_confidence": 0.75,
        "average_reliability": 0.78,
    }

    mock_agent_status = {
        "claude-strategy-advisor": {"health": "HEALTHY", "success_rate": 0.9},
        "claude-risk-advisor": {"health": "DEGRADED", "success_rate": 0.65},
    }

    health_report = monitor.check_system_health(mock_aggregator_data, mock_agent_status)

    print("\n" + "=" * 70)
    cprint("  SYSTEM HEALTH REPORT", "cyan", attrs=["bold"])
    print("=" * 70)
    print(f"\n  Status: {health_report['overall_status']}")
    print(f"  Health Score: {health_report['health_score']:.2f}")
    print(f"  Uptime: {monitor.get_system_uptime():.0f} seconds")

    print("\n  Recommendations:")
    for rec in health_report["recommendations"]:
        cprint(f"    - {rec}", "yellow")

    print("\n" + "=" * 70)
    cprint("  ALERT SUMMARY", "cyan", attrs=["bold"])
    print("=" * 70)
    summary = monitor.get_alert_summary()
    print(f"\n  Total Alerts: {summary['total_alerts']}")
    print(f"  Active Alerts: {summary['active_alerts']}")
    print(f"  Last 24h: {summary['last_24h']}")
    print(f"  Unresolved Critical: {summary['unresolved_critical']}")

    # Exporter les métriques
    metrics_file = monitor.export_metrics()
    print(f"\n  Metrics exported to: {metrics_file}")

    print("\n" + "=" * 70)
