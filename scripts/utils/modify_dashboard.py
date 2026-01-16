"""
Script pour modifier calories_dashboard.html et ajouter l'autocomplétion
"""
import re

# Lire le fichier
with open(r'c:\Users\Clement\.gemini\antigravity\playground\icy-interstellar\fitness-tracker\tracker\templates\tracker\calories_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remplacement du select par l'input avec autocomplétion
old_select = r'<select name="food" class="form-select"[^>]*>.*?</select>'
new_input = '''<div style="position: relative; flex: 1; min-width: 200px;">
                        <input type="text" class="form-control food-search-input" 
                            placeholder="Rechercher un aliment..." autocomplete="off"
                            style="background-color: #2b2d42; color: #ffffff; border-color: rgba(255, 255, 255, 0.1);">
                        <input type="hidden" name="food" class="selected-food-id" required>
                        <div class="autocomplete-results" style="position: absolute; top: 100%; left: 0; right: 0; background: #1a1c2e; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; max-height: 300px; overflow-y: auto; display: none; z-index: 1000; margin-top: 4px;"></div>
                    </div>'''

content = re.sub(old_select, new_input, content, flags=re.DOTALL)

# Ajouter le script avant {% endblock %}
if 'food_autocomplete.js' not in content:
    content = content.replace('{% endblock %}', '''<script src="{% static 'tracker/js/food_autocomplete.js' %}"></script>
{% endblock %}''')

# Sauvegarder
with open(r'c:\Users\Clement\.gemini\antigravity\playground\icy-interstellar\fitness-tracker\tracker\templates\tracker\calories_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Fichier modifié avec succès")
print("✓ Select remplacé par input avec autocomplétion")
print("✓ Script food_autocomplete.js ajouté")
