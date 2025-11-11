/**
 * Client WebSocket simple pour tester la connectivité NOVAQUOTE
 * Se connecte au port 7001 pour activer le statut WebSocket
 */

const WebSocket = require('ws');

console.log('🔌 Connexion au WebSocket NOVAQUOTE...');

const ws = new WebSocket('ws://localhost:7001');

ws.on('open', () => {
  console.log('✅ WebSocket connecté !');
  console.log('📡 Client actif pour NOVAQUOTE');

  // Envoyer un message ping
  ws.send(JSON.stringify({
    type: 'ping',
    timestamp: new Date().toISOString()
  }));
});

ws.on('message', (data) => {
  console.log('📨 Message reçu:', data.toString());
});

ws.on('error', (error) => {
  console.error('❌ Erreur WebSocket:', error.message);
});

ws.on('close', () => {
  console.log('🔌 WebSocket déconnecté');
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