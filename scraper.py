#!/usr/bin/env python3
"""
Web Scraper de Frases Inspiracionales
=====================================

Este módulo extrae frases inspiracionales del sitio quotes.toscrape.com
usando requests y BeautifulSoup. Proporciona funciones para:
- Extraer frases de múltiples páginas
- Guardar datos en formato JSON
- Manejar errores de red y validación

Autor: Manus AI
Versión: 1.0.0
Requisitos: requests>=2.34.0, beautifulsoup4>=4.15.0
"""

import json
import logging
import sys
from typing import Optional
from pathlib import Path

import requests
from bs4 import BeautifulSoup


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class QuoteScraper:
    """Extractor de frases del sitio quotes.toscrape.com."""

    BASE_URL = "https://quotes.toscrape.com"
    TIMEOUT = 10
    QUOTE_SELECTOR = ".quote"
    TEXT_SELECTOR = ".text"
    AUTHOR_SELECTOR = ".author"

    # Caracteres tipográficos a eliminar
    QUOTE_CHARS = {"\u201c": "", "\u201d": ""}  # Comillas tipográficas

    def __init__(self, timeout: int = TIMEOUT):
        """
        Inicializa el scraper.

        Args:
            timeout (int): Tiempo máximo de espera para cada petición HTTP (segundos).
        """
        self.timeout = timeout
        self.session = requests.Session()

    def extract_phrases(self, max_pages: Optional[int] = None) -> list[dict]:
        """
        Extrae todas las frases del sitio quotes.toscrape.com.

        Recorre la paginación del sitio (10 páginas con 10 frases cada una,
        en total 100 citas) y devuelve una lista de diccionarios con
        la estructura {"author": str, "phrase": str}.

        Args:
            max_pages (int, optional): Límite de seguridad de páginas a consultar.
                Si es None, se extraen todas las páginas disponibles.
                Por defecto, el sitio tiene exactamente 10 páginas.

        Returns:
            list[dict]: Lista con diccionarios de la forma
                {"author": str, "phrase": str} para cada cita.

        Raises:
            requests.exceptions.HTTPError: Si alguna página responde con
                un código de error HTTP.
            requests.exceptions.RequestException: Si falla la conexión.
            ValueError: Si el HTML no contiene la estructura esperada.
        """
        phrases = []
        page_number = 1

        logger.info("Iniciando extracción de frases...")

        while max_pages is None or page_number <= max_pages:
            try:
                url = f"{self.BASE_URL}/page/{page_number}/"
                logger.debug(f"Descargando página {page_number}: {url}")

                # 1) Petición HTTP a la página
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()

                # 2) Parseo del HTML
                soup = BeautifulSoup(response.text, "html.parser")

                # 3) Buscar todos los bloques de cita (clase CSS "quote")
                quote_blocks = soup.select(self.QUOTE_SELECTOR)

                # 4) Si la página no tiene citas, hemos llegado al final
                if not quote_blocks:
                    logger.info(f"Fin de la paginación en página {page_number}")
                    break

                # 5) Extraer frase y autor de cada bloque
                for block in quote_blocks:
                    try:
                        # Frase: elimina caracteres tipográficos
                        text_elem = block.select_one(self.TEXT_SELECTOR)
                        if not text_elem:
                            logger.warning(f"Bloque sin texto en página {page_number}")
                            continue

                        raw_phrase = text_elem.get_text()
                        phrase = raw_phrase
                        for char, replacement in self.QUOTE_CHARS.items():
                            phrase = phrase.replace(char, replacement)

                        # Autor
                        author_elem = block.select_one(self.AUTHOR_SELECTOR)
                        if not author_elem:
                            logger.warning(f"Bloque sin autor en página {page_number}")
                            continue

                        author = author_elem.get_text()

                        phrases.append({"author": author, "phrase": phrase})

                    except Exception as e:
                        logger.error(f"Error extrayendo bloque en página {page_number}: {e}")
                        continue

                logger.info(f"✓ Página {page_number}: {len(quote_blocks)} frases extraídas")
                page_number += 1

            except requests.exceptions.RequestException as e:
                logger.error(f"Error de conexión en página {page_number}: {e}")
                raise

        logger.info(f"Extracción completada: {len(phrases)} frases totales")
        return phrases

    def save_to_json(
        self,
        phrases: list[dict],
        output_path: str = "frases.json",
        ensure_ascii: bool = False,
        indent: int = 2
    ) -> None:
        """
        Guarda las frases en un archivo JSON.

        Args:
            phrases (list[dict]): Lista de frases a guardar.
            output_path (str): Ruta del archivo de salida.
            ensure_ascii (bool): Si False, permite caracteres Unicode directos.
            indent (int): Espacios de indentación en el JSON.

        Raises:
            IOError: Si hay error al escribir el archivo.
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(phrases, f, ensure_ascii=ensure_ascii, indent=indent)

            logger.info(f"✓ Archivo guardado: {output_path} ({len(phrases)} frases)")

        except IOError as e:
            logger.error(f"Error al guardar archivo: {e}")
            raise

    def close(self) -> None:
        """Cierra la sesión HTTP."""
        self.session.close()
        logger.debug("Sesión HTTP cerrada")


def main():
    """Función principal para ejecutar el scraper desde línea de comandos."""
    try:
        scraper = QuoteScraper()
        phrases = scraper.extract_phrases()
        scraper.save_to_json(phrases)

        # Mostrar resumen
        print("\n" + "=" * 60)
        print(f"RESUMEN: {len(phrases)} frases extraídas exitosamente")
        print("=" * 60)
        if phrases:
            print("\nEjemplo (primera frase):")
            print(f"  '{phrases[0]['phrase']}'")
            print(f"  -- {phrases[0]['author']}")

        scraper.close()
        return 0

    except Exception as e:
        logger.error(f"Error fatal: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
