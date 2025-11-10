# 🚀 Guide d'Intégration Claude Code - NOVAQUOTE

**Documentation complète pour l'utilisation des agents NOVAQUOTE avec Claude Code**

Pattern d'utilisation : `claude --agents @.claude/agents/`

---

## 📋 Table des Matières

1. [Vue d'ensemble](#-vue-densemble)
2. [Structure des Fichiers](#-structure-des-fichiers)
3. [Utilisation avec Python](#-utilisation-avec-python)
4. [Utilisation avec PowerShell](#-utilisation-avec-powershell)
5. [Exemples d'Usage](#-exemples-dusage)
6. [Patterns Avancés](#-patterns-avancés)
7. [Monitoring et Rapports](#-monitoring-et-rapports)
8. [Dépannage](#-dépannage)

---

## 🎯 Vue d'ensemble

### Architecture

```
NOVAQUOTE Trading System
├── claude-agents.json (configurateur principal)
├── .claude/agents/ (agents individuels)
│   ├── claude-strategy-advisor.json
│   ├── claude-risk-advisor.json
│   ├── claude-funding-advisor.json
│   └── claude-sentiment-analyzer.json
├── src/agents/
│   ├── claude_code_integration.py (gestionnaire principal)
│   └── iterative_subagent_manager.py (système d'itération)
└── scripts/
    ├── claude_code_agent_runner.py (CLI Python)
    ├── claude_code_agents.ps1 (PowerShell)
    └── test_claude_code_integration.py (tests)
```

### Agents Disponibles

| Agent                       | Rôle       | Spécialisation             | Timeout |
| --------------------------- | ---------- | -------------------------- | ------- |
| `claude-strategy-advisor`   | Stratégies | Signaux, backtesting       | 120s    |
| `claude-risk-advisor`       | Risques    | Position sizing, stop-loss | 120s    |
| `claude-funding-advisor`    | Funding    | Arbitrage, taux            | 120s    |
| `claude-sentiment-analyzer` | Sentiment  | Social, news, Twitter      | 120s    |

---

## 📁 Structure des Fichiers

### 1. Fichier Principal `claude-agents.json`

Configuration combinée pour délégation automatique :

```json
{
  "swarm_metadata": {
    "name": "NOVAQUOTE Trading Agents",
    "version": "1.0"
  },
  "agents": [
    {
      "id": "claude-strategy-advisor",
      "name": "Strategy Advisor",
      "description": "Analyse les signaux de trading...",
      "tools": ["Read", "Edit", "Bash", "Grep"],
      "model": "sonnet",
      "temperature": 0.3,
      "max_tokens": 4000
    }
  ]
}
```

### 2. Agents Individuels `.claude/agents/`

Chaque agent a sa configuration dédiée avec :

- Prompt spécialisé
- Outils autorisés
- Configuration d'itération
- Métadonnées

### 3. Gestionnaire Principal

`src/agents/claude_code_integration.py` :

- Orchestration des appels
- Système d'itération avancé
- Consensus et métriques
- Reporting automatisé

---

## 🐍 Utilisation avec Python

### Installation

```bash
cd /path/to/novaquote
pip install -r requirements.txt
```

### Script Principal : `claude_code_agent_runner.py`

#### Mode 1 : Agent Unique

```bash
python scripts/claude_code_agent_runner.py \
  --mode single \
  --agent claude-strategy-advisor \
  --task "Analyze BTC trading opportunity" \
  --iterations 3 \
  --context examples/market_context.json
```

**Output :**

```
============================================================
🚀 Running Agent: claude-strategy-advisor
============================================================

📋 Loaded context from: examples/market_context.json
✅ Agent completed in 45.23s
📊 Confidence: 0.87
🔄 Iterations: 3
🎯 Converged successfully!
💾 Report saved: reports/agents/claude-strategy-advisor_1640995200.json
```

#### Mode 2 : Délégation Automatique

```bash
python scripts/claude_code_agent_runner.py \
  --mode delegation \
  --task "Should I buy BTC at $50,000?" \
  --context examples/market_context.json
```

Utilise `claude-agents.json` pour déléguer automatiquement au bon agent.

#### Mode 3 : Analyse Complète

```bash
python scripts/claude_code_agent_runner.py \
  --mode complete \
  --context examples/market_context.json
```

Lance tous les agents et calcule un consensus.

**Output :**

```
============================================================
🎯 Complete NOVAQUOTE Analysis
============================================================

[1/4] Strategy Analysis...
[2/4] Risk Assessment...
[3/4] Funding Optimization...
[4/4] Sentiment Analysis...

============================================================
📊 ANALYSIS SUMMARY
============================================================
Total Agents: 4
Converged: 4
Avg Confidence: 0.89
Final Decision: BUY

🤝 Consensus: strategy: 0.89; risk: 0.85; funding: 0.92; sentiment: 0.87
```

#### Mode 4 : Batch Processing

```bash
python scripts/claude_code_agent_runner.py \
  --mode batch \
  --tasks-file examples/tasks_batch.json
```

Exécute plusieurs tâches séquentiellement.

#### Mode 5 : Boucle Autonome

```bash
# Exécuter toutes les 5 minutes, 10 itérations max
python scripts/claude_code_agent_runner.py \
  --mode autonomous \
  --interval 300 \
  --max-iterations 10 \
  --context examples/market_context.json

# Illimité, intervalle 15 minutes
python scripts/claude_code_agent_runner.py \
  --mode autonomous \
  --interval 900
```

### API Python Avancée

```python
from src.agents.claude_code_integration import ClaudeCodeIntegrationManager

# Initialiser
manager = ClaudeCodeIntegrationManager()

# Appel direct
result = manager.call_claude_code_agent(
    agent_id="claude-strategy-advisor",
    prompt="Analyze this trade",
    context_data=market_data,
    use_iterations=True,
    iteration_mode=IterationMode.PROGRESSIVE_REFINEMENT
)

# Délégation automatique
delegation = manager.delegate_to_claude_agents(
    task="Should I buy BTC?",
    context_data=market_data
)

# Analyse complète
analysis = manager.run_complete_trading_analysis(market_data)

# Sauvegarder rapport
report_path = manager.save_analysis_report(analysis, "my_report.json")
```

---

## 🔧 Utilisation avec PowerShell

### Script PowerShell : `claude_code_agents.ps1`

#### Prérequis

```powershell
# Vérifier Python
python --version

# Si pas installé, télécharger depuis : https://python.org
```

#### Exemples d'Usage

##### 1. Agent Unique

```powershell
.\scripts\claude_code_agents.ps1 -Mode single -Agent "claude-strategy-advisor" -Task "Analyze BTC" -Iterations 3
```

##### 2. Délégation

```powershell
.\scripts\claude_code_agents.ps1 -Mode delegation -Task "Should I buy BTC?" -ContextFile "examples\market_context.json"
```

##### 3. Analyse Complète

```powershell
.\scripts\claude_code_agents.ps1 -Mode complete
```

##### 4. Batch

```powershell
.\scripts\claude_code_agents.ps1 -Mode batch -TasksFile "examples\tasks_batch.json"
```

##### 5. Boucle Autonome

```powershell
# 5 minutes interval, 10 iterations max
.\scripts\claude_code_agents.ps1 -Mode autonomous -IntervalSeconds 300 -MaxIterations 10

# 15 minutes interval, unlimited
.\scripts\claude_code_agents.ps1 -Mode autonomous -IntervalSeconds 900
```

##### 6. Sans Sauvegarde (test rapide)

```powershell
.\scripts\claude_code_agents.ps1 -Mode single -Agent "claude-risk-advisor" -Task "Quick check" -NoSave
```

##### 7. Verbose Output

```powershell
.\scripts\claude_code_agents.ps1 -Mode complete -Verbose
```

#### Automatisation Windows

##### Service Windows

```powershell
# Créer un service
$serviceName = "NovaQuoteClaudeAgents"
$scriptPath = "C:\Path\to\novaquote\scripts\claude_code_agents.ps1"

New-Service -Name $serviceName `
           -BinaryPathName "powershell.exe -ExecutionPolicy Bypass -File `"$scriptPath`" -Mode autonomous -IntervalSeconds 300" `
           -DisplayName "NOVAQUOTE Claude Code Agents" `
           -StartupType Automatic

Start-Service $serviceName
```

##### Tâche Planifiée

```powershell
# Exécuter toutes les heures
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
    -Argument "-ExecutionPolicy Bypass -File C:\Path\to\novaquote\scripts\claude_code_agents.ps1 -Mode complete"

$trigger = New-ScheduledTaskTrigger -Once -At 00:00 -RepetitionInterval (New-TimeSpan -Hours 1)

Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "NovaQuoteAgents"
```

---

## 💡 Exemples d'Usage

### 1. Analyse de Trade Simple

**Commande :**

```bash
python scripts/claude_code_agent_runner.py \
  --mode single \
  --agent claude-strategy-advisor \
  --task "Should I buy 0.1 BTC at $50,000 with 2x leverage?" \
  --context examples/market_context.json
```

**Réponse-type :**

```json
{
  "decision": "BUY",
  "confidence": 0.87,
  "reasoning": "Multiple factors align: oversold RSI, bullish MACD, positive funding rate...",
  "execution_details": {
    "position_size": "10% of portfolio",
    "stop_loss": "$47,500 (-5%)",
    "take_profit": "$52,500 (+5%)"
  }
}
```

### 2. Audit de Risque Complet

**Commande :**

```bash
python scripts/claude_code_agent_runner.py \
  --mode complete \
  --context examples/market_context.json
```

**Affiche :**

- ✅ 4 agents activés
- 🎯 Converged: 3/4
- 📊 Avg Confidence: 0.85
- 🎯 Final Decision: BUY
- 📄 Rapport sauvegardé

### 3. Optimisation Funding Rate

**Commande :**

```bash
python scripts/claude_code_agent_runner.py \
  --mode single \
  --agent claude-funding-advisor \
  --task "Should I hold my long position to collect funding?" \
  --context examples/market_context.json
```

### 4. Monitoring Continu (Production)

**PowerShell :**

```powershell
# Lancer en arrière-plan
$job = Start-Job -ScriptBlock {
  while ($true) {
    & ".\scripts\claude_code_agents.ps1" -Mode complete -ContextFile "market_data.json"
    Start-Sleep -Seconds 300
  }
}

# Vérifier le statut
Get-Job

# Arrêter
Stop-Job $job
Remove-Job $job
```

---

## 🔬 Patterns Avancés

### Système d'Itération

Le système utilise 5 stratégies d'itération :

#### 1. Progressive Refinement (par défaut)

```python
# Affinage progressif avec feedback
result = manager.call_claude_code_agent(
    agent_id="claude-strategy-advisor",
    prompt="...",
    iteration_mode=IterationMode.PROGRESSIVE_REFINEMENT
)
```

#### 2. Cross Validation

```python
# Validation croisée avec perspectives multiples
result = manager.call_claude_code_agent(
    agent_id="claude-strategy-advisor",
    prompt="...",
    iteration_mode=IterationMode.CROSS_VALIDATION
)
```

#### 3. Convergence Seeking

```python
# Recherche de convergence automatique
result = manager.call_claude_code_agent(
    agent_id="claude-strategy-advisor",
    prompt="...",
    iteration_mode=IterationMode.CONVERGENCE_SEEKING
)
```

### Personnalisation des Agents

Modifier `.claude/agents/claude-strategy-advisor.json` :

```json
{
  "temperature": 0.2,
  "max_tokens": 5000,
  "iteration_config": {
    "max_iterations": 5,
    "confidence_threshold": 0.9
  }
}
```

### Contexte Personnalisé

Créer un fichier de contexte :

```json
{
  "symbol": "ETH-USD",
  "price": 3000,
  "my_custom_field": "my_value"
}
```

Utiliser :

```bash
python scripts/claude_code_agent_runner.py \
  --mode single \
  --agent claude-strategy-advisor \
  --task "Analyze ETH" \
  --context my_context.json
```

---

## 📊 Monitoring et Rapports

### Emplacement des Rapports

```
reports/
├── agents/
│   ├── claude-strategy-advisor_1640995200.json
│   └── claude-risk-advisor_1640995290.json
├── claude_code/
│   └── complete_analysis_1640995380.json
└── tests/
    └── claude_code_integration_test_20251109.json
```

### Contenu d'un Rapport

```json
{
  "timestamp": "2025-11-09T10:00:00Z",
  "agent": "claude-strategy-advisor",
  "task": "Analyze BTC trading",
  "execution_time": 45.23,
  "result": {
    "decision": "BUY",
    "confidence": 0.87,
    "converged": true,
    "iterations": 3
  },
  "convergence_metrics": {
    "stability": 0.92,
    "consistency": 0.88,
    "final_confidence": 0.87
  }
}
```

### Monitoring Temps Réel

**PowerShell :**

```powershell
# Surveiller les nouveaux rapports
Get-Content -Path "reports\claude_code\*.json" -Wait -Tail 10
```

**Python :**

```python
import json
import glob

for report_file in glob.glob("reports/agents/*.json"):
    with open(report_file) as f:
        report = json.load(f)
        if report.get("converged", False):
            print(f"✅ {report['agent']} converged")
```

---

## 🐛 Dépannage

### Problèmes Courants

#### 1. "Agent not found"

**Problème :**

```
Agent claude-strategy-advisor not found
```

**Solution :**

```bash
# Vérifier que les fichiers existent
ls .claude/agents/

# Si manquant, les créer automatiquement
python -c "from src.agents.claude_code_integration import ClaudeCodeIntegrationManager; ClaudeCodeIntegrationManager()._verify_configuration()"
```

#### 2. "Python not found"

**Problème :**

```
'python' is not recognized
```

**Solution :**

```powershell
# Utiliser python3
$Global:PythonExe = "python3"

# Ou utiliser le chemin complet
$Global:PythonExe = "C:\Python39\python.exe"
```

#### 3. "Permission denied"

**Problème :**

```
PermissionError: Access denied
```

**Solution :**

```bash
# Sur Linux/Mac
chmod +x scripts/claude_code_agent_runner.py
chmod +x scripts/claude_code_agents.ps1

# Sur Windows (PowerShell en admin)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 4. "Timeout" dans les agents

**Problème :**

```
Timeout calling claude-strategy-advisor
```

**Solution :**

```python
# Réduire le timeout dans la config
"timeout_per_iteration": 60  # Au lieu de 120

# Ou réduire les itérations
--iterations 2  # Au lieu de 3
```

#### 5. "Low confidence"

**Problème :**

```
Confidence: 0.45 (too low)
```

**Solution :**

```python
# Améliorer le contexte
# Ajouter plus de données dans le contexte
# Utiliser CROSS_VALIDATION pour plus de robustesse
```

### Debug Mode

```bash
# Mode verbose
python scripts/claude_code_agent_runner.py --mode complete --verbose

# PowerShell
.\scripts\claude_code_agents.ps1 -Mode complete -Verbose
```

### Logs Détaillés

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📈 Exemples de Workflows

### Workflow 1 : Décision de Trade

```python
from src.agents.claude_code_integration import ClaudeCodeIntegrationManager

manager = ClaudeCodeIntegrationManager()

# 1. Analyser le signal
strategy = manager.call_claude_code_agent(
    agent_id="claude-strategy-advisor",
    prompt="Is this a good buy signal?",
    context_data=market_data
)

# 2. Évaluer le risque
risk = manager.call_claude_code_agent(
    agent_id="claude-risk-advisor",
    prompt="What's the risk?",
    context_data={**market_data, "strategy": strategy}
)

# 3. Décider
if strategy.confidence > 0.8 and risk.confidence > 0.8:
    print("EXECUTE TRADE")
else:
    print("WAIT")
```

### Workflow 2 : Monitoring Automatique

```powershell
# Script de monitoring 24/7
while ($true) {
    $result = & ".\scripts\claude_code_agents.ps1" -Mode complete

    if ($result.decision -eq "BUY" -and $result.confidence -gt 0.9) {
        # Envoyer notification
        Send-MailMessage -To "trader@email.com" -Subject "High Confidence Buy Signal"

        # Logger
        Add-Content -Path "trades.log" -Value "$(Get-Date): BUY signal detected"
    }

    Start-Sleep -Seconds 300  # 5 minutes
}
```

### Workflow 3 : Batch Analysis

```bash
# Analyser 10 cryptomonnaies
for coin in BTC ETH ADA SOL MATIC DOT AVAX LINK UNI; do
  python scripts/claude_code_agent_runner.py \
    --mode single \
    --agent claude-strategy-advisor \
    --task "Analyze $coin" \
    --context "context_${coin}.json" \
    --no-save
done
```

---

## 🎓 Bonnes Pratiques

### 1. Gestion des Coûts

```python
# Limiter les itérations en production
config = IterationConfig(max_iterations=2)  # Au lieu de 5

# Utiliser le cache
manager = ClaudeCodeIntegrationManager()
result = manager.get_cached_result(cache_key)
```

### 2. Robustesse

```python
# Toujours vérifier le succès
result = manager.call_claude_code_agent(...)
if not result.get("success"):
    # Fallback vers une autre méthode
    pass
```

### 3. Monitoring

```python
# Logger toutes les exécutions
import logging
logging.info(f"Agent {agent} executed, confidence: {confidence}")
```

### 4. Tests

```bash
# Lancer la suite de tests avant déploiement
python scripts/test_claude_code_integration.py
```

---

## 📚 Ressources

- **Documentation Claude Code** : https://code.claude.com
- **Source Code** : `src/agents/claude_code_integration.py`
- **Tests** : `scripts/test_claude_code_integration.py`
- **Exemples** : `examples/`
- **Rapports** : `reports/`

---

## 🆘 Support

En cas de problème :

1. Consulter la section [Dépannage](#-dépannage)
2. Vérifier les logs dans `reports/`
3. Lancer les tests : `python scripts/test_claude_code_integration.py`
4. Ouvrir une issue sur GitHub

---

**🎯 Happy Trading with Claude Code!** 🚀

_Built with love by Deamon Dev_
