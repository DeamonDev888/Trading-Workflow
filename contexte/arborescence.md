projet trading/
├── .gitignore
├── agent-retro-ingenierie.md
├── backend/
|   ├── agent_auto_recovery.ts
|   ├── agent_health_monitor.ts
|   ├── agent_launcher.ts
|   ├── backtest_validator.js
|   ├── dashboard_data.json
|   ├── database_config.ts
|   ├── server-backend.js
|   ├── server-backend.ts
|   ├── server-backend.ts.backup
|   └── wallet-endpoints.ts
├── contexte/
|   ├── arborescence.md
|   └── context_app.md
├── data/
|   └── aggregator/
|       └── aggregation_agg_1763005934_20251112_225214.json
├── docs/
|   ├── agents/
|   ├── AGENTS_ARCHITECTURE_DIAGRAM.md
|   ├── AGENTS_GRAPH_VISUALIZATION.md
|   ├── api/
|   ├── architecture/
|   ├── COMMANDS_AGENTS.md
|   ├── COMMANDS_AGENTS_GUIDE.md
|   ├── guides/
|   ├── HYPERLIQUID_API_DOCUMENTATION.md
|   ├── other/
|   |   └── NOVAQUOTE_DIAGNOSTIC_REPORT.txt
|   └── WALLET_INTEGRATION_GUIDE.md
├── eslint.config.js
├── frontend/
|   ├── public/
|   |   ├── assets/
|   |   |   └── novaquote.css
|   |   ├── backtest.html
|   |   ├── config.html
|   |   ├── data/
|   |   |   └── production_backtests/
|   |   |       └── BTCDominance_FINAL_results_improved.json
|   |   ├── favicon.ico
|   |   ├── index.html
|   |   ├── portfolio-manager.js
|   |   ├── test_agents.html
|   |   └── test_claude_agents.html
|   ├── server-frontend.js
|   └── server-frontend.ts
├── NOVAQUOTE_ROADMAP_2025.md
├── NOVAQUOTE_ROADMAP_SIMPLIFIEE.md
├── package-lock.json
├── package.json
├── PROMPT_SYSTEME_NOVAQUOTE.md
├── README.md
├── reports/
|   ├── database/
|   |   ├── database_performance_20251111_093712.md
|   |   └── database_performance_20251111_094056.md
|   ├── database-validation-report-2025-11-13.md
|   ├── diagnostic-connexion-9001-2025-11-12.md
|   ├── documentation/
|   |   ├── documentation_status_20251111_092539.md
|   |   ├── documentation_status_20251111_092925.md
|   |   ├── documentation_status_20251111_093013.md
|   |   └── documentation_status_20251111_093304.md
|   ├── logging-system-validation-report-2025-11-13.md
|   ├── scan-report-2025-11-13_01-32-40.md
|   ├── scan-report-2025-11-13_01-34-02.md
|   ├── scan-report-2025-11-13_01-37-39.md
|   ├── scan-report-2025-11-13_01-49-14.md
|   ├── scan-report-2025-11-13_01-51-56.md
|   ├── scan-report-2025-11-13_01-52-25.md
|   ├── scan-report-2025-11-13_02-00-50.md
|   ├── scan-report-2025-11-13_02-03-44.md
|   ├── scan-report-2025-11-14_01-59-58.md
|   ├── scan-report-2025-11-14_02-05-06.md
|   ├── scan-report-2025-11-14_02-06-27.md
|   ├── scan-report-2025-11-14_02-06-55.md
|   └── scan-report-2025-11-14_02-07-37.md
├── run.ts
├── scripts/
|   ├── agent_logs_monitor.js
|   ├── answer_user_question.py
|   ├── claude_code_agent_runner.py
|   ├── database_manager.py
|   ├── database_startup_optimization.js
|   ├── database_validation.py
|   ├── db_validation_simple.py
|   ├── deploy-mainnet.js
|   ├── documentation_manager.py
|   ├── fix_database_constraints.py
|   ├── generate_context.py
|   ├── project_snapshot.py
|   ├── remove-console-logs.js
|   ├── scan/
|   |   ├── novaquote-complete-scan.js
|   |   ├── README.md
|   |   ├── scan-python.py
|   |   └── scan-typescript-javascript.js
|   ├── start_inference_monitoring.py
|   ├── start_persistent_agents.py
|   ├── test_claude_code_integration.py
|   ├── test_wallet_integration.ts
|   ├── test_wallet_simple.js
|   └── test_websocket_client.js
├── src/
|   ├── __init__.py
|   ├── agents/
|   |   ├── __init__.py
|   |   ├── advanced_risk_agent.py
|   |   ├── agent_inference_monitor.py
|   |   ├── agent_manager.py
|   |   ├── api.py
|   |   ├── automatic_coin_rotator.py
|   |   ├── base_agent.py
|   |   ├── claude_code_integration.py
|   |   ├── claude_code_orchestrator.py
|   |   ├── coin_rotation_integration.py
|   |   ├── coin_rotation_manager.py
|   |   ├── data_aggregator.py
|   |   ├── funding_agent.py
|   |   ├── hybrid_rotation_api.py
|   |   ├── hybrid_rotation_system.py
|   |   ├── intelligent_backtest_optimizer.py
|   |   ├── iterative_subagent_manager.py
|   |   ├── liquidity_tracker.py
|   |   ├── manager.py
|   |   ├── master_agent.py
|   |   ├── master_agent_logger.py
|   |   ├── persistent_agent_client.py
|   |   ├── persistent_agent_orchestrator.py
|   |   ├── reliability_monitor.py
|   |   ├── risk_agent.py
|   |   ├── risk_agent_enhanced.py
|   |   ├── rotation_interface.py
|   |   ├── sentiment_analysis_agent.py
|   |   ├── simple_agent.py
|   |   ├── strategy_agent.py
|   |   ├── strategy_library.py
|   |   └── volatility_tracker.py
|   ├── algorithms/
|   |   ├── __init__.py
|   |   ├── funding_agent.py
|   |   ├── hyperliquid_agent.py
|   |   ├── hyperliquid_mainnet_agent.py
|   |   ├── portfolio_manager.py
|   |   ├── real_funding_agent.py
|   |   ├── real_market_agent.py
|   |   ├── real_risk_agent.py
|   |   └── risk_agent.py
|   ├── audio/
|   ├── config.py
|   ├── core/
|   |   ├── __init__.py
|   |   ├── circuit-breaker.ts
|   |   ├── retry-manager.ts
|   |   └── websocket-manager.ts
|   ├── data/
|   |   ├── cycles/
|   |   |   ├── 2025-11-11_10
|   |   |   └── 2025-11-11_11
|   |   ├── funding/
|   |   ├── funding_history.csv
|   |   ├── funding_history_backup.csv
|   |   ├── market_database/
|   |   |   ├── data_collector.js
|   |   |   ├── market_data.db
|   |   |   └── setup_database.js
|   |   ├── metrics_collector.py
|   |   ├── portfolio_balance.csv
|   |   ├── production_backtests/
|   |   |   ├── BB_Squeeze_62_PRO_FINAL_results.json
|   |   |   ├── BTCDominance_FINAL.py
|   |   |   ├── BTCDominance_FINAL_results_improved.json
|   |   |   ├── DivergentVolReversal_FINAL.py
|   |   |   ├── Fear_Contrarian_73_PRO_FINAL_results.json
|   |   |   ├── FractalCascade_FINAL.py
|   |   |   ├── Funding_Arbitrage_85_PRO_FINAL_results.json
|   |   |   ├── GoldenCrossover_FINAL.py
|   |   |   ├── MACD_Crossover_65_PRO_FINAL_results.json
|   |   |   ├── README.md
|   |   |   ├── RSI_Oversold_68_PRO_FINAL_results.json
|   |   |   ├── Twitter_Sentiment_69_PRO_FINAL_results.json
|   |   |   ├── VolatilityEngulfing_FINAL.py
|   |   |   └── Volume_Breakout_71_PRO_FINAL_results.json
|   |   ├── realtime_backtester.py
|   |   ├── risk_agent/
|   |   ├── sentiment/
|   |   ├── sentiment_history.csv
|   |   └── test/
|   ├── exchange_manager.py
|   ├── health/
|   |   ├── health-checker.ts
|   |   └── inference_api.py
|   ├── hyperliquid/
|   |   ├── __init__.py
|   |   ├── client.py
|   |   ├── hyperliquid-api.js
|   |   ├── hyperliquid-signature.js
|   |   ├── hyperliquid-websocket.js
|   |   ├── signing.py
|   |   ├── types.py
|   |   └── websocket.py
|   ├── logger.py
|   ├── logging/
|   |   ├── __init__.py
|   |   ├── log_centralizer.py
|   |   ├── novaquote-winston-loggers.ts
|   |   ├── structured-logger.js
|   |   └── structured-logger.ts
|   ├── market_database/
|   |   ├── create_wallet_tables.sql
|   |   ├── fix_data.js
|   |   ├── market_data.db
|   |   ├── market_data.db-shm
|   |   ├── market_data.db-wal
|   |   ├── real_backtest_executor.js
|   |   ├── setup_database.js
|   |   ├── wallet_database.ts
|   |   └── wallet_database_sync.ts
|   ├── metrics/
|   |   └── prometheus.ts
|   ├── models/
|   |   ├── __init__.py
|   |   ├── base_model.py
|   |   ├── claude_model.py
|   |   ├── deepseek_model.py
|   |   ├── gemini_model.py
|   |   ├── groq_model.py
|   |   ├── model_factory.py
|   |   ├── ollama_model.py
|   |   ├── openai_model.py
|   |   ├── xai_model.py
|   |   └── zai_model.py
|   ├── nice_funcs.py
|   ├── security/
|   |   ├── rate-limiter.ts
|   |   └── security-headers.ts
|   ├── trading_engine.py
|   ├── user_identity.py
|   ├── utils/
|   |   └── unicode_support.py
|   ├── validation/
|   |   └── schemas.ts
|   └── wallet/
|       ├── __init__.py
|       ├── api_wallet_manager.py
|       ├── permission_controller.py
|       ├── signature_engine.py
|       └── wallet_registry.py
├── tests/
|   ├── README.md
|   ├── test-structured-logger.js
|   └── test-system.js
└── tsconfig.json

ignore:
  - dist/
  - logs/
  - node_modules/
  - scripts\__pycache__/
  - src\__pycache__/
  - src\agents\__pycache__/
  - src\algorithms\__pycache__/
  - src\cache/
  - src\core\__pycache__/
  - src\data\__pycache__/
  - src\data\production_backtests\__pycache__/
  - src\health\__pycache__/
  - src\hyperliquid\__pycache__/
  - src\logging\__pycache__/
  - src\models\__pycache__/
  - src\utils\__pycache__/
  - src\wallet\__pycache__/
  - tests\logs/