// ========================================
// FRASOTECA - Buscador de Vibras y Orador de Debates
// Conecta el frontend con la API del servidor Flask
// ========================================

document.addEventListener('DOMContentLoaded', function () {

    // ---------- Pestañas ----------

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

    // ---------- Utilidades ----------

    function escapar(texto) {
        var div = document.createElement('div');
        div.textContent = texto;
        return div.innerHTML;
    }

    async function peticion(url, cuerpo) {
        var respuesta = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(cuerpo)
        });

        var datos = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(datos.error || 'Error en la petición al servidor');
        }

        return datos;
    }

    // ---------- Buscador de Vibras ----------

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
            mostrarError(vibesError, vibesErrorText, 'Escribe una emoción, situación o pensamiento.');
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
                titulo.textContent = 'Frases que conectan con tu sentir';
                card.appendChild(titulo);

                datos.results.forEach(function (resultado) {
                    var cita = document.createElement('div');
                    cita.className = 'quote';

                    var texto = document.createElement('div');
                    texto.className = 'text';
                    texto.textContent = '“' + resultado.phrase + '”';

                    var autor = document.createElement('div');
                    autor.className = 'author';
                    autor.textContent = '— ' + resultado.author;

                    var score = document.createElement('div');
                    score.className = 'score';
                    score.textContent = 'Similitud semántica: ' + resultado.score_percent + '%';

                    cita.appendChild(texto);
                    cita.appendChild(autor);
                    cita.appendChild(score);
                    card.appendChild(cita);
                });

                var meta = document.createElement('div');
                meta.className = 'meta';
                meta.textContent = datos.total_phrases + ' frases en la base · ' +
                    datos.search_time_ms + ' ms · método: ' + datos.method;
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

    // ---------- Orador de Debates ----------

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
            mostrarError(debateError, debateErrorText, 'Escribe una pregunta filosófica o compleja.');
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
                    var ensayo = document.createElement('div');
                    ensayo.className = 'card';

                    var titulo = document.createElement('h2');
                    titulo.textContent = 'Mini-ensayo';
                    ensayo.appendChild(titulo);

                    var essay = document.createElement('div');
                    essay.className = 'essay';

                    datos.answer.split(/\n\s*\n/).forEach(function (parrafo) {
                        if (!parrafo.trim()) return;
                        var p = document.createElement('p');
                        p.textContent = parrafo.trim();
                        essay.appendChild(p);
                    });

                    ensayo.appendChild(essay);
                    debateResults.appendChild(ensayo);
                } else {
                    var aviso = document.createElement('div');
                    aviso.className = 'notice';
                    aviso.textContent = datos.answer;
                    debateResults.appendChild(aviso);
                }

                if (datos.sources && datos.sources.length > 0) {
                    var fuentes = document.createElement('div');
                    fuentes.className = 'card';

                    var tituloFuentes = document.createElement('h2');
                    tituloFuentes.textContent = 'Fuentes recuperadas';
                    fuentes.appendChild(tituloFuentes);

                    datos.sources.forEach(function (fuente) {
                        var cita = document.createElement('div');
                        cita.className = 'quote';

                        var texto = document.createElement('div');
                        texto.className = 'text';
                        texto.textContent = '“' + fuente.text + '”';

                        var autor = document.createElement('div');
                        autor.className = 'author';
                        autor.textContent = '— ' + fuente.author;

                        var score = document.createElement('div');
                        score.className = 'score';
                        score.textContent = 'Similitud semántica: ' + fuente.score;

                        cita.appendChild(texto);
                        cita.appendChild(autor);
                        cita.appendChild(score);
                        fuentes.appendChild(cita);
                    });

                    debateResults.appendChild(fuentes);
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

    // ---------- Ayudantes de visibilidad ----------

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
