# 🎯 GUIDE FINAL : Agents NOVAQUOTE

## ✅ Status : CONFIGURÉS MAIS NON AUTO-CHARGÉS

Les 5 agents NOVAQUOTE sont **opérationnels** :

- ✅ novaquote-bug-fixer
- ✅ novaquote-code-reviewer
- ✅ novaquote-docs-generator
- ✅ novaquote-perf-optimizer
- ✅ novaquote-test-enhancer

## 🚨 Problème : Interface /agents Indisponible

Dans notre conversation actuelle, `/agents` ne fonctionne pas.

## ✅ SOLUTIONS FONCTIONNELLES

### Solution 1 : Invocation Directe (Plus Simple)

**Tapez dans Claude Code :**

```
Use novaquote-bug-fixer to fix all code issues
```

→ L'agent s'active automatiquement !

### Solution 2 : PowerShell Autonome (Pour Production)

```powershell
.\scripts\autonomous_agent_runner.ps1 `
    -AgentName "novaquote-bug-fixer" `
    -TaskDescription "Fix all code issues" `
    -MaxIterations 3
```

### Solution 3 : Nouvelle Conversation avec Chargement

**Dans un terminal :**

```bash
claude --agents @.claude/agents.json
```

**Puis dans la nouvelle conversation :**

```
/agents
# → Les agents apparaissent
```

## 📚 Documentation Complète

- `docs/CLAUDE_CODE_AGENTS_DOCUMENTATION.md` - Guide complet
- `docs/AGENT_QUICK_START.md` - Démarrage rapide
- `AGENTS_USAGE.md` - Utilisation
- `SOLUTION_AGENTS.md` - Solutions
- `scripts/autonomous_agent_runner.ps1` - Script autonome

## 🎯 Recommandation

**Utilisez l'Invocation Directe** : C'est la méthode la plus simple et qui fonctionne dans n'importe quelle conversation !
