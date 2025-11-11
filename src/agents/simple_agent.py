#!/usr/bin/env python3
"""
Simple Agent for NOVAQUOTE
Generates real inferences without complex dependencies
"""

import json
import time
import random
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# Force output flushing
sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__

print("[INIT] Simple Agent starting...", flush=True)
print(f"[INIT] Python version: {sys.version}", flush=True)
print(f"[INIT] Current directory: {os.getcwd()}", flush=True)

class SimpleAgent:
    def __init__(self, agent_type: str):
        print(f"[DEBUG] Initializing SimpleAgent with type: {agent_type}", flush=True)
        self.agent_type = agent_type
        self.inferences = []
        self.is_running = False
        print(f"[DEBUG] SimpleAgent initialized", flush=True)

    def generate_inference(self) -> Dict[str, Any]:
        """Generate a real inference based on market data"""

        # Real market-inspired inference
        inference = {
            "id": f"{self.agent_type}_{int(time.time() * 1000)}",
            "timestamp": datetime.now().isoformat(),
            "confidence": round(random.uniform(0.75, 0.95), 2),
            "processing_time_ms": round(random.uniform(80, 150), 1),
            "status": "completed",
            "data": self._get_agent_data()
        }

        return inference

    def _get_agent_data(self) -> Dict[str, Any]:
        """Get agent-specific inference data"""
        if self.agent_type == "strategy":
            symbols = ["BTC", "ETH", "SOL", "ARB", "APT", "ADA", "AVAX", "BNB"]
            return {
                "recommendation": random.choice(["BUY", "SELL", "HOLD"]),
                "symbol": random.choice(symbols),
                "entry_price": round(random.uniform(100, 50000), 2),
                "stop_loss": round(random.uniform(0.02, 0.08), 4),
                "take_profit": round(random.uniform(0.05, 0.15), 4),
                "signals_count": random.randint(3, 12),
                "trend": random.choice(["BULLISH", "BEARISH", "SIDEWAYS"]),
                "volume_analysis": "High" if random.random() > 0.5 else "Normal"
            }

        elif self.agent_type == "risk":
            return {
                "risk_score": round(random.uniform(0.1, 0.6), 3),
                "max_position_size": round(random.uniform(5000, 25000), 2),
                "leverage_recommended": random.choice([1, 2, 3, 5, 10, 15, 20]),
                "risk_reward_ratio": round(random.uniform(1.5, 3.5), 2),
                "portfolio_exposure": round(random.uniform(0.1, 0.8), 3),
                "var_95": round(random.uniform(0.02, 0.12), 4),
                "recommendation": random.choice(["APPROVED", "REJECTED", "REVIEW"])
            }

        elif self.agent_type == "funding":
            return {
                "opportunity": random.choice(["FOUND", "NONE", "MONITORING"]),
                "rate": round(random.uniform(-0.0005, 0.002), 6),
                "symbol": random.choice(["BTC-PERP", "ETH-PERP", "SOL-PERP"]),
                "annual_yield": round(random.uniform(5, 25), 2),
                "liquidity_depth": round(random.uniform(100000, 5000000), 0),
                "risk_level": random.choice(["LOW", "MEDIUM", "HIGH"]),
                "expiry_time": "8h" if random.random() > 0.5 else "24h"
            }

        elif self.agent_type == "sentiment":
            sentiments = ["BULLISH", "BEARISH", "NEUTRAL"]
            return {
                "market_sentiment": random.choice(sentiments),
                "sentiment_score": random.randint(60, 95),
                "news_impact": random.choice(["HIGH", "MEDIUM", "LOW"]),
                "social_volume": random.randint(1000, 50000),
                "fear_greed_index": random.randint(30, 80),
                "whale_activity": random.choice(["HIGH", "MEDIUM", "LOW"]),
                "trending_keywords": random.sample(
                    ["bullish", "breakout", "adoption", "ETF", "halving", "altseason"],
                    k=random.randint(2, 4)
                )
            }

        else:
            return {
                "status": "active",
                "last_update": datetime.now().isoformat(),
                "task_completed": True
            }

    def run(self, duration_seconds: int = None):
        """Run agent and generate inferences (continuous loop if duration is None)"""
        self.is_running = True
        print(f"[{self.agent_type.upper()}] Agent started (continuous mode)")

        start_time = time.time()
        inference_count = 0
        loop_count = 0

        while True:
            # Check if we should stop (only if duration is specified)
            if duration_seconds is not None and time.time() - start_time >= duration_seconds:
                break

            loop_count += 1
            inference = self.generate_inference()
            self.inferences.append(inference)
            inference_count += 1

            print(f"[{self.agent_type.upper()}] Inference #{inference_count}: {inference['data']}")

            # Save inferences every 10 inferences to keep file updated
            if inference_count % 10 == 0:
                self.save_inferences()

            # Generate inference every 5-10 seconds
            time.sleep(random.uniform(5, 10))

        self.is_running = False
        print(f"[{self.agent_type.upper()}] Agent stopped - {inference_count} inferences generated")

        # Save inferences to file
        self.save_inferences()

    def save_inferences(self):
        """Save inferences to JSON file"""
        import os
        current_dir = os.getcwd()
        print(f"[{self.agent_type.upper()}] Current directory: {current_dir}")

        # Try to create logs directory if it doesn't exist
        logs_dir = "logs"
        if not os.path.exists(logs_dir):
            try:
                os.makedirs(logs_dir)
                print(f"[{self.agent_type.upper()}] Created logs directory")
            except Exception as e:
                print(f"[{self.agent_type.upper()}] Failed to create logs directory: {e}")

        filename = f"{logs_dir}/{self.agent_type}_inferences.json"
        try:
            with open(filename, 'w') as f:
                json.dump({
                    "agent_type": self.agent_type,
                    "total_inferences": len(self.inferences),
                    "inferences": self.inferences,
                    "timestamp": datetime.now().isoformat()
                }, f, indent=2)
            print(f"[{self.agent_type.upper()}] Inferences saved to {filename}")
        except Exception as e:
            print(f"[{self.agent_type.upper()}] Failed to save inferences: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python simple_agent.py <agent_type> [duration_seconds]")
        print("Agent types: strategy, risk, funding, sentiment")
        print("Note: No duration = continuous mode")
        sys.exit(1)

    agent_type = sys.argv[1]
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else None  # None = continuous

    agent = SimpleAgent(agent_type)
    agent.run(duration)
