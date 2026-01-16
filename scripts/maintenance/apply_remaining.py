"""
Filtrer et appliquer les corrections restantes (en excluant les mauvais matchings)
"""

import json
import re

# Charger les corrections
with open('remaining_corrections.json', 'r', encoding='utf-8') as f:
    corrections = json.load(f)

# Filtrer les mauvais matchings
bad_matches = {
    'Lait entier': 'Matché avec Laitue',
    'Lait demi-écrémé': 'Matché avec Laitue',
    'Banane': 'Banane plantain au lieu de banane normale',
    'Noix': 'Noix de coco au lieu de noix (walnut)',
}

good_corrections = []
skipped = []

for corr in corrections:
    if corr['name'] in bad_matches:
        skipped.append({
            'name': corr['name'],
            'reason': bad_matches[corr['name']]
        })
    else:
        good_corrections.append(corr)

print(f"{len(good_corrections)} bonnes corrections")
print(f"{len(skipped)} corrections ignorées\n")

# Lire views.py
with open(r'c:\Users\Clement\.gemini\antigravity\playground\icy-interstellar\fitness-tracker\tracker\views.py', 'r', encoding='utf-8') as f:
    views_content = f.read()

# Appliquer les corrections
applied = 0

for corr in good_corrections:
    food_name = corr['name']
    ciqual_name = corr['ciqual_name']
    nutrients = corr['nutrients']
    
    # Chercher la ligne dans views.py
    pattern = rf"\{{'name': '{re.escape(food_name)}'.*?\}}"
    match = re.search(pattern, views_content, re.DOTALL)
    
    if match:
        old_line = match.group(0)
        
        # Construire nouvelle ligne
        new_line = old_line
        for key, value in nutrients.items():
            if value > 0 or key in ['carbs', 'fiber']:  # Garder même si 0 pour carbs/fiber
                old_pattern = rf"'{key}': [\d.]+"
                new_val = f"'{key}': {value}"
                new_line = re.sub(old_pattern, new_val, new_line)
        
        # Ajouter commentaire source
        if "# Source:" not in old_line:
            indent = "        "
            comment = f"{indent}# Source: CIQUAL 2020 - {ciqual_name}\n{indent}"
            new_line = comment + new_line.lstrip()
        
        # Remplacer
        views_content = views_content.replace(old_line, new_line)
        applied += 1
        print(f"[{applied}] {food_name}")

# Sauvegarder
with open(r'c:\Users\Clement\.gemini\antigravity\playground\icy-interstellar\fitness-tracker\tracker\views.py', 'w', encoding='utf-8') as f:
    f.write(views_content)

print(f"\n{applied} corrections appliquées")
print(f"\nAliments ignorés:")
for skip in skipped:
    print(f"  - {skip['name']}: {skip['reason']}")
