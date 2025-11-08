"""
[OK] Persistent Agents Demo
Demonstration of the 4 persistent Claude Code CLI agents system
Built with love by Deamon Dev [ROCKET]

This demo shows:
1. Starting all agents
2. Submitting tasks to different agents
3. Running complete trading workflows
4. Monitoring agent performance
"""

import asyncio
import time
import json
from datetime import datetime

# Import our client
from src.agents.persistent_agent_client import (
    PersistentAgentClient,
    TradingTask,
    TaskPriority,
    quick_analysis,
    full_execution_workflow,
    risk_assessment
)

async def demo_basic_usage():
    """Demo basic agent usage"""
    print("\n" + "="*80)
    print("🚀 DEMO 1: Basic Agent Usage")
    print("="*80)

    async with PersistentAgentClient() as client:
        # Check agent status
        print("📊 Checking agent status...")
        status = await client.get_agent_status()

        if "error" in status:
            print("❌ Agents are not running! Please start them first:")
            print("   python start_persistent_agents.py")
            return

        print(f"✅ {status['orchestrator']['total_agents']} agents running")
        print(f"📈 Total tasks processed: {status['orchestrator']['metrics']['total_tasks']}")

        # Submit individual tasks
        print("\n🎯 Submitting individual tasks...")

        # Strategy task
        strategy_task = TradingTask(
            task_id="demo_strategy_001",
            agent_type="strategy",
            priority=TaskPriority.HIGH,
            payload={
                "task": "Analyze BTC trading opportunity",
                "asset": "BTC",
                "analysis_type": "quick_signal",
                "timeframe": "1h"
            },
            timeout=60
        )

        strategy_id = await client.submit_task(strategy_task)
        print(f"✅ Strategy task submitted: {strategy_id}")

        # Risk task
        risk_task = TradingTask(
            task_id="demo_risk_001",
            agent_type="risk",
            priority=TaskPriority.NORMAL,
            payload={
                "task": "Assess portfolio risk",
                "assets": ["BTC", "ETH", "SOL"],
                "risk_tolerance": "MODERATE"
            },
            timeout=45
        )

        risk_id = await client.submit_task(risk_task)
        print(f"✅ Risk task submitted: {risk_id}")

        # Wait for results
        print("\n⏳ Waiting for task results...")

        strategy_result = await client.get_task_result(strategy_id, timeout=90)
        risk_result = await client.get_task_result(risk_id, timeout=90)

        print(f"\n📋 Strategy Result: {'✅ Success' if strategy_result and strategy_result.get('success') else '❌ Failed'}")
        print(f"📋 Risk Result: {'✅ Success' if risk_result and risk_result.get('success') else '❌ Failed'}")

async def demo_trading_workflow():
    """Demo complete trading workflow"""
    print("\n" + "="*80)
    print("🔄 DEMO 2: Complete Trading Workflow")
    print("="*80)

    # Test different workflows
    symbols = ["BTC", "ETH", "SOL"]

    for symbol in symbols:
        print(f"\n💼 Running analysis workflow for {symbol}...")
        start_time = time.time()

        try:
            result = await quick_analysis(symbol)
            execution_time = time.time() - start_time

            if result.get("workflow", {}).get("success"):
                print(f"✅ {symbol} analysis completed in {execution_time:.1f}s")

                # Extract key insights
                strategy = result.get("strategy", {}).get("response", {})
                risk = result.get("risk", {}).get("response", {})
                liquidity = result.get("liquidity", {}).get("response", {})

                print(f"   📊 Strategy Signal: {strategy.get('signal', 'N/A')}")
                print(f"   🛡️ Risk Level: {risk.get('risk_level', 'N/A')}")
                print(f"   💧 Liquidity Score: {liquidity.get('liquidity_score', 'N/A')}")
            else:
                print(f"❌ {symbol} analysis failed")

        except Exception as e:
            print(f"❌ {symbol} analysis error: {e}")

async def demo_parallel_processing():
    """Demo parallel task processing"""
    print("\n" + "="*80)
    print("⚡ DEMO 3: Parallel Task Processing")
    print("="*80)

    async with PersistentAgentClient() as client:
        print("🚀 Submitting parallel tasks to different agents...")

        tasks = []
        start_time = time.time()

        # Submit multiple tasks simultaneously
        symbols = ["BTC", "ETH", "SOL", "AVAX", "MATIC"]

        for symbol in symbols:
            # Strategy analysis
            task = TradingTask(
                task_id=f"parallel_strategy_{symbol}_{int(time.time())}",
                agent_type="strategy",
                priority=TaskPriority.NORMAL,
                payload={
                    "task": f"Quick analysis of {symbol}",
                    "asset": symbol,
                    "analysis_type": "signal"
                },
                timeout=30
            )
            task_id = await client.submit_task(task)
            tasks.append((task_id, symbol, "strategy"))

        print(f"✅ Submitted {len(tasks)} parallel tasks")

        # Wait for all results
        results = []
        for task_id, symbol, agent_type in tasks:
            result = await client.get_task_result(task_id, timeout=60)
            if result and result.get("success"):
                results.append((symbol, "success"))
                print(f"✅ {symbol} ({agent_type}) completed")
            else:
                results.append((symbol, "failed"))
                print(f"❌ {symbol} ({agent_type}) failed")

        total_time = time.time() - start_time
        successful = sum(1 for _, status in results if status == "success")

        print(f"\n📊 Parallel Processing Results:")
        print(f"   ⏱️ Total time: {total_time:.1f}s")
        print(f"   ✅ Successful: {successful}/{len(tasks)}")
        print(f"   ⚡ Avg time per task: {total_time/len(tasks):.1f}s")

async def demo_real_time_monitoring():
    """Demo real-time agent monitoring"""
    print("\n" + "="*80)
    print("👁️ DEMO 4: Real-time Agent Monitoring")
    print("="*80)

    async with PersistentAgentClient() as client:
        print("🔍 Starting 30-second real-time monitoring...")

        # Submit some background tasks
        print("🎯 Submitting background tasks...")

        for i in range(3):
            task = TradingTask(
                task_id=f"monitoring_task_{i}_{int(time.time())}",
                agent_type="liquidity",
                priority=TaskPriority.LOW,
                payload={
                    "task": f"Background liquidity check {i+1}",
                    "asset": "BTC"
                },
                timeout=60
            )
            await client.submit_task(task)

        # Monitor for 30 seconds
        await client.monitor_agents(30)

async def demo_error_handling():
    """Demo error handling and recovery"""
    print("\n" + "="*80)
    print("🔧 DEMO 5: Error Handling & Recovery")
    print("="*80)

    async with PersistentAgentClient() as client:
        print("🧪 Testing error scenarios...")

        # Test 1: Invalid agent type
        try:
            invalid_task = TradingTask(
                task_id="invalid_agent_test",
                agent_type="invalid_agent",
                priority=TaskPriority.NORMAL,
                payload={"task": "test"},
                timeout=10
            )
            await client.submit_task(invalid_task)
        except Exception as e:
            print(f"✅ Caught invalid agent error: {str(e)[:50]}...")

        # Test 2: Task timeout
        try:
            timeout_task = TradingTask(
                task_id="timeout_test",
                agent_type="strategy",
                priority=TaskPriority.LOW,
                payload={
                    "task": "Very long analysis",
                    "delay_analysis": True
                },
                timeout=5  # Very short timeout
            )
            task_id = await client.submit_task(timeout_task)

            # This should timeout
            result = await client.get_task_result(task_id, timeout=10)
            if result is None:
                print("✅ Task timeout handled correctly")

        except Exception as e:
            print(f"⚠️ Timeout handling: {str(e)[:50]}...")

async def demo_performance_metrics():
    """Demo performance metrics collection"""
    print("\n" + "="*80)
    print("📈 DEMO 6: Performance Metrics")
    print("="*80)

    async with PersistentAgentClient() as client:
        print("📊 Collecting performance metrics...")

        # Submit various tasks with different priorities
        tasks_submitted = 0
        start_time = time.time()

        for priority in [TaskPriority.CRITICAL, TaskPriority.HIGH, TaskPriority.NORMAL, TaskPriority.LOW]:
            for i in range(2):
                task = TradingTask(
                    task_id=f"perf_test_{priority.name.lower()}_{i}",
                    agent_type="strategy",
                    priority=priority,
                    payload={
                        "task": f"Performance test {priority.name.lower()} {i+1}",
                        "test_type": "performance"
                    },
                    timeout=30
                )
                await client.submit_task(task)
                tasks_submitted += 1

        # Wait for all tasks
        completed_tasks = 0
        for i in range(tasks_submitted):
            result = await client.get_task_result(f"perf_test_{i}", timeout=60)
            if result and result.get("success"):
                completed_tasks += 1

        total_time = time.time() - start_time

        # Get final status
        final_status = await client.get_agent_status()
        metrics = final_status["orchestrator"]["metrics"]

        print(f"\n📊 Performance Summary:")
        print(f"   🎯 Tasks Submitted: {tasks_submitted}")
        print(f"   ✅ Tasks Completed: {completed_tasks}")
        print(f"   ⏱️ Total Time: {total_time:.1f}s")
        print(f"   📈 Throughput: {completed_tasks/total_time:.2f} tasks/sec")
        print(f"   🎯 Success Rate: {metrics['successful_tasks']/metrics['total_tasks']*100:.1f}%" if metrics['total_tasks'] > 0 else "N/A")

async def main():
    """Run all demos"""
    print("\n" + "="*80)
    print("🤖 PERSISTENT CLAUDE CODE CLI AGENTS - COMPLETE DEMO")
    print("="*80)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting demonstration...")

    try:
        # Run all demos
        await demo_basic_usage()
        await asyncio.sleep(2)

        await demo_trading_workflow()
        await asyncio.sleep(2)

        await demo_parallel_processing()
        await asyncio.sleep(2)

        await demo_real_time_monitoring()
        await asyncio.sleep(2)

        await demo_error_handling()
        await asyncio.sleep(2)

        await demo_performance_metrics()

        print("\n" + "="*80)
        print("🎉 ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*80)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Demo finished")
        print("\n💡 Next steps:")
        print("   1. Start agents: python start_persistent_agents.py")
        print("   2. Run workflows: python demo_persistent_agents.py")
        print("   3. Monitor performance: Check http://localhost:7999/status")
        print("   4. Use client: Import PersistentAgentClient in your code")

    except KeyboardInterrupt:
        print("\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n💥 Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())