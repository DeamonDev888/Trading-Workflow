# 🔧 GUIDE D'UTILISATION DES AGENTS NOVAQUOTE

## ✅ État : 5 Agents Configurés

Les agents NOVAQUOTE sont configurés dans `.claude/agents.json` mais **DOIVENT ÊTRE CHARGÉS MANUELLEMENT** dans chaque conversation.

## 📋 Agents Disponibles

1. **novaquote-bug-fixer** - Auto Bug Fixer
2. **novaquote-code-reviewer** - Code Reviewer Expert
3. **novaquote-docs-generator** - Documentation Generator
4. **novaquote-perf-optimizer** - Performance Optimizer
5. **novaquote-test-enhancer** - Test Coverage Enhancer

## 🚀 Méthode 1 : Chargement par Conversation

**Dans Claude Code (chaque nouvelle conversation) :**

```bash
# Charger les agents
claude --agents @.claude/agents.json

# Puis les utiliser
/agents
# → Les 5 agents apparaissent !
```

## 🚀 Méthode 2 : Invocation Directe

**Dans Claude Code :**

```bash
# Méthode directe (sans /agents)
使用 novaquote-bug-fixer 修复 src/ 目录中的所有问题

# Ou en anglais
Use novaquote-code-reviewer to review the code changes
```

## 🚀 Méthode 3 : PowerShell Autonome

```powershell
.\scripts\autonomous_agent_runner.ps1 `
    -AgentName "novaquote-bug-fixer" `
    -TaskDescription "Fix all code issues in src/" `
    -MaxIterations 3
```

## 📝 Note Importante

**Les agents ne sont PAS auto-chargés** à cause d'une limitation de Claude Code. Il faut utiliser `--agents @.claude/agents.json` au début de chaque conversation.
