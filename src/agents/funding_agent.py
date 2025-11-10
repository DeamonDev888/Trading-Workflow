"""
💰 Deamon Dev's Funding Agent
Built with love by Deamon Dev 🚀

Funding Agent tracks funding rate changes across different timeframes
and executes funding arbitrage strategies using Claude Code Sub-Agents.

Version 2.0: Utilise Claude Code Sub-Agents exclusively (no external APIs)
"""

import json
import os
import subprocess
import time
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict

from termcolor import cprint

from src.agents.base_agent import BaseAgent
from src.agents.strategy_library import PROVEN_STRATEGIES
from src.config import (
    AI_MAX_TOKENS,
    AI_MODEL,
    AI_TEMPERATURE,
    DATA_TIMEFRAME,
    HYPERLIQUID_SYMBOLS,
    MAX_ORDER_SIZE_USD,
    MONITORED_TOKENS,
)
from src.hyperliquid import HyperliquidClient

TIMEFRAME = "1h"
LOOKBACK_BARS = 50
NEGATIVE_THRESHOLD = -0.01
POSITIVE_THRESHOLD = 0.01

PROJECT_ROOT = Path(__file__).parent.parent.parent

FUNDING_ANALYSIS_PROMPT = """
You are Deamon Dev's Funding Rate Analysis Assistant

Analyze the funding rate opportunity and provide a trading recommendation:

Symbol: {symbol}
Current Funding Rate: {rate}% (annualized: {annual_rate}%)
Market Context: {context}

Evaluate:
1. Is this a profitable arbitrage opportunity?
2. Risk/reward ratio
3. Recommended action: BUY/SELL/NOTHING
4. Position size suggestion
5. Expected duration

Respond in this format:
1. First line: BUY, SELL, or NOTHING
2. Brief reasoning (1-2 lines)
3. Confidence: X%
4. Position size recommendation
5. Risk factors
"""


class FundingAgent(BaseAgent):
    """Funding Agent - Utilise Claude Code Sub-Agents"""

    def __init__(self):
        """Initialize Deamon Dev's Funding Agent"""
        super().__init__("funding", enable_postgres=True)

        self.subagent_name = "Deamon-funding-advisor"

        self.data_dir = PROJECT_ROOT / "src" / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.history_file = self.data_dir / "funding_history.csv"
        self.load_history()

        self._validate_funding_strategy()

        cprint(
            "[OK] Funding Agent initialized with Claude Code Sub-Agents!",
            "white",
            "on_blue",
        )

    def call_subagent(self, prompt: str, context_data: dict = None) -> str:
        """
        Appeler le sub-agent claude-funding-advisor via Claude Code CLI

        Args:
            prompt: Le prompt pour le sub-agent
            context_data: Données contextuelles (funding rates, market data, etc.)

        Returns:
            Réponse du sub-agent

        Raises:
            RuntimeError: Si l'appel au sub-agent échoue
        """
        full_prompt = f"""Use the Deamon-funding-advisor subagent to analyze this funding opportunity:

{prompt}

Context Data:
{json.dumps(context_data, indent=2) if context_data else 'N/A'}

Please provide a detailed funding analysis with clear BUY/SELL/NOTHING recommendations."""

        cmd = [
            "claude",
            "--dangerously-skip-permissions",
            "--agent",
            "Deamon-funding-advisor",
            full_prompt,
        ]

        cprint(
            f"[INFO] Calling sub-agent: Deamon-funding-advisor (skipping permissions)",
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

    def _validate_funding_strategy(self):
        """Validate that funding strategy is in the proven library"""
        funding_strategy = PROVEN_STRATEGIES.strategies.get("Funding_Arbitrage_85")

        if funding_strategy:
            cprint("\n" + "=" * 80, "green")
            cprint("🏆 FUNDING ARBITRAGE STRATEGY VALIDATED", "green")
            cprint("=" * 80, "green")
            cprint(f"✅ Strategy: {funding_strategy['name']}", "green")
            cprint(f"✅ Historical Win Rate: {funding_strategy['win_rate']:.1%}", "green")
            cprint(f"✅ Profit Factor: {funding_strategy['profit_factor']:.2f}", "green")
            cprint(
                f"✅ Tested on: {', '.join(funding_strategy['symbols_validated'])}",
                "green",
            )
            cprint(
                f"✅ Current Validation: {funding_strategy['current_validation']['valid']}",
                "green",
            )
            cprint("=" * 80, "green")
        else:
            cprint("⚠️ Funding_Arbitrage_85 strategy NOT found in library!", "yellow")

    def validate_funding_opportunity_with_proof(self, symbol: str, funding_rate: float) -> Dict:
        """
        Validate a funding opportunity using the proven Funding_Arbitrage_85 strategy

        Returns validation result with backtest proof
        """
        funding_strategy = PROVEN_STRATEGIES.strategies.get("Funding_Arbitrage_85")

        if not funding_strategy:
            return {
                "valid": False,
                "reason": "Funding_Arbitrage_85 strategy not in validated library",
            }

        if symbol not in funding_strategy["symbols_validated"]:
            return {
                "valid": False,
                "reason": f"Funding strategy not tested on {symbol}",
                "backtest_proof": funding_strategy,
            }

        min_funding = funding_strategy["conditions"].get("funding_rate", 0.01)

        if funding_rate < min_funding:
            return {
                "valid": False,
                "reason": f"Funding rate {funding_rate:.2%} below strategy threshold {min_funding:.2%}",
                "backtest_proof": funding_strategy,
            }

        if not funding_strategy["current_validation"]["valid"]:
            return {
                "valid": False,
                "reason": "Funding strategy currently not validated",
                "backtest_proof": funding_strategy,
            }

        return {
            "valid": True,
            "reason": f"Funding opportunity validated with {funding_strategy['name']}",
            "backtest_proof": funding_strategy,
            "strategy_definition": funding_strategy,
            "funding_rate": funding_rate,
            "threshold_met": funding_rate >= min_funding,
        }

    async def _analyze_opportunity(self, symbol, funding_data, market_data):
        """Get AI analysis of the opportunity using Claude Sub-Agent"""
        try:
            rate = funding_data["annual_rate"].iloc[0]
            print(f"\n🔍 Raw funding rate for {symbol}: {rate:.2f}%")

            async with HyperliquidClient() as client:
                btc_candles = await client.get_candles(
                    symbol="BTC",
                    interval=TIMEFRAME,
                )

                btc_data = pd.DataFrame(
                    [
                        {
                            "timestamp": c.timestamp,
                            "open": c.open,
                            "high": c.high,
                            "low": c.low,
                            "close": c.close,
                            "volume": c.volume,
                        }
                        for c in btc_candles[-LOOKBACK_BARS:]
                    ]
                )

                symbol_data = None
                if symbol != "BTC":
                    symbol_candles = await client.get_candles(
                        symbol=symbol,
                        interval=TIMEFRAME,
                    )
                    symbol_data = pd.DataFrame(
                        [
                            {
                                "timestamp": c.timestamp,
                                "open": c.open,
                                "high": c.high,
                                "low": c.low,
                                "close": c.close,
                                "volume": c.volume,
                            }
                            for c in symbol_candles[-LOOKBACK_BARS:]
                        ]
                    )

            market_context = (
                f"BTC Market Data (Last 5 candles):\n{btc_data.tail(5).to_string()}\n\n"
            )
            if symbol_data is not None and symbol != "BTC":
                market_context += f"{symbol} Technical Data (Last 5 candles):\n{symbol_data.tail(5).to_string()}\n\n"

            btc_close = btc_data["close"].iloc[-1]
            btc_sma = btc_data["close"].rolling(20).mean().iloc[-1]
            btc_trend = "UPTREND" if btc_close > btc_sma else "DOWNTREND"
            market_context += f"\nBTC Trend Analysis:\n- Current Price vs 20 SMA: {btc_trend}\n"

            rate = funding_data["annual_rate"].iloc[0]
            context = FUNDING_ANALYSIS_PROMPT.format(
                symbol=symbol,
                rate=f"{rate:.2f}",
                market_data=market_context,
                funding_data=funding_data.to_string(),
            )

            print(f"\n🤖 Analyzing {symbol} with Claude Sub-Agent...")

            context_data = {
                "symbol": symbol,
                "funding_rate": rate,
                "btc_trend": btc_trend,
                "active_model": self.active_model,
            }

            content = self.call_subagent(context, context_data)

            print("\n🔍 Raw response:")
            print(repr(content))

            content = content.replace("\\n", "\n")
            content = content.strip("[]")

            lines = [line.strip() for line in content.split("\n") if line.strip()]

            if not lines:
                print("❌ Empty response from sub-agent")
                return None

            action = lines[0].strip().upper()
            if action not in ["BUY", "SELL", "NOTHING"]:
                print(f"⚠️ Invalid action: {action}")
                return None

            analysis = lines[1] if len(lines) > 1 else ""

            confidence = 50  # Default confidence
            if len(lines) > 2:
                try:
                    import re

                    matches = re.findall(r"(\d+)%", lines[2])
                    if matches:
                        confidence = int(matches[0])
                except Exception:
                    print("⚠️ Could not parse confidence, using default")

            return {"action": action, "analysis": analysis, "confidence": confidence}

        except Exception as e:
            print(f"❌ Error in AI analysis: {str(e)}")
            traceback.print_exc()
            return None

    async def _detect_significant_changes(self, current_data):
        """Detect extreme funding rates and analyze opportunities - UPDATED FOR NEW MODULE"""
        try:
            opportunities = {}

            for _, row in current_data.iterrows():
                try:
                    annual_rate = float(row["annual_rate"])
                    symbol = str(row["symbol"])

                    if annual_rate < NEGATIVE_THRESHOLD or annual_rate > POSITIVE_THRESHOLD:
                        async with HyperliquidClient() as client:
                            candles = await client.get_candles(
                                symbol=symbol,
                                interval=TIMEFRAME,
                            )

                            if candles:
                                market_data = pd.DataFrame(
                                    [
                                        {
                                            "timestamp": c.timestamp,
                                            "open": c.open,
                                            "high": c.high,
                                            "low": c.low,
                                            "close": c.close,
                                            "volume": c.volume,
                                        }
                                        for c in candles[-LOOKBACK_BARS:]
                                    ]
                                )

                                analysis = await self._analyze_opportunity(
                                    symbol=symbol,
                                    funding_data=row.to_frame().T,
                                    market_data=market_data,
                                )

                                if analysis:
                                    opportunities[symbol] = {
                                        "annual_rate": annual_rate,
                                        "action": analysis["action"],
                                        "analysis": analysis["analysis"],
                                        "confidence": analysis["confidence"],
                                    }

                except Exception as e:
                    continue

            return opportunities if opportunities else None

        except Exception as e:
            return None

    def _format_announcement(self, opportunities):
        """Format funding rate changes and analysis into a speech-friendly message"""
        try:
            messages = []

            for symbol, data in opportunities.items():
                token_name = SYMBOL_NAMES.get(symbol, symbol)
                rate = data["annual_rate"]
                action = data["action"]
                confidence = data["confidence"]
                analysis = data["analysis"].split("\n")[0]  # Get just the first line of analysis

                if rate < NEGATIVE_THRESHOLD:
                    messages.append(
                        f"{token_name} has negative funding at {rate:.2f}% annual. "
                        f"AI suggests {action} with {confidence}% confidence. "
                        f"Analysis: {analysis} 🌙"
                    )
                elif rate > POSITIVE_THRESHOLD:
                    messages.append(
                        f"{token_name} has high funding at {rate:.2f}% annual. "
                        f"AI suggests {action} with {confidence}% confidence. "
                        f"Analysis: {analysis} 🌙"
                    )

            if messages:
                return "ayo moon dev seven seven seven! " + " | ".join(messages) + "!"
            return None

        except Exception as e:
            print(f"❌ Error formatting announcement: {str(e)}")
            return None

    def _announce(self, message):
        """Announce message to console (TTS removed - using Claude Sub-Agent only)"""
        if not message:
            return

        try:
            print(f"\n📢 Funding Alert: {message}")
            print("=" * 80)
        except Exception as e:
            print(f"❌ Error in announcement: {str(e)}")

    def load_history(self):
        """Load or initialize historical funding rate data"""
        try:
            self.funding_history = pd.DataFrame(
                columns=["timestamp", "symbol", "funding_rate", "annual_rate"]
            )
            print("📝 Initialized new funding rate history")

            if self.history_file.exists():
                backup_file = self.data_dir / "funding_history_backup.csv"
                os.rename(self.history_file, backup_file)
                print(f"📦 Backed up old history file")

        except Exception as e:
            print(f"❌ Error loading history: {str(e)}")
            self.funding_history = pd.DataFrame(
                columns=["timestamp", "symbol", "funding_rate", "annual_rate"]
            )

    def _get_current_funding(self):
        """Get current funding rate data"""
        try:
            df = self.api.get_funding_data()

            if df is not None and not df.empty:
                current_data = df.sort_values("event_time").groupby("symbol").last().reset_index()

                numeric_cols = ["funding_rate", "yearly_funding_rate"]
                for col in numeric_cols:
                    current_data[col] = pd.to_numeric(current_data[col], errors="coerce")

                current_data = current_data.rename(columns={"yearly_funding_rate": "annual_rate"})

                return current_data
            return None

        except Exception as e:
            print(f"❌ Error getting funding data: {str(e)}")
            traceback.print_exc()
            return None

    def _save_to_history(self, current_data):
        """Save current funding data to history"""
        try:
            if current_data is not None and not current_data.empty:
                wide_data = pd.DataFrame()
                wide_data["event_time"] = [
                    current_data["event_time"].iloc[0]
                ]  # Use first event_time

                for _, row in current_data.iterrows():
                    symbol = row["symbol"]
                    wide_data[f"{symbol}_funding_rate"] = row["funding_rate"]
                    wide_data[f"{symbol}_annual_rate"] = row["annual_rate"]

                if self.funding_history.empty:
                    self.funding_history = wide_data
                else:
                    self.funding_history = pd.concat(
                        [self.funding_history, wide_data], ignore_index=True
                    )

                self.funding_history = self.funding_history.drop_duplicates(
                    subset=["event_time"], keep="last"
                )

                cutoff_time = datetime.now() - timedelta(hours=24)
                self.funding_history = self.funding_history[
                    pd.to_datetime(self.funding_history["event_time"]) > cutoff_time
                ]

                self.funding_history = self.funding_history.sort_values("event_time")

                self.funding_history.to_csv(self.history_file, index=False)

        except Exception as e:
            print(f"❌ Error saving to history: {str(e)}")
            traceback.print_exc()

    async def run_monitoring_cycle(self):
        """Run one monitoring cycle - UPDATED FOR NEW MODULE"""
        try:
            current_data = self._get_current_funding()

            if current_data is not None:
                self._save_to_history(current_data)

                opportunities = await self._detect_significant_changes(current_data)

                if opportunities:
                    message = self._format_announcement(opportunities)
                    if message:
                        self._announce(message)

            print("\n" + "╔" + "═" * 50 + "╗")
            print("║         🌙 Deamon Dev's Funding Party 🎉          ║")
            print("╠" + "═" * 50 + "╣")
            print("║  Symbol  │  Annual Rate  │      Status      ║")
            print("╟" + "─" * 50 + "╢")

            for _, row in current_data.iterrows():
                if row["annual_rate"] > 20:
                    status = "🔥 SUPER HOT!"
                elif row["annual_rate"] < -5:
                    status = "❄️ SUPER COLD"
                elif row["annual_rate"] > 10:
                    status = "📈 HEATING UP"
                elif row["annual_rate"] < 0:
                    status = "📉 COOLING"
                else:
                    status = "😴 CHILL"

                symbol = row["symbol"][:4]
                print(f"║  {symbol:<4} │  {row['annual_rate']:>8.2f}%  │  {status:<13} ║")

            print("╚" + "═" * 50 + "╝")

        except Exception as e:
            print(f"❌ Error in monitoring cycle: {str(e)}")

    async def run(self):
        """Run the funding rate monitor continuously - UPDATED FOR NEW MODULE"""
        print("\n🚀 Starting funding rate monitoring...")

        while True:
            try:
                await self.run_monitoring_cycle()
                print(f"\n💤 Sleeping for {CHECK_INTERVAL_MINUTES} minutes...")
                time.sleep(CHECK_INTERVAL_MINUTES * 60)

            except KeyboardInterrupt:
                print("\n👋 Fran the Funding Agent shutting down gracefully...")
                break
            except Exception as e:
                print(f"❌ Error in main loop: {str(e)}")
                time.sleep(60)  # Sleep for a minute before retrying


if __name__ == "__main__":

    async def main():
        agent = FundingAgent()
        await agent.run()

    asyncio.run(main())
