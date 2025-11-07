/**
 * 🛡️ Rate Limiter Avancé
 * Protection contre les abus et les attaques par déni de service
 */

import rateLimit, {
  RateLimitRequestHandler,
  Options,
} from 'express-rate-limit';
import { MemoryStore } from 'express-rate-limit';

export interface RateLimitConfig {
  windowMs: number;
  max: number;
  message: string;
  standardHeaders: boolean;
  legacyHeaders: boolean;
  skipSuccessfulRequests?: boolean;
  skipFailedRequests?: boolean;
  keyGenerator?: (req: any) => string;
  handler?: (req: any, res: any) => void;
}

export interface RateLimitTier {
  name: string;
  windowMs: number;
  max: number;
  message: string;
  skipSuccessfulRequests?: boolean;
  skipFailedRequests?: boolean;
}

export class RateLimiterService {
  private static instances: Map<string, RateLimitRequestHandler> = new Map();

  /**
   * 🎯 Créer un rate limiter de base
   */
  static createBasic(
    config: Partial<RateLimitConfig> = {}
  ): RateLimitRequestHandler {
    const defaultConfig: RateLimitConfig = {
      windowMs: 15 * 60 * 1000, // 15 minutes
      max: 100, // 100 requêtes par fenêtre
      message: 'Too many requests from this IP, please try again later.',
      standardHeaders: true,
      legacyHeaders: false,
      ...config,
    };

    return rateLimit({
      windowMs: defaultConfig.windowMs,
      max: defaultConfig.max,
      message: defaultConfig.message,
      standardHeaders: defaultConfig.standardHeaders,
      legacyHeaders: defaultConfig.legacyHeaders,
      store: new MemoryStore(),
      skipSuccessfulRequests: defaultConfig.skipSuccessfulRequests,
      skipFailedRequests: defaultConfig.skipFailedRequests,
      keyGenerator: defaultConfig.keyGenerator,
      handler:
        defaultConfig.handler ||
        ((req, res) => {
          res.status(429).json({
            error: 'Rate limit exceeded',
            message:
              typeof defaultConfig.message === 'string'
                ? defaultConfig.message
                : defaultConfig.message.error,
            retryAfter:
              Math.ceil(defaultConfig.windowMs / 1000 / 60) + ' minutes',
            timestamp: new Date().toISOString(),
            ip: req.ip || req.connection.remoteAddress,
            path: req.path,
          });
        }),
    });
  }

  /**
   * 🔐 Créer un rate limiter strict pour les endpoints critiques
   */
  static createStrict(
    config: Partial<RateLimitConfig> = {}
  ): RateLimitRequestHandler {
    return this.createBasic({
      windowMs: 15 * 60 * 1000, // 15 minutes
      max: 10, // 10 requêtes par fenêtre
      message: 'Too many requests to this critical endpoint',
      skipSuccessfulRequests: false,
      skipFailedRequests: false,
      ...config,
    });
  }

  /**
   * 🚀 Créer un rate limiter permissif pour les endpoints publics
   */
  static createPermissive(
    config: Partial<RateLimitConfig> = {}
  ): RateLimitRequestHandler {
    return this.createBasic({
      windowMs: 15 * 60 * 1000, // 15 minutes
      max: 1000, // 1000 requêtes par fenêtre
      message: 'Too many requests, please slow down',
      ...config,
    });
  }

  /**
   * 💰 Créer un rate limiter pour les endpoints de trading
   */
  static createTradingLimiter(
    config: Partial<RateLimitConfig> = {}
  ): RateLimitRequestHandler {
    return this.createBasic({
      windowMs: 60 * 1000, // 1 minute
      max: 30, // 30 trades par minute
      message: 'Trading rate limit exceeded',
      skipSuccessfulRequests: false,
      skipFailedRequests: false,
      keyGenerator: (req) => {
        // Utiliser l'ID utilisateur si disponible, sinon l'IP
        return req.user?.id || req.ip || 'unknown';
      },
      ...config,
    });
  }

  /**
   * 📊 Créer un rate limiter pour les API de données
   */
  static createDataLimiter(
    config: Partial<RateLimitConfig> = {}
  ): RateLimitRequestHandler {
    return this.createBasic({
      windowMs: 1 * 60 * 1000, // 1 minute
      max: 200, // 200 requêtes par minute
      message: 'Data API rate limit exceeded',
      skipSuccessfulRequests: false,
      ...config,
    });
  }

  /**
   * 🤖 Créer un rate limiter pour les agents IA
   */
  static createAgentLimiter(
    config: Partial<RateLimitConfig> = {}
  ): RateLimitRequestHandler {
    return this.createBasic({
      windowMs: 5 * 60 * 1000, // 5 minutes
      max: 50, // 50 actions d'agent par 5 minutes
      message: 'Agent rate limit exceeded',
      keyGenerator: (req) => {
        // Utiliser l'ID de l'agent depuis les params
        return `agent:${req.params.agentId || 'unknown'}`;
      },
      ...config,
    });
  }

  /**
   * 🔍 Créer un rate limiter basé sur l'utilisateur
   */
  static createUserBasedLimiter(
    config: Partial<RateLimitConfig> = {}
  ): RateLimitRequestHandler {
    return this.createBasic({
      windowMs: 15 * 60 * 1000, // 15 minutes
      max: 500, // 500 requêtes par utilisateur par 15 minutes
      message: 'User rate limit exceeded',
      keyGenerator: (req) => {
        // Prioriser l'ID utilisateur authentifié
        return req.user?.id || req.ip || 'anonymous';
      },
      ...config,
    });
  }

  /**
   * 📈 Créer un rate limiter à plusieurs niveaux (tiered)
   */
  static createTieredLimiter(tiers: RateLimitTier[]): RateLimitRequestHandler {
    return (req, res, next) => {
      // Tester chaque tier du plus strict au plus permissif
      for (const tier of tiers) {
        const limiter = this.createBasic({
          windowMs: tier.windowMs,
          max: tier.max,
          message: tier.message,
          skipSuccessfulRequests: tier.skipSuccessfulRequests,
          skipFailedRequests: tier.skipFailedRequests,
        });

        // Stocker le limiter pour cette tier
        const key = `tiered_${tier.name}`;
        if (!this.instances.has(key)) {
          this.instances.set(key, limiter);
        }

        // Appliquer le limiter
        const storedLimiter = this.instances.get(key)!;
        return storedLimiter(req, res, next);
      }

      next();
    };
  }

  /**
   * 🔄 Créer un rate limiter progressif (adaptive)
   */
  static createAdaptiveLimiter(config: {
    baseMax: number;
    maxMultiplier: number;
    windowMs: number;
    checkInterval: number;
  }): RateLimitRequestHandler {
    const requestCounts = new Map<
      string,
      { count: number; lastReset: number }
    >();
    const loadFactor = { current: 1 }; // Facteur de charge actuel

    // Ajuster le facteur de charge périodiquement
    setInterval(() => {
      // Simuler une charge système (dans un vrai projet, utiliser des métriques réelles)
      const simulatedLoad = Math.random();
      loadFactor.current = 1 + simulatedLoad * config.maxMultiplier;
    }, config.checkInterval);

    return (req, res, next) => {
      const key = req.ip || 'unknown';
      const now = Date.now();

      // Réinitialiser le compteur si nécessaire
      if (
        !requestCounts.has(key) ||
        now - requestCounts.get(key)!.lastReset > config.windowMs
      ) {
        requestCounts.set(key, { count: 0, lastReset: now });
      }

      const counter = requestCounts.get(key)!;
      const adjustedMax = Math.floor(config.baseMax / loadFactor.current);

      if (counter.count >= adjustedMax) {
        return res.status(429).json({
          error: 'Adaptive rate limit exceeded',
          message: 'System under load, please try again later',
          currentLimit: adjustedMax,
          baseLimit: config.baseMax,
          loadFactor: loadFactor.current.toFixed(2),
          retryAfter: Math.ceil(config.windowMs / 1000) + ' seconds',
          timestamp: new Date().toISOString(),
        });
      }

      counter.count++;
      next();
    };
  }

  /**
   * 🧹 Nettoyer les anciennes instances de rate limiters
   */
  static cleanup(): void {
    this.instances.clear();
  }

  /**
   * 📊 Obtenir des statistiques sur les rate limiters
   */
  static getStats(): { activeLimiters: number; types: string[] } {
    return {
      activeLimiters: this.instances.size,
      types: Array.from(this.instances.keys()),
    };
  }

  /**
   * 🎯 Créer un middleware de rate limiting avec whitelist
   */
  static createWithWhitelist(
    config: Partial<RateLimitConfig>,
    whitelist: string[] = []
  ): RateLimitRequestHandler {
    return this.createBasic({
      ...config,
      skip: (req) => {
        const clientIp = req.ip || req.connection.remoteAddress;
        return whitelist.includes(clientIp!);
      },
    });
  }

  /**
   * 🎯 Créer un middleware de rate limiting avec blacklist
   */
  static createWithBlacklist(
    config: Partial<RateLimitConfig>,
    blacklist: string[] = []
  ): RateLimitRequestHandler {
    return rateLimit({
      windowMs: config.windowMs || 15 * 60 * 1000,
      max: config.max || 100,
      message: config.message || 'Rate limit exceeded',
      skip: (req) => {
        const clientIp = req.ip || req.connection.remoteAddress;
        return blacklist.includes(clientIp || '');
      },
      handler: (req, res) => {
        const clientIp = req.ip || req.connection.remoteAddress;
        if (blacklist.includes(clientIp || '')) {
          return res.status(403).json({
            error: 'Forbidden',
            message: 'Access denied from this IP address',
            timestamp: new Date().toISOString(),
          });
        }
        res.status(429).json({
          error: 'Too many requests',
          message: config.message || 'Rate limit exceeded',
        });
      },
    }) as any;
  }
}

// Export des rate limiters prédéfinis
export const rateLimiters = {
  // Limiter général pour toutes les API
  general: RateLimiterService.createBasic({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 1000, // 1000 requêtes par 15 minutes
    message: {
      error: 'General API rate limit exceeded',
      retryAfter: '15 minutes',
    },
  }),

  // Limiter strict pour les endpoints critiques
  auth: RateLimiterService.createStrict({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 5, // 5 tentatives d'auth par 15 minutes
    message: {
      error: 'Authentication rate limit exceeded',
      retryAfter: '15 minutes',
      type: 'auth_limit',
    },
  }),

  // Limiter pour les trades
  trading: RateLimiterService.createTradingLimiter(),

  // Limiter pour les données de marché
  market: RateLimiterService.createDataLimiter({
    windowMs: 1 * 60 * 1000, // 1 minute
    max: 300, // 300 requêtes par minute
    message: {
      error: 'Market data rate limit exceeded',
      retryAfter: '1 minute',
    },
  }),

  // Limiter pour les agents
  agents: RateLimiterService.createAgentLimiter(),

  // Limiter pour les requêtes WebSocket
  websocket: RateLimiterService.createStrict({
    windowMs: 1 * 60 * 1000, // 1 minute
    max: 10, // 10 connexions WebSocket par minute
    message: {
      error: 'WebSocket connection rate limit exceeded',
      retryAfter: '1 minute',
      type: 'websocket_limit',
    },
  }),

  // Limiter pour les health checks (très permissif)
  health: RateLimiterService.createPermissive({
    windowMs: 1 * 60 * 1000, // 1 minute
    max: 60, // 60 health checks par minute
    message: {
      error: 'Health check rate limit exceeded',
      retryAfter: '1 minute',
    },
  }),
};

export default RateLimiterService;
