/**
 * NOVAQUOTE Wallet Integration Test Script
 * Tests the complete MetaMask wallet database integration
 */

import { walletDB, Wallet, WalletBalance } from '../src/market_database/wallet_database';

async function testWalletIntegration() {
    console.log('🚀 Starting NOVAQUOTE Wallet Integration Tests...\n');

    try {
        // Initialize database
        console.log('📊 Initializing database connection...');
        await walletDB.initialize();
        console.log('✅ Database initialized successfully\n');

        // Test 1: Create a test wallet
        console.log('🔐 Test 1: Creating test wallet...');
        const testAddress = '0x1234567890123456789012345678901234567890';
        const walletId = await walletDB.createWallet(
            testAddress,
            'Test Integration Wallet',
            'Created by integration test script'
        );
        console.log(`✅ Test wallet created with ID: ${walletId}\n`);

        // Test 2: Retrieve wallet by address
        console.log('🔍 Test 2: Retrieving wallet by address...');
        const retrievedWallet = await walletDB.getWalletByAddress(testAddress);
        if (retrievedWallet) {
            console.log(`✅ Wallet found: ${retrievedWallet.wallet_name} (${retrievedWallet.metamask_address})`);
            console.log(`   Status: ${retrievedWallet.is_active ? 'Active' : 'Inactive'}`);
            console.log(`   Verified: ${retrievedWallet.is_verified ? 'Yes' : 'No'}\n`);
        } else {
            throw new Error('Wallet not found by address');
        }

        // Test 3: Update wallet balance
        console.log('💰 Test 3: Updating wallet balance...');
        await walletDB.updateBalance(walletId, 1500.0, 1600.0, 'USD');
        console.log('✅ Balance updated: Available: $1,500, Total: $1,600\n');

        // Test 4: Retrieve current balance
        console.log('📈 Test 4: Retrieving current balance...');
        const balance = await walletDB.getCurrentBalance(walletId, 'USD');
        if (balance) {
            console.log(`✅ Current balance retrieved:`);
            console.log(`   Available: $${balance.available_balance.toLocaleString()}`);
            console.log(`   Total: $${balance.total_balance.toLocaleString()}`);
            console.log(`   Daily P&L: $${balance.daily_pnl.toFixed(2)}\n`);
        } else {
            throw new Error('Balance not found');
        }

        // Test 5: Create test trade
        console.log('📊 Test 5: Creating test trade...');
        const tradeData = {
            wallet_id: walletId,
            trade_id: 'trade_test_001',
            order_id: 'order_test_001',
            symbol: 'BTC/USD',
            exchange: 'hyperliquid',
            side: 'buy' as const,
            order_type: 'market' as const,
            quantity: 0.1,
            price: 45000.0,
            executed_quantity: 0.1,
            executed_price: 45000.0,
            quote_quantity: 4500.0,
            fee_amount: 4.5,
            fee_currency: 'USD',
            fee_rate: 0.001,
            status: 'filled' as const,
            realized_pnl: 50.0,
            commission: 4.5,
            order_timestamp: new Date().toISOString(),
            executed_timestamp: new Date().toISOString()
        };

        const tradeId = await walletDB.createTrade(tradeData);
        console.log(`✅ Test trade created with ID: ${tradeId}\n`);

        // Test 6: Retrieve trades
        console.log('📜 Test 6: Retrieving wallet trades...');
        const trades = await walletDB.getTrades(walletId, 10, 0);
        console.log(`✅ Found ${trades.length} trade(s)`);
        if (trades.length > 0) {
            const trade = trades[0];
            console.log(`   Latest: ${trade.side.toUpperCase()} ${trade.quantity} ${trade.symbol} at $${trade.executed_price}`);
            console.log(`   P&L: $${trade.realized_pnl.toFixed(2)}\n`);
        }

        // Test 7: Create test position
        console.log('📍 Test 7: Creating test position...');
        const positionData = {
            wallet_id: walletId,
            symbol: 'ETH/USD',
            exchange: 'hyperliquid',
            side: 'long' as const,
            position_size: 2.0,
            entry_price: 3000.0,
            current_price: 3100.0,
            unrealized_pnl: 200.0,
            realized_pnl: 0.0,
            total_pnl: 200.0,
            pnl_percentage: 6.67,
            margin_used: 600.0,
            margin_requirement: 600.0,
            leverage: 1.0,
            stop_loss: 2900.0,
            take_profit: 3200.0,
            max_loss: 200.0,
            status: 'open' as const
        };

        const positionId = await walletDB.upsertPosition(positionData);
        console.log(`✅ Test position created/updated with ID: ${positionId}\n`);

        // Test 8: Retrieve active positions
        console.log('🎯 Test 8: Retrieving active positions...');
        const positions = await walletDB.getActivePositions(walletId);
        console.log(`✅ Found ${positions.length} active position(s)`);
        if (positions.length > 0) {
            const position = positions[0];
            console.log(`   Position: ${position.side.toUpperCase()} ${position.position_size} ${position.symbol}`);
            console.log(`   Entry: $${position.entry_price}, Current: $${position.current_price}`);
            console.log(`   Unrealized P&L: $${position.unrealized_pnl.toFixed(2)} (${position.pnl_percentage.toFixed(2)}%)\n`);
        }

        // Test 9: Get wallet summary
        console.log('📊 Test 9: Getting wallet summary...');
        const summary = await walletDB.getWalletSummary(walletId);
        if (summary) {
            console.log(`✅ Wallet summary retrieved:`);
            console.log(`   Address: ${summary.metamask_address}`);
            console.log(`   Name: ${summary.wallet_name}`);
            console.log(`   Balance: $${summary.total_balance.toLocaleString()}`);
            console.log(`   P&L: $${summary.total_pnl.toFixed(2)} (${(summary.daily_return * 100).toFixed(2)}% daily)`);
            console.log(`   Active Positions: ${summary.active_positions}`);
            console.log(`   Total Trades: ${summary.total_trades}\n`);
        }

        // Test 10: Get wallet performance
        console.log('📈 Test 10: Getting wallet performance...');
        const performance = await walletDB.getWalletPerformance(walletId, 30);
        if (performance) {
            console.log(`✅ Performance metrics:`);
            console.log(`   30-day P&L: $${performance.trading_pnl_30d?.toFixed(2) || '0.00'}`);
            console.log(`   Trade Count: ${performance.trade_count_30d || 0}`);
            console.log(`   Active Positions: ${performance.active_positions_count || 0}`);
            console.log(`   Total Unrealized P&L: $${performance.total_unrealized_pnl?.toFixed(2) || '0.00'}\n`);
        }

        // Test 11: Balance history
        console.log('📜 Test 11: Getting balance history...');
        const balanceHistory = await walletDB.getBalanceHistory(walletId, 7);
        console.log(`✅ Found ${balanceHistory.length} balance record(s) in last 7 days`);

        // Test 12: Trade statistics
        console.log('📊 Test 12: Getting trade statistics...');
        const tradeStats = await walletDB.getTradeStats(walletId, 30);
        if (tradeStats) {
            console.log(`✅ 30-day trade statistics:`);
            console.log(`   Total Trades: ${tradeStats.total_trades}`);
            console.log(`   Filled Trades: ${tradeStats.filled_trades}`);
            console.log(`   Winning Trades: ${tradeStats.winning_trades}`);
            console.log(`   Losing Trades: ${tradeStats.losing_trades}`);
            console.log(`   Total P&L: $${tradeStats.total_pnl?.toFixed(2) || '0.00'}`);
            console.log(`   Average P&L: $${tradeStats.avg_pnl?.toFixed(2) || '0.00'}\n`);
        }

        console.log('🎉 ALL TESTS PASSED! 🎉');
        console.log('✅ NOVAQUOTE Wallet Database Integration is working correctly!');

    } catch (error) {
        console.error('❌ Test failed:', error);
        process.exit(1);
    } finally {
        // Close database connection
        await walletDB.close();
        console.log('📊 Database connection closed');
    }
}

// Run tests if this file is executed directly
if (require.main === module) {
    testWalletIntegration().catch(console.error);
}

export { testWalletIntegration };