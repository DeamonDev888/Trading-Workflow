/**
 * 🤖 AGENT HEALTH MONITORING SYSTEM
 * Monitoring santé des AI Agents en temps réel
 * Q1 2025 Roadmap - Item 3.1
 */

import WebSocket from 'ws';
import { EventEmitter } from 'events';
import * as fs from 'fs';
import * as path from 'path';

interface AgentHealthStatus {
  name: string;
  status: 'healthy' | 'warning' | 'error' | 'offline';
  lastPing: number;
  lastActivity: number;
  errorCount: number;
  responseTime: number;
  uptime: number;
  memoryUsage: NodeJS.MemoryUsage;
  cpuUsage: number;
  activeConnections: number;
  tradesExecuted: number;
  lastError?: string;
  metrics?: {
    winRate: number;
    totalPnL: number;
    sharpeRatio: number;
    maxDrawdown: number;
  };
}

interface AgentProcess {
  name: string;
  pid?: number;
  startTime: number;
  scriptPath: string;
  process?: any;
  restartCount: number;
}

export class AgentHealthMonitor extends EventEmitter {
  private agents: Map<string, AgentHealthStatus> = new Map();
  private processes: Map<string, AgentProcess> = new Map();
  private healthCheckInterval: NodeJS.Timeout | null = null;
  private wsServer: WebSocket.Server | null = null;
  private logPath: string = path.join(__dirname, '../logs/agent_health.log');

  constructor() {
    super();
    this.initializeLogging();
    this.setupWebSocketServer();
    this.loadAgentConfigurations();
  }

  /**
   * Initialise le système de logging pour le health monitoring
   */
  private initializeLogging(): void {
    const logDir = path.dirname(this.logPath);
    if (!fs.existsSync(logDir)) {
      fs.mkdirSync(logDir, { recursive: true });
    }

    // Créer le header de log
    const header = `\n🤖 AGENT HEALTH MONITORING - ${new Date().toISOString()}\n` +
      `==================================================\n`;

    fs.appendFileSync(this.logPath, header);
    this.log('✅ Agent Health Monitoring System initialized');
  }

  /**
   * Configure le serveur WebSocket pour le monitoring en temps réel
   */
  private setupWebSocketServer(): void {
    this.wsServer = new WebSocket.Server({ port: 7002 });

    this.wsServer.on('connection', (ws) => {
      this.log('📡 Health monitoring WebSocket client connected');

      // Envoyer l'état actuel immédiatement
      ws.send(JSON.stringify({
        type: 'health_update',
        timestamp: Date.now(),
        agents: Array.from(this.agents.values())
      }));

      ws.on('close', () => {
        this.log('📡 Health monitoring WebSocket client disconnected');
      });
    });

    this.log('🌐 WebSocket Health Monitoring server started on port 7002');
  }

  /**
   * Charge la configuration des agents depuis les fichiers
   */
  private loadAgentConfigurations(): void {
    const agentConfigs = [
      { name: 'risk-agent', script: 'src/agents/risk_agent.py', description: 'Risk Management' },
      { name: 'strategy-agent', script: 'src/agents/strategy_agent.py', description: 'Strategy Generation' },
      { name: 'funding-agent', script: 'src/agents/funding_agent.py', description: 'Funding Rate Arbitrage' },
      { name: 'sentiment-agent', script: 'src/agents/sentiment_analysis_agent.py', description: 'Sentiment Analysis' },
      { name: 'hyperliquid-agent', script: 'src/hyperliquid/hyperliquid_mainnet_agent.py', description: 'HyperLiquid Trading' },
      { name: 'data-aggregator', script: 'src/agents/data_aggregator.py', description: 'Data Aggregation' },
      { name: 'reliability-monitor', script: 'src/agents/reliability_monitor.py', description: 'System Reliability' },
      { name: 'manager', script: 'src/agents/manager.py', description: 'Agent Manager' }
    ];

    agentConfigs.forEach(config => {
      const process: AgentProcess = {
        name: config.name,
        startTime: Date.now(),
        scriptPath: config.script,
        restartCount: 0
      };

      this.processes.set(config.name, process);

      // Initialiser l'état de santé
      const health: AgentHealthStatus = {
        name: config.name,
        status: 'offline',
        lastPing: 0,
        lastActivity: 0,
        errorCount: 0,
        responseTime: 0,
        uptime: 0,
        memoryUsage: process.memoryUsage(),
        cpuUsage: 0,
        activeConnections: 0,
        tradesExecuted: 0
      };

      this.agents.set(config.name, health);
    });

    this.log(`📋 Loaded ${agentConfigs.length} agent configurations`);
  }

  /**
   * Démarre le monitoring systématique
   */
  public startHealthMonitoring(): void {
    this.healthCheckInterval = setInterval(() => {
      this.performHealthChecks();
    }, 5000); // Check toutes les 5 secondes

    this.log('🚀 Health monitoring started - checking agents every 5 seconds');
  }

  /**
   * Effectue les contrôles de santé sur tous les agents
   */
  private async performHealthChecks(): Promise<void> {
    const promises = Array.from(this.processes.keys()).map(agentName =>
      this.checkAgentHealth(agentName)
    );

    try {
      await Promise.all(promises);
      this.broadcastHealthUpdate();
    } catch (error) {
      this.log(`❌ Error during health checks: ${error.message}`);
    }
  }

  /**
   * Vérifie la santé d'un agent spécifique
   */
  private async checkAgentHealth(agentName: string): Promise<void> {
    const startTime = Date.now();
    const health = this.agents.get(agentName);
    const process = this.processes.get(agentName);

    if (!health || !process) return;

    try {
      // Ping de l'agent via HTTP/WebSocket
      const isResponding = await this.pingAgent(agentName);
      const responseTime = Date.now() - startTime;

      health.lastPing = Date.now();
      health.responseTime = responseTime;

      if (isResponding) {
        health.status = 'healthy';
        health.uptime = Date.now() - process.startTime;

        // Récupérer les métriques de l'agent
        await this.updateAgentMetrics(agentName);
      } else {
        health.status = 'warning';
        health.errorCount++;
      }

      // Mettre à jour l'utilisation mémoire
      health.memoryUsage = process.memoryUsage();

      // Détecter les patterns d'erreur
      if (health.errorCount > 5) {
        health.status = 'error';
        this.emit('agent_error', { agentName, health });
      }

    } catch (error) {
      health.status = 'error';
      health.errorCount++;
      health.lastError = error.message;

      this.log(`⚠️ Agent ${agentName} health check failed: ${error.message}`);
    }
  }

  /**
   * Ping un agent pour vérifier sa disponibilité
   */
  private async pingAgent(agentName: string): Promise<boolean> {
    return new Promise((resolve) => {
      try {
        // Tenter une connexion HTTP à l'agent (si disponible)
        const healthUrl = `http://localhost:${7000 + this.processes.get(agentName)?.name?.length || 0}/health`;

        const req = require('http').get(healthUrl, (res: any) => {
          resolve(res.statusCode === 200);
        });

        req.on('error', () => {
          // Fallback: vérifier si le processus Python est en cours d'exécution
          this.checkPythonProcess(agentName).then(resolve);
        });

        req.setTimeout(2000, () => {
          req.destroy();
          resolve(false);
        });

      } catch (error) {
        // Fallback final
        this.checkPythonProcess(agentName).then(resolve);
      }
    });
  }

  /**
   * Vérifie si un processus Python est en cours d'exécution
   */
  private async checkPythonProcess(agentName: string): Promise<boolean> {
    try {
      const { spawn } = require('child_process');
      const process = this.processes.get(agentName);

      if (process?.process && !process.process.killed) {
        return true;
      }

      // Tenter de lancer l'agent s'il n'est pas actif
      if (!process?.process) {
        await this.startAgent(agentName);
        return true;
      }

      return false;
    } catch (error) {
      return false;
    }
  }

  /**
   * Démarre un agent
   */
  private async startAgent(agentName: string): Promise<void> {
    const process = this.processes.get(agentName);
    if (!process) return;

    try {
      const { spawn } = require('child_process');

      this.log(`🚀 Starting agent: ${agentName}`);

      const agentProcess = spawn('python', [process.scriptPath], {
        stdio: ['pipe', 'pipe', 'pipe'],
        cwd: process.cwd()
      });

      process.pid = agentProcess.pid;
      process.process = agentProcess;
      process.startTime = Date.now();

      // Logging des sorties de l'agent
      agentProcess.stdout.on('data', (data: Buffer) => {
        this.log(`📤 ${agentName}: ${data.toString().trim()}`);
        this.updateAgentActivity(agentName);
      });

      agentProcess.stderr.on('data', (data: Buffer) => {
        this.log(`❌ ${agentName} Error: ${data.toString().trim()}`);
        this.incrementAgentError(agentName);
      });

      agentProcess.on('close', (code: number) => {
        this.log(`🔴 Agent ${agentName} exited with code ${code}`);
        this.markAgentOffline(agentName);
      });

    } catch (error) {
      this.log(`❌ Failed to start agent ${agentName}: ${error.message}`);
    }
  }

  /**
   * Met à jour les métriques d'un agent
   */
  private async updateAgentMetrics(agentName: string): Promise<void> {
    const health = this.agents.get(agentName);
    if (!health) return;

    try {
      // Simuler des métriques (à connecter avec les vraies métriques des agents)
      health.metrics = {
        winRate: Math.random() * 100,
        totalPnL: (Math.random() - 0.5) * 10000,
        sharpeRatio: Math.random() * 2,
        maxDrawdown: Math.random() * 20
      };

      health.tradesExecuted += Math.floor(Math.random() * 3);
    } catch (error) {
      this.log(`⚠️ Failed to update metrics for ${agentName}: ${error.message}`);
    }
  }

  /**
   * Diffuse les mises à jour de santé via WebSocket
   */
  private broadcastHealthUpdate(): void {
    if (!this.wsServer) return;

    const message = JSON.stringify({
      type: 'health_update',
      timestamp: Date.now(),
      agents: Array.from(this.agents.values())
    });

    this.wsServer.clients.forEach((client) => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(message);
      }
    });
  }

  /**
   * Met à jour l'activité d'un agent
   */
  private updateAgentActivity(agentName: string): void {
    const health = this.agents.get(agentName);
    if (health) {
      health.lastActivity = Date.now();
    }
  }

  /**
   * Incrémente le compteur d'erreurs d'un agent
   */
  private incrementAgentError(agentName: string): void {
    const health = this.agents.get(agentName);
    if (health) {
      health.errorCount++;
      health.status = 'warning';
    }
  }

  /**
   * Marque un agent comme hors ligne
   */
  private markAgentOffline(agentName: string): void {
    const health = this.agents.get(agentName);
    if (health) {
      health.status = 'offline';
    }
  }

  /**
   * Récupère l'état de santé de tous les agents
   */
  public getHealthStatus(): AgentHealthStatus[] {
    return Array.from(this.agents.values());
  }

  /**
   * Récupère l'état de santé d'un agent spécifique
   */
  public getAgentHealth(agentName: string): AgentHealthStatus | undefined {
    return this.agents.get(agentName);
  }

  /**
   * Arrête le monitoring
   */
  public stopHealthMonitoring(): void {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
      this.healthCheckInterval = null;
    }

    if (this.wsServer) {
      this.wsServer.close();
      this.wsServer = null;
    }

    this.log('🛑 Health monitoring stopped');
  }

  /**
   * Logging des événements
   */
  private log(message: string): void {
    const timestamp = new Date().toISOString();
    const logEntry = `[${timestamp}] ${message}\n`;

    fs.appendFileSync(this.logPath, logEntry);
    console.log(`[HEALTH] ${message}`);
  }
}

// Export singleton instance
export const agentHealthMonitor = new AgentHealthMonitor();