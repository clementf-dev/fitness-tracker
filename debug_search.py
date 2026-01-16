import requests

def _search_off_api_debug(query: str, limit: int = 10):
    print(f"--- Searching for: '{query}' ---")
    try:
        url = 'https://world.openfoodfacts.org/cgi/search.pl'
        params = {
            'search_terms': query,
            'search_simple': 1,
            'action': 'process',
            'json': 1,
            'page_size': limit,
            'fields': 'code,product_name,brands,nutriments'
        }
        headers = {'User-Agent': 'FitnessTrackerApp - Version 1.0'}
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            products = data.get('products', [])
            print(f"Found {len(products)} raw results from API.")
            
            accepted_count = 0
            for i, p in enumerate(products):
                name = p.get('product_name', 'Inconnu')
                nutriments = p.get('nutriments', {})
                cal_raw = nutriments.get('energy-kcal_100g')
                
                cal = 0
                if cal_raw:
                    try:
                        cal = float(cal_raw)
                    except:
                        cal = 0
                
                # The filter logic
                is_kept = True
                if not cal_raw or cal <= 0:
                    is_kept = False
                
                status = "KEPT" if is_kept else "FILTERED (0 cal)"
                print(f"[{i+1}] {name} ({p.get('brands')}) - Cal: {cal_raw} -> {status}")
                
                if is_kept: accepted_count += 1
                
            print(f"Total accepted: {accepted_count}")
        else:
            print(f"Error: Status code {response.status_code}")
            
    except Exception as e:
        print(f"Exception: {e}")

_search_off_api_debug("poelee", 10)
_search_off_api_debug("nutella", 5)
