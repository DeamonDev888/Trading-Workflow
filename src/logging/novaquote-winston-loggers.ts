/**
 * 🚀 NOVAQUOTE WINSTON LOGGERS - 7 Expert Loggers System
 * Système complet de logging avec 7 loggers spécialisés pour la plateforme NOVAQUOTE
 */

import winston from 'winston';
const DailyRotateFile = require('winston-daily-rotate-file');
import * as path from 'path';
import * as fs from 'fs';

// Configuration des logs
const LOG_DIR = 'logs';
const LOG_LEVEL = process.env['LOG_LEVEL'] || 'info';
const NODE_ENV = process.env['NODE_ENV'] || 'development';

// Créer le répertoire de logs s'il n'existe pas
if (!fs.existsSync(LOG_DIR)) {
    fs.mkdirSync(LOG_DIR, { recursive: true });
}

// Format commun pour tous les loggers
const createLogFormat = (component: string) => winston.format.combine(
    winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss.SSS' }),
    winston.format.errors({ stack: true }),
    winston.format.json(),
    winston.format.printf(({ timestamp, level, message, ...meta }) => {
        const logEntry = {
            timestamp,
            level: level.toUpperCase(),
            component,
            message,
            ...meta
        };
        return JSON.stringify(logEntry);
    })
);

// Format console pour développement
const createConsoleFormat = (component: string) => winston.format.combine(
    winston.format.colorize(),
    winston.format.timestamp({ format: 'HH:mm:ss.SSS' }),
    winston.format.printf(({ timestamp, level, message, ...meta }) => {
        let msg = `${timestamp} [${level}] [${component}] ${message}`;
        if (Object.keys(meta).length > 0) {
            msg += ` ${JSON.stringify(meta)}`;
        }
        return msg;
    })
);

/**
 * 1. API Logger - Pour les logs d'API REST et requêtes HTTP
 */
export const apiLogger = winston.createLogger({
    level: LOG_LEVEL,
    format: createLogFormat('API'),
    transports: [
        new winston.transports.Console({
            format: createConsoleFormat('API'),
            level: NODE_ENV === 'production' ? 'info' : 'debug'
        }),
        new DailyRotateFile({
            filename: path.join(LOG_DIR, 'api-%DATE%.log'),
            datePattern: 'YYYY-MM-DD',
            maxSize: '50m',
            maxFiles: '30d',
            format: createLogFormat('API')
        })
    ],
    exceptionHandlers: [
        new DailyRotateFile({
            filename: path.join(LOG_DIR, 'api-exceptions-%DATE%.log'),
            datePattern: 'YYYY-MM-DD',
            maxSize: '20m',
            maxFiles: '30d'
        })
    ]
});

/**
 * 2. WebSocket Logger - Pour les logs WebSocket et temps réel
 */
export const wsLogger = winston.createLogger({
    level: LOG_LEVEL,
    format: createLogFormat('WS'),
    transports: [
        new winston.transports.Console({
            format: createConsoleFormat('WS'),
            level: NODE_ENV === 'production' ? 'info' : 'debug'
        }),
        new DailyRotateFile({
            filename: path.join(LOG_DIR, 'websocket-%DATE%.log'),
            datePattern: 'YYYY-MM-DD',
            maxSize: '30m',
            maxFiles: '30d',
            format: createLogFormat('WS')
        })
    ]
});

/**
 * 3. Agents Logger - Pour les logs des agents IA et cycles de vie
 */
export const agentsLogger = winston.createLogger({
    level: LOG_LEVEL,
    format: createLogFormat('AGENTS'),
    transports: [
        new winston.transports.Console({
            format: createConsoleFormat('AGENTS'),
            level: NODE_ENV === 'production' ? 'info' : 'debug'
        }),
        new DailyRotateFile({
            filename: path.join(LOG_DIR, 'agents-%DATE%.log'),
            datePattern: 'YYYY-MM-DD',
            maxSize: '40m',
            maxFiles: '60d',
            format: createLogFormat('AGENTS')
        })
    ]
});

/**
 * 4. Backtests Logger - Pour les logs de backtesting et optimisation
 */
export const backtestsLogger = winston.createLogger({
    level: LOG_LEVEL,
    format: createLogFormat('BACKTESTS'),
    transports: [
        new winston.transports.Console({
            format: createConsoleFormat('BACKTESTS'),
            level: NODE_ENV === 'production' ? 'info' : 'debug'
        }),
        new DailyRotateFile({
            filename: path.join(LOG_DIR, 'backtests-%DATE%.log'),
            datePattern: 'YYYY-MM-DD',
            maxSize: '60m',
            maxFiles: '90d',
            format: createLogFormat('BACKTESTS')
        })
    ]
});

/**
 * 5. Trading Logger - Pour les logs de trading et transactions
 */
export const tradingLogger = winston.createLogger({
    level: LOG_LEVEL,
    format: createLogFormat('TRADING'),
    transports: [
        new winston.transports.Console({
            format: createConsoleFormat('TRADING'),
            level: NODE_ENV === 'production' ? 'info' : 'debug'
        }),
        new DailyRotateFile({
            filename: path.join(LOG_DIR, 'trading-%DATE%.log'),
            datePattern: 'YYYY-MM-DD',
            maxSize: '100m',
            maxFiles: '365d', // Garder 1 an pour compliance
            format: createLogFormat('TRADING')
        }),
        // Fichier séparé pour les trades uniquement (format JSON structuré)
        new DailyRotateFile({
            filename: path.join(LOG_DIR, 'trades-only-%DATE%.log'),
            datePattern: 'YYYY-MM-DD',
            maxSize: '50m',
            maxFiles: '365d',
            format: createLogFormat('TRADING')
        })
    ]
});

/**
 * 6. Wallets Logger - Pour les logs de portefeuille et wallet
 */
export const walletsLogger = winston.createLogger({
    level: LOG_LEVEL,
    format: createLogFormat('WALLETS'),
    transports: [
        new winston.transports.Console({
            format: createConsoleFormat('WALLETS'),
            level: NODE_ENV === 'production' ? 'info' : 'debug'
        }),
        new DailyRotateFile({
            filename: path.join(LOG_DIR, 'wallets-%DATE%.log'),
            datePattern: 'YYYY-MM-DD',
            maxSize: '30m',
            maxFiles: '90d',
            format: createLogFormat('WALLETS')
        })
    ]
});

/**
 * 7. System Logger - Pour les logs système et infrastructure
 */
export const systemLogger = winston.createLogger({
    level: LOG_LEVEL,
    format: createLogFormat('SYSTEM'),
    transports: [
        new winston.transports.Console({
            format: createConsoleFormat('SYSTEM'),
            level: NODE_ENV === 'production' ? 'info' : 'debug'
        }),
        new DailyRotateFile({
            filename: path.join(LOG_DIR, 'system-%DATE%.log'),
            datePattern: 'YYYY-MM-DD',
            maxSize: '40m',
            maxFiles: '30d',
            format: createLogFormat('SYSTEM')
        }),
        // Fichier séparé pour les erreurs système critiques
        new DailyRotateFile({
            filename: path.join(LOG_DIR, 'system-errors-%DATE%.log'),
            datePattern: 'YYYY-MM-DD',
            maxSize: '20m',
            maxFiles: '90d',
            level: 'error',
            format: createLogFormat('SYSTEM')
        })
    ],
    exceptionHandlers: [
        new DailyRotateFile({
            filename: path.join(LOG_DIR, 'system-exceptions-%DATE%.log'),
            datePattern: 'YYYY-MM-DD',
            maxSize: '50m',
            maxFiles: '30d'
        })
    ],
    rejectionHandlers: [
        new DailyRotateFile({
            filename: path.join(LOG_DIR, 'system-rejections-%DATE%.log'),
            datePattern: 'YYYY-MM-DD',
            maxSize: '20m',
            maxFiles: '30d'
        })
    ]
});

// Objet contenant tous les loggers
export const novaquoteLoggers = {
    api: apiLogger,
    ws: wsLogger,
    agents: agentsLogger,
    backtests: backtestsLogger,
    trading: tradingLogger,
    wallets: walletsLogger,
    system: systemLogger
};

// Export par défaut
export default novaquoteLoggers;

/**
 * Helper functions pour des logs spécialisés
 */
export const logTrade = (action: string, symbol: string, details: any = {}) => {
    tradingLogger.info(`Trade ${action}: ${symbol}`, {
        action,
        symbol,
        timestamp: new Date().toISOString(),
        ...details
    });
};

export const logAgent = (agentId: string, event: string, details: any = {}) => {
    agentsLogger.info(`Agent ${agentId}: ${event}`, {
        agentId,
        event,
        timestamp: new Date().toISOString(),
        ...details
    });
};

export const logWebSocket = (event: string, details: any = {}) => {
    wsLogger.info(`WebSocket: ${event}`, {
        event,
        timestamp: new Date().toISOString(),
        ...details
    });
};

export const logApiRequest = (method: string, url: string, statusCode: number, duration: number, details: any = {}) => {
    apiLogger.info(`API ${method} ${url} - ${statusCode}`, {
        method,
        url,
        statusCode,
        duration,
        timestamp: new Date().toISOString(),
        ...details
    });
};

export const logSystemError = (error: Error, context: any = {}) => {
    systemLogger.error('System Error', {
        error: {
            name: error.name,
            message: error.message,
            stack: error.stack
        },
        timestamp: new Date().toISOString(),
        ...context
    });
};

// Fonction pour logger les métriques de performance sur tous les loggers
export const logPerformance = (operation: string, duration: number, component: string, details: any = {}) => {
    const logger = novaquoteLoggers[component as keyof typeof novaquoteLoggers] || systemLogger;
    logger.info(`Performance: ${operation}`, {
        operation,
        duration,
        component,
        timestamp: new Date().toISOString(),
        ...details
    });
};

// Initialisation des loggers
systemLogger.info('NOVAQUOTE WINSTON LOGGERS SYSTEM - 7 Expert Loggers Initialized', {
    loggers: Object.keys(novaquoteLoggers),
    logDirectory: LOG_DIR,
    logLevel: LOG_LEVEL,
    environment: NODE_ENV,
    timestamp: new Date().toISOString()
});