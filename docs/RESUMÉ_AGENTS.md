# 🎯 RÉSUMÉ : AGENTS NOVAQUOTE - Comment Les Utiliser

## ✅ Configuration Réussie

Les **5 agents NOVAQUOTE** sont **configurés** dans `.claude/agents.json` :

1. ✅ novaquote-bug-fixer
2. ✅ novaquote-code-reviewer
3. ✅ novaquote-docs-generator
4. ✅ novaquote-perf-optimizer
5. ✅ novaquote-test-enhancer

## ⚠️ IMPORTANT : Chargement Manuel Requis

**Claude Code ne charge PAS automatiquement les agents.**

## 🚀 Comment Utiliser (3 Méthodes)

### Méthode 1 : CLI avec Chargement

```bash
# Dans un terminal, LANCER Claude Code :
claude --agents @.claude/agents.json

# Puis dans la conversation :
/agents
# → Les 5 agents apparaissent !
```

### Méthode 2 : Invocation Directe

```bash
# Dans Claude Code (après avoir chargé avec --agents)
/使用 novaquote-bug-fixer 修复 src/ 目录中的所有问题
```

### Méthode 3 : PowerShell Autonome

```powershell
.\scripts\autonomous_agent_runner.ps1 -AgentName "novaquote-bug-fixer" -TaskDescription "Fix all code issues" -MaxIterations 3
```

## 📝 Problème de l'Interface /agents

L'interface `/agents` montre SEULEMENT :

- Les agents **built-in** (general-purpose, Explore, Plan, etc.)
- Les agents **chargés** dans la session courante

**Pour voir les agents NOVAQUOTE, il FAUT d'abord faire :**

```bash
claude --agents @.claude/agents.json
```

Puis `/agents` les affichera !

## 🎬 Démonstration

```bash
# 1. Lancer Claude avec les agents
claude --agents @.claude/agents.json

# 2. Dans la conversation
/agents
# → Devrait afficher les 5 agents NOVAQUOTE

# 3. Tester un agent
# → 5. Test agent
# → novaquote-bug-fixer
```

## ✅ Test Réussi

Dans nos tests, `echo "/agents\nlist" | claude --agents @.claude/agents.json`
**a bien listé les 5 agents** !
