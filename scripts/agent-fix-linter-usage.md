# 🔧 Guide d'Utilisation - Agent Fix Linter

## 🚀 Utilisation Rapide

### 1. **Correction Complète**
```bash
node scripts/agent-fix-linter.js
```
→ Scanne tout le projet et corrige automatiquement les erreurs "faciles"

### 2. **Correction Python Seulement**
```bash
node scripts/agent-fix-linter.js --python
```

### 3. **Correction TypeScript/JavaScript Seulement**
```bash
node scripts/agent-fix-linter.js --typescript
# ou
node scripts/agent-fix-linter.js --js
```

### 4. **Correction Ciblée**
```bash
node scripts/agent-fix-linter.js --target "src/models"
```

### 5. **Limiter le Nombre d'Itérations**
```bash
node scripts/agent-fix-linter.js --max-iterations 5
```

## 📋 Exemples Concrets

### Exemple 1: Nettoyage Automatique
```bash
# Commande
node scripts/agent-fix-linter.js

# Résultat attendu
✅ Auto-fix: backtest_validator.js:24 - MISSING_SEMICOLON
✅ Auto-fix: portfolio-manager.js:45 - UNUSED_IMPORT
✅ Auto-fix: config.html:12 - CONSOLE_LOG
📊 15 problèmes corrigés automatiquement
```

### Exemple 2: Focus Python
```bash
# Commande
node scripts/agent-fix-linter.js --python

# Résultat attendu
✅ Auto-fix: user_model.py:5 - UNUSED_IMPORT
✅ Auto-fix: helpers.py:23 - UNUSED_VARIABLE
📊 8 problèmes Python corrigés automatiquement
```

### Exemple 3: Ciblage Fichier
```bash
# Commande
node scripts/agent-fix-linter.js --target "backend"

# Résultat attendu
✅ Auto-fix: backend/server.js:15 - MISSING_SEMICOLON
✅ Auto-fix: backend/validator.js:8 - CONSOLE_LOG
📊 5 problèmes dans backend/ corrigés automatiquement
```

## 🎯 Ce que l'Agent Corrige Automatiquement

### ✅ Auto-Fixé (Sans Confirmation)
- **Imports non utilisés** - Commenté ou supprimé
- **Points-virgules manquants** - Ajouté automatiquement
- **console.log en production** - Commenté
- **Erreurs de syntaxe évidentes** - Parenthèses/accolades
- **Print statements** - Commenté

### ❌ Nécessite Confirmation Manuelle
- **Changements de logique** - Trop risqués
- **Modifications d'API** - Peut casser le code
- **Refactoring** - Impact trop important
- **Corrections complexes** - À évaluer au cas par cas

## 📊 Progression et Logs

### Début
```
🔧 NOVAQUOTE Lint & Fix Agent - Démarrage
📋 Objectif: Scan complet
⏰ Timeout: 10 itérations
```

### Progression
```
🔄 Itération 1/10
📊 Erreurs: 25, Warnings: 143
✅ Auto-fix: src/models/user.py:5 - UNUSED_IMPORT
✅ Auto-fix: src/models/user.py:8 - UNUSED_IMPORT
📝 12 problèmes corrigés automatiquement

🔄 Itération 2/10
📊 Erreurs: 13, Warnings: 89
...
```

### Fin (Succès)
```
✅ SUCCÈS: 0 erreur, 0 warning - Code parfait!
📋 RAPPORT FINAL
   ✅ Auto-corrigées: 187
   ⚠️  Manuelles (complexes): 23
   🔄 Itérations: 4
```

### Fin (Timeout)
```
⚠️  Progression nulle - Arrêt
📋 RAPPORT FINAL
   ✅ Auto-corrigées: 145
   ⚠️  Manuelles (complexes): 45
   🔄 Itérations: 10
```

## 🔍 Workflow de l'Agent

```
1. Scan Initial
   ↓
2. Parsing des erreurs
   ↓
3. Classification (auto-fixable vs manuel)
   ↓
4. Corrections auto
   ↓
5. Re-scan
   ↓
6. Progression? OUI → Retour à l'étape 1
           NON → Arrêt
```

## ⚙️ Options Avancées

| Option | Description | Exemple |
|--------|-------------|---------|
| `--python` | Scanner seulement Python | `node agent-fix-linter.js --python` |
| `--typescript` | Scanner seulement TS/JS | `node agent-fix-linter.js --typescript` |
| `--target PATH` | Cibler un répertoire | `node agent-fix-linter.js --target "src"` |
| `--max-iterations N` | Limiter les itérations | `node agent-fix-linter.js --max-iterations 5` |

## 🛡️ Sécurité

### Protections Intégrées
- ✅ **Commentaire au lieu de suppression** - Plus sûr
- ✅ **Pas de modification destructive** - Vérification avant écriture
- ✅ **Progression surveillée** - Arrêt si pas de progrès
- ✅ **Itération limitée** - Maximum 10 cycles
- ✅ **Validation syntaxique** - Après chaque correction

### Rollback Manual
Si une correction automatique pose problème:
```bash
# Voir le git diff
git diff

# Rollback si nécessaire
git checkout -- .
```

## 📈 Optimisations

### Réduire les Faux Positifs
Le scanner est déjà optimisé pour réduire les faux positifs:
- Flake8 configuré (`.flake8`)
- Vérifications internes désactivées
- Seules les vraies erreurs détectées

### Pour de Meilleurs Résultats
1. **Scan régulier**: Exécuter l'agent après chaque commit
2. **Petit à petit**: Corriger par petite partie (ex: `--target "src/models"`)
3. **Revue manuelle**: Vérifier les corrections avant de pusher

## 🆘 Dépannage

### Erreur: "Commandes non trouvées"
```bash
# Installer les dépendances
npm install
# ou
pip install flake8 pylint
```

### Erreur: "Permission refusée"
```bash
# Donner les permissions
chmod +x scripts/agent-fix-linter.js
```

### Agent s'arrête sans progresser
- **Cause**: Erreurs trop complexes
- **Solution**: Corriger manuellement les erreurs signalées, puis relancer l'agent

## 💡 Conseils

1. **Commencer par un scan sans correction**
   ```bash
   node scripts/scan/novaquote-complete-scan.js
   ```

2. **Corriger par étapes**
   ```bash
   # Étape 1: Python seulement
   node scripts/agent-fix-linter.js --python

   # Étape 2: TypeScript seulement
   node scripts/agent-fix-linter.js --typescript
   ```

3. **Vérifier après chaque session**
   ```bash
   git diff
   git status
   ```

---

## 🎯 Utilisation Recommandée

### Avant un Commit
```bash
# 1. Scanner
node scripts/scan/novaquote-complete-scan.js

# 2. Si problèmes → Corriger
node scripts/agent-fix-linter.js

# 3. Vérifier
git diff

# 4. Commit
git add .
git commit -m "Clean code: lint fixes"
```

### Nettoyage Hebdomadaire
```bash
# Correction complète du projet
node scripts/agent-fix-linter.js --max-iterations 15
```

