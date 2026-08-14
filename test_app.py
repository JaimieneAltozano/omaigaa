#!/usr/bin/env python3
"""
Suite de Pruebas - Servidor Flask (Buscador de Vibras + Orador de Debates)
=============================================================================

Pruebas del servidor web unificado usando el test client de Flask
(sin levantar el servidor real).

Ejecución:
    python test_app.py
    # o
    python -m unittest test_app -v
"""

import unittest

from app import app


class FrasotecaAppTestCase(unittest.TestCase):
    """Casos de prueba para el servidor Flask."""

    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()

    def test_index_ok(self):
        """GET / debe devolver la página principal (200)."""
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Frasoteca'.encode(), resp.data)
        self.assertIn('text/html', resp.content_type)

    def test_static_css_ok(self):
        """El CSS estático debe servirse correctamente."""
        resp = self.client.get('/static/css/style.css')
        self.assertEqual(resp.status_code, 200)

    def test_static_js_ok(self):
        """El JS estático debe servirse correctamente."""
        resp = self.client.get('/static/js/app.js')
        self.assertEqual(resp.status_code, 200)

    def test_health_ok(self):
        """GET /api/health debe reportar estado ok."""
        resp = self.client.get('/api/health')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['status'], 'ok')
        self.assertFalse(data['ai_used'])
        self.assertEqual(data['method'], 'cosine_similarity')
        self.assertGreaterEqual(data['total_phrases'], 100)

    def test_search_valid(self):
        """POST /api/search con consulta válida devuelve 3 resultados."""
        resp = self.client.post(
            '/api/search',
            json={'query': 'Me siento perdido en la vida'}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(len(data['results']), 3)
        for result in data['results']:
            self.assertIn('phrase', result)
            self.assertIn('author', result)
            self.assertIn('score_percent', result)
        self.assertIn('search_time_ms', data)

    def test_search_missing_query(self):
        """POST sin campo 'query' debe devolver 400."""
        resp = self.client.post('/api/search', json={})
        self.assertEqual(resp.status_code, 400)
        self.assertIn('error', resp.get_json())

    def test_search_empty_query(self):
        """POST con query vacía o solo espacios debe devolver 400."""
        for bad_query in ('', '   ', '\n\t'):
            resp = self.client.post(
                '/api/search',
                json={'query': bad_query}
            )
            self.assertEqual(resp.status_code, 400)

    def test_search_duplicate_phrases(self):
        """Consultas repetidas deben dar resultados coherentes."""
        payload = {'query': 'La sensación de paz al mirar la lluvia'}
        first = self.client.post('/api/search', json=payload).get_json()
        second = self.client.post('/api/search', json=payload).get_json()
        self.assertEqual(
            [r['phrase'] for r in first['results']],
            [r['phrase'] for r in second['results']]
        )

    def test_debate_valid(self):
        """POST /api/debate genera un mini-ensayo con fuentes."""
        resp = self.client.post(
            '/api/debate',
            json={'pregunta': '¿Es más importante el conocimiento o la imaginación?'}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertIn('answer', data)
        self.assertGreater(len(data['sources']), 0)
        # El mini-ensayo debe citar al menos una fuente textualmente.
        alguna_fuente_citada = any(
            fuente['text'] in data['answer']
            for fuente in data['sources']
        )
        self.assertTrue(alguna_fuente_citada)

    def test_debate_sin_fuentes(self):
        """Preguntas sin relación deben admitir falta de fuentes."""
        resp = self.client.post(
            '/api/debate',
            json={'pregunta': '¿Cuál es el color favorito del pez globo en Marte?'}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertFalse(data['success'])
        self.assertEqual(len(data['sources']), 0)

    def test_debate_missing_pregunta(self):
        """POST sin campo 'pregunta' debe devolver 400."""
        resp = self.client.post('/api/debate', json={})
        self.assertEqual(resp.status_code, 400)
        self.assertIn('error', resp.get_json())

    def test_index_conecta_frontend_backend(self):
        """El frontend debe enlazar el CSS y el JS que consumen la API."""
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'/static/css/style.css', resp.data)
        self.assertIn(b'/static/js/app.js', resp.data)
        self.assertIn(b'vibes-form', resp.data)
        self.assertIn(b'debate-form', resp.data)

    def test_index_get_solo(self):
        """POST / ya no es el mecanismo del frontend (usa la API JSON)."""
        resp = self.client.post('/', data={'modo': 'vibes', 'consulta': 'Me siento solo'})
        self.assertEqual(resp.status_code, 405)


if __name__ == '__main__':
    unittest.main(verbosity=2)
