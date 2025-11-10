# 🌍 SWARM INTELLIGENCE - QUICK START

## ⚡ Lancement Ultra-Rapide (1 minute)

### 1. Double-Click

```
double-click: quick-start-swarm.bat
```

### 2. Ou en Ligne de Commande

```bash
node scripts/launch-swarm.js check
node scripts/launch-swarm.js hybrid
```

## 📁 Fichiers Clés

| Fichier                      | Description                             |
| ---------------------------- | --------------------------------------- |
| `claude-agents.json`         | Configuration principale du swarm       |
| `.claude/agents/`            | Configurations individuelles des agents |
| `scripts/launch-swarm.js`    | Script principal Node.js                |
| `docs/SWARM_AGENTS_GUIDE.md` | Documentation complète                  |
| `quick-start-swarm.bat`      | Lancement Windows rapide                |

## 🎯 Usage Immédiat

```bash
# Vérifier les agents
node scripts/launch-swarm.js list

# Lancement hybride (recommandé)
node scripts/launch-swarm.js hybrid

# Lancement parallèle
node scripts/launch-swarm.js parallel

# Workflow spécifique
node scripts/launch-swarm.js workflow full_stack_app
```

## 🛠️ Personnalisation

Modifiez `claude-agents.json` pour adapter à votre domaine :

```json
{
  "swarm_metadata": {
    "name": "MON_SWARM",
    "description": "Description de votre mission"
  },
  "agents": [
    {
      "id": "expert-1",
      "name": "Mon Expert",
      "role": "Sa spécialité",
      "priority": "high"
    }
  ]
}
```

**⏱️ Temps: 5-10 minutes pour créer votre swarm personnalisé !**

## 📚 Documentation

Pour la documentation complète, consultez:
`docs/SWARM_AGENTS_GUIDE.md`

---

**🚀 Prêt à construire votre armée d'agents en 20 minutes !**
