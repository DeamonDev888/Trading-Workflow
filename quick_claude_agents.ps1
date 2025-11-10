# ============================================================================
# [OK] Quick NOVAQUOTE Claude Code Agents
# Script PowerShell simple pour utilisation rapide
# Built with love by Deamon Dev [ROCKET]
# ============================================================================

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("strategy", "risk", "funding", "sentiment", "complete", "test")]
    [string]$Mode = "complete",

    [Parameter(Mandatory=$false)]
    [string]$Task = "",

    [Parameter(Mandatory=$false)]
    [string]$ContextFile = "examples\market_context.json"
)

# Configuration
$Global:ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$Global:ProjectRoot = (Split-Path -Parent (Split-Path -Parent $ScriptDir))
$Global:PythonExe = "python"
$Global:AgentRunner = Join-Path $ScriptDir "claude_code_agent_runner.py"

# Fonctions utilitaires
function Write-Header {
    param([string]$Message)
    Write-Host "`n$('='*60)" -ForegroundColor Cyan
    Write-Host "  $Message" -ForegroundColor Cyan
    Write-Host "$('='*60)`n" -ForegroundColor Cyan
}

function Test-Python {
    try {
        & $PythonExe --version | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Afficher l'en-tête
Write-Header "NOVAQUOTE CLAUDE CODE AGENTS - QUICK MODE"

# Vérifier Python
Write-Host "Checking prerequisites..." -ForegroundColor Yellow
if (-not (Test-Python)) {
    Write-Host "❌ Python not found! Please install Python 3.8+" -ForegroundColor Red
    Write-Host "   Download: https://python.org" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Python found" -ForegroundColor Green

# Vérifier le script
if (-not (Test-Path $AgentRunner)) {
    Write-Host "❌ Agent runner not found: $AgentRunner" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Agent runner found" -ForegroundColor Green

# Exécuter selon le mode
Write-Host "`nExecuting: $Mode mode" -ForegroundColor Cyan

try {
    switch ($Mode) {
        "strategy" {
            if (-not $Task) { $Task = "Analyze BTC trading opportunity" }
            & $PythonExe $AgentRunner --mode single --agent "claude-strategy-advisor" --task $Task --context $ContextFile
        }
        "risk" {
            if (-not $Task) { $Task = "Assess portfolio risk" }
            & $PythonExe $AgentRunner --mode single --agent "claude-risk-advisor" --task $Task --context $ContextFile
        }
        "funding" {
            if (-not $Task) { $Task = "Optimize funding rate strategy" }
            & $PythonExe $AgentRunner --mode single --agent "claude-funding-advisor" --task $Task --context $ContextFile
        }
        "sentiment" {
            if (-not $Task) { $Task = "Analyze market sentiment" }
            & $PythonExe $AgentRunner --mode single --agent "claude-sentiment-analyzer" --task $Task --context $ContextFile
        }
        "complete" {
            & $PythonExe $AgentRunner --mode complete --context $ContextFile
        }
        "test" {
            & $PythonExe (Join-Path $ScriptDir "test_claude_code_integration.py")
        }
        default {
            Write-Host "❌ Unknown mode: $Mode" -ForegroundColor Red
            exit 1
        }
    }

    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ Execution completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "`n❌ Execution failed with exit code: $LASTEXITCODE" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}
catch {
    Write-Host "`n❌ Error: $_" -ForegroundColor Red
    exit 1
}

# ============================================================================
# Exemples d'utilisation (commentés)
# ============================================================================

<#

# Analyse rapide d'une stratégie
.\quick_claude_agents.ps1 -Mode strategy

# Évaluation de risque avec tâche personnalisée
.\quick_claude_agents.ps1 -Mode risk -Task "Should I close my position?"

# Analyse complète
.\quick_claude_agents.ps1 -Mode complete

# Lancer les tests
.\quick_claude_agents.ps1 -Mode test

# Avec contexte personnalisé
.\quick_claude_agents.ps1 -Mode strategy -ContextFile "my_context.json"

# Avec tâche personnalisée
.\quick_claude_agents.ps1 -Mode complete -Task "Analyze ETH trading opportunity"

#>
