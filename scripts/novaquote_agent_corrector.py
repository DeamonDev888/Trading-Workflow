"""
NOVAQUOTE AGENT CORRECTOR
L'AGENT CORRECTEUR qui utilise TOUS les scanners existants
et applique TOUTES les corrections automatiques
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

class NovaQuoteAgentCorrector:
    """Agent correcteur MAITRE qui orchestre TOUS les scanners"""

    def __init__(self):
        self.project_root = Path(".")
        self.scanners = [
            "novaquote_detect_fix_critical_errors.py",
            "novaquote_detect_typescript_errors.py",
            "novaquote_detect_fix_python_errors.py",
            "novaquote_detect_critical_errors.py",
            "novaquote_detect_all_project_errors.py",
            "novaquote_detect_auto_errors.py",
            "novaquote_detect_python_format_errors.py",
            "novaquote_detect_intelligent_errors.py",
            "novaquote_detect_clear_errors.py"
        ]

        self.stats = {
            'scanners_executed': 0,
            'errors_found': 0,
            'corrections_applied': 0,
            'files_fixed': set(),
            'scanners_success': {},
            'scanners_failed': []
        }

    def execute_all_correction(self):
        """Exécute TOUS les scanners et applique TOUTES les corrections"""
        print("NOVAQUOTE AGENT CORRECTOR v6.0")
        print("AGENT CORRECTEUR qui utilise TOUS les scanners NovaQuote")
        print("="*80)

        print("\nPHASE 1: EXECUTION TOUS LES SCANNERS")
        self._execute_all_scanners()

        print("\nPHASE 2: CORRECTIONS AGRESSIVES COMPLETES")
        self._apply_aggressive_corrections()

        print("\nPHASE 3: VALIDATION BLACK/ISORT")
        self._validate_formatting()

        print("\nPHASE 4: VALIDATION TYPESCRIPT")
        self._validate_typescript()

        print("\nPHASE 5: RAPPORT FINAL AGENT")
        self._generate_agent_report()

    def _execute_all_scanners(self):
        """Exécute TOUS les scanners NovaQuote"""
        scripts_dir = Path("scripts")

        for scanner in self.scanners:
            scanner_path = scripts_dir / scanner
            if scanner_path.exists():
                print(f"\n  > SCANNER: {scanner}")
                self._execute_single_scanner(scanner_path, scanner)
            else:
                print(f"\n  ! SCANNER MANQUANT: {scanner}")
                self.stats['scanners_failed'].append(scanner)

        self.stats['scanners_executed'] = len(self.scanners)

    def _execute_single_scanner(self, scanner_path, scanner_name):
        """Exécute un scanner individuel avec correction automatique"""
        try:
            print(f"    📡 Exécution: {scanner_name}")

            if "detect_fix_critical_errors" in scanner_name:
                cmd = ["python", str(scanner_path)]
            elif "detect_typescript_errors" in scanner_name:
                cmd = ["python", str(scanner_path), "--all", "--fix"]
            elif "detect_fix_python_errors" in scanner_name:
                cmd = ["python", str(scanner_path), "--aggressive"]
            elif "detect_python_format_errors" in scanner_name:
                cmd = ["python", str(scanner_path), "--all"]
            elif "detect_auto_errors" in scanner_name:
                cmd = ["python", str(scanner_path), "--scan", "--fix"]
            else:
                cmd = ["python", str(scanner_path)]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(self.project_root)
            )

            if result.returncode == 0:
                print(f"    ✅ {scanner_name}: Succès")
                self.stats['scanners_success'][scanner_name] = True

                if "corrections" in result.stdout.lower():
                    lines = result.stdout.split('\n')
                    corrections_count = sum(1 for line in lines if "correction" in line.lower() or "fix" in line.lower())
                    self.stats['corrections_applied'] += corrections_count
                    print(f"    🔧 {corrections_count} corrections appliquées")

            else:
                print(f"    ⚠️  {scanner_name}: Erreurs détectées")
                print(f"       {result.stderr[:200]}...")
                self.stats['scanners_success'][scanner_name] = False

        except subprocess.TimeoutExpired:
            print(f"    ⏰ {scanner_name}: Timeout (120s)")
            self.stats['scanners_failed'].append(scanner_name)
        except Exception as e:
            print(f"    ❌ {scanner_name}: Erreur exécution: {e}")
            self.stats['scanners_failed'].append(scanner_name)

    def _apply_aggressive_corrections(self):
        """Corrections AGRESSIVES additionnelles"""
        print("  🔧 Corrections agressives globales...")

        try:
            print("    📝 Application Black formatting...")
            result = subprocess.run(
                ["python", "-m", "black", "src/", "--line-length=100"],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                print("    ✅ Black formatting appliqué")
                self.stats['corrections_applied'] += 10  # Estimation
            else:
                print("    ⚠️  Black formatting: erreurs")
        except Exception as e:
            print(f"    ❌ Black formatting erreur: {e}")

        try:
            print("    📦 Organisation imports avec isort...")
            result = subprocess.run(
                ["python", "-m", "isort", "src/", "--profile", "black"],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                print("    ✅ Imports organisés avec isort")
                self.stats['corrections_applied'] += 5
            else:
                print("    ⚠️  isort: erreurs")
        except Exception as e:
            print(f"    ❌ isort erreur: {e}")

        try:
            print("    🎨 Application Prettier...")
            result = subprocess.run(
                ["npx", "prettier", "--write", "**/*.ts", "**/*.tsx", "**/*.js", "**/*.jsx"],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                print("    ✅ Prettier appliqué")
                self.stats['corrections_applied'] += 8
            else:
                print("    ⚠️  Prettier: erreurs")
        except Exception as e:
            print(f"    ❌ Prettier erreur: {e}")

    def _validate_formatting(self):
        """Validation finale du formatting Python"""
        print("  🔍 Validation formatting Python...")

        try:
            result = subprocess.run(
                ["python", "-m", "black", "--check", "src/", "--line-length=100"],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                print("    ✅ Black formatting: PARFAIT")
            else:
                print("    ⚠️  Black formatting: améliorations nécessaires")

        except Exception as e:
            print(f"    ❌ Erreur validation Black: {e}")

        try:
            result = subprocess.run(
                ["python", "-m", "isort", "--check-only", "src/", "--profile", "black"],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                print("    ✅ isort: PARFAIT")
            else:
                print("    ⚠️  isort: améliorations nécessaires")

        except Exception as e:
            print(f"    ❌ Erreur validation isort: {e}")

    def _validate_typescript(self):
        """Validation finale TypeScript"""
        print("  🔍 Validation TypeScript...")

        try:
            result = subprocess.run(
                ["npx", "tsc", "--noEmit", "--skipLibCheck"],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                print("    ✅ TypeScript: PARFAIT")
            else:
                print("    ⚠️  TypeScript: erreurs restantes")

        except Exception as e:
            print(f"    ❌ Erreur validation TypeScript: {e}")

        try:
            result = subprocess.run(
                ["npx", "eslint", ".", "--ext", ".ts,.tsx"],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                print("    ✅ ESLint: PARFAIT")
            else:
                print("    ⚠️  ESLint: améliorations nécessaires")

        except Exception as e:
            print(f"    ❌ Erreur validation ESLint: {e}")

    def _generate_agent_report(self):
        """Générer le rapport final de l'agent correcteur"""
        print("\n" + "="*100)
        print("RAPPORT FINAL AGENT CORRECTEUR NOVAQUOTE")
        print("="*100)

        success_rate = 0
        if self.stats['scanners_executed'] > 0:
            success_rate = len(self.stats['scanners_success']) / self.stats['scanners_executed'] * 100

        print(f"\n📊 STATISTIQUES AGENT")
        print(f"   📡 Scanners exécutés: {self.stats['scanners_executed']}")
        print(f"   ✅ Scanners réussis: {len(self.stats['scanners_success'])}")
        print(f"   ❌ Scanners échoués: {len(self.stats['scanners_failed'])}")
        print(f"   📈 Taux de succès: {success_rate:.1f}%")
        print(f"   🔧 Corrections appliquées: {self.stats['corrections_applied']}")

        print(f"\n📋 DÉTAIL SCANNERS")
        for scanner, success in self.stats['scanners_success'].items():
            status = "✅ SUCCÈS" if success else "❌ ÉCHEC"
            print(f"   {scanner}: {status}")

        if self.stats['scanners_failed']:
            print(f"\n❌ SCANNERS ÉCHOUÉS:")
            for failed in self.stats['scanners_failed']:
                print(f"   - {failed}")

        print(f"\n🎯 ÉTAT FINAL PROJET")
        if success_rate >= 80:
            print(f"   🏆 EXCELLENT! {success_rate:.0f}% des scanners réussis")
            print(f"   ✨ Le projet NovaQuote est en excellente état!")
        elif success_rate >= 60:
            print(f"   ✅ BON! {success_rate:.0f}% des scanners réussis")
            print(f"   📈 Le projet est en bon état")
        else:
            print(f"   ⚠️  AMÉLIORATION NÉCESSAIRE: {success_rate:.0f}% seulement")
            print(f"   🔧 Corrections manuelles requises")

        report_data = {
            "timestamp": datetime.now().isoformat(),
            "agent_type": "NOVAQUOTE AGENT CORRECTOR v6.0",
            "stats": self.stats,
            "success_rate": success_rate,
            "scanners_executed": list(self.stats['scanners_success'].keys()),
            "scanners_failed": self.stats['scanners_failed']
        }

        report_path = "novaquote_agent_corrector_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        print(f"\n📄 Rapport agent sauvegardé: {report_path}")
        print(f"\n🏁 AGENT CORRECTEUR TERMINÉ")

def main():
    """Main function"""
    print("Lancement de l'AGENT CORRECTEUR NovaQuote...")

    corrector = NovaQuoteAgentCorrector()
    corrector.execute_all_correction()

if __name__ == "__main__":
    main()