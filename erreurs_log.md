# ERREURS LOGS CRITIQUES - ACTION REQUIRED

## URGENT (À corriger immédiatement)

- [ ] **ERREUR**: Agents Python sans logging structuré
  **Fichier**: `src/agents/funding_agent.py`, `src/agents/strategy_agent.py`, `src/agents/risk_agent.py`
  **SOLUTION**: Ajouter `from src.logger import get_logger` et remplacer les `print()` par `logger.info/error/warning()`

- [ ] **ERREUR**: BaseAgent utilise print() au lieu de logging structuré
  **Fichier**: `src/agents/base_agent.py` ligne 34-39
  **SOLUTION**: Remplacer la méthode `log()` par `get_logger(self.name)` et utiliser `logging.INFO/ERROR/WARNING`

- [ ] **ERREUR**: Manager agent sans logging des erreurs de démarrage
  **Fichier**: `src/agents/manager.py`
  **SOLUTION**: Ajouter `from src.logger import get_logger` et logger les tentatives de démarrage/arrêt des agents

- [ ] **ERREUR**: Pas de logs de trading centralisés
  **Fichier**: `src/algorithms/hyperliquid_mainnet_agent.py`
  **SOLUTION**: Ajouter des logs structurés pour chaque ordre avec timestamp, symbol, size, price, order_id

- [ ] **ERREUR**: Logs directory vide - pas de rotation de logs
  **Fichier**: `logs/` directory
  **SOLUTION**: Implémenter `TimedRotatingFileHandler` dans `src/logger.py` pour rotation quotidienne

## IMPORTANT (À corriger rapidement)

- [ ] **ERREUR**: WebSocket sans logs des déconnexions répétées
  **Fichier**: `src/hyperliquid/websocket.py` lignes 192-209
  **SOLUTION**: Ajouter des logs détaillés pour chaque déconnexion avec `reconnect_count` et `reason`

- [ ] **ERREUR**: API responses 304 non loggées
  **Fichier**: `src/agents/api.py`
  **SOLUTION**: Logger chaque réponse API avec status code, surtout les 304 Not Modified

- [ ] **ERREUR**: HyperLiquid client sans logs des erreurs réseau
  **Fichier**: `src/hyperliquid/client.py`
  **SOLUTION**: Ajouter logging pour toutes les requêtes API avec response status

- [ ] **ERREUR**: Wallet managers sans logs des transactions critiques
  **Fichier**: `src/wallet/api_wallet_manager.py`, `src/wallet/permission_controller.py`
  **SOLUTION**: Logger toutes les permissions accordées/révquées et transactions

- [ ] **ERREUR**: Agents d'IA sans logs des appels LLM
  **Fichier**: `src/models/` tous les fichiers
  **SOLUTION**: Logger chaque appel API LLM avec token usage, response time, errors

## SECONDARY (Améliorations)

- [ ] **ERREUR**: Pas de logs de performance/latence
  **Fichier**: Système entier
  **SOLUTION**: Ajouter des logs de timing pour les opérations critiques (API calls, trading decisions)

- [ ] **ERREUR**: Logs non structurés impossibles à parser
  **Fichier**: Tous les fichiers utilisant `print()`
  **SOLUTION**: Standardiser avec JSON logging pour ingestion par ELK stack

- [ ] **ERREUR**: Pas de logs des erreurs 403/401 authentification
  **Fichier**: `src/hyperliquid/signing.py`
  **SOLUTION**: Logger toutes les erreurs d'authentification avec contexte

- [ ] **ERREUR**: Agent inference monitor sans logs des métriques
  **Fichier**: `src/agents/agent_inference_monitor.py`
  **SOLUTION**: Logger les métriques d'inférence en temps réel

- [ ] **ERREUR**: Tests logs non utilisés en production
  **Fichier**: `tests/logs/`
  **SOLUTION**: Déplacer vers `logs/` et configurer logging structuré

## ACTIONS TECHNIQUES IMMÉDIATES

1. **Créer un logger centralisé**:
   ```python
   # Dans src/logger.py
   import logging
   import json
   from datetime import datetime

   class JSONFormatter(logging.Formatter):
       def format(self, record):
           return json.dumps({
               'timestamp': datetime.utcnow().isoformat(),
               'level': record.levelname,
               'agent': record.name,
               'message': record.getMessage(),
               'module': record.module,
               'line': record.lineno
           })
   ```

2. **Logger tous les trades**:
   ```python
   logger.info("TRADE_EXECUTED", extra={
       'symbol': symbol,
       'side': side,
       'size': size,
       'price': price,
       'order_id': order_id,
       'agent': agent_name
   })
   ```

3. **Logger toutes les erreurs WebSocket**:
   ```python
   logger.error("WEBSOCKET_DISCONNECTED", extra={
       'reason': str(e),
       'reconnect_count': self.reconnect_count,
       'max_reconnects': self.max_reconnects
   })
   ```

## PRIORITÉS SYSTÈME

1. **IMMÉDIAT**: Logger tous les trades et erreurs critiques
2. **URGENT**: Centraliser les logs des 4 agents IA principaux
3. **IMPORTANT**: Logger toutes les déconnexions WebSocket
4. **SECONDARY**: Performance monitoring et structuration JSON

**AGENT SYSTEM-LAUNCHER: Commencer par les corrections URGENTES, puis IMPORTANT**