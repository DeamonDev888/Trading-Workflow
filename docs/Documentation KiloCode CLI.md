# Documentation KiloCode CLI - Utilisation des Sous-Agents

## Vue d'ensemble

KiloCode CLI est un outil de ligne de commande avancé qui permet d'interagir avec des modèles d'IA pour l'assistance au développement logiciel. L'une de ses fonctionnalités les plus puissantes est le système de sous-agents, qui permet de déléguer des tâches spécifiques à des agents spécialisés.

## Installation

KiloCode CLI est déjà installé sur votre système et prêt à être utilisé.

## Configuration

KiloCode CLI utilise un système de configuration flexible. Le fichier de configuration principal se trouve généralement dans `~/.kilocode/cli/config.json`.

### Modèles Disponibles

Voici les modèles actuellement disponibles avec KiloCode :

- **⭐ x-ai/grok-code-fast-1** (modèle actuel)
  - xAI: Grok Code Fast 1 (gratuit)
  - 256K contexte | $0.00/$0.00 par 1M | Cache, Reasoning

- **⭐ minimax/minimax-m2:free**
  - MiniMax: MiniMax M2 (gratuit)
  - 204K contexte | $0.00/$0.00 par 1M | Reasoning

### Exemple de configuration

```json
{
  "provider": "kilocode",
  "model": "x-ai/grok-code-fast-1"
}
```

## Les Modes de Fonctionnement (Sous-Agents)

### Qu'est-ce qu'un Mode/Sous-Agent ?

KiloCode CLI utilise différents modes de fonctionnement qui agissent comme des sous-agents spécialisés. Chaque mode est optimisé pour une tâche spécifique et utilise l'IA de manière ciblée.

### Modes Disponibles

#### 1. Mode Architect (`architect`)
Mode pour la conception et l'architecture logicielle. Idéal pour planifier la structure d'un projet.

```bash
kilocode -m architect "Concevoir l'architecture d'une application web moderne"
```

#### 2. Mode Code (`code`)
Mode pour l'écriture et modification de code. Génère du code directement.

```bash
kilocode -m code "Créer une fonction de validation d'email en JavaScript"
```

#### 3. Mode Ask (`ask`)
Mode conversationnel pour poser des questions et obtenir des réponses générales.

```bash
kilocode -m ask "Quelles sont les meilleures pratiques pour l'optimisation React ?"
```

#### 4. Mode Debug (`debug`)
Mode spécialisé pour le débogage et la résolution de problèmes. Supporte les modes `os` et `keyboard`.

```bash
kilocode debug os  # Diagnostic système
```

#### 5. Mode Orchestrator (`orchestrator`)
Mode avancé pour coordonner multiples tâches et workflows complexes.

```bash
kilocode -m orchestrator "Migrer cette base de données de MySQL vers PostgreSQL"
```

## Utilisation Avancée des Modes

### Mode Autonome

Pour utiliser les modes en mode non-interactif (utile pour la CI/CD et l'automatisation) :

```bash
kilocode -m architect --auto "Concevoir l'architecture pour une app mobile"
kilocode -m code --auto "Créer un composant React pour afficher une liste d'éléments"
```

### Mode Parallèle

Exécutez des tâches en parallèle en créant des branches git séparées :

```bash
kilocode -m code --parallel "Implémenter la fonctionnalité de recherche"
```

### Configuration des Espaces de Travail

Définissez différents espaces de travail pour différents projets :

```bash
kilocode -w ./mon-projet-frontend "Créér un nouveau composant"
kilocode -w ./mon-api-backend -m architect "Concevoir les endpoints API"
```

### Continuation de Conversation

Reprendre une conversation précédente dans le même espace de travail :

```bash
kilocode --continue -m code "Continuer l'implémentation de la fonction utilitaire"
```

## Commandes Spécialisées

### Diagnostic Système

```bash
# Diagnostic complet du système
kilocode debug os

# Diagnostic du clavier
kilocode debug keyboard
```

### Gestion de l'Authentification

```bash
# Configurer l'authentification
kilocode auth

# Ouvrir la configuration
kilocode config
```

## Workflows Pratiques

### Développement en Mode Architect + Code

```bash
# Étape 1: Concevoir
kilocode -m architect "Concevoir une architecture microservices pour une plateforme e-commerce"

# Étape 2: Implémenter
kilocode -m code "Créer le service d'authentification basé sur le design précédant"
```

### Revue et Résolution de Bugs

```bash
# Mode orchestrator pour coordonner la résolution
kilocode -m orchestrator "Résoudre le bug de performance dans la fonction de recherche"

# Mode debug pour analyser les problèmes système
kilocode debug os  # Diagnostics système si nécessaire
```

### Développement Itératif

```bash
# Garder le contexte avec --continue pour les sessions itératives
kilocode -m code --continue "Améliorer la gestion d'erreurs dans la fonction validateUser"
```

## Configuration Avancée

### Variables d'Environnement

Basé sur votre configuration actuelle avec MiniMax :

```bash
export KILOCODE_PROVIDER=minimax
export KILOCODE_MODEL=minimax/minimax-m2:free
```

Pour utiliser xAI :

```bash
export KILOCODE_PROVIDER=xai
export KILOCODE_MODEL=x-ai/grok-code-fast-1
```

## Test Final de Validation

Pour confirmer que votre documentation est fonctionnelle, testez avec une commande simple :

```bash
# Test du mode de diagnostic
kilocode debug os

# Test d'un mode principal
kilocode -m ask --auto "Confirmer que KiloCode fonctionne"
```

## Meilleures Pratiques

### 1. Choix du Bon Mode

- **Architect** : Utilisez pour la planification et conception avant le développement
- **Code** : Idéal pour l'écriture et modification de code existant
- **Ask** : Parfait pour les questions contextuelles et conseils généraux
- **Debug** : Utile pour diagnostiquer les problèmes système ou applicatifs
- **Orchestrator** : Meilleur pour les tâches complexes nécessitant coordination

### 2. Optimisation des Performances

```bash
# Mode autonome pour les tâches répétitives
kilocode -m code --auto "Créer des getters/setters TypeScript"

# Utiliser des workspaces dédiés pour des projets séparés
kilocode -w ./frontend -m code "Implémenter le composant de recherche"

# Mode parallèle pour les tâches indépendantes
kilocode -m code --parallel "Développer la fonction de pagination"
```

### 3. Gestion des Sessions Itératives

```bash
# Continuer une session précédente
kilocode --continue -m code "Améliorer la fonction de validation"

# Sauvegarder l'historique pour référence future
kilocode --continue "Documenter les changements apportés"
```

## Exemples Pratiques

### Développement d'une Application Web Moderne

#### Étape 1: Architecture et Planification
```bash
kilocode -m architect "Concevoir l'architecture d'une app React avec API REST"
```

#### Étape 2: Implémentation du Frontend
```bash
kilocode -m code "Créer les composants React pour le dashboard utilisateur"
```

#### Étape 3: Développement Backend
```bash
kilocode -m code "Implémenter les endpoints API pour la gestion des utilisateurs"
```

### Résolution de Bugs et Optimisation

#### Diagnostic Système
```bash
kilocode debug os  # Vérifier les ressources système
```

#### Analyse du Problème
```bash
kilocode -m orchestrator "Analyser et résoudre le problème de performance"
```

#### Implémentation de la Solution
```bash
kilocode -m code --auto "Optimiser les requêtes de base de données"
```

### Migration et Refactoring

#### Planification de la Migration
```bash
kilocode -m architect "Planifier la migration de jQuery vers React"
```

#### Conversion Itérative
```bash
# Première itération
kilocode -m code "Convertir le module de login vers React"

# Continuation pour affiner
kilocode --continue "Améliorer la gestion d'état du composant"
```

## Dépannage

### Problèmes Courants

1. **Mode qui ne répond pas** : Vérifiez la configuration du provider (`minimax` ou autre)
2. **Résultats inattendus** : Utilisez le mode approprié pour votre tâche
3. **Performance lente** : Essayez le modèle plus performant ou mode `--auto`

### Commandes de Diagnostic

```bash
# Diagnostic système complet
kilocode debug os

# Vérifier la configuration actuelle
kilocode config

# Test de connectivité avec le provider
# Le CLI affichera des erreurs spécifiques si la configuration est incorrecte
```

## Ressources Supplémentaires

- [Documentation Officielle](https://docs.kilocode.org/)
- [Guide des Agents](https://docs.kilocode.org/agents/)
- [Exemples de Workflows](https://github.com/Kilo-Org/kilocode-examples)
- [Forum de la Communauté](https://community.kilocode.org/)

## Version

Cette documentation couvre KiloCode CLI v2.1.0+
