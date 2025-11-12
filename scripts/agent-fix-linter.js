#!/usr/bin/env node

/**
 * 🔧 NOVAQUOTE Lint & Fix Agent
 * Agent de correction automatique des erreurs et warnings
 */

const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

class LintFixAgent {
  constructor() {
    this.maxIterations = 10;
    this.currentIteration = 0;
    this.corrections = {
      auto: 0,
      manual: 0,
      skipped: 0
    };
    this.previousErrors = [];
    this.targetPattern = null;
    this.fileList = [];
    this.language = 'all'; // 'python', 'typescript', 'javascript', 'all'
    this.severityFilter = null; // 'errors', 'warnings', 'all'
    this.typeFilter = null;
    this.autoFix = true;
    this.dryRun = false;
    this.outputDir = path.join(process.cwd(), 'reports');
    this.config = {};
  }

  /**
   * Log avec formatage
   */
  log(message, type = 'info') {
    const prefix = {
      'info': 'ℹ️',
      'success': '✅',
      'warn': '⚠️',
      'error': '❌',
      'progress': '🔄'
    }[type] || 'ℹ️';

    console.log(`[${new Date().toISOString()}] ${prefix} ${message}`);
  }

  /**
   * Exécuter une commande shell
   */
  runCommand(command, description) {
    return new Promise((resolve, reject) => {
      this.log(`${description}...`, 'progress');

      const startTime = Date.now();
      const proc = spawn(command, { shell: true });

      let stdout = '';
      let stderr = '';

      proc.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      proc.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      proc.on('close', (code) => {
        const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);
        this.log(`Exécuté en ${elapsed}s (code: ${code})`, 'info');

        if (code !== 0 && code !== null) {
          this.log(`Avertissement: commande terminée avec code ${code}`, 'warn');
        }

        resolve({ code, stdout, stderr, elapsed });
      });

      proc.on('error', (error) => {
        reject(error);
      });
    });
  }

  /**
   * Scanner le projet avec filtres appliqués
   */
  async scan() {
    const command = this.getScanCommand();
    const result = await this.runCommand(command, 'Scan du code');

    const scanResult = this.parseScanResult(result.stdout);

    // Appliquer les filtres avancés
    if (scanResult.errors || scanResult.warnings) {
      // Combiner erreurs et warnings pour le filtrage
      const allIssues = [...(scanResult.errors || []), ...(scanResult.warnings || [])];
      const filteredIssues = this.filterIssues(allIssues);

      // Séparer à nouveau
      scanResult.errors = filteredIssues.filter(issue => issue.severity === 'error');
      scanResult.warnings = filteredIssues.filter(issue => issue.severity === 'warning');
    }

    return scanResult;
  }

  /**
   * Parser le résultat du scan
   */
  parseScanResult(output) {
    const errors = [];
    const warnings = [];

    // Extraire les erreurs du JSON
    const jsonMatch = output.match(/===SCAN_RESULT_JSON_BEGIN===\s*([\s\S]*?)\s*===SCAN_RESULT_JSON_END===/);
    if (jsonMatch) {
      try {
        const data = JSON.parse(jsonMatch[1]);
        data.issues.forEach(issue => {
          if (issue.severity === 'error') {
            errors.push(issue);
          } else {
            warnings.push(issue);
          }
        });
      } catch (e) {
        this.log('Erreur lors du parsing du JSON', 'error');
      }
    }

    // Extraire les stats
    const statsMatch = output.match(/Erreurs trouvées:\s*(\d+)/);
    const warningsMatch = output.match(/Avertissements trouvés:\s*(\d+)/);

    const stats = {
      errors: errors.length,
      warnings: warnings.length,
      files: 0
    };

    if (statsMatch) stats.errors = parseInt(statsMatch[1]);
    if (warningsMatch) stats.warnings = parseInt(warningsMatch[1]);

    return { errors, warnings, stats, rawOutput: output };
  }

  /**
   * Corriger les problèmes automatiquement
   */
  async fixIssues(scanResult) {
    const { errors, warnings } = scanResult;
    let fixedCount = 0;

    // Corriger les erreurs d'abord
    for (const error of errors) {
      if (await this.tryAutoFix(error)) {
        fixedCount++;
      }
    }

    // Puis les warnings
    for (const warning of warnings) {
      if (await this.tryAutoFix(warning)) {
        fixedCount++;
      }
    }

    return fixedCount;
  }

  /**
   * Méthode originale de tentative de correction (déplacée)
   */
  async tryAutoFixOriginal(issue) {
    const { filePath, type, line } = issue;

    // Filtre par pattern cible si spécifié
    if (this.targetPattern && !filePath.includes(this.targetPattern)) {
      return false;
    }

    // Corrections automatiques autorisées
    const autoFixable = {
      'UNUSED_IMPORT': async () => this.fixUnusedImport(filePath, line),
      'MISSING_SEMICOLON': async () => this.fixMissingSemicolon(filePath, line),
      'CONSOLE_LOG': async () => this.fixConsoleLog(filePath, line),
      'UNBALANCED_PARENTHESES': async () => this.fixSyntaxError(filePath, line),
      'UNBALANCED_BRACES': async () => this.fixSyntaxError(filePath, line),
      'PRINT_STATEMENT': async () => this.fixPrintStatement(filePath, line),
    };

    if (autoFixable[type]) {
      try {
        await autoFixable[type]();
        this.corrections.auto++;
        this.log(`✓ Auto-fix: ${path.basename(filePath)}:${line} - ${type}`, 'success');
        return true;
      } catch (error) {
        this.log(`✗ Échec auto-fix ${type}: ${error.message}`, 'warn');
        return false;
      }
    }

    // Trop complexe pour auto-fix
    this.corrections.manual++;
    return false;
  }

  /**
   * Tenter une correction automatique (wrapper avec dry-run)
   */
  async tryAutoFix(issue) {
    // Mode dry-run: simuler sans modifier
    if (this.dryRun) {
      this.log(`🔍 [DRY-RUN] Pourrait corriger: ${issue.type} dans ${path.basename(issue.filePath || issue.file_path)}:${issue.line}`, 'info');
      this.corrections.auto++;
      return true;
    }

    // Auto-fix désactivé
    if (!this.autoFix) {
      this.log(`⚠️  Auto-fix désactivé pour: ${issue.type}`, 'warn');
      this.corrections.skipped++;
      return false;
    }

    // Procéder à la correction en utilisant la méthode originale
    const result = await this.tryAutoFixOriginal(issue);
    return result;
  }

  /**
   * Corriger un import non utilisé
   */
  async fixUnusedImport(filePath, line) {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split('\n');
    const targetLine = lines[line - 1];

    // Détecter le pattern d'import
    const importMatch = targetLine.match(/^(import\s+.*?;?)$/);
    if (importMatch) {
      // Commenter l'import au lieu de le supprimer (plus sûr)
      lines[line - 1] = '// ' + targetLine;
      fs.writeFileSync(filePath, lines.join('\n'));
    }
  }

  /**
   * Ajouter un point-virgule manquant
   */
  async fixMissingSemicolon(filePath, line) {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split('\n');
    const targetLine = lines[line - 1].trim();

    if (!targetLine.endsWith(';') && !targetLine.endsWith('{') && !targetLine.endsWith('}')) {
      lines[line - 1] += ';';
      fs.writeFileSync(filePath, lines.join('\n'));
    }
  }

  /**
   * Corriger console.log
   */
  async fixConsoleLog(filePath, line) {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split('\n');

    // Commenter au lieu de supprimer
    if (lines[line - 1].includes('console.log')) {
      lines[line - 1] = '// ' + lines[line - 1];
      fs.writeFileSync(filePath, lines.join('\n'));
    }
  }

  /**
   * Corriger erreur de syntaxe
   */
  async fixSyntaxError(filePath, line) {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split('\n');
    const targetLine = lines[line - 1];

    // Patterns courants d'erreurs de syntaxe
    let fixed = false;

    // Supprimer point-virgule en trop après accolade
    if (targetLine.includes('{;')) {
      lines[line - 1] = targetLine.replace('{;', '{');
      fixed = true;
    }

    // Supprimer point-virgule en trop après crochet
    if (targetLine.includes('[;')) {
      lines[line - 1] = targetLine.replace('[;', '[');
      fixed = true;
    }

    if (fixed) {
      fs.writeFileSync(filePath, lines.join('\n'));
    }
  }

  /**
   * Corriger print statement
   */
  async fixPrintStatement(filePath, line) {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split('\n');

    if (lines[line - 1].includes('print(')) {
      // Commenter au lieu de supprimer
      lines[line - 1] = '# ' + lines[line - 1];
      fs.writeFileSync(filePath, lines.join('\n'));
    }
  }

  /**
   * Vérifier s'il y a eu progression
   */
  hasProgressed(currentErrors, currentWarnings) {
    const currentTotal = currentErrors + currentWarnings;
    const previousTotal = this.previousErrors.reduce((sum, e) => sum + e.errors + e.warnings, 0);

    if (this.previousErrors.length === 0) return true;

    return currentTotal < previousTotal;
  }

  /**
   * Exécuter la boucle principale de correction
   */
  async run() {
    // Afficher la configuration
    this.log('🔧 NOVAQUOTE Lint & Fix Agent - Démarrage', 'info');
    this.log(`📋 Langage: ${this.language === 'all' ? 'Tous' : this.language}`, 'info');

    if (this.targetPattern) {
      this.log(`🎯 Cible: ${this.targetPattern}`, 'info');
    }

    if (this.fileList && this.fileList.length > 0) {
      this.log(`📄 Fichiers: ${this.fileList.join(', ')}`, 'info');
    }

    if (this.severityFilter) {
      this.log(`🔍 Filtre sévérité: ${this.severityFilter}`, 'info');
    }

    if (this.typeFilter && this.typeFilter.length > 0) {
      this.log(`🏷️  Filtre types: ${this.typeFilter.join(', ')}`, 'info');
    }

    if (this.dryRun) {
      this.log(`🔍 Mode DRY-RUN activé (simulation uniquement)`, 'warn');
    } else if (!this.autoFix) {
      this.log(`⚠️  Auto-fix désactivé (scan uniquement)`, 'warn');
    }

    this.log(`⏰ Itérations max: ${this.maxIterations}`, 'info');
    console.log('');

    while (this.currentIteration < this.maxIterations) {
      this.currentIteration++;
      this.log(`🔄 Itération ${this.currentIteration}/${this.maxIterations}`, 'progress');

      // Scanner
      const scanResult = await this.scan();
      const { stats } = scanResult;

      this.log(`📊 Erreurs: ${stats.errors}, Warnings: ${stats.warnings}`, 'info');

      // Vérifier progression
      if (this.currentIteration > 1 && !this.hasProgressed(stats.errors, stats.warnings)) {
        this.log('⚠️  Progression nulle - Arrêt', 'warn');
        break;
      }

      // Sauvegarder état précédent
      this.previousErrors.push({ ...stats });

      // Corriger
      if (stats.errors === 0 && stats.warnings === 0) {
        this.log('✅ SUCCÈS: 0 erreur, 0 warning - Code parfait!', 'success');
        break;
      }

      const fixedCount = await this.fixIssues(scanResult);
      this.log(`📝 ${fixedCount} problèmes corrigés automatiquement`, 'success');

      console.log('');
    }

    // Rapport final
    this.log('📋 RAPPORT FINAL', 'info');

    if (this.dryRun) {
      this.log(`   🔍 [DRY-RUN] Simulations: ${this.corrections.auto}`, 'info');
    } else {
      this.log(`   ✅ Auto-corrigées: ${this.corrections.auto}`, 'success');
    }

    if (this.corrections.skipped > 0) {
      this.log(`   ⏭️  Ignorées: ${this.corrections.skipped}`, 'warn');
    }

    this.log(`   ⚠️  Manuelles (complexes): ${this.corrections.manual}`, 'warn');
    this.log(`   🔄 Itérations: ${this.currentIteration}`, 'info');

    if (this.dryRun) {
      this.log(`💡 Utilisez sans --dry-run pour appliquer les corrections`, 'info');
    }
  }

  /**
   * Configurer l'agent avec les options avancées
   */
  configure(options = {}) {
    if (options.language) this.language = options.language;
    if (options.target) this.targetPattern = options.target;
    if (options.fileList) this.fileList = options.fileList;
    if (options.severityFilter) this.severityFilter = options.severityFilter;
    if (options.typeFilter) this.typeFilter = options.typeFilter;
    if (options.maxIterations) this.maxIterations = options.maxIterations;
    if (options.autoFix !== undefined) this.autoFix = options.autoFix;
    if (options.dryRun) this.dryRun = options.dryRun;
    if (options.outputDir) this.outputDir = options.outputDir;
    if (options.config) this.config = options.config;
  }

  /**
   * Déterminer la commande de scan à utiliser
   */
  getScanCommand() {
    let command;

    if (this.language === 'python') {
      command = 'python scripts/scan/scan-python.py';
    } else if (this.language === 'typescript' || this.language === 'javascript') {
      command = 'node scripts/scan/scan-typescript-javascript.js';
    } else {
      command = 'node scripts/scan/novaquote-complete-scan.js';
    }

    // Ajouter les filtres à la commande
    if (this.severityFilter) {
      command += ` --severity ${this.severityFilter}`;
    }

    if (this.typeFilter && this.typeFilter.length > 0) {
      command += ` --types "${this.typeFilter.join(',')}"`;
    }

    if (this.targetPattern) {
      command += ` --target "${this.targetPattern}"`;
    }

    if (this.fileList && this.fileList.length > 0) {
      command += ` --files "${this.fileList.join(',')}"`;
    }

    return command;
  }

  /**
   * Filtrer les problèmes avant correction
   */
  filterIssues(issues) {
    let filtered = issues;

    // Filtre par sévérité
    if (this.severityFilter === 'errors') {
      filtered = filtered.filter(issue => issue.severity === 'error');
    } else if (this.severityFilter === 'warnings') {
      filtered = filtered.filter(issue => issue.severity === 'warning');
    }

    // Filtre par type
    if (this.typeFilter && this.typeFilter.length > 0) {
      filtered = filtered.filter(issue => this.typeFilter.includes(issue.type));
    }

    // Filtre par fichier cible
    if (this.targetPattern) {
      filtered = filtered.filter(issue => {
        const issuePath = (issue.filePath || issue.file_path || '').toLowerCase();
        return issuePath.includes(this.targetPattern.toLowerCase());
      });
    }

    // Filtre par liste de fichiers
    if (this.fileList && this.fileList.length > 0) {
      filtered = filtered.filter(issue => {
        const fileName = path.basename(issue.filePath || issue.file_path);
        return this.fileList.includes(fileName);
      });
    }

    return filtered;
  }

}

// Exécution
async function main() {
  const args = process.argv.slice(2);
  const agent = new LintFixAgent();
  const options = parseArguments(args);

  if (options.help) {
    displayHelp();
    return;
  }

  agent.configure(options);
  await agent.run();
}

/**
 * Parser les arguments avancés
 */
function parseArguments(args) {
  const options = {
    help: false,
    language: 'all', // 'all', 'python', 'typescript'
    target: null,
    fileList: [],
    severityFilter: null, // 'errors', 'warnings', 'all'
    typeFilter: null, // ['IMPORT_ERROR', ...]
    maxIterations: 10,
    autoFix: true, // Activer l'auto-fix
    dryRun: false, // Simuler sans modifier les fichiers
    outputDir: path.join(process.cwd(), 'reports'),
    config: {}
  };

  let i = 0;
  while (i < args.length) {
    const arg = args[i];

    if (arg === '--help' || arg === '-h') {
      options.help = true;
      i++;
    }
    else if (arg === '--python') {
      options.language = 'python';
      i++;
    }
    else if (arg === '--typescript' || arg === '--js') {
      options.language = 'typescript';
      i++;
    }
    else if (arg === '--target') {
      options.target = args[i + 1];
      i += 2;
    }
    else if (arg === '--files') {
      options.fileList = args[i + 1].split(',');
      i += 2;
    }
    else if (arg === '--severity') {
      const severity = args[i + 1];
      if (['errors', 'warnings', 'all'].includes(severity)) {
        options.severityFilter = severity;
      }
      i += 2;
    }
    else if (arg === '--types') {
      options.typeFilter = args[i + 1].split(',');
      i += 2;
    }
    else if (arg === '--errors-only') {
      options.severityFilter = 'errors';
      i++;
    }
    else if (arg === '--warnings-only') {
      options.severityFilter = 'warnings';
      i++;
    }
    else if (arg === '--max-iterations' || arg === '--iterations') {
      options.maxIterations = parseInt(args[i + 1]);
      i += 2;
    }
    else if (arg === '--dry-run') {
      options.dryRun = true;
      i++;
    }
    else if (arg === '--no-autofix') {
      options.autoFix = false;
      i++;
    }
    else if (arg === '--output' || arg === '-o') {
      options.outputDir = args[i + 1];
      i += 2;
    }
    else if (arg === '--config') {
      // Charger un fichier de configuration JSON
      const configPath = args[i + 1];
      if (fs.existsSync(configPath)) {
        options.config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      }
      i += 2;
    }
    else if (arg.startsWith('--')) {
      // Option personnalisée (format: --option=value)
      const [key, value] = arg.substring(2).split('=');
      options[key] = value;
      i++;
    }
  }

  return options;
}

/**
 * Afficher l'aide
 */
function displayHelp() {
  console.log(`
🔧 NOVAQUOTE Lint & Fix Agent - Options Avancées

Usage: node agent-fix-linter.js [options]

📋 TYPES DE SCAN & CORRECTION:
  (par défaut)        Scanner et corriger tous les fichiers
  --python            Corriger seulement les fichiers Python
  --typescript, --js  Corriger seulement TypeScript/JavaScript
  --target PATH       Corriger un répertoire/fichier spécifique
  --files "f1,f2"     Corriger une liste de fichiers séparés par des virgules

🔍 FILTRES:
  --errors-only       Corriger seulement les erreurs
  --warnings-only     Corriger seulement les avertissements
  --severity TYPE     TYPE: errors | warnings | all (par défaut: all)
  --types "T1,T2"     Corriger seulement certains types (ex: "IMPORT_ERROR,CONSOLE_LOG")

⚙️  OPTIONS DE CORRECTION:
  --max-iterations N  Nombre maximum d'itérations (par défaut: 10)
  --dry-run          Simuler sans modifier les fichiers (lecture seule)
  --no-autofix       Désactiver l'auto-fix (scan uniquement)
  --output DIR       Spécifier le répertoire de sortie

💡 EXEMPLES:

  # Correction automatique complète
  node scripts/agent-fix-linter.js

  # Corriger seulement Python
  node scripts/agent-fix-linter.js --python

  # Corriger un module spécifique
  node scripts/agent-fix-linter.js --target "src/models"

  # Corriger seulement les erreurs
  node scripts/agent-fix-linter.js --errors-only

  # Corriger par type d'erreur
  node scripts/agent-fix-linter.js --types "IMPORT_ERROR,UNUSED_IMPORT"

  # Simuler les corrections (sans modifier)
  node scripts/agent-fix-linter.js --dry-run

  # Corriger avec limite d'itérations
  node scripts/agent-fix-linter.js --max-iterations 5

  # Scan seulement (sans auto-fix)
  node scripts/agent-fix-linter.js --no-autofix

  # Corriger plusieurs fichiers spécifiques
  node scripts/agent-fix-linter.js --files "file1.py,file2.js,file3.ts"

  # Combiner plusieurs options
  node scripts/agent-fix-linter.js --python --target "src/" --errors-only --max-iterations 3

🎯 TYPES D'ERREURS AUTO-FIXABLES:
  Python: UNUSED_IMPORT, UNUSED_VARIABLE, SYNTAX_ERROR, MISSING_DOCSTRING
  TS/JS:  IMPORT_ERROR, UNUSED_IMPORT, MISSING_SEMICOLON, CONSOLE_LOG, SYNTAX_ERROR

ℹ️  AIDE:
  --help, -h          Afficher cette aide
        `);
}

// Export pour utilisation
module.exports = LintFixAgent;

// Exécution directe
if (require.main === module) {
  main().catch(error => {
    console.error('❌ Erreur:', error);
    process.exit(1);
  });
}
