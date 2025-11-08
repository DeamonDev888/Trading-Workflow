"""
[OK] Persistent Agent Client
Client for interacting with persistent Claude Code CLI agents
Built with love by Deamon Dev [ROCKET]

Provides simple interface for:
- Submitting tasks to agents
- Getting results
- Monitoring agent status
"""

import asyncio
import json
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

import aiohttp


class TaskPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


@dataclass
class TradingTask:
    """Trading task definition"""

    task_id: str
    agent_type: str  # strategy, risk, liquidity, execution
    priority: TaskPriority
    payload: Dict[str, Any]
    timeout: int = 120
    callback_url: Optional[str] = None


class PersistentAgentClient:
    """Client for interacting with persistent agents"""

    def __init__(self, orchestrator_url: str = "http://localhost:7999"):
        self.orchestrator_url = orchestrator_url
        self.session = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def submit_task(self, task: TradingTask) -> str:
        """Submit a task to an agent"""
        try:
            payload = {
                "agent_type": task.agent_type,
                "payload": task.payload,
                "priority": task.priority.value,
                "timeout": task.timeout,
            }

            if task.callback_url:
                payload["callback_url"] = task.callback_url

            async with self.session.post(
                f"{self.orchestrator_url}/submit_task", json=payload, timeout=10
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"[TASK] Submitted {task.task_id} to {task.agent_type} agent")
                    return result["task_id"]
                else:
                    error_text = await response.text()
                    raise Exception(
                        f"Task submission failed: {response.status} - {error_text}"
                    )

        except Exception as e:
            print(f"[ERROR] Failed to submit task {task.task_id}: {e}")
            raise

    async def get_task_result(
        self, task_id: str, timeout: int = 300
    ) -> Optional[Dict[str, Any]]:
        """Get task result with timeout"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                async with self.session.get(
                    f"{self.orchestrator_url}/task_result/{task_id}", timeout=5
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get("status") != "pending":
                            print(
                                f"[TASK] {task_id} completed: {result.get('success', False)}"
                            )
                            return result
                    else:
                        print(f"[WARNING] Failed to get task result: {response.status}")

                await asyncio.sleep(2)

            except Exception as e:
                print(f"[ERROR] Error checking task result: {e}")
                await asyncio.sleep(5)

        print(f"[TIMEOUT] Task {task_id} did not complete within {timeout}s")
        return None

    async def get_agent_status(self) -> Dict[str, Any]:
        """Get overall agent status"""
        try:
            async with self.session.get(
                f"{self.orchestrator_url}/status", timeout=10
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Status request failed: {response.status}")

        except Exception as e:
            print(f"[ERROR] Failed to get agent status: {e}")
            return {"error": str(e)}

    async def execute_trading_workflow(
        self, symbol: str, trade_type: str = "analysis"
    ) -> Dict[str, Any]:
        """
        Execute a complete trading workflow using all agents

        Args:
            symbol: Trading symbol (e.g., "BTC")
            trade_type: Type of analysis ("analysis", "execution", "risk_assessment")

        Returns:
            Complete workflow results
        """
        print(f"[WORKFLOW] Starting {trade_type} workflow for {symbol}")
        workflow_start = time.time()

        try:
            results = {}

            if trade_type in ["analysis", "execution"]:
                # Step 1: Strategy Analysis
                print(f"[STEP 1/4] Strategy analysis for {symbol}...")
                strategy_task = TradingTask(
                    task_id=f"strategy_{symbol}_{int(time.time())}",
                    agent_type="strategy",
                    priority=TaskPriority.HIGH,
                    payload={
                        "task": f"Analyze trading opportunity for {symbol}",
                        "asset": symbol,
                        "market_data": await self._get_market_data(symbol),
                        "analysis_type": trade_type,
                    },
                    timeout=60,
                )

                strategy_task_id = await self.submit_task(strategy_task)
                strategy_result = await self.get_task_result(
                    strategy_task_id, timeout=120
                )
                results["strategy"] = strategy_result

                if strategy_result and strategy_result.get("success"):
                    # Step 2: Risk Assessment
                    print(f"[STEP 2/4] Risk assessment for {symbol}...")
                    risk_task = TradingTask(
                        task_id=f"risk_{symbol}_{int(time.time())}",
                        agent_type="risk",
                        priority=TaskPriority.HIGH,
                        payload={
                            "task": f"Assess risk for {symbol} trade",
                            "signal": strategy_result.get("response", {}),
                            "asset": symbol,
                            "risk_tolerance": "CONSERVATIVE",
                        },
                        timeout=45,
                    )

                    risk_task_id = await self.submit_task(risk_task)
                    risk_result = await self.get_task_result(risk_task_id, timeout=90)
                    results["risk"] = risk_result

                    # Step 3: Liquidity Analysis
                    print(f"[STEP 3/4] Liquidity analysis for {symbol}...")
                    liquidity_task = TradingTask(
                        task_id=f"liquidity_{symbol}_{int(time.time())}",
                        agent_type="liquidity",
                        priority=TaskPriority.HIGH,
                        payload={
                            "task": f"Analyze liquidity for {symbol}",
                            "asset": symbol,
                            "position_size": strategy_result.get("response", {}).get(
                                "recommended_size", 1.0
                            ),
                            "order_type": "market",
                        },
                        timeout=30,
                    )

                    liquidity_task_id = await self.submit_task(liquidity_task)
                    liquidity_result = await self.get_task_result(
                        liquidity_task_id, timeout=60
                    )
                    results["liquidity"] = liquidity_result

                    if trade_type == "execution":
                        # Step 4: Trade Execution
                        print(f"[STEP 4/4] Trade execution for {symbol}...")
                        execution_task = TradingTask(
                            task_id=f"execution_{symbol}_{int(time.time())}",
                            agent_type="execution",
                            priority=TaskPriority.CRITICAL,
                            payload={
                                "task": f"Execute {symbol} trade",
                                "signal": strategy_result.get("response", {}),
                                "risk_analysis": (
                                    risk_result.get("response", {})
                                    if risk_result
                                    else {}
                                ),
                                "liquidity_analysis": (
                                    liquidity_result.get("response", {})
                                    if liquidity_result
                                    else {}
                                ),
                                "execution_mode": "SAFE",
                            },
                            timeout=90,
                        )

                        execution_task_id = await self.submit_task(execution_task)
                        execution_result = await self.get_task_result(
                            execution_task_id, timeout=180
                        )
                        results["execution"] = execution_result

            elif trade_type == "risk_assessment":
                # Risk-only workflow
                print(f"[STEP 1/2] Getting current {symbol} data...")
                market_data = await self._get_market_data(symbol)

                print(f"[STEP 2/2] Risk assessment for {symbol}...")
                risk_task = TradingTask(
                    task_id=f"risk_only_{symbol}_{int(time.time())}",
                    agent_type="risk",
                    priority=TaskPriority.NORMAL,
                    payload={
                        "task": f"Comprehensive risk assessment for {symbol}",
                        "asset": symbol,
                        "market_data": market_data,
                        "position_size": 1.0,
                        "assessment_type": "portfolio_risk",
                    },
                    timeout=60,
                )

                risk_task_id = await self.submit_task(risk_task)
                risk_result = await self.get_task_result(risk_task_id, timeout=120)
                results["risk_assessment"] = risk_result

            # Calculate workflow metrics
            workflow_time = time.time() - workflow_start
            results["workflow"] = {
                "symbol": symbol,
                "trade_type": trade_type,
                "execution_time": workflow_time,
                "success": all(
                    result.get("success", False)
                    for result in results.values()
                    if isinstance(result, dict) and "success" in result
                ),
                "timestamp": datetime.now().isoformat(),
            }

            print(
                f"[WORKFLOW] {trade_type} workflow for {symbol} completed in {workflow_time:.1f}s"
            )
            return results

        except Exception as e:
            print(f"[ERROR] Workflow failed for {symbol}: {e}")
            return {
                "error": str(e),
                "workflow": {
                    "symbol": symbol,
                    "trade_type": trade_type,
                    "success": False,
                    "timestamp": datetime.now().isoformat(),
                },
            }

    async def _get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get market data for a symbol (mock implementation)"""
        try:
            # In production, this would fetch real market data
            return {
                "symbol": symbol,
                "price": 45000 if symbol == "BTC" else 3000 if symbol == "ETH" else 100,
                "volume": 1000000,
                "trend": "bullish",
                "volatility": "medium",
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            print(f"[ERROR] Failed to get market data for {symbol}: {e}")
            return {"symbol": symbol, "error": str(e)}

    async def monitor_agents(self, duration: int = 60) -> None:
        """Monitor agents for a specified duration"""
        print(f"[MONITOR] Starting agent monitoring for {duration}s...")

        start_time = time.time()
        while time.time() - start_time < duration:
            try:
                status = await self.get_agent_status()

                if "error" not in status:
                    total_tasks = status["orchestrator"]["total_tasks"]
                    successful = status["orchestrator"]["metrics"]["successful_tasks"]
                    failed = status["orchestrator"]["metrics"]["failed_tasks"]

                    print(
                        f"[{datetime.now().strftime('%H:%M:%S')}] "
                        f"Agents: {status['orchestrator']['total_agents']} | "
                        f"Tasks: {total_tasks} (✓{successful} ✗{failed}) | "
                        f"Queue: {status['orchestrator']['queued_tasks']}"
                    )

                await asyncio.sleep(10)

            except Exception as e:
                print(f"[ERROR] Monitoring error: {e}")
                await asyncio.sleep(10)

        print(f"[MONITOR] Monitoring completed")

    async def restart_agent(self, agent_type: str) -> bool:
        """Restart a specific agent"""
        try:
            # Find agent ID by type
            status = await self.get_agent_status()
            agent_id = None

            for aid, agent_info in status.get("agents", {}).items():
                if agent_info["type"] == agent_type:
                    agent_id = aid
                    break

            if not agent_id:
                print(f"[ERROR] Agent {agent_type} not found")
                return False

            async with self.session.post(
                f"{self.orchestrator_url}/restart_agent/{agent_id}", timeout=10
            ) as response:
                if response.status == 200:
                    print(f"[RESTART] Agent {agent_type} restart initiated")
                    return True
                else:
                    print(
                        f"[ERROR] Failed to restart agent {agent_type}: {response.status}"
                    )
                    return False

        except Exception as e:
            print(f"[ERROR] Agent restart failed: {e}")
            return False


# Convenience functions for common workflows
async def quick_analysis(symbol: str) -> Dict[str, Any]:
    """Quick trading analysis for a symbol"""
    async with PersistentAgentClient() as client:
        return await client.execute_trading_workflow(symbol, "analysis")


async def full_execution_workflow(symbol: str) -> Dict[str, Any]:
    """Complete trading execution workflow"""
    async with PersistentAgentClient() as client:
        return await client.execute_trading_workflow(symbol, "execution")


async def risk_assessment(symbol: str) -> Dict[str, Any]:
    """Risk assessment for a symbol"""
    async with PersistentAgentClient() as client:
        return await client.execute_trading_workflow(symbol, "risk_assessment")


if __name__ == "__main__":
    # Example usage
    async def main():
        async with PersistentAgentClient() as client:
            # Check agent status
            print("🔍 Checking agent status...")
            status = await client.get_agent_status()
            print(json.dumps(status, indent=2))

            # Run quick analysis
            print("\n📊 Running BTC analysis...")
            result = await client.execute_trading_workflow("BTC", "analysis")
            print(f"Analysis result: {json.dumps(result, indent=2)}")

            # Monitor agents for 30 seconds
            print("\n👀 Monitoring agents for 30s...")
            await client.monitor_agents(30)

    asyncio.run(main())
