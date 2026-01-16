"""
Script pour importer les produits Open Food Facts dans la base de données locale.
Télécharge uniquement les produits français pour limiter la taille.
"""

import os
import sys
import django
import requests
import gzip
import csv
from datetime import datetime
from io import TextIOWrapper

# Configuration Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_tracker.settings')
django.setup()

from tracker.models import OpenFoodFactsProduct

# URL du fichier CSV Open Food Facts (export complet)
OFF_CSV_URL = 'https://static.openfoodfacts.org/data/en.openfoodfacts.org.products.csv.gz'

# Fichier local temporaire
TEMP_FILE = 'openfoodfacts_temp.csv.gz'


def download_csv():
    """Télécharge le fichier CSV compressé d'Open Food Facts."""
    print(f"[DL] Téléchargement du fichier CSV depuis {OFF_CSV_URL}...")
    print("[!]  Attention : Le fichier fait environ 1 GB compressé. Cela peut prendre plusieurs minutes.")
    
    response = requests.get(OFF_CSV_URL, stream=True)
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    downloaded = 0
    
    with open(TEMP_FILE, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"\r[%] Progression : {percent:.1f}% ({downloaded / (1024**2):.1f} MB / {total_size / (1024**2):.1f} MB)", end='')
    
    print(f"\n[OK] Téléchargement terminé : {TEMP_FILE}")


def import_products(limit_french_only=True, max_products=None):
    """
    Importe les produits depuis le CSV dans la base de données.
    
    Args:
        limit_french_only: Si True, importe uniquement les produits français
        max_products: Nombre maximum de produits à importer (None = tous)
    """
    print(f"\n[PKG] Ouverture du fichier CSV compressé...")
    
    imported_count = 0
    skipped_count = 0
    batch = []
    batch_size = 1000  # Insérer par lots de 1000 pour la performance
    
    # Ouvrir le fichier gzip et le lire comme CSV
    with gzip.open(TEMP_FILE, 'rt', encoding='utf-8') as gz_file:
        # Utiliser le délimiteur tab comme spécifié dans la doc OFF
        reader = csv.DictReader(gz_file, delimiter='\t')
        
        print(f"[?] Colonnes disponibles : {reader.fieldnames[:10]}...")  # Afficher les 10 premières colonnes
        
        for i, row in enumerate(reader):
            # Afficher la progression tous les 10000 produits
            if i % 10000 == 0:
                print(f"\r[%] Traitement : {i} produits lus, {imported_count} importés, {skipped_count} ignorés", end='')
            
            # Filtrer les produits français si demandé
            if limit_french_only:
                countries = row.get('countries', '').lower()
                if 'france' not in countries and 'fr' not in countries:
                    skipped_count += 1
                    continue
            
            # Extraire les données essentielles
            try:
                code = row.get('code', '').strip()
                product_name = row.get('product_name', '').strip()
                
                # Ignorer les produits sans code ou sans nom
                if not code or not product_name:
                    skipped_count += 1
                    continue
                
                # Extraire les nutriments (gérer les valeurs vides)
                def safe_float(value):
                    try:
                        return float(value) if value and value.strip() else None
                    except (ValueError, AttributeError):
                        return None
                
                energy_kcal = safe_float(row.get('energy-kcal_100g', ''))
                proteins = safe_float(row.get('proteins_100g', ''))
                carbs = safe_float(row.get('carbohydrates_100g', ''))
                fat = safe_float(row.get('fat_100g', ''))
                fiber = safe_float(row.get('fiber_100g', ''))
                
                # Créer l'objet produit
                product = OpenFoodFactsProduct(
                    code=code,
                    product_name=product_name[:500],  # Limiter à 500 caractères
                    brands=row.get('brands', '')[:500],
                    energy_kcal_100g=energy_kcal,
                    proteins_100g=proteins,
                    carbohydrates_100g=carbs,
                    fat_100g=fat,
                    fiber_100g=fiber,
                    countries=row.get('countries', '')[:500],
                    categories=row.get('categories', '')[:1000],
                    last_modified=None,  # On pourrait parser last_modified_datetime si nécessaire
                )
                
                batch.append(product)
                imported_count += 1
                
                # Insérer par lots pour la performance
                if len(batch) >= batch_size:
                    OpenFoodFactsProduct.objects.bulk_create(batch, ignore_conflicts=True)
                    batch = []
                    print(f"\n[SAVE] {imported_count} produits importés en base...")
                
                # Limiter le nombre de produits si demandé
                if max_products and imported_count >= max_products:
                    print(f"\n[!]  Limite de {max_products} produits atteinte.")
                    break
                    
            except Exception as e:
                print(f"\n[!]  Erreur lors du traitement du produit {row.get('code', 'UNKNOWN')}: {e}")
                skipped_count += 1
                continue
        
        # Insérer les produits restants
        if batch:
            OpenFoodFactsProduct.objects.bulk_create(batch, ignore_conflicts=True)
            print(f"\n[SAVE] Dernier lot de {len(batch)} produits importé.")
    
    print(f"\n\n[OK] Import terminé !")
    print(f"[%] Statistiques :")
    print(f"   - Produits importés : {imported_count}")
    print(f"   - Produits ignorés : {skipped_count}")
    print(f"   - Total en base : {OpenFoodFactsProduct.objects.count()}")


import argparse

def cleanup():
    """Supprime le fichier temporaire."""
    if os.path.exists(TEMP_FILE):
        try:
            os.remove(TEMP_FILE)
            print(f"[DEL]  Fichier temporaire supprimé : {TEMP_FILE}")
        except OSError:
            pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Import Open Food Facts products.')
    parser.add_argument('--force', action='store_true', help='Delete existing products without confirmation')
    parser.add_argument('--keep', action='store_true', help='Keep existing products (skip deletion prompt)')
    parser.add_argument('--limit', type=int, help='Limit the number of products to import')
    parser.add_argument('--french-only', action='store_true', default=True, help='Import only French products (default: True)')
    parser.add_argument('--all-countries', action='store_false', dest='french_only', help='Import products from all countries')
    
    args = parser.parse_args()

    print("=" * 80)
    print("IMPORT OPEN FOOD FACTS")
    print("=" * 80)
    
    try:
        # Vérifier si des produits existent déjà
        existing_count = OpenFoodFactsProduct.objects.count()
        if existing_count > 0:
            if args.force:
                print(f"[!]  {existing_count} produits existants seront supprimés (--force).")
                OpenFoodFactsProduct.objects.all().delete()
                print("[OK] Produits supprimés.")
            elif args.keep:
                print(f"[i]  conservation des {existing_count} produits existants.")
            else:
                response = input(f"\n[!]  {existing_count} produits existent déjà en base. Voulez-vous les supprimer ? (o/N) : ")
                if response.lower() == 'o':
                    print("[DEL]  Suppression des produits existants...")
                    OpenFoodFactsProduct.objects.all().delete()
                    print("[OK] Produits supprimés.")
                else:
                    print("[i]  Les nouveaux produits seront ajoutés aux existants.")
        
        # Télécharger le CSV
        if not os.path.exists(TEMP_FILE):
            download_csv()
        else:
            print(f"[i]  Fichier {TEMP_FILE} déjà présent, utilisation du fichier existant.")
        
        # Importer les produits
        import_products(limit_french_only=args.french_only, max_products=args.limit)
        
        # Nettoyer
        cleanup()
        
        print("\n[*] Import terminé avec succès !")
        
    except KeyboardInterrupt:
        print("\n\n[!]  Import interrompu par l'utilisateur.")
        cleanup()
    except Exception as e:
        print(f"\n\n[X] Erreur lors de l'import : {e}")
        import traceback
        traceback.print_exc()
        cleanup()
