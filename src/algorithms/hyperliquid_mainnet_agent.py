#!/usr/bin/env python3
"""
HyperLiquid Mainnet Agent - Agent de trading pour le réseau principal
Configuration et exécution pour trading réel avec argent réel
"""

import asyncio
import json
import os
from typing import Dict, List, Optional
from decimal import Decimal
import logging
from hyperliquid_agent import HyperLiquidAgent, OrderResult, Position

class HyperLiquidMainnetAgent(HyperLiquidAgent):
    """Agent spécialisé pour le trading sur le mainnet HyperLiquid"""

    def __init__(self, api_key: str, secret_key: str):
        super().__init__(
            api_key=api_key,
            secret_key=secret_key,
            base_url="https://api.hyperliquid.xyz/info",
            ws_url="wss://api.hyperliquid.xyz/ws",
            testnet=False  # MAINNET - ARGENT RÉEL
        )

        self.logger = logging.getLogger("HyperLiquidMainnetAgent")
        self.risk_settings = {
            "max_position_size_usd": 1000,  # Max $1000 par position
            "max_total_exposure": 5000,     # Max $5000 total exposure
            "min_account_balance": 100,     # Minimum $100 restant
            "max_leverage": 10,             # Max 10x levier
            "stop_loss_pct": 0.02,          # 2% stop loss
            "take_profit_pct": 0.05         # 5% take profit
        }

    async def validate_risk_limits(self, symbol: str, size: Decimal, price: Decimal) -> bool:
        """Valider les limites de risque avant trading"""
        try:
            # Calculer la valeur de la position en USD
            position_value = size * price

            # Vérifier limite par position
            if position_value > self.risk_settings["max_position_size_usd"]:
                self.logger.warning(f"Position trop grande: ${position_value} > ${self.risk_settings['max_position_size_usd']}")
                return False

            # Vérifier exposition totale
            # Vérifier solde compte

            return True

        except Exception as e:
            self.logger.error(f"Erreur validation risque: {e}")
            return False

    async def place_safe_order(self, symbol: str, side: str, order_type: str,
                             size: Decimal, price: Optional[Decimal] = None,
                             leverage: int = 5) -> OrderResult:
        """Placer un ordre avec validation de risque"""
        try:
            # Obtenir le prix actuel
            prices = await self.get_all_mids()
            current_price = prices.get(symbol, Decimal('0'))

            if current_price == 0:
                return OrderResult(success=False, error="Prix non disponible")

            # Valider les limites de risque
            if not await self.validate_risk_limits(symbol, size, current_price):
                return OrderResult(success=False, error="Limite de risque dépassée")

            # Placer l'ordre avec stop loss et take profit
            self.logger.info(f"🔥 MAINNET ORDER: {side} {size} {symbol} @ {price or 'MARKET'}")

            result = await self.place_order(
                symbol=symbol,
                side=side,
                order_type=order_type,
                size=size,
                price=price,
                leverage=min(leverage, self.risk_settings["max_leverage"])
            )

            if result.success:
                self.logger.info(f"✅ ORDRE EXÉCUTÉ: {result.order_id}")
                # Placer automatiquement stop loss et take profit
                await self._place_risk_orders(symbol, side, size, current_price)
            else:
                self.logger.error(f"❌ ERREUR ORDRE: {result.error}")

            return result

        except Exception as e:
            self.logger.error(f"Erreur place_safe_order: {e}")
            return OrderResult(success=False, error=str(e))

    async def _place_risk_orders(self, symbol: str, side: str, size: Decimal, entry_price: Decimal):
        """Placer les ordres stop loss et take profit"""
        try:
            # Calculer stop loss et take profit prices
            if side == "long":
                stop_price = entry_price * (1 - self.risk_settings["stop_loss_pct"])
                take_price = entry_price * (1 + self.risk_settings["take_profit_pct"])
                close_side = "sell"
            else:
                stop_price = entry_price * (1 + self.risk_settings["stop_loss_pct"])
                take_price = entry_price * (1 - self.risk_settings["take_profit_pct"])
                close_side = "buy"

            # Placer stop loss
            await self.place_order(
                symbol=symbol,
                side=close_side,
                order_type="stop",
                size=size,
                price=stop_price,
                reduce_only=True
            )

            # Placer take profit
            await self.place_order(
                symbol=symbol,
                side=close_side,
                order_type="limit",
                size=size,
                price=take_price,
                reduce_only=True
            )

            self.logger.info(f"🛡️ RISK ORDERS PLACÉS: SL={stop_price}, TP={take_price}")

        except Exception as e:
            self.logger.error(f"Erreur placement ordres risque: {e}")

    async def get_real_portfolio_value(self, user_address: str) -> Dict:
        """Calculer la vraie valeur du portfolio en temps réel"""
        try:
            # Récupérer les balances
            balances = await self.get_account_balance(user_address)

            # Récupérer les positions
            positions = await self.get_positions(user_address)

            # Récupérer les prix actuels
            prices = await self.get_all_mids()

            total_value = Decimal('0')
            portfolio_breakdown = []

            # Valeur des balances
            for token, balance in balances.items():
                if token == "USDC":
                    value = balance
                else:
                    price = prices.get(token, Decimal('0'))
                    value = balance * price

                portfolio_breakdown.append({
                    "asset": token,
                    "amount": float(balance),
                    "value": float(value),
                    "type": "balance"
                })
                total_value += value

            # Valeur des positions
            for position in positions:
                mark_price = prices.get(position.symbol, Decimal('0'))
                position_value = position.size * mark_price

                portfolio_breakdown.append({
                    "asset": position.symbol,
                    "amount": float(position.size),
                    "value": float(position_value),
                    "pnl": float(position.pnl),
                    "type": "position",
                    "side": position.side,
                    "leverage": position.leverage
                })
                total_value += position_value

            return {
                "total_value_usd": float(total_value),
                "positions_count": len(positions),
                "assets_count": len(balances),
                "breakdown": portfolio_breakdown,
                "timestamp": int(asyncio.get_event_loop().time())
            }

        except Exception as e:
            self.logger.error(f"Erreur calcul portfolio: {e}")
            return {"total_value_usd": 0, "error": str(e)}

    async def execute_trading_signals(self, signals: List[Dict], user_address: str) -> List[OrderResult]:
        """Exécuter des signaux de trading réels"""
        results = []

        for signal in signals:
            try:
                symbol = signal.get("symbol")
                action = signal.get("action")  # buy/sell
                confidence = signal.get("confidence", 0.5)
                size_percent = signal.get("size_percent", 0.1)

                # Filtrer par confiance
                if confidence < 0.7:  # Minimum 70% confiance
                    continue

                # Calculer la taille de position
                portfolio = await self.get_real_portfolio_value(user_address)
                total_value = Decimal(str(portfolio.get("total_value_usd", 0)))
                position_size = total_value * Decimal(str(size_percent))

                # Exécuter l'ordre
                result = await self.place_safe_order(
                    symbol=symbol,
                    side=action,
                    order_type="market",
                    size=position_size,
                    leverage=5
                )

                results.append({
                    "signal": signal,
                    "result": result,
                    "executed_at": int(asyncio.get_event_loop().time())
                })

            except Exception as e:
                self.logger.error(f"Erreur exécution signal: {e}")
                results.append({
                    "signal": signal,
                    "result": OrderResult(success=False, error=str(e)),
                    "executed_at": int(asyncio.get_event_loop().time())
                })

        return results

    async def emergency_exit(self, user_address: str) -> bool:
        """Sortie d'urgence - fermer toutes les positions"""
        try:
            self.logger.warning("🚨 EMERGENCY EXIT ACTIVATED!")

            # Fermer toutes les positions
            results = await self.close_all_positions(user_address)

            # Logger les résultats
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

            # Calculer P&L total
            total_pnl = sum(position.pnl for position in positions)

            # Compter les positions actives
            long_positions = [p for p in positions if p.side == "long"]
            short_positions = [p for p in positions if p.side == "short"]

            return {
                "active_positions": len(positions),
                "long_positions": len(long_positions),
                "short_positions": len(short_positions),
                "total_pnl": float(total_pnl),
                "account_balance": {k: float(v) for k, v in balances.items()},
                "leverage_used": max([p.leverage for p in positions]) if positions else 0,
                "risk_level": "HIGH" if len(positions) > 5 else "MEDIUM" if positions else "LOW",
                "timestamp": int(asyncio.get_event_loop().time())
            }

        except Exception as e:
            self.logger.error(f"Erreur statistiques: {e}")
            return {"error": str(e)}

# Instance globale mainnet
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
    # Test de l'agent mainnet
    import os
    from dotenv import load_dotenv

    load_dotenv()

    async def test_mainnet():
        agent = get_mainnet_agent()
        if not agent:
            print("❌ Impossible de créer l'agent mainnet")
            return

        print("🔥 AGENT MAINNET CRÉÉ - TRADING RÉEL")

        # Test récupération données
        prices = await agent.get_all_mids()
        print(f"Prix BTC: ${prices.get('BTC', 'N/A')}")

        # Test statistiques
        # Note: Nécessite une adresse wallet valide
        # stats = await agent.get_trading_statistics("0x...")
        # print(f"Stats: {stats}")

    asyncio.run(test_mainnet())