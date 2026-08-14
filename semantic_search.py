#!/usr/bin/env python3
"""
Motor de Búsqueda Semántica para Frases Inspiracionales
========================================================

Este sistema implementa un motor de búsqueda que analiza la intención
emocional y semántica de una consulta, devolviendo las 3 frases más
relevantes de la base de datos SIN usar búsqueda por palabras clave.

**Arquitectura:**
- Usa un LLM (OpenAI, p. ej. gpt-4o-mini) para analizar la intención semántica
- El LLM compara la consulta emocional con todas las frases
- Devuelve el top 3 con explicación de por qué cada frase conecta
- No depende de palabras clave compartidas

**Características:**
- Búsqueda semántica (no por palabras clave)
- Análisis de emociones, situaciones y pensamientos abstractos
- Explicaciones de por qué cada frase conecta
- Logging estructurado

**Ejemplos de uso:**
- "Siento que el tiempo pasa muy rápido y no estoy logrando mis metas"
- "La sensación de paz al mirar la lluvia"
- "Necesito motivación para enfrentar un desafío difícil"

Autor: Manus AI
Versión: 1.0.0
"""

import json
import logging
from pathlib import Path
from typing import Optional

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SemanticSearchEngine:
    """
    Motor de búsqueda semántica para frases inspiracionales.
    
    Usa un LLM para analizar la intención emocional y semántica de las consultas,
    devolviendo las frases más relevantes con explicaciones de conexión.
    """

    def __init__(
        self,
        phrases_file: str = "frases.json",
        model: str = "gpt-4o-mini",
        top_k: int = 3,
        client: Optional[object] = None,
    ):
        """
        Inicializa el motor de búsqueda semántica.
        
        Args:
            phrases_file (str): Ruta al archivo JSON con las frases.
            model (str): Modelo LLM para análisis semántico.
            top_k (int): Número de frases a devolver.
        """
        self.phrases_file = Path(phrases_file)
        self.model = model
        self.top_k = top_k
        
        # Inicializar cliente OpenAI (se puede inyectar un cliente para pruebas)
        if client is not None:
            self.client = client
        else:
            if OpenAI is None:
                raise ImportError(
                    "openai package is not installed. Install it or pass a client instance to SemanticSearchEngine(client=...)"
                )
            self.client = OpenAI()
        
        # Cargar frases
        self.phrases = self._load_phrases()
        
        logger.info(f"✓ Motor inicializado: {len(self.phrases)} frases")

    def _load_phrases(self) -> list[dict]:
        """Carga las frases desde el archivo JSON."""
        try:
            with open(self.phrases_file, encoding="utf-8") as f:
                phrases = json.load(f)
            
            if not isinstance(phrases, list):
                raise ValueError("El archivo debe contener una lista")
            
            if len(phrases) == 0:
                raise ValueError("El archivo está vacío")
            
            # Validar estructura
            for i, phrase in enumerate(phrases):
                if not isinstance(phrase, dict):
                    raise ValueError(f"Elemento {i} no es diccionario")
                if "author" not in phrase or "phrase" not in phrase:
                    raise ValueError(f"Elemento {i} falta campos")
            
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

    def search(self, query: str, top_k: Optional[int] = None) -> list[dict]:
        """
        Busca las frases más relevantes para una consulta semántica.
        
        Analiza la intención emocional y semántica de la consulta usando un LLM,
        devolviendo las frases más similares SIN usar palabras clave.
        
        Args:
            query (str): Consulta del usuario (emoción, situación, pensamiento).
            top_k (int, optional): Número de resultados. Usa el default si es None.
        
        Returns:
            list[dict]: Lista de frases ordenadas por relevancia, cada una con:
                - author (str): Autor de la frase
                - phrase (str): Texto de la frase
                - relevance (str): Explicación de por qué conecta
        
        Raises:
            ValueError: Si la consulta está vacía.
            Exception: Si falla el análisis semántico.
        """
        if not query.strip():
            raise ValueError("La consulta no puede estar vacía")
        
        if top_k is None:
            top_k = self.top_k
        
        logger.info(f"\n{'='*60}")
        logger.info(f"CONSULTA: '{query}'")
        logger.info(f"{'='*60}")
        
        # Preparar contexto con todas las frases
        phrases_context = "\n".join([
            f"{i+1}. \"{p['phrase']}\" -- {p['author']}"
            for i, p in enumerate(self.phrases)
        ])
        
        # Crear prompt para el LLM
        system_prompt = """Eres un experto en psicología positiva y citas inspiracionales.
Tu tarea es analizar la intención emocional y semántica de una consulta del usuario
y seleccionar las frases que mejor conecten con ese sentimiento o situación.

IMPORTANTE:
- NO uses búsqueda por palabras clave
- Analiza la EMOCIÓN, SITUACIÓN o PENSAMIENTO subyacente
- Las frases pueden no compartir NINGUNA palabra con la consulta
- Busca la CONEXIÓN EMOCIONAL y SEMÁNTICA más profunda
- Considera el contexto, el significado, y el consejo implícito

Devuelve EXACTAMENTE {top_k} frases de la base de datos con explicación de por qué conectan."""

        user_prompt = f"""Consulta del usuario: "{query}"

Analiza la intención emocional y semántica de esta consulta, y selecciona las {top_k} frases
de la siguiente base de datos que mejor conecten con el sentimiento, situación o necesidad
expresada, incluso si no comparten palabras en común.

Base de datos de frases:
{phrases_context}

Devuelve EXACTAMENTE {top_k} frases con este formato:

1. "FRASE" — Autor
   💡 Por qué conecta: explicación

2. "FRASE" — Autor
   💡 Por qué conecta: explicación

3. "FRASE" — Autor
   💡 Por qué conecta: explicación

Las frases deben ser EXACTAMENTE las de la base de datos, sin modificaciones."""

        try:
            # Llamar al LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt.format(top_k=top_k)},
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            # Parsear respuesta
            content = response.choices[0].message.content
            
            # Extraer frases usando parsing simple
            results = self._parse_results(content, top_k)
            
            return results
            
        except Exception as e:
            logger.error(f"✗ Error en búsqueda semántica: {e}")
            raise

    def _parse_results(self, content: str, top_k: int) -> list[dict]:
        """Parsea la respuesta del LLM para extraer las frases y explicaciones."""
        import re
        
        results = []
        
        # Patrón simple: buscar frases numeradas con comillas
        # Formato esperado: 1. "FRASE" — Autor
        pattern = r'(\d+)\.\s*"(.*?)"\s*[—\-–]\s*([^\n]+)'
        
        matches = re.findall(pattern, content)
        
        for match in matches:
            if len(results) >= top_k:
                break
            
            phrase = match[1].strip()
            author = match[2].strip()
            
            results.append({
                "phrase": phrase,
                "author": author,
                "relevance": "Ver explicación en el contexto"
            })
        
        # Si no encontramos suficientes, buscar citas con >
        if len(results) < top_k:
            pattern_quote = r'>\s*\*?"([^"]+?)"\*?\s*\n>?\s*[—\-–]\s*([^\n]+)'
            matches_quote = re.findall(pattern_quote, content)
            for match in matches_quote:
                if len(results) >= top_k:
                    break
                results.append({
                    "phrase": match[0].strip(),
                    "author": match[1].strip(),
                    "relevance": "Ver explicación en el contexto"
                })
        
        # Si no encontramos nada, devolver la respuesta completa como texto
        if len(results) == 0:
            return [{"phrase": content, "author": "LLM", "relevance": "Respuesta completa"}]
        
        return results[:top_k]


def main():
    """Función principal para ejecutar el motor de búsqueda."""
    try:
        # Inicializar motor
        engine = SemanticSearchEngine()
        
        # Ejemplos de consultas
        examples = [
            "Siento que el tiempo pasa muy rápido y no estoy logrando mis metas",
            "La sensación de paz al mirar la lluvia",
            "Necesito motivación para enfrentar un desafío difícil"
        ]
        
        print("\n" + "="*70)
        print("MOTOR DE BÚSQUEDA SEMÁNTICA - FRASES INSPIRACIONALES")
        print("="*70)
        
        # Ejecutar ejemplos
        for i, query in enumerate(examples, 1):
            print(f"\n{'─'*70}")
            print(f"\nEJEMPLO {i}: '{query}'\n")
            
            # Llamar directamente y mostrar respuesta formateada
            results = engine.search(query)
            
            # Mostrar resultados
            if len(results) == 1 and results[0]["author"] == "LLM":
                print(results[0]["phrase"])
            else:
                print("Resultados:")
                for j, result in enumerate(results, 1):
                    print(f"\n  {j}. \"{result['phrase']}\"")
                    print(f"     -- {result['author']}")
        
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
                
                if len(results) == 1 and results[0]["author"] == "LLM":
                    print("\n" + results[0]["phrase"])
                else:
                    print("\n📚 Las 3 frases que mejor conectan con tu sentimiento:")
                    for i, result in enumerate(results, 1):
                        print(f"\n  {i}. \"{result['phrase']}\"")
                        print(f"     -- {result['author']}")
                
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
