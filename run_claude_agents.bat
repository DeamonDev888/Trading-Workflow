@echo off
REM ============================================================================
REM [OK] NOVAQUOTE Claude Code Agents - Windows Batch Runner
REM Built with love by Deamon Dev [ROCKET]
REM Pattern: claude --agents @.claude/agents/ avec script batch
REM ============================================================================

setlocal enabledelayedexpansion

REM Configuration
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%"
set "PYTHON_SCRIPT=%SCRIPT_DIR%scripts\claude_code_agent_runner.py"
set "PYTHON_EXE=python"

REM Couleurs (Windows 10+)
color 0B

echo.
echo  ============================================================================
echo   🚀 NOVAQUOTE CLAUDE CODE AGENTS
echo  ============================================================================
echo.

REM Vérifier Python
echo [1/4] Checking Python...
%PYTHON_EXE% --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8+
    echo    Download: https://python.org
    pause
    exit /b 1
)
echo ✅ Python found
echo.

REM Vérifier le script
echo [2/4] Checking script files...
if not exist "%PYTHON_SCRIPT%" (
    echo ❌ Script not found: %PYTHON_SCRIPT%
    pause
    exit /b 1
)
echo ✅ Script found
echo.

REM Afficher le menu
echo [3/4] Select mode:
echo.
echo   1. Single Agent (one specific agent)
echo   2. Delegation (auto-select agent)
echo   3. Complete Analysis (all agents)
echo   4. Batch Processing (multiple tasks)
echo   5. Autonomous Loop (continuous)
echo   6. Run Tests
echo.
set /p "mode_choice=Enter choice (1-6): "

if "%mode_choice%"=="1" goto SINGLE_AGENT
if "%mode_choice%"=="2" goto DELEGATION
if "%mode_choice%"=="3" goto COMPLETE
if "%mode_choice%"=="4" goto BATCH
if "%mode_choice%"=="5" goto AUTONOMOUS
if "%mode_choice%"=="6" goto RUN_TESTS

echo ❌ Invalid choice
pause
exit /b 1

REM ============================================================================
REM Mode 1: Agent Unique
REM ============================================================================
:SINGLE_AGENT
echo.
echo [4/4] Single Agent Mode
echo.
echo Available agents:
echo   1. claude-strategy-advisor
echo   2. claude-risk-advisor
echo   3. claude-funding-advisor
echo   4. claude-sentiment-analyzer
echo.
set /p "agent_choice=Select agent (1-4): "

if "%agent_choice%"=="1" set "AGENT_ID=claude-strategy-advisor"
if "%agent_choice%"=="2" set "AGENT_ID=claude-risk-advisor"
if "%agent_choice%"=="3" set "AGENT_ID=claude-funding-advisor"
if "%agent_choice%"=="4" set "AGENT_ID=claude-sentiment-analyzer"

if "!AGENT_ID!"=="" (
    echo ❌ Invalid agent
    pause
    exit /b 1
)

set /p "task=Enter task description: "
set /p "iterations=Iterations (default 3): "
if "!iterations!"=="" set "iterations=3"

echo.
echo 🚀 Running: !AGENT_ID!
echo    Task: !task!
echo    Iterations: !iterations!
echo.

%PYTHON_EXE% "%PYTHON_SCRIPT%" --mode single --agent "!AGENT_ID!" --task "!task!" --iterations !iterations!
goto END

REM ============================================================================
REM Mode 2: Délégation
REM ============================================================================
:DELEGATION
echo.
echo [4/4] Delegation Mode
echo.
set /p "task=Enter task description: "

echo.
echo 🚀 Delegating to appropriate agent(s)...
echo.

%PYTHON_EXE% "%PYTHON_SCRIPT%" --mode delegation --task "!task!"
goto END

REM ============================================================================
REM Mode 3: Analyse Complète
REM ============================================================================
:COMPLETE
echo.
echo [4/4] Complete Analysis Mode
echo.
set /p "context_file=Context file (or press Enter for default): "

if "!context_file!"=="" (
    %PYTHON_EXE% "%PYTHON_SCRIPT%" --mode complete
) else (
    %PYTHON_EXE% "%PYTHON_SCRIPT%" --mode complete --context "!context_file!"
)
goto END

REM ============================================================================
REM Mode 4: Batch
REM ============================================================================
:BATCH
echo.
echo [4/4] Batch Mode
echo.
echo Default: examples\tasks_batch.json
set /p "tasks_file=Tasks file: "

if "!tasks_file!"=="" set "tasks_file=examples\tasks_batch.json"

if not exist "!tasks_file!" (
    echo ❌ File not found: !tasks_file!
    pause
    exit /b 1
)

echo 🚀 Running batch: !tasks_file!
echo.

%PYTHON_EXE% "%PYTHON_SCRIPT%" --mode batch --tasks-file "!tasks_file!"
goto END

REM ============================================================================
REM Mode 5: Boucle Autonome
REM ============================================================================
:AUTONOMOUS
echo.
echo [4/4] Autonomous Loop Mode
echo.
set /p "interval=Interval in seconds (default 300): "
if "!interval!"=="" set "interval=300"

set /p "max_iter=Max iterations (or press Enter for unlimited): "

if "!max_iter!"=="" (
    echo 🚀 Starting autonomous loop (interval: !interval!s, unlimited)
    %PYTHON_EXE% "%PYTHON_SCRIPT%" --mode autonomous --interval !interval!
) else (
    echo 🚀 Starting autonomous loop (interval: !interval!s, max: !max_iter!)
    %PYTHON_EXE% "%PYTHON_SCRIPT%" --mode autonomous --interval !interval! --max-iterations !max_iter!
)
goto END

REM ============================================================================
REM Mode 6: Tests
REM ============================================================================
:RUN_TESTS
echo.
echo [4/4] Running Test Suite
echo.
echo 🚀 Starting integration tests...
echo.

%PYTHON_EXE% "%SCRIPT_DIR%scripts\test_claude_code_integration.py"

if errorlevel 1 (
    echo.
    echo ❌ Some tests failed
) else (
    echo.
    echo ✅ All tests passed
)
goto END

REM ============================================================================
REM Fin
REM ============================================================================
:END
echo.
echo ============================================================================
echo   ✅ Operation completed
echo ============================================================================
echo.
echo Reports saved in: %PROJECT_ROOT%\reports\
echo.
pause
exit /b 0
