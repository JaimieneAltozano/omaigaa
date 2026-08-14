## Instalación

Este proyecto implementa dos motores:

1. **Buscador de "Vibras" o Emociones** — analiza la intención de una
   frase y devuelve las 3 citas que mejor conectan (sin palabras clave).
2. **Orador de Debates Respaldado** — responde una pregunta con un
   mini-ensayo de dos párrafos que cita textualmente las fuentes de la
   base de datos.

Desde la carpeta del proyecto:

```bash
python3 -m venv venv
```

Activar:

```bash
source venv/bin/activate
```

Instalar:

```bash
pip install -r requirements.txt
```

Configurar la API (opcional, solo si quieres usar OpenAI en lugar de
la generación local del mini-ensayo):

```bash
export OPENAI_API_KEY="TU_API_KEY"
```

Ejecutar primero la versión de terminal:

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

Y después puedes levantar la interfaz:

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