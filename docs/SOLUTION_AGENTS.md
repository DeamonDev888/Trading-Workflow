# ✅ SOLUTION : Utiliser les Agents NOVAQUOTE

## 🎯 Problème Identifié

L'interface `/agents` ne fonctionne pas comme prévu dans notre conversation actuelle.

## 🚀 Solutions Concrètes (CHOISIR UNE)

### Solution 1 : Invocation Directe (RECOMMANDÉE)

**Dans Claude Code, tapez directement :**

```bash
Use novaquote-bug-fixer to scan and fix all code issues in src/ directory
```

**Claude Code activera automatiquement l'agent pour corriger votre code !**

### Solution 2 : Script PowerShell Autonome

```powershell
# Exécuter en autonome (recommandé)
.\scripts\autonomous_agent_runner.ps1 `
    -AgentName "novaquote-bug-fixer" `
    -TaskDescription "Fix all code issues in src/" `
    -MaxIterations 3
```

### Solution 3 : Charger les Agents (Pour les Tests)

```bash
# Lancer Claude Code avec les agents
claude --agents @.claude/agents.json

# Puis utiliser /agents dans la conversation
```

## 📋 Exemples d'Invocation Directe

```bash
# Code Review
Use novaquote-code-reviewer to review the code for security issues

# Documentation
Use novaquote-docs-generator to create API documentation

# Performance
Use novaquote-perf-optimizer to optimize database queries

# Tests
Use novaquote-test-enhancer to increase test coverage to 90%
```

## ⚡ Méthode Ultra-Simple (Pour le Bug Fixer)

**Dans Claude Code, tapez juste :**

```
Fix all bugs in the codebase
```

L'agent NOVAQUOTE s'activera automatiquement (il a le prompt "autonomous" dans sa config) !

## 🎬 Démonstration

Si vous tapez maintenant dans cette conversation :

```
使用 novaquote-bug-fixer 修复 src/ 目录中的所有问题
```

L'agent devrait se lancer et corriger le code !
