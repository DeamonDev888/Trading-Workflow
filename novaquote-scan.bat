@echo off
echo 🔍 Lancement scan automatique NOVAQUOTE...
echo 📅 Date: %date% %time%
echo.

:: Créer répertoire de rapports
if not exist "reports" mkdir reports

set REPORT_FILE=reports\novaquote-scan-%date:~-4,4%%date:~-7,2%%date:~-10,2%.txt

echo Rapport de scan NOVAQUOTE > %REPORT_FILE%
echo ================================ >> %REPORT_FILE%
echo Date: %date% %time% >> %REPORT_FILE%
echo. >> %REPORT_FILE%

echo 🐛 Etape 1: Bug Fixer...
echo [Bug Fixer] Analyse des bugs... >> %REPORT_FILE%
claude --agents .claude/agents/novaquote-bug-fixer.json --print --dangerously-skip-permissions "Analyse complete du codebase pour bugs et erreurs" >> %REPORT_FILE% 2>&1

echo.
echo 🔒 Etape 2: Code Reviewer...
echo [Code Reviewer] Audit de securite... >> %REPORT_FILE%
claude --agents .claude/agents/novaquote-code-reviewer.json --print --dangerously-skip-permissions "Audit securite complete du systeme" >> %REPORT_FILE% 2>&1

echo.
echo ⚡ Etape 3: Performance Optimizer...
echo [Performance] Optimisation... >> %REPORT_FILE%
claude --agents .claude/agents/novaquote-perf-optimizer.json --print --dangerously-skip-permissions "Optimisation performances" >> %REPORT_FILE% 2>&1

echo.
echo ✅ Scan termine ! Rapport sauvegarde dans: %REPORT_FILE%
echo.
pause