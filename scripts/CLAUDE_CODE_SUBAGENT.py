#!/usr/bin/env python3
"""
CLAUDE CODE SUB-AGENT TASK - NOVAQUOTE Bug Fixer
VRAI SUB-AGENT TASK POUR CLAUDE CODE CLI

Ce script est un sub-agent task qui est invoqué PAR Claude Code,
pas l'inverse. Il a accès aux outils Claude Code (Read, Edit, Bash, etc.)

Utilisation dans Claude Code:
```python
from task_agent import Task
agent = Task(
    subagent_type="novaquote_bug_fixer",
    description="Auto Bug Fixer NOVAQUOTE",
    prompt="Fix code in src/ with 3 iterations",
    tools=["Read", "Edit", "Bash", "Grep", "Glob"]
)
result = await agent.run()
```

OU en ligne de commande depuis Claude Code:
```python
# Dans Claude Code
import subprocess
result = subprocess.run(["python", "CLAUDE_CODE_SUBAGENT.py", "--path", "src/", "--iterations", "3"])
```
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

def main():
    """Point d'entrée du sub-agent task"""

    parser = argparse.ArgumentParser(
        description="CLAUDE CODE SUB-AGENT TASK - NOVAQUOTE Bug Fixer",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--path', type=str, default='src/', help='Target path')
    parser.add_argument('--iterations', type=int, default=3, help='Number of iterations')
    parser.add_argument('--check-only', action='store_true', help='Check only')
    parser.add_argument('--output', type=str, default='json', help='Output format')

    args = parser.parse_args()

    # Informations du sub-agent
    agent_info = {
        "name": "novaquote_bug_fixer",
        "type": "sub_agent_task",
        "version": "1.0.0",
        "capabilities": [
            "read_files",
            "edit_files",
            "bash_commands",
            "glob_search",
            "grep_search"
        ],
        "available_tools": ["Read", "Edit", "Bash", "Grep", "Glob"],
        "target_path": args.path,
        "max_iterations": args.iterations
    }

    print(f"[SUB-AGENT] {agent_info['name']} v{agent_info['version']}")
    print(f"[INFO] Path: {args.path}")
    print(f"[INFO] Iterations: {args.iterations}")
    print(f"[INFO] Tools available: {', '.join(agent_info['available_tools'])}")

    # Simuler le travail du sub-agent
    # En réalité, ce script SERA INVOQUÉ par Claude Code qui utilisera
    # ses propres outils (Read, Edit, Bash) pour faire le travail

    if args.check_only:
        print("\n[CHECK] Environment OK")
        print(f"[OK] Path exists: {os.path.exists(args.path)}")
        print(f"[OK] Python: {sys.version}")
        return 0

    print(f"\n[SUB-AGENT] Starting bug fixing in {args.path}...")

    # Ce script ne fait PAS le travail lui-même
    # Il informe Claude Code de ce qu'il faut faire
    # et Claude Code utilisera ses outils pour le faire

    instructions = {
        "mission": f"Fix code in {args.path}",
        "iterations": args.iterations,
        "actions": [
            "1. Use Read/Glob to scan Python/TS files",
            "2. Use Grep to find issues (unused imports, syntax errors, PEP8)",
            "3. Use Edit to fix files",
            "4. Use Bash to run linters (black, isort, eslint)",
            "5. Repeat until convergence or max iterations"
        ],
        "tools_to_use": ["Read", "Edit", "Bash", "Grep", "Glob"],
        "expected_output": {
            "files_modified": [],
            "corrections": [],
            "summary": "string"
        }
    }

    # Sauvegarder les instructions pour que Claude Code puisse les lire
    with open('subagent_instructions.json', 'w') as f:
        json.dump(instructions, f, indent=2)

    print(f"\n[INSTRUCTIONS] Saved to subagent_instructions.json")
    print(f"[INFO] Claude Code will read this file and execute the mission")
    print(f"[DONE] Sub-agent task prepared")

    return 0

if __name__ == "__main__":
    sys.exit(main())
