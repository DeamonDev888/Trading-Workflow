"""
👤 NOVAQUOTE User Identity Management
Built with love by Deamon Dev
Centralized user identification and tracking system
"""

import os
import hashlib
import json
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from src import config
from termcolor import cprint


class UserIdentity:
    """
    Centralized user identity management for NOVAQUOTE

    Handles:
    - User identification from wallet address
    - Anonymous user ID generation
    - Logging context creation
    - User session tracking
    """

    def __init__(self):
        self.user_address = getattr(config, 'USER_ADDRESS', None)
        self.anonymous_id = self._generate_anonymous_id()
        self.session_id = self._generate_session_id()
        self.user_context = self._build_user_context()

        # Log user identification at startup
        self._log_user_identification()

    def _generate_anonymous_id(self) -> str:
        """Generate anonymous user ID from wallet address"""
        if not self.user_address or self.user_address.startswith('0x0000'):
            # Fallback for test/demo environments
            return f"demo_user_{hashlib.md5('demo'.encode()).hexdigest()[:8]}"

        # Create anonymous hash of the address
        hash_input = f"novaquote_user_{self.user_address}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:12]

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_component = hashlib.md5(f"session_{timestamp}".encode()).hexdigest()[:8]
        return f"session_{timestamp}_{random_component}"

    def _build_user_context(self) -> Dict[str, Any]:
        """Build complete user context for logging"""
        return {
            # Anonymous identifiers (safe for logs)
            'anonymous_id': self.anonymous_id,
            'session_id': self.session_id,

            # Public identifiers (non-sensitive)
            'user_address_short': self._get_short_address(),
            'user_network': 'testnet' if getattr(config, 'HYPERLIQUID_TESTNET', False) else 'mainnet',
            'environment': 'development' if os.getenv('NODE_ENV') == 'development' else 'production',

            # System identifiers
            'system_name': 'NOVAQUOTE',
            'trading_mode': 'paper_trading' if getattr(config, 'PAPER_TRADING', True) else 'live_trading',

            # Timestamps
            'session_start': datetime.now().isoformat(),
            'timestamp': datetime.now().isoformat(),

            # User type classification
            'user_type': self._classify_user_type(),

            # Safety flags
            'is_demo': self.user_address.startswith('0x0000'),
            'is_testnet': getattr(config, 'HYPERLIQUID_TESTNET', False),
            'is_paper_trading': getattr(config, 'PAPER_TRADING', True)
        }

    def _get_short_address(self) -> str:
        """Get safe short version of wallet address"""
        if not self.user_address or len(self.user_address) < 10:
            return "unknown"

        if self.user_address.startswith('0x0000'):
            return "demo_address"

        return f"{self.user_address[:6]}...{self.user_address[-4:]}"

    def _classify_user_type(self) -> str:
        """Classify user type based on configuration"""
        if self.user_address.startswith('0x0000'):
            return 'demo_user'

        if getattr(config, 'HYPERLIQUID_TESTNET', False):
            return 'testnet_trader'

        if getattr(config, 'PAPER_TRADING', True):
            return 'paper_trader'

        return 'live_trader'

    def _log_user_identification(self):
        """Log user identification information"""
        cprint("👤 User Identity Established", "cyan", "on_blue")
        cprint(f"   Anonymous ID: {self.anonymous_id}", "green")
        cprint(f"   Session ID: {self.session_id}", "green")
        cprint(f"   Address: {self._get_short_address()}", "green")
        cprint(f"   User Type: {self.user_context['user_type']}", "green")
        cprint(f"   Network: {self.user_context['user_network']}", "green")
        cprint(f"   Trading Mode: {self.user_context['trading_mode']}", "green")

        if self.user_context['is_demo']:
            cprint("   ⚠️  Running in DEMO mode", "yellow")

    def get_log_context(self, **additional_fields) -> Dict[str, Any]:
        """
        Get logging context with user identification

        Args:
            **additional_fields: Additional fields to include in context

        Returns:
            Complete logging context
        """
        context = self.user_context.copy()
        context.update(additional_fields)
        context['log_timestamp'] = datetime.now().isoformat()
        return context

    def format_log_message(self, message: str, level: str = "INFO", **metadata) -> Dict[str, Any]:
        """
        Format a log message with user context

        Args:
            message: Log message
            level: Log level
            **metadata: Additional metadata

        Returns:
            Formatted log entry
        """
        return {
            'message': message,
            'level': level,
            'user_context': self.user_context,
            'metadata': metadata,
            'timestamp': datetime.now().isoformat()
        }

    def log_trade(self, symbol: str, side: str, size: float, price: float,
                  order_id: str, strategy: str = "unknown", **metadata):
        """
        Log a trade with user context

        Args:
            symbol: Trading symbol
            side: Buy/Sell
            size: Position size
            price: Execution price
            order_id: Order ID
            strategy: Strategy name
            **metadata: Additional trade metadata
        """
        trade_data = {
            'anonymous_id': self.anonymous_id,
            'session_id': self.session_id,
            'symbol': symbol,
            'side': side,
            'size': size,
            'price': price,
            'order_id': order_id,
            'strategy': strategy,
            'timestamp': datetime.now().isoformat(),
            'user_type': self.user_context['user_type'],
            'network': self.user_context['user_network'],
            **metadata
        }

        # Log to file (would be implemented with proper logging system)
        self._write_trade_log(trade_data)

        # Console output
        cprint(f"📈 TRADE LOGGED: {side} {size} {symbol} @ ${price:.2f}", "green")
        cprint(f"   Order ID: {order_id} | Strategy: {strategy}", "cyan")
        cprint(f"   User: {self.anonymous_id} ({self._get_short_address()})", "cyan")

    def log_agent_action(self, agent_name: str, action: str, **metadata):
        """
        Log an agent action with user context

        Args:
            agent_name: Name of the agent
            action: Action performed
            **metadata: Additional metadata
        """
        agent_data = {
            'anonymous_id': self.anonymous_id,
            'session_id': self.session_id,
            'agent_name': agent_name,
            'action': action,
            'timestamp': datetime.now().isoformat(),
            'user_context': self.user_context,
            **metadata
        }

        # Log to file
        self._write_agent_log(agent_data)

        # Console output
        cprint(f"🤖 AGENT ACTION: {agent_name} - {action}", "blue")
        cprint(f"   User: {self.anonymous_id}", "cyan")

    def _write_trade_log(self, trade_data: Dict[str, Any]):
        """Write trade log to file"""
        try:
            log_dir = Path("logs/trades")
            log_dir.mkdir(parents=True, exist_ok=True)

            log_file = log_dir / f"trades_{datetime.now().strftime('%Y%m%d')}.jsonl"

            with open(log_file, 'a') as f:
                f.write(json.dumps(trade_data) + '\n')

        except Exception as e:
            cprint(f"⚠️  Failed to write trade log: {e}", "yellow")

    def _write_agent_log(self, agent_data: Dict[str, Any]):
        """Write agent log to file"""
        try:
            log_dir = Path("logs/agents")
            log_dir.mkdir(parents=True, exist_ok=True)

            log_file = log_dir / f"agents_{datetime.now().strftime('%Y%m%d')}.jsonl"

            with open(log_file, 'a') as f:
                f.write(json.dumps(agent_data) + '\n')

        except Exception as e:
            cprint(f"⚠️  Failed to write agent log: {e}", "yellow")

    def get_user_summary(self) -> Dict[str, Any]:
        """Get user identification summary"""
        return {
            'anonymous_id': self.anonymous_id,
            'session_id': self.session_id,
            'address_short': self._get_short_address(),
            'user_type': self.user_context['user_type'],
            'network': self.user_context['user_network'],
            'trading_mode': self.user_context['trading_mode'],
            'session_start': self.user_context['session_start'],
            'is_demo': self.user_context['is_demo']
        }


# Global user identity instance
_user_identity = None

def get_user_identity() -> UserIdentity:
    """Get the global user identity instance"""
    global _user_identity
    if _user_identity is None:
        _user_identity = UserIdentity()
    return _user_identity

def get_user_context() -> Dict[str, Any]:
    """Get user context for logging"""
    return get_user_identity().get_log_context()

def log_user_trade(symbol: str, side: str, size: float, price: float,
                   order_id: str, strategy: str = "unknown", **metadata):
    """Log a trade with user identification"""
    get_user_identity().log_trade(symbol, side, size, price, order_id, strategy, **metadata)

def log_agent_action(agent_name: str, action: str, **metadata):
    """Log an agent action with user identification"""
    get_user_identity().log_agent_action(agent_name, action, **metadata)
