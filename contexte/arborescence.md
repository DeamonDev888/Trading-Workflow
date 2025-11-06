projet trading/
├── .gitignore
├── backend/
│   ├── backtest_validator.js
│   ├── server-backend.js
│   └── server-backend.ts
├── context.md
├── contexte/
│   ├── arborescence.md
│   └── context_app.md
├── docs/
│   ├── AGENTS_GRAPH_VISUALIZATION.md
│   ├── CIRCULAR_SYSTEM_GUIDE.md
│   ├── HYPERLIQUID_API_DOCUMENTATION.md
│   └── LOG_SYSTEM_DOCUMENTATION.md
├── frontend/
│   ├── public/
│   │   ├── assets/
│   │   │   └── novaquote.css
│   │   ├── backtest.html
│   │   ├── config.html
│   │   ├── dashboard_ascii.html
│   │   ├── index.html
│   │   ├── test_agents.html
│   │   └── validate_config.html
│   └── server-frontend.ts
├── package-lock.json
├── package.json
├── README.md
├── requirements.txt
├── run.ts
├── scripts/
│   ├── generate_context.py
│   ├── lint-format-py.py
│   ├── optimize_all_strategies.py
│   ├── project_snapshot.py
│   └── test_circular_system.py
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── api.py
│   │   ├── base_agent.py
│   │   ├── funding_agent.py
│   │   ├── intelligent_backtest_optimizer.py
│   │   ├── manager.py
│   │   ├── master_agent.py
│   │   ├── risk_agent.py
│   │   ├── sentiment_analysis_agent.py
│   │   ├── strategy_agent.py
│   │   └── strategy_library.py
│   ├── algorithms/
│   │   ├── funding_agent.py
│   │   ├── hyperliquid_agent.py
│   │   ├── hyperliquid_mainnet_agent.py
│   │   ├── portfolio_manager.py
│   │   ├── real_funding_agent.py
│   │   ├── real_market_agent.py
│   │   ├── real_risk_agent.py
│   │   └── risk_agent.py
│   ├── config.py
│   ├── core/
│   │   ├── circuit-breaker.ts
│   │   ├── retry-manager.ts
│   │   └── websocket-manager.ts
│   ├── data/
│   │   ├── metrics_collector.py
│   │   ├── production_backtests/
│   │   │   ├── BB_Squeeze_62_PRO_FINAL_results.json
│   │   │   ├── BTCDominance_FINAL.py
│   │   │   ├── DivergentVolReversal_FINAL.py
│   │   │   ├── Fear_Contrarian_73_PRO_FINAL_results.json
│   │   │   ├── FractalCascade_FINAL.py
│   │   │   ├── Funding_Arbitrage_85_PRO_FINAL_results.json
│   │   │   ├── GoldenCrossover_FINAL.py
│   │   │   ├── MACD_Crossover_65_PRO_FINAL_results.json
│   │   │   ├── README.md
│   │   │   ├── RSI_Oversold_68_PRO_FINAL_results.json
│   │   │   ├── Twitter_Sentiment_69_PRO_FINAL_results.json
│   │   │   ├── VolatilityEngulfing_FINAL.py
│   │   │   └── Volume_Breakout_71_PRO_FINAL_results.json
│   │   └── realtime_backtester.py
│   ├── health/
│   │   └── health-checker.ts
│   ├── hyperliquid/
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── hyperliquid-api.js
│   │   ├── hyperliquid-signature.js
│   │   ├── hyperliquid-websocket.js
│   │   ├── signing.py
│   │   ├── types.py
│   │   └── websocket.py
│   ├── logging/
│   │   ├── structured-logger.js
│   │   └── structured-logger.ts
│   ├── metrics/
│   │   └── prometheus.ts
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base_model.py
│   │   ├── claude_model.py
│   │   ├── deepseek_model.py
│   │   ├── gemini_model.py
│   │   ├── groq_model.py
│   │   ├── model_factory.py
│   │   ├── ollama_model.py
│   │   ├── openai_model.py
│   │   ├── xai_model.py
│   │   └── zai_model.py
│   ├── nice_funcs.py
│   ├── security/
│   │   ├── rate-limiter.ts
│   │   └── security-headers.ts
│   ├── validation/
│   │   └── schemas.ts
│   └── wallet/
│       ├── __init__.py
│       ├── api_wallet_manager.py
│       ├── permission_controller.py
│       ├── signature_engine.py
│       └── wallet_registry.py
├── tests/
│   ├── README.md
│   ├── run-all-tests.js
│   ├── test-structured-logger.js
│   └── test-system.js
└── tsconfig.json

ignore:
  - logs/
  - node_modules/
  - src\cache/
  - src\hyperliquid\__pycache__/
  - src\wallet\__pycache__/
  - tests\logs/