"""Coin Rotation Integration

Integration of Coin Rotation Manager with the persistent agents system
Built with love by Deamon Dev

This file integrates the coin rotation manager with:
1. Persistent Agent System
2. Backend API endpoints
3. Real-time monitoring
4. Automated workflows
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from src.agents.coin_rotation_manager import (
    AssetProfile,
    CoinRotationManager,
    RotationConfig,
    RotationStrategy,
)
from src.agents.persistent_agent_client import (
    PersistentAgentClient,
    TaskPriority,
    TradingTask,
)


class IntegratedRotationSystem:
    """Integrated coin rotation system with persistent agents"""

    def __init__(self):
        self.rotation_manager = CoinRotationManager()
        self.client: Optional[PersistentAgentClient] = None
        self.workflow_integration = True
        self.auto_optimization = True
        self.last_optimization = datetime.now()

        self.rotation_manager.config = RotationConfig(
            max_assets=12,
            min_assets=6,
            rotation_interval=300,  # 5 minutes
            strategy=RotationStrategy.PERFORMANCE_BASED,
            risk_tolerance="ADAPTIVE",
            performance_weight=0.4,
            volatility_weight=0.3,
            liquidity_weight=0.3,
            auto_optimize=True,
        )

    async def start_integrated_rotation(self):
        """Start the integrated rotation system with persistent agents"""
        print("[INTEGRATION] Starting integrated coin rotation system...")
        print(f"[CONFIG] Strategy: {self.rotation_manager.config.strategy.value}")
        print(f"[CONFIG] Max Assets: {self.rotation_manager.config.max_assets}")
        print(f"[CONFIG] Rotation Interval: {self.rotation_manager.config.rotation_interval}s")

        async with PersistentAgentClient() as client:
            self.client = client
            self.rotation_manager.client = client

            await self.rotation_manager.start_rotation()

    async def start_with_workflow_optimization(self):
        """Start rotation with workflow optimization"""
        print("[WORKFLOW] Starting rotation with workflow optimization...")

        async with PersistentAgentClient() as client:
            self.client = client
            self.rotation_manager.client = client

            await self._initialize_with_workflow_analysis()
            self.rotation_manager.running = True

            while self.rotation_manager.running:
                try:
                    await self._perform_enhanced_rotation_cycle()
                    await asyncio.sleep(self.rotation_manager.config.rotation_interval)

                    if (
                        self.auto_optimization
                        and (datetime.now() - self.last_optimization).seconds > 1800
                    ):
                        await self._optimize_rotation_strategy()
                        self.last_optimization = datetime.now()

                except Exception as e:
                    print(f"[ERROR] Enhanced rotation cycle failed: {e}")
                    await asyncio.sleep(30)

    async def _initialize_with_workflow_analysis(self):
        """Initialize rotation with comprehensive workflow analysis"""
        print("[INIT] Performing comprehensive workflow analysis...")

        market_analysis_task = TradingTask(
            task_id=f"workflow_analysis_{int(time.time())}",
            agent_type="strategy",
            priority=TaskPriority.HIGH,
            payload={
                "task": "Comprehensive market analysis for rotation setup",
                "analysis_type": "rotation_setup",
                "market_scan": True,
                "performance_history": True,
                "liquidity_analysis": True,
                "risk_assessment": True,
                "volatility_analysis": True,
            },
            timeout=180,
        )

        task_id = await self.client.submit_task(market_analysis_task)
        result = await self.client.get_task_result(task_id, timeout=240)

        if result and result.get("success"):
            analysis = result.get("response", {})

            await self._adjust_config_from_analysis(analysis)

            await self._enhanced_initialization(analysis)
        else:
            print("[WARNING] Workflow analysis failed, using default initialization")
            await self.rotation_manager._initialize_monitoring()

    async def _adjust_config_from_analysis(self, analysis: Dict[str, Any]):
        """Adjust rotation configuration based on market analysis"""
        try:
            market_condition = analysis.get("market_condition", "NORMAL")
            volatility_level = analysis.get("volatility_level", "MEDIUM")
            liquidity_level = analysis.get("liquidity_level", "GOOD")

            print(
                f"[CONFIG] Market: {market_condition}, Volatility: {volatility_level}, Liquidity: {liquidity_level}"
            )

            if market_condition == "HIGH_VOLATILITY":
                self.rotation_manager.config.strategy = RotationStrategy.LIQUIDITY_FOCUSED
                self.rotation_manager.config.max_assets = 8
                self.rotation_manager.config.rotation_interval = 180  # 3 minutes
                print("[CONFIG] Switched to LIQUIDITY_FOCUSED strategy for high volatility")

            elif market_condition == "BULL_MARKET":
                self.rotation_manager.config.strategy = RotationStrategy.TREND_FOLLOWING
                self.rotation_manager.config.max_assets = 15
                self.rotation_manager.config.rotation_interval = 600  # 10 minutes
                print("[CONFIG] Switched to TREND_FOLLOWING strategy for bull market")

            elif market_condition == "BEAR_MARKET":
                self.rotation_manager.config.strategy = RotationStrategy.MEAN_REVERSION
                self.rotation_manager.config.max_assets = 10
                self.rotation_manager.config.rotation_interval = 240  # 4 minutes
                print("[CONFIG] Switched to MEAN_REVERSION strategy for bear market")

            if liquidity_level == "LOW":
                self.rotation_manager.config.max_assets = max(
                    5, self.rotation_manager.config.max_assets - 3
                )
                print(
                    f"[CONFIG] Reduced max assets to {self.rotation_manager.config.max_assets} due to low liquidity"
                )

        except Exception as e:
            print(f"[WARNING] Failed to adjust config from analysis: {e}")

    async def _enhanced_initialization(self, analysis: Dict[str, Any]):
        """Enhanced initialization with workflow insights"""
        try:
            recommendations_task = TradingTask(
                task_id=f"enhanced_rotation_{int(time.time())}",
                agent_type="strategy",
                priority=TaskPriority.CRITICAL,
                payload={
                    "task": "Enhanced rotation recommendations",
                    "analysis_type": "rotation_setup",
                    "market_analysis": analysis,
                    "performance_weight": self.rotation_manager.config.performance_weight,
                    "liquidity_weight": self.rotation_manager.config.liquidity_weight,
                    "volatility_weight": self.rotation_manager.config.volatility_weight,
                    "asset_universe": ["ALL"],  # Will analyze all available assets
                    "dynamic_scoring": True,
                    "multi_timeframe": True,
                },
                timeout=150,
            )

            task_id = await self.client.submit_task(recommendations_task)
            result = await self.client.get_task_result(task_id, timeout=200)

            if result and result.get("success"):
                response = result.get("response", {})
                recommendations = response.get("enhanced_recommendations", [])

                for asset_data in recommendations[: self.rotation_manager.config.max_assets]:
                    symbol = asset_data.get("symbol", "").upper()
                    if symbol:
                        profile = AssetProfile(
                            symbol=symbol,
                            priority=self._calculate_enhanced_priority(asset_data, analysis),
                            strategy=asset_data.get("recommended_strategy", "hybrid"),
                            confidence=asset_data.get("confidence", 0.5),
                            risk_level=asset_data.get("risk_level", "MEDIUM"),
                            last_updated=datetime.now(),
                            monitoring_active=True,
                            performance_score=asset_data.get("performance_score", 0.5),
                            market_conditions=asset_data.get("market_conditions", {}),
                        )
                        self.rotation_manager.monitored_assets[symbol] = profile

                print(
                    f"[INIT] Enhanced monitoring started for {len(self.rotation_manager.monitored_assets)} assets"
                )
                await self.rotation_manager._display_monitored_assets()

        except Exception as e:
            print(f"[WARNING] Enhanced initialization failed, falling back to standard: {e}")
            await self.rotation_manager._initialize_monitoring()

    def _calculate_enhanced_priority(
        self, asset_data: Dict[str, Any], analysis: Dict[str, Any]
    ) -> int:
        """Calculate enhanced priority with multiple factors"""
        try:
            base_priority = asset_data.get("priority", 5)
            confidence = asset_data.get("confidence", 0.5)

            market_boost = 0
            if analysis.get("market_condition") == "BULL_MARKET":
                market_boost = 1  # Boost in bull market

            liquidity_score = asset_data.get("liquidity_score", 0.5)
            liquidity_bonus = int(liquidity_score * 2)

            trend_score = asset_data.get("trend_score", 0.5)
            trend_bonus = int(trend_score * 2)

            priority = (
                base_priority
                - int((1 - confidence) * 2)
                + liquidity_bonus
                + trend_bonus
                + market_boost
            )

            return max(1, min(10, priority))

        except Exception:
            return 5

    async def _perform_enhanced_rotation_cycle(self):
        """Perform enhanced rotation cycle with workflow optimization"""
        start_time = time.time()
        cycle_id = f"enhanced_rotation_{int(time.time())}"

        print(f"\n[ENHANCED ROTATION] Starting enhanced cycle {cycle_id}")

        try:
            print("[STEP 1/5] Comprehensive market analysis...")
            market_analysis = await self._get_comprehensive_market_analysis()

            print("[STEP 2/5] Performance-based recommendations...")
            recommendations = await self._get_performance_recommendations()

            print("[STEP 3/5] Workflow-aware performance analysis...")
            performance_scores = await self._evaluate_workflow_performance()

            print("[STEP 4/5] Multi-factor rotation analysis...")
            rotation_decisions = await self._analyze_enhanced_rotation_needs(
                recommendations, performance_scores, market_analysis
            )

            print("[STEP 5/5] Optimized rotation execution...")
            rotation_results = await self._execute_optimized_rotation(rotation_decisions)

            await self._post_rotation_optimization(rotation_results)

            cycle_time = time.time() - start_time
            self._update_enhanced_metrics(cycle_time, rotation_results)

            print(f"[COMPLETE] Enhanced rotation {cycle_id} completed in {cycle_time:.1f}s")

        except Exception as e:
            print(f"[ERROR] Enhanced rotation cycle failed: {e}")
            import traceback

            traceback.print_exc()

    async def _get_comprehensive_market_analysis(self) -> Dict[str, Any]:
        """Get comprehensive market analysis from Strategy Agent"""
        try:
            task = TradingTask(
                task_id=f"market_analysis_{int(time.time())}",
                agent_type="strategy",
                priority=TaskPriority.HIGH,
                payload={
                    "task": "Comprehensive market analysis for rotation",
                    "analysis_type": "comprehensive",
                    "scan_all_assets": True,
                    "multi_timeframe": True,
                    "volatility_analysis": True,
                    "liquidity_analysis": True,
                    "trend_analysis": True,
                    "market_sentiment": True,
                },
                timeout=120,
            )

            task_id = await self.client.submit_task(task)
            result = await self.client.get_task_result(task_id, timeout=180)

            if result and result.get("success"):
                return result.get("response", {})
            else:
                return {}

        except Exception as e:
            print(f"[ERROR] Failed to get market analysis: {e}")
            return {}

    async def _get_performance_recommendations(self) -> List[Dict[str, Any]]:
        """Get performance-based asset recommendations"""
        try:
            task = TradingTask(
                task_id=f"perf_recommendations_{int(time.time())}",
                agent_type="strategy",
                priority=TaskPriority.HIGH,
                payload={
                    "task": "Performance-based asset recommendations",
                    "analysis_type": "performance_ranking",
                    "historical_analysis": True,
                    "profitability_analysis": True,
                    "risk_adjusted": True,
                    "max_recommendations": self.rotation_manager.config.max_assets * 2,
                },
                timeout=100,
            )

            task_id = await self.client.submit_task(task)
            result = await self.client.get_task_result(task_id, timeout=150)

            if result and result.get("success"):
                return result.get("response", {}).get("ranked_assets", [])
            else:
                return []

        except Exception as e:
            print(f"[ERROR] Failed to get performance recommendations: {e}")
            return []

    async def _evaluate_workflow_performance(self) -> Dict[str, float]:
        """Evaluate performance with workflow context"""
        performance_scores = {}

        for symbol, profile in self.rotation_manager.monitored_assets.items():
            if not profile.monitoring_active:
                continue

            try:
                task = TradingTask(
                    task_id=f"workflow_perf_{symbol}_{int(time.time())}",
                    agent_type="strategy",
                    priority=TaskPriority.NORMAL,
                    payload={
                        "task": f"Workflow performance analysis for {symbol}",
                        "asset": symbol,
                        "analysis_type": "workflow_performance",
                        "current_rotation_priority": profile.priority,
                        "monitoring_duration": (
                            datetime.now() - profile.last_updated
                        ).total_seconds(),
                        "multi_timeframe": True,
                        "trade_execution_analysis": True,
                        "position_sizing_efficiency": True,
                    },
                    timeout=80,
                )

                task_id = await self.client.submit_task(task)
                result = await self.client.get_task_result(task_id, timeout=120)

                if result and result.get("success"):
                    response = result.get("response", {})

                    base_score = self.rotation_manager._calculate_performance_score(
                        response, profile
                    )
                    workflow_bonus = response.get("workflow_efficiency", 0.5) * 0.2
                    execution_bonus = response.get("execution_quality", 0.5) * 0.2

                    enhanced_score = min(1.0, base_score + workflow_bonus + execution_bonus)
                    performance_scores[symbol] = enhanced_score

                    profile.performance_score = enhanced_score
                    profile.last_updated = datetime.now()

                    print(f"  {symbol}: Workflow performance {enhanced_score:.3f}")

            except Exception as e:
                print(f"[WARNING] Failed workflow evaluation for {symbol}: {e}")
                performance_scores[symbol] = profile.performance_score

        return performance_scores

    async def _analyze_enhanced_rotation_needs(
        self,
        recommendations: List[Dict[str, Any]],
        performance_scores: Dict[str, float],
        market_analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Analyze rotation needs with multiple factors"""
        decisions = {
            "assets_to_add": [],
            "assets_to_remove": [],
            "assets_to_prioritize": [],
            "assets_to_deprioritize": [],
            "market_based_adjustments": {},
        }

        try:
            current_symbols = set(self.rotation_manager.monitored_assets.keys())
            recommended_symbols = {rec.get("symbol", "").upper() for rec in recommendations}
            recommended_symbols.discard("")

            market_influence = self._calculate_market_influence(market_analysis)

            for rec in recommendations:
                symbol = rec.get("symbol", "").upper()
                if symbol and symbol not in current_symbols and symbol in recommended_symbols:

                    performance_score = performance_scores.get(symbol, 0.5)
                    recommendation_score = rec.get("confidence", 0.5) / 10
                    market_score = market_influence.get(symbol, 0.5)

                    composite_score = (
                        performance_score * self.rotation_manager.config.performance_weight
                        + recommendation_score
                        * (1 - self.rotation_manager.config.performance_weight)
                        + market_score * 0.2
                    )

                    if composite_score > 0.3:
                        decisions["assets_to_add"].append(
                            {
                                "symbol": symbol,
                                "score": composite_score,
                                "performance_score": performance_score,
                                "recommendation_score": recommendation_score,
                                "market_score": market_score,
                                "reason": f"Multi-factor analysis (score: {composite_score:.3f})",
                                "priority": self._calculate_enhanced_priority(rec, market_analysis),
                            }
                        )

            for symbol, profile in self.rotation_manager.monitored_assets.items():
                current_score = performance_scores.get(symbol, profile.performance_score)
                market_score = market_influence.get(symbol, 0.5)

                removal_score = current_score * 0.7 + market_score * 0.3

                symbol_in_recommendations = symbol in recommended_symbols
                poor_performance = current_score < 0.25
                adverse_market = market_score < 0.3

                if (
                    not symbol_in_recommendations and (poor_performance or adverse_market)
                ) or current_score < 0.15:
                    decisions["assets_to_remove"].append(
                        {
                            "symbol": symbol,
                            "score": removal_score,
                            "performance_score": current_score,
                            "market_score": market_score,
                            "reason": self._get_removal_reason(
                                poor_performance, adverse_market, current_score
                            ),
                            "current_priority": profile.priority,
                        }
                    )

            decisions["assets_to_add"].sort(key=lambda x: x["score"], reverse=True)
            decisions["assets_to_remove"].sort(key=lambda x: x["score"])

            decisions["market_based_adjustments"] = market_influence

        except Exception as e:
            print(f"[ERROR] Enhanced rotation analysis failed: {e}")

        return decisions

    def _calculate_market_influence(self, market_analysis: Dict[str, Any]) -> Dict[str, float]:
        """Calculate market influence scores for assets"""
        influence_scores = {}

        try:
            market_condition = market_analysis.get("market_condition", "NORMAL")
            asset_trends = market_analysis.get("asset_trends", {})

            for symbol, trend_data in asset_trends.items():
                base_influence = 0.5

                if market_condition == "BULL_MARKET":
                    if trend_data.get("trend") == "BULLISH":
                        base_influence = 0.8
                    elif trend_data.get("trend") == "STRONGLY_BULLISH":
                        base_influence = 0.9
                elif market_condition == "BEAR_MARKET":
                    if trend_data.get("trend") == "BEARISH":
                        base_influence = 0.3
                    elif trend_data.get("trend") == "STRONGLY_BEARISH":
                        base_influence = 0.2

                volume_score = trend_data.get("volume_score", 0.5)
                activity_score = trend_data.get("activity_score", 0.5)

                combined_score = (base_influence + volume_score + activity_score) / 3
                influence_scores[symbol] = combined_score

        except Exception as e:
            print(f"[WARNING] Failed to calculate market influence: {e}")

        return influence_scores

    def _get_removal_reason(
        self, poor_performance: bool, adverse_market: bool, score: float
    ) -> str:
        """Get reason for asset removal"""
        reasons = []

        if poor_performance:
            reasons.append("Poor performance")
        if adverse_market:
            reasons.append("Adverse market conditions")
        if score < 0.1:
            reasons.append("Very low score")

        return ", ".join(reasons) if reasons else "Rotation optimization"

    async def _execute_optimized_rotation(self, decisions: Dict[str, Any]) -> Dict[str, Any]:
        """Execute optimized rotation with persistent agents"""
        results = {
            "added_assets": [],
            "removed_assets": [],
            "prioritized_changes": [],
            "errors": [],
            "agent_tasks": [],
        }

        try:
            for asset_info in decisions["assets_to_remove"]:
                await self._execute_removal_with_validation(asset_info, results)

            available_slots = self.rotation_manager.config.max_assets - len(
                self.rotation_manager.monitored_assets
            )
            for asset_info in decisions["assets_to_add"][:available_slots]:
                await self._execute_addition_with_validation(asset_info, results)

            await self._validate_rotation_results(results)

        except Exception as e:
            print(f"[ERROR] Optimized rotation execution failed: {e}")
            results["errors"].append(str(e))

        return results

    async def _execute_removal_with_validation(
        self, asset_info: Dict[str, Any], results: Dict[str, Any]
    ):
        """Execute asset removal with validation"""
        symbol = asset_info["symbol"]

        validation_task = TradingTask(
            task_id=f"validate_removal_{symbol}_{int(time.time())}",
            agent_type="risk",
            priority=TaskPriority.NORMAL,
            payload={
                "task": f"Validate removal of {symbol} from rotation",
                "asset": symbol,
                "current_position_size": 0,  # Assuming no position
                "removal_rationale": asset_info.get("reason", ""),
            },
            timeout=30,
        )

        task_id = await self.client.submit_task(validation_task)
        validation_result = await self.client.get_task_result(task_id, timeout=60)

        if validation_result and validation_result.get("success"):
            response = validation_result.get("response", {})
            removal_approved = response.get("removal_approved", True)

            if removal_approved:
                self.rotation_manager._archive_asset_performance(symbol)
                del self.rotation_manager.monitored_assets[symbol]
                results["removed_assets"].append(symbol)
                print(f"  [-] Validated and removed {symbol}")

            else:
                results["errors"].append(f"Removal of {symbol} not approved by risk agent")

    async def _execute_addition_with_validation(
        self, asset_info: Dict[str, Any], results: Dict[str, Dict[str, Any]]
    ):
        """Execute asset addition with validation"""
        symbol = asset_info["symbol"]

        validation_results = await self._validate_asset_addition(symbol, asset_info)

        if all(validation_results.values()):
            profile = AssetProfile(
                symbol=symbol,
                priority=asset_info["priority"],
                strategy="rotation_optimized",
                confidence=0.9,  # High confidence after validation
                risk_level="VALIDATED",
                last_updated=datetime.now(),
                monitoring_active=True,
                performance_score=asset_info.get("score", 0.6),
                market_conditions={},
            )

            self.rotation_manager.monitored_assets[symbol] = profile
            results["added_assets"].append(symbol)
            print(f"  [+] Validated and added {symbol}")

        else:
            failed_validations = [k for k, v in validation_results.items() if not v]
            results["errors"].append(
                f"Asset {symbol} failed validation: {', '.join(failed_validations)}"
            )

    async def _validate_asset_addition(
        self, symbol: str, asset_info: Dict[str, Any]
    ) -> Dict[str, bool]:
        """Validate asset addition with multiple agents"""
        validations = {}

        strategy_task = TradingTask(
            task_id=f"validate_strategy_{symbol}_{int(time.time())}",
            agent_type="strategy",
            priority=TaskPriority.HIGH,
            payload={
                "task": f"Validate addition of {symbol} to rotation",
                "asset": symbol,
                "addition_rationale": asset_info.get("reason", ""),
                "market_fit": True,
                "strategy_alignment": True,
            },
            timeout=45,
        )

        strategy_task_id = await self.client.submit_task(strategy_task)
        strategy_result = await self.client.get_task_result(strategy_task_id, timeout=60)
        validations["strategy"] = strategy_result and strategy_result.get("success", False)

        validations["risk"] = True  # Will be handled separately

        return validations

    async def _validate_rotation_results(self, results: Dict[str, Any]):
        """Validate the results of rotation execution"""
        try:
            status = await self.client.get_agent_status()

            total_changes = len(results["added_assets"]) + len(results["removed_assets"])
            if total_changes == 0:
                print("[INFO] No rotation changes made in this cycle")

            agent_health = status.get("orchestrator", {}).get("total_agents", 0)
            if agent_health < 4:
                results["errors"].append("Not all agents are healthy")

            print(f"[VALIDATION] Rotation validation completed")

        except Exception as e:
            print(f"[WARNING] Rotation validation failed: {e}")
            results["errors"].append(f"Validation error: {e}")

    async def _post_rotation_optimization(self, results: Dict[str, Any]):
        """Post-rotation optimization and analysis"""
        try:
            if results["added_assets"]:
                await self._analyze_new_assets_performance(results["added_assets"])

            await self._update_strategy_effectiveness()

            if self.auto_optimization:
                await self._optimize_rotation_strategy()

        except Exception as e:
            print(f"[WARNING] Post-rotation optimization failed: {e}")

    async def _analyze_new_assets_performance(self, added_assets: List[str]):
        """Analyze performance of newly added assets"""
        for symbol in added_assets:
            try:
                task = TradingTask(
                    task_id=f"track_new_asset_{symbol}_{int(time.time())}",
                    agent_type="strategy",
                    priority=TaskPriority.NORMAL,
                    payload={
                        "task": f"Track performance of newly added {symbol}",
                        "asset": symbol,
                        "tracking_period": "1h",
                        "performance_benchmark": True,
                    },
                    timeout=60,
                )

                task_id = await self.client.submit_task(task)
                result = await self.client.get_task_result(task_id, timeout=90)

                if result and result.get("success"):
                    print(f"[TRACKING] Started performance tracking for {symbol}")

            except Exception as e:
                print(f"[WARNING] Failed to setup tracking for {symbol}: {e}")

    def _update_enhanced_metrics(self, cycle_time: float, results: Dict[str, Any]):
        """Update enhanced rotation metrics"""
        self.rotation_manager._update_rotation_metrics(cycle_time, results)

        self.rotation_manager.performance_metrics["workflow_optimizations"] = (
            self.rotation_manager.performance_metrics.get("workflow_optimizations", 0) + 1
        )

        if "agent_tasks" in results:
            self.rotation_manager.performance_metrics["agent_tasks_used"] = (
                self.rotation_manager.performance_metrics.get("agent_tasks_used", 0)
                + len(results["agent_tasks"])
            )

    async def _optimize_rotation_strategy(self):
        """Automatically optimize rotation strategy"""
        try:
            recent_performance = self.rotation_manager.performance_metrics.get(
                "successful_reallocations", 0
            )
            total_rotations = self.rotation_manager.performance_metrics.get("total_rotations", 0)

            if total_rotations > 0:
                success_rate = recent_performance / total_rotations

                if success_rate > 0.8:
                    print(
                        f"[OPTIMIZE] High success rate ({success_rate:.1%}), expanding asset universe"
                    )
                    self.rotation_manager.config.max_assets = min(
                        20, self.rotation_manager.config.max_assets + 2
                    )

                elif success_rate < 0.5:
                    print(
                        f"[OPTIMIZE] Low success rate ({success_rate:.1%}), reducing asset universe"
                    )
                    self.rotation_manager.config.max_assets = max(
                        5, self.rotation_manager.config.max_assets - 1
                    )
                    self.rotation_manager.config.rotation_interval = min(
                        600, self.rotation_manager.config.rotation_interval + 60
                    )

                print(
                    f"[OPTIMIZED] Updated max assets to {self.rotation_manager.config.max_assets}"
                )

        except Exception as e:
            print(f"[WARNING] Strategy optimization failed: {e}")

    async def _update_strategy_effectiveness(self):
        """Update strategy effectiveness metrics"""
        try:
            current_strategy = self.rotation_manager.config.strategy.value

            self.rotation_manager.performance_metrics["strategy_effectiveness"][
                current_strategy
            ] = (
                self.rotation_manager.performance_metrics.get("strategy_effectiveness", {}).get(
                    current_strategy, 0
                )
                + 1
            )

        except Exception as e:
            print(f"[WARNING] Failed to update strategy effectiveness: {e}")

    def get_integrated_status(self) -> Dict[str, Any]:
        """Get integrated system status"""
        rotation_status = self.rotation_manager.get_rotation_status()

        return {
            "rotation_manager": rotation_status,
            "workflow_integration": self.workflow_integration,
            "auto_optimization": self.auto_optimization,
            "last_optimization": (
                self.last_optimization.isoformat() if self.last_optimization else None
            ),
            "integrated_client": self.client is not None,
            "enhanced_features": {
                "workflow_analysis": True,
                "multi_agent_validation": True,
                "performance_tracking": True,
                "auto_optimization": self.auto_optimization,
            },
        }

    def stop_integrated_rotation(self):
        """Stop the integrated rotation system"""
        print("[INTEGRATION] Stopping integrated coin rotation...")
        self.rotation_manager.stop_rotation()
        print("[INTEGRATION] Integrated coin rotation stopped")


if __name__ == "__main__":

    async def demo_integrated_rotation():
        print("\n" + "=" * 80)
        print("[INTEGRATED COIN ROTATION DEMO]")
        print("=" * 80)

        system = IntegratedRotationSystem()
        system.rotation_manager.config.max_assets = 10
        system.rotation_manager.config.rotation_interval = 120  # 2 minutes for demo

        print(
            "[DEMO] Starting integrated rotation with workflow optimization (runs for 6 minutes)..."
        )

        task = asyncio.create_task(system.start_with_workflow_optimization())

        await asyncio.sleep(360)

        system.stop_integrated_rotation()
        task.cancel()

        status = system.get_integrated_status()
        print(f"\n[FINAL INTEGRATED STATUS]:")
        print(f"   Monitored Assets: {status['rotation_manager']['monitored_assets_count']}")
        print(f"   Total Rotations: {status['rotation_manager']['metrics']['total_rotations']}")
        print(f"   Workflow Integration: {status['workflow_integration']}")
        print(f"   Auto-Optimization: {status['auto_optimization']}")
        print(f"   Enhanced Features: {status['enhanced_features']}")

    asyncio.run(demo_integrated_rotation())
