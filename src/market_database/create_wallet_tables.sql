-- =====================================================
-- NOVAQUOTE WALLET SYSTEM - DATABASE SCHEMA
-- =====================================================
-- Complete database schema for MetaMask wallet integration
-- Replaces paper wallet simulation with real database storage

-- ============================================
-- 1. WALLETS TABLE - MetaMask Wallet Management
-- ============================================
CREATE TABLE IF NOT EXISTS wallets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- MetaMask Integration
    metamask_address TEXT NOT NULL UNIQUE,
    metamask_address_hash TEXT NOT NULL,  -- Hashed address (will be computed in application)
    wallet_type TEXT NOT NULL DEFAULT 'metamask',

    -- Wallet Information
    wallet_name TEXT NOT NULL,
    description TEXT,

    -- Status and Permissions
    is_active BOOLEAN DEFAULT 1,
    is_verified BOOLEAN DEFAULT 0,
    verification_level TEXT DEFAULT 'pending',  -- pending, verified, restricted

    -- Trading Configuration
    allowed_exchanges TEXT DEFAULT '[]',  -- JSON array
    max_position_size REAL DEFAULT 10000.0,
    risk_level TEXT DEFAULT 'medium',  -- low, medium, high

    -- Metadata
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login_at DATETIME,

    -- Constraints
    CHECK (metamask_address IS NOT NULL AND metamask_address != ''),
    CHECK (LENGTH(metamask_address) = 42),  -- ETH address length
    CHECK (wallet_type IN ('metamask', 'phantom', 'walletconnect')),
    CHECK (verification_level IN ('pending', 'verified', 'restricted', 'suspended')),
    CHECK (risk_level IN ('low', 'medium', 'high'))
);

-- ============================================
-- 2. WALLET_BALANCES TABLE - Balance History
-- ============================================
CREATE TABLE IF NOT EXISTS wallet_balances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wallet_id INTEGER NOT NULL,

    -- Balance Information
    currency TEXT NOT NULL DEFAULT 'USD',
    available_balance REAL NOT NULL DEFAULT 0.0,
    total_balance REAL NOT NULL DEFAULT 0.0,
    frozen_balance REAL NOT NULL DEFAULT 0.0,

    -- P&L Tracking
    unrealized_pnl REAL NOT NULL DEFAULT 0.0,
    realized_pnl REAL NOT NULL DEFAULT 0.0,
    total_pnl REAL NOT NULL DEFAULT 0.0,

    -- Performance Metrics
    daily_pnl REAL NOT NULL DEFAULT 0.0,
    daily_return REAL NOT NULL DEFAULT 0.0,
    total_return REAL NOT NULL DEFAULT 0.0,

    -- Timestamps
    balance_timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Key
    FOREIGN KEY (wallet_id) REFERENCES wallets (id) ON DELETE CASCADE,

    -- Constraints
    CHECK (available_balance >= 0.0),
    CHECK (total_balance >= 0.0),
    CHECK (frozen_balance >= 0.0),
    CHECK (currency IS NOT NULL)
);

-- ============================================
-- 3. TRADES TABLE - Transaction Records
-- ============================================
CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wallet_id INTEGER NOT NULL,

    -- Trade Identification
    trade_id TEXT NOT NULL,  -- External exchange trade ID
    order_id TEXT NOT NULL,  -- Exchange order ID

    -- Trade Details
    symbol TEXT NOT NULL,
    exchange TEXT NOT NULL,
    side TEXT NOT NULL,  -- 'buy' or 'sell'
    order_type TEXT NOT NULL,  -- 'market', 'limit', 'stop', 'stop_limit'

    -- Quantities and Prices
    quantity REAL NOT NULL,
    price REAL NOT NULL,
    executed_quantity REAL NOT NULL,
    executed_price REAL NOT NULL,
    quote_quantity REAL NOT NULL,  -- quantity * price

    -- Fees
    fee_amount REAL NOT NULL DEFAULT 0.0,
    fee_currency TEXT NOT NULL DEFAULT 'USD',
    fee_rate REAL NOT NULL DEFAULT 0.0,

    -- Trade Status
    status TEXT NOT NULL DEFAULT 'pending',  -- pending, filled, partially_filled, cancelled, failed

    -- P&L Information
    realized_pnl REAL NOT NULL DEFAULT 0.0,
    commission REAL NOT NULL DEFAULT 0.0,

    -- Timestamps
    order_timestamp DATETIME NOT NULL,
    executed_timestamp DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Key
    FOREIGN KEY (wallet_id) REFERENCES wallets (id) ON DELETE CASCADE,

    -- Constraints
    CHECK (quantity > 0.0),
    CHECK (price > 0.0),
    CHECK (executed_quantity >= 0.0),
    CHECK (executed_price > 0.0),
    CHECK (quote_quantity >= 0.0),
    CHECK (fee_amount >= 0.0),
    CHECK (fee_rate >= 0.0),
    CHECK (side IN ('buy', 'sell')),
    CHECK (order_type IN ('market', 'limit', 'stop', 'stop_limit', 'take_profit')),
    CHECK (status IN ('pending', 'filled', 'partially_filled', 'cancelled', 'failed', 'rejected')),
    UNIQUE(wallet_id, trade_id)
);

-- ============================================
-- 4. POSITIONS TABLE - Active Positions
-- ============================================
CREATE TABLE IF NOT EXISTS positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wallet_id INTEGER NOT NULL,

    -- Position Identification
    symbol TEXT NOT NULL,
    exchange TEXT NOT NULL,

    -- Position Details
    side TEXT NOT NULL,  -- 'long' or 'short'
    position_size REAL NOT NULL,  -- Total position size
    entry_price REAL NOT NULL,  -- Average entry price
    current_price REAL NOT NULL,

    -- P&L Information
    unrealized_pnl REAL NOT NULL DEFAULT 0.0,
    realized_pnl REAL NOT NULL DEFAULT 0.0,
    total_pnl REAL NOT NULL DEFAULT 0.0,
    pnl_percentage REAL NOT NULL DEFAULT 0.0,

    -- Position Metrics
    margin_used REAL NOT NULL DEFAULT 0.0,
    margin_requirement REAL NOT NULL DEFAULT 0.0,
    leverage REAL NOT NULL DEFAULT 1.0,

    -- Risk Management
    stop_loss REAL,
    take_profit REAL,
    max_loss REAL NOT NULL DEFAULT 0.0,

    -- Position Status
    status TEXT NOT NULL DEFAULT 'open',  -- open, closed, liquidated

    -- Timestamps
    opened_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    closed_at DATETIME,
    last_updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Key
    FOREIGN KEY (wallet_id) REFERENCES wallets (id) ON DELETE CASCADE,

    -- Constraints
    CHECK (position_size > 0.0),
    CHECK (entry_price > 0.0),
    CHECK (current_price > 0.0),
    CHECK (leverage > 0.0),
    CHECK (margin_used >= 0.0),
    CHECK (margin_requirement >= 0.0),
    CHECK (max_loss >= 0.0),
    CHECK (side IN ('long', 'short')),
    CHECK (status IN ('open', 'closed', 'liquidated', 'reduced')),
    UNIQUE(wallet_id, symbol, exchange, status)
);

-- ============================================
-- 5. PERFORMANCE OPTIMIZATION - INDEXES
-- ============================================

-- Wallet indexes
CREATE INDEX IF NOT EXISTS idx_wallets_metamask_address ON wallets(metamask_address);
CREATE INDEX IF NOT EXISTS idx_wallets_active ON wallets(is_active);
CREATE INDEX IF NOT EXISTS idx_wallets_verified ON wallets(verification_level);

-- Balance indexes
CREATE INDEX IF NOT EXISTS idx_wallet_balances_wallet_id ON wallet_balances(wallet_id);
CREATE INDEX IF NOT EXISTS idx_wallet_balances_timestamp ON wallet_balances(balance_timestamp);
CREATE INDEX IF NOT EXISTS idx_wallet_balances_currency ON wallet_balances(currency);

-- Trade indexes
CREATE INDEX IF NOT EXISTS idx_trades_wallet_id ON trades(wallet_id);
CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol);
CREATE INDEX IF NOT EXISTS idx_trades_exchange ON trades(exchange);
CREATE INDEX IF NOT EXISTS idx_trades_status ON trades(status);
CREATE INDEX IF NOT EXISTS idx_trades_executed_timestamp ON trades(executed_timestamp);
CREATE INDEX IF NOT EXISTS idx_trades_symbol_exchange ON trades(symbol, exchange);

-- Position indexes
CREATE INDEX IF NOT EXISTS idx_positions_wallet_id ON positions(wallet_id);
CREATE INDEX IF NOT EXISTS idx_positions_symbol ON positions(symbol);
CREATE INDEX IF NOT EXISTS idx_positions_exchange ON positions(exchange);
CREATE INDEX IF NOT EXISTS idx_positions_status ON positions(status);
CREATE INDEX IF NOT EXISTS idx_positions_symbol_exchange ON positions(symbol, exchange);
CREATE INDEX IF NOT EXISTS idx_positions_opened_at ON positions(opened_at);

-- ============================================
-- 6. TRIGGERS FOR AUTOMATIC UPDATES
-- ============================================

-- Update wallet updated_at timestamp
CREATE TRIGGER IF NOT EXISTS update_wallet_timestamp
    AFTER UPDATE ON wallets
    FOR EACH ROW
BEGIN
    UPDATE wallets SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Update position last_updated_at
CREATE TRIGGER IF NOT EXISTS update_position_timestamp
    AFTER UPDATE ON positions
    FOR EACH ROW
BEGIN
    UPDATE positions SET last_updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Update trade updated_at
CREATE TRIGGER IF NOT EXISTS update_trade_timestamp
    AFTER UPDATE ON trades
    FOR EACH ROW
BEGIN
    UPDATE trades SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- ============================================
-- 7. VIEWS FOR COMMON QUERIES
-- ============================================

-- Wallet summary view
CREATE VIEW IF NOT EXISTS wallet_summary AS
SELECT
    w.id,
    w.metamask_address,
    w.wallet_name,
    w.is_active,
    w.verification_level,
    wb.total_balance,
    wb.available_balance,
    wb.total_pnl,
    wb.daily_pnl,
    wb.daily_return,
    COUNT(DISTINCT t.id) as total_trades,
    COUNT(DISTINCT p.id) as active_positions,
    w.created_at,
    w.last_login_at
FROM wallets w
LEFT JOIN wallet_balances wb ON w.id = wb.wallet_id
    AND wb.balance_timestamp = (
        SELECT MAX(balance_timestamp)
        FROM wallet_balances wb2
        WHERE wb2.wallet_id = w.id
    )
LEFT JOIN trades t ON w.id = t.wallet_id
LEFT JOIN positions p ON w.id = p.wallet_id AND p.status = 'open'
GROUP BY w.id, w.metamask_address, w.wallet_name, w.is_active, w.verification_level,
         wb.total_balance, wb.available_balance, wb.total_pnl, wb.daily_pnl, wb.daily_return,
         w.created_at, w.last_login_at;

-- Active positions view
CREATE VIEW IF NOT EXISTS active_positions_summary AS
SELECT
    p.id,
    w.metamask_address,
    p.symbol,
    p.exchange,
    p.side,
    p.position_size,
    p.entry_price,
    p.current_price,
    p.unrealized_pnl,
    p.pnl_percentage,
    p.leverage,
    p.stop_loss,
    p.take_profit,
    p.opened_at,
    p.last_updated_at
FROM positions p
JOIN wallets w ON p.wallet_id = w.id
WHERE p.status = 'open' AND w.is_active = 1;

-- Recent trades view
CREATE VIEW IF NOT EXISTS recent_trades AS
SELECT
    t.id,
    w.metamask_address,
    t.symbol,
    t.exchange,
    t.side,
    t.quantity,
    t.executed_price,
    t.quote_quantity,
    t.status,
    t.realized_pnl,
    t.executed_timestamp
FROM trades t
JOIN wallets w ON t.wallet_id = w.id
ORDER BY t.executed_timestamp DESC
LIMIT 1000;

-- ============================================
-- 8. SAMPLE DATA (Optional - for testing)
-- ============================================

-- Sample wallet (MetaMask address format)
INSERT OR IGNORE INTO wallets (
    metamask_address,
    metamask_address_hash,
    wallet_name,
    description,
    is_verified,
    verification_level
) VALUES (
    '0x742d35Cc6634C0532925a3b8D4E7E0E0e9e0d3a1',
    'hash_742d35cc6634c0532925a3b8d4e7e0e0e9e0d3a1',
    'NOVAQUOTE Trading Wallet',
    'Primary trading wallet for NOVAQUOTE platform',
    1,
    'verified'
);

-- Sample balance
INSERT OR IGNORE INTO wallet_balances (
    wallet_id,
    available_balance,
    total_balance,
    unrealized_pnl,
    total_pnl,
    daily_return
) VALUES (
    1,  -- ID of the inserted wallet
    950.0,
    1000.0,
    25.50,
    50.75,
    0.0536
);

-- ============================================
-- 9. PERFORMANCE QUERIES
-- ============================================

-- Query for wallet performance metrics
-- SELECT * FROM wallet_summary WHERE metamask_address = '0x...';

-- Query for active positions
-- SELECT * FROM active_positions_summary WHERE metamask_address = '0x...';

-- Query for recent trades
-- SELECT * FROM recent_trades WHERE metamask_address = '0x...' LIMIT 50;

-- Query for balance history
-- SELECT * FROM wallet_balances WHERE wallet_id = ? ORDER BY balance_timestamp DESC LIMIT 30;

-- Query for P&L analysis
-- SELECT
--     DATE(executed_timestamp) as trade_date,
--     COUNT(*) as trade_count,
--     SUM(realized_pnl) as daily_pnl,
--     AVG(realized_pnl) as avg_trade_pnl
-- FROM trades
-- WHERE wallet_id = ? AND status = 'filled'
-- GROUP BY DATE(executed_timestamp)
-- ORDER BY trade_date DESC;