// ========================================
// INTERESTELAR - Motor de Búsqueda Semántica
// JavaScript para interactividad
// ========================================

document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const queryInput = document.getElementById('query');
    const searchBtn = document.getElementById('search-btn');
    const resultsSection = document.getElementById('results-section');
    const resultsContainer = document.getElementById('results-container');
    const loadingSection = document.getElementById('loading');
    const errorSection = document.getElementById('error-section');
    const errorText = errorSection.querySelector('.error-text');
    const searchTimeSpan = document.getElementById('search-time');
    const totalPhrasesSpan = document.getElementById('total-phrases');
    const exampleBtns = document.querySelectorAll('.example-btn');

    // Función para realizar la búsqueda
    async function performSearch() {
        const query = queryInput.value.trim();
        
        if (!query) {
            showError('Por favor, ingresa una consulta.');
            return;
        }

        // Ocultar secciones previas
        resultsSection.classList.add('hidden');
        errorSection.classList.add('hidden');
        
        // Mostrar loading
        loadingSection.classList.remove('hidden');

        try {
            // Hacer petición al servidor Flask
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: query })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Error en la búsqueda');
            }

            // Ocultar loading
            loadingSection.classList.add('hidden');

            // Mostrar resultados
            displayResults(data);

        } catch (error) {
            loadingSection.classList.add('hidden');
            showError(error.message);
        }
    }

    // Función para mostrar resultados
    function displayResults(data) {
        resultsContainer.innerHTML = '';

        // Actualizar metadata
        searchTimeSpan.textContent = `⏱️ ${data.search_time_ms} ms`;
        totalPhrasesSpan.textContent = `📚 ${data.total_phrases} frases`;

        // Crear tarjetas de resultados
        data.results.forEach((result, index) => {
            const card = document.createElement('div');
            card.className = 'result-card';
            card.style.animationDelay = `${index * 0.1}s`;

            card.innerHTML = `
                <div class="result-number">${index + 1}</div>
                <p class="result-quote">"${result.phrase}"</p>
                <p class="result-author">— ${result.author}</p>
                <span class="result-score">📊 Similitud: ${result.score_percent}%</span>
            `;

            resultsContainer.appendChild(card);
        });

        // Mostrar sección de resultados
        resultsSection.classList.remove('hidden');

        // Scroll suave a los resultados
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // Función para mostrar errores
    function showError(message) {
        errorText.textContent = `❌ ${message}`;
        errorSection.classList.remove('hidden');
    }

    // Event listeners
    searchBtn.addEventListener('click', performSearch);

    queryInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            performSearch();
        }
    });

    // Botones de ejemplos
    exampleBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const query = this.getAttribute('data-query');
            queryInput.value = query;
            performSearch();
        });
    });

    // Focus inicial en el input
    queryInput.focus();
});
