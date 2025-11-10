"""
🚀 NOVAQUOTE Log Centralizer - 100% Visibility Monitoring System
Real-time log aggregation and monitoring for all NOVAQUOTE agents
Built by Moon Dev - Professional Trading Operations Dashboard
"""

import argparse
import asyncio
import json
import os
import sys
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from src.logger import get_logger


@dataclass
class LogEntry:
    """Structured log entry representation"""

    timestamp: float
    level: str
    logger: str
    message: str
    data: Dict
    agent_type: str
    symbol: Optional[str] = None


class NovaQuoteLogCentralizer:
    """
    Centralized log monitoring and analysis system
    Features: Real-time monitoring, trade tracking, risk alerts, performance metrics
    """

    def __init__(self, log_directory: str = "logs", update_interval: int = 5):
        self.log_directory = Path(log_directory)
        self.update_interval = update_interval
        self.logger = get_logger("centralizer.main")

        self.running = False
        self.log_files = {}
        self.file_positions = {}

        self.recent_logs = deque(maxlen=1000)  # Keep last 1000 logs
        self.agent_status = {}
        self.trade_summary = defaultdict(dict)
        self.risk_alerts = deque(maxlen=100)  # Keep last 100 risk alerts
        self.performance_metrics = defaultdict(list)

        self.stats = {
            "total_logs_processed": 0,
            "trades_executed": 0,
            "risk_alerts": 0,
            "errors_count": 0,
            "active_agents": 0,
            "start_time": time.time(),
        }

        self.log_directory.mkdir(exist_ok=True)

        self.logger.info(
            "NOVAQUOTE Log Centralizer initialized",
            {
                "log_directory": str(self.log_directory),
                "update_interval": update_interval,
                "features": [
                    "real_time_monitoring",
                    "trade_tracking",
                    "risk_analysis",
                    "performance_metrics",
                ],
            },
        )

    def discover_log_files(self):
        """Discover all log files in the log directory structure"""
        log_files = []

        for log_file in self.log_directory.rglob("*.log"):
            if log_file.is_file():
                log_files.append(log_file)

        return sorted(log_files)

    def parse_log_line(self, line: str) -> Optional[LogEntry]:
        """Parse a JSON log line into a LogEntry object"""
        try:
            line = line.strip()
            if not line:
                return None

            log_data = json.loads(line)

            timestamp = log_data.get("timestamp", "")
            level = log_data.get("level", "INFO")
            logger_name = log_data.get("logger", "")
            message = log_data.get("message", "")
            extra_data = log_data.get("extra_data", {})

            try:
                if isinstance(timestamp, str):
                    from datetime import datetime

                    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    timestamp_float = dt.timestamp()
                else:
                    timestamp_float = float(timestamp)
            except:
                timestamp_float = time.time()

            agent_type = logger_name.split(".")[-1] if "." in logger_name else logger_name

            symbol = None
            if "symbol" in extra_data:
                symbol = extra_data["symbol"]
            elif "trade_data" in extra_data and "symbol" in extra_data["trade_data"]:
                symbol = extra_data["trade_data"]["symbol"]

            return LogEntry(
                timestamp=timestamp_float,
                level=level,
                logger=logger_name,
                message=message,
                data=extra_data,
                agent_type=agent_type,
                symbol=symbol,
            )

        except Exception as e:
            return None

    def process_log_entry(self, entry: LogEntry):
        """Process a single log entry and update statistics"""
        self.recent_logs.append(entry)
        self.stats["total_logs_processed"] += 1

        if entry.agent_type not in self.agent_status:
            self.agent_status[entry.agent_type] = {
                "last_seen": entry.timestamp,
                "last_log_level": entry.level,
                "log_count": 0,
                "error_count": 0,
            }

        self.agent_status[entry.agent_type]["last_seen"] = entry.timestamp
        self.agent_status[entry.agent_type]["last_log_level"] = entry.level
        self.agent_status[entry.agent_type]["log_count"] += 1

        if entry.level in ["ERROR", "CRITICAL"]:
            self.stats["errors_count"] += 1
            self.agent_status[entry.agent_type]["error_count"] += 1

        if entry.level == "TRADE" or "trade" in entry.message.lower():
            self.process_trade_log(entry)

        if entry.level == "RISK" or "risk" in entry.message.lower():
            self.process_risk_log(entry)

        if "performance" in entry.message.lower() or "perf" in entry.message.lower():
            self.process_performance_log(entry)

    def process_trade_log(self, entry: LogEntry):
        """Process trade-related log entries"""
        self.stats["trades_executed"] += 1

        if entry.symbol:
            if entry.symbol not in self.trade_summary:
                self.trade_summary[entry.symbol] = {
                    "total_trades": 0,
                    "successful_trades": 0,
                    "failed_trades": 0,
                    "total_volume_usd": 0.0,
                    "last_trade_time": entry.timestamp,
                    "last_action": None,
                }

            trade_data = entry.data
            self.trade_summary[entry.symbol]["last_trade_time"] = entry.timestamp

            action = "UNKNOWN"
            if "BUY" in entry.message.upper():
                action = "BUY"
            elif "SELL" in entry.message.upper():
                action = "SELL"
            elif "action" in trade_data:
                action = trade_data["action"]

            self.trade_summary[entry.symbol]["last_action"] = action
            self.trade_summary[entry.symbol]["total_trades"] += 1

            if "EXECUTED" in entry.message.upper() or trade_data.get("success", False):
                self.trade_summary[entry.symbol]["successful_trades"] += 1
            elif "FAILED" in entry.message.upper() or not trade_data.get("success", True):
                self.trade_summary[entry.symbol]["failed_trades"] += 1

            if "estimated_value_usd" in trade_data:
                self.trade_summary[entry.symbol]["total_volume_usd"] += trade_data[
                    "estimated_value_usd"
                ]

    def process_risk_log(self, entry: LogEntry):
        """Process risk-related log entries"""
        self.stats["risk_alerts"] += 1

        self.risk_alerts.append(
            {
                "timestamp": entry.timestamp,
                "agent_type": entry.agent_type,
                "message": entry.message,
                "data": entry.data,
                "severity": entry.data.get("severity", "MEDIUM"),
            }
        )

    def process_performance_log(self, entry: LogEntry):
        """Process performance-related log entries"""
        operation = entry.data.get("operation", "unknown")
        duration = entry.data.get("duration_seconds", 0)

        self.performance_metrics[entry.agent_type].append(
            {"timestamp": entry.timestamp, "operation": operation, "duration": duration}
        )

        if len(self.performance_metrics[entry.agent_type]) > 100:
            self.performance_metrics[entry.agent_type] = self.performance_metrics[entry.agent_type][
                -100:
            ]

    def monitor_logs(self):
        """Main monitoring loop - read and process log files"""
        while self.running:
            try:
                log_files = self.discover_log_files()

                for log_file in log_files:
                    self.process_log_file(log_file)

                self.cleanup_agent_status()

                time.sleep(self.update_interval)

            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                time.sleep(self.update_interval)

    def process_log_file(self, log_file: Path):
        """Process a single log file for new entries"""
        try:
            file_key = str(log_file)

            current_size = log_file.stat().st_size

            if file_key not in self.file_positions or current_size > self.file_positions[file_key]:
                with open(log_file, "r", encoding="utf-8") as f:
                    if file_key in self.file_positions:
                        f.seek(self.file_positions[file_key])
                    else:
                        f.seek(0)

                    new_lines = f.readlines()
                    self.file_positions[file_key] = f.tell()

                    for line in new_lines:
                        entry = self.parse_log_line(line)
                        if entry:
                            self.process_log_entry(entry)

        except Exception as e:
            self.logger.warning(f"Error processing log file {log_file}: {e}")

    def cleanup_agent_status(self):
        """Remove agent status for agents not seen recently"""
        current_time = time.time()
        timeout = 3600  # 1 hour timeout

        inactive_agents = []
        for agent_type, status in self.agent_status.items():
            if current_time - status["last_seen"] > timeout:
                inactive_agents.append(agent_type)

        for agent_type in inactive_agents:
            del self.agent_status[agent_type]

        self.stats["active_agents"] = len(self.agent_status)

    def get_dashboard_summary(self) -> Dict:
        """Get comprehensive dashboard summary"""
        current_time = time.time()
        uptime = current_time - self.stats["start_time"]

        return {
            "system_status": {
                "running": self.running,
                "uptime_seconds": uptime,
                "uptime_hours": uptime / 3600,
                "monitoring_interval": self.update_interval,
            },
            "statistics": {
                "total_logs_processed": self.stats["total_logs_processed"],
                "logs_per_second": self.stats["total_logs_processed"] / max(1, uptime),
                "trades_executed": self.stats["trades_executed"],
                "risk_alerts": self.stats["risk_alerts"],
                "errors_count": self.stats["errors_count"],
                "active_agents": self.stats["active_agents"],
            },
            "active_agents": dict(self.agent_status),
            "trade_summary": dict(self.trade_summary),
            "recent_risk_alerts": list(self.risk_alerts)[-10:],  # Last 10 alerts
            "performance_summary": {
                agent: {
                    "avg_duration": sum(m["duration"] for m in metrics) / max(1, len(metrics)),
                    "total_operations": len(metrics),
                    "recent_operations": len(
                        [m for m in metrics if current_time - m["timestamp"] < 300]
                    ),  # Last 5 minutes
                }
                for agent, metrics in self.performance_metrics.items()
            },
        }

    def start(self):
        """Start the log centralizer"""
        if self.running:
            self.logger.warning("Log centralizer is already running")
            return

        self.running = True
        self.stats["start_time"] = time.time()

        self.logger.info(
            "Starting NOVAQUOTE Log Centralizer",
            {
                "monitoring_directory": str(self.log_directory),
                "update_interval": self.update_interval,
            },
        )

        monitor_thread = threading.Thread(target=self.monitor_logs, daemon=True)
        monitor_thread.start()

    def stop(self):
        """Stop the log centralizer"""
        self.running = False
        self.logger.info("Stopping NOVAQUOTE Log Centralizer")

    def print_dashboard(self):
        """Print real-time dashboard to console"""
        if not self.running:
            print("Log centralizer is not running")
            return

        summary = self.get_dashboard_summary()

        os.system("cls" if os.name == "nt" else "clear")

        print("🚀 NOVAQUOTE TRADING PLATFORM - REAL-TIME DASHBOARD")
        print("=" * 80)

        print(
            f"📊 System Status: {'🟢 ACTIVE' if summary['system_status']['running'] else '🔴 INACTIVE'}"
        )
        print(f"⏱️  Uptime: {summary['system_status']['uptime_hours']:.1f} hours")
        print(f"📈 Logs/sec: {summary['statistics']['logs_per_second']:.1f}")
        print()

        print("📈 KEY METRICS")
        print("-" * 40)
        print(f"📋 Total Logs: {summary['statistics']['total_logs_processed']:,}")
        print(f"💰 Trades Executed: {summary['statistics']['trades_executed']}")
        print(f"⚠️  Risk Alerts: {summary['statistics']['risk_alerts']}")
        print(f"❌ Errors: {summary['statistics']['errors_count']}")
        print(f"🤖 Active Agents: {summary['statistics']['active_agents']}")
        print()

        if summary["active_agents"]:
            print("🤖 ACTIVE AGENTS")
            print("-" * 40)
            for agent_type, status in summary["active_agents"].items():
                last_seen = time.time() - status["last_seen"]
                last_seen_str = (
                    f"{last_seen:.0f}s ago" if last_seen < 60 else f"{last_seen/60:.1f}m ago"
                )
                error_indicator = " 🔴" if status["error_count"] > 0 else " 🟢"
                print(
                    f"  {agent_type}{error_indicator}: {status['log_count']} logs, last seen {last_seen_str}"
                )
            print()

        if summary["trade_summary"]:
            print("💰 RECENT TRADING ACTIVITY")
            print("-" * 40)
            for symbol, trades in list(summary["trade_summary"].items())[:5]:  # Top 5 symbols
                last_trade = time.time() - trades["last_trade_time"]
                last_trade_str = (
                    f"{last_trade:.0f}s ago" if last_trade < 60 else f"{last_trade/60:.1f}m ago"
                )
                success_rate = (trades["successful_trades"] / max(1, trades["total_trades"])) * 100
                print(
                    f"  {symbol}: {trades['total_trades']} trades, {success_rate:.1f}% success, last {last_trade_str}"
                )
            print()

        if summary["recent_risk_alerts"]:
            print("⚠️  RECENT RISK ALERTS")
            print("-" * 40)
            for alert in summary["recent_risk_alerts"][:3]:  # Last 3 alerts
                alert_time = time.time() - alert["timestamp"]
                alert_time_str = (
                    f"{alert_time:.0f}s ago" if alert_time < 60 else f"{alert_time/60:.1f}m ago"
                )
                print(f"  {alert['severity']}: {alert['message'][:60]}... ({alert_time_str})")
            print()

        if summary["performance_summary"]:
            print("⚡ PERFORMANCE SUMMARY")
            print("-" * 40)
            for agent, perf in summary["performance_summary"].items():
                print(
                    f"  {agent}: {perf['avg_duration']:.3f}s avg, {perf['recent_operations']} recent ops"
                )
            print()

        print("=" * 80)
        print(f"🔄 Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("Press Ctrl+C to exit")


async def main():
    """Main function to run the log centralizer"""
    parser = argparse.ArgumentParser(description="NOVAQUOTE Log Centralizer")
    parser.add_argument("--log-dir", default="logs", help="Log directory path")
    parser.add_argument("--interval", type=int, default=5, help="Update interval in seconds")
    parser.add_argument("--dashboard", action="store_true", help="Show real-time dashboard")
    args = parser.parse_args()

    centralizer = NovaQuoteLogCentralizer(args.log_dir, args.interval)
    centralizer.start()

    if args.dashboard:
        try:
            while True:
                centralizer.print_dashboard()
                await asyncio.sleep(args.interval)
        except KeyboardInterrupt:
            print("\n👋 Shutting down NOVAQUOTE Log Centralizer...")
            centralizer.stop()
    else:
        try:
            print("🚀 NOVAQUOTE Log Centralizer running...")
            print("Press Ctrl+C to stop")
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Shutting down NOVAQUOTE Log Centralizer...")
            centralizer.stop()


if __name__ == "__main__":
    asyncio.run(main())
