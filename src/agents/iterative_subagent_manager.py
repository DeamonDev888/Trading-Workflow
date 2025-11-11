"""
[OK] Iterative Subagent Manager
Advanced multi-iteration system for Claude Code subagents
Built with love by Deamon Dev [ROCKET]

Progressive refinement, cross-validation, and adaptive learning for trading decisions.
"""

import json
import os
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class IterationMode(Enum):
    """Different iteration strategies for subagents"""

    PROGRESSIVE_REFINEMENT = "progressive_refinement"
    CROSS_VALIDATION = "cross_validation"
    CONVERGENCE_SEEKING = "convergence_seeking"
    MAJORITY_VOTING = "majority_voting"
    ADAPTIVE_LEARNING = "adaptive_learning"


@dataclass
class IterationConfig:
    """Configuration for iteration strategies"""

    max_iterations: int = 3
    confidence_threshold: float = 0.85
    timeout_per_iteration: int = 120
    convergence_threshold: float = 0.9
    diversity_requirement: bool = True
    learning_rate: float = 0.1


@dataclass
class SubagentResponse:
    """Structure for subagent responses"""

    iteration: int
    response: str
    confidence: float
    reasoning: str
    metadata: Dict[str, Any]
    timestamp: datetime
    execution_time: float


@dataclass
class IterationSession:
    """Complete iteration session with all responses"""

    session_id: str
    mode: IterationMode
    config: IterationConfig
    responses: List[SubagentResponse]
    final_result: Optional[Dict[str, Any]]
    convergence_metrics: Dict[str, float]
    total_time: float


class IterativeSubagentManager:
    """Advanced manager for multi-iteration subagent calls"""

    def __init__(self, default_config: Optional[IterationConfig] = None):
        self.config = default_config or IterationConfig()
        self.session_history: List[IterationSession] = []
        self.performance_metrics = {
            "total_sessions": 0,
            "average_iterations": 0,
            "convergence_rate": 0,
            "confidence_improvement": 0,
        }

    def call_subagent_iteration(
        self,
        prompt: str,
        context_data: dict = None,
        mode: IterationMode = IterationMode.PROGRESSIVE_REFINEMENT,
        config: Optional[IterationConfig] = None,
    ) -> IterationSession:
        """
        Execute multiple subagent iterations based on the specified mode

        Args:
            prompt: Initial prompt for the subagent
            context_data: Context data for the subagent
            mode: Iteration strategy to use
            config: Custom configuration (overrides default)

        Returns:
            Complete iteration session with all responses
        """
        session_config = config or self.config
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        session = IterationSession(
            session_id=session_id,
            mode=mode,
            config=session_config,
            responses=[],
            final_result=None,
            convergence_metrics={},
            total_time=0,
        )

        start_time = time.time()

        try:
            if mode == IterationMode.PROGRESSIVE_REFINEMENT:
                session = self._progressive_refinement(prompt, context_data, session)
            elif mode == IterationMode.CROSS_VALIDATION:
                session = self._cross_validation(prompt, context_data, session)
            elif mode == IterationMode.CONVERGENCE_SEEKING:
                session = self._convergence_seeking(prompt, context_data, session)
            elif mode == IterationMode.MAJORITY_VOTING:
                session = self._majority_voting(prompt, context_data, session)
            elif mode == IterationMode.ADAPTIVE_LEARNING:
                session = self._adaptive_learning(prompt, context_data, session)

            session.convergence_metrics = self._calculate_convergence_metrics(session.responses)

            session.final_result = self._generate_final_result(session)

        except Exception as e:
            print(f"[ERROR] Iteration session {session_id} failed: {e}")
            session.final_result = {
                "error": str(e),
                "fallback_mode": True,
                "last_response": (session.responses[-1].response if session.responses else None),
            }

        session.total_time = time.time() - start_time

        self.session_history.append(session)
        self._update_performance_metrics(session)

        return session

    def _progressive_refinement(
        self, prompt: str, context_data: dict, session: IterationSession
    ) -> IterationSession:
        """Progressive refinement: each iteration builds on the previous one"""
        current_prompt = prompt
        accumulated_context = context_data.copy() if context_data else {}

        for iteration in range(1, session.config.max_iterations + 1):
            print(
                f"[ITERATION {iteration}/{session.config.max_iterations}] Progressive refinement..."
            )

            if session.responses:
                accumulated_context["previous_responses"] = [
                    {
                        "iteration": r.iteration,
                        "response": r.response,
                        "confidence": r.confidence,
                    }
                    for r in session.responses
                ]
                accumulated_context["refinement_needed"] = True

            response = self._make_subagent_call(
                current_prompt, accumulated_context, iteration, session.config
            )
            session.responses.append(response)

            if response.confidence >= session.config.confidence_threshold:
                print(f"[CONVERGED] Confidence threshold reached: {response.confidence:.2f}")
                break

            if iteration < session.config.max_iterations:
                current_prompt = self._create_refinement_prompt(response, accumulated_context)

        return session

    def _cross_validation(
        self, prompt: str, context_data: dict, session: IterationSession
    ) -> IterationSession:
        """Cross-validation: multiple independent analyses for validation"""
        perspectives = [
            {"focus": "technical_analysis", "priority": "indicators"},
            {"focus": "risk_management", "priority": "safety"},
            {"focus": "market_conditions", "priority": "context"},
            {"focus": "liquidity_analysis", "priority": "execution"},
        ]

        for i, perspective in enumerate(perspectives[: session.config.max_iterations]):
            print(
                f"[VALIDATION {i+1}/{len(perspectives)}] Cross-validation: {perspective['focus']}"
            )

            validation_context = context_data.copy() if context_data else {}
            validation_context.update(perspective)

            validation_prompt = f"""
            Analyze this from a {perspective['focus']} perspective:

            Original Request: {prompt}

            Priority: {perspective['priority']}

            Please provide your analysis and confidence score (0-1).
            """

            response = self._make_subagent_call(
                validation_prompt, validation_context, i + 1, session.config
            )
            response.metadata["perspective"] = perspective["focus"]
            session.responses.append(response)

        return session

    def _convergence_seeking(
        self, prompt: str, context_data: dict, session: IterationSession
    ) -> IterationSession:
        """Convergence seeking: iterate until responses converge"""
        previous_response = None

        for iteration in range(1, session.config.max_iterations + 1):
            print(f"[CONVERGENCE {iteration}] Seeking stable response...")

            convergence_context = context_data.copy() if context_data else {}
            if previous_response:
                convergence_context["previous_response"] = previous_response.response
                convergence_context["convergence_target"] = session.config.convergence_threshold

            response = self._make_subagent_call(
                prompt, convergence_context, iteration, session.config
            )
            session.responses.append(response)

            if previous_response:
                similarity = self._calculate_response_similarity(response, previous_response)
                if similarity >= session.config.convergence_threshold:
                    print(f"[CONVERGED] Response stability achieved: {similarity:.2f}")
                    break

            previous_response = response

        return session

    def _majority_voting(
        self, prompt: str, context_data: dict, session: IterationSession
    ) -> IterationSession:
        """Majority voting: get multiple independent opinions and vote"""
        votes = {}

        for iteration in range(1, session.config.max_iterations + 1):
            print(f"[VOTE {iteration}] Collecting independent opinion...")

            vote_context = context_data.copy() if context_data else {}
            vote_context["vote_number"] = iteration
            vote_context["independent_analysis"] = True

            vote_prompt = f"""
            Independent analysis {iteration}:

            {prompt}

            Please provide your definitive recommendation and confidence (0-1).
            Be decisive and clear in your response.
            """

            response = self._make_subagent_call(
                vote_prompt, vote_context, iteration, session.config
            )
            session.responses.append(response)

            decision = self._extract_decision(response.response)
            if decision not in votes:
                votes[decision] = []
            votes[decision].append(response.confidence)

        session.final_result = {
            "voting_results": votes,
            "majority_decision": max(votes.keys(), key=lambda k: len(votes[k])),
            "vote_distribution": {k: len(v) for k, v in votes.items()},
        }

        return session

    def _adaptive_learning(
        self, prompt: str, context_data: dict, session: IterationSession
    ) -> IterationSession:
        """Adaptive learning: use historical performance to guide iterations"""
        relevant_history = self._get_relevant_history(prompt, context_data)

        current_prompt = prompt
        learning_context = context_data.copy() if context_data else {}

        for iteration in range(1, session.config.max_iterations + 1):
            print(f"[LEARNING {iteration}] Adaptive learning iteration...")

            if relevant_history:
                learning_context["historical_performance"] = relevant_history[
                    :3
                ]  # Top 3 most relevant
                learning_context["learning_rate"] = session.config.learning_rate

            response = self._make_subagent_call(
                current_prompt, learning_context, iteration, session.config
            )
            session.responses.append(response)

            if iteration < session.config.max_iterations:
                refinement = self._generate_adaptive_refinement(response, relevant_history)
                if refinement:
                    current_prompt = f"""
                    Previous analysis: {response.response}

                    Adaptive refinement suggestion: {refinement}

                    Please refine your analysis considering this suggestion.
                    """

        return session

    def _make_subagent_call(
        self, prompt: str, context_data: dict, iteration: int, config: IterationConfig
    ) -> SubagentResponse:
        """Make a single subagent call with timing and error handling"""
        start_time = time.time()

        try:
            full_prompt = f"""
            Iteration {iteration} Analysis Request:

            {prompt}

            Context Data:
            {json.dumps(context_data, indent=2) if context_data else 'N/A'}

            Please provide:
            1. Your analysis/response
            2. Confidence score (0-1)
            3. Reasoning/justification

            Format your response clearly with confidence score at the end.
            """

            cmd = [
                "claude",
                "--dangerously-skip-permissions",
                "--agent",
                "Deamon-strategy-advisor",
                full_prompt,
            ]

            print(f"[SUBAGENT] Calling Deamon-strategy-advisor (iteration {iteration})")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=config.timeout_per_iteration,
                cwd=os.getcwd(),
            )

            if result.returncode != 0:
                error_msg = f"[ERROR] Sub-agent error: {result.stderr}"
                print(error_msg)
                return SubagentResponse(
                    iteration=iteration,
                    response=f"Error: {result.stderr}",
                    confidence=0.0,
                    reasoning="Subagent call failed",
                    metadata={"error": True, "stderr": result.stderr},
                    timestamp=datetime.now(),
                    execution_time=time.time() - start_time,
                )

            response_text = result.stdout
            confidence = self._extract_confidence(response_text)
            reasoning = self._extract_reasoning(response_text)

            print(f"[SUBAGENT] Response received (confidence: {confidence:.2f})")

            return SubagentResponse(
                iteration=iteration,
                response=response_text,
                confidence=confidence,
                reasoning=reasoning,
                metadata={"success": True, "raw_output": result.stdout},
                timestamp=datetime.now(),
                execution_time=time.time() - start_time,
            )

        except subprocess.TimeoutExpired:
            print(f"[ERROR] Subagent timeout after {config.timeout_per_iteration}s")
            return SubagentResponse(
                iteration=iteration,
                response="Timeout: Subagent took too long to respond",
                confidence=0.0,
                reasoning="Timeout error",
                metadata={"error": True, "timeout": True},
                timestamp=datetime.now(),
                execution_time=config.timeout_per_iteration,
            )
        except Exception as e:
            print(f"[ERROR] Unexpected error in subagent call: {e}")
            return SubagentResponse(
                iteration=iteration,
                response=f"Error: {str(e)}",
                confidence=0.0,
                reasoning="Unexpected error",
                metadata={"error": True, "exception": str(e)},
                timestamp=datetime.now(),
                execution_time=time.time() - start_time,
            )

    def _extract_confidence(self, response: str) -> float:
        """Extract confidence score from response text"""
        import re

        patterns = [
            r"confidence[:\s]*(\d+\.?\d*)",
            r"confident[:\s]*(\d+\.?\d*)",
            r"score[:\s]*(\d+\.?\d*)",
            r"(\d+\.?\d*)\s*%?\s*confident",
        ]

        for pattern in patterns:
            match = re.search(pattern, response.lower())
            if match:
                try:
                    confidence = float(match.group(1))
                    if confidence > 1:
                        confidence = confidence / 100
                    return min(1.0, max(0.0, confidence))
                except ValueError:
                    continue

        return 0.5

    def _extract_reasoning(self, response: str) -> str:
        """Extract reasoning from response text"""
        lines = response.split("\n")
        reasoning_lines = []

        for line in lines:
            if any(
                keyword in line.lower()
                for keyword in ["reason", "because", "since", "due to", "analysis"]
            ):
                reasoning_lines.append(line.strip())

        return "\n".join(reasoning_lines) if reasoning_lines else response[:200]

    def _extract_decision(self, response: str) -> str:
        """Extract main decision from response (simplified)"""
        response_lower = response.lower()

        if "buy" in response_lower and "sell" not in response_lower:
            return "BUY"
        elif "sell" in response_lower and "buy" not in response_lower:
            return "SELL"
        elif "execute" in response_lower:
            return "EXECUTE"
        elif "reject" in response_lower or "avoid" in response_lower:
            return "REJECT"
        else:
            return "NEUTRAL"

    def _calculate_response_similarity(
        self, response1: SubagentResponse, response2: SubagentResponse
    ) -> float:
        """Calculate similarity between two responses"""
        confidence_similarity = 1 - abs(response1.confidence - response2.confidence)

        decision1 = self._extract_decision(response1.response)
        decision2 = self._extract_decision(response2.response)
        decision_similarity = 1.0 if decision1 == decision2 else 0.0

        return confidence_similarity * 0.4 + decision_similarity * 0.6

    def _create_refinement_prompt(self, response: SubagentResponse, context: dict) -> str:
        """Create a refinement prompt based on previous response"""
        return f"""
        Please refine your previous analysis:

        Previous Response (Confidence: {response.confidence:.2f}):
        {response.response}

        The confidence level needs improvement. Please:
        1. Reconsider your analysis with additional context
        2. Provide more detailed reasoning
        3. Increase your confidence if justified, or explain why uncertainty remains

        Additional Context: {json.dumps(context, indent=2)}
        """

    def _get_relevant_history(self, prompt: str, context_data: dict) -> List[Dict]:
        """Get relevant historical sessions for adaptive learning"""
        relevant_sessions = []

        for session in self.session_history[-10:]:  # Last 10 sessions
            if any(word in prompt.lower() for word in ["trading", "strategy", "signal"]):
                relevant_sessions.append(
                    {
                        "mode": session.mode.value,
                        "success": (
                            session.final_result.get("error") is None
                            if session.final_result
                            else True
                        ),
                        "iterations": len(session.responses),
                        "final_confidence": (
                            session.responses[-1].confidence if session.responses else 0
                        ),
                        "convergence_score": session.convergence_metrics.get("stability", 0),
                    }
                )

        return sorted(relevant_sessions, key=lambda x: x["final_confidence"], reverse=True)

    def _generate_adaptive_refinement(
        self, response: SubagentResponse, history: List[Dict]
    ) -> Optional[str]:
        """Generate adaptive refinement based on historical performance"""
        if not history:
            return None

        avg_confidence = sum(h["final_confidence"] for h in history) / len(history)

        if response.confidence < avg_confidence:
            return "Consider additional factors that may have been overlooked in previous similar analyses."

        return None

    def _calculate_convergence_metrics(self, responses: List[SubagentResponse]) -> Dict[str, float]:
        """Calculate various convergence metrics"""
        if len(responses) < 2:
            return {"stability": 1.0, "confidence_trend": 0.0, "consistency": 1.0}

        stability_scores = []
        for i in range(1, len(responses)):
            similarity = self._calculate_response_similarity(responses[i], responses[i - 1])
            stability_scores.append(similarity)

        stability = sum(stability_scores) / len(stability_scores) if stability_scores else 1.0

        confidence_trend = responses[-1].confidence - responses[0].confidence

        confidences = [r.confidence for r in responses]
        avg_confidence = sum(confidences) / len(confidences)
        variance = sum((c - avg_confidence) ** 2 for c in confidences) / len(confidences)
        consistency = 1 - min(1.0, variance)

        return {
            "stability": stability,
            "confidence_trend": confidence_trend,
            "consistency": consistency,
            "final_confidence": responses[-1].confidence if responses else 0,
            "iterations_used": len(responses),
        }

    def _generate_final_result(self, session: IterationSession) -> Dict[str, Any]:
        """Generate the final result from all iterations"""
        if session.final_result and "error" in session.final_result:
            return session.final_result

        last_response = session.responses[-1] if session.responses else None

        if not last_response:
            return {"error": "No valid responses received"}

        return {
            "final_decision": self._extract_decision(last_response.response),
            "final_confidence": last_response.confidence,
            "final_reasoning": last_response.reasoning,
            "iterations_used": len(session.responses),
            "convergence_metrics": session.convergence_metrics,
            "session_mode": session.mode.value,
            "recommended_action": (
                "EXECUTE"
                if last_response.confidence >= session.config.confidence_threshold
                else "REVIEW"
            ),
            "all_responses": [
                {
                    "iteration": r.iteration,
                    "confidence": r.confidence,
                    "decision": self._extract_decision(r.response),
                }
                for r in session.responses
            ],
        }

    def _update_performance_metrics(self, session: IterationSession):
        """Update overall performance metrics"""
        self.performance_metrics["total_sessions"] += 1

        if session.responses:
            self.performance_metrics["average_iterations"] = (
                self.performance_metrics["average_iterations"]
                * (self.performance_metrics["total_sessions"] - 1)
                + len(session.responses)
            ) / self.performance_metrics["total_sessions"]

            if session.convergence_metrics.get("stability", 0) > 0.8:
                self.performance_metrics["convergence_rate"] = (
                    self.performance_metrics["convergence_rate"]
                    * (self.performance_metrics["total_sessions"] - 1)
                    + 1
                ) / self.performance_metrics["total_sessions"]

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get summary of performance metrics"""
        return {
            "performance_metrics": self.performance_metrics,
            "recent_sessions": [
                {
                    "session_id": s.session_id,
                    "mode": s.mode.value,
                    "iterations": len(s.responses),
                    "final_confidence": (s.responses[-1].confidence if s.responses else 0),
                    "converged": s.convergence_metrics.get("stability", 0) > 0.8,
                }
                for s in self.session_history[-5:]
            ],
            "recommendations": self._generate_performance_recommendations(),
        }

    def _generate_performance_recommendations(self) -> List[str]:
        """Generate recommendations based on performance"""
        recommendations = []

        if self.performance_metrics["average_iterations"] > 2.5:
            recommendations.append("Consider increasing confidence threshold to reduce iterations")

        if self.performance_metrics["convergence_rate"] < 0.7:
            recommendations.append("Try cross-validation mode for better convergence")

        if self.performance_metrics["confidence_improvement"] < 0.1:
            recommendations.append("Prompts may need refinement for better confidence progression")

        return recommendations


def progressive_refinement_call(
    prompt: str, context_data: dict = None, max_iterations: int = 3
) -> IterationSession:
    """Quick progressive refinement call"""
    manager = IterativeSubagentManager()
    config = IterationConfig(max_iterations=max_iterations)
    return manager.call_subagent_iteration(
        prompt, context_data, IterationMode.PROGRESSIVE_REFINEMENT, config
    )


def cross_validation_call(
    prompt: str, context_data: dict = None, perspectives: List[str] = None
) -> IterationSession:
    """Quick cross-validation call"""
    manager = IterativeSubagentManager()
    config = IterationConfig(max_iterations=len(perspectives) if perspectives else 4)
    return manager.call_subagent_iteration(
        prompt, context_data, IterationMode.CROSS_VALIDATION, config
    )


def convergence_call(
    prompt: str, context_data: dict = None, convergence_threshold: float = 0.9
) -> IterationSession:
    """Quick convergence-seeking call"""
    manager = IterativeSubagentManager()
    config = IterationConfig(convergence_threshold=convergence_threshold)
    return manager.call_subagent_iteration(
        prompt, context_data, IterationMode.CONVERGENCE_SEEKING, config
    )


if __name__ == "__main__":

    def test_progressive_refinement():
        print("Testing Progressive Refinement...")

        session = progressive_refinement_call(
            "Analyze this trading signal: BUY BTC at $45000 with 0.8 strength",
            {"price": 45000, "strength": 0.8, "symbol": "BTC"},
            max_iterations=3,
        )

        print(f"Final decision: {session.final_result.get('final_decision')}")
        print(f"Final confidence: {session.final_result.get('final_confidence'):.2f}")
        print(f"Iterations used: {session.final_result.get('iterations_used')}")

        return session

    def test_cross_validation():
        print("\nTesting Cross-Validation...")

        session = cross_validation_call(
            "Evaluate this trading strategy: RSI-based reversal",
            {"strategy": "RSI_reversal", "timeframe": "1h"},
        )

        print(f"Final decision: {session.final_result.get('final_decision')}")
        print(f"Convergence metrics: {session.convergence_metrics}")

        return session

    test_progressive_refinement()
    test_cross_validation()
