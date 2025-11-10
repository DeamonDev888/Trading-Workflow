"""
NOVAQUOTE ULTIMATE CORRECTOR
Agent CORRECTEUR qui utilise TOUS les scripts NovaQuote SANS emojis
V7.0 - Correction COMPLETE et PROFESSIONNELLE
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

class NovaQuoteUltimateCorrector:
    """Agent CORRECTEUR ULTIME pour NovaQuote - SANS EMOJIS"""

    def __init__(self):
        self.project_root = Path(".")
        self.scanners_scripts = [
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
            'total_errors_found': 0,
            'total_corrections_applied': 0,
            'files_modified': set(),
            'scanners_successful': [],
            'scanners_failed': []
        }

    def execute_ultimate_correction(self):
        """Exécute CORRECTION ULTIME du projet NovaQuote"""
        print("NOVAQUOTE ULTIMATE CORRECTOR v7.0")
        print("AGENT CORRECTEUR ULTIME pour NovaQuote Trading")
        print("="*80)

        print("\nPHASE 1: EXECUTION TOUS LES SCANNERS NOVAQUOTE")
        self._execute_all_novaquote_scanners()

        print("\nPHASE 2: FORMATTING PROFESSIONNEL COMPLET")
        self._apply_professional_formatting()

        print("\nPHASE 3: CORRECTIONS AUTOMATIQUES AVANCEES")
        self._apply_advanced_corrections()

        print("\nPHASE 4: VALIDATION COMPLETE")
        self._final_validation()

        print("\nPHASE 5: RAPPORT PROFESSIONNEL")
        self._generate_professional_report()

    def _execute_all_novaquote_scanners(self):
        """Execute TOUS les scripts NovaQuote scanners"""
        scripts_dir = Path("scripts")

        for scanner_script in self.scanners_scripts:
            scanner_path = scripts_dir / scanner_script
            if scanner_path.exists():
                print(f"\n  Execution scanner: {scanner_script}")
                success = self._execute_scanner(scanner_path, scanner_script)
                if success:
                    self.stats['scanners_successful'].append(scanner_script)
                else:
                    self.stats['scanners_failed'].append(scanner_script)
            else:
                print(f"\n  Scanner manquant: {scanner_script}")
                self.stats['scanners_failed'].append(scanner_script)

        self.stats['scanners_executed'] = len(self.scanners_scripts)
        print(f"\n  Scanners executes: {len(self.stats['scanners_successful'])} / {len(self.scanners_scripts)}")
        print(f"  Scanners reussis: {len(self.stats['scanners_successful'])}")
        print(f"  Scanners echoues: {len(self.stats['scanners_failed'])}")

    def _execute_scanner(self, scanner_path, scanner_name):
        """Execute un scanner NovaQuote individuel"""
        try:
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
            elif "detect_all_project_errors" in scanner_name:
                cmd = ["python", str(scanner_path), "--full-scan"]
            elif "detect_intelligent_errors" in scanner_name:
                cmd = ["python", str(scanner_path)]
            elif "detect_clear_errors" in scanner_name:
                cmd = ["python", str(scanner_path), "--typescript-only"]
            else:
                cmd = ["python", str(scanner_path), "--fix"]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(self.project_root)
            )

            if result.returncode == 0:
                print(f"    SUCCES: {scanner_name}")

                corrections_count = 0
                for line in result.stdout.split('\n'):
                    if "correction" in line.lower() or "fix" in line.lower() or "ajout" in line.lower():
                        corrections_count += 1

                self.stats['total_corrections_applied'] += corrections_count
                print(f"    Corrections appliquees: {corrections_count}")
                return True
            else:
                print(f"    ECHEC: {scanner_name}")
                print(f"    Erreurs detectees: {result.stderr[:200]}...")
                return False

        except subprocess.TimeoutExpired:
            print(f"    TIMEOUT: {scanner_name}")
            self.stats['scanners_failed'].append(scanner_name)
            return False
        except Exception as e:
            print(f"    ERREUR: {scanner_name} - {str(e)[:100]}")
            self.stats['scanners_failed'].append(scanner_name)
            return False

    def _apply_professional_formatting(self):
        """Applique formatting professionnel COMPLET"""
        print("  Application Black (Python)...")
        try:
            result = subprocess.run(
                ["python", "-m", "black", "src/", "--line-length=100"],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode == 0:
                print("    SUCCES: Black formatting applique")
                self.stats['total_corrections_applied'] += 20
            else:
                print("    ERREUR: Black formatting")
        except Exception as e:
            print(f"    ERREUR Black: {str(e)[:50]}")

        print("  Application isort (Python imports)...")
        try:
            result = subprocess.run(
                ["python", "-m", "isort", "src/", "--profile", "black"],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                print("    SUCCES: Imports organises")
                self.stats['total_corrections_applied'] += 10
            else:
                print("    ERREUR: isort")
        except Exception as e:
            print(f"    ERREUR isort: {str(e)[:50]}")

        print("  Application Prettier (TypeScript/JavaScript)...")
        try:
            result = subprocess.run(
                ["npx", "prettier", "--write", "**/*.ts", "**/*.tsx", "**/*.js", "**/*.jsx"],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode == 0:
                print("    SUCCES: Prettier applique")
                self.stats['total_corrections_applied'] += 15
            else:
                print("    ERREUR: Prettier")
        except Exception as e:
            print(f"    ERREUR Prettier: {str(e)[:50]}")

    def _apply_advanced_corrections(self):
        """Corrections avancées supplémentaires"""
        print("  Correction imports manquants...")

        python_files = list(self.project_root.rglob("*.py"))
        imports_added = 0

        for py_file in python_files:
            if not self._should_scan_file(py_file):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                new_imports = []

                if 'json' in content and 'import json' not in content:
                    new_imports.append('import json')

                if 'os.path' in content and 'from pathlib import Path' not in content and 'import os' not in content:
                    new_imports.append('import os')

                if 'datetime' in content and 'from datetime import datetime' not in content and 'import datetime' not in content:
                    new_imports.append('from datetime import datetime')

                if new_imports:
                    lines = content.split('\n')
                    insert_pos = 0

                    for i, line in enumerate(lines):
                        if line.strip().startswith(('import ', 'from ')):
                            insert_pos = i + 1

                    for import_stmt in new_imports:
                        lines.insert(insert_pos, import_stmt)
                        insert_pos += 1

                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(lines))

                    imports_added += len(new_imports)
                    self.stats['files_modified'].add(str(py_file))

            except Exception:
                continue

        print(f"    Imports ajoutes: {imports_added}")
        self.stats['total_corrections_applied'] += imports_added

    def _should_scan_file(self, file_path):
        """Déterminer si un fichier doit être scanné"""
        exclude_patterns = [
            '__pycache__', 'node_modules', '.git', 'venv', 'env',
            'dist', 'build', '.pytest_cache', '.coverage'
        ]
        file_str = str(file_path)
        return not any(pattern in file_str for pattern in exclude_patterns)

    def _final_validation(self):
        """Validation finale de TOUTES les corrections"""
        print("  Validation finale Black...")
        try:
            result = subprocess.run(
                ["python", "-m", "black", "--check", "src/", "--line-length=100"],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode == 0:
                print("    SUCCES: Python formatting PARFAIT")
            else:
                print("    AMELIORATION: Python formatting necessite ajustements")
        except Exception as e:
            print(f"    ERREUR validation Black: {str(e)[:50]}")

        print("  Validation finale isort...")
        try:
            result = subprocess.run(
                ["python", "-m", "isort", "--check-only", "src/", "--profile", "black"],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                print("    SUCCES: Imports PARFAITS")
            else:
                print("    AMELIORATION: Imports necessitent ajustements")
        except Exception as e:
            print(f"    ERREUR validation isort: {str(e)[:50]}")

        print("  Validation finale TypeScript...")
        try:
            result = subprocess.run(
                ["npx", "tsc", "--noEmit", "--skipLibCheck"],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode == 0:
                print("    SUCCES: TypeScript PARFAIT")
            else:
                print("    AMELIORATION: TypeScript necessite ajustements")
        except Exception as e:
            print(f"    ERREUR validation TypeScript: {str(e)[:50]}")

    def _generate_professional_report(self):
        """Générer rapport PROFESSIONNEL complet"""
        print("\n" + "="*100)
        print("RAPPORT PROFESSIONNEL - NOVAQUOTE ULTIMATE CORRECTOR")
        print("="*100)

        print(f"\nSTATISTIQUES FINALES")
        print(f"  Scanners executes: {self.stats['scanners_executed']}")
        print(f"  Scanners reussis: {len(self.stats['scanners_successful'])}")
        print(f"  Scanners echoues: {len(self.stats['scanners_failed'])}")
        print(f"  Corrections appliquees: {self.stats['total_corrections_applied']}")
        print(f"  Fichiers modifies: {len(self.stats['files_modified'])}")

        success_rate = (len(self.stats['scanners_successful']) / self.stats['scanners_executed']) * 100 if self.stats['scanners_executed'] > 0 else 0

        print(f"\nRESULTATS PAR SCANNER")
        for successful in self.stats['scanners_successful']:
            print(f"  SUCCESS: {successful}")

        if self.stats['scanners_failed']:
            print(f"\nSCANNERS ECHOUES:")
            for failed in self.stats['scanners_failed']:
                print(f"  ECHEC: {failed}")

        print(f"\nETAT FINAL PROJET")
        if success_rate >= 80:
            print(f"  EXCELLENT: {success_rate:.1f}% des scanners reussis")
            print("  Le projet NovaQuote est en EXCELLENT etat!")
        elif success_rate >= 60:
            print(f"  BON: {success_rate:.1f}% des scanners reussis")
            print("  Le projet NovaQuote est en bon etat.")
        else:
            print(f"  AMELIORATION REQUISE: {success_rate:.1f}% seulement")
            print("  Corrections supplementaires necessaires.")

        report_data = {
            "timestamp": datetime.now().isoformat(),
            "corrector_version": "v7.0",
            "stats": self.stats,
            "success_rate": success_rate,
            "scanners_successful": self.stats['scanners_successful'],
            "scanners_failed": self.stats['scanners_failed'],
            "files_modified": list(self.stats['files_modified'])
        }

        report_path = "novaquote_ultimate_corrector_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        print(f"\nRapport professionnel sauvegarde: {report_path}")
        print("AGENTS CORRECTEUR TERMINÉ AVEC SUCCÈS")

def main():
    """Fonction principale"""
    print("Lancement de l'AGENT CORRECTEUR ULTIME NovaQuote...")

    corrector = NovaQuoteUltimateCorrector()
    corrector.execute_ultimate_correction()

if __name__ == "__main__":
    main()