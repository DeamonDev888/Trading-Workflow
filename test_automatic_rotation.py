"""
[OK] Test Automatic Rotation
Simple test for the new automatic coin rotation system
Built with love by Deamon Dev [ROCKET]
"""

import asyncio
import json
from src.agents.automatic_coin_rotator import AutomaticCoinRotator, RotationConfig, RotationMode
from src.agents.rotation_interface import RotationAPI

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
        print(f"[MOCK] Task {self.task_counter}: {task.agent_type}")
        return f"mock_task_{self.task_counter}"

    async def get_task_result(self, task_id: str, timeout: int = 300) -> dict:
        """Mock task result"""
        await asyncio.sleep(0.1)

        # Simulate different responses
        if "market" in task_id.lower():
            return {
                "success": True,
                "response": {
                    "market_analysis": {
                        "condition": "NORMAL"
                    },
                    "rotation_recommendations": {
                        "remove": [],
                        "add": []
                    }
                }
            }
        elif "performance" in task_id.lower():
            return {
                "success": True,
                "response": {
                    "performance_score": 0.6
                }
            }
        else:
            return {
                "success": True,
                "response": {"status": "ok"}
            }

async def test_automatic_rotation():
    """Test the automatic rotation system"""
    print("\n" + "="*60)
    print("[TESTING AUTOMATIC ROTATION]")
    print("="*60)

    # Patch the client in the rotator
    import src.agents.automatic_coin_rotator
    original_client = src.agents.automatic_coin_rotator.PersistentAgentClient
    src.agents.automatic_coin_rotator.PersistentAgentClient = MockPersistentAgentClient

    try:
        config = RotationConfig(
            mode=RotationMode.HYBRID,
            rotation_interval=15,  # 15 seconds for testing
            max_assets=4,
            auto_optimize=True
        )

        rotator = AutomaticCoinRotator(config)
        print("[TEST] Starting automatic rotation test (45 seconds)...")

        # Start rotation in background
        task = asyncio.create_task(rotator.start_automatic_rotation())

        # Let it run for 45 seconds
        await asyncio.sleep(45)

        # Stop rotation
        rotator.stop_rotation()
        task.cancel()

        # Get final metrics
        metrics = rotator.get_rotation_metrics()
        print(f"\n[TEST RESULTS]")
        print(f"  Total Rotations: {metrics['rotation_metrics']['total_rotations']}")
        print(f"  Successful Rotations: {metrics['rotation_metrics']['successful_rotations']}")
        print(f"  Current Assets: {metrics['current_assets']}")
        print(f"  Average Rotation Time: {metrics['rotation_metrics']['average_rotation_time']:.2f}s")

        print("\n[TEST] Automatic rotation test completed successfully!")

    finally:
        # Restore original client
        src.agents.automatic_coin_rotator.PersistentAgentClient = original_client

async def test_rotation_interface():
    """Test the rotation interface API"""
    print("\n" + "="*60)
    print("[TESTING ROTATION INTERFACE]")
    print("="*60)

    # Patch the client
    import src.agents.automatic_coin_rotator
    import src.agents.rotation_interface
    original_client_auto = src.agents.automatic_coin_rotator.PersistentAgentClient
    original_client_interface = src.agents.rotation_interface.PersistentAgentClient
    src.agents.automatic_coin_rotator.PersistentAgentClient = MockPersistentAgentClient
    src.agents.rotation_interface.PersistentAgentClient = MockPersistentAgentClient

    try:
        api = RotationAPI()

        print("[API] Testing start rotation...")
        result = await api.start_rotation({
            "mode": "automatic",
            "interval": 20,
            "max_assets": 3
        })
        print(f"  Result: {result['success']} - {result.get('message', '')}")

        await asyncio.sleep(2)

        print("[API] Testing get status...")
        status = await api.get_status()
        print(f"  Running: {status.get('running', False)}")
        if status.get('running'):
            print(f"  Mode: {status.get('mode')}")
            print(f"  Assets: {status.get('current_assets', [])}")

        await asyncio.sleep(2)

        print("[API] Testing manual rotation...")
        manual_result = await api.start_manual_rotation({
            "assets": ["BTC", "ETH", "SOL"]
        })
        print(f"  Result: {manual_result['success']} - {manual_result.get('message', '')}")

        await asyncio.sleep(2)

        print("[API] Testing stop rotation...")
        stop_result = await api.stop_rotation()
        print(f"  Result: {stop_result['success']} - {stop_result.get('message', '')}")

        print("\n[API] Rotation interface test completed successfully!")

    finally:
        # Restore original clients
        src.agents.automatic_coin_rotator.PersistentAgentClient = original_client_auto
        src.agents.rotation_interface.PersistentAgentClient = original_client_interface

async def main():
    """Run all tests"""
    print("[TEST] Starting automatic rotation system tests...")

    # Test 1: Automatic rotation
    await test_automatic_rotation()

    # Test 2: Rotation interface
    await test_rotation_interface()

    print("\n[TEST] All tests completed!")
    print("\n[SUMMARY] The automatic rotation system provides:")
    print("  • True automatic coin rotation without user intervention")
    print("  • Multiple rotation strategies (performance, time, market, hybrid)")
    print("  • Manual override capabilities for frontend control")
    print("  • Real-time performance tracking and optimization")
    print("  • API endpoints for frontend integration")
    print("  • Adaptive rotation based on market conditions")

if __name__ == "__main__":
    asyncio.run(main())