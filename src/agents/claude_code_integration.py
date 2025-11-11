"""
[OK] Claude Code Integration for NOVAQUOTE Agents
Built with love by Deamon Dev [ROCKET]

Pattern: Utilise claude-agents.json avec --agents @.claude/agents/
Intègre les agents trading (strategy, risk, funding, sentiment) avec sub-agents Claude Code
"""

import json
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from termcolor import cprint

from src.agents.iterative_subagent_manager import (
    IterationConfig,
    IterationMode,
    IterativeSubagentManager,
    SubagentResponse,
)


class ClaudeCodeIntegrationManager:
    """
    Gestionnaire principal pour l'intégration des agents NOVAQUOTE avec Claude Code

    Utilise le pattern:
    - claude-agents.json avec --agents @.claude/agents/
    - Sub-agents spécialisés pour chaque domaine métier
    - Système d'itération avancé
    """

    def __init__(self, project_path: Optional[str] = None):
        self.project_path = (
            Path(project_path) if project_path else Path(__file__).parent.parent.parent
        )
        self.agents_path = self.project_path / ".claude" / "agents"
        self.agents_config_file = self.project_path / "claude-agents.json"

        self.iteration_manager = IterativeSubagentManager()

        self.agent_to_subagent_mapping = {
            "strategy_agent": "claude-strategy-advisor",
            "risk_agent": "claude-risk-advisor",
            "funding_agent": "claude-funding-advisor",
            "sentiment_agent": "claude-sentiment-analyzer",
        }

        self._verify_configuration()

        cprint(
            f"[OK] Claude Code Integration Manager initialized with {len(self.agent_to_subagent_mapping)} agents",
            "green",
        )

    def _verify_configuration(self):
        """Vérifier que tous les fichiers de configuration existent"""
        if not self.agents_config_file.exists():
            cprint(
                f"[WARNING] {self.agents_config_file} not found! Creating default...",
                "yellow",
            )
            self._create_default_agents_config()

        if not self.agents_path.exists():
            self.agents_path.mkdir(parents=True, exist_ok=True)
            cprint(f"[OK] Created agents directory: {self.agents_path}", "green")

    def _create_default_agents_config(self):
        """Créer la configuration par défaut de claude-agents.json"""
        default_config = {
            "swarm_metadata": {
                "name": "NOVAQUOTE Trading Agents",
                "version": "1.0",
                "description": "Agents de trading NOVAQUOTE avec Claude Code sub-agents",
                "created": datetime.now().isoformat(),
            },
            "agents": [
                {
                    "id": "claude-strategy-advisor",
                    "name": "Strategy Advisor",
                    "description": "Analyse les signaux de trading et recommande des stratégies",
                    "tools": ["Read", "Edit", "Bash", "Grep"],
                    "model": "sonnet",
                    "temperature": 0.3,
                    "max_tokens": 4000,
                },
                {
                    "id": "claude-risk-advisor",
                    "name": "Risk Advisor",
                    "description": "Gestion des risques et position sizing",
                    "tools": ["Read", "Edit", "Bash"],
                    "model": "sonnet",
                    "temperature": 0.2,
                    "max_tokens": 3000,
                },
                {
                    "id": "claude-funding-advisor",
                    "name": "Funding Advisor",
                    "description": "Analyse de corrélation et optimisation des taux de funding",
                    "tools": ["Read", "Bash", "Grep"],
                    "model": "sonnet",
                    "temperature": 0.3,
                    "max_tokens": 3000,
                },
                {
                    "id": "claude-sentiment-analyzer",
                    "name": "Sentiment Analyzer",
                    "description": "Analyse du sentiment du marché et social",
                    "tools": ["Read", "Bash"],
                    "model": "sonnet",
                    "temperature": 0.4,
                    "max_tokens": 3500,
                },
            ],
            "orchestration": {
                "mode": "delegation",
                "default_iterations": 3,
                "timeout_per_call": 120,
            },
        }

        with open(self.agents_config_file, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)

        cprint(f"[OK] Created default config: {self.agents_config_file}", "green")

    def call_claude_code_agent(
        self,
        agent_id: str,
        prompt: str,
        context_data: Optional[dict] = None,
        use_iterations: bool = True,
        iteration_mode: IterationMode = IterationMode.PROGRESSIVE_REFINEMENT,
    ) -> Dict[str, Any]:
        """
        Appeler un agent Claude Code via le pattern --agents @.claude/agents/

        Args:
            agent_id: ID de l'agent (claude-strategy-advisor, etc.)
            prompt: Prompt pour l'agent
            context_data: Données contextuelles
            use_iterations: Utiliser le système d'itération avancé
            iteration_mode: Mode d'itération

        Returns:
            Résultat de l'exécution avec métadonnées
        """
        full_prompt = self._build_prompt(prompt, context_data)

        if use_iterations:
            cprint(f"[INFO] Using {iteration_mode.value} for {agent_id}", "cyan")
            session = self.iteration_manager.call_subagent_iteration(
                prompt=full_prompt,
                context_data=context_data,
                mode=iteration_mode,
            )

            return {
                "agent": agent_id,
                "session_id": session.session_id,
                "mode": iteration_mode.value,
                "iterations": len(session.responses),
                "converged": session.convergence_metrics.get("converged", False),
                "confidence": session.convergence_metrics.get("final_confidence", 0.0),
                "result": session.final_result,
                "metrics": session.convergence_metrics,
                "execution_time": session.total_time,
                "success": True,
            }
        else:
            result = self._direct_cli_call(agent_id, full_prompt)
            return {
                "agent": agent_id,
                "result": result,
                "success": True,
                "execution_time": 0.0,
            }

    def _build_prompt(self, prompt: str, context_data: Optional[dict] = None) -> str:
        """Construire le prompt complet avec contexte"""
        if not context_data:
            return prompt

        context_str = json.dumps(context_data, indent=2, ensure_ascii=False)
        return f"""{prompt}

=== CONTEXT DATA ===
{context_str}

=== INSTRUCTIONS ===
Analysez le contexte et fournissez une réponse détaillée avec:
1. Décision claire (BUY/SELL/HOLD)
2. Niveau de confiance (0.0-1.0)
3. Raisonnement détaillé
4. Métriques de risque
5. Recommandations d'exécution
"""

    def _direct_cli_call(self, agent_id: str, full_prompt: str) -> str:
        """
        Appel direct via CLI avec pattern --agents @.claude/agents/

        Pattern documenté:
        claude --agents @.claude/agents/novaquote-bug-fixer.json --print --dangerously-skip-permissions "task"
        """
        agent_file = self.agents_path / f"{agent_id}.json"

        if not agent_file.exists():
            self._create_agent_config_file(agent_id, agent_file)

        cmd = [
            "claude",
            "--agents",
            str(agent_file),
            "--print",
            "--dangerously-skip-permissions",
            full_prompt,
        ]

        cprint(f"[CLI] Executing: {' '.join(cmd[:4])}...", "cyan")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                cwd=self.project_path,
            )

            if result.returncode != 0:
                cprint(f"[ERROR] CLI call failed: {result.stderr}", "red")
                return f"ERROR: {result.stderr}"

            return result.stdout

        except subprocess.TimeoutExpired:
            cprint(f"[ERROR] Timeout calling {agent_id}", "red")
            return "ERROR: Timeout"
        except Exception as e:
            cprint(f"[ERROR] Exception calling {agent_id}: {e}", "red")
            return f"ERROR: {str(e)}"

    def _create_agent_config_file(self, agent_id: str, agent_file: Path):
        """Créer un fichier de configuration pour un agent"""
        config = {
            "name": agent_id,
            "description": f"Sub-agent {agent_id} for NOVAQUOTE",
            "model": "sonnet",
            "temperature": 0.3,
            "max_tokens": 4000,
            "tools": ["Read", "Edit", "Bash", "Grep"],
            "prompt": f"You are the {agent_id}, a specialized sub-agent for NOVAQUOTE trading system.",
        }

        with open(agent_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        cprint(f"[OK] Created agent config: {agent_file}", "green")

    def delegate_to_claude_agents(
        self, task_description: str, context_data: dict
    ) -> Dict[str, Any]:
        """
        Déléguer automatiquement aux agents via claude-agents.json

        Pattern: claude --agents @.claude/agents.json --print --dangerously-skip-permissions "task"
        """
        cprint("[INFO] Delegating to Claude Code agents via claude-agents.json", "cyan")

        delegation_prompt = f"""
        [NOVAQUOTE TRADING SYSTEM]
        Task: {task_description}

        Please use the appropriate NOVAQUOTE sub-agents to analyze and provide recommendations:
        - claude-strategy-advisor: For strategy and signal analysis
        - claude-risk-advisor: For risk management
        - claude-funding-advisor: For funding rate optimization
        - claude-sentiment-analyzer: For market sentiment analysis

        Context: {json.dumps(context_data, indent=2)}
        """

        cmd = [
            "claude",
            "--agents",
            str(self.agents_config_file),
            "--print",
            "--dangerously-skip-permissions",
            delegation_prompt,
        ]

        cprint(f"[CLI] Delegating: {' '.join(cmd[:4])}...", "cyan")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes pour délégation complète
                cwd=self.project_path,
            )

            if result.returncode != 0:
                return {
                    "success": False,
                    "error": result.stderr,
                    "delegation": False,
                }

            return {
                "success": True,
                "result": result.stdout,
                "delegation": True,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "delegation": False,
            }

    def run_complete_trading_analysis(self, market_data: dict) -> Dict[str, Any]:
        """
        Analyse complète de trading avec tous les agents

        Utilise le pattern d'orchestration documenté
        """
        cprint("[OK] Starting complete trading analysis...", "green")

        results = {}

        cprint("[1/4] Strategy Analysis...", "cyan")
        strategy_result = self.call_claude_code_agent(
            agent_id="claude-strategy-advisor",
            prompt="Analyze trading signals and market conditions",
            context_data=market_data,
            use_iterations=True,
        )
        results["strategy"] = strategy_result

        cprint("[2/4] Risk Assessment...", "cyan")
        risk_result = self.call_claude_code_agent(
            agent_id="claude-risk-advisor",
            prompt="Assess portfolio risk and position sizing",
            context_data={**market_data, "strategy_result": strategy_result},
            use_iterations=True,
        )
        results["risk"] = risk_result

        cprint("[3/4] Funding Correlation Analysis...", "cyan")
        funding_result = self.call_claude_code_agent(
            agent_id="claude-funding-advisor",
            prompt="Analyze funding rate correlations with market variables and regime-based opportunities",
            context_data=market_data,
            use_iterations=True,
        )
        results["funding"] = funding_result

        cprint("[4/4] Sentiment Analysis...", "cyan")
        sentiment_result = self.call_claude_code_agent(
            agent_id="claude-sentiment-analyzer",
            prompt="Analyze market sentiment and social signals",
            context_data=market_data,
            use_iterations=True,
        )
        results["sentiment"] = sentiment_result

        consensus = self._calculate_consensus(results)

        cprint("[OK] Complete analysis finished!", "green")

        return {
            "timestamp": datetime.now().isoformat(),
            "agents_results": results,
            "consensus": consensus,
            "summary": {
                "total_agents": len(results),
                "converged_agents": sum(1 for r in results.values() if r.get("converged", False)),
                "avg_confidence": consensus.get("avg_confidence", 0.0),
                "decision": consensus.get("decision", "HOLD"),
            },
        }

    def _calculate_consensus(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculer le consensus entre les agents"""
        decisions = []
        confidences = []
        reasoning_parts = []

        for agent_name, result in results.items():
            if result.get("success", False):
                if "result" in result and result["result"]:
                    text = str(result["result"])
                    if "BUY" in text or "SELL" in text or "HOLD" in text:
                        decisions.append(agent_name)

                confidences.append(result.get("confidence", 0.0))
                reasoning_parts.append(f"{agent_name}: {result.get('confidence', 0.0):.2f}")

        if decisions:
            decision = decisions[0]  # Prendre la première décision
        else:
            decision = "HOLD"

        return {
            "decision": decision,
            "avg_confidence": (sum(confidences) / len(confidences) if confidences else 0.0),
            "reasoning": "; ".join(reasoning_parts),
            "agents_agreed": len(decisions),
        }

    def save_analysis_report(self, results: Dict[str, Any], filename: Optional[str] = None):
        """Sauvegarder le rapport d'analyse"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"claude_code_analysis_{timestamp}.json"

        reports_dir = self.project_path / "reports" / "claude_code"
        reports_dir.mkdir(parents=True, exist_ok=True)

        report_path = reports_dir / filename

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        cprint(f"[OK] Report saved: {report_path}", "green")
        return report_path


if __name__ == "__main__":
    manager = ClaudeCodeIntegrationManager()

    test_market_data = {
        "symbol": "BTC-USD",
        "price": 50000,
        "volume": 1000000,
        "funding_rate": 0.0001,
        "market_cap": 1000000000,
        "timestamp": datetime.now().isoformat(),
    }

    print("\n" + "=" * 60)
    print("TEST 1: Direct Agent Call")
    print("=" * 60)
    result = manager.call_claude_code_agent(
        agent_id="claude-strategy-advisor",
        prompt="Should I buy BTC at $50,000?",
        context_data=test_market_data,
    )
    print(f"\nResult: {json.dumps(result, indent=2)}")

    print("\n" + "=" * 60)
    print("TEST 2: Delegation via claude-agents.json")
    print("=" * 60)
    delegation_result = manager.delegate_to_claude_agents(
        task_description="Analyze BTC trading opportunity",
        context_data=test_market_data,
    )
    print(f"\nDelegation Result: {json.dumps(delegation_result, indent=2)}")

    print("\n" + "=" * 60)
    print("TEST 3: Complete Trading Analysis")
    print("=" * 60)
    complete_result = manager.run_complete_trading_analysis(test_market_data)
    print(f"\nComplete Result Summary: {json.dumps(complete_result['summary'], indent=2)}")

    report_path = manager.save_analysis_report(complete_result)
    print(f"\n📄 Full report saved: {report_path}")
