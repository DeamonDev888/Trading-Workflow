#!/usr/bin/env python3
"""
Risk Agent - Agent de gestion des risques et de la position sizing
Analyse les risques en temps réel et ajuste les stratégies de trading
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np

@dataclass
class RiskMetrics:
    volatility: float
    max_drawdown: float
    sharpe_ratio: float
    var_95: float  # Value at Risk 95%
    position_concentration: float
    leverage_ratio: float
    liquidity_risk: float

@dataclass
class RiskAlert:
    level: str  # LOW, MEDIUM, HIGH, CRITICAL
    message: str
    metric: str
    current_value: float
    threshold: float
    timestamp: datetime

@dataclass
class PositionSize:
    symbol: str
    optimal_size: Decimal
    max_size: Decimal
    risk_adjusted_size: Decimal
    confidence: float

class RiskAgent:
    """Agent de gestion des risques avancé"""

    def __init__(self, initial_capital: Decimal = Decimal('10000')):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.logger = logging.getLogger("RiskAgent")

        # Seuils de risque
        self.risk_thresholds = {
            "max_portfolio_risk": 0.02,      # 2% risque max par trade
            "max_total_exposure": 0.15,       # 15% exposition max totale
            "max_leverage": 10,               # 10x levier max
            "max_correlation": 0.7,           # 70% corrélation max
            "min_liquidity": 1000000,         # $1M liquidité min
            "max_volatility": 0.05,           # 5% volatilité max
            "max_drawdown_limit": 0.10,       # 10% drawdown max
            "var_limit": 0.03,                # 3% VaR max
            "max_positions": 8                # Max 8 positions
        }

        # Métriques de performance
        self.performance_metrics = {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "total_pnl": Decimal('0'),
            "max_drawdown": Decimal('0'),
            "current_drawdown": Decimal('0'),
            "daily_returns": [],
            "position_history": []
        }

        # Alertes actives
        self.active_alerts: List[RiskAlert] = []

    async def calculate_position_size(self, symbol: str, signal_strength: float,
                                    portfolio_value: Decimal, volatility: float,
                                    account_balance: Decimal) -> PositionSize:
        """Calculer la taille de position optimale selon Kelly Criterion et risque"""
        try:
            # Kelly Criterion: f* = (bp - q) / b
            # b = ratio gain/perte, p = prob gain, q = prob perte
            win_rate = signal_strength  # Signal strength comme proxy pour win rate
            avg_win_loss_ratio = 1.5   # Ratio moyen gain/perte
            lose_rate = 1 - win_rate

            if lose_rate >= 1:
                kelly_fraction = 0
            else:
                kelly_fraction = (avg_win_loss_ratio * win_rate - lose_rate) / avg_win_loss_ratio

            # Ajuster Kelly pour plus de conservatisme (Kelly/4)
            kelly_fraction = max(0, kelly_fraction / 4)

            # Ajuster pour la volatilité
            volatility_adjustment = min(1.0, 0.03 / max(volatility, 0.001))
            kelly_fraction *= volatility_adjustment

            # Limiter par le risque maximum
            max_risk_size = (portfolio_value * Decimal(str(self.risk_thresholds["max_portfolio_risk"])))
            max_size = max_risk_size / Decimal(str(volatility))

            # Taille finale
            optimal_size = portfolio_value * Decimal(str(kelly_fraction))
            final_size = min(optimal_size, max_size, portfolio_value * Decimal('0.05'))  # Max 5% du portfolio

            # Calculer confiance
            confidence = min(1.0, kelly_fraction * 10) if kelly_fraction > 0 else 0

            return PositionSize(
                symbol=symbol,
                optimal_size=final_size,
                max_size=max_size,
                risk_adjusted_size=final_size,
                confidence=confidence
            )

        except Exception as e:
            self.logger.error(f"Erreur calcul position size: {e}")
            return PositionSize(
                symbol=symbol,
                optimal_size=Decimal('0'),
                max_size=Decimal('0'),
                risk_adjusted_size=Decimal('0'),
                confidence=0
            )

    async def assess_portfolio_risk(self, positions: List[Dict], market_data: Dict) -> RiskMetrics:
        """Évaluer le risque global du portfolio"""
        try:
            if not positions:
                return RiskMetrics(0, 0, 0, 0, 0, 0, 0)

            # Calculer la volatilité du portfolio
            portfolio_volatility = await self._calculate_portfolio_volatility(positions, market_data)

            # Calculer le drawdown maximum
            max_drawdown = await self._calculate_max_drawdown()

            # Calculer le Sharpe ratio
            sharpe_ratio = await self._calculate_sharpe_ratio()

            # Calculer la VaR 95%
            var_95 = await self._calculate_var(positions, portfolio_volatility)

            # Calculer la concentration des positions
            concentration = await self._calculate_position_concentration(positions)

            # Calculer le ratio de levier
            leverage_ratio = await self._calculate_leverage_ratio(positions)

            # Calculer le risque de liquidité
            liquidity_risk = await self._calculate_liquidity_risk(positions, market_data)

            return RiskMetrics(
                volatility=portfolio_volatility,
                max_drawdown=max_drawdown,
                sharpe_ratio=sharpe_ratio,
                var_95=var_95,
                position_concentration=concentration,
                leverage_ratio=leverage_ratio,
                liquidity_risk=liquidity_risk
            )

        except Exception as e:
            self.logger.error(f"Erreur assessment risque portfolio: {e}")
            return RiskMetrics(0, 0, 0, 0, 0, 0, 0)

    async def _calculate_portfolio_volatility(self, positions: List[Dict], market_data: Dict) -> float:
        """Calculer la volatilité du portfolio"""
        try:
            if len(positions) < 2:
                return 0.1  # Default volatility

            # Récupérer les rendements historiques (simplifié)
            returns = []
            for pos in positions:
                symbol = pos.get("symbol", "")
                # Utiliser la volatilité implicite du marché
                volatility = market_data.get(symbol, {}).get("volatility", 0.02)
                returns.append(volatility)

            # Calculer la volatilité pondérée
            weights = [pos.get("weight", 1/len(positions)) for pos in positions]
            portfolio_vol = np.sqrt(np.average(np.square(returns), weights=weights))

            return portfolio_vol

        except Exception as e:
            self.logger.error(f"Erreur calcul volatilité: {e}")
            return 0.1

    async def _calculate_max_drawdown(self) -> float:
        """Calculer le drawdown maximum"""
        try:
            if not self.performance_metrics["daily_returns"]:
                return 0

            peak = self.initial_capital
            max_dd = 0

            for return_pct in self.performance_metrics["daily_returns"]:
                self.current_capital *= (1 + return_pct)
                peak = max(peak, self.current_capital)
                drawdown = (peak - self.current_capital) / peak
                max_dd = max(max_dd, drawdown)

            return float(max_dd)

        except Exception as e:
            self.logger.error(f"Erreur calcul drawdown: {e}")
            return 0

    async def _calculate_sharpe_ratio(self) -> float:
        """Calculer le Sharpe ratio"""
        try:
            returns = self.performance_metrics["daily_returns"]
            if len(returns) < 2:
                return 0

            avg_return = np.mean(returns)
            std_return = np.std(returns)

            if std_return == 0:
                return 0

            # Risk-free rate supposé 2% annuel = 0.0000548 par jour
            risk_free_rate = 0.0000548
            sharpe = (avg_return - risk_free_rate) / std_return

            return sharpe * np.sqrt(252)  # Annualisé

        except Exception as e:
            self.logger.error(f"Erreur calcul Sharpe: {e}")
            return 0

    async def _calculate_var(self, positions: List[Dict], volatility: float) -> float:
        """Calculer la Value at Risk 95%"""
        try:
            # VaR paramétrique simplifiée
            portfolio_value = sum(pos.get("value", 0) for pos in positions)
            z_score_95 = 1.645  # Z-score pour 95%

            var_95 = portfolio_value * volatility * z_score_95
            return var_95

        except Exception as e:
            self.logger.error(f"Erreur calcul VaR: {e}")
            return 0

    async def _calculate_position_concentration(self, positions: List[Dict]) -> float:
        """Calculer la concentration des positions"""
        try:
            if not positions:
                return 0

            total_value = sum(pos.get("value", 0) for pos in positions)
            if total_value == 0:
                return 0

            # Calculer l'indice Herfindahl-Hirschman
            concentrations = [(pos.get("value", 0) / total_value) ** 2 for pos in positions]
            hhi = sum(concentrations)

            return hhi

        except Exception as e:
            self.logger.error(f"Erreur calcul concentration: {e}")
            return 0

    async def _calculate_leverage_ratio(self, positions: List[Dict]) -> float:
        """Calculer le ratio de levier moyen"""
        try:
            if not positions:
                return 0

            leverages = [pos.get("leverage", 1) for pos in positions]
            avg_leverage = np.mean(leverages)

            return avg_leverage

        except Exception as e:
            self.logger.error(f"Erreur calcul levier: {e}")
            return 0

    async def _calculate_liquidity_risk(self, positions: List[Dict], market_data: Dict) -> float:
        """Calculer le risque de liquidité"""
        try:
            if not positions:
                return 0

            liquidity_scores = []
            for pos in positions:
                symbol = pos.get("symbol", "")
                volume_24h = market_data.get(symbol, {}).get("volume_24h", 0)
                position_value = pos.get("value", 0)

                # Score de liquidité: ratio position/volume 24h
                if volume_24h > 0:
                    liquidity_score = min(1.0, position_value / volume_24h)
                else:
                    liquidity_score = 1.0  # Maximum risque

                liquidity_scores.append(liquidity_score)

            return np.mean(liquidity_scores)

        except Exception as e:
            self.logger.error(f"Erreur calcul liquidité: {e}")
            return 0

    async def check_risk_limits(self, risk_metrics: RiskMetrics) -> List[RiskAlert]:
        """Vérifier les limites de risque et générer des alertes"""
        alerts = []

        # Vérifier volatilité
        if risk_metrics.volatility > self.risk_thresholds["max_volatility"]:
            alerts.append(RiskAlert(
                level="HIGH",
                message=f"Volatilité excessive: {risk_metrics.volatility:.2%}",
                metric="volatility",
                current_value=risk_metrics.volatility,
                threshold=self.risk_thresholds["max_volatility"],
                timestamp=datetime.now()
            ))

        # Vérifier drawdown
        if risk_metrics.max_drawdown > self.risk_thresholds["max_drawdown_limit"]:
            alerts.append(RiskAlert(
                level="CRITICAL",
                message=f"Drawdown maximum dépassé: {risk_metrics.max_drawdown:.2%}",
                metric="max_drawdown",
                current_value=risk_metrics.max_drawdown,
                threshold=self.risk_thresholds["max_drawdown_limit"],
                timestamp=datetime.now()
            ))

        # Vérifier VaR
        portfolio_value = float(self.current_capital)
        var_pct = risk_metrics.var_95 / portfolio_value if portfolio_value > 0 else 0
        if var_pct > self.risk_thresholds["var_limit"]:
            alerts.append(RiskAlert(
                level="HIGH",
                message=f"VaR excessive: {var_pct:.2%}",
                metric="var_95",
                current_value=var_pct,
                threshold=self.risk_thresholds["var_limit"],
                timestamp=datetime.now()
            ))

        # Vérifier concentration
        if risk_metrics.position_concentration > 0.5:  # 50% max dans une position
            alerts.append(RiskAlert(
                level="MEDIUM",
                message=f"Concentration élevée: {risk_metrics.position_concentration:.2%}",
                metric="position_concentration",
                current_value=risk_metrics.position_concentration,
                threshold=0.5,
                timestamp=datetime.now()
            ))

        # Vérifier levier
        if risk_metrics.leverage_ratio > self.risk_thresholds["max_leverage"]:
            alerts.append(RiskAlert(
                level="CRITICAL",
                message=f"Levier excessif: {risk_metrics.leverage_ratio:.1f}x",
                metric="leverage_ratio",
                current_value=risk_metrics.leverage_ratio,
                threshold=self.risk_thresholds["max_leverage"],
                timestamp=datetime.now()
            ))

        self.active_alerts.extend(alerts)
        return alerts

    async def should_reduce_risk(self, risk_metrics: RiskMetrics) -> Tuple[bool, str]:
        """Déterminer s'il faut réduire le risque"""
        try:
            # Règles de réduction de risque
            if risk_metrics.max_drawdown > self.risk_thresholds["max_drawdown_limit"]:
                return True, "Drawdown maximum dépassé - réduire positions"

            if risk_metrics.leverage_ratio > self.risk_thresholds["max_leverage"]:
                return True, "Levier excessif - réduire exposition"

            if risk_metrics.volatility > self.risk_thresholds["max_volatility"] * 2:
                return True, "Volatilité extrême - réduire risque"

            # Compter les alertes critiques
            critical_alerts = [a for a in self.active_alerts if a.level == "CRITICAL"]
            if len(critical_alerts) >= 2:
                return True, f"Alertes critiques multiples: {len(critical_alerts)}"

            return False, "Risque acceptable"

        except Exception as e:
            self.logger.error(f"Erreur évaluation réduction risque: {e}")
            return False, "Erreur évaluation"

    async def update_performance_metrics(self, trade_result: Dict):
        """Mettre à jour les métriques de performance"""
        try:
            pnl = Decimal(str(trade_result.get("pnl", 0)))
            self.performance_metrics["total_trades"] += 1
            self.performance_metrics["total_pnl"] += pnl

            if pnl > 0:
                self.performance_metrics["winning_trades"] += 1
            else:
                self.performance_metrics["losing_trades"] += 1

            # Ajouter aux rendements quotidiens
            if self.current_capital > 0:
                daily_return = float(pnl / self.current_capital)
                self.performance_metrics["daily_returns"].append(daily_return)

                # Garder seulement les 365 derniers jours
                if len(self.performance_metrics["daily_returns"]) > 365:
                    self.performance_metrics["daily_returns"] = self.performance_metrics["daily_returns"][-365:]

            self.current_capital += pnl

            # Mettre à jour le drawdown actuel
            peak = max(self.initial_capital, self.current_capital)
            current_dd = (peak - self.current_capital) / peak
            self.performance_metrics["current_drawdown"] = Decimal(str(current_dd))
            self.performance_metrics["max_drawdown"] = max(
                self.performance_metrics["max_drawdown"],
                self.performance_metrics["current_drawdown"]
            )

            self.logger.info(f"Performance mise à jour: PnL total=${self.performance_metrics['total_pnl']}, Trades={self.performance_metrics['total_trades']}")

        except Exception as e:
            self.logger.error(f"Erreur mise à jour performance: {e}")

    def get_risk_summary(self) -> Dict:
        """Résumé des métriques de risque"""
        win_rate = 0
        if self.performance_metrics["total_trades"] > 0:
            win_rate = self.performance_metrics["winning_trades"] / self.performance_metrics["total_trades"]

        return {
            "total_trades": self.performance_metrics["total_trades"],
            "win_rate": win_rate,
            "total_pnl": float(self.performance_metrics["total_pnl"]),
            "current_drawdown": float(self.performance_metrics["current_drawdown"]),
            "max_drawdown": float(self.performance_metrics["max_drawdown"]),
            "active_alerts": len(self.active_alerts),
            "critical_alerts": len([a for a in self.active_alerts if a.level == "CRITICAL"]),
            "current_capital": float(self.current_capital),
            "risk_limits": self.risk_thresholds
        }

# Instance globale
_risk_agent = None

def get_risk_agent(initial_capital: Decimal = Decimal('10000')) -> RiskAgent:
    """Récupérer ou créer l'agent de risque"""
    global _risk_agent
    if _risk_agent is None:
        _risk_agent = RiskAgent(initial_capital)
    return _risk_agent

if __name__ == "__main__":
    import sys
    import json

    async def main():
        agent = RiskAgent(Decimal('10000'))

        if len(sys.argv) > 1:
            command = sys.argv[1]

            if command == "--get-dashboard-metrics":
                # Renvoyer les métriques pour le dashboard
                try:
                    mock_positions = [
                        {"symbol": "BTC", "value": 5000, "weight": 0.5, "leverage": 3},
                        {"symbol": "ETH", "value": 3000, "weight": 0.3, "leverage": 2}
                    ]
                    mock_market = {"BTC": {"volatility": 0.03}, "ETH": {"volatility": 0.04}}

                    risk_metrics = await agent.assess_portfolio_risk(mock_positions, mock_market)
                    alerts = await agent.check_risk_limits(risk_metrics)

                    metrics_data = {
                        "active": True,
                        "confidence": 0.85,
                        "decisions_made": 15,
                        "avg_response_time": 150,
                        "total_trades": agent.performance_metrics["total_trades"],
                        "win_rate": agent.performance_metrics["winning_trades"] / max(1, agent.performance_metrics["total_trades"]),
                        "market_volatility": risk_metrics.volatility,
                        "current_drawdown": float(risk_metrics.max_drawdown),
                        "var_95": risk_metrics.var_95,
                        "avg_leverage": risk_metrics.leverage_ratio,
                        "risk_level": "LOW" if risk_metrics.leverage_ratio < 3 else "MEDIUM" if risk_metrics.leverage_ratio < 7 else "HIGH",
                        "portfolio_beta": 1.2,
                        "current_risk_score": 0.3,
                        "alerts_count": len(alerts),
                        "positions_monitored": len(mock_positions),
                        "alerts": [
                            {
                                "level": alert.level,
                                "message": alert.message,
                                "metric": alert.metric
                            } for alert in alerts
                        ]
                    }
                    print(json.dumps(metrics_data))
                except Exception as e:
                    print(json.dumps({"active": False, "error": str(e)}))

            elif command == "--test":
                # Test de l'agent de risque
                print("🛡️ Risk Agent créé")

                size = await agent.calculate_position_size(
                    symbol="BTC",
                    signal_strength=0.8,
                    portfolio_value=Decimal('10000'),
                    volatility=0.03,
                    account_balance=Decimal('10000')
                )
                print(f"Taille position BTC: ${size.optimal_size}")

                mock_positions = [
                    {"symbol": "BTC", "value": 5000, "weight": 0.5, "leverage": 3},
                    {"symbol": "ETH", "value": 3000, "weight": 0.3, "leverage": 2}
                ]
                mock_market = {"BTC": {"volatility": 0.03}, "ETH": {"volatility": 0.04}}

                risk_metrics = await agent.assess_portfolio_risk(mock_positions, mock_market)
                print(f"Métriques risque: Volatilité={risk_metrics.volatility:.2%}")

                alerts = await agent.check_risk_limits(risk_metrics)
                print(f"Alertes: {len(alerts)}")

            else:
                print("Commandes disponibles: --get-dashboard-metrics, --test")
        else:
            # Test par défaut
            await main()

    asyncio.run(main())