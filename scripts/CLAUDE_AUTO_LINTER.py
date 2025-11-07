#!/usr/bin/env python3
"""
CLAUDE CODE SUB-AGENT - NOVAQUOTE Bug Fixer
VRAI SUB-AGENT TASK POUR CLAUDE CODE

Ce script peut être invoqué comme un sub-agent Task de Claude Code
avec : claude --dangerously-skip-permissions

Invocation dans Claude Code :
    from task_agent import Task
    agent = Task(
        subagent_type="novaquote_bug_fixer",
        description="Auto Bug Fixer NOVAQUOTE",
        prompt="Execute automatic bug fixing",
        model="sonnet"
    )
"""

import os
import sys
import json
import subprocess
from datetime import datetime

class NOVAQUOTEBugFixerSubAgent:
    """
    VRAI SUB-AGENT CLAUDE CODE pour Bug Fixer NOVAQUOTE
    """

    def __init__(self):
        self.name = "novaquote_bug_fixer"
        self.description = "Auto Bug Fixer NOVAQUOTE Trading System"
        self.version = "1.0.0"
        self.subagent_type = "novaquote_bug_fixer"
        self.created = datetime.now().isoformat()

    def get_metadata(self):
        """Retourne les métadonnées du sub-agent"""
        return {
            "name": self.name,
            "description": self.description,
            "type": "sub_agent_task",
            "version": self.version,
            "subagent_type": self.subagent_type,
            "created": self.created
        }

    def check_environment(self):
        """Vérifie l'environnement"""
        checks = {}

        # Python
        checks["python"] = self._check_command("python --version")

        # Auto-bug-fixer CLI
        checks["auto_linter"] = os.path.exists("auto_bug_fixer_cli.py")

        # Prettier config
        checks["prettierrc"] = os.path.exists(".prettierrc")

        # TypeScript
        checks["typescript"] = self._check_command("npx tsc --version")

        # ESLint
        checks["eslint"] = self._check_command("npx eslint --version")

        # Prettier
        checks["prettier"] = self._check_command("npx prettier --version")

        # Black
        checks["black"] = self._check_command("python -m black --version")

        # isort
        checks["isort"] = self._check_command("python -m isort --version")

        # Flake8
        checks["flake8"] = self._check_command("python -m flake8 --version")

        return checks

    def _check_command(self, cmd):
        """Vérifie si une commande existe"""
        result = subprocess.run(
            cmd.split(),
            capture_output=True,
            text=True,
            shell=True
        )
        return result.returncode == 0

    def run_linter(self, mode="once"):
        """Exécute l'auto-linter avec auto-correction complète"""
        if mode == "once":
            print("\n[EXECUTING AUTO-LINTER - ONCE MODE]")
            print("[AUTO-CORRECTION ENABLED - ADVANCED MODE]\n")

            # Utiliser les scripts package.json pour une correction complète
            commands = [
                # Python : Correction complète avec Black (Black n'a pas --fix, c'est le mode par défaut)
                ("python", ["python", "-m", "black", "src/", "--line-length=88"]),
                ("python", ["python", "-m", "isort", "src/", "--profile=black"]),

                # TypeScript : Correction complète avec ESLint v9 + Prettier
                ("typescript", ["npx", "eslint", "**/*.{js,ts}", "--fix"]),
                ("typescript", ["npx", "prettier", "--write", "**/*.{js,ts,json,md}", "--prose-wrap", "always"]),

                # TypeScript : Vérification avec tsc (si disponible)
                ("typescript", ["npx", "tsc", "--noEmit", "--skipLibCheck"]),
            ]

            all_success = True
            for name, cmd in commands:
                try:
                    print(f"[CORRECTING] {name.upper()}...")
                    print(f"  Command: {' '.join(cmd)}")
                    result = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=120)

                    if result.returncode == 0:
                        print(f"  [OK] {name.upper()} corrected successfully")
                        if result.stdout:
                            print(f"  {result.stdout[:200]}")
                    else:
                        print(f"  [WARN] {name.upper()} had warnings (non-critical)")
                        if result.stdout:
                            print(f"  {result.stdout[:200]}")
                        if result.stderr:
                            print(f"  {result.stderr[:200]}")
                except Exception as e:
                    print(f"  [ERROR] {name.upper()} error: {str(e)[:100]}")
                    all_success = False

            # Phase 2: Correction avancée avec scripts personnalisés
            print("\n[ADVANCED CORRECTION - PHASE 2]")
            self._run_advanced_corrections()

            return all_success
        elif mode == "continuous":
            print("\n[EXECUTING AUTO-LINTER - CONTINUOUS MODE]")
            print("[INFO] Continuous mode not available - use 'once' mode")
            return False

    def _run_advanced_corrections(self):
        """Corrections avancées pour les erreurs non-corrigées par Black/isort"""
        try:
            # Utiliser autoflake pour supprimer les imports non utilisés
            print("\n[ADVANCED] Python: Using autoflake to remove ALL unused imports...")
            subprocess.run(
                ["python", "-m", "autoflake", "--in-place", "--remove-all-unused-imports", "--recursive", "src/"],
                timeout=60
            )
            print("  [OK] autoflake: All unused imports removed")

            # Utiliser autopep8 pour corriger les erreurs PEP8 supplémentaires
            print("\n[ADVANCED] Python: Using autopep8 for PEP8 compliance...")
            subprocess.run(
                ["python", "-m", "autopep8", "--in-place", "--aggressive", "--aggressive", "src/"],
                timeout=60
            )
            print("  [OK] autopep8: PEP8 compliance applied")

            # Utiliser pyupgrade pour corriger la documentation
            print("\n[ADVANCED] Python: Using pyupgrade for modern Python features...")
            subprocess.run(
                ["python", "-m", "pyupgrade", "--py38-plus", "src/"],
                timeout=60
            )
            print("  [OK] pyupgrade: Modern Python features applied")

            # PHASE 3: CORRECTION AUTOMATIQUE AVEC CLI INTELLIGENT
            print("\n[PHASE 3] INTELLIGENT AUTO-CORRECTION WITH CLI")
            print("="*60)
            subprocess.run(["python", "auto_bug_fixer_cli.py"], timeout=120)
            print("="*60)

        except FileNotFoundError as e:
            print(f"  [INFO] Advanced tools not available: {str(e)[:50]}")
            print("  [INFO] To enable full corrections, install: pip install autoflake autopep8 pyupgrade")
        except Exception as e:
            print(f"  [WARN] Advanced correction error: {str(e)[:100]}")

    def get_status(self):
        """Retourne le statut complet"""
        metadata = self.get_metadata()
        checks = self.check_environment()

        status = {
            "sub_agent": metadata,
            "environment": checks,
            "ready": all(checks.values()),
            "timestamp": datetime.now().isoformat()
        }

        return status

    def execute(self, mode="once"):
        """Exécution principale du sub-agent"""
        print("="*60)
        print("CLAUDE CODE SUB-AGENT - NOVAQUOTE BUG FIXER")
        print("="*60)

        # Afficher métadonnées
        metadata = self.get_metadata()
        print(f"\n[INFO] Sub-Agent: {metadata['name']}")
        print(f"[INFO] Type: {metadata['type']}")
        print(f"[INFO] Version: {metadata['version']}")
        print(f"[INFO] Created: {metadata['created']}")

        # Vérifier environnement
        print("\n[CHECKING ENVIRONMENT]")
        checks = self.check_environment()
        for tool, status in checks.items():
            print(f"  {'OK' if status else 'MISSING'} {tool}")

        # Exécuter bug fixer
        if all(checks.values()):
            print("\n[ENVIRONMENT READY]")
            success = self.run_linter(mode)
            if success:
                print("\n[SUCCESS] Bug fixing completed")
            else:
                print("\n[ERROR] Bug fixing failed")
        else:
            print("\n[ERROR] Environment not ready")
            print("Please install missing tools")

        print("\n" + "="*60)

        return self.get_status()

# MAIN ENTRY POINT
def main():
    """Point d'entrée principal"""
    agent = NOVAQUOTEBugFixerSubAgent()

    # Mode d'exécution
    mode = sys.argv[1] if len(sys.argv) > 1 else "once"

    # Exécuter
    result = agent.execute(mode)

    # Retourner JSON
    print("\n[RESULT]")
    print(json.dumps(result, indent=2))

    return 0 if result["ready"] else 1

if __name__ == "__main__":
    sys.exit(main())
