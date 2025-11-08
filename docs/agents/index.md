# 🤖 Index des Agents NOVAQUOTE

## Navigation Rapide

### Agents IA Principaux

| Agent | Status | Confidence | LLM | Description |
|-------|--------|------------|-----|-------------|
| **[🛡️ Risk Agent](risk-agent.md)** | ✅ ACTIVE | 85% | Claude + DeepSeek | Gestion du risque en temps réel |
| **[📈 Strategy Agent](strategy-agent.md)** | ✅ ACTIVE | 80% | Claude (sub-agent) | Analyse technique et signaux |
| **[💰 Funding Agent](funding-agent.md)** | ✅ ACTIVE | 78% | Claude (sub-agent) | Arbitrage de funding |
| **[🗣️ Sentiment Agent](sentiment-agent.md)** | ✅ ACTIVE | 84% | Claude (sub-agent) | Analyse de sentiment marché |

### Documentation Générale

- **[📋 README Principal](README.md)** - Vue d'ensemble et architecture
- **[🔧 Configuration](README.md#configuration-model-factory)** - Model Factory
- **[📊 Métriques](README.md#métriques-et-monitoring)** - Monitoring
- **[🔐 Sécurité](README.md#sécurité)** - Mode unidirectionnel

## Liens Utiles

### Dashboard & Monitoring
- **Dashboard Principal** : http://localhost:9001/
- **API Health** : http://localhost:7000/api/health
- **Positions** : http://localhost:7000/api/positions
- **Prix Temps Réel** : http://localhost:7000/api/prices/realtime

### Fichiers Sources
- **Risk Agent** : `src/agents/risk_agent.py`
- **Strategy Agent** : `src/agents/strategy_agent.py`
- **Funding Agent** : `src/agents/funding_agent.py`
- **Sentiment Agent** : `src/agents/sentiment_analysis_agent.py`
- **Model Factory** : `src/models/model_factory.py`

### Configuration
- **Trading Config** : http://localhost:7000/api/trading/config
- **Unidirectional Mode** : Mode actif (LONG uniquement par défaut)

## Statut Global

```json
{
  "total_agents": 4,
  "active_agents": 4,
  "average_confidence": 81.75,
  "mode": "UNIDIRECTIONNEL",
  "allowed_side": "long",
  "last_update": "2025-11-08T00:24:57.491Z"
}
```

## Démarrage Rapide

```bash
# Démarrer le système
npm start

# Vérifier le statut des agents
curl http://localhost:7000/api/agents

# Voir les positions avec P&L temps réel
curl http://localhost:7000/api/positions

# Configurer le mode de trading
curl -X POST http://localhost:7000/api/trading/config \
  -H "Content-Type: application/json" \
  -d '{"UNIDIRECTIONAL_MODE": true, "ALLOWED_SIDE": "long"}'
```

## Architecture

```
                    ┌──────────────────┐
                    │  Dashboard UI    │
                    │  (Port 9001)     │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │  Backend API     │
                    │  (Port 7000)     │
                    └─────┬──────┬─────┘
                          │      │
            ┌─────────────┘      └─────────────┐
            │                                │
    ┌───────▼──────────┐          ┌──────────▼──────────┐
    │   Python Agents  │          │  HyperLiquid API    │
    │                  │          │                     │
    │ • Risk Agent     │          │ • getAllMids()      │
    │ • Strategy Agent │          │ • getMeta()         │
    │ • Funding Agent  │          │ • placeOrder()      │
    │ • Sentiment Agent│          │ • getUserState()    │
    └────────┬─────────┘          └─────────────────────┘
             │                             │
             │ Claude Code CLI             │ REST API
             │ (Sub-Agents only)           │
             │                             │
    ┌────────▼──────────┐                  │
    │ Claude Sub-Agents │                  │
    │                   │                  │
    │ • claude-strategy-│                  │
    │   advisor         │                  │
    │ • claude-risk-    │                  │
    │   advisor         │                  │
    │ • claude-funding- │                  │
    │   advisor         │                  │
    │ • claude-sentiment│                  │
    │   -advisor        │                  │
    └───────────────────┘                  │
                                          │
                            ┌─────────────▼──────────┐
                            │  WebSocket Server      │
                            │  (Port 7001)           │
                            │                        │
                            │ • Real-time prices     │
                            │ • Position updates     │
                            │ • Agent communications │
                            └────────────────────────┘
```

## Mode Unidirectionnel

Le système NOVAQUOTE fonctionne en **mode unidirectionnel** par défaut :

- ✅ **LONG uniquement** : Seules les positions LONG sont autorisées
- ❌ **Pas de SHORT** : Les positions SHORT sont automatiquement refusées
- 🔒 **Protection** : Empêche les positions contradictoires
- 💡 **Configuration** : Modifiable via `/api/trading/config`

### Exemple de Refus SHORT

```json
{
  "success": false,
  "error": "Position refusée par le mode unidirectionnel",
  "reason": "⚠️ MODE UNIDIRECTIONNEL: Seules les positions LONG sont autorisées. Position SHORT refusée.",
  "mode": "UNIDIRECTIONNEL",
  "allowedSide": "long",
  "stats": {
    "total": 0,
    "long": 0,
    "short": 0
  }
}
```

## Prix Temps Réel

Le système récupère **468 prix en temps réel** depuis l'API HyperLiquid :

```bash
# Récupérer tous les prix
curl http://localhost:7000/api/prices/realtime

# Exemple de réponse
{
  "success": true,
  "data": {
    "BTC": "103302.5",
    "ETH": "3438.25",
    "SOL": "162.265"
  },
  "count": 468,
  "source": "HyperLiquid API (getAllMids)"
}
```

## P&L et ROE Temps Réel

Les positions affichent le **P&L et ROE calculés en temps réel** :

```json
{
  "positions": [
    {
      "symbol": "BTC",
      "side": "LONG",
      "size": 0.5,
      "entryPrice": 100000,
      "markPrice": 103213.5,
      "pnl": 1606.75,
      "roe": 3.21,
      "unrealizedPnl": 1606.75
    }
  ],
  "realTimeData": {
    "pricesUpdated": "2025-11-08T00:24:57.491Z",
    "source": "HyperLiquid API (getAllMids)"
  }
}
```

## Logs et Debugging

### Emplacement des Logs
- **Dossier** : `logs/`
- **Loggers spécialisés** :
  - `riskLogger` - Agent de risque
  - `strategyLogger` - Agent de stratégie
  - `fundingLogger` - Agent de funding
  - `sentimentLogger` - Agent de sentiment
  - `tradingLogger` - Opérations trading

### Commande de Debug
```bash
# Voir les logs en temps réel
tail -f logs/agents.log

# Vérifier les erreurs
grep "ERROR" logs/system.log
```

## Support

### Problèmes Courants
1. **Agents inactifs** → Vérifier les API keys LLM
2. **Pas de prix** → Vérifier connectivité HyperLiquid
3. **Positions non mises à jour** → Redémarrer le backend
4. **Erreur LLM** → Vérifier Model Factory

### Contacts
- **Documentation** : `docs/agents/`
- **Code Source** : `src/agents/`
- **Logs** : `logs/`
- **Dashboard** : http://localhost:9001/

---

**Dernière mise à jour** : 2025-11-08 00:24:57 UTC
**Version** : NOVAQUOTE v2.0.0
**Système** : HyperLiquid Trading System
