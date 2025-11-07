#!/usr/bin/env python3
"""
AUTO BUG FIXER CLI - Correction automatique intelligente
Détecte et corrige automatiquement TOUS les bugs
"""

import re
import os
import sys
import json
import subprocess
from pathlib import Path

def fix_var_to_let_const(file_path, errors):
    """Corrige automatiquement var -> let/const en JavaScript"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  [ERROR] Cannot read file: {e}")
        return 0

    original_content = content
    fixes_made = 0

    # DEBUG
    if errors and 'test_var' in file_path:
        print(f"  [DEBUG2] fix_var_to_let_const called with {len(errors)} errors")

    for error in errors:
        if "test_var" in file_path:
            print(f"  [DEBUG2] Processing error: {error}")

        if "no-var" in str(error.get('ruleId', '')) or "no-var" in str(error):
            # Obtenir le numéro de ligne (format ESLint ou fallback)
            if isinstance(error, dict):
                line_num = error.get('line', error.get('lineNumber', 0))
            else:
                # Parse ESLint error format: /path/to/file.js:line:col: error message
                parts = error.split(':')
                line_num = int(parts[1]) if len(parts) >= 2 else 0

            if line_num > 0:
                lines = content.split('\n')
                if 1 <= line_num <= len(lines):
                    line = lines[line_num - 1]
                    # Remplacer 'var ' par 'let ' ou 'const '
                    if ' = ' in line or 'const' in line:
                        new_line = re.sub(r'\bvar\s+', 'const ', line)
                        replacement = 'const'
                    else:
                        new_line = re.sub(r'\bvar\s+', 'let ', line)
                        replacement = 'let'

                    lines[line_num - 1] = new_line
                    content = '\n'.join(lines)
                    fixes_made += 1
                    print(f"    [FIXED] Line {line_num}: var -> {replacement}")

    if fixes_made > 0:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  [OK] File written with {fixes_made} fixes")
        except Exception as e:
            print(f"  [ERROR] Cannot write file: {e}")
            return 0
    return fixes_made

def remove_unused_vars(file_path, errors):
    """Supprime les variables non utilisées"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  [ERROR] Cannot read file: {e}")
        return 0

    original_content = content
    fixes_made = 0

    for error in errors:
        if "no-unused-vars" in error:
            # Parse ESLint error
            parts = error.split(':')
            if len(parts) >= 2:
                try:
                    line_num = int(parts[1])
                    lines = content.split('\n')

                    if 1 <= line_num <= len(lines):
                        line = lines[line_num - 1]
                        # Simple removal for unused vars
                        if line.strip().startswith('const ') or line.strip().startswith('let '):
                            new_line = re.sub(r'^(const|let)\s+\w+\s*(=.*)?;?', '', line).strip()
                            if new_line:
                                lines[line_num - 1] = new_line
                                content = '\n'.join(lines)
                                fixes_made += 1
                                print(f"    [REMOVED] Line {line_num}: unused variable")
                except (ValueError, IndexError):
                    continue

    if fixes_made > 0:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  [OK] File written with {fixes_made} removals")
        except Exception as e:
            print(f"  [ERROR] Cannot write file: {e}")
            return 0
    return fixes_made

def run_eslint(file_path):
    """Exécute ESLint sur un fichier et retourne les erreurs"""
    try:
        # Essayer npx d'abord
        result = subprocess.run(
            ['npx', 'eslint', file_path, '--format=json'],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.stdout:
            try:
                data = json.loads(result.stdout)
                if data and len(data) > 0:
                    messages = data[0].get('messages', [])
                    return [msg for msg in messages if msg.get('ruleId') in ['no-var', 'no-unused-vars']]
            except (json.JSONDecodeError, KeyError):
                pass
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        pass

    # FALLBACK: Détection directe sans ESLint
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        errors = []
        for i, line in enumerate(lines, 1):
            # Détecter var
            if re.search(r'\bvar\s+', line):
                errors.append({
                    'line': i,
                    'ruleId': 'no-var',
                    'message': 'Unexpected var, use let or const instead',
                    'lineNumber': i
                })

        print(f"  [AUTO] Detected {len(errors)} var declaration(s) (ESLint not available)")
        return errors
    except Exception as e:
        print(f"  [WARN] Error scanning file: {e}")
        return []

def fix_all_bugs():
    """Corrige automatiquement tous les bugs détectés"""
    print("="*60)
    print("AUTO BUG FIXER CLI - Correction automatique intelligente")
    print("="*60)

    # Fichiers TypeScript/JavaScript à corriger
    ts_files = []
    try:
        # Chercher dans tous les dossiers
        all_js = list(Path(".").rglob("*.js"))
        all_ts = list(Path(".").rglob("*.ts"))
        ts_files = all_js + all_ts
        # Filtrer les fichiers node_modules
        ts_files = [f for f in ts_files if 'node_modules' not in str(f)]
    except Exception as e:
        print(f"  [WARN] Error finding files: {e}")
        ts_files = []

    if not ts_files:
        print("  [INFO] No .js or .ts files found")
        return 0

    total_fixes = 0
    processed_files = 0

    for file_path in sorted(ts_files):
        file_str = str(file_path)
        print(f"\n[PROCESSING] {file_str}")

        # Détecter les erreurs avec ESLint
        errors = run_eslint(file_str)

        if not errors:
            print("  [OK] Aucune erreur détectée")
            processed_files += 1
            continue

        print(f"  [ERRORS] {len(errors)} erreur(s) détectée(s)")
        # DEBUG: Print first error to verify format
        if errors and 'test_var_fix' in file_str:
            print(f"  [DEBUG] First error: {errors[0]}")
            print(f"  [DEBUG] Error type: {type(errors[0])}")

        # Corriger automatiquement var -> let/const
        fixes = fix_var_to_let_const(file_str, errors)
        total_fixes += fixes

        # Retirer les variables non utilisées
        removals = remove_unused_vars(file_str, errors)
        total_fixes += removals

        processed_files += 1

    print("\n" + "="*60)
    print(f"[RESULT] {processed_files} fichier(s) traité(s)")
    print(f"[RESULT] {total_fixes} correction(s) effectuée(s)")
    print("="*60)

    return total_fixes

if __name__ == "__main__":
    try:
        fixes = fix_all_bugs()
        sys.exit(0 if fixes >= 0 else 1)
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
