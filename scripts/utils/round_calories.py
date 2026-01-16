"""
Arrondir toutes les calories dans GENERIC_FOODS (28.5 -> 29, etc.)
"""

import re

print("Lecture de views.py...")
with open(r'c:\Users\Clement\.gemini\antigravity\playground\icy-interstellar\fitness-tracker\tracker\views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern pour trouver les calories
pattern = r"'calories': ([\d.]+)"

def round_calories(match):
    cal = float(match.group(1))
    rounded = round(cal)  # Arrondi standard Python (0.5 -> arrondi au pair le plus proche)
    # Pour forcer l'arrondi vers le haut à 0.5, on utilise:
    from decimal import Decimal, ROUND_HALF_UP
    rounded = int(Decimal(str(cal)).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
    
    print(f"Calories: {cal} -> {rounded}")
    return f"'calories': {rounded}"

# Appliquer l'arrondi
new_content = re.sub(pattern, round_calories, content)

# Sauvegarder
with open(r'c:\Users\Clement\.gemini\antigravity\playground\icy-interstellar\fitness-tracker\tracker\views.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("\nCalories arrondies avec succes!")
