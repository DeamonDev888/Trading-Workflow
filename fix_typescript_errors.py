"""
Script de correction automatique pour les erreurs TypeScript identifiées
Correction des erreurs de syntaxe systématiques : ":" au lieu de "as" pour le casting
"""

import os
import re
import sys
from pathlib import Path

def fix_typescript_syntax_errors(file_path):
    """Corrige les erreurs de syntaxe TypeScript dans un fichier"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        pattern1 = r'(\w+)\s*=\s*([^:;]+):\s*([^;]+);'
        replacement1 = r'\1 = \2 as \3;'
        content = re.sub(pattern1, replacement1, content)

        pattern2 = r'(\w+\.\w+\([^)]*\)):\s*(\w+)'
        replacement2 = r'\1 as \2'
        content = re.sub(pattern2, replacement2, content)

        pattern3 = r'(\w+)\s*=\s*([^:;]+):\s*(\w+);'
        replacement3 = r'\1 = \2 as \3;'
        content = re.sub(pattern3, replacement3, content)

        pattern4 = r'\)\s*:\s*(\w+)\s*;'
        replacement4 = r') as \1;'
        content = re.sub(pattern4, replacement4, content)

        content = re.sub(r'(\w+)\s*=\s*[^;]*$', r'\1;', content, flags=re.MULTILINE)

        content = re.sub(r'}\s*catch\s*\(', '} catch (', content)

        content = re.sub(r'return\s*([^;]*)$', r'return \1;', content, flags=re.MULTILINE)

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"Erreur en traitant {file_path}: {e}")
        return False

def main():
    """Fonction principale pour corriger tous les fichiers TypeScript"""
    print("Démarrage de la correction automatique des erreurs TypeScript...")

    ts_files = [
        "src/cache/memory-cache.ts",
        "src/core/circuit-breaker.ts",
        "src/core/retry-manager.ts",
        "src/core/websocket-manager.ts",
        "src/health/health-checker.ts",
        "src/logging/structured-logger.ts",
        "src/metrics/prometheus.ts",
        "src/security/rate-limiter.ts",
        "src/security/security-headers.ts",
        "src/validation/schemas.ts",
        "backend/server-backend.ts",
        "frontend/server-frontend.ts"
    ]

    corrected_files = []
    total_files = 0

    for ts_file in ts_files:
        file_path = Path(ts_file)
        if file_path.exists():
            total_files += 1
            if fix_typescript_syntax_errors(file_path):
                corrected_files.append(str(file_path))
                print(f"[CORRIGE] {ts_file}")
            else:
                print(f"[OK] Pas de correction nécessaire: {ts_file}")
        else:
            print(f"[ATTENTION] Fichier non trouvé: {ts_file}")

    print(f"\n{'='*60}")
    print("RÉSUMÉ DES CORRECTIONS")
    print(f"{'='*60}")
    print(f"Fichiers traités: {total_files}")
    print(f"Fichiers corrigés: {len(corrected_files)}")

    if corrected_files:
        print(f"\nFichiers modifiés:")
        for file in corrected_files:
            print(f"  - {file}")

    print(f"\n[SUCCESS] Correction automatique terminée !")

if __name__ == "__main__":
    main()