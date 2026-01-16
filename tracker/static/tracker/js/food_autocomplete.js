// Autocomplétion pour la recherche d'aliments dans le dashboard
document.addEventListener('DOMContentLoaded', function () {
    const searchInputs = document.querySelectorAll('.food-search-input');

    searchInputs.forEach(input => {
        const resultsDiv = input.nextElementSibling.nextElementSibling; // Skip hidden input
        const hiddenInput = input.nextElementSibling;
        const form = input.closest('form');
        let searchTimeout;

        let searchController = null;

        // Recherche avec debounce
        input.addEventListener('input', function () {
            clearTimeout(searchTimeout);
            const query = this.value.trim();

            if (query.length < 2) {
                resultsDiv.style.display = 'none';
                return;
            }

            // Annuler la requête précédente si elle est encore en cours
            if (searchController) {
                searchController.abort();
            }
            searchController = new AbortController();
            const signal = searchController.signal;

            searchTimeout = setTimeout(() => {
                fetch(`/api/food/search/?q=${encodeURIComponent(query)}&local_only=false`, { signal })
                    .then(response => response.json())
                    .then(data => {
                        displayResults(data.results, resultsDiv, input, hiddenInput);
                    })
                    .catch(error => {
                        if (error.name === 'AbortError') return; // Ignorer les requêtes annulées
                        console.error('Erreur recherche:', error);
                    });
            }, 100);
        });

        // Fermer les résultats si clic en dehors
        document.addEventListener('click', function (e) {
            if (!input.contains(e.target) && !resultsDiv.contains(e.target)) {
                resultsDiv.style.display = 'none';
            }
        });

        // Validation du formulaire
        form.addEventListener('submit', function (e) {
            if (!hiddenInput.value) {
                // Si l'utilisateur a tapé quelque chose mais pas sélectionné (ou pas trouvé)
                const query = input.value.trim();
                if (query.length > 1) {
                    e.preventDefault();
                    // Rediriger vers la page d'ajout avec le nom pré-rempli
                    // On utilise window.location pour sortir du formulaire actuel
                    const currentPath = window.location.pathname;
                    window.location.href = `/food/add/?name=${encodeURIComponent(query)}&next=${encodeURIComponent(currentPath)}`;
                } else {
                    e.preventDefault();
                    alert('Veuillez sélectionner un aliment dans la liste ou taper un nom pour le créer.');
                }
            }
        });
    });

    function displayResults(results, resultsDiv, input, hiddenInput) {
        if (!results || results.length === 0) {
            resultsDiv.innerHTML = '<div style="padding: 1rem; color: #888;">Aucun résultat trouvé</div>';
            resultsDiv.style.display = 'block';
            return;
        }

        resultsDiv.innerHTML = results.map(food => `
            <div class="autocomplete-item" 
                data-food-id="${food.id || ''}" 
                data-food-name="${food.name}"
                style="
                    padding: 0.75rem 1rem;
                    cursor: pointer;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
                    transition: background 0.2s;
                ">
                <div style="font-weight: 500; color: #ffffff;">${food.name}</div>
                <div style="font-size: 0.85rem; color: #888; margin-top: 0.25rem;">
                    ${food.brand || 'Aliment générique'} • 
                    <span style="color: #f5576c;">${food.calories} kcal</span> • 
                    P: ${food.protein}g • G: ${food.carbs}g • L: ${food.fat}g
                    ${food.fiber ? ` • F: ${food.fiber}g` : ''}
                </div>
            </div>
        `).join('');

        resultsDiv.style.display = 'block';

        // Ajouter événements de clic et hover
        resultsDiv.querySelectorAll('.autocomplete-item').forEach(item => {
            item.addEventListener('mouseenter', function () {
                this.style.background = 'rgba(102, 126, 234, 0.2)';
            });

            item.addEventListener('mouseleave', function () {
                this.style.background = 'transparent';
            });

            item.addEventListener('click', function () {
                const foodId = this.dataset.foodId;
                const foodName = this.dataset.foodName;

                input.value = foodName;
                hiddenInput.value = foodId;
                resultsDiv.style.display = 'none';
            });
        });
    }
});
