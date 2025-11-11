#!/usr/bin/env python3
"""
Master Agent Advanced Logger
Comprehensive logging system for NOVAQUOTE Master Agent
"""

import json
import time
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

class MasterAgentLogger:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # Initialize log files
        self.master_log_file = self.log_dir / "master_agent.log"
        self.cycles_log_file = self.log_dir / "master_cycles.log"
        self.agents_log_file = self.log_dir / "master_agents.log"
        self.decisions_log_file = self.log_dir / "master_decisions.log"
        self.performance_log_file = self.log_dir / "master_performance.log"

        # In-memory log buffer (for API access)
        self.log_buffer = []
        self.max_buffer_size = 1000

        # Start session
        self.start_session()

    def start_session(self):
        """Initialize logging session"""
        self.log_event("SYSTEM", "SESSION_START", {
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "pid": os.getpid()
        })

    def log_event(self, category: str, event_type: str, data: Dict[str, Any], level: str = "INFO"):
        """Log a structured event"""
        timestamp = datetime.now().isoformat()

        log_entry = {
            "timestamp": timestamp,
            "category": category,
            "event_type": event_type,
            "level": level,
            "data": data,
            "epoch": int(time.time() * 1000)
        }

        # Add to buffer
        self.log_buffer.append(log_entry)
        if len(self.log_buffer) > self.max_buffer_size:
            self.log_buffer.pop(0)

        # Write to appropriate file
        self._write_to_file(log_entry)

    def log_cycle_start(self, cycle_id: int, cycle_duration: int, agents: List[str]):
        """Log cycle start event"""
        self.log_event("CYCLE", "START", {
            "cycle_id": cycle_id,
            "cycle_duration_minutes": cycle_duration // 60,
            "agents_count": len(agents),
            "agents": agents,
            "expected_end": datetime.fromtimestamp(time.time() + cycle_duration).isoformat()
        })

    def log_cycle_end(self, cycle_id: int, duration_seconds: float, results: Dict[str, Any]):
        """Log cycle completion"""
        self.log_event("CYCLE", "END", {
            "cycle_id": cycle_id,
            "duration_seconds": round(duration_seconds, 2),
            "agents_executed": results.get("agents_count", 0),
            "decisions_made": results.get("decisions_count", 0),
            "success_rate": results.get("success_rate", 0.0),
            "average_confidence": results.get("average_confidence", 0.0),
            "errors": results.get("errors", [])
        })

    def log_agent_execution(self, agent_name: str, action: str, status: str, duration: float, data: Dict[str, Any]):
        """Log individual agent execution"""
        self.log_event("AGENT", "EXECUTE", {
            "agent_name": agent_name,
            "action": action,
            "status": status,
            "duration_seconds": round(duration, 3),
            "confidence": data.get("confidence", 0.0),
            "signals_count": data.get("signals_count", 0),
            "recommendation": data.get("recommendation", "NONE"),
            "metrics": data.get("metrics", {})
        }, level="DEBUG" if status == "SUCCESS" else "WARN" if status == "WARNING" else "ERROR")

    def log_decision(self, decision_type: str, input_data: Dict[str, Any], output_data: Dict[str, Any], confidence: float):
        """Log trading decision"""
        self.log_event("DECISION", decision_type, {
            "input_summary": {
                "agents_count": len(input_data.get("agents", [])),
                "signals_count": input_data.get("total_signals", 0),
                "risk_level": input_data.get("risk_level", "UNKNOWN")
            },
            "output": {
                "action": output_data.get("action", "NONE"),
                "symbol": output_data.get("symbol", "NONE"),
                "position_size": output_data.get("position_size", 0.0),
                "leverage": output_data.get("leverage", 1),
                "stop_loss": output_data.get("stop_loss", 0.0),
                "take_profit": output_data.get("take_profit", 0.0)
            },
            "confidence": confidence,
            "reasoning": output_data.get("reasoning", "No reasoning provided")
        })

    def log_performance(self, metrics: Dict[str, Any]):
        """Log performance metrics"""
        self.log_event("PERFORMANCE", "METRICS", {
            "total_cycles": metrics.get("total_cycles", 0),
            "successful_cycles": metrics.get("successful_cycles", 0),
            "success_rate": metrics.get("success_rate", 0.0),
            "average_cycle_duration": metrics.get("average_cycle_duration", 0.0),
            "agents_performance": metrics.get("agents_performance", {}),
            "decisions_made": metrics.get("decisions_made", 0),
            "active_strategies": metrics.get("active_strategies", []),
            "system_load": metrics.get("system_load", 0.0)
        })

    def log_error(self, component: str, error_type: str, error_message: str, stack_trace: Optional[str] = None):
        """Log error event"""
        self.log_event("ERROR", error_type, {
            "component": component,
            "error_message": error_message,
            "stack_trace": stack_trace
        }, level="ERROR")

    def log_warning(self, component: str, warning_type: str, warning_message: str, data: Dict[str, Any] = None):
        """Log warning event"""
        self.log_event("WARNING", warning_type, {
            "component": component,
            "warning_message": warning_message,
            "data": data or {}
        }, level="WARN")

    def get_recent_logs(self, category: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent logs from buffer"""
        logs = self.log_buffer
        if category:
            logs = [log for log in logs if log["category"] == category]
        return logs[-limit:]

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary from logs"""
        cycle_logs = [log for log in self.log_buffer if log["category"] == "CYCLE"]
        decision_logs = [log for log in self.log_buffer if log["category"] == "DECISION"]

        if not cycle_logs:
            return {"status": "NO_DATA"}

        # Calculate metrics
        total_cycles = len(cycle_logs)
        successful_cycles = len([log for log in cycle_logs if log["data"].get("errors", []) == []])

        durations = [log["data"].get("duration_seconds", 0) for log in cycle_logs]
        confidences = [log["data"].get("average_confidence", 0) for log in cycle_logs]

        return {
            "status": "ACTIVE",
            "total_cycles": total_cycles,
            "successful_cycles": successful_cycles,
            "success_rate": round(successful_cycles / total_cycles * 100, 2) if total_cycles > 0 else 0,
            "average_duration": round(sum(durations) / len(durations), 2) if durations else 0,
            "total_decisions": len(decision_logs),
            "last_cycle": cycle_logs[-1]["timestamp"] if cycle_logs else None,
            "uptime_hours": round((time.time() - cycle_logs[0]["epoch"] / 1000) / 3600, 2) if cycle_logs else 0
        }

    def get_agents_status(self) -> Dict[str, Any]:
        """Get current agents status from logs"""
        agent_logs = [log for log in self.log_buffer if log["category"] == "AGENT"]

        # Get latest status for each agent
        agents_status = {}
        for log in reversed(agent_logs):
            agent_name = log["data"].get("agent_name")
            if agent_name and agent_name not in agents_status:
                agents_status[agent_name] = {
                    "last_execution": log["timestamp"],
                    "status": log["data"].get("status", "UNKNOWN"),
                    "confidence": log["data"].get("confidence", 0.0),
                    "duration": log["data"].get("duration_seconds", 0.0),
                    "executions_count": 0
                }

        # Count executions
        for agent_name in agents_status:
            count = len([log for log in agent_logs if log["data"].get("agent_name") == agent_name])
            agents_status[agent_name]["executions_count"] = count

        return agents_status

    def _write_to_file(self, log_entry: Dict[str, Any]):
        """Write log entry to appropriate file"""
        category = log_entry["category"]
        log_line = json.dumps(log_entry) + "\n"

        if category == "CYCLE":
            with open(self.cycles_log_file, 'a', encoding='utf-8') as f:
                f.write(log_line)
        elif category == "AGENT":
            with open(self.agents_log_file, 'a', encoding='utf-8') as f:
                f.write(log_line)
        elif category == "DECISION":
            with open(self.decisions_log_file, 'a', encoding='utf-8') as f:
                f.write(log_line)
        elif category == "PERFORMANCE":
            with open(self.performance_log_file, 'a', encoding='utf-8') as f:
                f.write(log_line)
        else:
            with open(self.master_log_file, 'a', encoding='utf-8') as f:
                f.write(log_line)

    def export_logs(self, output_file: str, category: str = None, hours: int = 24):
        """Export logs to a file"""
        cutoff_time = time.time() - (hours * 3600)
        logs = [log for log in self.log_buffer if log["epoch"] / 1000 >= cutoff_time]

        if category:
            logs = [log for log in logs if log["category"] == category]

        with open(output_file, 'w', encoding='utf-8') as f:
            for log in logs:
                f.write(json.dumps(log) + "\n")

        return len(logs)

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status"""
        return {
            "status": "ACTIVE",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": time.time() - (self.log_buffer[0]["epoch"] / 1000) if self.log_buffer else 0,
            "total_logs": len(self.log_buffer),
            "performance_summary": self.get_performance_summary(),
            "agents_status": self.get_agents_status(),
            "log_files": {
                "master": str(self.master_log_file),
                "cycles": str(self.cycles_log_file),
                "agents": str(self.agents_log_file),
                "decisions": str(self.decisions_log_file),
                "performance": str(self.performance_log_file)
            }
        }
