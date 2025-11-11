"""
🚀 NOVAQUOTE EXPERT LOGGING SYSTEM - 100% Visibility Platform
Expert-level logging for trading agents, real-time monitoring, and complete system transparency
Built by Deamon Dev for professional trading operations
"""

import json
import logging
import logging.handlers
import os
import sys
import threading
import time
import traceback
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Union


class LogLevel(Enum):
    """Enhanced log levels for NOVAQUOTE"""

    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    TRADE = "TRADE"
    RISK = "RISK"
    AGENT = "AGENT"
    DEBUG = "DEBUG"
    TRACE = "TRACE"


class NovaQuoteLogger:
    """
    Expert-level structured logging system for NOVAQUOTE Trading Platform

    Features:
    - 100% Structured JSON logging
    - Real-time trade monitoring
    - Agent lifecycle tracking
    - Risk management logging
    - Centralized log collection
    - Performance metrics
    - Error tracking and analysis
    """

    _instances: Dict[str, "NovaQuoteLogger"] = {}
    _lock = threading.Lock()

    def __new__(cls, name: str):
        """Singleton pattern with thread safety"""
        with cls._lock:
            if name not in cls._instances:
                cls._instances[name] = super().__new__(cls)
            return cls._instances[name]

    def __init__(self, name: str):
        if hasattr(self, "_initialized"):
            return

        self.name = name
        self._initialized = True

        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)

        (self.logs_dir / "agents").mkdir(exist_ok=True)
        (self.logs_dir / "trades").mkdir(exist_ok=True)
        (self.logs_dir / "risk").mkdir(exist_ok=True)
        (self.logs_dir / "errors").mkdir(exist_ok=True)
        (self.logs_dir / "performance").mkdir(exist_ok=True)
        (self.logs_dir / "archive").mkdir(exist_ok=True)

        self.loggers = self._setup_loggers()

        self.metrics = {
            "total_logs": 0,
            "error_count": 0,
            "trade_count": 0,
            "risk_alerts": 0,
            "start_time": time.time(),
        }

        self.info(
            "NOVAQUOTE_LOGGING_SYSTEM_INITIALIZED",
            {
                "logger_name": name,
                "log_level": "EXPERT",
                "features": [
                    "structured_json",
                    "real_time_monitoring",
                    "agent_tracking",
                    "trade_logging",
                    "risk_management",
                ],
                "logs_directory": str(self.logs_dir),
                "timestamp": datetime.now().isoformat(),
            },
        )

    def _setup_loggers(self) -> Dict[str, logging.Logger]:
        """Setup multiple specialized loggers"""
        loggers = {}

        loggers["main"] = self._create_logger(
            f"novaquote.{self.name}",
            str(self.logs_dir / "novaquote.log"),
            level=logging.INFO,
        )

        loggers["trade"] = self._create_logger(
            f"novaquote.{self.name}.trades",
            str(self.logs_dir / "trades" / f"{self.name}_trades.log"),
            level=logging.INFO,
        )

        loggers["agent"] = self._create_logger(
            f"novaquote.{self.name}.agents",
            str(self.logs_dir / "agents" / f"{self.name}_agent.log"),
            level=logging.INFO,
        )

        loggers["risk"] = self._create_logger(
            f"novaquote.{self.name}.risk",
            str(self.logs_dir / "risk" / f"{self.name}_risk.log"),
            level=logging.INFO,
        )

        loggers["error"] = self._create_logger(
            f"novaquote.{self.name}.errors",
            str(self.logs_dir / "errors" / f"{self.name}_errors.log"),
            level=logging.ERROR,
        )

        loggers["performance"] = self._create_logger(
            f"novaquote.{self.name}.performance",
            str(self.logs_dir / "performance" / f"{self.name}_performance.log"),
            level=logging.INFO,
        )

        return loggers

    def _create_logger(self, name: str, filepath: str, level: int = logging.INFO) -> logging.Logger:
        """Create a specialized logger with rotation and JSON formatting"""
        logger = logging.getLogger(name)
        logger.setLevel(level)

        if logger.handlers:
            return logger

        file_handler = logging.handlers.RotatingFileHandler(
            filepath, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"  # 10MB
        )

        console_handler = logging.StreamHandler(sys.stdout)

        json_formatter = self._create_json_formatter()
        file_handler.setFormatter(json_formatter)

        console_formatter = self._create_console_formatter()
        console_handler.setFormatter(console_formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def _create_json_formatter(self) -> logging.Formatter:
        """Create JSON formatter for structured logging"""

        class JsonFormatter(logging.Formatter):
            def format(self, record):
                log_entry = {
                    "timestamp": datetime.fromtimestamp(record.created).isoformat(),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                    "module": record.module,
                    "function": record.funcName,
                    "line": record.lineno,
                    "thread": threading.current_thread().name,
                }

                if hasattr(record, "extra_data"):
                    log_entry.update(record.extra_data)

                if record.exc_info:
                    log_entry["exception"] = {
                        "type": record.exc_info[0].__name__,
                        "message": str(record.exc_info[1]),
                        "traceback": traceback.format_exception(*record.exc_info),
                    }

                return json.dumps(log_entry, ensure_ascii=False, separators=(",", ":"))

        return JsonFormatter()

    def _create_console_formatter(self) -> logging.Formatter:
        """Create colored console formatter"""

        class ColoredFormatter(logging.Formatter):
            COLORS = {
                "CRITICAL": "\033[91m",  # Red
                "ERROR": "\033[91m",  # Red
                "WARNING": "\033[93m",  # Yellow
                "INFO": "\033[94m",  # Blue
                "SUCCESS": "\033[92m",  # Green
                "TRADE": "\033[96m",  # Cyan
                "RISK": "\033[95m",  # Magenta
                "AGENT": "\033[93m",  # Yellow
                "DEBUG": "\033[90m",  # Gray
                "RESET": "\033[0m",
            }

            def format(self, record):
                color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
                reset = self.COLORS["RESET"]

                timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")

                return (
                    f"{color}[{timestamp}] {record.levelname:8} | "
                    f"{record.name.split('.')[-1]:15} | {record.getMessage()}{reset}"
                )

        return ColoredFormatter()

    def _log(
        self,
        level: str,
        message: str,
        extra_data: Optional[Dict] = None,
        logger_type: str = "main",
        exc_info: Optional[bool] = None,
    ):
        """Internal logging method"""
        logger = self.loggers.get(logger_type, self.loggers["main"])

        log_level = getattr(logging, level.upper(), logging.INFO)

        record = logger.makeRecord(
            logger.name,
            log_level,
            "",  # pathname
            0,  # lineno
            message,
            (),  # args
            None,  # exc_info
        )

        if extra_data:
            record.extra_data = extra_data

        if exc_info:
            record.exc_info = sys.exc_info()

        logger.handle(record)

        self.metrics["total_logs"] += 1
        if level == "ERROR":
            self.metrics["error_count"] += 1
        elif level == "TRADE":
            self.metrics["trade_count"] += 1
        elif level == "RISK":
            self.metrics["risk_alerts"] += 1

    def critical(self, message: str, data: Optional[Dict] = None):
        """Log critical error"""
        self._log("CRITICAL", message, data, exc_info=True)

    def error(self, message: str, data: Optional[Dict] = None, exc_info: bool = False):
        """Log error"""
        self._log("ERROR", message, data, "error", exc_info)

    def warning(self, message: str, data: Optional[Dict] = None):
        """Log warning"""
        self._log("WARNING", message, data)

    def info(self, message: str, data: Optional[Dict] = None):
        """Log info message"""
        self._log("INFO", message, data)

    def success(self, message: str, data: Optional[Dict] = None):
        """Log success message"""
        self._log("SUCCESS", message, data)

    def debug(self, message: str, data: Optional[Dict] = None):
        """Log debug message"""
        self._log("DEBUG", message, data)

    def trace(self, message: str, data: Optional[Dict] = None):
        """Log trace message"""
        self._log("TRACE", message, data)

    def trade(self, action: str, symbol: str, details: Dict):
        """
        Log trading activity with full details
        Args:
            action: BUY, SELL, CLOSE, OPEN, etc.
            symbol: Trading symbol
            details: Complete trade details (price, size, P&L, etc.)
        """
        trade_data = {
            "action": action,
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "trade_id": details.get("trade_id", f"{int(time.time()*1000)}"),
            **details,
        }

        self._log("TRADE", f"TRADE {action}: {symbol}", trade_data, "trade")

    def agent_lifecycle(self, event: str, agent_type: str, details: Dict):
        """
        Log agent lifecycle events
        Args:
            event: START, STOP, RESTART, ERROR, etc.
            agent_type: Type of agent
            details: Agent event details
        """
        agent_data = {
            "event": event,
            "agent_type": agent_type,
            "timestamp": datetime.now().isoformat(),
            **details,
        }

        self._log("AGENT", f"AGENT {event}: {agent_type}", agent_data, "agent")

    def risk_alert(self, alert_type: str, severity: str, details: Dict):
        """
        Log risk management alerts
        Args:
            alert_type: Type of risk alert
            severity: LOW, MEDIUM, HIGH, CRITICAL
            details: Risk alert details
        """
        risk_data = {
            "alert_type": alert_type,
            "severity": severity,
            "timestamp": datetime.now().isoformat(),
            **details,
        }

        self._log("RISK", f"RISK {alert_type} [{severity}]", risk_data, "risk")

    def performance(self, operation: str, duration: float, details: Dict):
        """
        Log performance metrics
        Args:
            operation: Operation being measured
            duration: Duration in seconds
            details: Additional performance details
        """
        perf_data = {
            "operation": operation,
            "duration_seconds": duration,
            "timestamp": datetime.now().isoformat(),
            **details,
        }

        self._log("INFO", f"PERF {operation}: {duration:.3f}s", perf_data, "performance")

    def portfolio_update(self, total_value: float, positions: Dict, pnl: float):
        """Log portfolio updates with P&L tracking"""
        portfolio_data = {
            "total_value_usd": total_value,
            "positions_count": len(positions),
            "total_pnl": pnl,
            "positions": positions,
            "timestamp": datetime.now().isoformat(),
        }

        self._log(
            "INFO",
            f"PORTFOLIO UPDATE: ${total_value:,.2f} (P&L: ${pnl:,.2f})",
            portfolio_data,
        )

    def market_data(self, symbol: str, data_type: str, data: Dict):
        """Log market data updates"""
        market_data = {
            "symbol": symbol,
            "data_type": data_type,
            "timestamp": datetime.now().isoformat(),
            **data,
        }

        self._log("DEBUG", f"MARKET DATA {symbol}: {data_type}", market_data)

    def get_metrics(self) -> Dict:
        """Get logging metrics"""
        uptime = time.time() - self.metrics["start_time"]
        return {
            **self.metrics,
            "uptime_seconds": uptime,
            "logs_per_second": self.metrics["total_logs"] / uptime if uptime > 0 else 0,
        }

    def flush_all(self):
        """Flush all loggers"""
        for logger in self.loggers.values():
            for handler in logger.handlers:
                handler.flush()

    def shutdown(self):
        """Gracefully shutdown logging system"""
        self.info("NOVAQUOTE_LOGGING_SYSTEM_SHUTTING_DOWN", self.get_metrics())
        self.flush_all()

        for logger in self.loggers.values():
            for handler in logger.handlers:
                handler.close()


_global_loggers: Dict[str, NovaQuoteLogger] = {}


def get_logger(name: str = __name__) -> NovaQuoteLogger:
    """
    Get or create a NOVAQUOTE logger instance

    Args:
        name: Logger name (typically __name__)

    Returns:
        NovaQuoteLogger instance with expert-level capabilities
    """
    if name not in _global_loggers:
        _global_loggers[name] = NovaQuoteLogger(name)
    return _global_loggers[name]


def log_trade(action: str, symbol: str, **details):
    """Quick trade logging"""
    get_logger().trade(action, symbol, details)


def log_agent(event: str, agent_type: str, **details):
    """Quick agent logging"""
    get_logger().agent_lifecycle(event, agent_type, details)


def log_risk(alert_type: str, severity: str, **details):
    """Quick risk logging"""
    get_logger().risk_alert(alert_type, severity, details)


def log_performance(operation: str, duration: float, **details):
    """Quick performance logging"""
    get_logger().performance(operation, duration, details)


def log_portfolio(total_value: float, positions: Dict, pnl: float):
    """Quick portfolio logging"""
    get_logger().portfolio_update(total_value, positions, pnl)


def get_simple_logger(name: str) -> logging.Logger:
    """Get simple Python logger for backward compatibility"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


print("[INIT] NOVAQUOTE EXPERT LOGGING SYSTEM - 100% Visibility Platform Initialized")
print(
    "[FEATURES] Structured JSON | Real-time Monitoring | Agent Tracking | Trade Logging | Risk Management"
)
