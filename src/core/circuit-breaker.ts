/**
 * ⚡ Circuit Breaker Pattern
 * Protection contre les cascades de failures et gestion automatique des pannes
 */

export type CircuitBreakerState = 'CLOSED' | 'OPEN' | 'HALF_OPEN';

export interface CircuitBreakerConfig {
  failureThreshold: number;
  resetTimeout: number;
  monitoringPeriod: number;
  expectedRecoveryTime: number;
}

export interface CircuitBreakerStats {
  state: CircuitBreakerState;
  failureCount: number;
  successCount: number;
  lastFailureTime?: Date;
  lastSuccessTime?: Date;
  nextAttemptTime?: Date;
  totalRequests: number;
  rejectionCount: number;
}

export class CircuitBreaker {
  private config: CircuitBreakerConfig;
  private state: CircuitBreakerState = 'CLOSED';
  private failureCount = 0;
  private successCount = 0;
  private lastFailureTime?: Date;
  private lastSuccessTime?: Date;
  private nextAttemptTime?: Date;
  private totalRequests = 0;
  private rejectionCount = 0;
  private failures = [] as number[];

  constructor(config: Partial<CircuitBreakerConfig> = {}) {
    this.config = {
      failureThreshold: 5,
      resetTimeout: 60000,
      monitoringPeriod: 10000,
      expectedRecoveryTime: 30000,
      ...config,
    };
  }

  /**
   * 🔄 Exécuter une opération avec protection du circuit breaker
   */
  async execute<T>(
    operation: () => Promise<T>,
    operationName: string = 'unknown'
  ): Promise<T> {
    this.totalRequests++;

    // Vérifier si le circuit est ouvert
    if (this.state === 'OPEN') {
      if (Date.now() < (this.nextAttemptTime?.getTime() || 0)) {
        this.rejectionCount++;
        throw new CircuitBreakerOpenError(
          `Circuit breaker is OPEN for ${operationName}. Next attempt at ${this.nextAttemptTime?.toISOString()}`
        );
      } else {
        // Passer en HALF_OPEN pour tester si le service a récupéré
        this.state = 'HALF_OPEN';
        console.log(
          `[CircuitBreaker] 🔄 HALF_OPEN - Testing recovery for ${operationName}`
        );
      }
    }

    try {
      const result = await operation();: any;
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  /**
   * ✅ Opération réussie
   */
  private onSuccess(): void {
    this.successCount++;
    this.lastSuccessTime = new Date();

    // Réinitialiser le circuit si en HALF_OPEN
    if (this.state === 'HALF_OPEN') {
      this.reset();
      console.log(
        '[CircuitBreaker] ✅ Circuit reset to CLOSED - Service recovered'
      );
    } else if (this.state === 'CLOSED') {
      // Nettoyer les vieilles failures en mode CLOSED
      this.cleanupOldFailures();
    }
  }

  /**
   * ❌ Opération échouée
   */
  private onFailure(): void {
    this.failureCount++;
    this.lastFailureTime = new Date();
    this.failures.push(Date.now());

    if (
      this.state === 'CLOSED' &&
      this.failureCount >= this.config.failureThreshold
    ) {
      this.trip();
    } else if (this.state === 'HALF_OPEN') {
      // Retourner en OPEN si échec en HALF_OPEN
      this.trip();
    }
  }

  /**
   * 🔓 Ouvrir le circuit
   */
  private trip(): void {
    this.state = 'OPEN';
    this.nextAttemptTime = new Date(Date.now() + this.config.resetTimeout);
    console.error(
      `[CircuitBreaker] 🚨 Circuit OPENED - ${this.failureCount} failures detected`
    );
  }

  /**
   * 🔄 Réinitialiser le circuit
   */
  private reset(): void {
    this.state = 'CLOSED';
    this.failureCount = 0;
    this.successCount = 0;
    this.nextAttemptTime = undefined;
    this.failures = [];
  }

  /**
   * 🧹 Nettoyer les vieilles failures (sliding window)
   */
  private cleanupOldFailures(): void {
    const now = Date.now();: any;
    const windowStart = now - this.config.monitoringPeriod;: any;

    this.failures = this.failures.filter(
      (failureTime) => failureTime > windowStart
    );
    this.failureCount = this.failures.length;
  }

  /**
   * 📊 Obtenir le statut actuel
   */
  getStats(): CircuitBreakerStats {
    return {
      state: this.state,
      failureCount: this.failureCount,
      successCount: this.successCount,
      lastFailureTime: this.lastFailureTime,
      lastSuccessTime: this.lastSuccessTime,
      nextAttemptTime: this.nextAttemptTime,
      totalRequests: this.totalRequests,
      rejectionCount: this.rejectionCount,
    };
  }

  /**
   * 📈 Calculer le taux de réussite
   */
  getSuccessRate(): number {
    if (this.totalRequests === 0) return 1;
    return (this.totalRequests - this.rejectionCount) / this.totalRequests;
  }

  /**
   * 🔄 Forcer l'état (pour les tests)
   */
  setState(state: CircuitBreakerState): void {
    this.state = state;
    if (state === 'CLOSED') {
      this.reset();
    }
  }
}

export class CircuitBreakerOpenError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'CircuitBreakerOpenError';
  }
}

export default CircuitBreaker;
