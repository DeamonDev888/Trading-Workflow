"""
[OK] Hybrid Rotation API
Complete API interface for the hybrid rotation system
Built with love by Deamon Dev [ROCKET]

Provides comprehensive frontend integration for hybrid rotation:
- Start/stop hybrid rotation
- Control all 5 modes
- User preference management
- Suggestion handling
- Real-time status monitoring
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, Optional

from src.agents.hybrid_rotation_system import (
    ControlMode,
    HybridConfig,
    HybridRotationManager,
)


class HybridRotationAPI:
    """Complete API for hybrid rotation system"""

    def __init__(self):
        self.hybrid_manager: Optional[HybridRotationManager] = None
        self.running = False

    async def start_hybrid_rotation(
        self, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Start hybrid rotation with specified configuration"""
        try:
            # Parse request
            control_mode = request_data.get("control_mode", "collaborative")
            max_assets = request_data.get("max_assets", 6)
            auto_weight = request_data.get("auto_weight", 0.6)
            user_weight = request_data.get("user_weight", 0.4)
            learning_enabled = request_data.get("learning_enabled", True)

            # Validate control mode
            try:
                mode = ControlMode(control_mode)
            except ValueError:
                return {
                    "success": False,
                    "error": f"Invalid control_mode: {control_mode}",
                    "valid_modes": [m.value for m in ControlMode],
                }

            # Create configuration
            config = HybridConfig(
                control_mode=mode,
                max_assets=max(1, min(20, max_assets)),
                auto_rotation_weight=max(0.0, min(1.0, auto_weight)),
                user_preference_weight=max(0.0, min(1.0, user_weight)),
                learning_enabled=bool(learning_enabled),
            )

            # Ensure weights sum to 1.0
            total_weight = config.auto_rotation_weight + config.user_preference_weight
            if total_weight > 0:
                config.auto_rotation_weight /= total_weight
                config.user_preference_weight /= total_weight

            # Stop existing rotation if running
            if self.running and self.hybrid_manager:
                await self.stop_hybrid_rotation()

            # Create and start hybrid manager
            self.hybrid_manager = HybridRotationManager(config)
            self.running = True

            # Start in background
            task = asyncio.create_task(self._run_hybrid_rotation())

            return {
                "success": True,
                "message": f"Hybrid rotation started in {control_mode} mode",
                "config": {
                    "control_mode": control_mode,
                    "max_assets": config.max_assets,
                    "auto_weight": config.auto_rotation_weight,
                    "user_weight": config.user_preference_weight,
                    "learning_enabled": config.learning_enabled,
                },
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def stop_hybrid_rotation(self) -> Dict[str, Any]:
        """Stop the hybrid rotation system"""
        try:
            if self.hybrid_manager:
                self.hybrid_manager.stop_hybrid_rotation()

            self.running = False

            return {
                "success": True,
                "message": "Hybrid rotation stopped",
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def get_hybrid_status(self) -> Dict[str, Any]:
        """Get comprehensive hybrid rotation status"""
        try:
            if not self.hybrid_manager or not self.running:
                return {
                    "running": False,
                    "control_mode": None,
                    "current_assets": [],
                    "suggestions": [],
                    "metrics": {},
                    "user_preferences": {},
                    "timestamp": datetime.now().isoformat(),
                }

            return self.hybrid_manager.get_hybrid_status()

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def update_control_mode(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Switch control mode"""
        try:
            if not self.hybrid_manager:
                return {"success": False, "error": "Hybrid rotation not running"}

            new_mode = request_data.get("control_mode")
            if not new_mode:
                return {"success": False, "error": "control_mode required"}

            return await self.hybrid_manager.switch_control_mode(new_mode)

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def get_user_preferences(self) -> Dict[str, Any]:
        """Get all user preferences"""
        try:
            if not self.hybrid_manager:
                return {"success": False, "error": "Hybrid rotation not running"}

            preferences = {}
            for symbol, pref in self.hybrid_manager.user_preferences.items():
                preferences[symbol] = {
                    "preference_score": pref.preference_score,
                    "weight_multiplier": pref.weight_multiplier,
                    "locked": pref.lock_until is not None
                    and pref.lock_until > datetime.now(),
                    "lock_until": (
                        pref.lock_until.isoformat() if pref.lock_until else None
                    ),
                    "min_allocation": pref.min_allocation,
                    "max_allocation": pref.max_allocation,
                    "tags": pref.tags,
                }

            return {
                "success": True,
                "preferences": preferences,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def update_user_preference(
        self, symbol: str, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update user preference for a specific asset"""
        try:
            if not self.hybrid_manager:
                return {"success": False, "error": "Hybrid rotation not running"}

            # Validate and prepare preference data
            preference_data = {}

            if "preference_score" in request_data:
                score = request_data["preference_score"]
                if isinstance(score, (int, float)) and 0.0 <= score <= 1.0:
                    preference_data["preference_score"] = score
                else:
                    return {
                        "success": False,
                        "error": "preference_score must be between 0.0 and 1.0",
                    }

            if "weight_multiplier" in request_data:
                multiplier = request_data["weight_multiplier"]
                if isinstance(multiplier, (int, float)) and multiplier >= 0:
                    preference_data["weight_multiplier"] = multiplier
                else:
                    return {"success": False, "error": "weight_multiplier must be >= 0"}

            if "lock_until" in request_data:
                lock_value = request_data["lock_until"]
                if lock_value is None or lock_value == "":
                    preference_data["lock_until"] = None
                else:
                    try:
                        lock_time = datetime.fromisoformat(
                            lock_value.replace("Z", "+00:00")
                        )
                        if lock_time > datetime.now():
                            preference_data["lock_until"] = lock_time.isoformat()
                        else:
                            return {
                                "success": False,
                                "error": "lock_until must be in the future",
                            }
                    except ValueError:
                        return {
                            "success": False,
                            "error": "Invalid lock_until format, use ISO 8601",
                        }

            if "min_allocation" in request_data:
                min_alloc = request_data["min_allocation"]
                if isinstance(min_alloc, (int, float)) and 0.0 <= min_alloc <= 1.0:
                    preference_data["min_allocation"] = min_alloc
                else:
                    return {
                        "success": False,
                        "error": "min_allocation must be between 0.0 and 1.0",
                    }

            if "max_allocation" in request_data:
                max_alloc = request_data["max_allocation"]
                if isinstance(max_alloc, (int, float)) and 0.0 <= max_alloc <= 1.0:
                    preference_data["max_allocation"] = max_alloc
                else:
                    return {
                        "success": False,
                        "error": "max_allocation must be between 0.0 and 1.0",
                    }

            if "tags" in request_data:
                tags = request_data["tags"]
                if isinstance(tags, list) and all(isinstance(tag, str) for tag in tags):
                    preference_data["tags"] = tags
                else:
                    return {
                        "success": False,
                        "error": "tags must be an array of strings",
                    }

            return await self.hybrid_manager.update_user_preference(
                symbol, preference_data
            )

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def get_suggestions(self) -> Dict[str, Any]:
        """Get current rotation suggestions"""
        try:
            if not self.hybrid_manager:
                return {"success": False, "error": "Hybrid rotation not running"}

            suggestions = []
            for i, suggestion in enumerate(self.hybrid_manager.active_suggestions):
                suggestion_data = {
                    "id": i,
                    "action": suggestion.action,
                    "assets": suggestion.assets,
                    "confidence": suggestion.confidence,
                    "reasoning": suggestion.reasoning,
                    "expected_impact": suggestion.expected_impact,
                    "auto_accept": suggestion.auto_accept,
                    "created_at": suggestion.created_at.isoformat(),
                    "user_response": suggestion.user_response,
                }
                suggestions.append(suggestion_data)

            return {
                "success": True,
                "suggestions": suggestions,
                "total_count": len(suggestions),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def respond_to_suggestion(
        self, suggestion_id: int, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Respond to a rotation suggestion"""
        try:
            if not self.hybrid_manager:
                return {"success": False, "error": "Hybrid rotation not running"}

            response = request_data.get("response")
            if response not in ["accept", "reject", "modify"]:
                return {
                    "success": False,
                    "error": "response must be 'accept', 'reject', or 'modify'",
                }

            modifications = (
                request_data.get("modifications") if response == "modify" else None
            )

            return await self.hybrid_manager.respond_to_suggestion(
                suggestion_id, response, modifications
            )

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def force_rotation(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Force a rotation operation"""
        try:
            if not self.hybrid_manager:
                return {"success": False, "error": "Hybrid rotation not running"}

            rotation_type = request_data.get("type", "suggestion")

            if rotation_type == "manual":
                # Manual asset selection
                assets = request_data.get("assets", [])
                if not assets:
                    return {
                        "success": False,
                        "error": "assets required for manual rotation",
                    }

                # Clear current assets and set new ones
                self.hybrid_manager.current_assets = []
                for asset in assets:
                    if asset in self.hybrid_manager.auto_rotator.asset_configs:
                        config = self.hybrid_manager.auto_rotator.asset_configs[asset]
                        self.hybrid_manager.current_assets.append(config)
                        self.hybrid_manager.auto_rotator.last_rotation[asset] = (
                            datetime.now()
                        )
                        self.hybrid_manager.auto_rotator.performance_history[asset] = [
                            0.6
                        ]

                return {
                    "success": True,
                    "message": f"Manual rotation executed with {len(assets)} assets",
                    "assets": assets,
                    "timestamp": datetime.now().isoformat(),
                }

            elif rotation_type == "suggestion":
                # Create and execute a suggestion
                suggestion_data = request_data.get("suggestion", {})
                if not suggestion_data:
                    return {"success": False, "error": "suggestion data required"}

                # This would implement creating a custom suggestion
                return {
                    "success": False,
                    "error": "Custom suggestion generation not implemented yet",
                }

            else:
                return {
                    "success": False,
                    "error": f"Invalid rotation_type: {rotation_type}",
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def get_available_control_modes(self) -> Dict[str, Any]:
        """Get information about available control modes"""
        try:
            modes = {}
            for mode in ControlMode:
                modes[mode.value] = {
                    "name": mode.value.replace("_", " ").title(),
                    "description": self._get_mode_description(mode),
                    "user_interaction": self._get_mode_user_interaction(mode),
                    "automatic_behavior": self._get_mode_automatic_behavior(mode),
                }

            return {
                "success": True,
                "modes": modes,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get detailed system metrics"""
        try:
            if not self.hybrid_manager:
                return {"success": False, "error": "Hybrid rotation not running"}

            base_status = self.hybrid_manager.get_hybrid_status()

            # Add detailed metrics
            detailed_metrics = {
                **base_status["metrics"],
                "decision_breakdown": {
                    "user_percentage": 0,
                    "auto_percentage": 0,
                    "collaborative_percentage": 0,
                },
                "preference_analysis": {},
                "suggestion_effectiveness": {
                    "acceptance_rate": 0,
                    "rejection_rate": 0,
                    "auto_accept_rate": 0,
                },
                "learning_progress": {
                    "patterns_identified": len(base_status.get("user_patterns", {})),
                    "adaptation_events": 0,  # Would be tracked in real implementation
                },
            }

            # Calculate percentages
            total_decisions = detailed_metrics["total_decisions"]
            if total_decisions > 0:
                detailed_metrics["decision_breakdown"]["user_percentage"] = (
                    detailed_metrics["user_decisions"] / total_decisions * 100
                )
                detailed_metrics["decision_breakdown"]["auto_percentage"] = (
                    detailed_metrics["auto_decisions"] / total_decisions * 100
                )
                detailed_metrics["decision_breakdown"]["collaborative_percentage"] = (
                    detailed_metrics["collaborative_decisions"] / total_decisions * 100
                )

            # Calculate suggestion effectiveness
            total_suggestions = detailed_metrics["suggestions_made"]
            if total_suggestions > 0:
                detailed_metrics["suggestion_effectiveness"]["acceptance_rate"] = (
                    detailed_metrics["suggestions_accepted"] / total_suggestions * 100
                )
                detailed_metrics["suggestion_effectiveness"]["rejection_rate"] = (
                    detailed_metrics["suggestions_rejected"] / total_suggestions * 100
                )

            return {
                "success": True,
                "metrics": detailed_metrics,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    # Private helper methods
    async def _run_hybrid_rotation(self):
        """Run hybrid rotation in background"""
        if self.hybrid_manager:
            await self.hybrid_manager.start_hybrid_rotation()

    def _get_mode_description(self, mode: ControlMode) -> str:
        """Get description for a control mode"""
        descriptions = {
            ControlMode.FULL_AUTO: "Complete automatic rotation without user intervention",
            ControlMode.USER_GUIDED: "Automatic rotation with user preferences and guidance",
            ControlMode.USER_OVERRIDE: "User decisions take priority over automatic suggestions",
            ControlMode.SEMI_AUTO: "User handles critical decisions, automatic handles optimization",
            ControlMode.COLLABORATIVE: "AI suggests improvements, user makes final decisions",
        }
        return descriptions.get(mode, "Unknown mode")

    def _get_mode_user_interaction(self, mode: ControlMode) -> str:
        """Get user interaction level for a control mode"""
        interactions = {
            ControlMode.FULL_AUTO: "None - Fully automatic",
            ControlMode.USER_GUIDED: "Low - Set preferences and guidelines",
            ControlMode.USER_OVERRIDE: "High - User can override any decision",
            ControlMode.SEMI_AUTO: "Medium - Handle critical issues only",
            ControlMode.COLLABORATIVE: "Medium - Review and approve suggestions",
        }
        return interactions.get(mode, "Unknown")

    def _get_mode_automatic_behavior(self, mode: ControlMode) -> str:
        """Get automatic behavior description for a control mode"""
        behaviors = {
            ControlMode.FULL_AUTO: "Manages everything automatically",
            ControlMode.USER_GUIDED: "Follows user preferences and guidelines",
            ControlMode.USER_OVERRIDE: "Suggests but waits for user approval",
            ControlMode.SEMI_AUTO: "Optimizes non-critical decisions",
            ControlMode.COLLABORATIVE: "Analyzes and suggests improvements",
        }
        return behaviors.get(mode, "Unknown")


# Demo and testing
if __name__ == "__main__":

    async def demo_hybrid_api():
        print("\n" + "=" * 70)
        print("[HYBRID ROTATION API DEMO]")
        print("=" * 70)

        api = HybridRotationAPI()

        print("[API] Demo 1: Starting collaborative mode...")
        result = await api.start_hybrid_rotation(
            {
                "control_mode": "collaborative",
                "max_assets": 5,
                "auto_weight": 0.6,
                "user_weight": 0.4,
                "learning_enabled": True,
            }
        )
        print(f"  Result: {result['success']}")
        print(f"  Message: {result.get('message', '')}")

        await asyncio.sleep(2)

        print("\n[API] Demo 2: Getting status...")
        status = await api.get_hybrid_status()
        print(f"  Running: {status.get('running', False)}")
        print(f"  Control Mode: {status.get('control_mode')}")
        print(f"  Current Assets: {status.get('current_assets', [])}")

        await asyncio.sleep(2)

        print("\n[API] Demo 3: Getting user preferences...")
        preferences = await api.get_user_preferences()
        if preferences["success"]:
            print(f"  Preferences loaded: {len(preferences['preferences'])} assets")
            for symbol, pref in list(preferences["preferences"].items())[:3]:
                print(f"    {symbol}: {pref['preference_score']:.2f}")

        await asyncio.sleep(2)

        print("\n[API] Demo 4: Updating user preference for BTC...")
        update_result = await api.update_user_preference(
            "BTC",
            {
                "preference_score": 0.9,
                "weight_multiplier": 1.5,
                "tags": ["favorite", "bluechip"],
            },
        )
        print(f"  Result: {update_result['success']}")
        print(f"  Message: {update_result.get('message', '')}")

        await asyncio.sleep(2)

        print("\n[API] Demo 5: Getting available control modes...")
        modes = await api.get_available_control_modes()
        if modes["success"]:
            print(f"  Available modes: {list(modes['modes'].keys())}")

        await asyncio.sleep(2)

        print("\n[API] Demo 6: Stopping hybrid rotation...")
        stop_result = await api.stop_hybrid_rotation()
        print(f"  Result: {stop_result['success']}")
        print(f"  Message: {stop_result.get('message', '')}")

        print("\n[API] API demo completed successfully!")

    asyncio.run(demo_hybrid_api())
