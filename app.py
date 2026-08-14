#!/usr/bin/env python3
"""
Servidor Flask - Buscador de Vibras + Orador de Debates
=========================================================

Unifica los dos motores del proyecto:

1. Buscador de "Vibras" o Emociones
   Analiza la intención de una frase (emoción, situación o pensamiento)
   y devuelve las 3 citas que mejor conectan, sin usar palabras clave.
   Implementación local: embeddings multilingües + similitud coseno.

2. Orador de Debates Respaldado
   Dada una pregunta compleja, recupera las frases relacionadas y redacta
   un mini-ensayo de dos párrafos que cita textualmente esas fuentes.
   Recuperación semántica local + generación (OpenAI o plantilla local).

Rutas:
- GET  /             → Página principal (HTML)
- GET  /api/health   → Estado del servicio (JSON)
- POST /api/search   → Buscador de vibras (JSON)
- POST /api/debate   → Orador de debates (JSON)

Configuración por variables de entorno:
- HOST → Interfaz a escuchar (default: 127.0.0.1)
- PORT → Puerto (default: 5000)
"""

import os

from flask import Flask, jsonify, render_template, request

from polemista import MODEL_NAME, Polemista
from semantic_search_local import LocalSemanticSearchEngine


HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "5000"))
TOP_K = 3

app = Flask(__name__)

buscador = LocalSemanticSearchEngine(top_k=TOP_K)
polemista = Polemista()


# -------------------------------------------------------------
# VISTA PRINCIPAL
# -------------------------------------------------------------

@app.route("/", methods=["GET"])
def index():
    """Página principal. El frontend consume las APIs JSON con JavaScript."""
    return render_template("index.html")


# -------------------------------------------------------------
# API
# -------------------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health():
    """Estado del servicio."""
    return jsonify({
        "status": "ok",
        "model": MODEL_NAME,
        "total_phrases": len(buscador.phrases),
        "method": "cosine_similarity",
        "ai_used": False
    }), 200


@app.route("/api/search", methods=["POST"])
def api_search():
    """
    Buscador de "Vibras": devuelve las 3 citas que mejor conectan
    con la emoción, situación o pensamiento descrito.
    """
    data = request.get_json(silent=True)

    if not data or not data.get("query"):
        return jsonify({
            "error": "No se proporcionó una consulta"
        }), 400

    consulta = data["query"].strip()

    if not consulta:
        return jsonify({
            "error": "La consulta no puede estar vacía"
        }), 400

    try:
        resultado = buscador.search_with_scores(consulta, top_k=TOP_K)
        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({
            "error": f"Error interno: {str(e)}"
        }), 500


@app.route("/api/debate", methods=["POST"])
def api_debate():
    """
    Orador de Debates: redacta un mini-ensayo de dos párrafos
    condicionado a citar las frases recuperadas de la base de datos.
    """
    data = request.get_json(silent=True)

    if not data or not data.get("pregunta"):
        return jsonify({
            "error": "No se proporcionó una pregunta"
        }), 400

    pregunta = data["pregunta"].strip()

    if not pregunta:
        return jsonify({
            "error": "La pregunta no puede estar vacía"
        }), 400

    try:
        resultado = polemista.generar_debate(pregunta)
        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({
            "error": f"Error interno: {str(e)}"
        }), 500


if __name__ == "__main__":
    app.run(
        host=HOST,
        port=PORT,
        debug=True
    )
