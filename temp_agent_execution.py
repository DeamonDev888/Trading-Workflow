
"""
Persistent Execution Agent
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

class PersistentExecutionAgent:
    """Persistent execution agent with Claude Code CLI integration"""

    def __init__(self, port: int, agent_id: str):
        self.port = port
        self.agent_id = agent_id
        self.current_task = None
        self.claude_process = None
        self.task_count = 0

        # Initialize FastAPI
        self.app = FastAPI(title=f"Persistent Execution Agent")
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
            return {
                "agent_id": self.agent_id,
                "agent_type": "execution",
                "status": "running",
                "current_task": self.current_task,
                "task_count": self.task_count,
                "timestamp": datetime.now().isoformat()
            }

        @self.app.post("/process")
        async def process_task(request: dict):
            """Process a task using Claude Code CLI"""
            try:
                task_id = request.get("task_id", str(uuid.uuid4()))
                task_data = request.get("payload", {})

                self.current_task = task_id
                self.task_count += 1

                # Prepare prompt for Claude Code
                prompt = self._create_claude_prompt(task_data)

                # Call Claude Code CLI
                response = await self._call_claude_code(prompt, task_data)

                self.current_task = None

                return {
                    "success": True,
                    "task_id": task_id,
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                }

            except Exception as e:
                self.current_task = None
                return {
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }

        @self.app.get("/status")
        async def get_status():
            """Get detailed agent status"""
            return {
                "agent_id": self.agent_id,
                "agent_type": "execution",
                "uptime": "running",  # Would calculate actual uptime
                "memory_usage": 0,  # Would get actual memory usage
                "task_count": self.task_count,
                "current_task": self.current_task,
                "claude_process_running": self.claude_process is not None
            }

    def _create_claude_prompt(self, task_data: dict) -> str:
        """Create Claude Code prompt based on agent type"""
        
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
        

    async def _call_claude_code(self, prompt: str, task_data: dict) -> dict:
        """Call Claude Code CLI"""
        try:
            cmd = [
                "claude",
                "--dangerously-skip-permissions",
                "--agent",
                "claude-execution-agent",
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
                return {
                    "response": stdout,
                    "success": True,
                    "execution_time": 0  # Would measure actual time
                }
            else:
                return {
                    "response": stderr,
                    "success": False,
                    "error": f"Claude Code CLI error: {stderr}"
                }

        except asyncio.TimeoutError:
            if self.claude_process:
                self.claude_process.terminate()
                self.claude_process = None
            return {
                "response": "Task timeout",
                "success": False,
                "error": "Claude Code CLI timeout after 120 seconds"
            }
        except Exception as e:
            self.claude_process = None
            return {
                "response": f"Error: {str(e)}",
                "success": False,
                "error": str(e)
            }

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

    agent = PersistentExecutionAgent(args.port, args.agent_id)
    asyncio.run(agent.run())
