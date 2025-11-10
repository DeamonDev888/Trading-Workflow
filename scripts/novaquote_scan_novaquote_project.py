"""
NOVAQUOTE SCAN NOVAQUOTE PROJECT
Scanner SPÉCIALISÉ et DÉDIÉ au projet NovaQuote Trading
V5.0 - Expertise complète de l'écosystème NovaQuote
"""

import ast
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

class NovaQuoteProjectScanner:
    """Scanner 100% dédié au projet NovaQuote Trading"""

    def __init__(self):
        self.novaquote_structure = {
            'agents': [
                'src/agents/master_agent.py',
                'src/agents/strategy_agent.py',
                'src/agents/risk_agent.py',
                'src/agents/funding_agent.py',
                'src/agents/data_aggregator.py',
                'src/agents/manager.py',
                'src/agents/base_agent.py',
                'src/agents/intelligent_backtest_optimizer.py',
                'src/agents/automatic_coin_rotator.py',
                'src/agents/sentiment_analysis_agent.py',
                'src/agents/volatility_tracker.py',
                'src/agents/liquidity_tracker.py',
                'src/agents/claude_code_integration.py',
                'src/agents/claude_code_orchestrator.py',
                'src/agents/persistent_agent_orchestrator.py',
                'src/agents/reliability_monitor.py'
            ],
            'algorithms': [
                'src/algorithms/funding_agent.py',
                'src/algorithms/hyperliquid_agent.py',
                'src/algorithms/hyperliquid_mainnet_agent.py',
                'src/algorithms/portfolio_manager.py',
                'src/algorithms/real_funding_agent.py',
                'src/algorithms/real_market_agent.py',
                'src/algorithms/real_risk_agent.py',
                'src/algorithms/risk_agent.py'
            ],
            'hyperliquid': [
                'src/hyperliquid/client.py',
                'src/hyperliquid/hyperliquid-api.js',
                'src/hyperliquid/hyperliquid-signature.js',
                'src/hyperliquid/hyperliquid-websocket.js',
                'src/hyperliquid/signing.py',
                'src/hyperliquid/types.py',
                'src/hyperliquid/websocket.py'
            ],
            'models': [
                'src/models/base_model.py',
                'src/models/claude_model.py',
                'src/models/deepseek_model.py',
                'src/models/gemini_model.py',
                'src/models/groq_model.py',
                'src/models/model_factory.py',
                'src/models/ollama_model.py',
                'src/models/openai_model.py',
                'src/models/xai_model.py',
                'src/models/zai_model.py'
            ],
            'wallet': [
                'src/wallet/__init__.py',
                'src/wallet/api_wallet_manager.py',
                'src/wallet/permission_controller.py',
                'src/wallet/signature_engine.py',
                'src/wallet/wallet_registry.py'
            ],
            'core': [
                'src/core/circuit-breaker.ts',
                'src/core/retry-manager.ts',
                'src/core/websocket-manager.ts'
            ],
            'data': [
                'src/data/metrics_collector.py',
                'src/data/realtime_backtester.py',
                'src/data/market_database/data_collector.js',
                'src/data/market_database/setup_database.js',
                'src/data/market_database/real_backtest_executor.js',
                'src/data/market_database/fix_data.js'
            ],
            'backend': [
                'backend/server-backend.js',
                'backend/backtest_validator.js'
            ],
            'frontend': [
                'frontend/server-frontend.ts',
                'frontend/public/portfolio-manager.js'
            ]
        }

        self.novaquote_patterns = {
            'agent_patterns': [
                r'class\s+\w+Agent\s*\(',
                r'def\s+run\s*\(',
                r'def\s+execute_trade\s*\(',
                r'def\s+risk_analysis\s*\(',
                r'self\.\w+_config\s*=',
                r'trading_pair\s*=',
                r'position_size\s*=',
                r'leverage\s*=',
                r'stop_loss\s*=',
                r'take_profit\s*='
            ],
            'hyperliquid_patterns': [
                r'hyperliquid\.api',
                r'HLClient\(',
                r'hyperliquid_websocket',
                r'sign_hl_order',
                r'subscribe_hl',
                r'HL_TYPE_\w+',
                r'HL_SIDE_\w+'
            ],
            'trading_patterns': [
                r'slippage_tolerance\s*=',
                r'max_position_size\s*=',
                r'risk_per_trade\s*=',
                r'portfolio_allocation\s*=',
                r'margin_requirement\s*=',
                r'funding_rate\s*=',
                r'market_impact\s*=',
                r'execution_latency\s*='
            ],
            'novaquote_imports': [
                r'from\s+src\.',
                r'from\s+\.\w+\s+import',
                r'from\s+agents\s+import',
                r'from\s+algorithms\s+import',
                r'from\s+hyperliquid\s+import',
                r'from\s+models\s+import',
                r'from\s+wallet\s+import'
            ]
        }

        self.stats = {
            'novaquote_files_scanned': 0,
            'novaquote_errors_found': 0,
            'novaquote_errors_fixed': 0,
            'categories_processed': set()
        }

    def scan_novaquote_project(self):
        """Scan spécialisé complet du projet NovaQuote"""
        print("🎯 NOVAQUOTE PROJECT SCANNER v5.0")
        print("📈 Scanner SPÉCIALISÉ NovaQuote Trading")
        print("="*80)

        all_errors = {}

        for category, files in self.novaquote_structure.items():
            print(f"\n🔍 SCANNING CATÉGORIE: {category.upper()} ({len(files)} fichiers)")
            category_errors = self._scan_novaquote_category(files, category)
            if category_errors:
                all_errors[category] = category_errors
                self.stats['categories_processed'].add(category)

        print(f"\n🎯 ANALYSE DES PATTERNS NOVAQUOTE")
        pattern_errors = self._analyze_novaquote_patterns()
        if pattern_errors:
            all_errors['patterns'] = pattern_errors

        self._generate_novaquote_report(all_errors)

        return all_errors

    def _scan_novaquote_category(self, files, category):
        """Scanner une catégorie spécifique NovaQuote"""
        errors = []

        for file_path in files:
            if Path(file_path).exists():
                self.stats['novaquote_files_scanned'] += 1
                file_errors = self._scan_novaquote_file(file_path, category)
                if file_errors:
                    errors.extend(file_errors)

        print(f"    ✅ {len([f for f in files if Path(f).exists()])}/{len(files)} fichiers trouvés")
        print(f"    🔍 {len(errors)} erreurs détectées")

        return errors

    def _scan_novaquote_file(self, file_path, category):
        """Scanner spécialisé selon la catégorie NovaQuote"""
        errors = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')

            if category == 'agents':
                errors.extend(self._scan_novaquote_agent(file_path, content, lines))
            elif category == 'algorithms':
                errors.extend(self._scan_novaquote_algorithm(file_path, content, lines))
            elif category == 'hyperliquid':
                errors.extend(self._scan_hyperliquid_file(file_path, content, lines))
            elif category == 'models':
                errors.extend(self._scan_novaquote_model(file_path, content, lines))
            elif category == 'wallet':
                errors.extend(self._scan_novaquote_wallet(file_path, content, lines))
            else:
                errors.extend(self._scan_generic_novaquote_file(file_path, content, lines, category))

        except Exception as e:
            errors.append({
                'file': file_path,
                'line': 1,
                'category': category,
                'type': 'READ_ERROR',
                'message': f"Erreur lecture fichier NovaQuote: {e}",
                'severity': 'HIGH'
            })

        return errors

    def _scan_novaquote_agent(self, file_path, content, lines):
        """Scanner spécialisé pour agents NovaQuote"""
        errors = []

        required_methods = ['__init__', 'run']
        for method in required_methods:
            if f'def {method}(' not in content:
                errors.append({
                    'file': file_path,
                    'line': 1,
                    'category': 'agent_structure',
                    'type': 'MISSING_METHOD',
                    'message': f"Agent NovaQuote doit avoir la méthode '{method}'",
                    'severity': 'HIGH',
                    'suggestion': f"Ajouter la méthode '{method}(self):'"
                })

        for i, line in enumerate(lines, 1):
            if 'self.config' not in content and 'self._config' not in content:
                errors.append({
                    'file': file_path,
                    'line': i,
                    'category': 'agent_config',
                    'type': 'MISSING_CONFIG',
                    'message': "Agent NovaQuote doit avoir une configuration",
                    'severity': 'MEDIUM',
                    'suggestion': "Ajouter self.config = config dans __init__"
                })

            if 'except:' in line and 'Exception' not in line:
                errors.append({
                    'file': file_path,
                    'line': i,
                    'category': 'trading_errors',
                    'type': 'BARE_EXCEPT',
                    'message': "Les agents NovaQuote doivent gérer les exceptions spécifiques",
                    'severity': 'MEDIUM',
                    'suggestion': "Remplacer 'except:' par 'except Exception as e:'"
                })

            if 'print(' in line:
                errors.append({
                    'file': file_path,
                    'line': i,
                    'category': 'logging',
                    'type': 'PRINT_STATEMENT',
                    'message': "Utiliser logging NovaQuote au lieu de print()",
                    'severity': 'LOW',
                    'suggestion': "Remplacer print() par self.logger.info() ou logging.getLogger()"
                })

        novaquote_imports_needed = self._check_novaquote_imports(content, 'agent')
        for imp in novaquote_imports_needed:
            errors.append({
                'file': file_path,
                'line': 1,
                'category': 'novaquote_imports',
                'type': 'MISSING_NOVAQUOTE_IMPORT',
                'message': f"Import NovaQuote manquant: {imp}",
                'severity': 'MEDIUM',
                'suggestion': f"Ajouter: {imp}"
            })

        return errors

    def _scan_novaquote_algorithm(self, file_path, content, lines):
        """Scanner spécialisé pour algorithmes de trading NovaQuote"""
        errors = []

        for i, line in enumerate(lines, 1):
            if 'def execute' in content and 'stop_loss' not in content:
                errors.append({
                    'file': file_path,
                    'line': 1,
                    'category': 'risk_management',
                    'type': 'MISSING_STOP_LOSS',
                    'message': "Algorithme trading doit implémenter stop_loss",
                    'severity': 'HIGH',
                    'suggestion': "Ajouter logique stop_loss dans execute()"
                })

            if 'position_size' in content and 'max_position_size' not in content:
                errors.append({
                    'file': file_path,
                    'line': i,
                    'category': 'position_sizing',
                    'type': 'MISSING_POSITION_LIMIT',
                    'message': "Algorithme doit limiter la taille des positions",
                    'severity': 'HIGH',
                    'suggestion': "Ajouter max_position_size dans configuration"
                })

            if 'def execute' in content and 'latency' not in content.lower():
                errors.append({
                    'file': file_path,
                    'line': i,
                    'category': 'performance',
                    'type': 'MISSING_LATENCY_TRACKING',
                    'message': "Algorithme doit tracker la latence d'exécution",
                    'severity': 'MEDIUM',
                    'suggestion': "Ajouter tracking temps d'exécution dans execute()"
                })

        return errors

    def _scan_hyperliquid_file(self, file_path, content, lines):
        """Scanner spécialisé pour fichiers HyperLiquid"""
        errors = []

        if 'api_key' in content and 'base64' not in content.lower():
            errors.append({
                'file': file_path,
                'line': 1,
                'category': 'hyperliquid_security',
                'type': 'UNENCRYPTED_API_KEY',
                'message': "Clés API HyperLiquid doivent être encodées",
                'severity': 'HIGH',
                'suggestion': "Utiliser base64.b64encode() pour les clés API"
            })

        if 'sign' in content and 'private_key' not in content and 'api_secret' not in content:
            errors.append({
                'file': file_path,
                'line': 1,
                'category': 'hyperliquid_signature',
                'type': 'MISSING_SIGNATURE_KEY',
                'message': "Signature HyperLiquid nécessite une clé privée/API secret",
                'severity': 'HIGH',
                'suggestion': "Ajouter private_key ou api_secret pour signing"
            })

        if 'websocket' in content.lower():
            for i, line in enumerate(lines, 1):
                if 'websocket' in line.lower() and 'reconnect' not in content.lower():
                    errors.append({
                        'file': file_path,
                        'line': i,
                        'category': 'websocket_handling',
                        'type': 'MISSING_RECONNECT_LOGIC',
                        'message': "WebSocket HyperLiquid doit avoir logique de reconnexion",
                        'severity': 'MEDIUM',
                        'suggestion': "Ajouter logique de reconnexion automatique"
                    })

        return errors

    def _scan_novaquote_model(self, file_path, content, lines):
        """Scanner spécialisé pour modèles IA NovaQuote"""
        errors = []

        if 'class ' in content:
            for i, line in enumerate(lines, 1):
                if 'class ' in line and 'Model' in line:
                    required_model_methods = ['generate', 'chat', 'query']
                    for method in required_model_methods:
                        if f'def {method}(' not in content:
                            errors.append({
                                'file': file_path,
                                'line': 1,
                                'category': 'model_interface',
                                'type': 'MISSING_MODEL_METHOD',
                                'message': f"Modèle IA NovaQuote doit implémenter {method}()",
                                'severity': 'MEDIUM',
                                'suggestion': f"Ajouter def {method}(self, prompt):"
                            })

        if 'api_key' in content and 'os.getenv' not in content and 'environment' not in content:
            errors.append({
                'file': file_path,
                'line': 1,
                'category': 'model_security',
                'type': 'HARDCODED_API_KEY',
                'message': "Clés API IA doivent utiliser variables d'environnement",
                'severity': 'HIGH',
                'suggestion': "Utiliser os.getenv('API_KEY') au lieu de clés en dur"
            })

        return errors

    def _scan_novaquote_wallet(self, file_path, content, lines):
        """Scanner spécialisé pour wallet NovaQuote"""
        errors = []

        for i, line in enumerate(lines, 1):
            if 'private_key' in line and 'encryption' not in content.lower():
                errors.append({
                    'file': file_path,
                    'line': i,
                    'category': 'wallet_security',
                    'type': 'UNENCRYPTED_PRIVATE_KEY',
                    'message': "Clés privées wallet doivent être encryptées",
                    'severity': 'CRITICAL',
                    'suggestion': "Utiliser encryption AES pour stocker les clés privées"
                })

            if 'permission' in content and 'validate' not in content.lower():
                errors.append({
                    'file': file_path,
                    'line': i,
                    'category': 'wallet_permissions',
                    'type': 'MISSING_PERMISSION_VALIDATION',
                    'message': "Wallet doit valider les permissions de trading",
                    'severity': 'HIGH',
                    'suggestion': "Ajouter validation permissions avant chaque trade"
                })

        return errors

    def _scan_generic_novaquote_file(self, file_path, content, lines, category):
        """Scanner générique pour autres catégories NovaQuote"""
        errors = []

        for i, line in enumerate(lines, 1):
            if 'print(' in line:
                errors.append({
                    'file': file_path,
                    'line': i,
                    'category': 'novaquote_logging',
                    'type': 'PRINT_INSTEAD_OF_LOGGING',
                    'message': "Utiliser logging NovaQuote au lieu de print",
                    'severity': 'LOW',
                    'suggestion': "Remplacer print() par logging.getLogger()"
                })

            if 'password' in line.lower() or 'secret' in line.lower():
                if 'os.getenv' not in line:
                    errors.append({
                        'file': file_path,
                        'line': i,
                        'category': 'novaquote_security',
                        'type': 'HARDCODED_SECRET',
                        'message': "Secrets NovaQuote doivent utiliser variables d'environnement",
                        'severity': 'HIGH',
                        'suggestion': "Utiliser os.getenv('SECRET_NAME')"
                    })

        return errors

    def _check_novaquote_imports(self, content, category):
        """Vérifier les imports NovaQuote requis"""
        missing_imports = []

        novaquote_base_imports = [
            'import logging',
            'from typing import'
        ]

        for imp in novaquote_base_imports:
            if imp not in content:
                missing_imports.append(imp)

        return missing_imports

    def _analyze_novaquote_patterns(self):
        """Analyser les patterns spécifiques NovaQuote"""
        errors = []

        novaquote_files = Path("src").rglob("*.py")

        for pattern_name, patterns in self.novaquote_patterns.items():
            for pattern in patterns:
                for file_path in novaquote_files:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if re.search(pattern, content):
                                pass
                    except:
                        continue

        return errors

    def _generate_novaquote_report(self, all_errors):
        """Générer rapport spécialisé NovaQuote"""
        print("\n" + "="*100)
        print("📈 RAPPORT NOVAQUOTE PROJECT SCANNER")
        print("="*100)

        print(f"\n📊 STATISTIQUES NOVAQUOTE")
        print(f"   📁 Fichiers NovaQuote scannés: {self.stats['novaquote_files_scanned']}")
        print(f"   🔢 Erreurs NovaQuote trouvées: {self.stats['novaquote_errors_found']}")
        print(f"   📂 Catégories traitées: {len(self.stats['categories_processed'])}")

        if all_errors:
            print(f"\n🔍 ERREURS PAR CATÉGORIE NOVAQUOTE")
            for category, errors in all_errors.items():
                if errors:
                    severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
                    for error in errors:
                        severity = error.get('severity', 'LOW')
                        severity_counts[severity] += 1

                    print(f"   {category.upper()}: {len(errors)} erreurs")
                    if sum(severity_counts.values()) > 0:
                        print(f"      🔴 CRITICAL: {severity_counts['CRITICAL']}")
                        print(f"      🔴 HIGH: {severity_counts['HIGH']}")
                        print(f"      🟡 MEDIUM: {severity_counts['MEDIUM']}")
                        print(f"      🟢 LOW: {severity_counts['LOW']}")

            critical_errors = []
            for category_errors in all_errors.values():
                critical_errors.extend([e for e in category_errors if e.get('severity') in ['CRITICAL', 'HIGH']])

            if critical_errors:
                print(f"\n🚨 ERREURS CRITIQUES NOVAQUOTE ({len(critical_errors)})")
                for i, error in enumerate(critical_errors[:10], 1):
                    print(f"   {i}. 🚨 {error['file']}")
                    print(f"      {error['message']}")
                    print(f"      💡 {error.get('suggestion', 'Correction requise')}")

        print(f"\n🎯 RECOMMANDATIONS NOVAQUOTE")

        if all_errors:
            high_priority = []
            medium_priority = []
            low_priority = []

            for category_errors in all_errors.values():
                for error in category_errors:
                    severity = error.get('severity', 'LOW')
                    if severity in ['CRITICAL', 'HIGH']:
                        high_priority.append(error)
                    elif severity == 'MEDIUM':
                        medium_priority.append(error)
                    else:
                        low_priority.append(error)

            if high_priority:
                print(f"   🔴 URGENT: Corriger {len(high_priority)} erreurs critiques avant production")
            if medium_priority:
                print(f"   🟡 OPTIMISATION: Améliorer {len(medium_priority)} points de qualité")
            if low_priority:
                print(f"   🟢 MAINTENANCE: Nettoyer {len(low_priority)} détails de code")
        else:
            print(f"   ✅ EXCELLENT: Aucune erreur NovaQuote détectée !")

        report_data = {
            "timestamp": datetime.now().isoformat(),
            "project": "NovaQuote Trading",
            "version": "5.0",
            "stats": self.stats,
            "novaquote_categories": list(self.stats['categories_processed']),
            "errors": all_errors
        }

        report_path = "novaquote_project_scan_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        print(f"\n📄 Rapport NovaQuote sauvegardé: {report_path}")
        print(f"\n🏁 SCAN NOVAQUOTE TERMINÉ")

def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="NovaQuote Project Scanner")
    parser.add_argument("--category", type=str, help="Scanner une catégorie spécifique (agents, algorithms, hyperliquid, etc.)")
    parser.add_argument("--agent", type=str, help="Scanner un agent spécifique")
    parser.add_argument("--security-only", action="store_true", help="Scanner seulement erreurs de sécurité")
    parser.add_argument("--fix", action="store_true", help="Tenter corrections automatiques")

    args = parser.parse_args()

    scanner = NovaQuoteProjectScanner()

    print("🎯 NOVAQUOTE PROJECT SCANNER - DÉDIÉ 100%")

    if args.category:
        print(f"📂 Catégorie spécifique: {args.category}")
    elif args.agent:
        print(f"🤖 Agent spécifique: {args.agent}")
    elif args.security_only:
        print(f"🔒 Focus sécurité seulement")
    else:
        errors = scanner.scan_novaquote_project()

    print(f"\n🏁 Scan NovaQuote Project terminé")

if __name__ == "__main__":
    main()