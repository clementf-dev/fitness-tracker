"""
Script final pour appliquer les corrections dans views.py
"""

import json
import re
import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Lire les corrections
with open('corrections_to_apply.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

corrections = data['corrections']

# Lire views.py
with open(r'c:\Users\Clement\.gemini\antigravity\playground\icy-interstellar\fitness-tracker\tracker\views.py', 'r', encoding='utf-8') as f:
    views_content = f.read()

print(f"Application de {len(corrections)} corrections...\n")

# Appliquer chaque correction
for i, corr in enumerate(corrections, 1):
    old_text = corr['old']
    new_text = corr['new']
    food_name = corr['food']
    
    if old_text in views_content:
        views_content = views_content.replace(old_text, new_text)
        print(f"[{i}/{len(corrections)}] {food_name}")
    else:
        print(f"[{i}/{len(corrections)}] ERREUR: {food_name} - texte non trouvé")

# Sauvegarder le fichier modifié
with open(r'c:\Users\Clement\.gemini\antigravity\playground\icy-interstellar\fitness-tracker\tracker\views.py', 'w', encoding='utf-8') as f:
    f.write(views_content)

print(f"\n{len(corrections)} corrections appliquées dans views.py")
