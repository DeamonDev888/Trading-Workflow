/**
 * MARKET DATABASE SETUP - Real Trading Data
 * Creates tables for OHLCV data from real exchanges
 */

const sqlite3 = require('sqlite3').verbose();
const fs = require('fs');
const path = require('path');

class MarketDatabase {
  constructor() {
    this.dbPath = path.join(__dirname, 'market_data.db');
    this.db = null;
  }

  async initialize() {
    return new Promise((resolve, reject) => {
      // Create directory if it doesn't exist
      const dir = path.dirname(this.dbPath);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }

      this.db = new sqlite3.Database(this.dbPath, (err) => {
        if (err) {
          reject(err);
          return;
        }
        console.info('✅ Connected to SQLite market database');
        this.createTables().then(resolve).catch(reject);
      });
    });
  }

  async createTables() {
    const tables = [;
      // OHLCV data table
      `CREATE TABLE IF NOT EXISTS ohlcv_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                exchange TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume REAL NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, exchange, timeframe, timestamp)
            )`,

      // Market metadata
      `CREATE TABLE IF NOT EXISTS markets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL UNIQUE,
                exchange TEXT NOT NULL,
                name TEXT NOT NULL,
                base_currency TEXT,
                quote_currency TEXT,
                is_active BOOLEAN DEFAULT 1,
                min_order_size REAL,
                price_precision INTEGER,
                volume_precision INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )`,

      // Backtest results
      `CREATE TABLE IF NOT EXISTS backtest_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_name TEXT NOT NULL,
                symbol TEXT NOT NULL,
                exchange TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                start_date DATETIME NOT NULL,
                end_date DATETIME NOT NULL,
                total_return REAL NOT NULL,
                annual_return REAL NOT NULL,
                sharpe_ratio REAL NOT NULL,
                max_drawdown REAL NOT NULL,
                total_trades INTEGER NOT NULL,
                win_rate REAL NOT NULL,
                profit_factor REAL NOT NULL,
                final_balance REAL NOT NULL,
                initial_balance REAL DEFAULT 1000000,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )`,

      // BTC Dominance data
      `CREATE TABLE IF NOT EXISTS btc_dominance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL UNIQUE,
                dominance_percentage REAL NOT NULL,
                btc_price REAL NOT NULL,
                total_market_cap REAL NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )`,

      // Indexes for performance
      'CREATE INDEX IF NOT EXISTS idx_ohlcv_symbol_time ON ohlcv_data(symbol, timestamp)',
      'CREATE INDEX IF NOT EXISTS idx_ohlcv_exchange_symbol ON ohlcv_data(exchange, symbol)',
      'CREATE INDEX IF NOT EXISTS idx_backtest_strategy ON backtest_results(strategy_name, created_at)',
      'CREATE INDEX IF NOT EXISTS idx_btc_dominance_time ON btc_dominance(timestamp)',
    ];

    for (const sql of tables) {
      await this.runQuery(sql);
    }

    console.info('✅ Database tables created successfully');
  }

  async runQuery(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.db.run(sql, params, function (err) {
        if (err) {
          reject(err);
          return;
        }
        resolve(this);
      });
    });
  }

  async close() {
    return new Promise((resolve) => {
      this.db.close((err) => {
        if (err) {
          console.error('❌ Error closing database:', err.message);
        } else {
          console.info('✅ Database connection closed');
        }
        resolve();
      });
    });
  }

  // Sample data insertion for testing
  async insertSampleMarkets() {
    const markets = [;
      ['BTC/USDT', 'binance', 'Bitcoin', 'BTC', 'USDT', 0.00001, 2, 8],
      ['ETH/USDT', 'binance', 'Ethereum', 'ETH', 'USDT', 0.001, 2, 8],
      ['SOL/USDT', 'binance', 'Solana', 'SOL', 'USDT', 0.01, 2, 8],
      [
        'BTC/USDC',
        'hyperliquid',
        'Bitcoin Perpetual',
        'BTC',
        'USDC',
        0.00001,
        2,
        8,
      ],
      [
        'ETH/USDC',
        'hyperliquid',
        'Ethereum Perpetual',
        'ETH',
        'USDC',
        0.001,
        2,
        8,
      ],
    ];

    for (const market of markets) {
      await this.runQuery(
        `INSERT OR REPLACE INTO markets
                 (symbol, exchange, name, base_currency, quote_currency, min_order_size, price_precision, volume_precision)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
        market
      );
    }

    console.info('✅ Sample markets inserted');
  }
}

// Auto-run if this file is executed directly
if (require.main === module) {
  const db = new MarketDatabase();

  db.initialize()
    .then(() => db.insertSampleMarkets())
    .then(() => {
      console.info('🎉 Market database setup completed successfully!');
      console.info('📊 Database location:', db.dbPath);
      console.info('🔧 Ready to insert real market data from exchanges');
    })
    .catch((err) => {
      console.error('❌ Database setup failed:', err.message);
    })
    .finally(() => db.close());
}

module.exports = MarketDatabase;
