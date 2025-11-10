/**
 * HyperLiquid WebSocket Client - JavaScript Wrapper
 * Simple WebSocket client for HyperLiquid real-time data
 */

const WebSocket = require('ws');

class HyperliquidWebSocket {
  constructor(useTestnet = false) {
    this.wsUrl = useTestnet
      ? 'wss://api.hyperliquid-testnet.xyz/ws'
      : 'wss://api.hyperliquid.xyz/ws';
    this.websocket = null;
    this.connected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 5000;
  }

  connect() {
    try {
      this.websocket = new WebSocket(this.wsUrl);

      this.websocket.on('open', () => {
        console.info('✅ HyperLiquid WebSocket connected');
        this.connected = true;
        this.reconnectAttempts = 0;
      });

      this.websocket.on('message', (data) => {
        try {
          const message = JSON.parse(data.toString());
          console.info('📡 WebSocket message received:', message.type || 'unknown');
        } catch (error) {
          console.warn('Failed to parse WebSocket message:', error);
        }
      });

      this.websocket.on('close', () => {
        console.info('❌ HyperLiquid WebSocket disconnected');
        this.connected = false;
        this.attemptReconnect();
      });

      this.websocket.on('error', (error) => {
        console.error('HyperLiquid WebSocket error:', error.message);
      });
    } catch (error) {
      console.error('Failed to connect HyperLiquid WebSocket:', error.message);
    }
  }

  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.info(`🔄 Reconnection attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
      setTimeout(() => this.connect(), this.reconnectDelay);
    } else {
      console.error('❌ Max reconnection attempts reached');
    }
  }

  disconnect() {
    if (this.websocket) {
      this.websocket.close();
      this.connected = false;
    }
  }

  isConnected() {
    return this.connected;
  }

  send(message) {
    if (this.connected && this.websocket) {
      this.websocket.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected, cannot send message');
    }
  }
}

module.exports = HyperliquidWebSocket;
