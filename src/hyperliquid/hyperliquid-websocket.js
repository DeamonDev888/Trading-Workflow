/**
 * HyperLiquid WebSocket Client - JavaScript Wrapper Résilient
 * WebSocket client with exponential backoff, heartbeat, and intelligent retry
 * Implements NOVAQUOTE patterns for production trading
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
    this.maxReconnectAttempts = 20; // Increased from 5
    this.baseReconnectDelay = 1000; // 1s base delay
    this.maxReconnectDelay = 30000; // Max 30s
    this.backoffMultiplier = 2; // Exponential backoff
    this.heartbeatInterval = 15000; // 15s heartbeat (critical fix for "Inactive" disconnects)
    this.heartbeatTimer = null;
    this.lastPingTime = null;
    this.connectionStartTime = null;
    this.totalReconnections = 0;
    this.lastConnectedTime = null;
    this.proactiveReconnectTimer = null;
    this.PROACTIVE_RECONNECT_INTERVAL = 300000; // 5 minutes (大幅減少不必要的重连)
  }

  connect() {
    try {
      this.connectionStartTime = new Date();
      this.websocket = new WebSocket(this.wsUrl);

      // Connection timeout
      const connectionTimeout = setTimeout(() => {
        if (this.websocket && this.websocket.readyState !== WebSocket.OPEN) {
          this.handleConnectionError(new Error('Connection timeout'));
        }
      }, 10000); // 10s timeout

      this.websocket.on('open', () => {
        clearTimeout(connectionTimeout);
        this.handleOpen();
      });

      this.websocket.on('message', (data) => {
        this.handleMessage(data);
      });

      this.websocket.on('close', (code, reason) => {
        clearTimeout(connectionTimeout);
        this.handleClose(code, reason);
      });

      this.websocket.on('error', (error) => {
        clearTimeout(connectionTimeout);
        this.handleError(error);
      });

      this.websocket.on('pong', () => {
        this.lastPingTime = new Date();
      });
    } catch (error) {
      this.handleConnectionError(error);
    }
  }

  handleOpen() {
    this.connected = true;
    this.reconnectAttempts = 0;
    this.lastConnectedTime = new Date();
    this.totalReconnections++;

    // Log with NOVAQUOTE pattern
    const timestamp = this.getTimestamp();
    console.info(`[${timestamp}] [SUCCESS] [SYSTEM] ✅ HyperLiquid WebSocket connected`);
    console.info(`[${timestamp}] [INFO] [WEBSOCKET] ℹ️  Connection #${this.totalReconnections} established`);

    // Subscribe to channels to maintain active connection (prevents "Inactive" disconnects)
    this.subscribeToChannels();

    // Start heartbeat (as backup)
    this.startHeartbeat();

    // Proactive reconnection disabled to prevent socket storms
    // Only use if connection stability issues occur
    // this.startProactiveReconnection();
  }

  handleMessage(data) {
    try {
      const message = JSON.parse(data.toString());

      // Heartbeat PONG response (for old format compatibility)
      if (message.type === 'pong' || data.toString() === 'pong') {
        this.lastPingTime = new Date();
        return;
      }

      // Heartbeat ACK response (for new JSON ping format)
      if (message.type === 'pong' || message.type === 'ack' || message.type === 'ping') {
        this.lastPingTime = new Date();
        return;
      }

      // Handle allMids subscription data (price updates)
      if (message.type === 'allMids' && message.data) {
        // Update lastPingTime to show activity
        this.lastPingTime = new Date();
        return; // Don't log every price update
      }

      // Log received message with NOVAQUOTE pattern (throttled to 0.1%)
      if (Math.random() < 0.001) { // Log only 0.1% to avoid spam
        const timestamp = this.getTimestamp();
        console.info(`[${timestamp}] [INFO] [WEBSOCKET] ℹ️  💰 WebSocket message: ${message.type || 'unknown'}`);
      }
    } catch (error) {
      // Non-JSON messages (like pings) are normal
    }
  }

  handleClose(code, reason) {
    this.connected = false;
    this.stopHeartbeat();
    this.stopProactiveReconnection();

    const timestamp = this.getTimestamp();
    console.info(`[${timestamp}] [INFO] [SYSTEM] ❌ HyperLiquid WebSocket disconnected`);
    console.info(`[${timestamp}] [INFO] [WEBSOCKET] ℹ️  Code: ${code} - Reason: ${reason || 'N/A'}`);

    // Auto-reconnect unless intentional close (but not for proactive reconnection)
    if (code !== 1000 || reason !== 'Proactive reconnection') {
      this.attemptReconnect();
    }
  }

  handleError(error) {
    const timestamp = this.getTimestamp();
    console.error(`[${timestamp}] [ERROR] [WEBSOCKET] ❌ HyperLiquid WebSocket error: ${error.message}`);
    this.connected = false;
    this.attemptReconnect();
  }

  handleConnectionError(error) {
    const timestamp = this.getTimestamp();
    console.error(`[${timestamp}] [ERROR] [WEBSOCKET] ❌ Connection failed: ${error.message}`);
    this.attemptReconnect();
  }

  attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      const timestamp = this.getTimestamp();
      console.error(`[${timestamp}] [ERROR] [SYSTEM] ❌ Max reconnection attempts reached (${this.maxReconnectAttempts})`);
      console.error(`[${timestamp}] [ERROR] [SYSTEM] ❌ Please check HyperLiquid API status`);
      return;
    }

    this.reconnectAttempts++;
    this.totalReconnections++;

    // Calculate exponential backoff with jitter
    const baseDelay = this.baseReconnectDelay;
    const exponentialDelay = Math.min(
      baseDelay * Math.pow(this.backoffMultiplier, this.reconnectAttempts - 1),
      this.maxReconnectDelay
    );
    const jitter = Math.random() * 1000; // Random 0-1s;
    const delay = Math.floor(exponentialDelay + jitter);

    const timestamp = this.getTimestamp();
    console.info(`[${timestamp}] [INFO] [SYSTEM] 🔄 Reconnection attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
    console.info(`[${timestamp}] [INFO] [SYSTEM] ⏱️  Retry in ${delay}ms (backoff: ${Math.floor(exponentialDelay)}ms + jitter: ${Math.floor(jitter)}ms)`);

    setTimeout(() => this.connect(), delay);
  }

  startHeartbeat() {
    this.stopHeartbeat();
    this.heartbeatTimeoutId = null;

    this.heartbeatTimer = setInterval(() => {
      if (this.connected && this.websocket) {
        this.lastPingTime = new Date();

        try {
          // Send JSON ping message in HyperLiquid format instead of low-level ping()
          const pingMessage = JSON.stringify({
            type: 'ping',
            timestamp: Date.now()
          });
          this.websocket.send(pingMessage);

          // Check for heartbeat timeout (20s to prevent "Inactive" disconnects)
          // Clear previous timeout to prevent accumulation
          if (this.heartbeatTimeoutId) {
            clearTimeout(this.heartbeatTimeoutId);
          }

          this.heartbeatTimeoutId = setTimeout(() => {
            if (this.connected && this.websocket &&
                this.lastPingTime && Date.now() - this.lastPingTime.getTime() > 20000) {
              const timestamp = this.getTimestamp();
              console.warn(`[${timestamp}] [WARNING] [WEBSOCKET] ⚠️  Heartbeat timeout - forcing reconnection`);
              this.websocket.terminate();
              this.handleClose(4000, 'Heartbeat timeout');
            }
          }, 20000);
        } catch (error) {
          const timestamp = this.getTimestamp();
          console.error(`[${timestamp}] [ERROR] [WEBSOCKET] ❌ Heartbeat failed: ${error.message}`);
        }
      }
    }, this.heartbeatInterval);
  }

  stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
    if (this.heartbeatTimeoutId) {
      clearTimeout(this.heartbeatTimeoutId);
      this.heartbeatTimeoutId = null;
    }
  }

  /**
   * Start proactive reconnection before HyperLiquid's 60s inactivity timeout
   * This ensures continuous service without interruptions
   */
  startProactiveReconnection() {
    this.stopProactiveReconnection();

    console.info(`[${this.getTimestamp()}] [INFO] [SYSTEM] 🔄 Starting proactive reconnection check (interval: ${this.PROACTIVE_RECONNECT_INTERVAL/1000}s)`);

    this.proactiveReconnectTimer = setInterval(() => {
      if (this.connected && this.websocket) {
        const timestamp = this.getTimestamp();
        const connectionAge = Date.now() - this.lastConnectedTime;

        // Only reconnect if connection is old (avoid disrupting stable connections)
        if (connectionAge > this.PROACTIVE_RECONNECT_INTERVAL * 0.8) {
          console.info(`[${timestamp}] [INFO] [SYSTEM] 🔄 Proactive reconnection (connection age: ${Math.round(connectionAge/1000)}s)`);

          this.websocket.close(1000, 'Proactive reconnection');
          this.handleClose(1000, 'Proactive reconnection');

          // Trigger reconnection after a brief delay
          setTimeout(() => {
            this.connect();
          }, 2000); // Increased delay to 2s for stability
        } else {
          console.info(`[${timestamp}] [INFO] [SYSTEM] ✅ Connection stable (age: ${Math.round(connectionAge/1000)}s) - no reconnection needed`);
        }
      }
    }, this.PROACTIVE_RECONNECT_INTERVAL);
  }

  stopProactiveReconnection() {
    if (this.proactiveReconnectTimer) {
      clearInterval(this.proactiveReconnectTimer);
      this.proactiveReconnectTimer = null;
    }
  }

  disconnect() {
    this.stopHeartbeat();
    this.stopProactiveReconnection();

    if (this.websocket) {
      this.websocket.close(1000, 'Client disconnect');
      this.connected = false;
    }

    const timestamp = this.getTimestamp();
    console.info(`[${timestamp}] [INFO] [SYSTEM] ℹ️  WebSocket disconnected by client`);
  }

  isConnected() {
    return this.connected && this.websocket?.readyState === WebSocket.OPEN;
  }

  send(message) {
    if (this.isConnected()) {
      try {
        this.websocket.send(JSON.stringify(message));
        return true;
      } catch (error) {
        const timestamp = this.getTimestamp();
        console.error(`[${timestamp}] [ERROR] [WEBSOCKET] ❌ Send failed: ${error.message}`);
        return false;
      }
    } else {
      const timestamp = this.getTimestamp();
      console.warn(`[${timestamp}] [WARNING] [WEBSOCKET] ⚠️  WebSocket not connected, cannot send message`);
      return false;
    }
  }

  getTimestamp() {
    const now = new Date();
    return now.toTimeString().split(' ')[0] + '.' + now.getMilliseconds().toString().padStart(2, '0');
  }

  /**
   * Subscribe to channels to maintain active connection
   * This prevents HyperLiquid from closing the connection due to inactivity
   */
  subscribeToChannels() {
    try {
      if (!this.isConnected()) {
        return;
      }

      // Subscribe to allMids channel (mid prices for all symbols)
      const subscriptionMessage = JSON.stringify({
        type: 'subscribe',
        channels: ['allMids']
      });

      this.websocket.send(subscriptionMessage);

      const timestamp = this.getTimestamp();
      console.info(`[${timestamp}] [INFO] [WEBSOCKET] ℹ️  📡 Subscribed to 'allMids' channel`);
    } catch (error) {
      const timestamp = this.getTimestamp();
      console.error(`[${timestamp}] [ERROR] [WEBSOCKET] ❌ Failed to subscribe to channels: ${error.message}`);
    }
  }

  // Get connection statistics
  getStats() {
    const uptime = this.connectionStartTime
      ? Date.now() - this.connectionStartTime.getTime()
      : 0;

    return {
      connected: this.connected,
      reconnectAttempts: this.reconnectAttempts,
      totalReconnections: this.totalReconnections,
      uptime: uptime,
      lastConnected: this.lastConnectedTime,
    };
  }
}

module.exports = HyperliquidWebSocket;
