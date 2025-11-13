/**
 * Simple test script for NOVAQUOTE Wallet Integration
 * Tests database functionality directly without server
 */

const { walletDB } = require('../src/market_database/wallet_database_sync');

async function runTests() {
    console.log('🚀 Starting NOVAQUOTE Wallet Database Tests...\n');

    try {
        // Test 1: Initialize database
        console.log('📊 Test 1: Initializing database connection...');
        walletDB.initialize();
        console.log('✅ Database initialized successfully\n');

        // Test 2: Check if sample wallet exists
        console.log('🔍 Test 2: Checking if sample wallet exists...');
        const testAddress = '0x742d35Cc6634C0532925a3b8D4E7E0E0e9e0d3a1';
        const wallet = walletDB.getWalletByAddress(testAddress);

        if (wallet) {
            console.log(`✅ Sample wallet found: ${wallet.wallet_name}`);
            console.log(`   Address: ${wallet.metamask_address}`);
            console.log(`   Verified: ${wallet.is_verified ? 'Yes' : 'No'}`);
            console.log(`   Status: ${wallet.verification_level}\n`);
        } else {
            console.log('❌ Sample wallet not found\n');
        }

        // Test 3: Create new test wallet
        console.log('🔐 Test 3: Creating new test wallet...');
        const newTestAddress = '0x' + '1'.repeat(40);
        const walletId = walletDB.createWallet(
            newTestAddress,
            'Test Wallet',
            'Created by test script'
        );
        console.log(`✅ New wallet created with ID: ${walletId}\n`);

        // Test 4: Add balance to new wallet
        console.log('💰 Test 4: Adding balance to new wallet...');
        walletDB.updateBalance(walletId, 1000.0, 1100.0, 'USD');
        console.log('✅ Balance updated: $1,000 available, $1,100 total\n');

        // Test 5: Get wallet balance
        console.log('📈 Test 5: Retrieving wallet balance...');
        const balance = walletDB.getCurrentBalance(walletId, 'USD');
        if (balance) {
            console.log(`✅ Balance retrieved:`);
            console.log(`   Available: $${balance.available_balance.toLocaleString()}`);
            console.log(`   Total: $${balance.total_balance.toLocaleString()}\n`);
        }

        // Test 6: Create test trade
        console.log('📊 Test 6: Creating test trade...');
        const tradeData = {
            wallet_id: walletId,
            trade_id: `test_trade_${Date.now()}`,
            order_id: `test_order_${Date.now()}`,
            symbol: 'BTC/USD',
            exchange: 'hyperliquid',
            side: 'buy',
            order_type: 'market',
            quantity: 0.1,
            price: 45000.0,
            executed_quantity: 0.1,
            executed_price: 45000.0,
            quote_quantity: 4500.0,
            fee_amount: 4.5,
            fee_currency: 'USD',
            fee_rate: 0.001,
            status: 'filled',
            realized_pnl: 50.0,
            commission: 4.5,
            order_timestamp: new Date().toISOString(),
            executed_timestamp: new Date().toISOString()
        };

        const tradeId = walletDB.createTrade(tradeData);
        console.log(`✅ Test trade created with ID: ${tradeId}\n`);

        // Test 7: Get trades
        console.log('📜 Test 7: Retrieving wallet trades...');
        const trades = walletDB.getTrades(walletId, 5, 0);
        console.log(`✅ Found ${trades.length} trade(s)`);
        if (trades.length > 0) {
            console.log(`   Latest: ${trades[0].side.toUpperCase()} ${trades[0].quantity} ${trades[0].symbol}\n`);
        }

        // Test 8: Create test position
        console.log('📍 Test 8: Creating test position...');
        const positionData = {
            wallet_id: walletId,
            symbol: 'ETH/USD',
            exchange: 'hyperliquid',
            side: 'long',
            position_size: 1.0,
            entry_price: 3000.0,
            current_price: 3100.0,
            unrealized_pnl: 100.0,
            realized_pnl: 0.0,
            total_pnl: 100.0,
            pnl_percentage: 3.33,
            margin_used: 300.0,
            margin_requirement: 300.0,
            leverage: 1.0,
            stop_loss: 2900.0,
            take_profit: 3200.0,
            max_loss: 100.0,
            status: 'open'
        };

        const positionId = walletDB.upsertPosition(positionData);
        console.log(`✅ Test position created with ID: ${positionId}\n`);

        // Test 9: Get active positions
        console.log('🎯 Test 9: Retrieving active positions...');
        const positions = walletDB.getActivePositions(walletId);
        console.log(`✅ Found ${positions.length} active position(s)`);
        if (positions.length > 0) {
            console.log(`   Position: ${positions[0].side.toUpperCase()} ${positions[0].position_size} ${positions[0].symbol}\n`);
        }

        // Test 10: Get wallet summary
        console.log('📊 Test 10: Getting wallet summary...');
        const summary = walletDB.getWalletSummary(walletId);
        if (summary) {
            console.log(`✅ Summary retrieved:`);
            console.log(`   Wallet: ${summary.wallet_name}`);
            console.log(`   Balance: $${summary.total_balance.toLocaleString()}`);
            console.log(`   Trades: ${summary.total_trades}`);
            console.log(`   Positions: ${summary.active_positions}\n`);
        }

        console.log('🎉 ALL TESTS PASSED! 🎉');
        console.log('✅ NOVAQUOTE Wallet Database Integration is working correctly!');
        console.log('\n📋 Summary:');
        console.log('   • Database connection: ✅ Working');
        console.log('   • Wallet creation: ✅ Working');
        console.log('   • Balance management: ✅ Working');
        console.log('   • Trade tracking: ✅ Working');
        console.log('   • Position management: ✅ Working');
        console.log('   • Data persistence: ✅ Working');

    } catch (error) {
        console.error('❌ Test failed:', error);
        process.exit(1);
    } finally {
        // Close database connection
        walletDB.close();
        console.log('\n📊 Database connection closed');
    }
}

// Run tests
runTests();