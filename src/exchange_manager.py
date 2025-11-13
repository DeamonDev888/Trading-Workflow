"""
🚀 HyperLiquid Exchange Manager
Built with love by Deamon Dev
Real-time trading data and execution for HyperLiquid DEX
"""
import json
import time
from typing import Any, Dict, List, Optional
import aiohttp

from termcolor import cprint


class HyperLiquidExchangeManager:
    """
    Exchange Manager for HyperLiquid with real-time data and execution
    Unified interface for market data, funding rates, and order management
    """

    def __init__(self, testnet: bool = False):
        """Initialize the Exchange Manager"""
        self.name = "HyperLiquid Exchange Manager"
        self.version = "2.0.0"

        self.testnet = testnet
        self.base_url = "https://api.hyperliquid.xyz/info"
        self.exchange_url = "https://api.hyperliquid.xyz/exchange"

        # Cache pour optimiser les performances
        self._price_cache: Dict[str, Dict] = {}
        self._cache_timeout = 5  # 5 secondes cache
        self._last_cache_update: Dict[str, float] = {}

        # Session HTTP pour performance
        self._session: Optional[aiohttp.ClientSession] = None

        cprint(f"🚀 {self.name} v{self.version} initialized", "cyan")
        cprint(f"   Testnet: {self.testnet}", "cyan")

    async def __aenter__(self):
        """Async context manager entry"""
        if not self._session:
            self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self._session:
            await self._session.close()
            self._session = None

    def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if not self._session:
            raise RuntimeError("Exchange Manager must be used in async context")
        return self._session

    def _is_cache_valid(self, symbol: str) -> bool:
        """Check if cached data is still valid"""
        if symbol not in self._last_cache_update:
            return False
        return (time.time() - self._last_cache_update[symbol]) < self._cache_timeout

    async def get_token_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive token data including price, volume, and market info

        Args:
            symbol: Token symbol (e.g., 'BTC', 'ETH')

        Returns:
            Token data dict or None if failed
        """
        try:
            # Check cache first
            if self._is_cache_valid(symbol):
                cprint(f"[CACHE] Using cached data for {symbol}", "green")
                return self._price_cache[symbol]

            cprint(f"[API] Fetching fresh data for {symbol}", "yellow")

            # Get meta data for universe info
            meta_data = await self.get_meta()
            if not meta_data or 'universe' not in meta_data:
                raise Exception("No universe data available")

            # Find symbol in universe
            symbol_data = None
            for asset in meta_data['universe']:
                if asset.get('name') == symbol:
                    symbol_data = asset
                    break

            if not symbol_data:
                cprint(f"[WARN] Symbol {symbol} not found in universe", "yellow")
                return None

            # Get current price from all mids
            price_data = await self.get_all_mids()
            current_price = price_data.get(symbol, 0.0) if price_data else symbol_data.get('fairPrice', 0.0)

            # Get 24h ticker data
            ticker_data = await self.get_ticker_data(symbol)

            token_info = {
                "symbol": symbol,
                "price": current_price,
                "fairPrice": symbol_data.get('fairPrice', current_price),
                "volume": ticker_data.get('volume', 0.0),
                "change_24h": ticker_data.get('change_24h', 0.0),
                "high_24h": ticker_data.get('high_24h', current_price),
                "low_24h": ticker_data.get('low_24h', current_price),
                "open_interest": ticker_data.get('open_interest', 0.0),
                "funding_rate": ticker_data.get('funding_rate', 0.0),
                "mark_price": current_price,
                "index_price": symbol_data.get('indexPrice', current_price),
                "timestamp": time.time()
            }

            # Update cache
            self._price_cache[symbol] = token_info
            self._last_cache_update[symbol] = time.time()

            cprint(f"[OK] Got data for {symbol}: ${current_price:.2f}", "green")
            return token_info

        except Exception as e:
            cprint(f"[ERROR] Failed to get token data for {symbol}: {e}", "red")
            return None

    async def get_meta(self) -> Optional[Dict[str, Any]]:
        """Get HyperLiquid meta information including universe"""
        try:
            session = self._get_session()

            payload = {"type": "meta"}
            async with session.post(self.base_url, json=payload, timeout=10) as response:
                if response.status != 200:
                    raise Exception(f"Meta API error: {response.status}")

                data = await response.json()
                cprint("[OK] Got universe data", "green")
                return data

        except Exception as e:
            cprint(f"[ERROR] Failed to get meta: {e}", "red")
            return None

    async def get_all_mids(self) -> Optional[Dict[str, float]]:
        """Get all mid prices"""
        try:
            session = self._get_session()

            payload = {"type": "allMids"}
            async with session.post(self.base_url, json=payload, timeout=10) as response:
                if response.status != 200:
                    raise Exception(f"AllMids API error: {response.status}")

                data = await response.json()
                cprint(f"[OK] Got prices for {len(data)} symbols", "green")
                return data

        except Exception as e:
            cprint(f"[ERROR] Failed to get all mids: {e}", "red")
            return None

    async def get_ticker_data(self, symbol: str) -> Dict[str, Any]:
        """Get 24h ticker data for a symbol"""
        try:
            session = self._get_session()

            payload = {
                "type": "ticker24h",
                "coin": symbol
            }

            async with session.post(self.base_url, json=payload, timeout=10) as response:
                if response.status != 200:
                    return {}

                data = await response.json()
                return {
                    "volume": float(data.get('volume24h', 0)),
                    "change_24h": float(data.get('change24h', 0)),
                    "high_24h": float(data.get('high24h', 0)),
                    "low_24h": float(data.get('low24h', 0)),
                    "open_interest": float(data.get('openInterest', 0)),
                }

        except Exception as e:
            cprint(f"[WARN] Failed to get ticker data for {symbol}: {e}", "yellow")
            return {}

    async def get_funding_rate(self, symbol: str) -> Optional[float]:
        """
        Get current funding rate for a symbol

        Args:
            symbol: Token symbol

        Returns:
            Funding rate as float or None if failed
        """
        try:
            session = self._get_session()

            payload = {
                "type": "premium",
                "coin": symbol
            }

            async with session.post(self.base_url, json=payload, timeout=10) as response:
                if response.status != 200:
                    return None

                data = await response.json()
                funding_rate = float(data.get('fundingRate', 0))

                cprint(f"[OK] {symbol} funding rate: {funding_rate:.6f}", "green")
                return funding_rate

        except Exception as e:
            cprint(f"[ERROR] Failed to get funding rate for {symbol}: {e}", "red")
            return None

    async def get_candles(self, symbol: str, timeframe: str = "1h", limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get candlestick data for a symbol

        Args:
            symbol: Token symbol
            timeframe: Time interval ('1m', '5m', '15m', '1h', '4h', '1d')
            limit: Number of candles to fetch

        Returns:
            List of candle data
        """
        try:
            session = self._get_session()

            payload = {
                "type": "candle",
                "req": {
                    "coin": symbol,
                    "interval": timeframe,
                    "num": limit
                }
            }

            async with session.post(self.base_url, json=payload, timeout=15) as response:
                if response.status != 200:
                    raise Exception(f"Candles API error: {response.status}")

                data = await response.json()
                candles = []

                for candle in data:
                    candles.append({
                        "timestamp": candle.get('t', 0),
                        "open": float(candle.get('o', 0)),
                        "high": float(candle.get('h', 0)),
                        "low": float(candle.get('l', 0)),
                        "close": float(candle.get('c', 0)),
                        "volume": float(candle.get('v', 0))
                    })

                cprint(f"[OK] Got {len(candles)} candles for {symbol} ({timeframe})", "green")
                return candles

        except Exception as e:
            cprint(f"[ERROR] Failed to get candles for {symbol}: {e}", "red")
            return []

    async def get_user_state(self, user_address: str) -> Optional[Dict[str, Any]]:
        """
        Get user account state including positions and balances

        Args:
            user_address: User wallet address

        Returns:
            User state data or None if failed
        """
        try:
            session = self._get_session()

            payload = {
                "type": "clearinghouseState",
                "user": user_address
            }

            async with session.post(self.base_url, json=payload, timeout=10) as response:
                if response.status != 200:
                    raise Exception(f"User state API error: {response.status}")

                data = await response.json()
                cprint(f"[OK] Got user state for {user_address[:8]}...", "green")
                return data

        except Exception as e:
            cprint(f"[ERROR] Failed to get user state: {e}", "red")
            return None

    async def place_order(self, symbol: str, side: str, order_type: str,
                         size: float, price: Optional[float] = None,
                         reduce_only: bool = False, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Place an order on HyperLiquid

        Args:
            symbol: Trading symbol
            side: 'B' for buy, 'S' for sell
            order_type: 'limit', 'market', 'trigger'
            size: Order size
            price: Order price (required for limit orders)
            reduce_only: Whether to reduce position only
            **kwargs: Additional order parameters

        Returns:
            Order result or None if failed
        """
        try:
            # Note: This would require authentication with private key
            # For now, return simulated order response
            cprint(f"[SIMULATION] Placing {side} {order_type} order for {size} {symbol}", "yellow")

            return {
                "status": "simulated",
                "symbol": symbol,
                "side": side,
                "type": order_type,
                "size": size,
                "price": price,
                "timestamp": time.time(),
                "order_id": f"sim_{int(time.time())}"
            }

        except Exception as e:
            cprint(f"[ERROR] Failed to place order: {e}", "red")
            return None

    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """
        Cancel an order

        Args:
            order_id: Order ID to cancel
            symbol: Trading symbol

        Returns:
            True if successful
        """
        try:
            cprint(f"[SIMULATION] Cancelling order {order_id} for {symbol}", "yellow")
            return True

        except Exception as e:
            cprint(f"[ERROR] Failed to cancel order: {e}", "red")
            return False

    async def get_positions(self, user_address: str) -> List[Dict[str, Any]]:
        """
        Get open positions for a user

        Args:
            user_address: User wallet address

        Returns:
            List of positions
        """
        try:
            user_state = await self.get_user_state(user_address)
            if not user_state or 'assetPositions' not in user_state:
                return []

            positions = []
            for pos in user_state['assetPositions']:
                if float(pos.get('position', {}).get('size', 0)) != 0:
                    positions.append({
                        'symbol': pos.get('position', {}).get('coin', ''),
                        'size': float(pos.get('position', {}).get('size', 0)),
                        'side': 'long' if float(pos.get('position', {}).get('size', 0)) > 0 else 'short',
                        'entry_price': float(pos.get('position', {}).get('entryPx', 0)),
                        'mark_price': float(pos.get('position', {}).get('valuationPx', 0)),
                        'unrealized_pnl': float(pos.get('position', {}).get('unrealizedPnl', 0)),
                        'leverage': float(pos.get('position', {}).get('leverage', {}).get('value', 1))
                    })

            cprint(f"[OK] Got {len(positions)} open positions", "green")
            return positions

        except Exception as e:
            cprint(f"[ERROR] Failed to get positions: {e}", "red")
            return []

    def clear_cache(self):
        """Clear all cached data"""
        self._price_cache.clear()
        self._last_cache_update.clear()
        cprint("[CACHE] Cleared all cached data", "yellow")

    async def health_check(self) -> bool:
        """Check if the Exchange Manager is healthy"""
        try:
            # Test basic API connectivity
            mids = await self.get_all_mids()
            return mids is not None and len(mids) > 0
        except Exception as e:
            cprint(f"[ERROR] Health check failed: {e}", "red")
            return False

    async def close(self):
        """Close the Exchange Manager and cleanup resources"""
        if self._session:
            await self._session.close()
            self._session = None
        self.clear_cache()
        cprint("🔌 Exchange Manager closed", "yellow")


# Factory function for easy initialization
async def get_exchange_manager(testnet: bool = False) -> HyperLiquidExchangeManager:
    """Get a configured Exchange Manager instance"""
    manager = HyperLiquidExchangeManager(testnet=testnet)
    await manager.__aenter__()
    return manager
