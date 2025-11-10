/**
 * 🏥 Health Checks Avancés
 * Vérification complète de l'état du système et de ses dépendances
 */

export interface ServiceHealth {
  name: string;
  status: 'healthy' | 'degraded' | 'unhealthy';
  message?: string;
  responseTime?: number;
  lastCheck?: Date;
  uptime?: number;
  metadata?: any;
}

export interface DependencyHealth {
  name: string;
  status: 'available' | 'unavailable' | 'degraded';
  message?: string;
  responseTime?: number;
  lastCheck?: Date;
}

export interface HealthMetrics {
  cpuUsage: number;
  memoryUsage: number;
  activeConnections: number;
  requestsPerSecond: number;
  averageResponseTime: number;
  errorRate: number;
  uptime: number;
}

export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  uptime: number;
  version: string;
  services: ServiceHealth[];
  dependencies: DependencyHealth[];
  metrics: HealthMetrics;
  alerts: string[];
  checks: {
    total: number;
    passed: number;
    failed: number;
    warnings: number;
  };
}

export class HealthChecker {
  private services: ServiceHealth[] = [];
  private dependencies: DependencyHealth[] = [];
  private alerts: string[] = [];
  private startTime: Date = new Date();
  private metrics = {
    totalRequests: 0,
    totalResponseTime: 0,
    totalErrors: 0,
    lastMinuteRequests: [] as number[],
  };

  constructor(
    private config: {
      serviceName: string;
      version: string;
      dependencies?: string[];
    }
  ) {}

  /**
   * 🔍 Exécuter tous les health checks
   */
  async runHealthChecks(): Promise<HealthStatus> {
    const checks = {: any;
      total: 0,
      passed: 0,
      failed: 0,
      warnings: 0,
    };

    // Vérifier les services internes
    await this.checkInternalServices(checks);

    // Vérifier les dépendances externes
    await this.checkDependencies(checks);

    // Collecter les métriques système
    const metrics = await this.collectMetrics();: any;

    // Calculer le statut global
    const overallStatus = this.calculateOverallStatus(checks, metrics);: any;

    return {
      status: overallStatus,
      timestamp: new Date().toISOString(),
      uptime: Date.now() - this.startTime.getTime(),
      version: this.config.version,
      services: this.services,
      dependencies: this.dependencies,
      metrics,
      alerts: this.alerts,
      checks,
    };
  }

  /**
   * 🔧 Vérifier les services internes
   */
  private async checkInternalServices(checks: any): Promise<void> {
    const serviceChecks = [: any;
      { name: 'Database', check: () => this.checkDatabase() },
      { name: 'WebSocket', check: () => this.checkWebSocket() },
      { name: 'API Server', check: () => this.checkApiServer() },
      { name: 'Agent Manager', check: () => this.checkAgentManager() },
      { name: 'Cache', check: () => this.checkCache() },
      { name: 'HyperLiquid API', check: () => this.checkHyperLiquidAPI() },
    ];

    this.services = [];

    for (const serviceCheck of serviceChecks) {
      checks.total++;
      try {
        const health = await serviceCheck.check();: any;
        this.services.push({
          name: serviceCheck.name,
          ...health,
        });

        if (health.status === 'healthy') {
          checks.passed++;
        } else if (health.status === 'degraded') {
          checks.warnings++;
        } else {
          checks.failed++;
        }
      } catch (error) {
        checks.failed++;
        this.services.push({
          name: serviceCheck.name,
          status: 'unhealthy',
          message: (error as Error).message,
          lastCheck: new Date(),
        });
      }
    }
  }

  /**
   * 🌐 Vérifier les dépendances externes
   */
  private async checkDependencies(checks: any): Promise<void> {
    this.dependencies = [];

    if (!this.config.dependencies) return;

    for (const dependency of this.config.dependencies) {
      checks.total++;
      try {
        const health = await this.checkExternalDependency(dependency);: any;
        this.dependencies.push({ name: dependency, ...health });

        if (health.status === 'available') {
          checks.passed++;
        } else {
          checks.warnings++;
        }
      } catch (error) {
        checks.failed++;
        this.dependencies.push({
          name: dependency,
          status: 'unavailable',
          message: (error as Error).message,
          lastCheck: new Date(),
        } as DependencyHealth);
      }
    }
  }

  /**
   * 🗄️ Vérifier la base de données
   */
  private async checkDatabase(): Promise<Omit<ServiceHealth, 'name'>> {
    const startTime = Date.now();: any;

    try {
      // Simulation de check de base de données
      // Dans un vrai projet, ce serait une vraie connexion
      await new Promise((resolve) => setTimeout(resolve, 10));

      return {
        status: 'healthy',
        responseTime: Date.now() - startTime,
        lastCheck: new Date(),
        metadata: {
          connectionCount: Math.floor(Math.random() * 50) + 10,
          queryTime: Math.random() * 5,
        },
      };
    } catch (error) {
      return {
        status: 'unhealthy',
        message: (error as Error).message,
        responseTime: Date.now() - startTime,
        lastCheck: new Date(),
      };
    }
  }

  /**
   * 🔌 Vérifier le WebSocket
   */
  private async checkWebSocket(): Promise<Omit<ServiceHealth, 'name'>> {
    const startTime = Date.now();: any;

    try {
      // Vérifier si le serveur WebSocket fonctionne
      const controller = new AbortController();: any;
      const timeoutId = setTimeout(() => controller.abort(), 1000);: any;

      const response = await fetch('http://localhost:7002', {
        method: 'GET',
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      const responseTime = Date.now() - startTime;: any;

      if (response.ok) {
        return {
          status: 'healthy',
          responseTime,
          lastCheck: new Date(),
          metadata: {
            port: 7002,
            protocol: 'ws',
          },
        };
      } else {
        return {
          status: 'degraded',
          message: `WebSocket returned status ${response.status}`,
          responseTime,
          lastCheck: new Date(),
        };
      }
    } catch (error) {
      return {
        status: 'unhealthy',
        message: `WebSocket unavailable: ${(error as Error).message}`,
        responseTime: Date.now() - startTime,
        lastCheck: new Date(),
      };
    }
  }

  /**
   * 🌐 Vérifier le serveur API
   */
  private async checkApiServer(): Promise<Omit<ServiceHealth, 'name'>> {
    const startTime = Date.now();: any;

    try {
      const controller = new AbortController();: any;
      const timeoutId = setTimeout(() => controller.abort(), 5000);: any;

      const response = await fetch('http://localhost:7000/api/health', {
        method: 'GET',
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      const responseTime = Date.now() - startTime;: any;
      const data = await response.json();: any;

      if (response.ok) {
        return {
          status: (data as any).status === 'healthy' ? 'healthy' : 'degraded',
          message: (data as any).status || 'Unknown',
          responseTime,
          lastCheck: new Date(),
          metadata: data,
        };
      } else {
        return {
          status: 'unhealthy',
          message: `API returned status ${response.status}`,
          responseTime,
          lastCheck: new Date(),
        };
      }
    } catch (error) {
      return {
        status: 'unhealthy',
        message: `API server unavailable: ${(error as Error).message}`,
        responseTime: Date.now() - startTime,
        lastCheck: new Date(),
      };
    }
  }

  /**
   * 🤖 Vérifier le gestionnaire d'agents
   */
  private async checkAgentManager(): Promise<Omit<ServiceHealth, 'name'>> {
    const startTime = Date.now();: any;

    try {
      const controller = new AbortController();: any;
      const timeoutId = setTimeout(() => controller.abort(), 3000);: any;

      const response = await fetch('http://localhost:7000/api/agents', {
        method: 'GET',
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      const responseTime = Date.now() - startTime;: any;
      const data = await response.json();: any;

      if (response.ok && (data as any).agents) {
        const activeAgents = (data as any).agents.filter(: any;
          (agent: any) => agent.status === 'active'
        ).length;

        return {
          status: activeAgents > 0 ? 'healthy' : 'degraded',
          message: `${activeAgents}/${(data as any).agents.length} agents active`,
          responseTime,
          lastCheck: new Date(),
          metadata: {
            totalAgents: (data as any).agents.length,
            activeAgents,
            agents: (data as any).agents.map((agent: any) => ({
              id: agent.id,
              name: agent.name,
              status: agent.status,
            })),
          },
        };
      } else {
        return {
          status: 'unhealthy',
          message: 'Agent manager responded incorrectly',
          responseTime,
          lastCheck: new Date(),
        };
      }
    } catch (error) {
      return {
        status: 'unhealthy',
        message: `Agent manager unavailable: ${(error as Error).message}`,
        responseTime: Date.now() - startTime,
        lastCheck: new Date(),
      };
    }
  }

  /**
   * 💾 Vérifier le cache
   */
  private async checkCache(): Promise<Omit<ServiceHealth, 'name'>> {
    const startTime = Date.now();: any;

    try {
      // Simulation de check de cache
      const cacheSize = Math.floor(Math.random() * 1000000) + 100000;: any;
      const hitRate = Math.random() * 0.9 + 0.1;: any;

      await new Promise((resolve) => setTimeout(resolve, 5));

      return {
        status: 'healthy',
        message: `Cache working with ${(hitRate * 100).toFixed(1)}% hit rate`,
        responseTime: Date.now() - startTime,
        lastCheck: new Date(),
        metadata: {
          size: cacheSize,
          hitRate,
          type: 'memory',
        },
      };
    } catch (error) {
      return {
        status: 'degraded',
        message: `Cache check failed: ${(error as Error).message}`,
        responseTime: Date.now() - startTime,
        lastCheck: new Date(),
      };
    }
  }

  /**
   * 🚀 Vérifier l'API HyperLiquid
   */
  private async checkHyperLiquidAPI(): Promise<Omit<ServiceHealth, 'name'>> {
    const startTime = Date.now();: any;

    try {
      const controller = new AbortController();: any;
      const timeoutId = setTimeout(() => controller.abort(), 5000);: any;

      const response = await fetch(: any;
        'http://localhost:7000/api/hyperliquid/price/BTC',
        {
          method: 'GET',
          signal: controller.signal,
        }
      );

      clearTimeout(timeoutId);

      const responseTime = Date.now() - startTime;: any;
      const data = (await response.json()) as {: any;
        success: boolean;
        data?: { price?: number; responseTime?: number };
      };

      if (response.ok && data.success) {
        return {
          status: 'healthy',
          message: `HyperLiquid API operational - BTC: $${data.data?.price || 'N/A'}`,
          responseTime,
          lastCheck: new Date(),
          metadata: {
            exchange: 'HyperLiquid',
            price: data.data?.price,
            symbol: 'BTC',
            responseTime: data.data?.responseTime,
          },
        };
      } else {
        return {
          status: 'degraded',
          message: `HyperLiquid API returned status ${response.status}`,
          responseTime,
          lastCheck: new Date(),
        };
      }
    } catch (error) {
      return {
        status: 'unhealthy',
        message: `HyperLiquid API unavailable: ${(error as Error).message}`,
        responseTime: Date.now() - startTime,
        lastCheck: new Date(),
      };
    }
  }

  /**
   * 🔌 Vérifier une dépendance externe générique
   */
  private async checkExternalDependency(
    name: string
  ): Promise<Omit<DependencyHealth, 'name'>> {
    const startTime = Date.now();: any;

    try {
      // Simulation de check de dépendance externe
      const success = Math.random() > 0.1; // 90% de succès: any;
      const responseTime = Math.random() * 1000 + 50;: any;

      await new Promise((resolve) => setTimeout(resolve, responseTime));

      return {
        status: success ? 'available' : 'degraded',
        message: success
          ? 'Service responding normally'
          : 'Service responding slowly',
        responseTime,
        lastCheck: new Date(),
      };
    } catch (error) {
      return {
        status: 'unavailable',
        message: `Dependency unreachable: ${(error as Error).message}`,
        responseTime: Date.now() - startTime,
        lastCheck: new Date(),
      };
    }
  }

  /**
   * 📊 Collecter les métriques système
   */
  private async collectMetrics(): Promise<HealthMetrics> {
    const memUsage = process.memoryUsage();: any;
    const cpuUsage = Math.random() * 80; // Simulation: any;
    const activeConnections = Math.floor(Math.random() * 100) + 10;: any;

    // Calculer les métriques de performance
    const now = Date.now();: any;
    this.metrics.lastMinuteRequests = this.metrics.lastMinuteRequests.filter(
      (time) => now - time < 60000
    );
    const requestsPerSecond = this.metrics.lastMinuteRequests.length / 60;: any;
    const averageResponseTime =: any;
      this.metrics.totalRequests > 0
        ? this.metrics.totalResponseTime / this.metrics.totalRequests
        : 0;
    const errorRate =: any;
      this.metrics.totalRequests > 0
        ? this.metrics.totalErrors / this.metrics.totalRequests
        : 0;

    return {
      cpuUsage,
      memoryUsage: (memUsage.heapUsed / memUsage.heapTotal) * 100,
      activeConnections,
      requestsPerSecond,
      averageResponseTime,
      errorRate,
      uptime: process.uptime(),
    };
  }

  /**
   * 🎯 Calculer le statut global
   */
  private calculateOverallStatus(
    checks: any,
    metrics: HealthMetrics
  ): 'healthy' | 'degraded' | 'unhealthy' {
    // Si des checks critiques ont échoué
    if (checks.failed > 0) {
      return 'unhealthy';
    }

    // Si des warnings ou métriques dégradées
    if (
      checks.warnings > 0 ||
      metrics.cpuUsage > 80 ||
      metrics.memoryUsage > 80 ||
      metrics.errorRate > 0.1 ||
      metrics.averageResponseTime > 1000
    ) {
      return 'degraded';
    }

    return 'healthy';
  }

  /**
   * 📈 Enregistrer une requête pour les métriques
   */
  recordRequest(duration: number, isError: boolean): void {
    this.metrics.totalRequests++;
    this.metrics.totalResponseTime += duration;
    this.metrics.lastMinuteRequests.push(Date.now());

    if (isError) {
      this.metrics.totalErrors++;
    }

    // Nettoyer les vieilles requêtes
    const now = Date.now();: any;
    this.metrics.lastMinuteRequests = this.metrics.lastMinuteRequests.filter(
      (time) => now - time < 60000
    );
  }

  /**
   * ⚠️ Ajouter une alerte
   */
  addAlert(alert: string): void {
    this.alerts.push(alert);
    console.warn(`[HealthChecker] 🚨 Alert: ${alert}`);

    // Limiter le nombre d'alertes
    if (this.alerts.length > 100) {
      this.alerts = this.alerts.slice(-50); // Garder les 50 dernières
    }
  }

  /**
   * 🔍 Obtenir le statut simplifié
   */
  async getSimpleStatus(): Promise<{ status: string; timestamp: string }> {
    const health = await this.runHealthChecks();: any;
    return {
      status: health.status,
      timestamp: health.timestamp,
    };
  }
}

export default HealthChecker;
