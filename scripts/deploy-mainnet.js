#!/usr/bin/env node

/**
 * 🚀 NOVAQUOTE MAINNET DEPLOYMENT SCRIPT
 * Déploiement sécurisé pour le trading avec argent réel
 * Built with love by Deamon Dev [START]
 */

const fs = require('fs');
const path = require('path');

console.log('🚀 NOVAQUOTE MAINNET DEPLOYMENT SCRIPT');
console.log('=====================================\n');

// Vérifications de sécurité
function safetyChecks() {
  console.log('🔒 Vérifications de sécurité...');

  // Vérifier si .env.mainnet existe
  if (!fs.existsSync('.env.mainnet')) {
    console.error('❌ ERREUR: .env.mainnet n\'existe pas');
    console.log('   Veuillez créer .env.mainnet à partir de .env.mainnet.example');
    process.exit(1);
  }

  // Vérifier si .env actuel est paper trading
  const currentEnv = fs.existsSync('.env') ? fs.readFileSync('.env', 'utf8') : '';
  if (currentEnv.includes('HYPERLIQUID_TESTNET=false') && !currentEnv.includes('your_eth_private_key_here')) {
    console.error('❌ ERREUR: Vous êtes déjà en mode MAINNET!');
    console.log('   Annulation du déploiement pour éviter les doublons');
    process.exit(1);
  }

  console.log('✅ Vérifications de sécurité passées\n');
}

// Sauvegarde de la configuration actuelle
function backupCurrentConfig() {
  console.log('💾 Sauvegarde de la configuration actuelle...');

  if (fs.existsSync('.env')) {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const backupPath = `.env.backup.${timestamp}`;
    fs.copyFileSync('.env', backupPath);
    console.log(`   ✅ Sauvegardé dans: ${backupPath}`);
  }

  console.log('✅ Sauvegarde complétée\n');
}

// Configuration mainnet
function setupMainnetConfig() {
  console.log('⚙️ Configuration du mode mainnet...');

  // Copier .env.mainnet vers .env
  fs.copyFileSync('.env.mainnet', '.env');
  console.log('   ✅ Configuration mainnet appliquée');

  // Vérifier que la clé privée n'est pas le placeholder
  const envContent = fs.readFileSync('.env', 'utf8');
  if (envContent.includes('votre_eth_private_key_ici_64_caracteres_hex')) {
    console.error('❌ ERREUR: Vous devez configurer votre clé privée Ethereum');
    console.log('   Éditez .env et remplacez "votre_eth_private_key_ici_64_caracteres_hex" par votre VRAIE clé');

    // Restaurer la config précédente
    if (fs.existsSync('.env.backup')) {
      fs.copyFileSync('.env.backup', '.env');
      console.log('   ✅ Configuration paper trading restaurée');
    }
    process.exit(1);
  }

  console.log('   ✅ Clé privée configurée');
  console.log('✅ Configuration mainnet prête\n');
}

// Avertissements finaux
function finalWarnings() {
  console.log('⚠️  AVERTISSEMENTS IMPORTANTS:');
  console.log('   • Vous êtes sur le point de trader avec de l\'argent VRAI');
  console.log('   • Les pertes peuvent aller jusqu\'à 100% de votre capital');
  console.log('   • Le trading crypto est extrêmement volatile');
  console.log('   • Surveillez attentivement les premières heures de trading');
  console.log('   • Ayez un plan de gestion des risques clair\n');

  console.log('📊 RECOMMANDATIONS:');
  console.log('   1. Commencez avec un petit capital (< 1% de votre portefeuille)');
  console.log('   2. Surveillez les logs en temps réel');
  console.log('   3. Arrêtez immédiatement si vous voyez des comportements anormaux');
  console.log('   4. Gardez un œil sur les frais de funding');
  console.log('   5. Testez en paper trading pendant au moins 1 semaine avant\n');
}

// Instructions post-déploiement
function postDeploymentInstructions() {
  console.log('🚀 DÉPLOIEMENT MAINNET RÉUSSI!');
  console.log('=====================================\n');

  console.log('📋 PROCHAINES ÉTAPES:');
  console.log('1. Vérifiez votre solde sur HyperLiquid');
  console.log('2. Démarrer le système: npm run dev');
  console.log('3. Surveillez l\'interface: http://localhost:9001');
  console.log('4. Démarrer l\'auto-trading manuellement au début');
  console.log('5. Surveillez les premiers trades attentivement\n');

  console.log('🔐 COMMANDES D\'URGENCE:');
  console.log('• Arrêter tout: Ctrl+C');
  console.log('• Revenir en paper: copiez .env.backup vers .env');
  console.log('• Vérifier les logs: tail -f logs/trading.log\n');

  console.log('📞 SUPPORT ET MONITORING:');
  console.log('• Logs système: http://localhost:7000/api/health');
  console.log('• Stats trading: http://localhost:7000/api/trading/stats');
  console.log('• Positions actives: http://localhost:7000/api/positions\n');
}

// Fonction principale
function main() {
  try {
    safetyChecks();
    backupCurrentConfig();
    setupMainnetConfig();
    finalWarnings();
    postDeploymentInstructions();

  } catch (error) {
    console.error('❌ ERREUR LORS DU DÉPLOIEMENT:', error.message);
    process.exit(1);
  }
}

// Confirmation utilisateur
if (process.argv.includes('--force')) {
  console.log('🔓 Mode forcé activé - déploiement direct...\n');
  main();
} else {
  console.log('⚠️  CE SCRIPT VA CONFIGURER LE TRADING AVEC ARGENT RÉEL');
  console.log('   Êtes-vous absolument sûr de vouloir continuer?');
  console.log('   Tapez "OUI" en majuscules pour confirmer: ');

  process.stdin.setEncoding('utf8');
  process.stdin.on('readable', () => {
    const chunk = process.stdin.read();
    if (chunk !== null) {
      const confirmation = chunk.trim();
      if (confirmation === 'OUI') {
        console.log('\n✅ Confirmation reçue - Déploiement mainnet en cours...\n');
        main();
      } else {
        console.log('\n❌ Déploiement annulé - Vous avez tapé:', confirmation);
        process.exit(0);
      }
    }
  });
}