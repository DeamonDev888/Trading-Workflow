# 📊 Scripts de Scan NOVAQUOTE

Collection complète de scripts pour détecter et analyser les erreurs dans les projets TypeScript, JavaScript et Python.

## 🎯 Objectif

Ces scripts scannent automatiquement vos fichiers de code pour identifier :
- ❌ Erreurs de syntaxe
- ⚠️ Avertissements de style
- 🔍 Problèmes potentiels
- 📈 Métriques de qualité

## 📁 Structure des Scripts

```
scripts/scan/
├── novaquote-complete-scan.js    # Scanner unifié principal
├── scan-typescript-javascript.js # Scanner TS/JS spécialisé
├── scan-python.py               # Scanner Python spécialisé
├── README.md                    # Documentation (ce fichier)
└── reports/                     # Répertoire des rapports générés
    └── scan-report-*.md         # Rapports Markdown
```

## 🚀 Utilisation Rapide

### Scanner Complet (Recommandé)

```bash
# Scanner le projet actuel
node scripts/scan/novaquote-complete-scan.js

# Scanner un répertoire spécifique
node scripts/scan/novaquote-complete-scan.js ./mon-projet

# Scanner sans inclure les avertissements
node scripts/scan/novaquote-complete-scan.js --no-warnings

# Spécifier un répertoire de sortie personnalisé
node scripts/scan/novaquote-complete-scan.js --output ./mes-rapports
```

### Scripts Individuels

#### TypeScript/JavaScript
```bash
node scripts/scan/scan-typescript-javascript.js
```

#### Python
```bash
python scripts/scan/scan-python.py
```

## 📊 Rapports Générés

Les scans génèrent des rapports Markdown détaillés dans le répertoire `reports/` avec :

### 📋 Contenu du Rapport

1. **Résumé Global**
   - Nombre de fichiers scannés
   - Total des erreurs et avertissements
   - Score de qualité du code

2. **Analyse par Langage**
   - TypeScript/JavaScript
   - Python

3. **Détail des Problèmes**
   - Tableau structuré avec fichier, ligne, type et message
   - Groupement par type de problème

4. **Recommandations**
   - Actions prioritaires
   - Bonnes pratiques
   - Suggestions d'amélioration

### 📈 Score de Qualité

- 🟢 **90-100%**: Excellent - Code de très haute qualité
- 🟡 **70-89%**: Bon - Améliorations mineures possibles
- 🟠 **50-69%**: Moyen - Révision nécessaire
- 🔴 **0-49%**: Faible - Attention immédiate requise

## 🔧 Types de Détection

### TypeScript/JavaScript

#### Erreurs Critiques
- Erreurs de syntaxe
- Imports/exports invalides
- Variables non déclarées
- Erreurs TypeScript

#### Avertissements
- console.log en production
- Variables non utilisées
- utilisation de `var`
- Lignes trop longues

#### Outils Externes
- **ESLint**: Si configuré dans le projet
- **TypeScript Compiler**: Si `tsconfig.json` présent

### Python

#### Erreurs Critiques
- Erreurs de syntaxe Python
- Imports invalides
- Exceptions non gérées

#### Avertissements
- `print()` en production
- Docstrings manquants
- Fonctions trop longues
- Variables non utilisées

#### Outils Externes
- **flake8**: Style et erreurs
- **pylint**: Analyse statique avancée
- **black**: Vérification du formatage
- **mypy**: Vérification des types

## ⚙️ Configuration

### Variables d'Environnement

```bash
# Répertoire de sortie des rapports
export NOVAQUOTE_REPORTS_DIR="./custom-reports"

# Inclure/exclure les avertissements
export NOVAQUOTE_INCLUDE_WARNINGS="true"
```

### Fichier de Configuration (optionnel)

Créez `novaquote-scan.config.json` à la racine:

```json
{
  "outputDir": "./reports",
  "includeWarnings": true,
  "includeInfo": false,
  "excludePatterns": [
    "node_modules/**",
    "dist/**",
    "**/*.min.js",
    "**/*.test.*"
  ],
  "rules": {
    "typescript": {
      "maxLineLength": 120,
      "checkConsoleLog": true
    },
    "python": {
      "maxLineLength": 88,
      "checkDocstrings": true,
      "maxFunctionLength": 50
    }
  }
}
```

## 🔍 Intégration CI/CD

### GitHub Actions

```yaml
name: Code Quality Scan
on: [push, pull_request]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '16'
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          npm install
          pip install flake8 pylint black mypy

      - name: Run NovaQuote Scan
        run: node scripts/scan/novaquote-complete-scan.js

      - name: Upload Report
        uses: actions/upload-artifact@v2
        with:
          name: scan-report
          path: reports/
```

### Pre-commit Hooks

```bash
# Installer husky
npm install --save-dev husky

# Configurer le hook
npx husky add .husky/pre-commit "node scripts/scan/novaquote-complete-scan.js"
```

## 🛠️ Développement

### Architecture

```
Scanner Principal (novaquote-complete-scan.js)
├── Scanner TypeScript/JavaScript
│   ├── Analyse syntaxique AST
│   ├── Détection de patterns
│   └── Intégration ESLint/TSC
└── Scanner Python
    ├── Analyse syntaxique AST
    ├── Vérifications PEP 8
    └── Intégration flake8/pylint
```

### Extensions

Pour ajouter un nouveau type de détection:

1. **Créer une méthode de détection** dans le scanner approprié
2. **Ajouter le type d'erreur** dans les constantes
3. **Mettre à jour le template de rapport** si nécessaire

Exemple pour TypeScript:

```javascript
checkNewFeature(filePath, content) {
    // Votre logique de détection
    if (problemDetected) {
        this.addError(filePath, 'NEW_FEATURE_TYPE', 'Message d\'erreur', lineNumber);
    }
}
```

## 📝 Personnalisation

### Ajouter des Règles Personnalisées

Créez `custom-rules.js`:

```javascript
module.exports = {
    typescript: {
        rules: {
            'no-magic-numbers': {
                severity: 'warning',
                check: (content) => {
                    // Logique de détection
                }
            }
        }
    },
    python: {
        rules: {
            'no-hardcoded-passwords': {
                severity: 'error',
                check: (content) => {
                    // Logique de détection
                }
            }
        }
    }
};
```

### Templates de Rapport Personnalisés

Modifiez la méthode `generateMarkdownReport()` dans `novaquote-complete-scan.js` pour personnaliser le format de sortie.

## 🐛 Dépannage

### Problèmes Communs

#### Erreur: "Python non disponible"
```bash
# Installer Python
# Windows: Télécharger depuis python.org
# macOS: brew install python
# Linux: sudo apt install python3
```

#### Erreur: "ESLint non trouvé"
```bash
# Installer ESLint localement
npm install --save-dev eslint
```

#### Erreur: "flake8 non trouvé"
```bash
# Installer flake8
pip install flake8
```

### Mode Debug

```bash
# Activer le mode debug
DEBUG=true node scripts/scan/novaquote-complete-scan.js
```

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## 🤝 Contribution

Les contributions sont bienvenues! Veuillez:

1. Forker le projet
2. Créer une branche de fonctionnalité
3. Committer vos changements
4. Pousser vers la branche
5. Créer une Pull Request

## 📞 Support

Pour toute question ou problème:

- Créer une issue sur GitHub
- Contacter l'équipe de développement
- Consulter la documentation du projet

---

**Développé avec ❤️ pour l'écosystème NOVAQUOTE**