"""
TYPESCRIPT ERROR FIXER
Corrige les erreurs de compilation TypeScript (types, imports, fonctions)
V1.0 - Complément à NovaQuote Linter v2.0
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

STATE_FILE = ".novaquote_typescript_state.json"

def load_state():
    """Load persistent state for TypeScript fixes"""
    if Path(STATE_FILE).exists():
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {
        "version": "1.0",
        "fixes": {},
        "statistics": {
            "types_fixed": 0,
            "imports_fixed": 0,
            "functions_fixed": 0,
            "files_fixed": []
        }
    }

def save_state(state):
    """Save TypeScript state"""
    try:
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"  [WARN] Could not save TypeScript state: {e}")

def analyze_typescript_errors(file_path):
    """Analyze TypeScript file for common errors with clear error detection"""
    errors = {
        "missing_types": [],
        "missing_imports": [],
        "undefined_functions": [],
        "missing_semicolons": [],
        "syntax_errors": [],
        "type_errors": [],
        "import_errors": [],
        "other_issues": []
    }

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

         \
       if re.search(r'(const|let|var)\s+\w+\s*=\s*[^;]+(?!:\s*\w+)', line) and not stripped.endswith(';'):
                if not any(x in line for x in ['//', '/*', '*']):
                    errors["missing_types"].append({
                        "line": i,
                        "content": line.strip(),
                        "issue": "variable without type annotation"
                    })

            if 'import' not in line and 'from' not in line and not line.startswith('//'):
                if 'express' in line.lower() and 'import express' not in content and 'Express' not in line:
                    errors["missing_imports"].append({
                        "line": i,
                        "content": line.strip(),
                        "issue": "ERREUR: Import 'express' manquant",
                        "suggestion": "AJOUTER: import express from 'express';",
                        "error_type": "IMPORT_ERROR",
                        "severity": "HIGH"
                    })

                if 'axios' in line.lower() and 'import axios' not in content and not line.startswith('//'):
                    errors["missing_imports"].append({
                        "line": i,
                        "content": line.strip(),
                        "issue": "ERREUR: Import 'axios' manquant",
                        "suggestion": "AJOUTER: import axios from 'axios';",
                        "error_type": "IMPORT_ERROR",
                        "severity": "HIGH"
                    })

                if 'fetch(' in line and 'import' not in content and 'node-fetch' not in content:
                    errors["missing_imports"].append({
                        "line": i,
                        "content": line.strip(),
                        "issue": "ERREUR: Import 'node-fetch' manquant pour fetch()",
                        "suggestion": "AJOUTER: import fetch from 'node-fetch';",
                        "error_type": "IMPORT_ERROR",
                        "severity": "HIGH"
                    })

            if re.search(r'(const|let|var)\s+\w+\s*=\s*[^;{}]$', stripped) and not stripped.startswith('//'):
                errors["missing_semicolons"].append({
                    "line": i,
                    "content": line.strip(),
                    "issue": "ERREUR: Point-virgule manquant",
                    "suggestion": "AJOUTER: ; à la fin de la ligne",
                    "error_type": "SYNTAX_ERROR",
                    "severity": "MEDIUM"
                })

    except Exception as e:
        print(f"  [ERROR] Could not analyze {file_path}: {e}")

    return errors

def fix_typescript_file(file_path, state=None, dry_run=False):
    """Fix TypeScript errors in file with clear fix reporting"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        lines = content.split('\n')
        fixes_made = 0
        fixes_details = []

        print(f"\n  [ANALYSE] Fichier: {file_path}")

        imports_to_add = []

        if 'express' in content.lower() and 'import express' not in content:
            imports_to_add.append("import express from 'express';")
            fixes_details.append("AJOUT: import express")

        if 'axios' in content.lower() and 'import axios' not in content:
            imports_to_add.append("import axios from 'axios';")
            fixes_details.append("AJOUT: import axios")

        if 'fetch(' in content and 'node-fetch' not in content and 'import fetch' not in content:
            imports_to_add.append("import fetch from 'node-fetch';")
            fixes_details.append("AJOUT: import fetch")

        if imports_to_add:
            import_section_end = 0
            for i, line in enumerate(lines):
                if line.strip().startswith('import '):
                    import_section_end = i

            for i, import_line in enumerate(imports_to_add):
                lines.insert(import_section_end + i + 1, import_line)
                fixes_made += 1
            print(f"    [CORRECTION] {len(imports_to_add)} import(s) ajouté(s)")

        semicolon_fixes = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
                continue

            if re.search(r'(const|let|var)\s+\w+\s*=\s*[^;{}]$', stripped):
                lines[i] = line.rstrip() + ';'
                fixes_made += 1
                semicolon_fixes += 1

        if semicolon_fixes > 0:
            print(f"    [CORRECTION] {semicolon_fixes} point(s)-virgule(s) ajouté(s)")

        type_fixes = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('//') or ':' in line or stripped.startswith('import'):
                continue

            if re.match(r'^(const|let|var)\s+\w+\s*=\s*', stripped):
                if ':' not in stripped:
                    if not line.strip().endswith(';'):
                        lines[i] = line.rstrip() + ': any;'
                    else:
                        lines[i] = line.rstrip()[:-1] + ': any;'
                    fixes_made += 1
                    type_fixes += 1

        if type_fixes > 0:
            print(f"    [CORRECTION] {type_fixes} type(s) ajouté(s)")

        for i, line in enumerate(lines):
            stripped = line.strip()
          \
      if stripped.startswith('//') or ':' in line or stripped.startswith('import'):
                continue

            if re.match(r'^(const|let|var)\s+\w+\s*=\s*', stripped):
                if not line.strip().endswith(';'):
                    lines[i] = line.rstrip() + ': any;'
                else:
                    lines[i] = line.rstrip()[:-1] + ': any;'
                fixes_made += 1

        if fixes_made > 0:
            print(f"    [DÉTAIL] {fixes_made} correction(s) totale(s):")
            for detail in fixes_details:
                print(f"      - {detail}")

            if not dry_run:
                fixed_content = '\n'.join(lines)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                print(f"  [SUCCÈS] {fixes_made} correction(s) appliquée(s) à {file_path}")

                if state:
                    state["fixes"][file_path] = {
                        "timestamp": datetime.now().isoformat(),
                        "fixes_applied": fixes_made,
                        "fixes_details": fixes_details
                    }
                    state["statistics"]["files_fixed"].append(file_path)
                    state["statistics"]["types_fixed"] += fixes_made
                    save_state(state)
            else:
                print(f"  [DRY-RUN] {fixes_made} correction(s) SERAIT appliquée(s) à {file_path}")
        else:
            print(f"    [OK] Aucune correction nécessaire pour {file_path}")

        return fixes_made

    except Exception as e:
        print(f"  [ERROR] Could not fix {file_path}: {e}")
        return 0

def find_typescript_files():
    """Find all TypeScript files in project"""
    ts_files = []
    for ext in ['*.ts', '*.tsx']:
        ts_files.extend(Path(".").rglob(ext))
    ts_files = [f for f in \
    ts_files if 'node_modules' not in str(f) and 'dist' not in str(f)]
    return sorted(ts_files)

def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="TypeScript Error Fixer")
    parser.add_argument("--fix", action="store_true", help="Apply fixes")
    parser.add_argument("--dry-run", \
    action="store_true", help="Show fixes without applying")
    parser.add_argument("--file", type=str, help="Fix specific file")
    parser.add_argument("--directory", type=str, help="Fix files in directory")
    parser.add_argument("--all", action="store_true", help="Fix all TypeScript files")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    print("="*60)
    print("TYPESCRIPT ERROR FIXER v1.0")
    print("="*60)

    state = load_state()
    print(f"\n[STATE] Loaded TypeScript state")
    print(f"[STATE] Files previously fixed: {len(state['statistics']['files_fixed'])}")

    if args.file:
        print(f"\n[FILE] Fixing: {args.file}")
        fixes = fix_typescript_file(args.file, state, args.dry_run)
        print(f"\n[RESULT] {fixes} \
    fix(es) would be applied" if args.dry_run else f"\n[RESULT] {fixes} fix(es) applied")

    elif args.directory:
        print(f"\n[DIRECTORY] Fixing: {args.directory}")
        ts_files = list(Path(args.directory).rglob("*.ts"))
        total_fixes = 0
        for ts_file in ts_files:
            fixes = fix_typescript_file(str(ts_file), state, args.dry_run)
            total_fixes += fixes
        print(f"\n[RESULT] {total_fixes} \
    fix(es) would be applied" if args.dry_run else f"\n[RESULT] {total_fixes} fix(es) applied")

    elif args.all:
        print(f"\n[ALL] Fixing all TypeScript files...")
        ts_files = find_typescript_files()
        print(f"Found {len(ts_files)} TypeScript files")
        total_fixes = 0
        for ts_file in ts_files:
            fixes = fix_typescript_file(str(ts_file), state, args.dry_run)
            total_fixes += fixes
        print(f"\n[RESULT] {total_fixes} \
    fix(es) would be applied" if args.dry_run else f"\n[RESULT] {total_fixes} fix(es) applied")
        if not args.dry_run:
            save_state(state)

    else:
        print(f"\n[ANALYZE] Analyzing TypeScript files...")
        ts_files = find_typescript_files()
        total_errors = 0
        for ts_file in ts_files:
            errors = analyze_typescript_errors(str(ts_file))
            error_count = sum(len(v) for v in errors.values())
            if error_count > 0:
                print(f"  {ts_file}: {error_count} issue(s) found")
                total_errors += error_count
        print(f"\n[TOTAL] {total_errors} issues found in {len(ts_files)} files")
        print("\nUse --fix to apply corrections")

    print("="*60)

if __name__ == "__main__":
    main()
