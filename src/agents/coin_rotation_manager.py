"""
[OK] Coin Rotation Manager
Dynamic asset monitoring based on Strategy Agent recommendations
Built with love by Deamon Dev [ROCKET]

Features:
- Real-time asset rotation based on strategy recommendations
- Market condition adaptive monitoring
- Performance tracking and optimization
- Risk-adjusted asset selection
"""

import asyncio
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


from src.agents.persistent_agent_client import (
    PersistentAgentClient,
    TaskPriority,
    TradingTask,
)


class RotationStrategy(Enum):
    """Coin rotation strategies"""

    VOLATILITY_FOCUSED = "volatility_focused"
    LIQUIDITY_FOCUSED = "liquidity_focused"
    BALANCED = "balanced"
    TREND_FOLLOWING = "trend_following"
    MEAN_REVERSION = "mean_reversion"
    PERFORMANCE_BASED = "performance_based"


@dataclass
class AssetProfile:
    """Asset monitoring profile"""

    symbol: str
    priority: int  # 1-10, 1 = highest
    strategy: str
    confidence: float
    risk_level: str  # LOW, MEDIUM, HIGH
    last_updated: datetime
    monitoring_active: bool
    performance_score: float
    market_conditions: Dict[str, Any]


@dataclass
class RotationConfig:
    """Configuration for coin rotation"""

    max_assets: int = 10
    min_assets: int = 5
    rotation_interval: int = 300  # 5 minutes
    strategy: RotationStrategy = RotationStrategy.BALANCED
    risk_tolerance: str = "MODERATE"
    performance_weight: float = 0.3
    volatility_weight: float = 0.3
    liquidity_weight: float = 0.4
    auto_optimize: bool = True


class CoinRotationManager:
    """Advanced coin rotation manager with Strategy Agent integration"""

    def __init__(self, config: Optional[RotationConfig] = None):
        self.config = config or RotationConfig()
        self.monitored_assets: Dict[str, AssetProfile] = {}
        self.client: Optional[PersistentAgentClient] = None
        self.running = False
        self.rotation_history: List[Dict[str, Any]] = []
        self.performance_metrics = {
            "total_rotations": 0,
            "successful_reallocations": 0,
            "avg_rotation_time": 0.0,
            "asset_performance": {},
            "strategy_effectiveness": {},
        }

        # Predefined asset universe
        self.asset_universe = {
            "BLUE_CHIPS": [
                "BTC",
                "ETH",
                "SOL",
                "AVAX",
                "MATIC",
                "DOT",
                "LINK",
                "UNI",
                "ATOM",
                "LTC",
            ],
            "DEFI": ["AAVE", "COMP", "CRV", "SUSHI", "YFI", "RUNE", "SNX", "MKR"],
            "LAYER2": ["ARB", "OP", "MATIC", "LRC"],
            "GAMING": ["GALA", "SAND", "MANA", "AXS", "ENJ"],
            "AI": ["FET", "RNDR", "OCEAN", "AGIX", "CTK"],
            "MEME": ["SHIB", "DOGE", "PEPE", "FLOKI", "BONK"],
        }

    async def start_rotation(self):
        """Start the coin rotation system"""
        print("[ROTATION] Starting coin rotation manager...")
        self.running = True

        async with PersistentAgentClient() as client:
            self.client = client

            # Initialize asset monitoring
            await self._initialize_monitoring()

            # Start rotation loop
            while self.running:
                try:
                    await self._perform_rotation_cycle()
                    await asyncio.sleep(self.config.rotation_interval)

                except Exception as e:
                    print(f"[ERROR] Rotation cycle failed: {e}")
                    await asyncio.sleep(30)

    async def _initialize_monitoring(self):
        """Initialize asset monitoring based on strategy recommendations"""
        print("[INIT] Initializing asset monitoring...")

        # Get initial asset recommendations from Strategy Agent
        recommended_assets = await self._get_strategy_recommendations()

        for asset_data in recommended_assets[: self.config.max_assets]:
            symbol = asset_data.get("symbol", "").upper()
            if symbol:
                profile = AssetProfile(
                    symbol=symbol,
                    priority=self._calculate_priority(asset_data),
                    strategy=asset_data.get("strategy", "unknown"),
                    confidence=asset_data.get("confidence", 0.5),
                    risk_level=asset_data.get("risk_level", "MEDIUM"),
                    last_updated=datetime.now(),
                    monitoring_active=True,
                    performance_score=0.5,
                    market_conditions={},
                )
                self.monitored_assets[symbol] = profile

        print(f"[INIT] Started monitoring {len(self.monitored_assets)} assets")
        self._display_monitored_assets()

    async def _get_strategy_recommendations(self) -> List[Dict[str, Any]]:
        """Get asset recommendations from Strategy Agent"""
        try:
            # Submit strategy task to get market-wide recommendations
            task = TradingTask(
                task_id=f"rotation_recommendations_{int(time.time())}",
                agent_type="strategy",
                priority=TaskPriority.HIGH,
                payload={
                    "task": "Get comprehensive market asset recommendations for rotation",
                    "analysis_type": "portfolio_rotation",
                    "risk_tolerance": self.config.risk_tolerance,
                    "max_assets": self.config.max_assets,
                    "strategy": self.config.strategy.value,
                    "market_scan": True,
                    "performance_analysis": True,
                    "liquidity_check": True,
                },
                timeout=120,
            )

            task_id = await self.client.submit_task(task)
            result = await self.client.get_task_result(task_id, timeout=180)

            if result and result.get("success"):
                response = result.get("response", {})
                recommendations = response.get("recommended_assets", [])

                # If no specific recommendations, use default blue chips
                if not recommendations:
                    recommendations = [
                        {"symbol": asset, "priority": i + 1, "confidence": 0.8}
                        for i, asset in enumerate(
                            self.asset_universe["BLUE_CHIPS"][: self.config.max_assets]
                        )
                    ]

                return recommendations
            else:
                print(
                    "[WARNING] Failed to get strategy recommendations, using defaults"
                )
                return []

        except Exception as e:
            print(f"[ERROR] Failed to get strategy recommendations: {e}")
            return []

    def _calculate_priority(self, asset_data: Dict[str, Any]) -> int:
        """Calculate asset priority based on strategy recommendations"""
        base_priority = asset_data.get("priority", 5)
        confidence = asset_data.get("confidence", 0.5)
        risk_adjustment = (
            0
            if asset_data.get("risk_level") == "LOW"
            else 2 if asset_data.get("risk_level") == "MEDIUM" else 4
        )

        # Adjust priority based on configuration weights
        priority = base_priority
        priority += int(
            (1 - confidence) * 3
        )  # Higher confidence = lower priority number
        priority += risk_adjustment

        return max(1, min(10, priority))

    async def _perform_rotation_cycle(self):
        """Perform one rotation cycle"""
        start_time = time.time()
        cycle_id = f"rotation_{int(time.time())}"

        print(f"\n[ROTATION CYCLE] Starting cycle {cycle_id}")
        print(f"[CONFIG] Strategy: {self.config.strategy.value}")
        print(f"[CONFIG] Max assets: {self.config.max_assets}")

        try:
            # Step 1: Get fresh strategy recommendations
            print("[STEP 1/4] Getting strategy recommendations...")
            fresh_recommendations = await self._get_strategy_recommendations()

            # Step 2: Evaluate current performance
            print("[STEP 2/4] Evaluating current performance...")
            performance_scores = await self._evaluate_current_performance()

            # Step 3: Determine rotation needs
            print("[STEP 3/4] Analyzing rotation needs...")
            rotation_decisions = await self._analyze_rotation_needs(
                fresh_recommendations, performance_scores
            )

            # Step 4: Execute rotation changes
            print("[STEP 4/4] Executing rotation changes...")
            rotation_results = await self._execute_rotation(rotation_decisions)

            # Update metrics
            cycle_time = time.time() - start_time
            self._update_rotation_metrics(cycle_time, rotation_results)

            print(
                f"[COMPLETE] Rotation cycle {cycle_id} completed in {cycle_time:.1f}s"
            )

        except Exception as e:
            print(f"[ERROR] Rotation cycle failed: {e}")
            import traceback

            traceback.print_exc()

    async def _evaluate_current_performance(self) -> Dict[str, float]:
        """Evaluate current performance of monitored assets"""
        performance_scores = {}

        for symbol, profile in self.monitored_items():
            if not profile.monitoring_active:
                continue

            try:
                # Get performance analysis from Strategy Agent
                task = TradingTask(
                    task_id=f"perf_{symbol}_{int(time.time())}",
                    agent_type="strategy",
                    priority=TaskPriority.NORMAL,
                    payload={
                        "task": f"Performance analysis for {symbol}",
                        "asset": symbol,
                        "analysis_type": "performance_check",
                        "timeframe": "1h",
                        "recent_trades": True,
                    },
                    timeout=60,
                )

                task_id = await self.client.submit_task(task)
                result = await self.client.get_task_result(task_id, timeout=90)

                if result and result.get("success"):
                    response = result.get("response", {})

                    # Calculate composite performance score
                    score = self._calculate_performance_score(response, profile)
                    performance_scores[symbol] = score

                    # Update asset profile
                    profile.performance_score = score
                    profile.last_updated = datetime.now()

                    print(f"  {symbol}: Performance score {score:.3f}")

            except Exception as e:
                print(f"[WARNING] Failed to evaluate {symbol}: {e}")
                performance_scores[symbol] = profile.performance_score

        return performance_scores

    def _calculate_performance_score(
        self, response: Dict[str, Any], profile: AssetProfile
    ) -> float:
        """Calculate comprehensive performance score"""
        try:
            # Extract performance metrics
            win_rate = response.get("win_rate", 0.5)
            profitability = response.get("profitability", 0)
            volatility = response.get("volatility", 0.5)
            trend_strength = response.get("trend_strength", 0.5)

            # Calculate risk-adjusted score
            risk_multiplier = {"LOW": 1.0, "MEDIUM": 0.8, "HIGH": 0.5}.get(
                profile.risk_level, 0.7
            )

            # Composite score calculation
            score = (
                win_rate * 0.3
                + profitability * 0.3
                + (1 - volatility) * 0.2
                + trend_strength * 0.2
            ) * risk_multiplier

            return max(0.0, min(1.0, score))

        except Exception:
            return profile.performance_score  # Return existing score on error

    async def _analyze_rotation_needs(
        self,
        recommendations: List[Dict[str, Any]],
        performance_scores: Dict[str, float],
    ) -> Dict[str, Any]:
        """Analyze what rotation changes are needed"""
        decisions = {
            "assets_to_add": [],
            "assets_to_remove": [],
            "assets_to_prioritize": [],
            "assets_to_deprioritize": [],
        }

        current_symbols = set(self.monitored_assets.keys())
        recommended_symbols = {rec.get("symbol", "").upper() for rec in recommendations}
        recommended_symbols.discard("")  # Remove empty strings

        # Identify assets to add (recommended but not monitored)
        for rec in recommendations:
            symbol = rec.get("symbol", "").upper()
            if (
                symbol
                and symbol not in current_symbols
                and symbol in recommended_symbols
            ):
                score = self._calculate_composite_score(
                    rec, performance_scores.get(symbol, 0.5)
                )
                if score > 0.4:  # Minimum threshold
                    decisions["assets_to_add"].append(
                        {
                            "symbol": symbol,
                            "score": score,
                            "reason": rec.get("reason", "Strategy recommendation"),
                            "priority": self._calculate_priority(rec),
                        }
                    )

        # Identify assets to remove (monitored but not recommended or poor performance)
        for symbol, profile in self.monitored_items().items():
            symbol_in_recommendations = symbol in recommended_symbols
            symbol_performance_ok = performance_scores.get(symbol, 0) > 0.3

            if not symbol_in_recommendations or not symbol_performance_ok:
                decisions["assets_to_remove"].append(
                    {
                        "symbol": symbol,
                        "score": performance_scores.get(
                            symbol, profile.performance_score
                        ),
                        "reason": "Poor performance or not recommended",
                        "current_priority": profile.priority,
                    }
                )

        # Sort by score
        decisions["assets_to_add"].sort(key=lambda x: x["score"], reverse=True)
        decisions["assets_to_remove"].sort(key=lambda x: x["score"])

        return decisions

    def _calculate_composite_score(
        self, recommendation: Dict[str, Any], performance_score: float
    ) -> float:
        """Calculate composite score combining recommendation and performance"""
        recommendation_score = (
            recommendation.get("confidence", 0.5) / 10.0
        )  # Normalize to 0-0.1

        # Apply configuration weights
        composite_score = (
            performance_score * self.config.performance_weight
            + recommendation_score * (1 - self.config.performance_weight)
        )

        return composite_score

    async def _execute_rotation(self, decisions: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the rotation changes"""
        results = {
            "added_assets": [],
            "removed_assets": [],
            "prioritized_changes": [],
            "errors": [],
        }

        try:
            # Remove underperforming assets
            for asset_info in decisions["assets_to_remove"]:
                symbol = asset_info["symbol"]
                if symbol in self.monitored_assets:
                    # Stop monitoring
                    self.monitored_assets[symbol].monitoring_active = False

                    # Archive performance data
                    self._archive_asset_performance(symbol)

                    del self.monitored_assets[symbol]
                    results["removed_assets"].append(symbol)
                    print(f"  [-] Removed {symbol} from monitoring")

            # Add new high-priority assets
            available_slots = self.config.max_assets - len(self.monitored_assets)

            for asset_info in decisions["assets_to_add"][:available_slots]:
                symbol = asset_info["symbol"]

                profile = AssetProfile(
                    symbol=symbol,
                    priority=asset_info["priority"],
                    strategy="rotation_added",
                    confidence=0.8,
                    risk_level="MEDIUM",
                    last_updated=datetime.now(),
                    monitoring_active=True,
                    performance_score=asset_info["score"],
                    market_conditions={},
                )

                self.monitored_assets[symbol] = profile
                results["added_assets"].append(symbol)
                print(f"  [+] Added {symbol} to monitoring")

            # Re-sort priorities
            await self._update_asset_priorities()

            print(
                f"[RESULT] Rotation: +{len(results['added_assets'])} -{len(results['removed_assets'])} assets"
            )
            print(f"[RESULT] Currently monitoring: {len(self.monitored_assets)} assets")

        except Exception as e:
            print(f"[ERROR] Rotation execution failed: {e}")
            results["errors"].append(str(e))

        return results

    async def _update_asset_priorities(self):
        """Update asset priorities based on current performance"""
        for symbol, profile in self.monitored_assets.items():
            # Recalculate priority based on performance score
            performance_priority = int((1 - profile.performance_score) * 10) + 1
            strategy_priority = profile.priority

            # Use weighted average
            new_priority = performance_priority * 0.6 + strategy_priority * 0.4
            profile.priority = max(1, min(10, int(new_priority)))

    def _archive_asset_performance(self, symbol: str):
        """Archive performance data for an asset"""
        if symbol in self.monitored_assets:
            profile = self.monitored_assets[symbol]

            # Store in performance history
            self.performance_metrics["asset_performance"][symbol] = {
                "final_score": profile.performance_score,
                "total_monitoring_time": (
                    datetime.now() - profile.last_updated
                ).total_seconds(),
                "average_confidence": profile.confidence,
                "strategy_used": profile.strategy,
                "archived_at": datetime.now().isoformat(),
            }

    def _update_rotation_metrics(self, cycle_time: float, results: Dict[str, Any]):
        """Update rotation performance metrics"""
        self.performance_metrics["total_rotations"] += 1
        self.performance_metrics["avg_rotation_time"] = (
            self.performance_metrics["avg_rotation_time"]
            * (self.performance_metrics["total_rotations"] - 1)
            + cycle_time
        ) / self.performance_metrics["total_rotations"]

        self.performance_metrics["successful_reallocations"] += len(
            results["added_assets"]
        ) + len(results["removed_assets"])

    def _display_monitored_assets(self):
        """Display currently monitored assets"""
        print(
            f"\n[MONITORED ASSETS] Currently tracking {len(self.monitored_assets)} assets:"
        )

        sorted_assets = sorted(
            self.monitored_assets.items(), key=lambda x: x[1].priority
        )

        for symbol, profile in sorted_assets:
            status_icon = "[ACTIVE]" if profile.monitoring_active else "[INACTIVE]"
            print(
                f"  {status_icon} {symbol:<6} Priority: {profile.priority:<2} Score: {profile.performance_score:.3f}"
            )

    def get_rotation_status(self) -> Dict[str, Any]:
        """Get current rotation status"""
        return {
            "config": asdict(self.config),
            "monitored_assets_count": len(self.monitored_assets),
            "active_monitoring": sum(
                1 for p in self.monitored_assets.values() if p.monitoring_active
            ),
            "metrics": self.performance_metrics,
            "asset_details": {
                symbol: {
                    "priority": profile.priority,
                    "strategy": profile.strategy,
                    "confidence": profile.confidence,
                    "risk_level": profile.risk_level,
                    "performance_score": profile.performance_score,
                    "monitoring_active": profile.monitoring_active,
                    "last_updated": profile.last_updated.isoformat(),
                }
                for symbol, profile in self.monitored_assets.items()
            },
        }

    async def force_rotation(
        self, strategy_override: Optional[RotationStrategy] = None
    ):
        """Force an immediate rotation cycle"""
        if strategy_override:
            self.config.strategy = strategy_override
            print(f"[FORCE] Strategy overridden to {strategy_override.value}")

        print("[FORCE] Executing immediate rotation...")
        await self._perform_rotation_cycle()

    async def add_asset(self, symbol: str, priority: int = 5) -> bool:
        """Manually add an asset to monitoring"""
        symbol = symbol.upper()

        if symbol in self.monitored_assets:
            print(f"[WARNING] {symbol} is already being monitored")
            return False

        if len(self.monitored_assets) >= self.config.max_assets:
            print(
                f"[ERROR] Cannot add {symbol}: maximum assets ({self.config.max_assets}) reached"
            )
            return False

        profile = AssetProfile(
            symbol=symbol,
            priority=priority,
            strategy="manual_add",
            confidence=0.7,
            risk_level="MEDIUM",
            last_updated=datetime.now(),
            monitoring_active=True,
            performance_score=0.5,
            market_conditions={},
        )

        self.monitored_assets[symbol] = profile
        print(f"[ADDED] {symbol} added to monitoring with priority {priority}")
        return True

    async def remove_asset(self, symbol: str) -> bool:
        """Manually remove an asset from monitoring"""
        symbol = symbol.upper()

        if symbol not in self.monitored_assets:
            print(f"[WARNING] {symbol} is not being monitored")
            return False

        self._archive_asset_performance(symbol)
        del self.monitored_assets[symbol]
        print(f"[REMOVED] {symbol} removed from monitoring")
        return True

    def stop_rotation(self):
        """Stop the rotation system"""
        self.running = False
        print("[ROTATION] Coin rotation stopped")


# Convenience functions
async def start_coin_rotation(config: Optional[RotationConfig] = None) -> None:
    """Start coin rotation manager with default or custom config"""
    manager = CoinRotationManager(config)
    await manager.start_rotation()


async def get_top_performers(limit: int = 10) -> List[Tuple[str, float]]:
    """Get top performing assets from current monitoring"""
    manager = CoinRotationManager()

    # This would need access to the current monitoring state
    # For now, return empty list
    return []


if __name__ == "__main__":
    # Demo the coin rotation manager
    async def demo_rotation():
        print("\n" + "=" * 60)
        print("[COIN ROTATION MANAGER DEMO]")
        print("=" * 60)

        config = RotationConfig(
            max_assets=8,
            rotation_interval=60,  # 1 minute for demo
            strategy=RotationStrategy.VOLATILITY_FOCUSED,
            auto_optimize=True,
        )

        manager = CoinRotationManager(config)

        print("🎯 Starting demo rotation (will run for 3 minutes)...")

        # Run rotation for 3 minutes
        task = asyncio.create_task(manager.start_rotation())
        await asyncio.sleep(180)  # 3 minutes

        # Stop rotation
        manager.stop_rotation()
        task.cancel()

        # Display final status
        status = manager.get_rotation_status()
        print(f"\n[FINAL STATUS]:")
        print(f"   Assets Monitored: {status['monitored_assets_count']}")
        print(f"   Total Rotations: {status['metrics']['total_rotations']}")
        print(
            f"   Success Rate: {status['metrics']['successful_reallocations'] / max(1, status['metrics']['total_rotations']) * 100:.1f}%"
        )

    asyncio.run(demo_rotation())
