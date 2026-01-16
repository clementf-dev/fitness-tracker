"""
Script pour rechercher manuellement les 27 aliments restants dans CIQUAL
et générer les corrections avec les bons matchings.
"""

import pandas as pd
import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Charger CIQUAL
df = pd.read_excel('ciqual_data.xls', sheet_name=0)

# Liste des aliments non corrigés (23 mauvais matchings + 4 OK)
remaining_foods = {
    # Mauvais matchings à corriger
    'Banane': 'banana',
    'Blanc d\'oeuf': 'egg white',
    'Jaune d\'oeuf': 'egg yolk',
    'Pamplemousse': 'grapefruit',
    'Pêche': 'peach',
    'Nectarine': 'nectarine',
    'Oignon': 'onion',
    'Poivron rouge': 'red pepper',
    'Poivron vert': 'green pepper',
    'Aubergine': 'eggplant',
    'Brocoli': 'broccoli',
    'Épinard (frais)': 'spinach',
    'Salade (laitue)': 'lettuce',
    'Haricot vert': 'green bean',
    'Petit pois': 'peas',
    'Maïs': 'corn',
    'Betterave': 'beet',
    'Asperge': 'asparagus',
    'Artichaut': 'artichoke',
    'Thon (frais, cru)': 'tuna',
    'Lait entier': 'whole milk',
    'Lait demi-écrémé': 'semi-skimmed milk',
    'Amande': 'almond',
    'Noix': 'walnut',
    'Noisette': 'hazelnut',
    'Cacahuète': 'peanut',
}

def safe_float(value):
    """Convertit une valeur CIQUAL en float."""
    if pd.isna(value) or value == '-' or value == '':
        return 0.0
    if isinstance(value, str):
        value = value.replace(',', '.')
    try:
        return float(value)
    except:
        return 0.0

def search_in_ciqual(french_name, english_hint):
    """Recherche intelligente dans CIQUAL."""
    name_col = 'alim_nom_fr'
    
    # Essayer différentes stratégies
    searches = [
        french_name.lower().split()[0],  # Premier mot
        french_name.lower().replace('(', '').replace(')', '').split()[0],
        french_name.lower()
    ]
    
    for search_term in searches:
        if len(search_term) < 3:
            continue
            
        # Recherche exacte au début
        mask = df[name_col].str.lower().str.startswith(search_term, na=False)
        candidates = df[mask]
        
        if len(candidates) > 0:
            # Prioriser "cru" ou "frais"
            for priority in ['cru', 'frais', 'fraîche']:
                priority_candidates = candidates[candidates[name_col].str.contains(priority, case=False, na=False)]
                if len(priority_candidates) > 0:
                    return priority_candidates.iloc[0]
            return candidates.iloc[0]
    
    return None

print("Recherche manuelle des aliments restants dans CIQUAL...\n")

corrections = []

for french_name, english_hint in remaining_foods.items():
    result = search_in_ciqual(french_name, english_hint)
    
    if result is not None:
        ciqual_name = result['alim_nom_fr']
        
        # Extraire nutriments
        nutrients = {
            'calories': safe_float(result.get('Energie, Règlement UE N° 1169/2011 (kcal/100 g)', 0)),
            'protein': safe_float(result.get('Protéines, N x facteur de Jones (g/100 g)', 0)),
            'carbs': safe_float(result.get('Glucides (g/100 g)', 0)),
            'fat': safe_float(result.get('Lipides (g/100 g)', 0)),
            'fiber': safe_float(result.get('Fibres alimentaires (g/100 g)', 0)),
        }
        
        # Vérifier si c'est une bonne correspondance
        if nutrients['calories'] > 0 or nutrients['protein'] > 0:
            corrections.append({
                'name': french_name,
                'ciqual_name': ciqual_name,
                'nutrients': nutrients
            })
            print(f"OK: {french_name}")
            print(f"   -> {ciqual_name}")
            print(f"   -> Cal:{nutrients['calories']} P:{nutrients['protein']} G:{nutrients['carbs']} L:{nutrients['fat']} F:{nutrients['fiber']}")
        else:
            print(f"SKIP: {french_name} - valeurs nulles")
    else:
        print(f"NOT FOUND: {french_name}")
    print()

print(f"\n{len(corrections)} corrections trouvées")

# Sauvegarder
import json
with open('remaining_corrections.json', 'w', encoding='utf-8') as f:
    json.dump(corrections, f, indent=2, ensure_ascii=False)

print("Sauvegardé dans remaining_corrections.json")
