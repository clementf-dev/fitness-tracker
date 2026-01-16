"""
Script pour extraire GENERIC_FOODS de views.py et mettre à jour audit_ciqual.py
"""
import re

# Lire views.py
with open(r'c:\Users\Clement\.gemini\antigravity\playground\icy-interstellar\fitness-tracker\tracker\views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Extraire GENERIC_FOODS
start = content.find('GENERIC_FOODS = [')
end = content.find('\n    ]\n', start) + len('\n    ]\n')
generic_foods_block = content[start:end]

# Compter les aliments
count = generic_foods_block.count("{'name':")
print(f"Trouvé {count} aliments dans GENERIC_FOODS")

# Extraire juste la liste
foods_list_start = generic_foods_block.find('[')
foods_list = generic_foods_block[foods_list_start:]

# Créer le code Python pour load_generic_foods
new_function = f'''def load_generic_foods():
    """Charge tous les aliments de GENERIC_FOODS depuis views.py."""
    return {foods_list}
'''

print(f"\nFonction générée avec {count} aliments")
print("Premiers 500 caractères:")
print(new_function[:500])

# Sauvegarder dans un fichier temporaire
with open('generic_foods_extracted.py', 'w', encoding='utf-8') as f:
    f.write(new_function)

print("\n✅ Extraction sauvegardée dans generic_foods_extracted.py")
