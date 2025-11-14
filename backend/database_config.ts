/**
 * 🗄️ POSTGRESQL DATABASE CONFIGURATION
 * Migration et connection pooling pour performances
 * Q1 2025 Roadmap - Item 4.1
 */

import { Pool, PoolConfig, QueryResult } from 'pg';
import { EventEmitter } from 'events';
import * as fs from 'fs';
import * as path from 'path';

interface DatabaseConfig {
  host: string;
  port: number;
  database: string;
  user: string;
  password: string;
  max: number;
  idleTimeoutMillis: number;
  connectionTimeoutMillis: number;
  min: number;
  acquireTimeoutMillis: number;
  createTimeoutMillis: number;
  destroyTimeoutMillis: number;
  reapIntervalMillis: number;
  createRetryIntervalMillis: number;
}

export class DatabaseManager extends EventEmitter {
  private pool: Pool | null = null;
  private config: DatabaseConfig;
  private isPostgreSQL: boolean = false;
  private logPath: string = path.join(__dirname, '../logs/database.log');

  constructor() {
    super();
    this.initializeConfig();
    this.initializeLogging();
  }

  /**
   * Initialise la configuration de la base de données
   */
  private initializeConfig(): void {
    // Configuration pour PostgreSQL (production)
    this.config = {
      host: process.env.DB_HOST || 'localhost',
      port: parseInt(process.env.DB_PORT || '5432'),
      database: process.env.DB_NAME || 'novaquote_prod',
      user: process.env.DB_USER || 'novaquote_user',
      password: process.env.DB_PASSWORD || 'your_secure_password',
      max: 20, // Maximum connections
      min: 5,  // Minimum connections
      idleTimeoutMillis: 30000, // 30 seconds
      connectionTimeoutMillis: 2000, // 2 seconds
      acquireTimeoutMillis: 60000, // 1 minute
      createTimeoutMillis: 30000, // 30 seconds
      destroyTimeoutMillis: 5000, // 5 seconds
      reapIntervalMillis: 1000, // 1 second
      createRetryIntervalMillis: 200 // 200ms
    };

    this.log('📋 Database configuration initialized');
  }

  /**
   * Initialise le système de logging
   */
  private initializeLogging(): void {
    const logDir = path.dirname(this.logPath);
    if (!fs.existsSync(logDir)) {
      fs.mkdirSync(logDir, { recursive: true });
    }

    const header = `\n🗄️ DATABASE MANAGEMENT SYSTEM - ${new Date().toISOString()}\n` +
      `========================================================\n`;

    fs.appendFileSync(this.logPath, header);
    this.log('✅ Database Management System initialized');
  }

  /**
   * Tente de se connecter à PostgreSQL, fallback sur SQLite si non disponible
   */
  public async initialize(): Promise<void> {
    this.log('🚀 Initializing database connection...');

    try {
      // Tenter PostgreSQL
      await this.connectToPostgreSQL();
      this.log('✅ Connected to PostgreSQL database');
      this.isPostgreSQL = true;
    } catch (error) {
      this.log(`⚠️ PostgreSQL not available: ${error.message}`);
      this.log('🔄 Falling back to SQLite...');

      // Fallback sur SQLite
      await this.connectToSQLite();
      this.isPostgreSQL = false;
      this.log('✅ Connected to SQLite database (fallback mode)');
    }

    // Créer les tables et index nécessaires
    await this.setupDatabase();
    this.emit('database_connected', { type: this.isPostgreSQL ? 'postgresql' : 'sqlite' });
  }

  /**
   * Connexion à PostgreSQL
   */
  private async connectToPostgreSQL(): Promise<void> {
    const poolConfig: PoolConfig = {
      ...this.config,
      ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
    };

    this.pool = new Pool(poolConfig);

    // Test de connexion
    const client = await this.pool.connect();
    const result = await client.query('SELECT version()');
    client.release();

    this.log(`📊 PostgreSQL version: ${result.rows[0].version}`);

    // Configuration des listeners du pool
    this.setupPoolListeners();
  }

  /**
   * Connexion à SQLite (fallback)
   */
  private async connectToSQLite(): Promise<void> {
    // Importer sqlite3 dynamiquement
    const sqlite3 = require('sqlite3').verbose();
    const dbPath = path.join(__dirname, '../src/market_database/market_data.db');

    // Créer une interface compatible pour SQLite
    this.createSQLiteInterface(dbPath);
  }

  /**
   * Configure les listeners du pool PostgreSQL
   */
  private setupPoolListeners(): void {
    if (!this.pool) return;

    this.pool.on('connect', (client) => {
      this.log('🔗 New database connection established');
    });

    this.pool.on('acquire', (client) => {
      this.log('📤 Connection acquired from pool');
    });

    this.pool.on('remove', (client) => {
      this.log('🗑️ Connection removed from pool');
    });

    this.pool.on('error', (err, client) => {
      this.log(`❌ Database error: ${err.message}`);
      this.emit('database_error', { error: err, client });
    });
  }

  /**
   * Crée une interface compatible pour SQLite
   */
  private createSQLiteInterface(dbPath: string): void {
    const sqlite3 = require('sqlite3');
    const db = new sqlite3.Database(dbPath);

    // Créer une interface pool-like pour SQLite
    this.pool = {
      query: (text: string, params?: any[]): Promise<QueryResult> => {
        return new Promise((resolve, reject) => {
          const stmt = db.prepare(text);
          stmt.run(params || [], function(err) {
            if (err) {
              reject(err);
            } else {
              resolve({
                rows: [],
                rowCount: this.changes,
                command: text.split(' ')[0].toLowerCase()
              } as QueryResult);
            }
          });
        });
      },
      connect: () => Promise.resolve({ query: this.pool!.query, release: () => {} }),
      end: () => new Promise(resolve => db.close(resolve)),
      totalCount: 1,
      idleCount: 0,
      waitingCount: 0
    } as any;
  }

  /**
   * Configure la base de données (tables, index, etc.)
   */
  private async setupDatabase(): Promise<void> {
    try {
      // Tables de trading
      await this.createTradingTables();

      // Tables de portefeuille
      await this.createWalletTables();

      // Tables d'agents
      await this.createAgentTables();

      // Tables de logs
      await this.createLogTables();

      // Index optimisés
      await this.createOptimizedIndexes();

      this.log('✅ Database setup completed');
    } catch (error) {
      this.log(`❌ Database setup failed: ${error.message}`);
      throw error;
    }
  }

  /**
   * Crée les tables de trading
   */
  private async createTradingTables(): Promise<void> {
    const queries = [
      // Table des trades
      `CREATE TABLE IF NOT EXISTS trades (
        id SERIAL PRIMARY KEY,
        symbol VARCHAR(20) NOT NULL,
        side VARCHAR(10) NOT NULL,
        size DECIMAL(20,8) NOT NULL,
        price DECIMAL(20,8) NOT NULL,
        fee DECIMAL(20,8) DEFAULT 0,
        timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        agent_id VARCHAR(50),
        strategy_id VARCHAR(50),
        pnl DECIMAL(20,8) DEFAULT 0,
        status VARCHAR(20) DEFAULT 'filled',
        exchange VARCHAR(20) DEFAULT 'hyperliquid',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
      ) ${this.isPostgreSQL ? 'PARTITION BY RANGE (timestamp)' : ''}`,

      // Table des positions
      `CREATE TABLE IF NOT EXISTS positions (
        id SERIAL PRIMARY KEY,
        symbol VARCHAR(20) NOT NULL,
        side VARCHAR(10) NOT NULL,
        size DECIMAL(20,8) NOT NULL,
        entry_price DECIMAL(20,8) NOT NULL,
        mark_price DECIMAL(20,8) DEFAULT 0,
        unrealized_pnl DECIMAL(20,8) DEFAULT 0,
        leverage INTEGER DEFAULT 1,
        margin_used DECIMAL(20,8) DEFAULT 0,
        timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        agent_id VARCHAR(50),
        status VARCHAR(20) DEFAULT 'open',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
      )`,

      // Table des OHLCV
      `CREATE TABLE IF NOT EXISTS ohlcv_data (
        id SERIAL PRIMARY KEY,
        symbol VARCHAR(20) NOT NULL,
        timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
        timeframe VARCHAR(10) NOT NULL,
        open DECIMAL(20,8) NOT NULL,
        high DECIMAL(20,8) NOT NULL,
        low DECIMAL(20,8) NOT NULL,
        close DECIMAL(20,8) NOT NULL,
        volume DECIMAL(20,8) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        UNIQUE(symbol, timestamp, timeframe)
      ) ${this.isPostgreSQL ? 'PARTITION BY RANGE (timestamp)' : ''}`,

      // Table des signaux d'agents
      `CREATE TABLE IF NOT EXISTS agent_signals (
        id SERIAL PRIMARY KEY,
        agent_name VARCHAR(50) NOT NULL,
        symbol VARCHAR(20) NOT NULL,
        signal_type VARCHAR(20) NOT NULL,
        confidence DECIMAL(5,4) NOT NULL,
        price DECIMAL(20,8),
        timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        metadata JSONB,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
      )`
    ];

    for (const query of queries) {
      await this.query(query);
    }

    this.log('📊 Trading tables created');
  }

  /**
   * Crée les tables de portefeuille
   */
  private async createWalletTables(): Promise<void> {
    const queries = [
      // Table des portefeuilles
      `CREATE TABLE IF NOT EXISTS wallets (
        id SERIAL PRIMARY KEY,
        address VARCHAR(100) UNIQUE NOT NULL,
        type VARCHAR(20) DEFAULT 'paper_trading',
        network VARCHAR(20) DEFAULT 'simulation',
        balance DECIMAL(20,8) DEFAULT 0,
        usd_balance DECIMAL(20,8) DEFAULT 0,
        collateral DECIMAL(20,8) DEFAULT 0,
        equity DECIMAL(20,8) DEFAULT 0,
        margin_usage DECIMAL(5,4) DEFAULT 0,
        leverage INTEGER DEFAULT 1,
        status VARCHAR(20) DEFAULT 'active',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
      )`,

      // Table des soldes de portefeuille
      `CREATE TABLE IF NOT EXISTS wallet_balances (
        id SERIAL PRIMARY KEY,
        wallet_id INTEGER REFERENCES wallets(id),
        token VARCHAR(20) NOT NULL,
        balance DECIMAL(20,8) DEFAULT 0,
        usd_value DECIMAL(20,8) DEFAULT 0,
        timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
      )`,

      // Table des transactions
      `CREATE TABLE IF NOT EXISTS transactions (
        id SERIAL PRIMARY KEY,
        wallet_id INTEGER REFERENCES wallets(id),
        type VARCHAR(20) NOT NULL,
        amount DECIMAL(20,8) NOT NULL,
        token VARCHAR(20) NOT NULL,
        usd_value DECIMAL(20,8) DEFAULT 0,
        fee DECIMAL(20,8) DEFAULT 0,
        status VARCHAR(20) DEFAULT 'pending',
        hash VARCHAR(100),
        timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
      )`
    ];

    for (const query of queries) {
      await this.query(query);
    }

    this.log('💰 Wallet tables created');
  }

  /**
   * Crée les tables d'agents
   */
  private async createAgentTables(): Promise<void> {
    const queries = [
      // Table des agents
      `CREATE TABLE IF NOT EXISTS agents (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50) UNIQUE NOT NULL,
        type VARCHAR(30) NOT NULL,
        status VARCHAR(20) DEFAULT 'offline',
        pid INTEGER,
        config JSONB,
        last_heartbeat TIMESTAMP WITH TIME ZONE,
        uptime BIGINT DEFAULT 0,
        memory_usage BIGINT DEFAULT 0,
        cpu_usage DECIMAL(5,2) DEFAULT 0,
        trades_executed INTEGER DEFAULT 0,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
      )`,

      // Table des métriques d'agents
      `CREATE TABLE IF NOT EXISTS agent_metrics (
        id SERIAL PRIMARY KEY,
        agent_id INTEGER REFERENCES agents(id),
        metric_name VARCHAR(50) NOT NULL,
        metric_value DECIMAL(20,8) NOT NULL,
        timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
      )`
    ];

    for (const query of queries) {
      await this.query(query);
    }

    this.log('🤖 Agent tables created');
  }

  /**
   * Crée les tables de logs
   */
  private async createLogTables(): Promise<void> {
    const queries = [
      // Table des logs structurés
      `CREATE TABLE IF NOT EXISTS logs (
        id SERIAL PRIMARY KEY,
        level VARCHAR(20) NOT NULL,
        message TEXT NOT NULL,
        module VARCHAR(50),
        agent_id INTEGER REFERENCES agents(id),
        metadata JSONB,
        timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
      ) ${this.isPostgreSQL ? 'PARTITION BY RANGE (timestamp)' : ''}`,

      // Table des erreurs
      `CREATE TABLE IF NOT EXISTS errors (
        id SERIAL PRIMARY KEY,
        error_type VARCHAR(50) NOT NULL,
        message TEXT NOT NULL,
        stack_trace TEXT,
        agent_id INTEGER REFERENCES agents(id),
        count INTEGER DEFAULT 1,
        first_occurred TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        last_occurred TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        resolved BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
      )`
    ];

    for (const query of queries) {
      await this.query(query);
    }

    this.log('📝 Log tables created');
  }

  /**
   * Crée les index optimisés
   */
  private async createOptimizedIndexes(): Promise<void> {
    const queries = [
      // Index pour trades
      'CREATE INDEX IF NOT EXISTS idx_trades_symbol_timestamp ON trades(symbol, timestamp DESC)',
      'CREATE INDEX IF NOT EXISTS idx_trades_agent_timestamp ON trades(agent_id, timestamp DESC)',
      'CREATE INDEX IF NOT EXISTS idx_trades_status ON trades(status)',
      'CREATE INDEX IF NOT EXISTS idx_trades_exchange ON trades(exchange)',

      // Index pour positions
      'CREATE INDEX IF NOT EXISTS idx_positions_symbol ON positions(symbol)',
      'CREATE INDEX IF NOT EXISTS idx_positions_agent ON positions(agent_id)',
      'CREATE INDEX IF NOT EXISTS idx_positions_status ON positions(status)',
      'CREATE INDEX IF NOT EXISTS idx_positions_updated ON positions(updated_at DESC)',

      // Index pour OHLCV
      'CREATE INDEX IF NOT EXISTS idx_ohlcv_symbol_timestamp ON ohlcv_data(symbol, timestamp DESC)',
      'CREATE INDEX IF NOT EXISTS idx_ohlcv_timeframe ON ohlcv_data(timeframe)',

      // Index pour signaux d'agents
      'CREATE INDEX IF NOT EXISTS idx_agent_signals_agent_timestamp ON agent_signals(agent_name, timestamp DESC)',
      'CREATE INDEX IF NOT EXISTS idx_agent_signals_symbol ON agent_signals(symbol)',
      'CREATE INDEX IF NOT EXISTS idx_agent_signals_type ON agent_signals(signal_type)',

      // Index pour wallets
      'CREATE INDEX IF NOT EXISTS idx_wallets_address ON wallets(address)',
      'CREATE INDEX IF NOT EXISTS idx_wallets_type ON wallets(type)',
      'CREATE INDEX IF NOT EXISTS idx_wallets_status ON wallets(status)',

      // Index pour logs
      'CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp DESC)',
      'CREATE INDEX IF NOT EXISTS idx_logs_level ON logs(level)',
      'CREATE INDEX IF NOT EXISTS idx_logs_module ON logs(module)',

      // Index pour erreurs
      'CREATE INDEX IF NOT EXISTS idx_errors_type ON errors(error_type)',
      'CREATE INDEX IF NOT EXISTS idx_errors_resolved ON errors(resolved)',
      'CREATE INDEX IF NOT EXISTS idx_errors_last_occurred ON errors(last_occurred DESC)'
    ];

    for (const query of queries) {
      await this.query(query);
    }

    this.log('🔍 Optimized indexes created');
  }

  /**
   * Exécute une requête SQL
   */
  public async query(text: string, params?: any[]): Promise<QueryResult> {
    if (!this.pool) {
      throw new Error('Database not initialized');
    }

    const startTime = Date.now();
    try {
      const result = await this.pool.query(text, params);
      const duration = Date.now() - startTime;

      // Log des requêtes lentes (>100ms)
      if (duration > 100) {
        this.log(`⚠️ Slow query (${duration}ms): ${text.substring(0, 100)}...`);
      }

      return result;
    } catch (error) {
      const duration = Date.now() - startTime;
      this.log(`❌ Query failed (${duration}ms): ${error.message} - ${text.substring(0, 100)}...`);
      throw error;
    }
  }

  /**
   * Exécute une transaction
   */
  public async transaction<T>(callback: (client: any) => Promise<T>): Promise<T> {
    const client = await this.pool!.connect();
    try {
      await client.query('BEGIN');
      const result = await callback(client);
      await client.query('COMMIT');
      return result;
    } catch (error) {
      await client.query('ROLLBACK');
      throw error;
    } finally {
      client.release();
    }
  }

  /**
   * Récupère les statistiques du pool de connexions
   */
  public getPoolStats(): any {
    if (!this.pool || this.isPostgreSQL === false) {
      return { type: 'sqlite', connections: 1 };
    }

    return {
      type: 'postgresql',
      totalCount: (this.pool as any).totalCount,
      idleCount: (this.pool as any).idleCount,
      waitingCount: (this.pool as any).waitingCount
    };
  }

  /**
   * Teste la connexion à la base de données
   */
  public async testConnection(): Promise<boolean> {
    try {
      const result = await this.query('SELECT 1 as test');
      return result.rows[0].test === 1;
    } catch (error) {
      this.log(`❌ Connection test failed: ${error.message}`);
      return false;
    }
  }

  /**
   * Ferme toutes les connexions
   */
  public async close(): Promise<void> {
    if (this.pool) {
      await this.pool.end();
      this.pool = null;
      this.log('🔌 Database connections closed');
    }
  }

  /**
   * Optimise la base de données
   */
  public async optimize(): Promise<void> {
    if (!this.isPostgreSQL) {
      this.log('⚠️ Optimization not available for SQLite');
      return;
    }

    const queries = [
      'VACUUM ANALYZE trades',
      'VACUUM ANALYZE positions',
      'VACUUM ANALYZE ohlcv_data',
      'ANALYZE',
      'REINDEX DATABASE novaquote_prod'
    ];

    for (const query of queries) {
      try {
        await this.query(query);
        this.log(`✅ Executed: ${query}`);
      } catch (error) {
        this.log(`❌ Optimization failed: ${query} - ${error.message}`);
      }
    }
  }

  /**
   * Nettoie les anciennes données
   */
  public async cleanup(daysToKeep: number = 30): Promise<void> {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - daysToKeep);

    const queries = [
      'DELETE FROM logs WHERE timestamp < $1',
      'DELETE FROM agent_signals WHERE timestamp < $1'
    ];

    for (const query of queries) {
      try {
        const result = await this.query(query, [cutoffDate]);
        this.log(`🗑️ Cleaned up ${result.rowCount} records`);
      } catch (error) {
        this.log(`❌ Cleanup failed: ${query} - ${error.message}`);
      }
    }
  }

  /**
   * Logging
   */
  private log(message: string): void {
    const timestamp = new Date().toISOString();
    const logEntry = `[${timestamp}] ${message}\n`;

    fs.appendFileSync(this.logPath, logEntry);
    console.log(`[DATABASE] ${message}`);
  }
}

// Export singleton instance
export const databaseManager = new DatabaseManager();