# Web Scraper de Frases Inspiracionales

**Versión:** 1.0.0  
**Autor:** Manus AI  
**Última actualización:** Agosto 2026

## Descripción General

Este proyecto es un **web scraper** que extrae frases inspiracionales del sitio [quotes.toscrape.com](https://quotes.toscrape.com/). El scraper automatiza la recopilación de 100 frases distribuidas en 10 páginas, extrayendo tanto el texto de la frase como el nombre del autor, y guardando los resultados en formato JSON.

El proyecto demuestra buenas prácticas de desarrollo Python, incluyendo manejo robusto de errores, logging estructurado, documentación clara y modularidad del código.

## Características Principales

- **Extracción automatizada:** Descarga y procesa múltiples páginas de manera eficiente
- **Manejo de errores:** Control de excepciones de red y validación de datos
- **Logging estructurado:** Seguimiento detallado de la ejecución con niveles de severidad
- **Modularidad:** Clase `QuoteScraper` reutilizable y extensible
- **Formato JSON:** Salida estructurada y fácil de procesar
- **Documentación completa:** Docstrings, comentarios y guías de uso

## Estructura del Proyecto

```
omaigaa/
├── README.md              # Este archivo
├── EJECUCION_Y_MEJORAS.md # Informe de ejecución, cambios y mejoras
├── SEMANTIC_SEARCH_README.md  # Documentación del motor de búsqueda semántica
├── ARCHITECTURE.md        # Documentación técnica detallada
├── app.py                 # Servidor Flask (interfaz Interestelar)
├── semantic_search_local.py    # Motor semántico local (embeddings + coseno)
├── generate_embeddings.py      # Generador de embeddings locales
├── scraper.py            # Script principal mejorado
├── semantic_search.py    # Motor de búsqueda semántica (LLM, requiere API)
├── test_semantic_search.py   # Suite de tests del motor LLM
├── test_app.py              # Suite de tests del servidor Flask
├── main.ipynb            # Notebook original de Jupyter
├── requirements.txt      # Dependencias del proyecto
├── .gitignore           # Configuración de Git
├── frases.json          # Datos generados (100 frases)
├── embeddings.npy       # Embeddings pre-generados (100 × 384)
├── embeddings_metadata.json  # Metadata de los embeddings
└── venv/                # Entorno virtual Python
```

> **Nota:** El entorno virtual `venv_local/` incluido en versiones anteriores
> estaba incompleto (layout de Linux, sin ejecutable en Windows). El proyecto se
> ejecuta con el entorno `.venv-2` (Python 3.14) situado en la raíz. Consulta
> [EJECUCION_Y_MEJORAS.md](EJECUCION_Y_MEJORAS.md) para el informe completo de
> cómo se ejecutó y las mejoras implementadas.

## Nuevo: Motor de Búsqueda Semántica

Se implementó un motor de búsqueda semántica que analiza la intención emocional de las consultas y devuelve las 3 frases más relevantes **sin usar búsqueda por palabras clave**.

### Características

- ✅ Análisis de emociones, situaciones y pensamientos abstractos
- ✅ Conecta con frases que no comparten palabras con la consulta
- ✅ Usa LLM (Claude Sonnet 4.6) para análisis semántico profundo
- ✅ Devuelve explicaciones de por qué cada frase conecta
- ✅ Validado con 10 casos de prueba (100% éxito)

### Uso Rápido

```bash
# Ejecutar el motor de búsqueda
python3 semantic_search.py

# Ejecutar tests de validación
python3 test_semantic_search.py
```

Para más detalles, consulta [SEMANTIC_SEARCH_README.md](SEMANTIC_SEARCH_README.md).

## Requisitos del Sistema

- **Python:** 3.8 o superior
- **Gestor de paquetes:** pip
- **Conexión a internet:** Para acceder a quotes.toscrape.com

## Instalación

### Opción 1: Usando el entorno virtual existente

Si el proyecto ya incluye un entorno virtual (`venv`), simplemente actívalo:

```bash
# En Linux/macOS
source venv/bin/activate

# En Windows
venv\Scripts\activate
```

### Opción 2: Crear un nuevo entorno virtual

Si prefieres crear un entorno limpio, ejecuta los siguientes comandos:

```bash
# Crear el entorno virtual
python3 -m venv venv

# Activar el entorno
source venv/bin/activate  # Linux/macOS
# o
venv\Scripts\activate     # Windows

# Instalar las dependencias
pip install -r requirements.txt
```

### Opción 3: Instalación automática (Windows)

En la raíz del proyecto (`omaigaa_interestelar/`) ejecuta:

```powershell
.\setup.ps1    # crea .venv-2 e instala requirements.txt
.\run.ps1      # arranca el servidor en http://localhost:5000
```

## Uso

### Servidor web omaigaa (búsqueda semántica local)

```bash
cd omaigaa
python3 app.py          # o .\run.ps1 desde la raíz del proyecto
# Abrir http://localhost:5000
```

Rutas disponibles:

| Ruta | Descripción |
|------|-------------|
| `GET /` | Página principal con interfaz Interestelar |
| `GET /api/health` | Estado del servicio (JSON) |
| `POST /api/search` | Búsqueda semántica `{"query": "..."}` (JSON) |

Configuración por variables de entorno: `HOST`, `PORT`, `FLASK_DEBUG`, `MODEL_NAME`.

### Ejecución desde línea de comandos

Para ejecutar el scraper y generar el archivo `frases.json`:

```bash
python3 scraper.py
```

La salida esperada será similar a:

```
2026-08-10 15:22:45,264 - INFO - Iniciando extracción de frases...
2026-08-10 15:22:48,039 - INFO - ✓ Página 1: 10 frases extraídas
...
============================================================
RESUMEN: 100 frases extraídas exitosamente
============================================================
Ejemplo (primera frase):
  'The world as we have created it is a process of our thinking...'
  -- Albert Einstein
```

### Uso como módulo Python

Para integrar el scraper en otros proyectos Python:

```python
from scraper import QuoteScraper

# Crear instancia del scraper
scraper = QuoteScraper(timeout=10)

# Extraer frases (máximo 5 páginas)
phrases = scraper.extract_phrases(max_pages=5)

# Guardar en JSON
scraper.save_to_json(phrases, output_path="mis_frases.json")

# Cerrar la sesión
scraper.close()

# Procesar los datos
for phrase in phrases:
    print(f"'{phrase['phrase']}' -- {phrase['author']}")
```

### Uso en Jupyter Notebook

El proyecto incluye `main.ipynb` que demuestra el uso del scraper en un entorno interactivo. Para ejecutarlo:

```bash
jupyter notebook main.ipynb
```

## Formato de Salida

El archivo `frases.json` contiene un array JSON con la siguiente estructura:

```json
[
  {
    "author": "Albert Einstein",
    "phrase": "The world as we have created it is a process of our thinking..."
  },
  {
    "author": "J.K. Rowling",
    "phrase": "It is our choices, Harry, that show what we truly are..."
  }
]
```

Cada objeto contiene dos campos:
- **author** (string): Nombre del autor de la frase
- **phrase** (string): Texto de la frase sin caracteres tipográficos

## Dependencias

| Paquete | Versión | Propósito |
|---------|---------|----------|
| requests | ≥2.34.0 | Realizar peticiones HTTP |
| beautifulsoup4 | ≥4.15.0 | Parsear y extraer datos del HTML |
| flask | ≥3.1.0 | Servidor web (interfaz Interestelar) |
| numpy | ≥1.26.0 | Cálculo numérico de embeddings |
| scikit-learn | ≥1.5.0 | Similitud coseno |
| sentence-transformers | ≥3.0.0 | Embeddings semánticos locales |

Para ver todas las dependencias instaladas, ejecuta:

```bash
pip list
```

## Arquitectura Técnica

### Clase `QuoteScraper`

La clase principal que encapsula toda la lógica de extracción:

**Atributos principales:**
- `BASE_URL`: URL base del sitio (https://quotes.toscrape.com)
- `TIMEOUT`: Tiempo máximo de espera por petición (10 segundos)
- `session`: Sesión HTTP reutilizable para eficiencia

**Métodos principales:**
- `extract_phrases(max_pages)`: Extrae frases de múltiples páginas
- `save_to_json(phrases, output_path)`: Guarda los datos en JSON
- `close()`: Cierra la sesión HTTP

### Flujo de Ejecución

1. **Inicialización:** Se crea una sesión HTTP reutilizable
2. **Iteración de páginas:** Se recorren las páginas comenzando desde la página 1
3. **Descarga:** Se realiza una petición GET a cada URL
4. **Parseo:** BeautifulSoup analiza el HTML y localiza los elementos `.quote`
5. **Extracción:** Se extraen texto del autor y frase, eliminando caracteres especiales
6. **Almacenamiento:** Los datos se acumulan en una lista
7. **Terminación:** El bucle termina cuando no hay más páginas
8. **Guardado:** Los datos se serializan a JSON

Para más detalles técnicos, consulta [ARCHITECTURE.md](ARCHITECTURE.md).

## Manejo de Errores

El scraper implementa un manejo robusto de errores:

- **Errores HTTP:** Se detectan con `response.raise_for_status()`
- **Errores de conexión:** Se capturan excepciones de `requests`
- **Errores de parseo:** Se valida la presencia de elementos HTML
- **Errores de I/O:** Se controlan al escribir archivos

Todos los errores se registran en el sistema de logging para facilitar el diagnóstico.

## Logging

El proyecto utiliza el módulo `logging` de Python para registrar eventos:

```python
import logging
logger = logging.getLogger(__name__)
logger.info("Mensaje informativo")
logger.warning("Advertencia")
logger.error("Error")
```

Para cambiar el nivel de logging, modifica el archivo `scraper.py`:

```python
logging.basicConfig(level=logging.DEBUG)  # Para más detalle
```

## Ejemplos de Uso Avanzado

### Extraer solo las primeras 3 páginas

```python
from scraper import QuoteScraper

scraper = QuoteScraper()
phrases = scraper.extract_phrases(max_pages=3)
print(f"Extraídas {len(phrases)} frases")  # Salida: Extraídas 30 frases
```

### Procesar frases por autor

```python
from scraper import QuoteScraper
from collections import defaultdict

scraper = QuoteScraper()
phrases = scraper.extract_phrases()

# Agrupar por autor
by_author = defaultdict(list)
for phrase in phrases:
    by_author[phrase['author']].append(phrase['phrase'])

# Mostrar frases por autor
for author, phrases_list in sorted(by_author.items()):
    print(f"\n{author} ({len(phrases_list)} frases):")
    for phrase in phrases_list:
        print(f"  - {phrase}")
```

### Guardar en múltiples formatos

```python
import json
import csv
from scraper import QuoteScraper

scraper = QuoteScraper()
phrases = scraper.extract_phrases()

# Guardar en JSON
scraper.save_to_json(phrases, "frases.json")

# Guardar en CSV
with open("frases.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["author", "phrase"])
    writer.writeheader()
    writer.writerows(phrases)
```

## Solución de Problemas

### Error: "No module named 'requests'"

**Solución:** Instala las dependencias:
```bash
pip install -r requirements.txt
```

### Error: "Connection timeout"

**Solución:** El sitio puede estar temporalmente inaccesible. Intenta nuevamente en unos minutos o aumenta el timeout:
```python
scraper = QuoteScraper(timeout=20)
```

### El archivo `frases.json` está vacío

**Solución:** Verifica que el script se ejecutó completamente. Si ves errores, consulta el logging para más detalles.

## Mejoras Futuras

Posibles extensiones del proyecto:

- Soporte para múltiples idiomas de frases
- Exportación a CSV, Excel o base de datos
- Interfaz web para visualizar las frases
- Caché local para evitar descargas repetidas
- Filtrado por autor o palabras clave
- API REST para acceder a las frases

## Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## Contacto y Soporte

Para reportar problemas, sugerencias o contribuciones, por favor contacta al equipo de desarrollo.

---

**Nota:** Este proyecto fue corregido y documentado por Manus AI el 10 de agosto de 2026. Se mejoró la modularidad, se agregó logging estructurado y se creó documentación completa.
