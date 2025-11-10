# 🛡️ Risk Agent Documentation

## Vue d'ensemble

Le **Risk Agent** est l'agent IA principal responsable de la gestion du risque
en temps réel dans le système NOVAQUOTE. Il utilise des appels LLM (Claude +
DeepSeek) pour prendre des décisions intelligentes de protection du
portefeuille.

## Informations Générales

- **Nom** : Risk Agent
- **Status** : ✅ ACTIVE
- **Confidence** : 85%
- **Appels LLM** : Claude
- **Temps de réponse** : 115ms
- **Fichier source** : `src/agents/risk_agent.py`
- **Type** : Agent IA véritable (avec appels LLM)

## Responsabilités

### 1. 🛡️ Surveillance du Risque en Temps Réel

- Monitoring continu des positions actives
- Calcul du risque de portefeuille (VaR, drawdown)
- Surveillance de la volatilité du marché
- Analyse de corrélation entre positions

### 2. 🎯 Gestion des Stop-Loss

- Calcul automatique des niveaux de stop-loss
- Ajustement dynamique basé sur la volatilité
- Exécution automatique en cas de dépassement
- Protection contre les glissements de marché

### 3. ⚖️ Contrôle de l'Exposition

- Limitation de l'exposition par actif
- Vérification de l'exposition totale du portefeuille
- Respect des limites de levier (max 50x sur HyperLiquid)
- Alertes en cas de dépassement

### 4. 🚨 Détection des Anomalies

- Détection de patterns de trading suspects
- Identification de comportements anormaux
- Surveillance des spreads et slippage
- Alertes de liquidité insuffisante

## Intégration LLM

### Modèles Utilisés

- **Claude** : Analyse de risque complexe, prise de décision
- **DeepSeek** : Calculs quantitatifs, modélisation mathématique

### Prompts Typiques

#### Analyse de Risque

```
Analyse le risque de la position suivante:
- Symbol: {symbol}
- Side: {side}
- Size: {size}
- Entry Price: {entryPrice}
- Current Price: {currentPrice}
- Volatility: {volatility}
- Portfolio Exposure: {exposure}

Évalue:
1. Risque de perte maximale
2. Probabilité de hit du stop-loss
3. Impact sur le portefeuille
4. Recommandation (maintenir/ajuster/fermer)
```

#### Décision d'Urgence

```
🚨 ALERTE RISQUE DÉTECTÉE 🚨

Situation:
- P&L actuel: {pnl}
- Drawdown: {drawdown}
- Volatilité: {volatility}
- Exposition: {exposure}

Décision urgente requise:
- Fermer position? (OUI/NON)
- Ajuster stop-loss? (niveau)
- Réduire exposition? (pourcentage)
- Justification:
```

## Métriques Surveillées

### Métriques de Risque

| Métrique                 | Seuil d'Alerte       | Seuil Critique        |
| ------------------------ | -------------------- | --------------------- |
| **VaR 95%**              | > 5% du portefeuille | > 10% du portefeuille |
| **Drawdown Max**         | > 8%                 | > 15%                 |
| **Exposition par Actif** | > 30%                | > 50%                 |
| **Leverage Total**       | > 5x                 | > 10x                 |
| **Volatilité Portfolio** | > 20%                | > 30%                 |

### Métriques de Performance

- **Win Rate** : Pourcentage de décisions correctes
- **Average Response Time** : 115ms (cible < 200ms)
- **Risk-Adjusted Return** : Return ajusté du risque
- **Maximum Favorable Excursion** : Profit maximum atteint
- **Maximum Adverse Excursion** : Perte maximum subie

## Actions Automatiques

### Niveau 1 - Information

- Alerte dans les logs
- Notification dashboard
- Monitoring renforcé

### Niveau 2 - Avertissement

- Ajustement stop-loss
- Réduction position (50%)

### Niveau 3 - Critique

- Fermeture automatique position
- Arrêt du trading
- Isolation des risques

## Configuration

### Paramètres par Défaut

```python
# Risque
MAX_PORTFOLIO_RISK = 0.15  # 15% max
MAX_SINGLE_POSITION = 0.30  # 30% max
MAX_LEVERAGE = 10  # 10x max (conservateur)
MAX_DRAWDOWN = 0.08  # 8% max

# Stop-Loss
DEFAULT_SL_ATR_MULTIPLIER = 2.0  # 2x ATR
MIN_SL_DISTANCE = 0.02  # 2% min

# Volatilité
MAX_VOLATILITY = 0.25  # 25% max
ATR_PERIOD = 14  # 14 périodes
```

### Personnalisation

```python
# Mode Conservateur
MAX_PORTFOLIO_RISK = 0.10
MAX_SINGLE_POSITION = 0.20
MAX_LEVERAGE = 5

# Mode Agresif
MAX_PORTFOLIO_RISK = 0.20
MAX_SINGLE_POSITION = 0.40
MAX_LEVERAGE = 20
```

## Mode Unidirectionnel

Le Risk Agent est le **gardien** du mode unidirectionnel :

### Validation Pré-Trade

```python
def validate_position(symbol, side, size):
    # Vérifier position opposée existante
    opposite = get_opposite_position(symbol, side)
    if opposite and UNIDIRECTIONAL_MODE:
        return {
            'approved': False,
            'reason': f'Position {side} refusée: {opposite.side} existe déjà',
            'action': 'REJECT'
        }

    # Vérifier direction autorisée
    if ALLOWED_SIDE != 'both' and side != ALLOWED_SIDE:
        return {
            'approved': False,
            'reason': f'Seules les positions {ALLOWED_SIDE} autorisées',
            'action': 'REJECT'
        }

    return {'approved': True}
```

## Intégration HyperLiquid

### Endpoints Utilisés

- `getAllMids()` - Prix mark en temps réel
- `getMeta()` - Métadonnées des symboles
- `getUserState()` - État du compte
- `getPositions()` - Positions actives
- `placeOrder()` / `cancelOrder()` - Exécution ordonnances

### Fréquence de Mise à Jour

- **Prix** : Temps réel (WebSocket)
- **Positions** : 1 seconde
- **Risk Metrics** : 5 secondes
- **Portfolio** : 10 secondes

## Logging

### Winston Logger

```javascript
const riskLogger = winston.loggers.get('riskLogger');

// Exemple de logs
riskLogger.info('Risk analysis completed', {
  position: 'BTC-LONG',
  riskScore: 0.65,
  recommendation: 'MAINTAIN',
});

riskLogger.warn('Risk threshold exceeded', {
  metric: 'VaR',
  value: 0.12,
  threshold: 0.1,
});

riskLogger.error('Critical risk detected', {
  action: 'POSITION_CLOSED',
  symbol: 'ETH',
  reason: 'Drawdown exceeded',
});
```

## Monitoring Dashboard

### Indicateurs Clés

- **Risk Score** : Score global de risque (0-100)
- **Active Alerts** : Nombre d'alertes actives
- **Positions Monitored** : Positions sous surveillance
- **Last Decision** : Dernière décision prise
- **Avg Response Time** : Temps de réponse moyen

### Graphiques

- Evolution du risk score
- Drawdown en temps réel
- Exposition par actif (pie chart)
- Performance des décisions

## Troubleshooting

### Problèmes Courants

#### 1. LLM Timeout

**Symptôme** : Response time > 500ms **Solution** :

- Vérifier la connectivité API
- Réduire la complexité des prompts
- Augmenter le timeout

#### 2. Faux Positifs

**Symptôme** : Alertes excessives **Solution** :

- Ajuster les seuils de risque
- Améliorer les prompts LLM
- Ajouter des filtres de bruit

#### 3. Décisions Contradictoires

**Symptôme** : Actions incohérentes **Solution** :

- Vérifier la logique LLM
- Ajouter une validation croisée
- Implémenter un système de vote

## Amélioration Continue

### Feedback Loop

1. Collecter les résultats des décisions
2. Analyser la performance (true/false positives)
3. Ajuster les seuils et prompts
4. Redéployer avec les améliorations

### A/B Testing

- Tester différentes configurations
- Comparer les performances
- Sélectionner les meilleurs paramètres

## APIs et Endpoints

### Endpoints Backend

- `GET /api/agents/risk/status` - Status du risk agent
- `POST /api/agents/risk/config` - Modifier la configuration
- `GET /api/agents/risk/metrics` - Métriques détaillées
- `GET /api/agents/risk/history` - Historique des décisions

### Exemple de Réponse

```json
{
  "status": "ACTIVE",
  "confidence": 0.85,
  "decisions_made": 1247,
  "avg_response_time": 115,
  "current_risk_score": 0.42,
  "positions_monitored": 8,
  "active_alerts": 0,
  "last_decision": {
    "timestamp": "2025-11-08T00:24:57.491Z",
    "action": "MAINTAIN",
    "symbol": "BTC",
    "reason": "Risk within acceptable limits"
  }
}
```

## Conclusion

Le Risk Agent est le **pilier de sécurité** du système NOVAQUOTE. Sa capacité à
analyser le risque en temps réel et à prendre des décisions éclairées via LLM
garantit la protection du capital et la conformité aux règles de trading
définies.

Sa collaboration avec les autres agents (Strategy, Funding, Sentiment) crée un
écosystème de trading intelligent et sécurisé.
