import datetime
import json
import subprocess
import sys
from pathlib import Path


class NovaQuoteAgentManager:
    def __init__(self, project_path):
        self.project_path = Path(project_path)
        self.agents_path = self.project_path / ".claude" / "agents"
        self.reports_path = self.project_path / "reports"
        self.reports_path.mkdir(exist_ok=True)

    def run_agent(self, agent_name, task, save_report=True):
        """
        Exécute un agent NOVAQUOTE et récupère sa réponse

        Args:
            agent_name (str): Nom de l'agent (bug-fixer, code-reviewer, etc.)
            task (str): Tâche à effectuer
            save_report (bool): Sauvegarder le rapport

        Returns:
            dict: Résultat de l'exécution avec sortie et statut
        """
        agent_file = self.agents_path / f"novaquote-{agent_name}.json"

        if not agent_file.exists():
            return {"error": f"Agent {agent_name} non trouvé", "status": "error"}

        cmd = [
            "claude",
            "--agents",
            str(agent_file),
            "--print",
            "--dangerously-skip-permissions",
            task,
        ]

        try:
            print(f"[START] Exécution de l'agent {agent_name}...")
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_path)

            response = {
                "agent": agent_name,
                "task": task,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "timestamp": datetime.datetime.now().isoformat(),
                "status": "success" if result.returncode == 0 else "error",
            }

            if save_report:
                self._save_report(response)

            return response

        except Exception as e:
            return {
                "agent": agent_name,
                "task": task,
                "error": str(e),
                "status": "exception",
                "timestamp": datetime.datetime.now().isoformat(),
            }

    def _save_report(self, response):
        """Sauvegarde le rapport de l'agent"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{response['agent']}_report_{timestamp}.json"
        report_file = self.reports_path / filename

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(response, f, indent=2, ensure_ascii=False)

        print(f"📄 Rapport sauvegardé: {report_file}")

    def analyze_file(self, file_path, agent_type="code-reviewer"):
        """
        Analyse un fichier spécifique avec un agent

        Args:
            file_path (str): Chemin du fichier à analyser
            agent_type (str): Type d'agent à utiliser

        Returns:
            dict: Résultat de l'analyse
        """
        task = f"Analyser le fichier {file_path} pour identifier les problèmes"
        return self.run_agent(agent_type, task)

    def fix_issues(self, file_path=None):
        """Utilise le bug-fixer pour corriger les problèmes"""
        if file_path:
            task = f"Corriger les problèmes dans le fichier {file_path}"
        else:
            task = "Analyser et corriger les problèmes dans tout le codebase"

        return self.run_agent("bug-fixer", task)

    def generate_docs(self, component=None):
        """Génère la documentation"""
        if component:
            task = f"Générer la documentation pour {component}"
        else:
            task = "Générer la documentation complète du projet"

        return self.run_agent("docs-generator", task)

    def optimize_performance(self, component=None):
        """Optimise les performances"""
        if component:
            task = f"Optimiser les performances de {component}"
        else:
            task = "Optimiser les performances du système complet"

        return self.run_agent("perf-optimizer", task)

    def enhance_tests(self, component=None):
        """Améliore les tests"""
        if component:
            task = f"Créer des tests pour {component}"
        else:
            task = "Améliorer la couverture de tests du projet"

        return self.run_agent("test-enhancer", task)

    def security_audit(self, component=None):
        """Effectue un audit de sécurité"""
        if component:
            task = f"Audit de sécurité de {component}"
        else:
            task = "Audit de sécurité complet du système"

        return self.run_agent("code-reviewer", task)

    def complete_analysis(self):
        """Effectue une analyse complète avec tous les agents"""
        print("🔍 Lancement analyse complète NOVAQUOTE...")

        results = {}

        print("🐛 Étape 1: Bug Fixer...")
        results["bug_fixer"] = self.fix_issues()

        print("🔒 Étape 2: Code Reviewer...")
        results["code_reviewer"] = self.security_audit()

        print("[FAST] Étape 3: Performance Optimizer...")
        results["performance"] = self.optimize_performance()

        print("🧪 Étape 4: Test Enhancer...")
        results["tests"] = self.enhance_tests()

        print("📚 Étape 5: Documentation Generator...")
        results["documentation"] = self.generate_docs()

        print("[OK] Analyse complète terminée !")

        print("\n[METRICS] Résumé des résultats:")
        for agent, result in results.items():
            status_icon = "[OK]" if result["status"] == "success" else "[ERROR]"
            print(f"{status_icon} {agent}: {result['status']}")

        return results


if __name__ == "__main__":
    current_file = Path(__file__).resolve()
    project_path = current_file.parent.parent.parent

    manager = NovaQuoteAgentManager(project_path)

    print("[START] NOVAQUOTE Agent Manager")
    print("=" * 40)

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "analyze":
            file_path = sys.argv[2] if len(sys.argv) > 2 else None
            if file_path:
                result = manager.analyze_file(file_path)
            else:
                print("Usage: python agent_manager.py analyze <file_path>")

        elif command == "fix":
            file_path = sys.argv[2] if len(sys.argv) > 2 else None
            result = manager.fix_issues(file_path)

        elif command == "docs":
            component = sys.argv[2] if len(sys.argv) > 2 else None
            result = manager.generate_docs(component)

        elif command == "perf":
            component = sys.argv[2] if len(sys.argv) > 2 else None
            result = manager.optimize_performance(component)

        elif command == "test":
            component = sys.argv[2] if len(sys.argv) > 2 else None
            result = manager.enhance_tests(component)

        elif command == "security":
            component = sys.argv[2] if len(sys.argv) > 2 else None
            result = manager.security_audit(component)

        elif command == "complete":
            result = manager.complete_analysis()

        else:
            print("Commandes disponibles:")
            print("  analyze <file>     - Analyser un fichier")
            print("  fix [file]         - Corriger les problèmes")
            print("  docs [component]   - Générer la documentation")
            print("  perf [component]   - Optimiser les performances")
            print("  test [component]   - Améliorer les tests")
            print("  security [component] - Audit de sécurité")
            print("  complete           - Analyse complète")
            exit(1)
    else:
        result = manager.complete_analysis()

    print(f"\nStatut final: {result.get('status', 'unknown')}")
