#!/usr/bin/env python3
"""
[OK] NOVAQUOTE Claude Code Agent Runner
Built with love by Deamon Dev [ROCKET]

Pattern d'utilisation:
1. Utilise claude-agents.json avec --agents @.claude/agents/
2. Exécution autonome des agents trading
3. Système d'itération avancée
4. Reporting et monitoring
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.claude_code_integration import ClaudeCodeIntegrationManager
from termcolor import cprint


class NovaQuoteAgentRunner:
    """Runner principal pour les agents NOVAQUOTE avec Claude Code"""

    def __init__(self, project_path: Optional[str] = None):
        self.project_path = Path(project_path) if project_path else project_root
        self.manager = ClaudeCodeIntegrationManager(self.project_path)
        self.reports_dir = self.project_path / "reports" / "agents"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def run_single_agent(
        self,
        agent_id: str,
        task: str,
        context_file: Optional[str] = None,
        iterations: int = 3,
        save_report: bool = True,
    ) -> Dict:
        """Exécuter un agent unique"""

        cprint(f"\n{'='*60}", "cyan")
        cprint(f"🚀 Running Agent: {agent_id}", "cyan")
        cprint(f"{'='*60}\n", "cyan")

        # Charger le contexte
        context_data = {}
        if context_file and Path(context_file).exists():
            with open(context_file, "r") as f:
                context_data = json.load(f)
            cprint(f"📋 Loaded context from: {context_file}", "green")

        # Exécuter l'agent
        start_time = time.time()
        result = self.manager.call_claude_code_agent(
            agent_id=agent_id,
            prompt=task,
            context_data=context_data,
            use_iterations=iterations > 1,
        )
        execution_time = time.time() - start_time

        # Afficher le résultat
        cprint(f"\n✅ Agent completed in {execution_time:.2f}s", "green")
        cprint(f"📊 Confidence: {result.get('confidence', 0.0):.2f}", "cyan")
        cprint(f"🔄 Iterations: {result.get('iterations', 1)}", "cyan")

        if result.get("converged"):
            cprint("🎯 Converged successfully!", "green")
        else:
            cprint("⚠️ Did not fully converge", "yellow")

        # Sauvegarder le rapport
        if save_report:
            report = {
                "timestamp": datetime.now().isoformat(),
                "agent": agent_id,
                "task": task,
                "execution_time": execution_time,
                "result": result,
                "context_file": context_file,
            }
            self._save_report(report, f"{agent_id}_{int(time.time())}.json")

        return result

    def run_delegation(self, task: str, context_file: Optional[str] = None) -> Dict:
        """Exécuter via délégation automatique (claude-agents.json)"""

        cprint(f"\n{'='*60}", "cyan")
        cprint(f"🎯 Delegating via claude-agents.json", "cyan")
        cprint(f"{'='*60}\n", "cyan")

        # Charger le contexte
        context_data = {}
        if context_file and Path(context_file).exists():
            with open(context_file, "r") as f:
                context_data = json.load(f)
            cprint(f"📋 Loaded context from: {context_file}", "green")

        # Déléguer
        start_time = time.time()
        result = self.manager.delegate_to_claude_agents(task, context_data)
        execution_time = time.time() - start_time

        cprint(f"\n✅ Delegation completed in {execution_time:.2f}s", "green")
        cprint(f"🤖 Success: {result.get('success', False)}", "cyan")

        # Sauvegarder
        report = {
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "execution_time": execution_time,
            "result": result,
            "context_file": context_file,
            "delegation": True,
        }
        self._save_report(report, f"delegation_{int(time.time())}.json")

        return result

    def run_complete_analysis(self, context_file: Optional[str] = None) -> Dict:
        """Exécuter l'analyse complète avec tous les agents"""

        cprint(f"\n{'='*60}", "cyan")
        cprint(f"🎯 Complete NOVAQUOTE Analysis", "cyan")
        cprint(f"{'='*60}\n", "cyan")

        # Charger le contexte
        context_data = {}
        if context_file and Path(context_file).exists():
            with open(context_file, "r") as f:
                context_data = json.load(f)
            cprint(f"📋 Loaded context from: {context_file}", "green")
        else:
            # Contexte par défaut
            context_data = {
                "symbol": "BTC-USD",
                "price": 50000,
                "volume": 1000000,
                "timestamp": datetime.now().isoformat(),
            }
            cprint("📋 Using default market context", "yellow")

        # Exécuter l'analyse complète
        result = self.manager.run_complete_trading_analysis(context_data)

        # Afficher le résumé
        cprint(f"\n{'='*60}", "cyan")
        cprint("📊 ANALYSIS SUMMARY", "cyan")
        cprint(f"{'='*60}", "cyan")

        summary = result.get("summary", {})
        cprint(f"Total Agents: {summary.get('total_agents', 0)}", "white")
        cprint(f"Converged: {summary.get('converged_agents', 0)}", "white")
        cprint(f"Avg Confidence: {summary.get('avg_confidence', 0.0):.2f}", "white")
        cprint(f"Final Decision: {summary.get('decision', 'HOLD')}", "white")

        consensus = result.get("consensus", {})
        cprint(f"\n🤝 Consensus: {consensus.get('reasoning', 'N/A')}", "green")

        # Sauvegarder
        report_path = self.manager.save_analysis_report(
            result, f"complete_analysis_{int(time.time())}.json"
        )
        cprint(f"\n📄 Full report saved: {report_path}", "green")

        return result

    def _save_report(self, report: Dict, filename: str):
        """Sauvegarder un rapport"""
        report_path = self.reports_dir / filename
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        cprint(f"💾 Report saved: {report_path}", "green")

    def run_batch(self, tasks_file: str, parallel: bool = False):
        """Exécuter un batch de tâches"""

        if not Path(tasks_file).exists():
            cprint(f"❌ Tasks file not found: {tasks_file}", "red")
            return

        with open(tasks_file, "r") as f:
            tasks = json.load(f)

        cprint(f"\n{'='*60}", "cyan")
        cprint(f"📦 Running Batch: {len(tasks)} tasks", "cyan")
        cprint(f"{'='*60}\n", "cyan")

        if parallel:
            # TODO: Implémentation parallèle
            cprint("⚠️ Parallel mode not yet implemented", "yellow")
            parallel = False

        results = []
        for i, task in enumerate(tasks, 1):
            cprint(f"\n[Task {i}/{len(tasks)}]", "cyan")
            result = self.run_single_agent(
                agent_id=task["agent"],
                task=task["task"],
                context_file=task.get("context"),
                iterations=task.get("iterations", 3),
            )
            results.append(result)

        cprint(f"\n✅ Batch completed: {len(results)} tasks", "green")
        self._save_report(
            {
                "timestamp": datetime.now().isoformat(),
                "batch_mode": True,
                "parallel": parallel,
                "results": results,
            },
            f"batch_{int(time.time())}.json",
        )

        return results

    def run_autonomous_loop(
        self,
        interval_seconds: int = 300,
        max_iterations: Optional[int] = None,
        context_file: Optional[str] = None,
    ):
        """Mode boucle autonome (tâche planifiée)"""

        cprint(f"\n{'='*60}", "cyan")
        cprint(f"🔄 Autonomous Loop Mode", "cyan")
        cprint(f"Interval: {interval_seconds}s", "cyan")
        cprint(f"Max Iterations: {max_iterations or 'Unlimited'}", "cyan")
        cprint(f"{'='*60}\n", "cyan")

        iteration = 0
        try:
            while True:
                iteration += 1
                cprint(f"\n[Iteration {iteration}]", "cyan")

                # Exécuter l'analyse complète
                result = self.run_complete_analysis(context_file)

                # Vérifier si on doit s'arrêter
                if max_iterations and iteration >= max_iterations:
                    cprint("\n✅ Reached max iterations", "green")
                    break

                # Attendre avant la prochaine itération
                cprint(f"\n⏳ Waiting {interval_seconds}s for next iteration...", "yellow")
                time.sleep(interval_seconds)

        except KeyboardInterrupt:
            cprint("\n\n🛑 Stopped by user", "yellow")
        except Exception as e:
            cprint(f"\n❌ Error: {e}", "red")
            raise


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(
        description="NOVAQUOTE Claude Code Agent Runner"
    )

    # Modes d'exécution
    parser.add_argument(
        "--mode",
        choices=["single", "delegation", "complete", "batch", "autonomous"],
        required=True,
        help="Mode d'exécution",
    )

    # Paramètres pour mode single
    parser.add_argument("--agent", help="Agent ID (pour mode single)")
    parser.add_argument("--task", help="Description de la tâche")

    # Paramètres communs
    parser.add_argument("--context", help="Fichier de contexte (JSON)")
    parser.add_argument("--iterations", type=int, default=3, help="Nombre d'itérations")
    parser.add_argument(
        "--no-save", action="store_true", help="Ne pas sauvegarder le rapport"
    )

    # Paramètres pour batch
    parser.add_argument("--tasks-file", help="Fichier de tâches (JSON)")

    # Paramètres pour autonomous
    parser.add_argument("--interval", type=int, default=300, help="Intervalle en secondes")
    parser.add_argument("--max-iterations", type=int, help="Nombre max d'itérations")

    # Paramètres généraux
    parser.add_argument(
        "--project-path", help="Chemin vers le projet (défaut: courant)"
    )

    args = parser.parse_args()

    # Initialiser le runner
    runner = NovaQuoteAgentRunner(args.project_path)

    try:
        if args.mode == "single":
            if not args.agent or not args.task:
                print("❌ --agent and --task required for single mode")
                sys.exit(1)

            runner.run_single_agent(
                agent_id=args.agent,
                task=args.task,
                context_file=args.context,
                iterations=args.iterations,
                save_report=not args.no_save,
            )

        elif args.mode == "delegation":
            if not args.task:
                print("❌ --task required for delegation mode")
                sys.exit(1)

            runner.run_delegation(task=args.task, context_file=args.context)

        elif args.mode == "complete":
            runner.run_complete_analysis(context_file=args.context)

        elif args.mode == "batch":
            if not args.tasks_file:
                print("❌ --tasks-file required for batch mode")
                sys.exit(1)

            runner.run_batch(tasks_file=args.tasks_file)

        elif args.mode == "autonomous":
            runner.run_autonomous_loop(
                interval_seconds=args.interval,
                max_iterations=args.max_iterations,
                context_file=args.context,
            )

    except Exception as e:
        cprint(f"\n❌ Fatal error: {e}", "red")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
