"""
[OK] Deamon Dev's AI Agents Module
Built with love by Deamon Dev [ROCKET]

This module contains ONLY scripts that make LLM API calls.
These are the 4 true AI agents in the system.

[ALERT] IMPORTANT: This module contains ONLY agents with LLM API calls
🔹 risk_agent.py - Risk management with Claude/DeepSeek
🔹 funding_agent.py - Funding monitoring with Claude/DeepSeek
🔹 strategy_agent.py - Strategy generation with Claude
🔹 sentiment_analysis_agent.py - Sentiment analysis with OpenAI TTS
"""

__version__ = "1.0.0"
__author__ = "Deamon Dev"

from .funding_agent import FundingAgent
from .risk_agent import RiskAgent
from .sentiment_analysis_agent import SentimentAnalysisAgent
from .strategy_agent import StrategyAgent

AI_AGENTS = {
    "risk_agent": RiskAgent,
    "funding_agent": FundingAgent,
    "strategy_agent": StrategyAgent,
    "sentiment_analysis_agent": SentimentAnalysisAgent,
}

__all__ = [
    "RiskAgent",
    "FundingAgent",
    "StrategyAgent",
    "SentimentAnalysisAgent",
    "AI_AGENTS",
]
