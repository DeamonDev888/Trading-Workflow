#!/usr/bin/env node

/**
 * NOVAQUOTE - Scanner Complet Unifié
 * Scan tous les fichiers (TS, JS, Python) et génère un rapport Markdown
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Importer les scanners spécialisés
const TypeScriptJavaScriptScanner = require('./scan-typescript-javascript.js');

class NovaQuoteCompleteScanner {
    constructor() {
        this.reports = {
            typescript: null,
            python: null
        };
        this.config = {
            outputDir: path.join(process.cwd(), 'reports'),
            reportFileName: `scan-report-${this.getTimestamp()}.md`,
            includeWarnings: true,
            includeInfo: true
        };
    }

    /**
     * Scanner complet du projet
     */
    async scanCompleteProject(rootDir = process.cwd()) {
        console.log('🚀 Démarrage du scan complet NOVAQUOTE...');
        console.log(`📁 Répertoire: ${rootDir}`);
        console.log('━'.repeat(60));

        // Créer le répertoire de rapports
        this.ensureReportDirectory();

        const startTime = Date.now();

        try {
            // Scanner TypeScript/JavaScript
            console.log('\n📝 Scan TypeScript/JavaScript...');
            await this.scanTypeScriptJavaScript(rootDir);

            // Scanner Python
            console.log('\n🐍 Scan Python...');
            await this.scanPython(rootDir);

            // Générer le rapport Markdown
            console.log('\n📄 Génération du rapport...');
            const reportPath = await this.generateMarkdownReport();

            const endTime = Date.now();
            const duration = ((endTime - startTime) / 1000).toFixed(2);

            console.log('\n✅ Scan terminé avec succès!');
            console.log(`⏱️  Durée: ${duration} secondes`);
            console.log(`📊 Rapport généré: ${reportPath}`);

            // Afficher le résumé
            this.displaySummary();

            return {
                success: true,
                reportPath,
                duration,
                summary: this.getGlobalSummary()
            };

        } catch (error) {
            console.error('❌ Erreur lors du scan:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Scanner les fichiers TypeScript/JavaScript
     */
    async scanTypeScriptJavaScript(rootDir) {
        const scanner = new TypeScriptJavaScriptScanner();
        this.reports.typescript = await scanner.scanProject(rootDir);

        console.log(`   ✓ ${this.reports.typescript.summary.filesScanned} fichiers TS/JS scannés`);
        console.log(`   ⚠️  ${this.reports.typescript.summary.errorsFound} erreurs, ${this.reports.typescript.summary.warningsFound} avertissements`);
    }

    /**
     * Scanner les fichiers Python
     */
    async scanPython(rootDir) {
        try {
            // Vérifier si Python est disponible
            execSync('python --version', { stdio: 'ignore' });

            const pythonScript = path.join(__dirname, 'scan-python.py');
            const outputFile = path.join(rootDir, 'temp-python-scan-result.json');

            // Exécuter Python et sauvegarder le résultat dans un fichier
            execSync(`python "${pythonScript}" --timeout 30 --output-file "${outputFile}"`, {
                cwd: rootDir,
                stdio: 'inherit',
                timeout: 60000
            });

            // Lire le fichier de résultat
            if (fs.existsSync(outputFile)) {
                const resultContent = fs.readFileSync(outputFile, 'utf8');
                this.reports.python = JSON.parse(resultContent);
                fs.unlinkSync(outputFile); // Nettoyer le fichier temporaire
            } else {
                throw new Error('Fichier de résultat non généré');
            }

            const filesScanned = this.reports.python.summary.files_scanned || this.reports.python.summary.filesScanned || 0;
            const errorsFound = this.reports.python.summary.errors_found || this.reports.python.summary.errorsFound || 0;
            const warningsFound = this.reports.python.summary.warnings_found || this.reports.python.summary.warningsFound || 0;

            console.log(`   ✓ ${filesScanned} fichiers Python scannés`);
            console.log(`   ⚠️  ${errorsFound} erreurs, ${warningsFound} avertissements`);

        } catch (error) {
            console.warn('   ⚠️ Impossible de scanner les fichiers Python:', error.message);
            this.reports.python = {
                summary: {
                    filesScanned: 0,
                    errorsFound: 0,
                    warningsFound: 0,
                    scanDate: new Date().toISOString(),
                    scanner: 'Python Scanner (unavailable)'
                },
                issues: []
            };
        }
    }

    /**
     * Scanner seulement TypeScript/JavaScript
     */
    async scanTypeScriptOnly(config) {
        console.log('📝 Scan TypeScript/JavaScript uniquement...');
        const scanner = new TypeScriptJavaScriptScanner();
        this.reports.typescript = await scanner.scanProject(config.rootDir || process.cwd());

        console.log(`   ✓ ${this.reports.typescript.summary.filesScanned} fichiers TS/JS scannés`);
        console.log(`   ⚠️  ${this.reports.typescript.summary.errorsFound} erreurs, ${this.reports.typescript.summary.warningsFound} avertissements`);

        // Générer le rapport
        const reportPath = await this.generateMarkdownReport({ typescript: true, python: false });
        return {
            success: true,
            reportPath,
            summary: this.getTypeScriptSummary()
        };
    }

    /**
     * Scanner seulement Python
     */
    async scanPythonOnly(config) {
        console.log('🐍 Scan Python uniquement...');
        const pythonScript = path.join(__dirname, 'scan-python.py');
        const outputFile = path.join(process.cwd(), 'temp-python-scan-result.json');

        try {
            execSync(`python "${pythonScript}" --timeout 30 --output-file "${outputFile}"`, {
                cwd: config.rootDir || process.cwd(),
                stdio: 'inherit',
                timeout: 60000
            });

            if (fs.existsSync(outputFile)) {
                const resultContent = fs.readFileSync(outputFile, 'utf8');
                this.reports.python = JSON.parse(resultContent);
                fs.unlinkSync(outputFile);
            }

            const filesScanned = this.reports.python.summary.files_scanned || 0;
            const errorsFound = this.reports.python.summary.errors_found || 0;
            const warningsFound = this.reports.python.summary.warnings_found || 0;

            console.log(`   ✓ ${filesScanned} fichiers Python scannés`);
            console.log(`   ⚠️  ${errorsFound} erreurs, ${warningsFound} avertissements`);

            const reportPath = await this.generateMarkdownReport({ typescript: false, python: true });
            return {
                success: true,
                reportPath,
                summary: this.getPythonSummary()
            };
        } catch (error) {
            console.error('❌ Erreur lors du scan Python:', error.message);
            return { success: false, error: error.message };
        }
    }

    /**
     * Scanner un répertoire/fichier ciblé
     */
    async scanTargeted(config) {
        console.log(`🎯 Scan ciblé: ${config.targetPath || config.fileList.join(', ')}`);

        // Pour l'instant, utiliser le scan normal avec filtrage
        const result = await this.scanCompleteProject(config.rootDir || process.cwd(), config);

        // Appliquer les filtres
        result = this.applyFilters(result, config);

        console.log(`   ✓ Scan terminé avec filtres appliqués`);
        return result;
    }

    /**
     * Appliquer les filtres à un résultat
     */
    applyFilters(result, config) {
        if (!result.issues) return result;

        let filteredIssues = result.issues;

        // Filtre par sévérité
        if (config.severityFilter === 'errors') {
            filteredIssues = filteredIssues.filter(issue => issue.severity === 'error');
        } else if (config.severityFilter === 'warnings') {
            filteredIssues = filteredIssues.filter(issue => issue.severity === 'warning');
        }

        // Filtre par type
        if (config.typeFilter && config.typeFilter.length > 0) {
            filteredIssues = filteredIssues.filter(issue => config.typeFilter.includes(issue.type));
        }

        // Filtre par fichier (si fileList spécifié)
        if (config.fileList && config.fileList.length > 0) {
            filteredIssues = filteredIssues.filter(issue => {
                const fileName = path.basename(issue.filePath || issue.file_path);
                return config.fileList.includes(fileName);
            });
        }

        // Filtre par répertoire cible
        if (config.targetPath) {
            const targetPath = config.targetPath.toLowerCase();
            filteredIssues = filteredIssues.filter(issue => {
                const issuePath = (issue.filePath || issue.file_path || '').toLowerCase();
                return issuePath.includes(targetPath);
            });
        }

        result.issues = filteredIssues;
        return result;
    }

    /**
     * Obtenir le résumé TypeScript
     */
    getTypeScriptSummary() {
        if (!this.reports.typescript) return { files: 0, errors: 0, warnings: 0 };

        return {
            files: this.reports.typescript.summary.filesScanned,
            errors: this.reports.typescript.summary.errorsFound,
            warnings: this.reports.typescript.summary.warningsFound
        };
    }

    /**
     * Obtenir le résumé Python
     */
    getPythonSummary() {
        if (!this.reports.python) return { files: 0, errors: 0, warnings: 0 };

        return {
            files: this.reports.python.summary.files_scanned || 0,
            errors: this.reports.python.summary.errors_found || 0,
            warnings: this.reports.python.summary.warnings_found || 0
        };
    }

    /**
     * Générer le rapport Markdown (mis à jour pour accepter config)
     */
    async generateMarkdownReport(sectionConfig = { typescript: true, python: true }) {
        const reportPath = path.join(this.config.outputDir, this.config.reportFileName);

        let markdown = this.generateMarkdownHeader();
        markdown += this.generateGlobalSummary();
        markdown += this.generateTypeScriptSection();
        markdown += this.generatePythonSection();
        markdown += this.generateDetailedIssues();
        markdown += this.generateRecommendations();
        markdown += this.generateMarkdownFooter();

        fs.writeFileSync(reportPath, markdown, 'utf8');
        return reportPath;
    }

    /**
     * Générer l'en-tête Markdown
     */
    generateMarkdownHeader() {
        const timestamp = new Date().toLocaleString('fr-FR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });

        return `# 📊 Rapport de Scan Complet NOVAQUOTE

**Date**: ${timestamp}
**Scanner**: NovaQuote Complete Scanner v1.0
**Projet**: ${path.basename(process.cwd())}

---

`;
    }

    /**
     * Générer le résumé global
     */
    generateGlobalSummary() {
        const summary = this.getGlobalSummary();

        let section = `## 📈 Résumé Global

| Métrique | TypeScript/JS | Python | Total |
|----------|---------------|--------|-------|
| 📁 Fichiers scannés | ${summary.ts.files} | ${summary.py.files} | **${summary.total.files}** |
| ❌ Erreurs | ${summary.ts.errors} | ${summary.py.errors} | **${summary.total.errors}** |
| ⚠️ Avertissements | ${summary.ts.warnings} | ${summary.py.warnings} | **${summary.total.warnings}** |
| 🔍 Total des problèmes | ${summary.ts.total} | ${summary.py.total} | **${summary.total.total}** |

`;

        // Indicateur de qualité
        const qualityScore = this.calculateQualityScore();
        let qualityEmoji = '🟢';
        if (qualityScore < 50) qualityEmoji = '🔴';
        else if (qualityScore < 80) qualityEmoji = '🟡';

        section += `
### 🎯 Score de Qualité du Code

${qualityEmoji} **${qualityScore.toFixed(1)}%** - ${this.getQualityMessage(qualityScore)}

`;

        return section;
    }

    /**
     * Générer la section TypeScript/JavaScript
     */
    generateTypeScriptSection() {
        if (!this.reports.typescript) return '';

        const report = this.reports.typescript;
        const section = `## 💻 TypeScript / JavaScript

**Scanner**: ${report.summary.scanner}
**Date**: ${new Date(report.summary.scanDate).toLocaleString('fr-FR')}

### 📊 Statistiques
- **Fichiers scannés**: ${report.summary.filesScanned}
- **Erreurs trouvées**: ${report.summary.errorsFound}
- **Avertissements trouvés**: ${report.summary.warningsFound}

`;

        if (report.summary.errorsFound > 0 || report.summary.warningsFound > 0) {
            return section + this.generateIssuesTable(report.issues, 'TS/JS');
        }

        return section + '✅ **Aucun problème détecté dans les fichiers TypeScript/JavaScript**\n\n';
    }

    /**
     * Générer la section Python
     */
    generatePythonSection() {
        if (!this.reports.python) return '';

        const report = this.reports.python;
        const section = `## 🐍 Python

**Scanner**: ${report.summary.scanner}
**Date**: ${new Date(report.summary.scanDate).toLocaleString('fr-FR')}

### 📊 Statistiques
- **Fichiers scannés**: ${report.summary.files_scanned || report.summary.filesScanned}
- **Erreurs trouvées**: ${report.summary.errors_found || report.summary.errorsFound}
- **Avertissements trouvés**: ${report.summary.warnings_found || report.summary.warningsFound}

`;

        const errors = report.summary.errors_found || report.summary.errorsFound;
        const warnings = report.summary.warnings_found || report.summary.warningsFound;

        if (errors > 0 || warnings > 0) {
            return section + this.generateIssuesTable(report.issues, 'Python');
        }

        return section + '✅ **Aucun problème détecté dans les fichiers Python**\n\n';
    }

    /**
     * Générer le tableau des problèmes
     */
    generateIssuesTable(issues, type) {
        if (!issues || issues.length === 0) return '';

        // Filtrer selon la configuration
        let filteredIssues = issues;
        if (!this.config.includeWarnings) {
            filteredIssues = issues.filter(issue => issue.severity === 'error');
        }

        if (filteredIssues.length === 0) return '';

        let table = `### 🔍 Détail des problèmes (${type})

| Fichier | Ligne | Type | Sévérité | Message |
|---------|-------|------|----------|---------|
`;

        filteredIssues.forEach(issue => {
            const filePath = path.relative(process.cwd(), issue.filePath || issue.file_path);
            const line = issue.line || '-';
            const type = issue.type || 'UNKNOWN';
            const severity = issue.severity === 'error' ? '❌ Erreur' : '⚠️ Avertissement';
            const message = this.escapeMarkdown(issue.message);

            table += `| \`${filePath}\` | ${line} | \`${type}\` | ${severity} | ${message} |\n`;
        });

        return table + '\n';
    }

    /**
     * Générer la section détaillée des problèmes
     */
    generateDetailedIssues() {
        let section = '## 🔬 Analyse Détaillée\n\n';

        // Problèmes par type
        const issuesByType = this.groupIssuesByType();

        for (const [type, issues] of Object.entries(issuesByType)) {
            if (issues.length > 0) {
                section += `### ${this.getTypeIcon(type)} ${type}\n\n`;

                issues.slice(0, 10).forEach(issue => {
                    const filePath = path.relative(process.cwd(), issue.filePath || issue.file_path);
                    section += `**\`${filePath}\`${issue.line ? `:${issue.line}` : ''}** - ${issue.message}\n\n`;
                });

                if (issues.length > 10) {
                    section += `*... et ${issues.length - 10} autres problèmes de ce type*\n\n`;
                }
            }
        }

        return section;
    }

    /**
     * Générer les recommandations
     */
    generateRecommendations() {
        const summary = this.getGlobalSummary();
        let recommendations = '## 💡 Recommandations\n\n';

        if (summary.total.errors > 0) {
            recommendations += `### 🚨 Actions Prioritaires (Erreurs)\n\n`;
            recommendations += `1. **Corriger les ${summary.total.errors} erreurs critiques** avant de continuer\n`;
            recommendations += `2. **Exécuter les tests unitaires** après correction\n`;
            recommendations += `3. **Valider la compilation** pour TypeScript\n\n`;
        }

        if (summary.total.warnings > 0) {
            recommendations += `### ⚠️ Améliorations Suggérées (Avertissements)\n\n`;

            if (summary.ts.warnings > 0) {
                recommendations += `- **TypeScript/JavaScript**: ${summary.ts.warnings} avertissements à examiner\n`;
                recommendations += `  - Considérer l'utilisation de règles ESLint plus strictes\n`;
                recommendations += `  - Configurer TypeScript avec des options plus strictes\n\n`;
            }

            if (summary.py.warnings > 0) {
                recommendations += `- **Python**: ${summary.py.warnings} avertissements à examiner\n`;
                recommendations += `  - Configurer flake8/pylint avec des règles plus strictes\n`;
                recommendations += `  - Ajouter des docstrings et typer le code\n\n`;
            }
        }

        // Recommandations générales
        recommendations += `### 🎯 Bonnes Pratiques\n\n`;
        recommendations += `1. **Intégration Continue**: Configurer CI/CD pour exécuter ces scans automatiquement\n`;
        recommendations += `2. **Pre-commit hooks**: Ajouter des hooks pour vérifier le code avant commit\n`;
        recommendations += `3. **Documentation**: Maintenir la documentation à jour\n`;
        recommendations += `4. **Tests**: Augmenter la couverture de tests\n\n`;

        return recommendations;
    }

    /**
     * Générer le pied de page Markdown
     */
    generateMarkdownFooter() {
        return `---

## 📝 Informations sur le Scan

- **Scanner**: NovaQuote Complete Scanner v1.0
- **Date**: ${new Date().toISOString()}
- **Répertoire scanné**: \`${process.cwd()}\`
- **Fichier de rapport**: \`${this.config.reportFileName}\`

### 🛠️ Outils Utilisés

#### TypeScript/JavaScript
- **Analyse syntaxique**: Parser AST natif
- **ESLint**: Si disponible dans le projet
- **TypeScript Compiler**: Si tsconfig.json présent

#### Python
- **Analyse syntaxique**: AST Python
- **flake8**: Si disponible
- **pylint**: Si disponible
- **black**: Pour vérifier le formatage
- **mypy**: Pour la vérification des types

---

*Généré par NOVAQUOTE Complete Scanner - ${new Date().getFullYear()}*
`;
    }

    /**
     * Obtenir le résumé global
     */
    getGlobalSummary() {
        const tsSummary = this.reports.typescript ? {
            files: this.reports.typescript.summary.filesScanned,
            errors: this.reports.typescript.summary.errorsFound,
            warnings: this.reports.typescript.summary.warningsFound
        } : { files: 0, errors: 0, warnings: 0 };

        const pySummary = this.reports.python ? {
            files: this.reports.python.summary.files_scanned || this.reports.python.summary.filesScanned || 0,
            errors: this.reports.python.summary.errors_found || this.reports.python.summary.errorsFound || 0,
            warnings: this.reports.python.summary.warnings_found || this.reports.python.summary.warningsFound || 0
        } : { files: 0, errors: 0, warnings: 0 };

        return {
            ts: {
                ...tsSummary,
                total: tsSummary.errors + tsSummary.warnings
            },
            py: {
                ...pySummary,
                total: pySummary.errors + pySummary.warnings
            },
            total: {
                files: tsSummary.files + pySummary.files,
                errors: tsSummary.errors + pySummary.errors,
                warnings: tsSummary.warnings + pySummary.warnings,
                total: tsSummary.total + pySummary.total
            }
        };
    }

    /**
     * Calculer le score de qualité
     */
    calculateQualityScore() {
        const summary = this.getGlobalSummary();
        const totalIssues = summary.total.total;
        const totalFiles = summary.total.files;

        if (totalFiles === 0) return 100;

        // Formule: score = 100 - (problemes_par_fichier * 10)
        const issuesPerFile = totalIssues / totalFiles;
        let score = Math.max(0, 100 - (issuesPerFile * 10));

        // Pénalité supplémentaire pour les erreurs
        const errorRatio = summary.total.errors / Math.max(1, totalIssues);
        score = score * (1 - errorRatio * 0.5);

        return Math.round(score * 10) / 10;
    }

    /**
     * Obtenir le message de qualité
     */
    getQualityMessage(score) {
        if (score >= 90) return 'Excellent! Le code est de très haute qualité.';
        if (score >= 80) return 'Très bon! Quelques améliorations mineures possibles.';
        if (score >= 70) return 'Bon! Des améliorations sont recommandées.';
        if (score >= 50) return 'Moyen. Une révision du code est nécessaire.';
        return 'Faible. Le code nécessite une attention immédiate.';
    }

    /**
     * Grouper les problèmes par type
     */
    groupIssuesByType() {
        const grouped = {};

        // TypeScript/JavaScript issues
        if (this.reports.typescript && this.reports.typescript.issues) {
            this.reports.typescript.issues.forEach(issue => {
                const type = issue.type || 'UNKNOWN';
                if (!grouped[type]) grouped[type] = [];
                grouped[type].push({ ...issue, language: 'TS/JS' });
            });
        }

        // Python issues
        if (this.reports.python && this.reports.python.issues) {
            this.reports.python.issues.forEach(issue => {
                const type = issue.type || 'UNKNOWN';
                if (!grouped[type]) grouped[type] = [];
                grouped[type].push({ ...issue, language: 'Python' });
            });
        }

        return grouped;
    }

    /**
     * Obtenir l'icône pour un type de problème
     */
    getTypeIcon(type) {
        const icons = {
            'SYNTAX_ERROR': '🚫',
            'IMPORT_ERROR': '📦',
            'UNDECLARED_VARIABLE': '🔍',
            'CONSOLE_LOG': '📝',
            'MISSING_DOCSTRING': '📄',
            'UNUSED_VARIABLE': '🗑️',
            'BROAD_EXCEPTION': '⚠️',
            'LONG_FUNCTION': '📏',
            'ESLINT_ERROR': '🔧',
            'TYPESCRIPT_ERROR': '📘',
            'FLAKE8_ERROR': '🐍',
            'MYPY_ERROR': '🔷'
        };
        return icons[type] || '⚡';
    }

    /**
     * Échapper les caractères Markdown
     */
    escapeMarkdown(text) {
        if (!text) return '';
        return text.replace(/[\\`*_{}[\]()#+\-.!|]/g, '\\$&');
    }

    /**
     * Obtenir un timestamp pour le nom de fichier
     */
    getTimestamp() {
        const now = new Date();
        return now.toISOString()
            .replace(/[:.]/g, '-')
            .replace('T', '_')
            .slice(0, -5);
    }

    /**
     * Assurer que le répertoire de rapports existe
     */
    ensureReportDirectory() {
        if (!fs.existsSync(this.config.outputDir)) {
            fs.mkdirSync(this.config.outputDir, { recursive: true });
        }
    }

    /**
     * Afficher le résumé dans la console
     */
    displaySummary() {
        const summary = this.getGlobalSummary();

        console.log('\n' + '='.repeat(60));
        console.log('📊 RÉSUMÉ DU SCAN');
        console.log('='.repeat(60));
        console.log(`📁 Fichiers scannés: ${summary.total.files}`);
        console.log(`❌ Erreurs trouvées: ${summary.total.errors}`);
        console.log(`⚠️  Avertissements: ${summary.total.warnings}`);
        console.log(`🎯 Score de qualité: ${this.calculateQualityScore()}%`);
        console.log('='.repeat(60));
    }

    /**
     * Scanner selon la configuration
     */
    async scanAccordingToConfig(config) {
        if (config.scanType === 'typescript') {
            return await this.scanTypeScriptOnly(config);
        } else if (config.scanType === 'python') {
            return await this.scanPythonOnly(config);
        } else if (config.scanType === 'targeted') {
            return await this.scanTargeted(config);
        } else {
            return await this.scanCompleteProject(config.rootDir || process.cwd(), config);
        }
    }
}

// Fonction principale
async function main() {
    const scanner = new NovaQuoteCompleteScanner();

    // Parser les arguments de ligne de commande
    const args = process.argv.slice(2);
    const config = parseArguments(args);

    if (config.help) {
        displayHelp();
        return;
    }

    // Appliquer la configuration
    scanner.config = { ...scanner.config, ...config.scannerConfig };

    // Scanner selon la configuration
    const result = await scanner.scanAccordingToConfig(config);

    if (!result.success) {
        process.exit(1);
    }
}

/**
 * Parser les arguments de ligne de commande
 */
function parseArguments(args) {
    const config = {
        help: false,
        scannerConfig: {
            includeWarnings: true,
            includeInfo: true
        },
        scanType: 'full', // 'full', 'typescript', 'python', 'targeted'
        targetPath: null,
        severityFilter: null, // 'errors', 'warnings', 'all'
        typeFilter: null, // ['IMPORT_ERROR', 'SYNTAX_ERROR', ...]
        fileList: [], // ['file1.js', 'file2.py', ...]
        outputDir: path.join(process.cwd(), 'reports')
    };

    let i = 0;
    while (i < args.length) {
        const arg = args[i];

        if (arg === '--help' || arg === '-h') {
            config.help = true;
            i++;
        }
        else if (arg === '--typescript' || arg === '--js') {
            config.scanType = 'typescript';
            i++;
        }
        else if (arg === '--python') {
            config.scanType = 'python';
            i++;
        }
        else if (arg === '--target') {
            config.scanType = 'targeted';
            config.targetPath = args[i + 1];
            i += 2;
        }
        else if (arg === '--files') {
            config.scanType = 'targeted';
            config.fileList = args[i + 1].split(',');
            i += 2;
        }
        else if (arg === '--severity') {
            const severity = args[i + 1];
            if (['errors', 'warnings', 'all'].includes(severity)) {
                config.severityFilter = severity;
            }
            i += 2;
        }
        else if (arg === '--types') {
            config.typeFilter = args[i + 1].split(',');
            i += 2;
        }
        else if (arg === '--errors-only') {
            config.severityFilter = 'errors';
            i++;
        }
        else if (arg === '--warnings-only') {
            config.severityFilter = 'warnings';
            i++;
        }
        else if (arg === '--output' || arg === '-o') {
            config.outputDir = args[i + 1];
            config.scannerConfig.outputDir = args[i + 1];
            i += 2;
        }
        else if (arg === '--no-warnings') {
            config.scannerConfig.includeWarnings = false;
            i++;
        }
        else if (arg === '--no-info') {
            config.scannerConfig.includeInfo = false;
            i++;
        }
        else {
            // Considéré comme répertoire racine
            if (!args[i].startsWith('-')) {
                config.rootDir = args[i];
            }
            i++;
        }
    }

    return config;
}

/**
 * Afficher l'aide
 */
function displayHelp() {
    console.log(`
🚀 NOVAQUOTE Complete Scanner - Options Avancées

Usage: node novaquote-complete-scan.js [options] [directory]

📋 TYPES DE SCAN:
  (par défaut)        Scanner tous les fichiers (TS/JS + Python)
  --typescript, --js  Scanner seulement TypeScript/JavaScript
  --python            Scanner seulement Python
  --target PATH       Scanner un répertoire/fichier spécifique
  --files "f1,f2"     Scanner une liste de fichiers séparés par des virgules

🔍 FILTRES:
  --errors-only       Afficher/corriger seulement les erreurs
  --warnings-only     Afficher/corriger seulement les avertissements
  --severity TYPE     TYPE: errors | warnings | all (par défaut: all)
  --types "T1,T2"     Filtrer par types spécifiques (ex: "IMPORT_ERROR,SYNTAX_ERROR")

📤 SORTIE:
  --output DIR, -o    Spécifier le répertoire de sortie (par défaut: reports/)
  --no-warnings       Exclure les avertissements du rapport
  --no-info           Exclure les infos du rapport

ℹ️  AIDE:
  --help, -h          Afficher cette aide

💡 EXEMPLES:

  # Scan complet standard
  node scripts/scan/novaquote-complete-scan.js

  # Scanner seulement TypeScript
  node scripts/scan/novaquote-complete-scan.js --typescript

  # Scanner un module spécifique
  node scripts/scan/novaquote-complete-scan.js --target "src/models"

  # Scanner une liste de fichiers
  node scripts/scan/novaquote-complete-scan.js --files "file1.py,file2.js,file3.ts"

  # Scanner et afficher seulement les erreurs
  node scripts/scan/novaquote-complete-scan.js --errors-only

  # Scanner et filtrer par type d'erreur
  node scripts/scan/novaquote-complete-scan.js --types "IMPORT_ERROR,CONSOLE_LOG"

  # Scanner et sauvegarder dans un dossier spécifique
  node scripts/scan/novaquote-complete-scan.js --output "./custom-reports"

  # Scanner un répertoire mais ignorer les warnings
  node scripts/scan/novaquote-complete-scan.js --target "backend" --no-warnings

  # Combiner plusieurs options
  node scripts/scan/novaquote-complete-scan.js --python --target "src/" --errors-only --output "./python-errors"

🎯 TYPES D'ERREURS DISPONIBLES:
  Python: IMPORT_ERROR, SYNTAX_ERROR, UNUSED_VARIABLE, BROAD_EXCEPTION,
         MISSING_DOCSTRING, LONG_FUNCTION, FLAKE8_ERROR, MYPY_ERROR
  TS/JS:  SYNTAX_ERROR, UNDECLARED_VARIABLE, CONSOLE_LOG, MISSING_SEMICOLON,
         ESLINT_ERROR, TYPESCRIPT_ERROR, IMPORT_ERROR, UNUSED_VARIABLE
        `);
}

/**
 * Scanner selon la configuration
 */
async function scanAccordingToConfig(config) {
    if (config.scanType === 'typescript') {
        return await this.scanTypeScriptOnly(config);
    } else if (config.scanType === 'python') {
        return await this.scanPythonOnly(config);
    } else if (config.scanType === 'targeted') {
        return await this.scanTargeted(config);
    } else {
        return await this.scanCompleteProject(config.rootDir || process.cwd(), config);
    }
}

// Exporter pour utilisation dans d'autres scripts
module.exports = NovaQuoteCompleteScanner;

// Exécuter si appelé directement
if (require.main === module) {
    main().catch(error => {
        console.error('❌ Erreur fatale:', error);
        process.exit(1);
    });
}
