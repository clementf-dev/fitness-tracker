"""
Food search and database views.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.core.paginator import Paginator
import requests

from tracker.models import Food, MealItem, MealTemplateItem, OpenFoodFactsProduct
from tracker.forms import FoodForm
from tracker.services.food_search_service import get_food_search_service


def food_database(request):
    """Liste des aliments dans la banque de données"""
    query = request.GET.get('q', '')
    page_number = request.GET.get('page', 1)
    
    if query:
        # Use optimized search service (Accent insensitive for user foods)
        search_service = get_food_search_service()
        foods = search_service.search(query, limit=100, local_only=True)
    else:
        foods = Food.objects.all().order_by('name')
    
    paginator = Paginator(foods, 20)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'total_foods': paginator.count,
    }
    return render(request, 'tracker/food_database.html', context)


def add_food(request):
    """Ajouter un aliment à la banque de données"""
    if request.method == 'POST':
        form = FoodForm(request.POST)
        if form.is_valid():
            food = form.save()
            messages.success(request, f'Aliment "{food.name}" ajouté avec succès!')
            
            # Redirection selon l'origine
            next_url = request.POST.get('next', '')
            if next_url:
                return redirect(next_url)
            return redirect('food_database')
    else:
        # Pré-remplir avec les données de recherche si disponibles
        initial = {}
        for field in ['name', 'brand', 'calories', 'protein', 'carbs', 'fat', 'fiber', 'serving_size', 'barcode']:
            if request.GET.get(field):
                initial[field] = request.GET.get(field)
        
        form = FoodForm(initial=initial)
    
    return render(request, 'tracker/add_food.html', {'form': form})


def edit_food(request, food_id):
    """Modifier un aliment existant"""
    food = get_object_or_404(Food, id=food_id)
    
    if request.method == 'POST':
        form = FoodForm(request.POST, instance=food)
        if form.is_valid():
            form.save()
            messages.success(request, f'Aliment "{food.name}" modifié avec succès!')
            return redirect('food_database')
    else:
        form = FoodForm(instance=food)
    
    return render(request, 'tracker/add_food.html', {'form': form, 'editing': True, 'food': food})


@require_POST
def delete_food(request, food_id):
    """Supprimer un aliment"""
    food = get_object_or_404(Food, id=food_id)
    
    # Vérifier si l'aliment est utilisé
    if MealItem.objects.filter(food=food).exists() or MealTemplateItem.objects.filter(food=food).exists():
        messages.error(request, f'Impossible de supprimer "{food.name}" car il est utilisé dans des repas.')
        return redirect('food_database')
    
    food_name = food.name
    food.delete()
    messages.success(request, f'Aliment "{food_name}" supprimé.')
    return redirect('food_database')


@require_GET
def search_food_api(request):
    """
    Rechercher des aliments via base locale + Open Food Facts API.
    
    Uses the new FoodSearchService for improved relevance scoring.
    Supports barcode scanning as well.
    """
    query = request.GET.get('q', '').strip()
    local_only = request.GET.get('local_only', 'false').lower() == 'true'
    
    if not query:
        return JsonResponse({'results': [], 'error': 'Veuillez entrer un terme de recherche.'})
    
    # Handle barcode search (digits only, length >= 8)
    if query.isdigit() and len(query) >= 8:
        barcode_result = _search_by_barcode(query)
        if barcode_result:
            return JsonResponse({'results': [barcode_result]})
    
    # Use the optimized search service
    search_service = get_food_search_service()
    results = search_service.search(query, limit=20, local_only=local_only)
    
    print(f"DEBUG: Search '{query}' -> Local results: {len(results)} (Threshold: 15)")
    
    # If not enough results and not local_only, try external API
    # Increased threshold (5 -> 15) to force more online results for generic terms
    if not local_only and len(results) < 15:
        print("DEBUG: Triggering API search...")
        external_results = _search_off_api(query, limit=20 - len(results))
        print(f"DEBUG: API returned {len(external_results)} results")
        results.extend(external_results)
    else:
        print("DEBUG: Skipping API search (enough local results or local_only)")
    
    return JsonResponse({'results': results[:20]})


def _search_by_barcode(code: str) -> dict:
    """Search for a product by barcode using OpenFoodFacts API."""
    try:
        url = f'https://world.openfoodfacts.org/api/v0/product/{code}.json'
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get('status') == 1:
            product = data.get('product', {})
            nutriments = product.get('nutriments', {})
            
            calories = nutriments.get('energy-kcal_100g', nutriments.get('energy_100g', 0))
            if isinstance(calories, str):
                try:
                    calories = float(calories)
                except:
                    calories = 0
            
            if calories > 400 and not nutriments.get('energy-kcal_100g'):
                calories = calories / 4.184
            
            protein = nutriments.get('proteins_100g', 0)
            carbs = nutriments.get('carbohydrates_100g', 0)
            fat = nutriments.get('fat_100g', 0)
            fiber = nutriments.get('fiber_100g', 0)
            
            # Save to local database
            OpenFoodFactsProduct.objects.update_or_create(
                code=product.get('code', code),
                defaults={
                    'product_name': product.get('product_name', 'Produit inconnu')[:200],
                    'brands': product.get('brands', '')[:200],
                    'energy_kcal_100g': calories,
                    'proteins_100g': protein,
                    'carbohydrates_100g': carbs,
                    'fat_100g': fat,
                    'fiber_100g': fiber,
                }
            )

            return {
                'id': f"off_{product.get('code', code)}",
                'name': product.get('product_name', 'Produit inconnu'),
                'brand': product.get('brands', ''),
                'calories': round(calories) if calories else 0,
                'protein': round(float(protein), 1) if protein else 0,
                'carbs': round(float(carbs), 1) if carbs else 0,
                'fat': round(float(fat), 1) if fat else 0,
                'fiber': round(float(fiber), 1) if fiber else 0,
                'serving_size': 100,
                'barcode': product.get('code', code),
                'is_unit_based': False,
                'unit_weight': None,
                'is_generic': False,
                'source': 'OpenFoodFacts',
            }
                
    except Exception as e:
        print(f"Erreur recherche code-barres: {str(e)}")
    
    return None


def _search_off_api(query: str, limit: int = 10) -> list:
    """Search OpenFoodFacts API and save results locally."""
    results = []
    
    try:
        url = 'https://world.openfoodfacts.org/cgi/search.pl'
        params = {
            'search_terms': query,
            'search_simple': 1,
            'action': 'process',
            'json': 1,
            'page_size': limit,
            'fields': 'code,product_name,brands,nutriments,countries,categories,last_modified_t'
        }
        headers = {'User-Agent': 'FitnessTrackerApp - Version 1.0'}
        # Increased timeout to 10s to avoid failure on slow pythonanywhere connection
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            for p in data.get('products', []):
                code = p.get('code', '')
                
                # Save to local database
                if code and not OpenFoodFactsProduct.objects.filter(code=code).exists():
                    try:
                        nutriments = p.get('nutriments', {})
                        
                        def safe_float(val):
                            try:
                                return float(val)
                            except:
                                return 0.0

                        OpenFoodFactsProduct.objects.create(
                            code=code,
                            product_name=p.get('product_name', '')[:500],
                            brands=p.get('brands', '')[:500],
                            energy_kcal_100g=safe_float(nutriments.get('energy-kcal_100g')),
                            proteins_100g=safe_float(nutriments.get('proteins_100g')),
                            carbohydrates_100g=safe_float(nutriments.get('carbohydrates_100g')),
                            fat_100g=safe_float(nutriments.get('fat_100g')),
                            fiber_100g=safe_float(nutriments.get('fiber_100g')),
                            countries=p.get('countries', '')[:500],
                            categories=p.get('categories', '')[:1000]
                        )
                    except Exception as e_save:
                        print(f"Erreur sauvegarde produit {code}: {e_save}")

                # Add to results
                nutriments = p.get('nutriments', {})
                cal = nutriments.get('energy-kcal_100g', 0)
                if isinstance(cal, str):
                    try:
                        cal = float(cal)
                    except:
                        cal = 0
                
                # Desired filtering: Remove 0 calorie items (pollution/incomplete data)
                if not cal or float(cal) <= 0:
                    continue

                results.append({
                    'id': f"off_{code}",
                    'name': p.get('product_name', 'Inconnu'),
                    'brand': p.get('brands', ''),
                    'calories': round(float(cal or 0)),
                    'protein': round(float(nutriments.get('proteins_100g', 0) or 0), 1),
                    'carbs': round(float(nutriments.get('carbohydrates_100g', 0) or 0), 1),
                    'fat': round(float(nutriments.get('fat_100g', 0) or 0), 1),
                    'fiber': round(float(nutriments.get('fiber_100g', 0) or 0), 1),
                    'serving_size': 100,
                    'barcode': code,
                    'is_unit_based': False,
                    'unit_weight': None,
                    'is_generic': False,
                    'source': 'OpenFoodFacts (API)',
                })
                
    except Exception as e:
        print(f"Erreur API OFF: {e}")
    
    return results
