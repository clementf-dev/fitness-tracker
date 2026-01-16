# 💪 Fitness Tracker

Application Django pour suivre votre santé et fitness au quotidien.

## 🎯 Fonctionnalités

- 📊 **Suivi du poids** - Importez ou saisissez manuellement vos données de poids et composition corporelle
- 👟 **Suivi des pas** - Suivez vos pas quotidiens depuis Google Fit ou manuellement
- 🏋️ **Séances de salle** - Marquez les jours où vous allez à la salle
- ❤️ **Cardio** - Suivez votre cardio (marche sur tapis, vélo)
- 🍽️ **Repas** - Trackez vos calories
- 📈 **Graphiques interactifs** - Visualisez votre évolution avec Chart.js

## 🚀 Installation

### Prérequis
- Python 3.8 ou supérieur
- pip

### Étapes d'installation

1. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

2. **Créer la base de données**
```bash
python manage.py migrate
```

3. **Créer un compte administrateur** (optionnel)
```bash
python manage.py createsuperuser
```

4. **Lancer le serveur**
```bash
python manage.py runserver
```

5. **Ouvrir l'application**
Ouvrez votre navigateur et allez sur : `http://localhost:8000`

## 📁 Importer des données CSV

### Depuis HealthSync (Google Fit)

1. Synchronisez vos données Google Fit avec Google Drive via HealthSync
2. Téléchargez les fichiers CSV depuis votre Drive
3. Dans l'application, allez sur **Importer CSV**
4. Sélectionnez le type de données (Poids, Pas, ou Activités)
5. Choisissez le fichier CSV correspondant
6. Cliquez sur **Importer**

### Format des fichiers CSV

**Poids :**
```
Date,Heure,Poids,Pourcentage de graisse corporelle,...
2026.01.07 11:33:25,11:33:25,86.1,24.18,...
```

**Pas :**
```
Date,Heure,Pas
2025.12.01 06:22:32,06:22:32,1098
```


## ✏️ Saisie manuelle

Vous pouvez également saisir toutes les données manuellement via le dashboard :
- Cliquez sur les boutons **➕ Poids**, **👟 Pas**, **🏃 Activité**, etc.
- Remplissez le formulaire
- Enregistrez

## 🔧 Troubleshooting HealthSync

Si vos données ne se synchronisent pas :
1. Vérifiez que HealthSync est bien configuré
2. Vérifiez l'intervalle de synchronisation dans les paramètres HealthSync
3. Assurez-vous que Google Fit a bien reçu les données de votre appareil
4. Vérifiez manuellement votre Google Drive pour voir si les fichiers CSV sont à jour

## 📊 Utilisation

### Dashboard
Le dashboard affiche :
- Statistiques rapides (poids actuel, moyenne des pas, etc.)
- Boutons d'action rapide pour ajouter des données
- Graphiques d'évolution (poids, pas, calories)

### Admin Panel
Accédez à `/admin/` pour gérer toutes vos données avec l'interface d'administration Django.

## 🛠️ Structure du projet

```
fitness-tracker/
├── fitness_tracker/        # Configuration Django
│   ├── settings.py
│   └── urls.py
├── tracker/               # Application principale
│   ├── models.py         # Modèles de données
│   ├── views.py          # Vues et logique
│   ├── forms.py          # Formulaires
│   ├── urls.py           # Routes
│   ├── admin.py          # Configuration admin
│   └── templates/        # Templates HTML
├── data/                 # Base de données SQLite
│   └── fitness.db
├── requirements.txt      # Dépendances Python
└── manage.py            # Script Django
```

## 🎨 Technologies utilisées

- **Backend** : Django 4.2
- **Base de données** : SQLite
- **Frontend** : Bootstrap 5, Chart.js
- **Formulaires** : Django Crispy Forms
- **Parsing CSV** : Pandas, python-dateutil

## 📝 Licence

Projet personnel - Libre d'utilisation

---

