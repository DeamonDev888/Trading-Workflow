/**
 * 🚀 AGENT EXPERT LOGS NOVAQUOTE - Dashboard Monitoring Temps Réel
 * Spécialiste du monitoring et analyse temps réel de tous les logs du système NOVAQUOTE
 *
 * Mission: Surveillance temps réel des patterns NOVAQUOTE, détection anomalies, performance système
 */

const fs = require('fs');
const path = require('path');
const http = require('http');
const ws = require('ws');

// Configuration NOVAQUOTE - Chemins corrigés
const NOVAQUOTE_LOGS_DIR = path.join(__dirname, '..', 'logs');
const NOVAQUOTE_BACKEND_PORT = 7000;
const NOVAQUOTE_WEBSOCKET_PORT = 7001;
const AGENT_LOGS_PORT = 9004;

// Ajouter Winston pour le monitoring
const winston = require('winston');
const DailyRotateFile = require('winston-daily-rotate-file');

// Créer un logger Winston pour le monitoring
const monitorLogger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      )
    }),
    new DailyRotateFile({
      filename: path.join(__dirname, '..', 'logs', 'agent-monitor-%DATE%.log'),
      datePattern: 'YYYY-MM-DD',
      maxSize: '20m',
      maxFiles: '14d'
    })
  ]
});

// Patterns NOVAQUOTE à surveiller
const NOVAQUOTE_PATTERNS = {
  SUCCESS: [
    /\[SUCCESS\] \[SYSTEM\] ✅ HyperLiquid modules loaded successfully/,
    /\[RESPONSE\] \[API\] \/api\/health → 200/,
    /✅.*Agent.*started/,
    /🚀.*system.*ready/
  ],
  ERRORS: [
    /\[ERROR\] \[.*\] ❌/,
    /failed.*to.*load/,
    /connection.*timeout/,
    /unable.*to.*connect/
  ],
  WARNINGS: [
    /\[WARN\] \[.*\] ⚠️/,
    /deprecated/,
    /retry.*attempt/
  ],
  PERFORMANCE: [
    /performance.*ms/,
    /response.*time/,
    /duration.*ms/
  ],
  TRADING: [
    /trading.*order/,
    /buy.*signal/,
    /sell.*signal/,
    /position.*opened/,
    /position.*closed/
  ],
  AGENTS: [
    /agent.*started/,
    /agent.*stopped/,
    /risk.*analysis/,
    /strategy.*execution/,
    /funding.*arbitrage/
  ],
  WEBSOCKET: [
    /websocket.*connected/,
    /websocket.*disconnected/,
    /client.*connected/,
    /subscription.*received/
  ]
};

class NovaQuoteLogsMonitor {
  constructor() {
    this.logsData = {
      total: 0,
      success: 0,
      errors: 0,
      warnings: 0,
      trading: 0,
      agents: 0,
      websocket: 0,
      performance: 0
    };

    this.systemStatus = {
      backend: false,
      frontend: false,
      websocket: false,
      agents: {
        hyperliquid: false,
        risk: false,
        funding: false,
        strategy: false
      }
    };

    this.recentLogs = [];
    this.alerts = [];
    this.metrics = {
      uptime: 0,
      responseTime: 0,
      memoryUsage: 0,
      activeConnections: 0
    };

    this.startMonitoring();
  }

  async startMonitoring() {
    console.log('\n🚀 ===============================================');
    console.log('📊 NOVAQUOTE AGENT EXPERT LOGS - MONITORING');
    console.log('==============================================\n');

    // Démarrer le monitoring des logs
    this.monitorLogs();

    // Démarrer le monitoring des services
    this.startServicesMonitoring();

    // Démarrer le serveur WebSocket pour le dashboard
    this.startWebSocketServer();

    // Démarrer le serveur HTTP pour le dashboard
    this.startHTTPServer();

    // Afficher le statut initial
    this.printInitialStatus();
  }

  monitorLogs() {
    monitorLogger.info('📋 Démarrage monitoring des logs NOVAQUOTE...', {
      logsDir: NOVAQUOTE_LOGS_DIR,
      timestamp: new Date().toISOString()
    });

    // Scanner les logs existants
    this.scanExistingLogs();

    // Surveillance continue des fichiers de logs
    setInterval(() => {
      this.scanExistingLogs();
    }, 5000); // Scan toutes les 5 secondes
  }

  scanExistingLogs() {
    try {
      if (!fs.existsSync(NOVAQUOTE_LOGS_DIR)) {
        monitorLogger.warn('📁 Répertoire de logs non trouvé', { logsDir: NOVAQUOTE_LOGS_DIR });
        return;
      }

      const logFiles = fs.readdirSync(NOVAQUOTE_LOGS_DIR).filter(file => file.endsWith('.log'));

      monitorLogger.info('📂 Analyse des fichiers de logs...', {
        logFilesCount: logFiles.length,
        logFiles: logFiles
      });

      logFiles.forEach(file => {
        const filePath = path.join(NOVAQUOTE_LOGS_DIR, file);
        const stats = fs.statSync(filePath);

        // Lire les dernières lignes du fichier
        const content = fs.readFileSync(filePath, 'utf8');
        const lines = content.split('\n').filter(line => line.trim());

        // Analyser les logs JSON structurés
        lines.forEach(line => {
          this.analyzeLogLine(line, file, stats);
        });
      });

      // Mettre à jour le statut du système
      this.updateSystemStatus();

    } catch (error) {
      monitorLogger.error('❌ Erreur lors de l\'analyse des logs', {
        error: error.message,
        stack: error.stack
      });
    }
  }

  analyzeLogLine(line, fileName, stats) {
    try {
      // Analyser si c'est un log JSON (format NOVAQUOTE)
      if (line.startsWith('{') && line.endsWith('}')) {
        const logEntry = JSON.parse(line);
        this.processNovaQuoteLog(logEntry, fileName, stats);
      } else {
        // Analyser les logs texte traditionnels
        this.processTextLog(line, fileName, stats);
      }
    } catch (error) {
      // Ignorer les erreurs de parsing JSON
      this.logsData.errors++;
    }
  }

  processNovaQuoteLog(logEntry, fileName, stats) {
    try {
      this.logsData.total++;

      // Catégoriser par niveau de log
      switch (logEntry.level?.toUpperCase()) {
        case 'SUCCESS':
        case 'SUCCESSFUL':
        case 'OK':
          this.logsData.success++;
          break;
        case 'ERROR':
        case 'FATAL':
        case 'CRITICAL':
          this.logsData.errors++;
          monitorLogger.error('🚨 Erreur critique détectée', {
            logEntry,
            fileName,
            timestamp: logEntry.timestamp
          });
          break;
        case 'WARNING':
        case 'WARN':
          this.logsData.warnings++;
          break;
        case 'TRADE':
        case 'RISK':
          this.logsData.trading++;
          break;
        case 'AGENT':
        case 'MASTER_AGENT':
        case 'RISK_AGENT':
        case 'STRATEGY_AGENT':
        case 'FUNDING_AGENT':
          this.logsData.agents++;
          break;
        case 'WEBSOCKET':
          this.logsData.websocket++;
          break;
        case 'PERFORMANCE':
          this.logsData.performance++;
          break;
        default:
          // Logs INFO ne nécessitent pas de comptage spécial
          break;
      }

      // Log spécifique pour les metrics de performance
      if (logEntry.duration || logEntry.responseTime) {
        this.logsData.performance++;
      }

      // Log des événements système importants
      if (logEntry.event) {
        monitorLogger.info('🔄 Événement système', {
          event: logEntry.event,
          agent: logEntry.logger_name,
          timestamp: logEntry.timestamp
        });
      }

    } catch (error) {
      monitorLogger.error('❌ Erreur traitement log JSON', {
        logEntry,
        error: error.message
      });
    }
  }

  updateSystemStatus() {
    try {
      // Calculer le health score basé sur les métriques de logs
      const totalLogs = this.logsData.total;
      const errorRate = totalLogs > 0 ? (this.logsData.errors / totalLogs) * 100 : 0;

      // Déterminer l'état de santé global
      if (errorRate > 10) {
        this.systemStatus.health = 'CRITICAL';
        this.addAlert('ERROR', {
          message: `Taux d'erreurs critique: ${errorRate.toFixed(2)}%`,
          category: 'SYSTEM_HEALTH',
          timestamp: new Date().toISOString()
        });
      } else if (errorRate > 5) {
        this.systemStatus.health = 'WARNING';
      } else if (errorRate > 1) {
        this.systemStatus.health = 'CAUTION';
      } else {
        this.systemStatus.health = 'HEALTHY';
      }

      // Logger le statut système avec Winston
      monitorLogger.info('📊 Mise à jour statut système', {
        health: this.systemStatus.health,
        errorRate: `${errorRate.toFixed(2)}%`,
        totalLogs,
        errors: this.logsData.errors,
        warnings: this.logsData.warnings,
        timestamp: new Date().toISOString()
      });

      // Performance monitoring
      if (this.logsData.performance > 0) {
        monitorLogger.debug('⚡ Performance monitoring', {
          performanceLogs: this.logsData.performance,
          tradingActivity: this.logsData.trading,
          agentActivity: this.logsData.agents
        });
      }

    } catch (error) {
      monitorLogger.error('❌ Erreur mise à jour statut système', {
        error: error.message,
        stack: error.stack
      });
    }
  }

  processTextLog(line, fileName, stats) {
    try {
      this.logsData.total++;

      // Analyse des patterns texte pour logs non-JSON
      for (const [category, patterns] of Object.entries(NOVAQUOTE_PATTERNS)) {
        for (const pattern of patterns) {
          if (pattern.test(line)) {
            switch (category) {
              case 'SUCCESS':
                this.logsData.success++;
                break;
              case 'ERRORS':
                this.logsData.errors++;
                monitorLogger.error('🚨 Erreur texte détectée', { line, fileName });
                this.addTextAlert('ERROR', line, fileName);
                break;
              case 'WARNINGS':
                this.logsData.warnings++;
                this.addTextAlert('WARNING', line, fileName);
                break;
              case 'TRADING':
                this.logsData.trading++;
                break;
              case 'AGENTS':
                this.logsData.agents++;
                break;
              case 'WEBSOCKET':
                this.logsData.websocket++;
                break;
              case 'PERFORMANCE':
                this.logsData.performance++;
                break;
            }
            break; // Sortir après première correspondance
          }
        }
      }
    } catch (error) {
      monitorLogger.error('❌ Erreur analyse log texte', { error: error.message });
    }
  }

  addTextAlert(type, message, fileName) {
    const alert = {
      type,
      message: message.substring(0, 200), // Limiter la longueur
      category: 'TEXT_LOG',
      file: fileName,
      timestamp: new Date().toISOString(),
      severity: type === 'ERROR' ? 'HIGH' : 'MEDIUM'
    };

    this.alerts.unshift(alert);

    // Limiter le nombre d'alerts
    if (this.alerts.length > 50) {
      this.alerts = this.alerts.slice(0, 50);
    }
  }

  async startServicesMonitoring() {
    console.log('🔍 Démarrage monitoring des services NOVAQUOTE...');

    setInterval(async () => {
      await this.checkBackendHealth();
      await this.checkFrontendHealth();
      await this.checkAgentsStatus();
    }, 10000); // Vérification toutes les 10 secondes
  }

  async checkBackendHealth() {
    try {
      const http = require('http');

      const options = {
        hostname: 'localhost',
        port: NOVAQUOTE_BACKEND_PORT,
        path: '/api/health',
        method: 'GET',
        timeout: 5000
      };

      const req = http.request(options, (res) => {
        let data = '';

        res.on('data', (chunk) => {
          data += chunk;
        });

        res.on('end', () => {
          try {
            const health = JSON.parse(data);
            this.systemStatus.backend = health.status === 'healthy';
            this.systemStatus.websocket = health.services?.websocket || false;
            this.metrics.uptime = health.uptime || 0;
            this.metrics.responseTime = Date.now() - req.startTime;
          } catch (e) {
            this.systemStatus.backend = false;
          }
        });
      });

      req.startTime = Date.now();

      req.on('error', () => {
        this.systemStatus.backend = false;
      });

      req.on('timeout', () => {
        req.destroy();
        this.systemStatus.backend = false;
      });

      req.end();

    } catch (error) {
      this.systemStatus.backend = false;
    }
  }

  async checkFrontendHealth() {
    try {
      const http = require('http');

      const options = {
        hostname: 'localhost',
        port: 9001,
        path: '/',
        method: 'GET',
        timeout: 5000
      };

      const req = http.request(options, (res) => {
        let data = '';

        res.on('data', (chunk) => {
          data += chunk;
        });

        res.on('end', () => {
          // Si on reçoit du HTML, le frontend fonctionne
          this.systemStatus.frontend = data.includes('<!doctype html>') || data.includes('<html');
        });
      });

      req.on('error', () => {
        this.systemStatus.frontend = false;
      });

      req.on('timeout', () => {
        req.destroy();
        this.systemStatus.frontend = false;
      });

      req.end();

    } catch (error) {
      this.systemStatus.frontend = false;
    }
  }

  async checkAgentsStatus() {
    try {
      const http = require('http');

      const options = {
        hostname: 'localhost',
        port: NOVAQUOTE_BACKEND_PORT,
        path: '/api/agents',
        method: 'GET',
        timeout: 5000
      };

      const req = http.request(options, (res) => {
        let data = '';

        res.on('data', (chunk) => {
          data += chunk;
        });

        res.on('end', () => {
          try {
            const apiResponse = JSON.parse(data);
            if (apiResponse.agents) {
              apiResponse.agents.forEach(agent => {
                switch (agent.id) {
                  case 'hyperliquid':
                    this.systemStatus.agents.hyperliquid = agent.status === 'active';
                    break;
                  case 'risk':
                    this.systemStatus.agents.risk = agent.status === 'active';
                    break;
                  case 'funding':
                    this.systemStatus.agents.funding = agent.status === 'active';
                    break;
                  case 'strategy':
                    this.systemStatus.agents.strategy = agent.status === 'active';
                    break;
                }
              });
            }
          } catch (e) {
            // Erreur parsing API
          }
        });
      });

      req.on('error', () => {
        // API non disponible
      });

      req.on('timeout', () => {
        req.destroy();
      });

      req.end();

    } catch (error) {
      // Erreur monitoring agents
    }
  }

  startWebSocketServer() {
    console.log(`🌐 Démarrage WebSocket Server sur port ${AGENT_LOGS_PORT}...`);

    this.wss = new ws.Server({ port: AGENT_LOGS_PORT });

    this.wss.on('connection', (ws) => {
      console.log('📊 Client dashboard connecté');

      // Envoyer l'état actuel
      this.sendDashboardUpdate(ws);

      // Envoyer les mises à jour toutes les secondes
      const interval = setInterval(() => {
        this.sendDashboardUpdate(ws);
      }, 1000);

      ws.on('close', () => {
        console.log('📊 Client dashboard déconnecté');
        clearInterval(interval);
      });

      ws.on('error', (error) => {
        console.error('❌ WebSocket error:', error.message);
      });
    });

    console.log(`✅ WebSocket Server démarré sur ws://localhost:${AGENT_LOGS_PORT}`);
  }

  sendDashboardUpdate(ws) {
    const update = {
      type: 'dashboard_update',
      timestamp: new Date().toISOString(),
      data: {
        logs: this.logsData,
        system: this.systemStatus,
        metrics: this.metrics,
        recentLogs: this.recentLogs.slice(0, 20),
        alerts: this.alerts.slice(0, 10)
      }
    };

    if (ws.readyState === ws.OPEN) {
      ws.send(JSON.stringify(update));
    }
  }

  startHTTPServer() {
    console.log(`🌐 Démarrage HTTP Server pour dashboard sur port ${AGENT_LOGS_PORT + 1}...`);

    const server = http.createServer((req, res) => {
      if (req.url === '/') {
        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.end(this.getDashboardHTML());
      } else if (req.url === '/api/status') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
          logs: this.logsData,
          system: this.systemStatus,
          metrics: this.metrics,
          recentLogs: this.recentLogs.slice(0, 50),
          alerts: this.alerts.slice(0, 20)
        }));
      } else {
        res.writeHead(404);
        res.end('Not Found');
      }
    });

    server.listen(AGENT_LOGS_PORT + 1, () => {
      console.log(`✅ Dashboard HTTP disponible sur http://localhost:${AGENT_LOGS_PORT + 1}`);
    });
  }

  getDashboardHTML() {
    return `<!DOCTYPE html>
<html>
<head>
    <title>🚀 NOVAQUOTE AGENT EXPERT LOGS</title>
    <meta charset="utf-8">
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: #0a0a0a; color: #fff; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { color: #00ff88; margin: 0; font-size: 2em; }
        .header p { color: #888; margin: 5px 0; }
        .dashboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card { background: #1a1a1a; border: 1px solid #333; border-radius: 8px; padding: 20px; }
        .card h3 { margin: 0 0 15px 0; color: #00ff88; }
        .metric { display: flex; justify-content: space-between; margin: 8px 0; padding: 8px; background: #0a0a0a; border-radius: 4px; }
        .metric .label { color: #888; }
        .metric .value { font-weight: bold; }
        .status-healthy { color: #00ff88; }
        .status-unhealthy { color: #ff4444; }
        .status-warning { color: #ffaa00; }
        .logs { font-family: 'Courier New', monospace; font-size: 12px; max-height: 400px; overflow-y: auto; }
        .log-entry { margin: 2px 0; padding: 4px; border-radius: 3px; }
        .log-info { background: #1a3a52; }
        .log-success { background: #1a5a3a; }
        .log-warning { background: #5a4a1a; }
        .log-error { background: #5a1a1a; }
        .alert { padding: 8px; margin: 5px 0; border-radius: 4px; border-left: 4px solid; }
        .alert-error { background: #5a1a1a; border-color: #ff4444; }
        .alert-warning { background: #5a4a1a; border-color: #ffaa00; }
        .real-time-indicator {
            position: fixed; top: 20px; right: 20px;
            background: #00ff88; color: #000;
            padding: 8px 16px; border-radius: 20px;
            font-weight: bold; animation: pulse 2s infinite;
        }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
    </style>
</head>
<body>
    <div class="real-time-indicator">🔴 LIVE</div>

    <div class="header">
        <h1>🚀 NOVAQUOTE AGENT EXPERT LOGS</h1>
        <p>Monitoring Temps Réel - Système de Trading HyperLiquid</p>
    </div>

    <div class="dashboard">
        <div class="card">
            <h3>📊 État Système</h3>
            <div class="metric">
                <span class="label">Backend API:</span>
                <span class="value" id="backend-status">Vérification...</span>
            </div>
            <div class="metric">
                <span class="label">WebSocket:</span>
                <span class="value" id="websocket-status">Vérification...</span>
            </div>
            <div class="metric">
                <span class="label">Uptime:</span>
                <span class="value" id="uptime">0s</span>
            </div>
            <div class="metric">
                <span class="label">Response Time:</span>
                <span class="value" id="response-time">0ms</span>
            </div>
        </div>

        <div class="card">
            <h3>🤖 Status Agents</h3>
            <div class="metric">
                <span class="label">HyperLiquid Agent:</span>
                <span class="value" id="agent-hyperliquid">Vérification...</span>
            </div>
            <div class="metric">
                <span class="label">Risk Agent:</span>
                <span class="value" id="agent-risk">Vérification...</span>
            </div>
            <div class="metric">
                <span class="label">Funding Agent:</span>
                <span class="value" id="agent-funding">Vérification...</span>
            </div>
            <div class="metric">
                <span class="label">Strategy Agent:</span>
                <span class="value" id="agent-strategy">Vérification...</span>
            </div>
        </div>

        <div class="card">
            <h3>📈 Statistiques Logs</h3>
            <div class="metric">
                <span class="label">Total Logs:</span>
                <span class="value" id="logs-total">0</span>
            </div>
            <div class="metric">
                <span class="label">Success:</span>
                <span class="value status-healthy" id="logs-success">0</span>
            </div>
            <div class="metric">
                <span class="label">Erreurs:</span>
                <span class="value status-unhealthy" id="logs-errors">0</span>
            </div>
            <div class="metric">
                <span class="label">Warnings:</span>
                <span class="value status-warning" id="logs-warnings">0</span>
            </div>
        </div>

        <div class="card">
            <h3>⚡ Activité Trading</h3>
            <div class="metric">
                <span class="label">Logs Trading:</span>
                <span class="value" id="logs-trading">0</span>
            </div>
            <div class="metric">
                <span class="label">Logs Agents:</span>
                <span class="value" id="logs-agents">0</span>
            </div>
            <div class="metric">
                <span class="label">WebSocket Events:</span>
                <span class="value" id="logs-websocket">0</span>
            </div>
            <div class="metric">
                <span class="label">Performance Logs:</span>
                <span class="value" id="logs-performance">0</span>
            </div>
        </div>

        <div class="card">
            <h3>🚨 Alerts Récentes</h3>
            <div id="alerts-container">
                <div class="metric">
                    <span class="label">Aucune alerte</span>
                </div>
            </div>
        </div>

        <div class="card">
            <h3>📋 Logs Récents</h3>
            <div id="logs-container" class="logs">
                <div class="metric">
                    <span class="label">Chargement des logs...</span>
                </div>
            </div>
        </div>
    </div>

    <script>
        const ws = new WebSocket('ws://localhost:${AGENT_LOGS_PORT}');

        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            if (data.type === 'dashboard_update') {
                updateDashboard(data.data);
            }
        };

        function updateDashboard(data) {
            // Mettre à jour les métriques
            document.getElementById('logs-total').textContent = data.logs.total;
            document.getElementById('logs-success').textContent = data.logs.success;
            document.getElementById('logs-errors').textContent = data.logs.errors;
            document.getElementById('logs-warnings').textContent = data.logs.warnings;
            document.getElementById('logs-trading').textContent = data.logs.trading;
            document.getElementById('logs-agents').textContent = data.logs.agents;
            document.getElementById('logs-websocket').textContent = data.logs.websocket;
            document.getElementById('logs-performance').textContent = data.logs.performance;

            // Mettre à jour le système
            document.getElementById('backend-status').innerHTML =
                '<span class="' + (data.system.backend ? 'status-healthy' : 'status-unhealthy') + '">' +
                (data.system.backend ? '✅ EN LIGNE' : '❌ HORS LIGNE') + '</span>';

            document.getElementById('websocket-status').innerHTML =
                '<span class="' + (data.system.websocket ? 'status-healthy' : 'status-unhealthy') + '">' +
                (data.system.websocket ? '✅ CONNECTÉ' : '❌ DÉCONNECTÉ') + '</span>';

            document.getElementById('uptime').textContent = Math.floor(data.metrics.uptime) + 's';
            document.getElementById('response-time').textContent = data.metrics.responseTime + 'ms';

            // Mettre à jour les agents
            document.getElementById('agent-hyperliquid').innerHTML =
                '<span class="' + (data.system.agents.hyperliquid ? 'status-healthy' : 'status-unhealthy') + '">' +
                (data.system.agents.hyperliquid ? '✅ ACTIF' : '❌ INACTIF') + '</span>';

            document.getElementById('agent-risk').innerHTML =
                '<span class="' + (data.system.agents.risk ? 'status-healthy' : 'status-unhealthy') + '">' +
                (data.system.agents.risk ? '✅ ACTIF' : '❌ INACTIF') + '</span>';

            document.getElementById('agent-funding').innerHTML =
                '<span class="' + (data.system.agents.funding ? 'status-healthy' : 'status-unhealthy') + '">' +
                (data.system.agents.funding ? '✅ ACTIF' : '❌ INACTIF') + '</span>';

            document.getElementById('agent-strategy').innerHTML =
                '<span class="' + (data.system.agents.strategy ? 'status-healthy' : 'status-unhealthy') + '">' +
                (data.system.agents.strategy ? '✅ ACTIF' : '❌ INACTIF') + '</span>';

            // Mettre à jour les alerts
            const alertsContainer = document.getElementById('alerts-container');
            if (data.alerts.length > 0) {
                alertsContainer.innerHTML = data.alerts.slice(0, 5).map(alert =>
                    '<div class="alert alert-' + alert.type.toLowerCase() + '">' +
                    '<strong>' + alert.type + '</strong>: ' + alert.message +
                    '<br><small>' + new Date(alert.timestamp).toLocaleString() + '</small>' +
                    '</div>'
                ).join('');
            } else {
                alertsContainer.innerHTML = '<div class="metric"><span class="label">✅ Aucune alerte active</span></div>';
            }

            // Mettre à jour les logs récents
            const logsContainer = document.getElementById('logs-container');
            if (data.recentLogs.length > 0) {
                logsContainer.innerHTML = data.recentLogs.slice(0, 20).map(log => {
                    const level = log.level || 'INFO';
                    const cssClass = 'log-' + level.toLowerCase();
                    return '<div class="log-entry ' + cssClass + '">' +
                        '<strong>' + level + '</strong> [' + (log.category || 'SYSTEM') + '] ' +
                        (log.message || 'No message') +
                        '<br><small>' + new Date(log.timestamp).toLocaleString() + '</small>' +
                        '</div>';
                }).join('');
            }
        }

        ws.onerror = function(error) {
            console.error('WebSocket error:', error);
        };

        // Auto-rafraîchissement
        setInterval(() => {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => updateDashboard(data))
                .catch(console.error);
        }, 5000);
    </script>
</body>
</html>`;
  }

  printInitialStatus() {
    console.log('\n📊 ===============================================');
    console.log('🎯 STATUT INITIAL SYSTÈME NOVAQUOTE');
    console.log('==============================================\n');

    console.log('🔍 Services Configuration:');
    console.log(`   • Backend API: http://localhost:${NOVAQUOTE_BACKEND_PORT}`);
    console.log(`   • WebSocket: ws://localhost:${NOVAQUOTE_WEBSOCKET_PORT}`);
    console.log(`   • Agent Logs: ws://localhost:${AGENT_LOGS_PORT}`);
    console.log(`   • Dashboard: http://localhost:${AGENT_LOGS_PORT + 1}`);

    console.log('\n📁 Logs Directory:', NOVAQUOTE_LOGS_DIR);
    console.log('📋 Monitoring Patterns:', Object.keys(NOVAQUOTE_PATTERNS).length, 'catégories');

    console.log('\n🚀 Dashboard Monitoring démarré!');
    console.log('   • Accès dashboard: http://localhost:' + (AGENT_LOGS_PORT + 1));
    console.log('   • WebSocket temps réel: ws://localhost:' + AGENT_LOGS_PORT);
    console.log('   • Monitoring 24/7 des logs NOVAQUOTE actif\n');
  }
}

// Démarrer l'Agent Expert Logs NOVAQUOTE
const novaQuoteMonitor = new NovaQuoteLogsMonitor();

// Export pour utilisation externe
module.exports = NovaQuoteLogsMonitor;