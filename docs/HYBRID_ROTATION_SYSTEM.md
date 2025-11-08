# Hybrid Rotation System - Documentation Complète

## 🎯 Vue d'Ensemble

Le **Hybrid Rotation System** est un système intelligent qui combine la rotation
automatique des cryptomonnaies avec le contrôle utilisateur. Il offre le
meilleur des deux mondes : optimisation par IA et préférences utilisateur
personnalisées.

## 🔄 Les 5 Modes de Contrôle

### 1. FULL_AUTO (100% Automatique)

- **Description** : Rotation entièrement gérée par l'IA sans intervention
  utilisateur
- **Idéal pour** : Utilisateurs qui veulent une gestion complètement passive
- **Comportement** : L'IA analyse, décide et exécute toutes les rotations

### 2. USER_GUIDED (Guidé par l'Utilisateur)

- **Description** : Rotation automatique qui suit les préférences utilisateur
- **Idéal pour** : Utilisateurs qui veulent définir leurs préférences et laisser
  l'IA optimiser
- **Comportement** : L'IA respecte les scores de préférence et les poids définis
  par l'utilisateur

### 3. USER_OVERRIDE (Priorité Utilisateur)

- **Description** : Les décisions utilisateur prennent le priorité sur les
  suggestions IA
- **Idéal pour** : Utilisateurs actifs qui veulent garder le contrôle final
- **Comportement** : L'IA suggère mais l'utilisateur peut toujours annuler

### 4. SEMI_AUTO (Semi-Automatique)

- **Description** : L'utilisateur gère les décisions critiques, l'IA optimise le
  reste
- **Idéal pour** : Utilisateurs qui veulent gérer uniquement les risques
  importants
- **Comportement** : Alertes uniquement pour les problèmes critiques,
  optimisation automatique du reste

### 5. COLLABORATIVE (Collaboratif)

- **Description** : L'IA suggère des améliorations, l'utilisateur décide
- **Idéal pour** : Utilisateurs qui veulent des suggestions IA avant de décider
- **Comportement** : Analyse et suggestions avec justification, validation
  utilisateur requise

## 🏗️ Architecture du Système

### Composants Principaux

#### 1. HybridRotationManager

- Cœur du système hybride
- Gère les 5 modes de contrôle
- Coordonne IA et utilisateur
- Apprend des comportements utilisateur

#### 2. AutomaticCoinRotator

- Moteur de rotation automatique
- Analyse de performance
- Génération de suggestions
- Optimisation continue

#### 3. HybridRotationAPI

- Interface complète pour le frontend
- 15+ endpoints REST
- Gestion des préférences utilisateur
- Monitoring en temps réel

#### 4. UserPreferences

- Stockage des préférences utilisateur
- Scores de préférence (0.0-1.0)
- Verrouillage d'actifs
- Tags personnalisés

## 🚀 Fonctionnalités Clés

### Intelligence Artificielle

- Analyse de performance en temps réel
- Détection d'opportunités de marché
- Apprentissage adaptatif
- Optimisation multi-critères

### Contrôle Utilisateur

- Préférences par actif (score 0.0-1.0)
- Verrouillage temporaire d'actifs
- Poids personnalisés
- Tags et classifications

### Système d'Apprentissage

- Adaptation aux choix utilisateur
- Évolution des préférences
- Reconnaissance de patterns
- Amélioration continue

### Gestion des Risques

- Analyse de liquidité
- Suivi de volatilité
- Seuils de performance
- Alertes automatiques

## 📡 API Complète

### Endpoints Principaux

```javascript
// Démarrer la rotation hybride
POST /api/hybrid/start
{
  "control_mode": "collaborative",
  "max_assets": 6,
  "auto_weight": 0.6,
  "user_weight": 0.4,
  "learning_enabled": true
}

// Obtenir le statut
GET /api/hybrid/status
{
  "running": true,
  "control_mode": "collaborative",
  "current_assets": ["BTC", "ETH", "SOL"],
  "suggestions": [...],
  "metrics": {...}
}

// Mettre à jour les préférences
PUT /api/hybrid/preferences/{symbol}
{
  "preference_score": 0.9,
  "weight_multiplier": 1.5,
  "lock_until": "2025-12-31T23:59:59Z",
  "tags": ["favorite", "core"]
}

// Gérer les suggestions
POST /api/hybrid/suggestions/{id}/respond
{
  "response": "accept", // "accept", "reject", "modify"
  "modifications": {...} // Optionnel
}

// Forcer une rotation
POST /api/hybrid/force-rotation
{
  "type": "manual",
  "assets": ["BTC", "ETH", "SOL", "AVAX"]
}
```

### Endpoints de Configuration

```javascript
// Changer le mode de contrôle
PUT /api/hybrid/control-mode
{
  "control_mode": "user_override"
}

// Obtenir les modes disponibles
GET /api/hybrid/control-modes

// Obtenir les métriques détaillées
GET /api/hybrid/metrics
```

## 🎨 Interface Frontend

### Dashboard Principal

- **Statut du système** : Mode actuel, actifs en rotation
- **Métriques** : Décisions IA/utilisateur, satisfaction
- **Suggestions** : Listes interactives avec boutons accept/reject
- **Performance** : Graphiques en temps réel

### Gestion des Préférences

- **Slider de préférence** : 0.0 (déteste) à 1.0 (adore)
- **Bouton de verrouillage** : Empêcher la rotation d'un actif
- **Tags personnalisés** : "favori", "core", "expérimental"
- **Poids personnalisé** : Influence sur les décisions

### Panneau de Contrôle

- **Sélecteur de mode** : 5 options avec descriptions
- **Configuration automatique** : Poids IA/utilisateur
- **Alertes** : Notifications pour actions requises
- **Historique** : Log détaillé des décisions

## 📊 Scénarios d'Utilisation

### Pour le Débutant

```javascript
// Mode COLLABORATIVE
// L'IA suggère, l'utilisateur apprend
{
  "control_mode": "collaborative",
  "learning_enabled": true,
  "suggestion_threshold": 0.7
}
```

### Pour l'Investisseur Actif

```javascript
// Mode USER_OVERRIDE
// Contrôle total avec optimisation IA
{
  "control_mode": "user_override",
  "auto_weight": 0.3,
  "user_weight": 0.7
}
```

### Pour le Trader Passif

```javascript
// Mode USER_GUIDED
// Définir les préférences, laisser l'IA travailler
{
  "control_mode": "user_guided",
  "user_preferences": {
    "BTC": {"score": 1.0, "locked": true},
    "ETH": {"score": 0.8},
    "SOL": {"score": 0.6}
  }
}
```

### Pour l'Expert en Risque

```javascript
// Mode SEMI_AUTO
// Alertes seulement pour les problèmes critiques
{
  "control_mode": "semi_auto",
  "critical_threshold": 0.2,
  "monitoring_level": "high"
}
```

## 🧠 Apprentissage et Adaptation

### Types d'Apprentissage

#### 1. Apprentissage des Préférences

- Analyse des réponses utilisateur
- Adaptation des scores de préférence
- Reconnaissance de patterns de décision

#### 2. Apprentissage de Performance

- Corrélation préférences/performance
- Ajustement automatique des poids
- Optimisation des recommandations

#### 3. Apprentissage de Marché

- Adaptation aux conditions de marché
- Reconnaissance de régimes
- Prédictions d'opportunités

### Métriques d'Apprentissage

- **Taux d'acceptation** des suggestions
- **Satisfaction utilisateur** estimée
- **Performance ajustée** au risque
- **Efficacité des adaptations**

## 🔧 Configuration Avancée

### Paramètres du Système

```javascript
const config = {
  // Contrôle
  control_mode: 'collaborative',
  max_assets: 6,

  // Pondération
  auto_weight: 0.6, // Influence des décisions IA
  user_weight: 0.4, // Influence des préférences

  // Seuils
  suggestion_threshold: 0.7, // Seuil de suggestion
  auto_accept_threshold: 0.9, // Auto-acceptation haute confiance

  // Apprentissage
  learning_enabled: true,
  adaptation_rate: 0.1, // Vitesse d'adaptation

  // Performance
  rotation_interval: 120, // Secondes entre analyses
  performance_window: 10, // Nombre de mesures pour performance
};
```

### Préférences Utilisateur

```javascript
const userPreferences = {
  BTC: {
    preference_score: 1.0, // 0.0-1.0
    weight_multiplier: 1.5, // Multiplicateur d'influence
    lock_until: null, // Date de fin de verrouillage
    min_allocation: 0.2, // Allocation minimale (%)
    max_allocation: 0.6, // Allocation maximale (%)
    tags: ['core', 'favorite'], // Tags personnalisés
  },
};
```

## 🎯 Cas d'Usage Spécifiques

### 1. Portfolio Diversifié Automatique

- **Mode** : USER_GUIDED
- **Préférences** : Distribution équilibrée
- **Avantages** : Diversification automatique

### 2. Trading de Focus

- **Mode** : USER_OVERRIDE
- **Préférences** : Focus sur 3-4 actifs favoris
- **Avantages** : Contrôle total avec optimisation

### 3. Apprentissage Progressif

- **Mode** : COLLABORATIVE
- **Préférences** : Apprentissage au fil du temps
- **Avantages** : Éducateur et performant

### 4. Gestion de Risque

- **Mode** : SEMI_AUTO
- **Préférences** : Seuils de risque stricts
- **Avantages** : Protection du capital

## 📈 Métriques et Monitoring

### KPIs Principaux

- **Taux de rotation** : Fréquence des changements
- **Performance ajustée** : Rendement par risque
- **Satisfaction utilisateur** : Taux d'acceptation
- **Efficacité d'apprentissage** : Amélioration continue

### Tableaux de Bord

- **Vue d'ensemble** : Statut actuel et tendances
- **Analyse détaillée** : Par actif et par période
- **Comparaison** : IA vs utilisateur
- **Prédictions** : Tendances futures

## 🚀 Intégration avec le Frontend

### Architecture Recommandée

```javascript
// Service de gestion hybride
class HybridRotationService {
  constructor(apiEndpoint) {
    this.api = new HybridRotationAPI(apiEndpoint);
  }

  async initializeHybrid(config) {
    return await this.api.startHybridRotation(config);
  }

  async updatePreference(symbol, preference) {
    return await this.api.updateUserPreference(symbol, preference);
  }

  async handleSuggestion(suggestionId, response) {
    return await this.api.respondToSuggestion(suggestionId, response);
  }
}
```

### Composants React

```jsx
// Contrôleur de mode
<ModeController
  currentMode={mode}
  onModeChange={handleModeChange}
  availableModes={modes}
/>

// Gestionnaire de préférences
<PreferenceManager
  assets={assets}
  preferences={preferences}
  onUpdatePreference={handleUpdatePreference}
/>

// Panneau de suggestions
<SuggestionPanel
  suggestions={suggestions}
  onRespond={handleSuggestionResponse}
/>

// Dashboard de performance
<PerformanceDashboard
  metrics={metrics}
  currentAssets={currentAssets}
  history={history}
/>
```

## 🔮 Évolutions Futures

### Fonctionnalités Planifiées

1. **ML avancé** : Modèles prédictifs plus sophistiqués
2. **Social trading** : Intégration des préférences communautaires
3. **Multi-portfolio** : Gestion de plusieurs stratégies
4. **Backtesting** : Simulation des stratégies
5. **Alertes mobiles** : Notifications push

### Améliorations Techniques

1. **Performance** : Optimisation des calculs
2. **Scalabilité** : Support de plus d'actifs
3. **Sécurité** : Validation renforcée
4. **Monitoring** : Métriques avancées
5. **API v2** : Endpoint GraphQL

---

## 📞 Support et Maintenance

### Documentation Complémentaire

- [API Reference](./API_REFERENCE.md)
- [Guide d'Intégration](./INTEGRATION_GUIDE.md)
- [Exemples de Code](./CODE_EXAMPLES.md)
- [Dépannage](./TROUBLESHOOTING.md)

### Support Technique

- Documentation détaillée inline
- Logs structurés pour debugging
- Monitoring d'état en temps réel
- Tests automatisés complets

---

_Ce système représente l'état de l'art de la collaboration entre intelligence
artificielle et décision humaine dans la gestion de portefeuilles
cryptographiques._
