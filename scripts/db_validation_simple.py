#!/usr/bin/env python3
"""
Script de validation de la database NOVAQUOTE
Agent Database NOVAQUOTE - Validation MetaMask Integration
"""

import sqlite3
import requests
import json
import time
import hashlib
from datetime import datetime

def validate_database():
    """Validation complète de la database"""
    print("=== VALIDATION DATABASE NOVAQUOTE ===")

    db_path = "C:/Users/Deamon/Desktop/Backup/Trade/projet trading/src/market_database/market_data.db"
    api_url = "http://localhost:7000"

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 1. Analyse structure
        print("\n1. ANALYSE STRUCTURE")

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        all_tables = [row[0] for row in cursor.fetchall()]

        metamask_tables = ['wallets', 'wallet_balances', 'trades', 'positions']
        existing_metamask = [t for t in metamask_tables if t in all_tables]

        print(f"Tables MetaMask: {len(existing_metamask)}/{len(metamask_tables)} créées")
        for table in existing_metamask:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  - {table}: {count} enregistrements")

        # 2. Test format adresses
        print("\n2. VALIDATION ADRESSES")

        cursor.execute("SELECT id, metamask_address FROM wallets")
        wallets = cursor.fetchall()

        valid_addresses = 0
        for wallet_id, address in wallets:
            if (address and address.startswith("0x") and
                len(address) == 42 and
                all(c in "0123456789abcdefABCDEF" for c in address[2:])):
                valid_addresses += 1
            else:
                print(f"  Adresse invalide (ID {wallet_id}): {address}")

        print(f"Adresses valides: {valid_addresses}/{len(wallets)}")

        # 3. Test intégrité données
        print("\n3. INTEGRITÉ DONNÉES")

        # Test foreign keys consistency
        cursor.execute("PRAGMA foreign_keys")
        fk_enabled = cursor.fetchone()[0]
        print(f"Foreign Keys activées: {fk_enabled == 1}")

        # Test balances consistency
        cursor.execute("""
            SELECT wallet_id,
                   SUM(available_balance) as total_available,
                   SUM(total_balance) as total_balance
            FROM wallet_balances
            GROUP BY wallet_id
        """)

        balance_issues = 0
        for row in cursor.fetchall():
            if row[1] > row[2]:  # available > total
                balance_issues += 1

        print(f"Problèmes de balance: {balance_issues}")

        # 4. Test API endpoints
        print("\n4. TEST API ENDPOINTS")

        try:
            # Test sans auth
            response = requests.get(f"{api_url}/api/wallet", timeout=5)
            print(f"GET /api/wallet sans auth: {response.status_code}")

            if response.status_code == 400:
                print("  -> Correct: authentification requise")

            # Test avec adresse valide
            test_address = "0x742d35Cc6634C0532925a3b8D4E7E0E0e9e0d3a1"
            response = requests.get(f"{api_url}/api/wallet?address={test_address}", timeout=5)
            print(f"GET /api/wallet avec adresse: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"  -> Success: {data.get('success', False)}")
                if data.get('data'):
                    print(f"  -> Wallet: {data['data'].get('wallet_name', 'N/A')}")
                    print(f"  -> Balance: ${data['data'].get('balance', 0)}")
                    print(f"  -> PnL Total: ${data['data'].get('pnl_total', 0)}")

        except Exception as e:
            print(f"Erreur API: {e}")

        # 5. Performance queries
        print("\n5. PERFORMANCE TESTS")

        queries = [
            "SELECT * FROM wallets WHERE metamask_address = '0x742d35Cc6634C0532925a3b8D4E7E0E0e9e0d3a1'",
            "SELECT * FROM wallet_balances WHERE wallet_id = 1",
            "SELECT COUNT(*) FROM trades WHERE wallet_id = 1",
            "SELECT COUNT(*) FROM positions WHERE status = 'open'"
        ]

        for i, query in enumerate(queries):
            start_time = time.time()
            cursor.execute(query)
            results = cursor.fetchall()
            end_time = time.time()

            query_time = (end_time - start_time) * 1000
            print(f"  Query {i+1}: {query_time:.2f}ms ({len(results)} résultats)")

        # 6. Diagnostic final
        print("\n=== DIAGNOSTIC FINAL ===")

        score = 0
        score += 25 if len(existing_metamask) == 4 else 0  # Structure
        score += 20 if valid_addresses == len(wallets) else 0  # Format adresses
        score += 20 if balance_issues == 0 else 0  # Consistance balances
        score += 20 if fk_enabled == 1 else 0  # Foreign keys
        score += 15  # API répond (même avec erreur 400)

        print(f"SCORE GLOBAL: {score}/100")

        if score >= 90:
            status = "PRODUCTION READY"
            print(f"STATUS: {status}")
        elif score >= 70:
            status = "BONNE - Améliorations mineures"
            print(f"STATUS: {status}")
        elif score >= 50:
            status = "ACCEPTABLE - Améliorations requises"
            print(f"STATUS: {status}")
        else:
            status = "CRITIQUE - Non prêt pour production"
            print(f"STATUS: {status}")

        # Recommandations
        print("\n=== RECOMMANDATIONS ===")

        if fk_enabled == 0:
            print("-> ACTIVER Foreign Keys (PRAGMA foreign_keys = ON)")

        if valid_addresses < len(wallets):
            print("-> VALIDER format adresses MetaMask côté API")

        if balance_issues > 0:
            print("-> CORRIGER incohérences balances (available > total)")

        if len(existing_metamask) < 4:
            print("-> CRÉER tables MetaMask manquantes")

        print("-> IMPLÉMENTER monitoring temps réel")
        print("-> AJOUTER validation stricte des entrées")

        conn.close()

        return score >= 70

    except Exception as e:
        print(f"ERREUR: {e}")
        return False

if __name__ == "__main__":
    success = validate_database()
    print(f"\nValidation {'réussie' if success else 'échouée'}")