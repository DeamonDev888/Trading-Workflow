# 🚀 NOVAQUOTE Claude Code Integration

**Implémentation complète des agents NOVAQUOTE avec Claude Code**

Pattern d'utilisation : `claude --agents @.claude/agents/`

---

## ✨ Fonctionnalités

- ✅ **4 agents spécialisés** : Strategy, Risk, Funding, Sentiment
- ✅ **Système d'itération avancé** : 5 stratégies (Progressive, Cross-Validation, etc.)
- ✅ **Délégation automatique** : Via `claude-agents.json`
- ✅ **Python + PowerShell** : Scripts pour les deux plateformes
- ✅ **Monitoring complet** : Rapports, métriques, logs
- ✅ **Boucle autonome** : Exécution continue avec intervalle configurable
- ✅ **Batch processing** : Traitement de multiples tâches
- ✅ **Tests intégrés** : Suite de tests complète

---

## 🎯 Agents Disponibles

| Agent                         | Rôle       | Spécialisation                  | Timeout |
| ----------------------------- | ---------- | ------------------------------- | ------- |
| **claude-strategy-advisor**   | Stratégies | Signaux de trading, backtesting | 120s    |
| **claude-risk-advisor**       | Risques    | Position sizing, stop-loss      | 120s    |
| **claude-funding-advisor**    | Funding    | Arbitrage, taux de funding      | 120s    |
| **claude-sentiment-analyzer** | Sentiment  | Social, news, marché            | 120s    |

---

## 🚀 Démarrage Rapide

### 1. Mode Simple (Agent Unique)

**Python :**

```bash
python scripts/claude_code_agent_runner.py \
  --mode single \
  --agent claude-strategy-advisor \
  --task "Should I buy BTC at $50,000?" \
  --context examples/market_context.json
```

**PowerShell :**

```powershell
.\scripts\claude_code_agents.ps1 -Mode single -Agent "claude-strategy-advisor" -Task "Should I buy BTC?"
```

**Windows Batch :**

```cmd
run_claude_agents.bat
# Puis choisir option 1
```

### 2. Délégation Automatique

**Python :**

```bash
python scripts/claude_code_agent_runner.py \
  --mode delegation \
  --task "Analyze BTC trading opportunity"
```

**PowerShell :**

```powershell
.\scripts\claude_code_agents.ps1 -Mode delegation -Task "Analyze BTC"
```

### 3. Analyse Complète (Tous les Agents)

**Python :**

```bash
python scripts/claude_code_agent_runner.py --mode complete
```

**PowerShell :**

```powershell
.\scripts\claude_code_agents.ps1 -Mode complete
```

**Windows Batch :**

```cmd
run_claude_agents.bat
# Choisir option 3
```

**Résultat :**

```
============================================================
📊 ANALYSIS SUMMARY
============================================================
Total Agents: 4
Converged: 4
Avg Confidence: 0.89
Final Decision: BUY

🤝 Consensus: strategy: 0.89; risk: 0.85; funding: 0.92; sentiment: 0.87
📄 Report saved: reports/claude_code/complete_analysis_1640995380.json
```

### 4. Boucle Autonome (Production)

**Toutes les 5 minutes :**

```bash
python scripts/claude_code_agent_runner.py \
  --mode autonomous \
  --interval 300
```

**PowerShell (service Windows) :**

```powershell
New-Service -Name "NovaQuoteAgents" `
           -BinaryPathName "powershell.exe -ExecutionPolicy Bypass -File .\scripts\claude_code_agents.ps1 -Mode autonomous -IntervalSeconds 300" `
           -DisplayName "NOVAQUOTE Claude Code Agents" `
           -StartupType Automatic

Start-Service NovaQuoteAgents
```

### 5. Tests

```bash
python scripts/test_claude_code_integration.py
```

**Ou via Windows Batch :**

```cmd
run_claude_agents.bat
# Choisir option 6
```

---

## 📁 Structure du Projet

```
projet trading/
├── claude-agents.json                    # Configurateur principal
├── .claude/agents/                       # Agents individuels
│   ├── claude-strategy-advisor.json
│   ├── claude-risk-advisor.json
│   ├── claude-funding-advisor.json
│   └── claude-sentiment-analyzer.json
├── src/agents/
│   ├── claude_code_integration.py        # 🧠 Gestionnaire principal
│   ├── iterative_subagent_manager.py     # 🔄 Système d'itération
│   ├── strategy_agent.py                 # Strategy Agent
│   ├── risk_agent.py                     # Risk Agent
│   ├── funding_agent.py                  # Funding Agent
│   └── sentiment_analysis_agent.py       # Sentiment Agent
├── scripts/
│   ├── claude_code_agent_runner.py       # 🐍 CLI Python
│   ├── claude_code_agents.ps1            # 🔧 PowerShell
│   ├── test_claude_code_integration.py   # 🧪 Tests
│   └── claude_code_subagent.py           # Sub-agent launcher
├── examples/
│   ├── market_context.json               # Exemple de contexte
│   └── tasks_batch.json                  # Exemple de batch
├── reports/
│   ├── agents/                           # Rapports agents
│   ├── claude_code/                      # Rapports délégation
│   └── tests/                            # Rapports tests
└── docs/
    ├── CLAUDE_CODE_INTEGRATION_GUIDE.md  # 📚 Guide complet
    ├── COMMANDS_AGENTS.md                # 📋 Commandes
    └── AGENT_QUICK_START.md              # 🚀 Démarrage rapide
```

---

## 💡 Exemples d'Usage Avancés

### 1. Analyse de Multiple Cryptomonnaies

**Python :**

```bash
# Créer un script batch
for coin in BTC ETH ADA SOL; do
  python scripts/claude_code_agent_runner.py \
    --mode single \
    --agent claude-strategy-advisor \
    --task "Analyze $coin" \
    --context "context_${coin}.json" \
    --no-save
done
```

### 2. PowerShell - Monitoring Continu

```powershell
# Lancer en arrière-plan avec job
$job = Start-Job -ScriptBlock {
  while ($true) {
    & ".\scripts\claude_code_agents.ps1" -Mode complete
    Start-Sleep -Seconds 300
  }
}

# Surveiller
Get-Job

# Arrêter
Stop-Job $job
Remove-Job $job
```

### 3. API Python Directe

```python
from src.agents.claude_code_integration import ClaudeCodeIntegrationManager
from src.agents.iterative_subagent_manager import IterationMode

# Initialiser
manager = ClaudeCodeIntegrationManager()

# Analyse avec itération avancée
result = manager.call_claude_code_agent(
    agent_id="claude-strategy-advisor",
    prompt="Analyze BTC trading opportunity",
    context_data=market_data,
    use_iterations=True,
    iteration_mode=IterationMode.CROSS_VALIDATION
)

# Vérifier le résultat
if result.get("converged", False) and result.get("confidence", 0) > 0.8:
    print(f"✅ Decision: {result['result']['decision']}")
    print(f"📊 Confidence: {result['confidence']:.2f}")
```

### 4. Batch Processing

**Créer `my_tasks.json` :**

```json
[
  {
    "agent": "claude-strategy-advisor",
    "task": "Analyze BTC",
    "context": "btc_context.json",
    "iterations": 3
  },
  {
    "agent": "claude-risk-advisor",
    "task": "Assess risk",
    "context": "portfolio.json",
    "iterations": 2
  }
]
```

**Exécuter :**

```bash
python scripts/claude_code_agent_runner.py \
  --mode batch \
  --tasks-file my_tasks.json
```

---

## 🔬 Système d'Itération

### Stratégies Disponibles

1. **Progressive Refinement** (par défaut) - Affinage progressif avec feedback
2. **Cross Validation** - Validation croisée avec perspectives multiples
3. **Convergence Seeking** - Recherche automatique de convergence
4. **Majority Voting** - Vote majoritaire sur plusieurs itérations
5. **Adaptive Learning** - Apprentissage adaptatif

### Configuration

```json
{
  "iteration_config": {
    "max_iterations": 3,
    "confidence_threshold": 0.85,
    "convergence_threshold": 0.9
  }
}
```

---

## 📊 Monitoring et Rapports

### Emplacement des Rapports

```
reports/
├── agents/                      # Agents individuels
│   ├── claude-strategy-advisor_1640995200.json
│   ├── claude-risk-advisor_1640995290.json
│   └── ...
├── claude_code/                # Délégation
│   └── complete_analysis_1640995380.json
└── tests/                      # Tests
    └── claude_code_integration_test_20251109.json
```

### Contenu Type d'un Rapport

```json
{
  "timestamp": "2025-11-09T10:00:00Z",
  "agent": "claude-strategy-advisor",
  "session_id": "session_20251109_101000",
  "mode": "progressive_refinement",
  "iterations": 3,
  "converged": true,
  "confidence": 0.87,
  "result": {
    "decision": "BUY",
    "reasoning": "Multiple indicators align..."
  },
  "metrics": {
    "stability": 0.92,
    "consistency": 0.88
  },
  "execution_time": 45.23
}
```

---

## ⚙️ Personnalisation

### 1. Modifier un Agent

Éditer `.claude/agents/claude-strategy-advisor.json` :

```json
{
  "temperature": 0.2,
  "max_tokens": 5000,
  "prompt": "Custom prompt here...",
  "iteration_config": {
    "max_iterations": 5,
    "confidence_threshold": 0.9
  }
}
```

### 2. Ajouter un Contexte

Créer `my_context.json` :

```json
{
  "symbol": "ETH-USD",
  "price": 3000,
  "my_custom_data": "value"
}
```

Utiliser :

```bash
--context my_context.json
```

### 3. Créer un Agent Personnalisé

Créer `.claude/agents/my-custom-agent.json` :

```json
{
  "name": "my-custom-agent",
  "description": "My custom agent",
  "model": "sonnet",
  "temperature": 0.3,
  "tools": ["Read", "Bash"],
  "prompt": "You are my custom agent..."
}
```

Utiliser :

```bash
--agent my-custom-agent
```

---

## 🐛 Dépannage Rapide

### ❌ "Agent not found"

```bash
# Vérifier que les fichiers existent
ls .claude/agents/

# Recréer automatiquement
python -c "from src.agents.claude_code_integration import ClaudeCodeIntegrationManager; ClaudeCodeIntegrationManager()._verify_configuration()"
```

### ❌ "Python not found"

```powershell
# PowerShell
$Global:PythonExe = "python3"

# Ou utiliser le chemin complet
$Global:PythonExe = "C:\Python39\python.exe"
```

### ❌ "Low confidence"

- Améliorer le contexte avec plus de données
- Utiliser `CROSS_VALIDATION` au lieu de `PROGRESSIVE_REFINEMENT`
- Augmenter le nombre d'itérations

### ❌ "Timeout"

```json
// Dans la config de l'agent
"timeout_per_iteration": 60  // Réduire à 60s
```

---

## 📈 Performance

### Métriques Cibles

| Métrique            | Cible | Acceptable |
| ------------------- | ----- | ---------- |
| Temps d'exécution   | < 60s | < 120s     |
| Confidence          | > 0.8 | > 0.6      |
| Taux de convergence | > 80% | > 60%      |
| Itérations moyennes | 2-3   | 4-5        |

### Optimisation

```python
# Réduire les itérations en production
config = IterationConfig(max_iterations=2)

# Utiliser le cache
result = manager.get_cached_result(cache_key)

# Parallelisation (future feature)
# result = await manager.run_parallel([agent1, agent2])
```

---

## 🎓 Bonnes Pratiques

### ✅ À Faire

- Utiliser le contexte avec des données réelles
- Surveiller les rapports régulièrement
- Tester avant la production
- Configurer les alertes pour les erreurs
- Sauvegarder les configurations personnalisées

### ❌ À Éviter

- Trop d'itérations (coût élevé)
- Contexte vide ou incomplet
- Exécution en boucle sans monitoring
- Ignorer les warnings de confiance basse
- Modifier les prompts par défaut sans tests

---

## 📚 Documentation Complète

- **Guide Complet** : [`docs/CLAUDE_CODE_INTEGRATION_GUIDE.md`](docs/CLAUDE_CODE_INTEGRATION_GUIDE.md)
- **Commandes** : [`docs/COMMANDS_AGENTS.md`](docs/COMMANDS_AGENTS.md)
- **Démarrage Rapide** : [`docs/AGENT_QUICK_START.md`](docs/AGENT_QUICK_START.md)
- **Architecture** : [`docs/CLAUDE_CODE_ARCHITECTURE.md`](docs/CLAUDE_CODE_ARCHITECTURE.md)

---

## 🆘 Support

**Ressources :**

1. **Tests** : `python scripts/test_claude_code_integration.py`
2. **Logs** : `reports/`
3. **Documentation** : `docs/`
4. **Exemples** : `examples/`

**En cas de problème :**

1. Consulter la [section Dépannage](docs/CLAUDE_CODE_INTEGRATION_GUIDE.md#-dépannage)
2. Lancer les tests
3. Vérifier les logs
4. Ouvrir une issue GitHub

---

## 🎯 Exemples de Workflows

### Workflow 1 : Décision de Trade

```bash
# 1. Analyser le signal
python scripts/claude_code_agent_runner.py \
  --mode single \
  --agent claude-strategy-advisor \
  --task "Is this a good buy signal?" \
  --context market.json

# 2. Si confidence > 0.8, évaluer le risque
python scripts/claude_code_agent_runner.py \
  --mode single \
  --agent claude-risk-advisor \
  --task "What's the risk?" \
  --context market.json

# 3. Exécuter si les deux sont d'accord
```

### Workflow 2 : Monitoring 24/7

```powershell
# Créer un service Windows
New-Service -Name "NovaQuoteAgents" `
           -BinaryPathName "powershell.exe -ExecutionPolicy Bypass -File .\scripts\claude_code_agents.ps1 -Mode autonomous -IntervalSeconds 300" `
           -StartupType Automatic

# Démarrer
Start-Service NovaQuoteAgents

# Surveiller
Get-Service NovaQuoteAgents
Get-EventLog -LogName Application -Source NovaQuoteAgents
```

### Workflow 3 : Analyse de Portefeuille

```bash
# Analyse complète
python scripts/claude_code_agent_runner.py --mode complete

# Le rapport contient :
# - Recommandations par actif
# - Évaluation des risques
# - Optimisation des taux de funding
# - Sentiment du marché
```

---

## 🏆 Fonctionnalités Avancées

### Consensus Multi-Agents

Le système calcule automatiquement un consensus entre tous les agents :

```json
{
  "consensus": {
    "decision": "BUY",
    "avg_confidence": 0.89,
    "agents_agreed": 4,
    "reasoning": "strategy: 0.89; risk: 0.85; funding: 0.92; sentiment: 0.87"
  }
}
```

### Convergence Metrics

Métriques sophistiquées pour chaque session :

```json
{
  "convergence_metrics": {
    "stability": 0.92, // Similarité entre itérations
    "confidence_trend": 0.15, // Amélioration de confiance
    "consistency": 0.88, // Variance en confiance
    "converged": true
  }
}
```

### Cache Intelligent

Le système met en cache les résultats pour optimiser les performances :

```python
# Le cache est automatique
result = manager.call_claude_code_agent(...)
# Si le même appel est refait, utilise le cache
```

---

## 🔐 Sécurité

- **Permissions** : `--dangerously-skip-permissions` pour les agents autorisés uniquement
- **Sandbox** : Isolation des agents dans des environnements séparés
- **Audit** : Logging complet de toutes les actions
- **Validation** : Validation automatique des entrées et sorties

---

## 🚀 Roadmap

- [ ] Parallelisation des agents
- [ ] API REST pour intégration externe
- [ ] Dashboard web temps réel
- [ ] Intégration Telegram/Discord
- [ ] Machine learning pour optimisation automatique
- [ ] Support multi-exchange

---

## 📄 License

NOVAQUOTE Trading System - Claude Code Integration
Built with love by Deamon Dev [ROCKET]

---

## 🙏 Remerciements

- **Anthropic Claude Code** - Plateforme d'agents
- **Claude** - Modèle de langage
- **NOVAQUOTE** - Système de trading

---

**🎯 Happy Trading with Claude Code!**

_Documentation mise à jour : 2025-11-09_
