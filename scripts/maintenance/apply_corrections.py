"""
Script pour appliquer automatiquement les corrections CIQUAL dans views.py.
Lit le rapport d'audit et génère les corrections validées.
"""

import re
import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Lire le rapport d'audit
with open('audit_ciqual_report.md', 'r', encoding='utf-8') as f:
    report = f.read()

# Lire views.py
with open(r'c:\Users\Clement\.gemini\antigravity\playground\icy-interstellar\fitness-tracker\tracker\views.py', 'r', encoding='utf-8') as f:
    views_content = f.read()

# Parser le rapport pour extraire les corrections
corrections = {}
current_food = None
current_ciqual = None
current_nutrients = {}

for line in report.split('\n'):
    if line.startswith('### ') and not line.startswith('### #'):
        current_food = line.replace('### ', '').strip()
        current_nutrients = {}
    elif line.startswith('**CIQUAL**:'):
        current_ciqual = line.replace('**CIQUAL**:', '').strip()
    elif '|' in line and current_food:
        parts = [p.strip() for p in line.split('|')]
        if len(parts) >= 4 and parts[1] and not parts[1].startswith('-') and 'Nutriment' not in parts[1]:
            nutrient_name = parts[1].replace('⚠️', '').replace('✓', '').strip()
            try:
                ciqual_value = float(parts[3])
                current_nutrients[nutrient_name.lower()] = ciqual_value
            except:
                pass
    elif line.strip() == '' and current_food and current_nutrients:
        corrections[current_food] = {
            'ciqual_match': current_ciqual,
            'nutrients': current_nutrients
        }
        current_food = None
        current_ciqual = None

print(f"Trouvé {len(corrections)} aliments dans le rapport\n")

# Filtrer les bonnes correspondances
good_corrections = {}
skip_reasons = {}

for food_name, data in corrections.items():
    ciqual_match = data['ciqual_match']
    nutrients = data['nutrients']
    
    # Critères de validation
    skip = False
    reason = ""
    
    # 1. Vérifier si calories = 0 (mauvais matching)
    if nutrients.get('calories', 0) == 0:
        skip = True
        reason = "calories = 0"
    
    # 2. Vérifier si tous les macros = 0 (catégorie générique)
    elif nutrients.get('protein', 0) == 0 and nutrients.get('carbs', 0) == 0 and nutrients.get('fat', 0) == 0:
        skip = True
        reason = "tous macros = 0"
    
    # 3. Aliments déjà corrigés
    elif food_name in ['Tomate', 'Carotte', 'Avocat', 'Yaourt nature']:
        skip = True
        reason = "déjà corrigé"
    
    if skip:
        skip_reasons[food_name] = reason
    else:
        good_corrections[food_name] = data
        print(f"OK: {food_name} -> {ciqual_match}")

print(f"\n{len(good_corrections)} corrections validées")
print(f"{len(skip_reasons)} aliments ignorés\n")

# Générer les lignes de code corrigées
print("Génération des corrections...\n")

corrections_applied = []

for food_name, data in good_corrections.items():
    nutrients = data['nutrients']
    ciqual_match = data['ciqual_match']
    
    # Chercher la ligne dans views.py
    pattern = rf"\{{'name': '{re.escape(food_name)}'.*?\}}"
    match = re.search(pattern, views_content, re.DOTALL)
    
    if match:
        old_line = match.group(0)
        
        # Extraire les valeurs actuelles
        current_values = {}
        for key in ['calories', 'protein', 'carbs', 'fat', 'fiber']:
            val_match = re.search(rf"'{key}': ([\d.]+)", old_line)
            if val_match:
                current_values[key] = float(val_match.group(1))
        
        # Créer la nouvelle ligne avec valeurs CIQUAL
        new_values = current_values.copy()
        for key in ['calories', 'protein', 'carbs', 'fat', 'fiber']:
            if key in nutrients:
                new_values[key] = nutrients[key]
        
        # Construire la nouvelle ligne
        new_line = old_line
        for key, value in new_values.items():
            old_val_pattern = rf"'{key}': [\d.]+"
            new_val_str = f"'{key}': {value}"
            new_line = re.sub(old_val_pattern, new_val_str, new_line)
        
        # Ajouter commentaire source CIQUAL
        if "# Source:" not in old_line:
            # Insérer commentaire avant la ligne
            indent = "        "
            comment = f"{indent}# Source: CIQUAL 2020 - {ciqual_match}\n{indent}"
            new_line = comment + new_line.lstrip()
        
        corrections_applied.append({
            'food': food_name,
            'old': old_line,
            'new': new_line
        })
        
        print(f"[{len(corrections_applied)}] {food_name}")

print(f"\n{len(corrections_applied)} corrections générées")

# Sauvegarder les corrections
import json
with open('corrections_to_apply.json', 'w', encoding='utf-8') as f:
    json.dump({
        'total': len(corrections_applied),
        'corrections': corrections_applied,
        'skipped': skip_reasons
    }, f, indent=2, ensure_ascii=False)

print("\nCorrections sauvegardées dans corrections_to_apply.json")
