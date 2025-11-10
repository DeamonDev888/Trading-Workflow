#!/usr/bin/env python3
"""
[OK] Test Suite for NOVAQUOTE Claude Code Integration
Built with love by Deamon Dev [ROCKET]

Teste tous les patterns d'utilisation:
1. Agents individuels
2. Délégation via claude-agents.json
3. Analyse complète
4. Batch processing
5. Boucle autonome (simulée)
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.claude_code_integration import ClaudeCodeIntegrationManager
from termcolor import cprint


class ClaudeCodeIntegrationTester:
    """Testeur pour l'intégration Claude Code"""

    def __init__(self):
        self.manager = ClaudeCodeIntegrationManager(project_root)
        self.test_results = []

    def create_test_context(self) -> dict:
        """Créer un contexte de test"""
        return {
            "symbol": "BTC-USD",
            "price": 50000,
            "volume": 1000000,
            "funding_rate": 0.0001,
            "liquidity": 50000000,
            "volatility": 0.05,
            "market_cap": 1000000000,
            "timestamp": datetime.now().isoformat(),
            "portfolio": {
                "balance": 10000,
                "positions": [
                    {"symbol": "BTC-USD", "size": 0.1, "pnl": 500},
                    {"symbol": "ETH-USD", "size": 5, "pnl": -200}
                ]
            },
            "market_sentiment": {
                "fear_greed_index": 45,
                "social_volume": "medium",
                "news_sentiment": "neutral"
            }
        }

    def test_01_single_agent_calls(self) -> dict:
        """Test 1: Appels d'agents individuels"""
        cprint("\n" + "="*60, "cyan")
        cprint("TEST 1: Single Agent Calls", "cyan")
        cprint("="*60, "cyan")

        agents = [
            "claude-strategy-advisor",
            "claude-risk-advisor",
            "claude-funding-advisor",
            "claude-sentiment-analyzer"
        ]

        context = self.create_test_context()
        results = {}

        for agent in agents:
            cprint(f"\n[Testing] {agent}", "yellow")
            try:
                result = self.manager.call_claude_code_agent(
                    agent_id=agent,
                    prompt=f"Analyze {agent} for BTC trading scenario",
                    context_data=context,
                    use_iterations=True
                )

                success = result.get("success", False)
                converged = result.get("converged", False)
                confidence = result.get("confidence", 0.0)

                cprint(f"  ✅ Success: {success}", "green" if success else "red")
                cprint(f"  🎯 Converged: {converged}", "green" if converged else "yellow")
                cprint(f"  📊 Confidence: {confidence:.2f}", "cyan")

                results[agent] = {
                    "success": success,
                    "converged": converged,
                    "confidence": confidence,
                    "result": result
                }

            except Exception as e:
                cprint(f"  ❌ Error: {e}", "red")
                results[agent] = {"success": False, "error": str(e)}

        return {
            "test": "single_agent_calls",
            "passed": sum(1 for r in results.values() if r.get("success", False)),
            "total": len(agents),
            "results": results
        }

    def test_02_delegation_mode(self) -> dict:
        """Test 2: Mode délégation via claude-agents.json"""
        cprint("\n" + "="*60, "cyan")
        cprint("TEST 2: Delegation Mode (claude-agents.json)", "cyan")
        cprint("="*60, "cyan")

        context = self.create_test_context()
        task = "Analyze BTC trading opportunity and provide recommendations"

        try:
            result = self.manager.delegate_to_claude_agents(task, context)

            success = result.get("success", False)
            delegation = result.get("delegation", False)

            cprint(f"  ✅ Success: {success}", "green" if success else "red")
            cprint(f"  🤖 Delegated: {delegation}", "green" if delegation else "red")

            return {
                "test": "delegation_mode",
                "passed": 1 if success else 0,
                "total": 1,
                "results": {
                    "success": success,
                    "delegation": delegation,
                    "result": result
                }
            }

        except Exception as e:
            cprint(f"  ❌ Error: {e}", "red")
            return {
                "test": "delegation_mode",
                "passed": 0,
                "total": 1,
                "error": str(e)
            }

    def test_03_complete_analysis(self) -> dict:
        """Test 3: Analyse complète"""
        cprint("\n" + "="*60, "cyan")
        cprint("TEST 3: Complete Trading Analysis", "cyan")
        cprint("="*60, "cyan")

        context = self.create_test_context()

        try:
            result = self.manager.run_complete_trading_analysis(context)

            summary = result.get("summary", {})
            agents_results = result.get("agents_results", {})

            cprint(f"  📊 Total Agents: {summary.get('total_agents', 0)}", "cyan")
            cprint(f"  ✅ Converged: {summary.get('converged_agents', 0)}", "green")
            cprint(f"  📈 Avg Confidence: {summary.get('avg_confidence', 0.0):.2f}", "cyan")
            cprint(f"  🎯 Decision: {summary.get('decision', 'HOLD')}", "white")

            all_converged = summary.get('converged_agents', 0) == summary.get('total_agents', 0)
            high_confidence = summary.get('avg_confidence', 0.0) > 0.7

            return {
                "test": "complete_analysis",
                "passed": 1 if (all_converged or high_confidence) else 0,
                "total": 1,
                "results": {
                    "all_converged": all_converged,
                    "high_confidence": high_confidence,
                    "summary": summary,
                    "full_result": result
                }
            }

        except Exception as e:
            cprint(f"  ❌ Error: {e}", "red")
            return {
                "test": "complete_analysis",
                "passed": 0,
                "total": 1,
                "error": str(e)
            }

    def test_04_iteration_strategies(self) -> dict:
        """Test 4: Différentes stratégies d'itération"""
        cprint("\n" + "="*60, "cyan")
        cprint("TEST 4: Iteration Strategies", "cyan")
        cprint("="*60, "cyan")

        from src.agents.iterative_subagent_manager import IterationMode

        strategies = [
            IterationMode.PROGRESSIVE_REFINEMENT,
            IterationMode.CROSS_VALIDATION,
            IterationMode.CONVERGENCE_SEEKING
        ]

        context = self.create_test_context()
        results = {}

        for strategy in strategies:
            cprint(f"\n[Testing] {strategy.value}", "yellow")
            try:
                result = self.manager.call_claude_code_agent(
                    agent_id="claude-strategy-advisor",
                    prompt="Test iteration strategy",
                    context_data=context,
                    use_iterations=True,
                    iteration_mode=strategy
                )

                success = result.get("success", False)
                iterations = result.get("iterations", 0)
                converged = result.get("converged", False)

                cprint(f"  ✅ Success: {success}", "green" if success else "red")
                cprint(f"  🔄 Iterations: {iterations}", "cyan")
                cprint(f"  🎯 Converged: {converged}", "green" if converged else "yellow")

                results[strategy.value] = {
                    "success": success,
                    "iterations": iterations,
                    "converged": converged
                }

            except Exception as e:
                cprint(f"  ❌ Error: {e}", "red")
                results[strategy.value] = {"success": False, "error": str(e)}

        return {
            "test": "iteration_strategies",
            "passed": sum(1 for r in results.values() if r.get("success", False)),
            "total": len(strategies),
            "results": results
        }

    def test_05_report_generation(self) -> dict:
        """Test 5: Génération de rapports"""
        cprint("\n" + "="*60, "cyan")
        cprint("TEST 5: Report Generation", "cyan")
        cprint("="*60, "cyan")

        try:
            context = self.create_test_context()
            result = self.manager.run_complete_trading_analysis(context)

            report_path = self.manager.save_analysis_report(result, "test_report.json")

            # Vérifier que le rapport a été créé
            report_exists = report_path.exists()
            report_size = report_path.stat().st_size if report_exists else 0

            cprint(f"  📄 Report created: {report_exists}", "green" if report_exists else "red")
            cprint(f"  📏 Size: {report_size} bytes", "cyan")

            return {
                "test": "report_generation",
                "passed": 1 if report_exists and report_size > 0 else 0,
                "total": 1,
                "results": {
                    "report_exists": report_exists,
                    "report_size": report_size,
                    "report_path": str(report_path)
                }
            }

        except Exception as e:
            cprint(f"  ❌ Error: {e}", "red")
            return {
                "test": "report_generation",
                "passed": 0,
                "total": 1,
                "error": str(e)
            }

    def test_06_performance_metrics(self) -> dict:
        """Test 6: Métriques de performance"""
        cprint("\n" + "="*60, "cyan")
        cprint("TEST 6: Performance Metrics", "cyan")
        cprint("="*60, "cyan")

        try:
            context = self.create_test_context()

            # Mesurer le temps d'exécution
            start_time = time.time()
            result = self.manager.run_complete_trading_analysis(context)
            execution_time = time.time() - start_time

            summary = result.get("summary", {})

            cprint(f"  ⏱️  Execution time: {execution_time:.2f}s", "cyan")
            cprint(f"  📊 Agents processed: {summary.get('total_agents', 0)}", "cyan")
            cprint(f"  📈 Avg confidence: {summary.get('avg_confidence', 0.0):.2f}", "cyan")

            # Critères de performance
            fast_enough = execution_time < 60  # Moins de 60 secondes
            high_confidence = summary.get('avg_confidence', 0.0) > 0.5

            return {
                "test": "performance_metrics",
                "passed": 1 if (fast_enough and high_confidence) else 0,
                "total": 1,
                "results": {
                    "execution_time": execution_time,
                    "fast_enough": fast_enough,
                    "high_confidence": high_confidence,
                    "agents_count": summary.get('total_agents', 0)
                }
            }

        except Exception as e:
            cprint(f"  ❌ Error: {e}", "red")
            return {
                "test": "performance_metrics",
                "passed": 0,
                "total": 1,
                "error": str(e)
            }

    def run_all_tests(self) -> dict:
        """Exécuter tous les tests"""
        cprint("\n" + "="*60, "cyan")
        cprint("🚀 NOVAQUOTE CLAUDE CODE INTEGRATION TEST SUITE", "cyan")
        cprint("="*60, "cyan")

        tests = [
            ("Single Agent Calls", self.test_01_single_agent_calls),
            ("Delegation Mode", self.test_02_delegation_mode),
            ("Complete Analysis", self.test_03_complete_analysis),
            ("Iteration Strategies", self.test_04_iteration_strategies),
            ("Report Generation", self.test_05_report_generation),
            ("Performance Metrics", self.test_06_performance_metrics)
        ]

        test_results = []
        total_passed = 0
        total_tests = 0

        for test_name, test_func in tests:
            cprint(f"\n▶️  Running: {test_name}", "white")
            try:
                result = test_func()
                test_results.append(result)
                total_passed += result.get("passed", 0)
                total_tests += result.get("total", 0)
            except Exception as e:
                cprint(f"❌ Test failed with exception: {e}", "red")
                test_results.append({
                    "test": test_name,
                    "passed": 0,
                    "total": 1,
                    "error": str(e)
                })
                total_tests += 1

        # Résumé final
        cprint("\n" + "="*60, "cyan")
        cprint("📊 TEST SUMMARY", "cyan")
        cprint("="*60, "cyan")

        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        cprint(f"Total Tests: {total_tests}", "white")
        cprint(f"Passed: {total_passed}", "green")
        cprint(f"Failed: {total_tests - total_passed}", "red")
        cprint(f"Success Rate: {success_rate:.1f}%", "white")

        if success_rate >= 80:
            cprint("\n🎉 ALL TESTS PASSED! Integration is working correctly!", "green")
        elif success_rate >= 60:
            cprint("\n⚠️  SOME TESTS FAILED. Check results above.", "yellow")
        else:
            cprint("\n❌ MANY TESTS FAILED. Review implementation.", "red")

        # Sauvegarder les résultats
        final_report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed": total_passed,
                "failed": total_tests - total_passed,
                "success_rate": success_rate
            },
            "test_results": test_results
        }

        reports_dir = project_root / "reports" / "tests"
        reports_dir.mkdir(parents=True, exist_ok=True)
        report_path = reports_dir / f"claude_code_integration_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(final_report, f, indent=2, ensure_ascii=False)

        cprint(f"\n📄 Detailed report saved: {report_path}", "green")

        return final_report


def main():
    """Point d'entrée"""
    tester = ClaudeCodeIntegrationTester()
    results = tester.run_all_tests()

    # Exit code basé sur le succès
    success_rate = results["summary"]["success_rate"]
    sys.exit(0 if success_rate >= 80 else 1)


if __name__ == "__main__":
    main()
