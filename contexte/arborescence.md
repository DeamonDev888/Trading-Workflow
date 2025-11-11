projet trading/
├── .gitignore
├── backend/
|   ├── backtest_validator.js
|   ├── dashboard_data.json
|   ├── server-backend.js
|   └── server-backend.ts
├── contexte/
|   ├── arborescence.md
|   └── context_app.md
├── docs/
|   ├── AGENT_QUICK_START.md
|   ├── agents_crypto/
|   |   ├── funding-agent.md
|   |   ├── index.md
|   |   ├── README.md
|   |   ├── risk-agent.md
|   |   ├── sentiment-agent.md
|   |   └── strategy-agent.md
|   ├── AGENTS_GRAPH_VISUALIZATION.md
|   ├── AGENTS_USAGE.md
|   ├── ARCHITECTURE_DIAGRAMS.md
|   ├── CIRCULAR_SYSTEM_GUIDE.md
|   ├── CLAUDE_CODE_ARCHITECTURE.md
|   ├── CLAUDE_CODE_INTEGRATION_GUIDE.md
|   ├── CLAUDE_CODE_INTEGRATION_README.md
|   ├── COMMANDS_AGENTS.md
|   ├── COMMANDS_AGENTS_GUIDE.md
|   ├── DATA_RECOVERY_AND_RELIABILITY_GUIDE.md
|   ├── EMOJIS_FALLBACKS.md
|   ├── FINAL_AGENT_GUIDE.md
|   ├── GUIDE_FINAL_AGENTS.md
|   ├── HYBRID_ROTATION_SYSTEM.md
|   ├── HYPERLIQUID_API_DOCUMENTATION.md
|   ├── LOG_SYSTEM_DOCUMENTATION.md
|   ├── RESUMÉ_AGENTS.md
|   └── SOLUTION_AGENTS.md
├── eslint.config.js
├── frontend/
|   ├── public/
|   |   ├── assets/
|   |   |   └── novaquote.css
|   |   ├── backtest.html
|   |   ├── config.html
|   |   ├── dashboard_ascii.html
|   |   ├── data/
|   |   |   └── production_backtests/
|   |   |       └── BTCDominance_FINAL_results_improved.json
|   |   ├── index.html
|   |   ├── portfolio-manager.js
|   |   ├── test_agents.html
|   |   ├── test_claude_agents.html
|   |   └── validate_config.html
|   └── server-frontend.ts
├── package-lock.json
├── package.json
├── PROMPT_SYSTEME_NOVAQUOTE.md
├── README.md
├── run.ts
├── scripts/
|   ├── agent_logs_monitor.js
|   ├── answer_user_question.py
|   ├── auto_bug_fixer_cli.py
|   ├── CLAUDE_AUTO_LINTER.py
|   ├── claude_code_agent_runner.py
|   ├── claude_code_agents.ps1
|   ├── claude_code_integration_demo.py
|   ├── claude_code_reliability_demo.py
|   ├── CLAUDE_CODE_SUBAGENT.py
|   ├── DEMO_SUBAGENT.py
|   ├── fix_emojis.py
|   ├── fix_syntax.js
|   ├── generate_context.py
|   ├── lint-format-py.py
|   ├── novaquote_agent_corrector.py
|   ├── novaquote_bug_fixer_task.py
|   ├── novaquote_detect_all_project_errors.py
|   ├── novaquote_detect_auto_errors.py
|   ├── novaquote_detect_clear_errors.py
|   ├── novaquote_detect_critical_errors.py
|   ├── novaquote_detect_fix_critical_errors.py
|   ├── novaquote_detect_fix_python_errors.py
|   ├── novaquote_detect_intelligent_errors.py
|   ├── novaquote_detect_python_format_errors.py
|   ├── novaquote_detect_typescript_errors.py
|   ├── novaquote_perfect_zero_error.py
|   ├── novaquote_scan_all_errors.py
|   ├── novaquote_scan_and_fix_complete.py
|   ├── novaquote_scan_novaquote_project.py
|   ├── novaquote_ultimate_corrector.py
|   ├── optimize_all_strategies.py
|   ├── project_snapshot.py
|   ├── start_inference_monitoring.py
|   ├── start_persistent_agents.py
|   ├── test_claude_code_integration.py
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
|   |   ├── funding/
|   |   ├── market_database/
|   |   |   ├── data_collector.js
|   |   |   ├── market_data.db
|   |   |   └── setup_database.js
|   |   ├── metrics_collector.py
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
|   |   ├── structured-logger.js
|   |   └── structured-logger.ts
|   ├── market_database/
|   |   ├── fix_data.js
|   |   ├── market_data.db
|   |   ├── real_backtest_executor.js
|   |   └── setup_database.js
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
  - src\data\__pycache__/
  - src\health\__pycache__/
  - src\hyperliquid\__pycache__/
  - src\models\__pycache__/
  - src\wallet\__pycache__/
  - tests\logs/