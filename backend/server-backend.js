/**
 * 🚀 NOVAQUOTE Backend Server - JavaScript Version
 * Trading API and WebSocket server for HyperLiquid integration
 */

const express = require('express');
const cors = require('cors');
const { WebSocketServer } = require('ws');
const winston = require('winston');
const path = require('path');

// Configure Winston logger
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: { service: 'novaquote-backend' },
  transports: [
    new winston.transports.File({ filename: 'logs/backend-error.log', level: 'error' }),
    new winston.transports.File({ filename: 'logs/backend.log' }),
  ],
});

if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console({
    format: winston.format.simple(),
  }));
}

const app = express();
const PORT = 7000;

// Middleware
app.use(cors({
  origin: ['http://localhost:3000', 'http://localhost:8080', 'http://localhost:9001'],
  credentials: true
}));

app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// API Routes
app.get('/api/health', async (req, res) => {
  try {
    const health = {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      memory: process.memoryUsage(),
      version: '8.0.0'
    };
    res.json(health);
  } catch (error) {
    logger.error('Health check failed', { error: error.message });
    res.status(500).json({
      status: 'unhealthy',
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

app.get('/api/agents', (req, res) => {
  // Mock agent status for now
  const agents = [
    { id: 'risk_agent', name: 'Risk Agent', status: 'active' },
    { id: 'strategy_agent', name: 'Strategy Agent', status: 'active' },
    { id: 'funding_agent', name: 'Funding Agent', status: 'active' },
    { id: 'sentiment_agent', name: 'Sentiment Agent', status: 'inactive' }
  ];

  res.json({ agents });
});

app.get('/api/hyperliquid/price/:symbol', async (req, res) => {
  try {
    const { symbol } = req.params;

    // Mock price data for now
    const mockPrices = {
      'BTC': 95000 + Math.random() * 1000,
      'ETH': 3800 + Math.random() * 200,
      'SOL': 180 + Math.random() * 10,
      'BNB': 650 + Math.random() * 30
    };

    const price = mockPrices[symbol] || 100;

    res.json({
      success: true,
      data: {
        symbol,
        price,
        timestamp: Date.now()
      }
    });
  } catch (error) {
    logger.error('Price fetch failed', { error: error.message, symbol: req.params.symbol });
    res.status(500).json({ success: false, error: error.message });
  }
});

// Error handling middleware
app.use((error, req, res, next) => {
  logger.error('Unhandled error', {
    error: error.message,
    stack: error.stack,
    url: req.url,
    method: req.method
  });

  res.status(500).json({
    error: 'Internal server error',
    timestamp: new Date().toISOString()
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    error: 'Endpoint not found',
    timestamp: new Date().toISOString()
  });
});


setTimeout(() => {
  try {
    wss = new WebSocketServer({ port: 7001 });
    wsStarted = true;
    logger.info('🔌 WebSocket Server running on port 7001');

    wss.on('connection', (ws) => {
      logger.info('WebSocket client connected');

      ws.on('message', (message) => {
        try {
          const data = JSON.parse(message.toString());
          logger.debug('WebSocket message received', { data });

          // Echo back for now
          ws.send(JSON.stringify({
            type: 'echo',
            data,
            timestamp: new Date().toISOString()
          }));
        } catch (error) {
          logger.error('WebSocket message error', { error: error.message });
          ws.send(JSON.stringify({
            type: 'error',
            error: error.message,
            timestamp: new Date().toISOString()
          }));
        }
      });

      ws.on('close', () => {
        logger.info('WebSocket client disconnected');
      });

      // Send welcome message
      ws.send(JSON.stringify({
        type: 'welcome',
        message: 'Connected to NOVAQUOTE Backend',
        timestamp: new Date().toISOString()
      }));
    });

    wss.on('error', (error) => {
      logger.error('WebSocket server error:', error);
    });
  } catch (error) {
    logger.warn('⚠️ WebSocket port 7001 unavailable, continuing without WebSocket');
    wsStarted = false;
  }
}, 1000); // Démarrer après 1 seconde

// Start server
app.listen(PORT, () => {
  logger.info(`🚀 NOVAQUOTE Backend Server running on port ${PORT}`);
  logger.info(`🔌 WebSocket Server running on port 7001`);
  console.log(`🚀 NOVAQUOTE Backend Server v8.0.0`);
  console.log(`📡 Port: ${PORT}`);
  console.log(`🔌 WebSocket: 7001`);
  console.log(`🏥 Health: http://localhost:${PORT}/api/health`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM received, shutting down gracefully');
  if (wss) wss.close();
  process.exit(0);
});

process.on('SIGINT', () => {
  logger.info('SIGINT received, shutting down gracefully');
  if (wss) wss.close();
  process.exit(0);
});

module.exports = app;