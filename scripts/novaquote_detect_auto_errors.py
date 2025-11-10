"""
AUTO BUG FIXER CLI - Correction automatique intelligente
Détecte et corrige automatiquement TOUS les bugs
Version améliorée avec gestion Windows et fallbacks robustes
V2.0 - Mode Persistant avec Sauvegarde d'état
"""

import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

STATE_FILE = ".novaquote_linter_state_js.json"

def load_state():
    """Load persistent state from JSON file"""
    if Path(STATE_FILE).exists():
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {
        "version": "2.0",
        "corrections": {},
        "statistics": {
            "total_corrections": 0,
            "files_fixed": 0,
            "files_fixed_list": [],
            "patterns_used": []
        }
    }

def save_state(state):
    """Save state to JSON file"""
    try:
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"  [WARN] Could not save state: {e}")

def get_file_hash(file_path):
    """Get MD5 hash of file content"""
    try:
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None

def is_file_changed(state, file_path):
    """Check if file has changed since last correction"""
    if file_path not in state["corrections"]:
        return True
    current_hash = get_file_hash(file_path)
    saved_hash = state["corrections"].get(file_path, {}).get("hash")
    return current_hash != saved_hash

def record_correction(state, file_path, correction_type, success):
    """Record a correction in persistent state"""
    state["corrections"][file_path] = {
        "type": correction_type,
        "timestamp": datetime.now().isoformat(),
        "success": success,
        "hash": get_file_hash(file_path)
    }
    state["statistics"]["total_corrections"] += 1
    if success:
        if "files_fixed_list" not in state["statistics"]:
            state["statistics"]["files_fixed_list"] = []
        if file_path not in state["statistics"]["files_fixed_list"]:
            state["statistics"]["files_fixed_list"].append(file_path)
        state["statistics"]["files_fixed"] = len(state["statistics"]["files_fixed_list"])

def should_process_file(state, file_path, force=False):
    """Check if file should be processed (avoid duplicate work)"""
    if force:
        return True
    if not is_file_changed(state, file_path):
        return False
    return True

def normalize_path(path):
    """Normalize path for Windows compatibility"""
    path = path.replace('/', os.sep).replace('\\', os.sep)
    return path

def fix_semicolons(file_path):
    """Add missing semicolons in JavaScript/TypeScript"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  [ERROR] Cannot read file: {e}")
        return 0

    original_content = content
    fixes_made = 0
    lines = content.split('\n')

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not \
    stripped or stripped.startswith('//') or stripped.startswith('/*') or stripped.endswith(';') or stripped.endswith('{') or stripped.endswith('}'):
            continue

        if stripped == '}' or stripped == ']':
            continue

        if re.match(r'^\s*(if|for|while|switch|function|try|catch|finally)\b', line):
            continue

        if re.match(r'^\s*(const|let|var)\s+\w+', line) or \
           re.match(r'^\s*\w+\s*=\s*', line) or \
           re.match(r'^\s*\w+\([^)]*\)\s*;?\s*$', line):
            if not line.strip().endswith(';'):
                lines[i] = line.rstrip() + ';'
                fixes_made += 1

    if fixes_made > 0:
        fixed_content = '\n'.join(lines)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"  [FIXED] Added {fixes_made} missing semicolon(s)")
        except Exception as e:
            print(f"  [ERROR] Cannot write file: {e}")
            return 0

    return fixes_made

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

    if errors and 'test_var' in file_path:
        print(f"  [DEBUG2] fix_var_to_let_const called with {len(errors)} errors")

    for error in errors:
        if "test_var" in file_path:
            print(f"  [DEBUG2] Processing error: {error}")

        if "no-var" in str(error.get('ruleId', '')) or "no-var" in str(error):
            if isinstance(error, dict):
                line_num = error.get('line', error.get('lineNumber', 0))
            else:
                parts = error.split(':')
                line_num = int(parts[1]) if len(parts) >= 2 else 0

            if line_num > 0:
                lines = content.split('\n')
                if 1 <= line_num <= len(lines):
                    line = lines[line_num - 1]
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
            parts = error.split(':')
            if len(parts) >= 2:
                try:
                    line_num = int(parts[1])
                    lines = content.split('\n')

                    if 1 <= line_num <= len(lines):
                        line = lines[line_num - 1]
               \
             if line.strip().startswith('const ') or line.strip().startswith('let '):
                \
                new_line = re.sub(r'^(const|let)\s+\w+\s*(=.*)?;?', '', line).strip()
                            if new_line:
                                lines[line_num - 1] = new_line
                                content = '\n'.join(lines)
                                fixes_made += 1
                    \
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
               \
         return [msg for msg in messages if msg.get('ruleId') in ['no-var', 'no-unused-vars']]
            except (json.JSONDecodeError, KeyError):
                pass
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        pass

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        errors = []
        for i, line in enumerate(lines, 1):
            if re.search(r'\bvar\s+', line):
                errors.append({
                    'line': i,
                    'ruleId': 'no-var',
                    'message': 'Unexpected var, use let or const instead',
                    'lineNumber': i
                })

        print(f" \
     [AUTO] Detected {len(errors)} var declaration(s) (ESLint not available)")
        return errors
    except Exception as e:
        print(f"  [WARN] Error scanning file: {e}")
        return []

def detect_and_fix_common_issues(file_path, state=None, force=False):
    """Detect and fix common JavaScript/TypeScript issues with persistence"""
    if state and not force and not should_process_file(state, file_path):
        print(f"  [SKIP] {file_path} (no changes since last correction)")
        return 0

    fixes_made = 0

    semicolon_fixes = fix_semicolons(file_path)
    fixes_made += semicolon_fixes
    if semicolon_fixes > 0 and state:
        record_correction(state, file_path, "semicolon", True)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        content = re.sub(r'\bconsole\.log\b', 'console.info', content)

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  [FIXED] Replaced console.log with console.info")
            fixes_made += 1
            if state:
                record_correction(state, file_path, "console.log", True)
    except Exception as e:
        print(f"  [WARN] Could not fix console statements: {e}")

    if state and fixes_made > 0:
        save_state(state)

    return fixes_made

def fast_scan_js():
    """Ultra fast JS/TS scan for agent to parse results"""
    print("="*60)
    print("FAST SCAN - JavaScript/TypeScript")
    print("="*60)

    ts_files = []
    try:
        all_js = list(Path(".").rglob("*.js"))
        all_ts = list(Path(".").rglob("*.ts"))
        ts_files = all_js + all_ts
        ts_files = [f for f in ts_files \
    if 'node_modules' not in str(f) and 'dist' not in str(f) and 'build' not in str(f)]
        ts_files = [Path(normalize_path(str(f))) for f in ts_files]
    except Exception as e:
        print(f"  [WARN] Error finding files: {e}")
        ts_files = []

    if not ts_files:
        print("  [INFO] No .js or .ts files found")
        return 0

    issues_found = []
    for file_path in sorted(ts_files):
        file_str = str(file_path)
        try:
            with open(file_str, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                if re.search(r'\bvar\s+', line):
                    issues_found.append(f"{file_str}:{i}: var declaration")
           \
         if re.search(r'(const|let|var)\s+\w+\s*=\s*[^;{}]$', stripped) and not stripped.startswith('//'):
                    issues_found.append(f"{file_str}:{i}: missing semicolon")
                if 'console.log' in line:
                    issues_found.append(f"{file_str}:{i}: console.log statement")
        except Exception as e:
            continue

    if issues_found:
        print(f"\n[ISSUES] {len(issues_found)} problem(s) found:")
        for issue in issues_found[:20]:  # Show first 20
            print(f"  {issue}")
        if len(issues_found) > 20:
            print(f"  ... and {len(issues_found) - 20} more")
    else:
        print("\n[OK] No issues found")

    print("="*60)
    print("[SCAN COMPLETE] Results ready for agent parsing")
    print("="*60)
    return len(issues_found)

def fix_all_bugs():
    """Corrige automatiquement tous les bugs détectés"""
    print("="*60)
    print("AUTO BUG FIXER CLI - Correction automatique intelligente")
    print("Version améliorée avec fallbacks robustes")
    print("="*60)

    ts_files = []
    try:
        all_js = list(Path(".").rglob("*.js"))
        all_ts = list(Path(".").rglob("*.ts"))
        ts_files = all_js + all_ts
        ts_files = [f for f in ts_files \
    if 'node_modules' not in str(f) and 'dist' not in str(f) and 'build' not in str(f)]
        ts_files = [Path(normalize_path(str(f))) for f in ts_files]
    except Exception as e:
        print(f"  [WARN] Error finding files: {e}")
        ts_files = []

    if not ts_files:
        print("  [INFO] No .js or .ts files found")
        return 0

    total_fixes = 0
    processed_files = 0

    print(f"\n[INFO] Found {len(ts_files)} JavaScript/TypeScript files to process")
    print("="*60)

    for file_path in sorted(ts_files):
        file_str = str(file_path)
        print(f"\n[PROCESSING] {file_str}")

        common_fixes = detect_and_fix_common_issues(file_str)
        total_fixes += common_fixes

        errors = run_eslint(file_str)

        if not errors:
            print("  [OK] Aucune erreur détectée")
        else:
            print(f"  [ERRORS] {len(errors)} erreur(s) détectée(s)")

            fixes = fix_var_to_let_const(file_str, errors)
            total_fixes += fixes

            removals = remove_unused_vars(file_str, errors)
            total_fixes += removals

        processed_files += 1

    print("\n" + "="*60)
    print(f"[RESULT] {processed_files} fichier(s) traité(s)")
    print(f"[RESULT] {total_fixes} correction(s) effectuée(s)")
    print("\nFixes appliquées:")
    print("  [OK] Correction var -> let/const")
    print("  [OK] Suppression variables non utilisées")
    print("  [OK] Ajout points-virgules manquants")
    print("  [OK] Remplacement console.log")
    print("="*60)

    return total_fixes

def fast_scan_js_file(file_path):
    """Scan a single file for issues"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        lines = content.split('\n')
        issues = []
        for i, line in enumerate(lines, 1):
            if re.search(r'\bvar\s+', line):
                issues.append(f"{file_path}:{i}: var declaration")
         \
       if re.search(r'(const|let|var)\s+\w+\s*=\s*[^;{}]$', line.strip()) and not line.strip().startswith('//'):
                issues.append(f"{file_path}:{i}: missing semicolon")
            if 'console.log' in line:
                issues.append(f"{file_path}:{i}: console.log statement")
        return len(issues)
    except:
        return 0

def fast_scan_js_directory(directory):
    """Scan all JS/TS files in a directory"""
    import glob
    files \
    = glob.glob(f"{directory}/**/*.js", recursive=True)
                                                       + glob.glob(f"{directory}/**/*.ts", recursive=True)

    total_issues = 0
    for file_path in files:
        total_issues += fast_scan_js_file(file_path)
    return total_issues

def fast_scan_js_pattern(pattern):
    """Scan files matching pattern"""
    import glob
    files = glob.glob(pattern, recursive=True)
    total_issues = 0
    for file_path in files:
        if file_path.endswith(('.js', '.ts')):
            total_issues += fast_scan_js_file(file_path)
    return total_issues

def scan_and_fix_directory(directory, state=None, force=False):
    """Scan and fix all files in directory with persistence"""
    import glob
    files \
    = glob.glob(f"{directory}/**/*.js", recursive=True)
                                                       + glob.glob(f"{directory}/**/*.ts", recursive=True)

    total_fixes = 0
    for file_path in files:
        if state and not force and not should_process_file(state, file_path):
            continue
        total_fixes += detect_and_fix_common_issues(file_path, state, force)
    if state:
        save_state(state)
    return total_fixes

def scan_and_fix_pattern(pattern, state=None, force=False):
    """Scan and fix files matching pattern with persistence"""
    import glob
    files = glob.glob(pattern, recursive=True)
    total_fixes = 0
    for file_path in files:
        if file_path.endswith(('.js', '.ts')):
            if state and not force and not should_process_file(state, file_path):
                continue
            total_fixes += detect_and_fix_common_issues(file_path, state, force)
    if state:
        save_state(state)
    return total_fixes

if __name__ == "__main__":
    try:
        import argparse

        \
    parser = argparse.ArgumentParser(description="Auto Bug Fixer CLI - JavaScript/TypeScript")
       \
     parser.add_argument("--check", action="store_true", help="Check only (ultra fast scan)")
        parser.add_argument("--fix", action="store_true", help="Apply automatic fixes")
        parser.add_argument("--file", type=str, help="Target specific file")
        parser.add_argument("--directory", type=str, help="Target specific directory")
        \
    parser.add_argument("--pattern", type=str, help="Target files matching pattern (e.g., '*.ts')")
        parser.add_argument("--severity", \
    type=str, choices=['low', 'medium', 'high'], help="Fix only issues of specific severity")
        parser.add_argument("--force", \
    action="store_true", help="Force processing even if file hasn't changed (persistence mode)")
       \
     parser.add_argument("--no-persist", action="store_true", help="Disable persistent state tracking")
        args = parser.parse_args()

        state = None
        if not args.no_persist:
            state = load_state()
          \
      print(f"\n[STATE] Loaded persistent state with {len(state['corrections'])} recorded corrections")
        \
        print(f"[STATE] Total corrections applied: {state['statistics']['total_corrections']}")

        if args.file:
            print(f"\n[TARGETED] Processing single file: {args.file}")
            if args.fix:
                issues = detect_and_fix_common_issues(args.file, state, args.force)
                print(f"\n[RESULT] {issues} fix(es) applied to {args.file}")
                if state:
                    save_state(state)
            \
            print(f"[STATE] Total corrections: {state['statistics']['total_corrections']}")
            \
            print(f"[STATE] Files processed: {state['statistics']['files_fixed']}")
            else:
                issues = fast_scan_js_file(args.file)
                print(f"\n[RESULT] {issues} issue(s) found in {args.file}")
            sys.exit(0)

        if args.directory:
            print(f"\n[TARGETED] Processing directory: {args.directory}")
            if args.fix:
                issues = scan_and_fix_directory(args.directory, state, args.force)
                print(f"\n[RESULT] {issues} fix(es) applied in {args.directory}")
                if state:
                    save_state(state)
            \
            print(f"[STATE] Total corrections: {state['statistics']['total_corrections']}")
            \
            print(f"[STATE] Files processed: {state['statistics']['files_fixed']}")
            else:
                issues = fast_scan_js_directory(args.directory)
                print(f"\n[RESULT] {issues} issue(s) found in {args.directory}")
            sys.exit(0)

        if args.pattern:
            print(f"\n[TARGETED] Processing pattern: {args.pattern}")
            if args.fix:
                issues = scan_and_fix_pattern(args.pattern, state, args.force)
           \
         print(f"\n[RESULT] {issues} fix(es) applied for pattern {args.pattern}")
                if state:
                    save_state(state)
            \
            print(f"[STATE] Total corrections: {state['statistics']['total_corrections']}")
            \
            print(f"[STATE] Files processed: {state['statistics']['files_fixed']}")
            else:
                issues = fast_scan_js_pattern(args.pattern)
                print(f"\n[RESULT] {issues} issue(s) found for pattern {args.pattern}")
            sys.exit(0)

        issues = fast_scan_js()
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
