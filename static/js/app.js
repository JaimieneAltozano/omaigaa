// ==========================================================================
// FRASOTECA - BUSCADOR DE VIBRAS & ORADOR DE DEBATES (BAUHAUS INTERFACE)
// Conecta la interfaz web interactiva con la API REST Flask
// ==========================================================================

document.addEventListener('DOMContentLoaded', function () {

    // ---------- PESTAÑAS (BAUHAUS TABS) ----------

    var botones = document.querySelectorAll('.tab');

    botones.forEach(function (boton) {
        boton.addEventListener('click', function () {
            var modo = this.dataset.modo;
            cambiarPestana(modo);
        });
    });

    function cambiarPestana(modo) {
        var vibes = document.getElementById('panel-vibes');
        var debate = document.getElementById('panel-debate');

        if (modo === 'debate') {
            debate.classList.add('active');
            vibes.classList.remove('active');
        } else {
            vibes.classList.add('active');
            debate.classList.remove('active');
        }

        botones.forEach(function (btn) {
            btn.classList.toggle('active', btn.dataset.modo === modo);
        });
    }

    // ---------- UTILIDADES DE PETICIÓN ----------

    async function peticion(url, cuerpo) {
        var respuesta = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(cuerpo)
        });

        var datos = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(datos.error || 'Error interno en la respuesta del servidor');
        }

        return datos;
    }

    // ---------- BUSCADOR DE VIBRAS ----------

    var vibesForm = document.getElementById('vibes-form');
    var vibesConsulta = document.getElementById('consulta');
    var vibesResults = document.getElementById('vibes-results');
    var vibesLoading = document.getElementById('vibes-loading');
    var vibesError = document.getElementById('vibes-error');
    var vibesErrorText = document.getElementById('vibes-error-text');
    var vibesButton = vibesForm.querySelector('button[type="submit"]');

    vibesForm.addEventListener('submit', function (e) {
        e.preventDefault();

        var consulta = vibesConsulta.value.trim();

        if (!consulta) {
            mostrarError(vibesError, vibesErrorText, 'Por favor, escribe una emoción, situación o inquietud.');
            return;
        }

        ocultar(vibesError);
        ocultar(vibesResults);
        mostrar(vibesLoading);
        vibesButton.disabled = true;

        peticion('/api/search', { query: consulta })
            .then(function (datos) {
                vibesResults.innerHTML = '';

                var card = document.createElement('div');
                card.className = 'card';

                var titulo = document.createElement('h2');
                titulo.innerHTML = '<span>CITAS QUE CONECTAN CON TU SENTIR</span> <span class="badge-tag">TOP 3 MATCH</span>';
                card.appendChild(titulo);

                datos.results.forEach(function (resultado, index) {
                    var cita = document.createElement('div');
                    cita.className = 'quote';
                    cita.style.animationDelay = (index * 0.1) + 's';

                    var texto = document.createElement('div');
                    texto.className = 'text';
                    texto.textContent = '“' + resultado.phrase + '”';

                    var autor = document.createElement('div');
                    autor.className = 'author';
                    autor.textContent = '— ' + resultado.author;

                    var score = document.createElement('div');
                    score.className = 'score';
                    score.textContent = 'AFINIDAD SEMÁNTICA: ' + resultado.score_percent + '%';

                    cita.appendChild(texto);
                    cita.appendChild(autor);
                    cita.appendChild(score);
                    card.appendChild(cita);
                });

                var meta = document.createElement('div');
                meta.className = 'meta';
                meta.innerHTML = '<span>BASE: ' + datos.total_phrases + ' FRASES</span> ' +
                    '<span>TIEMPO: ' + datos.search_time_ms + ' MS</span> ' +
                    '<span>MÉTODO: SIMILITUD COSENO</span>';
                card.appendChild(meta);

                vibesResults.appendChild(card);
                mostrar(vibesResults);
            })
            .catch(function (error) {
                mostrarError(vibesError, vibesErrorText, error.message);
            })
            .finally(function () {
                ocultar(vibesLoading);
                vibesButton.disabled = false;
            });
    });

    // ---------- ORADOR DE DEBATES ----------

    var debateForm = document.getElementById('debate-form');
    var debatePregunta = document.getElementById('pregunta');
    var debateResults = document.getElementById('debate-results');
    var debateLoading = document.getElementById('debate-loading');
    var debateError = document.getElementById('debate-error');
    var debateErrorText = document.getElementById('debate-error-text');
    var debateButton = debateForm.querySelector('button[type="submit"]');

    debateForm.addEventListener('submit', function (e) {
        e.preventDefault();

        var pregunta = debatePregunta.value.trim();

        if (!pregunta) {
            mostrarError(debateError, debateErrorText, 'Por favor, escribe una pregunta filosófica o compleja.');
            return;
        }

        ocultar(debateError);
        ocultar(debateResults);
        mostrar(debateLoading);
        debateButton.disabled = true;

        peticion('/api/debate', { pregunta: pregunta })
            .then(function (datos) {
                debateResults.innerHTML = '';

                if (datos.success) {
                    var ensayoCard = document.createElement('div');
                    ensayoCard.className = 'card essay-wrapper';

                    var titulo = document.createElement('h2');
                    titulo.innerHTML = '<span>ENSAYO FILOSÓFICO EXPLICATIVO</span> <span class="badge-tag">RAG GROUNDED</span>';
                    ensayoCard.appendChild(titulo);

                    var essay = document.createElement('div');
                    essay.className = 'essay';

                    var parrafos = datos.answer.split(/\n\s*\n/);
                    parrafos.forEach(function (parrafo) {
                        if (!parrafo.trim()) return;
                        var p = document.createElement('p');
                        p.textContent = parrafo.trim();
                        essay.appendChild(p);
                    });

                    ensayoCard.appendChild(essay);

                    var meta = document.createElement('div');
                    meta.className = 'meta';
                    meta.innerHTML = '<span>ESTRUCTURA: ' + parrafos.length + ' PÁRRAFOS ANALÍTICOS</span> ' +
                        '<span>CITAS VERIFICADAS: SÍ</span>';
                    ensayoCard.appendChild(meta);

                    debateResults.appendChild(ensayoCard);
                } else {
                    var aviso = document.createElement('div');
                    aviso.className = 'notice';
                    aviso.textContent = '▲ ' + datos.answer;
                    debateResults.appendChild(aviso);
                }

                if (datos.sources && datos.sources.length > 0) {
                    var fuentesCard = document.createElement('div');
                    fuentesCard.className = 'card';

                    var tituloFuentes = document.createElement('h2');
                    tituloFuentes.innerHTML = '<span>FUENTES RECUPERADAS</span> <span class="badge-tag">' + datos.sources.length + ' CITAS</span>';
                    fuentesCard.appendChild(tituloFuentes);

                    datos.sources.forEach(function (fuente, index) {
                        var cita = document.createElement('div');
                        cita.className = 'quote';
                        cita.style.animationDelay = (index * 0.1) + 's';

                        var texto = document.createElement('div');
                        texto.className = 'text';
                        texto.textContent = '“' + fuente.text + '”';

                        var autor = document.createElement('div');
                        autor.className = 'author';
                        autor.textContent = '— ' + fuente.author;

                        var score = document.createElement('div');
                        score.className = 'score';
                        score.textContent = 'SIMILITUD COSENO: ' + fuente.score;

                        cita.appendChild(texto);
                        cita.appendChild(autor);
                        cita.appendChild(score);
                        fuentesCard.appendChild(cita);
                    });

                    debateResults.appendChild(fuentesCard);
                }

                mostrar(debateResults);
            })
            .catch(function (error) {
                mostrarError(debateError, debateErrorText, error.message);
            })
            .finally(function () {
                ocultar(debateLoading);
                debateButton.disabled = false;
            });
    });

    // ---------- AYUDANTES DE VISIBILIDAD ----------

    function mostrar(elemento) {
        elemento.classList.remove('hidden');
    }

    function ocultar(elemento) {
        elemento.classList.add('hidden');
    }

    function mostrarError(contenedor, texto, mensaje) {
        texto.textContent = '▲ ' + mensaje;
        mostrar(contenedor);
    }
});
