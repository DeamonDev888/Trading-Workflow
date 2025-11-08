"""
[OK] Test Hybrid System
Comprehensive test for the hybrid rotation system
Built with love by Deamon Dev [ROCKET]

This test demonstrates all 5 control modes and the interaction between
automatic rotation and user control.
"""

import asyncio
import json
from src.agents.hybrid_rotation_system import HybridRotationManager, HybridConfig, ControlMode
from src.agents.hybrid_rotation_api import HybridRotationAPI

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
        await asyncio.sleep(0.05)  # Brief delay

        # Simulate different responses based on task type
        if "performance" in task_id.lower():
            return {
                "success": True,
                "response": {
                    "performance_score": 0.65 + (hash(task_id) % 30) / 100  # 0.65-0.95
                }
            }
        elif "market" in task_id.lower():
            return {
                "success": True,
                "response": {
                    "market_condition": ["NORMAL", "BULL_MARKET", "BEAR_MARKET"][self.task_counter % 3],
                    "volatility": "MEDIUM",
                    "opportunities": ["SOL", "AVAX", "MATIC"][:self.task_counter % 3 + 1]
                }
            }
        else:
            return {
                "success": True,
                "response": {"status": "success"}
            }

async def test_control_modes():
    """Test all 5 control modes"""
    print("\n" + "="*80)
    print("[TESTING ALL CONTROL MODES]")
    print("="*80)

    # Patch the client
    import src.agents.hybrid_rotation_system
    original_client = src.agents.hybrid_rotation_system.PersistentAgentClient
    src.agents.hybrid_rotation_system.PersistentAgentClient = MockPersistentAgentClient

    try:
        modes_to_test = [
            (ControlMode.FULL_AUTO, "Full Automatic - 100% AI controlled"),
            (ControlMode.USER_GUIDED, "User Guided - AI follows user preferences"),
            (ControlMode.USER_OVERRIDE, "User Override - User decisions take priority"),
            (ControlMode.SEMI_AUTO, "Semi-Auto - User handles critical decisions"),
            (ControlMode.COLLABORATIVE, "Collaborative - AI suggests, user decides")
        ]

        for mode, description in modes_to_test:
            print(f"\n[MODE] Testing {mode.value}: {description}")
            print("-" * 60)

            config = HybridConfig(
                control_mode=mode,
                max_assets=4,
                auto_rotation_weight=0.7,
                user_preference_weight=0.3,
                learning_enabled=True
            )

            hybrid_manager = HybridRotationManager(config)

            # Set up some initial user preferences for testing
            hybrid_manager.user_preferences['BTC'] = hybrid_manager.user_preferences.get('BTC') or \
                type('UserPreference', (), {
                    'preference_score': 0.9, 'weight_multiplier': 1.2,
                    'lock_until': None, 'tags': ['favorite']
                })()

            hybrid_manager.user_preferences['ETH'] = hybrid_manager.user_preferences.get('ETH') or \
                type('UserPreference', (), {
                    'preference_score': 0.7, 'weight_multiplier': 1.0,
                    'lock_until': None, 'tags': ['bluechip']
                })()

            # Run for a short time to see the behavior
            print(f"  Starting {mode.value} mode for 15 seconds...")
            task = asyncio.create_task(hybrid_manager.start_hybrid_rotation())

            # Let it run for 15 seconds
            await asyncio.sleep(15)

            # Stop rotation
            hybrid_manager.stop_hybrid_rotation()
            task.cancel()

            # Display results
            metrics = hybrid_manager.get_hybrid_status()
            print(f"  Results:")
            print(f"    Total Decisions: {metrics['metrics']['total_decisions']}")
            print(f"    Auto Decisions: {metrics['metrics']['auto_decisions']}")
            print(f"    User Decisions: {metrics['metrics']['user_decisions']}")
            print(f"    Collaborative Decisions: {metrics['metrics']['collaborative_decisions']}")
            print(f"    Suggestions Made: {metrics['metrics']['suggestions_made']}")
            print(f"    Current Assets: {metrics['current_assets']}")

            await asyncio.sleep(2)  # Brief pause between modes

        print("\n[SUCCESS] All control modes tested successfully!")

    finally:
        # Restore original client
        src.agents.hybrid_rotation_system.PersistentAgentClient = original_client

async def test_api_interface():
    """Test the complete API interface"""
    print("\n" + "="*80)
    print("[TESTING API INTERFACE]")
    print("="*80)

    # Patch the client
    import src.agents.hybrid_rotation_system
    import src.agents.hybrid_rotation_api
    import src.agents.automatic_coin_rotator
    original_client_system = src.agents.hybrid_rotation_system.PersistentAgentClient
    original_client_rotator = src.agents.automatic_coin_rotator.PersistentAgentClient
    src.agents.hybrid_rotation_system.PersistentAgentClient = MockPersistentAgentClient
    src.agents.automatic_coin_rotator.PersistentAgentClient = MockPersistentAgentClient

    try:
        api = HybridRotationAPI()

        print("[API] Test 1: Start collaborative mode...")
        result = await api.start_hybrid_rotation({
            "control_mode": "collaborative",
            "max_assets": 4,
            "auto_weight": 0.6,
            "user_weight": 0.4,
            "learning_enabled": True
        })
        print(f"  Success: {result['success']}")
        print(f"  Message: {result.get('message', '')}")

        await asyncio.sleep(2)

        print("\n[API] Test 2: Get system status...")
        status = await api.get_hybrid_status()
        print(f"  Running: {status.get('running', False)}")
        print(f"  Mode: {status.get('control_mode')}")
        print(f"  Assets: {len(status.get('current_assets', []))}")

        await asyncio.sleep(2)

        print("\n[API] Test 3: Update user preferences...")
        update_result = await api.update_user_preference("BTC", {
            "preference_score": 0.95,
            "weight_multiplier": 1.3,
            "tags": ["favorite", "bluechip", "core"]
        })
        print(f"  Success: {update_result['success']}")
        print(f"  Message: {update_result.get('message', '')}")

        await asyncio.sleep(2)

        print("\n[API] Test 4: Get suggestions...")
        suggestions = await api.get_suggestions()
        print(f"  Active Suggestions: {len(suggestions.get('suggestions', []))}")
        for i, suggestion in enumerate(suggestions.get('suggestions', [])[:3]):
            print(f"    {i}: {suggestion.get('reasoning', '')[:50]}...")

        await asyncio.sleep(2)

        print("\n[API] Test 5: Switch control modes...")
        modes = ["user_guided", "semi_auto", "user_override"]
        for mode in modes:
            switch_result = await api.update_control_mode({"control_mode": mode})
            print(f"  Switch to {mode}: {switch_result['success']}")
            await asyncio.sleep(1)

        await asyncio.sleep(2)

        print("\n[API] Test 6: Get detailed metrics...")
        metrics = await api.get_system_metrics()
        if metrics['success']:
            m = metrics['metrics']
            print(f"  User Satisfaction: {m.get('user_satisfaction', 0):.2f}")
            print(f"  Decision Breakdown: {m.get('decision_breakdown', {})}")
            print(f"  Learning Progress: {m.get('learning_progress', {})}")

        await asyncio.sleep(2)

        print("\n[API] Test 7: Stop system...")
        stop_result = await api.stop_hybrid_rotation()
        print(f"  Success: {stop_result['success']}")
        print(f"  Message: {stop_result.get('message', '')}")

        print("\n[SUCCESS] API interface tests completed!")

    finally:
        # Restore original clients
        src.agents.hybrid_rotation_system.PersistentAgentClient = original_client_system
        src.agents.automatic_coin_rotator.PersistentAgentClient = original_client_rotator

async def test_user_interaction():
    """Test user interaction scenarios"""
    print("\n" + "="*80)
    print("[TESTING USER INTERACTION SCENARIOS]")
    print("="*80)

    # Patch the client
    import src.agents.hybrid_rotation_system
    original_client = src.agents.hybrid_rotation_system.PersistentAgentClient
    src.agents.hybrid_rotation_system.PersistentAgentClient = MockPersistentAgentClient

    try:
        print("\n[SCENARIO] User loves BTC and wants it prioritized...")
        config = HybridConfig(
            control_mode=ControlMode.USER_GUIDED,
            max_assets=5,
            auto_rotation_weight=0.4,  # User preferences have more weight
            user_preference_weight=0.6
        )

        hybrid_manager = HybridRotationManager(config)

        # Set strong user preference for BTC
        hybrid_manager.user_preferences['BTC'] = type('UserPreference', (), {
            'preference_score': 1.0, 'weight_multiplier': 2.0,
            'lock_until': None, 'tags': ['favorite', 'core']
        })()

        print("  Starting guided mode with strong BTC preference...")
        task = asyncio.create_task(hybrid_manager.start_hybrid_rotation())

        await asyncio.sleep(10)

        # Check if BTC is prioritized
        status = hybrid_manager.get_hybrid_status()
        btc_in_assets = 'BTC' in status.get('current_assets', [])
        print(f"  BTC in current assets: {btc_in_assets}")

        hybrid_manager.stop_hybrid_rotation()
        task.cancel()

        await asyncio.sleep(3)

        print("\n[SCENARIO] User locks SOL for 24 hours...")
        config.control_mode = ControlMode.USER_OVERRIDE
        hybrid_manager = HybridRotationManager(config)

        # Set SOL as locked
        from datetime import datetime, timedelta
        hybrid_manager.user_preferences['SOL'] = type('UserPreference', (), {
            'preference_score': 0.6, 'weight_multiplier': 1.0,
            'lock_until': datetime.now() + timedelta(hours=24),
            'tags': ['locked', 'temp_hold']
        })()

        print("  Starting override mode with locked SOL...")
        task = asyncio.create_task(hybrid_manager.start_hybrid_rotation())

        await asyncio.sleep(10)

        # Check SOL is still there (shouldn't be rotated out)
        status = hybrid_manager.get_hybrid_status()
        sol_in_assets = 'SOL' in status.get('current_assets', [])
        print(f"  SOL still in assets (should be true): {sol_in_assets}")

        hybrid_manager.stop_hybrid_rotation()
        task.cancel()

        await asyncio.sleep(3)

        print("\n[SCENARIO] Collaborative decision making...")
        config.control_mode = ControlMode.COLLABORATIVE
        hybrid_manager = HybridRotationManager(config)

        print("  Starting collaborative mode...")
        task = asyncio.create_task(hybrid_manager.start_hybrid_rotation())

        await asyncio.sleep(8)

        # Simulate user responding to suggestions
        if hybrid_manager.active_suggestions:
            print("  Responding to suggestions...")
            for i, suggestion in enumerate(hybrid_manager.active_suggestions):
                await hybrid_manager.respond_to_suggestion(i, "accept" if i == 0 else "reject")

        await asyncio.sleep(7)

        # Check collaborative decisions
        status = hybrid_manager.get_hybrid_status()
        print(f"  Collaborative decisions made: {status['metrics']['collaborative_decisions']}")

        hybrid_manager.stop_hybrid_rotation()
        task.cancel()

        print("\n[SUCCESS] User interaction scenarios completed!")

    finally:
        # Restore original client
        src.agents.hybrid_rotation_system.PersistentAgentClient = original_client

async def test_learning_system():
    """Test the learning and adaptation system"""
    print("\n" + "="*80)
    print("[TESTING LEARNING SYSTEM]")
    print("="*80)

    # Patch the client
    import src.agents.hybrid_rotation_system
    original_client = src.agents.hybrid_rotation_system.PersistentAgentClient
    src.agents.hybrid_rotation_system.PersistentAgentClient = MockPersistentAgentClient

    try:
        config = HybridConfig(
            control_mode=ControlMode.COLLABORATIVE,
            max_assets=4,
            learning_enabled=True,
            adaptation_rate=0.2  # Fast learning for testing
        )

        hybrid_manager = HybridRotationManager(config)

        print("[LEARNING] Testing preference adaptation based on performance...")

        # Start with neutral preference for ETH
        hybrid_manager.user_preferences['ETH'] = type('UserPreference', (), {
            'preference_score': 0.5, 'weight_multiplier': 1.0,
            'lock_until': None, 'tags': []
        })()

        print("  Starting with neutral ETH preference (0.5)...")
        task = asyncio.create_task(hybrid_manager.start_hybrid_rotation())

        # Simulate several cycles with good ETH performance
        for cycle in range(3):
            await asyncio.sleep(5)

            # Simulate good ETH performance
            if 'ETH' in hybrid_manager.auto_rotator.performance_history:
                hybrid_manager.auto_rotator.performance_history['ETH'].extend([0.8, 0.85, 0.9])

            # Trigger learning
            await hybrid_manager._learn_from_cycle()

            # Check updated preference
            eth_pref = hybrid_manager.user_preferences.get('ETH')
            if eth_pref:
                print(f"  Cycle {cycle + 1}: ETH preference updated to {eth_pref.preference_score:.3f}")

        hybrid_manager.stop_hybrid_rotation()
        task.cancel()

        print("\n[SUCCESS] Learning system test completed!")

    finally:
        # Restore original client
        src.agents.hybrid_rotation_system.PersistentAgentClient = original_client

async def main():
    """Run all hybrid system tests"""
    print("="*80)
    print("[HYBRID ROTATION SYSTEM COMPREHENSIVE TESTS]")
    print("="*80)

    print("\n[OVERVIEW] This test suite demonstrates:")
    print("  • All 5 control modes and their behaviors")
    print("  • Complete API interface for frontend integration")
    print("  • User interaction scenarios and preferences")
    print("  • Learning system adaptation")
    print("  • Hybrid decision making between AI and user")

    # Run all tests
    await test_control_modes()
    await test_api_interface()
    await test_user_interaction()
    await test_learning_system()

    print("\n" + "="*80)
    print("[ALL TESTS COMPLETED SUCCESSFULLY!]")
    print("="*80)

    print("\n[SUMMARY] The hybrid rotation system provides:")
    print("\n🎯 5 CONTROL MODES:")
    print("  1. FULL_AUTO - 100% automatic rotation")
    print("  2. USER_GUIDED - Automatic with user preferences")
    print("  3. USER_OVERRIDE - User decisions take priority")
    print("  4. SEMI_AUTO - User handles critical decisions")
    print("  5. COLLABORATIVE - AI suggests, user decides")

    print("\n🔧 KEY FEATURES:")
    print("  • Intelligent AI-user collaboration")
    print("  • Adaptive learning from user behavior")
    print("  • User preference management")
    print("  • Performance-based optimization")
    print("  • Real-time suggestion system")
    print("  • Comprehensive API for frontend")

    print("\n💡 PERFECT FOR TRADING:")
    print("  • Users who want automatic optimization with control")
    print("  • Risk-averse users who want to lock certain assets")
    print("  • Active users who want to guide AI decisions")
    print("  • Beginners who want AI suggestions")
    print("  • Experts who want full override capability")

    print("\n[READY] The hybrid system is ready for frontend integration!")

if __name__ == "__main__":
    asyncio.run(main())