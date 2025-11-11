# 🏗️ Architecture des Agents NOVAQUOTE - Diagramme de Flux

## 📊 Diagramme Complet du Système d'Agents

```mermaid
graph TB
    %% Styles
    classDef master fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef agent fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef script fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef config fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef cli fill:#fce4ec,stroke:#880e4f,stroke-width:2px

    %% Master Components
    subgraph "🎯 MASTER ORCHESTRATOR"
        MO[ClaudeCodeIntegrationManager<br/>src/agents/claude_code_integration.py]
        MA[IterativeSubagentManager<br/>src/agents/iterative_subagent_manager.py]
        MO --> MA
    end

    %% Core Agents
    subgraph "🤖 CORE AGENTS"
        SA[Strategy Advisor<br/>claude-strategy-advisor.json<br/>📈 Analyse signaux & stratégies]
        RA[Risk Advisor<br/>claude-risk-advisor.json<br/>⚠️ Gestion risques & sizing]
        FA[Funding Advisor<br/>claude-funding-advisor.json<br/>💰 Analyse corrélation funding]
        SE[Sentiment Analyzer<br/>claude-sentiment-analyzer.json<br/>📊 Analyse sentiment marché]
    end

    %% Configuration Layer
    subgraph "⚙️ CONFIGURATION LAYER"
        CA[claude-agents.json<br/>.claude/agents/claude-agents.json<br/>Configuration swarm]
        CF[Agent Configs<br/>.claude/agents/*.json<br/>Configs individuelles]
        CA --> CF
    end

    %% Script Interfaces
    subgraph "📜 SCRIPT INTERFACES"
        RA1[claude_code_agent_runner.py<br/>Runner principal avec itérations]
        FA1[funding_agent.py<br/>Agent funding spécialisé]
        OA1[agent_manager.py<br/>Manager générique Python]
        DA1[data_aggregator.py<br/>Agrégation données agents]
    end

    %% CLI Interfaces
    subgraph "💻 CLI INTERFACES"
        C1[claude --agents @claude-agents.json<br/>Délégation automatique]
        C2[claude --agents agent.json<br/>Appel individuel]
        C3[novaquote-cli.bat<br/>Interface interactive Windows]
        C4[novaquote-quick.bat<br/>Commandes rapides]
        C5[novaquote-scan.bat<br/>Scan automatisé]
    end

    %% Workflow Connections
    MO --> SA
    MO --> RA
    MO --> FA
    MO --> SE

    CA --> MO
    CF --> MO

    RA1 --> MO
    FA1 --> FA
    OA1 --> MO
    DA1 --> MO

    C1 --> CA
    C2 --> CF
    C3 --> CA
    C4 --> CF
    C5 --> CA

    %% Data Flow
    SA -.->|"BUY/SELL/HOLD"| MO
    RA -.->|"Risk Assessment"| MO
    FA -.->|"Correlation Analysis"| MO
    SE -.->|"Sentiment Data"| MO

    MO -.->|"Consensus Decision"| RA1
    MO -.->|"Funding Strategy"| FA1

    %% Styling
    class MO,MA master
    class SA,RA,FA,SE agent
    class RA1,FA1,OA1,DA1 script
    class CA,CF config
    class C1,C2,C3,C4,C5 cli
```

## 🔄 Flux de Fonctionnement Détaillé

### **1. Initialisation du Système**
```mermaid
sequenceDiagram
    participant User
    participant Runner
    participant Manager
    participant Config
    participant Agent

    User->>Runner: python claude_code_agent_runner.py --mode complete
    Runner->>Manager: ClaudeCodeIntegrationManager()
    Manager->>Config: Load claude-agents.json
    Config-->>Manager: Agent configurations
    Manager-->>Runner: Ready for execution
```

### **2. Exécution d'Analyse Complète**
```mermaid
sequenceDiagram
    participant Manager
    participant Strategy
    participant Risk
    participant Funding
    participant Sentiment
    participant Consensus

    Manager->>Strategy: Analyze signals & conditions
    Strategy-->>Manager: Decision + Confidence

    Manager->>Risk: Assess portfolio risk
    Risk-->>Manager: Risk metrics + Position sizing

    Manager->>Funding: Analyze correlations
    Funding-->>Manager: Correlation analysis + Regime

    Manager->>Sentiment: Analyze market sentiment
    Sentiment-->>Manager: Sentiment indicators

    Manager->>Consensus: Calculate final decision
    Consensus-->>Manager: BUY/SELL/HOLD + Confidence
```

### **3. Flux de Données par Agent**
```mermaid
flowchart TD
    A[Market Data Input] --> B{Agent Type}

    B -->|Strategy| C[Technical Analysis]
    C --> D[Signal Strength]
    D --> E[BUY/SELL/HOLD]

    B -->|Risk| F[Portfolio Assessment]
    F --> G[Position Sizing]
    G --> H[Stop Loss Levels]

    B -->|Funding| I[Correlation Analysis]
    I --> J[Regime Detection]
    J --> K[OPTIMIZE_HOLD/CLOSE]

    B -->|Sentiment| L[Social Media Analysis]
    L --> M[Market Mood]
    M --> N[Confidence Adjustment]

    E --> O[Consensus Engine]
    H --> O
    K --> O
    N --> O

    O --> P[Final Trading Decision]
```

## 🎯 Points d'Entrée du Système

### **A. Via Scripts Python**
```python
# 1. Runner Principal
python scripts/claude_code_agent_runner.py --mode complete

# 2. Agent Spécialisé
python src/agents/funding_agent.py

# 3. Manager Générique
from src.agents.agent_manager import NovaQuoteAgentManager
manager = NovaQuoteAgentManager()
result = manager.run_agent("funding-advisor", "Analyze BTC correlations")
```

### **B. Via Interface CLI**
```bash
# 1. Délégation Automatique
claude --agents @claude-agents.json --print --dangerously-skip-permissions "Complete analysis"

# 2. Agent Individuel
claude --agents .claude/agents/claude-funding-advisor.json --print --dangerously-skip-permissions "Correlation analysis"

# 3. Scripts Batch Windows
novaquote-cli.bat          # Interface interactive
novaquote-quick.bat all    # Analyse complète
novaquote-scan.bat         # Scan automatisé
```

## 🔧 Architecture Technique

### **Couches du Système**
```
┌─────────────────┐
│   CLI Layer     │ ← Scripts batch, commandes directes
├─────────────────┤
│ Script Layer    │ ← Python runners, managers spécialisés
├─────────────────┤
│ Orchestrator    │ ← ClaudeCodeIntegrationManager
├─────────────────┤
│ Iteration Engine│ ← IterativeSubagentManager
├─────────────────┤
│  Agent Layer    │ ← Sub-agents Claude spécialisés
├─────────────────┤
│ Config Layer    │ ← JSON configurations
└─────────────────┘
```

### **Types d'Exécution**
1. **Synchrone** : Appel direct d'un agent
2. **Itératif** : Amélioration progressive avec convergence
3. **Parallèle** : Exécution simultanée de plusieurs agents
4. **Délégation** : Routage automatique vers agent approprié

### **Gestion d'État**
- **Session Management** : Suivi des itérations par session
- **Convergence Metrics** : Mesure de stabilité des décisions
- **Confidence Scoring** : Niveau de confiance par agent
- **Consensus Calculation** : Agrégation des recommandations

## 📈 Métriques et Monitoring

### **Indicateurs Clés**
- **Convergence Rate** : % d'agents ayant convergé
- **Confidence Average** : Confiance moyenne des décisions
- **Execution Time** : Temps de réponse par agent
- **Success Rate** : Taux de succès des appels

### **Rapports Générés**
- **Analysis Reports** : `reports/claude_code/analysis_*.json`
- **Agent Logs** : `reports/agents/agent_*.json`
- **Performance Metrics** : Métriques d'exécution et convergence

---

## 🎯 Résumé Architecture

Le système NOVAQUOTE utilise une **architecture modulaire multi-couches** avec :

- **4 agents spécialisés** (Strategy, Risk, Funding, Sentiment)
- **3 modes d'accès** (CLI, Scripts Python, API)
- **2 moteurs principaux** (Orchestrateur + Itération)
- **Système de consensus** pour décisions finales

Chaque agent peut être appelé **individuellement** ou **via orchestration complète**, avec support pour **itérations avancées** et **convergence automatique**.

Le **ClaudeCodeIntegrationManager** sert de **chef d'orchestre** coordonnant tous les agents selon les patterns documentés dans `COMMANDS_AGENTS_GUIDE.md`. 🚀
