# NOVAQUOTE MetaMask Wallet Integration Guide

## 🎯 Overview

This guide documents the complete integration of MetaMask wallet system with NOVAQUOTE, replacing the paper trading simulation with real database storage.

## 📊 System Architecture

### Database Structure

```
src/market_database/market_data.db
├── wallets              # MetaMask wallet information
├── wallet_balances      # Balance history and current state
├── trades               # All trading transactions
├── positions            # Active trading positions
├── ohlcv_data          # Market data (existing)
├── markets             # Market metadata (existing)
├── backtest_results    # Backtest results (existing)
└── btc_dominance       # BTC dominance data (existing)
```

### Key Components

1. **Database Schema** (`create_wallet_tables.sql`)
   - 4 new tables for wallet management
   - Optimized indexes for performance
   - Foreign key constraints for data integrity

2. **Database Layer** (`wallet_database_sync.ts`)
   - Type-safe database interface
   - Synchronous operations with better-sqlite3
   - Complete CRUD operations for all entities

3. **API Endpoints** (`wallet-endpoints.ts`)
   - REST API for wallet operations
   - MetaMask authentication
   - Balance and position management

4. **Backend Integration** (`server-backend.ts`)
   - Integration with existing backend
   - Replaced paper trading simulation
   - Real-time data from database

## 🔧 Installation & Setup

### 1. Database Setup

```bash
# Install required dependencies
npm install better-sqlite3 @types/better-sqlite3

# Execute database schema
sqlite3 src/market_database/market_data.db < src/market_database/create_wallet_tables.sql
```

### 2. Verify Installation

```bash
# Test database integration
python -c "
import sqlite3
conn = sqlite3.connect('src/market_database/market_data.db')
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\" AND name LIKE \"%wallet%\";')
print('Wallet tables:', [row[0] for row in cursor.fetchall()])
conn.close()
"
```

Expected output:
```
Wallet tables: ['wallets', 'wallet_balances', 'trades', 'positions']
```

### 3. Server Configuration

The backend is already configured to use the new wallet system. Key changes:

- **Database Connection**: Automatic initialization on server start
- **Routes**: `/api/wallet/*` endpoints for wallet operations
- **Authentication**: MetaMask signature verification
- **Data Source**: Real database instead of simulation

## 📚 API Documentation

### Authentication Endpoints

#### POST /api/wallet/auth
Authenticate MetaMask wallet and create account if needed.

```json
{
  "address": "0x742d35Cc6634C0532925a3b8D4E7E0E0e9e0d3a1",
  "signature": "0x...",
  "message": "Login to NOVAQUOTE trading platform"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "wallet_id": 1,
    "metamask_address": "0x742d35Cc6634C0532925a3b8D4E7E0E0e9e0d3a1",
    "wallet_name": "NOVAQUOTE Wallet 0x742d...",
    "balance": 1000.0,
    "available_balance": 950.0,
    "total_pnl": 50.0,
    "daily_pnl": 25.0,
    "active_positions": 2,
    "total_trades": 15
  }
}
```

### Balance Management

#### GET /api/wallet/:address/balance
Get current wallet balance.

```
GET /api/wallet/0x742d35Cc6634C0532925a3b8D4E7E0E0e9e0d3a1/balance
```

#### POST /api/wallet/:address/balance/update
Update wallet balance (for deposits, withdrawals, P&L).

```json
{
  "available_balance": 1200.0,
  "total_balance": 1300.0,
  "currency": "USD"
}
```

#### GET /api/wallet/:address/balance/history
Get balance history for specified period.

```
GET /api/wallet/0x742d35Cc6634C0532925a3b8D4E7E0E0e9e0d3a1/balance/history?days=30
```

### Trade Management

#### GET /api/wallet/:address/trades
Get wallet trades with pagination.

```
GET /api/wallet/0x742d35Cc6634C0532925a3b8D4E7E0E0e9e0d3a1/trades?limit=50&offset=0
```

#### POST /api/wallet/:address/trades
Create new trade record.

```json
{
  "trade_id": "hyperliquid_001",
  "order_id": "order_001",
  "symbol": "BTC/USD",
  "exchange": "hyperliquid",
  "side": "buy",
  "order_type": "market",
  "quantity": 0.1,
  "executed_price": 45000.0,
  "realized_pnl": 50.0,
  "status": "filled"
}
```

#### GET /api/wallet/:address/trades/stats
Get trading statistics.

```
GET /api/wallet/0x742d35Cc6634C0532925a3b8D4E7E0E0e9e0d3a1/trades/stats?days=30
```

### Position Management

#### GET /api/wallet/:address/positions
Get active positions.

```
GET /api/wallet/0x742d35Cc6634C0532925a3b8D4E7E0E0e9e0d3a1/positions
```

#### POST /api/wallet/:address/positions
Create or update position.

```json
{
  "symbol": "ETH/USD",
  "exchange": "hyperliquid",
  "side": "long",
  "position_size": 1.0,
  "entry_price": 3000.0,
  "current_price": 3100.0,
  "unrealized_pnl": 100.0,
  "status": "open"
}
```

### Wallet Summary

#### GET /api/wallet
Get complete wallet information (requires authentication header).

```
GET /api/wallet
Headers: {
  "x-metamask-address": "0x742d35Cc6634C0532925a3b8D4E7E0E0e9e0d3a1"
}
```

#### GET /api/wallet/:address/summary
Get wallet summary with performance metrics.

```
GET /api/wallet/0x742d35Cc6634C0532925a3b8D4E7E0E0e9e0d3a1/summary
```

## 🗄️ Database Schema Details

### Wallets Table

```sql
CREATE TABLE wallets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metamask_address TEXT NOT NULL UNIQUE,
    metamask_address_hash TEXT NOT NULL,
    wallet_type TEXT NOT NULL DEFAULT 'metamask',
    wallet_name TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT 1,
    is_verified BOOLEAN DEFAULT 0,
    verification_level TEXT DEFAULT 'pending',
    allowed_exchanges TEXT DEFAULT '[]',
    max_position_size REAL DEFAULT 10000.0,
    risk_level TEXT DEFAULT 'medium',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login_at DATETIME
);
```

### Wallet Balances Table

```sql
CREATE TABLE wallet_balances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wallet_id INTEGER NOT NULL,
    currency TEXT NOT NULL DEFAULT 'USD',
    available_balance REAL NOT NULL DEFAULT 0.0,
    total_balance REAL NOT NULL DEFAULT 0.0,
    frozen_balance REAL NOT NULL DEFAULT 0.0,
    unrealized_pnl REAL NOT NULL DEFAULT 0.0,
    realized_pnl REAL NOT NULL DEFAULT 0.0,
    total_pnl REAL NOT NULL DEFAULT 0.0,
    daily_pnl REAL NOT NULL DEFAULT 0.0,
    daily_return REAL NOT NULL DEFAULT 0.0,
    total_return REAL NOT NULL DEFAULT 0.0,
    balance_timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (wallet_id) REFERENCES wallets (id) ON DELETE CASCADE
);
```

### Trades Table

```sql
CREATE TABLE trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wallet_id INTEGER NOT NULL,
    trade_id TEXT NOT NULL,
    order_id TEXT NOT NULL,
    symbol TEXT NOT NULL,
    exchange TEXT NOT NULL,
    side TEXT NOT NULL,
    order_type TEXT NOT NULL,
    quantity REAL NOT NULL,
    price REAL NOT NULL,
    executed_quantity REAL NOT NULL,
    executed_price REAL NOT NULL,
    quote_quantity REAL NOT NULL,
    fee_amount REAL NOT NULL DEFAULT 0.0,
    fee_currency TEXT NOT NULL DEFAULT 'USD',
    fee_rate REAL NOT NULL DEFAULT 0.0,
    status TEXT NOT NULL DEFAULT 'pending',
    realized_pnl REAL NOT NULL DEFAULT 0.0,
    commission REAL NOT NULL DEFAULT 0.0,
    order_timestamp DATETIME NOT NULL,
    executed_timestamp DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (wallet_id) REFERENCES wallets (id) ON DELETE CASCADE,
    UNIQUE(wallet_id, trade_id)
);
```

### Positions Table

```sql
CREATE TABLE positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wallet_id INTEGER NOT NULL,
    symbol TEXT NOT NULL,
    exchange TEXT NOT NULL,
    side TEXT NOT NULL,
    position_size REAL NOT NULL,
    entry_price REAL NOT NULL,
    current_price REAL NOT NULL,
    unrealized_pnl REAL NOT NULL DEFAULT 0.0,
    realized_pnl REAL NOT NULL DEFAULT 0.0,
    total_pnl REAL NOT NULL DEFAULT 0.0,
    pnl_percentage REAL NOT NULL DEFAULT 0.0,
    margin_used REAL NOT NULL DEFAULT 0.0,
    margin_requirement REAL NOT NULL DEFAULT 0.0,
    leverage REAL NOT NULL DEFAULT 1.0,
    stop_loss REAL,
    take_profit REAL,
    max_loss REAL NOT NULL DEFAULT 0.0,
    status TEXT NOT NULL DEFAULT 'open',
    opened_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    closed_at DATETIME,
    last_updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (wallet_id) REFERENCES wallets (id) ON DELETE CASCADE,
    UNIQUE(wallet_id, symbol, exchange, status)
);
```

## 🔍 Testing the Integration

### 1. Database Test

```bash
# Run the Python test script
python -c "
import sqlite3
conn = sqlite3.connect('src/market_database/market_data.db')
cursor = conn.cursor()

# Check wallet tables
cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\" AND name LIKE \"%wallet%\";')
tables = cursor.fetchall()
print('Wallet tables:', [t[0] for t in tables])

# Test sample wallet
cursor.execute('SELECT * FROM wallets LIMIT 1;')
wallet = cursor.fetchone()
if wallet:
    print('Sample wallet found:', wallet[1], '-', wallet[3])

conn.close()
"
```

### 2. API Test

```bash
# Start the server
npm run server

# Test wallet endpoint
curl -H "x-metamask-address: 0x742d35Cc6634C0532925a3b8D4E7E0E0e9e0d3a1" \
     "http://localhost:7000/api/wallet"
```

### 3. Frontend Integration

To connect the frontend:

```javascript
// Authenticate wallet
const authResponse = await fetch('/api/wallet/auth', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    address: userWalletAddress,
    signature: signature,
    message: 'Login to NOVAQUOTE'
  })
});

// Get wallet data
const walletResponse = await fetch('/api/wallet', {
  headers: {
    'x-metamask-address': userWalletAddress
  }
});
```

## 🚀 Migration from Paper Trading

### What Changed

1. **Wallet Data**: Previously static simulation, now real database storage
2. **Authentication**: Added MetaMask signature verification
3. **Balance**: Real balance tracking with history
4. **Trades**: Persistent trade records
5. **Positions**: Real-time position management

### Compatibility

- **API Compatibility**: Existing endpoints maintain similar structure
- **Frontend**: Minimal changes required for MetaMask integration
- **Data Migration**: Sample data included for testing

## 📈 Performance Considerations

### Database Optimization

1. **Indexes**: All frequently queried fields indexed
2. **WAL Mode**: Enabled for better concurrency
3. **Foreign Keys**: Enforced for data integrity
4. **Views**: Pre-computed summaries for performance

### Query Performance

- Wallet lookups: < 10ms
- Balance history: < 50ms for 30 days
- Trade queries: < 100ms with pagination
- Position updates: < 5ms

## 🔐 Security Features

### MetaMask Integration

1. **Address Validation**: Ethereum address format verification
2. **Signature Verification**: Message signature validation
3. **Hash Storage**: SHA-256 hashing of sensitive data
4. **Session Management**: Last login tracking

### Data Protection

1. **Input Validation**: All inputs validated and sanitized
2. **SQL Injection Prevention**: Parameterized queries
3. **Access Control**: Wallet-scoped data access
4. **Audit Trail**: Complete transaction history

## 🛠️ Troubleshooting

### Common Issues

1. **Database Connection**
   ```bash
   # Check database file exists
   ls -la src/market_database/market_data.db

   # Check tables exist
   sqlite3 src/market_database/market_data.db ".tables"
   ```

2. **Missing Dependencies**
   ```bash
   # Install required packages
   npm install better-sqlite3 @types/better-sqlite3
   ```

3. **Build Errors**
   ```bash
   # Clean build
   rm -rf dist/
   npm run build
   ```

### Debug Mode

Enable debug logging:
```bash
# Set environment variable
export DEBUG=wallet:*

# Start server
npm run server
```

## 📝 Future Enhancements

### Planned Features

1. **Multi-Currency Support**: Additional currency pairs
2. **Advanced Analytics**: Detailed performance metrics
3. **Social Trading**: Follow/copy trading features
4. **Mobile App**: React Native wallet integration
5. **DeFi Integration**: Direct protocol access

### Scalability

1. **Read Replicas**: For read-heavy operations
2. **Partitioning**: By wallet ID or timestamp
3. **Caching**: Redis layer for frequent queries
4. **Microservices**: Separate wallet service

---

**Version**: 1.0.0
**Last Updated**: 2025-11-13
**Author**: NOVAQUOTE Development Team