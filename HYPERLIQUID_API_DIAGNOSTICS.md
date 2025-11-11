# 🔧 HyperLiquid API Diagnostics Guide
## Guide de diagnostic pour "HyperLiquid API not available"

---

## 🔍 Problème Actuel

```
[16:42:19.43] [WARN] [PRICES] ⚠️  HyperLiquid API not available for real-time prices
```

**Cause identifiée :** Le module `hlAPI` n'était pas initialisé au démarrage du backend.

---

## ✅ Corrections Appliquées

### 1. **Initialisation Manquante**
```typescript
// AVANT: jamais appelé
// APRÈS: ajouté au démarrage
await initializeHyperLiquid();
initializeHyperLiquidWS();
```

### 2. **Logging Amélioré**
```typescript
// Logs détaillés pour debugging
log.info(`HyperLiquid API loaded: ${!!HyperliquidAPI ? '✅' : '❌'}`, 'HYPERLIQUID');
log.info(`HyperLiquid WebSocket loaded: ${!!HyperliquidWebSocket ? '✅' : '❌'}`, 'HYPERLIQUID');
```

### 3. **Fallback Robuste**
```typescript
// Si API échoue → prix de fallback
const fallbackPrices = {
  'BTC': 43250.0,
  'ETH': 2280.0,
  'SOL': 98.5,
  'BNB': 312.0,
  'AVAX': 28.5,
  'LINK': 14.2,
  'LDO': 2.8
};
```

---

## 🔧 Étape par Étape pour Diagnostiquer

### Étape 1: Vérifier les Logs au Démarrage
```bash
# Démarrer le backend et chercher ces logs:
npm start

# Chercher:
[SUCCESS] HyperLiquid modules loaded successfully
[INFO] HyperLiquid API loaded: ✅
[INFO] HyperLiquid WebSocket loaded: ✅
[SUCCESS] HyperLiquid API initialized
```

### Étape 2: Vérifier l'API HyperLiquid
```bash
# Test direct de l'API
curl -X POST https://api.hyperliquid.xyz/info \
  -H "Content-Type: application/json" \
  -d '{"type": "allMids"}'

# Devrait retourner les prix actuels
{"BTC": 43250.5, "ETH": 2280.2, ...}
```

### Étape 3: Vérifier les Modules
```javascript
// Dans backend/server-backend.ts - console logs
console.log('HyperliquidAPI:', typeof HyperliquidAPI);
console.log('hlAPI after init:', typeof hlAPI);
```

### Étape 4: Diagnostic de Réseau
```bash
# Test connectivité
ping api.hyperliquid.xyz
telnet api.hyperliquid.xyz 443

# Vérifier proxy/firewall
curl -I https://api.hyperliquid.xyz/info
```

---

## 🚨 Scénarios d'Erreur et Solutions

### ❌ **Module Not Found**
```
Failed to load HyperLiquid modules: Cannot find module '../src/hyperliquid/hyperliquid-api'
```
**Solution:**
```bash
# Vérifier les fichiers existent
ls -la src/hyperliquid/
npm install axios  # Dépendance manquante
```

### ❌ **API Timeout**
```
Failed to get real-time prices: timeout of 10000ms exceeded
```
**Solution:**
```typescript
// Augmenter timeout dans hyperliquid-api.js
this.client = axios.create({
  timeout: 30000,  // 30 secondes
});
```

### ❌ **Rate Limiting**
```
Failed to get real-time prices: Request failed with status code 429
```
**Solution:**
```typescript
// Ajouter rate limiting
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));
await delay(1000);  // 1 seconde entre appels
```

### ❌ **Network Issues**
```
Failed to get real-time prices: connect ECONNREFUSED
```
**Solution:**
- Vérifier connectivité internet
- Tester avec VPN
- Vérifier configuration DNS

---

## 📊 Monitoring Continu

### **Logs à Surveiller**
```bash
# En temps réel
tail -f logs/novaquote.log | grep "PRICES"

# Erreurs API
grep "PRICES-ERROR" logs/novaquote.log

# Mode fallback
grep "PRICES-FALLBACK" logs/novaquote.log
```

### **Métriques Clés**
```json
{
  "api_status": "healthy | degraded | failed",
  "price_count": 469,
  "last_update": "2024-12-10T16:45:30.123Z",
  "cache_hits": 15,
  "api_errors": 0,
  "fallback_used": false
}
```

---

## 🔄 Auto-Récovery

### **1. Cache System**
```typescript
// Prix gardés en cache pendant 5 secondes
const cached = getFromCache('prices');
if (cached) {
  log.info('💰 Using cached real-time prices', 'PRICES-CACHE');
  return cached;
}
```

### **2. Fallback Prices**
```typescript
// Si API échoue → prix mock continuent de fonctionner
log.warn('Using fallback prices - system continues in degraded mode', 'PRICES-FALLBACK');
```

### **3. Retry Logic**
```typescript
// 3 tentatives avec backoff exponentiel
for (let attempt = 1; attempt <= 3; attempt++) {
  try {
    return await hlAPI.getAllMids();
  } catch (error) {
    if (attempt === 3) throw error;
    await delay(1000 * attempt); // 1s, 2s, 3s
  }
}
```

---

## 🧪 Tests de Validation

### **1. API Health Check**
```bash
curl http://localhost:7000/api/health
# Doit retourner: {"hyperliquid": true, "status": "healthy"}
```

### **2. Prices Endpoint**
```bash
curl http://localhost:7000/api/prices
# Doit retourner les prix actuels ou fallback
```

### **3. WebSocket Test**
```javascript
// Tester connexion WebSocket
const ws = new WebSocket('ws://localhost:7001');
ws.onopen = () => console.log('✅ WebSocket connecté');
ws.onerror = (e) => console.log('❌ WebSocket erreur:', e);
```

---

## ✅ Checklist de Résolution

- [ ] **Modules chargés** : `HyperliquidAPI` et `HyperliquidWebSocket`
- [ ] **API initialisée** : `hlAPI` non null au démarrage
- [ ] **Connectivité réseau** : Accès à `api.hyperliquid.xyz`
- [ ] **Logs status** : Pas d'erreurs dans les logs de démarrage
- [ ] **Cache fonctionnel** : Prix récupérés depuis cache
- [ ] **Fallback actif** : Prix mock si API échoue
- [ ] **WebSocket connecté** : Pas de déconnexions anormales

---

## 🚀 Résultat Attendu

Après corrections, vous devriez voir:

```
[SUCCESS] HyperLiquid modules loaded successfully
[INFO] HyperLiquid API loaded: ✅
[INFO] HyperLiquid WebSocket loaded: ✅
[SUCCESS] HyperLiquid API initialized
[INFO] 💰 Retrieved 469 real-time prices from HyperLiquid
```

**Plus de warnings "HyperLiquid API not available" !** 🎉

---

## 📞 Support et Debug

1. **Logs complets** : `logs/novaquote.log`
2. **Health check** : `http://localhost:7000/api/health`
3. **Documentation API** : https://docs.hyperliquid.xyz/

Le système continue de fonctionner même avec des problèmes temporaires grâce aux fallbacks ! 🛡️