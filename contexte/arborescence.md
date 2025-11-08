projet trading/
├── .gitignore
├── backend/
│   ├── backtest_validator.js
│   ├── server-backend.js
│   └── server-backend.ts
├── contexte/
│   ├── arborescence.md
│   └── context_app.md
├── docs/
│   ├── agents/
│   │   ├── funding-agent.md
│   │   ├── index.md
│   │   ├── README.md
│   │   ├── risk-agent.md
│   │   ├── sentiment-agent.md
│   │   └── strategy-agent.md
│   ├── AGENTS_GRAPH_VISUALIZATION.md
│   ├── ARCHITECTURE_DIAGRAMS.md
│   ├── CIRCULAR_SYSTEM_GUIDE.md
│   ├── HYPERLIQUID_API_DOCUMENTATION.md
│   └── LOG_SYSTEM_DOCUMENTATION.md
├── eslint.config.js
├── frontend/
│   ├── public/
│   │   ├── assets/
│   │   │   └── novaquote.css
│   │   ├── backtest.html
│   │   ├── config.html
│   │   ├── dashboard_ascii.html
│   │   ├── data/
│   │   │   └── production_backtests/
│   │   │       └── BTCDominance_FINAL_results_improved.json
│   │   ├── index.html
│   │   ├── portfolio-manager.js
│   │   ├── test_agents.html
│   │   └── validate_config.html
│   └── server-frontend.ts
├── package-lock.json
├── package.json
├── README.md
├── run.ts
├── scripts/
│   ├── auto_bug_fixer_cli.py
│   ├── CLAUDE_AUTO_LINTER.py
│   ├── fix_emojis.py
│   ├── generate_context.py
│   ├── lint-format-py.py
│   ├── optimize_all_strategies.py
│   ├── project_snapshot.py
│   └── test_circular_system.py
├── src/
│   ├── __init__.py
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
│   │   ├── __init__.py
│   │   ├── funding_agent.py
│   │   ├── hyperliquid_agent.py
│   │   ├── hyperliquid_mainnet_agent.py
│   │   ├── portfolio_manager.py
│   │   ├── real_funding_agent.py
│   │   ├── real_market_agent.py
│   │   ├── real_risk_agent.py
│   │   └── risk_agent.py
│   ├── audio/
│   ├── config.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── circuit-breaker.ts
│   │   ├── retry-manager.ts
│   │   └── websocket-manager.ts
│   ├── data/
│   │   ├── funding/
│   │   ├── market_database/
│   │   │   ├── data_collector.js
│   │   │   ├── market_data.db
│   │   │   └── setup_database.js
│   │   ├── metrics_collector.py
│   │   ├── production_backtests/
│   │   │   ├── BB_Squeeze_62_PRO_FINAL_results.json
│   │   │   ├── BTCDominance_FINAL.py
│   │   │   ├── BTCDominance_FINAL_results_improved.json
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
│   │   ├── realtime_backtester.py
│   │   ├── risk_agent/
│   │   ├── sentiment/
│   │   └── sentiment_history.csv
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
│   ├── logger.py
│   ├── logging/
│   │   ├── __init__.py
│   │   ├── structured-logger.js
│   │   └── structured-logger.ts
│   ├── market_database/
│   │   ├── fix_data.js
│   │   ├── market_data.db
│   │   ├── real_backtest_executor.js
│   │   └── setup_database.js
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
│   ├── test-system.js
│   └── test_backtest_display.html
└── tsconfig.json

ignore:
  - dist/
  - logs/
  - node_modules/
  - src\__pycache__/
  - src\agents\__pycache__/
  - src\algorithms\__pycache__/
  - src\cache/
  - src\hyperliquid\__pycache__/
  - src\wallet\__pycache__/
  - tests\logs/