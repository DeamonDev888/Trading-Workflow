@echo off
echo === AGENTS NOVAQUOTE - Lancement Rapide ===
echo.
echo 1. Bug Fixer - Analyser et corriger les bugs
echo 2. Code Reviewer - Revoir la qualite du code
echo 3. Doc Generator - Generer la documentation
echo 4. Performance Optimizer - Optimiser les performances
echo 5. Test Enhancer - Ameliorer la couverture de tests
echo.
set /p choice="Choisissez un agent (1-5): "

if "%choice%"=="1" (
    echo Lancement du Bug Fixer...
    claude --agents "{\"novaquote-bug-fixer\": {\"description\": \"Auto Bug Fixer for NOVAQUOTE\", \"prompt\": \"MISSION: Scan, analyze and fix code issues in the NOVAQUOTE project.\", \"model\": \"sonnet\", \"tools\": [\"Read\", \"Edit\", \"Bash\", \"Grep\", \"Glob\"]}}" --print --dangerously-skip-permissions "Analyser les bugs dans le codebase NOVAQUOTE"
)
if "%choice%"=="2" (
    echo Lancement du Code Reviewer...
    claude --agents "{\"novaquote-code-reviewer\": {\"description\": \"Code reviewer for NOVAQUOTE\", \"prompt\": \"Review code quality and suggest improvements.\", \"model\": \"sonnet\", \"tools\": [\"Read\", \"Grep\", \"Bash\"]}}" --print --dangerously-skip-permissions "Revoir la qualite du code NOVAQUOTE"
)
if "%choice%"=="3" (
    echo Lancement du Doc Generator...
    claude --agents "{\"novaquote-docs-generator\": {\"description\": \"Documentation generator for NOVAQUOTE\", \"prompt\": \"Generate comprehensive documentation.\", \"model\": \"sonnet\", \"tools\": [\"Read\", \"Write\", \"Glob\"]}}" --print --dangerously-skip-permissions "Generer la documentation NOVAQUOTE"
)
if "%choice%"=="4" (
    echo Lancement du Performance Optimizer...
    claude --agents "{\"novaquote-perf-optimizer\": {\"description\": \"Performance optimizer for NOVAQUOTE\", \"prompt\": \"Optimize code performance.\", \"model\": \"sonnet\", \"tools\": [\"Read\", \"Edit\", \"Bash\", \"Grep\"]}}" --print --dangerously-skip-permissions "Optimiser les performances NOVAQUOTE"
)
if "%choice%"=="5" (
    echo Lancement du Test Enhancer...
    claude --agents "{\"novaquote-test-enhancer\": {\"description\": \"Test enhancer for NOVAQUOTE\", \"prompt\": \"Enhance test coverage.\", \"model\": \"sonnet\", \"tools\": [\"Read\", \"Write\", \"Grep\", \"Glob\"]}}" --print --dangerously-skip-permissions "Ameliorer les tests NOVAQUOTE"
)

pause