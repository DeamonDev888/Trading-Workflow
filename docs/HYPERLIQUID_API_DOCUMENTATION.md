# 📚 Documentation Complète de l'API Hyperliquid

_Documentation officielle récupérée et adaptée pour le projet Deamon Dev AI
Agents_

## 🎯 Vue d'ensemble

Hyperliquid fournit une API REST complète pour interagir avec sa plateforme de
trading décentralisée. Cette documentation couvre tous les aspects de l'API
nécessaires pour développer des agents de trading automatisés.

### 🔗 URLs des Endpoints

- **Mainnet** : `https://api.hyperliquid.xyz`
- **Testnet** : `https://api.hyperliquid-testnet.xyz`

### 🛠️ SDKs Officiels

- **Python SDK** :
  [https://github.com/hyperliquid-dex/hyperliquid-python-sdk](https://github.com/hyperliquid-dex/hyperliquid-python-sdk)
- **Rust SDK** :
  [https://github.com/hyperliquid-dex/hyperliquid-rust-sdk](https://github.com/hyperliquid-dex/hyperliquid-rust-sdk)
- **SDKs communautaires TypeScript** :
  - [https://github.com/nktkas/hyperliquid](https://github.com/nktkas/hyperliquid)
  - [https://github.com/nomeida/hyperliquid](https://github.com/nomeida/hyperliquid)
- **CCXT** :
  [https://docs.ccxt.com/#/exchanges/hyperliquid](https://docs.ccxt.com/#/exchanges/hyperliquid)

---

## 📝 Notation et Conventions

### Abréviations Standard

| Abréviation | Signification | Description                                       |
| ----------- | ------------- | ------------------------------------------------- |
| `Px`        | Price         | Prix                                              |
| `Sz`        | Size          | Taille en unités de base (coin)                   |
| `Szi`       | Signed size   | Taille signée (positive = long, négative = short) |
| `Ntl`       | Notional      | Montant USD (Px × Sz)                             |
| `Side`      | Side          | Côté du trade (B = Bid/Buy, A = Ask/Short)        |
| `Asset`     | Asset         | Index entier représentant l'asset                 |
| `Tif`       | Time in force | Durée de validité de l'ordre                      |

### Time in Force (TIF)

- `GTC` : Good 'til canceled
- `ALO` : Add liquidity only (post only)
- `IOC` : Immediate or cancel
- `Market` : Ordre marché
- `Limit` : Ordre limite

---

## 🏷️ Asset IDs et Mapping

### Pérpetuels (Perpetuals)

Les endpoints de perpétuels utilisent un entier `asset` qui correspond à l'index
dans la réponse `meta`.

**Exemple** : `BTC = 0` sur mainnet

### Spot Trading

Les endpoints spot utilisent `10000 + spotInfo["index"]` où `spotInfo` est
l'objet correspondant dans `spotMeta.universe`.

**Exemple** : Pour `PURR/USDC`, l'asset est `10000` car son index dans spotInfo
est `0`.

### Pérpetuels Builder-Déployés

`100000 + perp_dex_index * 10000 + index_in_meta`

**Exemple** : `test:ABC` sur testnet a `perp_dex_index = 1`,
`index_in_meta = 0`, donc `asset = 110000`.

### Exemples Pratiques

| Asset       | Mainnet ID | Testnet ID | Remarques         |
| ----------- | ---------- | ---------- | ----------------- |
| BTC (perp)  | 0          | 0          | Index dans meta   |
| ETH (perp)  | 1          | 1          | Index dans meta   |
| HYPE (spot) | 107        | 1035       | 10000 + spotIndex |
| PURR/USDC   | 10000      | 10000      | 10000 + spotIndex |

---

## 🔐 Signature et Authentification

### ⚠️ Avertissement Important

Il est fortement recommandé d'utiliser un SDK officiel plutôt que d'implémenter
manuellement les signatures. De nombreuses erreurs peuvent survenir lors de la
génération manuelle des signatures.

### Erreurs Courantes de Signature

1. **Non-réalisation de schémas de signature multiples** : L1 vs L1 user-signed
   actions
2. **Ordre des champs incorrect** : Le msgpack nécessite un ordre spécifique
3. **Zéros de fin manquants** : Problèmes avec les nombres
4. **Casse des adresses** : Les adresses doivent être en minuscules
5. **Payload de signature incorrect** : Différent du payload local

### Schémas de Signature

#### L1 Actions (Exchange Endpoint)

- Utilisent `sign_l1_action()` du SDK Python
- Signature directe avec clé privée

#### User-Signed Actions (Transfers, Withdrawals)

- Utilisent `sign_user_signed_action()` du SDK Python
- Signature EIP-712 avec typed data

---

## 🌐 Endpoints API

### Info Endpoint (`/info`)

Endpoint GET pour récupérer des informations publiques sur l'échange.

#### Récupérer les Prix du Milieu (`allMids`)

```http
POST https://api.hyperliquid.xyz/info
Content-Type: application/json

{
  "type": "allMids"
}
```

**Réponse** :

```json
{
  "APE": "4.33245",
  "ARB": "1.21695",
  "BTC": "43250.5"
}
```

#### Ordres Ouverts d'un Utilisateur (`openOrders`)

```http
POST https://api.hyperliquid.xyz/info
Content-Type: application/json

{
  "type": "openOrders",
  "user": "0x742d35Cc6464C73d8a0F2E3b3A1b4c7e9f5a8b3"
}
```

#### Fills d'un Utilisateur (`userFills`)

```http
POST https://api.hyperliquid.xyz/info
Content-Type: application/json

{
  "type": "userFills",
  "user": "0x742d35Cc6464C73d8a0F2E3b3A1b4c7e9f5a8b3"
}
```

#### L2 Order Book (`l2Book`)

```http
POST https://api.hyperliquid.xyz/info
Content-Type: application/json

{
  "type": "l2Book",
  "coin": "BTC"
}
```

#### Historique des Bougies (`candleSnapshot`)

```http
POST https://api.hyperliquid.xyz/info
Content-Type: application/json

{
  "type": "candleSnapshot",
  "req": {
    "coin": "BTC",
    "interval": "15m",
    "startTime": 1681923600000,
    "endTime": 1681924500000
  }
}
```

### Exchange Endpoint (`/exchange`)

Endpoint POST pour les actions de trading nécessitant une signature.

#### Placer un Ordre (`order`)

```http
POST https://api.hyperliquid.xyz/exchange
Content-Type: application/json

{
  "action": {
    "type": "order",
    "orders": [{
      "a": 0,        // asset (BTC = 0)
      "b": true,     // isBuy
      "p": "43000",  // price
      "s": "0.01",   // size
      "r": false,    // reduceOnly
      "t": {
        "limit": {
          "tif": "Gtc"
        }
      }
    }],
    "grouping": "na"
  },
  "nonce": 1681923600000,
  "signature": {...}
}
```

#### Annuler des Ordres (`cancel`)

```http
POST https://api.hyperliquid.xyz/exchange
Content-Type: application/json

{
  "action": {
    "type": "cancel",
    "cancels": [{
      "a": 0,        // asset
      "o": 12345     // order ID
    }]
  },
  "nonce": 1681923600000,
  "signature": {...}
}
```

#### Modifier un Ordre (`modify`)

```http
POST https://api.hyperliquid.xyz/exchange
Content-Type: application/json

{
  "action": {
    "type": "modify",
    "oid": 12345,
    "order": {
      "a": 0,
      "b": true,
      "p": "43500",
      "s": "0.01",
      "r": false,
      "t": {
        "limit": {
          "tif": "Gtc"
        }
      }
    }
  },
  "nonce": 1681923600000,
  "signature": {...}
}
```

#### Transfert USDC (`usdSend`)

```http
POST https://api.hyperliquid.xyz/exchange
Content-Type: application/json

{
  "action": {
    "type": "usdSend",
    "hyperliquidChain": "Mainnet",
    "signatureChainId": "0xa4b1",
    "destination": "0x742d35Cc6464C73d8a0F2E3b3A1b4c7e9f5a8b3",
    "amount": "100.0",
    "time": 1681923600000
  },
  "nonce": 1681923600000,
  "signature": {...}
}
```

#### Mise à Jour du Levier (`updateLeverage`)

```http
POST https://api.hyperliquid.xyz/exchange
Content-Type: application/json

{
  "action": {
    "type": "updateLeverage",
    "asset": 0,
    "isCross": true,
    "leverage": 5
  },
  "nonce": 1681923600000,
  "signature": {...}
}
```

---

## 🔌 WebSocket API

### URLs WebSocket

- **Mainnet** : `wss://api.hyperliquid.xyz/ws`
- **Testnet** : `wss://api.hyperliquid-testnet.xyz/ws`

### Connexion

```bash
wscat -c wss://api.hyperliquid.xyz/ws
```

### Souscription aux Trades

```json
{
  "method": "subscribe",
  "subscription": {
    "type": "trades",
    "coin": "BTC"
  }
}
```

### Souscription au Order Book L2

```json
{
  "method": "subscribe",
  "subscription": {
    "type": "l2Book",
    "coin": "BTC"
  }
}
```

### Souscription aux Ordres d'un Utilisateur

```json
{
  "method": "subscribe",
  "subscription": {
    "type": "orderUpdates",
    "user": "0x742d35Cc6464C73d8a0F2E3b3A1b4c7e9f5a8b3"
  }
}
```

---

## ⚡ Limites de Taux (Rate Limits)

### Limites par Adresse

- **Requêtes par minute** : 300 par adresse
- **Requêtes par heure** : Variable selon le volume de trading
- **Actions de trading** : 10 par seconde maximum

### Limites Utilisateur

- **Ordres par jour** : Variable selon le VIP tier
- **Volume minimum** : $10 par ordre
- **Levier maximum** : 50x (varie par asset)

### VIP Tiers

| Tier     | Volume 30j (USDC) | Réduction Frais |
| -------- | ----------------- | --------------- |
| Bronze   | 1M                | 5%              |
| Silver   | 5M                | 10%             |
| Gold     | 10M               | 15%             |
| Platinum | 25M               | 20%             |
| Diamond  | 50M               | 25%             |

---

## 🔧 HyperEVM

### Vue d'ensemble

HyperEVM est une machine virtuelle Ethereum intégrée à Hyperliquid, utilisant le
consensus HyperBFT pour la sécurité.

### Configuration Réseau

#### Mainnet

- **Chain ID** : 999
- **RPC URL** : `https://rpc.hyperliquid.xyz/evm`
- **Token natif** : HYPE (18 décimales)

#### Testnet

- **Chain ID** : 998
- **RPC URL** : `https://rpc.hyperliquid-testnet.xyz/evm`
- **Token natif** : HYPE (18 décimales)

### Caractéristiques

- **Hardfork** : Cancun (sans blobs)
- **EIP-1559** : Activé
- **Gas fees** : Base fees et priority fees sont brûlés
- **Wrapped HYPE** : Transferts entre HyperCore et HyperEVM

### Transferts HyperCore ↔ HyperEVM

Pour transférer HYPE de HyperCore vers HyperEVM :

1. Envoyer HYPE à l'adresse `0x2222222222222222222222222222222222222222`
2. Le HYPE apparaît automatiquement sur HyperEVM

### JSON-RPC

HyperEVM supporte les méthodes JSON-RPC standard d'Ethereum :

```json
{
  "jsonrpc": "2.0",
  "method": "eth_getBalance",
  "params": ["0x742d35Cc6464C73d8a0F2E3b3A1b4c7e9f5a8b3", "latest"],
  "id": 1
}
```

---

## 🚨 Gestion des Erreurs

### Codes d'Erreur Courants

| Erreur                                        | Description             |
| --------------------------------------------- | ----------------------- |
| `User or API Wallet 0x0123... does not exist` | Signature invalide      |
| `Must deposit before performing actions`      | Compte non initialisé   |
| `Order must have minimum value of $10`        | Ordre trop petit        |
| `Insufficient margin`                         | Marge insuffisante      |
| `Rate limit exceeded`                         | Limite de taux dépassée |

### Debugging des Signatures

1. **Vérifier l'ordre des champs** dans le payload
2. **Minusculer les adresses** avant signature
3. **Utiliser le SDK officiel** plutôt que l'implémentation manuelle
4. **Comparer avec les exemples** du SDK Python

---

## 📊 Intégration dans le Projet

### Structure Recommandée

```
src/
├── hyperliquid/
│   ├── client.py          # Client API principal
│   ├── websocket.py       # Gestion WebSocket
│   ├── signature.py       # Utilitaires de signature
│   └── types.py          # Types de données
├── wallet/
│   ├── manager.py        # Gestionnaire de wallet
│   ├── signature_engine.py # Moteur de signature
│   └── permission_controller.py
└── agents/
    └── trading_agent.py  # Agent de trading
```

### Exemple d'Utilisation

```python
from src.hyperliquid import HyperliquidClient
from src.wallet import WalletManager

# Initialisation
wallet = WalletManager()
client = HyperliquidClient(wallet)

# Récupérer les prix
mids = await client.get_all_mids()

# Placer un ordre
order_result = await client.place_order(
    asset="BTC",
    is_buy=True,
    price=43000,
    size=0.01
)

# Souscription WebSocket
await client.subscribe_trades("BTC")
```

---

## 🔗 Ressources Utiles

- **Documentation officielle** :
  [https://hyperliquid.gitbook.io/hyperliquid-docs](https://hyperliquid.gitbook.io/hyperliquid-docs)
- **Python SDK** :
  [https://github.com/hyperliquid-dex/hyperliquid-python-sdk](https://github.com/hyperliquid-dex/hyperliquid-python-sdk)
- **Discord** : [https://discord.gg/hyperliquid](https://discord.gg/hyperliquid)
- **Explorer** : [https://app.hyperliquid.xyz](https://app.hyperliquid.xyz)

---

_Documentation créée pour le projet Deamon Dev AI Agents - Version 1.0_
