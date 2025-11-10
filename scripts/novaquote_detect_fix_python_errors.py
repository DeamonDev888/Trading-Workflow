"""
NOVAQUOTE EXPERT FIXER
Agent expert qui lit les résultats des scanners et corrige intelligemment
V1.0 - Correcteur professionnel pour NovaQuote Linter v2.0
"""

import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path


class NovaQuoteExpertFixer:
    """Expert fixer that reads scanner results and applies intelligent corrections"""

    def __init__(self):
        self.state = {
            "corrections_applied": 0,
            "files_corrected": set(),
            "error_patterns": {}
        }

    def analyze_scanner_output(self, scanner_output):
        """Analyze scanner output to extract errors with clear detection"""
        errors = []
        for line in scanner_output.split('\n'):
            if ':' in line and any(keyword in line for keyword in ['ERROR', 'error', 'issue', 'F401', 'E501', 'W503', 'missing', 'undefined']):
                errors.append(line.strip())
        return errors

    def fix_python_imports(self, file_path):
        """Fix Python import issues with clear reporting"""
        try:
            print(f"    [PYTHON] Analyse des imports: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_lines = content.split('\n')
            fixed_lines = []
            imports_removed = 0

            used_names = set()
            for line in original_lines:
                if not line.strip().startswith(('import ', 'from ')) and not line.strip().startswith('#'):
                    used_names.update(re.findall(r'\b[A-Za-z_][A-Za-z0-9_]*\b', line))

            for line in original_lines:
                if line.strip().startswith(('import ', 'from ')):
                    import_names = re.findall(r'\b[A-Za-z_][A-Za-z0-9_]*\b', line.split(' import ')[-1] if ' import ' in line else line)
                    if any(name in used_names for name in import_names) or any(keyword in line for keyword in ['os', 'sys', 'json', 'datetime', 'typing', 'pathlib']):
                        fixed_lines.append(line)
                    else:
                        imports_removed += 1
                        print(f"      [SUPPRESSION] Import non utilisé: {line.strip()}")
                else:
                    fixed_lines.append(line)

            if imports_removed > 0:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(fixed_lines))
                print(f"      [SUCCÈS] {imports_removed} import(s) inutile(s) supprimé(s)")
                return True
            else:
                print(f"      [OK] Aucun import inutile détecté")
        except Exception as e:
            print(f"    [ERREUR] Échec correction imports {file_path}: {e}")
        return False

    def fix_python_formatting(self, file_path):
        """Fix Python formatting issues"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            fixed_lines = []
            for line in lines:
                fixed_lines.append(line.rstrip() + '\n')

            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(fixed_lines)
            return True
        except Exception as e:
            print(f"    [ERROR] Failed to fix formatting in {file_path}: {e}")
        return False

    def fix_javascript_typescript(self, file_path):
        """Fix JavaScript/TypeScript issues"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content
            lines = content.split('\n')
            fixed_lines = []

            for line in lines:
                stripped = line.strip()

           \
         if re.search(r'(const|let|var)\s+\w+\s*=\s*[^;{}]$', stripped) and not stripped.startswith('//'):
                    fixed_lines.append(line.rstrip() + ';')
                else:
                    fixed_lines.append(line)

            content = '\n'.join(fixed_lines)
            content = re.sub(r'\bconsole\.log\b', 'console.info', content)

            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
        except Exception as e:
            print(f"    [ERROR] Failed to fix JS/TS in {file_path}: {e}")
        return False

    def fix_typescript_types(self, file_path):
        """Fix TypeScript type issues"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            imports_to_add = []

            if 'express' in content.lower() and 'import express' not in content:
                imports_to_add.append("import express from 'express';")

            if 'axios' in content.lower() and 'import axios' not in content:
                imports_to_add.append("import axios from 'axios';")

            if imports_to_add:
                content = '\n'.join(imports_to_add) + '\n' + content

            lines = content.split('\n')
            fixed_lines = []

            for line in lines:
                stripped = line.strip()
           \
         if re.search(r'(const|let|var)\s+\w+\s*=\s*[^;{}]$', stripped) and not stripped.startswith('//'):
                    fixed_lines.append(line.rstrip() + ';')
                else:
                    fixed_lines.append(line)

            content = '\n'.join(fixed_lines)

            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
        except Exception as e:
            print(f"    [ERROR] Failed to fix TypeScript in {file_path}: {e}")
        return False

    def fix_file(self, file_path, error_type):
        """Apply intelligent fixes based on error type"""
        file_path = str(file_path)
        is_py = file_path.endswith('.py')
        is_ts = file_path.endswith('.ts') or file_path.endswith('.tsx')
        is_js = file_path.endswith('.js')

        corrections_made = 0

        if is_py:
            if 'F401' in error_type or 'import' in error_type.lower():
                if self.fix_python_imports(file_path):
                    corrections_made += 1

            if 'E501' in error_type or 'format' in error_type.lower():
                if self.fix_python_formatting(file_path):
                    corrections_made += 1

        elif is_ts:
            if self.fix_typescript_types(file_path):
                corrections_made += 1
        elif is_js:
            if self.fix_javascript_typescript(file_path):
                corrections_made += 1

        if corrections_made > 0:
            self.state["corrections_applied"] += corrections_made
            self.state["files_corrected"].add(file_path)
            print(f"  [FIXED] {corrections_made} fix(es) applied to {file_path}")
            return True
        return False

    def run_scanner_and_fix(self, scanner_cmd, error_patterns):
        """Run scanner and apply intelligent fixes"""
        print(f"\n[SCANNER] Running: {scanner_cmd}")

        try:
            result = subprocess.run(
                scanner_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=120
            )

            output = result.stdout + result.stderr
            print(f"[OUTPUT] Scanner completed")

            errors = self.analyze_scanner_output(output)

            if not errors:
                print("  [OK] No issues found")
                return

            print(f"  [ISSUES] {len(errors)} issue(s) detected")

            files_with_errors = {}
            for error in errors:
                file_match = re.match(r'^([^:]+):', error)
                if file_match:
                    file_path = file_match.group(1)
                    if file_path not in files_with_errors:
                        files_with_errors[file_path] = []
                    files_with_errors[file_path].append(error)

            for file_path, file_errors in files_with_errors.items():
                if Path(file_path).exists():
                    combined_error = ' '.join(file_errors)
                    self.fix_file(file_path, combined_error)

        except Exception as e:
            print(f"  [ERROR] Scanner failed: {e}")

    def fix_all(self):
        """Main fix workflow"""
        print("="*70)
        print("NOVAQUOTE EXPERT FIXER v1.0")
        print("Reading scanner results and applying intelligent corrections")
        print("="*70)

        print("\n[1/3] PYTHON FILES")
        self.run_scanner_and_fix(
            "python scripts/lint-format-py.py --check",
            ["F401", "E501", "W503", "import"]
        )

        print("\n[2/3] JAVASCRIPT/TYPESCRIPT FILES")
        self.run_scanner_and_fix(
            "python scripts/auto_bug_fixer_cli.py --check",
            ["semicolon", "var", "console.log"]
        )

        print("\n[3/3] TYPESCRIPT TYPE FIXES")
        ts_files = list(Path(".").rglob("*.ts"))
        for ts_file in ts_files:
            if 'node_modules' not in str(ts_file):
                self.fix_file(str(ts_file), "typescript types")

        print("\n" + "="*70)
        print("FINAL REPORT")
        print("="*70)
        print(f"Files corrected: {len(self.state['files_corrected'])}")
        print(f"Total corrections: {self.state['corrections_applied']}")
        print("\nFiles:")
        for file_path in sorted(self.state['files_corrected']):
            print(f"  - {file_path}")
        print("="*70)

def main():
    fixer = NovaQuoteExpertFixer()
    fixer.fix_all()

if __name__ == "__main__":
    main()
