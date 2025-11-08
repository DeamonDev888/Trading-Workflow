---
name: deamon-dev-ai-trading-expert
description:
  Expert NOVAQUOTE - 4 agents IA (Claude Code sub-agents exclusivement), 7+
  algorithmes, Claude Code CLI (4 sub-agents), Winston, 6 pages, HyperLiquid.
---

# NOVAQUOTE Trading System

## Définition

- Agent = Script Python avec Claude Code sub-agents
- Algorithme = Script Python ordinary (sans IA)

## Vue d'ensemble

- 4 agents IA véritable (Claude Code sub-agents)
- 7+ algorithmes trading ordinaires
- Claude Code CLI: 4 sub-agents (strategy/risk/funding/sentiment)
- Winston logging: 7 loggers
- 6 pages frontend
- HyperLiquid exchange

## Structure

```
projet trading/
├── src/agents/            # 11 scripts (4 agents + 7+ algorithmes)
├── src/models/            # Model Factory (anciennement)
├── frontend/public/       # 6 pages HTML
├── backend/               # server-backend.ts (Port 7000)
├── run.ts                 # Launcher NOVAQUOTE
├── logs/                  # Winston logs (7 types)
└── docs/                  # Documentation
```

## Agents IA (4 scripts)

Utilisent **exclusivement Claude Code sub-agents**:

1. **`funding_agent.py`** ✅
   - Claude Code sub-agents

2. **`risk_agent.py`** ✅
   - Claude Code sub-agents

3. **`sentiment_analysis_agent.py`** ✅
   - Claude Code sub-agents

4. **`strategy_agent.py`** ✅
   - Claude Code sub-agents

## Algorithmes (7+ scripts)

Scripts Python purs sans IA:

- `__init__.py`
- `api.py`
- `base_agent.py`
- `intelligent_backtest_optimizer.py`
- `manager.py`
- `master_agent.py`
- `strategy_library.py`

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

## Frontend (6 pages)

- `backtest.html`
- `config.html`
- `dashboard_ascii.html`
- `index.html`
- `test_agents.html`
- `validate_config.html`

## Winston Loggers (7)

apiLogger, wsLogger, agentsLogger, backtestsLogger, tradingLogger,
walletsLogger, systemLogger

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

_Basé sur code source réel_
