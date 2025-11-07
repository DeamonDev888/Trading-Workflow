projet trading/ ├── .gitignore ├── auto_bug_fixer_cli.py ├──
auto_linter_continuous.py ├── AUTO_LINTER_README.md ├── AUTO_LINTER_REPORT.md
├── AUTO_LINTER_TEST_REPORT.md ├── backend/ │ ├── backtest_validator.js │ ├──
server-backend.js │ └── server-backend.ts ├── BOUTONS_SUPPRIMES_RAPPORT.md ├──
CLAUDE_AUTO_LINTER.py ├── CLAUDE_SUB_AGENT_DOCS.md ├── contexte/ │ ├──
arborescence.md │ └── context_app.md ├── docs/ │ ├──
AGENTS_GRAPH_VISUALIZATION.md │ ├── ARCHITECTURE_DIAGRAMS.md │ ├──
CIRCULAR_SYSTEM_GUIDE.md │ ├── CLAUDE_CODE_SUBAGENTS_DOCUMENTATION.md │ ├──
HYPERLIQUID_API_DOCUMENTATION.md │ └── LOG_SYSTEM_DOCUMENTATION.md ├──
errors.txt ├── eslint.config.js ├── eslint_output.json ├── FINAL_SUMMARY.md ├──
frontend/ │ ├── public/ │ │ ├── assets/ │ │ │ └── novaquote.css │ │ ├──
backtest.html │ │ ├── config.html │ │ ├── dashboard_ascii.html │ │ ├── data/ │ │
│ └── production_backtests/ │ │ │ └── BTCDominance_FINAL_results_improved.json │
│ ├── index.html │ │ ├── portfolio-manager.js │ │ ├── test_agents.html │ │ └──
validate_config.html │ └── server-frontend.ts ├── GRAPHIQUES_CORRIGES_RAPPORT.md
├── lanceur_auto_linter.py ├── lint-format.js ├── linter_output.log ├──
MODE_NUIT_COMPLET_RAPPORT.md ├── NOVAQUOTE_SUB_AGENT_TASK.py ├──
package-lock.json ├── package.json ├── run.ts ├── scripts/ │ ├── fix_emojis.py │
├── generate_context.py │ ├── lint-format-py.py │ ├── optimize_all_strategies.py
│ ├── project_snapshot.py │ └── test_circular_system.py ├── skills/ │ └──
Playwright_browser/ │ └── SKILL.md ├── src/ │ ├── **init**.py │ ├── agents/ │ │
├── **init**.py │ │ ├── api.py │ │ ├── base_agent.py │ │ ├── funding_agent.py │
│ ├── intelligent_backtest_optimizer.py │ │ ├── manager.py │ │ ├──
master_agent.py │ │ ├── risk_agent.py │ │ ├── sentiment_analysis_agent.py │ │
├── strategy_agent.py │ │ └── strategy_library.py │ ├── algorithms/ │ │ ├──
**init**.py │ │ ├── funding_agent.py │ │ ├── hyperliquid_agent.py │ │ ├──
hyperliquid_mainnet_agent.py │ │ ├── portfolio_manager.py │ │ ├──
real_funding_agent.py │ │ ├── real_market_agent.py │ │ ├── real_risk_agent.py │
│ └── risk_agent.py │ ├── audio/ │ ├── config.py │ ├── core/ │ │ ├── **init**.py
│ │ ├── circuit-breaker.ts │ │ ├── retry-manager.ts │ │ └── websocket-manager.ts
│ ├── data/ │ │ ├── funding/ │ │ ├── market_database/ │ │ │ ├──
data_collector.js │ │ │ ├── market_data.db │ │ │ └── setup_database.js │ │ ├──
metrics_collector.py │ │ ├── production_backtests/ │ │ │ ├──
BB_Squeeze_62_PRO_FINAL_results.json │ │ │ ├── BTCDominance_FINAL.py │ │ │ ├──
BTCDominance_FINAL_results_improved.json │ │ │ ├── DivergentVolReversal_FINAL.py
│ │ │ ├── Fear_Contrarian_73_PRO_FINAL_results.json │ │ │ ├──
FractalCascade_FINAL.py │ │ │ ├── Funding_Arbitrage_85_PRO_FINAL_results.json │
│ │ ├── GoldenCrossover_FINAL.py │ │ │ ├──
MACD_Crossover_65_PRO_FINAL_results.json │ │ │ ├── README.md │ │ │ ├──
RSI_Oversold_68_PRO_FINAL_results.json │ │ │ ├──
Twitter_Sentiment_69_PRO_FINAL_results.json │ │ │ ├──
VolatilityEngulfing_FINAL.py │ │ │ └── Volume_Breakout_71_PRO_FINAL_results.json
│ │ ├── realtime_backtester.py │ │ ├── risk_agent/ │ │ ├── sentiment/ │ │ └──
sentiment_history.csv │ ├── health/ │ │ └── health-checker.ts │ ├── hyperliquid/
│ │ ├── **init**.py │ │ ├── client.py │ │ ├── hyperliquid-api.js │ │ ├──
hyperliquid-signature.js │ │ ├── hyperliquid-websocket.js │ │ ├── signing.py │ │
├── types.py │ │ └── websocket.py │ ├── logger.py │ ├── logging/ │ │ ├──
**init**.py │ │ ├── structured-logger.js │ │ └── structured-logger.ts │ ├──
market_database/ │ │ ├── fix_data.js │ │ ├── market_data.db │ │ ├──
real_backtest_executor.js │ │ └── setup_database.js │ ├── metrics/ │ │ └──
prometheus.ts │ ├── models/ │ │ ├── **init**.py │ │ ├── base_model.py │ │ ├──
claude_model.py │ │ ├── deepseek_model.py │ │ ├── gemini_model.py │ │ ├──
groq_model.py │ │ ├── model_factory.py │ │ ├── ollama_model.py │ │ ├──
openai_model.py │ │ ├── xai_model.py │ │ └── zai_model.py │ ├── nice_funcs.py │
├── security/ │ │ ├── rate-limiter.ts │ │ └── security-headers.ts │ ├──
validation/ │ │ └── schemas.ts │ └── wallet/ │ ├── **init**.py │ ├──
api_wallet_manager.py │ ├── permission_controller.py │ ├── signature_engine.py │
└── wallet_registry.py ├── SUB_AGENT_AUTO_LINTER_FINAL.md ├──
test_backtest_display.html ├── test_final_results.txt ├── test_output.txt ├──
tests/ │ ├── README.md │ ├── run-all-tests.js │ ├── test-structured-logger.js │
└── test-system.js ├── tsconfig.json ├── UNIFICATION_REPORT.md ├──
WALLET_HYPERLIQUID_CORRECTION.md ├── WALLET_POSITIONS_CORRECTION_RAPPORT.md ├──
WALLET_SELECTOR_RAPPORT.md └── WHY_BACKTESTS_DIFFERENT_DASHBOARD.md

ignore:

- dist/
- logs/
- node_modules/
- src\_\_pycache\_\_/
- src\agents\_\_pycache\_\_/
- src\algorithms\_\_pycache\_\_/
- src\cache/
- src\hyperliquid\_\_pycache\_\_/
- src\wallet\_\_pycache\_\_/
- tests\logs/
