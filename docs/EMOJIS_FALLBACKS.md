# 📝 Guide des Emojis & Fallbacks

## 🎨 Emojis Unicode Utilisés

| Emoji | Unicode | Fallback    | Nom               | Usage                 |
| ----- | ------- | ----------- | ----------------- | --------------------- |
| 🌍    | U+1F30D | [WORLD]     | Earth Globe       | Titre principal       |
| 🚀    | U+1F680 | [ROCKET]    | Rocket            | Lancement, action     |
| 🤖    | U+1F916 | [ROBOT]     | Robot             | Agents, IA            |
| ⚡    | U+26A1  | [LIGHTNING] | High Voltage      | Vitesse, énergie      |
| ⏱️    | U+23F1  | [CLOCK]     | Stopwatch         | Temps, deadline       |
| 📖    | U+1F4D6 | [BOOK]      | Open Book         | Documentation         |
| 💡    | U+1F4A1 | [BULB]      | Light Bulb        | Idées, conseils       |
| 🛠️    | U+1F6E0 | [WRENCH]    | Hammer and Wrench | Outils, scripts       |
| ✨    | U+2728  | [SPARKLES]  | Sparkles          | Avantages, magie      |
| 🎯    | U+1F3AF | [TARGET]    | Direct Hit        | Objectif, focus       |
| 🔥    | U+1F525 | [FIRE]      | Fire              | Performance, urgent   |
| 🏆    | U+1F3C6 | [TROPHY]    | Trophy            | Résultats, succès     |
| 👥    | U+1F465 | [PEOPLE]    | People            | Équipe, collaboration |
| 🌟    | U+1F31F | [STAR]      | Glowing Star      | Excellence            |
| 💪    | U+1F4AA | [FLEX]      | Flexed Biceps     | Force, pouvoir        |
| 🔄    | U+1F504 | [ARROWS]    | Counterclockwise  | Synchronisation       |
| 📊    | U+1F4CA | [CHART]     | Bar Chart         | Métriques             |
| 📈    | U+1F4C8 | [CHART_UP]  | Chart Increasing  | Croissance            |
| ✅    | U+2705  | [CHECK]     | Check Mark        | Validation            |
| ❌    | U+274C  | [CROSS]     | Cross Mark        | Erreur                |
| ⚠️    | U+26A0  | [WARNING]   | Warning           | Attention             |
| ℹ️    | U+2139  | [INFO]      | Information       | Info                  |
| 💻    | U+1F4BB | [LAPTOP]    | Laptop            | Code, tech            |
| 🎮    | U+1F3AE | [GAME]      | Video Game        | Contrôle, interface   |
| 🏗️    | U+1F3D7 | [BUILDING]  | Building          | Architecture          |
| 🧠    | U+1F9E0 | [BRAIN]     | Brain             | Intelligence          |
| 👁️    | U+1F441 | [EYE]       | Eye               | Monitoring            |
| 🔐    | U+1F510 | [LOCK]      | Locked            | Sécurité              |
| 🔍    | U+1F50D | [MAGNIFY]   | Magnifying Glass  | Recherche             |
| 🗂️    | U+1F5C2 | [FOLDER]    | File Folder       | Organisation          |
| 📋    | U+1F5C2 | [LIST]      | Clipboard         | Liste                 |
| 🔗    | U+1F517 | [LINK]      | Link              | Connexion             |
| 🌐    | U+1F310 | [GLOBE]     | Globe             | Réseau                |
| ⚙️    | U+2699  | [GEAR]      | Gear              | Configuration         |
| 🎨    | U+1F3A8 | [ART]       | Palette           | Design                |
| 📱    | U+1F4F1 | [MOBILE]    | Mobile            | App mobile            |
| 🖥️    | U+1F5A5 | [DESKTOP]   | Desktop           | Interface             |
| 💾    | U+1F4BE | [FLOPPY]    | Floppy Disk       | Stockage              |
| 🌊    | U+1F30A | [WAVE]      | Water Wave        | Flux                  |
| 🛡️    | U+1F6E1 | [SHIELD]    | Shield            | Protection            |
| 🎭    | U+1F3AD | [MASKS]     | Performing Arts   | Rôle                  |
| 🔑    | U+1F511 | [KEY]       | Key               | Accès                 |
| 📡    | U+1F4E1 | [SATELLITE] | Satellite Antenna | Communication         |
| ⚖️    | U+2696  | [SCALES]    | Balance           | Équilibre             |
| 🎪    | U+1F3AA | [CIRCUS]    | Circus Tent       | Orchestration         |
| 🎬    | U+1F3AC | [FILM]      | Movie Camera      | Action                |
| 🔥    | U+1F525 | [FIRE]      | Fire              | Hot, urgent           |
| 🎊    | U+1F38A | [CONFETTI]  | Confetti Ball     | Félicitations         |
| 💯    | U+1F4AF | [100]       | Hundred Points    | Parfait               |

## 🎯 Format Recommandé

### Dans le Code Markdown:

```markdown
# [WORLD] SWARM INTELLIGENCE

[ROCKET] Lancement rapide
[ROBOT] Agents spécialisés
[CLOCK] 20 minutes
```

### Dans les Interfaces:

```javascript
const EMOJI = {
  WORLD: '🌍 [WORLD]',
  ROCKET: '🚀 [ROCKET]',
  ROBOT: '🤖 [ROBOT]',
  CLOCK: '⏱️ [CLOCK]',
  BOOK: '📖 [BOOK]',
  BULB: '💡 [BULB]',
  WRENCH: '🛠️ [WRENCH]',
  SPARKLES: '✨ [SPARKLES]',
  TARGET: '🎯 [TARGET]',
  FIRE: '🔥 [FIRE]',
  TROPHY: '🏆 [TROPHY]',
  PEOPLE: '👥 [PEOPLE]',
  STAR: '🌟 [STAR]',
  FLEX: '💪 [FLEX]',
  ARROWS: '🔄 [ARROWS]',
  CHART: '📊 [CHART]',
  CHART_UP: '📈 [CHART_UP]',
  CHECK: '✅ [CHECK]',
  CROSS: '❌ [CROSS]',
  WARNING: '⚠️ [WARNING]',
  INFO: 'ℹ️ [INFO]',
  LAPTOP: '💻 [LAPTOP]',
  GAME: '🎮 [GAME]',
  BUILDING: '🏗️ [BUILDING]',
  BRAIN: '🧠 [BRAIN]',
  EYE: '👁️ [EYE]',
  LOCK: '🔐 [LOCK]',
  MAGNIFY: '🔍 [MAGNIFY]',
  FOLDER: '🗂️ [FOLDER]',
  LIST: '📋 [LIST]',
  LINK: '🔗 [LINK]',
  GLOBE: '🌐 [GLOBE]',
  GEAR: '⚙️ [GEAR]',
  ART: '🎨 [ART]',
  MOBILE: '📱 [MOBILE]',
  DESKTOP: '🖥️ [DESKTOP]',
  FLOPPY: '💾 [FLOPPY]',
  WAVE: '🌊 [WAVE]',
  SHIELD: '🛡️ [SHIELD]',
  MASKS: '🎭 [MASKS]',
  KEY: '🔑 [KEY]',
  SATELLITE: '📡 [SATELLITE]',
  SCALES: '⚖️ [SCALES]',
  CIRCUS: '🎪 [CIRCUS]',
  FILM: '🎬 [FILM]',
  CONFETTI: '🎊 [CONFETTI]',
  HUNDRED: '💯 [100]',
};

// Usage
console.log(`${EMOJIS.ROCKET} Lancement en cours...`);
```

## 🔧 Avantages

1. **Compatibilité**: Fonctionne même si les emojis ne s'affichent pas
2. **Lisibilité**: Texte clair entre crochets
3. **Accessibilité**: Meilleure pour les lecteurs d'écran
4. **Universalité**: Compatible tous systèmes
5. **Professionnel**: Plus formel pour documentation

## 📝 Règles d'Usage

- ✅ **Toujours** ajouter le fallback entre [CROCHETS]
- ✅ **Emoji d'abord**, puis le texte
- ✅ **Consistance** dans tout le document
- ❌ **Éviter** les emojis sans fallback
- ❌ **Pas** d'émojis dans les titres principaux
