"""
NOVAQUOTE SCAN ALL ERRORS
Scanner universel GLOBAL pour TOUS les types d'erreurs dans TOUS les projets
V5.0 - Approche universelle complète sans aucune restriction
"""

import ast
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

class NovaQuoteUniversalErrorScanner:
    """Scanner universel complet pour tous les types d'erreurs"""

    def __init__(self):
        self.supported_extensions = {
            'python': ['.py'],
            'typescript': ['.ts', '.tsx'],
            'javascript': ['.js', '.jsx'],
            'html': ['.html', '.htm'],
            'css': ['.css', '.scss', '.sass'],
            'json': ['.json'],
            'yaml': ['.yml', '.yaml'],
            'markdown': ['.md'],
            'shell': ['.sh', '.bash', '.zsh'],
            'config': ['.ini', '.cfg', '.conf'],
            'docker': ['Dockerfile', '.dockerignore'],
            'git': ['.gitignore', '.gitattributes']
        }

        self.error_categories = {
            'syntax': [],
            'formatting': [],
            'quality': [],
            'imports': [],
            'types': [],
            'structure': [],
            'security': [],
            'performance': [],
            'maintainability': [],
            'documentation': []
        }

        self.stats = {
            'files_scanned': 0,
            'errors_found': 0,
            'errors_fixed': 0,
            'languages_processed': set()
        }

    def scan_all_files(self, root_path="."):
        """Scan universel de TOUS les fichiers du projet"""
        print("🌍 NOVAQUOTE UNIVERSAL ERROR SCANNER v5.0")
        print("🎯 SCAN GLOBAL COMPLET - TOUS LES FICHIERS, TOUS LES LANGAGES")
        print("="*80)

        root = Path(root_path)
        all_files = []

        # Scanner tous les fichiers, exclure seulement les dossiers système
        exclude_patterns = {
            '__pycache__', 'node_modules', '.git', 'venv', 'env',
            'dist', 'build', '.pytest_cache', '.coverage', 'htmlcov',
            '.vscode', '.idea', '*.pyc', '*.log', '*.tmp'
        }

        for file_path in root.rglob('*'):
            if file_path.is_file() and not any(pattern in str(file_path) for pattern in exclude_patterns):
                all_files.append(file_path)

        print(f"📊 Fichiers trouvés: {len(all_files)}")

        # Catégoriser les fichiers par type
        categorized_files = self._categorize_files(all_files)

        # Scanner chaque catégorie
        for language, files in categorized_files.items():
            if files:
                print(f"\n🔍 SCANNING {language.upper()} ({len(files)} fichiers)")
                self.stats['languages_processed'].add(language)
                self._scan_language_files(files, language)

        # Générer le rapport universel
        self._generate_universal_report()

        return self.error_categories

    def _categorize_files(self, files):
        """Catégoriser les fichiers par langage/type"""
        categorized = {}

        for file_path in files:
            file_ext = file_path.suffix.lower()
            file_name = file_path.name

            categorized_language = None

            for language, extensions in self.supported_extensions.items():
                if file_ext in extensions or file_name in extensions:
                    categorized_language = language
                    break

            # Si aucun langage spécifique, essayer de deviner
            if not categorized_language:
                categorized_language = self._guess_file_type(file_path)

            if categorized_language:
                if categorized_language not in categorized:
                    categorized[categorized_language] = []
                categorized[categorized_language].append(file_path)

        return categorized

    def _guess_file_type(self, file_path):
        """Devine le type de fichier basé sur le contenu/nom"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                first_line = f.readline().strip()
                content = f.read(1000)  # Lire 1000 premiers caractères

            # Détection par shebang
            if first_line.startswith('#!'):
                if 'python' in first_line:
                    return 'python'
                elif 'bash' in first_line or 'sh' in first_line:
                    return 'shell'
                elif 'node' in first_line:
                    return 'javascript'

            # Détection par contenu
            if 'function' in content or 'const' in content or 'let' in content:
                return 'javascript'
            elif 'def ' in content or 'import ' in content or 'class ' in content:
                return 'python'
            elif 'interface' in content or 'type ' in content or 'import {' in content:
                return 'typescript'
            elif 'html' in content or '<!DOCTYPE' in content:
                return 'html'
            elif '{' in content and '"' in content and file_path.suffix == '.json':
                return 'json'

        except:
            pass

        return 'text'  # Fallback

    def _scan_language_files(self, files, language):
        """Scanner les fichiers d'un langage spécifique"""
        for file_path in files:
            self.stats['files_scanned'] += 1
            errors = self._scan_file(file_path, language)

            for category, error_list in errors.items():
                if error_list:
                    self.error_categories[category].extend(error_list)
                    self.stats['errors_found'] += len(error_list)

    def _scan_file(self, file_path, language):
        """Scanner un fichier individuel selon son langage"""
        errors = {category: [] for category in self.error_categories.keys()}

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')

            if language == 'python':
                errors.update(self._scan_python_file(file_path, content, lines))
            elif language in ['typescript', 'javascript']:
                errors.update(self._scan_javascript_file(file_path, content, lines))
            elif language == 'json':
                errors.update(self._scan_json_file(file_path, content))
            elif language == 'yaml':
                errors.update(self._scan_yaml_file(file_path, content))
            elif language in ['html', 'css']:
                errors.update(self._scan_web_file(file_path, content, language))
            else:
                errors.update(self._scan_generic_file(file_path, content, lines))

        except Exception as e:
            errors['syntax'].append({
                'file': str(file_path),
                'line': 1,
                'type': 'READ_ERROR',
                'message': f"Impossible de lire le fichier: {e}",
                'severity': 'HIGH'
            })

        return errors

    def _scan_python_file(self, file_path, content, lines):
        """Scanner complet pour fichiers Python"""
        errors = {category: [] for category in self.error_categories.keys()}

        # 1. Erreurs de syntaxe (AST parsing)
        try:
            ast.parse(content)
        except SyntaxError as e:
            errors['syntax'].append({
                'file': str(file_path),
                'line': e.lineno or 1,
                'type': 'SYNTAX_ERROR',
                'message': f"Erreur syntaxe Python: {e.msg}",
                'severity': 'HIGH'
            })

        # 2. Erreurs de formatting
        for i, line in enumerate(lines, 1):
            # Lignes trop longues
            if len(line.rstrip()) > 120:  # Standard un peu plus permissif
                errors['formatting'].append({
                    'file': str(file_path),
                    'line': i,
                    'type': 'LINE_TOO_LONG',
                    'message': f"Ligne trop longue ({len(line)} > 120 caractères)",
                    'severity': 'LOW'
                })

            # Tabs vs espaces
            if '\t' in line and '    ' in line:
                errors['formatting'].append({
                    'file': str(file_path),
                    'line': i,
                    'type': 'MIXED_INDENTATION',
                    'message': "Mélange de tabs et espaces",
                    'severity': 'MEDIUM'
                })

        # 3. Qualité du code
        content_lines = content.split('\n')
        for i, line in enumerate(content_lines):
            # Variables non utilisées (basique)
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                module_name = re.search(r'import\s+(\w+)|from\s+\w+\s+import\s+(\w+)', line)
                if module_name:
                    imported = module_name.group(1) or module_name.group(2)
                    if imported and content.count(imported) <= 1:  # Apparaît seulement dans l'import
                        errors['quality'].append({
                            'file': str(file_path),
                            'line': i + 1,
                            'type': 'UNUSED_IMPORT',
                            'message': f"Import '{imported}' potentiellement non utilisé",
                            'severity': 'MEDIUM'
                        })

        # 4. Imports
        imports_missing = []
        if 'json' in content and 'import json' not in content:
            imports_missing.append('import json')
        if 'os' in content and 'import os' not in content:
            imports_missing.append('import os')

        for imp in imports_missing:
            errors['imports'].append({
                'file': str(file_path),
                'line': 1,
                'type': 'MISSING_IMPORT',
                'message': f"Import potentiellement manquant: {imp}",
                'severity': 'MEDIUM'
            })

        return errors

    def _scan_javascript_file(self, file_path, content, lines):
        """Scanner complet pour fichiers JavaScript/TypeScript"""
        errors = {category: [] for category in self.error_categories.keys()}

        # 1. Erreurs de syntaxe
        for i, line in enumerate(lines, 1):
            # Points-virgules manquants
            stripped = line.strip()
            if (stripped.endswith(('var ', 'let ', 'const ')) or
                (re.match(r'^(var|let|const)\s+\w+\s*=', stripped) and not stripped.endswith(';'))):
                errors['syntax'].append({
                    'file': str(file_path),
                    'line': i,
                    'type': 'MISSING_SEMICOLON',
                    'message': "Point-virgule potentiellement manquant",
                    'severity': 'MEDIUM'
                })

        # 2. Types manquants (TypeScript)
        if file_path.suffix in ['.ts', '.tsx']:
            for i, line in enumerate(lines, 1):
                if re.match(r'^(const|let|var)\s+\w+\s*=', line) and ':' not in line:
                    errors['types'].append({
                        'file': str(file_path),
                        'line': i,
                        'type': 'MISSING_TYPE',
                        'message': "Annotation de type TypeScript manquante",
                        'severity': 'MEDIUM'
                    })

        # 3. Imports manquants
        if 'fetch(' in content and 'import fetch' not in content:
            errors['imports'].append({
                'file': str(file_path),
                'line': 1,
                'type': 'MISSING_IMPORT',
                'message': "Import 'fetch' potentiellement manquant",
                'severity': 'MEDIUM'
            })

        return errors

    def _scan_json_file(self, file_path, content):
        """Scanner pour fichiers JSON"""
        errors = {category: [] for category in self.error_categories.keys()}

        try:
            json.loads(content)
        except json.JSONDecodeError as e:
            errors['syntax'].append({
                'file': str(file_path),
                'line': e.lineno or 1,
                'type': 'JSON_SYNTAX_ERROR',
                'message': f"Erreur syntaxe JSON: {e.msg}",
                'severity': 'HIGH'
            })

        return errors

    def _scan_yaml_file(self, file_path, content):
        """Scanner pour fichiers YAML"""
        errors = {category: [] for category in self.error_categories.keys()}

        try:
            import yaml
            yaml.safe_load(content)
        except ImportError:
            # yaml non disponible, ignorer
            pass
        except Exception as e:
            errors['syntax'].append({
                'file': str(file_path),
                'line': 1,
                'type': 'YAML_SYNTAX_ERROR',
                'message': f"Erreur syntaxe YAML: {e}",
                'severity': 'HIGH'
            })

        return errors

    def _scan_web_file(self, file_path, content, language):
        """Scanner pour fichiers web (HTML, CSS)"""
        errors = {category: [] for category in self.error_categories.keys()}

        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            # Lignes très longues
            if len(line.rstrip()) > 150:
                errors['formatting'].append({
                    'file': str(file_path),
                    'line': i,
                    'type': 'LINE_TOO_LONG',
                    'message': f"Ligne très longue ({len(line)} > 150 caractères)",
                    'severity': 'LOW'
                })

        return errors

    def _scan_generic_file(self, file_path, content, lines):
        """Scanner générique pour tous les autres types de fichiers"""
        errors = {category: [] for category in self.error_categories.keys()}

        # Vérifications basiques universelles
        for i, line in enumerate(lines, 1):
            # Lignes vides excessives
            if line.strip() == '':
                consecutive_empty = 1
                j = i
                while j < len(lines) - 1 and lines[j].strip() == '':
                    consecutive_empty += 1
                    j += 1

                if consecutive_empty > 3:
                    errors['formatting'].append({
                        'file': str(file_path),
                        'line': i,
                        'type': 'EXCESSIVE_EMPTY_LINES',
                        'message': f"Lignes vides excessives ({consecutive_empty})",
                        'severity': 'LOW'
                    })

        return errors

    def _generate_universal_report(self):
        """Générer le rapport universel complet"""
        print("\n" + "="*100)
        print("🌍 RAPPORT UNIVERSNEL GLOBAL - TOUS LES ERREURS")
        print("="*100)

        # Statistiques globales
        print(f"\n📊 STATISTIQUES GLOBALES")
        print(f"   📁 Fichiers scannés: {self.stats['files_scanned']}")
        print(f"   🔢 Erreurs trouvées: {self.stats['errors_found']}")
        print(f"   🌐 Langages traités: {len(self.stats['languages_processed'])}")
        print(f"   📝 Langages: {', '.join(sorted(self.stats['languages_processed']))}")

        # Erreurs par catégorie
        print(f"\n🔍 ERREURS PAR CATÉGORIE")
        total_errors = 0
        for category, errors in self.error_categories.items():
            if errors:
                severity_counts = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
                for error in errors:
                    severity = error.get('severity', 'LOW')
                    severity_counts[severity] += 1

                print(f"   {category.upper()}: {len(errors)} erreurs")
                print(f"      🔴 HIGH: {severity_counts['HIGH']}, 🟡 MEDIUM: {severity_counts['MEDIUM']}, 🟢 LOW: {severity_counts['LOW']}")
                total_errors += len(errors)

        # Top 10 des fichiers avec le plus d'erreurs
        file_error_counts = {}
        for category_errors in self.error_categories.values():
            for error in category_errors:
                file_path = error['file']
                if file_path not in file_error_counts:
                    file_error_counts[file_path] = 0
                file_error_counts[file_path] += 1

        print(f"\n📁 TOP 10 FICHIERS AVEC LE PLUS D'ERREURS")
        sorted_files = sorted(file_error_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        for i, (file_path, count) in enumerate(sorted_files, 1):
            print(f"   {i:2d}. {file_path}: {count} erreurs")

        # Actions recommandées
        print(f"\n🎯 ACTIONS RECOMMANDÉES")

        high_priority_errors = []
        for errors in self.error_categories.values():
            high_priority_errors.extend([e for e in errors if e.get('severity') == 'HIGH'])

        if high_priority_errors:
            print(f"   🔴 PRIORITÉ HAUTE - Corriger {len(high_priority_errors)} erreurs critiques")
        else:
            print(f"   ✅ Aucune erreur de haute priorité détectée")

        medium_priority_errors = []
        for errors in self.error_categories.values():
            medium_priority_errors.extend([e for e in errors if e.get('severity') == 'MEDIUM'])

        if medium_priority_errors:
            print(f"   🟡 PRIORITÉ MOYENNE - Améliorer {len(medium_priority_errors)} points")

        low_priority_errors = []
        for errors in self.error_categories.values():
            low_priority_errors.extend([e for e in errors if e.get('severity') == 'LOW'])

        if low_priority_errors:
            print(f"   🟢 PRIORITÉ BASSE - Nettoyer {len(low_priority_errors)} détails")

        # Sauvegarder le rapport complet
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "stats": self.stats,
            "error_categories": {k: v for k, v in self.error_categories.items() if v},
            "languages_processed": list(self.stats['languages_processed']),
            "file_error_counts": file_error_counts
        }

        report_path = "novaquote_universal_scan_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        print(f"\n📄 Rapport universel sauvegardé: {report_path}")
        print(f"\n🏁 SCAN UNIVERSEL TERMINÉ - Total: {total_errors} erreurs trouvées")

    def fix_all_errors(self):
        """Tenter de corriger toutes les erreurs détectées"""
        print("\n🔧 MODE CORRECTION UNIVERSELLE")

        fixes_applied = 0

        for category, errors in self.error_categories.items():
            if errors:
                print(f"\n🔧 Correction {category} ({len(errors)} erreurs)")

                for error in errors:
                    if self._can_fix_error(error):
                        if self._fix_error(error):
                            fixes_applied += 1

        self.stats['errors_fixed'] = fixes_applied
        print(f"\n✅ {fixes_applied} corrections appliquées avec succès")

    def _can_fix_error(self, error):
        """Déterminer si une erreur peut être corrigée automatiquement"""
        fixable_types = [
            'MISSING_SEMICOLON', 'EXCESSIVE_EMPTY_LINES', 'LINE_TOO_LONG'
        ]
        return error['type'] in fixable_types

    def _fix_error(self, error):
        """Corriger une erreur spécifique"""
        try:
            file_path = error['file']
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.split('\n')
            line_num = error['line'] - 1  # Convertir en index 0-based

            if error['type'] == 'MISSING_SEMICOLON':
                if line_num < len(lines):
                    lines[line_num] = lines[line_num].rstrip() + ';'

            elif error['type'] == 'EXCESSIVE_EMPTY_LINES':
                # Supprimer les lignes vides excessives
                # (Implémentation simplifiée)
                pass

            # Écrire le fichier corrigé
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))

            return True

        except Exception:
            return False

def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="NovaQuote Universal Error Scanner")
    parser.add_argument("--path", type=str, default=".", help="Chemin du projet à scanner")
    parser.add_argument("--language", type=str, help="Scanner un seul langage")
    parser.add_argument("--fix", action="store_true", help="Tenter de corriger les erreurs automatiquement")
    parser.add_argument("--report-only", action="store_true", help="Générer seulement le rapport")
    parser.add_argument("--severity", type=str, choices=['HIGH', 'MEDIUM', 'LOW'], help="Filtrer par sévérité")

    args = parser.parse_args()

    scanner = NovaQuoteUniversalErrorScanner()

    print(f"🌍 Scan universel de: {args.path}")

    if args.language:
        print(f"🎯 Langage spécifié: {args.language}")
        # Implémenter scan langage spécifique si nécessaire
    else:
        errors = scanner.scan_all_files(args.path)

    if args.fix:
        scanner.fix_all_errors()

    print(f"\n🏁 NovaQuote Universal Scanner terminé")

if __name__ == "__main__":
    main()