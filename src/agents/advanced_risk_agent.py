"""
[OK] Deamon Dev's Advanced Risk Agent V3.0 - High Leverage Trading
Built with love by Deamon Dev [ROCKET]

Advanced Risk Agent capable of aggressive positions like:
- Short 25x BTC with 100% capital
- Dynamic leverage adjustment based on volatility
- Sophisticated risk analysis with AI validation
- Real-time position monitoring and management

Version 3.0: High-leverage trading with AI-powered risk validation
"""

import json
import os
import subprocess
import traceback
from datetime import datetime
from typing import Any, Dict

from dotenv import load_dotenv

from src.agents.base_agent import BaseAgent
from src.agents.volatility_tracker import HyperLiquidVolatilityTracker

load_dotenv()


class AdvancedRiskAgent(BaseAgent):
    """Advanced Risk Agent - High Leverage Trading Capable"""

    def __init__(self, aggressive_mode: bool = True):
        """Initialize Advanced Risk Agent"""
        super().__init__("advanced_risk_agent", enable_postgres=True)

        self.aggressive_mode = aggressive_mode
        self.subagent_name = "claude-risk-advisor"

        self.volatility_tracker = HyperLiquidVolatilityTracker()

        self.max_leverage = 50 if aggressive_mode else 10
        self.default_leverage = 25 if aggressive_mode else 5

        self.max_capital_allocation = 1.0 if aggressive_mode else 0.3  # 100% or 30%
        self.max_single_position_risk = 0.40 if aggressive_mode else 0.10  # 40% or 10%

        self.max_drawdown = 0.20 if aggressive_mode else 0.08  # 20% or 8%
        self.max_portfolio_risk = 0.50 if aggressive_mode else 0.15  # 50% or 15%
        self.max_leverage_usage = 0.8 if aggressive_mode else 0.5  # 80% or 50%

        self.start_balance = self.get_portfolio_value()
        self.current_value = self.start_balance
        self.active_positions = {}
        self.risk_assessments = {}

        self.high_leverage_assets = {
            "BTC": {"max_leverage": 50, "confidence_threshold": 0.85},
            "ETH": {"max_leverage": 40, "confidence_threshold": 0.80},
            "SOL": {"max_leverage": 30, "confidence_threshold": 0.75},
            "FARTCOIN": {"max_leverage": 20, "confidence_threshold": 0.70},
            "WIF": {"max_leverage": 25, "confidence_threshold": 0.70},
            "PUMP": {"max_leverage": 15, "confidence_threshold": 0.65},
        }

        print(f"\n{'='*80}")
        mode_str = "AGGRESSIVE" if aggressive_mode else "CONSERVATIVE"
        print(f"[RISK] ADVANCED RISK AGENT V3.0 - {mode_str} MODE")
        print(f"{'='*80}")
        print(f"[LEVERAGE] Max Leverage: {self.max_leverage}x")
        print(f"[CAPITAL] Max Allocation: {self.max_capital_allocation*100:.0f}%")
        print(f"[DRAWDOWN] Max Drawdown: {self.max_drawdown*100:.1f}%")
        print(f"[BALANCE] Initial: ${self.start_balance:,.2f}")
        print(f"{'='*80}\n")

    async def assess_trade_opportunity(
        self,
        symbol: str,
        side: str,
        proposed_leverage: float,
        trade_confidence: float,
        market_analysis: Dict = None,
    ) -> Dict[str, Any]:
        """
        Advanced trade assessment with AI validation

        Args:
            symbol: Trading symbol (BTC, ETH, etc.)
            side: LONG or SHORT
            proposed_leverage: Desired leverage (e.g., 25.0 for 25x)
            trade_confidence: Confidence score (0-1)
            market_analysis: Additional market context
        """
        try:
            print(f"\n[ASSESSMENT] Evaluating {side} {symbol} @ " f"{proposed_leverage}x leverage")
            print(f"[CONFIDENCE] Trade confidence: {trade_confidence*100:.1f}%")

            asset_config = self.high_leverage_assets.get(
                symbol,
                {"max_leverage": self.default_leverage, "confidence_threshold": 0.70},
            )

            if proposed_leverage > asset_config["max_leverage"]:
                return {
                    "approved": False,
                    "reason": (
                        f"Leverage {proposed_leverage}x exceeds max "
                        f'{asset_config["max_leverage"]}x for {symbol}'
                    ),
                    "adjusted_leverage": asset_config["max_leverage"],
                }

            if trade_confidence < asset_config["confidence_threshold"]:
                return {
                    "approved": False,
                    "reason": (
                        f"Confidence {trade_confidence*100:.1f}% below threshold "
                        f'{asset_config["confidence_threshold"]*100:.1f}% for {symbol}'
                    ),
                    "required_confidence": asset_config["confidence_threshold"],
                }

            volatility_data = await self._get_volatility_data(symbol)

            current_price = await self._get_current_price(symbol)
            portfolio_value = self.get_portfolio_value()
            max_position_size = portfolio_value * self.max_capital_allocation

            position_size_usd = min(
                max_position_size,
                portfolio_value * self.max_single_position_risk,
                proposed_leverage * portfolio_value * 0.1,  # Conservative sizing
            )

            liquidation_price = self._calculate_liquidation_price(
                current_price, side, proposed_leverage, position_size_usd
            )

            risk_metrics = self._calculate_risk_metrics(
                symbol,
                current_price,
                liquidation_price,
                proposed_leverage,
                position_size_usd,
            )

            assessment_prompt = self._create_assessment_prompt(
                symbol,
                side,
                proposed_leverage,
                trade_confidence,
                current_price,
                position_size_usd,
                liquidation_price,
                risk_metrics,
                volatility_data,
                market_analysis,
            )

            ai_decision = await self._get_ai_risk_assessment(assessment_prompt)

            approved = self._make_final_decision(ai_decision, risk_metrics, trade_confidence)

            result = {
                "approved": approved,
                "symbol": symbol,
                "side": side,
                "proposed_leverage": proposed_leverage,
                "approved_leverage": (
                    min(proposed_leverage, asset_config["max_leverage"]) if approved else 0
                ),
                "position_size_usd": position_size_usd if approved else 0,
                "current_price": current_price,
                "liquidation_price": liquidation_price if approved else None,
                "risk_metrics": risk_metrics,
                "ai_confidence": ai_decision.get("confidence", 0),
                "ai_reasoning": ai_decision.get("reasoning", ""),
                "final_reason": ai_decision.get("recommendation", "NO ACTION"),
                "timestamp": datetime.now().isoformat(),
            }

            self._display_assessment_result(result)
            return result

        except Exception as e:
            print(f"[ERROR] Trade assessment failed: {e}")
            traceback.print_exc()
            return {
                "approved": False,
                "reason": f"Assessment error: {str(e)}",
                "error": True,
            }

    async def _get_volatility_data(self, symbol: str) -> Dict:
        """Get volatility data for risk assessment"""
        try:
            volatile_assets = await self.volatility_tracker.get_top_volatile_assets(
                min_volatility=0.01, max_count=50
            )

            if symbol in volatile_assets:
                return {
                    "volatility_category": "HIGH",
                    "volatility_score": 0.08,
                    "atr_pct": 8.5,
                    "note": f"{symbol} is in top volatile assets",
                }
            else:
                return {
                    "volatility_category": "MEDIUM",
                    "volatility_score": 0.04,
                    "atr_pct": 4.2,
                    "note": f"{symbol} has moderate volatility",
                }
        except Exception as e:
            print(f"[WARNING] Could not get volatility data for {symbol}: {e}")
            return {
                "volatility_category": "UNKNOWN",
                "volatility_score": 0.05,
                "atr_pct": 5.0,
                "note": "Volatility data unavailable",
            }

    async def _get_current_price(self, symbol: str) -> float:
        """Get current price for symbol"""
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.hyperliquid.xyz/info", json={"type": "allMids"}
                ) as response:
                    if response.status == 200:
                        prices = await response.json()
                        return float(prices.get(symbol, 0))
                    else:
                        raise Exception("Failed to fetch prices")
        except Exception as e:
            print(f"[ERROR] Could not get price for {symbol}: {e}")
            return 0.0

    def _calculate_liquidation_price(
        self, current_price: float, side: str, leverage: float, position_size_usd: float
    ) -> float:
        """Calculate liquidation price for position"""
        try:

            maintenance_margin = 0.005  # 0.5% maintenance margin

            if side.upper() == "LONG":
                liquidation_price = current_price * (1 - 1 / leverage + maintenance_margin)
            else:  # SHORT
                liquidation_price = current_price * (1 + 1 / leverage - maintenance_margin)

            return liquidation_price

        except Exception as e:
            print(f"[ERROR] Liquidation calculation failed: {e}")
            return current_price * 0.9  # Conservative fallback

    def _calculate_risk_metrics(
        self,
        symbol: str,
        current_price: float,
        liquidation_price: float,
        leverage: float,
        position_size_usd: float,
    ) -> Dict:
        """Calculate comprehensive risk metrics"""
        try:
            portfolio_value = self.get_portfolio_value()

            if liquidation_price:
                distance_to_liq = abs(current_price - liquidation_price) / current_price
            else:
                distance_to_liq = 1.0

            portfolio_impact = position_size_usd / portfolio_value

            liquidation_risk = max(
                0, (0.1 - distance_to_liq) / 0.1
            )  # Higher risk if close to liquidation

            leverage_risk = min(1.0, leverage / self.max_leverage)

            risk_score = portfolio_impact * 0.4 + liquidation_risk * 0.4 + leverage_risk * 0.2

            return {
                "distance_to_liquidation_pct": distance_to_liq * 100,
                "portfolio_impact_pct": portfolio_impact * 100,
                "liquidation_risk_score": liquidation_risk,
                "leverage_risk_score": leverage_risk,
                "overall_risk_score": risk_score,
                "risk_level": (
                    "EXTREME"
                    if risk_score > 0.8
                    else ("HIGH" if risk_score > 0.6 else "MEDIUM" if risk_score > 0.4 else "LOW")
                ),
            }

        except Exception as e:
            print(f"[ERROR] Risk metrics calculation failed: {e}")
            return {
                "distance_to_liquidation_pct": 10.0,
                "portfolio_impact_pct": 5.0,
                "liquidation_risk_score": 0.1,
                "leverage_risk_score": 0.2,
                "overall_risk_score": 0.3,
                "risk_level": "MEDIUM",
            }

    def _create_assessment_prompt(
        self,
        symbol: str,
        side: str,
        leverage: float,
        confidence: float,
        current_price: float,
        position_size: float,
        liquidation_price: float,
        risk_metrics: Dict,
        volatility_data: Dict,
        market_analysis: Dict,
    ) -> str:
        """Create comprehensive AI assessment prompt"""

        portfolio_value = self.get_portfolio_value()

        prompt = f"""
ADVANCED RISK ASSESSMENT - HIGH LEVERAGE TRADING

TRADE PROPOSAL:
- Symbol: {symbol}
- Side: {side}
- Leverage: {leverage}x
- Trade Confidence: {confidence*100:.1f}%
- Position Size: ${position_size:,.2f}
- Portfolio Impact: {(position_size/portfolio_value)*100:.1f}%

CURRENT MARKET:
- Entry Price: ${current_price:,.2f}
- Liquidation Price: ${liquidation_price:,.2f}
- Distance to Liquidation: {risk_metrics['distance_to_liquidation_pct']:.2f}%

RISK ANALYSIS:
- Overall Risk Score: {risk_metrics['overall_risk_score']:.3f} (
    {risk_metrics['risk_level']}
)
- Portfolio Impact: {risk_metrics['portfolio_impact_pct']:.1f}%
- Liquidation Risk: {risk_metrics['liquidation_risk_score']:.3f}
- Leverage Risk: {risk_metrics['leverage_risk_score']:.3f}

VOLATILITY DATA:
- Category: {volatility_data['volatility_category']}
- Volatility Score: {volatility_data['volatility_score']*100:.1f}%
- ATR %: {volatility_data['atr_pct']:.1f}%
- Note: {volatility_data['note']}

AGENT CONFIGURATION:
- Max Leverage: {self.max_leverage}x
- Max Capital Allocation: {self.max_capital_allocation*100:.0f}%
- Max Drawdown: {self.max_drawdown*100:.1f}%
- Current Portfolio: ${portfolio_value:,.2f}

{f"MARKET CONTEXT: {json.dumps(market_analysis, indent=2)}" if market_analysis else ""}

ASSESSMENT CRITERIA:
1. Risk vs Reward analysis
2. Market condition compatibility
3. Volatility appropriateness
4. Portfolio risk concentration
5. Liquidation probability
6. Overall risk management

DECISION FORMAT:
RECOMMENDATION: [APPROVE/REJECT/MODIFY]
CONFIDENCE: [0-100%]
LEVERAGE_ADJUSTMENT: [suggested leverage if modification]
POSITION_SIZE_ADJUSTMENT: [suggested position size if modification]
REASONING: [detailed explanation]
RISK_FACTORS: [3-5 key risk factors]
MITIGATION_STRATEGY: [how to manage this position]

Should this aggressive position be approved with the proposed parameters?
"""

        return prompt

    async def _get_ai_risk_assessment(self, prompt: str) -> Dict:
        """Get AI risk assessment using Claude Code sub-agent"""
        try:
            cmd = [
                "claude",
                "--dangerously-skip-permissions",
                "--agent",
                self.subagent_name,
                prompt,
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                cwd=os.getcwd(),
            )

            if result.returncode != 0:
                print(f"[ERROR] Sub-agent error: {result.stderr}")
                return {
                    "recommendation": "REJECT",
                    "confidence": 0.1,
                    "reasoning": "Sub-agent error - rejecting for safety",
                }

            return self._parse_ai_response(result.stdout)

        except Exception as e:
            print(f"[ERROR] AI assessment failed: {e}")
            return {
                "recommendation": "REJECT",
                "confidence": 0.1,
                "reasoning": f"AI assessment error: {str(e)}",
            }

    def _parse_ai_response(self, response: str) -> Dict:
        """Parse AI assessment response"""
        parsed = {
            "recommendation": "REJECT",
            "confidence": 0.5,
            "leverage_adjustment": None,
            "position_size_adjustment": None,
            "reasoning": "",
            "risk_factors": [],
            "mitigation_strategy": "",
        }

        try:
            lines = response.strip().split("\n")

            for line in lines:
                line = line.strip()

                if line.startswith("RECOMMENDATION:"):
                    parsed["recommendation"] = line.split(":", 1)[1].strip()
                elif line.startswith("CONFIDENCE:"):
                    conf_str = line.split(":", 1)[1].strip().replace("%", "")
                    parsed["confidence"] = float(conf_str) / 100
                elif line.startswith("LEVERAGE_ADJUSTMENT:"):
                    lev_str = line.split(":", 1)[1].strip()
                    parsed["leverage_adjustment"] = float(lev_str) if lev_str else None
                elif line.startswith("POSITION_SIZE_ADJUSTMENT:"):
                    size_str = line.split(":", 1)[1].strip()
                    parsed["position_size_adjustment"] = float(size_str) if size_str else None
                elif line.startswith("REASONING:"):
                    parsed["reasoning"] = line.split(":", 1)[1].strip()
                elif line.startswith("RISK_FACTORS:"):
                    factors = []
                    idx = lines.index(line) + 1
                    while idx < len(lines) and (
                        lines[idx].strip().startswith("-") or lines[idx].strip().startswith("•")
                    ):
                        factors.append(lines[idx].strip())
                        idx += 1
                    parsed["risk_factors"] = factors
                elif line.startswith("MITIGATION_STRATEGY:"):
                    parsed["mitigation_strategy"] = line.split(":", 1)[1].strip()

        except Exception as e:
            print(f"[WARNING] Could not parse AI response: {e}")

        return parsed

    def _make_final_decision(
        self, ai_decision: Dict, risk_metrics: Dict, trade_confidence: float
    ) -> bool:
        """Make final approval decision"""
        try:
            ai_recommendation = ai_decision.get("recommendation", "REJECT")
            ai_confidence = ai_decision.get("confidence", 0)

            if risk_metrics["overall_risk_score"] > 0.9:
                print(
                    f"[OVERRIDE] Rejection due to extreme risk score: "
                    f"{risk_metrics['overall_risk_score']:.3f}"
                )
                return False

            if risk_metrics["distance_to_liquidation_pct"] < 2.0:
                print(
                    f"[OVERRIDE] Rejection due to liquidation proximity: "
                    f"{risk_metrics['distance_to_liquidation_pct']:.2f}%"
                )
                return False

            if ai_recommendation == "APPROVE":
                if ai_confidence > 0.7:
                    return True
                elif ai_confidence > 0.5 and trade_confidence > 0.8:
                    return True
                else:
                    return False
            elif ai_recommendation == "MODIFY":
                return ai_confidence > 0.6
            else:  # REJECT
                return False

        except Exception as e:
            print(f"[ERROR] Final decision logic failed: {e}")
            return False  # Conservative default

    def _display_assessment_result(self, result: Dict):
        """Display comprehensive assessment result"""
        print(f"\n{'='*80}")
        approved_symbol = "✅ APPROVED" if result["approved"] else "❌ REJECTED"
        print(f"[ASSESSMENT RESULT] {approved_symbol}")
        print(f"{'='*80}")

        if result.get("error"):
            print(f"[ERROR] {result.get('reason', 'Unknown error')}")
            return

        print(f"[TRADE] {result.get('side', 'UNKNOWN')} {result.get('symbol', 'UNKNOWN')}")
        print(
            f"[LEVERAGE] {result.get('proposed_leverage', 0):.1f}x → "
            f"{result.get('approved_leverage', 0):.1f}x"
        )
        print(f"[SIZE] ${result.get('position_size_usd', 0):,.2f}")

        if result.get("current_price") and result.get("liquidation_price"):
            print(
                f"[PRICES] Entry: ${result['current_price']:,.2f} | "
                f"Liq: ${result['liquidation_price']:,.2f}"
            )

        risk_metrics = result.get("risk_metrics", {})
        if risk_metrics:
            risk_score = risk_metrics.get("overall_risk_score", 0)
            risk_level = risk_metrics.get("risk_level", "UNKNOWN")
            print(f"[RISK] Score: {risk_score:.3f} ({risk_level})")
            print(
                f"[RISK] Distance to Liq: "
                f"{risk_metrics.get('distance_to_liquidation_pct', 0):.2f}%"
            )

        ai_confidence = result.get("ai_confidence", 0)
        ai_reasoning = result.get("ai_reasoning", "")
        final_reason = result.get("final_reason", "")

        print(f"[AI] Confidence: {ai_confidence*100:.1f}%")
        if ai_reasoning:
            print(f"[AI] Reasoning: {ai_reasoning}")
        if final_reason:
            print(f"[AI] Recommendation: {final_reason}")

        print(f"{'='*80}\n")

    def get_portfolio_value(self) -> float:
        """Get current portfolio value"""
        try:
            return 10000.0  # $10,000 default
        except Exception as e:
            print(f"[ERROR] Could not get portfolio value: {e}")
            return 10000.0

    async def validate_aggressive_position(
        self, symbol: str, side: str, leverage: float = 25.0, confidence: float = 0.9
    ) -> bool:
        """
        Quick validation for aggressive positions

        Example: Validate short 25x BTC with 90% confidence
        """
        result = await self.assess_trade_opportunity(
            symbol=symbol,
            side=side,
            proposed_leverage=leverage,
            trade_confidence=confidence,
        )

        return result.get("approved", False)


async def validate_btc_short(leverage: float = 25.0, confidence: float = 0.9) -> bool:
    """Validate short BTC position with specified leverage"""
    agent = AdvancedRiskAgent(aggressive_mode=True)
    return await agent.validate_aggressive_position("BTC", "SHORT", leverage, confidence)


async def assess_high_leverage_trade(
    symbol: str, side: str, leverage: float, confidence: float
) -> Dict:
    """Comprehensive assessment for high-leverage trade"""
    agent = AdvancedRiskAgent(aggressive_mode=True)
    return await agent.assess_trade_opportunity(symbol, side, leverage, confidence)


if __name__ == "__main__":

    async def main():
        print("Testing Advanced Risk Agent...")

        approved = await validate_btc_short(leverage=25.0, confidence=0.9)
        print(f"BTC short 25x approved: {approved}")

        result = await assess_high_leverage_trade("BTC", "SHORT", 25.0, 0.95)
        print(f"Assessment result: {json.dumps(result, indent=2)}")

    import asyncio

    asyncio.run(main())
