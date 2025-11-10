@echo off
echo.
echo ===============================================
echo  🌍 SWARM INTELLIGENCE - INITIALISATION
echo  Construire votre armée d'agents en 20 min
echo ===============================================
echo.

REM Vérifier si Node.js est installé
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js requis! Installez-le depuis: https://nodejs.org
    pause
    exit /b 1
)

REM Vérifier si le fichier de config existe
if not exist "claude-agents.json" (
    echo ❌ Fichier claude-agents.json manquant!
    echo 💡 Utilisez le template dans docs/SWARM_AGENTS_GUIDE.md
    pause
    exit /b 1
)

REM Lancer le script Node.js
echo 🚀 Lancement du Swarm Launcher...
echo.
node scripts/launch-swarm.js

echo.
echo ✅ Opération terminée!
pause
