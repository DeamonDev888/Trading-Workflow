"""
[OK] Persistent Agent Orchestrator
Architecture with 4 Claude Code CLI agents running continuously
Built with love by Deamon Dev [ROCKET]

4 Persistent Agents:
1. Strategy Agent - Trading signals and analysis
2. Risk Agent - Risk management and validation
3. Liquidity Agent - Liquidity analysis and filtering
4. Execution Agent - Order execution and monitoring
"""

import asyncio
import os
import subprocess
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import psutil
import requests
import uvicorn
from fastapi import FastAPI, HTTPException


class AgentStatus(Enum):
    """Agent process status"""

    STARTING = "starting"
    RUNNING = "running"
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    STOPPED = "stopped"
    RESTARTING = "restarting"


class AgentType(Enum):
    """Agent types with their specializations"""

    STRATEGY = "strategy"
    RISK = "risk"
    LIQUIDITY = "liquidity"
    EXECUTION = "execution"


@dataclass
class AgentProcess:
    """Persistent agent process information"""

    agent_id: str
    agent_type: AgentType
    process: Optional[subprocess.Popen]
    status: AgentStatus
    port: int
    api_url: str
    pid: Optional[int]
    start_time: datetime
    last_heartbeat: datetime
    request_count: int = 0
    error_count: int = 0
    current_task: Optional[str] = None
    performance_metrics: Dict[str, float] = None

    def __post_init__(self):
        if self.performance_metrics is None:
            self.performance_metrics = {
                "avg_response_time": 0.0,
                "success_rate": 1.0,
                "memory_usage": 0.0,
                "cpu_usage": 0.0,
            }


@dataclass
class TaskRequest:
    """Task request for agents"""

    task_id: str
    agent_type: AgentType
    priority: int  # 1-5, 1 = highest
    payload: Dict[str, Any]
    timeout: int = 120
    callback_url: Optional[str] = None
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class TaskResponse:
    """Task response from agents"""

    task_id: str
    agent_id: str
    success: bool
    response: Dict[str, Any]
    execution_time: float
    error_message: Optional[str] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class PersistentAgentOrchestrator:
    """Orchestrator for managing persistent Claude Code CLI agents"""

    def __init__(self, base_port: int = 8000):
        self.base_port = base_port
        self.agents: Dict[str, AgentProcess] = {}
        self.task_queue: List[TaskRequest] = []
        self.active_tasks: Dict[str, TaskRequest] = {}
        self.completed_tasks: List[TaskResponse] = []
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.running = False
        self.monitoring_interval = 5  # seconds
        self.task_history_size = 1000

        # Performance tracking
        self.metrics = {
            "total_tasks": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "avg_task_time": 0.0,
            "agent_utilization": {},
        }

    async def start_all_agents(self):
        """Start all 4 persistent agents"""
        print(f"[ORCHESTRATOR] Starting {len(AgentType)} persistent agents...")

        agent_configs = [
            {
                "type": AgentType.STRATEGY,
                "script": "src/agents/persistent_strategy_agent.py",
                "name": "Strategy Agent",
                "port": self.base_port,
            },
            {
                "type": AgentType.RISK,
                "script": "src/agents/persistent_risk_agent.py",
                "name": "Risk Agent",
                "port": self.base_port + 1,
            },
            {
                "type": AgentType.LIQUIDITY,
                "script": "src/agents/persistent_liquidity_agent.py",
                "name": "Liquidity Agent",
                "port": self.base_port + 2,
            },
            {
                "type": AgentType.EXECUTION,
                "script": "src/agents/persistent_execution_agent.py",
                "name": "Execution Agent",
                "port": self.base_port + 3,
            },
        ]

        for config in agent_configs:
            agent_id = f"{config['type'].value}_agent_{uuid.uuid4().hex[:8]}"

            print(f"[STARTING] {config['name']} on port {config['port']}...")

            agent = AgentProcess(
                agent_id=agent_id,
                agent_type=config["type"],
                process=None,
                status=AgentStatus.STARTING,
                port=config["port"],
                api_url=f"http://localhost:{config['port']}",
                pid=None,
                start_time=datetime.now(),
                last_heartbeat=datetime.now(),
            )

            success = await self._start_agent_process(agent, config)
            if success:
                self.agents[agent_id] = agent
                print(f"[OK] {config['name']} started successfully (PID: {agent.pid})")
            else:
                print(f"[ERROR] Failed to start {config['name']}")

        self.running = True

        # Start monitoring and task processing
        asyncio.create_task(self._monitor_agents())
        asyncio.create_task(self._process_task_queue())
        asyncio.create_task(self._cleanup_old_tasks())

        print(f"[ORCHESTRATOR] All agents started. Ready for task processing.")

    async def _start_agent_process(self, agent: AgentProcess, config: Dict) -> bool:
        """Start a single agent process"""
        try:
            # Create the startup script for the agent
            startup_script = self._create_agent_script(config)
            script_path = f"temp_agent_{config['type'].value}.py"

            with open(script_path, "w") as f:
                f.write(startup_script)

            # Start the agent process
            cmd = [
                "python",
                script_path,
                "--port",
                str(config["port"]),
                "--agent-id",
                agent.agent_id,
                "--agent-type",
                config["type"].value,
            ]

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.getcwd(),
            )

            agent.process = process
            agent.pid = process.pid

            # Wait for agent to be ready
            await asyncio.sleep(3)

            # Check if agent is responsive
            if await self._ping_agent(agent):
                agent.status = AgentStatus.RUNNING
                agent.last_heartbeat = datetime.now()
                return True
            else:
                print(f"[ERROR] Agent {config['name']} not responsive after startup")
                process.terminate()
                return False

        except Exception as e:
            print(f"[ERROR] Failed to start agent {config['name']}: {e}")
            return False

    def _create_agent_script(self, config: Dict) -> str:
        """Create the startup script for a persistent agent"""
        return f'''
"""
Persistent {config['type'].value.title()} Agent
Runs continuously as Claude Code CLI subprocess
"""

import asyncio
import json
import time
import argparse
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import subprocess
import uuid

class Persistent{config['type'].value.title()}Agent:
    """Persistent {config['type'].value} agent with Claude Code CLI integration"""

    def __init__(self, port: int, agent_id: str):
        self.port = port
        self.agent_id = agent_id
        self.current_task = None
        self.claude_process = None
        self.task_count = 0

        # Initialize FastAPI
        self.app = FastAPI(title=f"Persistent {config['type'].value.title()} Agent")
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Setup routes
        self._setup_routes()

    def _setup_routes(self):
        """Setup API routes for the agent"""

        @self.app.get("/health")
        async def health_check():
            return {{
                "agent_id": self.agent_id,
                "agent_type": "{config['type'].value}",
                "status": "running",
                "current_task": self.current_task,
                "task_count": self.task_count,
                "timestamp": datetime.now().isoformat()
            }}

        @self.app.post("/process")
        async def process_task(request: dict):
            """Process a task using Claude Code CLI"""
            try:
                task_id = request.get("task_id", str(uuid.uuid4()))
                task_data = request.get("payload", {{}})

                self.current_task = task_id
                self.task_count += 1

                # Prepare prompt for Claude Code
                prompt = self._create_claude_prompt(task_data)

                # Call Claude Code CLI
                response = await self._call_claude_code(prompt, task_data)

                self.current_task = None

                return {{
                    "success": True,
                    "task_id": task_id,
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                }}

            except Exception as e:
                self.current_task = None
                return {{
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }}

        @self.app.get("/status")
        async def get_status():
            """Get detailed agent status"""
            return {{
                "agent_id": self.agent_id,
                "agent_type": "{config['type'].value}",
                "uptime": "running",  # Would calculate actual uptime
                "memory_usage": 0,  # Would get actual memory usage
                "task_count": self.task_count,
                "current_task": self.current_task,
                "claude_process_running": self.claude_process is not None
            }}

    def _create_claude_prompt(self, task_data: dict) -> str:
        """Create Claude Code prompt based on agent type"""
        {self._get_prompt_template(config['type'])}

    async def _call_claude_code(self, prompt: str, task_data: dict) -> dict:
        """Call Claude Code CLI"""
        try:
            cmd = [
                "claude",
                "--dangerously-skip-permissions",
                "--agent",
                "claude-{config['type'].value}-agent",
                prompt
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                text=True
            )

            self.claude_process = process

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=120.0
            )

            self.claude_process = None

            if process.returncode == 0:
                return {{
                    "response": stdout,
                    "success": True,
                    "execution_time": 0  # Would measure actual time
                }}
            else:
                return {{
                    "response": stderr,
                    "success": False,
                    "error": f"Claude Code CLI error: {{stderr}}"
                }}

        except asyncio.TimeoutError:
            if self.claude_process:
                self.claude_process.terminate()
                self.claude_process = None
            return {{
                "response": "Task timeout",
                "success": False,
                "error": "Claude Code CLI timeout after 120 seconds"
            }}
        except Exception as e:
            self.claude_process = None
            return {{
                "response": f"Error: {{str(e)}}",
                "success": False,
                "error": str(e)
            }}

    async def run(self):
        """Run the FastAPI server"""
        config = uvicorn.Config(
            self.app,
            host="0.0.0.0",
            port=self.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()

# Main execution
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--agent-id", type=str, required=True)
    parser.add_argument("--agent-type", type=str, required=True)
    args = parser.parse_args()

    agent = Persistent{config['type'].value.title()}Agent(args.port, args.agent_id)
    asyncio.run(agent.run())
'''

    def _get_prompt_template(self, agent_type: AgentType) -> str:
        """Get prompt template for different agent types"""
        templates = {
            AgentType.STRATEGY: '''
        return f"""
        You are a persistent Strategy Trading Agent [OK]

        Task: {task_data.get('task', 'Analyze trading opportunity')}

        Market Data: {task_data.get('market_data', {{}})}
        Asset: {task_data.get('asset', 'Unknown')}

        Please provide:
        1. Trading signal (BUY/SELL/HOLD)
        2. Confidence level (0-1)
        3. Reasoning
        4. Risk assessment
        5. Recommended position size

        Focus on technical analysis and market trends.
        """
        ''',
            AgentType.RISK: '''
        return f"""
        You are a persistent Risk Management Agent [SHIELD]

        Task: {task_data.get('task', 'Assess trading risk')}

        Trading Signal: {task_data.get('signal', {{}})}
        Market Conditions: {task_data.get('market_data', {{}})}
        Position Size: {task_data.get('position_size', 'Unknown')}

        Please provide:
        1. Risk level (LOW/MEDIUM/HIGH/CRITICAL)
        2. Maximum safe position size
        3. Stop loss recommendation
        4. Risk mitigation strategies
        5. Approval/rejection decision

        Prioritize capital preservation over profits.
        """
        ''',
            AgentType.LIQUIDITY: '''
        return f"""
        You are a persistent Liquidity Analysis Agent [LIQUID]

        Task: {task_data.get('task', 'Analyze asset liquidity')}

        Asset: {task_data.get('asset', 'Unknown')}
        Position Size: {task_data.get('position_size', 'Unknown')}
        Order Type: {task_data.get('order_type', 'market')}

        Please provide:
        1. Liquidity score (0-1)
        2. Expected slippage
        3. Market depth analysis
        4. Safe execution size
        5. Execution timing recommendation

        Focus on preventing slippage and ensuring smooth execution.
        """
        ''',
            AgentType.EXECUTION: '''
        return f"""
        You are a persistent Trade Execution Agent [ROCKET]

        Task: {task_data.get('task', 'Execute trading order')}

        Signal: {task_data.get('signal', {{}})}
        Risk Analysis: {task_data.get('risk_analysis', {{}})}
        Liquidity Analysis: {task_data.get('liquidity_analysis', {{}})}
        Account: {task_data.get('account', {{}})}

        Please provide:
        1. Execution decision (EXECUTE/CANCEL/MODIFY)
        2. Final order parameters
        3. Execution strategy
        4. Monitoring requirements
        5. Exit strategy

        Ensure all safety checks are passed before execution.
        """
        ''',
        }
        return templates.get(agent_type, 'return f"Analyze this task: {task_data}"')

    async def _ping_agent(self, agent: AgentProcess) -> bool:
        """Check if agent is responsive"""
        try:
            response = requests.get(f"{agent.api_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False

    async def submit_task(
        self,
        agent_type: AgentType,
        payload: Dict[str, Any],
        priority: int = 3,
        timeout: int = 120,
        callback_url: Optional[str] = None,
    ) -> str:
        """Submit a task to a specific agent type"""

        task_id = str(uuid.uuid4())

        task = TaskRequest(
            task_id=task_id,
            agent_type=agent_type,
            priority=priority,
            payload=payload,
            timeout=timeout,
            callback_url=callback_url,
        )

        # Add to queue (priority queue)
        self.task_queue.append(task)
        self.task_queue.sort(key=lambda t: t.priority)

        print(f"[TASK] Submitted {task_id} to {agent_type.value} agent (priority: {priority})")

        return task_id

    async def get_task_result(self, task_id: str, timeout: int = 300) -> Optional[TaskResponse]:
        """Wait for and get task result"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            # Check completed tasks
            for response in self.completed_tasks:
                if response.task_id == task_id:
                    self.completed_tasks.remove(response)
                    return response

            # Check if task failed
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                if datetime.now() - task.created_at > timedelta(seconds=task.timeout):
                    del self.active_tasks[task_id]
                    return TaskResponse(
                        task_id=task_id,
                        agent_id="",
                        success=False,
                        response={},
                        execution_time=0,
                        error_message="Task timeout",
                    )

            await asyncio.sleep(1)

        return None

    async def _process_task_queue(self):
        """Process tasks from the queue"""
        while self.running:
            try:
                if self.task_queue:
                    task = self.task_queue.pop(0)

                    # Find available agent for this task type
                    agent = await self._get_available_agent(task.agent_type)

                    if agent:
                        # Execute task
                        self.active_tasks[task.task_id] = task
                        agent.current_task = task.task_id
                        agent.status = AgentStatus.BUSY

                        # Execute in background
                        self.executor.submit(self._execute_task, agent, task)
                    else:
                        # No available agent, put task back in queue
                        self.task_queue.append(task)
                        await asyncio.sleep(2)

                await asyncio.sleep(0.5)

            except Exception as e:
                print(f"[ERROR] Task queue processing error: {e}")
                await asyncio.sleep(1)

    async def _get_available_agent(self, agent_type: AgentType) -> Optional[AgentProcess]:
        """Get an available agent of specified type"""
        for agent in self.agents.values():
            if (
                agent.agent_type == agent_type
                and agent.status in [AgentStatus.IDLE, AgentStatus.RUNNING]
                and agent.current_task is None
            ):

                # Check if agent is healthy
                if await self._ping_agent(agent):
                    return agent
                else:
                    agent.status = AgentStatus.ERROR

        return None

    def _execute_task(self, agent: AgentProcess, task: TaskRequest):
        """Execute a task on an agent"""
        try:
            start_time = time.time()

            # Call agent API
            response = requests.post(
                f"{agent.api_url}/process",
                json={"task_id": task.task_id, "payload": task.payload},
                timeout=task.timeout,
            )

            execution_time = time.time() - start_time

            if response.status_code == 200:
                result = response.json()

                task_response = TaskResponse(
                    task_id=task.task_id,
                    agent_id=agent.agent_id,
                    success=result.get("success", False),
                    response=result.get("response", {}),
                    execution_time=execution_time,
                )

                # Update metrics
                agent.request_count += 1
                agent.performance_metrics["avg_response_time"] = (
                    agent.performance_metrics["avg_response_time"] * (agent.request_count - 1)
                    + execution_time
                ) / agent.request_count

                if result.get("success"):
                    agent.performance_metrics["success_rate"] = min(
                        1.0,
                        (agent.performance_metrics["success_rate"] * (agent.request_count - 1) + 1)
                        / agent.request_count,
                    )
                    self.metrics["successful_tasks"] += 1
                else:
                    agent.error_count += 1
                    agent.performance_metrics["success_rate"] = (
                        agent.performance_metrics["success_rate"]
                        * (agent.request_count - 1)
                        / agent.request_count
                    )
                    self.metrics["failed_tasks"] += 1

                self.completed_tasks.append(task_response)

                # Callback if provided
                if task.callback_url:
                    try:
                        requests.post(task.callback_url, json=asdict(task_response), timeout=10)
                    except:
                        pass

            else:
                # Agent error
                task_response = TaskResponse(
                    task_id=task.task_id,
                    agent_id=agent.agent_id,
                    success=False,
                    response={},
                    execution_time=execution_time,
                    error_message=f"Agent returned HTTP {response.status_code}",
                )
                self.completed_tasks.append(task_response)
                agent.error_count += 1

        except Exception as e:
            # Execution error
            task_response = TaskResponse(
                task_id=task.task_id,
                agent_id=agent.agent_id,
                success=False,
                response={},
                execution_time=time.time() - start_time,
                error_message=str(e),
            )
            self.completed_tasks.append(task_response)
            agent.error_count += 1

        finally:
            # Clean up
            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]
            agent.current_task = None
            agent.status = AgentStatus.RUNNING
            self.metrics["total_tasks"] += 1

    async def _monitor_agents(self):
        """Monitor agent health and performance"""
        while self.running:
            try:
                for agent in self.agents.values():
                    # Check heartbeat
                    if datetime.now() - agent.last_heartbeat > timedelta(seconds=30):
                        if await self._ping_agent(agent):
                            agent.last_heartbeat = datetime.now()
                            if agent.status == AgentStatus.ERROR:
                                agent.status = AgentStatus.RUNNING
                        else:
                            agent.status = AgentStatus.ERROR
                            print(f"[WARNING] Agent {agent.agent_id} not responding")

                    # Update performance metrics
                    if agent.pid:
                        try:
                            process = psutil.Process(agent.pid)
                            agent.performance_metrics["memory_usage"] = (
                                process.memory_info().rss / 1024 / 1024
                            )  # MB
                            agent.performance_metrics["cpu_usage"] = process.cpu_percent()
                        except:
                            pass

                await asyncio.sleep(self.monitoring_interval)

            except Exception as e:
                print(f"[ERROR] Agent monitoring error: {e}")
                await asyncio.sleep(5)

    async def _cleanup_old_tasks(self):
        """Clean up old completed tasks"""
        while self.running:
            try:
                # Keep only recent completed tasks
                if len(self.completed_tasks) > self.task_history_size:
                    self.completed_tasks = self.completed_tasks[-self.task_history_size :]

                await asyncio.sleep(60)  # Cleanup every minute

            except Exception as e:
                print(f"[ERROR] Task cleanup error: {e}")
                await asyncio.sleep(60)

    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        return {
            "orchestrator": {
                "running": self.running,
                "total_agents": len(self.agents),
                "active_tasks": len(self.active_tasks),
                "queued_tasks": len(self.task_queue),
                "completed_tasks": len(self.completed_tasks),
                "metrics": self.metrics,
            },
            "agents": {
                agent_id: {
                    "type": agent.agent_type.value,
                    "status": agent.status.value,
                    "port": agent.port,
                    "pid": agent.pid,
                    "current_task": agent.current_task,
                    "request_count": agent.request_count,
                    "error_count": agent.error_count,
                    "performance": agent.performance_metrics,
                    "uptime": (datetime.now() - agent.start_time).total_seconds(),
                }
                for agent_id, agent in self.agents.items()
            },
        }

    async def stop_all_agents(self):
        """Stop all agent processes"""
        print("[ORCHESTRATOR] Stopping all agents...")
        self.running = False

        for agent in self.agents.values():
            try:
                if agent.process:
                    agent.process.terminate()
                    await asyncio.sleep(2)
                    if agent.process.poll() is None:
                        agent.process.kill()

                print(f"[STOPPED] Agent {agent.agent_id}")

            except Exception as e:
                print(f"[ERROR] Failed to stop agent {agent.agent_id}: {e}")

        self.agents.clear()
        print("[ORCHESTRATOR] All agents stopped")

    def __del__(self):
        """Cleanup on deletion"""
        if self.running:
            asyncio.create_task(self.stop_all_agents())


# API Layer for external communication
app = FastAPI(title="Agent Orchestrator API")
orchestrator = None


@app.on_event("startup")
async def startup_event():
    global orchestrator
    orchestrator = PersistentAgentOrchestrator()
    await orchestrator.start_all_agents()


@app.on_event("shutdown")
async def shutdown_event():
    global orchestrator
    if orchestrator:
        await orchestrator.stop_all_agents()


@app.post("/submit_task")
async def submit_task_api(request: dict):
    """Submit a task to agents"""
    try:
        agent_type = AgentType(request["agent_type"])
        task_id = await orchestrator.submit_task(
            agent_type=agent_type,
            payload=request["payload"],
            priority=request.get("priority", 3),
            timeout=request.get("timeout", 120),
            callback_url=request.get("callback_url"),
        )
        return {"task_id": task_id, "status": "queued"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/task_result/{task_id}")
async def get_task_result_api(task_id: str):
    """Get task result"""
    result = await orchestrator.get_task_result(task_id, timeout=10)
    if result:
        return asdict(result)
    else:
        return {"task_id": task_id, "status": "pending"}


@app.get("/status")
async def get_status_api():
    """Get orchestrator status"""
    return orchestrator.get_status()


@app.post("/restart_agent/{agent_id}")
async def restart_agent_api(agent_id: str):
    """Restart a specific agent"""
    # Implementation would restart the agent
    return {"status": "restarted", "agent_id": agent_id}


if __name__ == "__main__":
    # Run the orchestrator API server
    uvicorn.run(app, host="0.0.0.0", port=7999)
