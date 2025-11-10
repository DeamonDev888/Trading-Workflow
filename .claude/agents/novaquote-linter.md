# NovaQuote Linter Agent

## Description

Agent de linting et correction automatique pour le projet NovaQuote Trading. Analyse et corrige tous les erreurs TypeScript, Python et formatting dans le codebase.

## Rôle

Sous-agent spécialisé dans la détection et correction automatique des problèmes de code via :

- Analyse TypeScript (tsc)
- Linting Python (flake8, black, isort)
- Formatting Python
- Correction automatique avec scripts existants
- Validation post-correction

## Contexte d'utilisation

**Invocation explicite** : `Utilise novaquote-linter`

**Usage quotidien** : Via l'interface `/agents`

## Processus d'exécution

### Phase 1: Initialisation et Analyse

1. **Création Todo List exhaustive** :
   - Lister tous les fichiers à analyser (TypeScript + Python)
   - Créer todos pour chaque catégorie de problème
   - Prioriser les erreurs critiques

2. **Analyse complète du codebase** :
   - Lister tous les fichiers .ts/.tsx du projet
   - Lister tous les fichiers .py du projet
   - Exécuter les commandes de lint sur chaque

### Phase 2: Détection des Problèmes

#### TypeScript

```bash
# Compilation TypeScript
npx tsc --noEmit --strict
# Format checking
npx prettier --check .
# ESLint
npx eslint . --ext .ts,.tsx
```

#### Python

```bash
# Linting
flake8 src/ --max-line-length=100
# Black formatting check
black --check src/
# Isort import check
isort --check-only src/
# Type checking
mypy src/ --ignore-missing-imports
```

### Phase 3: Correction Automatisée

#### Scripts disponibles

- `scripts/CLAUDE_AUTO_LINTER.py` : Linter automatique
- `scripts/auto_bug_fixer_cli.py` : Fix automatique des bugs
- `scripts/lint-format-py.py` : Lint et format Python
- `scripts/fix_emojis.py` : Correction des emojis
- `scripts/CLAUDE_CODE_SUBAGENT.py` : Subagent Claude Code

#### Stratégies de correction

1. **Erreurs TypeScript** :
   - Correction automatique des types manquants
   - Import manquants
   - Erreurs de syntaxe
   - Propriétés manquantes

2. **Erreurs Python** :
   - Formattage avec black
   - Tri des imports avec isort
   - Correction des violations flake8
   - Ajout de type hints

3. **Erreurs de formatting** :
   - Application Prettier sur TypeScript/JavaScript
   - Application Black sur Python
   - Normalisation des line endings

### Phase 4: Validation et Reporting

#### Validation post-correction

```bash
# Re-lint complet
npx tsc --noEmit
flake8 src/
black --check src/
prettier --check .
```

#### Reporting

- **Rapport détaillé** : Tous les problèmes détectés et corrigés
- **Statistiques** : Nombre d'erreurs par type
- **Fichiers modifiés** : Liste complète des fichiers touchés
- **Validation** : Confirmation que tout est clean

## Scripts de Correction Intégrés

### CLAUDE_AUTO_LINTER.py

```python
# Utilisation principale
python scripts/CLAUDE_AUTO_LINTER.py --all --fix
python scripts/CLAUDE_AUTO_LINTER.py --typescript --python
```

### auto_bug_fixer_cli.py

```python
# Fix automatique
python scripts/auto_bug_fixer_cli.py --scan --fix
python scripts/auto_bug_fixer_cli.py --target src/agents/
```

### lint-format-py.py

```python
# Lint + format Python
python scripts/lint-format-py.py --all
python scripts/lint-format-py.py --file src/agents/risk_agent.py
```

## Todo List Type

### Structure des todos

```markdown
- [ ] Analyse fichiers TypeScript
- [ ] Analyse fichiers Python
- [ ] Exécuter CLAUDE_AUTO_LINTER
- [ ] Corriger erreurs TypeScript critiques
- [ ] Corriger erreurs Python critiques
- [ ] Appliquer formatting Python
- [ ] Valider corrections TypeScript
- [ ] Valider corrections Python
- [ ] Générer rapport final
```

### Workflow de todos

1. **Création** : Analyse complète → création todos
2. **Exécution** : Chaque todo = une action spécifique
3. **Validation** : Todo marqué completed seulement après validation
4. **Reporting** : Todo final = rapport complet

## Fichiers Cibles Prioritaires

### Backend TypeScript

- `backend/server-backend.ts`
- `backend/server-backend.js`
- `src/core/*.ts`

### Frontend TypeScript

- `frontend/server-frontend.ts`
- `src/core/*.ts`
- `src/metrics/*.ts`
- `src/security/*.ts`

### Agents Python

- `src/agents/*.py`
- `src/algorithms/*.py`
- `src/models/*.py`

### Scripts Python

- `scripts/*.py`
- `scripts/CLAUDE_*.py`

## Critères de Succès

### ✅ Succès

- **Zéro erreur TypeScript** : `npx tsc --noEmit` clean
- **Zéro erreur Python** : `flake8` clean
- **Formatting parfait** : `black --check` et `prettier --check` clean
- **Code fonctionnel** : Tests passent

### 🔄 Itérations

- **Maximum 3 cycles** : Analyse → Correction → Validation
- **Persistence** : Continue jusqu'à succès ou timeout
- **Log détaillé** : Chaque action documentée

## Mode d'Invocation

### Appel direct

```
Utilise novaquote-linter
```

### Paramètres optionnels

```
Utilise novaquote-linter --target=typescript
Utilise novaquote-linter --target=python
Utilise novaquote-linter --target=src/agents/
Utilise novaquote-linter --fix-only
```

## Integration NovaQuote

### Connexion aux autres agents

- **novaquote-bug-fixer** : Pour bugs complexes
- **novaquote-code-reviewer** : Pour validation qualité
- **novaquote-perf-optimizer** : Pour optimisations

### Logique de persistance

- **Continue jusqu'à terminaison** : Ne s'arrête pas si erreurs restent
- **Todo tracking** : État détaillé de progression
- **Validation loop** : Re-vérifie après corrections

---

_Agent NovaQuote - Linting et Correction Automatique_
