projet trading/
├── .gitignore
├── backend/
│ ├── backtest_validator.js
│ ├── server-backend.js
│ └── server-backend.ts
├── contexte/
│ └── context_app.md
├── docs/
│ ├── agents/
│ │ ├── funding-agent.md
│ │ ├── index.md
│ │ ├── README.md
│ │ ├── risk-agent.md
│ │ ├── sentiment-agent.md
│ │ └── strategy-agent.md
│ ├── AGENTS_GRAPH_VISUALIZATION.md
│ ├── ARCHITECTURE_DIAGRAMS.md
│ ├── CIRCULAR_SYSTEM_GUIDE.md
│ ├── HYBRID_ROTATION_SYSTEM.md
│ ├── HYPERLIQUID_API_DOCUMENTATION.md
│ └── LOG_SYSTEM_DOCUMENTATION.md
├── eslint.config.js
├── frontend/
│ ├── public/
│ │ ├── assets/
│ │ │ └── novaquote.css
│ │ ├── backtest.html
│ │ ├── config.html
│ │ ├── dashboard_ascii.html
│ │ ├── data/
│ │ │ └── production_backtests/
│ │ │ └── BTCDominance_FINAL_results_improved.json
│ │ ├── index.html
│ │ ├── portfolio-manager.js
│ │ ├── test_agents.html
│ │ └── validate_config.html
│ └── server-frontend.ts
├── package-lock.json
├── package.json
├── README.md
├── run.ts
├── scripts/
│ ├── auto_bug_fixer_cli.py
│ ├── CLAUDE_AUTO_LINTER.py
│ ├── fix_emojis.py
│ ├── generate_context.py
│ ├── lint-format-py.py
│ ├── optimize_all_strategies.py
│ ├── project_snapshot.py
│ ├── simple_coin_rotation_test.py
│ ├── start_inference_monitoring.py
│ ├── start_persistent_agents.py
│ └── test_circular_system.py
├── src/
│ ├── **init**.py
│ ├── agents/
│ │ ├── **init**.py
│ │ ├── advanced_risk_agent.py
│ │ ├── agent_inference_monitor.py
│ │ ├── api.py
│ │ ├── automatic_coin_rotator.py
│ │ ├── base_agent.py
│ │ ├── coin_rotation_integration.py
│ │ ├── coin_rotation_manager.py
│ │ ├── funding_agent.py
│ │ ├── hybrid_rotation_api.py
│ │ ├── hybrid_rotation_system.py
│ │ ├── intelligent_backtest_optimizer.py
│ │ ├── iterative_subagent_manager.py
│ │ ├── liquidity_tracker.py
│ │ ├── manager.py
│ │ ├── master_agent.py
│ │ ├── persistent_agent_client.py
│ │ ├── persistent_agent_orchestrator.py
│ │ ├── risk_agent.py
│ │ ├── rotation_interface.py
│ │ ├── sentiment_analysis_agent.py
│ │ ├── strategy_agent.py
│ │ ├── strategy_library.py
│ │ └── volatility_tracker.py
│ ├── algorithms/
│ │ ├── **init**.py
│ │ ├── funding_agent.py
│ │ ├── hyperliquid_agent.py
│ │ ├── hyperliquid_mainnet_agent.py
│ │ ├── portfolio_manager.py
│ │ ├── real_funding_agent.py
│ │ ├── real_market_agent.py
│ │ ├── real_risk_agent.py
│ │ └── risk_agent.py
│ ├── audio/
│ ├── config.py
│ ├── core/
│ │ ├── **init**.py
│ │ ├── circuit-breaker.ts
│ │ ├── retry-manager.ts
│ │ └── websocket-manager.ts
│ ├── data/
│ │ ├── funding/
│ │ ├── market_database/
│ │ │ ├── data_collector.js
│ │ │ ├── market_data.db
│ │ │ └── setup_database.js
│ │ ├── metrics_collector.py
│ │ ├── production_backtests/
│ │ │ ├── BB_Squeeze_62_PRO_FINAL_results.json
│ │ │ ├── BTCDominance_FINAL.py
│ │ │ ├── BTCDominance_FINAL_results_improved.json
│ │ │ ├── DivergentVolReversal_FINAL.py
│ │ │ ├── Fear_Contrarian_73_PRO_FINAL_results.json
│ │ │ ├── FractalCascade_FINAL.py
│ │ │ ├── Funding_Arbitrage_85_PRO_FINAL_results.json
│ │ │ ├── GoldenCrossover_FINAL.py
│ │ │ ├── MACD_Crossover_65_PRO_FINAL_results.json
│ │ │ ├── README.md
│ │ │ ├── RSI_Oversold_68_PRO_FINAL_results.json
│ │ │ ├── Twitter_Sentiment_69_PRO_FINAL_results.json
│ │ │ ├── VolatilityEngulfing_FINAL.py
│ │ │ └── Volume_Breakout_71_PRO_FINAL_results.json
│ │ ├── realtime_backtester.py
│ │ ├── risk_agent/
│ │ ├── sentiment/
│ │ ├── sentiment_history.csv
│ │ └── test/
│ ├── health/
│ │ ├── health-checker.ts
│ │ └── inference_api.py
│ ├── hyperliquid/
│ │ ├── **init**.py
│ │ ├── client.py
│ │ ├── hyperliquid-api.js
│ │ ├── hyperliquid-signature.js
│ │ ├── hyperliquid-websocket.js
│ │ ├── signing.py
│ │ ├── types.py
│ │ └── websocket.py
│ ├── logger.py
│ ├── logging/
│ │ ├── **init**.py
│ │ ├── structured-logger.js
│ │ └── structured-logger.ts
│ ├── market_database/
│ │ ├── fix_data.js
│ │ ├── market_data.db
│ │ ├── real_backtest_executor.js
│ │ └── setup_database.js
│ ├── metrics/
│ │ └── prometheus.ts
│ ├── models/
│ │ ├── **init**.py
│ │ ├── base_model.py
│ │ ├── claude_model.py
│ │ ├── deepseek_model.py
│ │ ├── gemini_model.py
│ │ ├── groq_model.py
│ │ ├── model_factory.py
│ │ ├── ollama_model.py
│ │ ├── openai_model.py
│ │ ├── xai_model.py
│ │ └── zai_model.py
│ ├── nice_funcs.py
│ ├── security/
│ │ ├── rate-limiter.ts
│ │ └── security-headers.ts
│ ├── validation/
│ │ └── schemas.ts
│ └── wallet/
│ ├── **init**.py
│ ├── api_wallet_manager.py
│ ├── permission_controller.py
│ ├── signature_engine.py
│ └── wallet_registry.py
├── tests/
│ ├── README.md
│ ├── run-all-tests.js
│ ├── test-structured-logger.js
│ ├── test-system.js
│ └── test_backtest_display.html
└── tsconfig.json

ignore:

- dist/
- logs/
- node_modules/
- src\_\_pycache\_\_/
- src\agents\_\_pycache\_\_/
- src\algorithms\_\_pycache\_\_/
- src\cache/
- src\health\_\_pycache\_\_/
- src\hyperliquid\_\_pycache\_\_/
- src\wallet\_\_pycache\_\_/
- tests\logs/
