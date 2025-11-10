"""
[OK] Persistent Agents Launcher
Starts 4 Claude Code CLI agents with orchestration
Built with love by Deamon Dev [ROCKET]

Usage: python start_persistent_agents.py
"""

import asyncio
import sys
import os
import signal
import requests
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.agents.persistent_agent_orchestrator import PersistentAgentOrchestrator
import json

class PersistentAgentsLauncher:
    """Launcher for persistent Claude Code CLI agents"""

    def __init__(self):
        self.orchestrator = None
        self.running = False

    async def start(self):
        """Start all persistent agents"""
        print("\n" + "="*80)
        print("[PERSISTENT CLAUDE CODE CLI AGENTS LAUNCHER]")
        print("="*80)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Initializing agent orchestrator...")

        try:
            self.orchestrator = PersistentAgentOrchestrator(base_port=8000)

            await self.orchestrator.start_all_agents()

            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] [SUCCESS] All agents started successfully!")
            self.running = True

            await self.display_agent_status()

            signal.signal(signal.SIGINT, self.signal_handler)
            signal.signal(signal.SIGTERM, self.signal_handler)

            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] [RUNNING] Agents are running...")
            print(f"[INFO] Agent API endpoints:")
            print(f"  • Strategy Agent: http://localhost:8000")
            print(f"  • Risk Agent: http://localhost:8001")
            print(f"  • Liquidity Agent: http://localhost:8002")
            print(f"  • Execution Agent: http://localhost:8003")
            print(f"  • Orchestrator API: http://localhost:7999")
            print(f"\n[INFO] Press Ctrl+C to stop all agents")

            while self.running:
                await asyncio.sleep(10)
                await self.health_check()

        except Exception as e:
            print(f"[ERROR] Failed to start agents: {e}")
            await self.stop()

    async def display_agent_status(self):
        """Display current agent status"""
        status = self.orchestrator.get_status()

        print(f"\n📊 AGENT STATUS:")
        print(f"  • Total Agents: {status['orchestrator']['total_agents']}")
        print(f"  • Active Tasks: {status['orchestrator']['active_tasks']}")
        print(f"  • Queued Tasks: {status['orchestrator']['queued_tasks']}")
        print(f"  • Completed Tasks: {status['orchestrator']['completed_tasks']}")

        print(f"\n🤖 AGENT DETAILS:")
        for agent_id, agent_info in status['agents'].items():
            status_icon = "🟢" if agent_info['status'] == 'running' else "🔴" if agent_info['status'] == 'error' else "🟡"
            print(f"  {status_icon} {agent_info['type'].title()} Agent:")
            print(f"     - ID: {agent_id[:12]}...")
            print(f"     - Status: {agent_info['status']}")
            print(f"     - Port: {agent_info['port']}")
            print(f"     - Tasks: {agent_info['request_count']} completed, {agent_info['error_count']} errors")
            print(f"     - Memory: {agent_info['performance']['memory_usage']:.1f}MB")

    async def health_check(self):
        """Periodic health check"""
        try:
            response = requests.get("http://localhost:7999/status", timeout=5)
            if response.status_code != 200:
                print(f"[WARNING] Orchestrator API not responding")
                return

            status = response.json()
            error_agents = []

            for agent_id, agent_info in status['agents'].items():
                if agent_info['status'] == 'error':
                    error_agents.append(agent_info['type'])
                elif agent_info['error_count'] > 5:
                    error_agents.append(f"{agent_info['type']} (high errors)")

            if error_agents:
                print(f"[WARNING] Agents with issues: {', '.join(error_agents)}")

        except Exception as e:
            print(f"[WARNING] Health check failed: {e}")

    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🛑 Shutdown signal received...")
        self.running = False

    async def stop(self):
        """Stop all agents"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Stopping all agents...")
        if self.orchestrator:
            await self.orchestrator.stop_all_agents()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ All agents stopped")

async def test_agents():
    """Test the agents after startup"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🧪 Testing agents...")

    try:
        response = requests.post("http://localhost:8000/process", json={
            "task_id": "test_001",
            "payload": {
                "task": "Analyze BTC trading opportunity",
                "asset": "BTC",
                "market_data": {"price": 45000, "trend": "bullish"}
            }
        }, timeout=30)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Strategy Agent test: {result.get('success', False)}")
        else:
            print(f"❌ Strategy Agent test failed: {response.status_code}")

    except Exception as e:
        print(f"❌ Agent test failed: {e}")

if __name__ == "__main__":
    launcher = PersistentAgentsLauncher()

    try:
        asyncio.run(launcher.start())

    except KeyboardInterrupt:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] [INTERRUPTED] by user")
    except Exception as e:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] [ERROR] Fatal error: {e}")
    finally:
        if launcher.running:
            asyncio.run(launcher.stop())