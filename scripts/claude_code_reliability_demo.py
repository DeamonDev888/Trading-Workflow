"""
[OK] Claude Code Reliability System - Demonstration
Built with love by Deamon Dev [ROCKET]

Démontre:
1. Comment les agents récupèrent et valident les données
2. Comment le système assure la fiabilité
3. Comment l'orchestrateur prend des décisions
4. Comment le monitoring fonctionne
"""

import asyncio
import time
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent.parent
import sys
sys.path.insert(0, str(project_root))

from termcolor import cprint

from src.agents.claude_code_orchestrator import ClaudeCodeOrchestrator, OrchestratorConfig
from src.agents.data_aggregator import DataAggregator
from src.agents.reliability_monitor import ReliabilityMonitor, AlertLevel


def print_header(text):
    """Affiche un titre"""
    cprint("\n" + "="*70, "cyan")
    cprint(f"  {text}", "cyan", attrs=["bold"])
    cprint("="*70 + "\n", "cyan")


def print_section(text):
    """Affiche une section"""
    cprint(f"\n▶️  {text}", "yellow", attrs=["bold"])


def print_success(text):
    """Affiche un succès"""
    cprint(f"  ✓ {text}", "green")


def print_warning(text):
    """Affiche un avertissement"""
    cprint(f"  ⚠ {text}", "yellow")


def print_error(text):
    """Affiche une erreur"""
    cprint(f"  ✗ {text}", "red")


def simulate_market_data():
    """Crée des données de marché simulées"""
    return {
        "symbol": "BTC-USD",
        "timestamp": datetime.now().isoformat(),
        "price": 50000 + (time.time() % 1000),
        "price_change_24h": 0.025,
        "volume_24h": 1000000,
        "funding_rate": 0.0001,
        "volatility": 0.05,
        "liquidity": 50000000,
        "market_cap": 1000000000,
        "fear_greed_index": 45,
        "social_sentiment": 0.1,
        "portfolio": {
            "balance": 10000,
            "positions": [
                {"symbol": "BTC-USD", "size": 0.1, "pnl": 500},
                {"symbol": "ETH-USD", "size": 5, "pnl": -200}
            ]
        }
    }


async def demo_1_basic_orchestration():
    """Démonstration 1: Orchestration de base"""
    print_header("DÉMONSTRATION 1: ORCHESTRATION DE BASE")

    print_section("Configuration de l'orchestrateur")

    config = OrchestratorConfig(
        min_confidence=0.6,
        min_reliability=0.7,
        enable_monitoring=True,
        auto_recovery=True
    )
    print_success(f"Min confidence: {config.min_confidence}")
    print_success(f"Min reliability: {config.min_reliability}")
    print_success(f"Monitoring enabled: {config.enable_monitoring}")
    print_success(f"Auto recovery: {config.auto_recovery}")

    print_section("Initialisation de l'orchestrateur")

    orchestrator = ClaudeCodeOrchestrator(config)
    print_success(f"Required agents: {len(config.required_agents)}")
    print_success(f"Components initialized: integration, aggregator, monitor")

    print_section("Exécution de l'analyse de trading")

    market_data = simulate_market_data()
    print(f"  Market data: {market_data['symbol']} @ ${market_data['price']:.2f}")

    result = await orchestrator.execute_trading_analysis(
        task="Should I buy BTC at current price?",
        context_data=market_data,
        mode="complete"
    )

    print_section("Résultat de l'orchestration")
    print(f"  Success: {result.success}")
    print(f"  Decision: {result.decision}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Reliability: {result.reliability:.2f}")
    print(f"  Execution time: {result.execution_time:.2f}s")

    if result.warnings:
        print_warning(f"Warnings: {len(result.warnings)}")
        for warning in result.warnings:
            print(f"    - {warning}")

    return result


async def demo_2_data_aggregation():
    """Démonstration 2: Agrégation des données"""
    print_header("DÉMONSTRATION 2: AGRÉGATION DES DONNÉES")

    print_section("Création du DataAggregator")

    aggregator = DataAggregator()
    print_success("Aggregator initialized")

    print_section("Simulation de résultats d'agents")

    agent_results = {
        "claude-strategy-advisor": {
            "success": True,
            "confidence": 0.85,
            "converged": True,
            "iterations": 3,
            "execution_time": 45.2,
            "result": {
                "decision": "BUY",
                "reasoning": "Strong bullish signal, RSI oversold",
                "entry_price": 50000,
                "stop_loss": 47500,
                "take_profit": 53000
            },
            "timestamp": datetime.now().isoformat()
        },
        "claude-risk-advisor": {
            "success": True,
            "confidence": 0.78,
            "converged": True,
            "iterations": 2,
            "execution_time": 38.7,
            "result": {
                "decision": "BUY",
                "risk_level": "LOW",
                "position_size": "5% of portfolio",
                "max_risk": "2%"
            },
            "timestamp": datetime.now().isoformat()
        },
        "claude-funding-advisor": {
            "success": True,
            "confidence": 0.72,
            "converged": True,
            "iterations": 3,
            "execution_time": 42.1,
            "result": {
                "decision": "HOLD",
                "funding_rate": 0.0001,
                "recommendation": "Hold for funding collection",
                "optimal_hold_time": "24 hours"
            },
            "timestamp": datetime.now().isoformat()
        },
        "claude-sentiment-analyzer": {
            "success": True,
            "confidence": 0.68,
            "converged": False,
            "iterations": 2,
            "execution_time": 35.4,
            "result": {
                "decision": "SELL",
                "sentiment_score": -0.2,
                "fear_greed": "FEAR",
                "social_volume": "high"
            },
            "timestamp": datetime.now().isoformat()
        }
    }

    print_success(f"Simulated {len(agent_results)} agent results")
    for name, result in agent_results.items():
        print(f"    {name}: confidence={result['confidence']:.2f}, "
              f"converged={result['converged']}")

    print_section("Agrégation des données")

    context_data = simulate_market_data()
    aggregation_result = aggregator.aggregate_agent_data(agent_results, context_data)

    print_section("Résultats de l'agrégation")
    print(f"  Final Decision: {aggregation_result.final_decision}")
    print(f"  Confidence Score: {aggregation_result.confidence_score:.2f}")
    print(f"  Reliability Score: {aggregation_result.reliability_score:.2f}")

    consensus = aggregation_result.consensus
    print(f"\n  Consensus:")
    print(f"    Decision: {consensus['decision']}")
    print(f"    Confidence: {consensus['confidence']:.2f}")
    print(f"    Agreements: {len(consensus.get('agreements', []))}")

    print_section("Validation des agents")
    for agent_data in aggregation_result.agents_data:
        status_icon = "✓" if agent_data.validation_status == "VALID" else "⚠"
        print(f"  {status_icon} {agent_data.agent_name}:")
        print(f"    Status: {agent_data.validation_status}")
        print(f"    Reliability: {agent_data.reliability_score:.2f}")
        print(f"    Quality: {agent_data.quality_metrics}")

    if aggregation_result.warnings:
        print_warning(f"Warnings: {len(aggregation_result.warnings)}")
        for warning in aggregation_result.warnings[:3]:
            print(f"    - {warning}")

    if aggregation_result.errors:
        print_error(f"Errors: {len(aggregation_result.errors)}")
        for error in aggregation_result.errors[:3]:
            print(f"    - {error}")

    return aggregation_result


async def demo_3_reliability_monitoring():
    """Démonstration 3: Monitoring de fiabilité"""
    print_header("DÉMONSTRATION 3: MONITORING DE FIABILITÉ")

    print_section("Initialisation du ReliabilityMonitor")

    monitor = ReliabilityMonitor()
    print_success("Monitor initialized")

    print_section("Simulation de données de fiabilité")

    aggregator_data = {
        "total_aggregations": 100,
        "successful_aggregations": 85,
        "average_confidence": 0.75,
        "average_reliability": 0.78,
        "recent_aggregations": [
            {
                "id": f"agg_{i}",
                "final_decision": "BUY" if i % 2 == 0 else "HOLD",
                "confidence_score": 0.7 + (i % 10) * 0.03,
                "metadata": {"avg_execution_time": 45.0}
            }
            for i in range(10)
        ]
    }

    agent_status = {
        "claude-strategy-advisor": {
            "health": "HEALTHY",
            "success_rate": 0.9,
            "total_calls": 100,
            "successful_calls": 90
        },
        "claude-risk-advisor": {
            "health": "DEGRADED",
            "success_rate": 0.65,
            "total_calls": 100,
            "successful_calls": 65
        },
        "claude-funding-advisor": {
            "health": "HEALTHY",
            "success_rate": 0.85,
            "total_calls": 100,
            "successful_calls": 85
        },
        "claude-sentiment-analyzer": {
            "health": "HEALTHY",
            "success_rate": 0.88,
            "total_calls": 100,
            "successful_calls": 88
        }
    }

    print_success("Simulated reliability data")
    print_success("Simulated agent status data")

    print_section("Vérification de la santé du système")

    health_report = monitor.check_system_health(aggregator_data, agent_status)

    print_section("Rapport de santé")
    print(f"  Overall Status: {health_report['overall_status']}")
    print(f"  Health Score: {health_report['health_score']:.2f}")

    print(f"\n  Checks:")
    for check_name, check_data in health_report['checks'].items():
        status_icon = "✓" if check_data['status'] == 'PASS' else "⚠"
        print(f"    {status_icon} {check_name}: {check_data['status']} (score: {check_data['score']:.2f})")

    if health_report['recommendations']:
        print(f"\n  Recommendations:")
        for rec in health_report['recommendations']:
            print(f"    - {rec}")

    print_section("Génération d'alertes")

    monitor.create_alert(
        AlertLevel.WARNING,
        "Agent performance degraded",
        "demo",
        {"agent": "claude-risk-advisor", "success_rate": 0.65}
    )
    print_success("Warning alert created")

    monitor.create_alert(
        AlertLevel.CRITICAL,
        "Multiple agents showing issues",
        "demo",
        {"affected_agents": 2}
    )
    print_success("Critical alert created")

    print_section("Résumé des alertes")
    alert_summary = monitor.get_alert_summary()
    print(f"  Total Alerts: {alert_summary['total_alerts']}")
    print(f"  Active Alerts: {alert_summary['active_alerts']}")
    print(f"  Unresolved Critical: {alert_summary['unresolved_critical']}")

    return health_report


async def demo_4_integration():
    """Démonstration 4: Intégration complète"""
    print_header("DÉMONSTRATION 4: INTÉGRATION COMPLÈTE")

    print_section("Initialisation du système complet")

    config = OrchestratorConfig(
        min_confidence=0.6,
        min_reliability=0.7,
        enable_monitoring=True,
        auto_recovery=True,
        strict_validation=False
    )

    orchestrator = ClaudeCodeOrchestrator(config)
    print_success("Orchestrator initialized")

    def on_success(result):
        print(f"\n[Callback] Success: decision={result.decision}, confidence={result.confidence:.2f}")

    def on_failure(error):
        print(f"\n[Callback] Failure: {error}")

    def on_decision(result):
        print(f"\n[Callback] Decision: {result.decision}")

    orchestrator.add_success_callback(on_success)
    orchestrator.add_failure_callback(on_failure)
    orchestrator.add_decision_callback(on_decision)

    print_success("Callbacks registered")

    print_section("Exécution d'un scénario complet")

    market_context = {
        "symbol": "BTC-USD",
        "price": 50000,
        "volume": 1000000,
        "volatility": 0.05,
        "funding_rate": 0.0001,
        "portfolio": {
            "balance": 10000,
            "positions": [
                {"symbol": "BTC-USD", "size": 0.1, "pnl": 500},
            ]
        },
        "sentiment": {
            "fear_greed_index": 45,
            "social_sentiment": 0.1,
        }
    }

    print(f"  Context: {market_context['symbol']} @ ${market_context['price']}")

    result = await orchestrator.execute_trading_analysis(
        task="Comprehensive trading analysis for BTC",
        context_data=market_context,
        mode="complete"
    )

    print_section("Vérification de la santé du système")
    is_healthy = orchestrator.is_system_healthy()
    print(f"  System Healthy: {is_healthy}")

    if is_healthy:
        print_success("System is operating normally")
    else:
        print_warning("System has health issues - check alerts")

    print_section("Statistiques finales")
    stats = orchestrator.get_statistics()
    print(f"  Total Executions: {stats['execution_stats']['total_executions']}")
    print(f"  Success Rate: {stats['success_rate']:.2%}")
    print(f"  Average Confidence: {stats['execution_stats']['average_confidence']:.2f}")
    print(f"  Average Reliability: {stats['execution_stats']['average_reliability']:.2f}")
    print(f"  Active Alerts: {stats['active_alerts']}")

    return result


async def demo_5_system_verification():
    """Démonstration 5: Vérification de la fiabilité du système"""
    print_header("DÉMONSTRATION 5: VÉRIFICATION DE LA FIABILITÉ")

    print_section("Initialisation des composants")

    aggregator = DataAggregator()
    monitor = ReliabilityMonitor()
    orchestrator = ClaudeCodeOrchestrator()

    print_success("All components initialized")

    print_section("Test de fiabilité - Scénario 1: Succès")

    good_results = {
        "claude-strategy-advisor": {
            "success": True, "confidence": 0.85, "converged": True,
            "iterations": 3, "execution_time": 45, "result": {"decision": "BUY"},
            "timestamp": datetime.now().isoformat()
        },
        "claude-risk-advisor": {
            "success": True, "confidence": 0.82, "converged": True,
            "iterations": 2, "execution_time": 38, "result": {"decision": "BUY"},
            "timestamp": datetime.now().isoformat()
        },
        "claude-funding-advisor": {
            "success": True, "confidence": 0.80, "converged": True,
            "iterations": 3, "execution_time": 42, "result": {"decision": "HOLD"},
            "timestamp": datetime.now().isoformat()
        },
        "claude-sentiment-analyzer": {
            "success": True, "confidence": 0.75, "converged": True,
            "iterations": 2, "execution_time": 35, "result": {"decision": "BUY"},
            "timestamp": datetime.now().isoformat()
        }
    }

    aggregation = aggregator.aggregate_agent_data(good_results)
    is_reliable = aggregator.is_system_reliable()

    print(f"  Aggregation Success: {aggregation.final_decision}")
    print(f"  System Reliable: {is_reliable}")

    if is_reliable:
        print_success("System is reliable - all agents functioning correctly")
    else:
        print_warning("System may have reliability issues")

    print_section("Test de fiabilité - Scénario 2: Échecs partiels")

    mixed_results = {
        "claude-strategy-advisor": {
            "success": True, "confidence": 0.85, "converged": True,
            "iterations": 3, "execution_time": 45, "result": {"decision": "BUY"},
            "timestamp": datetime.now().isoformat()
        },
        "claude-risk-advisor": {
            "success": False, "confidence": 0.0, "converged": False,
            "iterations": 0, "execution_time": 0, "result": {},
            "timestamp": datetime.now().isoformat(), "error": "Timeout"
        },
        "claude-funding-advisor": {
            "success": True, "confidence": 0.80, "converged": True,
            "iterations": 3, "execution_time": 42, "result": {"decision": "HOLD"},
            "timestamp": datetime.now().isoformat()
        },
        "claude-sentiment-analyzer": {
            "success": True, "confidence": 0.75, "converged": True,
            "iterations": 2, "execution_time": 35, "result": {"decision": "BUY"},
            "timestamp": datetime.now().isoformat()
        }
    }

    aggregation2 = aggregator.aggregate_agent_data(mixed_results)
    is_reliable2 = aggregator.is_system_reliable()

    print(f"  Aggregation Success: {aggregation2.final_decision}")
    print(f"  System Reliable: {is_reliable2}")

    if is_reliable2:
        print_success("System remains reliable despite partial failures")
    else:
        print_warning("System reliability affected by failures")

    print_section("Test de fiabilité - Scénario 3: Échecs massifs")

    bad_results = {
        "claude-strategy-advisor": {
            "success": True, "confidence": 0.60, "converged": False,
            "iterations": 1, "execution_time": 30, "result": {"decision": "HOLD"},
            "timestamp": datetime.now().isoformat()
        },
        "claude-risk-advisor": {
            "success": False, "confidence": 0.0, "converged": False,
            "iterations": 0, "execution_time": 0, "result": {},
            "timestamp": datetime.now().isoformat(), "error": "Connection failed"
        },
        "claude-funding-advisor": {
            "success": False, "confidence": 0.0, "converged": False,
            "iterations": 0, "execution_time": 0, "result": {},
            "timestamp": datetime.now().isoformat(), "error": "Timeout"
        },
        "claude-sentiment-analyzer": {
            "success": True, "confidence": 0.45, "converged": False,
            "iterations": 1, "execution_time": 25, "result": {"decision": "HOLD"},
            "timestamp": datetime.now().isoformat()
        }
    }

    aggregation3 = aggregator.aggregate_agent_data(bad_results)
    is_reliable3 = aggregator.is_system_reliable()

    print(f"  Aggregation Success: {aggregation3.final_decision}")
    print(f"  System Reliable: {is_reliable3}")

    if is_reliable3:
        print_success("System still operational")
    else:
        print_error("System reliability compromised - intervention required")

    print_section("Rapport de fiabilité global")
    report = aggregator.get_reliability_report()
    print(f"  Total Aggregations: {report['summary']['total_aggregations']}")
    print(f"  Success Rate: {report['summary']['successful_aggregations']}/{report['summary']['total_aggregations']}")
    print(f"  Average Confidence: {report['summary']['average_confidence']:.2f}")
    print(f"  Average Reliability: {report['summary']['average_reliability']:.2f}")

    return {
        "scenario_1_reliable": is_reliable,
        "scenario_2_reliable": is_reliable2,
        "scenario_3_reliable": is_reliable3,
        "report": report
    }


async def main():
    """Fonction principale - Exécute toutes les démonstrations"""
    print("\n" + "="*70)
    cprint("  NOVAQUOTE CLAUDE CODE - SYSTÈME DE FIABILITÉ", "white", attrs=["bold"])
    cprint("  Démonstration complète", "cyan")
    print("="*70 + "\n")

    demos = [
        ("Orchestration de base", demo_1_basic_orchestration),
        ("Agrégation des données", demo_2_data_aggregation),
        ("Monitoring de fiabilité", demo_3_reliability_monitoring),
        ("Intégration complète", demo_4_integration),
        ("Vérification système", demo_5_system_verification),
    ]

    results = {}

    for demo_name, demo_func in demos:
        try:
            result = await demo_func()
            results[demo_name] = result
            cprint(f"\n✅ {demo_name}: SUCCESS", "green")
        except Exception as e:
            cprint(f"\n❌ {demo_name}: FAILED - {e}", "red")
            import traceback
            traceback.print_exc()
            results[demo_name] = {"error": str(e)}

    print_header("RÉSUMÉ FINAL")

    cprint("Composants démontrés:", "white", attrs=["bold"])
    print_success("ClaudeCodeIntegrationManager - Lancement des sub-agents")
    print_success("DataAggregator - Agrégation et validation des données")
    print_success("ReliabilityMonitor - Surveillance continue")
    print_success("ClaudeCodeOrchestrator - Orchestration complète")

    cprint("\nFlux de données:", "white", attrs=["bold"])
    print("  1. Orchestrateur lance les agents")
    print("  2. Agents retournent leurs résultats")
    print("  3. DataAggregator agrège et valide")
    print("  4. ReliabilityMonitor surveille")
    print("  5. Décision finale est prise")

    cprint("\nMécanismes de fiabilité:", "white", attrs=["bold"])
    print_success("Validation des données par agent")
    print_success("Calcul de scores de confiance et fiabilité")
    print_success("Consensus multi-agents")
    print_success("Monitoring en temps réel")
    print_success("Alertes automatiques")
    print_success("Auto-récupération")

    cprint("\nCritères de fiabilité:", "white", attrs=["bold"])
    print("  - Taux de succès > 70%")
    print("  - Confiance moyenne > 0.6")
    print("  - Fiabilité moyenne > 0.7")
    print("  - Moins de 3 échecs consécutifs")
    print("  - Minimum 2 agents en ligne")

    cprint("\n✅ Toutes les démonstrations terminées!", "green", attrs=["bold"])
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
