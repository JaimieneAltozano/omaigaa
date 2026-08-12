#!/usr/bin/env python3
"""
Generador de Embeddings Locales para Frases Inspiracionales
============================================================

Este script genera embeddings semánticos para las 100 frases usando
sentence-transformers (modelo local, sin IA/API) y los guarda
en un archivo NumPy para búsqueda rápida.

Modelo: all-MiniLM-L6-v2 (384 dimensiones, rápido y eficiente)

Autor: Manus AI
Versión: 1.0.0
"""

import json
import sys
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


# Directorio base = ubicación de este archivo (independiente del CWD)
BASE_DIR = Path(__file__).resolve().parent


def main():
    """Genera embeddings para todas las frases."""
    # Forzar consola UTF-8 (evita caracteres corruptos en Windows)
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass

    phrases_file = BASE_DIR / "frases.json"
    output_file = BASE_DIR / "embeddings.npy"
    metadata_file = BASE_DIR / "embeddings_metadata.json"

    print("\n" + "="*70)
    print("GENERANDO EMBEDDINGS SEMÁNTICOS LOCALES")
    print("="*70)
    
    # Cargar frases
    print("\n[1/3] Cargando frases desde frases.json...")
    with open(phrases_file, encoding="utf-8") as f:
        phrases = json.load(f)
    
    print(f"  ✓ {len(phrases)} frases cargadas")
    
    # Cargar modelo
    print("\n[2/3] Cargando modelo sentence-transformers...")
    print("  Modelo: all-MiniLM-L6-v2")
    print("  Dimensiones: 384")
    print("  Descargando primera vez (puede tardar)...")
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("  ✓ Modelo cargado")
    
    # Generar embeddings
    print("\n[3/3] Generando embeddings para las frases...")
    texts = [f"{p['phrase']} - {p['author']}" for p in phrases]
    
    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        convert_to_numpy=True
    )
    
    print(f"  ✓ Embeddings generados: {embeddings.shape}")
    
    # Guardar embeddings
    np.save(output_file, embeddings)
    print(f"  ✓ Embeddings guardados en: {output_file}")
    
    # Guardar metadata
    metadata = {
        "model": "all-MiniLM-L6-v2",
        "dimensions": embeddings.shape[1],
        "num_phrases": len(phrases),
        "phrases": phrases
    }
    
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"  ✓ Metadata guardada en: {metadata_file}")
    
    # Mostrar ejemplo
    print("\n" + "="*70)
    print("EJEMPLO DE EMBEDDING (primera frase):")
    print("="*70)
    print(f"Frase: \"{phrases[0]['phrase']}\"")
    print(f"Autor: {phrases[0]['author']}")
    print(f"Vector: {embeddings[0][:10]}... ({embeddings.shape[1]} dimensiones)")
    
    print("\n" + "="*70)
    print("✓ GENERACIÓN COMPLETADA")
    print("="*70)
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
