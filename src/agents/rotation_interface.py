"""Rotation Interface

User interface for controlling automatic coin rotation
Built with love by Deamon Dev

Provides both programmatic and frontend interfaces for rotation control:
- API endpoints for frontend integration
- Manual override capabilities
- Real-time rotation status
- Configuration management
"""

import asyncio
import json
from dataclasses import asdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.agents.automatic_coin_rotator import (
    AutomaticCoinRotator,
    RotationConfig,
    RotationMode,
)


class RotationController:
    """Controller for managing coin rotation with user interface"""

    def __init__(self):
        self.rotator: Optional[AutomaticCoinRotator] = None
        self.running = False
        self.user_override_active = False
        self.manual_assets: List[str] = []
        self.rotation_history: List[Dict[str, Any]] = []

        self.config = RotationConfig()

    async def start_rotation(
        self, mode: str = "hybrid", interval: int = 300, max_assets: int = 5
    ) -> Dict[str, Any]:
        """Start rotation with specified parameters"""
        try:
            self.config.mode = RotationMode(mode)
            self.config.rotation_interval = interval
            self.config.max_assets = max_assets

            if not self.rotator:
                self.rotator = AutomaticCoinRotator(self.config)

            if self.running:
                await self.stop_rotation()

            self.user_override_active = False
            self.manual_assets = []

            self.running = True
            task = asyncio.create_task(self._run_rotation())

            return {
                "success": True,
                "message": f"Rotation started in {mode} mode",
                "config": asdict(self.config),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def start_manual_rotation(self, assets: List[str]) -> Dict[str, Any]:
        """Start manual rotation with specified assets"""
        try:
            if not assets:
                return {"success": False, "error": "No assets specified"}

            available_assets = await self._get_available_assets()
            valid_assets = [asset for asset in assets if asset in available_assets]

            if not valid_assets:
                return {"success": False, "error": "No valid assets specified"}

            self.user_override_active = True
            self.manual_assets = valid_assets

            manual_config = RotationConfig(
                mode=RotationMode.AUTOMATIC,
                rotation_interval=600,  # Longer interval for manual
                max_assets=len(valid_assets),
            )

            if self.running:
                await self.stop_rotation()

            self.rotator = AutomaticCoinRotator(manual_config)
            self.running = True

            await self._initialize_manual_rotation(valid_assets)

            return {
                "success": True,
                "message": f"Manual rotation started with {len(valid_assets)} assets",
                "assets": valid_assets,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def stop_rotation(self) -> Dict[str, Any]:
        """Stop the current rotation"""
        try:
            if self.rotator:
                self.rotator.stop_rotation()

            self.running = False
            self.user_override_active = False
            self.manual_assets = []

            return {
                "success": True,
                "message": "Rotation stopped",
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def get_rotation_status(self) -> Dict[str, Any]:
        """Get current rotation status"""
        try:
            if not self.running or not self.rotator:
                return {
                    "running": False,
                    "mode": None,
                    "current_assets": [],
                    "metrics": {},
                    "user_override": False,
                }

            rotator_metrics = self.rotator.get_rotation_metrics()

            return {
                "running": True,
                "mode": self.config.mode.value,
                "current_assets": [ac.symbol for ac in self.rotator.current_assets],
                "metrics": rotator_metrics["rotation_metrics"],
                "performance": rotator_metrics["performance_history"],
                "user_override": self.user_override_active,
                "manual_assets": self.manual_assets,
                "config": asdict(self.config),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    async def update_configuration(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update rotation configuration"""
        try:
            valid_updates = {}

            if "mode" in updates:
                try:
                    valid_updates["mode"] = RotationMode(updates["mode"])
                except ValueError:
                    return {
                        "success": False,
                        "error": f"Invalid mode: {updates['mode']}",
                    }

            if "rotation_interval" in updates:
                interval = updates["rotation_interval"]
                if isinstance(interval, int) and interval >= 60:
                    valid_updates["rotation_interval"] = interval
                else:
                    return {
                        "success": False,
                        "error": "rotation_interval must be >= 60 seconds",
                    }

            if "max_assets" in updates:
                max_assets = updates["max_assets"]
                if isinstance(max_assets, int) and 1 <= max_assets <= 20:
                    valid_updates["max_assets"] = max_assets
                else:
                    return {
                        "success": False,
                        "error": "max_assets must be between 1 and 20",
                    }

            for key, value in valid_updates.items():
                setattr(self.config, key, value)

            if self.rotator:
                self.rotator.config = self.config

            return {
                "success": True,
                "message": "Configuration updated",
                "config": asdict(self.config),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def force_rotation(
        self, assets_to_add: List[str] = None, assets_to_remove: List[str] = None
    ) -> Dict[str, Any]:
        """Force a rotation cycle with specific assets"""
        try:
            if not self.running or not self.rotator:
                return {"success": False, "error": "Rotation not running"}

            available_assets = await self._get_available_assets()

            if assets_to_add:
                assets_to_add = [asset for asset in assets_to_add if asset in available_assets]

            if assets_to_remove:
                assets_to_remove = [
                    asset for asset in assets_to_remove if asset in available_assets
                ]

            decision = {
                "should_rotate": True,
                "reason": "Manual forced rotation",
                "assets_to_add": assets_to_add or [],
                "assets_to_remove": assets_to_remove or [],
            }

            results = await self.rotator._execute_rotation(decision)

            self.rotation_history.append(
                {
                    "type": "forced",
                    "timestamp": datetime.now().isoformat(),
                    "decision": decision,
                    "results": results,
                }
            )

            return {
                "success": True,
                "message": "Forced rotation executed",
                "results": results,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def get_available_assets(self) -> Dict[str, Any]:
        """Get list of assets available for rotation"""
        try:
            available_assets = await self._get_available_assets()

            asset_info = {}
            for asset in available_assets:
                if asset in self.rotator.asset_configs if self.rotator else {}:
                    config = self.rotator.asset_configs[asset]
                    asset_info[asset] = {
                        "priority": config.priority,
                        "weight": config.weight,
                        "enabled": config.enabled,
                        "min_hold_time": config.min_hold_time,
                        "max_hold_time": config.max_hold_time,
                    }

            return {
                "success": True,
                "available_assets": available_assets,
                "asset_info": asset_info,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def get_rotation_history(self, limit: int = 50) -> Dict[str, Any]:
        """Get rotation history"""
        try:
            return {
                "success": True,
                "history": (self.rotation_history[-limit:] if limit > 0 else self.rotation_history),
                "total_count": len(self.rotation_history),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def _run_rotation(self):
        """Run the rotation loop"""
        if not self.user_override_active:
            await self.rotator.start_automatic_rotation()
        else:
            while self.running:
                await asyncio.sleep(60)
                await self._update_manual_performance()

    async def _initialize_manual_rotation(self, assets: List[str]):
        """Initialize manual rotation with specified assets"""
        self.rotator.current_assets = []
        for asset in assets:
            if asset in self.rotator.asset_configs:
                self.rotator.current_assets.append(self.rotator.asset_configs[asset])
                self.rotator.last_rotation[asset] = datetime.now()
                self.rotator.performance_history[asset] = [0.5]

        print(f"[MANUAL] Initialized with {len(assets)} assets: {assets}")

    async def _update_manual_performance(self):
        """Update performance for manual rotation"""
        if self.rotator:
            await self.rotator._update_performance_data()

    async def _get_available_assets(self) -> List[str]:
        """Get list of available assets"""
        try:
            return [
                "BTC",
                "ETH",
                "SOL",
                "AVAX",
                "MATIC",
                "DOT",
                "LINK",
                "UNI",
                "AAVE",
                "CRV",
            ]
        except Exception:
            return ["BTC", "ETH", "SOL"]


class RotationAPI:
    """API endpoints for frontend integration"""

    def __init__(self):
        self.controller = RotationController()

    async def start_rotation(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """API endpoint to start rotation"""
        mode = request_data.get("mode", "hybrid")
        interval = request_data.get("interval", 300)
        max_assets = request_data.get("max_assets", 5)

        return await self.controller.start_rotation(mode, interval, max_assets)

    async def start_manual_rotation(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """API endpoint to start manual rotation"""
        assets = request_data.get("assets", [])
        return await self.controller.start_manual_rotation(assets)

    async def stop_rotation(self) -> Dict[str, Any]:
        """API endpoint to stop rotation"""
        return await self.controller.stop_rotation()

    async def get_status(self) -> Dict[str, Any]:
        """API endpoint to get rotation status"""
        return await self.controller.get_rotation_status()

    async def update_config(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """API endpoint to update configuration"""
        return await self.controller.update_configuration(request_data)

    async def force_rotation(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """API endpoint to force rotation"""
        assets_to_add = request_data.get("assets_to_add", [])
        assets_to_remove = request_data.get("assets_to_remove", [])
        return await self.controller.force_rotation(assets_to_add, assets_to_remove)

    async def get_assets(self) -> Dict[str, Any]:
        """API endpoint to get available assets"""
        return await self.controller.get_available_assets()

    async def get_history(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """API endpoint to get rotation history"""
        limit = request_data.get("limit", 50)
        return await self.controller.get_rotation_history(limit)


if __name__ == "__main__":

    async def demo_rotation_interface():
        print("\n" + "=" * 70)
        print("[ROTATION INTERFACE DEMO]")
        print("=" * 70)

        api = RotationAPI()

        print("\n[DEMO] Starting automatic rotation...")
        result = await api.start_rotation(
            {"mode": "hybrid", "interval": 60, "max_assets": 4}  # 1 minute for demo
        )
        print(f"Result: {result}")

        await asyncio.sleep(5)

        print("\n[DEMO] Getting status...")
        status = await api.get_status()
        print(f"Status: {json.dumps(status, indent=2)}")

        print("\n[DEMO] Getting available assets...")
        assets = await api.get_assets()
        print(f"Assets: {assets}")

        print("\n[DEMO] Starting manual rotation...")
        manual_result = await api.start_manual_rotation({"assets": ["BTC", "ETH", "SOL"]})
        print(f"Manual result: {manual_result}")

        await asyncio.sleep(3)

        print("\n[DEMO] Stopping rotation...")
        stop_result = await api.stop_rotation()
        print(f"Stop result: {stop_result}")

    asyncio.run(demo_rotation_interface())
