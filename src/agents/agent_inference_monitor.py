"""
Real-time Agent Inference Monitor
Monitors Claude CLI agents and displays inference results in dashboard
"""

import asyncio
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import aiohttp


@dataclass
class InferenceResult:
    """Single inference result from an agent"""

    agent_type: str
    timestamp: datetime
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    confidence: float
    processing_time: float
    success: bool
    error_message: Optional[str] = None


@dataclass
class AgentMetrics:
    """Metrics for a specific agent"""

    agent_type: str
    status: str  # 'online', 'offline', 'error'
    total_inferences: int
    successful_inferences: int
    average_confidence: float
    average_processing_time: float
    last_inference: Optional[datetime]
    last_error: Optional[str]
    uptime_percentage: float
    current_task: Optional[str] = None


class AgentInferenceMonitor:
    """Monitors agent inferences and provides real-time data"""

    def __init__(self):
        self.agent_endpoints = {
            "strategy": "http://localhost:8000",
            "risk": "http://localhost:8001",
            "liquidity": "http://localhost:8002",
            "execution": "http://localhost:8003",
        }
        self.orchestrator_endpoint = "http://localhost:7999"

        self.inference_history: List[InferenceResult] = []
        self.agent_metrics: Dict[str, AgentMetrics] = {}
        self.monitoring = False
        self.session = None

        # Initialize metrics for all agents
        self._initialize_metrics()

        # Logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _initialize_metrics(self):
        """Initialize metrics for all agents"""
        for agent_type in self.agent_endpoints.keys():
            self.agent_metrics[agent_type] = AgentMetrics(
                agent_type=agent_type,
                status="offline",
                total_inferences=0,
                successful_inferences=0,
                average_confidence=0.0,
                average_processing_time=0.0,
                last_inference=None,
                last_error=None,
                uptime_percentage=0.0,
            )

    async def start_monitoring(self):
        """Start monitoring all agents"""
        self.monitoring = True
        self.session = aiohttp.ClientSession()

        self.logger.info("[INFERENCE MONITOR] Starting agent monitoring...")

        # Start monitoring tasks
        tasks = [
            asyncio.create_task(self._monitor_agent(agent_type))
            for agent_type in self.agent_endpoints.keys()
        ]

        # Start orchestrator monitoring
        tasks.append(asyncio.create_task(self._monitor_orchestrator()))

        # Start cleanup task
        tasks.append(asyncio.create_task(self._cleanup_old_inferences()))

        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            self.logger.error(f"Monitoring error: {e}")
        finally:
            await self.stop_monitoring()

    async def stop_monitoring(self):
        """Stop monitoring all agents"""
        self.monitoring = False
        if self.session:
            await self.session.close()
        self.logger.info("[INFERENCE MONITOR] Stopped monitoring")

    async def _monitor_agent(self, agent_type: str):
        """Monitor a specific agent"""
        endpoint = self.agent_endpoints[agent_type]
        metrics = self.agent_metrics[agent_type]

        while self.monitoring:
            try:
                # Check agent health
                async with self.session.get(f"{endpoint}/health", timeout=5) as response:
                    if response.status == 200:
                        health_data = await response.json()
                        metrics.status = "online"
                        metrics.current_task = health_data.get("current_task")

                        # Get recent inferences
                        await self._fetch_recent_inferences(agent_type, endpoint)
                    else:
                        metrics.status = "error"
                        metrics.last_error = f"HTTP {response.status}"

            except asyncio.TimeoutError:
                metrics.status = "offline"
                metrics.last_error = "Connection timeout"
            except Exception as e:
                metrics.status = "offline"
                metrics.last_error = str(e)

            # Update uptime percentage
            await self._update_uptime_percentage(agent_type)

            await asyncio.sleep(2)  # Check every 2 seconds

    async def _fetch_recent_inferences(self, agent_type: str, endpoint: str):
        """Fetch recent inferences from an agent"""
        try:
            async with self.session.get(f"{endpoint}/inferences", timeout=5) as response:
                if response.status == 200:
                    data = await response.json()

                    for inference_data in data.get("recent_inferences", []):
                        # Process only new inferences
                        inference_timestamp = datetime.fromisoformat(inference_data["timestamp"])

                        # Check if we already have this inference
                        if not any(
                            inf.agent_type == agent_type and inf.timestamp == inference_timestamp
                            for inf in self.inference_history
                        ):
                            # Create new inference result
                            inference = InferenceResult(
                                agent_type=agent_type,
                                timestamp=inference_timestamp,
                                input_data=inference_data.get("input", {}),
                                output_data=inference_data.get("output", {}),
                                confidence=inference_data.get("confidence", 0.0),
                                processing_time=inference_data.get("processing_time", 0.0),
                                success=inference_data.get("success", True),
                                error_message=inference_data.get("error_message"),
                            )

                            # Add to history
                            self.inference_history.append(inference)

                            # Update metrics
                            self._update_agent_metrics(agent_type, inference)

        except Exception as e:
            self.logger.error(f"Error fetching inferences for {agent_type}: {e}")

    async def _monitor_orchestrator(self):
        """Monitor the orchestrator for system-wide metrics"""
        while self.monitoring:
            try:
                async with self.session.get(
                    f"{self.orchestrator_endpoint}/status", timeout=5
                ) as response:
                    if response.status == 200:
                        status_data = await response.json()

                        # Update system-wide metrics from orchestrator
                        for agent_status in status_data.get("agents", []):
                            agent_type = agent_status.get("type")
                            if agent_type in self.agent_metrics:
                                metrics = self.agent_metrics[agent_type]
                                metrics.uptime_percentage = agent_status.get("uptime", 0.0)

            except Exception as e:
                self.logger.error(f"Orchestrator monitoring error: {e}")

            await asyncio.sleep(5)  # Check every 5 seconds

    async def _cleanup_old_inferences(self):
        """Clean up old inference results (keep last 100 per agent)"""
        while self.monitoring:
            try:
                # Group inferences by agent
                agent_inferences = {}
                for inference in self.inference_history:
                    if inference.agent_type not in agent_inferences:
                        agent_inferences[inference.agent_type] = []
                    agent_inferences[inference.agent_type].append(inference)

                # Sort and keep only last 100 per agent
                new_history = []
                for agent_type, inferences in agent_inferences.items():
                    inferences.sort(key=lambda x: x.timestamp, reverse=True)
                    new_history.extend(inferences[:100])

                self.inference_history = new_history

            except Exception as e:
                self.logger.error(f"Cleanup error: {e}")

            await asyncio.sleep(60)  # Cleanup every minute

    def _update_agent_metrics(self, agent_type: str, inference: InferenceResult):
        """Update metrics for an agent based on new inference"""
        metrics = self.agent_metrics[agent_type]

        metrics.total_inferences += 1
        if inference.success:
            metrics.successful_inferences += 1

        metrics.last_inference = inference.timestamp

        # Update averages
        if inference.success:
            total_successful = metrics.successful_inferences
            metrics.average_confidence = (
                metrics.average_confidence * (total_successful - 1) + inference.confidence
            ) / total_successful

            metrics.average_processing_time = (
                metrics.average_processing_time * (total_successful - 1) + inference.processing_time
            ) / total_successful

    async def _update_uptime_percentage(self, agent_type: str):
        """Update uptime percentage based on recent status checks"""
        # This is a simplified calculation - in reality you'd track over time
        metrics = self.agent_metrics[agent_type]
        if metrics.status == "online":
            # Gradually increase uptime
            metrics.uptime_percentage = min(100.0, metrics.uptime_percentage + 0.1)
        else:
            # Gradually decrease uptime
            metrics.uptime_percentage = max(0.0, metrics.uptime_percentage - 0.5)

    def get_agent_metrics_json(self, agent_type: str) -> str:
        """Get agent metrics as JSON"""
        if agent_type not in self.agent_metrics:
            return json.dumps({"error": "Agent not found"})

        metrics = self.agent_metrics[agent_type]

        # Convert datetime to string for JSON serialization
        metrics_dict = asdict(metrics)
        if metrics_dict["last_inference"]:
            metrics_dict["last_inference"] = metrics_dict["last_inference"].isoformat()

        return json.dumps(metrics_dict)

    def get_recent_inferences_json(self, agent_type: str, limit: int = 10) -> str:
        """Get recent inferences for an agent as JSON"""
        agent_inferences = [
            inference for inference in self.inference_history if inference.agent_type == agent_type
        ]

        # Sort by timestamp (newest first)
        agent_inferences.sort(key=lambda x: x.timestamp, reverse=True)
        agent_inferences = agent_inferences[:limit]

        # Convert to JSON-serializable format
        result = []
        for inference in agent_inferences:
            inference_dict = asdict(inference)
            inference_dict["timestamp"] = inference.timestamp.isoformat()
            result.append(inference_dict)

        return json.dumps(result)

    def get_system_summary_json(self) -> str:
        """Get system-wide summary as JSON"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_agents": len(self.agent_endpoints),
            "online_agents": sum(1 for m in self.agent_metrics.values() if m.status == "online"),
            "offline_agents": sum(1 for m in self.agent_metrics.values() if m.status == "offline"),
            "error_agents": sum(1 for m in self.agent_metrics.values() if m.status == "error"),
            "total_inferences_last_hour": len(
                [
                    inf
                    for inf in self.inference_history
                    if inf.timestamp > datetime.now() - timedelta(hours=1)
                ]
            ),
            "agents": {
                agent_type: asdict(metrics) for agent_type, metrics in self.agent_metrics.items()
            },
        }

        # Convert datetime objects to strings
        for agent_data in summary["agents"].values():
            if agent_data["last_inference"]:
                agent_data["last_inference"] = agent_data["last_inference"].isoformat()

        return json.dumps(summary)


# Global monitor instance
monitor = AgentInferenceMonitor()

if __name__ == "__main__":

    async def main():
        await monitor.start_monitoring()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[INFERENCE MONITOR] Stopped by user")
