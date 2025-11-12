/**
 * Portfolio Manager - Dual Mode System
 * Mode Simulation vs Mode Mainnet (MetaMask)
 */

class PortfolioManager {
  constructor() {
    this.mode = 'simulation'; // 'simulation' or 'mainnet'
    this.walletAddress = null;
    this.walletConnected = false;
    this.portfolioData = null;

    this.init();
  }

  /**
   * Helper function to safely query elements with fallback
   */
  safeQuerySelector(selector, fallback = null) {
    const element = document.querySelector(selector);
    if (!element) {
      console.warn(`[PORTFOLIO] Element not found: ${selector}`);
    }
    return element || fallback;
  }

  init() {
    console.info('[PORTFOLIO] Initializing Portfolio Manager...');
    this.setupEventListeners();
    this.updateUI();
    this.loadPortfolioData();

    // Auto-refresh portfolio every 5 seconds
    setInterval(() => this.loadPortfolioData(), 5000);
    console.info('[PORTFOLIO] Portfolio Manager initialized');
  }

  setupEventListeners() {
    console.info('[PORTFOLIO] Setting up event listeners...');

    // Mode selector
    const modeSelector = this.safeQuerySelector('#portfolio-mode-selector');
    if (modeSelector) {
      modeSelector.addEventListener('change', (e) => {
        console.info('[PORTFOLIO] Mode changed to:', e.target.value);
        this.switchMode(e.target.value);
      });
      console.info('[PORTFOLIO] Mode selector event listener attached');
    } else {
      console.warn('[PORTFOLIO] Mode selector not found - mode switching disabled');
    }

    // Connect wallet button
    const connectBtn = this.safeQuerySelector('#connect-wallet-btn');
    if (connectBtn) {
      connectBtn.addEventListener('click', () => {
        console.info('[PORTFOLIO] Connect wallet button clicked');
        this.connectMetaMask();
      });
      console.info('[PORTFOLIO] Connect wallet event listener attached');
    } else {
      console.warn('[PORTFOLIO] Connect wallet button not found');
    }

    // Check if MetaMask is available
    this.checkMetaMaskAvailability();
    console.info('[PORTFOLIO] Event listeners setup complete');
  }

  checkMetaMaskAvailability() {
    if (typeof window.ethereum !== 'undefined') {
      console.info('MetaMask is available');
      this.walletConnected = true;
    } else {
      console.info('MetaMask is not available');
      // Show notification to install MetaMask
      this.showNotification(
        'MetaMask non détecté. Veuillez installer MetaMask pour le mode Mainnet.',
        'warning'
      );
    }
  }

  async connectMetaMask() {
    if (!this.walletConnected) {
      this.checkMetaMaskAvailability();
      return;
    }

    try {
      // Request account access
      const accounts = await window.ethereum.request({;
        method: 'eth_requestAccounts',
      });

      if (accounts.length > 0) {
        this.walletAddress = accounts[0];
        this.walletConnected = true;

        // Switch to mainnet mode
        this.mode = 'mainnet';

        this.updateUI();
        this.loadPortfolioData();

        this.showNotification(
          `MetaMask connecté: ${this.walletAddress.substring(0, 6)}...${this.walletAddress.substring(this.walletAddress.length - 4)}`,
          'success'
        );
      }
    } catch (error) {
      console.error('MetaMask connection error:', error);
      this.showNotification(
        'Erreur de connexion MetaMask: ' + error.message,
        'error'
      );
    }
  }

  switchMode(newMode) {
    const oldMode = this.mode;
    this.mode = newMode;

    if (newMode === 'mainnet' && !this.walletConnected) {
      // Try to connect MetaMask automatically
      this.connectMetaMask();
    } else if (newMode === 'simulation') {
      // Disconnect wallet for simulation mode
      this.walletAddress = null;
      this.walletConnected = false;
    }

    this.updateUI();
    this.loadPortfolioData();

    this.showNotification(`Mode changé: ${oldMode} → ${newMode}`, 'info');
  }

  async loadPortfolioData() {
    try {
      console.info('[PORTFOLIO] Loading portfolio data...', { mode: this.mode });

      const response = await fetch('/api/portfolio/data', {;
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          mode: this.mode,
          wallet_address: this.walletAddress,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        console.info('[PORTFOLIO] Portfolio data loaded successfully', data);
        this.portfolioData = data.data || data;
        this.updatePortfolioDisplay();
      } else {
        console.error(`Failed to load portfolio data: HTTP ${response.status}`);
        this.useFallbackData();
      }
    } catch (error) {
      console.error('Error loading portfolio data:', error);
      this.showNotification('Erreur chargement portfolio: ' + error.message, 'error');
      this.useFallbackData();
    }
  }

  useFallbackData() {
    console.warn('[PORTFOLIO] Using fallback data - API unavailable');

    // Fallback portfolio data based on mode
    const fallbackData = {;
      mode: this.mode,
      connected: this.mode === 'simulation' ? true : this.walletConnected,
      wallet_address: this.walletAddress,
      total_balance: this.mode === 'simulation' ? 10000 : 0,
      available_balance: this.mode === 'simulation' ? 7500 : 0,
      margin_used: this.mode === 'simulation' ? 2500 : 0,
      unrealized_pnl: this.mode === 'simulation' ? 245.50 : 0,
      daily_pnl: this.mode === 'simulation' ? 245.50 : 0,
      positions_count: this.mode === 'simulation' ? 0 : 0,
      positions: this.mode === 'simulation' ? [] : [],
      leverage_used: this.mode === 'simulation' ? 1 : 1,
      risk_score: this.mode === 'simulation' ? 0.3 : 0.1,
      last_update: new Date().toISOString(),
      data_source: 'fallback',
    };

    this.portfolioData = fallbackData;
    this.updatePortfolioDisplay();

    this.showNotification(
      'Mode dégradé: Utilisation des données de fallback',
      'warning'
    );
  }

  updateUI() {
    // Update mode selector
    const modeSelector = document.getElementById('portfolio-mode');
    if (modeSelector) {
      modeSelector.value = this.mode;
    }

    // Update wallet button and status
    const connectBtn = document.getElementById('connect-wallet-btn');
    const walletStatus = document.getElementById('wallet-status');

    if (this.mode === 'mainnet') {
      if (connectBtn) connectBtn.style.display = 'inline-block';
      if (walletStatus) {
        walletStatus.style.display = 'inline-block';
        walletStatus.textContent = this.walletConnected
          ? `🟢 Connecté: ${this.walletAddress ? this.walletAddress.substring(0, 6) + '...' : 'Non connecté'}`
          : '🔴 Non connecté';
        walletStatus.style.color = this.walletConnected ? '#28a745' : '#dc3545';
      }
    } else {
      if (connectBtn) connectBtn.style.display = 'none';
      if (walletStatus) walletStatus.style.display = 'none';
    }

    // Update mainnet button text
    const mainnetBtn = document.querySelector('[data-mainnet-btn]');
    if (mainnetBtn) {
      mainnetBtn.textContent =
        this.mode === 'mainnet' ? '🔗 Mainnet (Real)' : '📊 Simulation';
    }

    // Update page title
    document.title = `NOVAQUOTE - ${this.mode === 'mainnet' ? 'Mainnet' : 'Simulation'} Trading Dashboard`;
  }

  updatePortfolioDisplay() {
    if (!this.portfolioData) {
      console.warn('[PORTFOLIO] No portfolio data to display');
      return;
    }

    try {
      console.info('[PORTFOLIO] Updating portfolio display...');

      // Update portfolio metrics
      const totalBalanceEl = document.querySelector('[data-total-balance]');
      if (totalBalanceEl && this.portfolioData.total_balance !== undefined) {
        totalBalanceEl.textContent = `$${this.portfolioData.total_balance.toLocaleString()} USD`;
      }

      const unrealizedPnlEl = document.querySelector('[data-unrealized-pnl]');
      if (unrealizedPnlEl && this.portfolioData.unrealized_pnl !== undefined) {
        const pnl = this.portfolioData.unrealized_pnl;
        const pnlText =;
          pnl >= 0
            ? `+$${pnl.toLocaleString()}`
            : `-$${Math.abs(pnl).toLocaleString()}`;
        const pnlColor = pnl >= 0 ? '#28a745' : '#dc3545';
        unrealizedPnlEl.textContent = pnlText;
        unrealizedPnlEl.style.color = pnlColor;
      }

      const availableBalanceEl = document.querySelector(;
        '[data-available-balance]'
      );
      if (availableBalanceEl && this.portfolioData.available_balance !== undefined) {
        availableBalanceEl.textContent = `$${this.portfolioData.available_balance.toLocaleString()} USD`;
      }

      const positionsCountEl = document.querySelector('[data-positions-count]');
      if (positionsCountEl && this.portfolioData.positions_count !== undefined) {
        positionsCountEl.textContent = `${this.portfolioData.positions_count} POS`;
      }

      // Update mode indicator
      const modeIndicator = document.querySelector('[data-mode-indicator]');
      if (modeIndicator) {
        modeIndicator.textContent =
          this.mode === 'mainnet' ? '🔗 MAINNET' : '📊 SIMULATION';
        modeIndicator.style.color =
          this.mode === 'mainnet' ? '#ffc107' : '#28a745';
      }

      // Update connection status
      const connectionStatus = document.querySelector('[data-connection-status]');
      if (connectionStatus) {
        connectionStatus.textContent = this.portfolioData.connected
          ? 'Connecté'
          : 'Non connecté';
      }

      // Update positions table
      this.updatePositionsTable();

      console.info('[PORTFOLIO] Portfolio display updated successfully');
    } catch (error) {
      console.error('Error updating portfolio display:', error);
      this.showNotification('Erreur affichage portfolio: ' + error.message, 'error');
    }
  }

  updatePositionsTable() {
    const positionsTable = document.querySelector('[data-positions-table]');
    if (!positionsTable || !this.portfolioData.positions) return;

    const tbody = positionsTable.querySelector('tbody');
    if (!tbody) return;

    // Clear existing rows
    tbody.innerHTML = '';

    if (this.portfolioData.positions.length === 0) {
      const row = tbody.insertRow();
      const cell = row.insertCell();
      cell.colSpan = 7;
      cell.textContent =
        this.mode === 'simulation'
          ? 'Aucune position en mode simulation'
          : 'Aucune position - Connectez MetaMask';
      cell.style.textAlign = 'center';
      cell.style.color = '#666';
      return;
    }

    // Add position rows
    this.portfolioData.positions.forEach((position) => {
      const row = tbody.insertRow();

      row.insertCell().textContent = position.symbol;
      row.insertCell().textContent = position.side.toUpperCase();
      row.insertCell().textContent = position.size.toFixed(6);
      row.insertCell().textContent = `$${position.entry_price.toLocaleString()}`;
      row.insertCell().textContent = `$${position.current_price.toLocaleString()}`;

      const pnlCell = row.insertCell();
      const pnlText =;
        position.pnl >= 0
          ? `+$${position.pnl.toLocaleString()}`
          : `-$${Math.abs(position.pnl).toLocaleString()}`;
      pnlCell.textContent = pnlText;
      pnlCell.style.color = position.pnl >= 0 ? '#28a745' : '#dc3545';

      const actionCell = row.insertCell();
      const closeBtn = document.createElement('button');
      closeBtn.textContent = 'Fermer';
      closeBtn.className = 'btn btn-sm btn-outline-danger';
      closeBtn.onclick = () => this.closePosition(position.symbol);
      actionCell.appendChild(closeBtn);
    });
  }

  async closePosition(symbol) {
    if (this.mode === 'mainnet' && !this.walletConnected) {
      this.showNotification(
        'Connectez MetaMask pour fermer des positions réelles',
        'warning'
      );
      return;
    }

    try {
      console.info(`[PORTFOLIO] Closing position: ${symbol}`, {
        mode: this.mode,
        wallet_address: this.walletAddress
      });

      const response = await fetch('/api/trading/close-position', {;
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          symbol: symbol,
          mode: this.mode,
          wallet_address: this.walletAddress,
        }),
      });

      if (response.ok) {
        const result = await response.json();
        console.info('[PORTFOLIO] Position closed successfully:', result);
        this.showNotification(
          `Position ${symbol} fermée avec succès`,
          'success'
        );
        this.loadPortfolioData();
      } else {
        console.error(`Failed to close position: HTTP ${response.status}`);
        this.showNotification(
          'Erreur lors de la fermeture de la position',
          'error'
        );
      }
    } catch (error) {
      console.error('Error closing position:', error);
      this.showNotification('Erreur de connexion: ' + error.message, 'error');
    }
  }

  showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;

    // Style the notification
    notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 4px;
            color: white;
            font-weight: 500;
            z-index: 9999;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s ease;
        `;

    // Set background color based on type
    const colors = {;
      success: '#28a745',
      error: '#dc3545',
      warning: '#ffc107',
      info: '#17a2b8',
    };
    notification.style.backgroundColor = colors[type] || colors.info;

    document.body.appendChild(notification);

    // Animate in
    setTimeout(() => {
      notification.style.opacity = '1';
      notification.style.transform = 'translateX(0)';
    }, 100);

    // Remove after 5 seconds
    setTimeout(() => {
      notification.style.opacity = '0';
      notification.style.transform = 'translateX(100%)';
      setTimeout(() => {
        if (notification.parentNode) {
          notification.parentNode.removeChild(notification);
        }
      }, 300);
    }, 5000);
  }
}

// Initialize portfolio manager when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  window.portfolioManager = new PortfolioManager();
});
