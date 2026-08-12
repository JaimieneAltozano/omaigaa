# Documentación Técnica - Arquitectura del Scraper

**Versión:** 1.0.0  
**Autor:** Manus AI  
**Última actualización:** Agosto 2026

## Tabla de Contenidos

1. [Visión General](#visión-general)
2. [Componentes Principales](#componentes-principales)
3. [Flujo de Datos](#flujo-de-datos)
4. [Manejo de Errores](#manejo-de-errores)
5. [Optimizaciones](#optimizaciones)
6. [Decisiones de Diseño](#decisiones-de-diseño)
7. [Extensibilidad](#extensibilidad)

## Visión General

El scraper está diseñado siguiendo el patrón de **arquitectura modular** con separación clara de responsabilidades. La clase `QuoteScraper` encapsula toda la lógica de extracción, permitiendo su reutilización en diferentes contextos.

### Principios de Diseño

- **Modularidad:** Código organizado en una clase reutilizable
- **Robustez:** Manejo exhaustivo de errores y casos límite
- **Observabilidad:** Logging detallado de todas las operaciones
- **Mantenibilidad:** Código bien documentado y fácil de entender
- **Eficiencia:** Reutilización de sesiones HTTP y parseo optimizado

## Componentes Principales

### 1. Clase `QuoteScraper`

La clase principal que implementa toda la lógica de extracción.

```python
class QuoteScraper:
    BASE_URL = "https://quotes.toscrape.com"
    TIMEOUT = 10
    QUOTE_SELECTOR = ".quote"
    TEXT_SELECTOR = ".text"
    AUTHOR_SELECTOR = ".author"
    QUOTE_CHARS = {"\u201c": "", "\u201d": ""}
```

**Responsabilidades:**
- Gestionar la sesión HTTP
- Descargar páginas del sitio
- Parsear HTML y extraer datos
- Validar y limpiar datos
- Guardar resultados en JSON

### 2. Método `extract_phrases()`

```python
def extract_phrases(self, max_pages: Optional[int] = None) -> list[dict]:
    """Extrae todas las frases del sitio quotes.toscrape.com."""
```

**Parámetros:**
- `max_pages` (int, optional): Límite de páginas a procesar. Si es `None`, procesa todas.

**Retorno:**
- Lista de diccionarios con estructura `{"author": str, "phrase": str}`

**Lógica:**
1. Inicializa un acumulador de frases vacío
2. Comienza en la página 1
3. Para cada página:
   - Construye la URL: `https://quotes.toscrape.com/page/{n}/`
   - Realiza petición GET con timeout
   - Valida el código HTTP (200)
   - Parsea el HTML con BeautifulSoup
   - Busca elementos con clase `.quote`
   - Si no hay elementos, termina el bucle
   - Extrae autor y frase de cada elemento
   - Limpia caracteres tipográficos
   - Agrega a la lista acumuladora
4. Retorna la lista completa

### 3. Método `save_to_json()`

```python
def save_to_json(
    self,
    phrases: list[dict],
    output_path: str = "frases.json",
    ensure_ascii: bool = False,
    indent: int = 2
) -> None:
```

**Responsabilidades:**
- Crear directorio de salida si no existe
- Serializar datos a JSON
- Escribir archivo con encoding UTF-8
- Registrar resultado en logging

**Parámetros:**
- `phrases`: Lista de frases a guardar
- `output_path`: Ruta del archivo (default: "frases.json")
- `ensure_ascii`: Si False, permite caracteres Unicode directos
- `indent`: Espacios de indentación (default: 2)

## Flujo de Datos

### Diagrama de Flujo

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Inicialización                                           │
│    - Crear sesión HTTP reutilizable                         │
│    - Configurar logging                                     │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ 2. Iteración de Páginas                                     │
│    - page_number = 1                                        │
│    - while page_number <= max_pages:                        │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ 3. Descarga de Página                                       │
│    - GET https://quotes.toscrape.com/page/{n}/              │
│    - Timeout: 10 segundos                                   │
│    - Validar código HTTP                                    │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ 4. Parseo HTML                                              │
│    - BeautifulSoup(response.text, "html.parser")            │
│    - Seleccionar elementos: soup.select(".quote")           │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ 5. Validación                                               │
│    - ¿Hay elementos .quote?                                 │
│    - NO → Fin de paginación                                 │
│    - SÍ → Continuar extracción                              │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ 6. Extracción de Datos                                      │
│    - Para cada elemento .quote:                             │
│      - Obtener .text → frase                                │
│      - Obtener .author → autor                              │
│      - Limpiar caracteres tipográficos                      │
│      - Crear diccionario {"author": ..., "phrase": ...}     │
│      - Agregar a lista                                      │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ 7. Siguiente Página                                         │
│    - page_number += 1                                       │
│    - Volver a paso 2                                        │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ 8. Guardado en JSON                                         │
│    - json.dump(phrases, file, ensure_ascii=False, indent=2) │
│    - Crear directorio si no existe                          │
│    - Escribir con encoding UTF-8                            │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│ 9. Cierre de Sesión                                         │
│    - session.close()                                        │
│    - Liberar recursos                                       │
└─────────────────────────────────────────────────────────────┘
```

### Estructura de Datos

**Entrada:** URL del sitio web

**Salida:** Lista de diccionarios

```python
[
    {
        "author": "Albert Einstein",
        "phrase": "The world as we have created it..."
    },
    {
        "author": "J.K. Rowling",
        "phrase": "It is our choices, Harry, that show..."
    },
    # ... más frases
]
```

**Archivo JSON generado:**
```json
[
  {
    "author": "Albert Einstein",
    "phrase": "The world as we have created it is a process of our thinking. It cannot be changed without changing our thinking."
  },
  ...
]
```

## Manejo de Errores

### Estrategia de Manejo

El scraper implementa un manejo defensivo de errores en múltiples niveles:

| Tipo de Error | Causa | Manejo | Resultado |
|---------------|-------|--------|-----------|
| `HTTPError` | Código HTTP no 2xx | `response.raise_for_status()` | Excepción capturada y registrada |
| `RequestException` | Conexión fallida, timeout | Try-except en bucle principal | Excepción propagada al caller |
| `AttributeError` | Elemento HTML faltante | Try-except en extracción | Elemento omitido, se continúa |
| `IOError` | Error escribiendo archivo | Try-except en `save_to_json()` | Excepción propagada |
| `ValueError` | Datos inválidos | Validación previa | Elemento omitido |

### Ejemplos de Manejo

**1. Error de conexión:**
```python
try:
    response = self.session.get(url, timeout=self.timeout)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    logger.error(f"Error de conexión en página {page_number}: {e}")
    raise
```

**2. Elemento faltante:**
```python
try:
    text_elem = block.select_one(self.TEXT_SELECTOR)
    if not text_elem:
        logger.warning(f"Bloque sin texto en página {page_number}")
        continue
except Exception as e:
    logger.error(f"Error extrayendo bloque: {e}")
    continue
```

**3. Error de I/O:**
```python
try:
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(phrases, f, ensure_ascii=ensure_ascii, indent=indent)
except IOError as e:
    logger.error(f"Error al guardar archivo: {e}")
    raise
```

## Optimizaciones

### 1. Reutilización de Sesión HTTP

```python
self.session = requests.Session()
# Reutilizar en cada petición
response = self.session.get(url)
```

**Beneficio:** Mantiene conexiones TCP abiertas, reduce overhead de conexión.

### 2. Timeout Configurables

```python
response = self.session.get(url, timeout=self.timeout)
```

**Beneficio:** Evita bloqueos indefinidos en conexiones lentas.

### 3. Parseo Selectivo

```python
quote_blocks = soup.select(self.QUOTE_SELECTOR)
```

**Beneficio:** Solo procesa elementos relevantes, ignora el resto del HTML.

### 4. Logging Estructurado

```python
logger.info(f"✓ Página {page_number}: {len(quote_blocks)} frases extraídas")
```

**Beneficio:** Facilita debugging y monitoreo sin afectar performance.

### 5. Limpieza de Caracteres

```python
phrase = raw_phrase
for char, replacement in self.QUOTE_CHARS.items():
    phrase = phrase.replace(char, replacement)
```

**Beneficio:** Normaliza caracteres tipográficos de manera eficiente.

## Decisiones de Diseño

### 1. ¿Por qué `requests` en lugar de `urllib`?

- **requests:** API simple, manejo automático de encoding, sesiones reutilizables
- **urllib:** Más bajo nivel, requiere más código boilerplate

**Decisión:** requests es más mantenible y legible.

### 2. ¿Por qué BeautifulSoup en lugar de Selenium/Playwright?

- **BeautifulSoup:** Ligero, rápido, suficiente para HTML estático
- **Selenium/Playwright:** Pesados, lentos, necesarios solo para JavaScript

**Decisión:** El sitio no usa JavaScript, BeautifulSoup es más eficiente.

### 3. ¿Por qué clase en lugar de funciones?

- **Clase:** Encapsulación, estado reutilizable, extensibilidad
- **Funciones:** Más simple para casos triviales

**Decisión:** La clase permite reutilización y extensión futura.

### 4. ¿Por qué logging en lugar de print?

- **logging:** Niveles de severidad, formato configurable, fácil de desactivar
- **print:** No configurable, siempre visible

**Decisión:** logging es más profesional y flexible.

## Extensibilidad

### Extensión 1: Soporte para Múltiples Sitios

```python
class GenericScraper(QuoteScraper):
    def __init__(self, base_url, quote_selector, text_selector, author_selector):
        super().__init__()
        self.BASE_URL = base_url
        self.QUOTE_SELECTOR = quote_selector
        self.TEXT_SELECTOR = text_selector
        self.AUTHOR_SELECTOR = author_selector
```

### Extensión 2: Caché Local

```python
def extract_phrases_with_cache(self, max_pages=None, cache_file="cache.json"):
    if Path(cache_file).exists():
        with open(cache_file) as f:
            return json.load(f)
    phrases = self.extract_phrases(max_pages)
    self.save_to_json(phrases, cache_file)
    return phrases
```

### Extensión 3: Exportación a Múltiples Formatos

```python
def save_to_csv(self, phrases, output_path="frases.csv"):
    import csv
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["author", "phrase"])
        writer.writeheader()
        writer.writerows(phrases)

def save_to_database(self, phrases, db_connection):
    for phrase in phrases:
        db_connection.insert("quotes", phrase)
```

### Extensión 4: Filtrado y Búsqueda

```python
def filter_by_author(self, phrases, author):
    return [p for p in phrases if p["author"].lower() == author.lower()]

def search_phrase(self, phrases, keyword):
    return [p for p in phrases if keyword.lower() in p["phrase"].lower()]
```

## Pruebas y Validación

### Casos de Prueba Recomendados

1. **Extracción completa:** Verificar que se extraen 100 frases
2. **Límite de páginas:** Verificar que `max_pages=3` extrae 30 frases
3. **Manejo de errores:** Simular timeout y verificar logging
4. **Formato JSON:** Validar estructura y encoding UTF-8
5. **Caracteres especiales:** Verificar limpieza de comillas tipográficas

### Ejemplo de Prueba

```python
def test_extract_phrases():
    scraper = QuoteScraper()
    phrases = scraper.extract_phrases(max_pages=1)
    assert len(phrases) == 10
    assert all("author" in p and "phrase" in p for p in phrases)
    assert all(isinstance(p["author"], str) for p in phrases)
    assert all(isinstance(p["phrase"], str) for p in phrases)
```

## Rendimiento

### Métricas Esperadas

| Métrica | Valor |
|---------|-------|
| Tiempo total | ~13 segundos (10 páginas) |
| Tiempo por página | ~1.3 segundos |
| Frases extraídas | 100 |
| Tamaño del archivo JSON | ~17.7 KB |
| Uso de memoria | < 10 MB |

### Optimizaciones Futuras

- Paralelización de descargas (usando `asyncio` o `concurrent.futures`)
- Compresión de datos (gzip)
- Índices de búsqueda (sqlite)
- Caché distribuido (Redis)

---

**Nota:** Esta documentación fue creada por Manus AI el 10 de agosto de 2026 como parte de la revisión integral del proyecto.
