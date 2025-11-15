/**
 * 🚀 AGENT LAUNCHER - PARALLEL AGENT MANAGEMENT
 * Lance tous les AI agents en parallèle avec monitoring et auto-recovery
 * Q1 2025 Roadmap - Final Implementation
 */

import { EventEmitter } from 'events';
import { spawn, ChildProcess } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';
import { agentHealthMonitor } from './agent_health_monitor';
import { agentAutoRecovery } from './agent_auto_recovery';
import { databaseManager } from './database_config';

interface AgentConfig {
  name: string;
  script: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  dependencies: string[];
  environment: { [key: string]: string };
  maxMemoryMB: number;
  timeout: number;
  restartPolicy: 'always' | 'on-failure' | 'never';
  healthCheckInterval: number;
}

interface AgentProcess {
  config: AgentConfig;
  process?: ChildProcess;
  pid?: number;
  startTime: number;
  restartCount: number;
  lastHealthCheck: number;
  status: 'starting' | 'running' | 'stopped' | 'error' | 'restarting';
  logs: string[];
}

export class AgentLauncher extends EventEmitter {
  private agents: Map<string, AgentProcess> = new Map();
  private isRunning: boolean = false;
  private healthCheckInterval: NodeJS.Timeout | null = null;
  private logPath: string = path.join(__dirname, '../logs/agent_launcher.log');

  constructor() {
    super();
    this.initializeLogging();
    this.loadAgentConfigurations();
  }

  /**
   * Initialise le système de logging
   */
  private initializeLogging(): void {
    const logDir = path.dirname(this.logPath);
    if (!fs.existsSync(logDir)) {
      fs.mkdirSync(logDir, { recursive: true });
    }

    const header = `\n🚀 AGENT LAUNCHER - ${new Date().toISOString()}\n` +
      `==============================================\n`;

    fs.appendFileSync(this.logPath, header);
    this.log('✅ Agent Launcher initialized');
  }

  /**
   * Charge la configuration de tous les agents
   */
  private loadAgentConfigurations(): void {
    const agentConfigs: AgentConfig[] = [
      {
        name: 'risk-agent',
        script: 'src/agents/risk_agent.py',
        description: 'Risk Management & Position Sizing',
        priority: 'high',
        dependencies: [],
        environment: { AGENT_TYPE: 'risk', LOG_LEVEL: 'info' },
        maxMemoryMB: 512,
        timeout: 30000,
        restartPolicy: 'always',
        healthCheckInterval: 10000
      },
      {
        name: 'strategy-agent',
        script: 'src/agents/strategy_agent.py',
        description: 'Trading Strategy Generation',
        priority: 'high',
        dependencies: [],
        environment: { AGENT_TYPE: 'strategy', LOG_LEVEL: 'info' },
        maxMemoryMB: 1024,
        timeout: 60000,
        restartPolicy: 'always',
        healthCheckInterval: 15000
      },
      {
        name: 'funding-agent',
        script: 'src/agents/funding_agent.py',
        description: 'Funding Rate Arbitrage',
        priority: 'medium',
        dependencies: [],
        environment: { AGENT_TYPE: 'funding', LOG_LEVEL: 'info' },
        maxMemoryMB: 256,
        timeout: 10000,
        restartPolicy: 'always',
        healthCheckInterval: 5000
      },
      {
        name: 'sentiment-agent',
        script: 'src/agents/sentiment_analysis_agent.py',
        description: 'Market Sentiment Analysis',
        priority: 'low',
        dependencies: [],
        environment: { AGENT_TYPE: 'sentiment', LOG_LEVEL: 'info' },
        maxMemoryMB: 512,
        timeout: 45000,
        restartPolicy: 'on-failure',
        healthCheckInterval: 20000
      },
      {
        name: 'hyperliquid-agent',
        script: 'src/hyperliquid/hyperliquid_mainnet_agent.py',
        description: 'HyperLiquid Trading Execution',
        priority: 'high',
        dependencies: [],
        environment: {
          AGENT_TYPE: 'trading',
          EXCHANGE: 'hyperliquid',
          LOG_LEVEL: 'info',
          MODE: 'paper_trading'
        },
        maxMemoryMB: 512,
        timeout: 15000,
        restartPolicy: 'always',
        healthCheckInterval: 3000
      },
      {
        name: 'data-aggregator',
        script: 'src/agents/data_aggregator.py',
        description: 'Market Data Aggregation',
        priority: 'high',
        dependencies: [],
        environment: { AGENT_TYPE: 'data', LOG_LEVEL: 'info' },
        maxMemoryMB: 768,
        timeout: 20000,
        restartPolicy: 'always',
        healthCheckInterval: 8000
      },
      {
        name: 'reliability-monitor',
        script: 'src/agents/reliability_monitor.py',
        description: 'System Reliability Monitoring',
        priority: 'medium',
        dependencies: [],
        environment: { AGENT_TYPE: 'monitor', LOG_LEVEL: 'info' },
        maxMemoryMB: 128,
        timeout: 10000,
        restartPolicy: 'on-failure',
        healthCheckInterval: 10000
      },
      {
        name: 'manager',
        script: 'src/agents/manager.py',
        description: 'Agent Orchestration Manager',
        priority: 'high',
        dependencies: ['risk-agent', 'strategy-agent', 'hyperliquid-agent'],
        environment: { AGENT_TYPE: 'manager', LOG_LEVEL: 'info' },
        maxMemoryMB: 256,
        timeout: 25000,
        restartPolicy: 'always',
        healthCheckInterval: 15000
      }
    ];

    agentConfigs.forEach(config => {
      const process: AgentProcess = {
        config,
        startTime: 0,
        restartCount: 0,
        lastHealthCheck: 0,
        status: 'stopped',
        logs: []
      };

      this.agents.set(config.name, process);
    });

    this.log(`📋 Loaded ${agentConfigs.length} agent configurations`);
  }

  /**
   * Démarre tous les agents en parallèle
   */
  public async startAllAgents(): Promise<void> {
    if (this.isRunning) {
      this.log('⚠️ Agents already running');
      return;
    }

    this.log('🚀 Starting all agents in parallel...');
    this.isRunning = true;

    try {
      // Initialiser le monitoring et l'auto-recovery
      agentHealthMonitor.startHealthMonitoring();

      // Démarrer les agents par ordre de priorité
      const sortedAgents = Array.from(this.agents.values())
        .sort((a, b) => this.getPriorityValue(b.config.priority) - this.getPriorityValue(a.config.priority));

      // Lancer les agents en parallèle par groupes de priorité
      await this.startAgentsByPriority(sortedAgents);

      // Démarrer le monitoring de santé
      this.startHealthMonitoring();

      this.log('✅ All agents started successfully');
      this.emit('agents_started', { count: this.agents.size });

    } catch (error) {
      this.log(`❌ Failed to start agents: ${error.message}`);
      this.isRunning = false;
      throw error;
    }
  }

  /**
   * Démarre les agents par groupes de priorité
   */
  private async startAgentsByPriority(agents: AgentProcess[]): Promise<void> {
    const groups = this.groupAgentsByPriority(agents);

    for (const [priority, groupAgents] of groups.entries()) {
      this.log(`📊 Starting ${priority} priority agents (${groupAgents.length} agents)...`);

      // Démarrer tous les agents du groupe en parallèle
      const startPromises = groupAgents.map(agent => this.startSingleAgent(agent));

      try {
        await Promise.allSettled(startPromises);
        this.log(`✅ ${priority} priority agents started`);

        // Petite pause entre les groupes de priorité
        if (priority !== 'high') {
          await this.sleep(2000);
        }
      } catch (error) {
        this.log(`⚠️ Some ${priority} priority agents failed to start: ${error.message}`);
      }
    }
  }

  /**
   * Regroupe les agents par priorité
   */
  private groupAgentsByPriority(agents: AgentProcess[]): Map<string, AgentProcess[]> {
    const groups = new Map<string, AgentProcess[]>();
    groups.set('high', []);
    groups.set('medium', []);
    groups.set('low', []);

    agents.forEach(agent => {
      groups.get(agent.config.priority)?.push(agent);
    });

    return groups;
  }

  /**
   * Démarre un agent individuel
   */
  private async startSingleAgent(agentProcess: AgentProcess): Promise<void> {
    const agentName = agentProcess.config.name;

    try {
      this.log(`🚀 Starting agent: ${agentName}`);

      // Vérifier les dépendances
      await this.checkDependencies(agentProcess);

      // Définir le statut
      agentProcess.status = 'starting';

      // Préparer les variables d'environnement
      const env = { ...process.env, ...agentProcess.config.environment };
      env['AGENT_NAME'] = agentName;
      env['AGENT_START_TIME'] = Date.now().toString();

      // Démarrer le processus
      const child = spawn('python', [agentProcess.config.script], {
        stdio: ['pipe', 'pipe', 'pipe'],
        cwd: process.cwd(),
        env: env
      });

      // Configurer le processus
      agentProcess.process = child;
      agentProcess.pid = child.pid;
      agentProcess.startTime = Date.now();
      agentProcess.status = 'running';

      // Configurer les handlers
      this.setupAgentProcessHandlers(agentProcess);

      // Attendre que le processus soit prêt
      await this.waitForAgentReady(agentProcess);

      this.log(`✅ Agent ${agentName} started successfully (PID: ${child.pid})`);
      this.emit('agent_started', { agentName, pid: child.pid });

    } catch (error) {
      agentProcess.status = 'error';
      this.log(`❌ Failed to start agent ${agentName}: ${error.message}`);
      throw error;
    }
  }

  /**
   * Vérifie les dépendances d'un agent
   */
  private async checkDependencies(agentProcess: AgentProcess): Promise<void> {
    const { dependencies } = agentProcess.config;

    for (const dependency of dependencies) {
      const depAgent = this.agents.get(dependency);
      if (!depAgent || depAgent.status !== 'running') {
        throw new Error(`Dependency ${dependency} not available for ${agentProcess.config.name}`);
      }
    }
  }

  /**
   * Configure les handlers d'événements du processus agent
   */
  private setupAgentProcessHandlers(agentProcess: AgentProcess): void {
    const agentName = agentProcess.config.name;
    const child = agentProcess.process!;

    // Logging stdout
    child.stdout?.on('data', (data: Buffer) => {
      const message = data.toString().trim();
      agentProcess.logs.push(`[OUT] ${message}`);

      // Garder seulement les 1000 derniers logs
      if (agentProcess.logs.length > 1000) {
        agentProcess.logs.splice(0, agentProcess.logs.length - 1000);
      }

      this.log(`📤 ${agentName}: ${message}`);
    });

    // Logging stderr
    child.stderr?.on('data', (data: Buffer) => {
      const message = data.toString().trim();
      agentProcess.logs.push(`[ERR] ${message}`);
      this.log(`❌ ${agentName}: ${message}`);
    });

    // Handler d'erreur
    child.on('error', (error: Error) => {
      agentProcess.status = 'error';
      this.log(`❌ Agent ${agentName} error: ${error.message}`);
      this.emit('agent_error', { agentName, error });
    });

    // Handler de fermeture
    child.on('close', (code: number, signal: string) => {
      agentProcess.status = 'stopped';
      this.log(`🔴 Agent ${agentName} exited (code: ${code}, signal: ${signal})`);
      this.emit('agent_stopped', { agentName, code, signal });

      // Auto-restart si configuré
      if (agentProcess.config.restartPolicy === 'always' ||
          (agentProcess.config.restartPolicy === 'on-failure' && code !== 0)) {
        this.scheduleAgentRestart(agentProcess);
      }
    });
  }

  /**
   * Attend qu'un agent soit prêt
   */
  private async waitForAgentReady(agentProcess: AgentProcess): Promise<void> {
    const timeout = agentProcess.config.timeout;
    const startTime = Date.now();

    return new Promise((resolve, reject) => {
      const checkReady = () => {
        if (Date.now() - startTime > timeout) {
          reject(new Error(`Agent ${agentProcess.config.name} startup timeout`));
          return;
        }

        // Vérifier si l'agent est prêt (ici on pourrait vérifier un endpoint HTTP)
        const isReady = agentProcess.status === 'running' &&
                       agentProcess.logs.some(log => log.includes('ready') || log.includes('started'));

        if (isReady) {
          resolve();
        } else {
          setTimeout(checkReady, 1000);
        }
      };

      checkReady();
    });
  }

  /**
   * Planifie le redémarrage d'un agent
   */
  private scheduleAgentRestart(agentProcess: AgentProcess): void {
    const delay = Math.min(5000 * Math.pow(2, agentProcess.restartCount), 30000); // Exponential backoff max 30s
    const agentName = agentProcess.config.name;

    this.log(`🔄 Scheduling restart for ${agentName} in ${delay}ms (restart #${agentProcess.restartCount + 1})`);

    setTimeout(async () => {
      try {
        agentProcess.restartCount++;
        agentProcess.status = 'restarting';
        await this.startSingleAgent(agentProcess);
        this.log(`✅ Agent ${agentName} restarted successfully`);
      } catch (error) {
        this.log(`❌ Failed to restart agent ${agentName}: ${error.message}`);
        agentProcess.status = 'error';
      }
    }, delay);
  }

  /**
   * Démarre le monitoring de santé
   */
  private startHealthMonitoring(): void {
    this.healthCheckInterval = setInterval(() => {
      this.performAgentHealthChecks();
    }, 5000); // Check toutes les 5 secondes

    this.log('🔍 Agent health monitoring started');
  }

  /**
   * Effectue les contrôles de santé des agents
   */
  private async performAgentHealthChecks(): Promise<void> {
    for (const [agentName, agentProcess] of this.agents.entries()) {
      try {
        await this.checkAgentHealth(agentProcess);
      } catch (error) {
        this.log(`⚠️ Health check failed for ${agentName}: ${error.message}`);
      }
    }
  }

  /**
   * Vérifie la santé d'un agent
   */
  private async checkAgentHealth(agentProcess: AgentProcess): Promise<void> {
    const now = Date.now();
    const timeSinceLastCheck = now - agentProcess.lastHealthCheck;

    if (timeSinceLastCheck < agentProcess.config.healthCheckInterval) {
      return;
    }

    agentProcess.lastHealthCheck = now;

    // Vérifier si le processus est toujours actif
    if (!agentProcess.process || agentProcess.process.killed) {
      agentProcess.status = 'error';
      this.emit('agent_health_issue', {
        agentName: agentProcess.config.name,
        issue: 'process_not_running'
      });
      return;
    }

    // Vérifier l'utilisation mémoire
    try {
      const memoryUsage = process.memoryUsage();
      const maxMemory = agentProcess.config.maxMemoryMB * 1024 * 1024;

      if (memoryUsage.heapUsed > maxMemory) {
        this.log(`⚠️ Agent ${agentProcess.config.name} memory usage high: ${Math.round(memoryUsage.heapUsed / 1024 / 1024)}MB`);
        this.emit('agent_health_issue', {
          agentName: agentProcess.config.name,
          issue: 'high_memory_usage',
          memoryUsage
        });
      }
    } catch (error) {
      // Ignore memory check errors
    }
  }

  /**
   * Arrête tous les agents
   */
  public async stopAllAgents(): Promise<void> {
    this.log('🛑 Stopping all agents...');
    this.isRunning = false;

    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
      this.healthCheckInterval = null;
    }

    const stopPromises = Array.from(this.agents.values()).map(agent =>
      this.stopSingleAgent(agent)
    );

    try {
      await Promise.allSettled(stopPromises);
      this.log('✅ All agents stopped');
      this.emit('agents_stopped');
    } catch (error) {
      this.log(`⚠️ Some agents failed to stop: ${error.message}`);
    }
  }

  /**
   * Arrête un agent individuel
   */
  private async stopSingleAgent(agentProcess: AgentProcess): Promise<void> {
    const agentName = agentProcess.config.name;

    try {
      if (agentProcess.process && !agentProcess.process.killed) {
        this.log(`🛑 Stopping agent: ${agentName}`);

        // Envoyer SIGTERM d'abord
        agentProcess.process.kill('SIGTERM');

        // Attendre 5 secondes puis forcer
        setTimeout(() => {
          if (agentProcess.process && !agentProcess.process.killed) {
            agentProcess.process.kill('SIGKILL');
          }
        }, 5000);

        agentProcess.status = 'stopped';
      }
    } catch (error) {
      this.log(`⚠️ Error stopping agent ${agentName}: ${error.message}`);
    }
  }

  /**
   * Récupère le statut de tous les agents
   */
  public getAgentStatus(): { [agentName: string]: any } {
    const status: { [agentName: string]: any } = {};

    for (const [agentName, agentProcess] of this.agents.entries()) {
      const uptime = agentProcess.startTime > 0 ? Date.now() - agentProcess.startTime : 0;

      status[agentName] = {
        name: agentName,
        description: agentProcess.config.description,
        status: agentProcess.status,
        pid: agentProcess.pid,
        uptime: uptime,
        restartCount: agentProcess.restartCount,
        priority: agentProcess.config.priority,
        memoryLimitMB: agentProcess.config.maxMemoryMB,
        logCount: agentProcess.logs.length,
        lastLog: agentProcess.logs.length > 0 ? agentProcess.logs[agentProcess.logs.length - 1] : null
      };
    }

    return status;
  }

  /**
   * Récupère les logs d'un agent
   */
  public getAgentLogs(agentName: string, lines: number = 100): string[] {
    const agent = this.agents.get(agentName);
    if (!agent) return [];

    return agent.logs.slice(-lines);
  }

  /**
   * Redémarre un agent spécifique
   */
  public async restartAgent(agentName: string): Promise<void> {
    const agentProcess = this.agents.get(agentName);
    if (!agentProcess) {
      throw new Error(`Agent ${agentName} not found`);
    }

    this.log(`🔄 Manually restarting agent: ${agentName}`);

    await this.stopSingleAgent(agentProcess);
    await this.sleep(2000);
    await this.startSingleAgent(agentProcess);

    this.log(`✅ Agent ${agentName} restarted successfully`);
    this.emit('agent_restarted', { agentName });
  }

  /**
   * Utilitaires
   */
  private getPriorityValue(priority: string): number {
    switch (priority) {
      case 'high': return 3;
      case 'medium': return 2;
      case 'low': return 1;
      default: return 0;
    }
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Logging
   */
  private log(message: string): void {
    const timestamp = new Date().toISOString();
    const logEntry = `[${timestamp}] ${message}\n`;

    fs.appendFileSync(this.logPath, logEntry);
    console.log(`[LAUNCHER] ${message}`);
  }
}

// Export singleton instance
export const agentLauncher = new AgentLauncher();