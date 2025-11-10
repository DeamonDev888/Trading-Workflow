# 🔄 Guide : Récupération des Données et Vérification de Fiabilité

**Comment l'agent principal récupère les données des sous-agents et comment vérifier la fiabilité du système**

---

## 📋 Table des Matières

1. [Vue d'ensemble](#-vue-densemble)
2. [Flux de Récupération des Données](#-flux-de-récupération-des-données)
3. [DataAggregator](#-dataaggregator)
4. [ReliabilityMonitor](#-reliabilitymonitor)
5. [ClaudeCodeOrchestrator](#-claudecodeorchestrator)
6. [Vérification de la Fiabilité](#-vérification-de-la-fiabilité)
7. [Exemples d'Usage](#-exemples-dusage)
8. [Monitoring en Temps Réel](#-monitoring-en-temps-réel)
9. [Dépannage](#-dépannage)

---

## 🎯 Vue d'ensemble

### Architecture de Récupération

```
┌─────────────────────────────────────────────────────────────┐
│                    ClaudeCodeOrchestrator                   │
│  (Orchestrateur principal)                                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│           ClaudeCodeIntegrationManager                      │
│  (Lance les sub-agents Claude Code)                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
┌──────────────┐        ┌──────────────┐
│  Data        │        │  Reliability │
│  Aggregator  │        │  Monitor     │
└──────────────┘        └──────────────┘
     │                       │
     ▼                       ▼
┌──────────────┐        ┌──────────────┐
│  Validation  │        │  Monitoring  │
│  Consensus   │        │  Alertes     │
└──────────────┘        └──────────────┘
```

### Composants Principaux

1. **DataAggregator** - Agrège et valide les données des agents
2. **ReliabilityMonitor** - Surveille la fiabilité et génère des alertes
3. **ClaudeCodeOrchestrator** - Orchestrateur principal qui coordonne tout

---

## 🔄 Flux de Récupération des Données

### Étapes de Récupération

#### 1. **Lancement des Agents**

```python
# L'orchestrateur lance les sub-agents
agent_results = await orchestrator._execute_agents(
    task="Should I buy BTC?",
    context_data=market_data,
    mode="complete"
)
```

#### 2. **Collecte des Résultats**

```python
# Chaque agent retourne ses données
{
    "claude-strategy-advisor": {
        "success": True,
        "confidence": 0.85,
        "converged": True,
        "iterations": 3,
        "execution_time": 45.2,
        "result": {"decision": "BUY", "reasoning": "..."},
        "timestamp": "2025-11-09T10:00:00Z"
    },
    "claude-risk-advisor": {
        "success": True,
        "confidence": 0.78,
        "converged": True,
        "iterations": 2,
        ...
    }
}
```

#### 3. **Agrégation**

```python
# Le DataAggregator agrège les données
aggregation_result = data_aggregator.aggregate_agent_data(
    agent_results,
    context_data
)
```

#### 4. **Validation**

```python
# Chaque agent est validé
for agent_data in agents_data:
    agent_data = _validate_agent_data(agent_data)
    # Vérifie: succès, confiance, convergence, vitesse, itérations
```

#### 5. **Calcul du Consensus**

```python
# Calcul du consensus entre agents
consensus = _calculate_consensus(agents_data)
# Vote pondéré par confiance et fiabilité
```

#### 6. **Décision Finale**

```python
# L'orchestrateur prend la décision finale
orchestrator_result = _make_final_decision(aggregation_result)
```

---

## 📊 DataAggregator

### Rôle

Le `DataAggregator` est responsable de :

- ✅ Convertir les résultats bruts en données structurées
- ✅ Valider chaque agent individuellement
- ✅ Calculer les scores de fiabilité
- ✅ Déterminer le consensus
- ✅ Identifier les anomalies

### Structure des Données

#### AgentData

```python
@dataclass
class AgentData:
    agent_name: str              # Nom de l'agent
    timestamp: str               # Horodatage
    raw_response: str            # Réponse brute
    parsed_data: Dict            # Données parsées
    confidence: float            # Confiance (0.0-1.0)
    convergence: bool            # Convergence atteinte
    iterations: int              # Nombre d'itérations
    execution_time: float        # Temps d'exécution (s)
    success: bool                # Succès de l'exécution
    error: Optional[str]         # Erreur éventuel
    validation_status: str       # VALID/WARNING/INVALID
    reliability_score: float     # Score de fiabilité (0.0-1.0)
    quality_metrics: Dict        # Métriques de qualité
```

#### AggregationResult

```python
@dataclass
class AggregationResult:
    aggregation_id: str              # ID unique
    timestamp: str                   # Horodatage
    agents_data: List[AgentData]     # Données des agents
    consensus: Dict                  # Consensus calculé
    final_decision: str              # Décision finale
    confidence_score: float          # Score de confiance global
    reliability_score: float         # Score de fiabilité global
    validation_results: Dict         # Résultats de validation
    warnings: List[str]              # Avertissements
    errors: List[str]                # Erreurs
    metadata: Dict                   # Métadonnées
```

### Méthodes de Validation

#### 1. **Validation Individuelle**

```python
def _validate_agent_data(self, agent_data: AgentData) -> AgentData:
    validations = []

    # 1. Vérifier le succès
    if not agent_data.success:
        agent_data.validation_status = "INVALID"
        return agent_data

    # 2. Vérifier la confiance
    if agent_data.confidence < 0.3:
        agent_data.validation_status = "WARNING"
    elif agent_data.confidence < 0.6:
        agent_data.validation_status = "WARNING"
    else:
        agent_data.validation_status = "VALID"

    # 3. Vérifier la convergence
    if not agent_data.convergence and agent_data.confidence < 0.7:
        agent_data.validation_status = "WARNING"

    # 4. Calculer le score de fiabilité
    agent_data.reliability_score = self._calculate_agent_reliability(agent_data)

    return agent_data
```

#### 2. **Calcul de Fiabilité**

```python
def _calculate_agent_reliability(self, agent_data: AgentData) -> float:
    if not agent_data.success:
        return 0.0

    score = 0.0

    # Confiance (40%)
    score += agent_data.confidence * 0.4

    # Convergence (30%)
    if agent_data.convergence:
        score += 0.3
    else:
        score += agent_data.confidence * 0.3

    # Vitesse d'exécution (15%)
    speed_score = max(0.0, 1.0 - (agent_data.execution_time / 120))
    score += speed_score * 0.15

    # Stabilité (15%)
    stability_score = max(0.0, 1.0 - abs(agent_data.iterations - 3) / 3)
    score += stability_score * 0.15

    return min(1.0, score)
```

#### 3. **Calcul du Consensus**

```python
def _calculate_consensus(self, agents_data: List[AgentData]) -> Dict:
    decisions = {}
    confidences = []

    for agent_data in agents_data:
        if not agent_data.success:
            continue

        decision = self._extract_decision(agent_data)
        if decision:
            weight = agent_data.confidence * agent_data.reliability_score
            decisions[decision] = decisions.get(decision, 0) + weight
            confidences.append(agent_data.confidence)

    # Décision majoritaire pondérée
    best_decision = max(decisions.items(), key=lambda x: x[1])
    final_confidence = best_decision[1] / sum(decisions.values())

    return {
        "decision": best_decision[0],
        "confidence": final_confidence,
        "agreements": agreements,
        "total_weighted_votes": sum(decisions.values())
    }
```

### Exemple d'Utilisation

```python
from src.agents.data_aggregator import DataAggregator

# Initialiser
aggregator = DataAggregator()

# Agréger les données
agent_results = {
    "claude-strategy-advisor": {
        "success": True,
        "confidence": 0.85,
        "converged": True,
        "result": {"decision": "BUY"},
        ...
    }
}

result = aggregator.aggregate_agent_data(
    agent_results,
    context_data={"symbol": "BTC-USD", "price": 50000}
)

print(f"Decision: {result.final_decision}")
print(f"Confidence: {result.confidence_score:.2f}")
print(f"Reliability: {result.reliability_score:.2f}")
```

---

## 🔍 ReliabilityMonitor

### Rôle

Le `ReliabilityMonitor` surveille en continu :

- ✅ Santé du système global
- ✅ Performance des agents
- ✅ Métriques de fiabilité
- ✅ Génération d'alertes
- ✅ Auto-récupération

### Vérifications de Santé

#### 1. **Vérification Système**

```python
def _check_system_metrics(self, aggregator_data):
    # Vérifier le taux de succès
    total = aggregator_data.get("total_aggregations", 0)
    successful = aggregator_data.get("successful_aggregations", 0)

    if total > 0:
        success_rate = successful / total
        if success_rate < self.thresholds["min_success_rate"]:
            return {"status": "FAIL", "score": 0.3}
```

#### 2. **Vérification Agents**

```python
def _check_agents_health(self, agent_status):
    healthy_agents = sum(1 for s in agent_status.values()
                        if s.get("health") in ["HEALTHY", "DEGRADED"])

    if healthy_agents < self.thresholds["min_agents_online"]:
        return {"status": "FAIL", "score": 0.2}
```

#### 3. **Vérification Performance**

```python
def _check_performance(self, aggregator_data):
    avg_time = average_execution_time
    if avg_time > self.thresholds["max_execution_time"]:
        return {"status": "WARNING", "score": 0.6}
```

### Système d'Alertes

#### Niveaux d'Alerte

1. **INFO** - Information générale
2. **WARNING** - Avertissement, attention requise
3. **CRITICAL** - Problème critique
4. **EMERGENCY** - Urgence, intervention immédiate

#### Génération d'Alerte

```python
monitor.create_alert(
    level=AlertLevel.WARNING,
    message="Agent performance degraded",
    source="reliability_monitor",
    details={"agent": "claude-risk-advisor", "success_rate": 0.65}
)
```

#### Résolution d'Alerte

```python
monitor.resolve_alert(alert)
```

### Seuils de Monitoring

```python
self.thresholds = {
    "min_success_rate": 0.7,        # Taux de succès minimum
    "min_confidence": 0.6,          # Confiance minimum moyenne
    "max_execution_time": 120,      # Temps d'exécution maximum
    "max_consecutive_failures": 3,  # Échecs consécutifs maximum
    "min_agents_online": 2,         # Agents minimum en ligne
    "health_check_interval": 60,    # Intervalle de vérification
}
```

### Exemple d'Utilisation

```python
from src.agents.reliability_monitor import ReliabilityMonitor, AlertLevel

# Initialiser
monitor = ReliabilityMonitor()

# Ajouter un callback d'alerte
def handle_alert(alert):
    print(f"[ALERT] {alert.level.value}: {alert.message}")

monitor.add_alert_callback(handle_alert)

# Vérifier la santé
health_report = monitor.check_system_health(
    aggregator_data,
    agent_status
)

print(f"Status: {health_report['overall_status']}")
print(f"Health Score: {health_report['health_score']:.2f}")

# Vérifier si le système est fiable
is_healthy = monitor.is_system_reliable()
if is_healthy:
    print("System is healthy")
else:
    print("System has issues - check alerts")
```

---

## 🎼 ClaudeCodeOrchestrator

### Rôle

Le `ClaudeCodeOrchestrator` est l'orchestrateur principal qui :

- ✅ Lance les sub-agents
- ✅ Orchestration l'exécution
- ✅ Agrège les données
- ✅ Valide la fiabilité
- ✅ Prend les décisions finales
- ✅ Surveille en continu

### Modes d'Exécution

#### 1. **Mode Complet** (`complete`)

- Exécute tous les agents
- Analyse complète
- Confiance maximale
- Temps: 3-5 minutes

```python
result = await orchestrator.execute_trading_analysis(
    task="Should I buy BTC?",
    mode="complete"
)
```

#### 2. **Mode Rapide** (`quick`)

- Agents essentiels uniquement
- Décision rapide
- Confiance réduite
- Temps: 1-2 minutes

```python
result = await orchestrator.execute_trading_analysis(
    task="Quick decision",
    mode="quick"
)
```

#### 3. **Mode Personnalisé** (`custom`)

- Selon la configuration
- Contrôle fin
- Flexibilité maximale

### Configuration

```python
@dataclass
class OrchestratorConfig:
    required_agents: List[str] = [
        "claude-strategy-advisor",
        "claude-risk-advisor",
        "claude-funding-advisor",
        "claude-sentiment-analyzer"
    ]

    min_confidence: float = 0.6
    min_reliability: float = 0.7
    min_agents_agreement: float = 0.5

    max_execution_time: float = 300.0

    enable_monitoring: bool = True
    health_check_interval: float = 60.0

    auto_recovery: bool = True
    max_retry_attempts: int = 3

    strict_validation: bool = False
```

### Méthode Principale

```python
async def execute_trading_analysis(
    self,
    task: str,
    context_data: Optional[Dict[str, Any]] = None,
    mode: str = "complete"
) -> OrchestratorResult:
```

**Processus :**

1. Lancer les agents selon le mode
2. Agréger les données
3. Valider avec le moniteur
4. Déterminer la décision finale
5. Exécuter les callbacks
6. Mettre à jour les stats
7. Auto-récupération si nécessaire

### Callbacks

#### Callback de Succès

```python
def on_success(result: OrchestratorResult):
    print(f"Success: {result.decision} "
          f"(confidence: {result.confidence:.2f})")

orchestrator.add_success_callback(on_success)
```

#### Callback d'Échec

```python
def on_failure(error: Exception):
    print(f"Failed: {error}")

orchestrator.add_failure_callback(on_failure)
```

#### Callback de Décision

```python
def on_decision(result: OrchestratorResult):
    # Logique personnalisée de décision
    if result.confidence > 0.8:
        execute_trade(result.decision)

orchestrator.add_decision_callback(on_decision)
```

### Exemple d'Utilisation

```python
from src.agents.claude_code_orchestrator import (
    ClaudeCodeOrchestrator,
    OrchestratorConfig
)

# Configuration
config = OrchestratorConfig(
    min_confidence=0.6,
    min_reliability=0.7,
    enable_monitoring=True,
    auto_recovery=True
)

# Initialiser
orchestrator = ClaudeCodeOrchestrator(config)

# Exécuter l'analyse
result = await orchestrator.execute_trading_analysis(
    task="Should I buy BTC at $50,000?",
    context_data={
        "symbol": "BTC-USD",
        "price": 50000,
        "portfolio": {...}
    },
    mode="complete"
)

# Vérifier le résultat
if result.success:
    print(f"Decision: {result.decision}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Reliability: {result.reliability:.2f}")

    if result.warnings:
        for warning in result.warnings:
            print(f"Warning: {warning}")
else:
    print(f"Error: {result.error}")
```

---

## ✅ Vérification de la Fiabilité

### Critères de Fiabilité

#### 1. **Taux de Succès Global**

```python
success_rate = successful_aggregations / total_aggregations
if success_rate < 0.7:
    return False  # Système peu fiable
```

#### 2. **Confiance Moyenne**

```python
avg_confidence = sum(c.confidence for c in aggregations) / len(aggregations)
if avg_confidence < 0.6:
    return False  # Confiance trop basse
```

#### 3. **Fiabilité Moyenne**

```python
avg_reliability = sum(r.reliability_score for r in aggregations) / len(aggregations)
if avg_reliability < 0.7:
    return False  # Fiabilité insuffisante
```

#### 4. **Agents en Ligne**

```python
online_agents = sum(1 for a in agents if a.health in ["HEALTHY", "DEGRADED"])
if online_agents < 2:
    return False  # Pas assez d'agents
```

#### 5. **Échecs Consécutifs**

```python
if consecutive_failures >= 3:
    return False  # Trop d'échecs
```

### Méthode de Vérification

```python
def is_system_reliable(self, threshold: float = 0.7) -> bool:
    # 1. Taux de succès > threshold
    if success_rate < threshold:
        return False

    # 2. Confiance moyenne > threshold
    if avg_confidence < threshold:
        return False

    # 3. Fiabilité moyenne > threshold
    if avg_reliability < threshold:
        return False

    # 4. Taux d'échec de validation < 0.3
    if validation_failure_rate > 0.3:
        return False

    # 5. Tous les agents taux de succès > 0.5
    for stats in agent_success_rates.values():
        if stats.successful / stats.total < 0.5:
            return False

    return True  # Système fiable
```

### Rapport de Fiabilité

```python
def get_reliability_report(self) -> Dict[str, Any]:
    return {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_aggregations": self.reliability_metrics["total_aggregations"],
            "successful_aggregations": self.reliability_metrics["successful_aggregations"],
            "average_confidence": self.reliability_metrics["average_confidence"],
            "average_reliability": self.reliability_metrics["average_reliability"],
            "validation_failure_rate": self.reliability_metrics["validation_failure_rate"]
        },
        "agent_reliability": {
            agent_name: {
                "total_calls": stats["total"],
                "successful_calls": stats["successful"],
                "success_rate": stats["successful"] / stats["total"]
            }
            for agent_name, stats in self.reliability_metrics["agent_success_rates"].items()
        },
        "recent_aggregations": [
            {
                "id": a.aggregation_id,
                "decision": a.final_decision,
                "confidence_score": a.confidence_score,
                "reliability_score": a.reliability_score,
                "has_errors": len(a.errors) > 0
            }
            for a in self.aggregation_history[-10:]
        ]
    }
```

### Exemple de Vérification

```python
from src.agents.data_aggregator import DataAggregator

aggregator = DataAggregator()

# Après plusieurs exécutions
is_reliable = aggregator.is_system_reliable()

if is_reliable:
    print("✅ System is reliable")
    print(f"  Success rate: {report['summary']['successful_aggregations']}/{report['summary']['total_aggregations']}")
    print(f"  Avg confidence: {report['summary']['average_confidence']:.2f}")
    print(f"  Avg reliability: {report['summary']['average_reliability']:.2f}")
else:
    print("❌ System reliability issues detected")
    print("  Review the reliability report")
    print("  Check active alerts")
```

---

## 💡 Exemples d'Usage

### Exemple 1: Analyse Simple

```python
import asyncio
from src.agents.claude_code_orchestrator import ClaudeCodeOrchestrator

async def simple_analysis():
    orchestrator = ClaudeCodeOrchestrator()

    result = await orchestrator.execute_trading_analysis(
        task="Analyze BTC trading opportunity",
        context_data={"symbol": "BTC-USD", "price": 50000}
    )

    return result

# Exécuter
result = asyncio.run(simple_analysis())
```

### Exemple 2: Analyse avec Configuration

```python
from src.agents.claude_code_orchestrator import OrchestratorConfig

config = OrchestratorConfig(
    min_confidence=0.7,        # Confiance plus stricte
    min_reliability=0.8,       # Fiabilité plus stricte
    strict_validation=True,    # Validation stricte
    auto_recovery=True         # Auto-récupération activée
)

orchestrator = ClaudeCodeOrchestrator(config)

# Avec callbacks
def on_success(result):
    if result.confidence > 0.8:
        print(f"High confidence: {result.decision}")

orchestrator.add_success_callback(on_success)

result = await orchestrator.execute_trading_analysis(
    task="Should I buy?",
    mode="complete"
)
```

### Exemple 3: Monitoring Continu

```python
from src.agents.reliability_monitor import ReliabilityMonitor, AlertLevel

monitor = ReliabilityMonitor()

# Callback d'alerte
def handle_alert(alert):
    if alert.level == AlertLevel.CRITICAL:
        # Envoyer notification
        send_notification(f"CRITICAL: {alert.message}")
    elif alert.level == AlertLevel.EMERGENCY:
        # Urgence - arrêter le trading
        stop_trading()
        send_emergency_alert(alert)

monitor.add_alert_callback(handle_alert)

# Vérification périodique
while True:
    health_report = monitor.check_system_health(aggregator_data, agent_status)

    if health_report['overall_status'] == 'CRITICAL':
        print("CRITICAL: System health critical!")

    time.sleep(60)  # Vérifier toutes les minutes
```

### Exemple 4: Agrégation Manuelle

```python
from src.agents.data_aggregator import DataAggregator

aggregator = DataAggregator()

# Données simulées
agent_results = {
    "agent1": {
        "success": True,
        "confidence": 0.85,
        "converged": True,
        "result": {"decision": "BUY"},
        "execution_time": 45.0,
        "timestamp": datetime.now().isoformat()
    },
    "agent2": {
        "success": True,
        "confidence": 0.80,
        "converged": True,
        "result": {"decision": "BUY"},
        "execution_time": 40.0,
        "timestamp": datetime.now().isoformat()
    }
}

# Agréger
result = aggregator.aggregate_agent_data(agent_results)

# Vérifier
print(f"Decision: {result.final_decision}")
print(f"Confidence: {result.confidence_score:.2f}")
print(f"Reliability: {result.reliability_score:.2f}")

# Obtenir le rapport
report = aggregator.get_reliability_report()
print(f"Success rate: {report['summary']['successful_aggregations']}/{report['summary']['total_aggregations']}")
```

---

## 📊 Monitoring en Temps Réel

### Dashboard de Surveillance

```python
def get_monitoring_dashboard():
    """Retourne un dashboard de monitoring complet"""
    return {
        "system_health": {
            "overall_status": "HEALTHY/DEGRADED/UNHEALTHY/CRITICAL",
            "health_score": 0.85,
            "uptime_seconds": get_uptime()
        },
        "agents_status": {
            agent_name: {
                "health": "HEALTHY/DEGRADED/UNHEALTHY",
                "success_rate": 0.9,
                "last_execution": "2025-11-09T10:00:00Z"
            }
            for agent_name in AGENT_NAMES
        },
        "reliability": {
            "total_aggregations": 100,
            "successful_aggregations": 85,
            "average_confidence": 0.75,
            "average_reliability": 0.78
        },
        "alerts": {
            "active": len(monitor.get_active_alerts()),
            "critical": len([a for a in monitor.get_active_alerts()
                           if a.level == AlertLevel.CRITICAL]),
            "last_24h": alert_summary['last_24h']
        },
        "performance": {
            "average_execution_time": 45.0,
            "max_execution_time": 120.0,
            "min_execution_time": 30.0
        }
    }
```

### Métriques Temps Réel

```python
def get_real_time_metrics():
    """Métriques en temps réel"""
    return {
        "timestamp": datetime.now().isoformat(),
        "system": {
            "is_running": orchestrator.is_running,
            "last_execution": orchestrator.last_execution,
            "execution_count": orchestrator.execution_count,
            "failure_count": orchestrator.failure_count
        },
        "aggregator": {
            "total_aggregations": len(aggregator.aggregation_history),
            "recent_decisions": [
                a.final_decision
                for a in aggregator.aggregation_history[-10:]
            ],
            "confidence_trend": calculate_trend(
                [a.confidence_score for a in aggregator.aggregation_history[-20:]]
            )
        },
        "monitor": {
            "active_alerts": len(monitor.get_active_alerts()),
            "system_healthy": monitor.is_system_healthy(),
            "alert_summary": monitor.get_alert_summary()
        }
    }
```

---

## 🐛 Dépannage

### Problèmes Courants

#### 1. **Agents qui échouent**

**Symptôme :**

```
ERROR: Only 1 agent succeeded (minimum: 2)
```

**Diagnostic :**

```python
# Vérifier le statut des agents
agent_status = aggregator.get_agent_status()
for name, status in agent_status.items():
    print(f"{name}: {status['health']} (success_rate: {status['success_rate']:.2%})")
```

**Solutions :**

- Redémarrer les agents en échec
- Vérifier la connectivité
- Réduire le nombre d'itérations
- Utiliser le mode "quick" temporairement

#### 2. **Confiance trop basse**

**Symptôme :**

```
Confidence too low: 0.45 (minimum: 0.6)
```

**Diagnostic :**

```python
# Analyser la dispersion
recent_confidences = [a.confidence_score for a in aggregator.aggregation_history[-10:]]
print(f"Recent confidences: {recent_confidences}")
print(f"Average: {sum(recent_confidences)/len(recent_confidences):.2f}")
```

**Solutions :**

- Améliorer le contexte (plus de données)
- Utiliser CROSS_VALIDATION au lieu de PROGRESSIVE_REFINEMENT
- Augmenter le nombre d'itérations
- Vérifier la qualité des données d'entrée

#### 3. **Fiabilité compromise**

**Symptôme :**

```
System reliability score: 0.45 (minimum: 0.7)
```

**Diagnostic :**

```python
# Obtenir le rapport détaillé
report = aggregator.get_reliability_report()
print(json.dumps(report, indent=2))
```

**Solutions :**

- Identifier les agents avec un taux de succès faible
- Vérifier les alertes actives
- Analyser les erreurs récurrentes
- Ajuster les seuils de monitoring

#### 4. **Alertes critiques**

**Symptôme :**

```
[ALERT CRITICAL] Multiple agents showing issues
```

**Diagnostic :**

```python
# Lister les alertes actives
active_alerts = monitor.get_active_alerts()
for alert in active_alerts:
    print(f"{alert.level.value}: {alert.message}")
    print(f"  Details: {alert.details}")
```

**Solutions :**

- Résoudre les alertes une par une
- Vérifier les logs détaillés
- Redémarrer le système si nécessaire
- Contacter le support si persistant

### Commandes de Debug

```bash
# Vérifier l'état du système
python -c "from src.agents.claude_code_orchestrator import ClaudeCodeOrchestrator; import asyncio; orchestrator = ClaudeCodeOrchestrator(); print(orchestrator.is_system_healthy())"

# Obtenir le rapport de fiabilité
python -c "from src.agents.data_aggregator import DataAggregator; agg = DataAggregator(); print(agg.get_reliability_report())"

# Voir les alertes actives
python -c "from src.agents.reliability_monitor import ReliabilityMonitor; monitor = ReliabilityMonitor(); print(monitor.get_alert_summary())"
```

### Logs de Debug

```python
import logging

# Activer le logging détaillé
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

# Logger personnalisés
logger = logging.getLogger('orchestrator')
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

---

## 📈 Optimisation des Performances

### Métriques de Performance

| Métrique          | Cible | Acceptable | Critique |
| ----------------- | ----- | ---------- | -------- |
| Temps d'exécution | < 60s | < 120s     | > 120s   |
| Confiance moyenne | > 0.8 | > 0.6      | < 0.6    |
| Fiabilité moyenne | > 0.8 | > 0.7      | < 0.7    |
| Taux de succès    | > 80% | > 70%      | < 70%    |
| Agents en ligne   | 4/4   | 3/4        | < 3/4    |

### Optimisation

#### 1. **Réduire le Temps d'Exécution**

```python
config = OrchestratorConfig(
    # Utiliser le mode quick pour les décisions urgentes
    required_agents=["claude-strategy-advisor", "claude-risk-advisor"],

    # Réduire le timeout
    max_execution_time=120.0  # 2 minutes au lieu de 5
)
```

#### 2. **Améliorer la Confiance**

```python
# Améliorer le contexte
context_data = {
    "symbol": "BTC-USD",
    "price": 50000,
    # Ajouter plus de données
    "historical_data": {...},
    "technical_indicators": {...},
    "news_sentiment": {...}
}

# Utiliser CROSS_VALIDATION
result = manager.call_claude_code_agent(
    agent_id="claude-strategy-advisor",
    iteration_mode=IterationMode.CROSS_VALIDATION
)
```

#### 3. **Augmenter la Fiabilité**

```python
# Mode strict pour plus de robustesse
config.strict_validation = True

# Auto-récupération activée
config.auto_recovery = True

# Monitoring activé
config.enable_monitoring = True
```

---

## 🎯 Résumé

### Flux Complet

1. **Lancement** → Orchestrateur lance les agents
2. **Exécution** → Agents analysent et retournent leurs résultats
3. **Agrégation** → DataAggregator collecte et valide
4. **Consensus** → Calcul du consensus multi-agents
5. **Décision** → Orchestrateur prend la décision finale
6. **Monitoring** → ReliabilityMonitor surveille
7. **Alertes** → Génération d'alertes si nécessaire
8. **Auto-récupération** → Récupération automatique en cas de problème

### Points Clés

- ✅ **DataAggregator** → Agrégation et validation
- ✅ **ReliabilityMonitor** → Surveillance et alertes
- ✅ **ClaudeCodeOrchestrator** → Orchestration complète
- ✅ **Consensus** → Vote pondéré multi-agents
- ✅ **Fiabilité** → Vérification continue
- ✅ **Auto-récupération** → Récupération automatique

### Bonnes Pratiques

1. **Toujours valider** les résultats avant de les utiliser
2. **Surveiller les alertes** en temps réel
3. **Vérifier la fiabilité** périodiquement
4. **Optimiser le contexte** pour de meilleurs résultats
5. **Utiliser les callbacks** pour les actions automatisées
6. **Conserver un historique** pour l'analyse

---

**🎉 Le système de récupération des données et de vérification de fiabilité est maintenant opérationnel !**

_Guide créé le 2025-11-09_
