"""
Hyperliquid API Integration
Complete Hyperliquid DEX API client with wallet integration
Built with love by Deamon Dev 🚀
"""

from . import signing
from .client import HyperliquidClient
from .types import AssetInfo, Candle, L2Book, Order, Position, Trade
# from .websocket import HyperliquidWebSocket  # TEMPORARILY DISABLED - syntax errors

__version__ = "1.0.0"
__all__ = [
    "HyperliquidClient",
    # "HyperliquidWebSocket",  # TEMPORARILY DISABLED
    "signing",
    "AssetInfo",
    "Order",
    "Position",
    "Trade",
    "L2Book",
    "Candle",
]
