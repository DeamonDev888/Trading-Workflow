/**
 * 🌐 NOVAQUOTE Frontend Server - JavaScript Version
 * Static file server for the trading dashboard
 */

const express = require('express');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = 9001;

// Middleware
app.use(cors({
  origin: ['http://localhost:3000', 'http://localhost:8080', 'http://localhost:7000'],
  credentials: true
}));

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve static files from public directory
app.use(express.static(path.join(__dirname, 'public')));

// API routes for frontend data
app.get('/api/dashboard', (req, res) => {
  // Mock dashboard data
  const dashboardData = {
    portfolio: {
      total_value: 10000,
      daily_pnl: 125.50,
      total_pnl: 2450.75,
      positions: [
        { symbol: 'BTC', size: 0.1, pnl: 85.20, side: 'long' },
        { symbol: 'ETH', size: 2.5, pnl: 40.30, side: 'long' }
      ]
    },
    market_data: {
      btc_price: 95000 + Math.random() * 1000,
      eth_price: 3800 + Math.random() * 200,
      timestamp: new Date().toISOString()
    },
    agents_status: [
      { name: 'Risk Agent', status: 'active', last_update: new Date().toISOString() },
      { name: 'Strategy Agent', status: 'active', last_update: new Date().toISOString() },
      { name: 'Funding Agent', status: 'active', last_update: new Date().toISOString() }
    ]
  };

  res.json(dashboardData);
});

app.get('/api/backtests', (req, res) => {
  // Mock backtest data
  const backtestData = {
    strategies: [
      {
        name: 'BTC Momentum',
        symbol: 'BTC',
        period: '7d',
        total_return: 12.5,
        max_drawdown: 3.2,
        win_rate: 68.5,
        total_trades: 45
      },
      {
        name: 'ETH Mean Reversion',
        symbol: 'ETH',
        period: '7d',
        total_return: 8.3,
        max_drawdown: 2.1,
        win_rate: 72.1,
        total_trades: 38
      }
    ]
  };

  res.json(backtestData);
});

// Serve index.html for all non-API routes
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Error handling middleware
app.use((error, req, res, next) => {
  console.error('Frontend server error:', error);
  res.status(500).json({
    error: 'Internal server error',
    timestamp: new Date().toISOString()
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`🌐 NOVAQUOTE Frontend Server v8.0.0`);
  console.log(`📡 Port: ${PORT}`);
  console.log(`🏠 Dashboard: http://localhost:${PORT}/`);
  console.log(`📊 Backtests: http://localhost:${PORT}/backtest.html`);
  console.log(`⚙️  Config: http://localhost:${PORT}/config.html`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('Frontend server shutting down gracefully');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('Frontend server shutting down gracefully');
  process.exit(0);
});

module.exports = app;