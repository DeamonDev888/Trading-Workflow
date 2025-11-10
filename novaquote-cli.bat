@echo off
setlocal enabledelayedexpansion

echo ====================================
echo     NOVAQUOTE AGENTS CLI v1.0
echo ====================================
echo.

:menu
echo Choisissez l'agent NOVAQUOTE:
echo 1) Bug Fixer - Correction de bugs
echo 2) Code Reviewer - Audit de securite
echo 3) Documentation Generator - Documentation
echo 4) Performance Optimizer - Optimisation
echo 5) Test Enhancer - Tests
echo 6) Analyse Complete - Tous les agents
echo 7) Exit
echo.
set /p choice="Votre choix (1-7): "

if "%choice%"=="1" goto bug-fixer
if "%choice%"=="2" goto code-reviewer
if "%choice%"=="3" goto docs-generator
if "%choice%"=="4" goto perf-optimizer
if "%choice%"=="5" goto test-enhancer
if "%choice%"=="6" goto complete-analysis
if "%choice%"=="7" goto exit
goto menu

:bug-fixer
echo.
set /p task="Tache pour Bug Fixer: "
echo 🐛 Execution Bug Fixer...
claude --agents .claude/agents/novaquote-bug-fixer.json --print --dangerously-skip-permissions "!task!"
pause
goto menu

:code-reviewer
echo.
set /p task="Tache pour Code Reviewer: "
echo 🔒 Execution Code Reviewer...
claude --agents .claude/agents/novaquote-code-reviewer.json --print --dangerously-skip-permissions "!task!"
pause
goto menu

:docs-generator
echo.
set /p task="Tache pour Documentation Generator: "
echo 📚 Execution Documentation Generator...
claude --agents .claude/agents/novaquote-docs-generator.json --print --dangerously-skip-permissions "!task!"
pause
goto menu

:perf-optimizer
echo.
set /p task="Tache pour Performance Optimizer: "
echo ⚡ Execution Performance Optimizer...
claude --agents .claude/agents/novaquote-perf-optimizer.json --print --dangerously-skip-permissions "!task!"
pause
goto menu

:test-enhancer
echo.
set /p task="Tache pour Test Enhancer: "
echo 🧪 Execution Test Enhancer...
claude --agents .claude/agents/novaquote-test-enhancer.json --print --dangerously-skip-permissions "!task!"
pause
goto menu

:complete-analysis
echo.
echo 🔍 Demarrage analyse complete du systeme...
echo 📅 Date: %date% %time%
echo ====================================
echo.

echo 🐛 Etape 1: Bug Fixer...
claude --agents .claude/agents/novaquote-bug-fixer.json --print --dangerously-skip-permissions "Analyse complete du codebase et correction des bugs critiques"

echo.
echo 🔒 Etape 2: Code Reviewer...
claude --agents .claude/agents/novaquote-code-reviewer.json --print --dangerously-skip-permissions "Audit de securite complet du systeme"

echo.
echo ⚡ Etape 3: Performance Optimizer...
claude --agents .claude/agents/novaquote-perf-optimizer.json --print --dangerously-skip-permissions "Optimisation des performances du systeme"

echo.
echo ✅ Analyse complete terminee !
pause
goto menu

:exit
echo Au revoir !
exit /b 0