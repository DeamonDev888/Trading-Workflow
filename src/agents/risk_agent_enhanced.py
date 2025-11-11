import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from .manager import AgentManager as NovaQuoteAgentManager
except ImportError:
    print("⚠️  agent_manager.py non trouvé. Utilisation du CLI direct.")
    NovaQuoteAgentManager = None


class EnhancedRiskAgent:
    def __init__(self, project_path=None):
        if project_path is None:
            project_path = Path(__file__).parent.parent.parent

        self.project_path = project_path

        if NovaQuoteAgentManager:
            self.manager = NovaQuoteAgentManager(project_path)
            self.use_manager = True
        else:
            self.use_manager = False
            print("⚠️  Mode CLI direct - fonctionnalités limitées")

    def comprehensive_analysis(self):
        """
        Analyse complète du module de risque avec tous les agents

        Returns:
            dict: Résultats complets de l'analyse
        """
        print("🚀 Lancement analyse complète du Risk Agent...")

        results = {}

        if self.use_manager:
            print("🐛 Étape 1: Bug Fixer pour risk_agent.py")
            bug_result = self.manager.run_agent(
                "bug-fixer",
                "Analyser et corriger tous les problèmes dans src/agents/risk_agent.py",
            )
            results["bug_fixer"] = bug_result

            print("🔒 Étape 2: Audit de sécurité")
            security_result = self.manager.run_agent(
                "code-reviewer",
                "Audit de sécurité complet de risk_agent.py : vérifier la logique de gestion des risques, les validations d'entrée, et les calculs de position",
            )
            results["security"] = security_result

            print("⚡ Étape 3: Optimisation performance")
            perf_result = self.manager.run_agent(
                "perf-optimizer",
                "Optimiser les performances des calculs de risque dans risk_agent.py : algorithmes, boucles, utilisation mémoire",
            )
            results["performance"] = perf_result

            print("🧪 Étape 4: Tests complets")
            test_result = self.manager.run_agent(
                "test-enhancer",
                "Créer une suite de tests complète pour risk_agent.py : tests unitaires, tests d'intégration, cas limites, tests de charge",
            )
            results["tests"] = test_result

            print("📚 Étape 5: Documentation")
            docs_result = self.manager.run_agent(
                "docs-generator",
                "Générer la documentation complète pour risk_agent.py : API, exemples d'utilisation, architecture",
            )
            results["documentation"] = docs_result
        else:
            print("⚠️  Mode CLI direct - exécution séquentielle...")
            import subprocess

            agents = [
                (
                    "bug-fixer",
                    "Analyser et corriger tous les problèmes dans src/agents/risk_agent.py",
                ),
                ("code-reviewer", "Audit de sécurité complet de risk_agent.py"),
                ("perf-optimizer", "Optimiser les performances des calculs de risque"),
                (
                    "test-enhancer",
                    "Créer une suite de tests complète pour risk_agent.py",
                ),
                (
                    "docs-generator",
                    "Générer la documentation complète pour risk_agent.py",
                ),
            ]

            for agent_name, task in agents:
                print(f"🔄 Exécution de {agent_name}...")
                cmd = [
                    "claude",
                    "--agents",
                    f".claude/agents/novaquote-{agent_name}.json",
                    "--print",
                    "--dangerously-skip-permissions",
                    task,
                ]

                try:
                    result = subprocess.run(
                        cmd, capture_output=True, text=True, cwd=self.project_path
                    )
                    results[agent_name.replace("-", "_")] = {
                        "status": "success" if result.returncode == 0 else "error",
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "returncode": result.returncode,
                    }
                except Exception as e:
                    results[agent_name.replace("-", "_")] = {
                        "status": "error",
                        "error": str(e),
                    }

        self._print_summary(results)

        return results

    def _print_summary(self, results):
        """Affiche un résumé des résultats"""
        print("\n" + "=" * 50)
        print("📊 RÉSUMÉ DE L'ANALYSE RISK_AGENT.PY")
        print("=" * 50)

        for agent, result in results.items():
            status_icon = "✅" if result.get("status") == "success" else "❌"
            agent_name = agent.replace("_", " ").title()
            print(f"{status_icon} {agent_name}: {result.get('status', 'unknown')}")

            if result.get("stdout") and len(result["stdout"]) > 100:
                print(f"   📄 {result['stdout'][:100]}...")

        print("=" * 50)
        print("🎯 Analyse terminée ! Consultez les rapports dans /reports/")

    def quick_fix(self, issue_description):
        """Correction rapide d'un problème spécifique"""
        print(f"🔧 Correction rapide : {issue_description}")

        if self.use_manager:
            task = f"Corriger le problème suivant dans risk_agent.py : {issue_description}"
            result = self.manager.run_agent("bug-fixer", task)
        else:
            import subprocess

            cmd = [
                "claude",
                "--agents",
                ".claude/agents/novaquote-bug-fixer.json",
                "--print",
                "--dangerously-skip-permissions",
                f"Corriger le problème suivant dans risk_agent.py : {issue_description}",
            ]
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_path)
                result = {
                    "status": "success" if result.returncode == 0 else "error",
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                }
            except Exception as e:
                result = {"status": "error", "error": str(e)}

        print(f"Statut : {result.get('status')}")
        if result.get("stdout"):
            print(f"Solution : {result['stdout']}")

        return result

    def validate_risk_logic(self):
        """Validation spécifique de la logique de risque"""
        print("🔍 Validation de la logique de gestion des risques...")

        task = """
        Valider la logique de gestion des risques dans risk_agent.py :
        1. Vérifier les calculs de position sizing
        2. Valider les limites de risque
        3. Contrôler la logique de stop-loss
        4. Vérifier la gestion du drawdown
        5. Analyser les scénarios de crise
        """

        if self.use_manager:
            result = self.manager.run_agent("code-reviewer", task)
        else:
            import subprocess

            cmd = [
                "claude",
                "--agents",
                ".claude/agents/novaquote-code-reviewer.json",
                "--print",
                "--dangerously-skip-permissions",
                task,
            ]
            try:
                subprocess_result = subprocess.run(
                    cmd, capture_output=True, text=True, cwd=self.project_path
                )
                result = {
                    "status": ("success" if subprocess_result.returncode == 0 else "error"),
                    "stdout": subprocess_result.stdout,
                    "stderr": subprocess_result.stderr,
                }
            except Exception as e:
                result = {"status": "error", "error": str(e)}

        return result

    def analyze_file(self, file_path="src/agents/risk_agent.py"):
        """Analyse rapide d'un fichier"""
        print(f"🔍 Analyse rapide de {file_path}...")

        if self.use_manager:
            result = self.manager.analyze_file(file_path)
        else:
            import subprocess

            cmd = [
                "claude",
                "--agents",
                ".claude/agents/novaquote-code-reviewer.json",
                "--print",
                "--dangerously-skip-permissions",
                f"Analyser le fichier {file_path} pour identifier les problèmes",
            ]
            try:
                subprocess_result = subprocess.run(
                    cmd, capture_output=True, text=True, cwd=self.project_path
                )
                result = {
                    "status": ("success" if subprocess_result.returncode == 0 else "error"),
                    "stdout": subprocess_result.stdout,
                    "stderr": subprocess_result.stderr,
                }
            except Exception as e:
                result = {"status": "error", "error": str(e)}

        print(f"Statut : {result.get('status')}")
        if result.get("stdout"):
            print(f"Analyse : {result['stdout'][:500]}...")

        return result


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Enhanced Risk Agent with NOVAQUOTE integration")
    parser.add_argument(
        "--action",
        choices=["analyze", "fix", "validate", "quick"],
        default="analyze",
        help="Action à effectuer",
    )
    parser.add_argument("--issue", help="Description du problème à corriger")
    parser.add_argument("--file", default="src/agents/risk_agent.py", help="Fichier à analyser")

    args = parser.parse_args()

    risk_agent = EnhancedRiskAgent()

    if args.action == "analyze":
        results = risk_agent.comprehensive_analysis()

    elif args.action == "fix" and args.issue:
        result = risk_agent.quick_fix(args.issue)

    elif args.action == "validate":
        result = risk_agent.validate_risk_logic()
        print(f"Validation : {result.get('status')}")

    elif args.action == "quick":
        result = risk_agent.analyze_file(args.file)

    else:
        print(
            "Usage: python risk_agent_enhanced.py --action [analyze|fix|validate|quick] [--issue 'description'] [--file filepath]"
        )
