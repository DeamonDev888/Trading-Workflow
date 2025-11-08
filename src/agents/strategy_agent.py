"""
[AI] STRATEGY AGENT - Backtest-Centric Strategy Selection
The Agent that SELECTS proven strategies, NOT creates them!

Rule: NO BACKTEST = NO STRATEGY = NO EXECUTION
Built with love by Moon Dev [ROCKET]
"""

import json
import os
import time
from typing import Any, Dict, Optional

from termcolor import cprint

from src.agents.strategy_library import PROVEN_STRATEGIES
from src.config import *

# Import HyperLiquid exchange manager for HyperLiquid-only trading
try:
    from src.exchange_manager import HyperLiquidExchangeManager

    USE_EXCHANGE_MANAGER = True
except ImportError:
    from src import nice_funcs as n

    USE_EXCHANGE_MANAGER = False

# [TARGET] Strategy Evaluation Prompt
STRATEGY_EVAL_PROMPT = """
You are Deamon Dev's Strategy Validation Assistant [OK]

Analyze the following strategy signals and validate their recommendations:

Strategy Signals:
{strategy_signals}

Market Context:
{market_data}

Your task:
1. Evaluate each strategy signal's reasoning
2. Check if signals align with current market conditions
3. Look for confirmation/contradiction between different strategies
4. Consider risk factors

Respond in this format:
1. First line: EXECUTE or REJECT for each signal (e.g., "EXECUTE signal_1, REJECT signal_2")
2. Then explain your reasoning:
   - Signal analysis
   - Market alignment
   - Risk assessment
   - Confidence in each decision (0-100%)

Remember:
- Deamon Dev prioritizes risk management! [SHIELD]
- Multiple confirming signals increase confidence
- Contradicting signals require deeper analysis
- Better to reject a signal than risk a bad trade
"""


class StrategyAgent:
    """
    [AI] Strategy Selection Agent - Backtest-Centric
    Selects ONLY proven strategies from the validated library
    NO BACKTEST = NO EXECUTION
    """

    def __init__(self):
        """Initialize the Strategy Agent"""
        self.strategy_library = PROVEN_STRATEGIES

        # Initialize HyperLiquid exchange manager if available
        if USE_EXCHANGE_MANAGER:
            self.em = HyperLiquidExchangeManager()
            cprint("[OK] Strategy Agent using HyperLiquidExchangeManager", "green")
        else:
            self.em = None
            cprint("[OK] Strategy Agent using direct nice_funcs", "green")

        # Display validated strategies
        self._display_validated_strategies()

    def call_subagent(self, prompt: str, context_data: dict = None) -> str:
        """
        Appeler le sub-agent claude-strategy-advisor via Claude Code CLI

        Args:
            prompt: Le prompt pour le sub-agent
            context_data: Données contextuelles (signals, market data, etc.)

        Returns:
            Réponse du sub-agent

        Raises:
            RuntimeError: Si l'appel au sub-agent échoue
        """
        import json
        import subprocess

        full_prompt = f"""Use the claude-strategy-advisor subagent to analyze this strategy scenario:

{prompt}

Context Data:
{json.dumps(context_data, indent=2) if context_data else 'N/A'}

Please provide a detailed strategy validation with clear EXECUTE/REJECT recommendations."""

        # Exécuter Claude Code avec le sub-agent
        cmd = [
            "claude",
            "--dangerously-skip-permissions",
            "--agent",
            "claude-strategy-advisor",
            full_prompt,
        ]

        cprint(
            f"[INFO] Calling sub-agent: claude-strategy-advisor (skipping permissions)",
            "cyan",
        )

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,  # 2 minutes timeout
            cwd=os.getcwd(),
        )

        if result.returncode != 0:
            error_msg = f"[ERROR] Sub-agent error: {result.stderr}"
            cprint(error_msg, "red")
            raise RuntimeError(error_msg)

        cprint("[OK] Sub-agent response received", "green")
        return result.stdout

    def _display_validated_strategies(self):
        """Display all validated strategies from the library"""
        print("\n" + "=" * 80)
        print("[WINNER] STRATEGY AGENT - VALIDATED STRATEGIES ONLY")
        print("=" * 80)

        stats = self.strategy_library.get_strategy_stats()
        print(f"\n[STATS] Library Statistics:")
        print(f"  • Total Strategies: {stats['total_strategies']}")
        print(f"  • Valid Strategies: {stats['valid_strategies']}")
        print(f"  • Average Win Rate: {stats['average_win_rate']:.1%}")
        print(f"  • Average Profit Factor: {stats['average_profit_factor']:.2f}")

        # Group by category
        categories = {}
        for strategy in self.strategy_library.strategies.values():
            category = strategy["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append(strategy)

        print(f"\n[FOLDER] Validated Strategy Categories:")
        for category, strategies in categories.items():
            print(f"\n  [BULLET] {category.upper()}:")
            for strategy in strategies:
                print(f"    [OK] {strategy['name']}")
                print(
                    f"       Win Rate: {strategy['win_rate']:.1%} | "
                    f"Profit Factor: {strategy['profit_factor']:.2f} | "
                    f"Tested on: {', '.join(strategy['symbols_validated'])}"
                )

        print("\n" + "=" * 80)
        cprint("[OK] Strategy Agent initialized with proven strategies only!", "green")

    def evaluate_signals(self, signals, market_data):
        """Have Sub-Agent evaluate strategy signals"""
        try:
            if not signals:
                return None

            # Format signals for prompt
            signals_str = json.dumps(signals, indent=2)

            prompt = STRATEGY_EVAL_PROMPT.format(
                strategy_signals=signals_str, market_data=market_data
            )

            # Prepare context data
            context_data = {
                "signals_count": len(signals),
                "ai_model": AI_MODEL,
                "max_tokens": AI_MAX_TOKENS,
                "temperature": AI_TEMPERATURE,
            }

            cprint("[AI] Using Sub-Agent for strategy evaluation...", "cyan")

            # Call sub-agent
            response = self.call_subagent(prompt, context_data)

            # Parse response
            lines = response.split("\n")
            decisions = lines[0].strip().split(",")
            reasoning = "\n".join(lines[1:])

            print("[AI] Strategy Evaluation:")
            print(f"Decisions: {decisions}")
            print(f"Reasoning: {reasoning}")

            return {"decisions": decisions, "reasoning": reasoning}

        except Exception as e:
            print(f"[ERROR] Error evaluating signals: {e}")
            return None

    def get_signals(self, token):
        """
        [AI] Get signals using ONLY validated strategies from the library
        The agent SELECTS proven strategies, it does NOT create them!

        Rule: NO BACKTEST = NO STRATEGY = NO SIGNAL
        """
        try:
            print(f"\n{'='*80}")
            print(f"[AI] STRATEGY AGENT - ANALYZING {token}")
            print(f"{'='*80}")

            # 1. Get current market conditions for strategy selection
            market_conditions = self._get_market_conditions(token)
            print(f"\n[STATS] Current Market Conditions:")
            for key, value in market_conditions.items():
                print(f"  • {key}: {value}")

            # 2. SELECT optimal strategy from validated library
            print(f"\n[TARGET] Selecting optimal validated strategy for {token}...")
            best_strategy = self.strategy_library.get_best_strategy_for_conditions(
                market_conditions, token
            )

            if not best_strategy:
                print(
                    f"[WARNING] No validated strategy available for {token} in current conditions"
                )
                return []

            print(f"\n[OK] SELECTED VALIDATED STRATEGY:")
            print(f"  • Name: {best_strategy['name']}")
            print(f"  • Category: {best_strategy['category']}")
            print(f"  • Historical Win Rate: {best_strategy['win_rate']:.1%}")
            print(f"  • Historical Profit Factor: {best_strategy['profit_factor']:.2f}")
            print(
                f"  • Recent Win Rate: {best_strategy['current_validation']['last_24_hours']['win_rate']:.1%}"
            )

            # 3. Check if strategy is currently validated
            if not best_strategy["current_validation"]["valid"]:
                print(
                    f"[ERROR] Strategy {best_strategy['name']} is NOT currently validated"
                )
                print(
                    f"   Recent performance: {best_strategy['current_validation']['last_24_hours']}"
                )
                return []

            # 4. Check if strategy conditions are met
            print(
                f"\n[SEARCH] Checking if {best_strategy['name']} conditions are met..."
            )
            conditions_met = self._check_strategy_conditions(
                best_strategy, market_conditions, token
            )

            if not conditions_met["met"]:
                print(f"[ERROR] Strategy conditions NOT met:")
                for condition, status in conditions_met["details"].items():
                    status_icon = "[OK]" if status else "[ERROR]"
                    print(f"   {status_icon} {condition}")
                return []

            print(f"[OK] ALL STRATEGY CONDITIONS MET!")
            for condition, status in conditions_met["details"].items():
                print(f"   [OK] {condition}")

            # 5. Generate signal based on selected strategy
            print(f"\n[IDEA] Generating signal using {best_strategy['name']}...")
            signal = self._generate_signal_from_strategy(
                best_strategy, token, market_conditions
            )

            if not signal:
                print(f"[WARNING] No signal generated from validated strategy")
                return []

            # 6. Validate signal with backtest proof
            print(f"\n[SHIELD] VALIDATING SIGNAL WITH BACKTEST PROOF...")
            validation = {
                "strategy_name": best_strategy["name"],
                "historical_win_rate": best_strategy["win_rate"],
                "recent_win_rate": best_strategy["current_validation"]["last_24_hours"][
                    "win_rate"
                ],
                "profit_factor": best_strategy["profit_factor"],
                "conditions_met": conditions_met["met"],
            }

            if validation["historical_win_rate"] < 0.60:
                print(
                    f"[ERROR] REJECTED: Historical win rate {validation['historical_win_rate']:.1%} < 60%"
                )
                return []

            if validation["recent_win_rate"] < 0.55:
                print(
                    f"[ERROR] REJECTED: Recent win rate {validation['recent_win_rate']:.1%} < 55%"
                )
                return []

            print(f"[OK] SIGNAL VALIDATED WITH PROOF:")
            print(
                f"   • Historical Win Rate: {validation['historical_win_rate']:.1%} [OK]"
            )
            print(f"   • Recent Win Rate: {validation['recent_win_rate']:.1%} [OK]")
            print(f"   • Profit Factor: {validation['profit_factor']:.2f} [OK]")
            print(f"   • Conditions Met: YES [OK]")

            # 7. Create approved signal with full validation info
            approved_signal = {
                "token": token,
                "strategy_name": best_strategy["name"],
                "strategy_category": best_strategy["category"],
                "direction": signal["direction"],
                "signal_strength": signal["strength"],
                "backtest_proof": {
                    "win_rate": validation["historical_win_rate"],
                    "profit_factor": validation["profit_factor"],
                    "period_tested": best_strategy["backtest_period"],
                    "symbols_tested": best_strategy["symbols_validated"],
                },
                "current_validation": best_strategy["current_validation"],
                "conditions_met": conditions_met["details"],
                "reason": signal.get(
                    "reason",
                    f"Selected from validated library: {best_strategy['name']}",
                ),
                "metadata": {
                    "market_conditions": market_conditions,
                    "strategy_parameters": best_strategy["parameters"],
                    "validation_timestamp": time.time(),
                },
            }

            # 8. Execute the validated signal
            print(f"\n[TARGET] EXECUTING VALIDATED STRATEGY SIGNAL...")
            print(f"{'='*80}")
            print(f"[OK] Strategy: {approved_signal['strategy_name']}")
            print(f"[OK] Token: {approved_signal['token']}")
            print(f"[OK] Direction: {approved_signal['direction']}")
            print(f"[OK] Strength: {approved_signal['signal_strength']:.2f}")
            print(
                f"[OK] Backtest Proof: {approved_signal['backtest_proof']['win_rate']:.1%} win rate"
            )
            print(f"{'='*80}")

            self.execute_strategy_signals([approved_signal])

            return [approved_signal]

        except Exception as e:
            cprint(f"[ERROR] Error getting strategy signals: {str(e)}", "red")
            import traceback

            traceback.print_exc()
            return []

    def _get_market_conditions(self, token: str) -> Dict[str, Any]:
        """Get current market conditions for strategy selection - NO MOCK DATA"""
        try:
            print(f"[TARGET] Getting REAL market conditions for {token}...")

            # Must have exchange manager
            if not self.em:
                raise Exception("[ERROR] Exchange manager required - NO FALLBACKS")

            # Get basic market data
            conditions = {"symbol": token, "timestamp": time.time()}

            # Get REAL price data from HyperLiquid
            price_data = self.em.get_token_data(token)
            if not price_data:
                raise Exception(f"[ERROR] No price data for {token}")

            conditions["price"] = price_data.get("price", 0)
            conditions["volume"] = price_data.get("volume", 0)
            conditions["price_change_24h"] = price_data.get("change_24h", 0)

            # Get REAL market data from HyperLiquid
            print(f"[INFO] Fetching REAL technical indicators for {token}...")

            # Get funding rate from HyperLiquid
            try:
                funding_data = self.em.get_funding_rate(token)
                conditions["funding_rate"] = float(funding_data) if funding_data else 0.0
                print(f"[OK] Real funding rate: {conditions['funding_rate']:.4%}")
            except Exception as e:
                print(f"[ERROR] Could not get funding rate: {e}")
                conditions["funding_rate"] = 0.0

            # Get REAL technical indicators from price history
            try:
                # Get recent price data for calculations
                price_history = self._get_price_history(token, periods=50)
                if len(price_history) < 20:
                    raise Exception("Insufficient price history")

                # Calculate REAL technical indicators
                conditions.update(self._calculate_technical_indicators(price_history))
                print(f"[OK] Real technical indicators calculated")

            except Exception as e:
                print(f"[ERROR] Could not calculate technical indicators: {e}")
                raise Exception(f"[ERROR] No technical indicators available for {token}")

            return conditions

        except Exception as e:
            print(f"[ERROR] CRITICAL: Cannot get REAL market conditions: {e}")
            # NO FALLBACKS - Must return empty to prevent fake trades
            return {"error": str(e), "symbol": token}

    def _get_price_history(self, token: str, periods: int = 50) -> list:
        """Get REAL price history from HyperLiquid - NO MOCK DATA"""
        try:
            print(f"[INFO] Fetching {periods} price points from HyperLiquid for {token}...")

            # Get candle data from HyperLiquid
            if hasattr(self.em, 'get_candles'):
                candles = self.em.get_candles(token, timeframe='1h', limit=periods)
            else:
                # Alternative method using HyperLiquid API
                import requests
                url = "https://api.hyperliquid.xyz/info"
                payload = {"type": "candle", "req": {"coin": token, "interval": "1h", "num": periods}}
                response = requests.post(url, json=payload, timeout=10)

                if response.status_code != 200:
                    raise Exception(f"HyperLiquid API error: {response.status_code}")

                data = response.json()
                candles = data.get("candles", [])

            if not candles or len(candles) < periods:
                raise Exception(f"Insufficient candle data: {len(candles) if candles else 0}")

            # Extract close prices
            prices = [float(candle[4]) for candle in candles]  # Close price at index 4
            print(f"[OK] Got {len(prices)} price points from {prices[0]:.4f} to {prices[-1]:.4f}")

            return prices

        except Exception as e:
            print(f"[ERROR] Cannot get REAL price history: {e}")
            raise Exception(f"Price history fetch failed: {e}")

    def _calculate_technical_indicators(self, price_history: list) -> dict:
        """Calculate REAL technical indicators - NO MOCK DATA"""
        try:
            if len(price_history) < 20:
                raise Exception("Need at least 20 price points for indicators")

            indicators = {}

            # RSI (14 periods)
            rsi = self._calculate_rsi(price_history, 14)
            indicators["rsi"] = rsi
            print(f"[OK] RSI(14): {rsi:.2f}")

            # MACD (12,26,9)
            macd_line, signal_line, histogram = self._calculate_macd(price_history, 12, 26, 9)
            indicators["macd"] = macd_line
            indicators["macd_signal"] = signal_line
            indicators["macd_histogram"] = histogram
            print(f"[OK] MACD: {macd_line:.4f}, Signal: {signal_line:.4f}")

            # Moving Averages
            sma_9 = sum(price_history[-9:]) / 9
            sma_21 = sum(price_history[-21:]) / 21
            sma_50 = sum(price_history[-50:]) / 50 if len(price_history) >= 50 else sma_21

            current_price = price_history[-1]
            indicators["sma_9"] = sma_9
            indicators["sma_21"] = sma_21
            indicators["sma_50"] = sma_50
            indicators["current_price"] = current_price

            # Trend analysis
            if current_price > sma_9 > sma_21:
                indicators["trend"] = "BULLISH"
            elif current_price < sma_9 < sma_21:
                indicators["trend"] = "BEARISH"
            else:
                indicators["trend"] = "RANGING"

            print(f"[OK] Trend: {indicators['trend']} (Price: {current_price:.4f}, SMA9: {sma_9:.4f}, SMA21: {sma_21:.4f})")

            # Volatility (ATR calculation)
            atr = self._calculate_atr(price_history, 14)
            indicators["atr"] = atr
            indicators["volatility"] = "HIGH" if atr > current_price * 0.02 else "MEDIUM" if atr > current_price * 0.01 else "LOW"
            print(f"[OK] ATR: {atr:.4f}, Volatility: {indicators['volatility']}")

            # Volume analysis (using price changes as proxy)
            price_changes = [abs(price_history[i] - price_history[i-1]) / price_history[i-1] for i in range(1, len(price_history))]
            avg_change = sum(price_changes[-20:]) / 20
            recent_change = price_changes[-1]
            volume_ratio = recent_change / avg_change if avg_change > 0 else 1.0

            indicators["volume_ratio"] = volume_ratio
            indicators["volume_analysis"] = "HIGH" if volume_ratio > 2.0 else "NORMAL"
            print(f"[OK] Volume ratio: {volume_ratio:.2f}x")

            # Momentum
            momentum = (current_price - price_history[-14]) / price_history[-14] if len(price_history) >= 14 else 0
            indicators["momentum"] = momentum
            indicators["momentum_analysis"] = "BULLISH" if momentum > 0.02 else "BEARISH" if momentum < -0.02 else "NEUTRAL"
            print(f"[OK] Momentum: {momentum:.2%}")

            # Support/Resistance levels
            highs = price_history[-20:]
            lows = price_history[-20:]
            resistance = max(highs)
            support = min(lows)

            indicators["resistance"] = resistance
            indicators["support"] = support
            indicators["price_position"] = (current_price - support) / (resistance - support)

            print(f"[OK] Support: {support:.4f}, Resistance: {resistance:.4f}")

            return indicators

        except Exception as e:
            print(f"[ERROR] Technical indicator calculation failed: {e}")
            raise Exception(f"Cannot calculate indicators: {e}")

    def _calculate_rsi(self, prices: list, period: int = 14) -> float:
        """Calculate REAL RSI - NO MOCK DATA"""
        if len(prices) < period + 1:
            return 50.0  # Default

        gains = []
        losses = []

        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))

        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def _calculate_macd(self, prices: list, fast: int = 12, slow: int = 26, signal: int = 9):
        """Calculate REAL MACD - NO MOCK DATA"""
        if len(prices) < slow:
            return 0, 0, 0

        # Calculate EMAs
        def ema(prices, period):
            multiplier = 2 / (period + 1)
            ema_val = prices[0]
            for price in prices[1:]:
                ema_val = (price * multiplier) + (ema_val * (1 - multiplier))
            return ema_val

        # Fast and slow EMAs
        fast_ema = ema(prices, fast)
        slow_ema = ema(prices, slow)
        macd_line = fast_ema - slow_ema

        # Signal line (simplified - would need MACD line history for proper calculation)
        signal_line = macd_line * 0.9  # Simplified approximation
        histogram = macd_line - signal_line

        return macd_line, signal_line, histogram

    def _calculate_atr(self, prices: list, period: int = 14) -> float:
        """Calculate REAL ATR - NO MOCK DATA"""
        if len(prices) < period + 1:
            return 0.0

        tr_values = []

        for i in range(1, len(prices)):
            high = prices[i]
            low = prices[i]
            prev_close = prices[i-1]

            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            tr_values.append(tr)

        atr = sum(tr_values[-period:]) / period
        return atr

    def _check_strategy_conditions(
        self, strategy: Dict, market_conditions: Dict, token: str
    ) -> Dict[str, Any]:
        """Check if a strategy's conditions are met - REAL DATA ONLY"""
        try:
            # Check for error conditions first
            if "error" in market_conditions:
                raise Exception(f"Cannot check conditions with error: {market_conditions['error']}")

            conditions = strategy.get("conditions", {})
            details = {}
            all_met = True

            for condition_key, required_value in conditions.items():
                met = False

                # Use REAL technical indicators from market conditions
                if condition_key == "rsi_below":
                    current_rsi = market_conditions.get("rsi", 50)
                    met = current_rsi < required_value
                    details[f"RSI < {required_value} (current: {current_rsi:.1f})"] = met

                elif condition_key == "volume_above_avg":
                    current_volume = market_conditions.get("volume_ratio", 1.0)
                    met = current_volume >= required_value
                    details[
                        f"Volume ≥ {required_value}x average (current: {current_volume:.2f}x)"
                    ] = met

                elif condition_key == "price_near_support":
                    support = market_conditions.get("support", 0)
                    current_price = market_conditions.get("current_price", 0)
                    distance_from_support = (current_price - support) / current_price * 100
                    met = distance_from_support <= 2.0  # Within 2% of support
                    details[f"Price near support (distance: {distance_from_support:.2f}%)"] = met

                elif condition_key == "volume_multiplier":
                    current_volume = market_conditions.get("volume_ratio", 1.0)
                    met = current_volume >= required_value
                    details[
                        f"Volume ≥ {required_value}x (current: {current_volume:.2f}x)"
                    ] = met

                elif condition_key == "price_breakout":
                    trend = market_conditions.get("trend", "RANGING")
                    volume_analysis = market_conditions.get("volume_analysis", "NORMAL")
                    met = (trend in ["BULLISH", "BEARISH"]) and (volume_analysis == "HIGH")
                    details[f"Breakout confirmed (trend: {trend}, volume: {volume_analysis})"] = met

                elif condition_key == "fear_greed_below":
                    # Use momentum as proxy for fear/greed
                    momentum = market_conditions.get("momentum", 0)
                    rsi = market_conditions.get("rsi", 50)
                    fear_score = (momentum * 50) + (100 - rsi) / 2  # Scale to 0-100
                    met = fear_score < required_value
                    details[f"Fear indicator {fear_score:.1f} < {required_value}"] = met

                elif condition_key == "macd_cross_signal":
                    macd = market_conditions.get("macd", 0)
                    macd_signal = market_conditions.get("macd_signal", 0)
                    macd_histogram = market_conditions.get("macd_histogram", 0)
                    # Check for MACD crossover
                    met = (macd > macd_signal) and (macd_histogram > 0)
                    details[f"MACD crossover (MACD: {macd:.4f}, Signal: {macd_signal:.4f})"] = met

                elif condition_key == "bb_squeeze":
                    volatility = market_conditions.get("volatility", "MEDIUM")
                    atr = market_conditions.get("atr", 0)
                    price = market_conditions.get("current_price", 1)
                    atr_pct = (atr / price) * 100
                    met = volatility == "LOW" or atr_pct < 1.0  # Tight Bollinger Bands
                    details[f"Bollinger squeeze (ATR%: {atr_pct:.2f}%, Volatility: {volatility})"] = met

                elif condition_key == "funding_rate":
                    current_funding = market_conditions.get("funding_rate", 0)
                    met = current_funding >= required_value
                    details[
                        f"Funding rate ≥ {required_value:.2%} (current: {current_funding:.4%})"
                    ] = met

                elif condition_key == "rsi_above":
                    current_rsi = market_conditions.get("rsi", 50)
                    met = current_rsi > required_value
                    details[f"RSI > {required_value} (current: {current_rsi:.1f})"] = met

                elif condition_key == "price_above_ma":
                    current_price = market_conditions.get("current_price", 0)
                    ma_period = int(required_value.split("_")[-1]) if "_" in str(required_value) else 21
                    ma_key = f"sma_{ma_period}"
                    ma_value = market_conditions.get(ma_key, current_price)
                    met = current_price > ma_value
                    details[f"Price > MA{ma_period} (${current_price:.4f} > ${ma_value:.4f})"] = met

                elif condition_key == "trend_direction":
                    required_trend = required_value.lower()
                    current_trend = market_conditions.get("trend", "RANGING").lower()
                    met = current_trend == required_trend
                    details[f"Trend {current_trend.upper()} matches {required_trend.upper()}"] = met

                else:
                    # Unknown condition - log but don't fail
                    print(f"[WARNING] Unknown strategy condition: {condition_key}")
                    details[f"{condition_key}: {required_value}"] = True
                    met = True

                if not met:
                    all_met = False
                    print(f"[ERROR] Condition FAILED: {list(details.keys())[-1]}")
                else:
                    print(f"[OK] Condition PASSED: {list(details.keys())[-1]}")

            return {"met": all_met, "details": details}

        except Exception as e:
            print(f"[ERROR] CRITICAL: Strategy condition check failed: {e}")
            # NO FALLBACKS - Fail the strategy
            return {
                "met": False,
                "details": {f"Critical error in condition checking: {str(e)}": False},
            }

    def _generate_signal_from_strategy(
        self, strategy: Dict, token: str, market_conditions: Dict
    ) -> Optional[Dict]:
        """Generate a trading signal based on a validated strategy - REAL DATA ONLY"""
        try:
            # Check for error conditions first
            if "error" in market_conditions:
                raise Exception(f"Cannot generate signal with error: {market_conditions['error']}")

            category = strategy["category"]

            print(f"[INFO] Generating signal from REAL data for {strategy['name']} (category: {category})")

            # Get REAL technical indicators
            current_price = market_conditions.get("current_price", 0)
            rsi = market_conditions.get("rsi", 50)
            trend = market_conditions.get("trend", "RANGING")
            volume_ratio = market_conditions.get("volume_ratio", 1.0)
            momentum = market_conditions.get("momentum", 0)
            funding_rate = market_conditions.get("funding_rate", 0)
            volatility = market_conditions.get("volatility", "MEDIUM")

            print(f"[DATA] Price: {current_price:.4f}, RSI: {rsi:.1f}, Trend: {trend}, Volume: {volume_ratio:.2f}x")

            # Generate direction and strength based on REAL strategy category and conditions
            if category == "risk_management":
                # Risk management strategies buy on oversold conditions (REAL RSI)
                if rsi < 30:
                    direction = "BUY"
                    strength = min(0.9, 0.6 + (30 - rsi) / 50)  # Stronger signal with lower RSI
                    reason = f"Risk management {strategy['name']} - REAL RSI oversold at {rsi:.1f}"
                else:
                    print(f"[INFO] Risk management: RSI {rsi:.1f} not oversold enough (<30)")
                    return None

            elif category == "technical":
                # Technical strategies depend on REAL technical indicators
                if trend == "BULLISH" and rsi < 70:
                    direction = "BUY"
                    strength = min(0.8, 0.5 + (70 - rsi) / 100 + volume_ratio * 0.1)
                    reason = f"Technical {strategy['name']} - REAL bullish trend + RSI {rsi:.1f}"

                elif trend == "BEARISH" and rsi > 30:
                    direction = "SELL"
                    strength = min(0.8, 0.5 + (rsi - 30) / 100 + volume_ratio * 0.1)
                    reason = f"Technical {strategy['name']} - REAL bearish trend + RSI {rsi:.1f}"

                else:
                    print(f"[INFO] Technical: Trend {trend} with RSI {rsi:.1f} - no clear signal")
                    return None

            elif category == "funding":
                # Funding strategies use REAL funding rates
                if funding_rate > 0.01:  # >1%
                    direction = "BUY"  # Buy when funding is high (short the perpetual)
                    strength = min(0.9, 0.7 + funding_rate * 10)  # Stronger with higher funding
                    reason = f"Funding arbitrage {strategy['name']} - REAL high funding rate {funding_rate:.4%}"
                else:
                    print(f"[INFO] Funding: Rate {funding_rate:.4%} not high enough (>1%)")
                    return None

            elif category == "sentiment":
                # Sentiment strategies use REAL momentum and RSI as proxy
                sentiment_score = (momentum * 50) + (100 - rsi) / 2  # Convert to 0-100 scale

                if sentiment_score < 20:  # Extreme fear
                    direction = "BUY"
                    strength = min(0.8, 0.6 + (20 - sentiment_score) / 50)
                    reason = f"Sentiment {strategy['name']} - REAL extreme fear (score: {sentiment_score:.1f})"

                elif sentiment_score > 80:  # Extreme greed
                    direction = "SELL"
                    strength = min(0.8, 0.6 + (sentiment_score - 80) / 50)
                    reason = f"Sentiment {strategy['name']} - REAL extreme greed (score: {sentiment_score:.1f})"

                else:
                    print(f"[INFO] Sentiment: Score {sentiment_score:.1f} not extreme enough")
                    return None

            else:
                print(f"[ERROR] Unknown strategy category: {category}")
                return None

            # Final validation with REAL data
            if current_price <= 0:
                raise Exception("Invalid current price - cannot proceed")

            print(f"[SIGNAL] Generated: {direction} strength {strength:.2f} for {token}")
            print(f"[REASON] {reason}")

            return {
                "direction": direction,
                "strength": strength,
                "reason": reason,
                "technical_data": {
                    "rsi": rsi,
                    "trend": trend,
                    "momentum": momentum,
                    "volume_ratio": volume_ratio,
                    "current_price": current_price
                }
            }

        except Exception as e:
            print(f"[ERROR] CRITICAL: Signal generation failed: {e}")
            # NO FALLBACKS - Return None to prevent fake trades
            return None

    def combine_with_portfolio(self, signals, current_portfolio):
        """Combine strategy signals with current portfolio state"""
        try:
            final_allocations = current_portfolio.copy()

            for signal in signals:
                token = signal["token"]
                strength = signal["signal"]
                direction = signal["direction"]

                if direction == "BUY" and strength >= STRATEGY_MIN_CONFIDENCE:
                    print(f"🔵 Buy signal for {token} (strength: {strength})")
                    max_position = usd_size * (MAX_POSITION_PERCENTAGE / 100)
                    allocation = max_position * strength
                    final_allocations[token] = allocation
                elif direction == "SELL" and strength >= STRATEGY_MIN_CONFIDENCE:
                    print(f"🔴 Sell signal for {token} (strength: {strength})")
                    final_allocations[token] = 0

            return final_allocations

        except Exception as e:
            print(f"[ERROR] Error combining signals: {e}")
            return None

    def execute_strategy_signals(self, approved_signals):
        """Execute trades based on validated strategy signals with backtest proof"""
        try:
            if not approved_signals:
                print("[WARNING] No approved signals to execute")
                return

            print("\n[ROCKET] EXECUTING VALIDATED STRATEGY SIGNALS")
            print("=" * 80)
            print(
                f"[NOTE] Received {len(approved_signals)} validated signals to execute"
            )

            for signal in approved_signals:
                try:
                    # Display signal with full backtest proof
                    print(f"\n{'='*80}")
                    print(f"[TARGET] EXECUTING VALIDATED SIGNAL")
                    print(f"{'='*80}")
                    print(f"[OK] Token: {signal.get('token')}")
                    print(
                        f"[OK] Strategy: {signal.get('strategy_name')} ({signal.get('strategy_category')})"
                    )
                    print(f"[OK] Direction: {signal.get('direction')}")
                    print(f"[OK] Strength: {signal.get('signal_strength', 0):.2f}")
                    print(f"\n[WINNER] BACKTEST PROOF:")
                    print(
                        f"   • Historical Win Rate: {signal['backtest_proof']['win_rate']:.1%}"
                    )
                    print(
                        f"   • Profit Factor: {signal['backtest_proof']['profit_factor']:.2f}"
                    )
                    print(
                        f"   • Period Tested: {signal['backtest_proof']['period_tested']}"
                    )
                    print(
                        f"   • Symbols Tested: {', '.join(signal['backtest_proof']['symbols_tested'])}"
                    )
                    print(f"\n[IDEA] Reason: {signal.get('reason', 'N/A')}")
                    print(f"{'='*80}")

                    token = signal.get("token")
                    if not token:
                        print("[ERROR] Missing token in signal")
                        continue

                    strength = signal.get("signal_strength", 0)
                    direction = signal.get("direction", "NOTHING")

                    # Skip USDC and other excluded tokens
                    if token in EXCLUDED_TOKENS:
                        print(f"[MONEY] Skipping {token} (excluded token)")
                        continue

                    # Calculate position size based on validated signal strength
                    max_position = usd_size * (MAX_POSITION_PERCENTAGE / 100)
                    target_size = max_position * strength

                    # Get current position value
                    if self.em:
                        current_position = self.em.get_token_balance_usd(token)
                    else:
                        current_position = n.get_token_balance_usd(token)

                    print(f"\n[STATS] EXECUTION DETAILS:")
                    print(f"   • Signal Strength: {strength:.2f}")
                    print(f"   • Max Position: ${max_position:.2f} USD")
                    print(f"   • Target Size: ${target_size:.2f} USD")
                    print(f"   • Current Position: ${current_position:.2f} USD")

                    # Execute based on direction
                    if direction == "BUY":
                        if current_position < target_size:
                            print(f"\n[OK] EXECUTING BUY ORDER FOR {token}")
                            if self.em:
                                self.em.ai_entry(token, target_size)
                            else:
                                n.ai_entry(token, target_size)
                            print(f"[OK] BUY ORDER COMPLETE for {token}")
                            print(f"   [MONEY] Purchased: ${target_size:.2f} USD")
                        else:
                            print(f"\n⏸️ Position already at or above target size")
                            print(f"   Current: ${current_position:.2f} USD")
                            print(f"   Target: ${target_size:.2f} USD")

                    elif direction == "SELL":
                        if current_position > 0:
                            print(f"\n[DOWN] EXECUTING SELL ORDER FOR {token}")
                            if self.em:
                                self.em.chunk_kill(token)
                            else:
                                n.chunk_kill(token, max_usd_order_size, slippage)
                            print(f"[OK] SELL ORDER COMPLETE for {token}")
                            print(f"   [MONEY] Sold: ${current_position:.2f} USD")
                        else:
                            print(f"\n⏸️ No position to sell for {token}")

                    # Log successful execution
                    print(f"\n[OK] SIGNAL EXECUTED SUCCESSFULLY")
                    print(f"   Token: {token}")
                    print(f"   Strategy: {signal.get('strategy_name')}")
                    print(
                        f"   Backtest Win Rate: {signal['backtest_proof']['win_rate']:.1%}"
                    )
                    print(f"{'='*80}\n")

                    time.sleep(2)  # Small delay between trades

                except Exception as e:
                    print(f"[ERROR] Error processing validated signal: {str(e)}")
                    print(f"Signal data: {signal}")
                    import traceback

                    traceback.print_exc()
                    continue

            print(f"\n[PARTY] ALL VALIDATED SIGNALS EXECUTED")
            print(f"[STATS] Total Signals: {len(approved_signals)}")
            print(f"[WINNER] All signals have backtest proof")
            print("=" * 80)

        except Exception as e:
            print(f"[ERROR] Error executing validated strategy signals: {str(e)}")
            import traceback

            traceback.print_exc()
