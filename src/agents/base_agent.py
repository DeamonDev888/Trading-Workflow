"""
🚀 NOVAQUOTE Enhanced BaseAgent - 100% Visibility System
Expert-level base agent with comprehensive logging and monitoring
Built with love by Deamon Dev [ROCKET] - Professional Trading Operations
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, Optional

from src.logger import NovaQuoteLogger, get_logger


class BaseAgent:
    """
    Enhanced base class for all NOVAQUOTE trading agents
    Features: 100% visibility logging, state management, performance tracking
    """

    def __init__(
        self,
        agent_type: str,
        enable_postgres: bool = False,
        config: Optional[Dict] = None,
    ):
        """Initialize the enhanced base agent with expert logging"""
        self.agent_type = agent_type
        self.name = f"{agent_type.title()} Agent"
        self.start_time = time.time()
        self.last_update = time.time()
        self.is_running = False
        self.state = {}
        self.enable_postgres = enable_postgres
        self.config = config or {}

        self.logger = get_logger(f"agent.{agent_type}")

        self.data_dir = Path(__file__).parent.parent / "data" / agent_type
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.metrics = {
            "operations_completed": 0,
            "errors_encountered": 0,
            "total_execution_time": 0.0,
            "last_operation_time": 0.0,
        }

        self.logger.agent_lifecycle(
            "INITIALIZED",
            self.agent_type,
            {
                "agent_name": self.name,
                "data_directory": str(self.data_dir),
                "postgres_enabled": self.enable_postgres,
                "config": self.config,
                "initial_metrics": self.metrics,
                "capabilities": [
                    "structured_logging",
                    "state_management",
                    "performance_tracking",
                    "error_handling",
                ],
            },
        )

        self.success(f"{self.name} initialized with 100% visibility logging")

    def critical(self, message: str, data: Optional[Dict] = None, exc_info: bool = True):
        """Log critical error with full context"""
        self.metrics["errors_encountered"] += 1
        self.logger.critical(
            f"[{self.name}] {message}",
            {
                "agent_type": self.agent_type,
                "is_running": self.is_running,
                "uptime": self.get_uptime(),
                **(data or {}),
            },
        )

    def error(self, message: str, data: Optional[Dict] = None, exc_info: bool = False):
        """Log error with context"""
        self.metrics["errors_encountered"] += 1
        self.logger.error(
            f"[{self.name}] {message}",
            {
                "agent_type": self.agent_type,
                "is_running": self.is_running,
                "state_size": len(self.state),
                "last_update": self.last_update,
                **(data or {}),
            },
            exc_info=exc_info,
        )

    def warning(self, message: str, data: Optional[Dict] = None):
        """Log warning with context"""
        self.logger.warning(
            f"[{self.name}] {message}",
            {
                "agent_type": self.agent_type,
                "uptime": self.get_uptime(),
                **(data or {}),
            },
        )

    def info(self, message: str, data: Optional[Dict] = None):
        """Log info message with context"""
        self.logger.info(
            f"[{self.name}] {message}",
            {
                "agent_type": self.agent_type,
                "is_running": self.is_running,
                **(data or {}),
            },
        )

    def success(self, message: str, data: Optional[Dict] = None):
        """Log success message with context"""
        self.logger.success(
            f"[{self.name}] {message}",
            {
                "agent_type": self.agent_type,
                "operations_completed": self.metrics["operations_completed"],
                **(data or {}),
            },
        )

    def debug(self, message: str, data: Optional[Dict] = None):
        """Log debug message with detailed context"""
        self.logger.debug(
            f"[{self.name}] {message}",
            {
                "agent_type": self.agent_type,
                "state_keys": list(self.state.keys()),
                "metrics": self.metrics,
                **(data or {}),
            },
        )

    def trace(self, message: str, data: Optional[Dict] = None):
        """Log trace message with maximum detail"""
        self.logger.trace(
            f"[{self.name}] {message}",
            {
                "agent_type": self.agent_type,
                "full_state": self.state,
                "full_metrics": self.metrics,
                "data_directory": str(self.data_dir),
                **(data or {}),
            },
        )

    def start_operation(self, operation_name: str):
        """Start timing an operation"""
        return time.time()

    def end_operation(
        self,
        operation_name: str,
        start_time: float,
        success: bool = True,
        details: Optional[Dict] = None,
    ):
        """End timing an operation and log performance"""
        duration = time.time() - start_time
        self.metrics["total_execution_time"] += duration
        self.metrics["last_operation_time"] = duration

        if success:
            self.metrics["operations_completed"] += 1

        self.logger.performance(
            operation_name,
            duration,
            {
                "agent_type": self.agent_type,
                "success": success,
                "operations_completed": self.metrics["operations_completed"],
                "average_operation_time": self.metrics["total_execution_time"]
                / max(1, self.metrics["operations_completed"]),
                **(details or {}),
            },
        )

        return duration

    def execute_with_timing(self, operation_name: str, func, *args, **kwargs):
        """Execute a function with automatic timing and logging"""
        start_time = self.start_operation(operation_name)

        try:
            result = func(*args, **kwargs)
            self.end_operation(operation_name, start_time, success=True)
            return result
        except Exception as e:
            self.end_operation(operation_name, start_time, success=False, details={"error": str(e)})
            self.error(
                f"Operation {operation_name} failed",
                {"error": str(e), "args": args, "kwargs": kwargs},
                exc_info=True,
            )
            raise

    def update_state(self, key: str, value: Any):
        """Update a specific state value with logging"""
        old_value = self.state.get(key)
        self.state[key] = value
        self.last_update = time.time()

        self.debug(
            f"State updated: {key}",
            {
                "key": key,
                "old_value": old_value,
                "new_value": value,
                "state_size": len(self.state),
            },
        )

    def batch_update_state(self, updates: Dict[str, Any]):
        """Update multiple state values at once"""
        old_state = self.state.copy()
        self.state.update(updates)
        self.last_update = time.time()

        self.debug(
            "Batch state update",
            {
                "updates": updates,
                "previous_state_size": len(old_state),
                "new_state_size": len(self.state),
            },
        )
    def save_state(self, filename: Optional[str] = None):
        """Save agent state to file with logging"""
        if filename is None:
            filename = f"{self.agent_type}_state.json"

        state_file = self.data_dir / filename

        state_data = {
            "agent_type": self.agent_type,
            "name": self.name,
            "start_time": self.start_time,
            "last_update": self.last_update,
            "is_running": self.is_running,
            "state": self.state,
            "metrics": self.metrics,
            "config": self.config,
        }

        try:
            start_time = self.start_operation("save_state")

            with open(state_file, "w") as f:
                json.dump(state_data, f, indent=2, default=str)

            self.end_operation(
                "save_state",
                start_time,
                success=True,
                details={
                    "file_path": str(state_file),
                    "state_size": len(json.dumps(state_data)),
                    "state_keys": len(self.state),
                },
            )

            self.success(
                f"State saved to {state_file}",
                {
                    "file_size_mb": state_file.stat().st_size / (1024 * 1024),
                    "state_entries": len(self.state),
                },
            )

        except Exception as e:
            self.error(
                f"Failed to save state to {state_file}",
                {"error": str(e)},
                exc_info=True,
            )
            raise

    def load_state(self, filename: Optional[str] = None):
        """Load agent state from file with logging"""
        if filename is None:
            filename = f"{self.agent_type}_state.json"

        state_file = self.data_dir / filename

        if not state_file.exists():
            self.warning(f"State file {state_file} does not exist, starting fresh")
            return False

        try:
            start_time = self.start_operation("load_state")

            with open(state_file, "r") as f:
                state_data = json.load(f)

            self.start_time = state_data.get("start_time", time.time())
            self.last_update = state_data.get("last_update", time.time())
            self.is_running = state_data.get("is_running", False)
            self.state = state_data.get("state", {})
            self.metrics = state_data.get("metrics", self.metrics)
            self.config = state_data.get("config", self.config)

            duration = self.end_operation(
                "load_state",
                start_time,
                success=True,
                details={
                    "file_path": str(state_file),
                    "state_entries_loaded": len(self.state),
                    "uptime_at_load": self.get_uptime(),
                },
            )

            self.success(
                f"State loaded from {state_file}",
                {
                    "state_entries": len(self.state),
                    "load_time_ms": duration * 1000,
                    "was_running": self.is_running,
                },
            )

            return True

        except Exception as e:
            self.error(
                f"Failed to load state from {state_file}",
                {"error": str(e)},
                exc_info=True,
            )
            return False

    def get_state_summary(self) -> Dict:
        """Get a summary of current agent state"""
        return {
            "agent_type": self.agent_type,
            "name": self.name,
            "is_running": self.is_running,
            "uptime": self.get_uptime(),
            "last_update": self.last_update,
            "state_size": len(self.state),
            "state_keys": list(self.state.keys()),
            "metrics": self.metrics.copy(),
            "data_directory": str(self.data_dir),
        }

    def start(self):
        """Start the agent with full logging"""
        if self.is_running:
            self.warning("Agent is already running", {"current_uptime": self.get_uptime()})
            return

        self.is_running = True
        self.logger.agent_lifecycle(
            "START",
            self.agent_type,
            {
                "start_time": self.start_time,
                "initial_state_size": len(self.state),
                "initial_metrics": self.metrics,
                "config": self.config,
            },
        )

        self.success(
            f"{self.name} started",
            {
                "uptime": 0,
                "state_entries": len(self.state),
                "ready_for_operations": True,
            },
        )

    def stop(self, save_state: bool = True):
        """Stop the agent with full logging"""
        if not self.is_running:
            self.warning("Agent is already stopped")
            return

        uptime = self.get_uptime()

        if save_state:
            try:
                self.save_state()
            except Exception as e:
                self.error("Failed to save state during shutdown", {"error": str(e)})

        self.is_running = False

        self.logger.agent_lifecycle(
            "STOP",
            self.agent_type,
            {
                "total_uptime": uptime,
                "final_metrics": self.metrics,
                "final_state_size": len(self.state),
                "operations_completed": self.metrics["operations_completed"],
                "total_errors": self.metrics["errors_encountered"],
                "average_operation_time": (
                    self.metrics["total_execution_time"]
                    / max(1, self.metrics["operations_completed"])
                    if self.metrics["operations_completed"] > 0
                    else 0
                ),
            },
        )

        self.success(
            f"{self.name} stopped",
            {
                "total_uptime_hours": uptime / 3600,
                "operations_completed": self.metrics["operations_completed"],
                "errors_encountered": self.metrics["errors_encountered"],
                "success_rate": (
                    self.metrics["operations_completed"] - self.metrics["errors_encountered"]
                )
                / max(1, self.metrics["operations_completed"])
                * 100,
            },
        )

    def restart(self):
        """Restart the agent"""
        self.info("Restarting agent", {"current_uptime": self.get_uptime()})
        self.stop(save_state=True)
        time.sleep(1)  # Brief pause
        self.start()

    def get_uptime(self) -> float:
        """Get agent uptime in seconds"""
        return time.time() - self.start_time

    def get_status(self) -> Dict:
        """Get comprehensive agent status"""
        uptime = self.get_uptime()

        return {
            "agent_type": self.agent_type,
            "name": self.name,
            "is_running": self.is_running,
            "uptime": {
                "seconds": uptime,
                "minutes": uptime / 60,
                "hours": uptime / 3600,
            },
            "last_update": self.last_update,
            "state": {"size": len(self.state), "keys": list(self.state.keys())},
            "metrics": self.metrics.copy(),
            "performance": {
                "operations_per_hour": self.metrics["operations_completed"] / max(1, uptime / 3600),
                "error_rate": self.metrics["errors_encountered"]
                / max(1, self.metrics["operations_completed"])
                * 100,
                "average_operation_time": (
                    self.metrics["total_execution_time"]
                    / max(1, self.metrics["operations_completed"])
                    if self.metrics["operations_completed"] > 0
                    else 0
                ),
            },
            "data_directory": str(self.data_dir),
            "logging": "NOVAQUOTE_EXPERT_SYSTEM",
        }

    def health_check(self) -> Dict:
        """Perform health check on the agent"""
        issues = []

        uptime = self.get_uptime()
        if uptime > 24 * 3600:  # Running for more than 24 hours
            issues.append("Long uptime detected - consider restart")

        if self.metrics["operations_completed"] > 0:
            error_rate = self.metrics["errors_encountered"] / self.metrics["operations_completed"]
            if error_rate > 0.1:  # More than 10% errors
                issues.append(f"High error rate: {error_rate:.1%}")

        if self.metrics["last_operation_time"] > 300:  # Last operation > 5 minutes
            issues.append("No recent operations")

        if len(self.state) > 10000:  # Very large state
            issues.append("Large state size detected")

        health_status = "HEALTHY" if not issues else "WARNING"

        return {
            "status": health_status,
            "uptime": uptime,
            "issues": issues,
            "metrics": self.metrics.copy(),
            "state_size": len(self.state),
            "last_check": time.time(),
        }


def log(message: str, level: str = "INFO"):
    """Legacy logging function - redirects to new system"""
    logger = get_logger("legacy")
    getattr(logger, level.lower(), logger.info)(f"[LEGACY] {message}")
