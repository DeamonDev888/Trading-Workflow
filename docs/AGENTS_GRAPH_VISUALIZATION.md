# Agents IA - Fonctionnement Réel

## Vue d'ensemble (4 agents)

```mermaid
graph TD
    A[Déclencheur] --> B{Risk Agent}
    A --> C{Strategy Agent}
    A --> D{Funding Agent}
    A --> E{Sentiment Agent}

    B --> B1[Appel: claude-risk-advisor]
    C --> C1[Appel: claude-strategy-advisor]
    D --> D1[Appel: claude-funding-advisor]
    E --> E1[Appel: claude-sentiment-advisor]

    B1 --> F[HyperLiquid API]
    C1 --> F
    D1 --> F
    E1 --> F

    F --> G[Position Management]
    G --> H[Winston Logging]
```

## Pattern Technique

```python
def call_subagent(self, prompt, context_data=None):
    cmd = ["claude", "--dangerously-skip-permissions", "--agent", self.subagent_name, prompt]
    return subprocess.run(cmd, timeout=120).stdout
```

## Architecture

Market Data → Claude Sub-Agents → Strategy Library → Order Execution

## Métriques

- **funding_agent.py**: Sub-agent claude-funding-advisor
- **risk_agent.py**: Sub-agent claude-risk-advisor
- **sentiment_analysis_agent.py**: Sub-agent claude-sentiment_analysis-advisor
- **strategy_agent.py**: Sub-agent claude-strategy-advisor

---

_Claude Code sub-agents exclusivement_
