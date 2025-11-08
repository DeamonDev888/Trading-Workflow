# 📈 Strategy Agent Documentation

## Vue d'ensemble

Le **Strategy Agent** est l'agent IA responsable de l'analyse technique et de la génération de signaux de trading dans le système NOVAQUOTE. Il utilise des appels LLM (Claude) pour interpréter les données de marché et générer des stratégies de trading optimisées.

## Informations Générales

- **Nom** : Strategy Agent
- **Status** : ✅ ACTIVE
- **Confidence** : 80%
- **Appels LLM** : Claude
- **Stratégies actives** : 7
- **Temps de réponse** : 110ms
- **Fichier source** : `src/agents/strategy_agent.py`
- **Type** : Agent IA véritable (avec appels LLM)

## Responsabilités

### 1. 📊 Analyse Technique
- Analyse des chandeliers et patterns
- Calcul d'indicateurs techniques (RSI, MACD, Bollinger, etc.)
- Détection de supports et résistances
- Identification des trends et retournements

### 2. 🎯 Génération de Signaux
- Signaux d'achat (BUY)
- Signaux de vente (SELL)
- Signaux de maintien (HOLD)
- Niveaux d'entrée et de sortie optimaux

### 3. 🧠 Optimisation des Stratégies
- Backtesting automatisé
- Ajustement des paramètres
- Sélection des meilleures configurations
- Adaptation aux conditions de marché

### 4. 🔄 Multi-Timeframe Analysis
- Analyse courte période (1m, 5m)
- Analyse moyenne période (15m, 1h)
- Analyse longue période (4h, 1d)
- Synthèse des signaux multi-échelles

## Stratégies Implémentées

### 1. Moving Average Crossover (MA Cross)
```python
def ma_crossover_strategy(data, fast=9, slow=21):
    # Signal: MA rapide > MA lente = BUY
    # Signal: MA rapide < MA lente = SELL
```

**Paramètres :**
- Fast MA : 9, 12, 18
- Slow MA : 21, 26, 50
- Timeframes : 1h, 4h

### 2. RSI Mean Reversion
```python
def rsi_strategy(data, period=14, oversold=30, overbought=70):
    # Signal: RSI < 30 = BUY (oversold)
    # Signal: RSI > 70 = SELL (overbought)
```

**Paramètres :**
- Période RSI : 14, 21
- Seuil oversold : 25, 30
- Seuil overbought : 70, 75

### 3. MACD Divergence
```python
def macd_strategy(data, fast=12, slow=26, signal=9):
    # Signal: MACD > Signal = BUY
    # Signal: MACD < Signal = SELL
    # Divergence = signal renforcé
```

### 4. Bollinger Bands Squeeze
```python
def bollinger_strategy(data, period=20, std=2):
    # Signal: Squeeze breakout = direction de rupture
    # Signal: Return to mean = mean reversion
```

### 5. Volume Profile Analysis
```python
def volume_strategy(data, lookback=20):
    # Signal: Volume spike = confirmation
    # Signal: OBV divergence = signal fort
```

### 6. Support/Resistance Breakout
```python
def sr_strategy(data, lookback=50):
    # Signal: Breakout au-dessus résistance = BUY
    # Signal: Breakout en-dessous support = SELL
```

### 7. Multi-Indicator Confluence
```python
def confluence_strategy(indicators):
    # Signal: 3+ indicateurs alignés = signal fort
    # Signal: Conflit = pas de trade
```

## Intégration LLM

### Méthode d'Appel
Le Strategy Agent utilise **Claude Code CLI** avec un sub-agent spécialisé au lieu d'appels API directs.

### Sub-Agent Utilisé
- **Nom** : `claude-strategy-advisor`
- **Type** : Sub-agent Claude Code
- **Invocation** : Via `claude --agent claude-strategy-advisor --dangerously-skip-permissions`

### Modèle de Configuration
Le système récupère sa configuration depuis `config.py` :
- **AI_MODEL** : Modèle configuré (ex: "glm-4.6", "claude-3-5-haiku-latest")
- **AI_TEMPERATURE** : Température des réponses (ex: 0.7)
- **AI_MAX_TOKENS** : Nombre maximum de tokens (ex: 1024)

Ces paramètres sont transmis au sub-agent dans les données contextuelles.

### Prompts Typiques

Le Strategy Agent utilise un prompt système spécialisé :

```python
STRATEGY_EVAL_PROMPT = """
You are Deamon Dev's Strategy Validation Assistant [OK]

Analyze the following strategy signals and validate their recommendations:
- Evaluate each strategy signal's reasoning
- Check if signals align with current market conditions
- Look for confirmation/contradiction between different strategies
- Consider risk factors

Response format:
1. First line: EXECUTE or REJECT for each signal
2. Then explain your reasoning

Remember: Deamon Dev prioritizes risk management! [SHIELD]
"""
```

#### Analyse de Pattern
```
Analyse le graphique suivant pour {symbol} sur {timeframe}:

Données OHLCV (100 dernières bougies):
{ohlcv_data}

Indicateurs calculés:
- RSI: {rsi}
- MACD: {macd}
- MA: {ma}
- Bollinger: {bb}
- Volume: {volume}

Analyse:
1. Trend direction (bullish/bearish/neutral)
2. Momentum (fort/moyen/faible)
3. Pattern identifié (triangle/flags/head&shoulders/etc.)
4. Signal de trading (BUY/SELL/HOLD)
5. Confiance (0-100%)
6. Niveaux clés (support/résistance)
7. Risk/reward ratio estimé
```

#### Génération de Signal
```
Génère un signal de trading pour {symbol}:

Conditions actuelles:
- Trend: {trend}
- Momentum: {momentum}
- Volatilité: {volatility}
- Volume: {volume}
- Stratégies activées: {active_strategies}

Décision requise:
- Action: BUY/SELL/HOLD
- Force du signal: 1-10
- Confiance: 0-100%
- Prix d'entrée: {entry_price}
- Stop-loss: {sl_price}
- Take-profit: {tp_price}
- Risk/reward: {rr_ratio}
```

## Indicateurs Techniques

### Indicateurs Principaux
| Indicateur | Période | Signal | Interpretation |
|------------|---------|--------|----------------|
| **RSI** | 14 | < 30 / > 70 | Oversold / Overbought |
| **MACD** | 12,26,9 | Signal line cross | Momentum change |
| **SMA** | 9,21,50 | Price cross | Trend direction |
| **EMA** | 12,26 | Price cross | Trend + weighted |
| **Bollinger** | 20, 2σ | Band touch/break | Volatility |
| **ATR** | 14 | Volatility | Stop-loss distance |
| **Volume** | 20 | Spike/dry | Confirmation |

### Indicateurs Avancés
- **Ichimoku Cloud** : Trend + momentum
- **Stochastic** : Oscillateur
- **Williams %R** : Momentum
- **CCI** : Commodity Channel Index
- **OBV** : On-Balance Volume
- **VWAP** : Volume Weighted Average

## Configuration des Stratégies

### Paramètres Globaux
```python
# Stratégies
ACTIVE_STRATEGIES = [
    'ma_crossover',
    'rsi_reversion',
    'macd_divergence',
    'bollinger_squeeze',
    'volume_profile',
    'sr_breakout',
    'confluence'
]

# Signal
MIN_SIGNAL_STRENGTH = 6  # 1-10
MIN_CONFIDENCE = 70      # 0-100
MIN_RISK_REWARD = 1.5    # Minimum R/R

# Timeframes
PRIMARY_TIMEFRAME = '1h'
SECONDARY_TIMEFRAMES = ['15m', '4h']
CONFIRMATION_TIMEFRAMES = ['5m', '1d']
```

### Pondération des Signaux
```python
SIGNAL_WEIGHTS = {
    'ma_crossover': 0.15,
    'rsi_reversion': 0.12,
    'macd_divergence': 0.18,
    'bollinger_squeeze': 0.15,
    'volume_profile': 0.10,
    'sr_breakout': 0.15,
    'confluence': 0.15
}

# Score final = Σ(weight * signal * strength * confidence)
```

## Filtres et Validation

### Filtres de Qualité
```python
# Filtre volatilité
MIN_VOLATILITY = 0.02   # 2%
MAX_VOLATILITY = 0.25   # 25%

# Filtre volume
MIN_VOLUME_RATIO = 1.5  # 1.5x moyenne

# Filtre spread
MAX_SPREAD = 0.001      # 0.1%

# Filtre liquidité
MIN_LIQUIDITY = 100000  # $100k
```

### Validation Croisée
```python
def validate_signal(signal):
    # Minimum 2 stratégies alignées
    aligned_strategies = count_aligned_strategies(signal)
    if aligned_strategies < 2:
        return REJECT

    # Timeframe alignment
    if not timeframes_aligned(signal):
        return REJECT

    # Risk validation
    if not risk_agent.validate(signal):
        return REJECT

    return APPROVE
```

## Backtesting Intégré

### Métriques de Performance
| Métrique | Cible | Acceptable |
|----------|-------|------------|
| **Win Rate** | > 60% | > 50% |
| **Sharpe Ratio** | > 1.5 | > 1.0 |
| **Max Drawdown** | < 10% | < 15% |
| **Profit Factor** | > 1.5 | > 1.2 |
| **Avg Trade** | > 0.5% | > 0.2% |

### Optimisation Automatique
```python
def optimize_parameters(strategy, data):
    # Grid search sur les paramètres
    best_params = grid_search(strategy, data)
    backtest_result = backtest(best_params, data)

    # Si amélioration > 5%, appliquer
    if backtest_result.sharpe > current.sharpe * 1.05:
        update_strategy_params(strategy, best_params)

    return best_params
```

## Mode Unidirectionnel

Le Strategy Agent respecte la direction autorisée :

```python
def generate_signal(symbol, timeframe):
    signal = analyze_technical_indicators(symbol, timeframe)

    # Filtrer selon le mode unidirectionnel
    if TRADING_CONFIG.UNIDIRECTIONAL_MODE:
        if signal.side == 'SELL' and TRADING_CONFIG.ALLOWED_SIDE == 'long':
            signal.side = 'HOLD'
            signal.reason = 'SELL not allowed in unidirectional mode'
        elif signal.side == 'BUY' and TRADING_CONFIG.ALLOWED_SIDE == 'short':
            signal.side = 'HOLD'
            signal.reason = 'BUY not allowed in unidirectional mode'

    return signal
```

## Intégration HyperLiquid

### Endpoints Utilisés
- `getAllMids()` - Prix mark
- `getMeta()` - Métadonnées symboles
- `getCandleSnapshot()` - Données OHLCV (si disponible)
- `placeOrder()` - Exécution signaux

### Fréquence d'Analyse
- **Signaux** : 1 minute
- **Backtest** : 1 heure
- **Optimisation** : 1 jour
- **Reconfiguration** : 1 semaine

## Logging

### Winston Logger
```javascript
const strategyLogger = winston.loggers.get('strategyLogger');

// Signal généré
strategyLogger.info('Signal generated', {
  symbol: 'BTC',
  action: 'BUY',
  strength: 8,
  confidence: 85,
  strategies: ['macd', 'ma_cross', 'confluence']
});

// Backtest terminé
strategyLogger.success('Backtest completed', {
  strategy: 'rsi_reversion',
  period: '30d',
  win_rate: 0.68,
  sharpe: 1.8
});

// Optimisation
strategyLogger.info('Parameters optimized', {
  strategy: 'bollinger_squeeze',
  old_params: { period: 20, std: 2 },
  new_params: { period: 18, std: 2.2 },
  improvement: 0.12
});
```

## Monitoring Dashboard

### Indicateurs Clés
- **Active Strategies** : 7 stratégies actives
- **Signals Today** : Signaux générés aujourd'hui
- **Win Rate** : Taux de réussite
- **Average Confidence** : Confiance moyenne
- **Best Performing** : Stratégie la plus performante

### Graphiques
- Performance par stratégie
- Signaux générés (timeline)
- Win rate évolution
- Heatmap de confiance
- Distribution des signals

## APIs et Endpoints

### Endpoints Backend
- `GET /api/agents/strategy/status` - Status du strategy agent
- `POST /api/agents/strategy/config` - Configurer stratégies
- `GET /api/agents/strategy/signals` - Signaux récents
- `GET /api/agents/strategy/performance` - Performance détaillée
- `GET /api/agents/strategy/backtest` - Résultats backtest

### Exemple de Réponse
```json
{
  "status": "ACTIVE",
  "confidence": 0.80,
  "active_strategies": 7,
  "signals_today": 23,
  "win_rate": 0.67,
  "best_strategy": "macd_divergence",
  "last_signal": {
    "timestamp": "2025-11-08T00:24:57.491Z",
    "symbol": "BTC",
    "action": "BUY",
    "strength": 8,
    "confidence": 85,
    "entry": 103200,
    "stop_loss": 101500,
    "take_profit": 105000
  }
}
```

## Troubleshooting

### Problèmes Courants

#### 1. Trop de Faux Signaux
**Symptôme** : Win rate < 50%
**Solution** :
- Augmenter le seuil de force du signal
- Ajouter plus de filtres de validation
- Réduire le nombre de stratégies

#### 2. Signaux Retardés
**Symptôme** : Entrée tardive sur les mouvements
**Solution** :
- Réduire la période des indicateurs
- Ajouter des timeframes plus courts
- Implémenter la détection précoce

#### 3. Conflits entre Stratégies
**Symptôme** : Signaux contradictoires
**Solution** :
- Améliorer l'algorithme de pondération
- Ajouter un système de vote
- Prioriser certaines stratégies

#### 4. Sur-Optimisation
**Symptôme** : Bonne perf backtest, mauvaise perf live
**Solution** :
- Utiliser plus de données out-of-sample
- Implémenter walk-forward analysis
- Ajouter de la régularisation

## Amélioration Continue

### Cycle d'Amélioration
1. **Collecte** : Signaux et résultats
2. **Analyse** : Performance par stratégie
3. **Optimisation** : Ajustement paramètres
4. **Test** : Validation sur données récentes
5. **Déploiement** : Mise en production

### Nouvelles Stratégies
- **Machine Learning** : Intégration de modèles ML
- **Deep Learning** : Réseaux de neurones
- **NLP** : Analyse de sentiment news
- **Alternative Data** : On-chain, social, etc.

## Conclusion

Le Strategy Agent est le **cerveau analytique** du système NOVAQUOTE. Sa capacité à générer des signaux de trading basés sur l'analyse technique avancée et l'IA lui permet d'identifier les meilleures opportunités de marché.

Sa collaboration avec le Risk Agent garantit que tous les signaux respectent les règles de risque et le mode unidirectionnel, créant un système de trading équilibré et performant.
