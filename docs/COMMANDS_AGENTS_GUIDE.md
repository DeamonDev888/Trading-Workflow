# 🚀 Guide Complet des Agents NOVAQUOTE

## 📋 Table des Matières

1. [Configuration des Agents](#configuration-des-agents)
2. [Scripts Windows (.bat)](#scripts-windows-bat)
3. [Intégration Python](#intégration-python)
4. [Exemples Pratiques](#exemples-pratiques)
5. [Optimisations et Bonnes Pratiques](#optimisations-et-bonnes-pratiques)

---

## 🎯 Configuration des Agents

### **Agents JSON Créés dans `.claude/agents/`**

✅ **5 agents JSON individuels prêts à l'emploi :**

- `novaquote-bug-fixer.json` - Expert debugging
- `novaquote-code-reviewer.json` - Code review & sécurité
- `novaquote-docs-generator.json` - Documentation
- `novaquote-perf-optimizer.json` - Optimisation performance
- `novaquote-test-enhancer.json` - Tests & couverture

### **Format de Commande Standard**

```bash
# Format recommandé pour tous les appels
claude --agents .claude/agents/[AGENT_FILE].json --print --dangerously-skip-permissions "Tâche spécifique"
```

**Pourquoi `--dangerously-skip-permissions` ?**

- ✅ Évite les blocages de permissions
- ✅ Permet aux agents d'exécuter des modifications
- ✅ Assure le fonctionnement optimal avec les outils
- ✅ Active l'accès complet aux fichiers et bash

---

## 🪟 Scripts Windows (.bat)

### **1. `novaquote-cli.bat` - Interface Interactive Complète**

**Usage :**

```batch
# Lancer l'interface interactive
novaquote-cli.bat
```

**Fonctionnalités :**

- 🎛️ Menu interactif pour choisir l'agent
- ⌨️ Saisie personnalisée des tâches
- 🔄 Navigation entre les agents
- 📊 Affichage du statut d'exécution

**Code du script :**

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

### **2. `novaquote-quick.bat` - Commandes Rapides**

**Usage :**

```batch
# Correction de bugs
novaquote-quick.bat bug "Fix import errors in strategy_agent.py"

# Audit de sécurité
novaquote-quick.bat review "Security audit of wallet management"

# Documentation
novaquote-quick.bat docs "Generate API documentation"

# Performance
novaquote-quick.bat perf "Optimize database queries"

# Tests
novaquote-quick.bat test "Create unit tests for risk management"

# Analyse complète
novaquote-quick.bat all "Complete system analysis"
```

**Code du script :**

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

### **3. `novaquote-scan.bat` - Automatisation avec Rapports**

**Usage :**

```batch
# Scan automatique complet avec rapports
novaquote-scan.bat
```

**Fonctionnalités :**

- 📁 Création automatique du dossier `reports/`
- 📊 Génération de rapports datés
- 🔄 Exécution séquentielle des agents
- 💾 Sauvegarde des résultats dans des fichiers texte

**Code du script :**

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

## 🐍 Intégration Python

### **`src/agents/agent_manager.py` - Manager Complet**

Ce script Python permet de gérer les agents NOVAQUOTE programmatiquement, récupérer leurs réponses et les intégrer dans d'autres scripts.

#### **Installation et Configuration**

```python
# Installation automatique du chemin
import sys
import os
from pathlib import Path

# Ajouter le chemin du projet
current_file = Path(__file__).resolve()
project_path = current_file.parent.parent.parent
sys.path.append(str(project_path))
```

#### **Usage de Base**

```python
from src.agents.agent_manager import NovaQuoteAgentManager

# Initialiser le manager
manager = NovaQuoteAgentManager("C:/Users/Deamon/Desktop/Backup/Trade/projet trading")

# Utiliser un agent spécifique
result = manager.run_agent("bug-fixer", "Fix import errors in strategy_agent.py")
print(f"Statut: {result['status']}")
print(f"Sortie: {result['stdout']}")
```

#### **Méthodes Disponibles**

```python
# Analyse d'un fichier spécifique
result = manager.analyze_file("src/agents/risk_agent.py", "code-reviewer")

# Correction de problèmes
result = manager.fix_issues("src/agents/risk_agent.py")

# Audit de sécurité
result = manager.security_audit("src/wallet/")

# Optimisation de performance
result = manager.optimize_performance("src/database/")

# Génération de documentation
result = manager.generate_docs("API endpoints")

# Amélioration des tests
result = manager.enhance_tests("src/trading/")

# Analyse complète avec tous les agents
results = manager.complete_analysis()
```

#### **Gestion des Réponses**

Chaque appel d'agent retourne un dictionnaire structuré :

```python
{
    "agent": "bug-fixer",
    "task": "Fix import errors in strategy_agent.py",
    "stdout": "Résultat complet de l'agent...",
    "stderr": "Erreurs éventuelles...",
    "returncode": 0,
    "timestamp": "2025-11-09T21:30:00.000000",
    "status": "success"  # ou "error"
}
```

---

## 📚 Exemples Pratiques

### **Exemple 1 : Intégration avec `risk_agent.py`**

**Scénario :** On veut analyser, corriger et optimiser le module de gestion des risques.

```python
# src/agents/risk_agent_enhanced.py
import sys
import os
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(str(Path(__file__).parent.parent.parent))

from agent_manager import NovaQuoteAgentManager

class EnhancedRiskAgent:
    def __init__(self, project_path=None):
        if project_path is None:
            project_path = Path(__file__).parent.parent.parent
        self.manager = NovaQuoteAgentManager(project_path)
        self.project_path = project_path

    def comprehensive_analysis(self):
        """
        Analyse complète du module de risque avec tous les agents

        Returns:
            dict: Résultats complets de l'analyse
        """
        print("🚀 Lancement analyse complète du Risk Agent...")

        results = {}

        # 1. Analyse et correction des bugs
        print("🐛 Étape 1: Bug Fixer pour risk_agent.py")
        bug_result = self.manager.run_agent(
            "bug-fixer",
            "Analyser et corriger tous les problèmes dans src/agents/risk_agent.py"
        )
        results['bug_fixer'] = bug_result

        # 2. Audit de sécurité du module de risque
        print("🔒 Étape 2: Audit de sécurité")
        security_result = self.manager.run_agent(
            "code-reviewer",
            "Audit de sécurité complet de risk_agent.py : vérifier la logique de gestion des risques, les validations d'entrée, et les calculs de position"
        )
        results['security'] = security_result

        # 3. Optimisation des performances
        print("⚡ Étape 3: Optimisation performance")
        perf_result = self.manager.run_agent(
            "perf-optimizer",
            "Optimiser les performances des calculs de risque dans risk_agent.py : algorithmes, boucles, utilisation mémoire"
        )
        results['performance'] = perf_result

        # 4. Création de tests
        print("🧪 Étape 4: Tests complets")
        test_result = self.manager.run_agent(
            "test-enhancer",
            "Créer une suite de tests complète pour risk_agent.py : tests unitaires, tests d'intégration, cas limites, tests de charge"
        )
        results['tests'] = test_result

        # 5. Documentation du module
        print("📚 Étape 5: Documentation")
        docs_result = self.manager.run_agent(
            "docs-generator",
            "Générer la documentation complète pour risk_agent.py : API, exemples d'utilisation, architecture"
        )
        results['documentation'] = docs_result

        # Résumé des résultats
        self._print_summary(results)

        return results

    def _print_summary(self, results):
        """Affiche un résumé des résultats"""
        print("\n" + "="*50)
        print("📊 RÉSUMÉ DE L'ANALYSE RISK_AGENT.PY")
        print("="*50)

        for agent, result in results.items():
            status_icon = "✅" if result.get('status') == 'success' else "❌"
            agent_name = agent.replace('_', ' ').title()
            print(f"{status_icon} {agent_name}: {result.get('status', 'unknown')}")

            # Afficher un extrait des résultats
            if result.get('stdout') and len(result['stdout']) > 100:
                print(f"   📄 {result['stdout'][:100]}...")

        print("="*50)
        print("🎯 Analyse terminée ! Consultez les rapports dans /reports/")

    def quick_fix(self, issue_description):
        """Correction rapide d'un problème spécifique"""
        print(f"🔧 Correction rapide : {issue_description}")

        task = f"Corriger le problème suivant dans risk_agent.py : {issue_description}"
        result = self.manager.run_agent("bug-fixer", task)

        print(f"Statut : {result.get('status')}")
        if result.get('stdout'):
            print(f"Solution : {result['stdout']}")

        return result

    def validate_risk_logic(self):
        """Validation spécifique de la logique de risque"""
        print("🔍 Validation de la logique de gestion des risques...")

        task = """
        Valider la logique de gestion des risques dans risk_agent.py :
        1. Vérifier les calculs de position sizing
        2. Valider les limites de risque
        3. Contrôler la logique de stop-loss
        4. Vérifier la gestion du drawdown
        5. Analyser les scénarios de crise
        """

        result = self.manager.run_agent("code-reviewer", task)
        return result

# Point d'entrée principal
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Enhanced Risk Agent with NOVAQUOTE integration")
    parser.add_argument("--action", choices=["analyze", "fix", "validate", "quick"],
                       default="analyze", help="Action à effectuer")
    parser.add_argument("--issue", help="Description du problème à corriger")

    args = parser.parse_args()

    # Initialiser l'agent
    risk_agent = EnhancedRiskAgent()

    if args.action == "analyze":
        # Analyse complète
        results = risk_agent.comprehensive_analysis()

    elif args.action == "fix" and args.issue:
        # Correction spécifique
        result = risk_agent.quick_fix(args.issue)

    elif args.action == "validate":
        # Validation de la logique
        result = risk_agent.validate_risk_logic()
        print(f"Validation : {result.get('status')}")

    elif args.action == "quick":
        # Analyse rapide
        result = risk_agent.manager.analyze_file("src/agents/risk_agent.py")
        print(f"Analyse rapide : {result.get('status')}")
        if result.get('stdout'):
            print(result['stdout'][:500] + "...")

    else:
        print("Usage: python risk_agent_enhanced.py --action [analyze|fix|validate|quick] [--issue 'description']")
```

#### **Usage du Script Enhanced Risk Agent**

```bash
# Analyse complète du module de risque
python src/agents/risk_agent_enhanced.py --action analyze

# Correction rapide d'un problème
python src/agents/risk_agent_enhanced.py --action fix --issue "Import error for exchange_manager"

# Validation de la logique de risque
python src/agents/risk_agent_enhanced.py --action validate

# Analyse rapide
python src/agents/risk_agent_enhanced.py --action quick
```

### **Exemple 2 : Workflow d'Intégration Continue**

```python
# scripts/ci_pipeline.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.agents.agent_manager import NovaQuoteAgentManager

def run_ci_pipeline():
    """Pipeline CI/CD avec agents NOVAQUOTE"""

    manager = NovaQuoteAgentManager(Path(__file__).parent.parent)

    print("🔄 Démarrage Pipeline CI/CD NOVAQUOTE...")

    # Étape 1 : Vérification des bugs
    print("1️⃣ Vérification des bugs...")
    bug_check = manager.fix_issues()
    if bug_check['status'] != 'success':
        print("❌ Échec de la vérification des bugs")
        return False

    # Étape 2 : Audit de sécurité
    print("2️⃣ Audit de sécurité...")
    security_check = manager.security_audit()
    if security_check['status'] != 'success':
        print("❌ Échec de l'audit de sécurité")
        return False

    # Étape 3 : Tests
    print("3️⃣ Vérification des tests...")
    test_check = manager.enhance_tests()

    # Étape 4 : Performance
    print("4️⃣ Vérification des performances...")
    perf_check = manager.optimize_performance()

    print("✅ Pipeline CI/CD terminé avec succès !")
    return True

if __name__ == "__main__":
    success = run_ci_pipeline()
    sys.exit(0 if success else 1)
```

### **Exemple 3 : Monitoring et Rapports**

```python
# scripts/daily_monitor.py
import datetime
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.agents.agent_manager import NovaQuoteAgentManager

def daily_health_check():
    """Check quotidien de santé du projet"""

    manager = NovaQuoteAgentManager(Path(__file__).parent.parent)

    print(f"🏥 Check quotidien NOVAQUOTE - {datetime.date.today()}")

    # Analyse rapide des agents critiques
    critical_agents = ["src/agents/risk_agent.py", "src/agents/strategy_agent.py"]

    report = {
        "date": datetime.date.today().isoformat(),
        "status": "healthy",
        "issues": [],
        "recommendations": []
    }

    for agent_file in critical_agents:
        print(f"🔍 Analyse de {agent_file}...")

        result = manager.analyze_file(agent_file)

        if result['status'] != 'success':
            report["status"] = "unhealthy"
            report["issues"].append(f"Problem in {agent_file}: {result.get('error', 'Unknown error')}")
        else:
            print(f"✅ {agent_file} : OK")

    # Rapport final
    print(f"\n📊 Statut final : {report['status']}")

    if report["issues"]:
        print("❌ Problèmes détectés :")
        for issue in report["issues"]:
            print(f"   • {issue}")
    else:
        print("✅ Aucun problème détecté")

    return report

if __name__ == "__main__":
    report = daily_health_check()
```

---

## 🚀 Optimisations et Bonnes Pratiques

### **1. Gestion des Performances**

```python
# Pour les gros projets, utiliser le mode asynchrone
import asyncio
import concurrent.futures

class OptimizedAgentManager(NovaQuoteAgentManager):
    def __init__(self, project_path, max_workers=3):
        super().__init__(project_path)
        self.max_workers = max_workers

    def parallel_analysis(self, agents_tasks):
        """Exécution parallèle de plusieurs agents"""

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []

            for agent_name, task in agents_tasks.items():
                future = executor.submit(self.run_agent, agent_name, task)
                futures.append((agent_name, future))

            results = {}
            for agent_name, future in futures:
                try:
                    result = future.result(timeout=300)  # 5 minutes max
                    results[agent_name] = result
                except Exception as e:
                    results[agent_name] = {"error": str(e), "status": "timeout"}

            return results
```

### **2. Cache des Résultats**

```python
import json
import hashlib
from pathlib import Path

class CachedAgentManager(NovaQuoteAgentManager):
    def __init__(self, project_path, cache_dir="cache"):
        super().__init__(project_path)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def _get_cache_key(self, agent_name, task):
        """Générer une clé de cache unique"""
        content = f"{agent_name}:{task}"
        return hashlib.md5(content.encode()).hexdigest()

    def run_agent(self, agent_name, task, save_report=True, use_cache=True):
        """Exécuter un agent avec cache"""

        if use_cache:
            cache_key = self._get_cache_key(agent_name, task)
            cache_file = self.cache_dir / f"{cache_key}.json"

            if cache_file.exists():
                print(f"📄 Utilisation du cache pour {agent_name}")
                with open(cache_file, 'r') as f:
                    return json.load(f)

        # Exécuter normalement si pas de cache
        result = super().run_agent(agent_name, task, save_report)

        # Sauvegarder dans le cache
        if use_cache and result.get('status') == 'success':
            cache_key = self._get_cache_key(agent_name, task)
            cache_file = self.cache_dir / f"{cache_key}.json"

            with open(cache_file, 'w') as f:
                json.dump(result, f)

        return result
```

### **3. Monitoring et Logging**

```python
import logging
from datetime import datetime

class MonitoredAgentManager(NovaQuoteAgentManager):
    def __init__(self, project_path, log_file="agent_monitoring.log"):
        super().__init__(project_path)

        # Configuration du logging
        self.logger = logging.getLogger("NovaQuoteAgents")
        self.logger.setLevel(logging.INFO)

        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def run_agent(self, agent_name, task, save_report=True):
        """Exécuter un agent avec monitoring"""

        start_time = datetime.now()
        self.logger.info(f"Début exécution agent {agent_name} pour tâche: {task[:50]}...")

        result = super().run_agent(agent_name, task, save_report)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        self.logger.info(f"Fin exécution agent {agent_name} - Statut: {result['status']} - Durée: {duration:.2f}s")

        if result['status'] != 'success':
            self.logger.error(f"Erreur agent {agent_name}: {result.get('error', 'Unknown error')}")

        return result
```

### **4. Interface Web (Optionnel)**

```python
# scripts/web_interface.py
from flask import Flask, request, jsonify
from src.agents.agent_manager import NovaQuoteAgentManager

app = Flask(__name__)
manager = NovaQuoteAgentManager(".")

@app.route('/api/agent/<agent_name>', methods=['POST'])
def run_agent_api(agent_name):
    """API REST pour exécuter les agents"""

    data = request.json
    task = data.get('task', '')

    if not task:
        return jsonify({"error": "Task required"}), 400

    result = manager.run_agent(agent_name, task)

    return jsonify(result)

@app.route('/api/analyze', methods=['POST'])
def analyze_file_api():
    """API pour analyser un fichier"""

    data = request.json
    file_path = data.get('file_path', '')
    agent_type = data.get('agent_type', 'code-reviewer')

    if not file_path:
        return jsonify({"error": "File path required"}), 400

    result = manager.analyze_file(file_path, agent_type)

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

### **5. Scripts d'Automatisation Avancés**

```batch
REM advanced_workflow.bat - Workflow avancé

@echo off
echo 🔧 Workflow avancé NOVAQUOTE
echo.

REM Étape 1 : Backup
echo 💾 Backup du codebase...
if not exist "backups" mkdir backups
xcopy /E /I /Y src backups\src_%date:~-4,4%%date:~-7,2%%date:~-10,2%_

REM Étape 2 : Analyse complète
echo 🔍 Analyse complète avec agents...
python src/agents/agent_manager.py complete

REM Étape 3 : Vérification spécifique des modules critiques
echo 🎯 Vérification modules critiques...
python src/agents/risk_agent_enhanced.py --action validate
python src/agents/agent_manager.py analyze src/agents/strategy_agent.py

REM Étape 4 : Rapport de synthèse
echo 📊 Génération rapport de synthèse...
python scripts/daily_monitor.py > reports\synthesis_%date:~-4,4%%date:~-7,2%%date:~-10,2%.txt

echo ✅ Workflow avancé terminé !
pause
```

---

## 📖 Résumé des Commandes

### **Scripts Windows**

```batch
# Interface interactive
novaquote-cli.bat

# Commandes rapides
novaquote-quick.bat bug "Fix import errors"
novaquote-quick.bat review "Security audit"
novaquote-quick.bat docs "Generate API docs"
novaquote-quick.bat perf "Optimize performance"
novaquote-quick.bat test "Create unit tests"
novaquote-quick.bat all "Complete analysis"

# Automatisation
novaquote-scan.bat
```

### **Python**

```python
# Via le manager
python src/agents/agent_manager.py complete
python src/agents/agent_manager.py analyze src/agents/risk_agent.py
python src/agents/agent_manager.py fix src/agents/risk_agent.py

# Via l'enhanced risk agent
python src/agents/risk_agent_enhanced.py --action analyze
python src/agents/risk_agent_enhanced.py --action fix --issue "Description"
python src/agents/risk_agent_enhanced.py --action validate

# CI/CD
python scripts/ci_pipeline.py

# Monitoring
python scripts/daily_monitor.py
```

### **CLI Direct**

```bash
# Commandes directes Claude
claude --agents .claude/agents/novaquote-bug-fixer.json --print --dangerously-skip-permissions "Fix issues"

# Avec fichier combiné
claude --agents @claude-agents.json --print --dangerously-skip-permissions "Complete analysis"
```

---

## 🎯 Recommandations Finales

1. **Commencer avec les scripts Windows** pour faciliter l'adoption
2. **Utiliser l'intégration Python** pour les workflows complexes
3. **Mettre en place le monitoring** pour suivre la performance
4. **Automatiser les analyses régulières** avec les scripts batch
5. **Documenter les workflows** spécifiques à votre projet

**Les agents NOVAQUOTE sont maintenant complètement intégrés et prêts à optimiser votre projet de trading !** 🚀
