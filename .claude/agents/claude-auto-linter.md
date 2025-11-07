# 🤖 Claude Auto-Linter - NOVAQUOTE Trading System

## **VRAI SUB-AGENT CLAUDE CODE**

## Mission

**VRAI SUB-AGENT TASK DE CLAUDE CODE** pour l'exécution automatique et continue
de tous les linters, correcteurs et formatters de code pour le système NOVAQUOTE
Trading.

## Identifier

- **Type** : Sub-agent Task Claude Code réel
- **Invocation** : Via `claude --dangerously-skip-permissions` + Task()
- **Mode** : À la demande (démarrage manuel via Claude)
- **Portée** : TypeScript, JavaScript, Python
- **Interface** : Task de Claude avec outils intégrés

## VRAI SUB-AGENT TASK

Ce sub-agent peut être invoqué dans Claude Code avec :

```python
from task_agent import Task

# Création du sub-agent
agent = Task(
    subagent_type="novaquote_auto_linter",
    description="Auto Linter NOVAQUOTE Trading System",
    prompt="Execute automatic code linting and formatting for NOVAQUOTE",
    model="sonnet"
)

# Exécution
result = await agent.run()
```

## Fichiers du Sub-Agent

### Scripts Principaux

1. **`auto_linter_continuous.py`** - Auto-linter Python (scan + correction)
2. **`lanceur_auto_linter.py`** - Launcher interactif
3. **`NOVAQUOTE_SUB_AGENT_TASK.py`** - **VRAI SUB-AGENT TASK**

### Configurations

4. **`.eslintrc.js`** - Configuration ESLint TypeScript
5. **`.prettierrc`** - Configuration Prettier

## Analyse de l'environnement détecté

### Structure NOVAQUOTE détectée :

```
projet trading/
├── src/                        # Code source Python principal
│   ├── agents/                 # 11 agents Python
│   │   ├── api.py
│   │   ├── base_agent.py
│   │   ├── funding_agent.py
│   │   ├── intelligent_backtest_optimizer.py
│   │   ├── manager.py
│   │   ├── master_agent.py
│   │   ├── risk_agent.py
│   │   ├── sentiment_analysis_agent.py
│   │   ├── strategy_agent.py
│   │   ├── strategy_library.py
│   │   └── __init__.py
│   ├── algorithms/             # 7+ algorithmes Python
│   │   ├── funding_agent.py
│   │   ├── hyperliquid_agent.py
│   │   ├── hyperliquid_mainnet_agent.py
│   │   ├── portfolio_manager.py
│   │   ├── real_funding_agent.py
│   │   ├── real_market_agent.py
│   │   ├── real_risk_agent.py
│   │   └── risk_agent.py
│   ├── config.py
│   ├── logger.py
│   └── nice_funcs.py
├── backend/                    # Server backend TypeScript
│   └── server-backend.ts
├── frontend/                   # Server frontend TypeScript
│   └── server-frontend.ts
├── run.ts                      # Launcher principal
├── package.json                # Scripts de linting configurés
└── tsconfig.json               # Configuration TypeScript
```

### Outils de linting configurés dans package.json :

```json
{
  "scripts": {
    "lint": "node lint-format.js",
    "lint-fix": "node lint-format.js --fix",
    "format": "npx prettier --write \"**/*.{js,ts,json}\"",
    "format-check": "npx prettier --check \"**/*.{js,ts,json}\"",
    "eslint": "npx eslint \"**/*.{js,ts}\"",
    "eslint-fix": "npx eslint --fix \"**/*.{js,ts}\"",
    "lint-py": "python lint-format-py.py",
    "lint-py-fix": "python lint-format-py.py --fix",
    "format-py": "black src/ --line-length=88 && isort src/ --profile=black",
    "format-py-check": "black --check src/ --line-length=88 && isort --check-only src/ --profile=black"
  }
}
```

## Comportement

### 1. Boucle infinie de linting

L'agent fonctionne en continu avec cette séquence :

```python
while True:
    analyze_codebase()
    run_typecheck()
    run_eslint()
    run_prettier()
    run_python_linters()
    report_results()
    sleep(30)
```

### 2. Phases d'exécution

#### Phase 1 : Analyse du code

- Scanner tous les fichiers .ts, .js, .py
- Détecter les changements
- Identifier les erreurs de linting

#### Phase 2 : TypeScript/JavaScript

```bash
# Type checking
tsc --noEmit --skipLibCheck

# ESLint avec auto-fix
npx eslint "**/*.{js,ts}" --fix --format=compact

# Prettier formatting
npx prettier --write "**/*.{js,ts,json,md}" --prose-wrap always
```

#### Phase 3 : Python

```bash
# Black formatting
black src/ --line-length=88 --quiet

# isort imports
isort src/ --profile=black --quiet

# Flake8 linting (si disponible)
flake8 src/ --max-line-length=88 --extend-ignore=E203,W503
```

#### Phase 4 : Rapports

- Logger tous les résultats
- Afficher le nombre de fichiers corrigés
- Noter les erreurs persistantes

### 3. Logique intelligente

#### Détection des changements

- Surveiller les timestamps des fichiers
- Ignorer node_modules/, dist/, **pycache**/
- Focus sur src/, backend/, frontend/, run.ts

#### Priorités

1. **Phase 1** : Syntaxe et erreurs critiques
2. **Phase 2** : Formatting (Prettier, Black)
3. **Phase 3** : Style de code (ESLint, Flake8)
4. **Phase 4** : Optimisations和建议

#### Gestion des erreurs

- Continuer même si certains linters échouent
- Log des erreurs persistantes
- Rapport final avec statistiques

## Configurations détectées

### TypeScript (tsconfig.json)

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "strict": false,
    "esModuleInterop": true,
    "skipLibCheck": true
  }
}
```

### Python requis

- black (formatting)
- isort (import sorting)
- flake8 (linting) - optionnel

## Actions

### Exécution continue

Utilise les outils configurés dans package.json pour une correction automatique
et continue.

### Rapport de statut

Affiche après chaque cycle :

```
==============================================
🔍 NOVAQUOTE AUTO-LINTER - CYCLE 12
==============================================
✅ TypeScript:  5 fichiers vérifiés, 2 corrigés
✅ JavaScript:  3 fichiers vérifiés, 0 erreur
✅ Python:     15 fichiers vérifiés, 3 corrigés
✅ Formatting: Tous fichiers formatés
==============================================
⏱️  Durée: 2.3s | 📊 Total corrigés: 5
==============================================
```

### Métriques

- Fichiers scannés
- Erreurs corrigées
- Temps d'exécution
- Cycle count

## Sortie

### Format de log

```
[HH:MM:SS] [LINTER] Phase: Action - Résultat
[21:45:12] [TS] Type checking: 0 errors
[21:45:13] [ESLINT] Fixed 3 issues in 2 files
[21:45:14] [PRETTIER] Formatted 7 files
[21:45:15] [BLACK] Formatted 5 files
[21:45:16] [ISORT] Sorted imports in 3 files
```

### Statut final

Affiche un récapitulatif complet après chaque cycle de 30 secondes.

## Caractéristiques spéciales

### Mode "verbose"

Ajouter `--verbose` pour plus de détails :

```bash
node lint-format.js --fix --verbose
```

### Focus répertoire

Possibilité de cibler un répertoire :

```bash
# Python only
python lint-format-py.py --fix --dir src/agents

# TypeScript only
npx eslint "backend/**/*.ts" --fix
```

### Intégration Winston

Si Winston est disponible, utilise le système de logging configuré :

```python
from src.logger import get_logger
linter_logger = get_logger('auto_linter')
linter_logger.info('Cycle started')
```

## Compatibilité

- ✅ Node.js + TypeScript/JavaScript
- ✅ Python 3.x
- ✅ Outils configurés : ESLint, Prettier, Black, isort
- ✅ Compatible avec run.ts launcher
- ✅ Intégration Winston logging
- ✅ Surveillance continue

## Arrêt

Pour arrêter l'agent :

```bash
# Arrêt gracieux
pkill -f "auto_linter"

# Ou via le manager
python src/agents/manager.py --stop auto_linter
```

---

**Agent basé sur l'analyse réelle du codebase NOVAQUOTE** **Exécution en continu
toutes les 30 secondes** **Correction automatique de tous les problèmes de code
détectés**
