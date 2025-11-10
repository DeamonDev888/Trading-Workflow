"""
🚀 NOVAQUOTE Trading Functions
Compatibility layer for refactored system
"""

import json
import logging
from datetime import datetime

from .logger import get_logger

# Use centralized logger
logger = get_logger("novaquote")


# Trading utilities placeholder
def format_usd(amount):
    """Format amount as USD"""
    return f"${amount:,.2f}"


def format_percentage(value):
    """Format value as percentage"""
    return f"{value:+.2f}%"


# API utilities placeholder
def make_api_request(url, method="GET", data=None):
    """Make API request placeholder"""
    logger.info(f"API Request: {method} {url}")
    return {"success": True, "data": None}


# WebSocket utilities placeholder
def send_websocket_message(ws, message):
    """Send WebSocket message"""
    if ws and hasattr(ws, "send"):
        ws.send(json.dumps(message))
        return True
    return False


# Time utilities
def get_timestamp():
    """Get current timestamp"""
    return datetime.now().isoformat()


def format_timestamp(ts):
    """Format timestamp"""
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return ts
