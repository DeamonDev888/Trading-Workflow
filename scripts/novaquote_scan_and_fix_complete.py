"""
NOVAQUOTE SCAN AND FIX COMPLETE
Scan COMPLET et correction AUTOMATIQUE de TOUT le projet NovaQuote
Script unifié pour éviter les erreurs de corrections multiples
"""

import ast
import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path

class NovaQuoteCompleteScanner:
    """Scanner COMPLET et correction unifiée du projet NovaQuote"""

    def __init__(self):
        self.project_root = Path(".")
        self.errors_found = {}
        self.corrections_applied = []
        self.stats = {
            'files_scanned': 0,
            'python_errors': 0,
            'typescript_errors': 0,
            'formatting_errors': 0,
            'corrections_made': 0
        }

    def scan_and_fix_complete_project(self):
        """Scan COMPLET et correction AUTOMATIQUE"""
        print("NOVAQUOTE COMPLETE SCANNER & FIXER")
        print("Scan et correction COMPLET du projet NovaQuote")
        print("="*80)

        print("\nPHASE 1: SCAN PYTHON COMPLET")
        python_errors = self._scan_python_files()
        self.errors_found['python'] = python_errors

        print("\nPHASE 2: SCAN TYPESCRIPT COMPLET")
        typescript_errors = self._scan_typescript_files()
        self.errors_found['typescript'] = typescript_errors

        print("\nPHASE 3: SCAN JAVASCRIPT COMPLET")
        javascript_errors = self._scan_javascript_files()
        self.errors_found['javascript'] = javascript_errors

        print("\nPHASE 4: CORRECTION AUTOMATIQUE UNIFIEE")
        self._apply_automatic_corrections()

        print("\nPHASE 5: VALIDATION FINALE")
        self._validate_corrections()

        self._generate_final_report()

    def _scan_python_files(self):
        """Scan TOUS les fichiers Python"""
        python_files = list(self.project_root.rglob("*.py"))
        python_files = [f for f in python_files if self._should_scan_file(f)]

        print(f"   {len(python_files)} fichiers Python trouvés")

        all_python_errors = []

        for py_file in python_files:
            self.stats['files_scanned'] += 1
            errors = self._scan_single_python_file(py_file)
            if errors:
                all_python_errors.extend(errors)
                self.stats['python_errors'] += len(errors)

        print(f"   {len(all_python_errors)} erreurs Python détectées")
        return all_python_errors

    def _scan_typescript_files(self):
        """Scan TOUS les fichiers TypeScript"""
        ts_files = list(self.project_root.rglob("*.ts")) + list(self.project_root.rglob("*.tsx"))
        ts_files = [f for f in ts_files if self._should_scan_file(f)]

        print(f"   {len(ts_files)} fichiers TypeScript trouvés")

        all_ts_errors = []

        for ts_file in ts_files:
            self.stats['files_scanned'] += 1
            errors = self._scan_single_typescript_file(ts_file)
            if errors:
                all_ts_errors.extend(errors)
                self.stats['typescript_errors'] += len(errors)

        print(f"   {len(all_ts_errors)} erreurs TypeScript détectées")
        return all_ts_errors

    def _scan_javascript_files(self):
        """Scan TOUS les fichiers JavaScript"""
        js_files = list(self.project_root.rglob("*.js")) + list(self.project_root.rglob("*.jsx"))
        js_files = [f for f in js_files if self._should_scan_file(f)]

        print(f"   {len(js_files)} fichiers JavaScript trouvés")

        all_js_errors = []

        for js_file in js_files:
            self.stats['files_scanned'] += 1
            errors = self._scan_single_javascript_file(js_file)
            if errors:
                all_js_errors.extend(errors)

        print(f"   {len(all_js_errors)} erreurs JavaScript détectées")
        return all_js_errors

    def _should_scan_file(self, file_path):
        """Déterminer si un fichier doit être scanné"""
        exclude_patterns = [
            '__pycache__', 'node_modules', '.git', 'venv', 'env',
            'dist', 'build', '.pytest_cache', '.coverage', 'htmlcov'
        ]

        file_str = str(file_path)
        return not any(pattern in file_str for pattern in exclude_patterns)

    def _scan_single_python_file(self, file_path):
        """Scan individuel d'un fichier Python"""
        errors = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

            try:
                ast.parse(content)
            except SyntaxError as e:
                errors.append({
                    'file': str(file_path),
                    'line': e.lineno or 1,
                    'type': 'SYNTAX_ERROR',
                    'message': f"Erreur syntaxe Python: {e.msg}",
                    'severity': 'HIGH',
                    'auto_fixable': False
                })

            for i, line in enumerate(lines, 1):
                if len(line.rstrip()) > 100:
                    errors.append({
                        'file': str(file_path),
                        'line': i,
                        'type': 'LINE_TOO_LONG',
                        'message': f"Ligne trop longue ({len(line)} > 100 caractères)",
                        'severity': 'LOW',
                        'auto_fixable': True,
                        'fix_function': self._fix_long_line
                    })

                if '\t' in line and '    ' in line:
                    errors.append({
                        'file': str(file_path),
                        'line': i,
                        'type': 'MIXED_INDENTATION',
                        'message': "Mélange de tabs et espaces",
                        'severity': 'MEDIUM',
                        'auto_fixable': True,
                        'fix_function': self._fix_mixed_indentation
                    })

            if 'json' in content and 'import json' not in content:
                errors.append({
                    'file': str(file_path),
                    'line': 1,
                    'type': 'MISSING_IMPORT',
                    'message': "Import 'json' manquant",
                    'severity': 'MEDIUM',
                    'auto_fixable': True,
                    'fix_function': self._add_missing_import,
                    'fix_args': {'import_statement': 'import json'}
                })

            lines_to_remove = []
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith('import ') or stripped.startswith('from '):
                    if self._is_import_unused(stripped, content):
                        errors.append({
                            'file': str(file_path),
                            'line': i + 1,
                            'type': 'UNUSED_IMPORT',
                            'message': f"Import non utilisé: {stripped}",
                            'severity': 'MEDIUM',
                            'auto_fixable': True,
                            'fix_function': self._remove_unused_import,
                            'fix_args': {'line_number': i + 1}
                        })

        except Exception as e:
            errors.append({
                'file': str(file_path),
                'line': 1,
                'type': 'SCAN_ERROR',
                'message': f"Erreur scan fichier: {e}",
                'severity': 'MEDIUM',
                'auto_fixable': False
            })

        return errors

    def _scan_single_typescript_file(self, file_path):
        """Scan individuel d'un fichier TypeScript"""
        errors = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

            for i, line in enumerate(lines, 1):
                stripped = line.strip()

                if stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
                    continue

                if re.match(r'^(const|let|var)\s+\w+\s*=', stripped) and ':' not in stripped:
                    errors.append({
                        'file': str(file_path),
                        'line': i,
                        'type': 'MISSING_TYPE',
                        'message': "Variable sans annotation de type",
                        'severity': 'MEDIUM',
                        'auto_fixable': True,
                        'fix_function': self._add_type_annotation,
                        'fix_args': {'line_number': i}
                    })

                if re.search(r'(const|let|var)\s+\w+\s*=[^;{]$', stripped):
                    errors.append({
                        'file': str(file_path),
                        'line': i,
                        'type': 'MISSING_SEMICOLON',
                        'message': "Point-virgule manquant",
                        'severity': 'MEDIUM',
                        'auto_fixable': True,
                        'fix_function': self._add_semicolon,
                        'fix_args': {'line_number': i}
                    })

                if 'express' in content.lower() and 'import express' not in content:
                    errors.append({
                        'file': str(file_path),
                        'line': 1,
                        'type': 'MISSING_IMPORT',
                        'message': "Import 'express' manquant",
                        'severity': 'MEDIUM',
                        'auto_fixable': True,
                        'fix_function': self._add_ts_import,
                        'fix_args': {'import_statement': "import express from 'express';"}
                    })

        except Exception as e:
            errors.append({
                'file': str(file_path),
                'line': 1,
                'type': 'SCAN_ERROR',
                'message': f"Erreur scan fichier: {e}",
                'severity': 'MEDIUM',
                'auto_fixable': False
            })

        return errors

    def _scan_single_javascript_file(self, file_path):
        """Scan individuel d'un fichier JavaScript"""
        errors = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

            for i, line in enumerate(lines, 1):
                stripped = line.strip()

                if stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
                    continue

                if re.search(r'(const|let|var)\s+\w+\s*=[^;{]$', stripped):
                    errors.append({
                        'file': str(file_path),
                        'line': i,
                        'type': 'MISSING_SEMICOLON',
                        'message': "Point-virgule manquant",
                        'severity': 'MEDIUM',
                        'auto_fixable': True,
                        'fix_function': self._add_semicolon,
                        'fix_args': {'line_number': i}
                    })

                if 'console.log' in line:
                    errors.append({
                        'file': str(file_path),
                        'line': i,
                        'type': 'CONSOLE_LOG',
                        'message': "Utiliser console.info au lieu de console.log",
                        'severity': 'LOW',
                        'auto_fixable': True,
                        'fix_function': self._replace_console_log,
                        'fix_args': {'line_number': i}
                    })

        except Exception as e:
            errors.append({
                'file': str(file_path),
                'line': 1,
                'type': 'SCAN_ERROR',
                'message': f"Erreur scan fichier: {e}",
                'severity': 'MEDIUM',
                'auto_fixable': False
            })

        return errors

    def _is_import_unused(self, import_line, full_content):
        """Vérifier si un import est utilisé"""
        if import_line.startswith('import '):
            imported_name = import_line.split()[1].split(',')[0].split(' as ')[0]
        elif import_line.startswith('from '):
            parts = import_line.split()
            if 'import' in parts:
                import_idx = parts.index('import')
                imported_name = parts[import_idx + 1].split(',')[0].split(' as ')[0]
            else:
                return False
        else:
            return False

        return imported_name not in full_content.replace(import_line, '')

    def _apply_automatic_corrections(self):
        """Appliquer TOUTES les corrections automatiques"""
        print("   Application des corrections automatiques...")

        all_errors = []
        for category, errors in self.errors_found.items():
            all_errors.extend(errors)

        errors_by_file = {}
        for error in all_errors:
            if error.get('auto_fixable', False):
                file_path = error['file']
                if file_path not in errors_by_file:
                    errors_by_file[file_path] = []
                errors_by_file[file_path].append(error)

        corrections_count = 0
        for file_path, file_errors in errors_by_file.items():
            if self._fix_file_unified(file_path, file_errors):
                corrections_count += len(file_errors)
                self.corrections_applied.extend(file_errors)

        self.stats['corrections_made'] = corrections_count
        print(f"   {corrections_count} corrections appliquées sur {len(errors_by_file)} fichiers")

    def _fix_file_unified(self, file_path, errors):
        """Correction unifiée d'un fichier avec TOUTES les erreurs"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            errors.sort(key=lambda x: x['line'], reverse=True)

            corrections_made = 0
            for error in errors:
                if self._apply_single_fix(lines, error):
                    corrections_made += 1

            if corrections_made > 0:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                return True

        except Exception as e:
            print(f"   Erreur correction {file_path}: {e}")

        return False

    def _apply_single_fix(self, lines, error):
        """Appliquer une correction individuelle"""
        try:
            line_idx = error['line'] - 1  # Convertir en index 0-based
            if 0 <= line_idx < len(lines):
                fix_function = error['fix_function']
                fix_args = error.get('fix_args', {})

                if fix_function(lines, line_idx, **fix_args):
                    return True
        except Exception as e:
            print(f"   Erreur application fix: {e}")

        return False

    def _fix_long_line(self, lines, line_idx):
        """Corriger une ligne trop longue"""
        if line_idx < len(lines):
            line = lines[line_idx]
            if len(line.rstrip()) > 100:
                if ' + ' in line:
                    parts = line.split(' + ')
                    if len(parts) > 1:
                        lines[line_idx] = parts[0].rstrip() + '\n'
                        for i, part in enumerate(parts[1:], 1):
                            indent = ' ' * len(parts[0])
                            lines.insert(line_idx + i, f'{indent}+ {part}\n')
                        return True
        return False

    def _fix_mixed_indentation(self, lines, line_idx):
        """Corriger indentation mixte"""
        if line_idx < len(lines):
            lines[line_idx] = lines[line_idx].replace('\t', '    ')
            return True
        return False

    def _add_missing_import(self, lines, line_idx, import_statement):
        """Ajouter un import manquant"""
        import_idx = 0
        for i, line in enumerate(lines):
            if line.strip().startswith(('import ', 'from ')):
                import_idx = i

        lines.insert(import_idx + 1, import_statement + '\n')
        return True

    def _add_ts_import(self, lines, line_idx, import_statement):
        """Ajouter un import TypeScript"""
        return self._add_missing_import(lines, line_idx, import_statement)

    def _remove_unused_import(self, lines, line_idx, line_number):
        """Supprimer un import non utilisé"""
        if 0 <= line_idx < len(lines):
            del lines[line_idx]
            return True
        return False

    def _add_type_annotation(self, lines, line_idx, line_number):
        """Ajouter une annotation de type"""
        if line_idx < len(lines):
            line = lines[line_idx]
            if 'const' in line or 'let' in line or 'var' in line:
                if '=' in line and ':' not in line:
                    lines[line_idx] = line.rstrip() + ': any;\n'
                    return True
        return False

    def _add_semicolon(self, lines, line_idx, line_number):
        """Ajouter un point-virgule"""
        if line_idx < len(lines):
            line = lines[line_idx]
            if not line.rstrip().endswith(';') and not line.strip().startswith('//'):
                lines[line_idx] = line.rstrip() + ';\n'
                return True
        return False

    def _replace_console_log(self, lines, line_idx, line_number):
        """Remplacer console.log par console.info"""
        if line_idx < len(lines):
            lines[line_idx] = lines[line_idx].replace('console.log', 'console.info')
            return True
        return False

    def _validate_corrections(self):
        """Valider que les corrections ont bien été appliquées"""
        print("   Validation des corrections...")

        try:
            result = subprocess.run(
                ['python', '-m', 'black', '--check', 'src/', '--line-length=100'],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                print("   Python formatting valide avec Black")
            else:
                print("   Certains fichiers Python nécessitent encore du formatting")
        except Exception as e:
            print(f"   Validation Black impossible: {e}")

    def _generate_final_report(self):
        """Générer le rapport final complet"""
        print("\n" + "="*100)
        print("RAPPORT FINAL COMPLET - NOVAQUOTE PROJECT")
        print("="*100)

        total_errors = sum(len(errors) for errors in self.errors_found.values())

        print(f"\nSTATISTIQUES FINALES")
        print(f"   Fichiers scannés: {self.stats['files_scanned']}")
        print(f"   Erreurs détectées: {total_errors}")
        print(f"   Corrections appliquées: {self.stats['corrections_made']}")

        print(f"\nDETAIL PAR LANGAGE")
        for language, errors in self.errors_found.items():
            if errors:
                fixable = sum(1 for e in errors if e.get('auto_fixable', False))
                print(f"   {language.upper()}: {len(errors)} erreurs ({fixable} corrigeables)")

        print(f"\nETAT FINAL")
        if self.stats['corrections_made'] > 0:
            print(f"   {self.stats['corrections_made']} corrections automatiques appliquées")
            print(f"   Amélioration significative de la qualité du code")
        else:
            print(f"   Le projet est déjà en bon état")

        report_data = {
            "timestamp": datetime.now().isoformat(),
            "project": "NovaQuote Trading",
            "stats": self.stats,
            "errors_found": {k: v for k, v in self.errors_found.items() if v},
            "corrections_applied": self.corrections_applied
        }

        report_path = "novaquote_complete_scan_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        print(f"\nRapport complet sauvegardé: {report_path}")
        print(f"\nSCAN ET CORRECTION COMPLETS TERMINÉS")

def main():
    """Main function"""
    scanner = NovaQuoteCompleteScanner()
    scanner.scan_and_fix_complete_project()

if __name__ == "__main__":
    main()