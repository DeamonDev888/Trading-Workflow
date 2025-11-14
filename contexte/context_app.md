---
name: deamon-dev-ai-trading-expert
description: Expert NOVAQUOTE - 13 agents IA (Claude Code sub-agents exclusivement), 19+ algorithmes, Claude Code CLI (4 sub-agents), Winston, 5 pages, HyperLiquid.
---

# NOVAQUOTE Trading System

## Définition
- Agent = Script Python avec Claude Code sub-agents
- Algorithme = Script Python ordinary (sans IA)

## Vue d'ensemble
- 13 agents IA véritable (Claude Code sub-agents)
- 19+ algorithmes trading ordinaires
- Claude Code CLI: 4 sub-agents (strategy/risk/funding/sentiment)
- Winston logging: 7 loggers
- 5 pages frontend
- HyperLiquid exchange

## Structure
```
projet trading/
├── src/agents/            # 32 scripts (13 agents + 19+ algorithmes)
├── src/models/            # Model Factory (anciennement)
├── frontend/public/       # 5 pages HTML
├── backend/               # server-backend.ts (Port 7000)
├── run.ts                 # Launcher NOVAQUOTE
├── logs/                  # Winston logs (7 types)
└── docs/                  # Documentation
```

## Agents IA (13 scripts)
Utilisent **exclusivement Claude Code sub-agents**:

1. **`advanced_risk_agent.py`** ✅
   - Claude Code sub-agents

2. **`agent_manager.py`** ✅
   - Claude Code sub-agents

3. **`claude_code_integration.py`** ✅
   - Claude Code sub-agents

4. **`claude_code_orchestrator.py`** ✅
   - Claude Code sub-agents

5. **`data_aggregator.py`** ✅
   - Claude Code sub-agents

6. **`funding_agent.py`** ✅
   - Claude Code sub-agents

7. **`iterative_subagent_manager.py`** ✅
   - Claude Code sub-agents

8. **`persistent_agent_orchestrator.py`** ✅
   - Claude Code sub-agents

9. **`reliability_monitor.py`** ✅
   - Claude Code sub-agents

10. **`risk_agent.py`** ✅
   - Claude Code sub-agents

11. **`risk_agent_enhanced.py`** ✅
   - Claude Code sub-agents

12. **`sentiment_analysis_agent.py`** ✅
   - Claude Code sub-agents

13. **`strategy_agent.py`** ✅
   - Claude Code sub-agents

## Algorithmes (19+ scripts)
Scripts Python purs sans IA:

- `__init__.py`
- `agent_inference_monitor.py`
- `api.py`
- `automatic_coin_rotator.py`
- `base_agent.py`
- `coin_rotation_integration.py`
- `coin_rotation_manager.py`
- `hybrid_rotation_api.py`
- `hybrid_rotation_system.py`
- `intelligent_backtest_optimizer.py`
- `liquidity_tracker.py`
- `manager.py`
- `master_agent.py`
- `master_agent_logger.py`
- `persistent_agent_client.py`
- `rotation_interface.py`
- `simple_agent.py`
- `strategy_library.py`
- `volatility_tracker.py`

## Pattern Claude Code
```python
def call_subagent(self, prompt: str, context_data: dict = None) -> str:
    cmd = ["claude", "--dangerously-skip-permissions", "--agent", self.subagent_name, full_prompt]
    return subprocess.run(cmd, timeout=120).stdout
```

## Sub-agents
- claude-strategy-advisor - Analyse technique
- claude-risk-advisor - Gestion risque
- claude-funding-advisor - Funding rates
- claude-sentiment-advisor - Sentiment analyse

## Frontend (5 pages)
- `backtest.html`
- `config.html`
- `index.html`
- `test_agents.html`
- `test_claude_agents.html`

## Winston Loggers (7)
apiLogger, wsLogger, agentsLogger, backtestsLogger, tradingLogger, walletsLogger, systemLogger

## API HyperLiquid
- get_all_mids(), get_meta(), get_user_state()
- place_order(), cancel_order()
- get_positions(), get_open_orders()

## Documentation Agents
- docs/agents/README.md - Vue d'ensemble et architecture
- docs/agents/index.md - Index des agents
- docs/agents/risk-agent.md - Risk Agent
- docs/agents/strategy-agent.md - Strategy Agent
- docs/agents/funding-agent.md - Funding Agent
- docs/agents/sentiment-agent.md - Sentiment Agent

## Launcher
run.ts: `ts-node run.ts start|stop|restart|test`
- Backend (Port 7000)
- Frontend (Port 9001)
- WebSocket (Port 7001)

---
*Basé sur code source réel*