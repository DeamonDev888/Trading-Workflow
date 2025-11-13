/**
 * NOVAQUOTE Wallet Database Manager
 * Complete database interface for MetaMask wallet integration
 * Replaces paper wallet simulation with real database storage
 */

import Database from 'better-sqlite3';
import path from 'path';
import crypto from 'crypto';

// Database configuration
const DB_PATH = path.join(__dirname, 'market_data.db');

// Database interface exports
export interface Wallet {
    id?: number;
    metamask_address: string;
    metamask_address_hash: string;
    wallet_type: string;
    wallet_name: string;
    description?: string;
    is_active: boolean;
    is_verified: boolean;
    verification_level: 'pending' | 'verified' | 'restricted' | 'suspended';
    allowed_exchanges: string; // JSON string
    max_position_size: number;
    risk_level: 'low' | 'medium' | 'high';
    created_at?: string;
    updated_at?: string;
    last_login_at?: string;
}

export interface WalletBalance {
    id?: number;
    wallet_id: number;
    currency: string;
    available_balance: number;
    total_balance: number;
    frozen_balance: number;
    unrealized_pnl: number;
    realized_pnl: number;
    total_pnl: number;
    daily_pnl: number;
    daily_return: number;
    total_return: number;
    balance_timestamp?: string;
}

export interface Trade {
    id?: number;
    wallet_id: number;
    trade_id: string;
    order_id: string;
    symbol: string;
    exchange: string;
    side: 'buy' | 'sell';
    order_type: 'market' | 'limit' | 'stop' | 'stop_limit' | 'take_profit';
    quantity: number;
    price: number;
    executed_quantity: number;
    executed_price: number;
    quote_quantity: number;
    fee_amount: number;
    fee_currency: string;
    fee_rate: number;
    status: 'pending' | 'filled' | 'partially_filled' | 'cancelled' | 'failed' | 'rejected';
    realized_pnl: number;
    commission: number;
    order_timestamp: string;
    executed_timestamp?: string;
    created_at?: string;
    updated_at?: string;
}

export interface Position {
    id?: number;
    wallet_id: number;
    symbol: string;
    exchange: string;
    side: 'long' | 'short';
    position_size: number;
    entry_price: number;
    current_price: number;
    unrealized_pnl: number;
    realized_pnl: number;
    total_pnl: number;
    pnl_percentage: number;
    margin_used: number;
    margin_requirement: number;
    leverage: number;
    stop_loss?: number;
    take_profit?: number;
    max_loss: number;
    status: 'open' | 'closed' | 'liquidated' | 'reduced';
    opened_at?: string;
    closed_at?: string;
    last_updated_at?: string;
}

export interface WalletSummary {
    id: number;
    metamask_address: string;
    wallet_name: string;
    is_active: boolean;
    verification_level: string;
    total_balance: number;
    available_balance: number;
    total_pnl: number;
    daily_pnl: number;
    daily_return: number;
    total_trades: number;
    active_positions: number;
    created_at?: string;
    last_login_at?: string;
}

class WalletDatabase {
    private db: Database.Database | null = null;

    // Initialize database connection
    initialize(): void {
        try {
            this.db = new Database(DB_PATH);

            // Enable foreign keys
            this.db.pragma('foreign_keys = ON');

            // Set WAL mode for better performance
            this.db.pragma('journal_mode = WAL');

            console.log('Wallet database initialized successfully');
        } catch (error) {
            console.error('Failed to initialize wallet database:', error);
            throw error;
        }
    }

    // Close database connection
    close(): void {
        if (this.db) {
            this.db.close();
            this.db = null;
        }
    }

    // Utility function to hash MetaMask address
    private hashAddress(address: string): string {
        return crypto.createHash('sha256').update(address.toLowerCase()).digest('hex');
    }

    // Utility function to validate Ethereum address
    private isValidEthereumAddress(address: string): boolean {
        return /^0x[a-fA-F0-9]{40}$/.test(address);
    }

    // ================================
    // WALLET MANAGEMENT
    // ================================

    // Create new wallet
    async createWallet(metamaskAddress: string, walletName: string, description?: string): Promise<number> {
        if (!this.db) await this.initialize();
        if (!this.isValidEthereumAddress(metamaskAddress)) {
            throw new Error('Invalid MetaMask address format');
        }

        const addressHash = this.hashAddress(metamaskAddress);

        const result = await this.db!.run(`
            INSERT INTO wallets (
                metamask_address,
                metamask_address_hash,
                wallet_name,
                description
            ) VALUES (?, ?, ?, ?)
        `, [metamaskAddress, addressHash, walletName, description]);

        return result.lastID!;
    }

    // Get wallet by MetaMask address
    async getWalletByAddress(metamaskAddress: string): Promise<Wallet | null> {
        if (!this.db) await this.initialize();

        const row = await this.db!.get(`
            SELECT * FROM wallets WHERE metamask_address = ?
        `, [metamaskAddress]);

        return row || null;
    }

    // Get wallet by ID
    async getWalletById(walletId: number): Promise<Wallet | null> {
        if (!this.db) await this.initialize();

        const row = await this.db!.get(`
            SELECT * FROM wallets WHERE id = ?
        `, [walletId]);

        return row || null;
    }

    // Update wallet verification status
    async updateWalletVerification(walletId: number, isVerified: boolean, level: string): Promise<void> {
        if (!this.db) await this.initialize();

        await this.db!.run(`
            UPDATE wallets
            SET is_verified = ?, verification_level = ?
            WHERE id = ?
        `, [isVerified, level, walletId]);
    }

    // Update last login timestamp
    async updateLastLogin(walletId: number): Promise<void> {
        if (!this.db) await this.initialize();

        await this.db!.run(`
            UPDATE wallets SET last_login_at = CURRENT_TIMESTAMP WHERE id = ?
        `, [walletId]);
    }

    // ================================
    // BALANCE MANAGEMENT
    // ================================

    // Get current balance for wallet
    async getCurrentBalance(walletId: number, currency: string = 'USD'): Promise<WalletBalance | null> {
        if (!this.db) await this.initialize();

        const row = await this.db!.get(`
            SELECT * FROM wallet_balances
            WHERE wallet_id = ? AND currency = ?
            ORDER BY balance_timestamp DESC
            LIMIT 1
        `, [walletId, currency]);

        return row || null;
    }

    // Update wallet balance
    async updateBalance(
        walletId: number,
        availableBalance: number,
        totalBalance: number,
        currency: string = 'USD'
    ): Promise<void> {
        if (!this.db) await this.initialize();

        await this.db!.run(`
            INSERT INTO wallet_balances (
                wallet_id, currency, available_balance, total_balance
            ) VALUES (?, ?, ?, ?)
        `, [walletId, currency, availableBalance, totalBalance]);
    }

    // Get balance history
    async getBalanceHistory(walletId: number, days: number = 30): Promise<WalletBalance[]> {
        if (!this.db) await this.initialize();

        const rows = await this.db!.all(`
            SELECT * FROM wallet_balances
            WHERE wallet_id = ? AND balance_timestamp >= datetime('now', '-${days} days')
            ORDER BY balance_timestamp DESC
        `, [walletId]);

        return rows;
    }

    // ================================
    // TRADE MANAGEMENT
    // ================================

    // Create new trade
    async createTrade(trade: Omit<Trade, 'id' | 'created_at' | 'updated_at'>): Promise<number> {
        if (!this.db) await this.initialize();

        const result = await this.db!.run(`
            INSERT INTO trades (
                wallet_id, trade_id, order_id, symbol, exchange, side, order_type,
                quantity, price, executed_quantity, executed_price, quote_quantity,
                fee_amount, fee_currency, fee_rate, status, realized_pnl, commission,
                order_timestamp, executed_timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `, [
            trade.wallet_id, trade.trade_id, trade.order_id, trade.symbol, trade.exchange,
            trade.side, trade.order_type, trade.quantity, trade.price, trade.executed_quantity,
            trade.executed_price, trade.quote_quantity, trade.fee_amount, trade.fee_currency,
            trade.fee_rate, trade.status, trade.realized_pnl, trade.commission,
            trade.order_timestamp, trade.executed_timestamp
        ]);

        return result.lastID!;
    }

    // Get trades for wallet
    async getTrades(walletId: number, limit: number = 50, offset: number = 0): Promise<Trade[]> {
        if (!this.db) await this.initialize();

        const rows = await this.db!.all(`
            SELECT * FROM trades
            WHERE wallet_id = ?
            ORDER BY executed_timestamp DESC, created_at DESC
            LIMIT ? OFFSET ?
        `, [walletId, limit, offset]);

        return rows;
    }

    // Get trade statistics
    async getTradeStats(walletId: number, days: number = 30): Promise<any> {
        if (!this.db) await this.initialize();

        const stats = await this.db!.get(`
            SELECT
                COUNT(*) as total_trades,
                SUM(CASE WHEN status = 'filled' THEN 1 ELSE 0 END) as filled_trades,
                SUM(CASE WHEN status = 'filled' THEN realized_pnl ELSE 0 END) as total_pnl,
                AVG(CASE WHEN status = 'filled' THEN realized_pnl ELSE NULL END) as avg_pnl,
                SUM(CASE WHEN status = 'filled' AND realized_pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                SUM(CASE WHEN status = 'filled' AND realized_pnl < 0 THEN 1 ELSE 0 END) as losing_trades
            FROM trades
            WHERE wallet_id = ? AND created_at >= datetime('now', '-${days} days')
        `, [walletId]);

        return stats;
    }

    // ================================
    // POSITION MANAGEMENT
    // ================================

    // Create or update position
    async upsertPosition(position: Omit<Position, 'id' | 'opened_at' | 'last_updated_at'>): Promise<number> {
        if (!this.db) await this.initialize();

        // Check if position exists
        const existing = await this.db!.get(`
            SELECT id FROM positions
            WHERE wallet_id = ? AND symbol = ? AND exchange = ? AND status = 'open'
        `, [position.wallet_id, position.symbol, position.exchange]);

        if (existing) {
            // Update existing position
            await this.db!.run(`
                UPDATE positions SET
                    position_size = ?, entry_price = ?, current_price = ?,
                    unrealized_pnl = ?, realized_pnl = ?, total_pnl = ?, pnl_percentage = ?,
                    margin_used = ?, margin_requirement = ?, leverage = ?,
                    stop_loss = ?, take_profit = ?, max_loss = ?, status = ?
                WHERE id = ?
            `, [
                position.position_size, position.entry_price, position.current_price,
                position.unrealized_pnl, position.realized_pnl, position.total_pnl, position.pnl_percentage,
                position.margin_used, position.margin_requirement, position.leverage,
                position.stop_loss, position.take_profit, position.max_loss, position.status,
                existing.id
            ]);

            return existing.id;
        } else {
            // Insert new position
            const result = await this.db!.run(`
                INSERT INTO positions (
                    wallet_id, symbol, exchange, side, position_size, entry_price, current_price,
                    unrealized_pnl, realized_pnl, total_pnl, pnl_percentage, margin_used,
                    margin_requirement, leverage, stop_loss, take_profit, max_loss, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            `, [
                position.wallet_id, position.symbol, position.exchange, position.side,
                position.position_size, position.entry_price, position.current_price,
                position.unrealized_pnl, position.realized_pnl, position.total_pnl, position.pnl_percentage,
                position.margin_used, position.margin_requirement, position.leverage,
                position.stop_loss, position.take_profit, position.max_loss, position.status
            ]);

            return result.lastID!;
        }
    }

    // Get active positions for wallet
    async getActivePositions(walletId: number): Promise<Position[]> {
        if (!this.db) await this.initialize();

        const rows = await this.db!.all(`
            SELECT * FROM positions
            WHERE wallet_id = ? AND status = 'open'
            ORDER BY opened_at DESC
        `, [walletId]);

        return rows;
    }

    // Close position
    async closePosition(positionId: number, closePrice: number, finalPnl: number): Promise<void> {
        if (!this.db) await this.initialize();

        await this.db!.run(`
            UPDATE positions SET
                status = 'closed',
                current_price = ?,
                realized_pnl = realized_pnl + ?,
                total_pnl = total_pnl + ?,
                closed_at = CURRENT_TIMESTAMP,
                last_updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        `, [closePrice, finalPnl, finalPnl, positionId]);
    }

    // ================================
    // WALLET SUMMARY AND ANALYTICS
    // ================================

    // Get complete wallet summary
    async getWalletSummary(walletId: number): Promise<WalletSummary | null> {
        if (!this.db) await this.initialize();

        const row = await this.db!.get(`
            SELECT * FROM wallet_summary WHERE id = ?
        `, [walletId]);

        return row || null;
    }

    // Get wallet performance metrics
    async getWalletPerformance(walletId: number, days: number = 30): Promise<any> {
        if (!this.db) await this.initialize();

        const performance = await this.db!.get(`
            SELECT
                wb.total_balance,
                wb.daily_pnl,
                wb.daily_return,
                COUNT(DISTINCT t.id) as trade_count_30d,
                SUM(CASE WHEN t.status = 'filled' THEN t.realized_pnl ELSE 0 END) as trading_pnl_30d,
                COUNT(DISTINCT p.id) as active_positions_count,
                SUM(p.unrealized_pnl) as total_unrealized_pnl
            FROM wallet_balances wb
            LEFT JOIN trades t ON wb.wallet_id = t.wallet_id AND t.created_at >= datetime('now', '-${days} days')
            LEFT JOIN positions p ON wb.wallet_id = p.wallet_id AND p.status = 'open'
            WHERE wb.wallet_id = ?
            GROUP BY wb.wallet_id
        `, [walletId]);

        return performance;
    }

    // ================================
    // UTILITY FUNCTIONS
    // ================================

    // Execute custom query
    async executeQuery(query: string, params: any[] = []): Promise<any> {
        if (!this.db) await this.initialize();

        try {
            const result = await this.db!.all(query, params);
            return result;
        } catch (error) {
            console.error('Database query error:', error);
            throw error;
        }
    }

    // Check database connection
    isConnected(): boolean {
        return this.db !== null;
    }
}

// Export singleton instance
export const walletDB = new WalletDatabase();

// Export types
export type { WalletDatabase };