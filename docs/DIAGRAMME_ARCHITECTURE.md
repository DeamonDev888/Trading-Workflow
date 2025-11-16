# 🏗️ DIAGRAMME D'ARCHITECTURE NOVAQUOTE v8.0

## Vue d'Ensemble

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              🚀 NOVAQUOTE TRADING SYSTEM v8.0                                │
│                                   Claude Code Framework                                 │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    FRONTEND LAYER                                            │
│                                     Port 9001                                               │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│     Dashboard       │  │   Agent Config     │  │    Backtest       │  │    Agent Info     │  │      Config       │
│   (index.html)      │  │ (agent-config.html) │  │  (backtest.html)   │  │ (agent-inf.html)   │  │   (config.html)    │
│                     │  │                     │  │                   │  │                   │  │                   │
│ 📊 Trading View     │  │ ⚙️ Agent Settings   │  │ 📈 Strategy Test  │  │ 🤖 Agent Status   │  │ ⚙️ Trading Config  │
│ 💰 Portfolio        │  │ 🎛️ Modify Params    │  │ 📊 Performance    │  │ 📊 Inferences     │  │ 🎯 Risk Settings   │
│ 📈 Charts           │  │ 🔗 Connect Experts  │  │ 📉 Results        │  │ 📈 Real-time       │  │ ⚡ Auto-Trading    │
└─────────────────────┘  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘
                                        │
                                        │ HTTP/WebSocket
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    BACKEND LAYER                                             │
│                                     Port 7000                                               │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              🤖 CLAUDE CODE FRAMEWORK                                    │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────────────────────────────────────────────┐
                    │                 API Orchestration Layer                │
                    │                                                             │
                    │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
                    │  │   API       │  │   WebSocket│  │ Database   │   │
                    │  │   Routes    │  │   Server   │  │ Manager   │   │
                    │  └─────────────┘  └─────────────┘  └─────────────┘   │
                    └─────────────────────────────────────────────────────────────┘

                    ┌─────────────────────────────────────────────────────────────┐
                    │              Sub-Agents Claude Code                     │
                    │                                                             │
                    │  ┌─────────────────────────────────────────────────────┐   │
                    │  │            claude-strategy-advisor.json           │   │
                    │  │  📊 Technical Analysis • 🎯 Signal Generation    │   │
                    │  │  📈 Strategy Selection • ⚡ Decision Making       │   │
                    │  │  Parameters: temperature=0.3, tokens=4000        │   │
                    │  └─────────────────────────────────────────────────────┘   │
                    │                                                             │
                    │  ┌─────────────────────────────────────────────────────┐   │
                    │  │            claude-risk-advisor.json                │   │
                    │  │  🛡️ Risk Assessment • 📏 Position Sizing        │   │
                    │  │  🎯 Loss Management • ⚖️ Portfolio Balance      │   │
                    │  │  Parameters: temperature=0.2, tokens=3000        │   │
                    │  └─────────────────────────────────────────────────────┘   │
                    │                                                             │
                    │  ┌─────────────────────────────────────────────────────┐   │
                    │  │            claude-funding-advisor.json             │   │
                    │  │  💰 Rate Analysis • 📊 Correlation Study        │   │
                    │  │  ⏰ Time Optimization • 💵 Yield Maximization     │   │
                    │  │  Parameters: temperature=0.3, tokens=3000        │   │
                    │  └─────────────────────────────────────────────────────┘   │
                    │                                                             │
                    │  ┌─────────────────────────────────────────────────────┐   │
                    │  │            claude-sentiment-analyzer.json          │   │
                    │  │  🧠 Market Sentiment • 📱 Social Analysis       │   │
                    │  │  📰 News Impact • 😊 Emotional Metrics          │   │
                    │  │  Parameters: temperature=0.4, tokens=3500        │
                    │  └─────────────────────────────────────────────────────┘   │
                    └─────────────────────────────────────────────────────────────┘

                    │
                    ▼
        ┌─────────────────────────────────────────────────────────────────────────────┐
        │                          SYSTEMS EXPERTS PYTHON                             │
        │                      Algorithmes & Logique Métier                        │
        └─────────────────────────────────────────────────────────────────────────────┘

        ┌─────────────────────────────────────────────────────────────────────────────┐
        │                      🧠 STRATEGY EXPERT SYSTEM                              │
        │                     src/agents/strategy_agent.py                            │
        │                                                                           │
        │  📊 Algorithmes:                                                       │
        │  ├─ RSI (Relative Strength Index)                                    │
        │  ├─ MACD (Moving Average Convergence Divergence)                      │
        │  ├─ Bollinger Bands                                                   │
        │  ├─ Volume Profile Analysis                                          │
        │  ├─ Fibonacci Retracements                                          │
        │  └─ Support/Resistance Levels                                       │
        │                                                                           │
        │  🔧 Configuration:                                                     │
        │  ├─ Timeframes: 1m, 5m, 15m, 1h, 4h                                   │
        │  ├─ Symbols: BTC, ETH, SOL, ARB, APT, ADA, AVAX, BNB                    │
        │  ├─ Strategies: Trend Following, Mean Reversion, Breakout            │
        │  └─ Risk Parameters: Max Drawdown, Stop Loss, Take Profit           │
        │                                                                           │
        │  📈 Performance:                                                       │
        │  └─ Win Rate: 68% • Avg Return: 2.3% • Max Drawdown: 8.5%          │
        └─────────────────────────────────────────────────────────────────────────────┘

        ┌─────────────────────────────────────────────────────────────────────────────┐
        │                       🛡️ RISK EXPERT SYSTEM                                   │
        │                      src/agents/risk_agent.py                                 │
        │                                                                           │
        │  🎯 Risk Management:                                                   │
        │  ├─ Position Sizing Algorithm (Kelly Criterion)                        │
        │  ├─ Portfolio Heatmap Monitoring                                     │
        │  ├─ Correlation Matrix Analysis                                       │
        │  ├─ VaR (Value at Risk) Calculation                                   │
        │  └─ Maximum Drawdown Projection                                     │
        │                                                                           │
        │  📊 Risk Metrics:                                                      │
        │  ├─ Max Loss Per Trade: 2%                                            │
        │  ├─ Max Daily Loss: 5%                                                 │
        │  ├─ Max Concurrent Positions: 5                                       │
        │  ├─ Minimum Portfolio Value: $1,000                                   │
        │  └─ Risk-Adjusted Returns: Sharpe Ratio 1.8                            │
        │                                                                           │
        │  🚨 Alert System:                                                      │
        │  └─ Real-time Risk Monitoring • Automatic Position Reduction           │
        └─────────────────────────────────────────────────────────────────────────────┘

        ┌─────────────────────────────────────────────────────────────────────────────┐
        │                      💰 FUNDING EXPERT SYSTEM                                  │
        │                     src/agents/funding_agent.py                               │
        │                                                                           │
        │  📊 Funding Analysis:                                                   │
        │  ├─ Rate Correlation Matrix                                             │
        │  ├─ Volatility-Funding Relationship                                   │
        │  ├─ Market Regime Detection                                           │
        │  ├─ Optimal Holding Time Calculation                                   │
        │  └─ Yield Curve Analysis                                                │
        │                                                                           │
        │  💸 Arbitrage Opportunities:                                              │
        │  ├─ Cross-Exchange Rate Differences                                   │
        │  ├─ Temporal Rate Arbitrage                                            │
        │  ├─ Market-Making Profits                                             │
        │  └─ Funding Rate Predictions                                           │
        │                                                                           │
        │  ⏱️ Optimization Parameters:                                              │
        │  └─ Min Rate: 0.01% • Optimization Mode: Correlation-based          │
        └─────────────────────────────────────────────────────────────────────────────┘

        ┌─────────────────────────────────────────────────────────────────────────────┐
        │                    🧠 SENTIMENT EXPERT SYSTEM                                 │
        │                src/agents/sentiment_analysis_agent.py                        │
        │                                                                           │
        │  📱 Data Sources:                                                       │
        │  ├─ Twitter/X API (Real-time)                                         │
        │  ├─ Reddit API (r/CryptoCurrency, r/Bitcoin)                           │
        │  ├─ News Aggregators (Coindesk, Cointelegraph)                        │
        │  ├─ On-Chain Metrics (Whale Transactions, Smart Contracts)           │
        │  └─ Fear & Greed Index                                               │
        │                                                                           │
        │  🔍 Sentiment Analysis:                                                  │
        │  ├─ Natural Language Processing (NLP)                                  │
        │  ├─ Social Media Sentiment Scoring                                      │
        │  ├─ News Impact Assessment                                             │
        │  ├─ Volume-Sentiment Correlation                                     │
        │  └─ Contrarian Signal Detection                                       │
        │                                                                           │
        │  📊 Sentiment Metrics:                                                   │
        │  └─ Score Range: -1.0 (Extreme Fear) to +1.0 (Extreme Greed)         │
        └─────────────────────────────────────────────────────────────────────────────┘

                    │
                    ▼
        ┌─────────────────────────────────────────────────────────────────────────────┐
        │                           DATABASE LAYER                                        │
        │                        PostgreSQL / SQLite                                   │
        └─────────────────────────────────────────────────────────────────────────────┘

        ┌─────────────────────────────────────────────────────────────────────────────┐
        │                        📊 PERSISTENT STORAGE                                   │
        │                                                                           │
        │  🏦 Agents Table:                                                       │
        │  ├─ agent_id, name, type, status                                           │
        │  ├─ configuration (JSONB)                                                 │
        │  ├─ last_heartbeat, performance_metrics                                 │
        │  └─ created_at, updated_at                                              │
        │                                                                           │
        │  💰 Trades Table:                                                       │
        │  ├─ trade_id, symbol, side, size, price                                    │
        │  ├─ agent_id, strategy_id, decision                                    │
        │  ├─ confidence, pnl, status                                               │
        │  └─ timestamp, metadata                                                   │
        │                                                                           │
        │  📈 Inferences Table:                                                   │
        │  ├─ inference_id, agent_type, decision                                  │
        │  ├─ confidence, reasoning, metadata                                    │
        │  ├─ model: 'claudecode'                                                 │
        │  └─ source: 'Claude Code Framework'                                   │
        │                                                                           │
        │  🛡️ Risk Metrics Table:                                                   │
        │  ├─ risk_score, position_size, correlation                            │
        │  ├─ max_drawdown, var_calculation                                        │
        │  └─ compliance_status, warnings                                       │
        └─────────────────────────────────────────────────────────────────────────────┘

                    │
                    ▼
        ┌─────────────────────────────────────────────────────────────────────────────┐
        │                        🌐 EXTERNAL INTEGRATION                                   │
        │                                                                           │
        │  📡 HyperLiquid API:                                                    │
        │  ├─ Real-time Price Feed (WebSocket)                                   │
        │  ├─ Order Management System                                            │
        │  ├─ Position Tracking                                                  │
        │  └─ Funding Rate Monitoring                                            │
        │                                                                           │
        │  🔌 WebSocket Layer:                                                    │
        │  ├─ Port 7001: Real-time Data Streaming                               │
        │  ├─ Price Updates: BTC, ETH, SOL, ARB, APT, ADA, AVAX, BNB          │
        │  ├─ Agent Status Updates                                                │
        │  └─ Trade Execution Notifications                                   │
        └─────────────────────────────────────────────────────────────────────────────┘

## 🔄 Flux de Données Complet

### 1. Flux d'Configuration
```
Frontend (agent-config.html)
    │
    ▼ HTTP POST /api/agents/{agent}/config
Backend API Layer
    │
    ▼ Claude Code Framework
    ├── sub-agent JSON configuration
    │   └── Parameters (temperature, tokens, etc.)
    │
    ▼ Python Expert System
    ├── src/agents/{agent}_agent.py
    │   └── Algorithm-specific configuration
    │
    ▼ Database (JSONB column)
    └── Persisted configuration
```

### 2. Flux d'Inférence
```
Frontend Request
    │
    ▼ WebSocket / API Request
Backend getAgentInferences()
    │
    ▼ Claude Code Sub-Agent Call
    ├── claude --agents .claude/agents/{agent}.json
    │   └── Trading Analysis Prompt
    │
    ▼ Python Expert System Integration
    ├── src/agents/{agent}_agent.py
    │   ├── Market Data Processing
    │   ├── Algorithm Execution
    │   └── Technical Analysis
    │
    ▼ JSON Response
    ├── decision: BUY/SELL/HOLD/ANALYZE
    ├── confidence: 0.0-1.0
    ├── reasoning: Detailed explanation
    ├── metadata.source: "Claude Code Framework"
    ├── metadata.model: "claudecode"
    └── metadata.duration: "XXXms"
    │
    ▼ Frontend Display
    └── Real-time card updates with claudecode model
```

### 3. Flux de Trading
```
Agent Decision
    │
    ▼ Risk Validation
    ├── claude-risk-advisor
    │   └── Position sizing check
    │
    ▼ Execution Decision
    ├── HyperLiquid API
    │   └── Order placement
    │
    ▼ Database Logging
    ├── trades table
    ├── inferences table
    └── performance metrics
    │
    ▼ Frontend Update
    └── Real-time portfolio updates
```

## 🎯 Avantages de l'Architecture

### ✅ **Claude Code Framework**
- **Modularité**: Chaque agent dans son propre fichier JSON
- **Extensibilité**: Facile ajout de nouveaux sub-agents
- **Versioning**: Configuration contrôlée et persistante
- **Debugging**: Traçabilité complète des décisions

### ✅ **Systèmes Experts Python**
- **Algorithmes Spécialisés**: Logique métier experte par domaine
- **Performance**: Traitement local optimisé
- **Flexibilité: Configuration modifiable via frontend
- **Intégration**: Interface standard avec Claude Code

### ✅ **Base de Données Unifiée**
- **Persistence**: Configuration et performances stockées
- **Analyse**: Historique complet des décisions
- **Monitoring**: Métriques en temps réel
- **Scalabilité**: Support PostgreSQL et SQLite

### ✅ **Interface Utilisateur**
- **Configuration**: Modification intuitive des paramètres
- **Monitoring**: Statut et performance des agents en temps réel
- **Testing**: Validation des configurations avant déploiement
- **Professional**: Design moderne et responsive

## 🔧 Technologies Utilisées

### **Frontend**
- HTML5 / CSS3 / JavaScript (Vanilla)
- Tailwind CSS pour le styling
- WebSocket pour le temps réel
- Chart.js pour les visualisations

### **Backend**
- Node.js / TypeScript / Express.js
- PostgreSQL / SQLite pour la persistance
- WebSocket Server pour les communications temps réel
- Claude Code CLI pour l'intelligence artificielle

### **Intelligence Artificielle**
- Claude Code Framework (sub-agents spécialisés)
- Systèmes Experts Python (algorithmes métier)
- Modèle Claude 3.5 Sonnet pour l'analyse
- Températures et tokens configurables par agent

### **Trading**
- HyperLiquid API pour l'exécution
- WebSocket pour les données temps réel
- Risk Management intégré
- Support multi-symboles (8 cryptomonnaies)

---

*Architecture NOVAQUOTE v8.0 - Claude Code Framework + Systèmes Experts Python*