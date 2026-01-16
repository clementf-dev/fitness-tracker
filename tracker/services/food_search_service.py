"""
Service de recherche d'aliments avec scoring de pertinence.

Ce service implémente un algorithme de recherche multicritère pour améliorer
la pertinence des résultats d'autocomplétion des aliments.
"""
import re
import unicodedata
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from django.db.models import Q

from tracker.models import Food, OpenFoodFactsProduct
from tracker.food_constants import GENERIC_FOODS


def normalize_text(text: str) -> str:
    """
    Normalise le texte pour la recherche:
    - Conversion en minuscules
    - Suppression des accents
    - Suppression de la ponctuation
    - Normalisation des espaces
    """
    if not text:
        return ""
    
    # Lowercase
    text = text.lower()
    
    # Remove accents using NFD normalization
    text = unicodedata.normalize('NFD', text)
    text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
    
    # Replace special characters with space
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    return text


def tokenize(text: str) -> List[str]:
    """Tokenize le texte normalisé en mots."""
    return normalize_text(text).split()


@dataclass
class SearchResult:
    """Résultat de recherche avec score de pertinence."""
    id: Any
    name: str
    brand: str
    calories: int
    protein: float
    carbs: float
    fat: float
    fiber: float
    serving_size: int
    barcode: str
    is_unit_based: bool
    unit_weight: Optional[float]
    is_generic: bool
    source: str
    score: float = 0.0
    
    # For deduplication
    name_normalized: str = field(default="", repr=False)
    
    def to_dict(self) -> Dict:
        """Convertit en dictionnaire pour JSON."""
        return {
            'id': self.id,
            'name': self.name,
            'brand': self.brand,
            'calories': self.calories,
            'protein': self.protein,
            'carbs': self.carbs,
            'fat': self.fat,
            'fiber': self.fiber,
            'serving_size': self.serving_size,
            'barcode': self.barcode,
            'is_unit_based': self.is_unit_based,
            'unit_weight': self.unit_weight,
            'is_generic': self.is_generic,
            'source': self.source,
        }


class FoodSearchService:
    """
    Service de recherche d'aliments avec scoring de pertinence.
    
    Critères de scoring (0-100):
    1. Correspondance exacte du nom: +50 points
    2. Nom commence par le terme: +30 points
    3. Mot complet trouvé dans le nom: +20 points par mot
    4. Correspondance partielle: +10 points
    5. Correspondance marque: +15 points
    6. Priorité source (bonus de base):
       - User Foods: +100 points
       - Generic (CIQUAL): +80 points
       - OFF Local: +60 points
       - OFF API: +40 points
    """
    
    # Priorités par source
    PRIORITY_USER_FOOD = 100
    PRIORITY_GENERIC = 80
    PRIORITY_OFF_LOCAL = 60
    PRIORITY_OFF_API = 40
    
    # Scores de matching
    SCORE_EXACT_MATCH = 50
    SCORE_STARTS_WITH = 30
    SCORE_WORD_MATCH = 20
    SCORE_PARTIAL_MATCH = 10
    SCORE_BRAND_MATCH = 15
    
    def __init__(self):
        self._cache = {}
    
    def search(
        self, 
        query: str, 
        limit: int = 20, 
        local_only: bool = False
    ) -> List[Dict]:
        """
        Recherche des aliments avec scoring de pertinence.
        
        Args:
            query: Terme de recherche
            limit: Nombre maximum de résultats
            local_only: Si True, ne cherche que dans les sources locales
            
        Returns:
            Liste de dictionnaires représentant les aliments triés par pertinence
        """
        if not query or len(query.strip()) < 2:
            return []
        
        query = query.strip()
        query_normalized = normalize_text(query)
        query_tokens = tokenize(query)
        
        results: List[SearchResult] = []
        seen_names: set = set()  # For deduplication
        
        # 1. User Foods (highest priority)
        user_results = self._search_user_foods(query, query_normalized, query_tokens)
        results.extend(user_results)
        
        # 2. Generic Foods (CIQUAL)
        generic_results = self._search_generic_foods(query, query_normalized, query_tokens)
        results.extend(generic_results)
        
        # 3. OpenFoodFacts Local Database
        off_results = self._search_off_local(query, query_normalized, query_tokens)
        results.extend(off_results)
        
        # Deduplicate by normalized name
        unique_results = []
        for result in results:
            if result.name_normalized not in seen_names:
                seen_names.add(result.name_normalized)
                unique_results.append(result)
        
        # Sort by score (descending)
        unique_results.sort(key=lambda x: x.score, reverse=True)
        
        # Convert to dicts and limit
        return [r.to_dict() for r in unique_results[:limit]]

    def _calculate_score(
        self, 
        name: str, 
        brand: str,
        keywords: List[str],
        query: str,
        query_normalized: str,
        query_tokens: List[str],
        base_priority: float
    ) -> float:
        """
        Calcule le score de pertinence pour un résultat.
        
        Args:
            name: Nom de l'aliment
            brand: Marque de l'aliment
            keywords: Mots-clés de recherche (pour génériques)
            query: Requête originale
            query_normalized: Requête normalisée
            query_tokens: Tokens de la requête
            base_priority: Priorité de base selon la source
            
        Returns:
            Score de pertinence (0-200+)
        """
        score = base_priority
        name_normalized = normalize_text(name)
        brand_normalized = normalize_text(brand) if brand else ""
        
        # Check keywords if present (for generic foods)
        all_searchable = [name_normalized]
        if keywords:
            all_searchable.extend([normalize_text(kw) for kw in keywords])
        
        # Exact match on name
        if query_normalized == name_normalized:
            score += self.SCORE_EXACT_MATCH
        
        # Name starts with query
        elif name_normalized.startswith(query_normalized):
            score += self.SCORE_STARTS_WITH
        
        # All query tokens found as complete words
        name_tokens = tokenize(name)
        all_keywords_normalized = [normalize_text(kw) for kw in keywords] if keywords else []
        all_tokens = set(name_tokens + all_keywords_normalized)
        
        matched_tokens = 0
        for qt in query_tokens:
            # Check if token matches any word completely
            if qt in all_tokens:
                matched_tokens += 1
                score += self.SCORE_WORD_MATCH
            # Check if token is contained in any word
            elif any(qt in t for t in all_tokens):
                score += self.SCORE_PARTIAL_MATCH
        
        # Boost if all query tokens matched
        if matched_tokens == len(query_tokens) and len(query_tokens) > 1:
            score += 15  # Multi-word complete match bonus
        
        # Brand match
        if brand_normalized and query_normalized in brand_normalized:
            score += self.SCORE_BRAND_MATCH
        
        return score
    
    def _is_match(self, name_normalized: str, brand_normalized: str, query_tokens: List[str]) -> bool:
        """Vérifie si les tokens correspondent au nom ou à la marque (normalisés)."""
        for token in query_tokens:
            if token in name_normalized:
                return True
            if brand_normalized and token in brand_normalized:
                return True
        return False

    def _search_user_foods(
        self, 
        query: str, 
        query_normalized: str, 
        query_tokens: List[str]
    ) -> List[SearchResult]:
        """Recherche dans les aliments créés par l'utilisateur."""
        results = []
        
        # NOTE: Pour supporter la recherche sans accent sur SQLite (ex: "poele" trouve "Poêlée"),
        # nous devons filtrer en Python car `icontains` est sensible aux accents.
        # Pour une base utilisateur personnelle (< quelques milliers), c'est performant.
        foods = Food.objects.all()
        
        for food in foods:
            name_normalized = normalize_text(food.name)
            brand_normalized = normalize_text(food.brand) if food.brand else ""
            
            if not self._is_match(name_normalized, brand_normalized, query_tokens):
                # print(f"DEBUG: FAIL {food.name} | {name_normalized}")
                continue
            print(f"DEBUG: MATCH {food.name} | {name_normalized}")
            
            score = self._calculate_score(
                name=food.name,
                brand=food.brand or '',
                keywords=[],
                query=query,
                query_normalized=query_normalized,
                query_tokens=query_tokens,
                base_priority=self.PRIORITY_USER_FOOD
            )
            
            results.append(SearchResult(
                id=food.id,
                name=food.name,
                brand=food.brand or 'Mon aliment',
                calories=food.calories,
                protein=float(food.protein),
                carbs=float(food.carbs),
                fat=float(food.fat),
                fiber=float(food.fiber),
                serving_size=food.serving_size,
                barcode=food.barcode,
                is_unit_based=False,
                unit_weight=None,
                is_generic=False,
                source='Mes Aliments',
                score=score,
                name_normalized=name_normalized
            ))
        
        return results
    
    def _search_generic_foods(
        self, 
        query: str, 
        query_normalized: str, 
        query_tokens: List[str]
    ) -> List[SearchResult]:
        """Recherche dans les aliments génériques (CIQUAL)."""
        results = []
        
        for idx, food in enumerate(GENERIC_FOODS):
            keywords = food.get('keywords', [])
            keywords_normalized = [normalize_text(kw) for kw in keywords]
            name_normalized = normalize_text(food['name'])
            
            # Check matches using helper manually or similar logic
            matches = False
            for token in query_tokens:
                if any(token in kw or kw in token for kw in keywords_normalized):
                    matches = True
                    break
                if token in name_normalized:
                    matches = True
                    break
            
            if not matches:
                continue
            
            score = self._calculate_score(
                name=food['name'],
                brand='',
                keywords=keywords,
                query=query,
                query_normalized=query_normalized,
                query_tokens=query_tokens,
                base_priority=self.PRIORITY_GENERIC
            )
            
            results.append(SearchResult(
                id=f"generic_{idx}",
                name=food['name'],
                brand='Aliment générique',
                calories=food['calories'],
                protein=food['protein'],
                carbs=food['carbs'],
                fat=food['fat'],
                fiber=food.get('fiber', 0),
                serving_size=food['unit_weight'],
                barcode='',
                is_unit_based=True,
                unit_weight=food['unit_weight'],
                is_generic=True,
                source='CIQUAL',
                score=score,
                name_normalized=name_normalized
            ))
        
        return results
    
    def _search_off_local(
        self, 
        query: str, 
        query_normalized: str, 
        query_tokens: List[str]
    ) -> List[SearchResult]:
        """Recherche dans la base OpenFoodFacts locale."""
        results = []
        
        # Build query filter for multi-word search
        q_filter = Q()
        for token in query_tokens:
            q_filter &= (Q(product_name__icontains=token) | Q(brands__icontains=token))
        
        # Pour récupérer les résultats sans tuer le serveur (500k+ produits), on réutilise le filtre SQL.
        # Limitation: sensible aux accents sur SQLite. Compromis nécessaire pour la performance.
        # Filter out 0 calorie items (often poor quality data)
        products = OpenFoodFactsProduct.objects.filter(q_filter, energy_kcal_100g__gt=0)[:30]
        
        for product in products:
            score = self._calculate_score(
                name=product.product_name,
                brand=product.brands or '',
                keywords=[],
                query=query,
                query_normalized=query_normalized,
                query_tokens=query_tokens,
                base_priority=self.PRIORITY_OFF_LOCAL
            )
            
            results.append(SearchResult(
                id=f"off_{product.code}",
                name=product.product_name,
                brand=product.brands or '',
                calories=round(product.energy_kcal_100g or 0),
                protein=round(product.proteins_100g or 0, 1),
                carbs=round(product.carbohydrates_100g or 0, 1),
                fat=round(product.fat_100g or 0, 1),
                fiber=round(product.fiber_100g or 0, 1),
                serving_size=100,
                barcode=product.code,
                is_unit_based=False,
                unit_weight=None,
                is_generic=False,
                source='OpenFoodFacts',
                score=score,
                name_normalized=normalize_text(product.product_name)
            ))
        
        return results


# Singleton instance for convenience
_search_service = None

def get_food_search_service() -> FoodSearchService:
    """Get the singleton FoodSearchService instance."""
    global _search_service
    if _search_service is None:
        _search_service = FoodSearchService()
    return _search_service
