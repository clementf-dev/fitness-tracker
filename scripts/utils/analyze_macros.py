"""
Recalculer tous les GENERIC_FOODS avec les bonnes valeurs pour le poids unitaire.
Les valeurs CIQUAL sont pour 100g, il faut les adapter au unit_weight.
"""

import re

# Lire views.py
with open(r'c:\Users\Clement\.gemini\antigravity\playground\icy-interstellar\fitness-tracker\tracker\views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Extraire la section GENERIC_FOODS
start = content.find('GENERIC_FOODS = [')
end = content.find('\n    ]', start) + len('\n    ]')
generic_foods_section = content[start:end]

# Parser chaque aliment
import ast
# Extraire juste la liste
list_str = generic_foods_section.replace('GENERIC_FOODS = ', '')
# Évaluer de manière sécurisée n'est pas possible avec les commentaires, donc on va parser manuellement

# Pattern pour trouver les entrées
pattern = r"\{'name': '([^']+)',\s*'calories': ([\d.]+),\s*'protein': ([\d.]+),\s*'carbs': ([\d.]+),\s*'fat': ([\d.]+),\s*'fiber': ([\d.]+),\s*'unit_weight': ([\d.]+)"

matches = re.findall(pattern, generic_foods_section)

print(f"Trouvé {len(matches)} aliments")
print("\nExemples de recalcul (valeurs actuelles sont pour 100g, pas pour unit_weight):")
print("-" * 80)

for i, match in enumerate(matches[:5]):
    name, cal, prot, carbs, fat, fiber, unit_weight = match
    cal, prot, carbs, fat, fiber, unit_weight = float(cal), float(prot), float(carbs), float(fat), float(fiber), float(unit_weight)
    
    # Les valeurs actuelles semblent être pour 100g (d'après CIQUAL)
    # Il faut les recalculer pour unit_weight
    cal_unit = round(cal * unit_weight / 100, 1)
    prot_unit = round(prot * unit_weight / 100, 1)
    carbs_unit = round(carbs * unit_weight / 100, 1)
    fat_unit = round(fat * unit_weight / 100, 1)
    fiber_unit = round(fiber * unit_weight / 100, 1)
    
    print(f"{name} ({unit_weight}g):")
    print(f"  Actuel: {cal} kcal, P:{prot}g, G:{carbs}g, L:{fat}g, F:{fiber}g")
    print(f"  Correct: {cal_unit} kcal, P:{prot_unit}g, G:{carbs_unit}g, L:{fat_unit}g, F:{fiber_unit}g")
    print()

print("\nVoulez-vous appliquer ces corrections? (créer un nouveau script)")
