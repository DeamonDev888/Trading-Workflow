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
const AGENT_LOGS_WS_PORT = 9002;
const AGENT_LOGS_HTTP_PORT = 9003;

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

// Patterns NOVAQUOTE Winston JSON à surveiller
const NOVAQUOTE_PATTERNS = {
  SUCCESS: [
    /"message": "NOVAQUOTE WINSTON LOGGERS SYSTEM - 7 Expert Loggers Initialized"/,
    /"message": "Server listening on http:\/\/localhost:7000"/,
    /"message": "WebSocket connection established"/,
    /"message": "Agent initialized"/
  ],
  ERRORS: [
    /"level": "ERROR"/,
    /"message": ".*failed.*/i,
    /"message": ".*timeout.*/i,
    /"message": ".*connection.*lost.*/i,
    /"message": ".*unable.*to.*connect.*/i
  ],
  WARNINGS: [
    /"level": "WARN"/,
    /"message": ".*deprecated.*/i,
    /"message": ".*retry.*attempt.*/i,
    /"message": "Unknown route"/
  ],
  PERFORMANCE: [
    /"duration": *[0-9]+/,
    /"message": ".*performance.*/i,
    /"message": ".*response.*time.*/i
  ],
  TRADING: [
    /"component": "TRADING"/,
    /"message": ".*trade.*/i,
    /"message": ".*position.*/i,
    /"symbol": "(BTC|ETH|SOL|ARB|APT|ADA|AVAX|BNB)"/
  ],
  AGENTS: [
    /"component": "AGENTS"/,
    /"message": ".*agent.*/i,
    /"agentId": ".*_agent"/,
    /"message": ".*cycle.*/i
  ],
  WEBSOCKET: [
    /"component": "WS"/,
    /"message": "WebSocket.*/i,
    /"event": "(connect|disconnect|message)"/,
    /"clientId": "ws_*/
  ]
};

class NovaQuoteLogsMonitor {
  constructor() {
    // Suivi des positions dans les fichiers pour éviter les relectures complètes
    this.filePositions = new Map();

    // Suivi des timers pour prévenir les memory leaks
    this.timers = {
      scanInterval: null,
      healthCheckInterval: null,
      monitoringInterval: null
    };

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

    // Nouveau: Suivi des 7 loggers Winston spécialisés
    this.winstonLoggers = {
      API: { count: 0, errors: 0, lastActivity: null },
      WS: { count: 0, errors: 0, lastActivity: null },
      AGENTS: { count: 0, errors: 0, lastActivity: null },
      BACKTESTS: { count: 0, errors: 0, lastActivity: null },
      TRADING: { count: 0, errors: 0, lastActivity: null, trades: [] },
      WALLETS: { count: 0, errors: 0, lastActivity: null },
      SYSTEM: { count: 0, errors: 0, lastActivity: null }
    };

    this.startMonitoring();
  }

  async startMonitoring() {
    console.info('\n🚀 ===============================================');
    console.info('📊 NOVAQUOTE AGENT EXPERT LOGS - MONITORING');
    console.info('==============================================\n');

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

    // Surveillance continue des fichiers de logs - avec suivi du timer
    this.timers.scanInterval = setInterval(() => {
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

        // Lire seulement les nouvelles lignes depuis la dernière position
        const newPosition = this.readNewLogLines(filePath, file, stats);
        this.filePositions.set(file, newPosition);
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

  readNewLogLines(filePath, fileName, stats) {
    try {
      const currentPosition = this.filePositions.get(fileName) || 0;

      // Si le fichier a été tourné (log rotation), réinitialiser la position
      if (stats.size < currentPosition) {
        this.filePositions.set(fileName, 0);
        return this.readNewLogLines(filePath, fileName, stats);
      }

      // Lire seulement les nouvelles données
      if (stats.size > currentPosition) {
        const buffer = Buffer.alloc(stats.size - currentPosition);
        const fd = fs.openSync(filePath, 'r');
        fs.readSync(fd, buffer, 0, buffer.length, currentPosition);
        fs.closeSync(fd);

        const newContent = buffer.toString('utf8');
        const lines = newContent.split('\n').filter(line => line.trim());

        // Analyser les nouvelles lignes
        lines.forEach(line => {
          this.analyzeLogLine(line, fileName, stats);
        });

        return stats.size;
      }

      return currentPosition;
    } catch (error) {
      monitorLogger.error('❌ Erreur lecture fichier logs', {
        error: error.message,
        file: fileName
      });
      return 0;
    }
  }

  processNovaQuoteLog(logEntry, fileName, stats) {
    try {
      this.logsData.total++;
      const component = logEntry.component?.toUpperCase() || 'SYSTEM';
      const level = logEntry.level?.toUpperCase() || 'INFO';

      // Suivi des 7 loggers Winston spécialisés
      if (this.winstonLoggers[component]) {
        this.winstonLoggers[component].count++;
        this.winstonLoggers[component].lastActivity = logEntry.timestamp || new Date().toISOString();

        if (level === 'ERROR') {
          this.winstonLoggers[component].errors++;
        }
      }

      // Traitement spécial pour les logs de trading
      if (component === 'TRADING') {
        this.logsData.trading++;

        // Extraire les informations de trading si disponibles
        if (logEntry.symbol || logEntry.action || logEntry.tradeId) {
          const tradeInfo = {
            timestamp: logEntry.timestamp,
            symbol: logEntry.symbol,
            action: logEntry.action,
            tradeId: logEntry.tradeId,
            message: logEntry.message
          };

          this.winstonLoggers.TRADING.trades.unshift(tradeInfo);
          if (this.winstonLoggers.TRADING.trades.length > 10) {
            this.winstonLoggers.TRADING.trades = this.winstonLoggers.TRADING.trades.slice(0, 10);
          }
        }
      }

      // Catégoriser par niveau de log
      switch (level) {
        case 'SUCCESS':
        case 'SUCCESSFUL':
        case 'OK':
          this.logsData.success++;
          break;
        case 'ERROR':
        case 'FATAL':
        case 'CRITICAL':
          this.logsData.errors++;
          this.addNovaQuoteAlert('ERROR', component, logEntry);
          monitorLogger.error('🚨 Erreur critique détectée', {
            component,
            logEntry,
            fileName,
            timestamp: logEntry.timestamp
          });
          break;
        case 'WARNING':
        case 'WARN':
          this.logsData.warnings++;
          this.addNovaQuoteAlert('WARNING', component, logEntry);
          break;
        case 'INFO':
          // Catégoriser selon le composant
          switch (component) {
            case 'AGENTS':
              this.logsData.agents++;
              break;
            case 'WS':
            case 'WEBSOCKET':
              this.logsData.websocket++;
              break;
            case 'BACKTESTS':
            case 'TRADING':
            case 'WALLETS':
              // Déjà comptés ci-dessus
              break;
          }
          break;
        default:
          // Logs DEBUG ne nécessitent pas de comptage spécial
          break;
      }

      // Log spécifique pour les metrics de performance
      if (logEntry.duration || logEntry.responseTime) {
        this.logsData.performance++;
      }

      // Log des événements système importants
      if (logEntry.event || logEntry.action) {
        monitorLogger.info('🔄 Événement système', {
          component,
          event: logEntry.event || logEntry.action,
          timestamp: logEntry.timestamp
        });
      }

      // Ajouter aux logs récents pour le dashboard
      this.recentLogs.unshift({
        timestamp: logEntry.timestamp,
        level,
        component,
        message: logEntry.message,
        file: fileName
      });

      if (this.recentLogs.length > 100) {
        this.recentLogs = this.recentLogs.slice(0, 100);
      }

    } catch (error) {
      monitorLogger.error('❌ Erreur traitement log JSON', {
        logEntry,
        error: error.message
      });
    }
  }

  addNovaQuoteAlert(type, component, logEntry) {
    const alert = {
      type,
      component,
      message: logEntry.message || `Alerte ${type} dans ${component}`,
      timestamp: logEntry.timestamp || new Date().toISOString(),
      severity: type === 'ERROR' ? 'HIGH' : 'MEDIUM'
    };

    this.alerts.unshift(alert);

    // Limiter le nombre d'alerts
    if (this.alerts.length > 50) {
      this.alerts = this.alerts.slice(0, 50);
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
    console.info('🔍 Démarrage monitoring des services NOVAQUOTE...');

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
    console.info(`🌐 Démarrage WebSocket Server sur port ${AGENT_LOGS_WS_PORT}...`);

    this.wss = new ws.Server({ port: AGENT_LOGS_WS_PORT });

    this.wss.on('connection', (ws) => {
      console.info('📊 Client dashboard connecté');

      // Envoyer l'état actuel
      this.sendDashboardUpdate(ws);

      // Envoyer les mises à jour toutes les secondes
      const interval = setInterval(() => {
        this.sendDashboardUpdate(ws);
      }, 1000);

      ws.on('close', () => {
        console.info('📊 Client dashboard déconnecté');
        clearInterval(interval);
      });

      ws.on('error', (error) => {
        console.error('❌ WebSocket error:', error.message);
      });
    });

    console.info(`✅ WebSocket Server démarré sur ws://localhost:${AGENT_LOGS_WS_PORT}`);
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
        alerts: this.alerts.slice(0, 10),
        winstonLoggers: this.winstonLoggers,
        recentTrades: this.winstonLoggers.TRADING.trades.slice(0, 5)
      }
    };

    if (ws.readyState === ws.OPEN) {
      ws.send(JSON.stringify(update));
    }
  }

  startHTTPServer() {
    console.info(`🌐 Démarrage HTTP Server pour dashboard sur port ${AGENT_LOGS_HTTP_PORT}...`);

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

    server.listen(AGENT_LOGS_HTTP_PORT, () => {
      console.info(`✅ Dashboard HTTP disponible sur http://localhost:${AGENT_LOGS_HTTP_PORT}`);
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
            <h3>📊 Loggers Winston NovaQuote</h3>
            <div class="metric">
                <span class="label">API Logger:</span>
                <span class="value" id="winston-api">0</span>
            </div>
            <div class="metric">
                <span class="label">WebSocket Logger:</span>
                <span class="value" id="winston-ws">0</span>
            </div>
            <div class="metric">
                <span class="label">Agents Logger:</span>
                <span class="value" id="winston-agents">0</span>
            </div>
            <div class="metric">
                <span class="label">Trading Logger:</span>
                <span class="value" id="winston-trading">0</span>
            </div>
            <div class="metric">
                <span class="label">System Logger:</span>
                <span class="value" id="winston-system">0</span>
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
            <h3>💰 Trades Récents</h3>
            <div id="trades-container">
                <div class="metric">
                    <span class="label">Aucun trade détecté</span>
                </div>
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
        const ws = new WebSocket('ws://localhost:${AGENT_LOGS_WS_PORT}');

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

            // Mettre à jour les loggers Winston NovaQuote
            if (data.winstonLoggers) {
                document.getElementById('winston-api').textContent = data.winstonLoggers.API?.count || 0;
                document.getElementById('winston-ws').textContent = data.winstonLoggers.WS?.count || 0;
                document.getElementById('winston-agents').textContent = data.winstonLoggers.AGENTS?.count || 0;
                document.getElementById('winston-trading').textContent = data.winstonLoggers.TRADING?.count || 0;
                document.getElementById('winston-system').textContent = data.winstonLoggers.SYSTEM?.count || 0;
            }

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

            // Mettre à jour les trades récents
            const tradesContainer = document.getElementById('trades-container');
            if (data.recentTrades && data.recentTrades.length > 0) {
                tradesContainer.innerHTML = data.recentTrades.map(trade =>
                    '<div class="metric" style="background: #1a5a3a;">' +
                    '<strong>' + (trade.symbol || 'Unknown') + '</strong>: ' + (trade.action || 'No action') +
                    '<br><small>' + (trade.message || 'No message') + '</small>' +
                    '<br><small style="color: #888;">' + new Date(trade.timestamp).toLocaleString() + '</small>' +
                    '</div>'
                ).join('');
            } else {
                tradesContainer.innerHTML = '<div class="metric"><span class="label">Aucun trade détecté</span></div>';
            }

            // Mettre à jour les alerts
            const alertsContainer = document.getElementById('alerts-container');
            if (data.alerts.length > 0) {
                alertsContainer.innerHTML = data.alerts.slice(0, 5).map(alert =>
                    '<div class="alert alert-' + alert.type.toLowerCase() + '">' +
                    '<strong>' + alert.type + '</strong>: ' + alert.message +
                    (alert.component ? '<br><small>Component: ' + alert.component + '</small>' : '') +
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
    console.info('\n📊 ===============================================');
    console.info('🎯 STATUT INITIAL SYSTÈME NOVAQUOTE');
    console.info('==============================================\n');

    console.info('🔍 Services Configuration:');
    console.info(`   • Backend API: http://localhost:${NOVAQUOTE_BACKEND_PORT}`);
    console.info(`   • WebSocket: ws://localhost:${NOVAQUOTE_WEBSOCKET_PORT}`);
    console.info(`   • Agent Logs: ws://localhost:${AGENT_LOGS_WS_PORT}`);
    console.info(`   • Dashboard: http://localhost:${AGENT_LOGS_HTTP_PORT}`);

    console.info('\n📁 Logs Directory:', NOVAQUOTE_LOGS_DIR);
    console.info('📋 Monitoring Patterns:', Object.keys(NOVAQUOTE_PATTERNS).length, 'catégories');

    console.info('\n🚀 Dashboard Monitoring démarré!');
    console.info('   • Accès dashboard: http://localhost:' + AGENT_LOGS_HTTP_PORT);
    console.info('   • WebSocket temps réel: ws://localhost:' + AGENT_LOGS_WS_PORT);
    console.info('   • Monitoring 24/7 des logs NOVAQUOTE actif\n');
  }
}

// Démarrer l'Agent Expert Logs NOVAQUOTE
const novaQuoteMonitor = new NovaQuoteLogsMonitor();

// Export pour utilisation externe
module.exports = NovaQuoteLogsMonitor;