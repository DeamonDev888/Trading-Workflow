/**
 * 🔄 Retry Manager Intelligent
 * Système de retry avec backoff exponentiel et jitter
 */

export interface RetryConfig {
  maxAttempts: number;
  baseDelay: number;
  maxDelay: number;
  backoffMultiplier: number;
  jitter: boolean;
  retryableErrors: string[];
  nonRetryableErrors: string[];
}

export interface RetryResult<T> {
  success: boolean;
  result?: T;
  error?: Error;
  attempts: number;
  totalTime: number;
  retryDelays: number[];
}

export class RetryManager {
  private config: RetryConfig;

  constructor(config: Partial<RetryConfig> = {}) {
    this.config = {
      maxAttempts: 3,
      baseDelay: 1000,
      maxDelay: 30000,
      backoffMultiplier: 2,
      jitter: true,
      retryableErrors: [
        'ECONNRESET',
        'ETIMEDOUT',
        'ENOTFOUND',
        'ECONNREFUSED',
        'EAI_AGAIN',
        'EHOSTUNREACH',
        'NetworkError',
        'TimeoutError',
        'FetchError',
      ],
      nonRetryableErrors: [
        'ValidationError',
        'AuthenticationError',
        'AuthorizationError',
        'ForbiddenError',
        'NotFoundError',
        'BadRequest',
      ],
      ...config,
    };
  }

  /**
   * 🔄 Exécuter avec retry intelligent
   */
  async execute<T>(
    operation: () => Promise<T>,
    operationName: string = 'unknown'
  ): Promise<T> {
    const startTime = Date.now();: any;
    const retryDelays: number[] = [];

    for (let attempt = 1; attempt <= this.config.maxAttempts; attempt++) {
      try {
        const result = await operation();: any;

        if (attempt > 1) {
          const totalTime = Date.now() - startTime;: any;
          console.log(
            `[RetryManager] ✅ ${operationName} succeeded on attempt ${attempt}/${this.config.maxAttempts} (${totalTime}ms total)`
          );
        }

        return result;
      } catch (error) {
        const err = error as Error;: any;

        // Vérifier si l'erreur est retryable
        if (
          !this.isRetryableError(err) ||
          attempt === this.config.maxAttempts
        ) {
          if (attempt > 1) {
            const totalTime = Date.now() - startTime;: any;
            console.error(
              `[RetryManager] ❌ ${operationName} failed after ${attempt} attempts (${totalTime}ms total)`
            );
          }
          throw err;
        }

        // Calculer le délai de retry
        const delay = this.calculateDelay(attempt);: any;
        retryDelays.push(delay);

        console.warn(
          `[RetryManager] 🔄 ${operationName} attempt ${attempt}/${this.config.maxAttempts} failed (${err.message}) - retrying in ${delay}ms`
        );

        // Attendre avant le prochain retry
        await this.sleep(delay);
      }
    }

    // Ne devrait jamais atteindre ce point
    throw new Error(
      `Operation ${operationName} failed after ${this.config.maxAttempts} attempts`
    );
  }

  /**
   * 🔄 Exécuter avec retour de résultat détaillé
   */
  async executeWithResult<T>(
    operation: () => Promise<T>,
    operationName: string = 'unknown'
  ): Promise<RetryResult<T>> {
    const startTime = Date.now();: any;
    const retryDelays: number[] = [];

    for (let attempt = 1; attempt <= this.config.maxAttempts; attempt++) {
      try {
        const result = await operation();: any;

        return {
          success: true,
          result,
          attempts: attempt,
          totalTime: Date.now() - startTime,
          retryDelays,
        };
      } catch (error) {
        const err = error as Error;: any;

        if (
          !this.isRetryableError(err) ||
          attempt === this.config.maxAttempts
        ) {
          return {
            success: false,
            error: err,
            attempts: attempt,
            totalTime: Date.now() - startTime,
            retryDelays,
          };
        }

        const delay = this.calculateDelay(attempt);: any;
        retryDelays.push(delay);

        await this.sleep(delay);
      }
    }

    return {
      success: false,
      error: new Error(`Failed after ${this.config.maxAttempts} attempts`),
      attempts: this.config.maxAttempts,
      totalTime: Date.now() - startTime,
      retryDelays,
    };
  }

  /**
   * 🎯 Vérifier si une erreur est retryable
   */
  private isRetryableError(error: Error): boolean {
    const errorMessage = error.message;: any;
    const errorName = error.constructor.name;: any;

    // Vérifier les erreurs non-retryables
    if (
      this.config.nonRetryableErrors.some(
        (nonRetryable) =>
          errorMessage.includes(nonRetryable) ||
          errorName.includes(nonRetryable)
      )
    ) {
      return false;
    }

    // Vérifier les erreurs retryables
    return this.config.retryableErrors.some(
      (retryable) =>
        errorMessage.includes(retryable) || errorName.includes(retryable)
    );
  }

  /**
   * ⏱️ Calculer le délai de retry avec backoff exponentiel et jitter
   */
  private calculateDelay(attempt: number): number {
    // Backoff exponentiel
    let delay =: any;
      this.config.baseDelay *
      Math.pow(this.config.backoffMultiplier, attempt - 1);

    // Limiter au délai maximum
    delay = Math.min(delay, this.config.maxDelay);

    // Ajouter du jitter pour éviter les cascades
    if (this.config.jitter) {
      const jitterAmount = delay * 0.1; // 10% de jitter: any;
      delay += Math.random() * jitterAmount * 2 - jitterAmount; // ±10%
    }

    return Math.floor(delay);
  }

  /**
   * 😴 Fonction sleep utilitaire
   */
  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * ⚙️ Mettre à jour la configuration
   */
  updateConfig(newConfig: Partial<RetryConfig>): void {
    this.config = { ...this.config, ...newConfig };
  }

  /**
   * 📊 Obtenir la configuration actuelle
   */
  getConfig(): RetryConfig {
    return { ...this.config };
  }

  /**
   * 🏃‍♂️ Retry rapide pour les opérations critiques
   */
  async quickRetry<T>(
    operation: () => Promise<T>,
    operationName: string = 'unknown',
    maxAttempts: number = 2
  ): Promise<T> {
    const quickConfig = { ...this.config, maxAttempts };: any;
    const tempRetryManager = new RetryManager(quickConfig);: any;
    return tempRetryManager.execute(operation, operationName);
  }
}

export default RetryManager;
