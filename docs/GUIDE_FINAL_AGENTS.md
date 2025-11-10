# 🎯 AGENTS NOVAQUOTE - GUIDE FINAL

## ✅ Status : OPÉRATIONNEL !

Les **5 agents NOVAQUOTE** sont **configurés et testés** dans `claude-agents.json` (racine).

## 🚀 Comment Les Utiliser

### Étape 1 : Lancer Claude Code avec les Agents

**Dans un terminal :**

```bash
claude --agents @claude-agents.json
```

### Étape 2 : Utiliser l'Interface /agents

**Dans la conversation Claude Code :**

```bash
/agents
# → Liste les 5 agents NOVAQUOTE
```

### Étape 3 : Utiliser un Agent

**Option A - Interface :**

```bash
/agents
# → 5. Test agent
# → novaquote-bug-fixer
```

**Option B - Invocation Directe (Plus Simple) :**

```bash
Use novaquote-bug-fixer to fix all code issues in src/
```

## 📋 Les 5 Agents

1. **novaquote-bug-fixer** - Auto Bug Fixer
2. **novaquote-code-reviewer** - Code Reviewer Expert
3. **novaquote-docs-generator** - Documentation Generator
4. **novaquote-perf-optimizer** - Performance Optimizer
5. **novaquote-test-enhancer** - Test Coverage Enhancer

## ⚡ Exemples d'Invocation

```bash
# Bug Fixing
Use novaquote-bug-fixer to scan and fix all code issues

# Code Review
Use novaquote-code-reviewer to review code for security

# Documentation
Use novaquote-docs-generator to create API documentation

# Performance
Use novaquote-perf-optimizer to optimize database queries

# Testing
Use novaquote-test-enhancer to increase test coverage
```

## 🔄 Exécution Autonome PowerShell

```powershell
.\scripts\autonomous_agent_runner.ps1 `
    -AgentName "novaquote-bug-fixer" `
    -TaskDescription "Fix all code issues" `
    -MaxIterations 3
```

## 📁 Fichiers de Configuration

- `claude-agents.json` - Configuration des agents (RACINE) ✅
- `config/novaquote-agents.json` - Backup de la config
- `.claude/` - Supprimé (mauvais emplacement) ❌

## 🎉 Test Réussi !

```bash
# Cette commande fonctionne :
claude --agents @claude-agents.json
# → Liste les 5 agents NOVAQUOTE
```

## ✅ Prêt à Utiliser !

Lancer `claude --agents @claude-agents.json` dans un terminal, puis utiliser `/agents` dans la conversation !
