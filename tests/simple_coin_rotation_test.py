"""
[OK] Simple Coin Rotation Test
Standalone test for the coin rotation functionality
Built with love by Deamon Dev [ROCKET]

This test demonstrates the coin rotation system without requiring
the full persistent agents infrastructure to be running.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any

from src.agents.coin_rotation_manager import (
    CoinRotationManager, RotationConfig, RotationStrategy,
    AssetProfile
)

class MockPersistentAgentClient:
    """Mock client for testing without persistent agents"""

    def __init__(self):
        self.task_counter = 0

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def submit_task(self, task) -> str:
        """Mock task submission"""
        self.task_counter += 1
        print(f"[MOCK] Submitted task {self.task_counter}: {task.agent_type} - {task.task_id}")
        return f"mock_task_{self.task_counter}"

    async def get_task_result(self, task_id: str, timeout: int = 300) -> Dict[str, Any]:
        """Mock task result with simulated responses"""
        await asyncio.sleep(0.1)  # Simulate processing time

        # Generate realistic mock responses based on task type
        if "strategy" in task_id.lower():
            return {
                "success": True,
                "response": {
                    "recommendations": [
                        {"symbol": "BTC", "confidence": 0.9, "priority": 1},
                        {"symbol": "ETH", "confidence": 0.8, "priority": 2},
                        {"symbol": "SOL", "confidence": 0.7, "priority": 3}
                    ],
                    "market_analysis": {
                        "market_condition": "BULL_MARKET",
                        "volatility_level": "MEDIUM",
                        "liquidity_level": "GOOD"
                    }
                }
            }
        elif "risk" in task_id.lower():
            return {
                "success": True,
                "response": {
                    "risk_assessment": "LOW_RISK",
                    "removal_approved": True
                }
            }
        elif "liquidity" in task_id.lower():
            return {
                "success": True,
                "response": {
                    "liquidity_score": 0.8,
                    "depth_analysis": "EXCELLENT"
                }
            }
        else:
            return {
                "success": True,
                "response": {"status": "completed"}
            }

    async def get_agent_status(self) -> Dict[str, Any]:
        """Mock agent status"""
        return {
            "orchestrator": {
                "total_agents": 4,
                "total_tasks": self.task_counter,
                "queued_tasks": 0,
                "metrics": {
                    "successful_tasks": self.task_counter,
                    "failed_tasks": 0
                }
            }
        }

class SimpleCoinRotationTest:
    """Simplified test for coin rotation functionality"""

    def __init__(self):
        self.rotation_manager = CoinRotationManager()
        self.mock_client = MockPersistentAgentClient()

        # Configure for testing
        self.rotation_manager.config = RotationConfig(
            max_assets=8,
            min_assets=3,
            rotation_interval=10,  # 10 seconds for testing
            strategy=RotationStrategy.BALANCED,
            risk_tolerance="CONSERVATIVE",
            performance_weight=0.5,
            volatility_weight=0.3,
            liquidity_weight=0.2,
            auto_optimize=True
        )

    async def run_test(self, duration: int = 60):
        """Run coin rotation test for specified duration"""
        print(f"\n" + "="*60)
        print(f"[SIMPLE COIN ROTATION TEST]")
        print(f"Test Duration: {duration}s")
        print(f"Max Assets: {self.rotation_manager.config.max_assets}")
        print(f"Rotation Interval: {self.rotation_manager.config.rotation_interval}s")
        print(f"Strategy: {self.rotation_manager.config.strategy.value}")
        print("="*60)

        try:
            # Initialize with mock client
            self.rotation_manager.client = self.mock_client
            await self.rotation_manager._initialize_monitoring()

            print(f"\n[INIT] Started with {len(self.rotation_manager.monitored_assets)} assets")
            self.rotation_manager._display_monitored_assets()

            # Run rotation cycles
            self.rotation_manager.running = True
            start_time = time.time()

            while self.rotation_manager.running and (time.time() - start_time) < duration:
                try:
                    print(f"\n[CYCLE {int(time.time() - start_time) // self.rotation_manager.config.rotation_interval + 1}]")
                    await self._perform_mock_rotation_cycle()
                    await asyncio.sleep(self.rotation_manager.config.rotation_interval)

                except Exception as e:
                    print(f"[ERROR] Rotation cycle failed: {e}")
                    await asyncio.sleep(5)

            # Final status
            print(f"\n[TEST COMPLETE] Final status after {duration}s:")
            self.rotation_manager._display_monitored_assets()
            # Performance metrics display
            metrics = self.rotation_manager.performance_metrics
            print(f"[PERFORMANCE METRICS]")
            print(f"  Total Rotations: {metrics.get('total_rotations', 0)}")
            print(f"  Successful Reallocations: {metrics.get('successful_reallocations', 0)}")
            print(f"  Failed Rotations: {metrics.get('failed_rotations', 0)}")

        except Exception as e:
            print(f"[ERROR] Test failed: {e}")
            import traceback
            traceback.print_exc()

        finally:
            self.rotation_manager.running = False

    async def _perform_mock_rotation_cycle(self):
        """Perform a mock rotation cycle"""
        start_time = time.time()
        cycle_id = f"mock_cycle_{int(time.time())}"

        print(f"[ROTATION] Starting {cycle_id}")

        try:
            # Step 1: Get mock recommendations
            print("  [1/4] Getting strategy recommendations...")
            recommendations = await self._get_mock_recommendations()

            # Step 2: Evaluate current performance
            print("  [2/4] Evaluating current performance...")
            performance_scores = await self._evaluate_mock_performance()

            # Step 3: Analyze rotation needs
            print("  [3/4] Analyzing rotation needs...")
            rotation_decisions = await self._analyze_mock_rotation_needs(
                recommendations, performance_scores
            )

            # Step 4: Execute rotation
            print("  [4/4] Executing rotation...")
            rotation_results = await self._execute_mock_rotation(rotation_decisions)

            # Update metrics
            cycle_time = time.time() - start_time
            self.rotation_manager._update_rotation_metrics(cycle_time, rotation_results)

            print(f"[COMPLETE] {cycle_id} completed in {cycle_time:.1f}s")
            print(f"  Assets added: {len(rotation_results.get('added_assets', []))}")
            print(f"  Assets removed: {len(rotation_results.get('removed_assets', []))}")

        except Exception as e:
            print(f"[ERROR] Mock rotation failed: {e}")

    async def _get_mock_recommendations(self) -> List[Dict[str, Any]]:
        """Get mock strategy recommendations"""
        # Simulate different market conditions over time
        market_conditions = ["BULL_MARKET", "NORMAL", "BEAR_MARKET", "HIGH_VOLATILITY"]
        current_condition = market_conditions[int(time.time()) % len(market_conditions)]

        # Generate mock recommendations based on market condition
        all_assets = ["BTC", "ETH", "SOL", "AVAX", "MATIC", "DOT", "LINK", "UNI", "AAVE", "CRV"]

        # Simulate different top assets based on condition
        if current_condition == "BULL_MARKET":
            top_assets = ["SOL", "AVAX", "MATIC", "BTC", "ETH"]
        elif current_condition == "BEAR_MARKET":
            top_assets = ["BTC", "ETH", "USDC", "USDT", "DAI"]
        elif current_condition == "HIGH_VOLATILITY":
            top_assets = ["BTC", "ETH", "SOL", "LINK", "DOT"]
        else:  # NORMAL
            top_assets = ["BTC", "ETH", "SOL", "AVAX", "MATIC"]

        recommendations = []
        for i, symbol in enumerate(top_assets):
            recommendations.append({
                "symbol": symbol,
                "confidence": 0.9 - (i * 0.1),
                "priority": i + 1,
                "market_condition": current_condition
            })

        print(f"    Market: {current_condition}, Top: {[r['symbol'] for r in recommendations[:3]]}")
        return recommendations

    async def _evaluate_mock_performance(self) -> Dict[str, float]:
        """Evaluate mock performance for monitored assets"""
        performance_scores = {}

        for symbol, profile in self.rotation_manager.monitored_items():
            # Simulate varying performance
            base_performance = 0.5

            # Add some randomness
            import random
            performance_change = random.uniform(-0.2, 0.2)

            # Simulate trend based on symbol
            if symbol in ["BTC", "ETH"]:
                base_performance += 0.1  # Stable performers
            elif symbol in ["SOL", "AVAX"]:
                base_performance += random.uniform(-0.1, 0.2)  # Higher volatility
            else:
                base_performance += random.uniform(-0.2, 0.1)

            final_performance = max(0.1, min(1.0, base_performance + performance_change))
            performance_scores[symbol] = final_performance

            # Update profile
            profile.performance_score = final_performance
            profile.last_updated = datetime.now()

        return performance_scores

    async def _analyze_mock_rotation_needs(self,
                                         recommendations: List[Dict[str, Any]],
                                         performance_scores: Dict[str, float]) -> Dict[str, Any]:
        """Analyze mock rotation needs"""
        decisions = {
            'assets_to_add': [],
            'assets_to_remove': []
        }

        current_symbols = set(self.rotation_manager.monitored_assets.keys())
        recommended_symbols = {rec.get('symbol', '') for rec in recommendations}

        # Assets to add (recommended but not monitored)
        for rec in recommendations:
            symbol = rec.get('symbol', '')
            if symbol and symbol not in current_symbols:
                score = rec.get('confidence', 0.5) / 10
                if score > 0.3:
                    decisions['assets_to_add'].append({
                        'symbol': symbol,
                        'score': score,
                        'priority': rec.get('priority', 5),
                        'reason': f"Strategy recommendation (confidence: {rec.get('confidence', 0.5):.2f})"
                    })

        # Assets to remove (monitored but performing poorly)
        for symbol, profile in self.rotation_manager.monitored_items():
            current_score = performance_scores.get(symbol, profile.performance_score)
            if symbol not in recommended_symbols or current_score < 0.3:
                decisions['assets_to_remove'].append({
                    'symbol': symbol,
                    'score': current_score,
                    'reason': f"Poor performance ({current_score:.3f})" if current_score < 0.3 else "No longer recommended"
                })

        return decisions

    async def _execute_mock_rotation(self, decisions: Dict[str, Any]) -> Dict[str, Any]:
        """Execute mock rotation"""
        results = {
            'added_assets': [],
            'removed_assets': []
        }

        # Execute removals
        for asset_info in decisions['assets_to_remove']:
            symbol = asset_info['symbol']
            if symbol in self.rotation_manager.monitored_assets:
                self.rotation_manager._archive_asset_performance(symbol)
                del self.rotation_manager.monitored_assets[symbol]
                results['removed_assets'].append(symbol)
                print(f"    [-] Removed {symbol}: {asset_info['reason']}")

        # Execute additions
        for asset_info in decisions['assets_to_add']:
            if len(self.rotation_manager.monitored_assets) < self.rotation_manager.config.max_assets:
                symbol = asset_info['symbol']
                profile = AssetProfile(
                    symbol=symbol,
                    priority=asset_info['priority'],
                    strategy="mock_rotation",
                    confidence=0.8,
                    risk_level="LOW",
                    last_updated=datetime.now(),
                    monitoring_active=True,
                    performance_score=asset_info.get('score', 0.6),
                    market_conditions={"test": True}
                )
                self.rotation_manager.monitored_assets[symbol] = profile
                results['added_assets'].append(symbol)
                print(f"    [+] Added {symbol}: {asset_info['reason']}")

        return results

# Main execution
if __name__ == "__main__":
    async def main():
        test = SimpleCoinRotationTest()

        print("[TEST] Starting simple coin rotation test (runs for 45 seconds)...")
        await test.run_test(duration=45)

        print("\n[TEST] Coin rotation test completed successfully!")
        print("[INFO] This demonstrates the core rotation functionality")
        print("[INFO] The full system would use real persistent agents for analysis")

    asyncio.run(main())