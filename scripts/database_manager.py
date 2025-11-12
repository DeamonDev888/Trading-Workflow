#!/usr/bin/env python3
"""
[OK] NOVAQUOTE Database Manager
Built with love by Deamon Dev [ROCKET]

Script d'analyse, optimisation et maintenance de la database NOVAQUOTE.
Analyse la structure SQL, optimise les requêtes, maintient l'intégrité.
"""

import sqlite3
import os
// import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
// import hashlib

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "src" / "market_database" / "market_data.db"

# Tables principales de la database
MAIN_TABLES = [
    "ohlcv_data",
    "markets",
    "backtest_results",
    "btc_dominance"
]

# Requêtes de test de performance
PERFORMANCE_QUERIES = [
    {
        "name": "latest_ohlcv_btc",
        "query": "SELECT * FROM ohlcv_data WHERE symbol = 'BTC/USDT' ORDER BY timestamp DESC LIMIT 100",
        "description": "Dernières 100 bougies BTC"
    },
    {
        "name": "backtest_performance",
        "query": "SELECT strategy_name, AVG(win_rate) as avg_win_rate FROM backtest_results GROUP BY strategy_name ORDER BY avg_win_rate DESC LIMIT 10",
        "description": "Top 10 stratégies par win rate"
    },
    {
        "name": "market_volume_analysis",
        "query": "SELECT symbol, AVG(volume) as avg_volume FROM ohlcv_data WHERE timestamp >= datetime('now', '-30 days') GROUP BY symbol ORDER BY avg_volume DESC LIMIT 20",
        "description": "Volume moyen par symbole (30 derniers jours)"
    },
    {
        "name": "btc_dominance_trend",
        "query": "SELECT date(timestamp) as date, AVG(dominance_percentage) as avg_dominance FROM btc_dominance GROUP BY date(timestamp) ORDER BY date DESC LIMIT 30",
        "description": "Évolution dominance BTC (30 derniers jours)"
    }
]

class DatabaseManager:
    """Gestionnaire de database NOVAQUOTE"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.db_path = DB_PATH
        self.connection = None
        self.cursor = None

        print("🗄️ Database Manager initialized")
        print(f"📍 Database path: {self.db_path}")

    def connect(self) -> bool:
        """Établir la connexion à la database"""
        try:
            self.connection = sqlite3.connect(str(self.db_path))
            self.cursor = self.connection.cursor()
            print("✅ Connected to database")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

    def disconnect(self):
        """Fermer la connexion"""
        if self.connection:
            self.connection.close()
            print("✅ Database connection closed")

    def analyze_database_schema(self) -> Dict[str, Any]:
        """Analyser le schéma complet de la database"""
        print("\n🔍 Analyzing database schema...")

        schema_info = {
            "database_size": 0,
            "tables": {},
            "indexes": [],
            "constraints": [],
            "triggers": []
        }

        try:
            # Taille de la database
            if self.db_path.exists():
                schema_info["database_size"] = self.db_path.stat().st_size

            # Analyser chaque table principale
            for table_name in MAIN_TABLES:
                table_info = self._analyze_table(table_name)
                if table_info:
                    schema_info["tables"][table_name] = table_info

            # Récupérer les indexes
            self.cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND sql IS NOT NULL")
            schema_info["indexes"] = [{"name": row[0], "sql": row[1]} for row in self.cursor.fetchall()]

            # Récupérer les triggers
            self.cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='trigger'")
            schema_info["triggers"] = [{"name": row[0], "sql": row[1]} for row in self.cursor.fetchall()]

            print(f"📊 Analyzed {len(schema_info['tables'])} tables, {len(schema_info['indexes'])} indexes")

        except Exception as e:
            print(f"❌ Schema analysis error: {e}")
            schema_info["error"] = str(e)

        return schema_info

    def _analyze_table(self, table_name: str) -> Optional[Dict[str, Any]]:
        """Analyser une table spécifique"""
        try:
            # Schéma de la table
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            columns = self.cursor.fetchall()

            # Statistiques de données
            self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = self.cursor.fetchone()[0]

            # Taille estimée
            self.cursor.execute(f"SELECT SUM(LENGTH(sql)) FROM sqlite_master WHERE name='{table_name}'")
            size_estimate = self.cursor.fetchone()[0] or 0

            # Indexes de la table
            self.cursor.execute(f"PRAGMA index_list({table_name})")
            indexes = self.cursor.fetchall()

            return {
                "columns": [{"name": col[1], "type": col[2], "nullable": not col[3], "default": col[4], "primary_key": col[5]}
                           for col in columns],
                "row_count": row_count,
                "estimated_size": size_estimate,
                "indexes": [{"name": idx[1], "unique": idx[2], "origin": idx[3]} for idx in indexes]
            }

        except Exception as e:
            print(f"❌ Error analyzing table {table_name}: {e}")
            return None

    def optimize_query_performance(self) -> Dict[str, Any]:
        """Optimiser les performances des requêtes"""
        print("\n⚡ Optimizing query performance...")

        performance_results = {
            "query_tests": [],
            "index_recommendations": [],
            "optimization_suggestions": []
        }

        # Tester les requêtes de performance
        for query_info in PERFORMANCE_QUERIES:
            result = self._test_query_performance(query_info)
            performance_results["query_tests"].append(result)

            # Analyser et suggérer des optimisations
            if result["execution_time"] > 0.5:  # Plus de 500ms
                performance_results["optimization_suggestions"].append({
                    "query": query_info["name"],
                    "issue": f"Slow execution: {result['execution_time']:.3f}s",
                    "suggestion": self._suggest_query_optimization(query_info["query"])
                })

        # Analyser l'utilisation des indexes
        index_analysis = self._analyze_index_usage()
        performance_results["index_recommendations"] = index_analysis

        print(f"🧪 Tested {len(performance_results['query_tests'])} queries")
        print(f"💡 Generated {len(performance_results['optimization_suggestions'])} optimization suggestions")

        return performance_results

    def _test_query_performance(self, query_info: Dict[str, Any]) -> Dict[str, Any]:
        """Tester la performance d'une requête"""
        try:
            start_time = time.time()
            self.cursor.execute(query_info["query"])
            results = self.cursor.fetchall()
            execution_time = time.time() - start_time

            return {
                "query_name": query_info["name"],
                "description": query_info["description"],
                "execution_time": execution_time,
                "result_count": len(results),
                "status": "fast" if execution_time < 0.1 else "slow" if execution_time > 0.5 else "acceptable"
            }

        except Exception as e:
            return {
                "query_name": query_info["name"],
                "error": str(e),
                "execution_time": 0,
                "status": "failed"
            }

    def _suggest_query_optimization(self, query: str) -> str:
        """Suggérer des optimisations pour une requête"""
        suggestions = []

        # Analyser la requête pour des patterns d'optimisation
        if "ORDER BY" in query and "LIMIT" in query:
            suggestions.append("Consider adding index on ORDER BY column")

        if "GROUP BY" in query:
            suggestions.append("Ensure GROUP BY column has an index")

        if "WHERE" in query and "timestamp" in query:
            suggestions.append("Add index on timestamp column for time-based queries")

        if "AVG(" in query or "SUM(" in query:
            suggestions.append("Consider pre-computed aggregates for frequent calculations")

        return "; ".join(suggestions) if suggestions else "Review query structure and add appropriate indexes"

    def _analyze_index_usage(self) -> List[Dict[str, Any]]:
        """Analyser l'utilisation des indexes"""
        recommendations = []

        try:
            # Vérifier les indexes manquants pour les requêtes fréquentes
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in self.cursor.fetchall()]

            for table in tables:
                if table in MAIN_TABLES:
                    # Vérifier les indexes existants
                    self.cursor.execute(f"PRAGMA index_list({table})")
                    existing_indexes = [row[1] for row in self.cursor.fetchall()]

                    # Suggestions basées sur les patterns d'usage
                    if table == "ohlcv_data":
                        if not any("symbol_time" in idx for idx in existing_indexes):
                            recommendations.append({
                                "table": table,
                                "recommendation": "Add composite index on (symbol, timestamp)",
                                "benefit": "Optimize time-series queries"
                            })
                        if not any("exchange_symbol" in idx for idx in existing_indexes):
                            recommendations.append({
                                "table": table,
                                "recommendation": "Add index on (exchange, symbol)",
                                "benefit": "Optimize exchange-specific queries"
                            })

                    elif table == "backtest_results":
                        if not any("strategy" in idx for idx in existing_indexes):
                            recommendations.append({
                                "table": table,
                                "recommendation": "Add index on strategy_name",
                                "benefit": "Optimize strategy analysis queries"
                            })

        except Exception as e:
            print(f"❌ Index analysis error: {e}")

        return recommendations

    def maintain_data_integrity(self) -> Dict[str, Any]:
        """Maintenir l'intégrité des données"""
        print("\n🔒 Maintaining data integrity...")

        integrity_results = {
            "constraint_checks": [],
            "duplicate_analysis": [],
            "referential_integrity": [],
            "data_quality_issues": []
        }

        try:
            # Vérifier les contraintes d'intégrité
            for table_name in MAIN_TABLES:
                constraints = self._check_table_constraints(table_name)
                integrity_results["constraint_checks"].extend(constraints)

            # Analyser les doublons
            duplicates = self._analyze_duplicates()
            integrity_results["duplicate_analysis"] = duplicates

            # Vérifier l'intégrité référentielle
            referential_issues = self._check_referential_integrity()
            integrity_results["referential_integrity"] = referential_issues

            # Analyser la qualité des données
            quality_issues = self._analyze_data_quality()
            integrity_results["data_quality_issues"] = quality_issues

            print(f"🔍 Checked {len(integrity_results['constraint_checks'])} constraints")
            print(f"🔄 Found {len(integrity_results['duplicate_analysis'])} duplicate issues")
            print(f"🔗 Checked {len(integrity_results['referential_integrity'])} referential links")

        except Exception as e:
            print(f"❌ Integrity check error: {e}")
            integrity_results["error"] = str(e)

        return integrity_results

    def _check_table_constraints(self, table_name: str) -> List[Dict[str, Any]]:
        """Vérifier les contraintes d'une table"""
        constraints = []

        try:
            # Vérifier les valeurs NULL inappropriées
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            columns = self.cursor.fetchall()

            for col in columns:
                col_name, col_type, not_null, default_value, pk = col[1], col[2], col[3], col[4], col[5]

                if not_null and not pk:  # Vérifier les colonnes NOT NULL non-PK
                    self.cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {col_name} IS NULL")
                    null_count = self.cursor.fetchone()[0]

                    if null_count > 0:
                        constraints.append({
                            "table": table_name,
                            "column": col_name,
                            "issue": f"{null_count} NULL values in NOT NULL column",
                            "severity": "high"
                        })

            # Vérifier les contraintes d'unicité
            if table_name == "ohlcv_data":
                self.cursor.execute("""
                    SELECT symbol, exchange, timeframe, timestamp, COUNT(*)
                    FROM ohlcv_data
                    GROUP BY symbol, exchange, timeframe, timestamp
                    HAVING COUNT(*) > 1
                """)
                duplicates = self.cursor.fetchall()

                if duplicates:
                    constraints.append({
                        "table": table_name,
                        "issue": f"{len(duplicates)} duplicate timestamp entries",
                        "severity": "high"
                    })

        except Exception as e:
            constraints.append({
                "table": table_name,
                "issue": f"Constraint check error: {str(e)}",
                "severity": "error"
            })

        return constraints

    def _analyze_duplicates(self) -> List[Dict[str, Any]]:
        """Analyser les données dupliquées"""
        duplicates = []

        try:
            # Vérifier les marchés dupliqués
            self.cursor.execute("""
                SELECT symbol, exchange, COUNT(*)
                FROM markets
                GROUP BY symbol, exchange
                HAVING COUNT(*) > 1
            """)
            market_duplicates = self.cursor.fetchall()

            if market_duplicates:
                duplicates.append({
                    "table": "markets",
                    "issue": f"{len(market_duplicates)} duplicate market entries",
                    "details": market_duplicates[:5]  # Premiers 5 exemples
                })

        except Exception as e:
            duplicates.append({
                "table": "unknown",
                "issue": f"Duplicate analysis error: {str(e)}"
            })

        return duplicates

    def _check_referential_integrity(self) -> List[Dict[str, Any]]:
        """Vérifier l'intégrité référentielle"""
        issues = []

        try:
            # Vérifier que les données OHLCV référencent des marchés existants
            self.cursor.execute("""
                SELECT COUNT(*)
                FROM ohlcv_data o
                LEFT JOIN markets m ON o.symbol = m.symbol AND o.exchange = m.exchange
                WHERE m.id IS NULL
            """)
            orphaned_ohlcv = self.cursor.fetchone()[0]

            if orphaned_ohlcv > 0:
                issues.append({
                    "issue": f"{orphaned_ohlcv} OHLCV records reference non-existent markets",
                    "severity": "medium"
                })

        except Exception as e:
            issues.append({
                "issue": f"Referential integrity check error: {str(e)}",
                "severity": "error"
            })

        return issues

    def _analyze_data_quality(self) -> List[Dict[str, Any]]:
        """Analyser la qualité des données"""
        quality_issues = []

        try:
            # Vérifier les prix OHLCV incohérents (high < low, etc.)
            self.cursor.execute("""
                SELECT COUNT(*)
                FROM ohlcv_data
                WHERE high < low OR open < 0 OR close < 0 OR volume < 0
            """)
            invalid_ohlcv = self.cursor.fetchone()[0]

            if invalid_ohlcv > 0:
                quality_issues.append({
                    "table": "ohlcv_data",
                    "issue": f"{invalid_ohlcv} records with invalid OHLCV values",
                    "severity": "high"
                })

            # Vérifier les dates futures
            self.cursor.execute("""
                SELECT COUNT(*)
                FROM ohlcv_data
                WHERE timestamp > datetime('now')
            """)
            future_dates = self.cursor.fetchone()[0]

            if future_dates > 0:
                quality_issues.append({
                    "table": "ohlcv_data",
                    "issue": f"{future_dates} records with future timestamps",
                    "severity": "medium"
                })

        except Exception as e:
            quality_issues.append({
                "issue": f"Data quality analysis error: {str(e)}",
                "severity": "error"
            })

        return quality_issues

    def generate_performance_report(self, schema_info: Dict, performance_results: Dict,
                                  integrity_results: Dict) -> str:
        """Générer un rapport complet de performance"""
        print("\n📋 Generating performance report...")

        report = f"""# 🗄️ NOVAQUOTE Database Performance Report
**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Database Overview

### Size & Structure
- **Database size:** {schema_info.get('database_size', 0) / 1024:.1f} KB
- **Tables:** {len(schema_info.get('tables', {}))}
- **Indexes:** {len(schema_info.get('indexes', []))}
- **Triggers:** {len(schema_info.get('triggers', []))}

### Tables Summary
"""

        # Résumé des tables
        for table_name, table_info in schema_info.get('tables', {}).items():
            report += f"#### {table_name}\n"
            report += f"- **Rows:** {table_info.get('row_count', 0):,}\n"
            report += f"- **Columns:** {len(table_info.get('columns', []))}\n"
            report += f"- **Indexes:** {len(table_info.get('indexes', []))}\n\n"

        # Résultats de performance
        report += "## ⚡ Query Performance Results\n\n"

        for query_result in performance_results.get('query_tests', []):
            status_emoji = {
                "fast": "✅",
                "acceptable": "⚠️",
                "slow": "❌",
                "failed": "💥"
            }.get(query_result.get('status'), "❓")

            report += f"### {status_emoji} {query_result['query_name']}\n"
            report += f"- **Description:** {query_result['description']}\n"
            report += f"- **Execution time:** {query_result.get('execution_time', 0):.3f}s\n"
            report += f"- **Results:** {query_result.get('result_count', 0)} rows\n\n"

        # Recommandations d'optimisation
        if performance_results.get('optimization_suggestions'):
            report += "## 💡 Optimization Recommendations\n\n"
            for suggestion in performance_results['optimization_suggestions']:
                report += f"### {suggestion['query']}\n"
                report += f"- **Issue:** {suggestion['issue']}\n"
                report += f"- **Suggestion:** {suggestion['suggestion']}\n\n"

        # Recommandations d'indexes
        if performance_results.get('index_recommendations'):
            report += "## 🏷️ Index Recommendations\n\n"
            for rec in performance_results['index_recommendations']:
                report += f"### {rec['table']}\n"
                report += f"- **Recommendation:** {rec['recommendation']}\n"
                report += f"- **Benefit:** {rec['benefit']}\n\n"

        # Résultats d'intégrité
        report += "## 🔒 Data Integrity Results\n\n"

        total_issues = (len(integrity_results.get('constraint_checks', [])) +
                       len(integrity_results.get('duplicate_analysis', [])) +
                       len(integrity_results.get('referential_integrity', [])) +
                       len(integrity_results.get('data_quality_issues', [])))

        report += f"**Total integrity issues found:** {total_issues}\n\n"

        # Détails des problèmes
        for category, issues in integrity_results.items():
            if issues:
                report += f"### {category.replace('_', ' ').title()}\n"
                for issue in issues:
                    severity_emoji = {
                        "high": "🔴",
                        "medium": "🟡",
                        "low": "🟢",
                        "error": "💥"
                    }.get(issue.get('severity', 'medium'), "⚠️")

                    report += f"- {severity_emoji} {issue.get('issue', 'Unknown issue')}\n"
                report += "\n"

        # Recommandations finales
        report += "## 🎯 Action Plan\n\n"

        if total_issues > 0:
            report += "### Immediate Actions Required\n"
            report += "1. Review and fix data integrity issues\n"
            report += "2. Implement recommended indexes\n"
            report += "3. Optimize slow queries\n"
            report += "4. Clean up duplicate data\n\n"

        report += "### Maintenance Recommendations\n"
        report += "1. Run this analysis weekly\n"
        report += "2. Monitor query performance regularly\n"
        report += "3. Update indexes as data grows\n"
        report += "4. Archive old data periodically\n\n"

        report += "---\n*Report generated by NOVAQUOTE Database Manager*"

        return report

    def save_report(self, report: str, filename: Optional[str] = None):
        """Sauvegarder le rapport"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"database_performance_{timestamp}.md"

        reports_dir = self.project_root / "reports" / "database"
        reports_dir.mkdir(parents=True, exist_ok=True)

        report_path = reports_dir / filename

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"💾 Report saved: {report_path}")
        return report_path

    def run_full_analysis(self):
        """Exécuter l'analyse complète de la database"""
        print("=" * 80)
        print("🗄️ NOVAQUOTE Database Manager - Full Analysis")
        print("=" * 80)

        if not self.connect():
            print("❌ Cannot proceed without database connection")
            return None

        try:
            # 1. Analyser le schéma
            schema_info = self.analyze_database_schema()

            # 2. Optimiser les performances
            performance_results = self.optimize_query_performance()

            # 3. Maintenir l'intégrité
            integrity_results = self.maintain_data_integrity()

            # 4. Générer le rapport
            report = self.generate_performance_report(
                schema_info, performance_results, integrity_results
            )

            # 5. Sauvegarder le rapport
            report_path = self.save_report(report)

            print("\n" + "=" * 80)
            print("✅ ANALYSIS COMPLETE")
            print("=" * 80)
            print(f"📄 Full report: {report_path}")
            print("\n🎯 Summary:")
            print(f"   • Database size: {schema_info.get('database_size', 0) / 1024:.1f} KB")
            print(f"   • Tables analyzed: {len(schema_info.get('tables', {}))}")
            print(f"   • Queries tested: {len(performance_results.get('query_tests', []))}")
            print(f"   • Integrity issues: {len(integrity_results.get('constraint_checks', [])) + len(integrity_results.get('duplicate_analysis', [])) + len(integrity_results.get('referential_integrity', [])) + len(integrity_results.get('data_quality_issues', []))}")
            print(f"   • Optimization suggestions: {len(performance_results.get('optimization_suggestions', []))}")

            return {
                "schema_info": schema_info,
                "performance_results": performance_results,
                "integrity_results": integrity_results,
                "report_path": report_path
            }

        finally:
            self.disconnect()


def main():
    """Point d'entrée principal"""
    manager = DatabaseManager()
    results = manager.run_full_analysis()

    if results:
        print("\n" + "=" * 80)
        print("🎉 Database analysis completed successfully!")
        print("=" * 80)
    else:
        print("\n❌ Database analysis failed!")
        exit(1)


if __name__ == "__main__":
    main()
