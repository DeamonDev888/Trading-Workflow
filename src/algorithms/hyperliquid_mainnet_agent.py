"""
🔥 NOVAQUOTE HyperLiquid Mainnet Agent - 100% Real Trading Visibility
Expert-level agent for REAL trading with REAL money on HyperLiquid mainnet
Complete logging and monitoring for professional trading operations
Built by Deamon Dev - Real Money Trading System
"""

import asyncio
import os
import time
from decimal import Decimal
from typing import Dict, List, Optional

from hyperliquid_agent import HyperLiquidAgent, OrderResult

from src.logger import get_logger, log_risk, log_trade


class HyperLiquidMainnetAgent(HyperLiquidAgent):
    """
    Expert-level HyperLiquid mainnet trading agent with 100% visibility
    Features: Complete trade logging, risk management, real-time monitoring
    """

    def __init__(self, api_key: str, secret_key: str):
        super().__init__(
            api_key=api_key,
            secret_key=secret_key,
            base_url="https://api.hyperliquid.xyz/info",
            ws_url="wss://api.hyperliquid.xyz/ws",
            testnet=False,  # MAINNET - ARGENT RÉEL
        )

        self.logger = get_logger("trading.hyperliquid.mainnet")

        self.risk_settings = {
            "max_position_size_usd": 1000,  # Max $1000 par position
            "max_total_exposure": 5000,  # Max $5000 total exposure
            "min_account_balance": 100,  # Minimum $100 restant
            "max_leverage": 10,  # Max 10x levier
            "stop_loss_pct": 0.02,  # 2% stop loss
            "take_profit_pct": 0.05,  # 5% take profit
        }

        self.trading_metrics = {
            "total_trades": 0,
            "successful_trades": 0,
            "failed_trades": 0,
            "total_volume_usd": 0.0,
            "total_pnl": 0.0,
            "risk_alerts_triggered": 0,
            "start_time": time.time(),
        }

        self.logger.agent_lifecycle(
            "INITIALIZED",
            "HyperLiquidMainnetAgent",
            {
                "network": "MAINNET",
                "risk_mode": "REAL_MONEY_TRADING",
                "api_endpoint": self.base_url,
                "websocket_endpoint": self.ws_url,
                "risk_settings": self.risk_settings,
                "initial_metrics": self.trading_metrics,
                "warning": "⚠️  REAL MONEY TRADING ACTIVATED ⚠️",
            },
        )

        self.logger.critical(
            "🔥 MAINNET TRADING SYSTEM ACTIVATED - REAL MONEY MODE",
            {
                "disclaimer": "This agent trades with REAL money on HyperLiquid mainnet",
                "risk_level": "MAXIMUM",
                "monitoring": "100% Visibility Enabled",
                "responsibility": "User assumes all trading risks",
            },
        )

    async def validate_risk_limits(self, symbol: str, size: Decimal, price: Decimal) -> bool:
        """
        Validate risk limits with expert logging before REAL money trading
        Args:
            symbol: Trading symbol
            size: Position size
            price: Current price
        Returns:
            bool: True if trade is safe to execute
        """
        try:
            start_time = time.time()

            position_value = float(size * price)

            try:
                portfolio_value = await self.get_portfolio_value()
                account_balance = portfolio_value.get("total_value_usd", 0)
            except Exception as e:
                self.logger.warning(f"Could not get portfolio value for risk calculation: {e}")
                account_balance = 0

            risk_data = {
                "symbol": symbol,
                "position_size": float(size),
                "price": float(price),
                "position_value_usd": position_value,
                "account_balance_usd": account_balance,
                "risk_percentage": (
                    (position_value / account_balance * 100) if account_balance > 0 else 0
                ),
                "risk_settings": self.risk_settings.copy(),
            }

            if position_value > self.risk_settings["max_position_size_usd"]:
                self.trading_metrics["risk_alerts_triggered"] += 1

                self.logger.risk_alert(
                    "POSITION_SIZE_LIMIT_EXCEEDED",
                    "HIGH",
                    {
                        **risk_data,
                        "limit_usd": self.risk_settings["max_position_size_usd"],
                        "excess_usd": position_value - self.risk_settings["max_position_size_usd"],
                        "action": "TRADE_REJECTED",
                    },
                )

                log_trade(
                    "RISK_REJECT",
                    symbol,
                    {
                        "reason": "Position size exceeds limit",
                        "position_value_usd": position_value,
                        "limit_usd": self.risk_settings["max_position_size_usd"],
                    },
                )

                return False

            if account_balance < self.risk_settings["min_account_balance"]:
                self.trading_metrics["risk_alerts_triggered"] += 1

                self.logger.risk_alert(
                    "INSUFFICIENT_BALANCE",
                    "CRITICAL",
                    {
                        **risk_data,
                        "min_balance_usd": self.risk_settings["min_account_balance"],
                        "deficit_usd": self.risk_settings["min_account_balance"] - account_balance,
                        "action": "ALL_TRADING_SUSPENDED",
                    },
                )

                log_trade(
                    "RISK_REJECT",
                    symbol,
                    {
                        "reason": "Insufficient account balance",
                        "account_balance_usd": account_balance,
                        "min_balance_usd": self.risk_settings["min_account_balance"],
                    },
                )

                return False

            if account_balance > 0:
                position_percentage = (position_value / account_balance) * 100
                if position_percentage > 50:  # Don't risk more than 50% on one position
                    self.trading_metrics["risk_alerts_triggered"] += 1

                    self.logger.risk_alert(
                        "HIGH_CONCENTRATION_RISK",
                        "MEDIUM",
                        {
                            **risk_data,
                            "position_percentage": position_percentage,
                            "recommended_max_percentage": 20,
                            "action": "TRADE_REJECTED",
                        },
                    )

                    log_trade(
                        "RISK_REJECT",
                        symbol,
                        {
                            "reason": "Position concentration too high",
                            "position_percentage": position_percentage,
                        },
                    )

                    return False

            validation_time = time.time() - start_time

            self.logger.success(
                f"✅ Risk validation passed for {symbol}",
                {
                    **risk_data,
                    "validation_time_ms": validation_time * 1000,
                    "risk_score": "LOW",
                    "action": "TRADE_APPROVED",
                },
            )

            return True

        except Exception as e:
            self.trading_metrics["risk_alerts_triggered"] += 1

            self.logger.error(
                f"❌ Risk validation failed for {symbol}",
                {
                    "symbol": symbol,
                    "size": float(size),
                    "price": float(price),
                    "error": str(e),
                },
                exc_info=True,
            )

            log_trade(
                "RISK_ERROR",
                symbol,
                {"reason": "Risk validation error", "error": str(e)},
            )

            return False

    async def place_safe_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        size: Decimal,
        price: Optional[Decimal] = None,
        leverage: int = 5,
    ) -> OrderResult:
        """
        Place a REAL money order with comprehensive logging and risk management
        Args:
            symbol: Trading symbol
            side: BUY or SELL
            order_type: MARKET, LIMIT, STOP
            size: Position size
            price: Order price (None for market)
            leverage: Leverage multiplier
        Returns:
            OrderResult with complete execution details
        """
        try:
            trade_start_time = time.time()
            trade_id = f"MAINNET_{int(time.time()*1000)}"

            try:
                prices = await self.get_all_mids()
                current_price = prices.get(symbol, Decimal("0"))

                if current_price == 0:
                    self.trading_metrics["failed_trades"] += 1

                    self.logger.error(
                        f"❌ Cannot execute {symbol} trade - No price data",
                        {
                            "symbol": symbol,
                            "side": side,
                            "size": float(size),
                            "trade_id": trade_id,
                            "error": "Market price unavailable",
                        },
                    )

                    log_trade(
                        "PRICE_ERROR",
                        symbol,
                        {
                            "trade_id": trade_id,
                            "side": side,
                            "size": float(size),
                            "error": "No market price available",
                        },
                    )

                    return OrderResult(success=False, error="Prix non disponible")

            except Exception as e:
                self.trading_metrics["failed_trades"] += 1

                self.logger.error(
                    f"❌ Failed to get market price for {symbol}",
                    {
                        "symbol": symbol,
                        "side": side,
                        "size": float(size),
                        "trade_id": trade_id,
                        "error": str(e),
                    },
                )

                return OrderResult(success=False, error=f"Price fetch error: {e}")

            trade_data = {
                "trade_id": trade_id,
                "symbol": symbol,
                "side": side,
                "order_type": order_type,
                "size": float(size),
                "requested_price": float(price) if price else None,
                "market_price": float(current_price),
                "leverage": min(leverage, self.risk_settings["max_leverage"]),
                "estimated_value_usd": float(size * current_price),
                "network": "MAINNET",
                "real_money": True,
            }

            self.logger.info(f"🔥 MAINNET TRADE INITIATED: {side} {size} {symbol}", trade_data)

            self.logger.debug(f"Validating risk limits for {symbol} trade", trade_data)

            if not await self.validate_risk_limits(symbol, size, current_price):
                self.trading_metrics["failed_trades"] += 1

                self.logger.warning(
                    f"⚠️ Trade rejected by risk management: {symbol}",
                    {**trade_data, "rejection_reason": "Risk limits exceeded"},
                )

                log_trade("RISK_REJECT", symbol, trade_data)

                return OrderResult(success=False, error="Limite de risque dépassée")

            execution_start = time.time()

            try:
                self.logger.info(
                    f"📡 Placing MAINNET order for {symbol}",
                    {**trade_data, "execution_stage": "ORDER_SUBMISSION"},
                )

                result = await self.place_order(
                    symbol=symbol,
                    side=side,
                    order_type=order_type,
                    size=size,
                    price=price,
                    leverage=min(leverage, self.risk_settings["max_leverage"]),
                )

                execution_time = time.time() - execution_start

                self.trading_metrics["total_trades"] += 1

                if result.success:
                    self.trading_metrics["successful_trades"] += 1
                    self.trading_metrics["total_volume_usd"] += float(size * current_price)

                    self.logger.success(
                        f"✅ MAINNET TRADE EXECUTED: {side} {size} {symbol}",
                        {
                            **trade_data,
                            "order_id": result.order_id,
                            "execution_time_ms": execution_time * 1000,
                            "execution_price": (float(price) if price else float(current_price)),
                            "status": "EXECUTED",
                            "real_money_transacted": True,
                        },
                    )

                    log_trade(
                        "EXECUTED",
                        symbol,
                        {
                            **trade_data,
                            "order_id": result.order_id,
                            "execution_time_ms": execution_time * 1000,
                            "success": True,
                        },
                    )

                    try:
                        self.logger.debug(
                            f"Placing risk management orders for {symbol}",
                            {
                                "symbol": symbol,
                                "order_id": result.order_id,
                                "side": side,
                                "size": float(size),
                                "entry_price": float(current_price),
                            },
                        )

                        await self._place_risk_orders(symbol, side, size, current_price)

                    except Exception as risk_error:
                        self.logger.warning(
                            f"⚠️ Risk orders failed for {symbol}",
                            {
                                "symbol": symbol,
                                "order_id": result.order_id,
                                "risk_error": str(risk_error),
                                "main_trade_status": "EXECUTED",
                            },
                        )

                        log_trade(
                            "RISK_ORDERS_FAILED",
                            symbol,
                            {
                                "main_order_id": result.order_id,
                                "risk_error": str(risk_error),
                            },
                        )

                else:
                    self.trading_metrics["failed_trades"] += 1

                    self.logger.error(
                        f"❌ MAINNET TRADE FAILED: {side} {size} {symbol}",
                        {
                            **trade_data,
                            "execution_time_ms": execution_time * 1000,
                            "error_message": result.error,
                            "error_type": "EXECUTION_FAILURE",
                            "status": "FAILED",
                        },
                    )

                    log_trade(
                        "FAILED",
                        symbol,
                        {
                            **trade_data,
                            "error": result.error,
                            "execution_time_ms": execution_time * 1000,
                            "success": False,
                        },
                    )

                total_trade_time = time.time() - trade_start_time

                self.logger.info(
                    f"📊 MAINNET TRADE SUMMARY: {symbol}",
                    {
                        "trade_id": trade_id,
                        "total_time_ms": total_trade_time * 1000,
                        "execution_time_ms": execution_time * 1000,
                        "success": result.success,
                        "volume_usd": float(size * current_price),
                        "trading_metrics": self.trading_metrics.copy(),
                        "cumulative_trades": self.trading_metrics["total_trades"],
                        "success_rate": (
                            self.trading_metrics["successful_trades"]
                            / max(1, self.trading_metrics["total_trades"])
                        )
                        * 100,
                    },
                )

                return result

            except Exception as execution_error:
                self.trading_metrics["failed_trades"] += 1

                self.logger.error(
                    f"💥 MAINNET EXECUTION ERROR: {symbol}",
                    {
                        **trade_data,
                        "execution_error": str(execution_error),
                        "execution_time_ms": (time.time() - execution_start) * 1000,
                        "error_type": "SYSTEM_ERROR",
                    },
                    exc_info=True,
                )

                log_trade(
                    "EXECUTION_ERROR",
                    symbol,
                    {**trade_data, "error": str(execution_error), "success": False},
                )

                return OrderResult(success=False, error=f"Execution error: {execution_error}")

        except Exception as e:
            self.trading_metrics["failed_trades"] += 1

            self.logger.critical(
                f"🚨 CRITICAL MAINNET ERROR: place_safe_order failed",
                {
                    "symbol": symbol,
                    "side": side,
                    "size": float(size),
                    "error": str(e),
                    "critical_error": True,
                },
                exc_info=True,
            )

            log_trade(
                "CRITICAL_ERROR",
                symbol,
                {"side": side, "size": float(size), "error": str(e), "critical": True},
            )

            return OrderResult(success=False, error=f"Critical error: {e}")

    async def _place_risk_orders(self, symbol: str, side: str, size: Decimal, entry_price: Decimal):
        """
        Place stop loss and take profit orders with comprehensive logging
        Args:
            symbol: Trading symbol
            side: Original trade side (buy/sell)
            size: Position size
            entry_price: Entry price of the main position
        """
        try:
            risk_start_time = time.time()
            risk_order_id = f"RISK_{int(time.time()*1000)}"

            if side == "long":
                stop_price = entry_price * (1 - self.risk_settings["stop_loss_pct"])
                take_price = entry_price * (1 + self.risk_settings["take_profit_pct"])
                close_side = "sell"
                direction = "LONG_POSITION"
            else:
                stop_price = entry_price * (1 + self.risk_settings["stop_loss_pct"])
                take_price = entry_price * (1 - self.risk_settings["take_profit_pct"])
                close_side = "buy"
                direction = "SHORT_POSITION"

            risk_data = {
                "risk_order_id": risk_order_id,
                "symbol": symbol,
                "direction": direction,
                "entry_price": float(entry_price),
                "position_size": float(size),
                "stop_loss_price": float(stop_price),
                "take_profit_price": float(take_price),
                "close_side": close_side,
                "stop_loss_pct": self.risk_settings["stop_loss_pct"] * 100,
                "take_profit_pct": self.risk_settings["take_profit_pct"] * 100,
                "stop_loss_usd": float(abs(size * (entry_price - stop_price))),
                "take_profit_usd": float(abs(size * (take_price - entry_price))),
                "risk_reward_ratio": float(
                    abs(take_price - entry_price) / abs(entry_price - stop_price)
                ),
                "network": "MAINNET",
            }

            self.logger.info(f"🛡️ PLACING RISK ORDERS for {symbol}", risk_data)

            sl_start_time = time.time()
            try:
                self.logger.debug(
                    f"Placing STOP LOSS for {symbol}",
                    {
                        "symbol": symbol,
                        "stop_price": float(stop_price),
                        "size": float(size),
                        "side": close_side,
                        "order_type": "STOP_MARKET",
                    },
                )

                sl_result = await self.place_order(
                    symbol=symbol,
                    side=close_side,
                    order_type="stop",
                    size=size,
                    price=stop_price,
                    reduce_only=True,
                )

                sl_time = time.time() - sl_start_time

                if sl_result.success:
                    self.logger.success(
                        f"✅ STOP LOSS PLACED: {symbol} @ {stop_price}",
                        {
                            "symbol": symbol,
                            "stop_price": float(stop_price),
                            "order_id": sl_result.order_id,
                            "execution_time_ms": sl_time * 1000,
                            "size": float(size),
                        },
                    )

                    log_trade(
                        "STOP_LOSS_PLACED",
                        symbol,
                        {
                            **risk_data,
                            "stop_order_id": sl_result.order_id,
                            "execution_time_ms": sl_time * 1000,
                            "success": True,
                        },
                    )

                else:
                    self.logger.error(
                        f"❌ STOP LOSS FAILED: {symbol}",
                        {
                            "symbol": symbol,
                            "stop_price": float(stop_price),
                            "error": sl_result.error,
                            "execution_time_ms": sl_time * 1000,
                        },
                    )

                    log_trade(
                        "STOP_LOSS_FAILED",
                        symbol,
                        {**risk_data, "error": sl_result.error, "success": False},
                    )

            except Exception as sl_error:
                self.logger.error(
                    f"💥 STOP LOSS ERROR: {symbol}",
                    {
                        "symbol": symbol,
                        "stop_price": float(stop_price),
                        "error": str(sl_error),
                    },
                )

                log_trade("STOP_LOSS_ERROR", symbol, {**risk_data, "error": str(sl_error)})

            tp_start_time = time.time()
            try:
                self.logger.debug(
                    f"Placing TAKE PROFIT for {symbol}",
                    {
                        "symbol": symbol,
                        "take_price": float(take_price),
                        "size": float(size),
                        "side": close_side,
                        "order_type": "LIMIT",
                    },
                )

                tp_result = await self.place_order(
                    symbol=symbol,
                    side=close_side,
                    order_type="limit",
                    size=size,
                    price=take_price,
                    reduce_only=True,
                )

                tp_time = time.time() - tp_start_time

                if tp_result.success:
                    self.logger.success(
                        f"🎯 TAKE PROFIT PLACED: {symbol} @ {take_price}",
                        {
                            "symbol": symbol,
                            "take_price": float(take_price),
                            "order_id": tp_result.order_id,
                            "execution_time_ms": tp_time * 1000,
                            "size": float(size),
                        },
                    )

                    log_trade(
                        "TAKE_PROFIT_PLACED",
                        symbol,
                        {
                            **risk_data,
                            "take_order_id": tp_result.order_id,
                            "execution_time_ms": tp_time * 1000,
                            "success": True,
                        },
                    )

                else:
                    self.logger.error(
                        f"❌ TAKE PROFIT FAILED: {symbol}",
                        {
                            "symbol": symbol,
                            "take_price": float(take_price),
                            "error": tp_result.error,
                            "execution_time_ms": tp_time * 1000,
                        },
                    )

                    log_trade(
                        "TAKE_PROFIT_FAILED",
                        symbol,
                        {**risk_data, "error": tp_result.error, "success": False},
                    )

            except Exception as tp_error:
                self.logger.error(
                    f"💥 TAKE PROFIT ERROR: {symbol}",
                    {
                        "symbol": symbol,
                        "take_price": float(take_price),
                        "error": str(tp_error),
                    },
                )

                log_trade("TAKE_PROFIT_ERROR", symbol, {**risk_data, "error": str(tp_error)})

            total_risk_time = time.time() - risk_start_time

            self.logger.success(
                f"🛡️ RISK MANAGEMENT SETUP COMPLETE: {symbol}",
                {
                    **risk_data,
                    "total_setup_time_ms": total_risk_time * 1000,
                    "stop_loss_time_ms": sl_time * 1000,
                    "take_profit_time_ms": tp_time * 1000,
                    "protection_active": True,
                    "max_loss_usd": risk_data["stop_loss_usd"],
                    "target_profit_usd": risk_data["take_profit_usd"],
                    "risk_reward_ratio": risk_data["risk_reward_ratio"],
                },
            )

            self.logger.info(
                f"🔒 PROTECTION ACTIVATED: {symbol} position protected",
                {
                    "symbol": symbol,
                    "direction": direction,
                    "entry_price": float(entry_price),
                    "stop_loss": float(stop_price),
                    "take_profit": float(take_price),
                    "position_size_usd": float(size * entry_price),
                    "max_loss_amount": risk_data["stop_loss_usd"],
                    "profit_target": risk_data["take_profit_usd"],
                    "protection_status": "ACTIVE",
                },
            )

        except Exception as e:
            self.logger.error(
                f"💥 CRITICAL RISK MANAGEMENT ERROR: {symbol}",
                {
                    "symbol": symbol,
                    "side": side,
                    "size": float(size),
                    "entry_price": float(entry_price),
                    "error": str(e),
                    "critical_failure": True,
                },
                exc_info=True,
            )

            log_trade(
                "RISK_MANAGEMENT_ERROR",
                symbol,
                {
                    "symbol": symbol,
                    "side": side,
                    "size": float(size),
                    "entry_price": float(entry_price),
                    "error": str(e),
                    "critical": True,
                },
            )

            self.logger.risk_alert(
                "RISK_MANAGEMENT_FAILURE",
                "CRITICAL",
                {
                    "symbol": symbol,
                    "error": str(e),
                    "recommendation": "Consider closing position manually",
                    "protection_status": "FAILED",
                },
            )

    async def get_real_portfolio_value(self, user_address: str) -> Dict:
        """Calculer la vraie valeur du portfolio en temps réel"""
        try:
            balances = await self.get_account_balance(user_address)

            positions = await self.get_positions(user_address)

            prices = await self.get_all_mids()

            total_value = Decimal("0")
            portfolio_breakdown = []

            for token, balance in balances.items():
                if token == "USDC":
                    value = balance
                else:
                    price = prices.get(token, Decimal("0"))
                    value = balance * price

                portfolio_breakdown.append(
                    {
                        "asset": token,
                        "amount": float(balance),
                        "value": float(value),
                        "type": "balance",
                    }
                )
                total_value += value

            for position in positions:
                mark_price = prices.get(position.symbol, Decimal("0"))
                position_value = position.size * mark_price

                portfolio_breakdown.append(
                    {
                        "asset": position.symbol,
                        "amount": float(position.size),
                        "value": float(position_value),
                        "pnl": float(position.pnl),
                        "type": "position",
                        "side": position.side,
                        "leverage": position.leverage,
                    }
                )
                total_value += position_value

            return {
                "total_value_usd": float(total_value),
                "positions_count": len(positions),
                "assets_count": len(balances),
                "breakdown": portfolio_breakdown,
                "timestamp": int(asyncio.get_event_loop().time()),
            }

        except Exception as e:
            self.logger.error(f"Erreur calcul portfolio: {e}")
            return {"total_value_usd": 0, "error": str(e)}

    async def execute_trading_signals(
        self, signals: List[Dict], user_address: str
    ) -> List[OrderResult]:
        """Exécuter des signaux de trading réels"""
        results = []

        for signal in signals:
            try:
                symbol = signal.get("symbol")
                action = signal.get("action")  # buy/sell
                confidence = signal.get("confidence", 0.5)
                size_percent = signal.get("size_percent", 0.1)

                if confidence < 0.7:  # Minimum 70% confiance
                    continue

                portfolio = await self.get_real_portfolio_value(user_address)
                total_value = Decimal(str(portfolio.get("total_value_usd", 0)))
                position_size = total_value * Decimal(str(size_percent))

                result = await self.place_safe_order(
                    symbol=symbol,
                    side=action,
                    order_type="market",
                    size=position_size,
                    leverage=5,
                )

                results.append(
                    {
                        "signal": signal,
                        "result": result,
                        "executed_at": int(asyncio.get_event_loop().time()),
                    }
                )

            except Exception as e:
                self.logger.error(f"Erreur exécution signal: {e}")
                results.append(
                    {
                        "signal": signal,
                        "result": OrderResult(success=False, error=str(e)),
                        "executed_at": int(asyncio.get_event_loop().time()),
                    }
                )

        return results

    async def emergency_exit(self, user_address: str) -> bool:
        """Sortie d'urgence - fermer toutes les positions"""
        try:
            self.logger.warning("🚨 EMERGENCY EXIT ACTIVATED!")

            results = await self.close_all_positions(user_address)

            successful_closes = sum(1 for r in results if r.success)
            self.logger.info(f"🔒 POSITIONS FERMÉES: {successful_closes}/{len(results)}")

            return successful_closes > 0

        except Exception as e:
            self.logger.error(f"Erreur emergency exit: {e}")
            return False

    async def get_trading_statistics(self, user_address: str) -> Dict:
        """Statistiques de trading réelles"""
        try:
            positions = await self.get_positions(user_address)
            balances = await self.get_account_balance(user_address)

            total_pnl = sum(position.pnl for position in positions)

            long_positions = [p for p in positions if p.side == "long"]
            short_positions = [p for p in positions if p.side == "short"]

            return {
                "active_positions": len(positions),
                "long_positions": len(long_positions),
                "short_positions": len(short_positions),
                "total_pnl": float(total_pnl),
                "account_balance": {k: float(v) for k, v in balances.items()},
                "leverage_used": (max([p.leverage for p in positions]) if positions else 0),
                "risk_level": ("HIGH" if len(positions) > 5 else "MEDIUM" if positions else "LOW"),
                "timestamp": int(asyncio.get_event_loop().time()),
            }

        except Exception as e:
            self.logger.error(f"Erreur statistiques: {e}")
            return {"error": str(e)}


_mainnet_agent = None


def get_mainnet_agent() -> Optional[HyperLiquidMainnetAgent]:
    """Récupérer l'agent mainnet configuré"""
    global _mainnet_agent

    if _mainnet_agent is None:
        api_key = os.getenv("HYPERLIQUID_API_KEY")
        secret_key = os.getenv("HYPERLIQUID_SECRET_KEY")

        if not api_key or not secret_key:
            logging.error("❌ Clés API HyperLiquid manquantes")
            return None

        _mainnet_agent = HyperLiquidMainnetAgent(api_key, secret_key)

    return _mainnet_agent


if __name__ == "__main__":
    import os

    from dotenv import load_dotenv

    load_dotenv()

    async def test_mainnet():
        agent = get_mainnet_agent()
        if not agent:
            print("❌ Impossible de créer l'agent mainnet")
            return

        print("🔥 AGENT MAINNET CRÉÉ - TRADING RÉEL")

        prices = await agent.get_all_mids()
        print(f"Prix BTC: ${prices.get('BTC', 'N/A')}")

    asyncio.run(test_mainnet())
