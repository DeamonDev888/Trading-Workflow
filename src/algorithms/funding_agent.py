#!/usr/bin/env python3
"""
Funding Agent - Agent de trading de funding rate arbitrage
Exploite les différences de taux de funding entre les exchanges
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List

import numpy as np
import requests


@dataclass
class FundingRate:
    exchange: str
    symbol: str
    rate: float
    next_funding_time: datetime
    predicted_rate: float
    annualized_rate: float


@dataclass
class ArbitrageOpportunity:
    symbol: str
    exchange_long: str
    exchange_short: str
    long_rate: float
    short_rate: float
    spread: float
    annualized_yield: float
    confidence: float
    min_amount: Decimal
    max_amount: Decimal


@dataclass
class FundingPosition:
    symbol: str
    exchange: str
    side: str  # long/short
    size: Decimal
    entry_rate: float
    current_rate: float
    accrued_funding: Decimal
    entry_time: datetime


class FundingAgent:
    """Agent spécialisé dans le funding rate arbitrage"""

    def __init__(self, initial_capital: Decimal = Decimal("10000")):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.logger = logging.getLogger("FundingAgent")

        # Exchanges supportés
        self.exchanges = {
            "hyperliquid": {
                "name": "HyperLiquid",
                "api_url": "https://api.hyperliquid.xyz/info",
                "funding_interval": 1,  # heures
                "fee_rate": 0.0002,  # 0.02% fee
                "min_amount": 10,
            },
            "binance": {
                "name": "Binance Futures",
                "api_url": "https://fapi.binance.com/fapi/v1",
                "funding_interval": 8,
                "fee_rate": 0.0004,
                "min_amount": 5,
            },
            "bybit": {
                "name": "Bybit",
                "api_url": "https://api.bybit.com/v5/market",
                "funding_interval": 8,
                "fee_rate": 0.00055,
                "min_amount": 1,
            },
        }

        # Symboles supportés pour funding arbitrage
        self.funding_symbols = [
            "BTC",
            "ETH",
            "SOL",
            "BNB",
            "AVAX",
            "MATIC",
            "DOT",
            "LINK",
            "UNI",
            "AAVE",
            "SUSHI",
            "CRV",
            "LDO",
            "INJ",
            "ATOM",
            "OP",
        ]

        # Seuils de trading
        self.min_funding_spread = 0.0001  # 0.01% spread minimum
        self.max_position_size_pct = 0.2  # 20% max du capital par position
        self.max_total_exposure = 0.6  # 60% max exposition totale
        self.min_yield_threshold = 0.001  # 0.1% yield minimum annualisé

        # Positions actives
        self.active_positions: List[FundingPosition] = []
        self.closed_positions: List[FundingPosition] = []

        # Historique des taux
        self.funding_history: Dict[str, List[FundingRate]] = {}

    async def get_funding_rates(self) -> Dict[str, List[FundingRate]]:
        """Récupérer les taux de funding de tous les exchanges"""
        all_rates = {}

        for exchange_id, exchange_config in self.exchanges.items():
            try:
                rates = await self._fetch_exchange_funding_rates(exchange_id)
                all_rates[exchange_id] = rates
                self.logger.info(f"📊 {exchange_config['name']}: {len(rates)} taux récupérés")
            except Exception as e:
                self.logger.error(f"Erreur récupération taux {exchange_id}: {e}")
                all_rates[exchange_id] = []

        return all_rates

    async def _fetch_exchange_funding_rates(self, exchange_id: str) -> List[FundingRate]:
        """Récupérer les taux de funding d'un exchange spécifique"""
        try:
            if exchange_id == "hyperliquid":
                return await self._fetch_hyperliquid_funding()
            elif exchange_id == "binance":
                return await self._fetch_binance_funding()
            elif exchange_id == "bybit":
                return await self._fetch_bybit_funding()
            else:
                return []

        except Exception as e:
            self.logger.error(f"Erreur fetching {exchange_id}: {e}")
            return []

    async def _fetch_hyperliquid_funding(self) -> List[FundingRate]:
        """Récupérer les taux HyperLiquid"""
        try:
            # Simuler pour l'instant - à remplacer avec vraie API
            mock_rates = []
            for symbol in self.funding_symbols:
                rate = np.random.normal(0.0001, 0.0005)  # Taux aléatoire autour de 0.01%
                next_funding = datetime.now() + timedelta(hours=1)

                mock_rates.append(
                    FundingRate(
                        exchange="hyperliquid",
                        symbol=symbol,
                        rate=float(rate),
                        next_funding_time=next_funding,
                        predicted_rate=float(rate * np.random.normal(1.0, 0.1)),
                        annualized_rate=float(rate * 24 * 365),  # Toutes les heures
                    )
                )

            return mock_rates

        except Exception as e:
            self.logger.error(f"Erreur HyperLiquid funding: {e}")
            return []

    async def _fetch_binance_funding(self) -> List[FundingRate]:
        """Récupérer les taux Binance"""
        try:
            url = "https://fapi.binance.com/fapi/v1/premiumIndex"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                rates = []

                for item in data:
                    symbol = item.get("symbol", "").replace("USDT", "")
                    if symbol in self.funding_symbols:
                        rate = float(item.get("lastFundingRate", 0))
                        next_funding = int(item.get("nextFundingTime", 0))

                        rates.append(
                            FundingRate(
                                exchange="binance",
                                symbol=symbol,
                                rate=rate,
                                next_funding_time=datetime.fromtimestamp(next_funding / 1000),
                                predicted_rate=rate,  # Binance ne fournit pas de prédiction
                                annualized_rate=rate * (365 * 3),  # 8 heures = 3 fois par jour
                            )
                        )

                return rates

        except Exception as e:
            self.logger.error(f"Erreur Binance funding: {e}")
            return []

    async def _fetch_bybit_funding(self) -> List[FundingRate]:
        """Récupérer les taux Bybit"""
        try:
            url = "https://api.bybit.com/v5/market/funding/history?category=linear&limit=100"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                rates = []

                if data.get("retCode") == 0:
                    for item in data.get("result", {}).get("list", []):
                        symbol = item.get("symbol", "").replace("USDT", "")
                        if symbol in self.funding_symbols:
                            rate = float(item.get("fundingRate", 0))
                            next_funding = int(item.get("fundingRateTimestamp", 0))

                            rates.append(
                                FundingRate(
                                    exchange="bybit",
                                    symbol=symbol,
                                    rate=rate,
                                    next_funding_time=datetime.fromtimestamp(next_funding / 1000),
                                    predicted_rate=rate,
                                    annualized_rate=rate * (365 * 3),  # 8 heures = 3 fois par jour
                                )
                            )

                return rates

        except Exception as e:
            self.logger.error(f"Erreur Bybit funding: {e}")
            return []

    async def identify_arbitrage_opportunities(
        self, funding_rates: Dict[str, List[FundingRate]]
    ) -> List[ArbitrageOpportunity]:
        """Identifier les opportunités d'arbitrage de funding"""
        opportunities = []

        # Combiner tous les taux par symbole
        symbol_rates = {}
        for exchange_id, rates in funding_rates.items():
            for rate in rates:
                if rate.symbol not in symbol_rates:
                    symbol_rates[rate.symbol] = {}
                symbol_rates[rate.symbol][exchange_id] = rate

        # Analyser chaque symbole
        for symbol, exchanges_data in symbol_rates.items():
            if len(exchanges_data) < 2:
                continue  # Besoin d'au moins 2 exchanges

            # Trouver les meilleures combinaisons long/short
            for exchange_long, rate_long in exchanges_data.items():
                for exchange_short, rate_short in exchanges_data.items():
                    if exchange_long == exchange_short:
                        continue

                    spread = rate_short.rate - rate_long.rate
                    if spread < self.min_funding_spread:
                        continue

                    # Calculer le rendement annualisé
                    annualized_yield = spread * 365 * 24  # Toutes les heures

                    # Soustraire les fees
                    total_fees = (
                        self.exchanges[exchange_long]["fee_rate"]
                        + self.exchanges[exchange_short]["fee_rate"]
                    )
                    net_yield = annualized_yield - (total_fees * 365 * 24)

                    if net_yield < self.min_yield_threshold:
                        continue

                    # Calculer la confiance basée sur la stabilité des taux
                    confidence = self._calculate_confidence(rate_long, rate_short)

                    # Calculer les tailles de position
                    min_amount = max(
                        self.exchanges[exchange_long]["min_amount"],
                        self.exchanges[exchange_short]["min_amount"],
                    )
                    max_amount = self.current_capital * Decimal(str(self.max_position_size_pct))

                    opportunities.append(
                        ArbitrageOpportunity(
                            symbol=symbol,
                            exchange_long=exchange_long,
                            exchange_short=exchange_short,
                            long_rate=rate_long.rate,
                            short_rate=rate_short.rate,
                            spread=spread,
                            annualized_yield=net_yield,
                            confidence=confidence,
                            min_amount=Decimal(str(min_amount)),
                            max_amount=max_amount,
                        )
                    )

        # Trier par rendement décroissant
        opportunities.sort(key=lambda x: x.annualized_yield, reverse=True)
        return opportunities[:10]  # Top 10 opportunités

    def _calculate_confidence(self, rate_long: FundingRate, rate_short: FundingRate) -> float:
        """Calculer la confiance dans l'opportunité d'arbitrage"""
        try:
            # Facteurs de confiance
            spread_confidence = min(
                1.0, (rate_short.rate - rate_long.rate) / 0.001
            )  # Spread vs 0.1%
            time_confidence = 1.0  # Les deux ont des intervalles similaires

            # Prédiction de stabilité
            stability_long = 1.0 - abs(rate_long.predicted_rate - rate_long.rate) / max(
                abs(rate_long.rate), 0.0001
            )
            stability_short = 1.0 - abs(rate_short.predicted_rate - rate_short.rate) / max(
                abs(rate_short.rate), 0.0001
            )

            confidence = (
                spread_confidence + time_confidence + stability_long + stability_short
            ) / 4
            return max(0.0, min(1.0, confidence))

        except Exception as e:
            self.logger.error(f"Erreur calcul confiance: {e}")
            return 0.5

    async def execute_arbitrage(self, opportunity: ArbitrageOpportunity) -> bool:
        """Exécuter une opportunité d'arbitrage"""
        try:
            self.logger.info(f"🔄 Exécution arbitrage: {opportunity.symbol}")

            # Calculer la taille de position optimale
            position_size = min(
                opportunity.max_amount,
                self.current_capital * Decimal("0.1"),  # 10% max par trade
                opportunity.min_amount * Decimal("2"),  # Au moins 2x le minimum
            )

            # Vérifier l'exposition totale
            current_exposure = sum(pos.size for pos in self.active_positions)
            if current_exposure + position_size > self.current_capital * Decimal(
                str(self.max_total_exposure)
            ):
                self.logger.warning("Exposition maximale atteinte")
                return False

            # Exécuter les trades (simulation pour l'instant)
            success_long = await self._execute_position_trade(
                opportunity.exchange_long, opportunity.symbol, "long", position_size
            )

            success_short = await self._execute_position_trade(
                opportunity.exchange_short, opportunity.symbol, "short", position_size
            )

            if success_long and success_short:
                # Enregistrer les positions
                self.active_positions.append(
                    FundingPosition(
                        symbol=opportunity.symbol,
                        exchange=opportunity.exchange_long,
                        side="long",
                        size=position_size,
                        entry_rate=opportunity.long_rate,
                        current_rate=opportunity.long_rate,
                        accrued_funding=Decimal("0"),
                        entry_time=datetime.now(),
                    )
                )

                self.active_positions.append(
                    FundingPosition(
                        symbol=opportunity.symbol,
                        exchange=opportunity.exchange_short,
                        side="short",
                        size=position_size,
                        entry_rate=opportunity.short_rate,
                        current_rate=opportunity.short_rate,
                        accrued_funding=Decimal("0"),
                        entry_time=datetime.now(),
                    )
                )

                self.logger.info(
                    f"✅ Arbitrage exécuté: {opportunity.symbol} - Yield: {opportunity.annualized_yield:.2%}"
                )
                return True
            else:
                self.logger.error("❌ Échec exécution arbitrage")
                return False

        except Exception as e:
            self.logger.error(f"Erreur exécution arbitrage: {e}")
            return False

    async def _execute_position_trade(
        self, exchange: str, symbol: str, side: str, size: Decimal
    ) -> bool:
        """Exécuter un trade de position (simulation)"""
        try:
            # Simuler l'exécution du trade
            self.logger.info(f"📈 Trade {side} {size} {symbol} sur {exchange}")
            return True

        except Exception as e:
            self.logger.error(f"Erreur trade {exchange}: {e}")
            return False

    async def monitor_funding_positions(self):
        """Surveiller et mettre à jour les positions de funding"""
        try:
            current_rates = await self.get_funding_rates()

            for position in self.active_positions:
                # Trouver le taux actuel pour cette position
                exchange_rates = current_rates.get(position.exchange, [])
                current_rate = None

                for rate in exchange_rates:
                    if rate.symbol == position.symbol:
                        current_rate = rate
                        break

                if current_rate:
                    # Calculer le funding accumulé
                    time_delta = (
                        datetime.now() - position.entry_time
                    ).total_seconds() / 3600  # heures
                    funding_earned = (
                        position.size * Decimal(str(current_rate.rate)) * Decimal(str(time_delta))
                    )

                    position.current_rate = current_rate.rate
                    position.accrued_funding += funding_earned

                    # Vérifier s'il faut fermer la position
                    should_close = await self._should_close_position(position, current_rate)
                    if should_close:
                        await self.close_position(position)

        except Exception as e:
            self.logger.error(f"Erreur monitoring positions: {e}")

    async def _should_close_position(
        self, position: FundingPosition, current_rate: FundingRate
    ) -> bool:
        """Déterminer s'il faut fermer une position"""
        try:
            # Fermer si le spread s'est inversé
            if position.side == "long" and current_rate.rate < -0.0001:
                return True
            if position.side == "short" and current_rate.rate > 0.0001:
                return True

            # Fermer après 24h ou si le profit cible est atteint
            time_held = datetime.now() - position.entry_time
            if time_held > timedelta(hours=24):
                return True

            # Fermer si perte maximale
            if position.accrued_funding < -position.size * Decimal("0.01"):  # 1% max perte
                return True

            return False

        except Exception as e:
            self.logger.error(f"Erreur décision fermeture: {e}")
            return False

    async def close_position(self, position: FundingPosition):
        """Fermer une position de funding"""
        try:
            self.logger.info(f"🔒 Fermeture position: {position.symbol} {position.side}")

            # Simuler la fermeture
            success = True  # await self._execute_close_trade(position)

            if success:
                self.active_positions.remove(position)
                self.closed_positions.append(position)

                # Mettre à jour le capital
                self.current_capital += position.accrued_funding

                self.logger.info(f"✅ Position fermée - PnL funding: ${position.accrued_funding}")

        except Exception as e:
            self.logger.error(f"Erreur fermeture position: {e}")

    def get_funding_summary(self) -> Dict:
        """Résumé des performances de funding arbitrage"""
        total_accrued = sum(pos.accrued_funding for pos in self.active_positions)
        closed_pnl = sum(pos.accrued_funding for pos in self.closed_positions)

        return {
            "active_positions": len(self.active_positions),
            "closed_positions": len(self.closed_positions),
            "total_accrued_funding": float(total_accrued),
            "realized_pnl": float(closed_pnl),
            "current_capital": float(self.current_capital),
            "total_return": float(
                (self.current_capital - self.initial_capital) / self.initial_capital
            ),
            "active_exposure": float(sum(pos.size for pos in self.active_positions)),
        }


# Instance globale
_funding_agent = None


def get_funding_agent(initial_capital: Decimal = Decimal("10000")) -> FundingAgent:
    """Récupérer ou créer l'agent de funding"""
    global _funding_agent
    if _funding_agent is None:
        _funding_agent = FundingAgent(initial_capital)
    return _funding_agent


if __name__ == "__main__":
    import json
    import sys

    async def main():
        agent = FundingAgent(Decimal("10000"))

        if len(sys.argv) > 1:
            command = sys.argv[1]

            if command == "--get-dashboard-summary":
                # Renvoyer le résumé pour le dashboard
                try:
                    summary = agent.get_funding_summary()
                    summary_data = {
                        "active": True,
                        "confidence": 0.78,
                        "active_positions": summary["active_positions"],
                        "accrued_funding": summary["total_accrued_funding"],
                        "best_yield": 0.025,  # Test data
                        "active_opportunities": 3,
                        "total_exposure": summary["active_exposure"],
                        "current_rates": {"BTC": 0.0001, "ETH": 0.00015, "SOL": 0.0002},
                    }
                    print(json.dumps(summary_data))
                except Exception as e:
                    print(json.dumps({"active": False, "error": str(e)}))

            elif command == "--test":
                # Test de l'agent de funding
                print("💰 Funding Agent créé")

                rates = await agent.get_funding_rates()
                print(f"Taux récupérés: {sum(len(r) for r in rates.values())}")

                opportunities = await agent.identify_arbitrage_opportunities(rates)
                print(f"Opportunités trouvées: {len(opportunities)}")

                if opportunities:
                    best = opportunities[0]
                    print(
                        f"Meilleure opportunité: {best.symbol} - Yield: {best.annualized_yield:.2%}"
                    )

                await agent.monitor_funding_positions()
                summary = agent.get_funding_summary()
                print(f"Résumé funding: {summary}")

            else:
                print("Commandes disponibles: --get-dashboard-summary, --test")
        else:
            # Test par défaut
            await main()

    asyncio.run(main())
