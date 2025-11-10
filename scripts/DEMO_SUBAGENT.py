"""
EXEMPLE D'UTILISATION D'UN SUB-AGENT CLAUDE CODE

Ce script montre COMMENT utiliser un sub-agent task dans Claude Code
"""

def demo_subagent_usage():
    """
    COMMENT utiliser un sub-agent task dans Claude Code :

    1. Le sub-agent EST un script Python définissant les outils
    2. Il EST INVOQUÉ par Claude Code avec accès aux outils
    3. Claude Code utilise SES propres outils (Read, Edit, Bash)
    """

    print("="*70)
    print("VRAIE UTILISATION D'UN SUB-AGENT CLAUDE CODE")
    print("="*70)

    code_example = '''

from task_agent import Task

agent = Task(
    subagent_type="novaquote_bug_fixer",
    description="Fix code in src/ with 3 iterations",
    tools=["Read", "Edit", "Bash", "Grep", "Glob"],  # ← Outils Claude Code
    prompt="""
    Fix all code issues in src/:
    1. Use Read/Glob to scan files
    2. Use Grep to find issues
    3. Use Edit to fix them
    4. Use Bash to run linters
    Repeat until clean or 3 iterations
    """,
    model="sonnet"  # ou "haiku" pour rapide
)

result = await agent.run()

print(result)

    print(code_example)

    print("\n" + "="*70)
    print("DÉFINITION DU SUB-AGENT TASK")
    print("="*70)

    definition = '''

class BugFixerSubAgent:
    def __init__(self):
        self.name = "novaquote_bug_fixer"
        self.description = "Auto Bug Fixer"
        self.tools = ["Read", "Edit", "Bash", "Grep", "Glob"]
        self.iteration_count = 0
        self.max_iterations = 5

    async def run(self, path="src/"):
        """Exécute le sub-agent - Claude Code utilise SES outils"""


        for i in range(self.max_iterations):
            files = await glob(f"{path}/**/*.py")

            issues = await grep(r"import.*unused", files)

            for file, line in issues:
                await Edit(file, old, new)

        return {"status": "done", "files_fixed": x}
    '''

    print(definition)

    print("\n" + "="*70)
    print("AVANTAGES DU VRAI SUB-AGENT")
    print("="*70)

    advantages = '''
✅ Accès DIRECT aux outils Claude Code (Read, Edit, Bash)
✅ Pas besoin de subprocess ou communication externe
✅ Claude Code lit/édite LES VRAIS fichiers
✅ Intégration native avec l'environment Claude Code
✅ Permissions Claude Code automatiquement appliquées
✅ Accès à l'historique et contexte de la session
    '''

    print(advantages)

if __name__ == "__main__":
    demo_subagent_usage()
