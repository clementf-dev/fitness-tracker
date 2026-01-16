# Fitness Tracker Web App

Une application Django personnelle pour suivre ses données de santé (Poids, Pas, Calories) et synchroniser automatiquement avec Google Fit via FitSync (Android).

## Fonctionnalités

*   **Tableau de Bord :** Visualisation des courbes de poids, masse grasse, et activité.
*   **Journal Alimentaire :** Suivi des calories et macros (Protéines, Glucides, Lipides).
*   **Synchronisation Drive :** Import automatique des fichiers CSV générés par l'application Android FitSync.
*   **Base de Données CIQUAL :** Recherche d'aliments intégrée.

## Installation Locale

1.  Cloner le projet.
2.  Installer les dépendances : `pip install -r requirements.txt`
3.  Configurer l'authentification Google :
    *   Placer `credentials.json` à la racine (Client ID OAuth 2.0).
4.  Lancer le serveur : `python manage.py runserver`

## Déploiement (PythonAnywhere)

Ce projet est prêt pour être déployé sur PythonAnywhere.

**Important :**
*   Le fichier `.gitignore` est configuré pour **ne pas envoyer** votre base de données locale (`data/fitness.db`) ni vos secrets (`credentials.json`, `token.json`) sur GitHub.
*   Vous devrez uploader ces fichiers manuellement dans votre espace privé PythonAnywhere.

## Structure

*   `fitness_tracker/` : Configuration Django.
*   `tracker/` : Application principale (Modèles, Vues).
*   `scripts/` : Scripts de maintenance et d'import de données.
*   `data/` : Dossier contenant la base de données SQLite (Exclu de Git).
