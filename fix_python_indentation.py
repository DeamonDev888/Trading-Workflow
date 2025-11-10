"""
Script pour corriger les erreurs d'indentation Python critiques
"""

import os
import re
from pathlib import Path

def fix_indentation_errors(file_path):
    """Corrige les erreurs d'indentation courantes"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        content = re.sub(r'\\\s*\n\s*', ' ', content)

        content = re.sub(r'\n(\s+)if\s+([^\n]+):\s*\n\s+(\S)', r'\n\1if \2:\n\1\3', content, flags=re.MULTILINE)

        content = re.sub(r'\n(\s+)try\s*:\s*\n\s+(\S)', r'\n\1try:\n\1\2', content, flags=re.MULTILINE)

        content = re.sub(r'\n(\s+)def\s+([^\n]+):\s*\n\s+(\S)', r'\n\1def \2:\n\1\3', content, flags=re.MULTILINE)

        content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)

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
    print("Correction des erreurs d'indentation Python critiques...")

    problem_files = [
        "src/agents/claude_code_integration.py",
        "src/agents/data_aggregator.py",
        "src/agents/hybrid_rotation_api.py",
        "src/agents/funding_agent.py",
        "src/agents/claude_code_orchestrator.py",
        "src/agents/persistent_agent_client.py",
        "src/agents/iterative_subagent_manager.py",
        "src/agents/intelligent_backtest_optimizer.py",
        "src/agents/risk_agent.py",
        "src/agents/hybrid_rotation_system.py",
        "src/agents/rotation_interface.py",
        "src/agents/strategy_library.py",
        "src/agents/strategy_agent.py",
        "src/agents/sentiment_analysis_agent.py",
        "src/algorithms/hyperliquid_mainnet_agent.py",
        "src/algorithms/portfolio_manager.py",
        "src/agents/volatility_tracker.py",
        "src/algorithms/funding_agent.py",
        "src/algorithms/hyperliquid_agent.py",
        "src/data/realtime_backtester.py",
        "src/models/model_factory.py",
        "src/models/groq_model.py",
        "src/models/zai_model.py",
        "src/hyperliquid/websocket.py"
    ]

    corrected_files = []
    total_files = 0

    for py_file in problem_files:
        file_path = Path(py_file)
        if file_path.exists():
            total_files += 1
            if fix_indentation_errors(file_path):
                corrected_files.append(str(file_path))
                print(f"[CORRIGE] {py_file}")
            else:
                print(f"[OK] Pas de correction nécessaire: {py_file}")
        else:
            print(f"[ATTENTION] Fichier non trouvé: {py_file}")

    print(f"\n{'='*60}")
    print("RÉSUMÉ DES CORRECTIONS D'INDENTATION")
    print(f"{'='*60}")
    print(f"Fichiers traités: {total_files}")
    print(f"Fichiers corrigés: {len(corrected_files)}")

    if corrected_files:
        print(f"\nFichiers modifiés:")
        for file in corrected_files:
            print(f"  - {file}")

    print(f"\n[SUCCESS] Correction d'indentation terminée !")

if __name__ == "__main__":
    main()