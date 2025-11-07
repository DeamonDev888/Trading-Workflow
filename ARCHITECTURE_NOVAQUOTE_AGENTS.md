# 🤖 NOVAQUOTE Trading System - Architecture Complète des Agents IA

## 📊 Vue d'Ensemble du Système

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    🧠 NOVAQUOTE TRADING SYSTEM ARCHITECTURE                │
│                    Le Chef d'Orchestre : AGENT MASTER                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🏗️ Architecture Globale

```
                            ┌─────────────────────────────┐
                            │      FRONTEND (Port 9000)   │
                            │     Static HTML + CSS        │
                            │        + JavaScript          │
                            └────────────┬────────────────┘
                                         │
                            ┌────────────▼────────────────┐
                            │     BACKEND (Port 7000)     │
                            │  Node.js + Express + WebSocket│
                            └────────────┬────────────────┘
                                         │
                            ┌────────────▼────────────────┐
                            │    🧠 AGENT MASTER (Chef)   │
                            │   src/agents/manager.py     │
                            │   • Coordonne 4 Agents IA   │
                            │   • API REST Management     │
                            │   • CLI Interface           │
                            └────────────┬────────────────┘
                                         │
               ┌────────────────────────┴────────────────────────┐
               │                                                 │
    ┌──────────▼──────────┐                          ┌─────────▼──────────┐
    │ 🛡️  RISK AGENT      │                          │ 💰 FUNDING AGENT   │
    │ src/agents/risk_agent.py │                    │ src/agents/funding_agent.py │
    │ • Utilise Claude/DeepSeek│                    │ • Utilise Claude/DeepSeek│
    │ • Analyse P&L Limits   │                    │ • Monitoring Funding   │
    │ • Gère les arrêts     │                    │ • Détection arbitrages │
    │ d'urgence             │                    │ • Alertes TTS          │
    └──────────┬───────────┘                    └──────────┬──────────┘
               │                                            │
    ┌──────────▼──────────┐                          ┌───────▼──────────────┐
    │ 📊 STRATEGY AGENT   │                          │ 🎭 SENTIMENT AGENT  │
    │ src/agents/strategy_agent.py│                  │ src/agents/sentiment...│
    │ • Utilise Claude    │                          │ • BERT + TTS         │
    │ • Sélectionne       │                          │ • Analyse Twitter   │
    │   stratégies backtestées│                      │ • Détection sentiment│
    │ • Génère signaux    │                          │ • Alertes           │
    │   trading           │                          │                     │
    └─────────────────────┘                          └─────────────────────┘
```

## 🔄 Flux de Données Détaillé

### 1. 📥 Comment les Agents Récupèrent les Données

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    🔄 FLUX DE DONNÉES - AGENT RISK                      │
└─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────┐
    │ config.py       │◄─── Configuration centralisée (AI_MODEL, etc.)
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │ nice_funcs.py   │◄─── Fonctions utilitaires trading
    │ • get_token...  │    • get_token_balance_usd()
    │ • fetch_wallet  │    • fetch_wallet_holdings_og()
    │ • get_data()    │    • get_data() pour OHLCV
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │ HyperLiquid API │◄─── Échange principal (Perpétuels)
    │ • get_positions│    • get_positions()
    │ • get_balance  │    • get_balance()
    │ • place_order  │    • place_order()
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │ 🤖 LLM (IA)     │◄─── Claude ou DeepSeek selon config
    │ • Claude-3-Haiku│    • Anthropic API
    │ • DeepSeek-Chat │    • DeepSeek API
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │ 🛡️ RISK AGENT   │◄─── Analyse avec IA
    │ • should_over...│    • Analyse P&L
    │ • check_pnl...  │    • Recommandations
    │ • handle_limit  │    • Décisions
    └─────────────────┘
```

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  🔄 FLUX DE DONNÉES - AGENT FUNDING                     │
└─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────┐
    │ funding_agent.py│
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │ DeamonDevAPI    │◄─── API client (src/agents/api.py)
    │ • get_funding.. │    • Connect au backend
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │ HyperLiquid API │◄─── Exchange manager
    │ • get_funding   │    • Données Perpetuals
    │ • get_candles   │    • Données OHLCV
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │ 🤖 LLM (IA)     │◄─── DeepSeek ou Claude
    │ • deepseek-chat │    • Analyse funding
    │ • claude-3      │    • Recommandations
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │ OpenAI TTS      │◄─── Synthèse vocale
    │ • tts-1         │    • Alertes audio
    │ • fable voice   │    • Annonces
    └─────────────────┘
```

```
┌─────────────────────────────────────────────────────────────────────────┐
│                🔄 FLUX DE DONNÉES - AGENT STRATEGY                      │
└─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────┐
    │ strategy_agent.py│
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │ Strategy Library│◄─── PROVEN_STRATEGIES
    │ • Funding_Arb.. │    • Backtests validés
    │ • 85% win rate  │    • 19+ stratégies
    │ • 2.5 PF        │    • Profit factor
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │ HyperLiquid     │◄─── Exchange Manager
    │ • get_token..   │    • Données marché
    │ • ai_entry()    │    • Exécution trades
    │ • chunk_kill()  │    • Gestion positions
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │ 🤖 LLM (IA)     │◄─── Claude
    │ • claude-3      │    • Évaluation signaux
    │ • AI_MODEL      │    • Validation
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │ 📊 Signaux      │◄─── BACKTEST PROOF
    │ • EXECUTE/...   │    • Win rate > 60%
    │ • Confidence    │    • Conditions validées
    └─────────────────┘
```

## 👑 L'Agent Master - Le Chef d'Orchestre

### 🎯 Rôle Central

L'**Agent Master** (src/agents/manager.py) est le **vrai chef** qui :

1. **Coordonne** les 3 agents IA principaux
2. **Surveille** leurs performances
3. **Gère** leurs configurations
4. **Contrôle** leurs arrêts/démarrages
5. **Collecte** leurs statistiques

### 📋 API REST du Master

```python
# Les 4 Agents IA dans la config
AGENTS_CONFIG = {
    "risk_agent": {
        "class": "RiskAgent",
        "module": "src.agents.risk_agent",
        "category": "risk",
        "is_ai_agent": True,  # ✅ VRAI agent IA
        "can_trade": True,
    },
    "funding_agent": {
        "class": "FundingAgent",
        "module": "src.agents.funding_agent",
        "category": "analysis",
        "is_ai_agent": True,  # ✅ VRAI agent IA
        "can_trade": False,
    },
    "strategy_agent": {
        "class": "StrategyAgent",
        "module": "src.agents.strategy_agent",
        "category": "strategy",
        "is_ai_agent": True,  # ✅ VRAI agent IA
        "can_trade": False,
    },
    "sentiment_analysis_agent": {
        "class": "SentimentAnalysisAgent",
        "module": "src.agents.sentiment_analysis_agent",
        "category": "analysis",
        "is_ai_agent": True,  # ✅ VRAI agent IA
    },
}
```

### 🔧 Méthodes du Master

| Méthode | Action | Usage |
|---------|--------|-------|
| `get_all_agents()` | Liste les 4 agents | Dashboard |
| `start_agent(agent_id)` | Démarre un agent | Activation |
| `stop_agent(agent_id)` | Arrête un agent | Désactivation |
| `get_agent_status()` | Statut d'un agent | Monitoring |
| `update_agent_config()` | Met à jour config | Configuration |
| `get_agent_statistics()` | Statistiques | Analyse performance |

## 🤖 Model Factory - Le Cerveau IA

### 🧠 8 Modèles IA Disponibles

```
    ┌─────────────────────────────────────────────────────────────┐
    │                🧠 MODEL FACTORY                             │
    │         src/models/model_factory.py                         │
    └─────────────────────────────────────────────────────────────┘

    Modèles Configurés:
    ┌──────────────┬──────────────────┬────────────────────────┐
    │ Type         │ Modèle           │ API Key                 │
    ├──────────────┼──────────────────┼────────────────────────┤
    │ claude       │ claude-3-5-haiku │ ANTHROPIC_KEY          │
    │ openai       │ gpt-4o           │ OPENAI_KEY             │
    │ deepseek     │ deepseek-reasoner│ DEEPSEEK_KEY           │
    │ gemini       │ gemini-2.5-flash │ GEMINI_KEY             │
    │ xai          │ grok-4-fast...   │ GROK_API_KEY           │
    │ zai          │ glm-4.6          │ ZAI_API_KEY            │
    │ groq         │ mixtral-8x7b     │ GROQ_API_KEY (désact.) │
    │ ollama       │ llama3.2         │ Local (désact.)        │
    └──────────────┴──────────────────┴────────────────────────┘
```

### 🔌 Utilisation par les Agents

```python
# Dans chaque agent
from src.models.model_factory import model_factory

# Obtenir un modèle
model = model_factory.get_model("claude", "claude-3-sonnet-20240229")

# Générer une réponse
response = model.generate(
    system_prompt="Tu es un expert trading...",
    user_content="Analyse ce marché...",
    temperature=0.7,
    max_tokens=1024
)
```

## 📊 Communication Frontend ↔ Backend ↔ Agents

### 🖥️ Frontend (Port 9000)

```
    ┌─────────────────────────────────────────┐
    │              FRONTEND                   │
    │              (HTML/CSS/JS)              │
    ├─────────────────────────────────────────┤
    │ • index.html          (Dashboard)      │
    │ • backtest.html       (Backtests)      │
    │ • config.html         (Configuration)  │
    │ • dashboard_ascii.html(ASCII Art)      │
    │ • test_agents.html    (Test agents)    │
    │ • validate_config.html(Validation)     │
    └────────────┬────────────────────────────┘
                 │ HTTP/AJAX
                 ▼
    ┌─────────────────────────────────────────┐
    │          BACKEND (Port 7000)            │
    │         Node.js + Express               │
    └────────────┬────────────────────────────┘
                 │ WebSocket + REST
                 ▼
    ┌─────────────────────────────────────────┐
    │          AGENT MASTER                   │
    │        (Python Process)                 │
    └────────────┬────────────────────────────┘
                 │ Python subprocess
                 ▼
    ┌─────────────────────────────────────────┐
    │        4 AGENTS IA                      │
    │   (Risk, Funding, Strategy,             │
    │    Sentiment)                           │
    └─────────────────────────────────────────┘
```

## 🔄 Flux de Communication Complet

### 1️⃣ Démarrage d'un Agent

```
[Frontend] ──HTTP POST──> [Backend:7000] ──spawn──> [Agent Master] ──> [Agent spécifique]
                                                                          │
                                                                          ▼
                                                                          [LLM API]
                                                                          Anthropic/OpenAI/DeepSeek
```

### 2️⃣ Exécution d'un Agent

```
[Agent] ──> [HyperLiquid API] ──> [Données marché]
               │
               ▼
          [Model Factory] ──> [LLM]
               │
               ▼
       [Décision + Exécution] ──> [Orders] ──> [Backend] ──> [Frontend]
```

### 3️⃣ Monitoring en Temps Réel

```
[Agent Master] ◄─── WebSocket ───┐
                                   │
[Agent Risk] ──── REST ───────────┤
                                   ├─── [Backend] ──> [Frontend]
[Agent Funding] ─── REST ─────────┤
                                   │
[Agent Strategy] ── REST ─────────┘
```

## 📈 Logs et Surveillance

### 🗂️ Système Winston (7 Loggers)

```
    ┌─────────────────────────────────────────┐
    │        7 LOGGERS WINSTON                │
    ├─────────────────────────────────────────┤
    │ 1. apiLogger        - Appels API        │
    │ 2. wsLogger         - WebSocket         │
    │ 3. agentsLogger     - Opérations agents │
    │ 4. backtestsLogger  - Backtests         │
    │ 5. tradingLogger    - Opérations trading│
    │ 6. walletsLogger    - Auth wallets      │
    │ 7. systemLogger     - Surveillance      │
    └─────────────────────────────────────────┘
```

### 📊 Données Traitées

| Agent | Fréquence | Données d'Entrée | Données de Sortie |
|-------|-----------|------------------|-------------------|
| **Risk** | 5 min | P&L, Portfolio, OHLCV | Décisions risque |
| **Funding** | 15 min | Funding rates, Candles | Opportunités |
| **Strategy** | Variable | Backtests, Conditions | Signaux trading |
| **Sentiment** | Variable | Twitter, News | Score sentiment |

## 🎯 Synthèse - Distinction Fondamentale

### ✅ **AGENTS IA (4 scripts avec LLM)**

1. **risk_agent.py** → Appelle Claude/DeepSeek
2. **funding_agent.py** → Appelle Claude/DeepSeek
3. **strategy_agent.py** → Appelle Claude
4. **sentiment_analysis_agent.py** → Appelle BERT + TTS

### ⚙️ **ALGORITHMES (scripts sans IA)**

1. **api.py** → Client API simple
2. **base_agent.py** → Classe de base
3. **intelligent_backtest_optimizer.py** → Backtesting pur
4. **strategy_library.py** → Stratégies validées
5. **manager.py** → Gestionnaire d'agents

### 🧠 **MODEL FACTORY**

- Centralise 8 modèles IA
- Utilisé SEULEMENT par les 4 agents IA
- Configuration dans config.py

---

**🎯 L'Agent Master (manager.py) est le TRUE CHEF qui coordonne tout le système !**
