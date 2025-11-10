"""
[OK] Claude Code Orchestrator for NOVAQUOTE
Built with love by Deamon Dev [ROCKET]

Orchestrateur principal qui:
1. Lance les sub-agents Claude Code
2. Récupère et agrège leurs données
3. Valide la fiabilité du système
4. Prend des décisions finales
5. Surveille en continu
"""

import asyncio
import json
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from termcolor import cprint

from src.agents.claude_code_integration import ClaudeCodeIntegrationManager
from src.agents.data_aggregator import AggregationResult, DataAggregator
from src.agents.reliability_monitor import AlertLevel, ReliabilityMonitor


@dataclass
class OrchestratorConfig:
    """Configuration de l'orchestrateur"""

    # Agents à utiliser
    required_agents: List[str] = None

    # Seuils de décision
    min_confidence: float = 0.6
    min_reliability: float = 0.7
    min_agents_agreement: float = 0.5

    # Timeout
    max_execution_time: float = 300.0  # 5 minutes

    # Monitoring
    enable_monitoring: bool = True
    health_check_interval: float = 60.0  # 1 minute

    # Auto-récupération
    auto_recovery: bool = True
    max_retry_attempts: int = 3

    # Validation
    strict_validation: bool = False

    def __post_init__(self):
        if self.required_agents is None:
            self.required_agents = [
                "claude-strategy-advisor",
                "claude-risk-advisor",
                "claude-funding-advisor",
                "claude-sentiment-analyzer",
            ]


@dataclass
class OrchestratorResult:
    """Résultat de l'orchestration"""

    success: bool
    decision: str
    confidence: float
    reliability: float
    aggregation_result: Optional[AggregationResult] = None
    execution_time: float = 0.0
    error: Optional[str] = None
    warnings: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.metadata is None:
            self.metadata = {}


class ClaudeCodeOrchestrator:
    """
    Orchestrateur principal pour les agents Claude Code
    Gère tout le cycle de vie: exécution, agrégation, validation, décision
    """

    def __init__(
        self,
        config: Optional[OrchestratorConfig] = None,
        project_path: Optional[str] = None,
    ):
        self.config = config or OrchestratorConfig()
        self.project_path = (
            Path(project_path) if project_path else Path(__file__).parent.parent.parent
        )

        # Composants
        self.integration_manager = ClaudeCodeIntegrationManager(self.project_path)
        self.data_aggregator = DataAggregator(self.project_path)
        self.reliability_monitor = ReliabilityMonitor(self.project_path)

        # État interne
        self.is_running = False
        self.last_execution: Optional[datetime] = None
        self.execution_count = 0
        self.failure_count = 0

        # Statistiques
        self.stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "average_execution_time": 0.0,
            "average_confidence": 0.0,
            "average_reliability": 0.0,
        }

        # Callbacks
        self.success_callbacks: List[Callable[[OrchestratorResult], None]] = []
        self.failure_callbacks: List[Callable[[Exception], None]] = []
        self.decision_callbacks: List[Callable[[OrchestratorResult], None]] = []

        cprint("[OK] Claude Code Orchestrator initialized", "green")
        cprint(f"[OK] Required agents: {', '.join(self.config.required_agents)}", "cyan")

    def add_success_callback(self, callback: Callable[[OrchestratorResult], None]):
        """Ajoute un callback de succès"""
        self.success_callbacks.append(callback)

    def add_failure_callback(self, callback: Callable[[Exception], None]):
        """Ajoute un callback d'échec"""
        self.failure_callbacks.append(callback)

    def add_decision_callback(self, callback: Callable[[OrchestratorResult], None]):
        """Ajoute un callback de décision"""
        self.decision_callbacks.append(callback)

    async def execute_trading_analysis(
        self,
        task: str,
        context_data: Optional[Dict[str, Any]] = None,
        mode: str = "complete",
    ) -> OrchestratorResult:
        """
        Exécute une analyse de trading complète

        Args:
            task: Description de la tâche
            context_data: Données de contexte (marché, portfolio, etc.)
            mode: Mode d'exécution (complete, quick, custom)

        Returns:
            OrchestratorResult avec la décision finale
        """
        start_time = time.time()
        execution_id = f"exec_{int(start_time)}"

        cprint(f"\n{'='*70}", "cyan")
        cprint(f"  ORCHESTRATOR: Starting execution {execution_id}", "cyan", attrs=["bold"])
        cprint(f"{'='*70}\n", "cyan")

        try:
            self.is_running = True
            self.execution_count += 1
            self.last_execution = datetime.now()

            # 1. Lancer les agents selon le mode
            agent_results = await self._execute_agents(task, context_data, mode)

            # 2. Agréger les données
            aggregation_result = self.data_aggregator.aggregate_agent_data(
                agent_results, context_data
            )

            # 3. Valider avec le moniteur de fiabilité
            if self.config.enable_monitoring:
                await self._run_health_checks()

            # 4. Déterminer la décision finale
            orchestrator_result = self._make_final_decision(aggregation_result, execution_id)

            # 5. Exécuter les callbacks
            if orchestrator_result.success:
                self.stats["successful_executions"] += 1
                for callback in self.success_callbacks:
                    try:
                        callback(orchestrator_result)
                    except Exception as e:
                        cprint(f"[ORCHESTRATOR] Success callback failed: {e}", "red")
            else:
                self.stats["failed_executions"] += 1
                self.failure_count += 1

            for callback in self.decision_callbacks:
                try:
                    callback(orchestrator_result)
                except Exception as e:
                    cprint(f"[ORCHESTRATOR] Decision callback failed: {e}", "red")

            # 6. Mettre à jour les statistiques
            self._update_stats(orchestrator_result, time.time() - start_time)

            # 7. Vérifier si auto-récupération nécessaire
            if not orchestrator_result.success and self.config.auto_recovery:
                await self._attempt_recovery(orchestrator_result)

            # 8. Afficher le résultat final
            self._print_final_result(orchestrator_result, time.time() - start_time)

            return orchestrator_result

        except Exception as e:
            self.stats["failed_executions"] += 1
            self.failure_count += 1

            cprint(f"\n[ORCHESTRATOR] Execution failed: {e}", "red", attrs=["bold"])

            # Créer une alerte
            self.reliability_monitor.create_alert(
                AlertLevel.CRITICAL,
                f"Orchestration failed: {str(e)}",
                "orchestrator",
                {"execution_id": execution_id, "error": str(e)},
            )

            # Exécuter les callbacks d'échec
            for callback in self.failure_callbacks:
                try:
                    callback(e)
                except Exception as callback_error:
                    cprint(
                        f"[ORCHESTRATOR] Failure callback failed: {callback_error}",
                        "red",
                    )

            result = OrchestratorResult(
                success=False,
                decision="HOLD",
                confidence=0.0,
                reliability=0.0,
                error=str(e),
                execution_time=time.time() - start_time,
            )

            return result

        finally:
            self.is_running = False

    async def _execute_agents(
        self, task: str, context_data: Optional[Dict[str, Any]], mode: str
    ) -> Dict[str, Dict[str, Any]]:
        """Exécute les agents selon le mode"""
        agent_results = {}

        if mode == "complete":
            # Exécuter tous les agents en parallèle
            cprint("[ORCHESTRATOR] Executing all agents (complete mode)", "cyan")

            for agent_id in self.config.required_agents:
                cprint(f"  Launching: {agent_id}", "white")
                result = await self._execute_single_agent(agent_id, task, context_data)
                agent_results[agent_id] = result

        elif mode == "quick":
            # Exécuter uniquement les agents essentiels
            essential_agents = ["claude-strategy-advisor", "claude-risk-advisor"]
            cprint(
                f"[ORCHESTRATOR] Executing essential agents: {', '.join(essential_agents)}",
                "cyan",
            )

            for agent_id in essential_agents:
                result = await self._execute_single_agent(agent_id, task, context_data)
                agent_results[agent_id] = result

        else:  # custom
            # Exécuter selon la configuration
            cprint(
                f"[ORCHESTRATOR] Executing custom agents: {', '.join(self.config.required_agents)}",
                "cyan",
            )

            for agent_id in self.config.required_agents:
                result = await self._execute_single_agent(agent_id, task, context_data)
                agent_results[agent_id] = result

        return agent_results

    async def _execute_single_agent(
        self, agent_id: str, task: str, context_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Exécute un agent unique"""
        try:
            # Utiliser le gestionnaire d'intégration
            result = self.integration_manager.call_claude_code_agent(
                agent_id=agent_id,
                prompt=task,
                context_data=context_data,
                use_iterations=True,
            )

            return {
                "success": result.get("success", False),
                "confidence": result.get("confidence", 0.0),
                "converged": result.get("converged", False),
                "iterations": result.get("iterations", 1),
                "execution_time": result.get("execution_time", 0.0),
                "result": result.get("result", {}),
                "timestamp": datetime.now().isoformat(),
                "error": result.get("error"),
            }

        except Exception as e:
            cprint(f"    ERROR: {e}", "red")
            return {
                "success": False,
                "confidence": 0.0,
                "converged": False,
                "iterations": 0,
                "execution_time": 0.0,
                "result": {},
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
            }

    async def _run_health_checks(self):
        """Exécute les vérifications de santé"""
        try:
            # Récupérer les données du moniteur
            reliability_data = self.data_aggregator.get_reliability_report()
            agent_status = self.data_aggregator.get_agent_status()

            # Vérifier la santé du système
            health_report = self.reliability_monitor.check_system_health(
                reliability_data, agent_status
            )

            # Générer des alertes si nécessaire
            if health_report["overall_status"] == "CRITICAL":
                self.reliability_monitor.create_alert(
                    AlertLevel.EMERGENCY,
                    "System health is CRITICAL",
                    "orchestrator",
                    health_report,
                )
            elif health_report["overall_status"] == "UNHEALTHY":
                self.reliability_monitor.create_alert(
                    AlertLevel.CRITICAL,
                    "System health is UNHEALTHY",
                    "orchestrator",
                    health_report,
                )

            # Vérifier les échecs consécutifs
            for agent_name, stats in reliability_data.get("agent_reliability", {}).items():
                if stats["total_calls"] > 0:
                    failure_rate = 1.0 - stats["success_rate"]
                    if failure_rate > 0.5:  # Plus de 50% d'échecs
                        # Calculer le nombre d'échecs consécutifs
                        recent_calls = self.data_aggregator.aggregation_history[-10:]
                        consecutive_failures = 0
                        for agg in reversed(recent_calls):
                            agent_data = next(
                                (a for a in agg.agents_data if a.agent_name == agent_name),
                                None,
                            )
                            if agent_data and not agent_data.success:
                                consecutive_failures += 1
                            else:
                                break

                        self.reliability_monitor.check_consecutive_failures(
                            agent_name, consecutive_failures
                        )

        except Exception as e:
            cprint(f"[ORCHESTRATOR] Health check failed: {e}", "red")

    def _make_final_decision(
        self, aggregation_result: AggregationResult, execution_id: str
    ) -> OrchestratorResult:
        """Détermine la décision finale"""
        warnings = []

        # 1. Vérifier que l'agrégation a réussi
        if not aggregation_result.agents_data:
            return OrchestratorResult(
                success=False,
                decision="HOLD",
                confidence=0.0,
                reliability=0.0,
                aggregation_result=aggregation_result,
                error="No agent data available",
                warnings=warnings,
            )

        # 2. Vérifier le nombre d'agents réussis
        successful_agents = [a for a in aggregation_result.agents_data if a.success]
        if len(successful_agents) < 2:
            warnings.append(f"Only {len(successful_agents)} agents succeeded (minimum: 2)")

        # 3. Vérifier la confiance
        if aggregation_result.confidence_score < self.config.min_confidence:
            warnings.append(
                f"Confidence too low: {aggregation_result.confidence_score:.2f} "
                f"(minimum: {self.config.min_confidence})"
            )

        # 4. Vérifier la fiabilité
        if aggregation_result.reliability_score < self.config.min_reliability:
            warnings.append(
                f"Reliability too low: {aggregation_result.reliability_score:.2f} "
                f"(minimum: {self.config.min_reliability})"
            )

        # 5. Vérifier les erreurs critiques
        if aggregation_result.errors:
            return OrchestratorResult(
                success=False,
                decision="HOLD",
                confidence=0.0,
                reliability=0.0,
                aggregation_result=aggregation_result,
                error=f"Critical errors: {len(aggregation_result.errors)}",
                warnings=warnings,
            )

        # 6. Déterminer la décision finale
        final_decision = aggregation_result.final_decision

        # 7. Ajuster selon le mode strict
        if self.config.strict_validation and warnings:
            # En mode strict, être plus conservative
            if aggregation_result.confidence_score < 0.8:
                final_decision = "HOLD"
                warnings.append("Decision adjusted to HOLD due to strict validation")

        # 8. Calculer la décision finale avec pondération
        decision_confidence = aggregation_result.confidence_score
        decision_reliability = aggregation_result.reliability_score

        # Score final (moyenne pondée)
        final_score = decision_confidence * 0.6 + decision_reliability * 0.4

        return OrchestratorResult(
            success=True,
            decision=final_decision,
            confidence=decision_confidence,
            reliability=decision_reliability,
            aggregation_result=aggregation_result,
            warnings=warnings,
            metadata={
                "execution_id": execution_id,
                "final_score": final_score,
                "num_successful_agents": len(successful_agents),
                "num_total_agents": len(aggregation_result.agents_data),
            },
        )

    async def _attempt_recovery(self, result: OrchestratorResult):
        """Tente une auto-récupération"""
        cprint("\n[ORCHESTRATOR] Attempting auto-recovery...", "yellow")

        # Stratégies de récupération
        recovery_strategies = [
            self._restart_failed_agents,
            self._reduce_iterations,
            self._switch_to_quick_mode,
        ]

        for strategy in recovery_strategies:
            try:
                await strategy(result)
                cprint(
                    f"[ORCHESTRATOR] Recovery strategy applied: {strategy.__name__}",
                    "green",
                )
                break
            except Exception as e:
                cprint(f"[ORCHESTRATOR] Recovery strategy failed: {e}", "red")

    async def _restart_failed_agents(self, result: OrchestratorResult):
        """Redémarre les agents en échec"""
        # TODO: Implémenter le redémarrage des agents
        pass

    async def _reduce_iterations(self, result: OrchestratorResult):
        """Réduit le nombre d'itérations"""
        # TODO: Ajuster la configuration des itérations
        pass

    async def _switch_to_quick_mode(self, result: OrchestratorResult):
        """Bascule en mode rapide"""
        # TODO: Réduire le nombre d'agents utilisés
        pass

    def _update_stats(self, result: OrchestratorResult, execution_time: float):
        """Met à jour les statistiques"""
        self.stats["total_executions"] += 1

        # Moyenne mobile
        n = self.stats["total_executions"]
        self.stats["average_execution_time"] = (
            self.stats["average_execution_time"] * (n - 1) + execution_time
        ) / n
        self.stats["average_confidence"] = (
            self.stats["average_confidence"] * (n - 1) + result.confidence
        ) / n
        self.stats["average_reliability"] = (
            self.stats["average_reliability"] * (n - 1) + result.reliability
        ) / n

    def _print_final_result(self, result: OrchestratorResult, execution_time: float):
        """Affiche le résultat final"""
        print("\n" + "=" * 70)
        cprint("  ORCHESTRATOR RESULT", "cyan", attrs=["bold"])
        print("=" * 70)

        if result.success:
            cprint(f"\n  ✓ SUCCESS", "green", attrs=["bold"])
            cprint(f"  Decision: {result.decision}", "white", attrs=["bold"])
            cprint(f"  Confidence: {result.confidence:.2f}", "cyan")
            cprint(f"  Reliability: {result.reliability:.2f}", "cyan")
        else:
            cprint(f"\n  ✗ FAILED", "red", attrs=["bold"])
            if result.error:
                cprint(f"  Error: {result.error}", "red")

        cprint(f"\n  Execution Time: {execution_time:.2f}s", "white")
        cprint(f"  Total Agents: {result.metadata.get('num_total_agents', 0)}", "white")
        cprint(
            f"  Successful Agents: {result.metadata.get('num_successful_agents', 0)}",
            "white",
        )

        if result.warnings:
            cprint(f"\n  Warnings: {len(result.warnings)}", "yellow")
            for warning in result.warnings[:3]:
                cprint(f"    - {warning}", "yellow")

        print("\n" + "=" * 70)

    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques complètes"""
        return {
            "execution_stats": self.stats,
            "is_running": self.is_running,
            "last_execution": (self.last_execution.isoformat() if self.last_execution else None),
            "execution_count": self.execution_count,
            "failure_count": self.failure_count,
            "success_rate": (
                self.stats["successful_executions"] / max(1, self.stats["total_executions"])
            ),
            "reliability_data": self.data_aggregator.get_reliability_report(),
            "active_alerts": len(self.reliability_monitor.get_active_alerts()),
        }

    def is_system_healthy(self) -> bool:
        """Vérifie si le système est globalement en bonne santé"""
        # Vérifier le taux de succès
        if self.stats["total_executions"] > 0:
            success_rate = self.stats["successful_executions"] / self.stats["total_executions"]
            if success_rate < 0.6:  # Moins de 60% de succès
                return False

        # Vérifier les alertes critiques
        active_alerts = self.reliability_monitor.get_active_alerts()
        critical_alerts = [
            a for a in active_alerts if a.level in [AlertLevel.CRITICAL, AlertLevel.EMERGENCY]
        ]
        if critical_alerts:
            return False

        # Vérifier les échecs consécutifs
        if self.failure_count >= 5:  # Plus de 5 échecs consécutifs
            return False

        return True


# Test de l'orchestrateur
if __name__ == "__main__":
    import asyncio

    async def main():
        # Configuration
        config = OrchestratorConfig(
            min_confidence=0.6,
            min_reliability=0.7,
            enable_monitoring=True,
            auto_recovery=True,
        )

        # Initialiser l'orchestrateur
        orchestrator = ClaudeCodeOrchestrator(config)

        # Données de test
        test_context = {
            "symbol": "BTC-USD",
            "price": 50000,
            "volume": 1000000,
            "timestamp": datetime.now().isoformat(),
        }

        # Exécuter l'analyse
        result = await orchestrator.execute_trading_analysis(
            task="Should I buy BTC at current price?",
            context_data=test_context,
            mode="complete",
        )

        # Afficher les statistiques
        print("\n" + "=" * 70)
        cprint("  ORCHESTRATOR STATISTICS", "cyan", attrs=["bold"])
        print("=" * 70)

        stats = orchestrator.get_statistics()
        print(f"\n  Total Executions: {stats['execution_stats']['total_executions']}")
        print(f"  Success Rate: {stats['success_rate']:.2%}")
        print(f"  Average Confidence: {stats['execution_stats']['average_confidence']:.2f}")
        print(f"  Average Reliability: {stats['execution_stats']['average_reliability']:.2f}")
        print(f"  System Healthy: {orchestrator.is_system_healthy()}")

        print("\n" + "=" * 70)

    asyncio.run(main())
