"""
Script d'audit utilisant la base CIQUAL (ANSES - France).

Parse le fichier Excel téléchargé et compare avec GENERIC_FOODS.
"""

import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

import pandas as pd
import re
from typing import Dict, List, Optional

# Configuration
CIQUAL_FILE = "ciqual_data.xls"

# Seuils de tolérance
THRESHOLDS = {
    'calories': 0.05,  # 5%
    'protein': 0.10,   # 10%
    'carbs': 0.10,     # 10%
    'fat': 0.10,       # 10%
    'fiber': 0.15,     # 15%
}


def load_ciqual_data(filename: str) -> pd.DataFrame:
    """
    Charge le fichier Excel CIQUAL.
    """
    print(f"[*] Chargement de {filename}...")
    try:
        df = pd.read_excel(filename, sheet_name=0)
        print(f"[OK] {len(df)} entrées chargées")
        return df
    except Exception as e:
        print(f"[ERREUR] Impossible de charger {filename}: {e}")
        return None


def load_generic_foods():
    """Charge tous les aliments de GENERIC_FOODS depuis views.py."""
    # Version complète - copié de views.py lignes 552-630
    return [
        # Oeufs
        {'name': 'Oeuf entier (cru)', 'calories': 155, 'protein': 13, 'carbs': 1.1, 'fat': 11, 'fiber': 0},
        {'name': 'Blanc d\'oeuf', 'calories': 52, 'protein': 11, 'carbs': 0.7, 'fat': 0.2, 'fiber': 0},
        {'name': 'Jaune d\'oeuf', 'calories': 322, 'protein': 16, 'carbs': 3.6, 'fat': 27, 'fiber': 0},
        
        # Fruits
        {'name': 'Banane', 'calories': 89, 'protein': 1.1, 'carbs': 23, 'fat': 0.3, 'fiber': 2.6},
        {'name': 'Pomme', 'calories': 52, 'protein': 0.3, 'carbs': 14, 'fat': 0.2, 'fiber': 2.4},
        {'name': 'Orange', 'calories': 47, 'protein': 0.9, 'carbs': 12, 'fat': 0.1, 'fiber': 2.4},
        {'name': 'Avocat', 'calories': 160, 'protein': 2, 'carbs': 9, 'fat': 15, 'fiber': 6.7},
        
        # Légumes
        {'name': 'Tomate', 'calories': 18, 'protein': 0.9, 'carbs': 3.9, 'fat': 0.2, 'fiber': 1.2},
        {'name': 'Carotte', 'calories': 41, 'protein': 0.9, 'carbs': 10, 'fat': 0.2, 'fiber': 2.8},
        {'name': 'Brocoli', 'calories': 34, 'protein': 2.8, 'carbs': 7, 'fat': 0.4, 'fiber': 2.6},
        
        # Viandes/Poissons
        {'name': 'Poulet (blanc, cru)', 'calories': 120, 'protein': 22, 'carbs': 0, 'fat': 3, 'fiber': 0},
        {'name': 'Saumon (filet, cru)', 'calories': 208, 'protein': 20, 'carbs': 0, 'fat': 13, 'fiber': 0},
        
        # Céréales
        {'name': 'Riz blanc (cru)', 'calories': 365, 'protein': 7, 'carbs': 79, 'fat': 0.6, 'fiber': 1.3},
        {'name': 'Pâtes (crues)', 'calories': 350, 'protein': 12, 'carbs': 72, 'fat': 1.5, 'fiber': 2.5},
        {'name': 'Flocons d\'avoine', 'calories': 367, 'protein': 14, 'carbs': 58, 'fat': 7, 'fiber': 10},
        
        # Produits laitiers
        {'name': 'Lait entier', 'calories': 61, 'protein': 3.2, 'carbs': 4.7, 'fat': 3.3, 'fiber': 0},
        {'name': 'Yaourt nature', 'calories': 61, 'protein': 4, 'carbs': 5, 'fat': 3, 'fiber': 0},
        
        # Oléagineux
        {'name': 'Amande', 'calories': 579, 'protein': 21, 'carbs': 22, 'fat': 50, 'fiber': 12.5},
        {'name': 'Noix', 'calories': 654, 'protein': 15, 'carbs': 14, 'fat': 65, 'fiber': 7},
    ]


def search_ciqual_food(food_name: str, df: pd.DataFrame) -> Optional[pd.Series]:
    """
    Recherche intelligente dans CIQUAL avec fuzzy matching.
    """
    name_column = 'alim_nom_fr'
    
    # Nettoyer le nom de recherche
    search_clean = food_name.lower()
    # Retirer les précisions entre parenthèses
    search_clean = re.sub(r'\([^)]*\)', '', search_clean).strip()
    
    # Extraire le mot-clé principal (premier mot significatif)
    keywords = [w for w in search_clean.split() if len(w) > 2]
    main_keyword = keywords[0] if keywords else search_clean
    
    print(f"   -> Recherche CIQUAL: mot-clé '{main_keyword}'")
    
    # 1. Recherche exacte du mot-clé au début
    mask_exact = df[name_column].str.lower().str.startswith(main_keyword, na=False)
    candidates = df[mask_exact]
    
    if len(candidates) > 0:
        # Prioriser les entrées "crues" ou "fraîches" pour produits bruts
        for priority_term in ['cru', 'frais', 'pulpe']:
            priority_candidates = candidates[candidates[name_column].str.contains(priority_term, case=False, na=False)]
            if len(priority_candidates) > 0:
                return priority_candidates.iloc[0]
        return candidates.iloc[0]
    
    # 2. Recherche partielle
    mask_partial = df[name_column].str.lower().str.contains(main_keyword, na=False)
    candidates = df[mask_partial]
    
    if len(candidates) > 0:
        # Même priorisation
        for priority_term in ['cru', 'frais', 'pulpe']:
            priority_candidates = candidates[candidates[name_column].str.contains(priority_term, case=False, na=False)]
            if len(priority_candidates) > 0:
                return priority_candidates.iloc[0]
        return candidates.iloc[0]
    
    return None


def extract_ciqual_nutrients(row: pd.Series) -> Dict[str, float]:
    """
    Extrait les nutriments d'une ligne CIQUAL (valeurs pour 100g).
    """
    nutrients = {}
    
    def safe_float(value):
        """Convertit une valeur CIQUAL en float (gère virgules et tirets)."""
        if pd.isna(value) or value == '-' or value == '':
            return 0.0
        # Remplacer virgule par point (format EU → US)
        if isinstance(value, str):
            value = value.replace(',', '.')
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    # Mapping exact des colonnes CIQUAL
    if 'Energie, Règlement UE N° 1169/2011 (kcal/100 g)' in row.index:
        nutrients['calories'] = round(safe_float(row['Energie, Règlement UE N° 1169/2011 (kcal/100 g)']), 1)
    
    if 'Protéines, N x facteur de Jones (g/100 g)' in row.index:
        nutrients['protein'] = round(safe_float(row['Protéines, N x facteur de Jones (g/100 g)']), 1)
    
    if 'Glucides (g/100 g)' in row.index:
        nutrients['carbs'] = round(safe_float(row['Glucides (g/100 g)']), 1)
    
    if 'Lipides (g/100 g)' in row.index:
        nutrients['fat'] = round(safe_float(row['Lipides (g/100 g)']), 1)
    
    if 'Fibres alimentaires (g/100 g)' in row.index:
        nutrients['fiber'] = round(safe_float(row['Fibres alimentaires (g/100 g)']), 1)
    
    return nutrients


def calculate_difference(our_value: float, ciqual_value: float, nutrient: str) -> Dict:
    """Calcule la différence entre nos valeurs et CIQUAL."""
    if ciqual_value == 0:
        return {'diff_abs': 0, 'diff_pct': 0, 'significant': False}
    
    diff_abs = our_value - ciqual_value
    diff_pct = (diff_abs / ciqual_value) * 100
    threshold = THRESHOLDS.get(nutrient, 0.10)
    significant = abs(diff_pct) > (threshold * 100)
    
    return {
        'diff_abs': round(diff_abs, 2),
        'diff_pct': round(diff_pct, 1),
        'significant': significant
    }


def audit_with_ciqual(food: Dict, df: pd.DataFrame) -> Dict:
    """Audite un aliment avec CIQUAL."""
    print(f"\n[*] Recherche: {food['name']}...")
    
    ciqual_row = search_ciqual_food(food['name'], df)
    if ciqual_row is None:
        return {
            'name': food['name'],
            'status': 'NOT_FOUND',
            'message': f"Aucune correspondance CIQUAL pour '{food['name']}'"
        }
    
    # Extraire nom de la colonne nom
    name_col = [col for col in df.columns if 'nom' in col.lower() and 'fr' in col.lower()][0]
    
    ciqual_nutrients = extract_ciqual_nutrients(ciqual_row)
    
    comparison = {
        'name': food['name'],
        'ciqual_match': ciqual_row[name_col],
        'status': 'OK',
        'nutrients': {}
    }
    
    has_significant_diff = False
    
    for nutrient in ['calories', 'protein', 'carbs', 'fat', 'fiber']:
        our_value = food.get(nutrient, 0)
        ciqual_value = ciqual_nutrients.get(nutrient, 0)
        
        diff = calculate_difference(our_value, ciqual_value, nutrient)
        
        comparison['nutrients'][nutrient] = {
            'ours': our_value,
            'ciqual': ciqual_value,
            **diff
        }
        
        if diff['significant']:
            has_significant_diff = True
    
    if has_significant_diff:
        comparison['status'] = 'NEEDS_REVIEW'
    
    return comparison


def generate_report(results: List[Dict]) -> str:
    """Génère rapport Markdown."""
    report = "# Audit GENERIC_FOODS avec CIQUAL (ANSES)\n\n"
    
    needs_review = [r for r in results if r.get('status') == 'NEEDS_REVIEW']
    ok = [r for r in results if r.get('status') == 'OK']
    not_found = [r for r in results if r.get('status') == 'NOT_FOUND']
    
    report += f"## Résumé\n\n"
    report += f"- ✅ OK: {len(ok)}\n"
    report += f"- ⚠️ À réviser: {len(needs_review)}\n"
    report += f"- ❌ Non trouvés: {len(not_found)}\n\n"
    
    if needs_review:
        report += "## ⚠️ Aliments à Réviser\n\n"
        for item in needs_review:
            report += f"### {item['name']}\n"
            report += f"**CIQUAL**: {item['ciqual_match']}\n\n"
            report += "| Nutriment | Notre Valeur | CIQUAL | Écart | % |\n"
            report += "|-----------|--------------|--------|-------|---|\n"
            
            for nutrient, data in item['nutrients'].items():
                flag = "⚠️" if data['significant'] else "✓"
                report += f"| {flag} {nutrient} | {data['ours']} | {data['ciqual']} | {data['diff_abs']:+.1f} | {data['diff_pct']:+.1f}% |\n"
            
            report += "\n"
    
    if not_found:
        report += "## ❌ Non trouvés\n\n"
        for item in not_found:
            report += f"- **{item['name']}**: {item['message']}\n"
    
    return report


def main():
    """Point d'entrée."""
    print("=" * 60)
    print("AUDIT GENERIC_FOODS avec CIQUAL (ANSES - France)")
    print("=" * 60)
    
    # Charger CIQUAL
    df = load_ciqual_data(CIQUAL_FILE)
    if df is None:
        return
    
    # Charger tous les aliments
    foods = load_generic_foods()
    print(f"\n[INFO] {len(foods)} aliments à auditer\n")
    
    # Auditer
    results = []
    for food in foods:
        result = audit_with_ciqual(food, df)
        results.append(result)
    
    # Générer rapport
    report = generate_report(results)
    
    with open("audit_ciqual_report.md", 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ Rapport généré: audit_ciqual_report.md")
    
    needs_review = len([r for r in results if r.get('status') == 'NEEDS_REVIEW'])
    if needs_review > 0:
        print(f"⚠️ {needs_review} aliment(s) nécessitent une révision")


if __name__ == "__main__":
    main()
