from polemista import Polemista


def test_cargar_frases():
    polemista = Polemista()

    assert len(polemista.frases) > 0


def test_embeddings():
    polemista = Polemista()

    assert len(polemista.embeddings) == len(polemista.frases)


def test_busqueda_semantica():
    polemista = Polemista()

    resultados = polemista.buscar_fuentes(
        "¿Es importante aprender y adquirir conocimiento?"
    )

    assert isinstance(resultados, list)


def test_fuentes_tienen_estructura_correcta():
    polemista = Polemista()

    resultados = polemista.buscar_fuentes(
        "¿Qué importancia tiene la imaginación?"
    )

    for resultado in resultados:
        assert "text" in resultado
        assert "author" in resultado
        assert "score" in resultado


def test_fuentes_relevantes_no_vacias():
    """Una pregunta relacionada con la base debe recuperar fuentes."""
    polemista = Polemista()

    resultados = polemista.buscar_fuentes(
        "¿Es más importante el conocimiento o la imaginación?"
    )

    assert len(resultados) > 0


def test_fuentes_irrelevantes_vacias():
    """Una pregunta sin relación debe devolver lista vacía."""
    polemista = Polemista()

    resultados = polemista.buscar_fuentes(
        "¿Cuál es el color favorito del pez globo en Marte?"
    )

    assert resultados == []


def test_validacion_citas():
    polemista = Polemista()

    fuentes = [
        {
            "text": "Knowledge is power.",
            "author": "Francis Bacon",
            "score": 0.8
        }
    ]

    respuesta = (
        'El conocimiento tiene un papel fundamental porque '
        '"Knowledge is power." (Francis Bacon).\n\n'
        'Esta idea permite considerar que adquirir conocimiento '
        'fortalece nuestra capacidad para comprender el mundo.'
    )

    assert polemista._validar_citas(
        respuesta,
        fuentes
    )


def test_ensayo_local_dos_parrafos():
    """El generador local produce exactamente dos párrafos."""
    polemista = Polemista()

    fuentes = [
        {
            "text": "Knowledge is power.",
            "author": "Francis Bacon",
            "score": 0.8
        },
        {
            "text": "Imagination is more important than knowledge.",
            "author": "Albert Einstein",
            "score": 0.7
        }
    ]

    ensayo = polemista._generar_mini_ensayo_local(
        "¿Es más importante el conocimiento o la imaginación?",
        fuentes
    )

    parrafos = [
        p.strip()
        for p in ensayo.split("\n\n")
        if p.strip()
    ]

    assert len(parrafos) == 2


def test_ensayo_local_citas_validas():
    """El generador local cita textualmente las fuentes."""
    polemista = Polemista()

    fuentes = [
        {
            "text": "Knowledge is power.",
            "author": "Francis Bacon",
            "score": 0.8
        },
        {
            "text": "Imagination is more important than knowledge.",
            "author": "Albert Einstein",
            "score": 0.7
        }
    ]

    ensayo = polemista._generar_mini_ensayo_local(
        "¿Es más importante el conocimiento o la imaginación?",
        fuentes
    )

    assert polemista._validar_citas(ensayo, fuentes)
    assert "Knowledge is power." in ensayo
    assert "Imagination is more important than knowledge." in ensayo
