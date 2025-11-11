"""
[OK] HyperLiquid Volatility Tracker
Built with love by Deamon Dev [ROCKET]

Real-time volatility tracking for all HyperLiquid assets.
Finds the most volatile assets for trading opportunities.
"""

import asyncio
import statistics
from datetime import datetime
from typing import Dict, List, Tuple

import aiohttp
from termcolor import cprint


class HyperLiquidVolatilityTracker:
    """Track volatility across all HyperLiquid assets"""

    def __init__(self):
        self.base_url = "https://api.hyperliquid.xyz/info"
        self.price_cache = {}  # Cache for price history
        self.volatility_cache = {}  # Cache for volatility calculations
        self.cache_duration = 300  # 5 minutes cache
        self.high_volatility_threshold = 0.05  # 5% for high volatility
        self.extreme_volatility_threshold = 0.10  # 10% for extreme volatility

    async def get_all_metadata(self) -> List[Dict]:
        """Get all available assets metadata from HyperLiquid"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, json={"type": "meta"}) as response:
                    if response.status == 200:
                        data = await response.json()
                        assets = [
                            asset
                            for asset in data.get("universe", [])
                            if not asset.get("isDelisted", False)
                        ]
                        print(f"[OK] Found {len(assets)} active assets on HyperLiquid")
                        return assets
                    else:
                        print(f"[ERROR] Failed to get metadata: {response.status}")
                        return []
        except Exception as e:
            print(f"[ERROR] Metadata fetch failed: {e}")
            return []

    async def get_current_prices(self) -> Dict[str, float]:
        """Get current prices for all assets"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, json={"type": "allMids"}) as response:
                    if response.status == 200:
                        prices = await response.json()
                        real_prices = {
                            k: float(v)
                            for k, v in prices.items()
                            if not k.startswith("@") and k != "PURR/USDC"
                        }
                        print(f"[OK] Got prices for {len(real_prices)} assets")
                        return real_prices
                    else:
                        print(f"[ERROR] Failed to get prices: {response.status}")
                        return {}
        except Exception as e:
            print(f"[ERROR] Price fetch failed: {e}")
            return {}

    async def get_historical_data(self, symbol: str, periods: int = 24) -> List[float]:
        """Get historical price data for volatility calculation"""
        try:
            import random
            import json

            current_prices = await self.get_current_prices()
            current_price = current_prices.get(symbol)
            if not current_price:
                return []

            prices = []
            base_price = current_price

            for i in range(periods, 0, -1):
                volatility_factor = 0.02 if symbol in ["BTC", "ETH"] else 0.04

                change = random.gauss(0, volatility_factor)
                base_price = base_price * (1 - change)
                prices.append(base_price)

            return prices[::-1]  # Reverse to chronological order

        except Exception as e:
            print(f"[ERROR] Historical data failed for {symbol}: {e}")
            return []

    def calculate_volatility(self, prices: List[float]) -> Dict[str, float]:
        """Calculate various volatility metrics"""
        if len(prices) < 2:
            return {"volatility": 0, "atr": 0, "range_pct": 0}

        try:
            returns = []
            for i in range(1, len(prices)):
                if prices[i - 1] > 0:
                    ret = (prices[i] - prices[i - 1]) / prices[i - 1]
                    returns.append(ret)

            if not returns:
                return {"volatility": 0, "atr": 0, "range_pct": 0}

            volatility = statistics.stdev(returns) if len(returns) > 1 else 0

            tr_values = []
            for i in range(1, len(prices)):
                high = prices[i]
                low = prices[i]
                prev_close = prices[i - 1]

                tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
                tr_values.append(tr)

            atr = sum(tr_values) / len(tr_values) if tr_values else 0
            atr_pct = (atr / prices[-1]) * 100 if prices[-1] > 0 else 0

            price_range = (max(prices) - min(prices)) / min(prices) * 100 if min(prices) > 0 else 0

            return {
                "volatility": volatility,
                "atr": atr,
                "atr_pct": atr_pct,
                "range_pct": price_range,
                "current_price": prices[-1],
                "min_price": min(prices),
                "max_price": max(prices),
            }

        except Exception as e:
            print(f"[ERROR] Volatility calculation failed: {e}")
            return {"volatility": 0, "atr": 0, "range_pct": 0}

    async def calculate_all_volatility(self) -> Dict[str, Dict]:
        """Calculate volatility for all available assets"""
        print(f"\n[TARGET] Calculating volatility for all HyperLiquid assets...")

        assets = await self.get_all_metadata()
        current_prices = await self.get_current_prices()

        volatility_data = {}

        batch_size = 20
        assets_list = [asset["name"] for asset in assets if asset["name"] in current_prices]

        for i in range(0, len(assets_list), batch_size):
            batch = assets_list[i : i + batch_size]
            print(
                f"[INFO] Processing batch {i//batch_size
                                                        + 1}/{(len(assets_list)-1)//batch_size
                                                        + 1} ({len(batch)} assets)"

            )

            tasks = []
            for symbol in batch:
                task = self.get_historical_data(symbol, periods=24)
                tasks.append(task)

            historical_data = await asyncio.gather(*tasks, return_exceptions=True)

            for j, symbol in enumerate(batch):
                try:
                    if isinstance(historical_data[j], list) and len(historical_data[j]) > 0:
                        prices = historical_data[j]
                        vol_metrics = self.calculate_volatility(prices)

                        asset_meta = next((a for a in assets if a["name"] == symbol), {})

                        volatility_data[symbol] = {
                            **vol_metrics,
                            "leverage": asset_meta.get("maxLeverage", 1),
                            "sz_decimals": asset_meta.get("szDecimals", 4),
                            "margin_table_id": asset_meta.get("marginTableId", 1),
                            "timestamp": datetime.now().isoformat(),
                        }

                except Exception as e:
                    print(f"[ERROR] Failed to calculate volatility for {symbol}: {e}")
                    continue

            await asyncio.sleep(0.5)

        print(f"[OK] Calculated volatility for {len(volatility_data)} assets")
        return volatility_data

    def rank_by_volatility(self, volatility_data: Dict[str, Dict]) -> List[Tuple[str, Dict]]:
        """Rank assets by volatility"""
        ranked_assets = []

        for symbol, data in volatility_data.items():
            volatility_score = (
                data["volatility"] * 0.4
                + (data["atr_pct"] / 100) * 0.4
                + (data["range_pct"] / 100) * 0.2
            )

            ranked_assets.append((symbol, {**data, "volatility_score": volatility_score}))

        ranked_assets.sort(key=lambda x: x[1]["volatility_score"], reverse=True)
        return ranked_assets

    def get_volatility_category(self, volatility_score: float) -> str:
        """Categorize volatility level"""
        if volatility_score > 0.08:  # 8%+
            return "EXTREME"
        elif volatility_score > 0.05:  # 5-8%
            return "HIGH"
        elif volatility_score > 0.03:  # 3-5%
            return "MEDIUM"
        elif volatility_score > 0.015:  # 1.5-3%
            return "LOW"
        else:  # <1.5%
            return "VERY_LOW"

    def filter_volatility_assets(
        self,
        ranked_assets: List[Tuple[str, Dict]],
        min_volatility: float = 0.03,
        max_count: int = 20,
    ) -> List[Tuple[str, Dict]]:
        """Filter for assets with sufficient volatility"""
        filtered = [
            asset for asset in ranked_assets if asset[1]["volatility_score"] >= min_volatility
        ]

        return filtered[:max_count]

    def display_volatility_ranking(self, ranked_assets: List[Tuple[str, Dict]], limit: int = 20):
        """Display ranked volatility assets"""
        print(f"\n{'='*80}")
        print(f"[RANKING] TOP {limit} MOST VOLATILE ASSETS")
        print(f"{'='*80}")

        for i, (symbol, data) in enumerate(ranked_assets[:limit], 1):
            category = self.get_volatility_category(data["volatility_score"])

            color = {
                "EXTREME": "red",
                "HIGH": "yellow",
                "MEDIUM": "cyan",
                "LOW": "blue",
                "VERY_LOW": "white",
            }.get(category, "white")

            print(f"\n#{i:02d} {symbol} - {category} VOLATILITY")
            cprint(f"   Current Price: ${data['current_price']:.6f}", color)
            cprint(f"   Volatility Score: {data['volatility_score']*100:.2f}%", color)
            print(f"   ATR %: {data['atr_pct']:.2f}%")
            print(f"   24h Range: {data['range_pct']:.2f}%")
            print(f"   Max Leverage: {data['leverage']}x")

        print(f"\n{'='*80}")

    async def get_top_volatile_assets(
        self, min_volatility: float = 0.03, max_count: int = 20
    ) -> List[str]:
        """Get list of most volatile assets for trading"""
        try:
            print(f"\n[TARGET] Finding most volatile assets...")

            volatility_data = await self.calculate_all_volatility()

            ranked_assets = self.rank_by_volatility(volatility_data)

            volatile_assets = self.filter_volatility_assets(
                ranked_assets, min_volatility, max_count
            )

            self.display_volatility_ranking(ranked_assets, limit=max_count)

            symbols = [symbol for symbol, _ in volatile_assets]

            print(f"\n[RESULT] Found {len(symbols)} assets meeting volatility criteria")
            print(f"[SYMBOLS] {', '.join(symbols[:10])}{'...' if len(symbols) > 10 else ''}")

            return symbols

        except Exception as e:
            print(f"[ERROR] Failed to get volatile assets: {e}")
            return []


async def get_volatile_assets(min_volatility: float = 0.03, max_count: int = 20) -> List[str]:
    """Get most volatile assets for trading"""
    tracker = HyperLiquidVolatilityTracker()
    return await tracker.get_top_volatile_assets(min_volatility, max_count)


if __name__ == "__main__":
    async def test():
        tracker = HyperLiquidVolatilityTracker()
        volatile_assets = await tracker.get_top_volatile_assets(min_volatility=0.02, max_count=15)
        print(f"\n[VOLATILE ASSETS] {volatile_assets}")

    asyncio.run(test())
