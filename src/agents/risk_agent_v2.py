"""
🌙 Deamon Dev's Risk Management Agent V2 - Claude Code Sub-Agent Version
Built with love by Deamon Dev 🚀

Version 2.0: Utilise les sub-agents Claude Code au lieu d'appels LLM directs
Garde la même logique que V1 mais délègue l'analyse IA au sub-agent claude-risk-advisor
"""

import json
import os
import re
import subprocess
import time
import traceback
from datetime import datetime, timedelta

import pandas as pd
from dotenv import load_dotenv
from termcolor import colored, cprint

from src import config
from src import nice_funcs as n
from src.agents.base_agent import BaseAgent
from src.config import *

# Load environment variables
load_dotenv()


class RiskAgentV2(BaseAgent):
    """Risk Agent V2 - Utilise Claude Code Sub-Agents"""

    def __init__(self):
        """Initialize Deamon Dev's Risk Agent V2"""
        super().__init__(
            "risk_agent_v2", enable_postgres=True
        )  # Initialize base agent with PostgreSQL support

        # Configuration pour le sub-agent
        self.subagent_name = "claude-risk-advisor"
        self.claude_code_available = self._check_claude_code()

        if not self.claude_code_available:
            cprint(
                "⚠️ Claude Code CLI not found - falling back to direct LLM calls",
                "yellow",
            )
            # Fallback au V1
            self._init_fallback()

        # Initialize start balance using portfolio value
        self.start_balance = self.get_portfolio_value()
        print(f"🏦 Initial Portfolio Balance: ${self.start_balance:.2f}")

        self.current_value = self.start_balance
        cprint("🛡️ Risk Agent V2 initialized with Claude Code Sub-Agents!", "white", "on_blue")

    def _check_claude_code(self) -> bool:
        """Vérifier si Claude Code CLI est disponible"""
        try:
            result = subprocess.run(
                ["claude", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                cprint(f"✅ Claude Code CLI found: {result.stdout.strip()}", "green")
                return True
            else:
                cprint("❌ Claude Code CLI not working properly", "red")
                return False
        except FileNotFoundError:
            cprint("❌ Claude Code CLI not found in PATH", "red")
            return False
        except Exception as e:
            cprint(f"❌ Error checking Claude Code: {e}", "red")
            return False

    def _init_fallback(self):
        """Initialiser le fallback vers V1 si Claude Code n'est pas disponible"""
        import anthropic
        import openai

        # Get API keys
        openai_key = os.getenv("OPENAI_KEY")
        anthropic_key = os.getenv("ANTHROPIC_KEY")
        deepseek_key = os.getenv("DEEPSEEK_KEY")

        if not openai_key:
            raise ValueError("🚨 OPENAI_KEY not found in environment variables!")
        if not anthropic_key:
            raise ValueError("🚨 ANTHROPIC_KEY not found in environment variables!")

        # Initialize OpenAI client for DeepSeek
        if deepseek_key:
            self.deepseek_client = openai.OpenAI(
                api_key=deepseek_key, base_url="https://api.deepseek.com"
            )
            print("🚀 DeepSeek model initialized for fallback!")
        else:
            self.deepseek_client = None

        # Initialize Anthropic client
        self.client = anthropic.Anthropic(api_key=anthropic_key)

        self.override_active = False
        self.last_override_check = None

    def call_subagent(self, prompt: str, context_data: dict = None) -> str:
        """
        Appeler le sub-agent claude-risk-advisor via Claude Code CLI

        Args:
            prompt: Le prompt pour le sub-agent
            context_data: Données contextuelles (portfolio, market data, etc.)

        Returns:
            Réponse du sub-agent
        """
        if not self.claude_code_available:
            # Fallback vers V1
            return self._call_fallback_llm(prompt)

        try:
            # Construire la commande Claude Code
            # Le sub-agent sera automatiquement sélectionné via sa description
            # ou on peut l'invoquer explicitement

            # Option 1: Invocation automatique (basé sur la description)
            # Claude Code sélectionnera automatiquement le sub-agent

            # Option 2: Invocation explicite (plus fiable)
            full_prompt = f"""Use the claude-risk-advisor subagent to analyze this risk scenario:

{prompt}

Context Data:
{json.dumps(context_data, indent=2) if context_data else 'N/A'}

Please provide a detailed risk assessment with clear recommendations."""

            # Exécuter Claude Code avec le sub-agent
            # Note: La syntaxe exacte peut varier selon la version de Claude Code
            cmd = ["claude", "--agent", self.subagent_name, full_prompt]

            cprint(f"🔄 Calling sub-agent: {self.subagent_name}", "cyan")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,  # 2 minutes timeout
                cwd=os.getcwd()
            )

            if result.returncode == 0:
                cprint("✅ Sub-agent response received", "green")
                return result.stdout
            else:
                cprint(f"❌ Sub-agent error: {result.stderr}", "red")
                # Fallback vers V1 en cas d'erreur
                return self._call_fallback_llm(prompt)

        except subprocess.TimeoutExpired:
            cprint("⏱️ Sub-agent timeout - falling back", "yellow")
            return self._call_fallback_llm(prompt)
        except Exception as e:
            cprint(f"❌ Error calling sub-agent: {e}", "red")
            cprint("🔄 Falling back to direct LLM", "yellow")
            return self._call_fallback_llm(prompt)

    def _call_fallback_llm(self, prompt: str) -> str:
        """Fallback vers les appels LLM directs (V1)"""
        try:
            from src.models.model_factory import model_factory

            # Obtenir le modèle depuis la factory
            model = model_factory.get_model("claude", AI_MODEL)

            if model:
                response = model.generate(
                    system_prompt="You are Deamon Dev's Risk Management AI. Analyze the provided data and respond with detailed risk assessment.",
                    user_content=prompt,
                    temperature=0.7,
                    max_tokens=2048
                )
                return str(response)
            else:
                # Fallback manuel
                message = self.client.messages.create(
                    model=AI_MODEL,
                    max_tokens=AI_MAX_TOKENS,
                    temperature=AI_TEMPERATURE,
                    messages=[{"role": "user", "content": prompt}],
                )
                return str(message.content)

        except Exception as e:
            cprint(f"❌ Fallback LLM error: {e}", "red")
            return "ERROR: Unable to analyze risk - all methods failed"

    def get_portfolio_value(self):
        """Calculate total portfolio value in USD"""
        total_value = 0.0

        try:
            print("\n🔍 Deamon Dev's Portfolio Value Calculator Starting... 🚀")

            # Get USDC balance first
            print("💵 Getting USDC balance...")
            try:
                print(f"🔍 Checking USDC balance for address: {config.USDC_ADDRESS}")
                usdc_value = n.get_token_balance_usd(config.USDC_ADDRESS)
                print(f"✅ USDC Value: ${usdc_value:.2f}")
                total_value += usdc_value
            except Exception as e:
                print(f"❌ Error getting USDC balance: {str(e)}")
                print(f"🔍 Debug info - USDC Address: {config.USDC_ADDRESS}")
                traceback.print_exc()

            # Get balance of each monitored token
            print("\n📊 Getting monitored token balances...")
            print(f"🎯 Total tokens to check: {len(config.MONITORED_TOKENS)}")
            print(f"📝 Token list: {config.MONITORED_TOKENS}")

            for token in config.MONITORED_TOKENS:
                if token != config.USDC_ADDRESS:  # Skip USDC as we already counted it
                    try:
                        print(f"\n🪙 Checking token: {token[:8]}...")
                        token_value = n.get_token_balance_usd(token)
                        if token_value > 0:
                            print(f"💰 Found position worth: ${token_value:.2f}")
                            total_value += token_value
                        else:
                            print("ℹ️ No balance found for this token")
                    except Exception as e:
                        print(f"❌ Error getting balance for {token[:8]}: {str(e)}")
                        print("🔍 Full error trace:")
                        traceback.print_exc()

            print(f"\n💎 Deamon Dev's Total Portfolio Value: ${total_value:.2f} 🌙")
            return total_value

        except Exception as e:
            cprint(f"❌ Error calculating portfolio value: {str(e)}", "white", "on_red")
            print("🔍 Full error trace:")
            traceback.print_exc()
            return 0.0

    def log_daily_balance(self):
        """Log portfolio value if not logged in past check period"""
        try:
            print("\n📝 Checking if we need to log daily balance...")

            # Create data directory if it doesn't exist
            os.makedirs("src/data", exist_ok=True)
            balance_file = "src/data/portfolio_balance.csv"
            print(f"📁 Using balance file: {balance_file}")

            # Check if we already have a recent log
            if os.path.exists(balance_file):
                print("✅ Found existing balance log file")
                df = pd.read_csv(balance_file)
                if not df.empty:
                    df["timestamp"] = pd.to_datetime(df["timestamp"])
                    last_log = df["timestamp"].max()
                    hours_since_log = (datetime.now() - last_log).total_seconds() / 3600

                    print(f"⏰ Hours since last log: {hours_since_log:.1f}")
                    print(
                        f"⚙️ Max hours between checks: {config.MAX_LOSS_GAIN_CHECK_HOURS}"
                    )

                    if hours_since_log < config.MAX_LOSS_GAIN_CHECK_HOURS:
                        cprint(
                            f"✨ Recent balance log found ({hours_since_log:.1f} hours ago)",
                            "white",
                            "on_blue",
                        )
                        return
            else:
                print("📊 Creating new balance log file")
                df = pd.DataFrame(columns=["timestamp", "balance"])

            # Get current portfolio value
            print("\n💰 Getting fresh portfolio value...")
            current_value = self.get_portfolio_value()

            # Add new row
            new_row = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "balance": current_value,
            }
            print(f"📝 Adding new balance record: {new_row}")

            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

            # Save updated log
            df.to_csv(balance_file, index=False)
            cprint(
                f"💾 New portfolio balance logged: ${current_value:.2f}",
                "white",
                "on_green",
            )

        except Exception as e:
            cprint(f"❌ Error logging balance: {str(e)}", "white", "on_red")
            traceback.print_exc()  # Print full stack trace

    def get_position_data(self, token):
        """Get recent market data for a token"""
        try:
            # Get 8h of 15m data
            data_15m = n.get_data(token, 0.33, "15m")  # 8 hours = 0.33 days

            # Get 2h of 5m data
            data_5m = n.get_data(token, 0.083, "5m")  # 2 hours = 0.083 days

            return {
                "15m": data_15m.to_dict() if data_15m is not None else None,
                "5m": data_5m.to_dict() if data_5m is not None else None,
            }
        except Exception as e:
            cprint(f"❌ Error getting data for {token}: {str(e)}", "white", "on_red")
            return None

    def should_override_limit(self, limit_type):
        """Ask AI (sub-agent) if we should override the limit based on recent market data"""
        try:
            # Only check every 15 minutes
            if (
                self.last_override_check
                and datetime.now() - self.last_override_check < timedelta(minutes=15)
            ):
                return self.override_active

            # Get current positions first
            positions = n.fetch_wallet_holdings_og(config.address)

            # Filter for tokens that are both in MONITORED_TOKENS and in our positions
            # Exclude USDC and SOL
            positions = positions[
                positions["Mint Address"].isin(MONITORED_TOKENS)
                & ~positions["Mint Address"].isin(EXCLUDED_TOKENS)
            ]

            if positions.empty:
                cprint("❌ No monitored positions found to analyze", "white", "on_red")
                return False

            # Collect data only for monitored tokens we have positions in
            position_data = {}
            for _, row in positions.iterrows():
                token = row["Mint Address"]
                current_value = row["USD Value"]

                if current_value > 0:  # Double check we have a position
                    cprint(
                        f"📊 Getting market data for monitored position: {token}",
                        "white",
                        "on_blue",
                    )
                    token_data = self.get_position_data(token)
                    if token_data:
                        position_data[token] = {
                            "value_usd": current_value,
                            "data": token_data,
                        }

            if not position_data:
                cprint(
                    "❌ Could not get market data for any monitored positions",
                    "white",
                    "on_red",
                )
                return False

            # Format data for sub-agent analysis
            prompt = f"""
RISK LIMIT BREACH DETECTED

Limit Type: {limit_type}
Current Portfolio Value: ${self.current_value}
Start Balance: ${self.start_balance}
Current P&L: ${self.current_value - self.start_balance}

POSITION DATA:
{json.dumps(position_data, indent=2)}

Please analyze this risk scenario and recommend whether to OVERRIDE the limit (keep positions open) or RESPECT the limit (close all positions).

Consider:
- Recent price action on 15m and 5m timeframes
- Volume patterns and trends
- Market conditions and volatility
- Risk/reward ratio for each position
- Overall market sentiment

Provide a detailed analysis with clear recommendation.
"""

            # Appeler le sub-agent
            context_data = {
                "limit_type": limit_type,
                "current_value": self.current_value,
                "start_balance": self.start_balance,
                "position_data": position_data,
                "config": {
                    "max_loss_usd": MAX_LOSS_USD,
                    "max_gain_usd": MAX_GAIN_USD,
                    "use_percentage": USE_PERCENTAGE,
                    "max_loss_percent": MAX_LOSS_PERCENT,
                    "max_gain_percent": MAX_GAIN_PERCENT,
                }
            }

            cprint("🤖 Claude Code Sub-Agent analyzing risk...", "white", "on_green")

            response = self.call_subagent(prompt, context_data)

            self.last_override_check = datetime.now()

            # Check if we should override (keep positions open)
            self.override_active = "OVERRIDE" in response.upper()

            # Print the sub-agent's reasoning
            cprint("\n🧠 Risk Sub-Agent Analysis:", "white", "on_blue")
            print("=" * 80)
            print(response)
            print("=" * 80)

            if self.override_active:
                cprint(
                    "\n🤖 Sub-Agent suggests keeping positions open",
                    "white",
                    "on_yellow",
                )
            else:
                cprint("\n🛡️ Sub-Agent recommends closing positions", "white", "on_red")

            return self.override_active

        except Exception as e:
            cprint(f"❌ Error in override check: {str(e)}", "white", "on_red")
            return False

    def check_pnl_limits(self):
        """Check if PnL limits have been hit"""
        try:
            self.current_value = self.get_portfolio_value()

            if USE_PERCENTAGE:
                # Calculate percentage change
                percent_change = (
                    (self.current_value - self.start_balance) / self.start_balance
                ) * 100

                if percent_change <= -MAX_LOSS_PERCENT:
                    cprint("\n🛑 MAXIMUM LOSS PERCENTAGE REACHED", "white", "on_red")
                    cprint(
                        f"📉 Loss: {percent_change:.2f}% (Limit: {MAX_LOSS_PERCENT}%)",
                        "red",
                    )
                    return True

                if percent_change >= MAX_GAIN_PERCENT:
                    cprint("\n🎯 MAXIMUM GAIN PERCENTAGE REACHED", "white", "on_green")
                    cprint(
                        f"📈 Gain: {percent_change:.2f}% (Limit: {MAX_GAIN_PERCENT}%)",
                        "green",
                    )
                    return True

            else:
                # Calculate USD change
                usd_change = self.current_value - self.start_balance

                if usd_change <= -MAX_LOSS_USD:
                    cprint("\n🛑 MAXIMUM LOSS USD REACHED", "white", "on_red")
                    cprint(
                        f"📉 Loss: ${abs(usd_change):.2f} (Limit: ${MAX_LOSS_USD:.2f})",
                        "red",
                    )
                    return True

                if usd_change >= MAX_GAIN_USD:
                    cprint("\n🎯 MAXIMUM GAIN USD REACHED", "white", "on_green")
                    cprint(
                        f"📈 Gain: ${usd_change:.2f} (Limit: ${MAX_GAIN_USD:.2f})",
                        "green",
                    )
                    return True

            return False

        except Exception as e:
            cprint(f"❌ Error checking PnL limits: {e}", "red")
            return False

    def close_all_positions(self):
        """Close all monitored positions except USDC and SOL"""
        try:
            cprint("\n🔄 Closing monitored positions...", "white", "on_cyan")

            # Get all positions
            positions = n.fetch_wallet_holdings_og(config.address)

            # Debug print to see what we're working with
            cprint("\n📊 Current positions:", "cyan")
            print(positions)
            cprint("\n🎯 Monitored tokens:", "cyan")
            print(MONITORED_TOKENS)

            # Filter for tokens that are both in MONITORED_TOKENS and not in EXCLUDED_TOKENS
            positions = positions[
                positions["Mint Address"].isin(MONITORED_TOKENS)
                & ~positions["Mint Address"].isin(EXCLUDED_TOKENS)
            ]

            if positions.empty:
                cprint("📝 No monitored positions to close", "white", "on_blue")
                return

            # Close each monitored position
            for _, row in positions.iterrows():
                token = row["Mint Address"]
                value = row["USD Value"]

                cprint(
                    f"\n💰 Closing position: {token} (${value:.2f})", "white", "on_cyan"
                )
                try:
                    n.chunk_kill(token, config.max_usd_order_size, config.slippage)
                    cprint(
                        f"✅ Successfully closed position for {token}",
                        "white",
                        "on_green",
                    )
                except Exception as e:
                    cprint(
                        f"❌ Error closing position for {token}: {str(e)}",
                        "white",
                        "on_red",
                    )

            cprint("\n✨ All monitored positions closed", "white", "on_green")

        except Exception as e:
            cprint(f"❌ Error in close_all_positions: {str(e)}", "white", "on_red")

    def check_risk_limits(self):
        """Check if any risk limits have been breached"""
        try:
            # Get current PnL
            current_pnl = self.get_current_pnl()
            current_balance = self.get_portfolio_value()

            print(f"\n💰 Current PnL: ${current_pnl:.2f}")
            print(f"💼 Current Balance: ${current_balance:.2f}")
            print(f"📉 Minimum Balance Limit: ${MINIMUM_BALANCE_USD:.2f}")

            # Check minimum balance limit
            if current_balance < MINIMUM_BALANCE_USD:
                print(
                    f"⚠️ ALERT: Current balance ${current_balance:.2f} is below minimum ${MINIMUM_BALANCE_USD:.2f}"
                )
                self.handle_limit_breach("MINIMUM_BALANCE", current_balance)
                return True

            # Check PnL limits
            if USE_PERCENTAGE:
                if abs(current_pnl) >= MAX_LOSS_PERCENT:
                    print(f"⚠️ PnL limit reached: {current_pnl}%")
                    self.handle_limit_breach("PNL_PERCENT", current_pnl)
                    return True
            else:
                if abs(current_pnl) >= MAX_LOSS_USD:
                    print(f"⚠️ PnL limit reached: ${current_pnl:.2f}")
                    self.handle_limit_breach("PNL_USD", current_pnl)
                    return True

            print("✅ All risk limits OK")
            return False

        except Exception as e:
            print(f"❌ Error checking risk limits: {str(e)}")
            return False

    def handle_limit_breach(self, breach_type, current_value):
        """Handle breached risk limits with sub-agent consultation"""
        try:
            # If AI confirmation is disabled, close positions immediately
            if not USE_AI_CONFIRMATION:
                print(
                    f"\n🚨 {breach_type} limit breached! Closing all positions immediately..."
                )
                print(f"💡 (AI confirmation disabled in config)")
                self.close_all_positions()
                return

            # Get all current positions
            positions_df = n.fetch_wallet_holdings_og(config.address)

            # Prepare breach context
            if breach_type == "MINIMUM_BALANCE":
                context = f"Current balance (${current_value:.2f}) has fallen below minimum balance limit (${MINIMUM_BALANCE_USD:.2f})"
            elif breach_type == "PNL_USD":
                context = f"Current PnL (${current_value:.2f}) has exceeded USD limit (${MAX_LOSS_USD:.2f})"
            else:
                context = f"Current PnL ({current_value}%) has exceeded percentage limit ({MAX_LOSS_PERCENT}%)"

            # Format positions for sub-agent
            positions_str = "\nCurrent Positions:\n"
            for _, row in positions_df.iterrows():
                if row["USD Value"] > 0:
                    positions_str += f"- {row['Mint Address']}: {row['Amount']} (${row['USD Value']:.2f})\n"

            # Get sub-agent recommendation
            prompt = f"""
🚨 RISK LIMIT BREACH ALERT 🚨

{context}

{positions_str}

Should we close all positions immediately? Consider:
1. Market conditions
2. Position sizes
3. Recent price action
4. Risk of further losses

Please provide a detailed risk assessment with clear recommendation: CLOSE_ALL or HOLD_POSITIONS.
"""

            # Préparer les données contextuelles
            context_data = {
                "breach_type": breach_type,
                "current_value": current_value,
                "config": {
                    "minimum_balance_usd": MINIMUM_BALANCE_USD,
                    "max_loss_usd": MAX_LOSS_USD,
                    "max_loss_percent": MAX_LOSS_PERCENT,
                    "use_ai_confirmation": USE_AI_CONFIRMATION,
                },
                "positions": positions_str
            }

            # Appeler le sub-agent
            cprint("\n🤖 Consulting Claude Code Sub-Agent for risk decision...", "white", "on_yellow")
            response = self.call_subagent(prompt, context_data)

            print("\n🤖 Sub-Agent Risk Assessment:")
            print("=" * 80)
            print(response)
            print("=" * 80)

            # Parse decision
            decision = response.split("\n")[0].strip()
            if "CLOSE_ALL" in decision.upper():
                print("🚨 Sub-Agent recommends closing all positions!")
                self.close_all_positions()
            else:
                print("✋ Sub-Agent recommends holding positions despite breach")

        except Exception as e:
            print(f"❌ Error handling limit breach: {str(e)}")
            # Default to closing positions on error
            print("⚠️ Error in sub-agent consultation - defaulting to close all positions")
            self.close_all_positions()

    def get_current_pnl(self):
        """Calculate current PnL based on start balance"""
        try:
            current_value = self.get_portfolio_value()
            print(f"\n💰 Start Balance: ${self.start_balance:.2f}")
            print(f"📊 Current Value: ${current_value:.2f}")

            pnl = current_value - self.start_balance
            print(f"📈 Current PnL: ${pnl:.2f}")
            return pnl

        except Exception as e:
            print(f"❌ Error calculating PnL: {str(e)}")
            return 0.0

    def run(self):
        """Run the risk agent V2 (implements BaseAgent interface)"""
        try:
            # Get current PnL
            current_pnl = self.get_current_pnl()
            current_balance = self.get_portfolio_value()

            print(f"\n💰 Current PnL: ${current_pnl:.2f}")
            print(f"💼 Current Balance: ${current_balance:.2f}")
            print(f"📉 Minimum Balance Limit: ${MINIMUM_BALANCE_USD:.2f}")

            # Check minimum balance limit
            if current_balance < MINIMUM_BALANCE_USD:
                print(
                    f"⚠️ ALERT: Current balance ${current_balance:.2f} is below minimum ${MINIMUM_BALANCE_USD:.2f}"
                )
                self.handle_limit_breach("MINIMUM_BALANCE", current_balance)
                return True

            # Check PnL limits
            if USE_PERCENTAGE:
                if abs(current_pnl) >= MAX_LOSS_PERCENT:
                    print(f"⚠️ PnL limit reached: {current_pnl}%")
                    self.handle_limit_breach("PNL_PERCENT", current_pnl)
                    return True
            else:
                if abs(current_pnl) >= MAX_LOSS_USD:
                    print(f"⚠️ PnL limit reached: ${current_pnl:.2f}")
                    self.handle_limit_breach("PNL_USD", current_pnl)
                    return True

            print("✅ All risk limits OK")
            return False

        except Exception as e:
            print(f"❌ Error checking risk limits: {str(e)}")
            return False


def main():
    """Main function to run the risk agent V2"""
    cprint("🛡🛡🛡️ Risk Agent V2 (Claude Code Sub-Agents) Starting...", "white", "on_blue")

    agent = RiskAgentV2()

    while True:
        try:
            # Always try to log balance (function will check if 12 hours have passed)
            agent.log_daily_balance()

            # Always check PnL limits
            agent.check_pnl_limits()

            # Sleep for 5 minutes before next check
            time.sleep(300)

        except KeyboardInterrupt:
            print("\n👋 Risk Agent V2 shutting down gracefully...")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            print("🔧 Deamon Dev suggests checking the logs and trying again!")
            time.sleep(300)  # Still sleep on error


if __name__ == "__main__":
    main()
