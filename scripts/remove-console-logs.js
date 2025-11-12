#!/usr/bin/env node

/**
 * Script pour supprimer les console.log du code de production
 * NOVAQUOTE Lint & Fix Agent
 */

const fs = require('fs');
const path = require('path');

// Fichiers à ignorer (logs et tests)
const IGNORE_PATTERNS = [
    /node_modules/,
    /\.git/,
    /reports/,
    /logs/,
    /test.*\.js$/,
    /test.*\.ts$/,
    /.*\.test\.js$/,
    /.*\.spec\.js$/,
    /scan-.*\.js$/,
    /agent-.*-monitor\.js$/,
];

// Types de console à traiter
const CONSOLE_TYPES = ['log', 'info', 'warn', 'error', 'debug'];

function shouldIgnoreFile(filePath) {
    return IGNORE_PATTERNS.some(pattern => pattern.test(filePath));
}

function removeConsoleLogs(content) {
    let lines = content.split('\n');
    let inBlockComment = false;
    let result = [];
    let changes = 0;

    for (let i = 0; i < lines.length; i++) {
        let line = lines[i];

        // Détecter début/fin de bloc de commentaires
        if (line.includes('/*')) {
            inBlockComment = true;
        }
        if (line.includes('*/')) {
            inBlockComment = false;
        }

        // Ignorer les lignes dans les commentaires de bloc
        if (inBlockComment) {
            result.push(line);
            continue;
        }

        // Ignorer les lignes de commentaires sur une seule ligne
        if (line.trim().startsWith('//')) {
            result.push(line);
            continue;
        }

        // Supprimer console.log, console.info, console.warn, console.error, console.debug
        let modifiedLine = line;
        let found = false;

        CONSOLE_TYPES.forEach(type => {
            const pattern = new RegExp(`console\\.${type}\\s*\\(`, 'g');
            if (pattern.test(modifiedLine)) {
                modifiedLine = modifiedLine.replace(pattern, '// console.' + type + '(');
                found = true;
            }
        });

        if (found) {
            changes++;
        }

        result.push(modifiedLine);
    }

    return {
        content: result.join('\n'),
        changes: changes
    };
}

function processFile(filePath) {
    try {
        const content = fs.readFileSync(filePath, 'utf8');
        const { content: newContent, changes } = removeConsoleLogs(content);

        if (changes > 0) {
            fs.writeFileSync(filePath, newContent, 'utf8');
            console.log(`✅ ${filePath}: ${changes} console.* statements commented out`);
            return changes;
        }
        return 0;
    } catch (error) {
        console.log(`❌ Error processing ${filePath}: ${error.message}`);
        return 0;
    }
}

function scanDirectory(dir) {
    let totalChanges = 0;
    let filesProcessed = 0;

    const items = fs.readdirSync(dir);

    for (const item of items) {
        const fullPath = path.join(dir, item);
        const stat = fs.statSync(fullPath);

        if (shouldIgnoreFile(fullPath)) {
            continue;
        }

        if (stat.isDirectory()) {
            totalChanges += scanDirectory(fullPath);
        } else if (stat.isFile()) {
            const ext = path.extname(item);
            if (['.js', '.ts'].includes(ext)) {
                const changes = processFile(fullPath);
                if (changes > 0) {
                    totalChanges += changes;
                    filesProcessed++;
                }
            }
        }
    }

    return totalChanges;
}

console.log('🧹 NOVAQUOTE Console Log Remover');
console.log('=' .repeat(60));

const projectRoot = path.join(__dirname, '..');
const totalChanges = scanDirectory(projectRoot);

console.log('=' .repeat(60));
console.log(`✅ Total: ${totalChanges} console.* statements commented out`);
console.log('🎯 Code cleanup completed!');
