# 🚀 Commandes des Agents NOVAQUOTE - Guide Complet

## 📁 Agents JSON Créés dans `.claude/agents/`

✅ **5 agents JSON individuels créés :**

- `novaquote-bug-fixer.json`
- `novaquote-code-reviewer.json`
- `novaquote-docs-generator.json`
- `novaquote-perf-optimizer.json`
- `novaquote-test-enhancer.json`

---

## 🎯 Commandes d'Appel des Agents

### **1. Bug Fixer**

```bash
# Appel individuel
claude --agents .claude/agents/novaquote-bug-fixer.json --print --dangerously-skip-permissions "Scan for bugs in src/agents/"

# Tâche spécifique
claude --agents .claude/agents/novaquote-bug-fixer.json --print --dangerously-skip-permissions "Fix the import errors in strategy_agent.py"

# Analyse complète avec permissions
claude --agents .claude/agents/novaquote-bug-fixer.json --print --dangerously-skip-permissions "Analyze and fix all critical issues in the codebase"
```

### **2. Code Reviewer**

```bash
# Appel individuel
claude --agents .claude/agents/novaquote-code-reviewer.json --print --dangerously-skip-permissions "Review the security of the trading system"

# Audit de sécurité
claude --agents .claude/agents/novaquote-code-reviewer.json --print --dangerously-skip-permissions "Check for SQL injection vulnerabilities"

# Audit complet
claude --agents .claude/agents/novaquote-code-reviewer.json --print --dangerously-skip-permissions "Perform comprehensive security audit of all modules"
```

### **3. Documentation Generator**

```bash
# Appel individuel
claude --agents .claude/agents/novaquote-docs-generator.json --print --dangerously-skip-permissions "Generate API documentation"

# Documentation spécifique
claude --agents .claude/agents/novaquote-docs-generator.json --print --dangerously-skip-permissions "Create setup guide for new developers"

# Documentation complète
claude --agents .claude/agents/novaquote-docs-generator.json --print --dangerously-skip-permissions "Generate complete project documentation including all guides"
```

### **4. Performance Optimizer**

```bash
# Appel individuel
claude --agents .claude/agents/novaquote-perf-optimizer.json --print --dangerously-skip-permissions "Optimize database queries"

# Optimisation spécifique
claude --agents .claude/agents/novaquote-perf-optimizer.json --print --dangerously-skip-permissions "Improve trading execution speed"

# Optimisation système
claude --agents .claude/agents/novaquote-perf-optimizer.json --print --dangerously-skip-permissions "Optimize entire system performance including API and algorithms"
```

### **5. Test Enhancer**

```bash
# Appel individuel
claude --agents .claude/agents/novaquote-test-enhancer.json --print --dangerously-skip-permissions "Enhance test coverage"

# Tests spécifiques
claude --agents .claude/agents/novaquote-test-enhancer.json --print --dangerously-skip-permissions "Create unit tests for risk management"

# Suite de tests complète
claude --agents .claude/agents/novaquote-test-enhancer.json --print --dangerously-skip-permissions "Create comprehensive test suite with unit, integration and performance tests"
```

---

## 🔧 Variations de Commandes

### **Avec Fichier JSON Combiné**

```bash
# Utiliser le fichier complet
claude --agents @claude-agents.json --print --dangerously-skip-permissions "I need to review code quality"

# Délégation automatique
claude --agents @claude-agents.json --print --dangerously-skip-permissions "Generate documentation for the API"

# Analyse complète
claude --agents @claude-agents.json --print --dangerously-skip-permissions "Perform complete system analysis and optimization"
```

### **Avec JSON Inline**

```bash
# Bug fixer inline
claude --agents '{
  "novaquote-bug-fixer": {
    "description": "Expert debugging specialist",
    "prompt": "Scan and fix code issues",
    "tools": ["Read", "Edit", "Bash"]
  }
}' --print --dangerously-skip-permissions "Fix syntax errors in the codebase"

# Code reviewer inline
claude --agents '{
  "novaquote-code-reviewer": {
    "description": "Security expert",
    "prompt": "Audit for security vulnerabilities",
    "tools": ["Read", "Grep", "Bash"]
  }
}' --print --dangerously-skip-permissions "Security audit of payment system"
```

### **Multiple Agents**

```bash
# Combiner plusieurs agents
claude --agents .claude/agents/novaquote-bug-fixer.json --agents .claude/agents/novaquote-code-reviewer.json --print --dangerously-skip-permissions "Fix and review the authentication module"

# Workflow complet
claude --agents .claude/agents/novaquote-bug-fixer.json --agents .claude/agents/novaquote-perf-optimizer.json --print --dangerously-skip-permissions "Fix bugs and optimize performance of trading engine"
```

---

## 🎯 Appels par Délégation Automatique

```bash
# Délégation vers bug-fixer
claude --agents @claude-agents.json --print --dangerously-skip-permissions "There are bugs in the trading algorithms that need fixing"

# Délégation vers code-reviewer
claude --agents @claude-agents.json --print --dangerously-skip-permissions "I need a security audit of the payment system"

# Délégation vers docs-generator
claude --agents @claude-agents.json --print --dangerously-skip-permissions "Create comprehensive documentation for the frontend"

# Délégation vers perf-optimizer
claude --agents @claude-agents.json --print --dangerously-skip-permissions "The API responses are too slow, optimize them"

# Délégation vers test-enhancer
claude --agents @claude-agents.json --print --dangerously-skip-permissions "We need more test coverage for the risk management module"
```

---

## 🚀 Appels Explicites

```bash
# Appel explicite par nom
claude --agents @claude-agents.json --print --dangerously-skip-permissions "Use the novaquote-bug-fixer agent to analyze the exchange_manager.py issue"

claude --agents @claude-agents.json --print --dangerously-skip-permissions "Use the novaquote-code-reviewer agent to audit the wallet security"

claude --agents @claude-agents.json --print --dangerously-skip-permissions "Use the novaquote-docs-generator agent to create the README"

claude --agents @claude-agents.json --print --dangerously-skip-permissions "Use the novaquote-perf-optimizer agent to improve database performance"

claude --agents @claude-agents.json --print --dangerously-skip-permissions "Use the novaquote-test-enhancer agent to add integration tests"
```

---

## 📋 Options Supplémentaires

### **Standard (Recommandé)**

```bash
# Toutes les commandes incluent --dangerously-skip-permissions
claude --agents .claude/agents/novaquote-bug-fixer.json --print --dangerously-skip-permissions "Debug the system"
```

### **Avec Sortie Verbose**

```bash
claude --agents .claude/agents/novaquote-bug-fixer.json --print --dangerously-skip-permissions --verbose "Debug the system with detailed output"
```

### **Mode Plan**

```bash
claude --agents .claude/agents/novaquote-docs-generator.json --plan --dangerously-skip-permissions "Create comprehensive documentation plan"
```

---

## 🪟 **Scripts Windows (.bat)**

### **Script Principal : `novaquote-cli.bat`**

```batch
@echo off
setlocal enabledelayedexpansion

echo ====================================
echo     NOVAQUOTE AGENTS CLI v1.0
echo ====================================
echo.

:menu
echo Choisissez l'agent NOVAQUOTE:
echo 1) Bug Fixer - Correction de bugs
echo 2) Code Reviewer - Audit de securite
echo 3) Documentation Generator - Documentation
echo 4) Performance Optimizer - Optimisation
echo 5) Test Enhancer - Tests
echo 6) Analyse Complete - Tous les agents
echo 7) Exit
echo.
set /p choice="Votre choix (1-7): "

if "%choice%"=="1" goto bug-fixer
if "%choice%"=="2" goto code-reviewer
if "%choice%"=="3" goto docs-generator
if "%choice%"=="4" goto perf-optimizer
if "%choice%"=="5" goto test-enhancer
if "%choice%"=="6" goto complete-analysis
if "%choice%"=="7" goto exit
goto menu

:bug-fixer
echo.
set /p task="Tache pour Bug Fixer: "
echo 🐛 Execution Bug Fixer...
claude --agents .claude/agents/novaquote-bug-fixer.json --print --dangerously-skip-permissions "!task!"
pause
goto menu

:code-reviewer
echo.
set /p task="Tache pour Code Reviewer: "
echo 🔒 Execution Code Reviewer...
claude --agents .claude/agents/novaquote-code-reviewer.json --print --dangerously-skip-permissions "!task!"
pause
goto menu

:docs-generator
echo.
set /p task="Tache pour Documentation Generator: "
echo 📚 Execution Documentation Generator...
claude --agents .claude/agents/novaquote-docs-generator.json --print --dangerously-skip-permissions "!task!"
pause
goto menu

:perf-optimizer
echo.
set /p task="Tache pour Performance Optimizer: "
echo ⚡ Execution Performance Optimizer...
claude --agents .claude/agents/novaquote-perf-optimizer.json --print --dangerously-skip-permissions "!task!"
pause
goto menu

:test-enhancer
echo.
set /p task="Tache pour Test Enhancer: "
echo 🧪 Execution Test Enhancer...
claude --agents .claude/agents/novaquote-test-enhancer.json --print --dangerously-skip-permissions "!task!"
pause
goto menu

:complete-analysis
echo.
echo 🔍 Demarrage analyse complete du systeme...
echo 📅 Date: %date% %time%
echo ====================================
echo.

echo 🐛 Etape 1: Bug Fixer...
claude --agents .claude/agents/novaquote-bug-fixer.json --print --dangerously-skip-permissions "Analyse complete du codebase et correction des bugs critiques"

echo.
echo 🔒 Etape 2: Code Reviewer...
claude --agents .claude/agents/novaquote-code-reviewer.json --print --dangerously-skip-permissions "Audit de securite complet du systeme"

echo.
echo ⚡ Etape 3: Performance Optimizer...
claude --agents .claude/agents/novaquote-perf-optimizer.json --print --dangerously-skip-permissions "Optimisation des performances du systeme"

echo.
echo ✅ Analyse complete terminee !
pause
goto menu

:exit
echo Au revoir !
exit /b 0
```

### **Script Rapide : `novaquote-quick.bat`**

```batch
@echo off
if "%1"=="" goto help

if "%1"=="bug" (
    claude --agents .claude/agents/novaquote-bug-fixer.json --print --dangerously-skip-permissions "%~2"
    goto end
)
if "%1"=="review" (
    claude --agents .claude/agents/novaquote-code-reviewer.json --print --dangerously-skip-permissions "%~2"
    goto end
)
if "%1"=="docs" (
    claude --agents .claude/agents/novaquote-docs-generator.json --print --dangerously-skip-permissions "%~2"
    goto end
)
if "%1"=="perf" (
    claude --agents .claude/agents/novaquote-perf-optimizer.json --print --dangerously-skip-permissions "%~2"
    goto end
)
if "%1"=="test" (
    claude --agents .claude/agents/novaquote-test-enhancer.json --print --dangerously-skip-permissions "%~2"
    goto end
)
if "%1"=="all" (
    echo 🔍 Analyse complete...
    claude --agents @claude-agents.json --print --dangerously-skip-permissions "Analyse complete du systeme"
    goto end
)

:help
echo Usage: novaquote-quick.bat [agent] [task]
echo.
echo Agents disponibles:
echo   bug     - Bug Fixer
echo   review  - Code Reviewer
echo   docs    - Documentation Generator
echo   perf    - Performance Optimizer
echo   test    - Test Enhancer
echo   all     - Analyse complete
echo.
echo Exemples:
echo   novaquote-quick.bat bug "Fix import errors"
echo   novaquote-quick.bat review "Security audit"
echo   novaquote-quick.bat all "Complete analysis"

:end
```

### **Script d'Automatisation : `novaquote-scan.bat`**

```batch
@echo off
echo 🔍 Lancement scan automatique NOVAQUOTE...
echo 📅 Date: %date% %time%
echo.

:: Créer répertoire de rapports
if not exist "reports" mkdir reports

set REPORT_FILE=reports\novaquote-scan-%date:~-4,4%%date:~-7,2%%date:~-10,2%.txt

echo Rapport de scan NOVAQUOTE > %REPORT_FILE%
echo ================================ >> %REPORT_FILE%
echo Date: %date% %time% >> %REPORT_FILE%
echo. >> %REPORT_FILE%

echo 🐛 Etape 1: Bug Fixer...
echo [Bug Fixer] Analyse des bugs... >> %REPORT_FILE%
claude --agents .claude/agents/novaquote-bug-fixer.json --print --dangerously-skip-permissions "Analyse complete du codebase pour bugs et erreurs" >> %REPORT_FILE% 2>&1

echo.
echo 🔒 Etape 2: Code Reviewer...
echo [Code Reviewer] Audit de securite... >> %REPORT_FILE%
claude --agents .claude/agents/novaquote-code-reviewer.json --print --dangerously-skip-permissions "Audit securite complete du systeme" >> %REPORT_FILE% 2>&1

echo.
echo ⚡ Etape 3: Performance Optimizer...
echo [Performance] Optimisation... >> %REPORT_FILE%
claude --agents .claude/agents/novaquote-perf-optimizer.json --print --dangerously-skip-permissions "Optimisation performances" >> %REPORT_FILE% 2>&1

echo.
echo ✅ Scan termine ! Rapport sauvegarde dans: %REPORT_FILE%
echo.
pause
```

---

## 🔗 **Intégration avec Scripts Python**

### **Exemple : Gestion des Agents et Réponses**

```python
# src/agents/agent_manager.py
import subprocess
import json
import datetime
from pathlib import Path

class NovaQuoteAgentManager:
    def __init__(self, project_path):
        self.project_path = Path(project_path)
        self.agents_path = self.project_path / ".claude" / "agents"
        self.reports_path = self.project_path / "reports"
        self.reports_path.mkdir(exist_ok=True)

    def run_agent(self, agent_name, task, save_report=True):
        """
        Exécute un agent NOVAQUOTE et récupère sa réponse

        Args:
            agent_name (str): Nom de l'agent (bug-fixer, code-reviewer, etc.)
            task (str): Tâche à effectuer
            save_report (bool): Sauvegarder le rapport

        Returns:
            dict: Résultat de l'exécution avec sortie et statut
        """
        agent_file = self.agents_path / f"novaquote-{agent_name}.json"

        if not agent_file.exists():
            return {"error": f"Agent {agent_name} non trouvé", "status": "error"}

        cmd = [
            "claude",
            "--agents", str(agent_file),
            "--print",
            "--dangerously-skip-permissions",
            task
        ]

        try:
            print(f"🚀 Exécution de l'agent {agent_name}...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_path
            )

            response = {
                "agent": agent_name,
                "task": task,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "timestamp": datetime.datetime.now().isoformat(),
                "status": "success" if result.returncode == 0 else "error"
            }

            if save_report:
                self._save_report(response)

            return response

        except Exception as e:
            return {
                "agent": agent_name,
                "task": task,
                "error": str(e),
                "status": "exception",
                "timestamp": datetime.datetime.now().isoformat()
            }

    def _save_report(self, response):
        """Sauvegarde le rapport de l'agent"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{response['agent']}_report_{timestamp}.json"
        report_file = self.reports_path / filename

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(response, f, indent=2, ensure_ascii=False)

        print(f"📄 Rapport sauvegardé: {report_file}")

    def analyze_file(self, file_path, agent_type="code-reviewer"):
        """
        Analyse un fichier spécifique avec un agent

        Args:
            file_path (str): Chemin du fichier à analyser
            agent_type (str): Type d'agent à utiliser

        Returns:
            dict: Résultat de l'analyse
        """
        task = f"Analyser le fichier {file_path} pour identifier les problèmes"
        return self.run_agent(agent_type, task)

    def fix_issues(self, file_path=None):
        """Utilise le bug-fixer pour corriger les problèmes"""
        if file_path:
            task = f"Corriger les problèmes dans le fichier {file_path}"
        else:
            task = "Analyser et corriger les problèmes dans tout le codebase"

        return self.run_agent("bug-fixer", task)

    def generate_docs(self, component=None):
        """Génère la documentation"""
        if component:
            task = f"Générer la documentation pour {component}"
        else:
            task = "Générer la documentation complète du projet"

        return self.run_agent("docs-generator", task)

# Exemple d'utilisation
if __name__ == "__main__":
    manager = NovaQuoteAgentManager("C:/Users/Deamon/Desktop/Backup/Trade/projet trading")

    # Analyser un fichier spécifique
    print("🔍 Analyse de risk_agent.py...")
    result = manager.analyze_file("src/agents/risk_agent.py")
    print(f"Statut: {result['status']}")
    print(f"Sortie: {result['stdout'][:500]}...")

    # Corriger les bugs
    print("\n🐛 Correction des bugs...")
    bug_result = manager.fix_issues()
    print(f"Statut: {bug_result['status']}")

    # Générer la documentation
    print("\n📚 Génération de la documentation...")
    docs_result = manager.generate_docs()
    print(f"Statut: {docs_result['status']}")
```

### **Exemple : Intégration avec risk_agent.py**

```python
# src/agents/risk_agent.py (modifié pour intégration)
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_manager import NovaQuoteAgentManager

class RiskAgent:
    def __init__(self, project_path):
        self.manager = NovaQuoteAgentManager(project_path)

    def analyze_risk_logic(self):
        """Analyse la logique de gestion des risques"""
        print("🔍 Analyse de la logique de gestion des risques...")

        # Utiliser le code-reviewer pour analyser la sécurité
        result = self.manager.run_agent(
            "code-reviewer",
            "Analyser la logique de gestion des risques dans risk_agent.py pour identifier les vulnérabilités et erreurs de logique"
        )

        return result

    def optimize_risk_calculations(self):
        """Optimise les calculs de risque"""
        print("⚡ Optimisation des calculs de risque...")

        result = self.manager.run_agent(
            "perf-optimizer",
            "Optimiser les performances des calculs de risque dans risk_agent.py"
        )

        return result

    def create_risk_tests(self):
        """Crée des tests pour le module de risque"""
        print("🧪 Création des tests pour le module de risque...")

        result = self.manager.run_agent(
            "test-enhancer",
            "Créer une suite de tests complète pour risk_agent.py incluant les cas limites et tests d'intégration"
        )

        return result

    def fix_risk_issues(self):
        """Corrige les problèmes dans le module de risque"""
        print("🐛 Correction des problèmes dans risk_agent.py...")

        result = self.manager.run_agent(
            "bug-fixer",
            "Analyser et corriger tous les problèmes dans risk_agent.py"
        )

        return result

# Point d'entrée pour le script
if __name__ == "__main__":
    project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    risk_agent = RiskAgent(project_path)

    print("🚀 Lancement de l'analyse complète du Risk Agent...")

    # Analyse de la logique de risque
    logic_result = risk_agent.analyze_risk_logic()

    # Correction des problèmes
    fix_result = risk_agent.fix_risk_issues()

    # Optimisation
    perf_result = risk_agent.optimize_risk_calculations()

    # Création des tests
    test_result = risk_agent.create_risk_tests()

    print("\n✅ Analyse complète terminée !")
    print(f"Logique: {logic_result['status']}")
    print(f"Corrections: {fix_result['status']}")
    print(f"Performance: {perf_result['status']}")
    print(f"Tests: {test_result['status']}")
```

---

## 💡 Conseils d'Usage

1. **Agents individuels JSON** : Pour tâches spécifiques et ciblées
2. **Fichier combiné** : Pour délégation automatique et workflows complexes
3. **Appel explicite** : Quand vous voulez un agent spécifique
4. **JSON inline** : Pour tests rapides et configurations temporaires

## ⚠️ **Important : --dangerously-skip-permissions**

**Toutes les commandes incluent `--dangerously-skip-permissions` pour :**

- ✅ Éviter les blocages de permissions
- ✅ Permettre aux agents d'exécuter des modifications
- ✅ Assurer le fonctionnement optimal avec les outils
- ✅ Activer l'accès complet aux fichiers et bash

**Usage recommandé pour les agents NOVAQUOTE :**

```bash
# Format standard pour tous les appels
claude --agents [AGENT_FILE] --print --dangerously-skip-permissions "Tâche spécifique"
```

---

## 📑 **Récapitulatif des Commandes Principales**

### **Plus Utilisées**

```bash
# Bug Fixer - Analyse et correction
claude --agents .claude/agents/novaquote-bug-fixer.json --print --dangerously-skip-permissions "Fix critical issues"

# Code Reviewer - Audit de sécurité
claude --agents .claude/agents/novaquote-code-reviewer.json --print --dangerously-skip-permissions "Security audit"

# Documentation Generator - Documentation complète
claude --agents .claude/agents/novaquote-docs-generator.json --print --dangerously-skip-permissions "Generate docs"

# Performance Optimizer - Optimisation
claude --agents .claude/agents/novaquote-perf-optimizer.json --print --dangerously-skip-permissions "Optimize performance"

# Test Enhancer - Tests
claude --agents .claude/agents/novaquote-test-enhancer.json --print --dangerously-skip-permissions "Enhance tests"
```

### **Workflow Complet**

```bash
# Analyse complète avec délégation automatique
claude --agents @claude-agents.json --print --dangerously-skip-permissions "Complete system analysis and optimization"
```

### **Scripts Windows**

```batch
# Interface interactive
novaquote-cli.bat

# Commandes rapides
novaquote-quick.bat bug "Fix import errors"
novaquote-quick.bat review "Security audit"

# Scan automatique
novaquote-scan.bat
```

### **Python Integration**

```python
# Via le manager
manager = NovaQuoteAgentManager(project_path)
result = manager.run_agent("bug-fixer", "Fix issues in risk_agent.py")
```

**Toutes ces commandes fonctionnent avec les agents JSON créés dans `.claude/agents/` !** 🎯
