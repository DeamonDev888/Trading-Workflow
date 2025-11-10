@echo off
if "%1"=="" goto help

if "%1"=="bug" (
    claude --agents .claude/agents/novaquote-bug-fixer.json --print --dangerously-skip-permissions "%~2"
    goto end
)
if "%1"=="review" (
    claude --agents .claude/agents/novaquote-code-reviewer.json --print --dangerously-skip-permissions "%~2"
    goto end
)
if "%1"=="docs" (
    claude --agents .claude/agents/novaquote-docs-generator.json --print --dangerously-skip-permissions "%~2"
    goto end
)
if "%1"=="perf" (
    claude --agents .claude/agents/novaquote-perf-optimizer.json --print --dangerously-skip-permissions "%~2"
    goto end
)
if "%1"=="test" (
    claude --agents .claude/agents/novaquote-test-enhancer.json --print --dangerously-skip-permissions "%~2"
    goto end
)
if "%1"=="all" (
    echo 🔍 Analyse complete...
    claude --agents @claude-agents.json --print --dangerously-skip-permissions "Analyse complete du systeme"
    goto end
)

:help
echo Usage: novaquote-quick.bat [agent] [task]
echo.
echo Agents disponibles:
echo   bug     - Bug Fixer
echo   review  - Code Reviewer
echo   docs    - Documentation Generator
echo   perf    - Performance Optimizer
echo   test    - Test Enhancer
echo   all     - Analyse complete
echo.
echo Exemples:
echo   novaquote-quick.bat bug "Fix import errors"
echo   novaquote-quick.bat review "Security audit"
echo   novaquote-quick.bat all "Complete analysis"

:end