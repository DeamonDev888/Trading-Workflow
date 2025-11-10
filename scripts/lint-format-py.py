
import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description, check_output=True):
    """Run a command and handle errors"""
    try:
        print(f"\n🔄 {description}...")

        command = command.replace("&&", ";")

        if check_output:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
                encoding='utf-8',
                errors='replace'
            )

            if result.returncode == 0:
                print(f"✅ {description} completed successfully")
                if result.stdout.strip():
                    print("Output:")
                    print(result.stdout)
                return True
            else:
                print(f"❌ {description} failed")
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
                errors='replace'
            )

            if result.returncode == 0:
                print(f"✅ {description} completed successfully")
                return True
            else:
                print(f"❌ {description} failed")
                return False

    except Exception as e:
        print(f"❌ {description} failed with exception: {e}")
        return False

def check_console_statements():
    """Check for problematic print statements (except in certain files)"""
    print("\n🔍 Checking for problematic print statements...")

    try:
        result = subprocess.run(
            'findstr /R /S "print\\(" src\\*.py 2>nul',
            shell=True,
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )

        if result.stdout.strip():
            print("⚠️  Found print statements:")
            print(result.stdout)
            print("Consider replacing with proper logging")
        else:
            print("✅ No problematic print statements found")

    except Exception as e:
        print(f"⚠️  Could not check for print statements: {e}")

def main():
    """Main function to run all linting and formatting checks"""
    print("🚀 Starting Python linting and formatting process...")

    if not Path("src").exists():
        print("❌ No 'src' directory found. Are you in the correct project directory?")
        sys.exit(1)

    success = True

    source_dirs = "src/agents src/models src/scripts src/strategies src/database"
    success = run_command(
        f"flake8 {source_dirs} --max-line-length=88 --exclude=__pycache__,*.pyc,.git,venv,env",
        "Flake8 linting check"
    ) and success

    success = run_command(
        f"black --check {source_dirs} --line-length=88",
        "Black formatting check"
    ) and success

    print("\n🔍 Running Pylint analysis...")
    pylint_success = run_command(
        f"pylint {source_dirs} --disable=missing-module-docstring,missing-class-docstring,missing-function-docstring --max-line-length=88",
        "Pylint comprehensive analysis",
        check_output=True
    )

    if not pylint_success:
        print("⚠️  Pylint found issues (this is normal for development code)")

    check_console_statements()

    if success:
        print("\n🎉 All Python linting and formatting checks passed!")
        print("\nSummary:")
        print("✅ Flake8: No syntax or style issues")
        print("✅ Black: Code formatting is correct")
        print("⚠️  Pylint: May have warnings (normal for development)")
        sys.exit(0)
    else:
        print("\n💥 Some Python checks failed. Please fix the issues above.")
        print("\nTo auto-fix formatting issues, run:")
        print("python lint-format-py.py --fix")
        sys.exit(1)

def apply_fixes():
    """Apply automatic fixes"""
    print("🔧 Applying automatic fixes...")

    success = True

    source_dirs = "src/agents src/models src/scripts src/strategies src/database"
    success = run_command(
        f"black {source_dirs} --line-length=88",
        "Black formatting application"
    ) and success

    success = run_command(
        f"isort {source_dirs} --profile=black",
        "Import sorting"
    ) and success

    if success:
        print("\n🎉 Automatic fixes applied successfully!")
        print("Please review the changes and run the checks again.")
    else:
        print("\n❌ Some fixes failed. Please review the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--fix":
        apply_fixes()
    else:
        main()