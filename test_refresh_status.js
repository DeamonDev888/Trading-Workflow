#!/usr/bin/env node
/**
 * TEST: Refresh Status Button
 * Vérifie que la fonction refreshAllAgentStatus() est définie et accessible
 */

const fs = require('fs');
const path = require('path');

console.log('\n' + '='.repeat(70));
console.log('  🔍 TEST: Refresh Status Button Function');
console.log('='.repeat(70) + '\n');

// Lire le fichier index.html
const indexPath = path.join(__dirname, 'frontend', 'public', 'index.html');
const content = fs.readFileSync(indexPath, 'utf8');

// Vérifier que la fonction refreshAllAgentStatus existe
const hasFunction = content.includes('function refreshAllAgentStatus()');
console.log(
  `✓ Function refreshAllAgentStatus() exists: ${hasFunction ? '✅ YES' : '❌ NO'}`
);

// Vérifier que le bouton l'appelle
const hasButtonCall = content.includes('onclick="refreshAllAgentStatus()"');
console.log(
  `✓ Button calls refreshAllAgentStatus(): ${hasButtonCall ? '✅ YES' : '❌ NO'}`
);

// Vérifier qu'elle appelle checkAgentStatus
const callsCheckAgent = content.includes('await checkAgentStatus()');
console.log(
  `✓ Function calls checkAgentStatus(): ${callsCheckAgent ? '✅ YES' : '❌ NO'}`
);

// Vérifier les notifications
const hasNotifications = content.includes('showNotification');
console.log(
  `✓ Function shows notifications: ${hasNotifications ? '✅ YES' : '❌ NO'}`
);

// Test API backend
const { spawn } = require('child_process');

async function testAPI() {
  return new Promise((resolve) => {
    const curl = spawn('curl', [
      '-s',
      'http://localhost:7000/api/agents/status',
    ]);

    let output = '';
    curl.stdout.on('data', (data) => {
      output += data.toString();
    });

    curl.on('close', (code) => {
      if (code === 0) {
        try {
          const data = JSON.parse(output);
          console.log(`✓ Backend API responds: ✅ YES`);
          console.log(`  - Total agents: ${data.agents?.length || 0}`);
          console.log(`  - Active agents: ${data.summary?.active || 0}`);
          console.log(
            `  - System status: ${data.summary?.systemStatus || 'UNKNOWN'}`
          );
          resolve(true);
        } catch (e) {
          console.log(`✓ Backend API responds: ⚠️  YES (but invalid JSON)`);
          resolve(true);
        }
      } else {
        console.log(`✓ Backend API responds: ❌ NO (exit code ${code})`);
        resolve(false);
      }
    });
  });
}

async function main() {
  const apiWorks = await testAPI();

  console.log('\n' + '-'.repeat(70));

  if (hasFunction && hasButtonCall && callsCheckAgent && apiWorks) {
    console.log('\n✅ ALL CHECKS PASSED');
    console.log('   The Refresh Status button should work correctly!\n');
    process.exit(0);
  } else {
    console.log('\n❌ SOME CHECKS FAILED');
    console.log('   The Refresh Status button may not work properly.\n');
    process.exit(1);
  }
}

main();
