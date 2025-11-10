"""
NOVBQUOTE BUG FIXER - VRAI SUB-AGENT TASK CLAUDE CODE

Ce module définit un VRAI sub-agent task pour Claude Code.
Il est utilisé avec task_agent.Task() et a accès aux outils Claude Code.

Utilisation dans Claude Code:
    from novaquote_bug_fixer_task import NOVAQUOTEBugFixerTask
    from task_agent import Task

    task = NOVAQUOTEBugFixerTask(
        target_path="src/",
        max_iterations=3
    )

    agent = Task(
        subagent_type="novaquote_bug_fixer",
        tools=["Read", "Edit", "Bash", "Grep", "Glob"],  # [OK] Outils Claude Code
        prompt=task.generate_prompt(),
        model="sonnet"
    )

    result = await agent.run()
"""

import json
from typing import Any, Dict, List


class NOVAQUOTEBugFixerTask:
    """
    Sub-Agent Task pour corriger le code avec les outils Claude Code
    """

    def __init__(self, target_path: str = "src/", max_iterations: int = 3):
        self.name = "novaquote_bug_fixer"
        self.version = "1.0.0"
        self.target_path = target_path
        self.max_iterations = max_iterations
        self.current_iteration = 0

    def get_metadata(self) -> Dict[str, Any]:
        """Métadonnées du sub-agent task"""
        return {
            "name": self.name,
            "version": self.version,
            "description": "Auto Bug Fixer avec outils Claude Code",
            "tools": ["Read", "Edit", "Bash", "Grep", "Glob"],
            "target_path": self.target_path,
            "max_iterations": self.max_iterations,
        }

    def generate_prompt(self) -> str:
        """
        Génère le prompt pour Claude Code
        Ce prompt utilise LES OUTILS CLAUDE CODE (Read, Edit, Bash, Grep, Glob)
        """
        prompt = f"""
MISSION: Corriger automatiquement le code dans {self.target_path}

INSTRUCTIONS:
Tu es un expert en correction de code. Utilise les outils Claude Code pour:

1. SCAN: Utilise Glob pour trouver tous les fichiers Python/TypeScript
2. LIRE: Utilise Read pour examiner le contenu des fichiers
3. CHERCHER: Utilise Grep pour trouver \
    les problèmes (imports inutiles, erreurs syntax, etc.)
4. CORRIGER: Utilise Edit pour modifier les fichiers directement
5. VÉRIFIER: Utilise Bash pour lancer black, isort, eslint

TYPES DE CORRECTIONS:
- Python: imports inutiles, variables non utilisées, format PEP8, type hints
- TypeScript: types manquants, any, variables non utilisées

PROCESSUS ITÉRATIF:
1. Itération 1: Scanner et corriger les erreurs de syntaxe
2. Itération 2: Corriger les imports et formatage
3. Itération 3: Optimisation et vérifications finales

RÉPONSE ATTENDUE:
- Liste des fichiers modifiés
- Nombre de corrections appliquées
- Résumé des actions

COMMENCE MAINTENANT avec l'outil Glob.
"""
        return prompt

    def get_iteration_prompt(self, iteration: int) -> str:
        """Prompt pour une itération spécifique"""
        prompts = {
            1: "Focus: Syntax errors, unused imports, basic PEP8 issues",
            2: "Focus: Type hints, variable naming, code structure",
            3: "Focus: Final optimizations, linting, clean-up",
        }

        base = self.generate_prompt()
        specific = prompts.get(iteration, "Final cleanup and verification")

        return f"{base}\n\nITÉRATION {iteration}/{self.max_iterations}\n{specific}"


def example_usage():
    """
    EXEMPLE D'UTILISATION DANS CLAUDE CODE

    Dans votre conversation Claude Code, vous faites:
    """

    example_code = """

from novaquote_bug_fixer_task import NOVAQUOTEBugFixerTask
from task_agent import Task

bug_fixer = NOVAQUOTEBugFixerTask(
    target_path="src/",
    max_iterations=3
)

agent = Task(
    subagent_type=bug_fixer.name,
    description="Auto Bug Fixer NOVAQUOTE",
    tools=["Read", "Edit", "Bash", "Grep", "Glob"],  # [OK] Outils Claude Code
    prompt=bug_fixer.generate_prompt(),
    model="sonnet"
)

print("Lancement du sub-agent task...")
result = await agent.run()

print("Résultat:", result)
    """

    print(example_code)


if __name__ == "__main__":
    example_usage()

    task = NOVAQUOTEBugFixerTask(target_path="src/", max_iterations=3)

    print("\n" + "=" * 70)
    print("SUB-AGENT TASK DÉFINI")
    print("=" * 70)
    print(json.dumps(task.get_metadata(), indent=2))
    print("\nPrompt généré:")
    print(task.generate_prompt()[:500] + "...")
