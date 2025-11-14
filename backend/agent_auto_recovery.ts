/**
 * 🔄 AGENT AUTO-RECOVERY SYSTEM
 * Redémarrage automatique et récupération des agents en erreur
 * Q1 2025 Roadmap - Item 3.2
 */

import { EventEmitter } from 'events';
import { exec } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';
import { agentHealthMonitor, AgentHealthStatus } from './agent_health_monitor';

interface RecoveryPolicy {
  agentName: string;
  maxRestarts: number;
  restartDelay: number;
  escalationDelay: number;
  maxMemoryUsage: number;
  maxResponseTime: number;
  healthCheckInterval: number;
}

interface RecoveryAttempt {
  timestamp: number;
  reason: string;
  success: boolean;
  duration: number;
  details?: any;
}

interface AgentErrorPattern {
  type: 'memory_leak' | 'api_timeout' | 'database_error' | 'network_error' | 'crash';
  frequency: number;
  lastOccurred: number;
  autoFixable: boolean;
  fixCommand?: string;
}

export class AgentAutoRecovery extends EventEmitter {
  private recoveryPolicies: Map<string, RecoveryPolicy> = new Map();
  private recoveryHistory: Map<string, RecoveryAttempt[]> = new Map();
  private errorPatterns: Map<string, AgentErrorPattern[]> = new Map();
  private recoveryCooldowns: Map<string, number> = new Map();
  private logPath: string = path.join(__dirname, '../logs/agent_recovery.log');

  constructor() {
    super();
    this.initializeRecoveryPolicies();
    this.setupHealthMonitorListeners();
    this.initializeLogging();
  }

  /**
   * Initialise les politiques de récupération pour chaque agent
   */
  private initializeRecoveryPolicies(): void {
    const policies: RecoveryPolicy[] = [
      {
        agentName: 'risk-agent',
        maxRestarts: 5,
        restartDelay: 5000,
        escalationDelay: 30000,
        maxMemoryUsage: 512 * 1024 * 1024, // 512MB
        maxResponseTime: 2000,
        healthCheckInterval: 10000
      },
      {
        agentName: 'strategy-agent',
        maxRestarts: 3,
        restartDelay: 10000,
        escalationDelay: 60000,
        maxMemoryUsage: 1024 * 1024 * 1024, // 1GB
        maxResponseTime: 5000,
        healthCheckInterval: 15000
      },
      {
        agentName: 'funding-agent',
        maxRestarts: 10,
        restartDelay: 2000,
        escalationDelay: 15000,
        maxMemoryUsage: 256 * 1024 * 1024, // 256MB
        maxResponseTime: 1000,
        healthCheckInterval: 5000
      },
      {
        agentName: 'sentiment-agent',
        maxRestarts: 3,
        restartDelay: 15000,
        escalationDelay: 120000,
        maxMemoryUsage: 512 * 1024 * 1024, // 512MB
        maxResponseTime: 10000,
        healthCheckInterval: 20000
      },
      {
        agentName: 'hyperliquid-agent',
        maxRestarts: 7,
        restartDelay: 3000,
        escalationDelay: 30000,
        maxMemoryUsage: 256 * 1024 * 1024, // 256MB
        maxResponseTime: 1500,
        healthCheckInterval: 3000
      },
      {
        agentName: 'data-aggregator',
        maxRestarts: 5,
        restartDelay: 8000,
        escalationDelay: 45000,
        maxMemoryUsage: 768 * 1024 * 1024, // 768MB
        maxResponseTime: 3000,
        healthCheckInterval: 8000
      },
      {
        agentName: 'reliability-monitor',
        maxRestarts: 2,
        restartDelay: 20000,
        escalationDelay: 180000,
        maxMemoryUsage: 128 * 1024 * 1024, // 128MB
        maxResponseTime: 1500,
        healthCheckInterval: 10000
      },
      {
        agentName: 'manager',
        maxRestarts: 2,
        restartDelay: 30000,
        escalationDelay: 300000,
        maxMemoryUsage: 256 * 1024 * 1024, // 256MB
        maxResponseTime: 2000,
        healthCheckInterval: 25000
      }
    ];

    policies.forEach(policy => {
      this.recoveryPolicies.set(policy.agentName, policy);
      this.recoveryHistory.set(policy.agentName, []);
      this.errorPatterns.set(policy.agentName, []);
    });

    this.log(`📋 Initialized recovery policies for ${policies.length} agents`);
  }

  /**
   * Configure les listeners pour le health monitoring
   */
  private setupHealthMonitorListeners(): void {
    agentHealthMonitor.on('agent_error', (data: { agentName: string; health: AgentHealthStatus }) => {
      this.handleAgentError(data.agentName, data.health);
    });

    // Démarrer le monitoring proactif
    this.startProactiveMonitoring();
  }

  /**
   * Initialise le système de logging
   */
  private initializeLogging(): void {
    const logDir = path.dirname(this.logPath);
    if (!fs.existsSync(logDir)) {
      fs.mkdirSync(logDir, { recursive: true });
    }

    const header = `\n🔄 AGENT AUTO-RECOVERY SYSTEM - ${new Date().toISOString()}\n` +
      `========================================================\n`;

    fs.appendFileSync(this.logPath, header);
    this.log('✅ Agent Auto-Recovery System initialized');
  }

  /**
   * Démarre le monitoring proactif des agents
   */
  private startProactiveMonitoring(): void {
    setInterval(() => {
      this.performProactiveHealthChecks();
    }, 10000); // Check toutes les 10 secondes

    this.log('🔍 Proactive monitoring started');
  }

  /**
   * Effectue les contrôles de santé proactifs
   */
  private async performProactiveHealthChecks(): Promise<void> {
    const healthStatuses = agentHealthMonitor.getHealthStatus();

    for (const health of healthStatuses) {
      const policy = this.recoveryPolicies.get(health.name);
      if (!policy) continue;

      // Vérifier l'utilisation mémoire
      if (health.memoryUsage.heapUsed > policy.maxMemoryUsage) {
        await this.handleMemoryLeak(health.name, health.memoryUsage.heapUsed);
        continue;
      }

      // Vérifier le temps de réponse
      if (health.responseTime > policy.maxResponseTime) {
        await this.handleSlowResponse(health.name, health.responseTime);
        continue;
      }

      // Vérifier les erreurs consécutives
      if (health.errorCount >= 3) {
        await this.handleConsecutiveErrors(health.name, health.errorCount);
        continue;
      }
    }
  }

  /**
   * Gère les erreurs d'agent
   */
  private async handleAgentError(agentName: string, health: AgentHealthStatus): Promise<void> {
    const policy = this.recoveryPolicies.get(agentName);
    if (!policy) return;

    // Vérifier si l'agent est en cooldown
    if (this.isAgentInCooldown(agentName)) {
      this.log(`⏰ Agent ${agentName} is in cooldown, skipping recovery`);
      return;
    }

    this.log(`🚨 Handling agent error: ${agentName} - Status: ${health.status}`);

    const recoveryStart = Date.now();
    let success = false;

    try {
      // Analyser le pattern d'erreur
      const errorPattern = this.analyzeErrorPattern(agentName, health);

      // Appliquer la stratégie de récupération appropriée
      switch (errorPattern.type) {
        case 'memory_leak':
          success = await this.recoverFromMemoryLeak(agentName);
          break;
        case 'api_timeout':
          success = await this.recoverFromApiTimeout(agentName);
          break;
        case 'database_error':
          success = await this.recoverFromDatabaseError(agentName);
          break;
        case 'network_error':
          success = await this.recoverFromNetworkError(agentName);
          break;
        case 'crash':
          success = await this.recoverFromCrash(agentName);
          break;
        default:
          success = await this.performStandardRecovery(agentName);
      }

    } catch (error) {
      this.log(`❌ Recovery failed for ${agentName}: ${error.message}`);
      success = false;
    }

    // Enregistrer la tentative de récupération
    const attempt: RecoveryAttempt = {
      timestamp: recoveryStart,
      reason: health.status,
      success,
      duration: Date.now() - recoveryStart,
      details: { health, errorPattern: health.lastError }
    };

    this.recordRecoveryAttempt(agentName, attempt);

    if (success) {
      this.log(`✅ Successfully recovered agent: ${agentName}`);
      this.emit('agent_recovered', { agentName, attempt });
    } else {
      this.log(`❌ Failed to recover agent: ${agentName}`);
      this.handleRecoveryFailure(agentName);
    }
  }

  /**
   * Analyse le pattern d'erreur
   */
  private analyzeErrorPattern(agentName: string, health: AgentHealthStatus): AgentErrorPattern {
    const lastError = health.lastError?.toLowerCase() || '';

    // Memory leak detection
    if (health.memoryUsage.heapUsed > (this.recoveryPolicies.get(agentName)?.maxMemoryUsage || 0)) {
      return {
        type: 'memory_leak',
        frequency: 1,
        lastOccurred: Date.now(),
        autoFixable: true
      };
    }

    // API timeout detection
    if (lastError.includes('timeout') || lastError.includes('etimedout')) {
      return {
        type: 'api_timeout',
        frequency: 1,
        lastOccurred: Date.now(),
        autoFixable: true
      };
    }

    // Database error detection
    if (lastError.includes('database') || lastError.includes('sqlite') || lastError.includes('connection')) {
      return {
        type: 'database_error',
        frequency: 1,
        lastOccurred: Date.now(),
        autoFixable: true,
        fixCommand: 'restart_database_connection'
      };
    }

    // Network error detection
    if (lastError.includes('network') || lastError.includes('connection') || lastError.includes('enotfound')) {
      return {
        type: 'network_error',
        frequency: 1,
        lastOccurred: Date.now(),
        autoFixable: true
      };
    }

    // Crash detection
    if (health.status === 'offline' || health.lastError?.includes('exited')) {
      return {
        type: 'crash',
        frequency: 1,
        lastOccurred: Date.now(),
        autoFixable: true
      };
    }

    // Default error
    return {
      type: 'crash',
      frequency: 1,
      lastOccurred: Date.now(),
      autoFixable: true
    };
  }

  /**
   * Récupération depuis un memory leak
   */
  private async recoverFromMemoryLeak(agentName: string): Promise<boolean> {
    this.log(`🔧 Recovering ${agentName} from memory leak`);

    try {
      // Force garbage collection
      if (global.gc) {
        global.gc();
      }

      // Attendre un peu et vérifier
      await this.sleep(2000);

      // Si le problème persiste, redémarrer l'agent
      const health = agentHealthMonitor.getAgentHealth(agentName);
      if (health && health.memoryUsage.heapUsed > (this.recoveryPolicies.get(agentName)?.maxMemoryUsage || 0)) {
        return await this.restartAgent(agentName, 'memory_leak_recovery');
      }

      return true;
    } catch (error) {
      this.log(`❌ Memory leak recovery failed for ${agentName}: ${error.message}`);
      return false;
    }
  }

  /**
   * Récupération depuis un timeout API
   */
  private async recoverFromApiTimeout(agentName: string): Promise<boolean> {
    this.log(`🔧 Recovering ${agentName} from API timeout`);

    try {
      // Augmenter le timeout de l'agent
      await this.adjustAgentTimeout(agentName, 30000);

      // Redémarrer l'agent avec un timeout plus long
      return await this.restartAgent(agentName, 'api_timeout_recovery');
    } catch (error) {
      this.log(`❌ API timeout recovery failed for ${agentName}: ${error.message}`);
      return false;
    }
  }

  /**
   * Récupération depuis une erreur de base de données
   */
  private async recoverFromDatabaseError(agentName: string): Promise<boolean> {
    this.log(`🔧 Recovering ${agentName} from database error`);

    try {
      // Recréer la connexion à la base de données
      await this.recreateDatabaseConnection();

      // Redémarrer l'agent
      return await this.restartAgent(agentName, 'database_error_recovery');
    } catch (error) {
      this.log(`❌ Database error recovery failed for ${agentName}: ${error.message}`);
      return false;
    }
  }

  /**
   * Récupération depuis une erreur réseau
   */
  private async recoverFromNetworkError(agentName: string): Promise<boolean> {
    this.log(`🔧 Recovering ${agentName} from network error`);

    try {
      // Attendre la reconnexion réseau
      await this.sleep(5000);

      // Vérifier la connectivité
      const isConnected = await this.checkNetworkConnectivity();
      if (!isConnected) {
        this.log(`⚠️ Network still unavailable, delaying recovery for ${agentName}`);
        return false;
      }

      // Redémarrer l'agent
      return await this.restartAgent(agentName, 'network_error_recovery');
    } catch (error) {
      this.log(`❌ Network error recovery failed for ${agentName}: ${error.message}`);
      return false;
    }
  }

  /**
   * Récupération depuis un crash
   */
  private async recoverFromCrash(agentName: string): Promise<boolean> {
    this.log(`🔧 Recovering ${agentName} from crash`);

    return await this.restartAgent(agentName, 'crash_recovery');
  }

  /**
   * Effectue une récupération standard
   */
  private async performStandardRecovery(agentName: string): Promise<boolean> {
    this.log(`🔧 Performing standard recovery for ${agentName}`);

    return await this.restartAgent(agentName, 'standard_recovery');
  }

  /**
   * Redémarre un agent
   */
  private async restartAgent(agentName: string, reason: string): Promise<boolean> {
    const policy = this.recoveryPolicies.get(agentName);
    if (!policy) return false;

    const history = this.recoveryHistory.get(agentName) || [];
    const recentRestarts = history.filter(attempt =>
      Date.now() - attempt.timestamp < 300000 // 5 minutes
    ).length;

    if (recentRestarts >= policy.maxRestarts) {
      this.log(`⚠️ Agent ${agentName} exceeded max restarts (${policy.maxRestarts}), escalating`);
      return await this.escalateRecovery(agentName);
    }

    try {
      this.log(`🔄 Restarting agent ${agentName} (reason: ${reason})`);

      // Tuer le processus existant
      await this.killAgentProcess(agentName);

      // Attendre avant de redémarrer
      await this.sleep(policy.restartDelay);

      // Démarrer le nouvel agent
      const success = await this.startAgentProcess(agentName);

      if (success) {
        this.log(`✅ Agent ${agentName} restarted successfully`);
        this.setAgentCooldown(agentName, policy.escalationDelay);
        return true;
      } else {
        this.log(`❌ Failed to restart agent ${agentName}`);
        return false;
      }

    } catch (error) {
      this.log(`❌ Error restarting agent ${agentName}: ${error.message}`);
      return false;
    }
  }

  /**
   * Tue un processus d'agent
   */
  private async killAgentProcess(agentName: string): Promise<void> {
    return new Promise((resolve) => {
      exec(`taskkill /F /IM python.exe /FI "WINDOWTITLE eq ${agentName}*" 2>nul || true`, (error) => {
        // Tenter aussi avec pkill si disponible
        exec(`pkill -f "${agentName}" 2>/dev/null || true`, () => {
          resolve();
        });
      });
    });
  }

  /**
   * Démarre un processus d'agent
   */
  private async startAgentProcess(agentName: string): Promise<boolean> {
    return new Promise((resolve) => {
      const agentScripts = {
        'risk-agent': 'src/agents/risk_agent.py',
        'strategy-agent': 'src/agents/strategy_agent.py',
        'funding-agent': 'src/agents/funding_agent.py',
        'sentiment-agent': 'src/agents/sentiment_analysis_agent.py',
        'hyperliquid-agent': 'src/hyperliquid/hyperliquid_mainnet_agent.py',
        'data-aggregator': 'src/agents/data_aggregator.py',
        'reliability-monitor': 'src/agents/reliability_monitor.py',
        'manager': 'src/agents/manager.py'
      };

      const script = agentScripts[agentName as keyof typeof agentScripts];
      if (!script) {
        this.log(`❌ Unknown agent: ${agentName}`);
        resolve(false);
        return;
      }

      const child = require('child_process').spawn('python', [script], {
        stdio: 'pipe',
        cwd: process.cwd(),
        env: { ...process.env, PYTHONPATH: process.cwd() }
      });

      child.on('error', (error: any) => {
        this.log(`❌ Failed to start ${agentName}: ${error.message}`);
        resolve(false);
      });

      child.on('spawn', () => {
        this.log(`🚀 Agent ${agentName} spawned (PID: ${child.pid})`);

        // Logging des sorties
        child.stdout?.on('data', (data: Buffer) => {
          this.log(`📤 ${agentName}: ${data.toString().trim()}`);
        });

        child.stderr?.on('data', (data: Buffer) => {
          this.log(`❌ ${agentName} Error: ${data.toString().trim()}`);
        });

        child.on('close', (code: number) => {
          this.log(`🔴 Agent ${agentName} exited with code ${code}`);
        });

        resolve(true);
      });

      setTimeout(() => {
        resolve(false);
      }, 10000); // Timeout après 10 secondes
    });
  }

  /**
   * Gère les fuites de mémoire proactives
   */
  private async handleMemoryLeak(agentName: string, memoryUsage: number): Promise<void> {
    this.log(`🚨 Memory leak detected in ${agentName}: ${Math.round(memoryUsage / 1024 / 1024)}MB`);
    await this.handleAgentError(agentName, {
      name: agentName,
      status: 'warning',
      lastPing: Date.now(),
      lastActivity: Date.now(),
      errorCount: 1,
      responseTime: 0,
      uptime: 0,
      memoryUsage: { heapUsed: memoryUsage, heapTotal: memoryUsage, external: 0, rss: 0, arrayBuffers: 0 },
      cpuUsage: 0,
      activeConnections: 0,
      tradesExecuted: 0,
      lastError: 'Memory leak detected'
    });
  }

  /**
   * Gère les réponses lentes
   */
  private async handleSlowResponse(agentName: string, responseTime: number): Promise<void> {
    this.log(`⚠️ Slow response detected in ${agentName}: ${responseTime}ms`);

    const health = agentHealthMonitor.getAgentHealth(agentName);
    if (health && health.errorCount > 0) {
      await this.handleAgentError(agentName, health);
    }
  }

  /**
   * Gère les erreurs consécutives
   */
  private async handleConsecutiveErrors(agentName: string, errorCount: number): Promise<void> {
    this.log(`🚨 Consecutive errors detected in ${agentName}: ${errorCount}`);

    const health = agentHealthMonitor.getAgentHealth(agentName);
    if (health) {
      await this.handleAgentError(agentName, health);
    }
  }

  /**
   * Gère les échecs de récupération
   */
  private handleRecoveryFailure(agentName: string): void {
    this.log(`🆘 Recovery failed for ${agentName}, sending alert`);

    // Envoyer une alerte (Slack, email, etc.)
    this.sendAlert(agentName, 'Recovery failure - manual intervention required');
  }

  /**
   * Escalade la récupération
   */
  private async escalateRecovery(agentName: string): Promise<boolean> {
    this.log(`🚨 Escalating recovery for ${agentName}`);

    // Arrêter l'agent complètement
    await this.killAgentProcess(agentName);

    // Envoyer une alerte critique
    this.sendAlert(agentName, 'Agent escalation - manual intervention required');

    // Marquer comme nécessitant une intervention manuelle
    this.emit('agent_intervention_required', { agentName });

    return false;
  }

  /**
   * Enregistre une tentative de récupération
   */
  private recordRecoveryAttempt(agentName: string, attempt: RecoveryAttempt): void {
    const history = this.recoveryHistory.get(agentName) || [];
    history.push(attempt);

    // Garder seulement les 100 dernières tentatives
    if (history.length > 100) {
      history.splice(0, history.length - 100);
    }

    this.recoveryHistory.set(agentName, history);
  }

  /**
   * Vérifie si un agent est en cooldown
   */
  private isAgentInCooldown(agentName: string): boolean {
    const cooldown = this.recoveryCooldowns.get(agentName);
    return cooldown && (Date.now() - cooldown) < 0;
  }

  /**
   * Définit un cooldown pour un agent
   */
  private setAgentCooldown(agentName: string, delay: number): void {
    this.recoveryCooldowns.set(agentName, Date.now() + delay);
  }

  /**
   * Utilitaires
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private async adjustAgentTimeout(agentName: string, timeout: number): Promise<void> {
    // Implémentation pour ajuster le timeout de l'agent
    this.log(`⏱️ Adjusting timeout for ${agentName} to ${timeout}ms`);
  }

  private async recreateDatabaseConnection(): Promise<void> {
    // Implémentation pour recréer la connexion DB
    this.log('🗄️ Recreating database connection');
  }

  private async checkNetworkConnectivity(): Promise<boolean> {
    return new Promise((resolve) => {
      require('dns').lookup('google.com', (error: any) => {
        resolve(!error);
      });
    });
  }

  private sendAlert(agentName: string, message: string): void {
    this.log(`🚨 ALERT: ${agentName} - ${message}`);

    // Ici on pourrait intégrer Slack, email, etc.
    this.emit('critical_alert', { agentName, message, timestamp: Date.now() });
  }

  /**
   * Récupère l'historique de récupération d'un agent
   */
  public getRecoveryHistory(agentName: string): RecoveryAttempt[] {
    return this.recoveryHistory.get(agentName) || [];
  }

  /**
   * Récupère les statistiques de récupération
   */
  public getRecoveryStats(): { [agentName: string]: any } {
    const stats: { [agentName: string]: any } = {};

    for (const [agentName, history] of this.recoveryHistory.entries()) {
      const successful = history.filter(attempt => attempt.success).length;
      const failed = history.length - successful;
      const avgDuration = history.length > 0
        ? history.reduce((sum, attempt) => sum + attempt.duration, 0) / history.length
        : 0;

      stats[agentName] = {
        totalAttempts: history.length,
        successful,
        failed,
        successRate: history.length > 0 ? (successful / history.length) * 100 : 0,
        avgDuration: Math.round(avgDuration),
        lastAttempt: history.length > 0 ? history[history.length - 1].timestamp : 0
      };
    }

    return stats;
  }

  /**
   * Logging
   */
  private log(message: string): void {
    const timestamp = new Date().toISOString();
    const logEntry = `[${timestamp}] ${message}\n`;

    fs.appendFileSync(this.logPath, logEntry);
    console.log(`[RECOVERY] ${message}`);
  }
}

// Export singleton instance
export const agentAutoRecovery = new AgentAutoRecovery();