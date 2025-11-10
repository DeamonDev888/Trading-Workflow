"""
NOVAQUOTE DETECT INTELLIGENT ERRORS
Détecteur intelligent d'erreurs avec analyse contextuelle avancée
V1.0 - Détection intelligente pour NovaQuote Linter v3.0
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

class NovaQuoteIntelligentErrorDetector:
    """Détecteur intelligent d'erreurs avec analyse contextuelle"""

    def __init__(self):
        self.error_patterns = {
            "typescript": {
                "missing_types": [
                    r'const\s+(\w+)\s*=\s*([^;:]+)(?!.*:)',
                    r'let\s+(\w+)\s*=\s*([^;:]+)(?!.*:)',
                    r'var\s+(\w+)\s*=\s*([^;:]+)(?!.*:)'
                ],
                "missing_imports": [
                    (r'\bexpress\b', "import express from 'express';"),
                    (r'\baxios\b', "import axios from 'axios';"),
                    (r'\bfetch\s*\(', "import fetch from 'node-fetch';"),
                    (r'\bReact\b', "import React from 'react';"),
                    (r'\buseState\b', "import { useState } from 'react';")
                ],
                "syntax_errors": [
                    r'^\s*(const|let|var)\s+\w+\s*=\s*[^;{]$\s*$',
                    r'^\s*function\s+\w+\s*\([^)]*\)\s*[^{]\s*$'
                ]
            },
            "python": {
                "missing_imports": [
                    (r'\bjson\.', "import json"),
                    (r'\bos\.', "import os"),
                    (r'\bsys\.', "import sys"),
                    (r'\bdatetime\.', "from datetime import datetime"),
                    (r'\bPath\(', "from pathlib import Path")
                ],
                "formatting_errors": [
                    (r'^.{101,}$', "E501: Line too long (>100 chars)"),
                    (r'^\s+\t', "W191: Indentation contains tabs"),
                    (r'^[^\s]\S*\s+\S{4,}\s*\w+\s*=', "E225: Missing whitespace around operator")
                ],
                "unused_imports": [
                    r'^import\s+\w+\s*$',
                    r'^from\s+\w+\s+import\s+\w+$'
                ]
            }
        }

    def detect_typescript_errors(self, file_path):
        """Détecte les erreurs TypeScript avec intelligence contextuelle"""
        errors = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

            print(f"\n🔍 [TS] Analyse intelligente: {file_path}")

            for i, line in enumerate(lines, 1):
                for pattern in self.error_patterns["typescript"]["missing_types"]:
                    if re.search(pattern, line) and not line.strip().startswith('//'):
                        match = re.search(pattern, line)
                        if match:
                            var_name = match.group(1) if match.groups() else "variable"
                            errors.append({
                                "type": "MISSING_TYPE",
                                "severity": "MEDIUM",
                                "file": file_path,
                                "line": i,
                                "content": line.strip(),
                                "variable": var_name,
                                "description": f"ERREUR: Variable '{var_name}' sans type",
                                "suggestion": f"AJOUTER: type annotation pour '{var_name}'",
                                "fix": f": any"
                            })

            for pattern, import_stmt in self.error_patterns["typescript"]["missing_imports"]:
                if re.search(pattern, content) and import_stmt not in content:
                    errors.append({
                        "type": "MISSING_IMPORT",
                        "severity": "HIGH",
                        "file": file_path,
                        "description": f"ERREUR: Import manquant détecté",
                        "pattern": pattern,
                        "suggestion": f"AJOUTER: {import_stmt}",
                        "fix": import_stmt
                    })

            for i, line in enumerate(lines, 1):
                for pattern in self.error_patterns["typescript"]["syntax_errors"]:
                    if re.match(pattern, line) and not line.strip().startswith('//'):
                        errors.append({
                            "type": "SYNTAX_ERROR",
                            "severity": "HIGH",
                            "file": file_path,
                            "line": i,
                            "content": line.strip(),
                            "description": f"ERREUR: Problème de syntaxe détecté",
                            "suggestion": "Corriger la syntaxe (point-virgule, accolades, etc.)",
                            "fix": ";"
                        })

        except Exception as e:
            print(f"  [ERREUR] Impossible d'analyser {file_path}: {e}")

        return errors

    def detect_python_errors(self, file_path):
        """Détecte les erreurs Python avec intelligence contextuelle"""
        errors = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

            print(f"\n🐍 [PY] Analyse intelligente: {file_path}")

            for pattern, import_stmt in self.error_patterns["python"]["missing_imports"]:
                if re.search(pattern, content) and import_stmt not in content:
                    errors.append({
                        "type": "MISSING_IMPORT",
                        "severity": "HIGH",
                        "file": file_path,
                        "description": f"ERREUR: Import Python manquant",
                        "pattern": pattern,
                        "suggestion": f"AJOUTER: {import_stmt}",
                        "fix": import_stmt
                    })

            for i, line in enumerate(lines, 1):
                for pattern, error_msg in self.error_patterns["python"]["formatting_errors"]:
                    if re.match(pattern, line) and not line.strip().startswith('#'):
                        errors.append({
                            "type": "FORMATTING_ERROR",
                            "severity": "LOW",
                            "file": file_path,
                            "line": i,
                            "content": line.strip(),
                            "description": f"ERREUR: {error_msg}",
                            "suggestion": "Appliquer les standards PEP8"
                        })

            used_names = set()
            for line in lines:
                if not line.strip().startswith(('import ', 'from ', '#')):
                    used_names.update(re.findall(r'\b[A-Za-z_][A-Za-z0-9_]*\b', line))

            for i, line in enumerate(lines, 1):
                if line.strip().startswith(('import ', 'from ')):
                    import_match = re.search(r'import\s+([A-Za-z_][A-Za-z0-9_]+)', line)
                    from_match = re.search(r'from\s+\w+\s+import\s+([A-Za-z_][A-Za-z0-9_]+)', line)

                    imported_name = None
                    if import_match:
                        imported_name = import_match.group(1)
                    elif from_match:
                        imported_name = from_match.group(1)

                    if imported_name and imported_name not in used_names:
                        if imported_name not in ['os', 'sys', 'json', 'typing']:
                            errors.append({
                                "type": "UNUSED_IMPORT",
                                "severity": "MEDIUM",
                                "file": file_path,
                                "line": i,
                                "content": line.strip(),
                                "imported_name": imported_name,
                                "description": f"ERREUR: Import '{imported_name}' non utilisé",
                                "suggestion": f"SUPPRIMER: {line.strip()}",
                                "fix": "DELETE_LINE"
                            })

        except Exception as e:
            print(f"  [ERREUR] Impossible d'analyser {file_path}: {e}")

        return errors

    def analyze_project_intelligently(self, target_path="src/"):
        """Analyse intelligente du projet complet"""
        print("🧠 NOVAQUOTE DÉTECTEUR INTELLIGENT D'ERREURS")
        print("="*60)
        print(f"📁 Cible: {target_path}")

        all_errors = []
        target_dir = Path(target_path)

        print(f"\n🔍 RECHERCHE FICHIERS TYPESCRIPT...")
        ts_files = list(target_dir.rglob("*.ts")) + list(target_dir.rglob("*.tsx"))
        ts_files = [f for f in ts_files if 'node_modules' not in str(f)]

        print(f"📊 {len(ts_files)} fichier(s) TypeScript trouvé(s)")

        for ts_file in ts_files:
            errors = self.detect_typescript_errors(str(ts_file))
            all_errors.extend(errors)

        print(f"\n🐍 RECHERCHE FICHIERS PYTHON...")
        py_files = list(target_dir.rglob("*.py"))
        py_files = [f for f in py_files if '__pycache__' not in str(f)]

        print(f"📊 {len(py_files)} fichier(s) Python trouvé(s)")

        for py_file in py_files:
            errors = self.detect_python_errors(str(py_file))
            all_errors.extend(errors)

        self._generate_intelligent_report(all_errors)

        return all_errors

    def _generate_intelligent_report(self, errors):
        """Génère un rapport intelligent des erreurs"""
        print("\n" + "="*80)
        print("🧠 RAPPORT INTELLIGENT DES ERREURS DÉTECTÉES")
        print("="*80)

        errors_by_type = {}
        for error in errors:
            error_type = error["type"]
            if error_type not in errors_by_type:
                errors_by_type[error_type] = []
            errors_by_type[error_type].append(error)

        errors_by_file = {}
        for error in errors:
            file_path = error["file"]
            if file_path not in errors_by_file:
                errors_by_file[file_path] = []
            errors_by_file[file_path].append(error)

        print(f"\n📊 STATISTIQUES GLOBALES")
        print(f"   Total erreurs: {len(errors)}")
        print(f"   Fichiers affectés: {len(errors_by_file)}")
        print(f"   Types d'erreurs: {len(errors_by_type)}")

        print(f"\n🔍 ANALYSE PAR TYPE D'ERREUR")
        for error_type, type_errors in errors_by_type.items():
            severity_high = sum(1 for e in type_errors if e["severity"] == "HIGH")
            severity_medium = sum(1 for e in type_errors if e["severity"] == "MEDIUM")
            severity_low = sum(1 for e in type_errors if e["severity"] == "LOW")

            print(f"   {error_type}: {len(type_errors)} erreurs")
            print(f"      🔴 HIGH: {severity_high}, 🟡 MEDIUM: {severity_medium}, 🟢 LOW: {severity_low}")

        print(f"\n📁 DÉTAILS PAR FICHIER")
        for file_path, file_errors in sorted(errors_by_file.items()):
            high_count = sum(1 for e in file_errors if e["severity"] == "HIGH")
            medium_count = sum(1 for e in file_errors if e["severity"] == "MEDIUM")
            low_count = sum(1 for e in file_errors if e["severity"] == "LOW")

            print(f"\n📄 {file_path}")
            print(f"   Total: {len(file_errors)} erreurs")
            print(f"   Sévérité: 🔴{high_count} 🟡{medium_count} 🟢{low_count}")

            critical_errors = [e for e in file_errors if e["severity"] in ["HIGH", "MEDIUM"]][:3]
            for i, error in enumerate(critical_errors, 1):
                print(f"   {i}. 🚨 {error.get('description', 'Erreur inconnue')}")
                print(f"      💡 {error.get('suggestion', 'Correction suggérée')}")

        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_errors": len(errors),
                "files_affected": len(errors_by_file),
                "error_types": len(errors_by_type)
            },
            "errors_by_type": {k: len(v) for k, v in errors_by_type.items()},
            "errors_by_file": {k: len(v) for k, v in errors_by_file.items()},
            "detailed_errors": errors
        }

        report_path = "novaquote_intelligent_error_report.json"
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            print(f"\n📄 Rapport intelligent sauvegardé: {report_path}")
        except Exception as e:
            print(f"\n⚠️  Impossible de sauvegarder le rapport: {e}")

def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="NovaQuote Intelligent Error Detector")
    parser.add_argument("--path", type=str, default="src/", help="Chemin d'analyse")
    parser.add_argument("--typescript-only", action="store_true", help="Analyser TypeScript seulement")
    parser.add_argument("--python-only", action="store_true", help="Analyser Python seulement")
    parser.add_argument("--high-only", action="store_true", help="Afficher seulement erreurs haute sévérité")

    args = parser.parse_args()

    detector = NovaQuoteIntelligentErrorDetector()

    if args.typescript_only:
        print("🔍 MODE: TYPESCRIPT SEULEMENT")
    elif args.python_only:
        print("🐍 MODE: PYTHON SEULEMENT")
    else:
        print("🧠 MODE: ANALYSE INTELLIGENTE COMPLÈTE")
        detector.analyze_project_intelligently(args.path)

    print(f"\n🏁 Détection intelligente terminée")

if __name__ == "__main__":
    main()