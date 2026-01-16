---
description: Corriger les boutons de suppression qui ne fonctionnent pas
---
// turbo-all

# Résolution du bug des boutons de suppression

Ce workflow documente la solution au bug récurrent où les boutons de suppression (🗑️) ne fonctionnent pas au clic.

## Diagnostic

Le problème se manifeste généralement par :
- Clic sur la corbeille sans effet
- Pas de message d'erreur visible
- La page ne se recharge pas

## Causes racines identifiées

1. **Requêtes GET au lieu de POST** : Les liens `<a href>` pour la suppression sont vulnérables au cache/prefetch du navigateur
2. **Dialogues `confirm()` bloqués** : Le `onclick="return confirm(...)"` peut être annulé ou bloqué
3. **Protection CSRF manquante** : Django rejette les POST sans token CSRF
4. **Décorateur `@require_POST` absent** : La vue accepte les GET, ce qui cause des comportements imprévisibles

## Solution en 4 étapes

### Étape 1 : Convertir le lien en formulaire POST

**Avant (problématique)** :
```html
<a href="{% url 'delete_item' id=item.id %}" onclick="return confirm('Supprimer ?')">🗑️</a>
```

**Après (correct)** :
```html
<form method="post" action="{% url 'delete_item' id=item.id %}" style="display: inline;">
    {% csrf_token %}
    <button type="submit" class="delete-btn" title="Supprimer">🗑️</button>
</form>
```

### Étape 2 : Ajouter le décorateur @require_POST à la vue

```python
from django.views.decorators.http import require_POST

@login_required
@require_POST  # Ajouter cette ligne
def delete_item(request, id):
    item = get_object_or_404(Model, id=id)
    item.delete()
    messages.success(request, "Élément supprimé.")
    return redirect('list_view')
```

### Étape 3 : Retirer les confirm() si nécessaire

Les dialogues `confirm()` peuvent causer des problèmes. Si le bouton ne fonctionne toujours pas, retirer l'attribut `onclick`.

### Étape 4 : Vérifier l'encodage du template (si erreurs Django)

Si une `TemplateSyntaxError` ou `UnicodeDecodeError` apparaît :

1. Vérifier les espaces autour des opérateurs Django : `{% if a == b %}` (pas `{% if a==b %}`)
2. Si le fichier est corrompu, utiliser ce script Python :

```python
filepath = r'chemin/vers/template.html'

with open(filepath, 'rb') as f:
    content = f.read()

# Retirer le BOM si présent
if content.startswith(b'\xef\xbb\xbf'):
    content = content[3:]

# Normaliser les fins de ligne
content = content.replace(b'\r\r\n', b'\r\n')

# Décoder et corriger les caractères corrompus
text = content.decode('utf-8', errors='replace')
text = text.replace('\ufffd', 'é')  # Remplacer par le caractère approprié selon contexte

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(text)
```

## Fichiers typiquement concernés

- `tracker/templates/tracker/calories_dashboard.html` - Suppression MealItem
- `tracker/templates/tracker/meal_templates.html` - Suppression MealTemplate
- `tracker/templates/tracker/edit_meal_template.html` - Suppression MealTemplateItem
- `tracker/templates/tracker/food_database.html` - Suppression Food
- `tracker/views/calories.py` - Vue delete_meal_item
- `tracker/views/templates_views.py` - Vues delete_meal_template, delete_template_item
- `tracker/views/food.py` - Vue delete_food

## Test de vérification

1. Ouvrir la page concernée dans le navigateur
2. Cliquer sur un bouton 🗑️
3. L'élément doit être supprimé immédiatement sans confirmation
4. Un message de succès doit s'afficher
