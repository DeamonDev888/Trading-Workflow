"""
Script avancé de correction TypeScript pour les erreurs complexes identifiées
"""

import os
import re
from pathlib import Path

def fix_typescript_file_advanced(file_path):
    """Corrige les erreurs TypeScript avancées dans un fichier"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        content = re.sub(r'\(([^)]+)\)\s+as\s+(void|string|number|boolean|any)', r'(\1): \2', content)

        content = re.sub(r'(\w+\([^)]*)\s+as\s+(\w+)', r'\1', content)

        content = re.sub(r'(\w+\.\w+)\s*:\s*\w+', r'\1', content)

        content = re.sub(r'\(([^)]+)\)\s+(void|string|number|boolean|any)', r'(\1): \2', content)

        content = re.sub(r'(\w+)\s*:\s*([^;}{\n]+)\s*;', r'\1: \2;', content)

        content = re.sub(r'(\w+:\s+[^,\n}]+)\n(\s+\w+:)', r'\1,\n\2', content)

        content = re.sub(r'private\s+(\w+)\s*:\s*([^;]+)\s*;', r'private \1: \2;', content)
        content = re.sub(r'public\s+(\w+)\s*:\s*([^;]+)\s*;', r'public \1: \2;', content)
        content = re.sub(r'(\w+)\s*:\s*([^;]+)\s*;', r'\1: \2;', content)

        content = re.sub(r'}\s*catch\(', '} catch (', content)

        content = re.sub(r'(\w+)\s*=\s*[^;]*$', r'\1;', content, flags=re.MULTILINE)
        content = re.sub(r'return\s+[^;]*$', r'return \1;', content, flags=re.MULTILINE)

        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"Erreur en traitant {file_path}: {e}")
        return False

def main():
    """Fonction principale"""
    print("Correction avancée des erreurs TypeScript...")

    ts_files = [
        "backend/server-backend.ts",
        "frontend/server-frontend.ts"
    ]

    corrected_files = []
    total_files = 0

    for ts_file in ts_files:
        file_path = Path(ts_file)
        if file_path.exists():
            total_files += 1
            if fix_typescript_file_advanced(file_path):
                corrected_files.append(str(file_path))
                print(f"[CORRIGE] {ts_file}")
            else:
                print(f"[OK] Pas de correction nécessaire: {ts_file}")
        else:
            print(f"[ATTENTION] Fichier non trouvé: {ts_file}")

    print(f"\n{'='*60}")
    print("RÉSUMÉ DES CORRECTIONS AVANCÉES")
    print(f"{'='*60}")
    print(f"Fichiers traités: {total_files}")
    print(f"Fichiers corrigés: {len(corrected_files)}")

    if corrected_files:
        print(f"\nFichiers modifiés:")
        for file in corrected_files:
            print(f"  - {file}")

    print(f"\n[SUCCESS] Correction avancée terminée !")

if __name__ == "__main__":
    main()