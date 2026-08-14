#!/usr/bin/env python3
"""
Motor de Búsqueda Semántica Local (Sin IA)
===========================================

Este motor de búsqueda usa embeddings locales generados por
sentence-transformers y similitud coseno para encontrar las frases
más relevantes SIN usar IA, APIs externas ni palabras clave.

**Características:**
- ✅ Sin IA/API (todo local)
- ✅ Embeddings semánticos multilingües (paraphrase-multilingual-MiniLM-L12-v2)
- ✅ Similitud coseno para matching
- ✅ Búsqueda rápida (milisegundos)
- ✅ Sin dependencias de internet

**Arquitectura:**
1. Cargar embeddings pre-generados (embeddings.npy)
2. Generar embedding para la consulta del usuario
3. Calcular similitud coseno con todas las frases
4. Ordenar por similitud y devolver top 3

Autor: Manus AI
Versión: 1.0.0
"""

import json
import logging
import time
from pathlib import Path
from typing import Optional

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Directorio base = ubicación de este archivo (independiente del CWD)
BASE_DIR = Path(__file__).resolve().parent


class LocalSemanticSearchEngine:
    """
    Motor de búsqueda semántica local usando embeddings y similitud coseno.
    
    No usa IA ni APIs externas. Todo el procesamiento es local.
    """

    def __init__(
        self,
        phrases_file: Optional[str] = None,
        embeddings_file: Optional[str] = None,
        metadata_file: Optional[str] = None,
        model_name: str = "paraphrase-multilingual-MiniLM-L12-v2",
        top_k: int = 3
    ):
        """
        Inicializa el motor de búsqueda semántica local.
        
        Args:
            phrases_file (str, optional): Ruta al archivo JSON con las frases.
                Si es None, usa "<directorio del módulo>/frases.json".
            embeddings_file (str, optional): Ruta al archivo NumPy con embeddings.
                Si es None, usa "<directorio del módulo>/embeddings.npy".
            metadata_file (str, optional): Ruta al archivo JSON con metadata.
                Si es None, usa "<directorio del módulo>/embeddings_metadata.json".
            model_name (str): Nombre del modelo sentence-transformers.
            top_k (int): Número de resultados a devolver.
        """
        self.phrases_file = Path(phrases_file) if phrases_file else BASE_DIR / "frases.json"
        self.embeddings_file = Path(embeddings_file) if embeddings_file else BASE_DIR / "embeddings.npy"
        self.metadata_file = Path(metadata_file) if metadata_file else BASE_DIR / "embeddings_metadata.json"
        self.model_name = model_name
        self.top_k = top_k
        
        # Cargar datos
        self.phrases = self._load_phrases()

        # Cargar modelo (necesario para generar embeddings de consultas)
        logger.info("Cargando modelo sentence-transformers...")
        self.model = SentenceTransformer(model_name)

        # Cargar (o regenerar) embeddings usando el modelo cargado
        self.embeddings = self._load_embeddings()
        logger.info(f"✓ Motor local inicializado: {len(self.phrases)} frases")

    def _load_phrases(self) -> list[dict]:
        """Carga las frases desde el archivo JSON."""
        try:
            with open(self.phrases_file, encoding="utf-8") as f:
                phrases = json.load(f)
            
            if not isinstance(phrases, list):
                raise ValueError("El archivo debe contener una lista")
            
            logger.info(f"✓ Frases cargadas: {len(phrases)}")
            return phrases
            
        except FileNotFoundError:
            logger.error(f"✗ Archivo no encontrado: {self.phrases_file}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"✗ JSON inválido: {e}")
            raise
        except Exception as e:
            logger.error(f"✗ Error cargando frases: {e}")
            raise

    def _load_embeddings(self) -> np.ndarray:
        """Carga los embeddings pre-generados (o los regenera si no coinciden)."""
        dimension = self._model_dimension()

        try:
            embeddings = np.load(self.embeddings_file)

            if (
                embeddings.ndim == 2
                and embeddings.shape[1] == dimension
                and embeddings.shape[0] == len(self.phrases)
            ):
                logger.info(f"✓ Embeddings cargados: {embeddings.shape}")
                return embeddings

        except FileNotFoundError:
            logger.info("✗ Embeddings no encontrados, se generarán nuevos.")
        except Exception as e:
            logger.warning(f"⚠ Embeddings no utilizables ({e}), se regenerarán.")

        # Si no existen embeddings compatibles, los generamos ahora.
        logger.info("Generando embeddings para las frases...")
        textos = [
            f"{p['phrase']} - {p['author']}"
            for p in self.phrases
        ]

        embeddings = self.model.encode(
            textos,
            convert_to_numpy=True
        )

        np.save(self.embeddings_file, embeddings)
        logger.info(f"✓ Embeddings generados: {embeddings.shape}")
        return embeddings

    def _model_dimension(self) -> int:
        """Devuelve la dimensión del embedding del modelo cargado."""
        metodo = getattr(self.model, "get_embedding_dimension", None)

        if metodo is not None:
            return metodo()

        return self.model.get_sentence_embedding_dimension()

    def search(self, query: str, top_k: Optional[int] = None) -> list[dict]:
        """
        Busca las frases más similares semánticamente a la consulta.
        
        Usa similitud coseno entre el embedding de la consulta y los
        embeddings de las frases. NO usa IA ni palabras clave.
        
        Args:
            query (str): Consulta del usuario (emoción, situación, pensamiento).
            top_k (int, optional): Número de resultados. Usa el default si es None.
        
        Returns:
            list[dict]: Lista de frases ordenadas por similitud, cada una con:
                - phrase (str): Texto de la frase
                - author (str): Autor de la frase
                - similarity (float): Similitud coseno (0.0 a 1.0)
                - score_percent (float): Similitud en porcentaje
        
        Raises:
            ValueError: Si la consulta está vacía.
            Exception: Si falla el cálculo de embeddings.
        """
        if not query.strip():
            raise ValueError("La consulta no puede estar vacía")
        
        if top_k is None:
            top_k = self.top_k
        
        start_time = time.time()
        
        logger.info(f"\n{'='*60}")
        logger.info(f"CONSULTA: '{query}'")
        logger.info(f"{'='*60}")
        
        # Generar embedding para la consulta
        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True
        )
        
        # Calcular similitud coseno con todas las frases
        similarities = cosine_similarity(
            query_embedding,
            self.embeddings
        )[0]
        
        # Ordenar por similitud (descendente)
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Construir resultados
        results = []
        for idx in top_indices:
            phrase_data = self.phrases[idx]
            similarity = float(similarities[idx])
            
            results.append({
                "phrase": phrase_data["phrase"],
                "author": phrase_data["author"],
                "similarity": similarity,
                "score_percent": round(similarity * 100, 2)
            })
        
        elapsed = time.time() - start_time
        logger.info(f"✓ Búsqueda completada en {elapsed:.3f} segundos")
        logger.info(f"✓ Top {len(results)} resultados:")
        
        for i, result in enumerate(results, 1):
            logger.info(f"  {i}. \"{result['phrase'][:60]}...\" -- {result['author']} ({result['score_percent']}%)")
        
        return results

    def search_with_scores(self, query: str, top_k: int = 3) -> dict:
        """
        Busca y devuelve resultados con información adicional.
        
        Returns:
            dict: Diccionario con:
                - query (str): Consulta original
                - results (list): Resultados de búsqueda
                - total_phrases (int): Total de frases en la base
                - search_time_ms (float): Tiempo de búsqueda en milisegundos
                - model (str): Modelo utilizado
        """
        start_time = time.time()
        results = self.search(query, top_k)
        elapsed_ms = (time.time() - start_time) * 1000
        
        return {
            "query": query,
            "results": results,
            "total_phrases": len(self.phrases),
            "search_time_ms": round(elapsed_ms, 2),
            "model": self.model_name,
            "method": "cosine_similarity",
            "ai_used": False
        }


def main():
    """Función principal para ejecutar el motor de búsqueda."""
    try:
        # Inicializar motor
        engine = LocalSemanticSearchEngine()
        
        # Ejemplos de consultas
        examples = [
            "Siento que el tiempo pasa muy rápido y no estoy logrando mis metas",
            "La sensación de paz al mirar la lluvia",
            "Necesito motivación para enfrentar un desafío difícil"
        ]
        
        print("\n" + "="*70)
        print("MOTOR DE BÚSQUEDA SEMÁNTICA LOCAL (SIN IA)")
        print("="*70)
        
        # Ejecutar ejemplos
        for i, query in enumerate(examples, 1):
            print(f"\n{'─'*70}")
            print(f"\nEJEMPLO {i}: '{query}'\n")
            
            results = engine.search(query)
            
            print("Resultados:")
            for j, result in enumerate(results, 1):
                print(f"\n  {j}. \"{result['phrase']}\"")
                print(f"     -- {result['author']}")
                print(f"     📊 Similitud: {result['score_percent']}%")
        
        # Modo interactivo
        print("\n" + "="*70)
        print("MODO INTERACTIVO")
        print("="*70)
        print("\nIngresa tu consulta (o 'salir' para terminar):\n")
        
        while True:
            try:
                query = input("\n💭 Tu consulta: ").strip()
                
                if query.lower() in ["salir", "exit", "quit"]:
                    print("\n✓ Saliendo del motor de búsqueda...")
                    break
                
                if not query:
                    print("⚠ La consulta no puede estar vacía")
                    continue
                
                results = engine.search(query)
                
                print("\n📚 Las 3 frases más similares semánticamente:")
                for i, result in enumerate(results, 1):
                    print(f"\n  {i}. \"{result['phrase']}\"")
                    print(f"     -- {result['author']}")
                    print(f"     📊 Similitud: {result['score_percent']}%")
                
            except KeyboardInterrupt:
                print("\n\n✓ Saliendo...")
                break
            except Exception as e:
                logger.error(f"✗ Error: {e}")
                print(f"✗ Error: {e}")
        
        return 0
        
    except Exception as e:
        logger.error(f"✗ Error fatal: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
