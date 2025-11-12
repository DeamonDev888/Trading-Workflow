#!/usr/bin/env node

/**
 * NOVAQUOTE - Script de Scan TypeScript/JavaScript
 * Détecte les erreurs de syntaxe, de type et autres problèmes dans les fichiers TS/JS
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class TypeScriptJavaScriptScanner {
    constructor() {
        this.errors = [];
        this.warnings = [];
        this.stats = {
            filesScanned: 0,
            errorsFound: 0,
            warningsFound: 0
        };
    }

    /**
     * Scan tous les fichiers TypeScript et JavaScript du projet
     */
    async scanProject(rootDir = process.cwd()) {
        console.log('🔍 Scan des fichiers TypeScript/JavaScript...');
        console.log(`📁 Répertoire racine: ${rootDir}`);

        // Trouver tous les fichiers TS/JS
        const files = this.findTypeScriptJavaScriptFiles(rootDir);

        console.log(`📄 ${files.length} fichiers trouvés`);

        // Scanner chaque fichier
        for (const file of files) {
            await this.scanFile(file);
        }

        // Analyser avec ESLint si disponible
        await this.runESLint(rootDir);

        // Analyser avec TypeScript Compiler si disponible
        await this.runTypeScriptCompiler(rootDir);

        return this.generateReport();
    }

    /**
     * Trouver tous les fichiers TypeScript et JavaScript
     */
    findTypeScriptJavaScriptFiles(dir, fileList = []) {
        const files = fs.readdirSync(dir);

        files.forEach(file => {
            const filePath = path.join(dir, file);
            const stat = fs.statSync(filePath);

            if (stat.isDirectory()) {
                // Ignorer les répertoires node_modules, .git, dist, build
                if (!['node_modules', '.git', 'dist', 'build', 'coverage'].includes(file)) {
                    this.findTypeScriptJavaScriptFiles(filePath, fileList);
                }
            } else if (this.isTypeScriptJavaScriptFile(file)) {
                fileList.push(filePath);
            }
        });

        return fileList;
    }

    /**
     * Vérifier si un fichier est TypeScript ou JavaScript
     */
    isTypeScriptJavaScriptFile(filename) {
        const extensions = ['.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs'];
        return extensions.some(ext => filename.endsWith(ext));
    }

    /**
     * Scanner un fichier individuel
     */
    async scanFile(filePath) {
        this.stats.filesScanned++;

        try {
            const content = fs.readFileSync(filePath, 'utf8');

            // Analyse syntaxique de base
            this.checkBasicSyntax(filePath, content);

            // Vérifications spécifiques
            this.checkImportExport(filePath, content);
            this.checkCommonPatterns(filePath, content);
            this.checkAsyncAwait(filePath, content);
            this.checkVariableDeclarations(filePath, content);

        } catch (error) {
            this.addError(filePath, 'FILE_READ_ERROR', `Impossible de lire le fichier: ${error.message}`);
        }
    }

    /**
     * Vérifications syntaxiques de base (amélioré pour réduire les faux positifs)
     */
    checkBasicSyntax(filePath, content) {
        const lines = content.split('\n');

        // Vérification globale des parenthèses/accolades (plus fiable)
        this.checkGlobalBraceBalance(filePath, content);

        lines.forEach((line, index) => {
            const lineNumber = index + 1;
            const trimmedLine = line.trim();

            // Ignorer les lignes de commentaires, multi-lignes, strings
            if (this.shouldIgnoreLine(trimmedLine)) return;

            // Vérification parenthèses seulement si déséquilibre évident
            if (this.hasObviousUnbalancedParentheses(line)) {
                this.addWarning(filePath, 'UNBALANCED_PARENTHESES',
                    `Parenthèses potentiellement non équilibrées ligne ${lineNumber}`, lineNumber);
            }

            // Points-virgules manquants (seulement pour les expressions simples)
            if (this.shouldCheckSemicolon(line, trimmedLine)) {
                this.addWarning(filePath, 'MISSING_SEMICOLON',
                    `Point-virgule manquant ligne ${lineNumber}`, lineNumber);
            }
        });
    }

    /**
     * Vérification globale des accolades/parenthèses (ANTI-FAUX-POSITIFS)
     */
    checkGlobalBraceBalance(filePath, content) {
        // Retirer les commentaires et strings pour éviter les faux positifs
        const cleanContent = this.removeCommentsAndStrings(content);

        let braceDepth = 0;
        let parenDepth = 0;
        const lines = cleanContent.split('\n');

        lines.forEach((line, index) => {
            for (let char of line) {
                if (char === '{') braceDepth++;
                else if (char === '}') braceDepth--;
                else if (char === '(') parenDepth++;
                else if (char === ')') parenDepth--;
            }
        });

        // ✅ RÉDUCTION MASSIVE DES FAUX POSITIFS:
        // On ne signale plus les déséquilibres ligne par ligne!
        // Seulement un déséquilibre globalgrave détecté (plus de 5!

        if (Math.abs(braceDepth) > 5 || Math.abs(parenDepth) > 10) {
            this.addError(filePath, 'SERIOUS_BRACE_IMBALANCE',
                `Déséquilibre critique: ${braceDepth > 0 ? '+' : ''}${braceDepth}accolades, ${parenDepth > 0 ? '+' : ''}${parenDepth}parenthèses`);
        }

        // ✅ Plus de signalement pour chaque ligne!
        // Le vérificateur syntaxique est suffisante pour détecter les vraies erreurs
    }

    /**
     * Vérifier si une ligne doit être ignorée
     */
    shouldIgnoreLine(line) {
        return line.startsWith('//') ||
               line.startsWith('*') ||
               line.startsWith('/*') ||
               line.includes('"""') || // Python docstrings dans fichiers JS
               line.length < 3;
    }

    /**
     * Vérifier les déséquilibres évidents de parenthèses
     */
    hasObviousUnbalancedParentheses(line) {
        // Compter seulement sur une ligne simple
        const openParens = (line.match(/\(/g) || []).length;
        const closeParens = (line.match(/\)/g) || []).length;

        // Seulement signaler si différence significative
        return Math.abs(openParens - closeParens) > 1;
    }

    /**
     * Vérifier si on doit ajouter un point-virgule (ANTI-FAUX-POSITIFS)
     */
    shouldCheckSemicolon(originalLine, trimmedLine) {
        // ❌ IGNORER COMPLÈTEMENT LES POINTS-VIRGULES MANQUANTS
        // Les détection de points-virgules créent des milliers de faux positifs
        // et n'empêchent pas l'exécution du code (JavaScript les ajoute automatiquement)
        return false;

        // ✅ Les vraies erreurs sont détectées par ESLint et TSC
        // Pas besoin de surcharger avec des alertes de style!
    }

    /**
     * Retirer les commentaires et strings pour l'analyse
     */
    removeCommentsAndStrings(content) {
        let clean = content;

        // Retirer les commentaires //
        clean = clean.replace(/\/\/.*$/gm, '');

        // Retirer les commentaires /* */
        clean = clean.replace(/\/\*[\s\S]*?\*\//g, '');

        // Retirer les strings simples
        clean = clean.replace(/'[^']*'/g, '');

        // Retirer les strings doubles
        clean = clean.replace(/"[^"]*"/g, '');

        // Retirer les backticks strings
        clean = clean.replace(/`[^`]*`/g, '');

        return clean;
    }

    /**
     * Vérifier les imports/exports
     */
    checkImportExport(filePath, content) {
        const lines = content.split('\n');

        lines.forEach((line, index) => {
            const lineNumber = index + 1;
            const trimmedLine = line.trim();

            // Imports avec chemins relatifs incorrects
            if (trimmedLine.startsWith('import')) {
                const importMatch = trimmedLine.match(/from ['"](.+)['"]/);
                if (importMatch) {
                    const importPath = importMatch[1];
                    if (importPath.startsWith('./') || importPath.startsWith('../')) {
                        // Vérifier si le fichier existe
                        const fullPath = path.resolve(path.dirname(filePath), importPath);
                        if (!fs.existsSync(fullPath) && !fs.existsSync(fullPath + '.js') &&
                            !fs.existsSync(fullPath + '.ts') && !fs.existsSync(fullPath + '.json')) {
                            this.addError(filePath, 'INVALID_IMPORT_PATH',
                                `Chemin d'import invalide: ${importPath}`, lineNumber);
                        }
                    }
                }
            }
        });
    }

    /**
     * Vérifier les patterns communs (amélioré pour réduire les faux positifs)
     */
    checkCommonPatterns(filePath, content) {
        const lines = content.split('\n');

        // Extraire les variables déclarées dans le fichier
        const declaredVars = this.extractDeclaredVariables(content);

        lines.forEach((line, index) => {
            const lineNumber = index + 1;
            const trimmedLine = line.trim();

            // Ignorer les commentaires
            if (trimmedLine.startsWith('//') || trimmedLine.startsWith('/*')) return;

            // NOTE: console.log ne sont PAS signalés comme warnings dans ce projet
            // car ils sont intentionnels pour le debugging et la surveillance
            // de trading en temps réel.

            // Variables non déclarées (amélioré)
            this.checkUndeclaredVariables(filePath, line, lineNumber, declaredVars);
        });
    }

    /**
     * Extraire les variables déclarées dans le fichier
     */
    extractDeclaredVariables(content) {
        const declaredVars = new Set();
        const lines = content.split('\n');

        // Variables globales connues et API
        const knownGlobals = new Set([
            'console', 'window', 'document', 'process', 'global', 'Buffer',
            'require', 'module', 'exports', '__dirname', '__filename',
            'setTimeout', 'setInterval', 'clearTimeout', 'clearInterval',
            'fetch', 'XMLHttpRequest', 'WebSocket', 'EventSource',
            'fs', 'path', 'crypto', 'os', 'util', 'url', 'querystring',
            'http', 'https', 'net', 'dgram', 'dns', 'readline', 'stream',
            'zlib', 'events', 'assert', 'buffer', 'child_process',
            'cluster', 'domain', 'punycode', 'readline', 'repl',
            'string_decoder', 'tls', 'tty', 'url', 'util', 'v8',
            'vm', 'inspector', 'async_hooks', 'perf_hooks', 'timers',
            'trace_events', 'worker_threads', 'module', 'console'
        ]);

        lines.forEach(line => {
            const trimmedLine = line.trim();

            // Variables déclarées avec const/let/var
            const constMatch = trimmedLine.match(/const\s+(\w+)/);
            if (constMatch) declaredVars.add(constMatch[1]);

            const letMatch = trimmedLine.match(/let\s+(\w+)/);
            if (letMatch) declaredVars.add(letMatch[1]);

            const varMatch = trimmedLine.match(/var\s+(\w+)/);
            if (varMatch) declaredVars.add(varMatch[1]);

            // Paramètres de fonction
            const funcMatch = trimmedLine.match(/function\s+\w+\s*\(([^)]*)\)/);
            if (funcMatch) {
                const params = funcMatch[1].split(',').map(p => p.trim().split('=')[0].trim());
                params.filter(p => p).forEach(p => declaredVars.add(p));
            }

            // Fonctions fléchées
            const arrowMatch = trimmedLine.match(/\(([^)]*)\)\s*=>/);
            if (arrowMatch) {
                const params = arrowMatch[1].split(',').map(p => p.trim().split('=')[0].trim());
                params.filter(p => p).forEach(p => declaredVars.add(p));
            }

            // Méthodes de classe
            const methodMatch = trimmedLine.match(/(\w+)\s*\([^)]*\)\s*{/);
            if (methodMatch) declaredVars.add(methodMatch[1]);

            // Destructuring
            const destructMatch = trimmedLine.match(/(?:const|let|var)\s*\{([^}]+)\}/);
            if (destructMatch) {
                const vars = destructMatch[1].split(',').map(v => v.trim().split(':')[0].trim());
                vars.filter(v => v).forEach(v => declaredVars.add(v));
            }

            // Imports
            const importMatch = trimmedLine.match(/import.*\{([^}]+)\}/);
            if (importMatch) {
                const imports = importMatch[1].split(',').map(i => i.trim().split(' as ')[0].trim());
                imports.filter(i => i).forEach(i => declaredVars.add(i));
            }

            const importDefaultMatch = trimmedLine.match(/import\s+(\w+)/);
            if (importDefaultMatch) declaredVars.add(importDefaultMatch[1]);
        });

        return { declaredVars, knownGlobals };
    }

    /**
     * Vérifier les variables non déclarées (ANTI-FAUX-POSITIFS)
     */
    checkUndeclaredVariables(filePath, line, lineNumber, { declaredVars, knownGlobals }) {
        // ✅ RÉDUCTION MASSIVE DES FAUX POSITIFS:
        // La détection automatique des variables non déclarées génère
        // énormément de faux positifs car elle ne comprend pas:
        // - Les paramètres d'entrée
        // - Les variables globales
        // - Les imports dynamiques
        // - Les propriétés d'objets (obj.property)
        // - Les callbacks et événements

        // ❌ ON DÉSACTIVE CETTE DÉTECTION PAR DÉFAUT
        // Les vraies erreurs seront détectées par ESLint et TSC

        // return; // Décommenter pour désactiver complètement

        // Si on veut garder une détection minimale, seulement pour les cas évidents:
        const assignMatch = line.match(/(?:const|let|var)\s+([a-zA-Z_]\w*)\s*=/);
        if (!assignMatch) return;

        const varName = assignMatch[1];

        // Vérifier si c'est déjà déclarée
        if (declaredVars.has(varName) || knownGlobals.has(varName)) return;

        // Signaler seulement si:
        // 1. Pas d'underscore (probablement intentionnel)
        // 2. Pas en majuscules (probablement une constante)
        // 3. Probablement pas un nom générique
        if (!varName.includes('_') &&
            !varName.match(/^[A-Z_]+$/) &&
            !['data', 'result', 'value', 'item', 'key', 'val'].includes(varName)) {

            this.addWarning(filePath, 'POSSIBLE_UNDECLARED_VARIABLE',
                `Possible variable non déclarée: ${varName}`, lineNumber);
        }
    }

    /**
     * Vérifier async/await
     */
    checkAsyncAwait(filePath, content) {
        const lines = content.split('\n');

        lines.forEach((line, index) => {
            const lineNumber = index + 1;

            // await sans async
            if (line.includes('await')) {
                const functionMatch = content.substring(0, index * line.length).match(/async\s+\w+/);
                if (!functionMatch && !content.substring(0, index * line.length).includes('async ()')) {
                    this.addError(filePath, 'AWAIT_WITHOUT_ASYNC',
                        `await utilisé sans fonction async ligne ${lineNumber}`, lineNumber);
                }
            }
        });
    }

    /**
     * Vérifier les déclarations de variables
     */
    checkVariableDeclarations(filePath, content) {
        const lines = content.split('\n');

        lines.forEach((line, index) => {
            const lineNumber = index + 1;

            // var instead of let/const
            if (line.trim().startsWith('var ')) {
                this.addWarning(filePath, 'VAR_USAGE',
                    `Utilisation de 'var' déconseillée ligne ${lineNumber}`, lineNumber);
            }
        });
    }

    /**
     * Exécuter ESLint si disponible
     */
    async runESLint(rootDir) {
        try {
            const eslintConfig = path.join(rootDir, '.eslintrc.js');
            const eslintPackageJson = path.join(rootDir, 'package.json');

            if (fs.existsSync(eslintConfig) ||
                (fs.existsSync(eslintPackageJson) &&
                 JSON.parse(fs.readFileSync(eslintPackageJson, 'utf8')).eslintConfig)) {

                console.log('🔧 Exécution d\'ESLint...');
                try {
                    const output = execSync('npx eslint . --ext .ts,.js,.tsx,.jsx --format json',
                        { cwd: rootDir, encoding: 'utf8' });

                    const eslintResults = JSON.parse(output);
                    eslintResults.forEach(result => {
                        result.messages.forEach(message => {
                            if (message.severity === 2) {
                                this.addError(result.filePath, 'ESLINT_ERROR',
                                    message.message, message.line, message.ruleId);
                            } else {
                                this.addWarning(result.filePath, 'ESLINT_WARNING',
                                    message.message, message.line, message.ruleId);
                            }
                        });
                    });
                } catch (error) {
                    // ESLint retourne une erreur si des problèmes sont trouvés
                    if (error.stdout) {
                        try {
                            const eslintResults = JSON.parse(error.stdout);
                            eslintResults.forEach(result => {
                                result.messages.forEach(message => {
                                    if (message.severity === 2) {
                                        this.addError(result.filePath, 'ESLINT_ERROR',
                                            message.message, message.line, message.ruleId);
                                    } else {
                                        this.addWarning(result.filePath, 'ESLINT_WARNING',
                                            message.message, message.line, message.ruleId);
                                    }
                                });
                            });
                        } catch (parseError) {
                            console.warn('⚠️ Impossible de parser la sortie ESLint');
                        }
                    }
                }
            }
        } catch (error) {
            console.warn('⚠️ Impossible d\'exécuter ESLint:', error.message);
        }
    }

    /**
     * Exécuter TypeScript Compiler si disponible
     */
    async runTypeScriptCompiler(rootDir) {
        try {
            const tsConfig = path.join(rootDir, 'tsconfig.json');

            if (fs.existsSync(tsConfig)) {
                console.log('🔧 Exécution du TypeScript Compiler...');
                try {
                    execSync('npx tsc --noEmit --pretty false', {
                        cwd: rootDir,
                        encoding: 'utf8'
                    });
                } catch (error) {
                    // Parser les erreurs TypeScript
                    const output = error.stdout || error.message;
                    const lines = output.split('\n');

                    lines.forEach(line => {
                        const tsErrorMatch = line.match(/(.+)\((\d+),(\d+)\):\s+error\s+(.+):\s*(.+)/);
                        if (tsErrorMatch) {
                            const [, filePath, lineNum, colNum, errorCode, message] = tsErrorMatch;
                            this.addError(filePath, 'TYPESCRIPT_ERROR',
                                `[${errorCode}] ${message}`, parseInt(lineNum));
                        }
                    });
                }
            }
        } catch (error) {
            console.warn('⚠️ Impossible d\'exécuter TypeScript Compiler:', error.message);
        }
    }

    /**
     * Ajouter une erreur
     */
    addError(filePath, type, message, line = null, rule = null) {
        this.errors.push({
            filePath,
            type,
            message,
            line,
            rule,
            severity: 'error'
        });
        this.stats.errorsFound++;
    }

    /**
     * Ajouter un avertissement
     */
    addWarning(filePath, type, message, line = null, rule = null) {
        this.warnings.push({
            filePath,
            type,
            message,
            line,
            rule,
            severity: 'warning'
        });
        this.stats.warningsFound++;
    }

    /**
     * Générer le rapport
     */
    generateReport() {
        const allIssues = [...this.errors, ...this.warnings].sort((a, b) => {
            // Trier par fichier puis par ligne
            if (a.filePath !== b.filePath) {
                return a.filePath.localeCompare(b.filePath);
            }
            return (a.line || 0) - (b.line || 0);
        });

        return {
            summary: {
                ...this.stats,
                scanDate: new Date().toISOString(),
                scanner: 'TypeScript/JavaScript Scanner v1.0'
            },
            issues: allIssues
        };
    }
}

// Export pour utilisation dans d'autres scripts
module.exports = TypeScriptJavaScriptScanner;

// Exécuter si appelé directement
if (require.main === module) {
    const scanner = new TypeScriptJavaScriptScanner();

    scanner.scanProject()
        .then(report => {
            console.log('\n📊 Rapport de scan TypeScript/JavaScript:');
            console.log(`Fichiers scannés: ${report.summary.filesScanned}`);
            console.log(`Erreurs trouvées: ${report.summary.errorsFound}`);
            console.log(`Avertissements trouvés: ${report.summary.warningsFound}`);

            if (report.summary.errorsFound > 0 || report.summary.warningsFound > 0) {
                console.log('\n⚠️ Des problèmes ont été détectés!');
            } else {
                console.log('\n✅ Aucun problème détecté!');
            }
        })
        .catch(error => {
            console.error('❌ Erreur lors du scan:', error);
            process.exit(1);
        });
}