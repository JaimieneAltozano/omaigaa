#!/usr/bin/env python3
"""
Servidor Flask - Motor de Búsqueda Semántica (Interestelar)
============================================================

Servidor web que conecta el motor de búsqueda semántica local
(sin IA) con la interfaz web inspirada en Interestelar.

Rutas:
- GET  /             → Página principal (HTML)
- GET  /api/health   → Estado del servicio (JSON)
- POST /api/search   → Endpoint de búsqueda (JSON)

Configuración por variables de entorno:
- HOST        → Interfaz a escuchar (default: 0.0.0.0)
- PORT        → Puerto (default: 5000)
- FLASK_DEBUG → "1" habilita el modo debug (default: "0")
- MODEL_NAME  → Modelo sentence-transformers (default: all-MiniLM-L6-v2)

Tecnología:
- Flask (servidor web)
- sentence-transformers (embeddings locales)
- scikit-learn (similitud coseno)

Autor: Manus AI
Versión: 1.1.0
"""

import json
import logging
import os
import sys
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from semantic_search_local import LocalSemanticSearchEngine


# Forzar consola UTF-8 (evita caracteres corruptos en Windows)
for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8")
    except Exception:
        pass


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Configuración desde variables de entorno
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "5000"))
DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
MODEL_NAME = os.getenv("MODEL_NAME", "all-MiniLM-L6-v2")


# Inicializar Flask
app = Flask(__name__)


def create_search_engine() -> LocalSemanticSearchEngine:
    """Crea el motor de búsqueda semántica con manejo de errores claro."""
    logger.info("Inicializando motor de búsqueda semántica local...")
    try:
        engine = LocalSemanticSearchEngine(model_name=MODEL_NAME)
    except Exception as e:
        logger.error(f"✗ Error inicializando el motor: {e}")
        logger.error(
            "Verifica que existen 'frases.json' y 'embeddings.npy' "
            "(genera este último con: python generate_embeddings.py) "
            "y que hay conexión a internet la primera vez (descarga del modelo)."
        )
        raise
    logger.info("✓ Motor listo")
    return engine


# Motor de búsqueda (se carga una sola vez al iniciar)
search_engine = create_search_engine()


@app.route('/')
def index():
    """Página principal con interfaz Interestelar."""
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health():
    """Endpoint de estado del servicio."""
    return jsonify({
        "status": "ok",
        "model": MODEL_NAME,
        "total_phrases": len(search_engine.phrases),
        "method": "cosine_similarity",
        "ai_used": False
    }), 200


@app.route('/api/search', methods=['POST'])
def search():
    """
    Endpoint de búsqueda semántica.
    
    Recibe una consulta y devuelve las 3 frases más similares
    usando embeddings locales y similitud coseno (sin IA).
    """
    try:
        # Obtener datos del request
        data = request.get_json(silent=True)
        
        if not data or 'query' not in data:
            return jsonify({
                "error": "No se proporcionó una consulta"
            }), 400
        
        query = data['query'].strip()
        
        if not query:
            return jsonify({
                "error": "La consulta no puede estar vacía"
            }), 400
        
        # Realizar búsqueda
        results = search_engine.search_with_scores(query, top_k=3)
        
        # Devolver resultados
        return jsonify(results), 200
        
    except Exception as e:
        logger.error(f"✗ Error en búsqueda: {e}", exc_info=True)
        return jsonify({
            "error": f"Error interno: {str(e)}"
        }), 500


if __name__ == '__main__':
    logger.info("\n" + "="*70)
    logger.info("🚀 SERVIDOR FLASK - INTERESTELAR")
    logger.info("="*70)
    logger.info(f"📍 URL: http://localhost:{PORT}")
    logger.info(f"🔧 Debug: {DEBUG}")
    logger.info(f"🌐 Host: {HOST}")
    logger.info("="*70 + "\n")
    
    app.run(
        host=HOST,
        port=PORT,
        debug=DEBUG
    )
