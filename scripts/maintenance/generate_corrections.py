"""
Script pour générer automatiquement les corrections CIQUAL à appliquer dans views.py.
Lit le rapport d'audit et génère les lignes de code corrigées.
"""

import json
import re

# Lire le rapport d'audit
with open('audit_ciqual_report.md', 'r', encoding='utf-8') as f:
    report = f.read()

# Extraire les aliments avec leur correspondance CIQUAL
corrections = []

# Parser le rapport pour extraire les données
sections = report.split('### ')

for section in sections[1:]:  # Skip le premier (header)
    lines = section.split('\n')
    food_name = lines[0].strip()
    
    # Trouver la correspondance CIQUAL
    ciqual_match = None
    for line in lines:
        if line.startswith('**CIQUAL**:'):
            ciqual_match = line.replace('**CIQUAL**:', '').strip()
            break
    
    # Extraire les valeurs CIQUAL du tableau
    nutrients = {}
    in_table = False
    for line in lines:
        if '| Nutriment |' in line:
            in_table = True
            continue
        if in_table and '|' in line:
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 4 and parts[1] and not parts[1].startswith('-'):
                nutrient_name = parts[1].replace('⚠️', '').replace('✓', '').strip()
                try:
                    ciqual_value = float(parts[3])
                    nutrients[nutrient_name.lower()] = ciqual_value
                except:
                    pass
    
    if nutrients and ciqual_match:
        corrections.append({
            'name': food_name,
            'ciqual_match': ciqual_match,
            'nutrients': nutrients
        })

print(f"Trouvé {len(corrections)} aliments avec données CIQUAL\n")

# Filtrer les aliments avec de bonnes correspondances
# Exclure ceux qui ont matché avec de mauvaises catégories
good_matches = []
bad_categories = ['fruits, légumes, légumineuses et oléagineux', 'entrées et plats composés', 'produits céréaliers']

for corr in corrections:
    # Vérifier si c'est une vraie correspondance ou juste une catégorie
    if corr['ciqual_match'] in bad_categories:
        # Vérifier si les valeurs sont cohérentes (pas toutes à 0)
        if corr['nutrients'].get('protein', 0) == 0 and corr['nutrients'].get('carbs', 0) == 0:
            print(f"❌ SKIP {corr['name']}: mauvais matching (catégorie générique)")
            continue
    
    # Vérifier si les calories sont cohérentes
    if 'calories' in corr['nutrients'] and corr['nutrients']['calories'] == 0:
        print(f"❌ SKIP {corr['name']}: calories = 0 (mauvais matching)")
        continue
    
    good_matches.append(corr)
    print(f"✓ {corr['name']}: {corr['ciqual_match']}")

print(f"\n{len(good_matches)} aliments avec de bonnes correspondances CIQUAL")

# Sauvegarder en JSON pour utilisation ultérieure
with open('ciqual_corrections.json', 'w', encoding='utf-8') as f:
    json.dump(good_matches, f, indent=2, ensure_ascii=False)

print("\n✅ Corrections sauvegardées dans ciqual_corrections.json")
