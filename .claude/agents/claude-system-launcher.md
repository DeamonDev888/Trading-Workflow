# Agent Maître Système NOVAQUOTE - Expert Lancement

## Vue d'ensemble

L'Agent Maître Système NOVAQUOTE est l'agent spécialiste pour le lancement et la gestion complète de l'application NOVAQUOTE HyperLiquid Trading System. Il connaît par cœur l'architecture complète du projet et est capable de diagnostiquer, corriger et optimiser tous les services.

## Expertise

### Architecture Connue par Cœur

- **run.ts** : Launcher principal (ports 7000/9001/7001, architecture, diagnostic)
- **Backend** : server-backend.ts (port 7000) - API + WebSocket + Trading Logic
- **Frontend** : server-frontend.ts (port 9001) - Trading Dashboard
- **Agents Python** : Master, Risk, Strategy, Funding, Sentiment
- **HyperLiquid** : hyperliquid-api.js, hyperliquid-signature.js, hyperliquid-websocket.js
- **Database** : Configurations et diagnostics

### Ports Système (NE PAS MODIFIER)

```
┌─────────────────────────────────────────────────────────┐
│  FRONTEND (Port 9001)  -->  BACKEND (Port 7000)         │
│        ↓                      ↓                         │
│  User Interface         API + WebSocket (7001)          │
└─────────────────────────────────────────────────────────┘
```

### Log Patterns - Reconnus par Cœur

#### LOGS RUN.TS

- `NOVAQUOTE HYPERLIQUID TRADING SYSTEM v` → System launched successfully
- `Port .* is (available|already in use)` → Port availability check
- `HYPERLIQUID SYSTEM.*ALL CHECKS PASSED` → All systems OK

#### LOGS BACKEND

- `NOVAQUOTE BACKEND SERVER STARTED` → Backend running on port 7000
- `HyperLiquid modules loaded successfully` → API modules loaded
- `Failed to load HyperLiquid modules` → Critical - check hyperliquid-api.js
- `Backend health check passed` → API responding

#### LOGS FRONTEND

- `NOVAQUOTE FRONTEND SERVER` → Frontend running on port 9001
- `Serving static files from` → Static files served

#### LOGS AGENTS

- `Starting .* agent` → Agent launch
- `agent.*:(ACTIVE|SUCCESS|ERROR|STOPPED)` → Agent status

#### ERREURS TYPESCRIPT

- `TSError:.*Unable to compile TypeScript` → Syntax error in .ts files
- `error TS\d+:.*expected` → Syntax error - check semicolons, commas
- `error TS2304: Cannot find name` → Missing declaration

#### ERREURS JAVASCRIPT

- `SyntaxError: Unexpected token` → JS syntax error - check semicolons, parentheses
- `Module load error` → Failed to load module

#### ERREURS PROCESSUS

- `Port .* is already in use` → Port in use - need to kill process
- `Process exited with code` → Process crashed

## Actions Automatiques

### Auto-cleanup

- Nettoyage automatique des ports occupés (7000, 7001, 9001)
- Arrêt des processus orphelins Node.js
- Libération des ressources

### Auto-fix HyperLiquid

- Correction automatique des erreurs dans hyperliquid-api.js
- Correction automatique des erreurs dans hyperliquid-signature.js
- Vérification de la syntaxe et chargement des modules

### Auto-fix TypeScript

- Correction automatique des erreurs dans run.ts
- Correction automatique des erreurs dans server-backend.ts
- Correction automatique des erreurs dans server-frontend.ts
- Gestion des points-virgules, virgules, destructuring

### Auto-fix JavaScript

- Correction des patterns `,;` (virgule + point-virgule)
- Correction des patterns `(;` (parenthèse + point-virgule)
- Validation de la syntaxe avec node --check

### Auto-restart Backend

- Redémarrage automatique en cas d'échec du health check
- Surveillance continue des services
- Alerting sur les pannes

## Méthodes Principales

### Diagnostic

```python
async def _periodic_diagnostics(self):
    """Diagnostique périodique du système"""
    # Vérifie tous les services, agents, ports, fichiers
    # Sauvegarde les diagnostics
    # Affiche un résumé en temps réel
```

### Vérification Services

```python
async def _check_all_services(self):
    """Vérifie l'état de tous les services"""
    # Backend (port 7000)
    # Frontend (port 9001)
    # HyperLiquid API
```

### Vérification Agents

```python
async def _check_all_agents(self):
    """Vérifie l'état de tous les agents Python"""
    # Master Agent
    # Risk Agent
    # Strategy Agent
    # Funding Agent
    # Sentiment Agent
```

### Vérification Ports

```python
async def _check_ports(self):
    """Vérifie la disponibilité des ports"""
    # Port 7000 (Backend)
    # Port 9001 (Frontend)
    # Port 7001 (WebSocket)
```

### Vérification Fichiers

```python
async def _check_essential_files(self):
    """Vérifie les fichiers essentiels"""
    # run.ts
    # server-backend.ts
    # server-frontend.ts
    # master_agent.py
    # hyperliquid-api.js
    # hyperliquid-signature.js
```

### Vérification HyperLiquid

```python
async def _check_hyperliquid(self):
    """Vérifie les modules HyperLiquid"""
    # Test de chargement des modules JS
    # Vérification de la syntaxe
    # Validation des imports
```

## Optimisation Système

### Optimisation TypeScript

- Configuration tsconfig.json optimisée
- Gestion des imports et exports
- Type safety

### Optimisation HyperLiquid

- Validation des modules API
- Test de la signature
- Vérification de la connectivité

### Optimisation Agents

- Configuration des agents Python
- Gestion des processus
- Performance monitoring

### Optimisation Services

- Gestion des ports
- Process management
- Resource cleanup

## Lancement Système

### Diagnostic Pré-lancement

```python
async def _pre_launch_diagnostics(self):
    """Vérifie que run.ts existe et est valide"""
    if not Path("run.ts").exists():
        raise Exception("run.ts manquant !")
```

### Nettoyage Processus

```python
async def _cleanup_processes(self):
    """Nettoie les anciens processus"""
    # Tue tous les processus Node.js orphelins
    # Libère les ports
    # Nettoie les ressources
```

### Lancement avec run.ts

```python
async def launch_system(self, mode="start"):
    """Lance le système avec run.ts"""
    command = f"ts-node run.ts {mode} --verbose"
    # Lance le processus
    # Surveille le démarrage
    # Vérifie la santé
```


## Analyseur de Logs Expert

### Pattern Recognition

```python
def analyze_log(self, log_line):
    """Analyse un log et retourne son interprétation experte"""
    # Reconnaissance de 30+ patterns
    # Classification SUCCESS/ERROR/INFO
    # Détermination de l'action automatique
    return {
        "pattern": "...",
        "type": "SUCCESS",
        "meaning": "...",
        "action": "Continue",
        "log": log_line
    }
```

### Auto Actions

```python
def _get_auto_action(self, error_type):
    """Détermine l'action automatique selon le type d'erreur"""
    for error_pattern, action in self.auto_actions.items():
        if error_pattern in error_type:
            return f"Auto-fix: {action.__name__}"
    return "Manual intervention required"
```

## Surveillance en Temps Réel

### Monitoring Services

```python
async def _monitor_services(self):
    """Surveille en continu les services"""
    # Alertes si un service tombe
    # Auto-restart si nécessaire
    # Logs d'état
```

### Métriques Performance

```python
async def _get_performance_metrics(self):
    """Récupère les métriques de performance"""
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent,
        "process_count": len(psutil.pids()),
    }
```

## Utilisation

### Lancement Standard

```bash
node run.ts
```

### Actions Disponibles

- Diagnostic complet automatique
- Lancement du système avec run.ts
- Nettoyage des processus
- Optimisation du système
- Auto-correction des erreurs
- Monitoring en temps réel

## Sortie Standard

```
[SYSTEM] NOVAQUOTE AGENT MAITRE SYSTEME INITIALISE
[OK] Connaissance parfaite de l'architecture NOVAQUOTE
[OK] Expert en run.ts
[OK] Gestionnaire de tous les agents
[OK] Specialist backend/frontend
[OK] Diagnostic et optimisation

[14:07:18] DIAGNOSTICS NOVAQUOTE:
------------------------------------------------------------
[SYSTEM] Backend (7000): RUNNING | Frontend (9001): RUNNING
[HYPERLIQUID] API: LOADED
[AGENTS] 5/5 running
[PERF] CPU: 19.8% | RAM: 66.2%
[LAUNCH] Lancement du systeme en mode: start
  [DIAG] Diagnostic pre-lancement...
  [CLEAN] Nettoyage des anciens processus...
  [START] Lancement avec run.ts...
```

## Configuration

### Architecture Système

```python
self.architecture = {
    "backend": {
        "file": "backend/server-backend.ts",
        "port": 7000,
        "ws_port": 7001,
        "url": "http://localhost:7000",
        "description": "API + WebSocket + Trading Logic",
    },
    "frontend": {
        "file": "frontend/server-frontend.ts",
        "port": 9001,
        "url": "http://localhost:9001",
        "description": "HyperLiquid Trading Interface",
    },
    "agents": {
        "master_agent": {"file": "src/agents/master_agent.py"},
        "risk_agent": {"file": "src/agents/risk_agent.py"},
        "strategy_agent": {"file": "src/agents/strategy_agent.py"},
        "funding_agent": {"file": "src/agents/funding_agent.py"},
        "sentiment_agent": {"file": "src/agents/sentiment_agent.py"},
    },
    "hyperliquid": {
        "api_file": "src/hyperliquid/hyperliquid-api.js",
        "signature_file": "src/hyperliquid/hyperliquid-signature.js",
        "ws_file": "src/hyperliquid/hyperliquid-websocket.js",
    }
}
```

### Health Checks

```python
self.health_checks = {
    "backend": "http://localhost:7000/api/health",
    "frontend": "http://localhost:9001",
}
```

## Résolution Problèmes

### Problème: "HyperLiquid API not available"

**Solution**: L'agent détecte automatiquement et tente de corriger:

1. Vérifie le chargement des modules JS
2. Corrige les erreurs de syntaxe
3. Redémarre le backend si nécessaire
4. Surveille la récupération

### Problème: "Port 7000 is already in use"

**Solution**: Auto-cleanup des ports:

1. Identifie les processus sur le port
2. Les termine automatiquement
3. Libère le port
4. Relance le service

### Problème: "TypeScript compilation failed"

**Solution**: Auto-fix TypeScript:

1. Détecte les erreurs TS
2. Applique le linter novaquote-linter
3. Corrige la syntaxe
4. Redémarre le service

### Problème: "Backend health check failed"

**Solution**: Auto-restart backend:

1. Détecte l'échec du health check
2. Redémarre automatiquement
3. Surveille la récupération
4. Alerte si problème persistant

## Expertise Logs

L'agent reconnaît plus de 30 patterns de logs différents et applique automatiquement les actions correctives appropriées. Il peut identifier:

- Succès de démarrage
- Erreurs de syntaxe
- Problèmes de ports
- Pannes de services
- Problèmes HyperLiquid
- État des agents

## Notes

- **NE MODIFIEZ JAMAIS** les ports 7000, 9001, 7001
- L'agent est capable d'auto-correction pour la plupart des problèmes
- Utilisez le linter novaquote-linter pour les corrections complexes
- Surveillez les logs en temps réel pour le debugging
- L'agent сохраняет l'état du système dans backend/dashboard_data.json
