"""
NOVAQUOTE CLEAR ERROR FINDER
Détecte et rapporte clairement les erreurs dans le codebase avec détails précis
V1.0 - Outil de détection claire pour NovaQuote Linter v3.0
"""

import json
import os
import re
import subprocess
from datetime import datetime

class NovaQuoteClearErrorFinder:
    """Tool that finds and clearly reports errors in codebase"""

    def __init__(self):
        self.errors_found = {}
        self.summary = {
            "total_errors": 0,
            "files_with_errors": 0,
            "error_types": {}
        }

    def run_typescript_check(self):
        """Run TypeScript check and extract errors clearly"""
        print("\n" + "="*60)
        print("VÉRIFICATION TYPESCRIPT - DÉTECTION CLAIRE")
        print("="*60)

        ts_errors = []

        try:
            result = subprocess.run(
                ["npx", "tsc", "--noEmit"],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                for line in result.stderr.split('\n'):
                    if ':' in line and 'error' in line.lower():
                        ts_errors.append(self._parse_ts_error(line))
        except:
            print("  [AVERTISSEMENT] TypeScript compiler non disponible")

        try:
            result = subprocess.run(
                ["npx", "eslint", ".", "--ext", ".ts,.tsx", "--format", "compact"],
                capture_output=True,
                text=True,
                timeout=60
            )

            for line in result.stdout.split('\n'):
                if ':' in line and 'error' in line:
                    ts_errors.append(self._parse_eslint_error(line))
        except:
            print("  [AVERTISSEMENT] ESLint non disponible")

        return ts_errors

    def run_python_check(self):
        """Run Python check and extract errors clearly"""
        print("\n" + "="*60)
        print("VÉRIFICATION PYTHON - DÉTECTION CLAIRE")
        print("="*60)

        py_errors = []

        try:
            result = subprocess.run(
                ["flake8", "src/", "--format=default"],
                capture_output=True,
                text=True,
                timeout=60
            )

            for line in result.stdout.split('\n'):
                if ':' in line and any(code in line for code in ['F401', 'E501', 'W503', 'E999', 'F821']):
                    py_errors.append(self._parse_flake8_error(line))
        except:
            print("  [AVERTISSEMENT] Flake8 non disponible")

        try:
            result = subprocess.run(
                ["mypy", "src/", "--ignore-missing-imports", "--show-error-codes"],
                capture_output=True,
                text=True,
                timeout=60
            )

            for line in result.stdout.split('\n'):
                if ':' in line and 'error' in line.lower():
                    py_errors.append(self._parse_mypy_error(line))
        except:
            print("  [AVERTISSEMENT] MyPy non disponible")

        return py_errors

    def _parse_ts_error(self, line):
        """Parse TypeScript compiler error"""
        try:
            parts = line.split(':')
            if len(parts) >= 4:
                file_path = parts[0]
                line_num = parts[1]
                error_code = parts[2].strip()
                error_msg = ':'.join(parts[3:]).strip()

                return {
                    "type": "TYPESCRIPT_ERROR",
                    "severity": "HIGH",
                    "file": file_path,
                    "line": line_num,
                    "code": error_code,
                    "message": error_msg,
                    "description": f"ERREUR TS{error_code}: {error_msg}",
                    "suggestion": self._get_ts_suggestion(error_code, error_msg)
                }
        except:
            pass
        return None

    def _parse_eslint_error(self, line):
        """Parse ESLint error"""
        try:
            parts = line.split(':')
            if len(parts) >= 3:
                file_path = parts[0]
                line_num = parts[1]
                error_msg = ':'.join(parts[2:]).strip()

                return {
                    "type": "ESLINT_ERROR",
                    "severity": "MEDIUM",
                    "file": file_path,
                    "line": line_num,
                    "message": error_msg,
                    "description": f"ERREUR ESLINT: {error_msg}",
                    "suggestion": self._get_eslint_suggestion(error_msg)
                }
        except:
            pass
        return None

    def _parse_flake8_error(self, line):
        """Parse Flake8 error"""
        try:
            parts = line.split(':')
            if len(parts) >= 4:
                file_path = parts[0]
                line_num = parts[1]
                col_num = parts[2]
                error_code = parts[3].strip()
                error_msg = ':'.join(parts[4:]).strip() if len(parts) > 4 else ""

                return {
                    "type": "FLAKE8_ERROR",
                    "severity": "MEDIUM",
                    "file": file_path,
                    "line": line_num,
                    "column": col_num,
                    "code": error_code,
                    "message": error_msg,
                    "description": f"ERREUR FLAKE8 {error_code}: {error_msg}",
                    "suggestion": self._get_flake8_suggestion(error_code)
                }
        except:
            pass
        return None

    def _parse_mypy_error(self, line):
        """Parse MyPy error"""
        try:
            if ':' in line and 'error' in line.lower():
                parts = line.split(':')
                if len(parts) >= 3:
                    file_path = parts[0]
                    line_num = parts[1]
                    error_msg = ':'.join(parts[2:]).strip()

                    return {
                        "type": "MYPY_ERROR",
                        "severity": "HIGH",
                        "file": file_path,
                        "line": line_num,
                        "message": error_msg,
                        "description": f"ERREUR MYPY: {error_msg}",
                        "suggestion": "Ajouter des annotations de type ou corriger les types incompatibles"
                    }
        except:
            pass
        return None

    def _get_ts_suggestion(self, code, msg):
        """Get TypeScript fix suggestion"""
        suggestions = {
            "2304": "Ajouter l'import manquant ou déclarer la variable",
            "2339": "Vérifier la propriété de l'objet ou ajouter une déclaration de type",
            "7006": "Ajouter une annotation de type explicite",
            "2322": "Corriger le type ou ajouter une conversion de type"
        }
        return suggestions.get(code.strip(), "Vérifier la syntaxe et les types")

    def _get_eslint_suggestion(self, msg):
        """Get ESLint fix suggestion"""
        if "semicolon" in msg.lower():
            return "Ajouter un point-virgule à la fin de la ligne"
        elif "undefined" in msg.lower():
            return "Déclarer la variable ou ajouter un import"
        elif "unused" in msg.lower():
            return "Supprimer la variable non utilisée"
        else:
            return "Appliquer les conventions de code ESLint"

    def _get_flake8_suggestion(self, code):
        """Get Flake8 fix suggestion"""
        suggestions = {
            "F401": "Supprimer l'import non utilisé",
            "E501": "Raccourcir la ligne (max 100 caractères)",
            "W503": "Déplacer l'opérateur avant le saut de ligne",
            "E999": "Corriger la syntaxe Python invalide",
            "F821": "Définir la variable ou ajouter un import"
        }
        return suggestions.get(code, "Appliquer les standards PEP8")

    def analyze_files(self):
        """Main analysis function"""
        print("NOVAQUOTE CLEAR ERROR FINDER v1.0")
        print("Détection claire et précise des erreurs")

        ts_errors = [e for e in self.run_typescript_check() if e]

        py_errors = [e for e in self.run_python_check() if e]

        all_errors = ts_errors + py_errors

        files_with_errors = {}
        for error in all_errors:
            file_path = error["file"]
            if file_path not in files_with_errors:
                files_with_errors[file_path] = []
            files_with_errors[file_path].append(error)

        self._generate_report(files_with_errors)

        return files_with_errors

    def _generate_report(self, files_with_errors):
        """Generate clear error report"""
        print("\n" + "="*80)
        print("RAPPORT D'ERREURS CLAIR ET PRÉCIS")
        print("="*80)

        total_errors = 0
        total_files = len(files_with_errors)

        for file_path, errors in files_with_errors.items():
            print(f"\n📁 FICHIER: {file_path}")
            print(f"   {len(errors)} erreur(s) trouvée(s)")
            print("-" * 50)

            for error in errors:
                total_errors += 1

                print(f"\n   🚨 ERREUR #{total_errors}")
                print(f"   Type: {error['type']}")
                print(f"   Sévérité: {error['severity']}")
                print(f"   Ligne: {error.get('line', 'N/A')}")
                if 'column' in error:
                    print(f"   Colonne: {error['column']}")
                if 'code' in error:
                    print(f"   Code: {error['code']}")
                print(f"   Message: {error['description']}")
                print(f"   💡 SUGGESTION: {error['suggestion']}")

        print("\n" + "="*80)
        print("RÉSUMÉ GLOBAL")
        print("="*80)
        print(f"📊 Total fichiers avec erreurs: {total_files}")
        print(f"🔢 Total erreurs détectées: {total_errors}")

        if total_errors == 0:
            print("✅ PARFAIT! Aucune erreur détectée dans le codebase")
        else:
            print(f"⚠️  {total_errors} erreur(s) à corriger")

        report_path = "novaquote_error_report.json"
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_files": total_files,
                "total_errors": total_errors
            },
            "files": files_with_errors
        }

        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            print(f"📄 Rapport détaillé sauvegardé: {report_path}")
        except Exception as e:
            print(f"  [AVERTISSEMENT] Impossible de sauvegarder le rapport: {e}")

def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="NovaQuote Clear Error Finder")
    parser.add_argument("--typescript-only", action="store_true", help="Analyser seulement TypeScript")
    parser.add_argument("--python-only", action="store_true", help="Analyser seulement Python")
    parser.add_argument("--output", type=str, help="Fichier de sortie du rapport")

    args = parser.parse_args()

    finder = NovaQuoteClearErrorFinder()

    if args.typescript_only:
        print("\n⚡ MODE: TYPESCRIPT SEULEMENT")
        errors = finder.run_typescript_check()
    elif args.python_only:
        print("\n⚡ MODE: PYTHON SEULEMENT")
        errors = finder.run_python_check()
    else:
        print("\n⚡ MODE: ANALYSE COMPLÈTE")
        errors = finder.analyze_files()

    print(f"\n🏁 Analyse terminée")

if __name__ == "__main__":
    main()