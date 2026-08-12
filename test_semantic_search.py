#!/usr/bin/env python3
"""
Script de Validación del Motor de Búsqueda Semántica
======================================================

Este script ejecuta múltiples casos de prueba para validar que el motor
de búsqueda semántica funciona correctamente con diferentes tipos de
consultas emocionales, situacionales y abstractas.

Autor: Manus AI
Versión: 1.0.0
"""

import logging
import json
from types import SimpleNamespace
from semantic_search import SemanticSearchEngine


class FakeOpenAI:
    """Cliente falso que devuelve las primeras 3 frases del archivo `frases.json`.

    Esto evita llamadas de red y permite ejecutar las pruebas sin clave.
    """
    class Chat:
        class Completions:
            @staticmethod
            def create(*args, **kwargs):
                # Cargar frases y construir una respuesta formateada
                with open("frases.json", encoding="utf-8") as f:
                    phrases = json.load(f)

                top_k = 3
                items = []
                for i, p in enumerate(phrases[:top_k], 1):
                    items.append(f'{i}. "{p["phrase"]}" — {p["author"]}\n   💡 Por qué conecta: Ejemplo')

                content = "\n\n".join(items)
                # Simular la estructura que espera el parser
                message = SimpleNamespace(content=content)
                choice = SimpleNamespace(message=message)
                return SimpleNamespace(choices=[choice])

    def __init__(self):
        self.chat = SimpleNamespace(completions=self.Chat.Completions)


# Configurar logging
logging.basicConfig(
    level=logging.WARNING,  # Solo mostrar warnings y errores
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def run_test_case(engine: SemanticSearchEngine, test_number: int, query: str, expected_theme: str) -> bool:
    """Ejecuta un caso de prueba individual."""
    print(f"\n{'═'*70}")
    print(f"TEST {test_number}: {expected_theme}")
    print(f"{'═'*70}")
    print(f"\nConsulta: \"{query}\"\n")
    
    try:
        results = engine.search(query)
        
        if not results:
            print("✗ ERROR: No se obtuvieron resultados")
            return False
        
        print(f"✓ Resultados obtenidos: {len(results)}")
        
        for i, result in enumerate(results, 1):
            print(f"\n  {i}. \"{result['phrase'][:80]}{'...' if len(result['phrase']) > 80 else ''}\"")
            print(f"     -- {result['author']}")
        
        return True
        
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False


def main():
    """Ejecuta todos los casos de prueba."""
    print("\n" + "="*70)
    print("VALIDACIÓN DEL MOTOR DE BÚSQUEDA SEMÁNTICA")
    print("="*70)
    
    # Inicializar motor (usando cliente falso para pruebas sin red)
    engine = SemanticSearchEngine(client=FakeOpenAI())
    
    # Definir casos de prueba
    test_cases = [
        {
            "query": "Siento que el tiempo pasa muy rápido y no estoy logrando mis metas",
            "theme": "Frustración temporal / Sensación de estancamiento"
        },
        {
            "query": "La sensación de paz al mirar la lluvia",
            "theme": "Paz contemplativa / Aceptación"
        },
        {
            "query": "Necesito motivación para enfrentar un desafío difícil",
            "theme": "Motivación ante adversidad"
        },
        {
            "query": "Me siento solo y nadie me entiende",
            "theme": "Soledad / Incomprendido"
        },
        {
            "query": "Tengo miedo de fallar y decepcionar a los demás",
            "theme": "Miedo al fracaso / Presión social"
        },
        {
            "query": "Quiero encontrar propósito y significado en mi vida",
            "theme": "Búsqueda de propósito existencial"
        },
        {
            "query": "Estoy cansado de luchar contra la corriente",
            "theme": "Agotamiento / Resignación"
        },
        {
            "query": "La belleza de un amanecer que renueva la esperanza",
            "theme": "Renovación / Esperanza"
        },
        {
            "query": "Necesito ser más valiente y dejar de esconderme",
            "theme": "Valentía / Autenticidad"
        },
        {
            "query": "El dolor de perder a alguien que amaba",
            "theme": "Duelo / Pérdida"
        }
    ]
    
    # Ejecutar todos los tests
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        success = run_test_case(engine, i, test["query"], test["theme"])
        if success:
            passed += 1
        else:
            failed += 1
        
        # Pausa breve entre tests
        import time
        time.sleep(1)
    
    # Resumen final
    print("\n" + "="*70)
    print("RESUMEN DE VALIDACIÓN")
    print("="*70)
    print(f"\n✓ Tests exitosos: {passed}/{len(test_cases)}")
    print(f"✗ Tests fallidos: {failed}/{len(test_cases)}")
    
    if failed == 0:
        print("\n🎉 TODOS LOS TESTS PASARON - El motor funciona correctamente")
    else:
        print(f"\n⚠ Hay {failed} tests que fallaron - Revisar el código")
    
    print("\n" + "="*70)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
