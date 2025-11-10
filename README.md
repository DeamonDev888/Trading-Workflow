# 🚀 NOVAQUOTE Trading System

**Expert System de Trading IA avec 4 agents spécialisés et 10+ algorithmes performants**

> 🎯 **Objectif** : Système de trading automatisé professionnel sur HyperLiquid avec analyse intelligente et gestion des risques

**📖 Navigation rapide** : [Documentation](#-navigation-documentation) • [Agents IA](#-agents-ia-4-scripts) • [Installation](#-utilisation-rapide)

---

## 📋 Vue d'ensemble

### Architecture Principale

- **4 Agents IA** avec Claude Code sub-agents exclusivement
- **10+ Algorithmes** de trading Python ordinaires (sans IA)
- **Frontend 6 pages** avec Dashboard temps réel
- **Backend Node.js** avec API REST et WebSocket
- **Integration HyperLiquid** pour trading réel
- **Système de logging Winston** à 7 niveaux

### distinction Agent vs Algorithme

- **Agent** = Script Python avec Claude Code sub-agents (IA)
- **Algorithme** = Script Python ordinary (logique pure)

---

## 🏗️ Architecture Complète

```
projet trading/
├── 📁 src/
│   ├── 🤖 agents/                    # 11 scripts agents + algorithmes
│   │   ├── funding_agent.py         # Agent IA funding rates
│   │   ├── risk_agent.py            # Agent IA gestion risque
│   │   ├── sentiment_analysis_agent.py # Agent IA sentiment
│   │   ├── strategy_agent.py        # Agent IA stratégie
│   │   ├── manager.py               # Agent master coordinateur
│   │   ├── api.py                   # Utilitaires API
│   │   ├── base_agent.py           # Agent de base
│   │   ├── intelligent_backtest_optimizer.py # Optimiseur backtest
│   │   ├── master_agent.py         # Agent principal
│   │   └── strategy_library.py     # Bibliothèque stratégies
│   │
│   ├── 🧮 algorithms/               # Algorithmes trading purs
│   │   ├── funding_agent.py        # Algorithme funding
│   │   ├── hyperliquid_agent.py    # Connexion HyperLiquid
│   │   ├── portfolio_manager.py    # Gestion portefeuille
│   │   └── risk_agent.py           # Algorithme risque
│   │
│   ├── 🔌 hyperliquid/             # API HyperLiquid
│   │   ├── client.py               # Client Python
│   │   ├── hyperliquid-api.js      # API Node.js
│   │   └── websocket.py            # WebSocket client
│   │
│   ├── 🧠 models/                   # Model Factory pour IA
│   │   ├── claude_model.py         # Claude AI
│   │   ├── openai_model.py         # OpenAI GPT
│   │   └── model_factory.py        # Factory pattern
│   │
│   ├── 💼 wallet/                   # Gestion wallets
│   │   ├── api_wallet_manager.py   # Manager API
│   │   ├── signature_engine.py     # Moteur signatures
│   │   └── wallet_registry.py      # Registre wallets
│   │
│   ├── 📊 data/                     # Données et backtests
│   │   ├── production_backtests/   # Résultats backtests
│   │   ├── funding/               # Données funding
│   │   ├── sentiment/             # Données sentiment
│   │   └── market_database/       # Base de données marché
│   │
│   ├── 🛡️ core/                     # Cœur système
│   │   ├── circuit-breaker.ts     # Protection système
│   │   ├── retry-manager.ts       # Gestion réessais
│   │   └── websocket-manager.ts   # Manager WebSocket
│   │
│   └── 📝 logging/                  # Système de logs
│       ├── structured-logger.js   # Logger structuré
│       └── structured-logger.ts   # Logger TypeScript
│
├── 🌐 frontend/
│   └── public/                     # 6 pages HTML
│       ├── index.html             # Dashboard principal
│       ├── backtest.html          # Interface backtest
│       ├── config.html            # Configuration système
│       ├── test_agents.html       # Test agents
│       ├── dashboard_ascii.html   # Dashboard ASCII
│       └── validate_config.html   # Validation config
│
├── 🔧 backend/                     # Backend Node.js
│   ├── server-backend.ts         # Serveur principal (Port 7000)
│   └── backtest_validator.js     # Validateur backtests
│
├── 📚 docs/                        # Documentation complète
│   ├── agents/                    # Docs agents
│   │   ├── README.md              # Vue d'ensemble agents
│   │   ├── funding-agent.md       # Documentation Funding Agent
│   │   ├── risk-agent.md          # Documentation Risk Agent
│   │   ├── strategy-agent.md      # Documentation Strategy Agent
│   │   └── sentiment-agent.md     # Documentation Sentiment Agent
│   ├── AGENTS_GRAPH_VISUALIZATION.md
│   ├── ARCHITECTURE_DIAGRAMS.md
│   ├── CIRCULAR_SYSTEM_GUIDE.md
│   ├── HYPERLIQUID_API_DOCUMENTATION.md
│   └── LOG_SYSTEM_DOCUMENTATION.md
│
├── 🧪 tests/                       # Suite de tests
├── 📜 scripts/                     # Scripts utilitaires
├── 🎯 contexte/                    # Fichiers contexte
├── 🚀 run.ts                      # Launcher système
└── 📋 README.md                   # Ce fichier
```

---

## 🤖 Agents IA (4 scripts)

Tous utilisent **exclusivement Claude Code sub-agents** :

### 1. **funding_agent.py**

- **Rôle** : Analyse des funding rates
- **Sub-agent** : `claude-funding-advisor`
- **Fonction** : Détection opportunités de funding arbitrage

### 2. **risk_agent.py**

- **Rôle** : Gestion des risques et positions
- **Sub-agent** : `claude-risk-advisor`
- **Fonction** : Calculs risque, stop-loss, position sizing

### 3. **sentiment_analysis_agent.py**

- **Rôle** : Analyse sentiment marché
- **Sub-agent** : `claude-sentiment-advisor`
- **Fonction** : Analyse Twitter, news, indicateurs sentiment

### 4. **strategy_agent.py**

- **Rôle** : Développement stratégies trading
- **Sub-agent** : `claude-strategy-advisor`
- **Fonction** : Création et optimisation stratégies

### Pattern Claude Code

```python
def call_subagent(self, prompt: str, context_data: dict = None) -> str:
    """Appelle un sub-agent Claude Code avec permissions étendues"""
    cmd = [
        "claude",
        "--dangerously-skip-permissions",
        "--agent",
        self.subagent_name,
        full_prompt
    ]
    return subprocess.run(cmd, timeout=120, cwd=os.getcwd()).stdout
```

---

## ⚙️ Algorithmes Trading (10+ scripts)

Scripts Python purs sans IA pour le trading automatisé :

### Algorithmes Principaux

- **hyperliquid_agent.py** : Interface trading HyperLiquid
- **base_agent.py** : Agent de base commun
- **strategy_library.py** : Bibliothèque de stratégies
- **manager.py** : Gestionnaire multi-agents
- **intelligent_backtest_optimizer.py** : Optimisation backtests

### Algorithmes Spécialisés

- **portfolio_manager.py** : Gestion portefeuille
- **funding_agent.py** : Logique funding arbitrage
- **risk_agent.py** : Calculs risque purs
- **real_market_agent.py** : Trading marché réel
- **master_agent.py** : Coordination principale

---

## 🌐 Frontend (6 pages)

### Pages Principales

1. **`index.html`** - Dashboard principal temps réel
2. **`backtest.html`** - Interface de backtesting
3. **`config.html`** - Configuration système
4. **`test_agents.html`** - Interface test agents
5. **`dashboard_ascii.html`** - Dashboard ASCII terminal
6. **`validate_config.html`** - Validation configuration

### Technologies

- **HTML5/CSS3/JavaScript** vanilla
- **WebSocket** pour temps réel
- **Charts.js** pour graphiques
- **Bootstrap** pour styling

---

## 🔧 Backend Node.js

### Serveur Principal (`server-backend.ts`)

- **Port** : 7000
- **API REST** complète
- **WebSocket** : Port 7001
- **Middleware** : Sécurité, rate limiting, logging

### Fonctionnalités

- **Gestion agents** : Start/stop/restart
- **API HyperLiquid** : Positions, ordres, historique
- **Backtesting** : Exécution et résultats
- **Monitoring** : État système en temps réel

---

## 📊 Système de Logging Winston

### 7 Loggers Spécialisés

```javascript
// API et communications
apiLogger; // Logs appels API HyperLiquid
wsLogger; // Logs WebSocket connections

// Agents et trading
agentsLogger; // Logs actions des agents IA
tradingLogger; // Logs ordres et positions

// Analyses et backtests
backtestsLogger; // Logs résultats backtests

// Wallets et système
walletsLogger; // Logs opérations wallets
systemLogger; // Logs système globaux
```

### Niveaux de Log

- **ERROR** : Erreurs critiques
- **WARN** : Avertissements
- **INFO** : Informations générales
- **DEBUG** : Débogage détaillé

---

## 🔌 API HyperLiquid

### Endpoints Principaux

```python
# Market Data
get_all_mids()    # Prix milieux tous marchés
get_meta()        # Métadonnées marchés
get_user_state()  # État compte utilisateur

# Trading
place_order()     # Placer ordre
cancel_order()    # Annuler ordre
get_positions()   # Positions ouvertes
get_open_orders() # Ordres ouverts
```

### Fonctionnalités

- **Trading spot et futures**
- **Gestion positions**
- **Ordres avancés** (market, limit, stop)
- **Données temps réel** via WebSocket

---

## 🚀 Lancement Système

### Script `run.ts`

```bash
# Commandes de base
ts-node run.ts start      # Démarrer système complet
ts-node run.ts stop       # Arrêter système
ts-node run.ts restart    # Redémarrer système
ts-node run.ts test       # Lancer tests

# Options avancées
ts-node run.ts --mode=production
ts-node run.ts --debug=true
ts-node run.ts --agents=all
```

### Services Lancés

1. **Backend** : Port 7000 (API REST)
2. **Frontend** : Port 9001 (Interface web)
3. **WebSocket** : Port 7001 (Temps réel)
4. **Agents** : 4 agents IA + algorithmes

---

## 📈 Backtests Production

### Résultats Disponibles

```
src/data/production_backtests/
├── BTCDominance_FINAL_results_improved.json
├── BB_Squeeze_62_PRO_FINAL_results.json
├── Fear_Contrarian_73_PRO_FINAL_results.json
├── MACD_Crossover_65_PRO_FINAL_results.json
├── RSI_Oversold_68_PRO_FINAL_results.json
├── Twitter_Sentiment_69_PRO_FINAL_results.json
├── Volume_Breakout_71_PRO_FINAL_results.json
└── Funding_Arbitrage_85_PRO_FINAL_results.json
```

### Stratégies Testées

- **Bitcoin Dominance** : Stratégie basée dominance BTC
- **Bollinger Bands Squeeze** : Compression volatilité
- **Fear & Greed Contrarian** : Sentiment contraire
- **MACD Crossover** : Signaux MACD classiques
- **RSI Oversold** : Survente RSI
- **Twitter Sentiment** : Analyse tweets
- **Volume Breakout** : Cassures volumes
- **Funding Arbitrage** : Arbitrage funding rates

---

## 🛡️ Sécurité et Monitoring

### Sécurité

- **Rate Limiting** : Protection attaques
- **Security Headers** : Headers HTTP sécurisés
- **Input Validation** : Validation entrées
- **API Keys** : Gestion clés API sécurisée

### Monitoring

- **Health Checks** : Vérification état système
- **Prometheus Metrics** : Métriques performance
- **Circuit Breaker** : Protection cascades erreurs
- **Retry Manager** : Gestion réessais automatique

---

## 🤝 Sub-Agents Claude Code

### Disponibles

- **claude-strategy-advisor** : Analyse technique et stratégies
- **claude-risk-advisor** : Gestion risque et positions
- **claude-funding-advisor** : Funding rates et arbitrage
- **claude-sentiment-advisor** : Sentiment marché et news

### Configuration

```typescript
// Dans chaque agent IA
const subagentName = 'claude-strategy-advisor';
const response = await callSubAgent(prompt, context);
```

---

## 🧭 Navigation Documentation

### 📚 Documentation Principale

- **[🏠 Vue d'ensemble](docs/README.md)** : Documentation principale du projet
- **[📖 Index agents](docs/agents/index.md)** : Index complet des agents
- **[🗂️ Vue d'ensemble agents](docs/agents/README.md)** : Architecture des agents IA

### 🤖 Documentation Agents IA

- **[💰 Funding Agent](docs/agents/funding-agent.md)** : Documentation Funding Agent
- **[⚠️ Risk Agent](docs/agents/risk-agent.md)** : Documentation Risk Agent
- **[📈 Strategy Agent](docs/agents/strategy-agent.md)** : Documentation Strategy Agent
- **[💭 Sentiment Agent](docs/agents/sentiment-agent.md)** : Documentation Sentiment Agent

### 🔧 Guides Techniques

- **[🏗️ Architecture Claude Code](docs/CLAUDE_CODE_ARCHITECTURE.md)** : Architecture complète des agents
- **[🏗️ Architecture Diagrams](docs/ARCHITECTURE_DIAGRAMS.md)** : Diagrammes système complets
- **[🔄 Circular System](docs/CIRCULAR_SYSTEM_GUIDE.md)** : Guide interactions circulaires
- **[🔌 API HyperLiquid](docs/HYPERLIQUID_API_DOCUMENTATION.md)** : Documentation API HyperLiquid
- **[📝 Log System](docs/LOG_SYSTEM_DOCUMENTATION.md)** : Système de logging Winston

### 📊 Visualisations

- **[🕸️ Agents Graph](docs/AGENTS_GRAPH_VISUALIZATION.md)** : Visualisation graphique des agents
- **[🎯 Backtests Results](frontend/public/data/production_backtests/README.md)** : Résultats backtests production

### 📁 Documentation Contexte

- **[🌳 Arborescence Projet](contexte/arborescence.md)** : Structure complète des fichiers
- **[🎯 Contexte Application](contexte/context_app.md)** : Contexte et architecture NOVAQUOTE

---

## 🎯 Utilisation Rapide

### 1. Installation

```bash
# Installer dépendances
npm install
pip install -r requirements.txt

# Configurer environnement
cp .env.example .env
# Éditer .env avec clés API HyperLiquid
```

### 2. Lancement

```bash
# Démarrer système complet
ts-node run.ts start

# Accéder interfaces
# Frontend : http://localhost:9001
# API : http://localhost:7000
# WebSocket : ws://localhost:7001
```

### 3. Monitoring

```bash
# Voir logs en temps réel
tail -f logs/system.log
tail -f logs/trading.log

# Vérifier état agents
curl http://localhost:7000/api/agents/status
```

---

## 🚀 Fonctionnalités Avancées

### Trading Automatisé

- **Multi-stratégies** : Exécution parallèle stratégies
- **Gestion risque** : Stop-loss automatique, position sizing
- **Arbitrage** : Detection opportunités funding
- **Sentiment analysis** : Analyse Twitter/news temps réel

### Analytics

- **Backtesting** : Optimisation paramètres historiques
- **Performance tracking** : Métriques temps réel
- **Risk metrics** : VaR, Sharpe ratio, drawdown
- **Portfolio analysis** : Corrélation, diversification

### Interface Web

- **Dashboard temps réel** : Positions, P&L, métriques
- **Configuration agent** : Paramètres modifiables
- **Backtesting UI** : Tests visuels
- **Alert system** : Notifications seuils

---

## 📞 Support et Maintenance

### Outils Utilitaires

```bash
# Snapshot projet complet
python scripts/project_snapshot.py

# Nettoyage logs
npm run logs:clean

# Mise à jour dépendances
npm run update

# Tests système
npm run test:all
```

### Monitoring Production

- **Health checks** automatiques
- **Alertes** email/Discord
- **Backup** données automatique
- **Updates** sans interruption (hot-reload)

---

## 📋 Requirements

### System Requirements

- **Node.js** 18+
- **Python** 3.8+
- **MongoDB** (données)
- **Redis** (cache)

### API Keys Requises

- **HyperLiquid** : Trading API
- **Twitter** : Sentiment analysis (optionnel)
- **News API** : Actualités marché (optionnel)

---

## 🔮 Roadmap

### Phase 1 (Actuelle)

- ✅ 4 agents IA avec Claude Code
- ✅ Frontend 6 pages
- ✅ Integration HyperLiquid
- ✅ Backtesting production

### Phase 2 (Prochainement)

- 🔄 Mobile app (React Native)
- 🔄 Plus d'exchanges (Binance, Bybit)
- 🔄 Machine learning models
- 🔄 Social trading features

### Phase 3 (Futur)

- 📋 DeFi integration
- 📋 NFT trading
- 📋 DAO governance
- 📋 Multi-asset support

---

**Auteur** : DeamonDev888
**License** : MIT
**Version** : 1.0.0
**Dernière mise à jour** : Novembre 2024

---

> 🎯 **NOVAQUOTE** : Expert trading system avec intelligence artificielle pour performance optimale et gestion risque professionnelle
