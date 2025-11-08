# 💰 Funding Agent Documentation

## Vue d'ensemble

Le **Funding Agent** est l'agent IA spécialisé dans la détection et
l'exploitation des opportunités de funding arbitrage sur HyperLiquid. Il utilise
**Claude Code Sub-Agents** pour analyser les taux de funding et identifier les
trades rentables.

## Informations Générales

- **Nom** : Funding Agent
- **Status** : ✅ ACTIVE
- **Confidence** : 78%
- **Appels LLM** : Claude (via sub-agent)
- **Sub-Agent** : claude-funding-advisor
- **Temps de réponse** : 109ms
- **Fichier source** : `src/agents/funding_agent.py`
- **Type** : Agent IA véritable (avec Claude Code sub-agents)

## Responsabilités

### 1. 💹 Surveillance des Taux de Funding

- Monitoring en temps réel des taux de funding
- Comparaison inter-exchanges
- Détection d'anomalies et opportunités
- Alertes sur les écarts significatifs

### 2. 🔄 Arbitrage de Funding

- Calcul des spreads de taux
- Optimisation des positions de couverture
- Exécution automatique des arbitrages
- Gestion du risque de basis

### 3. 📊 Analyse de Rentabilité

- Calcul du yield annualisé
- Analyse coût/bénéfice
- Projection de收益 sur différentes périodes
- Optimisation du capital alloué

### 4. 🎯 Stratégies de Funding

- **Spot-Futures Arbitrage** : Couverture spot vs perp
- **Cross-Exchange Arbitrage** : Multi-exchanges
- **Funding Harvesting** : Collecte de funding positif
- **Basis Trading** : Trading de base (perp - spot)

## Compréhension du Funding

### Qu'est-ce que le Funding ?

Le **funding rate** est un paiement périodique (toutes les 8h sur HyperLiquid)
entre les longues et les courtes positions sur les perpetual swaps.

**Formule :**

```
Funding = Position Size × (Mark Price - Index Price) / Index Price
```

**Exemple :**

- Position : 1 BTC LONG
- Mark Price : $50,000
- Index Price : $49,500
- Funding Rate : 0.01%
- **Funding reçu** : 1 × ($50,000 - $49,500) / $49,500 = **0.0101 BTC**

### Types d'Opportunités

#### 1. Funding Positif (LONG pay SHORT)

- **Quand** : Mark > Index
- **Action** : Ouvrir LONG, couvrir en spot
- **Gain** : Recevoir funding à chaque période
- **Risque** : Movement adverse du spot

#### 2. Funding Négatif (SHORT pay LONG)

- **Quand** : Mark < Index
- **Action** : Ouvrir SHORT, couvrir en spot
- **Gain** : Payer moins de funding que reçu en compensation
- **Risque** : Movement adverse du spot

#### 3. Cross-Exchange Arbitrage

- **Comparaison** : Funding rate HyperLiquid vs Binance/Bybit
- **Action** : LONG sur l'exchange à taux élevé, SHORT sur l'autre
- **Gain** : Différence des taux
- **Risque** : Risque de contrepartie, latence

## Intégration LLM

### Méthode d'Appel

Le Funding Agent utilise **Claude Code CLI** avec un sub-agent spécialisé au
lieu d'appels API directs.

### Sub-Agent Utilisé

- **Nom** : `claude-funding-advisor`
- **Type** : Sub-agent Claude Code
- **Invocation** : Via
  `claude --agent claude-funding-advisor --dangerously-skip-permissions`

### Prompt Système

```python
FUNDING_ANALYSIS_PROMPT = '''
You are Deamon Dev's Funding Rate Analysis Assistant

Analyze the funding rate opportunity and provide a trading recommendation:

Symbol: {symbol}
Current Funding Rate: {rate}% (annualized: {annual_rate}%)
Market Context: {context}

Evaluate:
1. Is this a profitable arbitrage opportunity?
2. Risk/reward ratio
3. Recommended action: BUY/SELL/NOTHING
4. Position size suggestion
5. Expected duration

Respond in this format:
1. First line: BUY, SELL, or NOTHING
2. Brief reasoning (1-2 lines)
3. Confidence: X%
4. Position size recommendation
5. Risk factors
'''
```

## Calculs et Métriques

### Yield Annualisé

```python
def calculate_annualized_yield(funding_rate, frequency_per_year=1095):
    """
    funding_rate: Taux de funding par période (ex: 0.01% = 0.0001)
    frequency_per_year: 1095 = 3 fois par jour × 365
    """
    return funding_rate * frequency_per_year
```

**Exemple :**

- Funding rate : 0.01% toutes les 8h
- Annualisé : 0.01% × 1095 = **10.95% par an**

### Basis (’écart Perp-Spot)

```python
basis = (perp_price - spot_price) / spot_price
```

**Types de basis :**

- **Contango** : Perp > Spot (fonding positif attendu)
- **Backwardation** : Perp < Spot (fonding négatif attendu)

### ROI d'Arbitrage

```python
def calculate_arbitrage_roi(funding_received, spot_costs, position_size):
    net_funding = funding_received - spot_costs
    roi = (net_funding / position_size) * 100
    return roi
```

## Stratégies Implémentées

### 1. Spot-Perp Arbitrage

```python
def spot_perp_arbitrage(symbol, funding_rate, position_size):
    # Étape 1: Ouvrir position perp
    perp_order = place_perp_order(
        symbol=symbol,
        side='LONG' if funding_rate > 0 else 'SHORT',
        size=position_size
    )

    # Étape 2: Couverture spot (inverse)
    spot_order = place_spot_order(
        symbol=symbol,
        side='SHORT' if funding_rate > 0 else 'LONG',
        size=position_size
    )

    return {
        'perp_order': perp_order,
        'spot_order': spot_order,
        'hedge_ratio': 1.0
    }
```

### 2. Funding Harvesting

```python
def harvest_funding(symbol, min_rate, max_position):
    current_rate = get_funding_rate(symbol)

    if current_rate >= min_rate:
        # Calculer taille optimale
        size = calculate_optimal_size(symbol, current_rate)

        if size <= max_position:
            return open_funding_position(symbol, size)
        else:
            return {
                'action': 'WAIT',
                'reason': 'Position size exceeds limit'
            }

    return {
        'action': 'WAIT',
        'reason': f'Rate {current_rate}% below threshold {min_rate}%'
    }
```

### 3. Cross-Exchange Basis Trade

```python
def cross_exchange_arbitrage(symbol, hl_rate, other_rate):
    rate_diff = hl_rate - other_rate

    if abs(rate_diff) > MIN_RATE_DIFF:
        # LONG sur l'exchange avec taux élevé
        # SHORT sur l'exchange avec taux faible
        return open_cross_hedge(symbol, rate_diff)
```

## Gestion du Risque

### Risques Identifiés

1. **Movement Spot** : Le spot bouge et réduit le profit d'arbitrage
2. **Liquidity Risk** : Difficulté à couvrir ou déboucler
3. **Funding Change** : Le taux change avant la prochaine période
4. **Counterparty Risk** : Risque d'échange
5. **Execution Risk** : Slippage, latence

### Stratégies de Mitigation

#### 1. Dynamic Hedging

```python
def dynamic_hedge(symbol, target_ratio=1.0):
    current_ratio = get_hedge_ratio(symbol)

    if abs(current_ratio - target_ratio) > HEDGE_TOLERANCE:
        adjust_hedge(symbol, target_ratio)
```

#### 2. Stop-Loss Basis

```python
def monitor_basis(symbol, entry_basis, max_basis_move):
    current_basis = calculate_basis(symbol)
    basis_move = abs(current_basis - entry_basis)

    if basis_move > max_basis_move:
        close_arbitrage(symbol, reason='Basis moved too far')
```

#### 3. Rate Floor/Ceiling

```python
RATE_LIMITS = {
    'min_profitable_rate': 0.005,  # 0.005% minimum
    'max_funding_exposure': 0.20,  # 20% max du capital
    'min_liquidity': 1000000      # $1M minimum
}
```

## Configuration

### Paramètres par Défaut

```python
# Funding
MIN_FUNDING_RATE = 0.005    # 0.005% minimum
MAX_POSITION_SIZE = 0.15    # 15% du capital max
HEDGE_TOLERANCE = 0.02      # 2% de déviation max

# Arbitrage
MIN_RATE_DIFF = 0.01        # 0.01% différentiel min
MAX_BASIS_MOVE = 0.005      # 0.5% basis move max
REBALANCE_FREQUENCY = '8h'  # Rebalancing toutes les 8h

# Risk
MAX_CAPITAL_ALLOCATION = 0.30  # 30% max du capital
STOP_LOSS_BASIS = 0.02         # 2% stop loss
```

### Personnalisation par Symbol

```python
SYMBOL_CONFIG = {
    'BTC': {
        'min_rate': 0.003,
        'max_size': 0.20,
        'liquidity_threshold': 2000000
    },
    'ETH': {
        'min_rate': 0.005,
        'max_size': 0.15,
        'liquidity_threshold': 1000000
    },
    'SOL': {
        'min_rate': 0.008,
        'max_size': 0.10,
        'liquidity_threshold': 500000
    }
}
```

## Mode Unidirectionnel

Le Funding Agent respecte le mode unidirectionnel :

```python
def open_funding_position(symbol, size, rate):
    # Déterminer la direction du funding
    direction = 'LONG' if rate > 0 else 'SHORT'

    # Vérifier le mode unidirectionnel
    if UNIDIRECTIONAL_MODE and direction != ALLOWED_SIDE:
        return {
            'approved': False,
            'reason': f'Funding arbitrage requires {direction}, but only {ALLOWED_SIDE} allowed',
            'alternative': 'Consider spot-perp basis trade instead'
        }

    return execute_arbitrage(symbol, size, direction)
```

## Intégration HyperLiquid

### Endpoints Utilisés

- `getMeta()` - Métadonnées symboles
- `getAllMids()` - Prix mark
- `placeOrder()` - Ouverture positions perp
- `getUserState()` - État du compte

### Calcul du Funding

```python
def calculate_next_funding(symbol):
    # Récupérer taux actuel
    current_rate = get_current_funding_rate(symbol)

    # Prochaine période de funding
    next_funding_time = get_next_funding_time()

    # Estimer taux futur (moyenne mobile)
    predicted_rate = predict_funding_rate(symbol)

    return {
        'current_rate': current_rate,
        'next_funding': next_funding_time,
        'predicted_rate': predicted_rate
    }
```

## Performance Tracking

### Métriques Clés

| Métrique                | Cible     | Acceptable |
| ----------------------- | --------- | ---------- |
| **Annualized Yield**    | > 12%     | > 8%       |
| **Funding Accuracy**    | > 80%     | > 70%      |
| **Hedge Ratio**         | 100% ± 2% | 100% ± 5%  |
| **Capital Utilization** | 25-30%    | 20-35%     |
| **Basis P&L**           | > 0       | >= 0       |

### Rapport Quotidien

```python
def daily_funding_report():
    return {
        'date': today,
        'total_funding_received': sum(today_funding),
        'total_arbitrages': count_today_trades,
        'average_rate': average_rate,
        'best_opportunity': best_symbol,
        'pnl_breakdown': {
            'funding': funding_pnl,
            'basis': basis_pnl,
            'fees': fees_paid
        }
    }
```

## Logging

### Winston Logger

```javascript
const fundingLogger = winston.loggers.get('fundingLogger');

// Arbitrage ouvert
fundingLogger.info('Arbitrage opened', {
  symbol: 'BTC',
  side: 'LONG',
  size: 0.5,
  rate: 0.015,
  annualized_yield: 16.4,
  hedge_ratio: 1.0,
});

// Funding reçu
fundingLogger.success('Funding received', {
  symbol: 'ETH',
  period: '2025-11-08 00:00:00',
  amount: 0.023,
  value: 78.92,
  annual_rate: 12.8,
});

// Opportunité détectée
fundingLogger.warn('Opportunity detected', {
  symbol: 'SOL',
  rate_diff: 0.045,
  potential_yield: 49.2,
  risk: 'HIGH',
});
```

## Monitoring Dashboard

### Indicateurs Clés

- **Active Arbitrages** : Nombre d'arbitrages en cours
- **Daily Funding** : Funding reçu aujourd'hui
- **Annualized Yield** : Rendement annualisé moyen
- **Best Rate** : Meilleur taux actuellement disponible
- **Capital Utilized** : % du capital utilisé

### Graphiques

- Evolution des funding rates
- P&L cumulatif funding
- Distribution des opportunités
- Heatmap des taux par symbol
- Performance vs benchmarks

## APIs et Endpoints

### Endpoints Backend

- `GET /api/agents/funding/status` - Status du funding agent
- `GET /api/agents/funding/rates` - Taux de funding actuels
- `GET /api/agents/funding/opportunities` - Opportunités détectées
- `POST /api/agents/funding/execute` - Exécuter arbitrage
- `GET /api/agents/funding/performance` - Performance détaillée

### Exemple de Réponse

```json
{
  "status": "ACTIVE",
  "confidence": 0.78,
  "active_arbitrages": 3,
  "daily_funding": 245.67,
  "annualized_yield": 14.2,
  "best_opportunity": {
    "symbol": "SOL",
    "rate": 0.032,
    "yield_annualized": 35.0,
    "risk": "MEDIUM"
  },
  "capital_utilized": 0.23
}
```

## Troubleshooting

### Problèmes Courants

#### 1. Funding Rate Chute Brutalement

**Symptôme** : ROI drops suddenly **Solution** :

- Fermer positions non profitables
- Attendre stabilisation
- Réduire exposition

#### 2. Hedge Ratio Déséquilibré

**Symptôme** : Ratio != 100% **Solution** :

- Rebalancing automatique
- Vérifier exécutions spot
- Ajuster tolérances

#### 3. Latence d'Exécution

**Symptôme** : Opportunités manquées **Solution** :

- Optimiser temps de réponse
- Pré-positionner ordres
- Améliorer connectivité

#### 4. Basis Move Adverses

**Symptôme** : P&L basis négatif **Solution** :

- Stop-loss sur basis
- Réduire taille positions
- Diversifier symbols

## Amélioration Continue

### Optimisations Futures

- **ML Prediction** : Prédiction des taux de funding
- **Dynamic Sizing** : Taille de position adaptative
- **Multi-Exchange** : Plus d'exchanges supportés
- **DeFi Integration** : Intégration yield farming

### Automatisation

- **Auto-Rebalancing** : Rebalancing automatique
- **Smart Hedge** : Couverture intelligente
- **Rate Alerts** : Alertes personnalisables
- **Portfolio Optimization** : Optimisation globale

## Conclusion

Le Funding Agent est le **spécialiste de l'arbitrage** du système NOVAQUOTE. Sa
capacité à détecter et exploiter les opportunités de funding lui permet de
générer des rendements réguliers et peu correlés aux mouvements de prix.

Sa collaboration avec le Risk Agent garantit que tous les arbitrages respectent
les limites de risque et le mode unidirectionnel, créant une source de revenus
stable et durable.
