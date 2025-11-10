# 🤖 NOVAQUOTE Trading Agents Documentation

## Vue d'ensemble

Le système NOVAQUOTE Trading System intègre **4 agents IA distincts** qui
fonctionnent de manière coordonnée pour gérer le trading automatisé sur
HyperLiquid. Chaque agent a un rôle spécialisé et utilise **Claude Code
Sub-Agents** pour prendre des décisions intelligentes.

## Architecture des Agents

### Classification Fondamentale

**🚨 Distinction Cruciale :**

- **Agent** = Script Python qui utilise Claude Code CLI avec sub-agents
  spécialisés
- **Algorithme** = Script Python ordinaire de trading/monitoring (sans IA)

## Agents IA Véritables (4 scripts avec LLM)

### 1. 🛡️ Risk Agent

- **Fichier** : `src/agents/risk_agent.py`
- **Status** : ACTIVE
- **Confidence** : 85%
- **Appels LLM** : Claude + DeepSeek
- **Temps de réponse** : 115ms
- **Documentation** : [`risk-agent.md`](./risk-agent.md)

**Fonction :** Gestion du risque en temps réel, surveillance des positions,
stop-loss automatiques

### 2. 📈 Strategy Agent

- **Fichier** : `src/agents/strategy_agent.py`
- **Status** : ACTIVE
- **Confidence** : 80%
- **Appels LLM** : Claude via sub-agent
- **Sub-Agent** : claude-strategy-advisor
- **Stratégies actives** : 7
- **Temps de réponse** : 110ms
- **Documentation** : [`strategy-agent.md`](./strategy-agent.md)

**Fonction :** Analyse technique, génération de signaux de trading, optimisation
des stratégies

**Architecture LLM :**

- Utilise Claude Code CLI avec sub-agent spécialisé
- Prompt système : "Deamon Dev's Strategy Validation Assistant"
- Configuration via config.py (AI_MODEL, AI_TEMPERATURE, AI_MAX_TOKENS)

### 3. 💰 Funding Agent

- **Fichier** : `src/agents/funding_agent.py`
- **Status** : ACTIVE
- **Confidence** : 78%
- **Appels LLM** : Claude (via sub-agent)
- **Sub-Agent** : claude-funding-advisor
- **Temps de réponse** : 109ms
- **Documentation** : [`funding-agent.md`](./funding-agent.md)

**Fonction :** Détection d'opportunités de funding arbitrage, optimisation des
taux

### 4. 🗣️ Sentiment Agent

- **Fichier** : `src/agents/sentiment_analysis_agent.py`
- **Status** : ACTIVE
- **Confidence** : 84%
- **Appels LLM** : Claude (via sub-agent)
- **Sub-Agent** : claude-sentiment-advisor
- **Temps de réponse** : 111ms
- **Documentation** : [`sentiment-agent.md`](./sentiment-agent.md)

**Fonction :** Analyse de sentiment du marché, détection de fear & greed, news
impact

## Sub-Agents Architecture

Tous les agents utilisent **Claude Code CLI** avec des sub-agents spécialisés :

```python
# Sub-agents utilisés
- claude-strategy-advisor   : Analyse technique et stratégies
- claude-risk-advisor       : Gestion du risque
- claude-funding-advisor    : Analyse des taux de funding
- claude-sentiment-advisor  : Analyse de sentiment
```

**Avantages :**

- Utilisation exclusive de Claude (pas d'APIs multiples)
- Prompts système spécialisés pour chaque agent
- Configuration centralisée via config.py
- Contrôle total des réponses et des formats

## Communication entre Agents

Les agents communiquent via :

- **API REST** : Endpoints du backend (Port 7000)
- **WebSocket** : Données temps réel (Port 7001)
- **Dashboard** : Monitoring centralisé (Port 9001)

## Métriques et Monitoring

Chaque agent expose ses métriques :

- **Status** : ACTIVE/INACTIVE/ERROR
- **Confidence** : Niveau de confiance (0-100%)
- **Response Time** : Temps de réponse moyen
- **LLM Calls** : Nombre d'appels LLM effectués
- **Win Rate** : Taux de réussite des décisions

## Logs et Debugging

Système de logging Winston avec 7 loggers spécialisés :

- `agentsLogger` - Opérations des 4 agents IA
- `riskLogger` - Agent de risque
- `strategyLogger` - Agent de stratégie
- `fundingLogger` - Agent de funding
- `sentimentLogger` - Agent de sentiment
- `tradingLogger` - Opérations trading
- `systemLogger` - Surveillance système

## Sécurité

- **Mode Unidirectionnel** : Empêche les positions LONG + SHORT simultanées
- **Validation LLM** : Chaque décision est validée par le Risk Agent
- **API Keys** : Stockage sécurisé des clés API
- **Rate Limiting** : Limitation des appels API

## Amélioration Continue

Les agents sont améliorés en continu via :

1. **Backtesting** : Tests algorithmiques sur données historiques
2. **Machine Learning** : Optimisation des modèles
3. **Feedback Loop** : Apprentissage des résultats passés
4. **A/B Testing** : Comparaison des stratégies

## Support

Pour toute question sur les agents :

- Consultez la documentation spécifique de chaque agent
- Vérifiez les logs dans le dossier `logs/`
- Surveillez le dashboard en temps réel
