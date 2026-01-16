def load_generic_foods():
    """Charge tous les aliments de GENERIC_FOODS depuis views.py."""
    return [
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
        # Source: CIQUAL 2020 - Tomate, pulpe et peau, crue
        {'name': 'Tomate', 'calories': 19, 'protein': 0.9, 'carbs': 2.5, 'fat': 0.3, 'fiber': 1.2, 'unit_weight': 150, 'keywords': ['tomate', 'tomato']},
        {'name': 'Oignon', 'calories': 40, 'protein': 1.1, 'carbs': 9, 'fat': 0.1, 'fiber': 1.7, 'unit_weight': 150, 'keywords': ['oignon', 'onion']},
        {'name': 'Poivron rouge', 'calories': 31, 'protein': 1, 'carbs': 6, 'fat': 0.3, 'fiber': 2.1, 'unit_weight': 150, 'keywords': ['poivron', 'pepper', 'bell pepper']},
        {'name': 'Poivron vert', 'calories': 20, 'protein': 0.9, 'carbs': 4.6, 'fat': 0.2, 'fiber': 1.7, 'unit_weight': 150, 'keywords': ['poivron', 'pepper', 'bell pepper']},
        # Source: CIQUAL 2020 - Carotte, crue
        {'name': 'Carotte', 'calories': 40, 'protein': 0.6, 'carbs': 7.6, 'fat': 0.2, 'fiber': 2.7, 'unit_weight': 80, 'keywords': ['carotte', 'carrot']},
        {'name': 'Courgette', 'calories': 17, 'protein': 1.2, 'carbs': 3.1, 'fat': 0.3, 'fiber': 1, 'unit_weight': 200, 'keywords': ['courgette', 'zucchini']},
        {'name': 'Concombre', 'calories': 15, 'protein': 0.7, 'carbs': 3.6, 'fat': 0.1, 'fiber': 0.5, 'unit_weight': 300, 'keywords': ['concombre', 'cucumber']},
        # Source: CIQUAL 2020 - Avocat, pulpe, cru
        {'name': 'Avocat', 'calories': 205, 'protein': 1.6, 'carbs': 0.8, 'fat': 20.6, 'fiber': 3.6, 'unit_weight': 200, 'keywords': ['avocat', 'avocado']},
        {'name': 'Ail (gousse)', 'calories': 149, 'protein': 6.4, 'carbs': 33, 'fat': 0.5, 'fiber': 2.1, 'unit_weight': 5, 'keywords': ['ail', 'garlic', 'gousse']},
        {'name': 'Pomme de terre', 'calories': 77, 'protein': 2, 'carbs': 17, 'fat': 0.1, 'fiber': 2.2, 'unit_weight': 175, 'keywords': ['pomme de terre', 'potato', 'patate']},
        {'name': 'Champignon de Paris', 'calories': 22, 'protein': 3.1, 'carbs': 3.3, 'fat': 0.3, 'fiber': 1, 'unit_weight': 20, 'keywords': ['champignon', 'mushroom']},
        {'name': 'Poireau', 'calories': 61, 'protein': 1.5, 'carbs': 14, 'fat': 0.3, 'fiber': 1.8, 'unit_weight': 200, 'keywords': ['poireau', 'leek']},
        {'name': 'Aubergine', 'calories': 25, 'protein': 1, 'carbs': 6, 'fat': 0.2, 'fiber': 3, 'unit_weight': 300, 'keywords': ['aubergine', 'eggplant']},
        {'name': 'Brocoli', 'calories': 34, 'protein': 2.8, 'carbs': 7, 'fat': 0.4, 'fiber': 2.6, 'unit_weight': 150, 'keywords': ['brocoli', 'broccoli']},
        {'name': 'Chou-fleur', 'calories': 25, 'protein': 1.9, 'carbs': 5, 'fat': 0.3, 'fiber': 2, 'unit_weight': 600, 'keywords': ['chou-fleur', 'cauliflower', 'chou fleur']},
        {'name': 'Épinard (frais)', 'calories': 23, 'protein': 2.9, 'carbs': 3.6, 'fat': 0.4, 'fiber': 2.2, 'unit_weight': 30, 'keywords': ['epinard', 'épinard', 'spinach']},
        {'name': 'Salade (laitue)', 'calories': 15, 'protein': 1.4, 'carbs': 2.9, 'fat': 0.2, 'fiber': 1.3, 'unit_weight': 300, 'keywords': ['salade', 'laitue', 'lettuce']},
        {'name': 'Haricot vert', 'calories': 31, 'protein': 1.8, 'carbs': 7, 'fat': 0.1, 'fiber': 2.7, 'unit_weight': 10, 'keywords': ['haricot', 'green bean']},
        {'name': 'Petit pois', 'calories': 81, 'protein': 5.4, 'carbs': 14, 'fat': 0.4, 'fiber': 5.7, 'unit_weight': 100, 'keywords': ['petit pois', 'peas', 'pois']},
        {'name': 'Maïs', 'calories': 86, 'protein': 3.3, 'carbs': 19, 'fat': 1.4, 'fiber': 2, 'unit_weight': 250, 'keywords': ['mais', 'maïs', 'corn']},
        {'name': 'Céleri', 'calories': 16, 'protein': 0.7, 'carbs': 3, 'fat': 0.2, 'fiber': 1.6, 'unit_weight': 40, 'keywords': ['celeri', 'céleri', 'celery']},
        {'name': 'Betterave', 'calories': 43, 'protein': 1.6, 'carbs': 10, 'fat': 0.2, 'fiber': 2.8, 'unit_weight': 150, 'keywords': ['betterave', 'beet']},
        {'name': 'Radis', 'calories': 16, 'protein': 0.7, 'carbs': 3.4, 'fat': 0.1, 'fiber': 1.6, 'unit_weight': 10, 'keywords': ['radis', 'radish']},
        {'name': 'Fenouil', 'calories': 31, 'protein': 1.2, 'carbs': 7, 'fat': 0.2, 'fiber': 3.1, 'unit_weight': 250, 'keywords': ['fenouil', 'fennel']},
        {'name': 'Asperge', 'calories': 20, 'protein': 2.2, 'carbs': 3.9, 'fat': 0.1, 'fiber': 2.1, 'unit_weight': 20, 'keywords': ['asperge', 'asparagus']},
        {'name': 'Artichaut', 'calories': 47, 'protein': 3.3, 'carbs': 11, 'fat': 0.2, 'fiber': 5.4, 'unit_weight': 300, 'keywords': ['artichaut', 'artichoke']},
        
        # Viandes basiques (très peu de fibres)
        {'name': 'Poulet (blanc, cru)', 'calories': 120, 'protein': 22, 'carbs': 0, 'fat': 3, 'fiber': 0, 'unit_weight': 150, 'keywords': ['poulet', 'chicken', 'blanc de poulet', 'filet de poulet']},
        {'name': 'Boeuf haché (5% MG)', 'calories': 137, 'protein': 21, 'carbs': 0, 'fat': 5, 'fiber': 0, 'unit_weight': 125, 'keywords': ['boeuf', 'beef', 'steak haché', 'viande hachée']},
        {'name': 'Dinde (escalope, crue)', 'calories': 104, 'protein': 24, 'carbs': 0, 'fat': 1, 'fiber': 0, 'unit_weight': 150, 'keywords': ['dinde', 'turkey', 'escalope']},
        
        # Poissons (très peu de fibres)
        {'name': 'Saumon (filet, cru)', 'calories': 208, 'protein': 20, 'carbs': 0, 'fat': 13, 'fiber': 0, 'unit_weight': 150, 'keywords': ['saumon', 'salmon']},
        {'name': 'Thon (frais, cru)', 'calories': 144, 'protein': 23, 'carbs': 0, 'fat': 5, 'fiber': 0, 'unit_weight': 150, 'keywords': ['thon', 'tuna']},
        {'name': 'Cabillaud (filet, cru)', 'calories': 82, 'protein': 18, 'carbs': 0, 'fat': 0.7, 'fiber': 0, 'unit_weight': 150, 'keywords': ['cabillaud', 'cod', 'colin']},
        {'name': 'Crevette (crue)', 'calories': 99, 'protein': 24, 'carbs': 0.2, 'fat': 0.3, 'fiber': 0, 'unit_weight': 15, 'keywords': ['crevette', 'shrimp', 'prawn']},
        
        # Produits laitiers basiques (très peu de fibres)
        {'name': 'Lait entier', 'calories': 61, 'protein': 3.2, 'carbs': 4.7, 'fat': 3.3, 'fiber': 0, 'unit_weight': 250, 'keywords': ['lait', 'milk', 'lait entier']},
        {'name': 'Lait demi-écrémé', 'calories': 46, 'protein': 3.2, 'carbs': 4.8, 'fat': 1.5, 'fiber': 0, 'unit_weight': 250, 'keywords': ['lait', 'milk', 'demi']},
        # Source: CIQUAL 2020 - Yaourt, nature, au lait entier
        {'name': 'Yaourt nature', 'calories': 69, 'protein': 3.8, 'carbs': 5, 'fat': 3.4, 'fiber': 0, 'unit_weight': 125, 'keywords': ['yaourt', 'yogurt', 'yoghurt']},
        {'name': 'Fromage blanc 0%', 'calories': 45, 'protein': 8, 'carbs': 4, 'fat': 0, 'fiber': 0, 'unit_weight': 100, 'keywords': ['fromage blanc', 'cottage']},
        
        # Céréales et féculents
        {'name': 'Riz blanc (cru)', 'calories': 365, 'protein': 7, 'carbs': 79, 'fat': 0.6, 'fiber': 1.3, 'unit_weight': 80, 'keywords': ['riz', 'rice']},
        {'name': 'Pâtes (crues)', 'calories': 350, 'protein': 12, 'carbs': 72, 'fat': 1.5, 'fiber': 2.5, 'unit_weight': 100, 'keywords': ['pates', 'pâtes', 'pasta', 'spaghetti']},
        {'name': 'Pain (baguette)', 'calories': 274, 'protein': 9, 'carbs': 56, 'fat': 1.3, 'fiber': 2.7, 'unit_weight': 250, 'keywords': ['pain', 'bread', 'baguette']},
        {'name': 'Flocons d\'avoine', 'calories': 367, 'protein': 14, 'carbs': 58, 'fat': 7, 'fiber': 10, 'unit_weight': 40, 'keywords': ['avoine', 'oats', 'flocons', 'porridge']},
        
        # Oléagineux
        {'name': 'Amande', 'calories': 579, 'protein': 21, 'carbs': 22, 'fat': 50, 'fiber': 12.5, 'unit_weight': 1.2, 'keywords': ['amande', 'almond']},
        {'name': 'Noix', 'calories': 654, 'protein': 15, 'carbs': 14, 'fat': 65, 'fiber': 7, 'unit_weight': 5, 'keywords': ['noix', 'walnut']},
        {'name': 'Noisette', 'calories': 628, 'protein': 15, 'carbs': 17, 'fat': 61, 'fiber': 10, 'unit_weight': 2, 'keywords': ['noisette', 'hazelnut']},
        {'name': 'Cacahuète', 'calories': 567, 'protein': 26, 'carbs': 16, 'fat': 49, 'fiber': 9, 'unit_weight': 1.5, 'keywords': ['cacahuete', 'cacahuète', 'peanut', 'arachide']},
    ]

