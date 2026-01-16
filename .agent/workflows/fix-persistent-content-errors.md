---
description: Stratégie pour corriger les erreurs de contenu persistantes (résistantes aux éditeurs classiques)
---

# Fix Persistent Content Errors

Si une erreur de contenu (syntaxe, texte, etc.) persiste malgré plusieurs tentatives de correction via les outils d'édition classiques (`replace_file_content`, `multi_replace_file_content`), suivre cette procédure impérativement :

1. **Arrêter l'utilisation des éditeurs** : Ne plus tenter `replace_file_content`.
2. **Vérifier via Terminal** : Utiliser `Get-Content` (PowerShell) ou `cat` (Bash) pour lire le fichier tel qu'il est réellement sur le disque.
3. **Corriger via Terminal** : Utiliser une commande système pour écraser le contenu ou faire un remplacement regex.
   - PowerShell : `(Get-Content 'path/to/file') -replace 'Old', 'New' | Set-Content 'path/to/file'`
   - Si le remplacement est complexe, réécrire tout le fichier via `Set-Content`.
4. **Vérifier le Fix** : Relire le fichier via Terminal pour confirmer la modification.

// turbo-all
Cette annotation assure que toutes les commandes de ce workflow sont exécutées sans confirmation utilisateur (SafeToAutoRun=true).
