# Guía de Mantenimiento y Troubleshooting

**Versión:** 1.0.0  
**Autor:** Manus AI  
**Última actualización:** Agosto 2026

## Tabla de Contenidos

1. [Mantenimiento Preventivo](#mantenimiento-preventivo)
2. [Solución de Problemas Comunes](#solución-de-problemas-comunes)
3. [Actualización de Dependencias](#actualización-de-dependencias)
4. [Monitoreo y Logging](#monitoreo-y-logging)
5. [Backup y Recuperación](#backup-y-recuperación)

## Mantenimiento Preventivo

### Verificación Periódica

Se recomienda ejecutar las siguientes verificaciones regularmente:

**Semanal:**
- Ejecutar el scraper para verificar que funciona: `python3 scraper.py`
- Revisar el tamaño del archivo `frases.json`
- Verificar que el sitio `quotes.toscrape.com` está accesible

**Mensual:**
- Revisar el archivo de log para errores
- Verificar que las dependencias están actualizadas
- Hacer backup del archivo `frases.json`

**Trimestral:**
- Revisar cambios en la estructura HTML del sitio
- Actualizar selectores CSS si es necesario
- Revisar y actualizar la documentación

### Actualización de Dependencias

Para mantener el proyecto seguro y con las últimas características:

```bash
# Verificar versiones disponibles
pip list --outdated

# Actualizar una dependencia específica
pip install --upgrade requests

# Actualizar todas las dependencias
pip install --upgrade -r requirements.txt

# Actualizar el archivo requirements.txt
pip freeze > requirements.txt
```

### Monitoreo de Cambios en el Sitio

El sitio `quotes.toscrape.com` puede cambiar su estructura HTML. Para detectar cambios:

```python
# Script de validación
import requests
from bs4 import BeautifulSoup

url = "https://quotes.toscrape.com/page/1/"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Verificar que los selectores esperados existen
quotes = soup.select(".quote")
print(f"Frases encontradas: {len(quotes)}")

if len(quotes) == 0:
    print("ALERTA: No se encontraron frases. El sitio puede haber cambiado.")
```

## Solución de Problemas Comunes

### Problema 1: "ModuleNotFoundError: No module named 'requests'"

**Síntomas:**
```
Traceback (most recent call last):
  File "scraper.py", line 1, in <module>
    import requests
ModuleNotFoundError: No module named 'requests'
```

**Causas posibles:**
- Dependencias no instaladas
- Entorno virtual no activado
- Python incorrecto

**Soluciones:**

```bash
# Opción 1: Instalar dependencias
pip install -r requirements.txt

# Opción 2: Verificar que el entorno virtual está activado
source venv/bin/activate  # Linux/macOS
# o
venv\Scripts\activate     # Windows

# Opción 3: Usar Python explícitamente
python3 -m pip install requests beautifulsoup4
```

### Problema 2: "Connection timeout" o "ConnectionError"

**Síntomas:**
```
requests.exceptions.ConnectionError: HTTPConnectionPool(host='quotes.toscrape.com', port=80)
```

**Causas posibles:**
- Conexión a internet no disponible
- El sitio está caído
- Firewall bloqueando la conexión
- Timeout muy corto

**Soluciones:**

```bash
# Opción 1: Verificar conectividad
ping quotes.toscrape.com

# Opción 2: Aumentar el timeout
python3 -c "from scraper import QuoteScraper; s = QuoteScraper(timeout=30); s.extract_phrases()"

# Opción 3: Verificar firewall
curl -v https://quotes.toscrape.com/page/1/
```

### Problema 3: El archivo "frases.json" está vacío o corrupto

**Síntomas:**
```
$ cat frases.json
$ wc -c frases.json
0 frases.json
```

**Causas posibles:**
- El script se interrumpió
- Permisos insuficientes
- Espacio en disco insuficiente

**Soluciones:**

```bash
# Opción 1: Ejecutar nuevamente
python3 scraper.py

# Opción 2: Verificar permisos
ls -la frases.json
chmod 644 frases.json

# Opción 3: Verificar espacio en disco
df -h

# Opción 4: Restaurar desde backup
cp frases.json.backup frases.json
```

### Problema 4: "No se extraen todas las frases"

**Síntomas:**
- El script termina prematuramente
- Menos de 100 frases extraídas

**Causas posibles:**
- El sitio cambió su estructura
- Selectores CSS incorrectos
- Límite de páginas muy bajo

**Soluciones:**

```bash
# Opción 1: Verificar selectores
python3 << 'EOF'
import requests
from bs4 import BeautifulSoup

url = "https://quotes.toscrape.com/page/1/"
soup = BeautifulSoup(requests.get(url).text, "html.parser")

# Listar todos los divs con clase quote
quotes = soup.select(".quote")
print(f"Frases en página 1: {len(quotes)}")

# Inspeccionar estructura
if quotes:
    print("\nPrimer elemento:")
    print(quotes[0].prettify())
EOF

# Opción 2: Aumentar max_pages
python3 -c "from scraper import QuoteScraper; s = QuoteScraper(); phrases = s.extract_phrases(max_pages=15); print(f'Extraídas {len(phrases)} frases')"

# Opción 3: Revisar logs
python3 scraper.py 2>&1 | grep -i error
```

### Problema 5: "Permission denied" al escribir archivo

**Síntomas:**
```
IOError: [Errno 13] Permission denied: 'frases.json'
```

**Causas posibles:**
- Permisos insuficientes en el directorio
- Archivo bloqueado por otro proceso
- Directorio de salida no existe

**Soluciones:**

```bash
# Opción 1: Cambiar permisos del directorio
chmod 755 .

# Opción 2: Cambiar propietario
chown $USER:$USER frases.json

# Opción 3: Ejecutar con permisos elevados (no recomendado)
sudo python3 scraper.py

# Opción 4: Usar directorio diferente
python3 -c "from scraper import QuoteScraper; s = QuoteScraper(); phrases = s.extract_phrases(); s.save_to_json(phrases, '/tmp/frases.json')"
```

### Problema 6: Caracteres especiales corrupto en JSON

**Síntomas:**
- Caracteres acentuados o especiales aparecen como `\uXXXX`
- Emojis o símbolos no se muestran correctamente

**Causas posibles:**
- Encoding incorrecto
- Parámetro `ensure_ascii=True`

**Soluciones:**

```bash
# Opción 1: Verificar encoding del archivo
file frases.json
# Salida esperada: frases.json: UTF-8 Unicode text

# Opción 2: Regenerar con encoding correcto
python3 << 'EOF'
from scraper import QuoteScraper
scraper = QuoteScraper()
phrases = scraper.extract_phrases()
# ensure_ascii=False permite caracteres Unicode
scraper.save_to_json(phrases, ensure_ascii=False)
EOF

# Opción 3: Convertir encoding
iconv -f UTF-8 -t UTF-8 frases.json > frases_fixed.json
mv frases_fixed.json frases.json
```

## Actualización de Dependencias

### Proceso Seguro de Actualización

```bash
# 1. Verificar versiones actuales
pip list

# 2. Crear backup del entorno
pip freeze > requirements_backup.txt

# 3. Actualizar dependencias
pip install --upgrade -r requirements.txt

# 4. Verificar que todo funciona
python3 scraper.py

# 5. Si algo falla, restaurar
pip install -r requirements_backup.txt
```

### Actualización de Python

Si necesitas actualizar Python:

```bash
# 1. Verificar versión actual
python3 --version

# 2. Instalar nueva versión (varía por SO)
# Ubuntu/Debian:
sudo apt-get install python3.11

# macOS:
brew install python@3.11

# 3. Recrear entorno virtual
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Verificar
python3 scraper.py
```

## Monitoreo y Logging

### Niveles de Logging

El scraper soporta diferentes niveles de detalle:

```python
import logging

# DEBUG: Información detallada para diagnóstico
logging.basicConfig(level=logging.DEBUG)

# INFO: Información general (default)
logging.basicConfig(level=logging.INFO)

# WARNING: Solo advertencias y errores
logging.basicConfig(level=logging.WARNING)

# ERROR: Solo errores
logging.basicConfig(level=logging.ERROR)
```

### Redirigir Logs a Archivo

```bash
# Guardar logs en archivo
python3 scraper.py > scraper.log 2>&1

# Ver logs en tiempo real
tail -f scraper.log

# Filtrar solo errores
grep ERROR scraper.log

# Contar eventos por tipo
grep -c INFO scraper.log
grep -c ERROR scraper.log
```

### Análisis de Logs

```bash
# Buscar errores específicos
grep "Connection" scraper.log

# Ver últimas 20 líneas
tail -20 scraper.log

# Ver logs de una hora específica
grep "15:22" scraper.log

# Estadísticas de ejecución
grep "Página" scraper.log | wc -l
```

## Backup y Recuperación

### Estrategia de Backup

```bash
# Backup diario
0 2 * * * cd /path/to/omaigaa && cp frases.json frases.json.$(date +\%Y\%m\%d)

# Backup semanal comprimido
0 3 * * 0 cd /path/to/omaigaa && tar -czf frases_backup_$(date +\%Y\%m\%d).tar.gz frases.json

# Mantener solo últimos 30 días
0 4 * * * find /path/to/omaigaa -name "frases.json.*" -mtime +30 -delete
```

### Restauración de Backup

```bash
# Listar backups disponibles
ls -la frases.json.*

# Restaurar backup específico
cp frases.json.20260810 frases.json

# Restaurar desde archivo comprimido
tar -xzf frases_backup_20260810.tar.gz

# Verificar integridad del JSON
python3 -c "import json; json.load(open('frases.json'))"
```

### Validación de Datos

```bash
# Script de validación
python3 << 'EOF'
import json
from pathlib import Path

def validate_frases_json(filepath="frases.json"):
    """Valida la integridad del archivo frases.json"""
    
    if not Path(filepath).exists():
        print(f"ERROR: {filepath} no existe")
        return False
    
    try:
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            print("ERROR: Raíz no es una lista")
            return False
        
        if len(data) == 0:
            print("WARNING: Lista vacía")
            return False
        
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                print(f"ERROR: Elemento {i} no es diccionario")
                return False
            
            if "author" not in item or "phrase" not in item:
                print(f"ERROR: Elemento {i} falta campos")
                return False
            
            if not isinstance(item["author"], str) or not isinstance(item["phrase"], str):
                print(f"ERROR: Elemento {i} tipos incorrectos")
                return False
        
        print(f"✓ Validación exitosa: {len(data)} frases")
        return True
        
    except json.JSONDecodeError as e:
        print(f"ERROR: JSON inválido: {e}")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

validate_frases_json()
EOF
```

## Checklist de Mantenimiento

### Checklist Mensual

- [ ] Ejecutar scraper y verificar que funciona
- [ ] Revisar logs para errores
- [ ] Hacer backup de `frases.json`
- [ ] Verificar que el sitio es accesible
- [ ] Revisar cambios en dependencias

### Checklist Trimestral

- [ ] Actualizar dependencias
- [ ] Revisar estructura HTML del sitio
- [ ] Actualizar documentación si es necesario
- [ ] Ejecutar pruebas de validación
- [ ] Revisar permisos de archivos

### Checklist Anual

- [ ] Revisar y actualizar Python
- [ ] Auditar seguridad de dependencias
- [ ] Revisar arquitectura del proyecto
- [ ] Documentar cambios significativos
- [ ] Planificar mejoras futuras

---

**Nota:** Esta guía fue creada por Manus AI el 10 de agosto de 2026 como parte de la documentación integral del proyecto.
