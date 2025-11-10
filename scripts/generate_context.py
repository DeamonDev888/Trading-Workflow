#!/usr/bin/env python3
"""
🔄 CONTEXT GENERATOR - Automatisation quotidienne du contexte
Génère un context.md à jour avec :
1. Snapshot du projet (arborescence)
2. Analyse Git (changements)
3. Appel Claude pour analyse IA des changements
"""

import re
import subprocess
from pathlib import Path
from datetime import datetime

class ContextGenerator:
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.today = datetime.now().strftime("%Y-%m-%d")

    def run_git_command(self, command):
        """Exécute une commande Git et retourne le résultat"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.root_path
            )
            return result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            return "", str(e)

    def get_git_status(self):
        """Analyse le statut Git"""
        status, _ = self.run_git_command("git status --porcelain")
        return status

    def get_git_log(self, days=7):
        """Récupère les logs Git récents"""
        log, _ = self.run_git_command(f"git log --oneline --since=\"{days} days ago\"")
        return log

    def get_git_diff_stats(self, commits=5):
        """Statistiques des changements"""
        diff, _ = self.run_git_command(f"git diff --stat HEAD~{commits}..HEAD")
        return diff

    def call_claude_for_analysis(self, context_data):
        """Appelle Claude pour analyser les changements avec IA"""

        # Construire le prompt pour Claude
        prompt = f"""
Analyse ces changements du projet trading NOVAQUOTE et génère des insights:

**DATE**: {self.today}

**CHANGEMENTS GIT**:
{context_data['git_status']}

**LOGS RÉCENTS**:
{context_data['git_log']}

**STATS DIFF**:
{context_data['git_diff']}

**ARCHITECTURE**:
- Agents IA: {context_data['agents_count']}
- Algorithmes: {context_data['algorithms_count']}
- Pages Frontend: {context_data['frontend_count']}

Génère une analyse concise (max 300 mots) avec:
1. Impact des changements sur le système
2. Risques identifiés
3. Actions recommandées
4. Opportunités d'amélioration

Sois précis et technique.
"""

        try:
            # Appel Claude avec PowerShell (Windows)
            ps_cmd = f'''
            claude --dangerously-skip-permissions --print --output-format text --model sonnet << "EOF"
{prompt}
EOF
            '''

            process = subprocess.Popen(
                ["powershell", "-Command", ps_cmd],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.root_path
            )

            stdout, stderr = process.communicate(timeout=90)

            if process.returncode == 0:
                return stdout.strip()
            else:
                # Fallback: analyse simple sans Claude
                return self._fallback_analysis(context_data)

        except subprocess.TimeoutExpired:
            return "Timeout: Claude n'a pas répondu dans le temps imparti"
        except Exception as e:
            # Fallback: analyse simple sans Claude
            return self._fallback_analysis(context_data)

    def _fallback_analysis(self, context_data):
        """Analyse de secours si Claude n'est pas disponible"""

        analysis_parts = []

        # Analyser les changements Git
        if context_data['git_status']:
            modified_files = len([line for line in context_data['git_status'].split('\n') if line.strip()])
            analysis_parts.append(f"**Impact Changements**: {modified_files} fichiers modifiés détectés")

        # Analyser les logs
        if context_data['git_log']:
            recent_commits = len([line for line in context_data['git_log'].split('\n') if line.strip()])
            analysis_parts.append(f"**Activité**: {recent_commits} commits récents")

        # Analyser l'évolution de l'architecture
        agents = context_data.get('agents_count', 0)
        algorithms = context_data.get('algorithms_count', 0)
        frontend = context_data.get('frontend_count', 0)

        analysis_parts.append(f"**Architecture**: {agents} agents IA, {algorithms}+ algorithmes, {frontend} pages frontend")

        # Recommandations basiques
        modified_files = len([line for line in context_data['git_status'].split('\n') if line.strip()]) if context_data['git_status'] else 0
        if modified_files > 5:
            analysis_parts.append("**Risque**: Changements multiples - tester avant production")

        if "src/algorithms/" in context_data.get('git_status', ''):
            analysis_parts.append("**Opportunité**: Nouveaux algorithmes détectés - valider les backtests")

        return "\n\n".join(analysis_parts) if analysis_parts else "Analyse de base: Aucun changement significatif détecté"

    def run_project_snapshot(self):
        """Exécute le script de snapshot existant"""
        try:
            snapshot_script = self.root_path / "scripts" / "project_snapshot.py"
            result = subprocess.run(
                ["python", str(snapshot_script)],
                capture_output=True,
                text=True,
                cwd=self.root_path
            )

            if result.returncode == 0:
                # Lire le contexte généré
                context_file = self.root_path / "contexte" / "context_app.md"
                if context_file.exists():
                    with open(context_file, 'r', encoding='utf-8') as f:
                        return f.read()
            return ""
        except Exception as e:
            return f"Erreur snapshot: {str(e)}"

    def extract_counts_from_snapshot(self, snapshot_content):
        """Extrait les compteurs du contenu du snapshot"""
        counts = {
            'agents_count': 0,
            'algorithms_count': 0,
            'frontend_count': 0
        }

        lines = snapshot_content.split('\n')
        for line in lines:
            if 'agents IA véritables' in line:
                match = re.search(r'(\d+)\s+agents IA', line)
                if match:
                    counts['agents_count'] = int(match.group(1))
            elif 'algorithmes de trading ordinaires' in line:
                match = re.search(r'(\d+)\+?\s+algorithmes', line)
                if match:
                    counts['algorithms_count'] = int(match.group(1))
            elif 'pages frontend' in line:
                match = re.search(r'(\d+)\s+pages', line)
                if match:
                    counts['frontend_count'] = int(match.group(1))

        return counts

    def generate_context_file(self):
        """Génère le fichier context.md final"""

        try:
            print("Generation du contexte quotidien...")
        except UnicodeEncodeError:
            print("Generation du contexte quotidien...")

        # 1. Récupérer les données Git
        try:
            print("Analyse des changements Git...")
        except UnicodeEncodeError:
            print("Analyse des changements Git...")
        git_status = self.get_git_status()
        git_log = self.get_git_log()
        git_diff = self.get_git_diff_stats()

        # 2. Exécuter le snapshot du projet
        try:
            print("Generation du snapshot du projet...")
        except UnicodeEncodeError:
            print("Generation du snapshot du projet...")
        snapshot_content = self.run_project_snapshot()
        counts = self.extract_counts_from_snapshot(snapshot_content)

        # 3. Préparer les données pour Claude
        context_data = {
            'git_status': git_status,
            'git_log': git_log,
            'git_diff': git_diff,
            **counts
        }

        # 4. Appeler Claude pour analyse
        try:
            print("Analyse IA avec Claude...")
        except UnicodeEncodeError:
            print("Analyse IA avec Claude...")
        claude_analysis = self.call_claude_for_analysis(context_data)

        # 5. Générer le contexte final
        try:
            print("Generation du contexte final...")
        except UnicodeEncodeError:
            print("Generation du contexte final...")

        context_content = f"""# 🧠 NOVAQUOTE Trading System - Contexte Quotidien

**Dernière mise à jour** : {self.today}
**Version** : Production Live Trading
**Généré par** : generate_context.py + Analyse Claude AI

---

## 🤖 **Analyse IA des Changements (Claude Sonnet)**

{claude_analysis}

---

## 📊 **État Actuel du Système**

### Architecture
- **Agents IA** : {counts['agents_count']} scripts avec appels LLM
- **Algorithmes** : {counts['algorithms_count']}+ scripts de trading purs
- **Pages Frontend** : {counts['frontend_count']} interfaces web
- **Model Factory** : 11 modèles IA disponibles
- **Trading** : HyperLiquid mainnet live

---

## 🔄 **CHANGEMENTS GIT AUJOURD'HUI**

### 📋 **Fichiers Modifiés**
```
{git_status if git_status else "Aucun changement non commité"}
```

### 📈 **Logs Récents**
```
{git_log if git_log else "Aucun commit récent"}
```

### 📊 **Statistiques des Changements**
```
{git_diff if git_diff else "Aucun changement statistique"}
```

---

## 🎯 **Actions Recommandées**

Basé sur l'analyse Claude et les changements détectés :

1. **Revoir les fichiers modifiés** avant commit
2. **Tester les nouvelles fonctionnalités** ajoutées
3. **Valider la régression** sur les composants modifiés
4. **Mettre à jour la documentation** si nécessaire

---

## 📝 **Méthodologie**

Ce contexte est généré par :
1. **project_snapshot.py** : Analyse de l'architecture du code
2. **Git analytics** : Détection des changements source
3. **Claude AI** : Analyse intelligente de l'impact
4. **Synthèse automatisée** : Contexte exploitable

**Pour mise à jour manuelle** : `python scripts/generate_context.py`

---

*Généré automatiquement le {self.today} avec intelligence artificielle*
"""

        # 6. Écrire le fichier final
        context_file = self.root_path / "context.md"
        with open(context_file, 'w', encoding='utf-8') as f:
            f.write(context_content)

        try:
            print(f"Contexte généré : {context_file}")
        except UnicodeEncodeError:
            print(f"Contexte genere : {context_file}")
        return str(context_file)

def main():
    """Point d'entrée principal"""
    generator = ContextGenerator()
    generator.generate_context_file()

if __name__ == "__main__":
    main()