"""Automatic Coin Rotator

True automatic rotation system that cycles through crypto assets
Built with love by Deamon Dev

This system implements true automatic rotation:
- Automatically cycles through different crypto assets
- No user intervention required
- Performance-based rotation decisions
- Adaptive rotation intervals
- Multi-strategy support
"""

import asyncio
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from src.agents.liquidity_tracker import HyperLiquidLiquidityTracker
from src.agents.persistent_agent_client import (
    PersistentAgentClient,
    TaskPriority,
    TradingTask,
)


class RotationMode(Enum):
    AUTOMATIC = "automatic"  # Full automatic rotation
    PERFORMANCE_DRIVEN = "performance"  # Rotation based on performance
    TIME_BASED = "time"  # Fixed interval rotation
    MARKET_ADAPTIVE = "market"  # Rotation based on market conditions
    HYBRID = "hybrid"  # Combination of strategies


@dataclass
class AssetConfig:
    """Configuration for an asset in rotation"""

    symbol: str
    weight: float = 1.0  # Weight in rotation (0.1-1.0)
    min_hold_time: int = 300  # Minimum hold time in seconds
    max_hold_time: int = 1800  # Maximum hold time in seconds
    priority: int = 5  # Priority in rotation (1-10)
    performance_threshold: float = 0.3  # Performance threshold for rotation
    enabled: bool = True


@dataclass
class RotationConfig:
    """Configuration for automatic rotation"""

    mode: RotationMode = RotationMode.HYBRID
    rotation_interval: int = 300  # Base rotation interval in seconds
    max_assets: int = 5  # Maximum assets to monitor
    performance_weight: float = 0.4
    market_weight: float = 0.3
    time_weight: float = 0.3
    adaptive_threshold: float = 0.5  # Threshold for adaptive decisions
    auto_optimize: bool = True


class AutomaticCoinRotator:
    """True automatic coin rotation system"""

    def __init__(self, config: Optional[RotationConfig] = None):
        self.config = config or RotationConfig()
        self.liquidity_tracker = HyperLiquidLiquidityTracker()
        self.client: Optional[PersistentAgentClient] = None

        self.running = False
        self.current_assets: List[AssetConfig] = []
        self.rotation_queue: List[str] = []
        self.last_rotation: Dict[str, datetime] = {}
        self.performance_history: Dict[str, List[float]] = {}
        self.rotation_count = 0

        self.rotation_metrics = {
            "total_rotations": 0,
            "successful_rotations": 0,
            "failed_rotations": 0,
            "performance_rotations": 0,
            "time_rotations": 0,
            "market_rotations": 0,
            "last_rotation_time": None,
            "average_rotation_time": 0.0,
        }

        self.asset_configs = {
            "BTC": AssetConfig(
                "BTC", weight=1.0, min_hold_time=600, max_hold_time=3600, priority=1
            ),
            "ETH": AssetConfig(
                "ETH", weight=1.0, min_hold_time=600, max_hold_time=3600, priority=2
            ),
            "SOL": AssetConfig(
                "SOL", weight=0.9, min_hold_time=300, max_hold_time=2400, priority=3
            ),
            "AVAX": AssetConfig(
                "AVAX", weight=0.8, min_hold_time=300, max_hold_time=1800, priority=4
            ),
            "MATIC": AssetConfig(
                "MATIC", weight=0.8, min_hold_time=300, max_hold_time=1800, priority=5
            ),
            "DOT": AssetConfig(
                "DOT", weight=0.7, min_hold_time=240, max_hold_time=1500, priority=6
            ),
            "LINK": AssetConfig(
                "LINK", weight=0.7, min_hold_time=240, max_hold_time=1500, priority=7
            ),
            "UNI": AssetConfig(
                "UNI", weight=0.6, min_hold_time=180, max_hold_time=1200, priority=8
            ),
            "AAVE": AssetConfig(
                "AAVE", weight=0.6, min_hold_time=180, max_hold_time=1200, priority=9
            ),
            "CRV": AssetConfig(
                "CRV", weight=0.5, min_hold_time=120, max_hold_time=900, priority=10
            ),
        }

    async def start_automatic_rotation(self):
        """Start the automatic rotation system"""
        print("[AUTO-ROTATOR] Starting automatic coin rotation system")
        print(f"[CONFIG] Mode: {self.config.mode.value}")
        print(f"[CONFIG] Max Assets: {self.config.max_assets}")
        print(f"[CONFIG] Base Interval: {self.config.rotation_interval}s")

        async with PersistentAgentClient() as client:
            self.client = client
            self.running = True

            await self._initialize_rotation()

            while self.running:
                try:
                    await self._perform_rotation_cycle()
                    await asyncio.sleep(self.config.rotation_interval)

                except Exception as e:
                    print(f"[ERROR] Rotation cycle failed: {e}")
                    await asyncio.sleep(60)  # Wait before retry

    async def _initialize_rotation(self):
        """Initialize the rotation system"""
        print("[INIT] Initializing automatic rotation...")

        liquid_assets = await self._get_liquid_assets()

        selected_assets = await self._select_initial_assets(liquid_assets)

        await self._setup_rotation_queue(selected_assets)

        print(f"[INIT] Initialized with {len(self.current_assets)} assets")
        await self._display_rotation_status()

    async def _get_liquid_assets(self) -> List[str]:
        """Get liquid assets suitable for rotation"""
        try:
            liquid_assets = await self.liquidity_tracker.get_liquid_assets(
                min_liquidity_score=0.4, max_count=20
            )

            available_assets = [asset for asset in liquid_assets if asset in self.asset_configs]

            print(f"[LIQUID] Found {len(available_assets)} liquid, configured assets")
            return available_assets

        except Exception as e:
            print(f"[ERROR] Failed to get liquid assets: {e}")
            return ["BTC", "ETH", "SOL", "AVAX", "MATIC"]

    async def _select_initial_assets(self, available_assets: List[str]) -> List[str]:
        """Select initial assets for rotation"""
        selected = []

        sorted_assets = sorted(
            available_assets,
            key=lambda x: (
                self.asset_configs[x].priority,
                -self.asset_configs[x].weight,
            ),
        )

        for asset in sorted_assets[: self.config.max_assets]:
            if self.asset_configs[asset].enabled:
                selected.append(asset)
                self.current_assets.append(self.asset_configs[asset])
                self.last_rotation[asset] = datetime.now()
                self.performance_history[asset] = [0.5]  # Start with neutral performance

        print(f"[SELECT] Selected {len(selected)} assets: {selected}")
        return selected

    async def _setup_rotation_queue(self, assets: List[str]):
        """Setup the rotation queue"""
        weighted_assets = []
        for asset in assets:
            config = self.asset_configs[asset]
            queue_entries = int(config.weight * 10)
            weighted_assets.extend([asset] * queue_entries)

        import random

        random.shuffle(weighted_assets)

        self.rotation_queue = weighted_assets
        print(f"[QUEUE] Rotation queue setup with {len(weighted_assets)} entries")

    async def _perform_rotation_cycle(self):
        """Perform one rotation cycle"""
        cycle_start = time.time()
        self.rotation_count += 1

        print(f"\n[ROTATION] Cycle {self.rotation_count} started")

        try:
            rotation_decision = await self._analyze_rotation_needs()

            if rotation_decision["should_rotate"]:
                results = await self._execute_rotation(rotation_decision)

                await self._update_rotation_metrics(results, cycle_start)

                print(f"[ROTATION] Completed: {rotation_decision['reason']}")
            else:
                print(f"[ROTATION] No rotation needed: {rotation_decision['reason']}")

        except Exception as e:
            print(f"[ERROR] Rotation cycle {self.rotation_count} failed: {e}")
            self.rotation_metrics["failed_rotations"] += 1

    async def _analyze_rotation_needs(self) -> Dict[str, Any]:
        """Analyze if rotation is needed and what to rotate"""
        decision = {
            "should_rotate": False,
            "reason": "",
            "rotation_type": None,
            "assets_to_add": [],
            "assets_to_remove": [],
        }

        current_time = datetime.now()

        if self.config.mode in [RotationMode.PERFORMANCE_DRIVEN, RotationMode.HYBRID]:
            perf_decision = await self._check_performance_rotation(current_time)
            if perf_decision["should_rotate"]:
                decision.update(perf_decision)
                decision["rotation_type"] = "performance"
                return decision

        if self.config.mode in [RotationMode.TIME_BASED, RotationMode.HYBRID]:
            time_decision = await self._check_time_rotation(current_time)
            if time_decision["should_rotate"]:
                decision.update(time_decision)
                decision["rotation_type"] = "time"
                return decision

        if self.config.mode in [RotationMode.MARKET_ADAPTIVE, RotationMode.HYBRID]:
            market_decision = await self._check_market_rotation(current_time)
            if market_decision["should_rotate"]:
                decision.update(market_decision)
                decision["rotation_type"] = "market"
                return decision

        if self.config.mode == RotationMode.AUTOMATIC and self.rotation_queue:
            next_asset = self.rotation_queue.pop(0)
            if len(self.current_assets) < self.config.max_assets:
                decision["should_rotate"] = True
                decision["reason"] = "Automatic rotation - adding new asset"
                decision["assets_to_add"] = [next_asset]
                decision["rotation_type"] = "automatic"
            else:
                lowest_priority_asset = min(self.current_assets, key=lambda x: x.priority).symbol
                decision["should_rotate"] = True
                decision["reason"] = f"Automatic rotation - replacing {lowest_priority_asset}"
                decision["assets_to_remove"] = [lowest_priority_asset]
                decision["assets_to_add"] = [next_asset]
                decision["rotation_type"] = "automatic"
            return decision

        decision["reason"] = "No rotation criteria met"
        return decision

    async def _check_performance_rotation(self, current_time: datetime) -> Dict[str, Any]:
        """Check if performance-based rotation is needed"""
        decision = {
            "should_rotate": False,
            "reason": "",
            "assets_to_remove": [],
            "assets_to_add": [],
        }

        for asset_config in self.current_assets:
            asset = asset_config.symbol

            if len(self.performance_history[asset]) < 3:
                continue

            avg_performance = sum(self.performance_history[asset][-5:]) / min(
                5, len(self.performance_history[asset])
            )

            if avg_performance < asset_config.performance_threshold:
                decision["should_rotate"] = True
                decision["reason"] = (
                    f"Performance rotation - {asset} performance ({avg_performance:.3f}) below threshold"
                )
                decision["assets_to_remove"].append(asset)

        if decision["assets_to_remove"]:
            replacements = await self._find_replacement_assets(decision["assets_to_remove"])
            decision["assets_to_add"] = replacements

        return decision

    async def _check_time_rotation(self, current_time: datetime) -> Dict[str, Any]:
        """Check if time-based rotation is needed"""
        decision = {
            "should_rotate": False,
            "reason": "",
            "assets_to_remove": [],
            "assets_to_add": [],
        }

        for asset_config in self.current_assets:
            asset = asset_config.symbol
            last_rotation_time = self.last_rotation.get(asset, current_time)
            hold_time = (current_time - last_rotation_time).total_seconds()

            if hold_time > asset_config.max_hold_time:
                decision["should_rotate"] = True
                decision["reason"] = (
                    f"Time rotation - {asset} held for {hold_time:.0f}s (max: {asset_config.max_hold_time}s)"
                )
                decision["assets_to_remove"].append(asset)

        if decision["assets_to_remove"]:
            replacements = await self._find_replacement_assets(decision["assets_to_remove"])
            decision["assets_to_add"] = replacements

        return decision

    async def _check_market_rotation(self, current_time: datetime) -> Dict[str, Any]:
        """Check if market-adaptive rotation is needed"""
        decision = {
            "should_rotate": False,
            "reason": "",
            "assets_to_remove": [],
            "assets_to_add": [],
        }

        try:
            market_task = TradingTask(
                task_id=f"market_rotation_{int(time.time())}",
                agent_type="strategy",
                priority=TaskPriority.HIGH,
                payload={
                    "task": "Market analysis for rotation decisions",
                    "analysis_type": "rotation_market",
                    "current_assets": [ac.symbol for ac in self.current_assets],
                    "rotation_threshold": self.config.adaptive_threshold,
                },
                timeout=60,
            )

            task_id = await self.client.submit_task(market_task)
            result = await self.client.get_task_result(task_id, timeout=90)

            if result and result.get("success"):
                response = result.get("response", {})
                market_analysis = response.get("market_analysis", {})

                market_condition = market_analysis.get("condition", "NORMAL")
                asset_recommendations = response.get("rotation_recommendations", {})

                if market_condition in [
                    "HIGH_VOLATILITY",
                    "TREND_CHANGE",
                    "LOW_LIQUIDITY",
                ]:
                    assets_to_remove = asset_recommendations.get("remove", [])
                    assets_to_add = asset_recommendations.get("add", [])

                    if assets_to_remove or assets_to_add:
                        decision["should_rotate"] = True
                        decision["reason"] = f"Market rotation - condition: {market_condition}"
                        decision["assets_to_remove"] = assets_to_remove
                        decision["assets_to_add"] = assets_to_add[
                            : len(assets_to_remove)
                        ]  # Balance additions/removals

        except Exception as e:
            print(f"[WARNING] Market analysis failed: {e}")

        return decision

    async def _find_replacement_assets(self, assets_to_remove: List[str]) -> List[str]:
        """Find replacement assets for removed ones"""
        replacements = []
        current_symbols = {ac.symbol for ac in self.current_assets}

        liquid_assets = await self._get_liquid_assets()

        available_assets = [
            asset
            for asset in liquid_assets
            if asset not in current_symbols and asset not in assets_to_remove
        ]

        sorted_replacements = sorted(
            available_assets,
            key=lambda x: (
                self.asset_configs[x].priority,
                -self.asset_configs[x].weight,
            ),
        )

        for asset in sorted_replacements[: len(assets_to_remove)]:
            if self.asset_configs[asset].enabled:
                replacements.append(asset)

        return replacements

    async def _execute_rotation(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the rotation decision"""
        results = {
            "removed_assets": [],
            "added_assets": [],
            "execution_time": 0,
            "success": False,
        }

        try:
            for asset in decision["assets_to_remove"]:
                success = await self._remove_asset(asset)
                if success:
                    results["removed_assets"].append(asset)

            for asset in decision["assets_to_add"]:
                success = await self._add_asset(asset)
                if success:
                    results["added_assets"].append(asset)

            results["success"] = True
            print(
                f"[EXECUTE] Rotation executed: +{len(results['added_assets'])} -{len(results['removed_assets'])}"
            )

        except Exception as e:
            print(f"[ERROR] Rotation execution failed: {e}")
            results["success"] = False

        return results

    async def _remove_asset(self, asset: str) -> bool:
        """Remove an asset from rotation"""
        try:
            self.current_assets = [ac for ac in self.current_assets if ac.symbol != asset]

            if asset in self.performance_history:
                self.performance_history[asset] = self.performance_history[asset][-5:]

            print(f"  [-] Removed {asset} from rotation")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to remove {asset}: {e}")
            return False

    async def _add_asset(self, asset: str) -> bool:
        """Add an asset to rotation"""
        try:
            if asset not in self.asset_configs:
                print(f"[WARNING] Asset {asset} not in configuration")
                return False

            asset_config = self.asset_configs[asset]

            self.current_assets.append(asset_config)

            self.last_rotation[asset] = datetime.now()
            if asset not in self.performance_history:
                self.performance_history[asset] = [0.5]  # Start with neutral performance

            print(
                f"  [+] Added {asset} to rotation (priority: {asset_config.priority}, weight: {asset_config.weight})"
            )
            return True

        except Exception as e:
            print(f"[ERROR] Failed to add {asset}: {e}")
            return False

    async def _update_performance_data(self):
        """Update performance data for current assets"""
        for asset_config in self.current_assets:
            asset = asset_config.symbol

            try:
                perf_task = TradingTask(
                    task_id=f"perf_update_{asset}_{int(time.time())}",
                    agent_type="strategy",
                    priority=TaskPriority.NORMAL,
                    payload={
                        "task": f"Performance analysis for {asset}",
                        "asset": asset,
                        "analysis_type": "performance_update",
                        "rotation_context": True,
                    },
                    timeout=45,
                )

                task_id = await self.client.submit_task(perf_task)
                result = await self.client.get_task_result(task_id, timeout=60)

                if result and result.get("success"):
                    response = result.get("response", {})
                    performance_score = response.get("performance_score", 0.5)

                    if asset not in self.performance_history:
                        self.performance_history[asset] = []

                    self.performance_history[asset].append(performance_score)

                    if len(self.performance_history[asset]) > 10:
                        self.performance_history[asset] = self.performance_history[asset][-10:]

            except Exception as e:
                print(f"[WARNING] Failed to update performance for {asset}: {e}")

    async def _update_rotation_metrics(self, results: Dict[str, Any], cycle_start: float):
        """Update rotation metrics"""
        execution_time = time.time() - cycle_start

        self.rotation_metrics["total_rotations"] += 1
        self.rotation_metrics["last_rotation_time"] = datetime.now().isoformat()

        if results["success"]:
            self.rotation_metrics["successful_rotations"] += 1
        else:
            self.rotation_metrics["failed_rotations"] += 1

        total_time = (
            self.rotation_metrics["average_rotation_time"]
            * (self.rotation_metrics["total_rotations"] - 1)
            + execution_time
        )
        self.rotation_metrics["average_rotation_time"] = (
            total_time / self.rotation_metrics["total_rotations"]
        )

    async def _display_rotation_status(self):
        """Display current rotation status"""
        print(f"\n[ROTATION STATUS] Currently monitoring {len(self.current_assets)} assets:")

        sorted_assets = sorted(self.current_assets, key=lambda x: x.priority)

        for asset_config in sorted_assets:
            asset = asset_config.symbol
            last_rotation = self.last_rotation.get(asset, datetime.now())
            time_since_rotation = (datetime.now() - last_rotation).total_seconds()
            avg_performance = sum(self.performance_history.get(asset, [0.5])) / max(
                1, len(self.performance_history.get(asset, []))
            )

            print(
                f"  {asset:<6} Priority: {asset_config.priority:<2} "
                f"Time: {time_since_rotation:.0f}s Perf: {avg_performance:.3f}"
            )

    def get_rotation_metrics(self) -> Dict[str, Any]:
        """Get rotation performance metrics"""
        return {
            "rotation_metrics": self.rotation_metrics,
            "current_assets": len(self.current_assets),
            "rotation_count": self.rotation_count,
            "performance_history": {
                asset: {
                    "avg_performance": sum(scores) / len(scores),
                    "recent_performance": scores[-3:],
                    "trend": (
                        "improving" if len(scores) >= 2 and scores[-1] > scores[-2] else "declining"
                    ),
                }
                for asset, scores in self.performance_history.items()
            },
        }

    def stop_rotation(self):
        """Stop the rotation system"""
        print("[AUTO-ROTATOR] Stopping automatic rotation")
        self.running = False


if __name__ == "__main__":

    async def demo_automatic_rotation():
        print("\n" + "=" * 70)
        print("[AUTOMATIC COIN ROTATOR DEMO]")
        print("=" * 70)

        config = RotationConfig(
            mode=RotationMode.HYBRID,
            rotation_interval=30,  # 30 seconds for demo
            max_assets=5,
            performance_weight=0.4,
            market_weight=0.3,
            time_weight=0.3,
            auto_optimize=True,
        )

        rotator = AutomaticCoinRotator(config)

        print("[DEMO] Starting automatic rotation (runs for 120 seconds)...")

        try:
            task = asyncio.create_task(rotator.start_automatic_rotation())

            await asyncio.sleep(120)

            rotator.stop_rotation()
            task.cancel()

            metrics = rotator.get_rotation_metrics()
            print(f"\n[FINAL METRICS]")
            print(f"  Total Rotations: {metrics['rotation_metrics']['total_rotations']}")
            print(f"  Successful Rotations: {metrics['rotation_metrics']['successful_rotations']}")
            print(
                f"  Average Rotation Time: {metrics['rotation_metrics']['average_rotation_time']:.1f}s"
            )
            print(f"  Current Assets: {metrics['current_assets']}")

        except KeyboardInterrupt:
            print("\n[INTERRUPTED] Stopping rotation...")
            rotator.stop_rotation()

    asyncio.run(demo_automatic_rotation())
