#!/usr/bin/env python3
"""
NOVAQUOTE Project Snapshot - Génère contexte dynamique basé sur l'analyse réelle
"""

import os
import re
from pathlib import Path

class ProjectSnapshot:
    IGNORED_DIRS = {
        'node_modules', '.git', '__pycache__', '.pytest_cache',
        'venv', 'env', '.env', 'dist', 'build', '.next', '.nuxt',
        'target', 'bin', 'obj', '.vscode', '.idea', 'logs',
        'tmp', 'temp', 'cache', 'caches', '.DS_Store'
    }

    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.ignored_found = set()

    def print_tree(self, dir_path: Path, prefix: str = "", is_last: bool = True):
        try:
            items = sorted(dir_path.iterdir())
        except PermissionError:
            return

        filtered_items = []
        for item in items:
            if item.name.startswith('.') and item.name not in ['.env_example', '.gitignore']:
                continue
            if item.is_dir() and item.name in self.IGNORED_DIRS:
                self.ignored_found.add(str(item.relative_to(self.root_path)))
                continue
            filtered_items.append(item)

        for i, item in enumerate(filtered_items):
            is_last_item = (i == len(filtered_items) - 1)
            connector = "└── " if is_last_item else "├── "

            if item.is_file():
                print(f"{prefix}{connector}{item.name}")
            elif item.is_dir():
                print(f"{prefix}{connector}{item.name}/")
                extension = "    " if is_last_item else "│   "
                self.print_tree(item, prefix + extension, is_last_item)

    def print_tree_to_list(self, dir_path: Path, output_lines: list, prefix: str = "", is_last: bool = True):
        try:
            items = sorted(dir_path.iterdir())
        except PermissionError:
            output_lines.append(f"{prefix}└── [Permission denied]")
            return

        filtered_items = []
        for item in items:
            if item.name.startswith('.') and item.name not in ['.env_example', '.gitignore']:
                continue
            if item.is_dir() and item.name in self.IGNORED_DIRS:
                self.ignored_found.add(str(item.relative_to(self.root_path)))
                continue
            filtered_items.append(item)

        for i, item in enumerate(filtered_items):
            is_last_item = (i == len(filtered_items) - 1)
            connector = "└── " if is_last_item else "├── "

            if item.is_file():
                output_lines.append(f"{prefix}{connector}{item.name}")
            elif item.is_dir():
                output_lines.append(f"{prefix}{connector}{item.name}/")
                extension = "    " if is_last_item else "│   "
                self.print_tree_to_list(item, output_lines, prefix + extension, is_last_item)

    def analyze_codebase(self):
        agents_dir = self.root_path / "src" / "agents"
        models_dir = self.root_path / "src" / "models"
        frontend_dir = self.root_path / "frontend" / "public"
        docs_dir = self.root_path / "docs"

        analysis = {
            "agents_ia": [],
            "algorithmes": [],
            "modeles_ia": [],
            "pages_frontend": [],
            "docs_hyperliquid": [],
            "agent_master": None
        }

        if agents_dir.exists():
            py_files = list(agents_dir.glob("*.py"))
            for py_file in py_files:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Détecter Claude Code sub-agents
                    pattern_subagents = any(re.search(p, content) for p in [
                        r'claude\s+--agent\s+claude-',
                        r'subprocess\.run.*claude',
                        r'claude-risk-advisor',
                        r'claude-strategy-advisor',
                        r'claude-funding-advisor',
                        r'claude-sentiment-advisor',
                        r'--dangerously-skip-permissions',
                    ])

                    has_llm_calls = pattern_subagents

                    if has_llm_calls and py_file.name.endswith('.py'):
                        analysis["agents_ia"].append(py_file.name)
                    else:
                        analysis["algorithmes"].append(py_file.name)

                except Exception:
                    analysis["algorithmes"].append(py_file.name)

        if models_dir.exists():
            analysis["modeles_ia"] = [f.name for f in models_dir.glob("*.py")]

        if frontend_dir.exists():
            analysis["pages_frontend"] = [f.name for f in frontend_dir.glob("*.html")]

        if docs_dir.exists():
            analysis["docs_hyperliquid"] = [f.name for f in docs_dir.glob("*hyperliquid*.md")]

        return analysis

    def create_context_file(self, contexte_dir):
        analysis = self.analyze_codebase()

        context_lines = []
        context_lines.append("---")
        context_lines.append("name: deamon-dev-ai-trading-expert")
        context_lines.append("description: Expert NOVAQUOTE - {} agents IA (Claude Code sub-agents exclusivement), {}+ algorithmes, Claude Code CLI (4 sub-agents), Winston, {} pages, HyperLiquid.".format(
            len(analysis["agents_ia"]), len(analysis["algorithmes"]), len(analysis["pages_frontend"])
        ))
        context_lines.append("---")
        context_lines.append("")
        context_lines.append("# NOVAQUOTE Trading System")
        context_lines.append("")
        context_lines.append("## Définition")
        context_lines.append("- Agent = Script Python avec Claude Code sub-agents")
        context_lines.append("- Algorithme = Script Python ordinary (sans IA)")
        context_lines.append("")
        context_lines.append("## Vue d'ensemble")
        context_lines.append("- {} agents IA véritable (Claude Code sub-agents)".format(len(analysis["agents_ia"])))
        context_lines.append("- {}+ algorithmes trading ordinaires".format(len(analysis["algorithmes"])))
        context_lines.append("- Claude Code CLI: 4 sub-agents (strategy/risk/funding/sentiment)")
        context_lines.append("- Winston logging: 7 loggers")
        context_lines.append("- {} pages frontend".format(len(analysis["pages_frontend"])))
        context_lines.append("- HyperLiquid exchange")
        context_lines.append("")
        context_lines.append("## Structure")
        context_lines.append("```")
        context_lines.append("projet trading/")
        context_lines.append("├── src/agents/            # {} scripts ({} agents + {}+ algorithmes)".format(
            len(analysis["agents_ia"]) + len(analysis["algorithmes"]), len(analysis["agents_ia"]), len(analysis["algorithmes"])))
        context_lines.append("├── src/models/            # Model Factory (anciennement)")
        context_lines.append("├── frontend/public/       # {} pages HTML".format(len(analysis["pages_frontend"])))
        context_lines.append("├── backend/               # server-backend.ts (Port 7000)")
        context_lines.append("├── run.ts                 # Launcher NOVAQUOTE")
        context_lines.append("├── logs/                  # Winston logs (7 types)")
        context_lines.append("└── docs/                  # Documentation")
        context_lines.append("```")
        context_lines.append("")
        context_lines.append("## Agents IA ({} scripts)".format(len(analysis["agents_ia"])))
        context_lines.append("Utilisent **exclusivement Claude Code sub-agents**:")
        context_lines.append("")

        for i, agent in enumerate(sorted(analysis["agents_ia"]), 1):
            context_lines.append("{}. **`{}`** ✅".format(i, agent))
            context_lines.append("   - Claude Code sub-agents")
            context_lines.append("")

        context_lines.append("## Algorithmes ({}+ scripts)".format(len(analysis["algorithmes"])))
        context_lines.append("Scripts Python purs sans IA:")
        context_lines.append("")

        for algo in sorted(analysis["algorithmes"]):
            context_lines.append("- `{}`".format(algo))

        context_lines.append("")
        context_lines.append("## Pattern Claude Code")
        context_lines.append("```python")
        context_lines.append("def call_subagent(self, prompt: str, context_data: dict = None) -> str:")
        context_lines.append('    cmd = ["claude", "--dangerously-skip-permissions", "--agent", self.subagent_name, full_prompt]')
        context_lines.append("    return subprocess.run(cmd, timeout=120).stdout")
        context_lines.append("```")
        context_lines.append("")
        context_lines.append("## Sub-agents")
        context_lines.append("- claude-strategy-advisor - Analyse technique")
        context_lines.append("- claude-risk-advisor - Gestion risque")
        context_lines.append("- claude-funding-advisor - Funding rates")
        context_lines.append("- claude-sentiment-advisor - Sentiment analyse")
        context_lines.append("")
        context_lines.append("## Frontend ({} pages)".format(len(analysis["pages_frontend"])))
        for page in sorted(analysis["pages_frontend"]):
            context_lines.append("- `{}`".format(page))
        context_lines.append("")
        context_lines.append("## Winston Loggers (7)")
        context_lines.append("apiLogger, wsLogger, agentsLogger, backtestsLogger, tradingLogger, walletsLogger, systemLogger")
        context_lines.append("")
        context_lines.append("## API HyperLiquid")
        context_lines.append("- get_all_mids(), get_meta(), get_user_state()")
        context_lines.append("- place_order(), cancel_order()")
        context_lines.append("- get_positions(), get_open_orders()")
        context_lines.append("")
        context_lines.append("## Launcher")
        context_lines.append("run.ts: `ts-node run.ts start|stop|restart|test`")
        context_lines.append("- Backend (Port 7000)")
        context_lines.append("- Frontend (Port 9001)")
        context_lines.append("- WebSocket (Port 7001)")
        context_lines.append("")
        context_lines.append("---")
        context_lines.append("*Basé sur code source réel*")

        with open(contexte_dir / "context_app.md", 'w', encoding='utf-8') as f:
            f.write('\n'.join(context_lines))

    def create_agents_visualization_file(self):
        analysis = self.analyze_codebase()

        viz_lines = []
        viz_lines.append("# Agents IA - Fonctionnement Réel")
        viz_lines.append("")
        viz_lines.append("## Vue d'ensemble ({} agents)".format(len(analysis["agents_ia"])))
        viz_lines.append("")
        viz_lines.append("```mermaid")
        viz_lines.append("graph TD")
        viz_lines.append("    A[Déclencheur] --> B{Risk Agent}")
        viz_lines.append("    A --> C{Strategy Agent}")
        viz_lines.append("    A --> D{Funding Agent}")
        viz_lines.append("    A --> E{Sentiment Agent}")
        viz_lines.append("")
        viz_lines.append("    B --> B1[Appel: claude-risk-advisor]")
        viz_lines.append("    C --> C1[Appel: claude-strategy-advisor]")
        viz_lines.append("    D --> D1[Appel: claude-funding-advisor]")
        viz_lines.append("    E --> E1[Appel: claude-sentiment-advisor]")
        viz_lines.append("")
        viz_lines.append("    B1 --> F[HyperLiquid API]")
        viz_lines.append("    C1 --> F")
        viz_lines.append("    D1 --> F")
        viz_lines.append("    E1 --> F")
        viz_lines.append("")
        viz_lines.append("    F --> G[Position Management]")
        viz_lines.append("    G --> H[Winston Logging]")
        viz_lines.append("```")
        viz_lines.append("")
        viz_lines.append("## Pattern Technique")
        viz_lines.append("```python")
        viz_lines.append("def call_subagent(self, prompt, context_data=None):")
        viz_lines.append('    cmd = ["claude", "--dangerously-skip-permissions", "--agent", self.subagent_name, prompt]')
        viz_lines.append("    return subprocess.run(cmd, timeout=120).stdout")
        viz_lines.append("```")
        viz_lines.append("")
        viz_lines.append("## Architecture")
        viz_lines.append("Market Data → Claude Sub-Agents → Strategy Library → Order Execution")
        viz_lines.append("")
        viz_lines.append("## Métriques")
        for agent in sorted(analysis["agents_ia"]):
            subagent = agent.replace('_agent.py', '').replace('_analysis_agent.py', '')
            viz_lines.append(f"- **{agent}**: Sub-agent claude-{subagent}-advisor")
        viz_lines.append("")
        viz_lines.append("---")
        viz_lines.append("*Claude Code sub-agents exclusivement*")

        docs_dir = self.root_path / "docs"
        docs_dir.mkdir(exist_ok=True)
        with open(docs_dir / "AGENTS_GRAPH_VISUALIZATION.md", 'w', encoding='utf-8') as f:
            f.write('\n'.join(viz_lines))

    def generate_tree(self):
        output_lines = []
        output_lines.append(f"{self.root_path.name}/")
        self.print_tree_to_list(self.root_path, output_lines)

        if self.ignored_found:
            output_lines.append("")
            output_lines.append("ignore:")
            for ignored in sorted(self.ignored_found):
                output_lines.append(f"  - {ignored}/")

        contexte_dir = self.root_path / "contexte"
        contexte_dir.mkdir(exist_ok=True)

        with open(contexte_dir / "arborescence.md", 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))

        self.create_context_file(contexte_dir)
        self.create_agents_visualization_file()

        return output_lines

def main():
    print("\n" + "="*80)
    print("NOVAQUOTE Project Snapshot")
    print("="*80)
    print("\nAnalyse du code source...")

    snapshot = ProjectSnapshot()
    tree = snapshot.generate_tree()

    print("\n" + "="*80)
    print("ANALYSE TERMINÉE - Fichiers générés:")
    print("="*80)
    print("\ncontexte/arborescence.md - Arborescence complète")
    print("contexte/context_app.md - Contexte dynamique NOVAQUOTE")
    print("docs/AGENTS_GRAPH_VISUALIZATION.md - Graphique technique")
    print("\n" + "="*80)
    print("Tip: ts-node run.ts start")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
