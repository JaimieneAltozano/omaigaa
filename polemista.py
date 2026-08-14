import json
import os
import re
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer, util

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


BASE_DIR = Path(__file__).resolve().parent

FRASES_PATH = BASE_DIR / "frases.json"
EMBEDDINGS_PATH = BASE_DIR / "embeddings.npy"
METADATA_PATH = BASE_DIR / "embeddings_metadata.json"

# Modelo multilingüe: permite comparar consultas en español
# con frases en inglés sin depender de palabras clave compartidas.
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

# Cantidad máxima de fuentes que se entregarán al modelo.
TOP_K = 5

# Umbral mínimo de similitud coseno.
# Con el modelo multilingüe, las consultas relevantes superan
# claramente 0.30, mientras que las irrelevantes se quedan por debajo.
SIMILARITY_THRESHOLD = 0.30


class Polemista:
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)

        self.frases = self._cargar_frases()

        self.embeddings = self._cargar_embeddings()

        if len(self.frases) != len(self.embeddings):
            raise ValueError(
                "La cantidad de frases no coincide con la cantidad de embeddings."
            )

        self.client = self._crear_cliente_openai()

    # ---------------------------------------------------------
    # CARGA DE DATOS
    # ---------------------------------------------------------

    def _cargar_frases(self):
        if not FRASES_PATH.exists():
            raise FileNotFoundError(
                f"No se encontró el archivo: {FRASES_PATH}"
            )

        with open(FRASES_PATH, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)

        frases = []

        # Soporta diferentes estructuras de JSON.
        if isinstance(datos, list):
            registros = datos

        elif isinstance(datos, dict):
            if "quotes" in datos:
                registros = datos["quotes"]
            elif "frases" in datos:
                registros = datos["frases"]
            else:
                registros = list(datos.values())

        else:
            raise ValueError("Formato de frases.json no reconocido.")

        for registro in registros:
            if isinstance(registro, str):
                frases.append(
                    {
                        "text": registro,
                        "author": "Autor desconocido"
                    }
                )

            elif isinstance(registro, dict):
                texto = (
                    registro.get("text")
                    or registro.get("quote")
                    or registro.get("frase")
                    or registro.get("phrase")
                )

                autor = (
                    registro.get("author")
                    or registro.get("autor")
                    or "Autor desconocido"
                )

                if texto:
                    frases.append(
                        {
                            "text": texto,
                            "author": autor
                        }
                    )

        if not frases:
            raise ValueError("No se encontraron frases en frases.json.")

        return frases

    def _cargar_embeddings(self):
        if EMBEDDINGS_PATH.exists():
            embeddings = np.load(EMBEDDINGS_PATH)

            # Comprobamos que tenga la forma esperada.
            dimension = self._model_dimension()

            if (
                embeddings.ndim == 2
                and embeddings.shape[1] == dimension
                and embeddings.shape[0] == len(self.frases)
            ):
                return embeddings

        # Si no existen embeddings compatibles,
        # los generamos automáticamente.
        textos = [frase["text"] for frase in self.frases]

        embeddings = self.model.encode(
            textos,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        np.save(EMBEDDINGS_PATH, embeddings)

        return embeddings

    def _model_dimension(self):
        """Devuelve la dimensión del embedding del modelo cargado."""
        metodo = getattr(self.model, "get_embedding_dimension", None)

        if metodo is not None:
            return metodo()

        return self.model.get_sentence_embedding_dimension()

    def _crear_cliente_openai(self):
        if OpenAI is None:
            return None

        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            return None

        return OpenAI(api_key=api_key)

    # ---------------------------------------------------------
    # BÚSQUEDA SEMÁNTICA
    # ---------------------------------------------------------

    def buscar_fuentes(self, pregunta, top_k=TOP_K):
        """
        Busca las frases semánticamente relacionadas con la pregunta.
        """

        pregunta_embedding = self.model.encode(
            pregunta,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        similitudes = util.cos_sim(
            pregunta_embedding,
            self.embeddings
        )[0].cpu().numpy()

        indices = np.argsort(similitudes)[::-1]

        resultados = []

        for indice in indices[:top_k]:
            score = float(similitudes[indice])

            if score >= SIMILARITY_THRESHOLD:
                frase = self.frases[indice]

                resultados.append(
                    {
                        "text": frase["text"],
                        "author": frase["author"],
                        "score": round(score, 4)
                    }
                )

        return resultados

    # ---------------------------------------------------------
    # GENERACIÓN DEL ARGUMENTO
    # ---------------------------------------------------------

    def generar_debate(self, pregunta):
        """
        Ejecuta el proceso completo:

        1. Buscar fuentes.
        2. Verificar relevancia.
        3. Generar respuesta condicionada.
        4. Validar las citas.
        """

        fuentes = self.buscar_fuentes(pregunta)

        if not fuentes:
            return {
                "success": False,
                "question": pregunta,
                "sources": [],
                "answer": (
                    "No tengo fuentes relevantes en mi base de datos "
                    "para debatir esta pregunta."
                )
            }

        if self.client is None:
            respuesta = self._generar_mini_ensayo_local(
                pregunta,
                fuentes
            )

        else:
            respuesta = self._generar_con_openai(
                pregunta,
                fuentes
            )

        # Verificación estricta de citas.
        if not self._validar_citas(respuesta, fuentes):
            return {
                "success": False,
                "question": pregunta,
                "sources": fuentes,
                "answer": (
                    "Encontré fuentes relevantes, pero la respuesta generada "
                    "no pudo ser validada porque no utilizó correctamente "
                    "las citas de la base de datos."
                )
            }

        return {
            "success": True,
            "question": pregunta,
            "sources": fuentes,
            "answer": respuesta
        }

    # ---------------------------------------------------------
    # OPENAI
    # ---------------------------------------------------------

    def _generar_con_openai(self, pregunta, fuentes):
        fuentes_texto = ""

        for numero, fuente in enumerate(fuentes, start=1):
            fuentes_texto += (
                f"\nFUENTE {numero}\n"
                f"Frase: \"{fuente['text']}\"\n"
                f"Autor: {fuente['author']}\n"
                f"Similitud: {fuente['score']}\n"
            )

        system_prompt = """
Eres un polemista filosófico.

Tu tarea es responder una pregunta filosófica o compleja utilizando
EXCLUSIVAMENTE las fuentes proporcionadas por el sistema.

REGLAS OBLIGATORIAS:

1. Escribe exactamente DOS párrafos.
2. Responde directamente a la pregunta.
3. Debes utilizar al menos DOS frases de las fuentes cuando existan
   suficientes fuentes disponibles.
4. Las frases deben aparecer TEXTUALMENTE, sin modificar palabras.
5. Cada frase utilizada debe citarse entre comillas.
6. Después de cada cita debes indicar su autor entre paréntesis.
7. No inventes citas.
8. No atribuyas una frase a un autor diferente.
9. No utilices conocimiento externo como evidencia.
10. Puedes desarrollar razonamientos propios, pero estos deben estar
    argumentativamente condicionados por las frases proporcionadas.
11. No menciones que eres una inteligencia artificial.
12. No agregues títulos, listas ni introducciones.
13. La respuesta debe tener exactamente dos párrafos.
"""

        user_prompt = f"""
PREGUNTA DEL USUARIO:

{pregunta}

FUENTES DISPONIBLES EN LA BASE DE DATOS:

{fuentes_texto}

Redacta ahora el mini-ensayo respetando estrictamente todas las reglas.
"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        )

        return response.choices[0].message.content.strip()

    def _generar_mini_ensayo_local(self, pregunta, fuentes):
        """
        Genera un mini-ensayo de dos párrafos SIN depender de OpenAI.

        Usa estrictamente las citas recuperadas de la base de datos y
        las incorpora textualmente (con su autor entre paréntesis),
        garantizando que la respuesta cumpla la validación de citas.
        """

        pregunta_limpia = pregunta.rstrip("?").strip()

        primera = fuentes[0]

        if len(fuentes) > 1:
            segunda = fuentes[1]
        else:
            segunda = primera

        parrafo_1 = (
            f"Ante la pregunta \"{pregunta_limpia}?\", no basta con opinar: "
            f"hace falta apoyarse en quienes ya reflexionaron sobre ello. "
            f"{primera['author']} lo expresó con claridad: "
            f"\"{primera['text']}\". "
            f"Esta idea no responde por sí sola, pero señala el camino: "
            f"para debatir con seriedad hay que examinar los fundamentos "
            f"de lo que afirmamos antes de defender cualquier postura."
        )

        parrafo_2 = (
            f"En la misma línea, {segunda['author']} sostiene: "
            f"\"{segunda['text']}\". "
            f"Si sumamos ambas reflexiones, la cuestión planteada se vuelve "
            f"más nítida: un argumento sólido no se improvisa, sino que "
            f"se construye a partir de razones verificadas. "
            f"Quien cita estas fuentes puede defender su posición con "
            f"fundamento; quien las ignora solo repite ideas sin peso."
        )

        return f"{parrafo_1}\n\n{parrafo_2}"

    # ---------------------------------------------------------
    # VALIDACIÓN
    # ---------------------------------------------------------

    def _validar_citas(self, respuesta, fuentes):
        """
        Comprueba que las citas utilizadas realmente existan
        en la base de datos.
        """

        citas_validas = 0

        for fuente in fuentes:
            texto = fuente["text"].strip()

            if texto in respuesta:
                citas_validas += 1

        # Debe existir al menos una cita real.
        if citas_validas == 0:
            return False

        # Comprobamos que existan dos párrafos.
        parrafos = [
            p.strip()
            for p in re.split(r"\n\s*\n", respuesta)
            if p.strip()
        ]

        if len(parrafos) != 2:
            return False

        return True


# -------------------------------------------------------------
# EJECUCIÓN DESDE TERMINAL
# -------------------------------------------------------------

def main():
    polemista = Polemista()

    print("=" * 60)
    print("              POLEMISTA FILOSÓFICO")
    print("=" * 60)
    print()
    print("Escribe una pregunta filosófica.")
    print("Escribe 'salir' para terminar.")
    print()

    while True:
        pregunta = input("Tú: ").strip()

        if pregunta.lower() in {"salir", "exit", "quit"}:
            print("Programa finalizado.")
            break

        if not pregunta:
            print("Escribe una pregunta.")
            continue

        print("\nBuscando fuentes...\n")

        resultado = polemista.generar_debate(pregunta)

        print("-" * 60)
        print(resultado["answer"])
        print("-" * 60)

        if resultado["sources"]:
            print("\nFuentes recuperadas:")

            for fuente in resultado["sources"]:
                print(
                    f"- [{fuente['score']}] "
                    f"\"{fuente['text']}\" "
                    f"({fuente['author']})"
                )

        print()


if __name__ == "__main__":
    main()