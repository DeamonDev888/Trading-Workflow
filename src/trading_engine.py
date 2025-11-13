"""
🚀 NOVAQUOTE Trading Engine
Built with love by Deamon Dev
Active trading signal execution and position management
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from termcolor import cprint

from src.exchange_manager import HyperLiquidExchangeManager
from src.agents.risk_agent import RiskAgent
from src.agents.strategy_agent import StrategyAgent
from src.agents.funding_agent import FundingAgent
from src.user_identity import get_user_identity, log_user_trade, log_agent_action


class SignalType(Enum):
    """Types of trading signals"""
    BUY = "BUY"
    SELL = "SELL"
    CLOSE_LONG = "CLOSE_LONG"
    CLOSE_SHORT = "CLOSE_SHORT"
    HEDGE = "HEDGE"


class SignalStrength(Enum):
    """Signal strength levels"""
    WEAK = 0.3
    MODERATE = 0.6
    STRONG = 0.8
    VERY_STRONG = 1.0


@dataclass
class TradingSignal:
    """Trading signal data structure"""
    symbol: str
    signal_type: SignalType
    strength: float
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    size: Optional[float] = None
    reason: str = ""
    timestamp: float = None
    confidence: float = 0.5
    strategy_name: str = ""

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class NOVAQUOTETradingEngine:
    """
    Advanced trading engine for NOVAQUOTE system
    Combines strategy signals with risk management and active execution
    """

    def __init__(self, testnet: bool = False, paper_trading: bool = True):
        """Initialize the trading engine"""
        self.name = "NOVAQUOTE Trading Engine"
        self.version = "3.0.0"

        self.testnet = testnet
        self.paper_trading = paper_trading  # Safety first!

        # User identity management
        self.user_identity = get_user_identity()

        # Initialize components
        self.exchange_manager = None
        self.risk_agent = RiskAgent()
        self.strategy_agent = StrategyAgent()
        self.funding_agent = FundingAgent()

        # Signal management
        self.active_signals: List[TradingSignal] = []
        self.executed_signals: List[TradingSignal] = []
        self.signal_history: List[Dict[str, Any]] = []

        # Position tracking
        self.active_positions: Dict[str, Dict[str, Any]] = {}
        self.max_positions = 5
        self.max_position_size_usd = 1000

        # Risk management
        self.max_daily_loss = 100  # USD
        self.daily_pnl = 0
        self.last_reset_date = datetime.now().date()

        # Configuration
        self.min_signal_strength = 0.6
        self.signal_timeout = 300  # 5 minutes

        cprint(f"🚀 {self.name} v{self.version} initialized", "cyan")
        cprint(f"   Mode: {'PAPER TRADING' if paper_trading else 'LIVE TRADING'}", "yellow" if paper_trading else "red")
        cprint(f"   Testnet: {self.testnet}", "cyan")

        # Log engine initialization with user context
        log_agent_action(
            agent_name="TradingEngine",
            action="initialized",
            version=self.version,
            mode='paper_trading' if paper_trading else 'live_trading',
            testnet=self.testnet
        )

    async def initialize(self):
        """Initialize async components"""
        try:
            cprint("🔧 Initializing trading engine components...", "yellow")

            # Initialize exchange manager
            self.exchange_manager = HyperLiquidExchangeManager(testnet=self.testnet)
            await self.exchange_manager.__aenter__()

            # Health check
            if not await self.exchange_manager.health_check():
                raise Exception("Exchange manager health check failed")

            cprint("✅ Trading engine initialized successfully!", "green")

        except Exception as e:
            cprint(f"❌ Failed to initialize trading engine: {e}", "red")
            raise

    async def generate_trading_signals(self) -> List[TradingSignal]:
        """
        Generate trading signals from all agents

        Returns:
            List of valid trading signals
        """
        try:
            signals = []

            # Get strategy signals
            cprint("📊 Generating strategy signals...", "blue")
            strategy_signals = await self._get_strategy_signals()
            signals.extend(strategy_signals)

            # Get funding arbitrage signals
            cprint("💰 Generating funding arbitrage signals...", "blue")
            funding_signals = await self._get_funding_signals()
            signals.extend(funding_signals)

            # Filter and validate signals
            valid_signals = await self._validate_signals(signals)

            cprint(f"🎯 Generated {len(valid_signals)} valid signals", "green")
            return valid_signals

        except Exception as e:
            cprint(f"❌ Error generating signals: {e}", "red")
            return []

    async def _get_strategy_signals(self) -> List[TradingSignal]:
        """Get signals from strategy agent"""
        try:
            # Get volatile signals from strategy agent
            volatile_signals = await self.strategy_agent.get_volatile_signals(
                min_volatility=0.02,
                max_assets=8
            )

            signals = []
            for signal_data in volatile_signals:
                if isinstance(signal_data, dict):
                    signal = TradingSignal(
                        symbol=signal_data.get('symbol', ''),
                        signal_type=SignalType.BUY if signal_data.get('action') == 'BUY' else SignalType.SELL,
                        strength=signal_data.get('confidence', 0.5),
                        reason=signal_data.get('reason', ''),
                        strategy_name=signal_data.get('strategy', 'unknown'),
                        confidence=signal_data.get('confidence', 0.5)
                    )
                    signals.append(signal)

            return signals

        except Exception as e:
            cprint(f"⚠️ Error getting strategy signals: {e}", "yellow")
            return []

    async def _get_funding_signals(self) -> List[TradingSignal]:
        """Get funding arbitrage signals"""
        try:
            signals = []

            # Get current funding data
            funding_data = self.funding_agent._get_current_funding()
            if funding_data is None or funding_data.empty:
                return signals

            # Look for high funding rate opportunities
            for _, row in funding_data.iterrows():
                symbol = row.get('symbol', '')
                annual_rate = row.get('annual_rate', 0)

                # High positive funding = short opportunity
                if annual_rate > 0.05:  # >5% annual
                    signal = TradingSignal(
                        symbol=symbol,
                        signal_type=SignalType.SELL,
                        strength=min(annual_rate / 0.2, 1.0),  # Scale to max 1.0
                        reason=f"High funding rate: {annual_rate:.2%} annual",
                        strategy_name="Funding_Arbitrage",
                        confidence=0.7
                    )
                    signals.append(signal)

                # High negative funding = long opportunity
                elif annual_rate < -0.05:  # <-5% annual
                    signal = TradingSignal(
                        symbol=symbol,
                        signal_type=SignalType.BUY,
                        strength=min(abs(annual_rate) / 0.2, 1.0),
                        reason=f"Negative funding rate: {annual_rate:.2%} annual",
                        strategy_name="Funding_Arbitrage",
                        confidence=0.7
                    )
                    signals.append(signal)

            return signals

        except Exception as e:
            cprint(f"⚠️ Error getting funding signals: {e}", "yellow")
            return []

    async def _validate_signals(self, signals: List[TradingSignal]) -> List[TradingSignal]:
        """Validate and filter trading signals"""
        valid_signals = []

        for signal in signals:
            # Check signal strength
            if signal.strength < self.min_signal_strength:
                cprint(f"❌ Weak signal for {signal.symbol}: {signal.strength:.2f} < {self.min_signal_strength}", "red")
                continue

            # Check risk limits
            if not await self._check_risk_limits(signal):
                cprint(f"❌ Risk limits exceeded for {signal.symbol}", "red")
                continue

            # Check if we already have position
            if signal.symbol in self.active_positions:
                # Only allow signals that would reduce or close existing position
                existing_pos = self.active_positions[signal.symbol]
                if not self._is_closing_signal(signal, existing_pos):
                    cprint(f"⚠️ Position already exists for {signal.symbol}", "yellow")
                    continue

            # Calculate position size
            signal.size = await self._calculate_position_size(signal)
            if signal.size <= 0:
                cprint(f"❌ Invalid position size for {signal.symbol}", "red")
                continue

            valid_signals.append(signal)
            cprint(f"✅ Valid signal: {signal.symbol} {signal.signal_type.value} @ strength {signal.strength:.2f}", "green")

        return valid_signals

    async def _check_risk_limits(self, signal: TradingSignal) -> bool:
        """Check if signal respects risk limits"""
        try:
            # Check daily loss limit
            if self.daily_pnl < -self.max_daily_loss:
                cprint(f"❌ Daily loss limit exceeded: ${self.daily_pnl:.2f}", "red")
                return False

            # Check position count
            if len(self.active_positions) >= self.max_positions:
                cprint(f"❌ Max positions reached: {len(self.active_positions)}", "red")
                return False

            # Get portfolio value from risk agent
            portfolio_value = self.risk_agent.get_portfolio_value()
            if portfolio_value < 100:  # Minimum portfolio value
                cprint(f"❌ Portfolio value too low: ${portfolio_value:.2f}", "red")
                return False

            return True

        except Exception as e:
            cprint(f"⚠️ Error checking risk limits: {e}", "yellow")
            return False

    def _is_closing_signal(self, signal: TradingSignal, position: Dict[str, Any]) -> bool:
        """Check if signal would close existing position"""
        pos_side = position.get('side', '')
        signal_side = signal.signal_type.value

        # Buy signal closes short position
        if pos_side == 'short' and signal_side == 'BUY':
            return True

        # Sell signal closes long position
        if pos_side == 'long' and signal_side == 'SELL':
            return True

        return False

    async def _calculate_position_size(self, signal: TradingSignal) -> float:
        """Calculate optimal position size for signal"""
        try:
            # Get current price
            if self.exchange_manager:
                token_data = await self.exchange_manager.get_token_data(signal.symbol)
                if token_data:
                    current_price = token_data.get('price', 0)
                else:
                    current_price = 0
            else:
                current_price = 0

            if current_price <= 0:
                return 0

            # Base position size on signal strength and risk
            risk_factor = min(signal.strength * signal.confidence, 1.0)
            base_size_usd = self.max_position_size_usd * risk_factor

            # Convert to token amount
            position_size = base_size_usd / current_price

            return max(position_size, 0.001)  # Minimum size

        except Exception as e:
            cprint(f"⚠️ Error calculating position size: {e}", "yellow")
            return 0

    async def execute_signals(self, signals: List[TradingSignal]) -> List[Dict[str, Any]]:
        """
        Execute trading signals

        Args:
            signals: List of signals to execute

        Returns:
            List of execution results
        """
        results = []

        for signal in signals:
            try:
                result = await self._execute_single_signal(signal)
                results.append(result)

                # Add to active positions if successful
                if result.get('success') and signal.signal_type in [SignalType.BUY, SignalType.SELL]:
                    self.active_positions[signal.symbol] = {
                        'side': 'long' if signal.signal_type == SignalType.BUY else 'short',
                        'size': signal.size,
                        'entry_price': result.get('executed_price', signal.entry_price),
                        'timestamp': signal.timestamp,
                        'signal': signal
                    }

                # Update signal lists
                self.active_signals.remove(signal) if signal in self.active_signals else None
                self.executed_signals.append(signal)

            except Exception as e:
                cprint(f"❌ Error executing signal for {signal.symbol}: {e}", "red")
                results.append({
                    'symbol': signal.symbol,
                    'success': False,
                    'error': str(e),
                    'timestamp': time.time()
                })

        return results

    async def _execute_single_signal(self, signal: TradingSignal) -> Dict[str, Any]:
        """Execute a single trading signal"""
        try:
            cprint(f"🎯 Executing {signal.signal_type.value} signal for {signal.symbol}", "blue")

            if self.paper_trading:
                # Simulate execution
                cprint(f"📋 PAPER TRADING: {signal.signal_type.value} {signal.size} {signal.symbol}", "yellow")

                # Get current price for simulation
                if self.exchange_manager:
                    token_data = await self.exchange_manager.get_token_data(signal.symbol)
                    executed_price = token_data.get('price', signal.entry_price or 0)
                else:
                    executed_price = signal.entry_price or 100.0

                # Create order ID
                order_id = f"paper_{int(time.time())}"

                # Log trade with user identification
                log_user_trade(
                    symbol=signal.symbol,
                    side=signal.signal_type.value,
                    size=signal.size,
                    price=executed_price,
                    order_id=order_id,
                    strategy=signal.strategy_name,
                    trade_type='paper_trading',
                    signal_strength=signal.strength
                )

                return {
                    'symbol': signal.symbol,
                    'success': True,
                    'executed_price': executed_price,
                    'executed_size': signal.size,
                    'type': 'paper_trading',
                    'timestamp': time.time(),
                    'order_id': order_id
                }

            else:
                # Real execution
                side = 'B' if signal.signal_type == SignalType.BUY else 'S'
                order_type = 'market'  # Use market orders for active trading

                result = await self.exchange_manager.place_order(
                    symbol=signal.symbol,
                    side=side,
                    order_type=order_type,
                    size=signal.size,
                    price=signal.entry_price
                )

                if result:
                    cprint(f"✅ Order executed: {result.get('order_id', 'unknown')}", "green")
                    return {
                        'symbol': signal.symbol,
                        'success': True,
                        'executed_price': result.get('price', signal.entry_price),
                        'executed_size': signal.size,
                        'order_id': result.get('order_id'),
                        'timestamp': time.time()
                    }
                else:
                    raise Exception("Order execution failed")

        except Exception as e:
            cprint(f"❌ Execution failed for {signal.symbol}: {e}", "red")
            return {
                'symbol': signal.symbol,
                'success': False,
                'error': str(e),
                'timestamp': time.time()
            }

    async def manage_positions(self):
        """Manage active positions - stop losses, take profits, etc."""
        try:
            if not self.active_positions:
                return

            cprint(f"📊 Managing {len(self.active_positions)} active positions...", "blue")

            for symbol, position in list(self.active_positions.items()):
                try:
                    # Get current price
                    if self.exchange_manager:
                        token_data = await self.exchange_manager.get_token_data(symbol)
                        current_price = token_data.get('price', 0)
                    else:
                        current_price = 0

                    if current_price <= 0:
                        continue

                    entry_price = position.get('entry_price', 0)
                    side = position.get('side', '')
                    size = position.get('size', 0)

                    if entry_price <= 0 or size <= 0:
                        continue

                    # Calculate P&L
                    if side == 'long':
                        pnl_pct = (current_price - entry_price) / entry_price
                    else:  # short
                        pnl_pct = (entry_price - current_price) / entry_price

                    # Check exit conditions
                    should_exit = False
                    exit_reason = ""

                    # Stop loss (5%)
                    if pnl_pct < -0.05:
                        should_exit = True
                        exit_reason = "Stop loss triggered"

                    # Take profit (15%)
                    elif pnl_pct > 0.15:
                        should_exit = True
                        exit_reason = "Take profit triggered"

                    # Time-based exit (24 hours)
                    elif time.time() - position.get('timestamp', 0) > 86400:
                        should_exit = True
                        exit_reason = "Time exit"

                    if should_exit:
                        cprint(f"🚪 Exiting {symbol} position: {exit_reason} (P&L: {pnl_pct:.2%})", "yellow")

                        # Create exit signal
                        exit_signal = TradingSignal(
                            symbol=symbol,
                            signal_type=SignalType.SELL if side == 'long' else SignalType.BUY,
                            strength=1.0,
                            size=size,
                            reason=exit_reason,
                            strategy_name="Position_Management",
                            confidence=1.0
                        )

                        # Execute exit
                        result = await self._execute_single_signal(exit_signal)
                        if result.get('success'):
                            # Update daily P&L
                            self.daily_pnl += pnl_pct * size * entry_price

                            # Remove from active positions
                            del self.active_positions[symbol]

                            cprint(f"✅ Exited {symbol} position successfully", "green")

                except Exception as e:
                    cprint(f"❌ Error managing {symbol} position: {e}", "red")

        except Exception as e:
            cprint(f"❌ Error in position management: {e}", "red")

    async def run_trading_cycle(self):
        """Run one complete trading cycle"""
        try:
            cprint("🚀 Starting trading cycle...", "blue")

            # Reset daily P&L if new day
            if datetime.now().date() > self.last_reset_date:
                self.daily_pnl = 0
                self.last_reset_date = datetime.now().date()
                cprint("📅 Daily P&L reset", "green")

            # Step 1: Generate signals
            signals = await self.generate_trading_signals()
            self.active_signals.extend(signals)

            # Step 2: Execute signals
            if signals:
                cprint(f"⚡ Executing {len(signals)} signals...", "yellow")
                results = await self.execute_signals(signals)

                # Log results
                for result in results:
                    if result.get('success'):
                        cprint(f"✅ {result['symbol']}: Order executed", "green")
                    else:
                        cprint(f"❌ {result['symbol']}: {result.get('error', 'Unknown error')}", "red")

            # Step 3: Manage positions
            await self.manage_positions()

            # Step 4: Update statistics
            await self._update_statistics()

            cprint("✅ Trading cycle completed", "green")

        except Exception as e:
            cprint(f"❌ Trading cycle failed: {e}", "red")

    async def run_continuous(self, cycle_interval: int = 60):
        """Run trading engine continuously"""
        try:
            cprint(f"🔄 Starting continuous trading (interval: {cycle_interval}s)...", "blue")

            while True:
                try:
                    await self.run_trading_cycle()
                    cprint(f"💤 Waiting {cycle_interval}s for next cycle...", "cyan")
                    await asyncio.sleep(cycle_interval)

                except KeyboardInterrupt:
                    cprint("\n🛑 Trading engine stopped by user", "yellow")
                    break
                except Exception as e:
                    cprint(f"❌ Error in trading cycle: {e}", "red")
                    cprint("⏳ Waiting 30s before retry...", "yellow")
                    await asyncio.sleep(30)

        except Exception as e:
            cprint(f"❌ Fatal error in continuous trading: {e}", "red")

    async def _update_statistics(self):
        """Update trading statistics"""
        try:
            stats = {
                'timestamp': time.time(),
                'active_positions': len(self.active_positions),
                'daily_pnl': self.daily_pnl,
                'signals_generated': len(self.active_signals),
                'signals_executed': len(self.executed_signals),
                'portfolio_value': self.risk_agent.get_portfolio_value()
            }

            self.signal_history.append(stats)

            # Keep only last 1000 records
            if len(self.signal_history) > 1000:
                self.signal_history = self.signal_history[-1000:]

            cprint(f"📊 Stats: {len(self.active_positions)} positions, P&L: ${self.daily_pnl:.2f}", "blue")

        except Exception as e:
            cprint(f"⚠️ Error updating statistics: {e}", "yellow")

    def get_status(self) -> Dict[str, Any]:
        """Get current engine status"""
        return {
            'name': self.name,
            'version': self.version,
            'mode': 'paper_trading' if self.paper_trading else 'live_trading',
            'testnet': self.testnet,
            'active_positions': len(self.active_positions),
            'active_signals': len(self.active_signals),
            'daily_pnl': self.daily_pnl,
            'max_positions': self.max_positions,
            'portfolio_value': self.risk_agent.get_portfolio_value(),
            'last_reset': self.last_reset_date.isoformat(),
            'health': 'healthy'
        }

    async def shutdown(self):
        """Shutdown the trading engine"""
        try:
            cprint("🛑 Shutting down trading engine...", "yellow")

            # Close all positions if not paper trading
            if not self.paper_trading and self.active_positions:
                cprint("⚠️ Emergency position closing!", "red")
                # Implementation for emergency closing

            # Close exchange manager
            if self.exchange_manager:
                await self.exchange_manager.close()

            cprint("✅ Trading engine shutdown complete", "green")

        except Exception as e:
            cprint(f"❌ Error during shutdown: {e}", "red")


# Factory function
async def create_trading_engine(testnet: bool = False, paper_trading: bool = True) -> NOVAQUOTETradingEngine:
    """Create and initialize a trading engine"""
    engine = NOVAQUOTETradingEngine(testnet=testnet, paper_trading=paper_trading)
    await engine.initialize()
    return engine
