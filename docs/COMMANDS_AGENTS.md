# 🚀 Commandes des Agents NOVAQUOTE

## 📁 Agents JSON Créés dans `.claude/agents/`

✅ **5 agents JSON individuels créés :**

- `novaquote-bug-fixer.json`
- `novaquote-code-reviewer.json`
- `novaquote-docs-generator.json`
- `novaquote-perf-optimizer.json`
- `novaquote-test-enhancer.json`

---

## 🎯 Commandes d'Appel des Agents

### **1. Bug Fixer**

```bash
# Appel individuel
claude --agents .claude/agents/novaquote-bug-fixer.json --print --dangerously-skip-permissions "Scan for bugs in src/agents/"

# Tâche spécifique
claude --agents .claude/agents/novaquote-bug-fixer.json --print --dangerously-skip-permissions "Fix the import errors in strategy_agent.py"

# Analyse complète avec permissions
claude --agents .claude/agents/novaquote-bug-fixer.json --print --dangerously-skip-permissions "Analyze and fix all critical issues in the codebase"
```

### **2. Code Reviewer**

```bash
# Appel individuel
claude --agents .claude/agents/novaquote-code-reviewer.json --print --dangerously-skip-permissions "Review the security of the trading system"

# Audit de sécurité
claude --agents .claude/agents/novaquote-code-reviewer.json --print --dangerously-skip-permissions "Check for SQL injection vulnerabilities"

# Audit complet
claude --agents .claude/agents/novaquote-code-reviewer.json --print --dangerously-skip-permissions "Perform comprehensive security audit of all modules"
```

### **3. Documentation Generator**

```bash
# Appel individuel
claude --agents .claude/agents/novaquote-docs-generator.json --print --dangerously-skip-permissions "Generate API documentation"

# Documentation spécifique
claude --agents .claude/agents/novaquote-docs-generator.json --print --dangerously-skip-permissions "Create setup guide for new developers"

# Documentation complète
claude --agents .claude/agents/novaquote-docs-generator.json --print --dangerously-skip-permissions "Generate complete project documentation including all guides"
```

### **4. Performance Optimizer**

```bash
# Appel individuel
claude --agents .claude/agents/novaquote-perf-optimizer.json --print --dangerously-skip-permissions "Optimize database queries"

# Optimisation spécifique
claude --agents .claude/agents/novaquote-perf-optimizer.json --print --dangerously-skip-permissions "Improve trading execution speed"

# Optimisation système
claude --agents .claude/agents/novaquote-perf-optimizer.json --print --dangerously-skip-permissions "Optimize entire system performance including API and algorithms"
```

### **5. Test Enhancer**

```bash
# Appel individuel
claude --agents .claude/agents/novaquote-test-enhancer.json --print --dangerously-skip-permissions "Enhance test coverage"

# Tests spécifiques
claude --agents .claude/agents/novaquote-test-enhancer.json --print --dangerously-skip-permissions "Create unit tests for risk management"

# Suite de tests complète
claude --agents .claude/agents/novaquote-test-enhancer.json --print --dangerously-skip-permissions "Create comprehensive test suite with unit, integration and performance tests"
```

---

## 🔧 Variations de Commandes

### **Avec Fichier JSON Combiné**

```bash
# Utiliser le fichier complet
claude --agents @claude-agents.json --print --dangerously-skip-permissions "I need to review code quality"

# Délégation automatique
claude --agents @claude-agents.json --print --dangerously-skip-permissions "Generate documentation for the API"

# Analyse complète
claude --agents @claude-agents.json --print --dangerously-skip-permissions "Perform complete system analysis and optimization"
```

### **Avec JSON Inline**

```bash
# Bug fixer inline
claude --agents '{
  "novaquote-bug-fixer": {
    "description": "Expert debugging specialist",
    "prompt": "Scan and fix code issues",
    "tools": ["Read", "Edit", "Bash"]
  }
}' --print --dangerously-skip-permissions "Fix syntax errors in the codebase"

# Code reviewer inline
claude --agents '{
  "novaquote-code-reviewer": {
    "description": "Security expert",
    "prompt": "Audit for security vulnerabilities",
    "tools": ["Read", "Grep", "Bash"]
  }
}' --print --dangerously-skip-permissions "Security audit of payment system"
```

### **Multiple Agents**

```bash
# Combiner plusieurs agents
claude --agents .claude/agents/novaquote-bug-fixer.json --agents .claude/agents/novaquote-code-reviewer.json --print --dangerously-skip-permissions "Fix and review the authentication module"

# Workflow complet
claude --agents .claude/agents/novaquote-bug-fixer.json --agents .claude/agents/novaquote-perf-optimizer.json --print --dangerously-skip-permissions "Fix bugs and optimize performance of trading engine"
```

---

## 🎯 Appels par Délégation Automatique

```bash
# Délégation vers bug-fixer
claude --agents @claude-agents.json --print --dangerously-skip-permissions "There are bugs in the trading algorithms that need fixing"

# Délégation vers code-reviewer
claude --agents @claude-agents.json --print --dangerously-skip-permissions "I need a security audit of the payment system"

# Délégation vers docs-generator
claude --agents @claude-agents.json --print --dangerously-skip-permissions "Create comprehensive documentation for the frontend"

# Délégation vers perf-optimizer
claude --agents @claude-agents.json --print --dangerously-skip-permissions "The API responses are too slow, optimize them"

# Délégation vers test-enhancer
claude --agents @claude-agents.json --print --dangerously-skip-permissions "We need more test coverage for the risk management module"
```

---

## 🚀 Appels Explicites

```bash
# Appel explicite par nom
claude --agents @claude-agents.json --print --dangerously-skip-permissions "Use the novaquote-bug-fixer agent to analyze the exchange_manager.py issue"

claude --agents @claude-agents.json --print --dangerously-skip-permissions "Use the novaquote-code-reviewer agent to audit the wallet security"

claude --agents @claude-agents.json --print --dangerously-skip-permissions "Use the novaquote-docs-generator agent to create the README"

claude --agents @claude-agents.json --print --dangerously-skip-permissions "Use the novaquote-perf-optimizer agent to improve database performance"

claude --agents @claude-agents.json --print --dangerously-skip-permissions "Use the novaquote-test-enhancer agent to add integration tests"
```

---

## 📋 Options Supplémentaires

### **Standard (Recommandé)**

```bash
# Toutes les commandes incluent --dangerously-skip-permissions
claude --agents .claude/agents/novaquote-bug-fixer.json --print --dangerously-skip-permissions "Debug the system"
```

### **Avec Sortie Verbose**

```bash
claude --agents .claude/agents/novaquote-bug-fixer.json --print --dangerously-skip-permissions --verbose "Debug the system with detailed output"
```

### **Mode Plan**

```bash
claude --agents .claude/agents/novaquote-docs-generator.json --plan --dangerously-skip-permissions "Create comprehensive documentation plan"
```

### **Script d'Automatisation**

```bash
#!/bin/bash
# Exemple de script pour l'automatisation
claude --agents .claude/agents/novaquote-bug-fixer.json --print --dangerously-skip-permissions "Daily bug scan and fix"
claude --agents .claude/agents/novaquote-perf-optimizer.json --print --dangerously-skip-permissions "Daily performance optimization"
```

---

## 💡 Conseils d'Usage

1. **Agents individuels JSON** : Pour tâches spécifiques et ciblées
2. **Fichier combiné** : Pour délégation automatique et workflows complexes
3. **Appel explicite** : Quand vous voulez un agent spécifique
4. **JSON inline** : Pour tests rapides et configurations temporaires

## ⚠️ **Important : --dangerously-skip-permissions**

**Toutes les commandes incluent `--dangerously-skip-permissions` pour :**

- ✅ Éviter les blocages de permissions
- ✅ Permettre aux agents d'exécuter des modifications
- ✅ Assurer le fonctionnement optimal avec les outils
- ✅ Activer l'accès complet aux fichiers et bash

**Usage recommandé pour les agents NOVAQUOTE :**

```bash
# Format standard pour tous les appels
claude --agents [AGENT_FILE] --print --dangerously-skip-permissions "Tâche spécifique"
```

**Toutes ces commandes fonctionnent avec les agents JSON créés dans `.claude/agents/` !** 🎯

---

## 📑 **Récapitulatif des Commandes Principales**

### **Plus Utilisées**

```bash
# Bug Fixer - Analyse et correction
claude --agents .claude/agents/novaquote-bug-fixer.json --print --dangerously-skip-permissions "Fix critical issues"

# Code Reviewer - Audit de sécurité
claude --agents .claude/agents/novaquote-code-reviewer.json --print --dangerously-skip-permissions "Security audit"

# Documentation Generator - Documentation complète
claude --agents .claude/agents/novaquote-docs-generator.json --print --dangerously-skip-permissions "Generate docs"

# Performance Optimizer - Optimisation
claude --agents .claude/agents/novaquote-perf-optimizer.json --print --dangerously-skip-permissions "Optimize performance"

# Test Enhancer - Tests
claude --agents .claude/agents/novaquote-test-enhancer.json --print --dangerously-skip-permissions "Enhance tests"
```

### **Workflow Complet**

```bash
# Analyse complète avec délégation automatique
claude --agents @claude-agents.json --print --dangerously-skip-permissions "Complete system analysis and optimization"
```
