"""Hybrid Rotation System

Intelligent system combining automatic rotation with user control
Built with love by Deamon Dev

This system provides the best of both worlds:
- Automatic rotation for optimal performance
- User control for personal preferences
- Smart integration of both approaches
- Adaptive behavior based on user interaction
"""

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from src.agents.automatic_coin_rotator import AssetConfig, AutomaticCoinRotator
from src.agents.liquidity_tracker import HyperLiquidLiquidityTracker
from src.agents.persistent_agent_client import PersistentAgentClient


class ControlMode(Enum):
    FULL_AUTO = "full_auto"  # 100% automatic
    USER_GUIDED = "user_guided"  # Automatic with user preferences
    USER_OVERRIDE = "user_override"  # User decisions take priority
    SEMI_AUTO = "semi_auto"  # User handles critical decisions, auto handles optimization
    COLLABORATIVE = "collaborative"  # AI suggests, user decides


@dataclass
class UserPreference:
    """User preference for asset management"""

    symbol: str
    preference_score: float = 0.5  # 0.0 (hate) - 1.0 (love)
    weight_multiplier: float = 1.0  # How much this preference affects rotation
    lock_until: Optional[datetime] = None  # Prevent rotation of this asset until
    min_allocation: float = 0.0  # Minimum percentage allocation
    max_allocation: float = 1.0  # Maximum percentage allocation
    tags: List[str] = field(default_factory=list)  # User-defined tags


@dataclass
class HybridConfig:
    """Configuration for hybrid rotation system"""

    control_mode: ControlMode = ControlMode.COLLABORATIVE
    max_assets: int = 6
    auto_rotation_weight: float = 0.6  # How much automatic decisions matter
    user_preference_weight: float = 0.4  # How much user preferences matter
    suggestion_threshold: float = 0.7  # Threshold for showing user suggestions
    auto_accept_threshold: float = 0.9  # Auto-accept high-confidence suggestions
    learning_enabled: bool = True  # Learn from user choices
    adaptation_rate: float = 0.1  # How fast to adapt to user behavior


@dataclass
class RotationSuggestion:
    """AI-generated rotation suggestion for user review"""

    action: str  # "add", "remove", "replace", "rebalance"
    assets: List[str]  # Assets involved
    confidence: float  # AI confidence (0.0-1.0)
    reasoning: str  # Why this suggestion was made
    expected_impact: float  # Expected performance impact
    auto_accept: bool = False  # Whether to auto-execute this
    created_at: datetime = field(default_factory=datetime.now)
    user_response: Optional[str] = None  # User response: "accept", "reject", "modify"


class HybridRotationManager:
    """Intelligent hybrid rotation system"""

    def __init__(self, config: Optional[HybridConfig] = None):
        self.config = config or HybridConfig()
        self.liquidity_tracker = HyperLiquidLiquidityTracker()
        self.client: Optional[PersistentAgentClient] = None

        self.auto_rotator = AutomaticCoinRotator()
        self.user_preferences: Dict[str, UserPreference] = {}
        self.active_suggestions: List[RotationSuggestion] = []
        self.suggestion_history: List[RotationSuggestion] = []

        self.running = False
        self.current_assets: List[AssetConfig] = []
        self.last_rotation = datetime.now()
        self.user_interaction_count = 0
        self.auto_rotation_count = 0
        self.collaborative_decisions = 0

        self.user_patterns: Dict[str, Any] = {}
        self.preference_evolution: Dict[str, List[float]] = {}

        self.hybrid_metrics = {
            "total_decisions": 0,
            "user_decisions": 0,
            "auto_decisions": 0,
            "collaborative_decisions": 0,
            "suggestions_made": 0,
            "suggestions_accepted": 0,
            "suggestions_rejected": 0,
            "performance_improvement": 0.0,
            "user_satisfaction": 0.8,  # Estimated satisfaction
        }

    async def start_hybrid_rotation(self):
        """Start the hybrid rotation system"""
        print("[HYBRID] Starting intelligent hybrid rotation system")
        print(f"[CONFIG] Control Mode: {self.config.control_mode.value}")
        print(
            f"[CONFIG] Auto Weight: {self.config.auto_rotation_weight:.1f}, User Weight: {self.config.user_preference_weight:.1f}"
        )

        async with PersistentAgentClient() as client:
            self.client = client
            self.running = True

            await self._initialize_hybrid_system()

            while self.running:
                try:
                    await self._perform_hybrid_rotation_cycle()
                    await asyncio.sleep(120)  # Check every 2 minutes

                except Exception as e:
                    print(f"[ERROR] Hybrid rotation cycle failed: {e}")
                    await asyncio.sleep(60)

    async def _initialize_hybrid_system(self):
        """Initialize the hybrid system"""
        print("[INIT] Initializing hybrid rotation system...")

        await self.auto_rotator._initialize_monitoring()

        await self._load_user_preferences()

        initial_assets = await self._get_hybrid_initial_assets()

        print(f"[INIT] Hybrid system initialized with {len(initial_assets)} assets")
        await self._display_hybrid_status()

    async def _load_user_preferences(self):
        """Load or initialize user preferences"""
        default_assets = ["BTC", "ETH", "SOL", "AVAX", "MATIC", "DOT"]

        for asset in default_assets:
            self.user_preferences[asset] = UserPreference(
                symbol=asset,
                preference_score=0.6 + (hash(asset) % 40) / 100,  # Random-ish preference
                weight_multiplier=1.0,
                tags=["bluechip" if asset in ["BTC", "ETH"] else "altcoin"],
            )

        print(f"[PREF] Loaded {len(self.user_preferences)} user preferences")

    async def _get_hybrid_initial_assets(self) -> List[AssetConfig]:
        """Get initial assets considering both auto and user preferences"""
        auto_assets = await self.auto_rotator._get_liquid_assets()

        scored_assets = []
        for asset in auto_assets[:12]:  # Top 12 liquid assets
            if asset in self.auto_rotator.asset_configs:
                user_pref = self.user_preferences.get(asset)

                auto_score = 1.0 - (
                    auto_assets.index(asset) / len(auto_assets)
                )  # Higher for better rank
                user_score = user_pref.preference_score if user_pref else 0.5

                hybrid_score = (
                    auto_score * self.config.auto_rotation_weight
                    + user_score * self.config.user_preference_weight
                )

                scored_assets.append((asset, hybrid_score, user_pref))

        scored_assets.sort(key=lambda x: x[1], reverse=True)

        selected = []
        for asset, score, user_pref in scored_assets[: self.config.max_assets]:
            config = self.auto_rotator.asset_configs[asset]
            self.current_assets.append(config)
            selected.append(asset)

            self.auto_rotator.last_rotation[asset] = datetime.now()
            self.auto_rotator.performance_history[asset] = [score]

        return selected

    async def _perform_hybrid_rotation_cycle(self):
        """Perform one hybrid rotation cycle"""
        cycle_start = time.time()
        print(f"\n[HYBRID] Rotation cycle started")

        try:
            await self._update_performance_data()

            rotation_needs = await self._analyze_hybrid_rotation_needs()

            if rotation_needs["action_needed"]:
                suggestions = await self._generate_rotation_suggestions(rotation_needs)
                await self._process_suggestions(suggestions)

            await self._execute_hybrid_rotations()

            if self.config.learning_enabled:
                await self._learn_from_cycle()

            cycle_time = time.time() - cycle_start
            self._update_hybrid_metrics(cycle_time)

        except Exception as e:
            print(f"[ERROR] Hybrid rotation cycle failed: {e}")

    async def _analyze_hybrid_rotation_needs(self) -> Dict[str, Any]:
        """Analyze rotation needs based on control mode"""
        needs = {
            "action_needed": False,
            "reason": "",
            "auto_candidates": [],
            "user_preferences_violated": [],
            "performance_issues": [],
            "market_opportunities": [],
        }

        if self.config.control_mode == ControlMode.FULL_AUTO:
            return await self._analyze_auto_rotation(needs)

        elif self.config.control_mode == ControlMode.USER_OVERRIDE:
            return await self._analyze_user_override_rotation(needs)

        elif self.config.control_mode == ControlMode.USER_GUIDED:
            return await self._analyze_guided_rotation(needs)

        elif self.config.control_mode == ControlMode.SEMI_AUTO:
            return await self._analyze_semi_auto_rotation(needs)

        elif self.config.control_mode == ControlMode.COLLABORATIVE:
            return await self._analyze_collaborative_rotation(needs)

        return needs

    async def _analyze_auto_rotation(self, needs: Dict[str, Any]) -> Dict[str, Any]:
        """Full automatic rotation analysis"""
        auto_decision = await self.auto_rotator._analyze_rotation_needs()

        if auto_decision["should_rotate"]:
            needs["action_needed"] = True
            needs["reason"] = f"Automatic rotation: {auto_decision['reason']}"
            needs["auto_candidates"] = auto_decision.get("assets_to_add", [])

        return needs

    async def _analyze_user_override_rotation(self, needs: Dict[str, Any]) -> Dict[str, Any]:
        """User override analysis - check for locked assets and preference violations"""
        current_time = datetime.now()

        for asset_config in self.current_assets:
            asset = asset_config.symbol
            user_pref = self.user_preferences.get(asset)

            if user_pref and user_pref.lock_until and user_pref.lock_until > current_time:
                continue  # Skip locked assets

            if asset in self.auto_rotator.performance_history:
                perf_history = self.auto_rotator.performance_history[asset]
                if len(perf_history) >= 3:
                    avg_perf = sum(perf_history[-3:]) / 3
                    if avg_perf < 0.3:  # Poor performance
                        needs["action_needed"] = True
                        needs["reason"] = f"Poor performance for {asset}: {avg_perf:.3f}"
                        needs["performance_issues"].append(asset)

        return needs

    async def _analyze_guided_rotation(self, needs: Dict[str, Any]) -> Dict[str, Any]:
        """User-guided rotation analysis"""
        auto_decision = await self.auto_rotator._analyze_rotation_needs()

        if auto_decision.get("assets_to_add"):
            filtered_additions = []
            for asset in auto_decision["assets_to_add"]:
                user_pref = self.user_preferences.get(asset)
                if not user_pref or user_pref.preference_score > 0.3:  # User doesn't hate it
                    filtered_additions.append(asset)

            if filtered_additions:
                needs["action_needed"] = True
                needs["reason"] = "Guided rotation based on user preferences"
                needs["auto_candidates"] = filtered_additions

        return needs

    async def _analyze_semi_auto_rotation(self, needs: Dict[str, Any]) -> Dict[str, Any]:
        """Semi-automatic rotation - only critical issues trigger user interaction"""
        for asset_config in self.current_assets:
            asset = asset_config.symbol

            if asset in self.auto_rotator.performance_history:
                perf_history = self.auto_rotator.performance_history[asset]
                if len(perf_history) >= 5:
                    recent_perf = perf_history[-3:]
                    avg_recent = sum(recent_perf) / 3

                    if avg_recent < 0.2:
                        needs["action_needed"] = True
                        needs["reason"] = f"Critical performance issue for {asset}"
                        needs["performance_issues"].append(asset)

        return needs

    async def _analyze_collaborative_rotation(self, needs: Dict[str, Any]) -> Dict[str, Any]:
        """Collaborative rotation - AI suggests, user decides"""
        current_time = datetime.now()

        for asset_config in self.current_assets:
            asset = asset_config.symbol
            user_pref = self.user_preferences.get(asset)

            if user_pref and user_pref.lock_until and user_pref.lock_until > current_time:
                continue

            available_assets = await self.auto_rotator._get_liquid_assets()
            current_score = await self._calculate_asset_score(asset)

            for candidate in available_assets:
                if candidate not in [ac.symbol for ac in self.current_assets]:
                    candidate_score = await self._calculate_asset_score(candidate)
                    user_candidate_pref = self.user_preferences.get(candidate)

                    if candidate_score > current_score + 0.2 and (
                        not user_candidate_pref or user_candidate_pref.preference_score > 0.3
                    ):
                        needs["action_needed"] = True
                        needs["reason"] = "Collaborative improvement suggestions"
                        needs["market_opportunities"].append(
                            {
                                "current": asset,
                                "candidate": candidate,
                                "improvement": candidate_score - current_score,
                            }
                        )
                        break  # One suggestion per cycle is enough

        return needs

    async def _generate_rotation_suggestions(
        self, rotation_needs: Dict[str, Any]
    ) -> List[RotationSuggestion]:
        """Generate rotation suggestions based on analysis and control mode"""
        suggestions = []

        if self.config.control_mode == ControlMode.FULL_AUTO:
            return []

        elif self.config.control_mode == ControlMode.USER_OVERRIDE:
            for asset in rotation_needs["performance_issues"]:
                suggestion = RotationSuggestion(
                    action="replace",
                    assets=[asset],
                    confidence=0.8,
                    reasoning=f"Asset {asset} showing poor performance",
                    expected_impact=0.3,
                    auto_accept=False,
                )
                suggestions.append(suggestion)

        elif self.config.control_mode == ControlMode.USER_GUIDED:
            for asset in rotation_needs["auto_candidates"]:
                user_pref = self.user_preferences.get(asset)
                suggestion = RotationSuggestion(
                    action="add",
                    assets=[asset],
                    confidence=0.7,
                    reasoning=f"Good performance match for user preferences",
                    expected_impact=0.2,
                    auto_accept=user_pref and user_pref.preference_score > 0.8,
                )
                suggestions.append(suggestion)

        elif self.config.control_mode == ControlMode.SEMI_AUTO:
            for asset in rotation_needs["performance_issues"]:
                suggestion = RotationSuggestion(
                    action="replace",
                    assets=[asset],
                    confidence=0.9,
                    reasoning=f"Critical performance issue detected for {asset}",
                    expected_impact=0.4,
                    auto_accept=False,  # Critical issues need user approval
                )
                suggestions.append(suggestion)

        elif self.config.control_mode == ControlMode.COLLABORATIVE:
            for opportunity in rotation_needs["market_opportunities"]:
                suggestion = RotationSuggestion(
                    action="replace",
                    assets=[opportunity["current"], opportunity["candidate"]],
                    confidence=0.6 + opportunity["improvement"],
                    reasoning=f"Replace {opportunity['current']} with {opportunity['candidate']} for {opportunity['improvement']:.3f} improvement",
                    expected_impact=opportunity["improvement"],
                    auto_accept=opportunity["improvement"] > self.config.auto_accept_threshold,
                )
                suggestions.append(suggestion)

        self.active_suggestions.extend(suggestions)
        self.hybrid_metrics["suggestions_made"] += len(suggestions)

        return suggestions

    async def _process_suggestions(self, suggestions: List[RotationSuggestion]):
        """Process rotation suggestions based on control mode"""
        for suggestion in suggestions:
            if suggestion.auto_accept and self.config.control_mode != ControlMode.COLLABORATIVE:
                await self._execute_suggestion(suggestion, "auto_accepted")
            elif self.config.control_mode == ControlMode.COLLABORATIVE:
                print(f"[SUGGESTION] {suggestion.reason} (confidence: {suggestion.confidence:.2f})")
            else:
                await self._handle_mode_specific_suggestion(suggestion)

    async def _handle_mode_specific_suggestion(self, suggestion: RotationSuggestion):
        """Handle suggestions based on specific control mode"""
        if self.config.control_mode == ControlMode.USER_GUIDED:
            if suggestion.action == "add":
                user_pref = self.user_preferences.get(suggestion.assets[0])
                if user_pref and user_pref.preference_score > 0.7:
                    await self._execute_suggestion(suggestion, "user_guided_accept")

        elif self.config.control_mode == ControlMode.SEMI_AUTO:
            if suggestion.confidence > 0.85:
                await self._execute_suggestion(suggestion, "auto_critical")

    async def _execute_suggestion(self, suggestion: RotationSuggestion, response_type: str):
        """Execute a rotation suggestion"""
        try:
            success = False

            if suggestion.action == "add":
                asset = suggestion.assets[0]
                if len(self.current_assets) < self.config.max_assets:
                    if await self._add_asset_to_rotation(asset):
                        success = True

            elif suggestion.action == "remove":
                asset = suggestion.assets[0]
                if await self._remove_asset_from_rotation(asset):
                    success = True

            elif suggestion.action == "replace":
                old_asset = suggestion.assets[0]
                new_asset = suggestion.assets[1] if len(suggestion.assets) > 1 else None

                if new_asset:
                    if await self._remove_asset_from_rotation(old_asset):
                        if await self._add_asset_to_rotation(new_asset):
                            success = True

            suggestion.user_response = response_type
            self.suggestion_history.append(suggestion)
            self.active_suggestions.remove(suggestion)

            if success:
                if response_type in ["auto_accepted", "user_guided_accept"]:
                    self.auto_rotation_count += 1
                elif "user" in response_type:
                    self.user_interaction_count += 1
                elif "collaborative" in response_type:
                    self.collaborative_decisions += 1

            print(f"[EXECUTE] {suggestion.action} executed: {success} ({response_type})")

        except Exception as e:
            print(f"[ERROR] Failed to execute suggestion: {e}")

    async def _execute_hybrid_rotations(self):
        """Execute any pending rotations"""
        if self.config.control_mode == ControlMode.FULL_AUTO:
            auto_decision = await self.auto_rotator._analyze_rotation_needs()
            if auto_decision["should_rotate"]:
                await self.auto_rotator._execute_rotation(auto_decision)

    async def _add_asset_to_rotation(self, asset: str) -> bool:
        """Add an asset to the rotation"""
        try:
            if asset in self.auto_rotator.asset_configs:
                config = self.auto_rotator.asset_configs[asset]
                self.current_assets.append(config)

                self.auto_rotator.last_rotation[asset] = datetime.now()
                self.auto_rotator.performance_history[asset] = [0.6]

                print(f"  [+] Added {asset} to hybrid rotation")
                return True
        except Exception as e:
            print(f"[ERROR] Failed to add {asset}: {e}")
        return False

    async def _remove_asset_from_rotation(self, asset: str) -> bool:
        """Remove an asset from the rotation"""
        try:
            self.current_assets = [ac for ac in self.current_assets if ac.symbol != asset]
            print(f"  [-] Removed {asset} from hybrid rotation")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to remove {asset}: {e}")
        return False

    async def _update_performance_data(self):
        """Update performance data for current assets"""
        if self.client:
            await self.auto_rotator._update_performance_data()

    async def _calculate_asset_score(self, asset: str) -> float:
        """Calculate hybrid score for an asset"""
        perf_score = 0.5
        if asset in self.auto_rotator.performance_history:
            history = self.auto_rotator.performance_history[asset]
            if history:
                perf_score = sum(history) / len(history)

        user_score = 0.5
        if asset in self.user_preferences:
            user_score = self.user_preferences[asset].preference_score

        hybrid_score = (
            perf_score * self.config.auto_rotation_weight
            + user_score * self.config.user_preference_weight
        )

        return hybrid_score

    async def _learn_from_cycle(self):
        """Learn from the rotation cycle to improve future suggestions"""
        if not self.config.learning_enabled:
            return

        for suggestion in self.suggestion_history[-5:]:  # Last 5 suggestions
            if suggestion.user_response:
                await self._update_user_patterns(suggestion)

        for asset_config in self.current_assets:
            asset = asset_config.symbol
            if asset in self.auto_rotator.performance_history:
                perf_history = self.auto_rotator.performance_history[asset]
                if len(perf_history) >= 3:
                    recent_perf = sum(perf_history[-3:]) / 3

                    if asset in self.user_preferences:
                        user_pref = self.user_preferences[asset]
                        adjustment = (recent_perf - 0.5) * self.config.adaptation_rate
                        user_pref.preference_score = max(
                            0.1, min(1.0, user_pref.preference_score + adjustment)
                        )

    async def _update_user_patterns(self, suggestion: RotationSuggestion):
        """Update user behavior patterns"""
        pattern_key = f"{suggestion.action}_{suggestion.confidence:.1f}"

        if pattern_key not in self.user_patterns:
            self.user_patterns[pattern_key] = {"accept": 0, "reject": 0}

        if "accept" in suggestion.user_response:
            self.user_patterns[pattern_key]["accept"] += 1
        elif "reject" in suggestion.user_response:
            self.user_patterns[pattern_key]["reject"] += 1

    def _update_hybrid_metrics(self, cycle_time: float):
        """Update hybrid rotation metrics"""
        self.hybrid_metrics["total_decisions"] = (
            self.auto_rotation_count + self.user_interaction_count + self.collaborative_decisions
        )
        self.hybrid_metrics["user_decisions"] = self.user_interaction_count
        self.hybrid_metrics["auto_decisions"] = self.auto_rotation_count
        self.hybrid_metrics["collaborative_decisions"] = self.collaborative_decisions

        total_suggestions = self.hybrid_metrics["suggestions_made"]
        if total_suggestions > 0:
            acceptance_rate = self.hybrid_metrics["suggestions_accepted"] / total_suggestions
            self.hybrid_metrics["user_satisfaction"] = min(1.0, acceptance_rate * 1.2)

    async def respond_to_suggestion(
        self,
        suggestion_id: int,
        response: str,
        modifications: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Allow user to respond to a suggestion"""
        try:
            if 0 <= suggestion_id < len(self.active_suggestions):
                suggestion = self.active_suggestions[suggestion_id]

                if response == "accept":
                    await self._execute_suggestion(suggestion, "user_accept")
                    self.hybrid_metrics["suggestions_accepted"] += 1

                elif response == "reject":
                    suggestion.user_response = "user_reject"
                    self.suggestion_history.append(suggestion)
                    self.active_suggestions.remove(suggestion)
                    self.hybrid_metrics["suggestions_rejected"] += 1

                elif response == "modify" and modifications:
                    await self._apply_modifications(suggestion, modifications)

                return {
                    "success": True,
                    "message": f"Suggestion {response}ed",
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                return {"success": False, "error": "Invalid suggestion ID"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def update_user_preference(
        self, symbol: str, preference_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update user preferences for an asset"""
        try:
            if symbol not in self.user_preferences:
                self.user_preferences[symbol] = UserPreference(symbol=symbol)

            user_pref = self.user_preferences[symbol]

            if "preference_score" in preference_data:
                user_pref.preference_score = max(0.0, min(1.0, preference_data["preference_score"]))

            if "weight_multiplier" in preference_data:
                user_pref.weight_multiplier = preference_data["weight_multiplier"]

            if "lock_until" in preference_data:
                if preference_data["lock_until"]:
                    user_pref.lock_until = datetime.fromisoformat(preference_data["lock_until"])
                else:
                    user_pref.lock_until = None

            if "min_allocation" in preference_data:
                user_pref.min_allocation = preference_data["min_allocation"]

            if "max_allocation" in preference_data:
                user_pref.max_allocation = preference_data["max_allocation"]

            if "tags" in preference_data:
                user_pref.tags = preference_data["tags"]

            print(f"[PREF] Updated preference for {symbol}: {user_pref.preference_score:.2f}")

            return {
                "success": True,
                "message": f"Preference updated for {symbol}",
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def switch_control_mode(self, new_mode: str) -> Dict[str, Any]:
        """Switch the control mode"""
        try:
            old_mode = self.config.control_mode.value
            self.config.control_mode = ControlMode(new_mode)

            print(f"[MODE] Switched from {old_mode} to {new_mode}")

            return {
                "success": True,
                "message": f"Control mode switched to {new_mode}",
                "old_mode": old_mode,
                "new_mode": new_mode,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _display_hybrid_status(self):
        """Display current hybrid rotation status"""
        print(f"\n[HYBRID STATUS] Control Mode: {self.config.control_mode.value}")
        print(f"Current Assets ({len(self.current_assets)}):")

        for asset_config in self.current_assets:
            asset = asset_config.symbol
            user_pref = self.user_preferences.get(asset)
            user_score = user_pref.preference_score if user_pref else 0.5

            avg_perf = 0.5
            if asset in self.auto_rotator.performance_history:
                history = self.auto_rotator.performance_history[asset]
                if history:
                    avg_perf = sum(history) / len(history)

            print(
                f"  {asset:<6} Perf: {avg_perf:.3f} User: {user_score:.3f} "
                f"{'LOCKED' if user_pref and user_pref.lock_until else 'FREE'}"
            )

        if self.active_suggestions:
            print(f"\n[PENDING SUGGESTIONS] {len(self.active_suggestions)}:")
            for i, suggestion in enumerate(self.active_suggestions):
                print(f"  {i}: {suggestion.reason} (conf: {suggestion.confidence:.2f})")

    def get_hybrid_status(self) -> Dict[str, Any]:
        """Get comprehensive hybrid system status"""
        return {
            "running": self.running,
            "control_mode": self.config.control_mode.value,
            "config": {
                "max_assets": self.config.max_assets,
                "auto_weight": self.config.auto_rotation_weight,
                "user_weight": self.config.user_preference_weight,
                "learning_enabled": self.config.learning_enabled,
            },
            "current_assets": [ac.symbol for ac in self.current_assets],
            "active_suggestions": [
                {
                    "id": i,
                    "action": s.action,
                    "assets": s.assets,
                    "confidence": s.confidence,
                    "reasoning": s.reasoning,
                    "expected_impact": s.expected_impact,
                }
                for i, s in enumerate(self.active_suggestions)
            ],
            "user_preferences": {
                symbol: {
                    "preference_score": pref.preference_score,
                    "weight_multiplier": pref.weight_multiplier,
                    "locked": pref.lock_until is not None and pref.lock_until > datetime.now(),
                    "tags": pref.tags,
                }
                for symbol, pref in self.user_preferences.items()
            },
            "metrics": self.hybrid_metrics,
            "timestamp": datetime.now().isoformat(),
        }

    def stop_hybrid_rotation(self):
        """Stop the hybrid rotation system"""
        print("[HYBRID] Stopping hybrid rotation system")
        self.running = False


if __name__ == "__main__":

    async def demo_hybrid_rotation():
        print("\n" + "=" * 80)
        print("[HYBRID ROTATION SYSTEM DEMO]")
        print("=" * 80)

        config = HybridConfig(
            control_mode=ControlMode.COLLABORATIVE,
            max_assets=6,
            auto_rotation_weight=0.6,
            user_preference_weight=0.4,
            learning_enabled=True,
        )

        hybrid_manager = HybridRotationManager(config)

        print("[DEMO] Starting hybrid rotation system (runs for 60 seconds)...")

        try:
            task = asyncio.create_task(hybrid_manager.start_hybrid_rotation())

            await asyncio.sleep(60)

            hybrid_manager.stop_hybrid_rotation()
            task.cancel()

            status = hybrid_manager.get_hybrid_status()
            print(f"\n[FINAL HYBRID STATUS]")
            print(f"  Control Mode: {status['control_mode']}")
            print(f"  Total Decisions: {status['metrics']['total_decisions']}")
            print(f"  User Decisions: {status['metrics']['user_decisions']}")
            print(f"  Auto Decisions: {status['metrics']['auto_decisions']}")
            print(f"  Collaborative Decisions: {status['metrics']['collaborative_decisions']}")
            print(f"  User Satisfaction: {status['metrics']['user_satisfaction']:.2f}")

        except KeyboardInterrupt:
            print("\n[INTERRUPTED] Stopping hybrid rotation...")
            hybrid_manager.stop_hybrid_rotation()

    asyncio.run(demo_hybrid_rotation())
