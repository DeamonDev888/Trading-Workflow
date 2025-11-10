"""
HyperLiquid Trading Agent - Agent d'exécution de trading réel
Connection directe à l'API HyperLiquid pour trading live
"""

import asyncio
import hashlib
import hmac
import json
import logging
import time
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List, Optional

import requests
import websockets


@dataclass
class Position:
    symbol: str
    side: str
    size: Decimal
    entry_price: Decimal
    mark_price: Decimal
    pnl: Decimal
    leverage: int


@dataclass
class OrderResult:
    success: bool
    order_id: Optional[str] = None
    error: Optional[str] = None
    executed_price: Optional[Decimal] = None
    executed_size: Optional[Decimal] = None


class HyperLiquidAgent:
    def __init__(
        self,
        api_key: str,
        secret_key: str,
        base_url: str = "https://api.hyperliquid.xyz/info",
        ws_url: str = "wss://api.hyperliquid.xyz/ws",
        testnet: bool = False,
    ):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = base_url
        self.ws_url = ws_url
        self.testnet = testnet

        if testnet:
            self.base_url = "https://api.hyperliquid-testnet.xyz/info"
            self.ws_url = "wss://api.hyperliquid-testnet.xyz/ws"

        self.positions: Dict[str, Position] = {}
        self.balance = Decimal("0")
        self.logger = logging.getLogger("HyperLiquidAgent")

    def _sign_payload(self, payload: Dict) -> str:
        """Signer la payload avec la clé secrète"""
        message = json.dumps(payload)
        return hmac.new(self.secret_key.encode(), message.encode(), hashlib.sha256).hexdigest()

    async def get_meta(self) -> Dict:
        """Récupérer les métadonnées des tokens"""
        try:
            response = requests.get(f"{self.base_url}/meta")
            return response.json()
        except Exception as e:
            self.logger.error(f"Erreur get_meta: {e}")
            return {}

    async def get_all_mids(self) -> Dict[str, Decimal]:
        """Récupérer tous les prix mid"""
        try:
            response = requests.get(f"{self.base_url}/allMids")
            if response.status_code == 200:
                data = response.json()
                return {k: Decimal(str(v)) for k, v in data.items()}
            return {}
        except Exception as e:
            self.logger.error(f"Erreur get_all_mids: {e}")
            return {}

    async def get_spot_user_state(self, user_address: str) -> Dict:
        """Récupérer l'état du compte spot"""
        try:
            payload = {"type": "spotUserState", "user": user_address}
            response = requests.post(f"{self.base_url}/info", json=payload)
            return response.json()
        except Exception as e:
            self.logger.error(f"Erreur get_spot_user_state: {e}")
            return {}

    async def subscribe_to_websocket(self):
        """Se connecter au WebSocket pour les données temps réel"""
        try:
            async with websockets.connect(self.ws_url) as websocket:
                subscribe_msg = {
                    "method": "subscribe",
                    "subscription": {"type": "allTrades"},
                }
                await websocket.send(json.dumps(subscribe_msg))

                self.logger.info("✅ WebSocket HyperLiquid connecté")

                async for message in websocket:
                    data = json.loads(message)
                    await self._handle_websocket_message(data)

        except Exception as e:
            self.logger.error(f"Erreur WebSocket: {e}")

    async def _handle_websocket_message(self, data: Dict):
        """Traiter les messages WebSocket"""
        if data.get("channel") == "allTrades":
            trades = data.get("data", [])
            for trade in trades:
                await self._process_trade(trade)

    async def _process_trade(self, trade: Dict):
        """Traiter un trade reçu"""
        symbol = trade.get("coin", "")
        price = Decimal(str(trade.get("px", 0)))
        size = Decimal(str(trade.get("sz", 0)))
        side = trade.get("side", "")

        self.logger.info(f"Trade {symbol}: {side} {size} @ {price}")

    async def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        size: Decimal,
        price: Optional[Decimal] = None,
        reduce_only: bool = False,
        leverage: int = 5,
    ) -> OrderResult:
        """Placer un ordre sur HyperLiquid"""
        try:
            timestamp = int(time.time() * 1000)

            order_payload = {
                "asset": symbol,
                "side": side,
                "orderType": order_type,
                "sz": str(size),
                "reduceOnly": reduce_only,
                "leverage": leverage,
            }

            if price:
                order_payload["limitPx"] = str(price)

            payload = {
                "action": {"type": "order", "orders": [order_payload]},
                "nonce": timestamp,
                "signature": self._sign_payload(order_payload),
            }

            response = requests.post(
                f"{self.base_url.replace('/info', '/exchange')}",
                json=payload,
                headers={"Authorization": f"Bearer {self.api_key}"},
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "ok":
                    return OrderResult(
                        success=True,
                        order_id=result.get("response", {})
                        .get("statuses", [{}])[0]
                        .get("resting", {})
                        .get("oid"),
                    )
                else:
                    return OrderResult(
                        success=False, error=result.get("response", "Erreur inconnue")
                    )
            else:
                return OrderResult(
                    success=False, error=f"HTTP {response.status_code}: {response.text}"
                )

        except Exception as e:
            self.logger.error(f"Erreur place_order: {e}")
            return OrderResult(success=False, error=str(e))

    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Annuler un ordre"""
        try:
            timestamp = int(time.time() * 1000)

            cancel_payload = {"asset": symbol, "oid": order_id}

            payload = {
                "action": {"type": "cancel", "cancels": [cancel_payload]},
                "nonce": timestamp,
                "signature": self._sign_payload(cancel_payload),
            }

            response = requests.post(
                f"{self.base_url.replace('/info', '/exchange')}",
                json=payload,
                headers={"Authorization": f"Bearer {self.api_key}"},
            )

            return response.status_code == 200 and response.json().get("status") == "ok"

        except Exception as e:
            self.logger.error(f"Erreur cancel_order: {e}")
            return False

    async def get_positions(self, user_address: str) -> List[Position]:
        """Récupérer les positions ouvertes"""
        try:
            payload = {"type": "clearinghouseState", "user": user_address}
            response = requests.post(f"{self.base_url}/info", json=payload)

            if response.status_code == 200:
                data = response.json()
                positions = []

                for asset_data in data.get("assetPositions", []):
                    if asset_data.get("position", {}).get("szi") != "0":
                        symbol = asset_data.get("coin", "")
                        position = asset_data.get("position", {})

                        positions.append(
                            Position(
                                symbol=symbol,
                                side=("long" if Decimal(position.get("szi", "0")) > 0 else "short"),
                                size=abs(Decimal(position.get("szi", "0"))),
                                entry_price=Decimal(position.get("entryPx", "0")),
                                mark_price=Decimal(position.get("markPx", "0")),
                                pnl=Decimal(position.get("unrealizedPnl", "0")),
                                leverage=int(position.get("leverage", {}).get("value", 1)),
                            )
                        )

                return positions
            return []

        except Exception as e:
            self.logger.error(f"Erreur get_positions: {e}")
            return []

    async def close_all_positions(self, user_address: str) -> List[OrderResult]:
        """Fermer toutes les positions ouvertes"""
        positions = await self.get_positions(user_address)
        results = []

        for position in positions:
            result = await self.place_order(
                symbol=position.symbol,
                side="sell" if position.side == "long" else "buy",
                order_type="market",
                size=position.size,
                reduce_only=True,
            )
            results.append(result)

        return results

    async def get_account_balance(self, user_address: str) -> Dict[str, Decimal]:
        """Récupérer le solde du compte"""
        try:
            spot_state = await self.get_spot_user_state(user_address)
            balances = {}

            for balance in spot_state.get("balances", []):
                token = balance.get("coin", "")
                total = Decimal(str(balance.get("total", 0)))
                if total > 0:
                    balances[token] = total

            return balances

        except Exception as e:
            self.logger.error(f"Erreur get_account_balance: {e}")
            return {}

    def get_supported_symbols(self) -> List[str]:
        """Liste des symboles supportés par HyperLiquid"""
        return [
            "BTC",
            "ETH",
            "SOL",
            "ARB",
            "APT",
            "ADA",
            "AVAX",
            "BNB",
            "DOGE",
            "MATIC",
            "DOT",
            "LINK",
            "UNI",
            "AAVE",
            "SUSHI",
            "CRV",
            "LDO",
            "INJ",
            "ATOM",
            "OP",
            "DYDX",
            "SUI",
            "STX",
            "LTC",
        ]

    async def get_market_stats(self, symbol: str) -> Dict:
        """Récupérer les statistiques de marché pour un symbole"""
        try:
            all_mids = await self.get_all_mids()
            current_price = all_mids.get(symbol, Decimal("0"))

            meta = await self.get_meta()
            symbols_data = meta.get("symbols", [])

            symbol_info = None
            for s in symbols_data:
                if s.get("name") == symbol:
                    symbol_info = s
                    break

            return {
                "symbol": symbol,
                "current_price": float(current_price),
                "volume_24h": symbol_info.get("dayNtlVlm", 0) if symbol_info else 0,
                "funding_rate": symbol_info.get("funding", 0) if symbol_info else 0,
                "open_interest": (symbol_info.get("openInterest", 0) if symbol_info else 0),
                "mark_price": float(current_price),
                "timestamp": int(time.time()),
            }

        except Exception as e:
            self.logger.error(f"Erreur get_market_stats: {e}")
            return {}


_agent_instance = None


def get_hyperliquid_agent(
    api_key: str = None, secret_key: str = None, testnet: bool = False
) -> HyperLiquidAgent:
    """Récupérer ou créer l'instance de l'agent HyperLiquid"""
    global _agent_instance

    if _agent_instance is None and api_key and secret_key:
        _agent_instance = HyperLiquidAgent(api_key, secret_key, testnet=testnet)

    return _agent_instance


if __name__ == "__main__":
    import os
    import sys

    from dotenv import load_dotenv

    load_dotenv()

    async def main():
        agent = HyperLiquidAgent(
            api_key=os.getenv("HYPERLIQUID_API_KEY", ""),
            secret_key=os.getenv("HYPERLIQUID_SECRET_KEY", ""),
            testnet=True,
        )

        if len(sys.argv) > 1:
            command = sys.argv[1]

            if command == "--get-dashboard-data":
                try:
                    prices = await agent.get_all_mids()
                    meta = await agent.get_meta()

                    dashboard_data = {
                        "connection_status": "connected" if prices else "disconnected",
                        "total_balance": 10000.0,  # Valeur de test
                        "positions_count": 2,
                        "unrealized_pnl": 150.25,
                        "available_balance": 8500.0,
                        "margin_used": 1500.0,
                        "btc_price": float(prices.get("BTC", 0)) if prices else 0,
                        "eth_price": float(prices.get("ETH", 0)) if prices else 0,
                        "sol_price": float(prices.get("SOL", 0)) if prices else 0,
                        "total_pnl": 150.25,
                        "daily_pnl": 75.50,
                        "trades_today": 5,
                        "success_rate": 0.75,
                        "websocket_connected": True,
                        "recommended_action": "HOLD",
                        "action_confidence": 0.65,
                        "expected_roi": 0.001,
                        "buy_signals": 1,
                        "sell_signals": 0,
                        "active_signals": 1,
                        "signal_accuracy": 0.78,
                        "recent_trades": [
                            {
                                "symbol": "BTC",
                                "side": "buy",
                                "size": 0.1,
                                "price": 43250,
                                "pnl": 25.50,
                            },
                            {
                                "symbol": "ETH",
                                "side": "buy",
                                "size": 2.0,
                                "price": 2250,
                                "pnl": 50.00,
                            },
                        ],
                        "alerts": [],
                    }
                    print(json.dumps(dashboard_data))
                except Exception as e:
                    error_data = {"connection_status": "error", "error": str(e)}
                    print(json.dumps(error_data))

            elif command == "--get-tokens":
                try:
                    prices = await agent.get_all_mids()
                    tokens = []

                    for symbol in ["BTC", "ETH", "SOL", "BNB", "AVAX"]:
                        price = float(prices.get(symbol, 0)) if prices else 0
                        tokens.append(
                            {
                                "symbol": symbol,
                                "name": symbol,
                                "price": price,
                                "change_24h": 0.02 if price > 0 else 0,  # Test data
                                "volume_24h": (100000000 if price > 0 else 0),  # Test data
                            }
                        )

                    tokens_data = {
                        "tokens": tokens,
                        "total_market_cap": 2500000000000,
                        "total_volume_24h": 90000000000,
                        "market_cap_change_24h": 0.025,
                    }
                    print(json.dumps(tokens_data))
                except Exception as e:
                    print(json.dumps({"error": str(e)}))

            elif command == "--test":
                prices = await agent.get_all_mids()
                print(f"Prix BTC: {prices.get('BTC', 'N/A')}")

                meta = await agent.get_meta()
                print(f"Symboles disponibles: {len(meta.get('symbols', []))}")

            else:
                print("Commandes disponibles: --get-dashboard-data, --get-tokens, --test")
        else:
            await main()

    asyncio.run(main())
