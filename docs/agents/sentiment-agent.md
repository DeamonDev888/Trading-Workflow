# 🗣️ Sentiment Agent Documentation

## Vue d'ensemble

Le **Sentiment Agent** est l'agent IA spécialisé dans l'analyse de sentiment du
marché en temps réel. Il utilise **Claude Code Sub-Agents** pour traiter les
données de sentiment provenant de diverses sources (social media, etc.) et
fournir des insights sur l'émotion dominante du marché.

## Informations Générales

- **Nom** : Multi-Source Sentiment Agent V3.0
- **Status** : ✅ ACTIVE
- **Confidence** : 88%
- **Appels LLM** : Claude (via sub-agent claude-sentiment-analyzer)
- **Sub-Agent** : claude-sentiment-analyzer
- **Temps de réponse** : 165ms
- **Fichier source** : `src/agents/sentiment_analysis_agent.py`
- **Type** : Agent IA multi-sources (avec Claude Code sub-agents)

## Responsabilités

### 1. 📰 Analyse de Sentiment News

- Traitement des news crypto en temps réel
- Classification sentiment (positif/négatif/neutre)
- Score de sentiment pondéré par source
- Impact prédictif des news

### 2. 📱 Surveillance Social Media

- Twitter/X : Analyse des tweets
- Reddit : Sentiment des communautés
- Discord/Telegram : Sentiment des groupes
- Indicateurs de hype/fear

### 3. 🔍 On-Chain Sentiment

- Métriques on-chain ( adresses actives, whale movements)
- Métricas DeFi (TVL, liquidité, staking)
- Indicateurs de行為 (accumulation/distribution)
- Network activity

### 4. 📊 Fear & Greed Index

- Calcul du Fear & Greed Index
- Détection des extrêmes (extreme fear/greed)
- Corrélation sentiment vs prix
- Signaux de retournement

## Sources de Données

### News & Articles ✅ **IMPLÉMENTÉ**

- **CoinDesk API** : Articles crypto en temps réel
  - Recherche par token avec mots-clés
  - Titre, description, URL, timestamp extraits
  - Limite configurable par recherche

- **CryptoPanic API** : Agrégateur de news crypto
  - Free tier disponible
  - Filtrage par devises (BTC, ETH, SOL, etc.)
  - Posts "hot" avec votes
  - Auth token requis

- **Sources Additionnelles** (structure prête)
  - CoinTelegraph, Decrypt, The Block
  - API endpoints configurables
  - Scoring par crédibilité source

### Social Media ✅ **IMPLÉMENTÉ**

- **Twitter/X API** : Tweets récents, trending hashtags
  - Recherche avancée avec `#{token} OR ${token} crypto -is:retweet lang:en`
  - Métriques publiques et annotations de contexte
  - Fallback web scraping si API indisponible

- **Reddit API** : Posts et commentaires (r/cryptocurrency, r/bitcoin, r/ethereum, r/solana)
  - OAuth 2.0 avec access token
  - Search dans multiples subreddits crypto
  - Score, commentaires, timestamp extraits
  - Rate limiting respecté

- **Discord Webhooks** : Canaux crypto populaires (structure prête)
  - Support pour webhooks (envoi)
  - nécessite Discord Bot API pour réception historique

- **Telegram APIs** : Groupes news (structure prête)
  - Bot token configuration
  - Canaux crypto configurables
  - Messages des groupes analysés

### On-Chain Data

- **Blockchain APIs** : Ethereum, Solana, Bitcoin
- **Glassnode** : Métriques avancées
- **Santiment** : Sentiment on-chain
- **Dune Analytics** : Dashboards communautaires

### Market Data

- **Volume anomalies** : Spikes de volume
- **Whale alerts** : Mouvements importants
- **Exchange flows** : Entrées/sorties d'exchanges
- **Options flow** : Sentiment des options

## Intégration LLM

### Méthode d'Appel

Le Sentiment Agent utilise **Claude Code CLI** avec un sub-agent spécialisé au
lieu d'appels API directs.

### Sub-Agent Utilisé

- **Nom** : `claude-sentiment-analyzer`
- **Type** : Sub-agent Claude Code spécialisé
- **Invocation** : Via
  `claude --agent claude-sentiment-analyzer --dangerously-skip-permissions`

### Prompt Système

```python
SENTIMENT_ANALYSIS_PROMPT = '''
You are Deamon Dev's Sentiment Analysis Assistant

Analyze the following social media data and provide sentiment-based trading signals:

Social Media Data:
{sentiment_data}

Market Context:
{market_context}

Token: {token}

Evaluate:
1. Overall sentiment (VERY_BEARISH/BEARISH/NEUTRAL/BULLISH/VERY_BULLISH)
2. Sentiment strength (0-100%)
3. Trading signal (BUY/SELL/HOLD)
4. Confidence level (0-100%)
5. Key emotional indicators

Respond in this format:
1. First line: sentiment label
2. Sentiment strength: X%
3. Action: BUY/SELL/HOLD
4. Confidence: X%
5. Key factors:
6. Risk assessment
'''
```

## Indicateurs de Sentiment

### Sentiment Score

```python
def calculate_sentiment_score(sources):
    """
    sources: liste de sources avec score et poids
    """
    weighted_sum = sum(source.score * source.weight for source in sources)
    total_weight = sum(source.weight for source in sources)
    return weighted_sum / total_weight
```

**Échelle :**

- **-1.0 à -0.5** : Très Bearish
- **-0.5 à -0.1** : Bearish
- **-0.1 à +0.1** : Neutre
- **+0.1 à +0.5** : Bullish
- **+0.5 à +1.0** : Très Bullish

### Fear & Greed Index

```python
def calculate_fear_greed_index():
    # 6 composantes (chacune 0-100)
    volatility = get_volatility_score() * 0.25
    momentum = get_momentum_score() * 0.15
    social_media = get_social_score() * 0.15
    surveys = get_survey_score() * 0.15
    dominance = get_dominance_score() * 0.15
    trends = get_trends_score() * 0.15

    return volatility + momentum + social_media + surveys + dominance + trends
```

**Niveaux :**

- **0-25** : Extreme Fear 🔴
- **26-45** : Fear 🟠
- **46-55** : Neutral 🟡
- **56-75** : Greed 🟢
- **76-100** : Extreme Greed 🟢

### On-Chain Sentiment

```python
def get_onchain_sentiment():
    return {
        'active_addresses_trend': trend_score,
        'whale_activity': activity_score,
        'exchange_flows': flow_score,
        'staking_ratio': staking_score,
        'social_volume': volume_score,
        'overall': composite_score
    }
```

## Stratégies Basées sur le Sentiment

### 1. Contrarian Strategy

```python
def contrarian_strategy(sentiment_score):
    """
    Acheter quand fear, vendre quand greed
    """
    if sentiment_score < -0.7:  # Extreme fear
        return 'BUY', 'Extreme fear = opportunity'
    elif sentiment_score > 0.7:  # Extreme greed
        return 'SELL', 'Extreme greed = caution'
    else:
        return 'HOLD', 'Sentiment neutral'
```

### 2. Momentum Strategy

```python
def momentum_strategy(sentiment_momentum, price_momentum):
    """
    Suivre le sentiment si aligné avec le prix
    """
    if sentiment_momentum > 0.5 and price_momentum > 0:
        return 'BUY', 'Sentiment & price aligned bullish'
    elif sentiment_momentum < -0.5 and price_momentum < 0:
        return 'SELL', 'Sentiment & price aligned bearish'
    else:
        return 'HOLD', 'Sentiment-price divergence'
```

### 3. Divergence Detection

```python
def detect_divergence(price_data, sentiment_data):
    """
    Détecter divergence prix-sentiment
    """
    price_trend = calculate_trend(price_data)
    sentiment_trend = calculate_trend(sentiment_data)

    if price_trend > 0 and sentiment_trend < -0.3:
        return 'BEARISH_DIVERGENCE', 'Price up, sentiment down'
    elif price_trend < 0 and sentiment_trend > 0.3:
        return 'BULLISH_DIVERGENCE', 'Price down, sentiment up'

    return 'NO_DIVERGENCE', 'Aligned'
```

## Intégration Multi-Agents

### Collaboration avec Strategy Agent

```python
def combine_signals(strategy_signal, sentiment_signal):
    """
    Combiner signaux techniques et sentiment
    """
    if strategy_signal.action == sentiment_signal.action:
        # Signaux alignés = confiance renforcée
        return {
            'action': strategy_signal.action,
            'confidence': min(1.0, strategy_signal.confidence * 1.2)
        }
    else:
        # Signaux contradictoires = prudence
        return {
            'action': 'HOLD',
            'confidence': 0.3,
            'reason': 'Technical-sentiment divergence'
        }
```

### Validation par Risk Agent

```python
def sentiment_risk_validation(sentiment_signal):
    """
    Le Risk Agent valide la décision
    """
    if sentiment_signal.action in ['BUY', 'SELL']:
        if sentiment_signal.extreme:
            # Alert au Risk Agent pour validation
            risk_validation = risk_agent.validate({
                'action': sentiment_signal.action,
                'reason': f'Extreme sentiment: {sentiment_signal.emotion}'
            })
            return risk_validation

    return {'approved': True}
```

## Configuration V3.0

### Variables d'Environnement Requises

```bash
# Twitter/X API
TWITTER_BEARER_TOKEN=your_bearer_token_here

# Reddit API
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token

# CryptoPanic API
CRYPTOPANIC_API_KEY=your_api_key
```

### Configuration des Tokens Suivis

```python
# Tokens analysés
TOKENS_TO_TRACK = ["BTC", "ETH", "SOL", "AVAX", "MATIC", "DOT", "LINK", "UNI"]

# Posts par plateforme
POSTS_PER_PLATFORM = 25

# Subreddits Reddit
REDDIT_SUBREDDITS = [
    "cryptocurrency", "bitcoin", "ethereum", "solana",
    "CryptoCurrency", "binance", "CryptoMarkets"
]

# Discord Webhooks (à configurer)
DISCORD_WEBHOOKS = [
    "https://discord.com/api/webhooks/...",
    # Ajouter vos webhooks ici
]

# Telegram Channels (à configurer)
TELEGRAM_CHANNELS = [
    "@crypto_news",
    # Ajouter vos channels ici
]
```

### Paramètres d'Exécution

```python
# Intervalle d'analyse
CHECK_INTERVAL_MINUTES = 15

# Limites API
MAX_TWEETS_PER_RUN = 25
MAX_REDDIT_POSTS = 25
MAX_NEWS_ARTICLES = 25

# Timeout
API_TIMEOUT = 10  # secondes
SUBAGENT_TIMEOUT = 120  # secondes
```

### Pondération par Source

```python
SOURCE_CREDIBILITY = {
    'coindesk': 0.9,
    'cointelegraph': 0.85,
    'decrypt': 0.8,
    'twitter_verified': 0.7,
    'twitter_large_following': 0.6,
    'reddit_cryptocurrency': 0.65,
    'reddit_bitcoin': 0.7,
    'glassnode': 0.9,
    'santiment': 0.85
}
```

## Filtres et Validation

### Filtre de Qualité

```python
def validate_sentiment_data(source, data):
    # Vérifier authenticité
    if not verify_source(source):
        return False

    # Vérifier fraîcheur
    if is_stale(data.timestamp, max_age='1h'):
        return False

    # Vérifier cohérence
    if detect_outlier(data.score):
        return False

    return True
```

### Aggregation Robuste

```python
def robust_aggregation(scores):
    """
    Médiane au lieu de moyenne pour éviter outliers
    """
    return statistics.median(scores)
```

## Mode Unidirectionnel

Le Sentiment Agent adapte ses recommandations :

```python
def generate_sentiment_signal(symbol, sentiment_score):
    # Analyser sentiment normalement
    signal = analyze_sentiment_impact(sentiment_score)

    # Appliquer le mode unidirectionnel
    if UNIDIRECTIONAL_MODE:
        if signal.action == 'SELL' and ALLOWED_SIDE == 'long':
            signal.action = 'HOLD'
            signal.reason = 'SELL signals suppressed in LONG-only mode'
        elif signal.action == 'BUY' and ALLOWED_SIDE == 'short':
            signal.action = 'HOLD'
            signal.reason = 'BUY signals suppressed in SHORT-only mode'

    return signal
```

## Intégration HyperLiquid

### Endpoints Utilisés

- `getAllMids()` - Prix pour corrélation
- `getMeta()` - Métadonnées pour impact

### Fréquence d'Analyse

- **News** : 5 minutes
- **Social** : 2 minutes
- **On-Chain** : 15 minutes
- **Corrélation** : 1 minute

## Performance Tracking

### Métriques de Prédiction

| Métrique                        | Cible   | Acceptable |
| ------------------------------- | ------- | ---------- |
| **Sentiment Accuracy**          | > 70%   | > 60%      |
| **Price-Sentiment Correlation** | > 0.6   | > 0.4      |
| **Extreme Prediction**          | > 80%   | > 70%      |
| **Response Time**               | < 200ms | < 500ms    |

### Backtesting

```python
def backtest_sentiment_strategy(data, sentiment_data):
    # Simuler trades basés sur sentiment
    trades = []
    for i in range(len(data)):
        signal = get_sentiment_signal(sentiment_data[i])
        pnl = simulate_trade(data[i], signal)

    return {
        'total_trades': len(trades),
        'win_rate': win_rate,
        'avg_return': avg_return,
        'sharpe': sharpe_ratio,
        'max_drawdown': max_drawdown
    }
```

## Logging

### Winston Logger

```javascript
const sentimentLogger = winston.loggers.get('sentimentLogger');

// Analyse de news
sentimentLogger.info('News sentiment analyzed', {
  source: 'coindesk',
  title: 'Bitcoin ETF approved',
  sentiment: 'VERY_BULLISH',
  intensity: 95,
  confidence: 92,
});

// Score sentiment
sentimentLogger.success('Sentiment score calculated', {
  symbol: 'BTC',
  score: 0.68,
  sources: 15,
  timeframe: '24h',
  trend: 'improving',
});

// Détection d'extrêmes
sentimentLogger.warn('Extreme sentiment detected', {
  symbol: 'ETH',
  type: 'EXTREME_GREED',
  value: 89,
  action: 'SELL_SIGNAL',
  confidence: 76,
});
```

## Monitoring Dashboard

### Indicateurs Clés

- **Overall Sentiment** : Sentiment global (score -1 à +1)
- **Fear & Greed** : Index crypto (0-100)
- **News Impact** : Impact des news récentes
- **Social Momentum** : Momentum social
- **Whale Activity** : Activité baleines

### Graphiques

- Sentiment score timeline
- Fear & Greed evolution
- Corrélation prix-sentiment
- Heatmap des sources
- Word cloud des émotions

## APIs et Endpoints

### Endpoints Backend

- `GET /api/agents/sentiment/status` - Status du sentiment agent
- `GET /api/agents/sentiment/current` - Sentiment actuel
- `GET /api/agents/sentiment/history` - Historique
- `GET /api/agents/sentiment/news` - News analysées
- `GET /api/agents/sentiment/fear-greed` - Fear & Greed Index

### Exemple de Réponse

```json
{
  "status": "ACTIVE",
  "confidence": 0.84,
  "current_sentiment": {
    "score": 0.72,
    "label": "BULLISH",
    "confidence": 84,
    "sources": 23,
    "trend": "improving"
  },
  "fear_greed": {
    "value": 68,
    "label": "GREED",
    "components": {
      "volatility": 45,
      "momentum": 72,
      "social_media": 81,
      "surveys": 63,
      "dominance": 55,
      "trends": 73
    }
  },
  "extreme_signals": {
    "extreme_fear": false,
    "extreme_greed": false
  }
}
```

## Troubleshooting

### Problèmes Courants

#### 1. Bruit dans les Données

**Symptôme** : Sentiment instable **Solution** :

- Augmenter période d'agrégation
- Améliorer filtres de qualité
- Vérifier crédibilité sources

#### 2. Faux Positifs News

**Symptôme** : News pump/fake **Solution** :

- Whitelist sources fiables
- Croiser informations
- Attendre confirmation

#### 3. Latence API

**Symptôme** : Données obsolètes **Solution** :

- Cache local
- APIs prioritaires
- Fallback sources

#### 4. Overfitting Historique

**Symptôme** : Bonne perf backtest, mauvaise live **Solution** :

- Walk-forward analysis
- Régularisation
- Éviter sur-optimisation

## Amélioration Continue

### Enrichissement des Sources

- **Alternative Data** : Satellite, Google Trends
- **NLP Avancé** : BERT, GPT sentiment
- **Real-time** : Streaming data
- **Cross-Asset** : Corrélations inter-marchés

### Automatisation

- **Auto-training** : Modèles auto-adaptatifs
- **Dynamic Weighting** : Pondération dynamique
- **Smart Alerts** : Alertes intelligentes
- **Portfolio Sentiment** : Sentiment global

## Conclusion

Le Sentiment Agent est le **baromètre émotionnel** du système NOVAQUOTE. Sa
capacité à mesurer et interpréter le sentiment du marché lui permet d'identifier
les opportunités basées sur la psychologie des investisseurs.

Sa collaboration avec le Strategy Agent crée un système hybride
technique-sentiment, plus robuste et nuance. Couplé au Risk Agent, il garantit
que les décisions basées sur le sentiment respectent les règles de risque.
