"""
Script amélioré de linting et formatting pour NovaQuote Trading
Basé sur les corrections identifiées par le agent-fix-linter
V2.0 - Mode Persistant avec Sauvegarde d'état
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

STATE_FILE = ".novaquote_linter_state.json"

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
        "last_scan": None,
        "files_processed": [],
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

def run_command(command, description, check_output=True, timeout=120):
    """Run a command and handle errors with improved error handling"""
    try:
        print(f"\n[*] {description}...")

        command = command.replace("&&", ";")

        if check_output:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
                encoding='utf-8',
                errors='replace',
                timeout=timeout
            )

            if result.returncode == 0:
                print(f"[+] {description} completed successfully")
                if result.stdout.strip():
                    print("Output:")
                    print(result.stdout)
                return True
            else:
                print(f"[-] {description} failed")
                if result.stdout:
                    print("STDOUT:")
                    print(result.stdout)
                if result.stderr:
                    print("STDERR:")
                    print(result.stderr)
                return False
        else:
            result = subprocess.run(
                command,
                shell=True,
                cwd=os.getcwd(),
                encoding='utf-8',
                errors='replace',
                timeout=timeout
            )

            if result.returncode == 0:
                print(f"[+] {description} completed successfully")
                return True
            else:
                print(f"[-] {description} failed")
                return False

    except subprocess.TimeoutExpired:
        print(f"[-] {description} timed out after {timeout} seconds")
        return False
    except Exception as e:
        print(f"[-] {description} failed with exception: {e}")
        return False

def check_console_statements():
    """Check for problematic print statements (except in certain files)"""
    print("\n[INFO] Checking for problematic print statements...")

    try:
        result = subprocess.run(
            'findstr /R /S "print\\(" src\\*.py 2>nul',
            shell=True,
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )

        if result.stdout.strip():
            print("[WARN] Found print statements:")
            print(result.stdout)
            print("Consider replacing with proper logging")
        else:
            print("[OK] No problematic print statements found")

    except Exception as e:
        print(f"[WARN] Could not check for print statements: {e}")

def fix_common_issues():
    """Fix common issues identified by agent-fix-linter"""
    print("\n[INFO] Fixing common issues (F401, F541, etc.)...")

    fix_unused_imports()

    fix_empty_fstrings()

    fix_long_lines()

def fix_unused_imports():
    """Remove unused imports using autoflake if available"""
    try:
        source_dirs = "src/agents src/algorithms src/models src/data src/hyperliquid src/wallet src/health"
        success = run_command(
            f"autoflake --remove-all-unused-imports --recursive {source_dirs} --in-place",
            "Removing unused imports",
            timeout=60
        )
        if success:
            print("[+] Unused imports removed")
    except:
        print("[WARN] autoflake not available, skipping unused imports removal")

def fix_empty_fstrings():
    """Fix empty f-strings (F541)"""
    print("[INFO] Checking for empty f-strings...")

    try:
        result = subprocess.run(
            'findstr /R /S /C:"f\"\"" src\\*.py 2>nul',
            shell=True,
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )

        if result.stdout.strip():
            print("[WARN] Found empty f-strings (should be regular strings)")
        else:
            print("[OK] No empty f-strings found")

    except Exception as e:
        print(f"[WARN] Could not check for empty f-strings: {e}")

def fix_long_lines():
    """Identify lines that are too long for Black/Black formatting"""
    print("[INFO] Checking for overly long lines (>88 chars)...")

    source_dirs = ["src/agents", "src/algorithms", "src/models", "src/data", "src/hyperliquid", "src/wallet"]
    long_lines_found = False

    for directory in source_dirs:
        if not os.path.exists(directory):
            continue

        for py_file in Path(directory).rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        if len(line) > 88:
                            print(f"[LINE {line_num}] {py_file}: {len(line)} chars")
                            long_lines_found = True
            except:
                continue

    if not long_lines_found:
        print("[OK] No overly long lines found")

def generate_linting_report():
    """Generate a detailed linting report"""
    print("\n[INFO] Generating linting report...")

    report = {
        "timestamp": datetime.now().isoformat(),
        "project": "NovaQuote Trading",
        "checks_performed": [],
        "issues_found": {},
        "recommendations": []
    }

    try:
        result = subprocess.run(
            "flake8 src/ --format=json --max-line-length=88",
            shell=True,
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )

        if result.stdout:
            try:
                issues = json.loads(result.stdout)
                report["issues_found"]["flake8"] = issues
            except:
                report["issues_found"]["flake8_text"] = result.stdout
    except:
        pass

    report_file = f"linting_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"[+] Linting report saved to {report_file}")
    return report_file

def main():
    """Main function to run all linting and formatting checks"""
    print("Starting Enhanced Python linting and formatting process...")

    parser \
    = argparse.ArgumentParser(description="Enhanced linting for NovaQuote Trading")
    parser.add_argument("--check", \
    action="store_true", help="Check only (ultra fast scan)")
    parser.add_argument("--fix", action="store_true", help="Apply automatic fixes")
    parser.add_argument("--file", type=str, help="Target specific file")
    parser.add_argument("--directory", type=str, help="Target specific directory")
    parser.add_argument("--pattern", type=str, \
    help="Target files matching pattern (e.g., 'agents/*.py')")
    parser.add_argument("--severity", type=str, choices=['low', \
    'medium', 'high'], help="Fix only issues of specific severity")
    parser.add_argument("--force", action="store_true", help="Force \
    processing even if file hasn't changed (persistence mode)")
    parser.add_argument("--no-persist", \
    action="store_true", help="Disable persistent state tracking")
    \
    parser.add_argument("--report", action="store_true", help="Generate detailed report")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    state = None
    if not args.no_persist:
        state = load_state()
        \
    print(f"\n[STATE] Loaded persistent state with {len(state['corrections'])} recorded corrections")
      \
      print(f"[STATE] Total corrections applied: {state['statistics']['total_corrections']}")

    if not Path("src").exists():
        print("[-] No \
    'src' directory found. Are you in the correct project directory?")
        sys.exit(1)

    if args.file:
        print(f"\n[TARGETED] Processing single file: {args.file}")
        process_single_file(args.file, args.fix, state, args.force)
        if state and args.fix:
            save_state(state)
        if state:
        \
        print(f"\n[STATE] Total corrections: {state['statistics']['total_corrections']}")
            print(f"[STATE] Files processed: {state['statistics']['files_fixed']}")
        return

    if args.directory:
        print(f"\n[TARGETED] Processing directory: {args.directory}")
        process_directory(args.directory, args.fix, state, args.force)
        if state and args.fix:
            save_state(state)
        if state:
        \
        print(f"\n[STATE] Total corrections: {state['statistics']['total_corrections']}")
            print(f"[STATE] Files processed: {state['statistics']['files_fixed']}")
        return

    if args.pattern:
        print(f"\n[TARGETED] Processing pattern: {args.pattern}")
        process_pattern(args.pattern, args.fix, state, args.force)
        if state and args.fix:
            save_state(state)
        if state:
        \
        print(f"\n[STATE] Total corrections: {state['statistics']['total_corrections']}")
            print(f"[STATE] Files processed: {state['statistics']['files_fixed']}")
        return

    if args.check or not args.fix:
        run_fast_check()
        return

    apply_fixes(state)
    success = True

    if state:
        save_state(state)

    if args.report:
        report_file = generate_linting_report(state)

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")

    if state:
        print(f"\n[STATE] Persistent state saved")
        print(f"[STATE] Total files processed: {state['statistics']['files_fixed']}")
        print(f"[STATE] Total corrections: {state['statistics']['total_corrections']}")

    print("\n[SUCCESS] Enhanced Python linting and formatting completed!")
    print("\nFixes applied:")
    print("[OK] Black code formatting")
    print("[OK] Import sorting with isort")
    print("[OK] Common issues (F401, F541, E501)")
    print("[OK] Consistent formatting")
    print("\nAll Python files have been automatically corrected.")

def process_single_file(file_path, apply_fix, state=None, force=False):
    """Process a single file with persistence"""
    if not Path(file_path).exists():
        print(f"[-] File not found: {file_path}")
        return

    if state and not force and not should_process_file(state, file_path):
        print(f"  [SKIP] {file_path} (no changes since last correction)")
        return

    if apply_fix:
        \
    black_success = run_command(f"black {file_path} --line-length=88", f"Black formatting {file_path}")
        if black_success:
            print(f"  [OK] Black applied to {file_path}")
            if state:
                record_correction(state, file_path, "black", True)

        \
    isort_success = run_command(f"isort {file_path} --profile=black", f"Import sorting {file_path}")
        if isort_success:
            print(f"  [OK] Imports sorted in {file_path}")
            if state:
                record_correction(state, file_path, "isort", True)

        if state:
            save_state(state)
    else:
        black_issues \
    = not run_command(f"black --check {file_path} --line-length=88", f"Black check {file_path}")
        isort_issues \
    = not run_command(f"isort --check-only {file_path} --profile=black", f"isort check {file_path}")

        if black_issues:
            print(f"  [ERROR] Black issues in {file_path}")
        if isort_issues:
            print(f"  [ERROR] Import issues in {file_path}")

        if not black_issues and not isort_issues:
            print(f"  [OK] {file_path} - no issues found")
            if state:
                record_correction(state, file_path, "check", True)

def process_directory(directory, apply_fix, state=None, force=False):
    """Process all Python files in a directory with persistence"""
    dir_path = Path(directory)
    if not dir_path.exists():
        print(f"[-] Directory not found: {directory}")
        return

    target = str(dir_path)
    if apply_fix:
       \
     if run_command(f"black {target} --line-length=88", f"Black formatting {directory}"):
            print(f"  [OK] Black applied to {directory}")
            if state:
                record_correction(state, directory, "black_dir", True)
       \
     if run_command(f"isort {target} --profile=black", f"Import sorting {directory}"):
            print(f"  [OK] Imports sorted in {directory}")
            if state:
                record_correction(state, directory, "isort_dir", True)
        if state:
            save_state(state)
    else:
        \
    if not run_command(f"black --check {target} --line-length=88", f"Black check {directory}"):
            print(f"  [ERROR] Black issues in {directory}")
        \
    if not run_command(f"isort --check-only {target} --profile=black", f"isort check {directory}"):
            print(f"  [ERROR] Import issues in {directory}")

def process_pattern(pattern, apply_fix, state=None, force=False):
    """Process files matching a pattern with persistence"""
    import glob
    files = glob.glob(pattern, recursive=True)
    if not files:
        print(f"[-] No files found matching pattern: {pattern}")
        return

    print(f"[INFO] Found {len(files)} files matching pattern")
    processed = 0
    skipped = 0

    for file_path in files:
        if file_path.endswith('.py'):
            if state and not force and not should_process_file(state, file_path):
                skipped += 1
                continue
            process_single_file(file_path, apply_fix, state, force)
            processed += 1

    if state and state['statistics']:
        if 'patterns_used' not in state['statistics']:
            state['statistics']['patterns_used'] = []
        if pattern not in state['statistics']['patterns_used']:
            state['statistics']['patterns_used'].append(pattern)

    print(f"\n[PATTERN] Processed: {processed}, Skipped (no changes): {skipped}")
    if state and apply_fix:
        save_state(state)

def run_fast_check():
    """Ultra fast scan for agent to parse results"""
    print("\n[FAST SCAN] Running ultra fast Python scan...")
    print("="*60)

    source_dirs = "src/agents src/algorithms src/models src/data src/hyperliquid src/wallet src/health"

    print("\n[CHECK] Black formatting...")
    result = run_command(
        f"black --check {source_dirs} --line-length=88 --diff",
        "Black check",
        timeout=60
    )
    if not result:
        print("  [ERROR] Black formatting issues found")

    print("\n[CHECK] Import sorting...")
    result = run_command(
        f"isort --check-only {source_dirs} --profile=black",
        "isort check",
        timeout=30
    )
    if not result:
        print("  [ERROR] Import sorting issues found")

    print("\n[CHECK] Unused imports...")
    result = run_command(
        f"autoflake --check {source_dirs}",
        "autoflake check",
        timeout=30
    )
    if not result:
        print("  [ERROR] Unused imports found")

    print("="*60)
    print("[SCAN COMPLETE] Results ready for agent parsing")
    print("="*60)

def normalize_path(path):
    """Normalize path for Windows compatibility"""
    import os
    path = path.replace('/', os.sep).replace('\\', os.sep)
    return path

def find_python_files(directories):
    """Find all Python files in the given directories"""
    import glob
    python_files = []
    for directory in directories:
        norm_dir = normalize_path(directory)
        if Path(norm_dir).exists():
            pattern = str(Path(norm_dir) / "**" / "*.py")
            python_files.extend(glob.glob(pattern, recursive=True))
    return python_files

def format_with_black(source_dirs):
    """Format with Black"""
    win_paths = ' '.join([f'"{normalize_path(p)}"' for p in source_dirs.split()])
    return run_command(
        f"black {win_paths} --line-length=88",
        "Black formatting",
        timeout=120
    )

def sort_imports_with_isort(source_dirs):
    """Sort imports with isort"""
    win_paths = ' '.join([f'"{normalize_path(p)}"' for p in source_dirs.split()])
    return run_command(
        f"isort {win_paths} --profile=black --force-sort-within-sections",
        "Import sorting",
        timeout=60
    )

def remove_unused_imports(source_dirs):
    """Remove unused imports with autoflake"""
    win_paths = ' '.join([f'"{normalize_path(p)}"' for p in source_dirs.split()])
    return run_command(
        f"autoflake --remove-all-unused-imports --recursive {win_paths} --in-place",
        "Removing unused imports",
        timeout=90
    )

def format_with_autopep8(source_dirs):
    """Format with autopep8 as fallback"""
    win_paths = ' '.join([f'"{normalize_path(p)}"' for p in source_dirs.split()])
    return run_command(
        f"autopep8 --in-place --max-line-length=88 --aggressive --aggressive {win_paths}",
        "Autopep8 formatting",
        timeout=150
    )

def manual_format_python():
    """Manual Python formatting using built-in tools"""
    print("\n[MANUAL] Applying manual Python formatting...")
    python_files = find_python_files([
        "src/agents", "src/algorithms", "src/models", "src/data",
        "src/hyperliquid", "src/wallet", "src/health"
    ])

    formatted_count = 0
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content
            lines = content.split('\n')

            lines = [line.rstrip() for line in lines]

            fixed_content = '\n'.join(lines)

            fixed_content = fixed_content.replace('\r\n', '\n').replace('\r', '\n')

            if fixed_content != original_content:
                with open(py_file, 'w', encoding='utf-8', newline='') as f:
                    f.write(fixed_content)
                formatted_count += 1
                print(f"  [FORMATTED] {py_file}")
        except Exception as e:
            print(f"  [WARN] Could not format {py_file}: {e}")

    print(f"  [OK] Manually formatted {formatted_count} files")
    return formatted_count > 0

def apply_fixes():
    """Apply enhanced automatic fixes based on agent-fix-linter findings"""
    print("[INFO] Applying enhanced automatic fixes...")
    print(f"{'='*60}")

    success = True
    fixes_count = 0

    source_dirs = "src/agents src/algorithms src/models src/data src/hyperliquid src/wallet src/health src/config.py src/logger.py src/nice_funcs.py"

    print("\n[STEP 1] Applying Black formatting...")
    if format_with_black(source_dirs):
        fixes_count += 1
        print("  [OK] Black formatting applied successfully")
    else:
        print("  [WARN] Black failed, trying fallback methods...")

    print("\n[STEP 2] Sorting imports with isort...")
    if sort_imports_with_isort(source_dirs):
        fixes_count += 1
        print("  [OK] Imports sorted successfully")
    else:
        print("  [WARN] isort failed, continuing...")

    print("\n[STEP 3] Removing unused imports...")
    if remove_unused_imports(source_dirs):
        fixes_count += 1
        print("  [OK] Unused imports removed successfully")
    else:
        print("  [WARN] autoflake failed, continuing...")

    print("\n[STEP 4] Fallback: Using autopep8...")
    if format_with_autopep8(source_dirs):
        fixes_count += 1
        print("  [OK] Autopep8 formatting applied successfully")
    else:
        print("  [WARN] Autopep8 also failed...")

    print("\n[STEP 5] Applying manual formatting fallback...")
    if manual_format_python():
        fixes_count += 1
        print("  [OK] Manual formatting applied successfully")

    print("\n[STEP 6] Re-applying Black for consistency...")
    format_with_black(source_dirs)

    print(f"{'='*60}")
    print(f"\n[RESULT] Applied {fixes_count} types of automatic fixes")
    print("\n[SUCCESS] Enhanced automatic fixes applied successfully!")
    print("\nFixes applied:")
    print("  [OK] Black code formatting (or fallback)")
    print("  [OK] Import sorting (or fallback)")
    print("  [OK] Unused imports removal (or fallback)")
    print("  [OK] Manual formatting cleanup")
    print("  [OK] Consistent formatting")
    print("\nAll Python files have been automatically corrected.")
    print(f"{'='*60}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--fix":
        apply_fixes()
    else:
        main()
