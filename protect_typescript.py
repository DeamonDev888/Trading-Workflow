"""
Protection TypeScript pour NovaQuote
Empêche la modification des fichiers .ts par les scripts
"""

import re
import os
from pathlib import Path

PROTECTED_TS_FILES = [
    "run.ts",
    "backend/server-backend.ts",
    "frontend/server-frontend.ts"
]

def check_ts_files():
    """Vérifie si des fichiers TS ont été modifiés"""
    print("="*60)
    print("PROTECTION TYPESCRIPT - Vérification")
    print("="*60)

    violations = []

    for ts_file in PROTECTED_TS_FILES:
        if Path(ts_file).exists():
            with open(ts_file, 'r', encoding='utf-8') as f:
                content = f.read()

            if '{;' in content:
                violations.append(f"❌ {ts_file}: contient '{{;'")
            if '(;' in content:
                violations.append(f"❌ {ts_file}: contient '(;'")
            if ',;' in content and '//' not in content:
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if ',;' in line and not line.strip().startswith('//'):
                        violations.append(f"❌ {ts_file} ligne {i}: contient ',;'")

    if violations:
        print("\n⚠️  VIOLATIONS DÉTECTÉES:")
        for v in violations:
            print(f"  {v}")
        print("\n💡 Exécutez: git restore run.ts backend/server-backend.ts frontend/server-frontend.ts")
    else:
        print("\n✅ Tous les fichiers TypeScript sont SAINS")

    print("="*60)
    return violations

if __name__ == "__main__":
    check_ts_files()
