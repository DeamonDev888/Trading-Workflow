#!/usr/bin/env python3
"""
Portfolio Manager - Dual Mode System
Mode Simulation vs Mode Mainnet (MetaMask)
"""

import json
import sys
import requests
import random
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal

class PortfolioManager:
    def __init__(self, mode: str = "simulation", wallet_address: Optional[str] = None):
        """
        Initialize portfolio manager

        Args:
            mode: "simulation" or "mainnet"
            wallet_address: MetaMask wallet address (mainnet mode only)
        """
        self.mode = mode
        self.wallet_address = wallet_address
        self.connected = False

        if mode == "mainnet" and wallet_address:
            self.connected = self._connect_real_wallet()
        else:
            self.connected = True  # Simulation always connected

    def _connect_real_wallet(self) -> bool:
        """Connect to real MetaMask wallet via HyperLiquid API"""
        try:
            # Check if wallet exists on HyperLiquid
            url = "https://api.hyperliquid.xyz/info/userState"
            headers = {"Content-Type": "application/json"}

            if self.wallet_address:
                payload = {"user": self.wallet_address}
                response = requests.post(url, json=payload, headers=headers, timeout=10)
                return response.status_code == 200

            return False
        except Exception:
            return False

    def get_real_market_prices(self) -> Dict[str, float]:
        """Get real market prices"""
        try:
            # Binance API for real prices
            symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]
            prices = {}

            for symbol in symbols:
                url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    coin = symbol.replace("USDT", "")
                    prices[coin] = float(data['price'])

            return prices
        except Exception:
            # Fallback prices if API fails
            return {
                'BTC': 103500.0,
                'ETH': 3400.0,
                'SOL': 160.0,
                'BNB': 950.0
            }

    def get_simulation_portfolio(self, prices: Dict[str, float]) -> Dict[str, Any]:
        """Generate realistic simulation portfolio"""
        # Simulate a realistic trading portfolio
        base_allocation = {
            'BTC': {'percentage': 0.40, 'leverage': 2},
            'ETH': {'percentage': 0.30, 'leverage': 1.5},
            'SOL': {'percentage': 0.20, 'leverage': 3},
            'BNB': {'percentage': 0.10, 'leverage': 1}
        }

        total_portfolio_value = random.uniform(10000, 50000)
        positions = []
        total_value = 0
        total_pnl = 0

        for symbol, alloc in base_allocation.items():
            position_value = total_portfolio_value * alloc['percentage']
            position_size = position_value / prices[symbol] * alloc['leverage']

            # Simulate realistic P&L based on recent market movements
            pnl_pct = random.gauss(0.02, 0.05)  # 2% avg return, 5% std
            pnl = position_value * pnl_pct

            positions.append({
                'symbol': symbol,
                'side': 'long',
                'size': round(position_size, 6),
                'entry_price': round(prices[symbol] * (1 - pnl_pct), 2),
                'current_price': round(prices[symbol], 2),
                'pnl': round(pnl, 2),
                'pnl_percentage': round(pnl_pct * 100, 2),
                'leverage': alloc['leverage'],
                'value': round(position_value, 2)
            })

            total_value += position_value
            total_pnl += pnl

        return {
            'mode': 'simulation',
            'total_balance': round(total_value, 2),
            'available_balance': round(total_value * 0.3, 2),
            'margin_used': round(total_value * 0.7, 2),
            'unrealized_pnl': round(total_pnl, 2),
            'daily_pnl': round(total_pnl * 0.1, 2),
            'positions_count': len(positions),
            'positions': positions,
            'leverage_used': round(sum(p['leverage'] for p in positions) / len(positions), 2),
            'risk_score': round(min(1.0, abs(total_pnl) / total_value * 2), 3),
            'connected': True,
            'last_update': datetime.now().isoformat()
        }

    def get_mainnet_portfolio(self, prices: Dict[str, float]) -> Dict[str, Any]:
        """Get real MetaMask portfolio from HyperLiquid"""
        if not self.connected or not self.wallet_address:
            return {
                'mode': 'mainnet',
                'connected': False,
                'error': 'Wallet not connected',
                'wallet_address': self.wallet_address
            }

        try:
            # Get real portfolio data from HyperLiquid
            url = "https://api.hyperliquid.xyz/info/userState"
            headers = {"Content-Type": "application/json"}
            payload = {"user": self.wallet_address}

            response = requests.post(url, json=payload, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()

                # Parse real positions
                positions = []
                total_pnl = 0
                margin_used = 0

                for pos in data.get('assetPositions', []):
                    if pos['position']['size'] != 0:
                        symbol = pos['position']['coin']
                        if symbol in prices:
                            size = float(pos['position']['size'])
                            entry_price = float(pos['position']['entryPx'])
                            current_price = prices[symbol]

                            pnl = size * (current_price - entry_price)
                            total_pnl += pnl
                            margin_used += abs(size * current_price * 0.1)  # 10% margin requirement

                            positions.append({
                                'symbol': symbol,
                                'side': 'long' if size > 0 else 'short',
                                'size': abs(size),
                                'entry_price': entry_price,
                                'current_price': current_price,
                                'pnl': round(pnl, 2),
                                'pnl_percentage': round((current_price - entry_price) / entry_price * 100, 2),
                                'leverage': abs(size * current_price) / (abs(size * current_price) * 0.1),
                                'value': round(abs(size * current_price), 2)
                            })

                # Get wallet balance
                total_balance = float(data.get('crossMarginSummary', {}).get('accountValue', 0))
                available_balance = total_balance - margin_used

                return {
                    'mode': 'mainnet',
                    'connected': True,
                    'wallet_address': self.wallet_address,
                    'total_balance': round(total_balance, 2),
                    'available_balance': round(available_balance, 2),
                    'margin_used': round(margin_used, 2),
                    'unrealized_pnl': round(total_pnl, 2),
                    'daily_pnl': round(total_pnl * 0.05, 2),  # Estimate 5% of total P&L is daily
                    'positions_count': len(positions),
                    'positions': positions,
                    'leverage_used': round(sum(p['leverage'] for p in positions) / len(positions), 2) if positions else 1,
                    'risk_score': round(min(1.0, abs(total_pnl) / total_balance * 2), 3) if total_balance > 0 else 0,
                    'last_update': datetime.now().isoformat()
                }
            else:
                return {
                    'mode': 'mainnet',
                    'connected': False,
                    'error': 'Failed to fetch portfolio data',
                    'wallet_address': self.wallet_address
                }

        except Exception as e:
            return {
                'mode': 'mainnet',
                'connected': False,
                'error': str(e),
                'wallet_address': self.wallet_address
            }

    def get_portfolio_data(self) -> Dict[str, Any]:
        """Get portfolio data based on current mode"""
        prices = self.get_real_market_prices()

        if self.mode == "simulation":
            return self.get_simulation_portfolio(prices)
        else:
            return self.get_mainnet_portfolio(prices)

    def switch_mode(self, new_mode: str, wallet_address: Optional[str] = None) -> Dict[str, Any]:
        """Switch between simulation and mainnet modes"""
        old_mode = self.mode
        self.mode = new_mode

        if new_mode == "mainnet" and wallet_address:
            self.wallet_address = wallet_address
            self.connected = self._connect_real_wallet()
        elif new_mode == "simulation":
            self.wallet_address = None
            self.connected = True

        return {
            'switched': True,
            'old_mode': old_mode,
            'new_mode': new_mode,
            'connected': self.connected,
            'wallet_address': self.wallet_address
        }

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No command specified"}))
        return

    command = sys.argv[1]

    # Parse mode and wallet from arguments
    mode = "simulation"
    wallet_address = None

    if "--mode=" in sys.argv[1]:
        mode = sys.argv[1].split("=")[1]
    elif len(sys.argv) > 2 and "--mode=" in sys.argv[2]:
        mode = sys.argv[2].split("=")[1]

    if "--wallet=" in " ".join(sys.argv):
        for arg in sys.argv:
            if arg.startswith("--wallet="):
                wallet_address = arg.split("=")[1]
                break

    manager = PortfolioManager(mode=mode, wallet_address=wallet_address)

    if command == "--get-portfolio":
        portfolio_data = manager.get_portfolio_data()
        portfolio_data['data_source'] = f"portfolio_manager_{mode}"
        print(json.dumps(portfolio_data, indent=2))

    elif command == "--switch-mode":
        new_mode = sys.argv[2] if len(sys.argv) > 2 else "simulation"
        new_wallet = sys.argv[3] if len(sys.argv) > 3 else None

        result = manager.switch_mode(new_mode, new_wallet)
        print(json.dumps(result, indent=2))

    elif command == "--get-status":
        print(json.dumps({
            'mode': manager.mode,
            'connected': manager.connected,
            'wallet_address': manager.wallet_address,
            'last_check': datetime.now().isoformat()
        }, indent=2))

if __name__ == "__main__":
    main()