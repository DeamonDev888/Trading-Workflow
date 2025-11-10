"""
🚀 NOVAQUOTE LOGGING SYSTEM DEMONSTRATION
Complete demonstration of the 100% visibility logging platform
Shows: Expert logging, trade tracking, risk management, agent monitoring
Built by Moon Dev - Professional Trading Operations
"""

import time
import random
import asyncio
from decimal import Decimal
from typing import Dict, List

from src.logger import get_logger, log_trade, log_agent, log_risk, log_portfolio
from src.agents.base_agent import BaseAgent
from src.algorithms.hyperliquid_mainnet_agent import HyperLiquidMainnetAgent


class DemoTradingAgent(BaseAgent):
    """Demo trading agent using the new enhanced logging system"""

    def __init__(self):
        super().__init__("demo_trading", config={"demo_mode": True})

    def simulate_market_analysis(self, symbol: str):
        """Simulate market analysis with detailed logging"""
        self.info(f"Starting market analysis for {symbol}", {
            "symbol": symbol,
            "analysis_type": "technical_indicators",
            "timeframe": "5m"
        })

        start_time = self.start_operation("market_analysis")

        price = random.uniform(100, 1000)
        volume = random.uniform(1000000, 10000000)
        rsi = random.uniform(20, 80)
        macd = random.uniform(-10, 10)

        market_data = {
            "symbol": symbol,
            "current_price": price,
            "volume_24h": volume,
            "rsi": rsi,
            "macd": macd,
            "trend": "BULLISH" if rsi > 50 else "BEARISH",
            "volatility": random.uniform(0.01, 0.05)
        }

        self.logger.market_data(symbol, "technical_analysis", market_data)

        time.sleep(random.uniform(0.1, 0.5))

        self.end_operation("market_analysis", start_time, success=True, details={
            "symbol": symbol,
            "indicators_calculated": 4,
            "signals_found": random.randint(0, 3)
        })

        return market_data

    def simulate_trade_execution(self, symbol: str, action: str):
        """Simulate trade execution with comprehensive logging"""
        self.info(f"Simulating {action} trade for {symbol}", {
            "symbol": symbol,
            "action": action,
            "simulation": True
        })

        market_data = self.simulate_market_analysis(symbol)

        size = random.uniform(0.1, 2.0)
        price = market_data["current_price"]

        trade_details = {
            "symbol": symbol,
            "action": action,
            "size": size,
            "price": price,
            "value_usd": size * price,
            "leverage": random.randint(1, 10),
            "order_type": "MARKET",
            "demo_mode": True
        }

        log_trade(action, symbol, {
            **trade_details,
            "initiated_by": "DemoTradingAgent",
            "timestamp": time.time()
        })

        execution_start = self.start_operation("trade_execution")
        time.sleep(random.uniform(0.2, 1.0))  # Simulate network latency

        success = random.random() > 0.1  # 90% success rate

        if success:
            self.end_operation("trade_execution", execution_start, success=True, details=trade_details)

            log_trade("EXECUTED", symbol, {
                **trade_details,
                "execution_time_ms": (time.time() - execution_start) * 1000,
                "success": True,
                "order_id": f"DEMO_{int(time.time()*1000)}"
            })

            self.success(f"✅ {action} order executed: {size} {symbol} @ ${price:.2f}", {
                "symbol": symbol,
                "action": action,
                "size": size,
                "price": price,
                "value_usd": size * price
            })

        else:
            error_msg = "Insufficient liquidity" if random.random() > 0.5 else "Price moved"
            self.end_operation("trade_execution", execution_start, success=False, details={**trade_details, "error": error_msg})

            log_trade("FAILED", symbol, {
                **trade_details,
                "error": error_msg,
                "success": False
            })

            self.error(f"❌ {action} order failed: {error_msg}", trade_details)

        return success

    def simulate_risk_management(self, symbol: str, position_size: float):
        """Simulate risk management with logging"""
        portfolio_value = random.uniform(10000, 50000)
        positions = {symbol: position_size}
        pnl = random.uniform(-500, 500)

        log_portfolio(portfolio_value, positions, pnl)

        risk_score = random.uniform(0, 1)

        if risk_score > 0.8:
            log_risk("HIGH_RISK_DETECTED", "HIGH", {
                "symbol": symbol,
                "position_size": position_size,
                "portfolio_value": portfolio_value,
                "risk_score": risk_score,
                "recommendation": "REDUCE_POSITION"
            })

            self.warning(f"⚠️ High risk detected for {symbol}", {
                "risk_score": risk_score,
                "position_size": position_size,
                "portfolio_percentage": (position_size * 100) / portfolio_value
            })

        elif risk_score > 0.6:
            log_risk("MEDIUM_RISK_ALERT", "MEDIUM", {
                "symbol": symbol,
                "risk_score": risk_score,
                "monitoring_required": True
            })

        return risk_score


async def demo_enhanced_base_agent():
    """Demonstrate the enhanced BaseAgent capabilities"""
    print("🤖 DEMONSTRATION: Enhanced BaseAgent with 100% Visibility Logging")
    print("=" * 80)

    agent = DemoTradingAgent()

    try:
        agent.start()

        symbols = ["BTC", "ETH", "SOL", "MATIC", "AVAX"]

        for i in range(5):
            symbol = random.choice(symbols)
            action = random.choice(["BUY", "SELL"])

            print(f"\n🔄 Operation {i+1}: Simulating {action} for {symbol}")

            success = agent.simulate_trade_execution(symbol, action)

            if success:
                agent.simulate_risk_management(symbol, random.uniform(100, 1000))

            if i % 2 == 0:
                status = agent.get_status()
                print(f"\n📊 Agent Status:")
                print(f"   Operations: {status['metrics']['operations_completed']}")
                print(f"   Errors: {status['metrics']['errors_encountered']}")
                print(f"   Success Rate: {status['performance']['success_rate']:.1f}%")

            time.sleep(1)

        health = agent.health_check()
        print(f"\n🏥 Agent Health: {health['status']}")
        if health['issues']:
            print(f"   Issues: {health['issues']}")

        agent.stop()

    except Exception as e:
        agent.error(f"Demo failed: {e}", exc_info=True)


async def demo_expert_logging_direct():
    """Demonstrate direct expert logging system usage"""
    print("\n\n📝 DEMONSTRATION: Expert Logging System Direct Usage")
    print("=" * 80)

    logger = get_logger("demo.direct")

    logger.critical("🚨 CRITICAL: System critical event", {
        "event_type": "system_alert",
        "severity": "maximum",
        "action_required": True
    })

    logger.error("❌ ERROR: Operation failed", {
        "operation": "api_call",
        "error_code": 500,
        "retry_count": 3
    })

    logger.warning("⚠️ WARNING: Market volatility high", {
        "symbol": "BTC",
        "volatility": 0.05,
        "recommended_action": "reduce_position_size"
    })

    logger.info("ℹ️ INFO: Strategy update", {
        "strategy_name": "momentum_based",
        "version": "2.1",
        "parameters_updated": True
    })

    logger.success("✅ SUCCESS: Trade executed", {
        "symbol": "ETH",
        "action": "BUY",
        "size": 1.5,
        "price": 2850.75
    })

    logger.debug("🐛 DEBUG: Processing data", {
        "data_points": 1000,
        "processing_time_ms": 45,
        "memory_usage_mb": 128
    })

    logger.trade("BUY", "BTC", {
        "order_id": "DEMO_BTC_001",
        "size": 0.5,
        "price": 45000.0,
        "value_usd": 22500.0,
        "exchange": "HyperLiquid",
        "real_money": False
    })

    logger.agent_lifecycle("START", "StrategyAgent", {
        "agent_id": "strategy_001",
        "config": {"risk_level": "medium", "max_positions": 5},
        "start_time": time.time()
    })

    logger.risk_alert("POSITION_SIZE_LIMIT", "HIGH", {
        "symbol": "SOL",
        "current_size": 5000,
        "limit_size": 3000,
        "excess_amount": 2000,
        "action": "REDUCE_POSITION"
    })

    logger.performance("market_analysis", 0.125, {
        "symbol": "MATIC",
        "indicators": ["RSI", "MACD", "BB"],
        "data_points_processed": 500,
        "cache_hit": True
    })

    logger.portfolio_update(50000.0, {"BTC": 15000, "ETH": 10000, "USDC": 25000}, 2500.0)

    print("✅ Direct expert logging demonstration completed!")


async def demo_trade_simulation():
    """Demonstrate comprehensive trade simulation"""
    print("\n\n💰 DEMONSTRATION: Complete Trade Simulation with Logging")
    print("=" * 80)

    trades = [
        {"symbol": "BTC", "action": "BUY", "size": 0.1, "price": 45000},
        {"symbol": "ETH", "action": "BUY", "size": 1.5, "price": 2850},
        {"symbol": "SOL", "action": "SELL", "size": 10.0, "price": 105},
        {"symbol": "MATIC", "action": "BUY", "size": 100.0, "price": 0.85},
        {"symbol": "AVAX", "action": "SELL", "size": 5.0, "price": 38.5}
    ]

    portfolio_value = 50000.0
    positions = {}
    total_pnl = 0.0

    for i, trade in enumerate(trades):
        symbol = trade["symbol"]
        action = trade["action"]
        size = trade["size"]
        price = trade["price"]
        value = size * price

        print(f"\n💼 Trade {i+1}: {action} {size} {symbol} @ ${price}")

        log_trade("ORDER_PLACED", symbol, {
            "action": action,
            "size": size,
            "price": price,
            "value_usd": value,
            "session_id": f"DEMO_SESSION_{int(time.time())}",
            "trade_number": i + 1
        })

        await asyncio.sleep(0.1)

        if random.random() > 0.1:
            log_trade("EXECUTED", symbol, {
                "action": action,
                "size": size,
                "price": price,
                "value_usd": value,
                "execution_time_ms": random.uniform(50, 200),
                "order_id": f"EXEC_{int(time.time()*1000)}_{i}",
                "success": True
            })

            if symbol not in positions:
                positions[symbol] = 0

            if action == "BUY":
                positions[symbol] += value
                portfolio_value -= value
            else:
                positions[symbol] -= value
                portfolio_value += value

            pnl_change = random.uniform(-100, 100)
            total_pnl += pnl_change

            print(f"   ✅ Executed successfully")
            print(f"   💰 Value: ${value:,.2f}")
            print(f"   📊 Portfolio: ${portfolio_value:,.2f}")

        else:
            log_trade("FAILED", symbol, {
                "action": action,
                "size": size,
                "price": price,
                "error": "Insufficient liquidity",
                "success": False
            })

            print(f"   ❌ Trade failed: Insufficient liquidity")

        if (i + 1) % 2 == 0:
            log_portfolio(portfolio_value, positions, total_pnl)

        await asyncio.sleep(0.2)

    log_portfolio(portfolio_value, positions, total_pnl)

    print(f"\n📊 Final Portfolio Summary:")
    print(f"   💰 Total Value: ${portfolio_value:,.2f}")
    print(f"   📈 Total P&L: ${total_pnl:,.2f}")
    print(f"   🏦 Positions: {len([p for p in positions.values() if p != 0])}")


async def main():
    """Main demo function"""
    print("🚀 NOVAQUOTE LOGGING SYSTEM - COMPLETE DEMONSTRATION")
    print("=" * 80)
    print("100% Visibility Platform - Expert Trading Operations")
    print("Built by Moon Dev - Professional Trading Solutions")
    print("=" * 80)

    try:
        await demo_enhanced_base_agent()

        await demo_expert_logging_direct()

        await demo_trade_simulation()

        print("\n\n🎉 NOVAQUOTE LOGGING SYSTEM DEMO COMPLETED!")
        print("=" * 80)
        print("✅ Expert logging: 100% visibility achieved")
        print("✅ Trade tracking: Complete transaction monitoring")
        print("✅ Risk management: Real-time risk alerts")
        print("✅ Agent monitoring: Full lifecycle tracking")
        print("✅ Performance metrics: Detailed analytics")
        print("\n📁 Check the 'logs/' directory for structured log files:")
        print("   - logs/novaquote.log (main logs)")
        print("   - logs/trades/ (trade-specific logs)")
        print("   - logs/agents/ (agent lifecycle logs)")
        print("   - logs/risk/ (risk management logs)")
        print("   - logs/errors/ (error tracking logs)")
        print("   - logs/performance/ (performance metrics)")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())