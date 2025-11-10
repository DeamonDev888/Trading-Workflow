# ============================================================================
# [OK] NOVAQUOTE Claude Code Agents - PowerShell Automation
# Built with love by Deamon Dev [ROCKET]
# Pattern: claude --agents @.claude/agents/ avec script PowerShell
# ============================================================================

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("single", "delegation", "complete", "batch", "autonomous")]
    [string]$Mode,

    [string]$Agent = "",
    [string]$Task = "",
    [string]$ContextFile = "",
    [int]$Iterations = 3,
    [string]$TasksFile = "",
    [int]$IntervalSeconds = 300,
    [int]$MaxIterations = 0,
    [switch]$NoSave = $false,
    [string]$ProjectPath = "",
    [switch]$Verbose = $false
)

# Configuration
$ErrorActionPreference = "Stop"
$Global:ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$Global:ProjectRoot = if ($ProjectPath) { $ProjectPath } else { (Split-Path -Parent (Split-Path -Parent $ScriptDir)) }
$Global:PythonExe = "python"
$Global:AgentRunnerScript = Join-Path $ScriptDir "claude_code_agent_runner.py"

# Couleurs pour l'affichage
$Colors = @{
    Header = "Cyan"
    Success = "Green"
    Warning = "Yellow"
    Error = "Red"
    Info = "White"
}

# ============================================================================
# Fonctions utilitaires
# ============================================================================

function Write-Header {
    param([string]$Message)
    Write-Host "`n$('='*60)" -ForegroundColor $Colors.Header
    Write-Host $Message -ForegroundColor $Colors.Header
    Write-Host "$('='*60)`n" -ForegroundColor $Colors.Header
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor $Colors.Success
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor $Colors.Warning
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor $Colors.Error
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor $Colors.Info
}

function Test-Prerequisites {
    Write-Header "Checking Prerequisites"

    # Vérifier Python
    try {
        $pythonVersion = & $PythonExe --version 2>&1
        Write-Success "Python found: $pythonVersion"
    }
    catch {
        Write-Error "Python not found! Please install Python 3.8+"
        exit 1
    }

    # Vérifier le script runner
    if (-not (Test-Path $AgentRunnerScript)) {
        Write-Error "Agent runner script not found: $AgentRunnerScript"
        exit 1
    }
    Write-Success "Agent runner script found"

    # Vérifier le projet
    $projectConfig = Join-Path $ProjectRoot "claude-agents.json"
    if (-not (Test-Path $projectConfig)) {
        Write-Warning "claude-agents.json not found, will be created automatically"
    }
    else {
        Write-Success "Project configuration found"
    }
}

function Build-PythonArgs {
    param(
        [string]$Mode,
        [string]$Agent = "",
        [string]$Task = "",
        [string]$ContextFile = "",
        [int]$Iterations = 3,
        [string]$TasksFile = "",
        [int]$IntervalSeconds = 300,
        [int]$MaxIterations = 0,
        [bool]$NoSave = $false
    )

    $args = @($AgentRunnerScript, "--mode", $Mode)

    if ($Agent -and $Mode -eq "single") {
        $args += "--agent", $Agent
    }

    if ($Task) {
        $args += "--task", $Task
    }

    if ($ContextFile) {
        $args += "--context", $ContextFile
    }

    if ($Iterations -and $Mode -ne "autonomous") {
        $args += "--iterations", $Iterations.ToString()
    }

    if ($TasksFile) {
        $args += "--tasks-file", $TasksFile
    }

    if ($Mode -eq "autonomous") {
        $args += "--interval", $IntervalSeconds.ToString()
        if ($MaxIterations -gt 0) {
            $args += "--max-iterations", $MaxIterations.ToString()
        }
    }

    if ($NoSave) {
        $args += "--no-save"
    }

    if ($ProjectPath) {
        $args += "--project-path", $ProjectPath
    }

    return $args
}

function Invoke-PythonRunner {
    param([array]$Arguments)

    try {
        if ($Verbose) {
            Write-Info "Executing: $PythonExe $($Arguments -join ' ')"
        }

        & $PythonExe @Arguments

        if ($LASTEXITCODE -eq 0) {
            Write-Success "Execution completed successfully"
            return $true
        }
        else {
            Write-Error "Execution failed with exit code: $LASTEXITCODE"
            return $false
        }
    }
    catch {
        Write-Error "Exception during execution: $_"
        return $false
    }
}

# ============================================================================
# Modes d'exécution
# ============================================================================

function Start-SingleAgent {
    param([string]$Agent, [string]$Task, [string]$ContextFile, [int]$Iterations, [bool]$NoSave)

    if (-not $Agent -or -not $Task) {
        Write-Error "Agent and Task are required for single mode"
        return $false
    }

    Write-Header "Single Agent Mode"
    Write-Info "Agent: $Agent"
    Write-Info "Task: $Task"
    if ($ContextFile) { Write-Info "Context: $ContextFile" }
    Write-Info "Iterations: $Iterations"

    $args = Build-PythonArgs -Mode "single" -Agent $Agent -Task $Task -ContextFile $ContextFile -Iterations $Iterations -NoSave $NoSave
    return Invoke-PythonRunner $args
}

function Start-Delegation {
    param([string]$Task, [string]$ContextFile)

    if (-not $Task) {
        Write-Error "Task is required for delegation mode"
        return $false
    }

    Write-Header "Delegation Mode (claude-agents.json)"
    Write-Info "Task: $Task"
    if ($ContextFile) { Write-Info "Context: $ContextFile" }

    $args = Build-PythonArgs -Mode "delegation" -Task $Task -ContextFile $ContextFile
    return Invoke-PythonRunner $args
}

function Start-CompleteAnalysis {
    param([string]$ContextFile)

    Write-Header "Complete Trading Analysis"
    if ($ContextFile) { Write-Info "Context: $ContextFile" }

    $args = Build-PythonArgs -Mode "complete" -ContextFile $ContextFile
    return Invoke-PythonRunner $args
}

function Start-BatchMode {
    param([string]$TasksFile)

    if (-not $TasksFile) {
        Write-Error "TasksFile is required for batch mode"
        return $false
    }

    if (-not (Test-Path $TasksFile)) {
        Write-Error "Tasks file not found: $TasksFile"
        return $false
    }

    Write-Header "Batch Mode"
    Write-Info "Tasks file: $TasksFile"

    $args = Build-PythonArgs -Mode "batch" -TasksFile $TasksFile
    return Invoke-PythonRunner $args
}

function Start-AutonomousLoop {
    param([int]$IntervalSeconds, [int]$MaxIterations, [string]$ContextFile)

    Write-Header "Autonomous Loop Mode"
    Write-Info "Interval: $IntervalSeconds seconds"
    if ($MaxIterations -gt 0) { Write-Info "Max Iterations: $MaxIterations" }
    if ($ContextFile) { Write-Info "Context: $ContextFile" }
    Write-Info "Press Ctrl+C to stop"

    $args = Build-PythonArgs -Mode "autonomous" -IntervalSeconds $IntervalSeconds -MaxIterations $MaxIterations -ContextFile $ContextFile
    return Invoke-PythonRunner $args
}

# ============================================================================
# Script principal
# ============================================================================

try {
    Write-Header "NOVAQUOTE Claude Code Agents"
    Write-Info "Mode: $Mode"
    Write-Info "Project Path: $ProjectRoot"

    # Vérifier les prérequis
    Test-Prerequisites

    # Exécuter selon le mode
    $success = $false

    switch ($Mode) {
        "single" {
            $success = Start-SingleAgent -Agent $Agent -Task $Task -ContextFile $ContextFile -Iterations $Iterations -NoSave $NoSave
        }
        "delegation" {
            $success = Start-Delegation -Task $Task -ContextFile $ContextFile
        }
        "complete" {
            $success = Start-CompleteAnalysis -ContextFile $ContextFile
        }
        "batch" {
            $success = Start-BatchMode -TasksFile $TasksFile
        }
        "autonomous" {
            $success = Start-AutonomousLoop -IntervalSeconds $IntervalSeconds -MaxIterations $MaxIterations -ContextFile $ContextFile
        }
    }

    if ($success) {
        Write-Header "Execution Completed Successfully"
        exit 0
    }
    else {
        Write-Header "Execution Failed"
        exit 1
    }
}
catch {
    Write-Error "Unexpected error: $_"
    Write-Info $_.ScriptStackTrace
    exit 1
}

# ============================================================================
# Exemples d'utilisation (commentés)
# ============================================================================

<#

# Exemple 1: Agent unique
.\claude_code_agents.ps1 -Mode single -Agent "claude-strategy-advisor" -Task "Analyze BTC trading opportunity" -Iterations 3

# Exemple 2: Délégation
.\claude_code_agents.ps1 -Mode delegation -Task "Should I buy BTC at $50,000?" -ContextFile "market_data.json"

# Exemple 3: Analyse complète
.\claude_code_agents.ps1 -Mode complete

# Exemple 4: Batch
.\claude_code_agents.ps1 -Mode batch -TasksFile "tasks.json"

# Exemple 5: Boucle autonome (5 minutes, 10 itérations max)
.\claude_code_agents.ps1 -Mode autonomous -IntervalSeconds 300 -MaxIterations 10

# Exemple 6: Boucle autonome (15 minutes, illimité)
.\claude_code_agents.ps1 -Mode autonomous -IntervalSeconds 900

# Exemple 7: Sans sauvegarde
.\claude_code_agents.ps1 -Mode single -Agent "claude-risk-advisor" -Task "Assess risk" -NoSave

# Exemple 8: Avec contexte personnalisé
.\claude_code_agents.ps1 -Mode complete -ContextFile "my_context.json"

#>
