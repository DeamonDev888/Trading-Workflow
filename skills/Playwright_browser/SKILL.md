# 🎭 Expert Playwright Browser Automation (MCP Integration)

## Définition Fondamentale

🚨 **Distinction cruciale** :
- **MCP Playwright Tools** = Outils MCP disponibles pour automatisation browser
- **Playwright Scripts** = Scripts d'automatisation personnalisés (sans MCP)

## Vue d'ensemble du système

Le **Playwright Browser Automation System** est une plateforme composée de :

- **20+ outils MCP Playwright** pour automatisation browser complète
- **Système de navigation web** avec gestion multi-onglets
- **Capacités de testing** et scraping web
- **Gestion de formulaires** et interactions utilisateur
- **Capture d'écrans** et snapshots d'accessibilité
- **Support multi-formats** pour exports (PNG, JPEG)

## 🏗️ Architecture Technique MCP

### Outils MCP Playwright disponibles
```bash
# Navigation et contrôle
mcp__playwright__browser_navigate()          # Navigation URL
mcp__playwright__browser_navigate_back()    # Retour page précédente
mcp__playwright__browser_tabs()             # Gestion onglets (list/new/close/select)
mcp__playwright__browser_close()            # Fermer page

# Interactions utilisateur
mcp__playwright__browser_click()            # Click simple/double/bouton droit
mcp__playwright__browser_type()             # Saisie texte
mcp__playwright__browser_fill_form()        # Remplir formulaires multiples
mcp__playwright__browser_select_option()    # Sélection dropdown
mcp__playwright__browser_drag()             # Drag & drop
mcp__playwright__browser_hover()            # Survol éléments
mcp__playwright__browser_press_key()        # Appuis clavier

# Gestion dialogue et fichiers
mcp__playwright__browser_handle_dialog()    # Gérer boîtes de dialogue
mcp__playwright__browser_file_upload()      # Upload fichiers

# Évaluation et monitoring
mcp__playwright__browser_evaluate()         # Exécuter JavaScript
mcp__playwright__browser_console_messages() # Messages console (erreurs)
mcp__playwright__browser_network_requests() # Requêtes réseau
mcp__playwright__browser_wait_for()         # Attente conditions

# Capture et analyse
mcp__playwright__browser_snapshot()         # Snapshot accessibilité
mcp__playwright__browser_take_screenshot()  # Screenshots
mcp__playwright__browser_resize()           # Redimensionner fenêtre

# Configuration
mcp__playwright__browser_install()          # Installation browser
```

## 🤖 Classification des Fonctionnalités

### 🌐 **Navigation Web**
Ces outils gèrent **la navigation et le contrôle du browser** :

1. **`browser_navigate()`** ✅
   - Fonction : Navigation vers URL
   - Paramètres : `url` (obligatoire)

2. **`browser_navigate_back()`** ✅
   - Fonction : Retour page précédente

3. **`browser_tabs()`** ✅
   - Fonction : Gestion onglets (list/new/close/select)
   - Paramètres : `action`, `index` (optionnel)

### 🖱️ **Interactions Utilisateur**
Ces outils gèrent **les interactions utilisateur avancées** :

4. **`browser_click()`** ✅
   - Fonction : Click (simple/double/droit)
   - Paramètres : `element`, `ref`, `doubleClick`, `button`, `modifiers`

5. **`browser_type()`** ✅
   - Fonction : Saisie texte avec options
   - Paramètres : `element`, `ref`, `text`, `submit`, `slowly`

6. **`browser_fill_form()`** ✅
   - Fonction : Remplissage formulaire multiple
   - Paramètres : `fields[]` (nom, type, ref, valeur)

### 📋 **Gestion Formulaires**
Ces outils gèrent **les formulaires et fichiers** :

7. **`browser_select_option()`** ✅
   - Fonction : Sélection dropdown
   - Paramètres : `element`, `ref`, `values[]`

8. **`browser_file_upload()`** ✅
   - Fonction : Upload fichiers multiples
   - Paramètres : `paths[]`

### ⌨️ **Contrôle Clavier**
9. **`browser_press_key()`** ✅
    - Fonction : Appuis clavier
    - Paramètres : `key` (ex: "ArrowLeft", "a", "Enter")

### 🔄 **Drag & Drop**
10. **`browser_drag()`** ✅
    - Fonction : Drag & drop entre éléments
    - Paramètres : `startElement`, `startRef`, `endElement`, `endRef`

## 🔧 **Use Patterns et Workflows**

### Workflow 1: Navigation et Extraction
```javascript
// 1. Naviguer vers page
await mcp__playwright__browser_navigate({url: "https://example.com"});

// 2. Prendre snapshot pour analyser contenu
await mcp__playwright__browser_snapshot();

// 3. Remplir formulaire
await mcp__playwright__browser_fill_form({
    fields: [
        {name: "username", type: "textbox", ref: "input#username", value: "user123"},
        {name: "password", type: "textbox", ref: "input#password", value: "pass123"}
    ]
});

// 4. Soumettre
await mcp__playwright__browser_click({
    element: "Login button",
    ref: "button[type='submit']"
});
```

### Workflow 2: Testing et Validation
```javascript
// 1. Navigation
await mcp__playwright__browser_navigate({url: "https://app.test.com"});

// 2. Tester formulaire
await mcp__playwright__browser_fill_form({
    fields: [
        {name: "email", type: "textbox", ref: "input#email", value: "test@example.com"}
    ]
});

// 3. Vérifier console erreurs
const errors = await mcp__playwright__browser_console_messages({onlyErrors: true});

// 4. Capturer écran pour preuve
await mcp__playwright__browser_take_screenshot({
    type: "png",
    filename: "test-result.png",
    element: "Page complète",
    fullPage: true
});
```

### Workflow 3: Scraping Web
```javascript
// 1. Navigation page cible
await mcp__playwright__browser_navigate({url: "https://target-site.com"});

// 2. Attendre chargement contenu
await mcp__playwright__browser_wait_for({
    time: 3,
    text: "Chargement terminé"
});

// 3. Extraire données avec JavaScript
const data = await mcp__playwright__browser_evaluate({
    function: "() => Array.from(document.querySelectorAll('.product')).map(el => ({title: el.querySelector('h3').textContent, price: el.querySelector('.price').textContent}))"
});

// 4. Sauvegarder screenshot
await mcp__playwright__browser_take_screenshot({
    type: "jpeg",
    filename: "scraping-result.jpg",
    fullPage: true
});
```

## 📊 **Applications Pratiques**

### 🛒 **E-commerce Automation**
- Login sites marchands
- Recherche produits
- Ajout panier
- Checkout automatique
- Vérification prix

### 💼 **Business Intelligence**
- Monitoring concurrents
- Extraction rapports
- Vérification disponibilité services
- Tests A/B

### 🔍 **Testing Web**
- Tests fonctionnels
- Tests UI/UX
- Vérification accessibilité
- Monitoring performance

### 📈 **Data Collection**
- Scraping données structurées
- Monitoring prix
- Veille concurrentielle
- Analyse marché

## 🔧 **Configuration et Setup**

### Installation Prérequis
```bash
# 1. Configurer MCP server Playwright
npm install @modelcontextprotocol/server-playwright

# 2. Installation browser (si nécessaire)
await mcp__playwright__browser_install();
```

### Configuration Taille Fenêtre
```javascript
// Pour captures d'écran optimisées
await mcp__playwright__browser_resize({
    width: 1920,
    height: 1080
});
```

## 📝 **Best Practices**

### ✅ **Pratiques Recommandées**
- Toujours utiliser `browser_snapshot()` avant interactions
- Attendre chargement avec `browser_wait_for()`
- Gérer erreurs console avec `browser_console_messages()`
- Utiliser `fullPage: true` pour captures complètes
- Sauvegarder screenshots avec timestamps

### ❌ **À Éviter**
- Interactions sans vérification préalable
- Oublier de gérer popups/dialogues
- Naviguer sans attente de chargement
- Utiliser sélecteurs CSS fragiles

## 🔍 **Monitoring et Debug**

### Messages Console
```javascript
// Erreurs seulement
const errors = await mcp__playwright__browser_console_messages({onlyErrors: true});

// Tous les messages
const allMessages = await mcp__playwright__browser_console_messages({onlyErrors: false});
```

### Requêtes Réseau
```javascript
const requests = await mcp__playwright__browser_network_requests();
// Analyser appels API, ressources, etc.
```

### Évaluation JavaScript
```javascript
const result = await mcp__playwright__browser_evaluate({
    function: "() => document.title"
});
```

## 🎯 **Cas d'Usage Avancés**

### Multi-Onglets
```javascript
// Ouvrir nouvel onglet
await mcp__playwright__browser_tabs({action: "new"});

// Lister onglets
await mcp__playwright__browser_tabs({action: "list"});

// Sélectionner onglet
await mcp__playwright__browser_tabs({action: "select", index: 1});
```

### Gestion Dialogues
```javascript
// Accepter dialogue
await mcp__playwright__browser_handle_dialog({
    accept: true,
    promptText: "Texte optionnel"
});

// Refuser dialogue
await mcp__playwright__browser_handle_dialog({
    accept: false
});
```

## 📚 **Références MCP**

### Outils MCP disponibles
- Tous les outils préfixés `mcp__playwright__browser_*`
- Configuration via serveur MCP Playwright
- Support multi-browsers (Chrome, Firefox, Safari)

---

*Skill basé sur les outils MCP Playwright disponibles - Expert en automatisation browser et testing web*