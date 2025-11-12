/**
 * Client WebSocket simple pour tester la connectivité NOVAQUOTE
 * Se connecte au port 7001 pour activer le statut WebSocket
 */

const WebSocket = require('ws');

console.info('🔌 Connexion au WebSocket NOVAQUOTE...');

const ws = new WebSocket('ws://localhost:7001');

ws.on('open', () => {
  console.info('✅ WebSocket connecté !');
  console.info('📡 Client actif pour NOVAQUOTE');

  // Envoyer un message ping
  ws.send(JSON.stringify({
    type: 'ping',
    timestamp: new Date().toISOString()
  }));
});

ws.on('message', (data) => {
  console.info('📨 Message reçu:', data.toString());
});

ws.on('error', (error) => {
  console.error('❌ Erreur WebSocket:', error.message);
});

ws.on('close', () => {
  console.info('🔌 WebSocket déconnecté');
});

// Garder la connexion alive
setInterval(() => {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({
      type: 'ping',
      timestamp: new Date().toISOString()
    }));
  }
}, 30000); // Ping toutes les 30s