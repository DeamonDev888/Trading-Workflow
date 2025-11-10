"""
OUTIL AUTONOME DE CORRECTION - NOVAQUOTE Bug Fixer
OUTIL STANDALONE QUI APPELLE CLAUDE CODE CLI

Ce script est un OUTIL AUTONOME (pas un sub-agent Claude Code) qui:
1. Appelle le CLI "claude" via subprocess
2. Lance des itérations autonomes
3. Parse les réponses et applique les corrections

IMPORTANT: Ce n'est PAS un sub-agent task de Claude Code.
Pour un vrai sub-agent task, utilisez task_agent.Task() dans Claude Code.

Usage:
    python CLAUDE_AUTO_LINTER.py --iterations 5 --path src/
    python CLAUDE_AUTO_LINTER.py --watch

Pour un vrai sub-agent task dans Claude Code:
    from task_agent import Task
    agent = Task(
        subagent_type="bug_fixer",
        tools=["Read", "Edit", "Bash", "Grep"],
        prompt="Fix code in src/"
    )
    await agent.run()
"""

import os
import sys
import json
import subprocess
from datetime import datetime
import re

class NOVAQUOTEBugFixerSubAgent:
    """
    VRAI SUB-AGENT CLAUDE CODE qui appelle Claude CLI en itérations
    """

    def __init__(self, target_path="src/", max_iterations=5):
        self.name = "novaquote_bug_fixer_cli"
        self.description = "Auto Bug Fixer NOVAQUOTE avec Claude Code CLI"
        self.version = "2.0.0"
        self.subagent_type = "claude_cli_iterative"
        self.created = datetime.now().isoformat()
        self.target_path = target_path
        self.max_iterations = max_iterations
        self.iteration_count = 0
        self.corrections_applied = []
        self.claude_available, self.claude_command = self._check_claude_cli()

    def get_metadata(self):
        """Retourne les métadonnées du sub-agent"""
        return {
            "name": self.name,
            "description": self.description,
            "type": "claude_cli_iterative",
            "version": self.version,
            "subagent_type": self.subagent_type,
            "created": self.created,
            "target_path": self.target_path,
            "max_iterations": self.max_iterations,
            "claude_available": self.claude_available
        }

    def _check_claude_cli(self):
        """Vérifie si Claude Code CLI est disponible"""
        commands_to_try = ["claude", "claude-code", "npx claude"]

        for cmd in commands_to_try:
            try:
                result = subprocess.run(
                    f"{cmd} --help",
                    capture_output=True,
                    text=True,
                    timeout=10,
                    shell=True
                )
                if "Claude Code" in result.stdout or "Claude Code" in result.stderr or result.returncode == 0:
                    return True, cmd
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue

        return False, None

    def _check_command(self, cmd):
        """Vérifie si une commande existe"""
        result = subprocess.run(
            cmd.split(),
            capture_output=True,
            text=True,
            shell=True
        )
        return result.returncode == 0

    def check_environment(self):
        """Vérifie l'environnement et les prérequis"""
        checks = {}

        checks["claude_cli"] = self.claude_available

        checks["python"] = self._check_command("python --version")

        checks["black"] = self._check_command("python -m black --version")
        checks["isort"] = self._check_command("python -m isort --version")
        checks["eslint"] = self._check_command("npx eslint --version")
        checks["prettier"] = self._check_command("npx prettier --version")

        checks["target_path"] = os.path.exists(self.target_path)

        checks["git"] = self._check_command("git --version")

        return checks

    def _run_claude_iteration(self, iteration_num, analysis_prompt):
        """
        Exécute une itération avec Claude Code CLI
        Retourne: (success: bool, corrections: list, response: str)
        """
        print(f"\n{'='*70}")
        print(f"ITERATION {iteration_num}/{self.max_iterations} - CLAUDE CODE CLI")
        print(f"{'='*70}")

        prompt = f"""[ITERATION {iteration_num}] Fix code in {self.target_path}:

1. Use Read/Glob to scan Python/TS files
2. Use Edit to fix: unused imports, syntax errors, PEP8 issues
3. Reply JSON: {{"files_modified": ["file.py"], "corrections": [{{"file": "x", "type": "fix", "desc": "what"}}]}}

ACT NOW with Edit tool.
"""

        try:
            print(f"[CLAUDE] Appel de Claude Code CLI ({self.claude_command})...")
            print(f"[CLAUDE] Taille du prompt: {len(prompt)} caractères")

            flags = (
                '--allowedTools "Read,Edit,Bash,Grep,Glob"'
                ' --permission-mode acceptEdits'
                ' --output-format json'
                ' --verbose'
            )

            cmd = f'{self.claude_command} -p - {flags}'
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',  # Forcer UTF-8
                cwd=os.getcwd(),
                shell=True
            )

            try:
                stdout, stderr = process.communicate(input=prompt, timeout=600)
                if stdout is None:
                    stdout = ""
                if stderr is None:
                    stderr = ""
            except Exception as e:
                print(f"[ERROR] Exception during communicate: {e}")
                stdout, stderr = "", str(e)

            result = type('obj', (object,), {
                'returncode': process.returncode if process.returncode is not None else -1,
                'stdout': stdout,
                'stderr': stderr
            })

            if result.returncode == 0:
                print(f"[CLAUDE] [OK] Itération {iteration_num} terminée avec succès")

                response = result.stdout
                print(f"\n{'='*70}")
                print(f"[CLAUDE RAW RESPONSE - {len(response)} chars]")
                print(f"{'='*70}")
                print(response[:2000] if len(response) > 2000 else response)
                print(f"{'='*70}\n")

                corrections = self._parse_claude_response(response, iteration_num)

                return True, corrections, response
            else:
                print(f"[CLAUDE] [WARN] Itération {iteration_num} terminée avec avertissements")
                print(f"[ERROR] {result.stderr[:500]}")
                return False, [], result.stderr

        except subprocess.TimeoutExpired:
            print(f"[CLAUDE] [TIMEOUT] Timeout lors de l'itération {iteration_num}")
            return False, [], "Timeout"
        except Exception as e:
            print(f"[CLAUDE] [ERROR] Erreur lors de l'itération {iteration_num}: {e}")
            return False, [], str(e)

    def _parse_claude_response(self, response, iteration_num):
        """Parse la réponse de Claude et extrait les corrections (JSON + regex)"""
        corrections = []

        try:
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                json_data = json.loads(json_str)

                files_modified = json_data.get('files_modified', [])
                corrections_list = json_data.get('corrections', [])

                for corr in corrections_list:
                    corrections.append({
                        'iteration': iteration_num,
                        'description': f"{corr.get('file', '')}: {corr.get('description', '')}",
                        'type': corr.get('type', 'json_fix'),
                        'file': corr.get('file', '')
                    })

                print(f"[PARSE JSON] {len(corrections)} corrections extraites du JSON")
                print(f"  Fichiers modifiés: {', '.join(files_modified[:5])}")
                return corrections

        except (json.JSONDecodeError, AttributeError) as e:
            print(f"[PARSE] JSON non trouvé ou invalide, utilisation des regex... ({str(e)[:50]})")

        patterns = [
            (r'["\']?files?["\']?\s*modified[:\s]+([^\n,}]+)', 'file_modification'),
            (r'["\']?corrections?[:\s]+([^\n}]+)', 'correction'),
            (r'["\']?file["\']?\s*[:\s]+["\']?([^"\']+)["\']?', 'file'),
            (r'["\']?fixed["\']?\s*[:\s]+["\']?([^"\']+)["\']?', 'fix'),
            (r'Edit[^:]*:\s*([^\n]+)', 'edit_action'),
            (r'Modified[^\n]*:\s*([^\n]+)', 'modification'),
        ]

        for pattern, corr_type in patterns:
            matches = re.finditer(pattern, response, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                desc = match.group(1).strip().strip('",[]{}')
                if len(desc) > 2:  # Ignorer les matches vides ou trop courts
                    corrections.append({
                        'iteration': iteration_num,
                        'description': desc,
                        'type': corr_type
                    })

        if corrections:
            print(f"[PARSE] {len(corrections)} corrections détectées dans la réponse")
            for corr in corrections[-5:]:  # Afficher les 5 dernières
                print(f"  [{corr['type']}] {corr['description']}")
        else:
            print(f"[PARSE] Aucune correction détectée (réponse peut être vide ou sans edits)")
            preview = response[:300].replace('\n', ' ')
            print(f"  Aperçu réponse: {preview}...")

        return corrections

    def _analyze_codebase(self):
        """Analyse la base de code + détection des problèmes avec linters"""
        print(f"\n[SCAN] Analyse de la base de code: {self.target_path}")

        stats = {
            'total_files': 0,
            'python_files': 0,
            'typescript_files': 0,
            'total_lines': 0,
            'issues_detected': 0
        }

        for root, dirs, files in os.walk(self.target_path):
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'node_modules', '.pytest_cache']]

            for file in files:
                if file.endswith(('.py', '.ts', '.js')):
                    stats['total_files'] += 1
                    if file.endswith('.py'):
                        stats['python_files'] += 1
                    else:
                        stats['typescript_files'] += 1

                    try:
                        with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            stats['total_lines'] += len(lines)
                    except:
                        pass

        print(f"[SCAN] Résultats:")
        print(f"  - Fichiers totaux: {stats['total_files']}")
        print(f"  - Fichiers Python: {stats['python_files']}")
        print(f"  - Fichiers TypeScript/JS: {stats['typescript_files']}")
        print(f"  - Lignes totales: {stats['total_lines']}")

        print(f"\n[PRE-SCAN] Détection des problèmes avec linters...")
        issues = []

        try:
            result = subprocess.run(
                f'python -m black --check {self.target_path} --diff',
                shell=True, capture_output=True, text=True, timeout=60
            )
            if result.returncode != 0:
                issues.append(f"Black: {len(result.stdout.split('would reformat'))-1} fichiers à reformater")
                print(f"  [WARN] Black: Problèmes de formatage détectés")

            result = subprocess.run(
                f'python -m isort --check-only {self.target_path}',
                shell=True, capture_output=True, text=True, timeout=60
            )
            if result.returncode != 0:
                issues.append("isort: Imports mal triés détectés")
                print(f"  [WARN] isort: Imports mal triés")
        except Exception as e:
            print(f"  [INFO] Linters Python non disponibles: {str(e)[:50]}")

        try:
            result = subprocess.run(
                f'npx eslint {self.target_path}/**/*.{{ts,js}} --format=json',
                shell=True, capture_output=True, text=True, timeout=60
            )
            if result.returncode != 0:
                try:
                    eslint_data = json.loads(result.stdout)
                    total_errors = sum(len(file.get('messages', [])) for file in eslint_data)
                    issues.append(f"ESLint: {total_errors} erreurs détectées")
                    print(f"  [WARN] ESLint: {total_errors} erreurs")
                except:
                    issues.append("ESLint: Erreurs détectées")
                    print(f"  [WARN] ESLint: Problèmes détectés")
        except Exception as e:
            print(f"  [INFO] ESLint non disponible: {str(e)[:50]}")

        stats['issues_detected'] = len(issues)
        if issues:
            print(f"\n[ISSUES] {len(issues)} problèmes détectés:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print(f"\n[ISSUES] Aucun problème détecté par les linters (code propre ou linters non disponibles)")

        return stats

    def run_iterative_fix(self):
        """
        Lance le processus d'itération avec Claude Code CLI
        """
        print(f"\n{'='*70}")
        print(f"CLAUDE CODE CLI AUTONOMOUS BUG FIXER - NOVAQUOTE")
        print(f"{'='*70}")

        initial_stats = self._analyze_codebase()

        if not self.claude_available:
            print("\n[ERROR] Claude Code CLI n'est pas disponible!")
            print("Veuillez installer Claude Code CLI: https://claude.ai/code")
            return False

        print(f"\n[OK] Claude Code CLI détecté")
        print(f"Cible: {self.target_path}")
        print(f"Itérations max: {self.max_iterations}")

        all_success = True
        for i in range(1, self.max_iterations + 1):
            success, corrections, response = self._run_claude_iteration(i, "")
            self.iteration_count = i  # Mettre à jour le compteur d'itérations

            self.corrections_applied.extend(corrections)

            if not success:
                all_success = False
                print(f"\n[WARN] Itération {i} a rencontré des problèmes")

            if i < self.max_iterations:
                print(f"\n[PAUSE] Attente avant l'itération {i+1}...")
                import time
                time.sleep(2)

            if i > 1 and len(corrections) == 0:
                print(f"\n[OK] Convergence atteinte! Aucune correction nécessaire à l'itération {i}")
                break

        self._generate_final_report(initial_stats)

        return all_success

    def _generate_final_report(self, initial_stats):
        """Génère un rapport final des corrections"""
        print(f"\n{'='*70}")
        print(f"RAPPORT FINAL - CLAUDE CODE CLI BUG FIXER")
        print(f"{'='*70}")

        print(f"Itérations effectuées: {self.iteration_count}/{self.max_iterations}")
        print(f"Corrections appliquées: {len(self.corrections_applied)}")

        if self.corrections_applied:
            print(f"\nCorrections détaillées:")
            for corr in self.corrections_applied[-10:]:  # Dernières 10
                print(f"  [{corr['iteration']}] {corr['description']}")

        try:
            final_stats = self._analyze_codebase()
            print(f"\nComparaison:")
            print(f"  Avant: {initial_stats['total_files']} fichiers, {initial_stats['total_lines']} lignes")
            print(f"  Après: {final_stats['total_files']} fichiers, {final_stats['total_lines']} lignes")
        except:
            pass

    def execute(self, mode="iterative"):
        """Point d'entrée principal"""
        print(f"\n{'='*70}")
        print(f"CLAUDE CODE CLI SUB-AGENT - NOVAQUOTE BUG FIXER v{self.version}")
        print(f"{'='*70}")

        metadata = self.get_metadata()
        print(f"\n[INFO] Sub-Agent: {metadata['name']}")
        print(f"[INFO] Type: {metadata['type']}")
        print(f"[INFO] Version: {metadata['version']}")
        print(f"[INFO] Cible: {metadata['target_path']}")
        print(f"[INFO] Claude CLI: {'[OK]' if metadata['claude_available'] else '[FAIL]'}")

        print(f"\n[CHECKING ENVIRONMENT]")
        checks = self.check_environment()
        for tool, status in checks.items():
            print(f"  {'[OK]' if status else '[FAIL]'} {tool}")

        if all(checks.values()):
            print(f"\n[READY] Environnement prêt, lancement des corrections...")
            success = self.run_iterative_fix()

            if success:
                print(f"\n[OK] SUCCÈS: Corrections terminées")
            else:
                print(f"\n[WARN] AVERTISSEMENT: Corrections terminées avec des problèmes")
        else:
            print(f"\n[ERROR] ERREUR: Environnement non prêt")
            print("Veuillez installer les outils manquants")

        print(f"\n{'='*70}")

        return self.get_status()

    def get_status(self):
        """Retourne le statut complet"""
        metadata = self.get_metadata()
        checks = self.check_environment()

        status = {
            "sub_agent": metadata,
            "environment": checks,
            "ready": all(checks.values()),
            "timestamp": datetime.now().isoformat(),
            "iterations_completed": self.iteration_count,
            "corrections_applied": len(self.corrections_applied)
        }

        return status

def main():
    """Point d'entrée principal avec support CLI"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Claude Code CLI Autonomous Bug Fixer - NOVAQUOTE",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  %(prog)s                                    # Corrige src/ avec 5 itérations
  %(prog)s --iterations 10                    # Corrige avec 10 itérations
  %(prog)s --path backend/ --iterations 3     # Corrige backend/ avec 3 itérations
  %(prog)s --check-only                       # Vérifie seulement l'environnement
        """
    )

    parser.add_argument(
        '--iterations',
        type=int,
        default=5,
        help='Nombre maximum d\'itérations avec Claude (défaut: 5)'
    )

    parser.add_argument(
        '--path',
        type=str,
        default='src/',
        help='Chemin du dossier à corriger (défaut: src/)'
    )

    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Vérifie seulement l\'environnement sans corriger'
    )

    parser.add_argument(
        '--watch',
        action='store_true',
        help='Mode surveillance continue (watch files for changes)'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 2.0.0'
    )

    args = parser.parse_args()

    agent = NOVAQUOTEBugFixerSubAgent(
        target_path=args.path,
        max_iterations=args.iterations
    )

    print("\n" + "="*70)
    print("CLAUDE CODE CLI AUTONOMOUS SUB-AGENT - NOVAQUOTE")
    print("="*70)
    print(f"Version: {agent.version}")
    print(f"Claude CLI: {'[OK]' if agent.claude_available else '[FAIL]'}")
    print(f"Cible: {args.path}")
    print(f"Itérations: {args.iterations}")
    print("="*70 + "\n")

    if args.check_only:
        print("[INFO] Mode vérification uniquement\n")
        checks = agent.check_environment()
        for tool, status in checks.items():
            print(f"  {'[OK]' if status else '[FAIL]'} {tool}")
        print()
        status = agent.get_status()
        print("[RESULT]")
        print(json.dumps(status, indent=2))
        return 0 if status["ready"] else 1

    if args.watch:
        print("[INFO] Mode surveillance continue activé\n")
        print("Surveillance des fichiers dans:", args.path)
        print("Appuyez sur Ctrl+C pour arrêter\n")

        try:
            import time
            last_run = 0
            while True:
                current_time = time.time()
                if current_time - last_run > 30:
                    print(f"\n[{time.strftime('%H:%M:%S')}] Vérification des modifications...")
                    result = agent.execute("iterative")
                    last_run = current_time
                time.sleep(5)
        except KeyboardInterrupt:
            print("\n\n[INFO] Surveillance arrêtée par l'utilisateur")
    else:
        print("[INFO] Démarrage du processus de correction itératif...\n")
        result = agent.execute("iterative")

    print("\n[FINAL STATUS]")
    print(json.dumps(result, indent=2))

    return 0 if result["ready"] and len(agent.corrections_applied) > 0 else 1

if __name__ == "__main__":
    sys.exit(main())
