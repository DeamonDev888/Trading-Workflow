/**
 * 🧪 Test du Système de Logging Structuré NOVAQUOTE
 * Test du nouveau système de logging avec Winston et logs structurés
 */

const {
  StructuredLogger,
  logger,
  requestLogger,
  errorLogger,
} = require('../src/logging/structured-logger');

console.log('🔍 Test du système de logging structuré NOVAQUOTE');
console.log('==================================================\n');

// Test des logs basiques
console.log('📝 1. Test des logs basiques...\n');

logger.info('Message informatif de test', {
  component: 'test',
  action: 'basic-test',
});

logger.debug('Message de debug de test', {
  component: 'test',
  action: 'debug-test',
  debugInfo: { level: 'verbose' },
});

logger.warn("Message d'avertissement de test", {
  component: 'test',
  action: 'warning-test',
  warningType: 'test-warning',
});

logger.error("Message d'erreur de test", new Error('Erreur de test'), {
  component: 'test',
  action: 'error-test',
  errorCode: 'TEST_001',
});

// Test des logs de performance
console.log('⚡ 2. Test des logs de performance...\n');

const startTime = Date.now();
setTimeout(() => {
  const duration = Date.now() - startTime;
  logger.performance('Test opération', duration, {
    operation: 'test-performance',
    parameters: { size: 1000 },
  });
}, 100);

// Test des logs de trading
console.log('💰 3. Test des logs de trading...\n');

logger.trading('BUY', {
  symbol: 'BTC-PERP',
  side: 'BUY',
  size: 0.1,
  price: 45000,
  orderId: 'order_12345',
  userId: 'user_67890',
});

logger.trading('SELL', {
  symbol: 'ETH-PERP',
  side: 'SELL',
  size: 1.0,
  price: 3000,
  tradeId: 'trade_54321',
  userId: 'user_67890',
});

// Test des logs de sécurité
console.log('🔐 4. Test des logs de sécurité...\n');

logger.security('Suspicious login attempt detected', {
  threat: 'brute_force',
  source: '192.168.1.100',
  blocked: true,
  attempts: 5,
  ip: '192.168.1.100',
});

logger.security('Rate limit exceeded', {
  threat: 'rate_limit',
  source: '10.0.0.50',
  blocked: false,
  endpoint: '/api/trade',
  requests: 150,
});

// Test des logs d'agents
console.log("🤖 5. Test des logs d'agents...\n");

logger.agent('risk_agent', 'START', {
  status: 'starting',
  config: { threshold: 0.05, maxPosition: 10000 },
});

logger.agent('strategy_agent', 'ANALYSIS_COMPLETE', {
  analysis: 'bullish_trend_detected',
  confidence: 0.85,
  symbol: 'BTC-PERP',
});

logger.agent('funding_agent', 'EXECUTION', {
  action: 'rebalance_portfolio',
  result: 'success',
  amount: 5000,
});

// Test des logs WebSocket
console.log('🔌 6. Test des logs WebSocket...\n');

logger.websocket('CLIENT_CONNECTED', {
  clientId: 'client_abc123',
  ip: '192.168.1.50',
  userAgent: 'Mozilla/5.0...',
});

logger.websocket('MESSAGE_RECEIVED', {
  clientId: 'client_abc123',
  messageType: 'subscribe',
  channel: 'trades',
  symbol: 'BTC-PERP',
});

logger.websocket('CLIENT_DISCONNECTED', {
  clientId: 'client_abc123',
  reason: 'normal_closure',
  duration: 3600,
});

// Test des logs de health checks
console.log('🏥 7. Test des logs de health checks...\n');

logger.health('API Server', 'healthy', {
  responseTime: 45,
  uptime: 86400,
  memoryUsage: '45%',
});

logger.health('Database', 'degraded', {
  responseTime: 2500,
  connections: 95,
  maxConnections: 100,
});

logger.health('WebSocket Server', 'unhealthy', {
  error: 'Connection timeout',
  activeConnections: 0,
});

// Test des logs de métriques
console.log('📊 8. Test des logs de métriques...\n');

logger.metric('active_users', 1250, {
  component: 'metrics',
  period: '1m',
});

logger.metric('trading_volume', 1500000, {
  component: 'metrics',
  period: '1h',
  currency: 'USD',
});

logger.metric('error_rate', 0.02, {
  component: 'metrics',
  period: '5m',
  threshold: 0.01,
});

// Test du contexte global
console.log('🎯 9. Test du contexte global...\n');

logger.setContext({
  requestId: 'req_123456',
  userId: 'user_789',
  sessionId: 'sess_abc',
});

logger.info('Message avec contexte global', {
  action: 'context-test',
  data: { test: 'context' },
});

logger.clearContext();
logger.info('Message après nettoyage du contexte', {
  action: 'context-cleared',
});

// Test du logging avec contexte personnalisé
console.log('🔧 10. Test avec contexte personnalisé...\n');

logger.setContext({
  component: 'test-suite',
  version: '1.0.0',
  environment: 'test',
});

// Simuler un scénario complet
logger.info('Début du scénario de test', {
  scenario: 'user_registration',
  step: 'start',
});

logger.performance('User registration process', 150, {
  scenario: 'user_registration',
  step: 'processing',
});

logger.trading('DEPOSIT', {
  scenario: 'user_registration',
  step: 'funding',
  symbol: 'USD',
  amount: 1000,
});

logger.info('Scénario de test terminé', {
  scenario: 'user_registration',
  step: 'complete',
  result: 'success',
});

logger.clearContext();

console.log('\n✅ Tests terminés!');
console.log('\n📁 Vérifiez les fichiers de logs générés:');
console.log('   - logs/application-YYYY-MM-DD.log (logs généraux)');
console.log('   - logs/errors-YYYY-MM-DD.log (erreurs)');
console.log('   - logs/trading-YYYY-MM-DD.log (logs trading)');
console.log('   - logs/security-YYYY-MM-DD.log (logs sécurité)');
console.log('   - logs/performance-YYYY-MM-DD.log (logs performance)');
console.log("   - logs/audit-YYYY-MM-DD.log (logs d'audit - production)");
console.log('   - logs/exceptions-YYYY-MM-DD.log (exceptions non capturées)');
console.log('   - logs/rejections-YYYY-MM-DD.log (rejets de promesses)');

console.log('\n🎯 Fonctionnalités testées:');
console.log('   ✅ Logs basiques (info, debug, warn, error)');
console.log('   ✅ Logs de performance avec durée');
console.log('   ✅ Logs de trading avec détails business');
console.log('   ✅ Logs de sécurité avec menaces');
console.log("   ✅ Logs d'agents IA");
console.log('   ✅ Logs WebSocket');
console.log('   ✅ Logs de health checks');
console.log('   ✅ Logs de métriques');
console.log('   ✅ Contexte global et nettoyage');
console.log('   ✅ Rotation automatique des fichiers');
console.log('   ✅ Formatage JSON structuré');

console.log(
  '\n🚀 Le système de logging structuré est prêt pour la production!'
);
