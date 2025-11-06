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

    init() {
        this.setupEventListeners();
        this.updateUI();
        this.loadPortfolioData();

        // Auto-refresh portfolio every 5 seconds
        setInterval(() => this.loadPortfolioData(), 5000);
    }

    setupEventListeners() {
        // Mode selector
        const modeSelector = document.getElementById('portfolio-mode-selector');
        if (modeSelector) {
            modeSelector.addEventListener('change', (e) => {
                this.switchMode(e.target.value);
            });
        }

        // Connect wallet button
        const connectBtn = document.getElementById('connect-wallet-btn');
        if (connectBtn) {
            connectBtn.addEventListener('click', () => {
                this.connectMetaMask();
            });
        }

        // Check if MetaMask is available
        this.checkMetaMaskAvailability();
    }

    checkMetaMaskAvailability() {
        if (typeof window.ethereum !== 'undefined') {
            console.log('MetaMask is available');
            this.walletConnected = true;
        } else {
            console.log('MetaMask is not available');
            // Show notification to install MetaMask
            this.showNotification('MetaMask non détecté. Veuillez installer MetaMask pour le mode Mainnet.', 'warning');
        }
    }

    async connectMetaMask() {
        if (!this.walletConnected) {
            this.checkMetaMaskAvailability();
            return;
        }

        try {
            // Request account access
            const accounts = await window.ethereum.request({
                method: 'eth_requestAccounts'
            });

            if (accounts.length > 0) {
                this.walletAddress = accounts[0];
                this.walletConnected = true;

                // Switch to mainnet mode
                this.mode = 'mainnet';

                this.updateUI();
                this.loadPortfolioData();

                this.showNotification(`MetaMask connecté: ${this.walletAddress.substring(0, 6)}...${this.walletAddress.substring(this.walletAddress.length - 4)}`, 'success');
            }
        } catch (error) {
            console.error('MetaMask connection error:', error);
            this.showNotification('Erreur de connexion MetaMask: ' + error.message, 'error');
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
            const response = await fetch('/api/portfolio/data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    mode: this.mode,
                    wallet_address: this.walletAddress
                })
            });

            if (response.ok) {
                this.portfolioData = await response.json();
                this.updatePortfolioDisplay();
            } else {
                console.error('Failed to load portfolio data');
                this.useFallbackData();
            }
        } catch (error) {
            console.error('Error loading portfolio data:', error);
            this.useFallbackData();
        }
    }

    useFallbackData() {
        // Fallback portfolio data based on mode
        const fallbackData = {
            mode: this.mode,
            connected: this.mode === 'simulation' ? true : this.walletConnected,
            wallet_address: this.walletAddress,
            total_balance: this.mode === 'simulation' ? 25000 : 0,
            available_balance: this.mode === 'simulation' ? 17500 : 0,
            margin_used: this.mode === 'simulation' ? 7500 : 0,
            unrealized_pnl: this.mode === 'simulation' ? 1250 : 0,
            daily_pnl: this.mode === 'simulation' ? 125 : 0,
            positions_count: this.mode === 'simulation' ? 4 : 0,
            positions: this.mode === 'simulation' ? [
                {
                    symbol: 'BTC',
                    side: 'long',
                    size: 0.1,
                    entry_price: 102000,
                    current_price: 103500,
                    pnl: 150,
                    pnl_percentage: 1.47,
                    leverage: 2,
                    value: 10350
                }
            ] : [],
            leverage_used: this.mode === 'simulation' ? 2 : 1,
            risk_score: this.mode === 'simulation' ? 0.3 : 0.1,
            last_update: new Date().toISOString(),
            data_source: 'fallback'
        };

        this.portfolioData = fallbackData;
        this.updatePortfolioDisplay();
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
                walletStatus.textContent = this.walletConnected ?
                    `🟢 Connecté: ${this.walletAddress ? this.walletAddress.substring(0, 6) + '...' : 'Non connecté'}` :
                    '🔴 Non connecté';
                walletStatus.style.color = this.walletConnected ? '#28a745' : '#dc3545';
            }
        } else {
            if (connectBtn) connectBtn.style.display = 'none';
            if (walletStatus) walletStatus.style.display = 'none';
        }

        // Update mainnet button text
        const mainnetBtn = document.querySelector('[data-mainnet-btn]');
        if (mainnetBtn) {
            mainnetBtn.textContent = this.mode === 'mainnet' ?
                '🔗 Mainnet (Real)' : '📊 Simulation';
        }

        // Update page title
        document.title = `NOVAQUOTE - ${this.mode === 'mainnet' ? 'Mainnet' : 'Simulation'} Trading Dashboard`;
    }

    updatePortfolioDisplay() {
        if (!this.portfolioData) return;

        // Update portfolio metrics
        const totalBalanceEl = document.querySelector('[data-total-balance]');
        if (totalBalanceEl) {
            totalBalanceEl.textContent = `$${this.portfolioData.total_balance.toLocaleString()} USD`;
        }

        const unrealizedPnlEl = document.querySelector('[data-unrealized-pnl]');
        if (unrealizedPnlEl) {
            const pnl = this.portfolioData.unrealized_pnl;
            const pnlText = pnl >= 0 ? `+$${pnl.toLocaleString()}` : `-$${Math.abs(pnl).toLocaleString()}`;
            const pnlColor = pnl >= 0 ? '#28a745' : '#dc3545';
            unrealizedPnlEl.textContent = pnlText;
            unrealizedPnlEl.style.color = pnlColor;
        }

        const availableBalanceEl = document.querySelector('[data-available-balance]');
        if (availableBalanceEl) {
            availableBalanceEl.textContent = `$${this.portfolioData.available_balance.toLocaleString()} USD`;
        }

        const positionsCountEl = document.querySelector('[data-positions-count]');
        if (positionsCountEl) {
            positionsCountEl.textContent = `${this.portfolioData.positions_count} POS`;
        }

        // Update mode indicator
        const modeIndicator = document.querySelector('[data-mode-indicator]');
        if (modeIndicator) {
            modeIndicator.textContent = this.mode === 'mainnet' ? '🔗 MAINNET' : '📊 SIMULATION';
            modeIndicator.style.color = this.mode === 'mainnet' ? '#ffc107' : '#28a745';
        }

        // Update connection status
        const connectionStatus = document.querySelector('[data-connection-status]');
        if (connectionStatus) {
            connectionStatus.textContent = this.portfolioData.connected ? 'Connecté' : 'Non connecté';
        }

        // Update positions table
        this.updatePositionsTable();
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
            cell.textContent = this.mode === 'simulation' ?
                'Aucune position en mode simulation' :
                'Aucune position - Connectez MetaMask';
            cell.style.textAlign = 'center';
            cell.style.color = '#666';
            return;
        }

        // Add position rows
        this.portfolioData.positions.forEach(position => {
            const row = tbody.insertRow();

            row.insertCell().textContent = position.symbol;
            row.insertCell().textContent = position.side.toUpperCase();
            row.insertCell().textContent = position.size.toFixed(6);
            row.insertCell().textContent = `$${position.entry_price.toLocaleString()}`;
            row.insertCell().textContent = `$${position.current_price.toLocaleString()}`;

            const pnlCell = row.insertCell();
            const pnlText = position.pnl >= 0 ? `+$${position.pnl.toLocaleString()}` : `-$${Math.abs(position.pnl).toLocaleString()}`;
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
            this.showNotification('Connectez MetaMask pour fermer des positions réelles', 'warning');
            return;
        }

        try {
            const response = await fetch('/api/trading/close-position', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    symbol: symbol,
                    mode: this.mode,
                    wallet_address: this.walletAddress
                })
            });

            if (response.ok) {
                this.showNotification(`Position ${symbol} fermée avec succès`, 'success');
                this.loadPortfolioData();
            } else {
                this.showNotification('Erreur lors de la fermeture de la position', 'error');
            }
        } catch (error) {
            console.error('Error closing position:', error);
            this.showNotification('Erreur de connexion', 'error');
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
        const colors = {
            success: '#28a745',
            error: '#dc3545',
            warning: '#ffc107',
            info: '#17a2b8'
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