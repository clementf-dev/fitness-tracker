"""
Recalculer et appliquer les corrections pour GENERIC_FOODS.
Convertir les valeurs /100g en valeurs pour unit_weight.
"""

import re

print("Lecture de views.py...")
with open(r'c:\Users\Clement\.gemini\antigravity\playground\icy-interstellar\fitness-tracker\tracker\views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern pour matcher une entrée complète
pattern = r"(\s*(?:#[^\n]*\n\s*)*\{'name': '([^']+)',\s*'calories': ([\d.]+),\s*'protein': ([\d.]+),\s*'carbs': ([\d.]+),\s*'fat': ([\d.]+),\s*'fiber': ([\d.]+),\s*'unit_weight': ([\d.]+)[^}]*\})"

def replace_food(match):
    full_match = match.group(0)
    name = match.group(2)
    cal_100g = float(match.group(3))
    prot_100g = float(match.group(4))
    carbs_100g = float(match.group(5))
    fat_100g = float(match.group(6))
    fiber_100g = float(match.group(7))
    unit_weight = float(match.group(8))
    
    # Recalculer pour unit_weight
    cal_unit = round(cal_100g * unit_weight / 100, 1)
    prot_unit = round(prot_100g * unit_weight / 100, 1)
    carbs_unit = round(carbs_100g * unit_weight / 100, 1)
    fat_unit = round(fat_100g * unit_weight / 100, 1)
    fiber_unit = round(fiber_100g * unit_weight / 100, 1)
    
    # Reconstruire l'entrée avec les nouvelles valeurs
    # Garder les commentaires et la structure
    new_entry = re.sub(
        r"'calories': [\d.]+",
        f"'calories': {cal_unit}",
        full_match
    )
    new_entry = re.sub(
        r"'protein': [\d.]+",
        f"'protein': {prot_unit}",
        new_entry
    )
    new_entry = re.sub(
        r"'carbs': [\d.]+",
        f"'carbs': {carbs_unit}",
        new_entry
    )
    new_entry = re.sub(
        r"'fat': [\d.]+",
        f"'fat': {fat_unit}",
        new_entry
    )
    new_entry = re.sub(
        r"'fiber': [\d.]+",
        f"'fiber': {fiber_unit}",
        new_entry
    )
    
    print(f"Corrige: {name} ({unit_weight}g) - {cal_100g} -> {cal_unit} kcal")
    
    return new_entry

# Appliquer les corrections
new_content = re.sub(pattern, replace_food, content)

# Sauvegarder
with open(r'c:\Users\Clement\.gemini\antigravity\playground\icy-interstellar\fitness-tracker\tracker\views.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("\nCorrections appliquees avec succes!")
print("Tous les aliments ont maintenant des macros pour leur poids unitaire.")
