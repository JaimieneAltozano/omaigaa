## Instalación

Este proyecto implementa dos motores:

1. **Buscador de "Vibras" o Emociones** — analiza la intención de una
   frase y devuelve las 3 citas que mejor conectan (sin palabras clave).
2. **Orador de Debates Respaldado** — responde una pregunta con un
   mini-ensayo de dos párrafos que cita textualmente las fuentes de la
   base de datos.

Desde la carpeta del proyecto:

### 1. Crear el entorno virtual (venv)

> **Nota para Windows**: Los entornos virtuales creados en Linux/macOS no funcionan en Windows. En Windows debes crear un nuevo `venv` propio de la plataforma.

**En Windows (PowerShell / CMD):**
```powershell
python -m venv venv
```

**En Linux / macOS:**
```bash
python3 -m venv venv
```

---

### 2. Activar el entorno virtual

**En Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
# O simplemente:
.\venv\Scripts\activate
```
*(Si PowerShell bloquea la ejecución de scripts, ejecuta una sola vez: `Set-ExecutionPolicy -Scope Process Bypass`)*

**En Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**En Linux / macOS:**
```bash
source venv/bin/activate
```

---

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

### 4. Generar la base de frases (Primera ejecución)

Si es la primera vez que ejecutas el proyecto o no tienes el archivo `frases.json`, ejecuta el scraper:

```bash
python scraper.py
```

---

### 5. Configurar la API (Opcional)

Solo si quieres usar OpenAI en lugar de la generación local del mini-ensayo:

**En Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="TU_API_KEY"
```

**En Windows (CMD):**
```cmd
set OPENAI_API_KEY="TU_API_KEY"
```

**En Linux / macOS:**
```bash
export OPENAI_API_KEY="TU_API_KEY"
```

---

### 6. Ejecución del proyecto

#### Opción A: Interfaz Web (Servidor Flask)

```bash
python app.py
```

Abre en tu navegador:
```text
http://127.0.0.1:5000
```

#### Opción B: Ejecutar en Terminal

```bash
# Orador de debates (mini-ensayo con citas textuales)
python polemista.py

# Buscador de vibras (3 frases según tu emoción)
python semantic_search_local.py
```

El orador de debates funciona **sin API** (plantilla local con citas).
Si defines `OPENAI_API_KEY`, usa OpenAI para redactar el ensayo.

Deberías obtener algo parecido a:

```text
============================================================
              POLEMISTA FILOSÓFICO
============================================================

Escribe una pregunta filosófica.
Escribe 'salir' para terminar.

Tú: ¿Es más importante el conocimiento o la imaginación?

Buscando fuentes...

------------------------------------------------------------
[mini-ensayo de dos párrafos]
------------------------------------------------------------

Fuentes recuperadas:
- [0.71] "..." (Autor)
- [0.64] "..." (Autor)
- [0.52] "..." (Autor)
```

Abrir la interfaz:

```bash
python app.py
```

Abrir:

```text
http://127.0.0.1:5000
```

### ⚠️ Una decisión importante del diseño

Aquí está la parte que hace que esto sea realmente un **RAG/polemista** y no simplemente un chatbot:

```text
                 BASE DE DATOS
                       │
                  100 frases
                       │
                       ▼
              ┌─────────────────┐
              │ Búsqueda         │
              │ semántica        │
              └────────┬────────┘
                       │
                 Top 5 frases
                       │
                       ▼
               ┌─────────────────┐
               │ Modelo LLM      │
               │ o plantilla     │
               │ local con citas │
               │ SOLO recibe     │
               │ esas fuentes    │
               └────────┬────────┘
                       │
                       ▼
                Mini-ensayo
                       │
                       ▼
              ┌─────────────────┐
              │ VALIDACIÓN      │
              │                 │
              │ ¿Las citas      │
              │ existen?        │
              └────────┬────────┘
                       │
                       ▼
                    Usuario
```

Eso además te permite explicar en una sustentación que implementaste **recuperación semántica + generación aumentada por recuperación (RAG) + grounding + validación de citas**. Es bastante más sólido que simplemente conectar un chatbot a la API.