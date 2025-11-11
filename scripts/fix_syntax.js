// Script pour corriger la syntaxe de server-backend.ts
const fs = require('fs');
const path = require('path');

const filePath = 'backend/server-backend.ts';
const content = fs.readFileSync(filePath, 'utf8');

let fixed = content
  // Corriger les objets mal formés avec ;
  .replace(/{\s*;/g, '{\n  ')
  .replace(/,\s*;/g, ',\n  ')
  // Corriger les assignations incomplètes
  .replace(/const \w+\s*=\s*;\s*\n/g, '')
  // Corriger les map() avec ; avant {
  .replace(/\)\s*=>\s*{;/g, ') => {')
  // Corriger les accolades orphelines
  .replace(/};\s*\n\s*};/g, '}\n  };')
  // Corriger les objets avec des propriétés mal séparées
  .replace(/},\s*;/g, '},\n  ')
  // Corriger les parenthèses mal fermées
  .replace(/\)\s*;\s*\n/g, ') => {\n  ')
  // Corriger les try-catch
  .replace(/}\s*;\s*\n\s*catch/g, '}\n    catch')
  // Corriger les Promise avec ;
  .replace(/Promise<resolve>\s*=>\s*{;/g, 'Promise((resolve) => {');

fs.writeFileSync(filePath, fixed);
console.log('✅ Syntaxe corrigée dans server-backend.ts');
