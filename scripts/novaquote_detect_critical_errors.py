"""
NOVAQUOTE MASTER FIXER - VERSION SIMPLIFIÉE
Agent unique qui corrige TOUT : Linting + Erreurs + Format
"""

import re
import subprocess
from pathlib import Path


def fix_python_file(file_path):
    """Fix Python file"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original = content
        lines = content.split("\n")
        corrections = 0

        for i in range(len(lines)):
            if lines[i] != lines[i].rstrip():
                lines[i] = lines[i].rstrip()
                corrections += 1

        content = "\n".join(lines)
        content = re.sub(r"^[ \t]*#[^\n]*\n", "", content, flags=re.MULTILINE)

        if content != original:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
    except:
        pass
    return False


def fix_js_ts_file(file_path):
    """Fix JavaScript/TypeScript file"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original = content
        lines = content.split("\n")
        corrections = 0

        for i in range(len(lines)):
            line = lines[i].strip()
            if line and not line.startswith("//") and not line.endswith(";"):
                if "const " in line or "let " in line or "var " in line:
                    lines[i] = lines[i].rstrip() + ";"
                    corrections += 1

        content = "\n".join(lines)
        content = content.replace("console.log", "console.info")

        if content != original:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
    except:
        pass
    return False


def run_external_tools():
    """Run Black, isort, etc."""
    print("\n[EXTERNAL TOOLS] Running black...")
    try:
        subprocess.run(["black", "src", "--line-length=88"], timeout=60)
    except:
        print("  [WARN] Black failed or not available")

    print("[EXTERNAL TOOLS] Running isort...")
    try:
        subprocess.run(["isort", "src"], timeout=60)
    except:
        print("  [WARN] isort failed or not available")


def main():
    print("=" * 60)
    print("NOVAQUOTE MASTER FIXER v1.0 - SIMPLE")
    print("=" * 60)

    total_fixed = 0

    print("\n[PYTHON] Fixing Python files...")
    for py_file in Path(".").rglob("*.py"):
        if "node_modules" not in str(py_file):
            if fix_python_file(str(py_file)):
                print(f"  Fixed: {py_file}")
                total_fixed += 1

    print("\n[JAVASCRIPT ONLY] Fixing JS files (TypeScript excluded)...")
    for js_file in Path(".").rglob("*.js"):
        if "node_modules" not in str(js_file):
            if fix_js_ts_file(str(js_file)):
                print(f"  Fixed: {js_file}")
                total_fixed += 1

    run_external_tools()

    print("\n" + "=" * 60)
    print(f"TOTAL: {total_fixed} files fixed")
    print("=" * 60)


if __name__ == "__main__":
    main()
