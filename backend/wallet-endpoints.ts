/**
 * NOVAQUOTE MetaMask Wallet API Endpoints
 * Complete replacement for paper trading simulation with real database storage
 */

import express, { Request, Response } from 'express';
import { walletDB, Wallet, WalletBalance, Trade, Position } from '../src/market_database/wallet_database_sync';
import crypto from 'crypto';

const router = express.Router();

// Initialize database connection
router.use((req, res, next) => {
    try {
        if (!walletDB.isConnected()) {
            walletDB.initialize();
        }
        next();
    } catch (error) {
        console.error('Database connection error:', error);
        res.status(500).json({
            success: false,
            error: 'Database connection failed',
            timestamp: new Date().toISOString()
        });
    }
});

// Utility function for signature verification
function verifySignature(message: string, signature: string, address: string): boolean {
    try {
        // This is a simplified verification - in production, you'd use ethers.js or web3.js
        // For now, we'll do basic validation
        return signature.length === 132 && address.startsWith('0x') && address.length === 42;
    } catch (error) {
        return false;
    }
}

// ============================================
// WALLET AUTHENTICATION & MANAGEMENT
// ============================================

/**
 * POST /api/wallet/auth
 * Authenticate MetaMask wallet with signature
 */
router.post('/auth', async (req: Request, res: Response) => {
    try {
        const { address, signature, message } = req.body;

        // Validate inputs
        if (!address || !signature || !message) {
            return res.status(400).json({
                success: false,
                error: 'Missing required fields: address, signature, message',
                timestamp: new Date().toISOString()
            });
        }

        // Verify address format
        if (!/^0x[a-fA-F0-9]{40}$/.test(address)) {
            return res.status(400).json({
                success: false,
                error: 'Invalid MetaMask address format',
                timestamp: new Date().toISOString()
            });
        }

        // Verify signature (simplified)
        if (!verifySignature(message, signature, address)) {
            return res.status(401).json({
                success: false,
                error: 'Invalid signature',
                timestamp: new Date().toISOString()
            });
        }

        // Check if wallet exists
        let wallet = await walletDB.getWalletByAddress(address);

        if (!wallet) {
            // Create new wallet
            const walletId = await walletDB.createWallet(
                address,
                `NOVAQUOTE Wallet ${address.slice(0, 6)}...${address.slice(-4)}`,
                'Auto-created via MetaMask authentication'
            );

            wallet = await walletDB.getWalletById(walletId)!;

            // Create initial balance record
            await walletDB.updateBalance(walletId, 1000.0, 1000.0, 'USD');

            console.log(`Created new wallet: ${address} with ID: ${walletId}`);
        }

        // Update last login
        await walletDB.updateLastLogin(wallet.id!);

        // Get wallet summary
        const walletSummary = await walletDB.getWalletSummary(wallet.id!);

        res.json({
            success: true,
            data: {
                wallet_id: wallet.id,
                metamask_address: wallet.metamask_address,
                wallet_name: wallet.wallet_name,
                is_verified: wallet.is_verified,
                verification_level: wallet.verification_level,
                balance: walletSummary?.total_balance || 1000.0,
                available_balance: walletSummary?.available_balance || 1000.0,
                total_pnl: walletSummary?.total_pnl || 0.0,
                daily_pnl: walletSummary?.daily_pnl || 0.0,
                daily_return: walletSummary?.daily_return || 0.0,
                active_positions: walletSummary?.active_positions || 0,
                total_trades: walletSummary?.total_trades || 0,
                last_login_at: wallet.last_login_at,
                created_at: wallet.created_at
            },
            timestamp: new Date().toISOString()
        });

    } catch (error: any) {
        console.error('Wallet auth error:', error);
        res.status(500).json({
            success: false,
            error: error.message,
            timestamp: new Date().toISOString()
        });
    }
});

/**
 * GET /api/wallet/:address
 * Get wallet details by MetaMask address
 */
router.get('/:address', async (req: Request, res: Response) => {
    try {
        const { address } = req.params;

        if (!/^0x[a-fA-F0-9]{40}$/.test(address)) {
            return res.status(400).json({
                success: false,
                error: 'Invalid MetaMask address format',
                timestamp: new Date().toISOString()
            });
        }

        const wallet = await walletDB.getWalletByAddress(address);

        if (!wallet) {
            return res.status(404).json({
                success: false,
                error: 'Wallet not found',
                timestamp: new Date().toISOString()
            });
        }

        const walletSummary = await walletDB.getWalletSummary(wallet.id!);

        res.json({
            success: true,
            data: {
                wallet_id: wallet.id,
                metamask_address: wallet.metamask_address,
                wallet_name: wallet.wallet_name,
                description: wallet.description,
                is_active: wallet.is_active,
                is_verified: wallet.is_verified,
                verification_level: wallet.verification_level,
                risk_level: wallet.risk_level,
                max_position_size: wallet.max_position_size,
                balance: walletSummary?.total_balance || 0.0,
                available_balance: walletSummary?.available_balance || 0.0,
                total_pnl: walletSummary?.total_pnl || 0.0,
                daily_pnl: walletSummary?.daily_pnl || 0.0,
                daily_return: walletSummary?.daily_return || 0.0,
                active_positions: walletSummary?.active_positions || 0,
                total_trades: walletSummary?.total_trades || 0,
                created_at: wallet.created_at,
                updated_at: wallet.updated_at,
                last_login_at: wallet.last_login_at
            },
            timestamp: new Date().toISOString()
        });

    } catch (error: any) {
        console.error('Get wallet error:', error);
        res.status(500).json({
            success: false,
            error: error.message,
            timestamp: new Date().toISOString()
        });
    }
});

// ============================================
// BALANCE MANAGEMENT
// ============================================

/**
 * GET /api/wallet/:address/balance
 * Get current wallet balance
 */
router.get('/:address/balance', async (req: Request, res: Response) => {
    try {
        const { address } = req.params;
        const { currency = 'USD' } = req.query;

        const wallet = await walletDB.getWalletByAddress(address);
        if (!wallet) {
            return res.status(404).json({
                success: false,
                error: 'Wallet not found',
                timestamp: new Date().toISOString()
            });
        }

        const balance = await walletDB.getCurrentBalance(wallet.id!, currency as string);

        res.json({
            success: true,
            data: balance || {
                wallet_id: wallet.id,
                currency,
                available_balance: 0.0,
                total_balance: 0.0,
                frozen_balance: 0.0,
                unrealized_pnl: 0.0,
                realized_pnl: 0.0,
                total_pnl: 0.0,
                daily_pnl: 0.0,
                daily_return: 0.0,
                total_return: 0.0
            },
            timestamp: new Date().toISOString()
        });

    } catch (error: any) {
        console.error('Get balance error:', error);
        res.status(500).json({
            success: false,
            error: error.message,
            timestamp: new Date().toISOString()
        });
    }
});

/**
 * POST /api/wallet/:address/balance/update
 * Update wallet balance (for deposits, withdrawals, P&L)
 */
router.post('/:address/balance/update', async (req: Request, res: Response) => {
    try {
        const { address } = req.params;
        const { available_balance, total_balance, currency = 'USD' } = req.body;

        if (available_balance === undefined || total_balance === undefined) {
            return res.status(400).json({
                success: false,
                error: 'Missing required fields: available_balance, total_balance',
                timestamp: new Date().toISOString()
            });
        }

        const wallet = await walletDB.getWalletByAddress(address);
        if (!wallet) {
            return res.status(404).json({
                success: false,
                error: 'Wallet not found',
                timestamp: new Date().toISOString()
            });
        }

        await walletDB.updateBalance(wallet.id!, available_balance, total_balance, currency);

        const updatedBalance = await walletDB.getCurrentBalance(wallet.id!, currency);

        res.json({
            success: true,
            data: updatedBalance,
            message: 'Balance updated successfully',
            timestamp: new Date().toISOString()
        });

    } catch (error: any) {
        console.error('Update balance error:', error);
        res.status(500).json({
            success: false,
            error: error.message,
            timestamp: new Date().toISOString()
        });
    }
});

/**
 * GET /api/wallet/:address/balance/history
 * Get balance history for wallet
 */
router.get('/:address/balance/history', async (req: Request, res: Response) => {
    try {
        const { address } = req.params;
        const { days = 30 } = req.query;

        const wallet = await walletDB.getWalletByAddress(address);
        if (!wallet) {
            return res.status(404).json({
                success: false,
                error: 'Wallet not found',
                timestamp: new Date().toISOString()
            });
        }

        const history = await walletDB.getBalanceHistory(wallet.id!, parseInt(days as string));

        res.json({
            success: true,
            data: history,
            count: history.length,
            timestamp: new Date().toISOString()
        });

    } catch (error: any) {
        console.error('Get balance history error:', error);
        res.status(500).json({
            success: false,
            error: error.message,
            timestamp: new Date().toISOString()
        });
    }
});

// ============================================
// TRADES MANAGEMENT
// ============================================

/**
 * GET /api/wallet/:address/trades
 * Get trades for wallet
 */
router.get('/:address/trades', async (req: Request, res: Response) => {
    try {
        const { address } = req.params;
        const { limit = 50, offset = 0 } = req.query;

        const wallet = await walletDB.getWalletByAddress(address);
        if (!wallet) {
            return res.status(404).json({
                success: false,
                error: 'Wallet not found',
                timestamp: new Date().toISOString()
            });
        }

        const trades = await walletDB.getTrades(
            wallet.id!,
            parseInt(limit as string),
            parseInt(offset as string)
        );

        res.json({
            success: true,
            data: trades,
            count: trades.length,
            timestamp: new Date().toISOString()
        });

    } catch (error: any) {
        console.error('Get trades error:', error);
        res.status(500).json({
            success: false,
            error: error.message,
            timestamp: new Date().toISOString()
        });
    }
});

/**
 * POST /api/wallet/:address/trades
 * Create new trade record
 */
router.post('/:address/trades', async (req: Request, res: Response) => {
    try {
        const { address } = req.params;
        const tradeData = req.body;

        const wallet = await walletDB.getWalletByAddress(address);
        if (!wallet) {
            return res.status(404).json({
                success: false,
                error: 'Wallet not found',
                timestamp: new Date().toISOString()
            });
        }

        const trade: Omit<Trade, 'id' | 'created_at' | 'updated_at'> = {
            wallet_id: wallet.id!,
            ...tradeData
        };

        const tradeId = await walletDB.createTrade(trade);

        res.json({
            success: true,
            data: { trade_id: tradeId },
            message: 'Trade created successfully',
            timestamp: new Date().toISOString()
        });

    } catch (error: any) {
        console.error('Create trade error:', error);
        res.status(500).json({
            success: false,
            error: error.message,
            timestamp: new Date().toISOString()
        });
    }
});

/**
 * GET /api/wallet/:address/trades/stats
 * Get trading statistics for wallet
 */
router.get('/:address/trades/stats', async (req: Request, res: Response) => {
    try {
        const { address } = req.params;
        const { days = 30 } = req.query;

        const wallet = await walletDB.getWalletByAddress(address);
        if (!wallet) {
            return res.status(404).json({
                success: false,
                error: 'Wallet not found',
                timestamp: new Date().toISOString()
            });
        }

        const stats = await walletDB.getTradeStats(wallet.id!, parseInt(days as string));

        res.json({
            success: true,
            data: stats,
            timestamp: new Date().toISOString()
        });

    } catch (error: any) {
        console.error('Get trade stats error:', error);
        res.status(500).json({
            success: false,
            error: error.message,
            timestamp: new Date().toISOString()
        });
    }
});

// ============================================
// POSITIONS MANAGEMENT
// ============================================

/**
 * GET /api/wallet/:address/positions
 * Get active positions for wallet
 */
router.get('/:address/positions', async (req: Request, res: Response) => {
    try {
        const { address } = req.params;

        const wallet = await walletDB.getWalletByAddress(address);
        if (!wallet) {
            return res.status(404).json({
                success: false,
                error: 'Wallet not found',
                timestamp: new Date().toISOString()
            });
        }

        const positions = await walletDB.getActivePositions(wallet.id!);

        res.json({
            success: true,
            data: positions,
            count: positions.length,
            timestamp: new Date().toISOString()
        });

    } catch (error: any) {
        console.error('Get positions error:', error);
        res.status(500).json({
            success: false,
            error: error.message,
            timestamp: new Date().toISOString()
        });
    }
});

/**
 * POST /api/wallet/:address/positions
 * Create or update position
 */
router.post('/:address/positions', async (req: Request, res: Response) => {
    try {
        const { address } = req.params;
        const positionData = req.body;

        const wallet = await walletDB.getWalletByAddress(address);
        if (!wallet) {
            return res.status(404).json({
                success: false,
                error: 'Wallet not found',
                timestamp: new Date().toISOString()
            });
        }

        const position: Omit<Position, 'id' | 'opened_at' | 'last_updated_at'> = {
            wallet_id: wallet.id!,
            ...positionData
        };

        const positionId = await walletDB.upsertPosition(position);

        res.json({
            success: true,
            data: { position_id: positionId },
            message: 'Position updated successfully',
            timestamp: new Date().toISOString()
        });

    } catch (error: any) {
        console.error('Update position error:', error);
        res.status(500).json({
            success: false,
            error: error.message,
            timestamp: new Date().toISOString()
        });
    }
});

/**
 * POST /api/wallet/:address/positions/:positionId/close
 * Close a position
 */
router.post('/:address/positions/:positionId/close', async (req: Request, res: Response) => {
    try {
        const { address, positionId } = req.params;
        const { close_price, final_pnl } = req.body;

        const wallet = await walletDB.getWalletByAddress(address);
        if (!wallet) {
            return res.status(404).json({
                success: false,
                error: 'Wallet not found',
                timestamp: new Date().toISOString()
            });
        }

        if (close_price === undefined || final_pnl === undefined) {
            return res.status(400).json({
                success: false,
                error: 'Missing required fields: close_price, final_pnl',
                timestamp: new Date().toISOString()
            });
        }

        await walletDB.closePosition(parseInt(positionId), close_price, final_pnl);

        res.json({
            success: true,
            message: 'Position closed successfully',
            timestamp: new Date().toISOString()
        });

    } catch (error: any) {
        console.error('Close position error:', error);
        res.status(500).json({
            success: false,
            error: error.message,
            timestamp: new Date().toISOString()
        });
    }
});

// ============================================
// WALLET SUMMARY & PERFORMANCE
// ============================================

/**
 * GET /api/wallet/:address/summary
 * Get complete wallet summary
 */
router.get('/:address/summary', async (req: Request, res: Response) => {
    try {
        const { address } = req.params;

        const wallet = await walletDB.getWalletByAddress(address);
        if (!wallet) {
            return res.status(404).json({
                success: false,
                error: 'Wallet not found',
                timestamp: new Date().toISOString()
            });
        }

        const summary = await walletDB.getWalletSummary(wallet.id!);
        const performance = await walletDB.getWalletPerformance(wallet.id!);

        res.json({
            success: true,
            data: {
                wallet_info: {
                    id: wallet.id,
                    metamask_address: wallet.metamask_address,
                    wallet_name: wallet.wallet_name,
                    is_verified: wallet.is_verified,
                    verification_level: wallet.verification_level,
                    risk_level: wallet.risk_level
                },
                summary,
                performance
            },
            timestamp: new Date().toISOString()
        });

    } catch (error: any) {
        console.error('Get wallet summary error:', error);
        res.status(500).json({
            success: false,
            error: error.message,
            timestamp: new Date().toISOString()
        });
    }
});

export default router;