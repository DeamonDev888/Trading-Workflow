# 🚀 GUIDE DE DÉMARRAGE RAPIDE - AGENTS CLAUDE CODE

## 📋 **PRÉREQUIS**

1. **Claude Code CLI** installé : https://code.claude.com
2. **PowerShell** (Windows)
3. Accès au projet

---

## ✅ **ÉTAPE 1 : CRÉER UN AGENT**

### **Via l'Interface `/agents`**

Dans Claude Code :

```bash
/agents
# Choisir: 2. Create new agent
```

### **Configuration JSON**

Créer `agents.json` :

```json
{
  "novaquote-bug-fixer": {
    "description": "Auto Bug Fixer for NOVAQUOTE project",
    "prompt": "Scan, analyze and fix code issues autonomously:\n\n1. Use Glob to find all Python/TypeScript files\n2. Use Grep to find patterns (TODO, FIXME, BUG, XXX)\n3. Use Read to examine files with issues\n4. Use Edit to fix problems:\n   - Remove unused imports\n   - Fix syntax errors\n   - Improve variable names\n   - Add type hints (Python)\n5. Use Bash to run black, isort, eslint for verification\n6. Repeat until no more issues or 3 iterations\n7. Generate a summary report\n\nReport format:\n- Files modified: [list]\n- Issues fixed: [count]\n- Summary: [description]",
    "tools": ["Read", "Edit", "Bash", "Grep", "Glob"],
    "model": "sonnet",
    "temperature": 0.2,
    "max-tokens": 4000
  },
  "code-reviewer": {
    "description": "Expert code reviewer for quality checks",
    "prompt": "Review code for quality, security and best practices:\n\n1. Read all modified files\n2. Check for security issues (XSS, SQL injection, etc.)\n3. Verify PEP8 compliance (Python)\n4. Check TypeScript types and best practices\n5. Verify test coverage\n6. Suggest improvements\n\nGenerate a detailed report with:\n- Security issues found\n- Code quality score (1-10)\n- Suggestions for improvement\n- Files requiring attention",
    "tools": ["Read", "Grep", "Bash"],
    "model": "sonnet",
    "temperature": 0.5
  }
}
```

### **Charger la Configuration**

```bash
# Via CLI
claude --agents @agents.json

# Ou via interface
/agents
# Choisir: 6. Import from file
# Entrer: agents.json
```

---

## ✅ **ÉTAPE 2 : TESTER L'AGENT**

### **Test Interactif**

```bash
# Dans Claude Code
/agents
# Choisir: 5. Test agent
# Sélectionner: novaquote-bug-fixer
```

### **Test Automatique**

Créer `test-agent.ps1` :

```powershell
# Test automatique de l'agent
$agentName = "novaquote-bug-fixer"
$task = "Fix all issues in src/ directory"

Write-Host "Testing agent: $agentName" -ForegroundColor Cyan
Write-Host "Task: $task" -ForegroundColor Yellow

claude --agent $agentName --task $task --output json
```

Exécuter :

```powershell
.\test-agent.ps1
```

---

## ✅ **ÉTAPE 3 : UTILISER L'AGENT AUTONOME**

### **Mode Simple (Une fois)**

```powershell
# Exécuter l'agent une fois
.\autonomous_agent_runner.ps1 `
    -AgentName "novaquote-bug-fixer" `
    -TaskDescription "Fix all code issues in src/" `
    -MaxIterations 3 `
    -IntervalSeconds 60
```

### **Mode Boucle (Autonome)**

```powershell
# Exécuter en boucle toutes les 5 minutes
.\autonomous_agent_runner.ps1 `
    -AgentName "novaquote-bug-fixer" `
    -TaskDescription "Auto-fix code in src/" `
    -MaxIterations 10 `
    -IntervalSeconds 300
```

### **Mode Arrière-Plan**

```powershell
# Lancer en arrière-plan
.\autonomous_agent_runner.ps1 `
    -AgentName "novaquote-bug-fixer" `
    -TaskDescription "Continuous bug fixing" `
    -Background

# Vérifier le statut
Get-Job

# Arrêter l'agent
Stop-Job -Id <JobId>
```

---

## ✅ **ÉTAPE 4 : MONITORING**

### **Fichiers de Suivi**

L'agent crée automatiquement :

- `agent-state.json` - État actuel
- `agent-results.json` - Résultats finaux
- `agent-output.json` - Sortie de l'agent

### **Surveillance en Temps Réel**

```powershell
# Surveiller les logs
Get-Content -Path "agent-results.json" -Wait -Tail 50

# Vérifier l'état
Get-Content -Path "agent-state.json" | ConvertFrom-Json
```

### **Alertes PowerShell**

```powershell
# Script d'alerte
$state = Get-Content "agent-state.json" | ConvertFrom-Json

if ($state.status -eq "Error") {
    Write-Host "ALERT: Agent failed!" -ForegroundColor Red
    # Envoyer email, notification, etc.
}

if ($state.changesMade -gt 0) {
    Write-Host "INFO: $($state.changesMade) changes made" -ForegroundColor Green
}
```

---

## ✅ **ÉTAPE 5 : AUTOMATISATION COMPLÈTE**

### **Service Windows**

Créer un service pour l'agent :

```powershell
# Créer le service
$serviceName = "ClaudeBugFixer"
$scriptPath = "C:\Path\to\autonomous_agent_runner.ps1"
$serviceDisplay = "Claude Bug Fixer Service"

New-Service -Name $serviceName `
           -BinaryPathName "powershell.exe -ExecutionPolicy Bypass -File `"$scriptPath`" -AgentName novaquote-bug-fixer -TaskDescription 'Auto-fix code' -MaxIterations 10 -IntervalSeconds 300" `
           -DisplayName $serviceDisplay `
           -Description "Autonomous bug fixing with Claude Code" `
           -StartupType Automatic

# Démarrer le service
Start-Service $serviceName

# Vérifier le statut
Get-Service $serviceName
```

### **Tâche Planifiée (Scheduler)**

```powershell
# Créer une tâche qui s'exécute toutes les heures
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
    -Argument "-ExecutionPolicy Bypass -File C:\Path\to\autonomous_agent_runner.ps1 -AgentName novaquote-bug-fixer -TaskDescription 'Hourly fix' -MaxIterations 5 -RunOnce"

$trigger = New-ScheduledTaskTrigger -Once `
    -At 00:00 `
    -RepetitionInterval (New-TimeSpan -Hours 1)

Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "ClaudeBugFixer" -Description "Hourly autonomous bug fixing"

# Démarrer la tâche
Start-ScheduledTask -TaskName "ClaudeBugFixer"
```

### **Script de Surveillance Continu**

```powershell
# monitoring.ps1
while ($true) {
    $state = Get-Content "agent-state.json" -ErrorAction SilentlyContinue | ConvertFrom-Json

    if ($state) {
        $elapsed = (Get-Date) - $state.lastRun
        if ($elapsed.TotalMinutes -gt 60) {
            Write-Host "WARNING: Agent inactive for $($elapsed.TotalMinutes) minutes" -ForegroundColor Yellow
            # Redémarrer l'agent si nécessaire
        }
    }

    Start-Sleep -Seconds 60  # Vérifier toutes les minutes
}
```

---

## ✅ **ÉTAPE 6 : OPTIMISATION**

### **Configuration Optimale**

Pour un agent rapide et efficace :

```json
{
  "fast-bug-fixer": {
    "description": "Fast bug fixing agent",
    "prompt": "Quick fixes only: unused imports, syntax errors",
    "tools": ["Read", "Edit", "Bash"],
    "model": "haiku",
    "temperature": 0.1,
    "max-tokens": 2000
  }
}
```

### **Gestion des Coûts**

```powershell
# Script pour limiter les coûts
$maxCostPerDay = 10  # USD

# Surveiller les coûts
$usage = Invoke-RestMethod -Uri "https://api.anthropic.com/v1/usage" -Headers @{ "X-API-Key" = $env:ANTHROPIC_API_KEY }

if ($usage.dailyCost -gt $maxCostPerDay) {
    Write-Host "WARNING: Daily limit reached ($($usage.dailyCost) USD)" -ForegroundColor Red
    # Arrêter l'agent temporairement
    Stop-Service "ClaudeBugFixer"
}
```

---

## 📊 **EXEMPLES D'UTILISATION**

### **Exemple 1 : Fix Quotidien**

```powershell
# Exécuter chaque matin à 9h
$trigger = New-ScheduledTaskTrigger -Daily -At 9am
# ... créer la tâche ...
```

### **Exemple 2 : Fix sur Push Git**

```powershell
# hook-post-push.ps1 (exécuté après un git push)
$changes = git diff --name-only HEAD~1

if ($changes) {
    .\autonomous_agent_runner.ps1 -AgentName "code-reviewer" -TaskDescription "Review changed files: $changes" -MaxIterations 1
}
```

### **Exemple 3 : Monitoring Continu**

```powershell
# Lancer le monitoring 24/7
$job = Start-Job -ScriptBlock {
    while ($true) {
        .\autonomous_agent_runner.ps1 -AgentName "novaquote-bug-fixer" -TaskDescription "Continuous monitoring" -MaxIterations 3 -IntervalSeconds 900
        Start-Sleep -Seconds 900  # 15 minutes
    }
}
```

---

## 🛠️ **DÉPANNAGE**

### **Problèmes Courants**

| Problème               | Solution                                                       |
| ---------------------- | -------------------------------------------------------------- |
| Agent ne répond pas    | Vérifier que Claude Code CLI est installé : `claude --version` |
| Pas de résultats       | Vérifier les permissions des outils dans la config             |
| Coût élevé             | Utiliser le modèle `haiku` au lieu de `sonnet`                 |
| Agent bloqué           | Utiliser `--RunOnce` pour un seul passage                      |
| Service ne démarre pas | Vérifier l'ExecutionPolicy PowerShell                          |

### **Commandes de Debug**

```powershell
# Vérifier la version
claude --version

# Tester un agent manuellement
claude --agent novaquote-bug-fixer --task "Test"

# Vérifier les logs
Get-Content "agent-results.json" -Tail 100

# Vérifier l'état
Get-Content "agent-state.json" | ConvertFrom-Json
```

---

## 📚 **RESSOURCES**

- **Documentation Complète** : `docs/CLAUDE_CODE_AGENTS_DOCUMENTATION.md`
- **Exemples d'Agents** : `scripts/novaquote_bug_fixer_task.py`
- **Runner Autonome** : `scripts/autonomous_agent_runner.ps1`
- **Site Officiel** : https://code.claude.com

---

**🎯 Prêt à créer vos agents autonomes !** Pour toute question, consultez la documentation complète.
