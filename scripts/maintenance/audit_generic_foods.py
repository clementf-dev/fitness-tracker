"""
Script d'audit pour comparer GENERIC_FOODS avec les données USDA FoodData Central.

Ce script:
1. Extrait les aliments de views.py
2. Les recherche dans USDA FoodData Central
3. Compare les macros (calories, protéines, glucides, lipides, fibres)
4. Génère un rapport des écarts significatifs

Usage:
    python audit_generic_foods.py

Prérequis:
    - Clé API USDA (gratuite): https://fdc.nal.usda.gov/api-key-signup.html
    - pip install requests
"""

import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

import requests
import json
from typing import Dict, List, Optional

# Configuration
USDA_API_KEY = "dg9GOY3Af0n1XNzPL4AnT5l48DXy5oH0NjJghD7c"  # Clé API USDA
USDA_API_URL = "https://api.nal.usda.gov/fdc/v1"

# Seuils de tolérance pour les écarts
THRESHOLDS = {
    'calories': 0.05,  # 5%
    'protein': 0.10,   # 10%
    'carbs': 0.10,     # 10%
    'fat': 0.10,       # 10%
    'fiber': 0.15,     # 15% (plus variable)
}

# Notre base actuelle (extrait de views.py - LISTE COMPLETE)
GENERIC_FOODS = [
    # Oeufs
    {'name': 'Oeuf entier (cru)', 'calories': 155, 'protein': 13, 'carbs': 1.1, 'fat': 11, 'fiber': 0, 'unit_weight': 60, 'keywords': ['oeuf', 'œuf', 'egg']},
    {'name': 'Blanc d\'oeuf', 'calories': 52, 'protein': 11, 'carbs': 0.7, 'fat': 0.2, 'fiber': 0, 'unit_weight': 33, 'keywords': ['blanc', 'oeuf', 'œuf', 'egg white']},
    {'name': 'Jaune d\'oeuf', 'calories': 322, 'protein': 16, 'carbs': 3.6, 'fat': 27, 'fiber': 0, 'unit_weight': 17, 'keywords': ['jaune', 'oeuf', 'œuf', 'egg yolk']},
    
    # Fruits  
    {'name': 'Banane', 'calories': 89, 'protein': 1.1, 'carbs': 23, 'fat': 0.3, 'fiber': 2.6, 'unit_weight': 120, 'keywords': ['banane', 'banana']},
    {'name': 'Pomme', 'calories': 52, 'protein': 0.3, 'carbs': 14, 'fat': 0.2, 'fiber': 2.4, 'unit_weight': 180, 'keywords': ['pomme', 'apple']},
    {'name': 'Orange', 'calories': 47, 'protein': 0.9, 'carbs': 12, 'fat': 0.1, 'fiber': 2.4, 'unit_weight': 180, 'keywords': ['orange']},
    {'name': 'Poire', 'calories': 57, 'protein': 0.4, 'carbs': 15, 'fat': 0.1, 'fiber': 3.1, 'unit_weight': 180, 'keywords': ['poire', 'pear']},
    {'name': 'Kiwi', 'calories': 61, 'protein': 1.1, 'carbs': 15, 'fat': 0.5, 'fiber': 3, 'unit_weight': 75, 'keywords': ['kiwi']},
    {'name': 'Mangue', 'calories': 60, 'protein': 0.8, 'carbs': 15, 'fat': 0.4, 'fiber': 1.6, 'unit_weight': 300, 'keywords': ['mangue', 'mango']},
    {'name': 'Fraise', 'calories': 32, 'protein': 0.7, 'carbs': 8, 'fat': 0.3, 'fiber': 2, 'unit_weight': 15, 'keywords': ['fraise', 'strawberry']},
    {'name': 'Myrtille', 'calories': 57, 'protein': 0.7, 'carbs': 14, 'fat': 0.3, 'fiber': 2.4, 'unit_weight': 150, 'keywords': ['myrtille', 'blueberry']},
    {'name': 'Framboise', 'calories': 52, 'protein': 1.2, 'carbs': 12, 'fat': 0.7, 'fiber': 6.5, 'unit_weight': 125, 'keywords': ['framboise', 'raspberry']},
    {'name': 'Raisin', 'calories': 69, 'protein': 0.7, 'carbs': 18, 'fat': 0.2, 'fiber': 0.9, 'unit_weight': 5, 'keywords': ['raisin', 'grape']},
    {'name': 'Ananas', 'calories': 50, 'protein': 0.5, 'carbs': 13, 'fat': 0.1, 'fiber': 1.4, 'unit_weight': 900, 'keywords': ['ananas', 'pineapple']},
    {'name': 'Pastèque', 'calories': 30, 'protein': 0.6, 'carbs': 8, 'fat': 0.2, 'fiber': 0.4, 'unit_weight': 300, 'keywords': ['pasteque', 'watermelon', 'pastèque']},
    {'name': 'Melon', 'calories': 34, 'protein': 0.8, 'carbs': 8, 'fat': 0.2, 'fiber': 0.9, 'unit_weight': 400, 'keywords': ['melon', 'cantaloup']},
    {'name': 'Citron', 'calories': 29, 'protein': 1.1, 'carbs': 9, 'fat': 0.3, 'fiber': 2.8, 'unit_weight': 60, 'keywords': ['citron', 'lemon']},
    {'name': 'Pamplemousse', 'calories': 42, 'protein': 0.8, 'carbs': 11, 'fat': 0.1, 'fiber': 1.6, 'unit_weight': 300, 'keywords': ['pamplemousse', 'grapefruit']},
    {'name': 'Abricot', 'calories': 48, 'protein': 1.4, 'carbs': 11, 'fat': 0.4, 'fiber': 2, 'unit_weight': 35, 'keywords': ['abricot', 'apricot']},
    {'name': 'Pêche', 'calories': 39, 'protein': 0.9, 'carbs': 10, 'fat': 0.3, 'fiber': 1.5, 'unit_weight': 150, 'keywords': ['peche', 'pêche', 'peach']},
    {'name': 'Nectarine', 'calories': 44, 'protein': 1.1, 'carbs': 11, 'fat': 0.3, 'fiber': 1.7, 'unit_weight': 140, 'keywords': ['nectarine']},
    {'name': 'Prune', 'calories': 46, 'protein': 0.7, 'carbs': 11, 'fat': 0.3, 'fiber': 1.4, 'unit_weight': 50, 'keywords': ['prune', 'plum']},
    {'name': 'Cerise', 'calories': 63, 'protein': 1.1, 'carbs': 16, 'fat': 0.2, 'fiber': 2.1, 'unit_weight': 8, 'keywords': ['cerise', 'cherry']},
    
    # Légumes
    {'name': 'Tomate', 'calories': 18, 'protein': 0.9, 'carbs': 3.9, 'fat': 0.2, 'fiber': 1.2, 'unit_weight': 150, 'keywords': ['tomate', 'tomato']},
    {'name': 'Oignon', 'calories': 40, 'protein': 1.1, 'carbs': 9, 'fat': 0.1, 'fiber': 1.7, 'unit_weight': 150, 'keywords': ['oignon', 'onion']},
    {'name': 'Poivron rouge', 'calories': 31, 'protein': 1, 'carbs': 6, 'fat': 0.3, 'fiber': 2.1, 'unit_weight': 150, 'keywords': ['poivron', 'pepper', 'bell pepper']},
    {'name': 'Poivron vert', 'calories': 20, 'protein': 0.9, 'carbs': 4.6, 'fat': 0.2, 'fiber': 1.7, 'unit_weight': 150, 'keywords': ['poivron', 'pepper', 'bell pepper']},
    {'name': 'Carotte', 'calories': 41, 'protein': 0.9, 'carbs': 10, 'fat': 0.2, 'fiber': 2.8, 'unit_weight': 80, 'keywords': ['carotte', 'carrot']},
    {'name': 'Courgette', 'calories': 17, 'protein': 1.2, 'carbs': 3.1, 'fat': 0.3, 'fiber': 1, 'unit_weight': 200, 'keywords': ['courgette', 'zucchini']},
    {'name': 'Concombre', 'calories': 15, 'protein': 0.7, 'carbs': 3.6, 'fat': 0.1, 'fiber': 0.5, 'unit_weight': 300, 'keywords': ['concombre', 'cucumber']},
    {'name': 'Avocat', 'calories': 160, 'protein': 2, 'carbs': 9, 'fat': 15, 'fiber': 6.7, 'unit_weight': 200, 'keywords': ['avocat', 'avocado']},
    {'name': 'Ail (gousse)', 'calories': 149, 'protein': 6.4, 'carbs': 33, 'fat': 0.5, 'fiber': 2.1, 'unit_weight': 5, 'keywords': ['ail', 'garlic', 'gousse']},
    {'name': 'Pomme de terre', 'calories': 77, 'protein': 2, 'carbs': 17, 'fat': 0.1, 'fiber': 2.2, 'unit_weight': 175, 'keywords': ['pomme de terre', 'potato', 'patate']},
    {'name': 'Champignon de Paris', 'calories': 22, 'protein': 3.1, 'carbs': 3.3, 'fat': 0.3, 'fiber': 1, 'unit_weight': 20, 'keywords': ['champignon', 'mushroom']},
   {'name': 'Poireau', 'calories': 61, 'protein': 1.5, 'carbs': 14, 'fat': 0.3, 'fiber': 1.8, 'unit_weight': 200, 'keywords': ['poireau', 'leek']},
    {'name': 'Aubergine', 'calories': 25, 'protein': 1, 'carbs': 6, 'fat': 0.2, 'fiber': 3, 'unit_weight': 300, 'keywords': ['aubergine', 'eggplant']},
    {'name': 'Brocoli', 'calories': 34, 'protein': 2.8, 'carbs': 7, 'fat': 0.4, 'fiber': 2.6, 'unit_weight': 150, 'keywords': ['brocoli', 'broccoli']},
    {'name': 'Chou-fleur', 'calories': 25, 'protein': 1.9, 'carbs': 5, 'fat': 0.3, 'fiber': 2, 'unit_weight': 600, 'keywords': ['choufleur', 'cauliflower']},
    {'name': 'Épinard (frais)', 'calories': 23, 'protein': 2.9, 'carbs': 3.6, 'fat': 0.4, 'fiber': 2.2, 'unit_weight': 30, 'keywords': ['epinard', 'spinach']},
    {'name': 'Salade (laitue)', 'calories': 15, 'protein': 1.4, 'carbs': 2.9, 'fat': 0.2, 'fiber': 1.3, 'unit_weight': 300, 'keywords': ['salade', 'laitue', 'lettuce']},
    {'name': 'Haricot vert', 'calories': 31, 'protein': 1.8, 'carbs': 7, 'fat': 0.1, 'fiber': 2.7, 'unit_weight': 10, 'keywords': ['haricot', 'green bean']},
    {'name': 'Petit pois', 'calories': 81, 'protein': 5.4, 'carbs': 14, 'fat': 0.4, 'fiber': 5.7, 'unit_weight': 100, 'keywords': ['petit pois', 'peas', 'pois']},
    {'name': 'Maïs', 'calories': 86, 'protein': 3.3, 'carbs': 19, 'fat': 1.4, 'fiber': 2, 'unit_weight': 250, 'keywords': ['mais', 'corn']},
    {'name': 'Céleri', 'calories': 16, 'protein': 0.7, 'carbs': 3, 'fat': 0.2, 'fiber': 1.6, 'unit_weight': 40, 'keywords': ['celeri', 'celery']},
    {'name': 'Betterave', 'calories': 43, 'protein': 1.6, 'carbs': 10, 'fat': 0.2, 'fiber': 2.8, 'unit_weight': 150, 'keywords': ['betterave', 'beet']},
    {'name': 'Radis', 'calories': 16, 'protein': 0.7, 'carbs': 3.4, 'fat': 0.1, 'fiber': 1.6, 'unit_weight': 10, 'keywords': ['radis', 'radish']},
    {'name': 'Fenouil', 'calories': 31, 'protein': 1.2, 'carbs': 7, 'fat': 0.2, 'fiber': 3.1, 'unit_weight': 250, 'keywords': ['fenouil', 'fennel']},
    {'name': 'Asperge', 'calories': 20, 'protein': 2.2, 'carbs': 3.9, 'fat': 0.1, 'fiber': 2.1, 'unit_weight': 20, 'keywords': ['asperge', 'asparagus']},
    {'name': 'Artichaut', 'calories': 47, 'protein': 3.3, 'carbs': 11, 'fat': 0.2, 'fiber': 5.4, 'unit_weight': 300, 'keywords': ['artichaut', 'artichoke']},
    
    # Viandes
    {'name': 'Poulet (blanc, cru)', 'calories': 120, 'protein': 22, 'carbs': 0, 'fat': 3, 'fiber': 0, 'unit_weight': 150, 'keywords': ['poulet', 'chicken']},
    {'name': 'Boeuf haché (5% MG)', 'calories': 137, 'protein': 21, 'carbs': 0, 'fat': 5, 'fiber': 0, 'unit_weight': 125, 'keywords': ['boeuf', 'beef', 'steak']},
    {'name': 'Dinde (escalope, crue)', 'calories': 104, 'protein': 24, 'carbs': 0, 'fat': 1, 'fiber': 0, 'unit_weight': 150, 'keywords': ['dinde', 'turkey']},
    
    # Poissons
    {'name': 'Saumon (filet, cru)', 'calories': 208, 'protein': 20, 'carbs': 0, 'fat': 13, 'fiber': 0, 'unit_weight': 150, 'keywords': ['saumon', 'salmon']},
    {'name': 'Thon (frais, cru)', 'calories': 144, 'protein': 23, 'carbs': 0, 'fat': 5, 'fiber': 0, 'unit_weight': 150, 'keywords': ['thon', 'tuna']},
    {'name': 'Cabillaud (filet, cru)', 'calories': 82, 'protein': 18, 'carbs': 0, 'fat': 0.7, 'fiber': 0, 'unit_weight': 150, 'keywords': ['cabillaud', 'cod']},
    {'name': 'Crevette (crue)', 'calories': 99, 'protein': 24, 'carbs': 0.2, 'fat': 0.3, 'fiber': 0, 'unit_weight': 15, 'keywords': ['crevette', 'shrimp']},
    
    # Produits laitiers
    {'name': 'Lait entier', 'calories': 61, 'protein': 3.2, 'carbs': 4.7, 'fat': 3.3, 'fiber': 0, 'unit_weight': 250, 'keywords': ['lait', 'milk']},
    {'name': 'Yaourt nature', 'calories': 61, 'protein': 4, 'carbs': 5, 'fat': 3, 'fiber': 0, 'unit_weight': 125, 'keywords': ['yaourt', 'yogurt']},
    
    # Céréales
    {'name': 'Riz blanc (cru)', 'calories': 365, 'protein': 7, 'carbs': 79, 'fat': 0.6, 'fiber': 1.3, 'unit_weight': 80, 'keywords': ['riz', 'rice']},
    {'name': 'Pâtes (crues)', 'calories': 350, 'protein': 12, 'carbs': 72, 'fat': 1.5, 'fiber': 2.5, 'unit_weight': 100, 'keywords': ['pates', 'pasta']},
    {'name': 'Pain (baguette)', 'calories': 274, 'protein': 9, 'carbs': 56, 'fat': 1.3, 'fiber': 2.7, 'unit_weight': 250, 'keywords': ['pain', 'bread']},
    {'name': 'Flocons d\'avoine', 'calories': 367, 'protein': 14, 'carbs': 58, 'fat': 7, 'fiber': 10, 'unit_weight': 40, 'keywords': ['avoine', 'oats']},
    
    # Oléagineux
    {'name': 'Amande', 'calories': 579, 'protein': 21, 'carbs': 22, 'fat': 50, 'fiber': 12.5, 'unit_weight': 1.2, 'keywords': ['amande', 'almond']},
    {'name': 'Noix', 'calories': 654, 'protein': 15, 'carbs': 14, 'fat': 65, 'fiber': 7, 'unit_weight': 5, 'keywords': ['noix', 'walnut']},
    {'name': 'Noisette', 'calories': 628, 'protein': 15, 'carbs': 17, 'fat': 61, 'fiber': 10, 'unit_weight': 2, 'keywords': ['noisette', 'hazelnut']},
    {'name': 'Cacahuète', 'calories': 567, 'protein': 26, 'carbs': 16, 'fat': 49, 'fiber': 9, 'unit_weight': 1.5, 'keywords': ['cacahuete', 'peanut']},
]


def search_usda_food(food_name: str, api_key: str = USDA_API_KEY) -> Optional[Dict]:
    """
    Recherche un aliment dans USDA FoodData Central.
    Priorise les résultats de 'SR Legacy' et 'Foundation Foods'.
    """
    url = f"{USDA_API_URL}/foods/search"
    params = {
        'api_key': api_key,
        'query': food_name,
        'dataType': ['SR Legacy', 'Foundation'],  # Sources fiables analytiques
        'pageSize': 5
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('foods'):
            # Retourner le premier résultat (le plus pertinent)
            return data['foods'][0]
        return None
    except Exception as e:
        print(f"Erreur API USDA pour '{food_name}': {e}")
        return None


def extract_nutrients(usda_food: Dict) -> Dict[str, float]:
    """
    Extrait les nutriments d'un aliment USDA (valeurs pour 100g).
    """
    nutrients = {}
    nutrient_map = {
        'Energy': 'calories',  # kcal
        'Protein': 'protein',  # g
        'Carbohydrate, by difference': 'carbs',  # g
        'Total lipid (fat)': 'fat',  # g
        'Fiber, total dietary': 'fiber',  # g
    }
    
    for nutrient in usda_food.get('foodNutrients', []):
        nutrient_name = nutrient.get('nutrientName', '')
        
        for usda_name, our_name in nutrient_map.items():
            if usda_name in nutrient_name:
                value = nutrient.get('value', 0)
                nutrients[our_name] = round(value, 1)
                break
    
    return nutrients


def calculate_difference(our_value: float, usda_value: float, nutrient: str) -> Dict:
    """
    Calcule la différence absolue et relative entre nos valeurs et USDA.
    """
    if usda_value == 0:
        return {'diff_abs': 0, 'diff_pct': 0, 'significant': False}
    
    diff_abs = our_value - usda_value
    diff_pct = (diff_abs / usda_value) * 100
    threshold = THRESHOLDS.get(nutrient, 0.10)
    significant = abs(diff_pct) > (threshold * 100)
    
    return {
        'diff_abs': round(diff_abs, 2),
        'diff_pct': round(diff_pct, 1),
        'significant': significant
    }


def audit_food(food: Dict, api_key: str = USDA_API_KEY) -> Dict:
    """
    Audite un aliment en le comparant avec USDA.
    """
    # Chercher le meilleur terme anglais dans les keywords
    search_term = None
    english_keywords = [kw for kw in food['keywords'] if kw and kw.isascii() and len(kw) > 2]
    
    # Prioriser les mots anglais reconnaissables
    if english_keywords:
        search_term = english_keywords[0]  # Prendre le premier mot anglais
    else:
        # Fallback au nom français si aucun keyword anglais
        search_term = food['name']
    
    print(f"\n[*] Recherche: {food['name']} (terme USDA: '{search_term}')...")
    
    usda_food = search_usda_food(search_term, api_key)
    if not usda_food:
        return {
            'name': food['name'],
            'status': 'NOT_FOUND',
            'message': f"Aucune correspondance USDA trouvée pour '{search_term}'"
        }
    
    usda_nutrients = extract_nutrients(usda_food)
    
    # Comparer chaque nutriment
    comparison = {
        'name': food['name'],
        'usda_match': usda_food.get('description', 'Unknown'),
        'usda_source': usda_food.get('dataType', 'Unknown'),
        'status': 'OK',
        'nutrients': {}
    }
    
    has_significant_diff = False
    
    for nutrient in ['calories', 'protein', 'carbs', 'fat', 'fiber']:
        our_value = food.get(nutrient, 0)
        usda_value = usda_nutrients.get(nutrient, 0)
        
        diff = calculate_difference(our_value, usda_value, nutrient)
        
        comparison['nutrients'][nutrient] = {
            'ours': our_value,
            'usda': usda_value,
            **diff
        }
        
        if diff['significant']:
            has_significant_diff = True
    
    if has_significant_diff:
        comparison['status'] = 'NEEDS_REVIEW'
    
    return comparison


def generate_report(audit_results: List[Dict]) -> str:
    """
    Génère un rapport Markdown des résultats d'audit.
    """
    report = "# Rapport d'Audit : GENERIC_FOODS vs USDA FoodData Central\n\n"
    report += f"**Date**: {json.dumps(audit_results[0], indent=2) if audit_results else 'N/A'}\n\n"
    
    needs_review = [r for r in audit_results if r.get('status') == 'NEEDS_REVIEW']
    ok = [r for r in audit_results if r.get('status') == 'OK']
    not_found = [r for r in audit_results if r.get('status') == 'NOT_FOUND']
    
    report += f"## Résumé\n\n"
    report += f"- ✅ **OK**: {len(ok)} aliments\n"
    report += f"- ⚠️ **À réviser**: {len(needs_review)} aliments\n"
    report += f"- ❌ **Non trouvés**: {len(not_found)} aliments\n\n"
    
    # Aliments nécessitant révision
    if needs_review:
        report += "## ⚠️ Aliments à Réviser\n\n"
        for item in needs_review:
            report += f"### {item['name']}\n"
            report += f"**Correspondance USDA**: {item['usda_match']} ({item['usda_source']})\n\n"
            report += "| Nutriment | Notre Valeur | USDA | Écart | % |\n"
            report += "|-----------|--------------|------|-------|---|\n"
            
            for nutrient, data in item['nutrients'].items():
                flag = "⚠️" if data['significant'] else "✓"
                report += f"| {flag} {nutrient.capitalize()} | {data['ours']} | {data['usda']} | {data['diff_abs']:+.1f} | {data['diff_pct']:+.1f}% |\n"
            
            report += "\n"
    
    # Aliments non trouvés
    if not_found:
        report += "## ❌ Aliments Non Trouvés dans USDA\n\n"
        for item in not_found:
            report += f"- **{item['name']}**: {item['message']}\n"
        report += "\n"
    
    return report


def main():
    """Point d'entrée principal."""
    print("=" * 60)
    print("AUDIT GENERIC_FOODS vs USDA FoodData Central")
    print("=" * 60)
    
    audit_results = []
    
    for food in GENERIC_FOODS:
        result = audit_food(food)
        audit_results.append(result)
    
    # Générer rapport
    report = generate_report(audit_results)
    
    # Sauvegarder
    output_file = "audit_report.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ Rapport généré: {output_file}")
    
    # Afficher résumé
    needs_review = [r for r in audit_results if r.get('status') == 'NEEDS_REVIEW']
    if needs_review:
        print(f"\n⚠️ {len(needs_review)} aliment(s) nécessitent une révision!")


if __name__ == "__main__":
    main()
