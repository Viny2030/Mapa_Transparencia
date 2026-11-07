"""Coherencia de funcionamiento.json (grafos de funcionamiento de cada sitio)."""
import json
import os

RUTA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "funcionamiento.json")
COLUMNAS = {"fuente", "proceso", "dato", "salida"}


def _datos():
    with open(RUTA, encoding="utf-8") as f:
        return json.load(f)


def test_columnas_en_dos_idiomas():
    d = _datos()
    assert set(d["columnas"]) == COLUMNAS
    assert all(v["es"] and v["en"] for v in d["columnas"].values())


def test_cada_nodo_tiene_nombre_y_descripcion_en_es_y_en():
    for clave, s in _datos()["sitios"].items():
        assert s["nombre"]["es"] and s["nombre"]["en"] and s["url"].startswith("https://"), clave
        ids = [n["id"] for n in s["nodos"]]
        assert len(ids) == len(set(ids)), f"{clave}: ids repetidos"
        for n in s["nodos"]:
            assert n["col"] in COLUMNAS, (clave, n["id"])
            for campo in ("nom", "sub"):
                assert n[campo]["es"].strip() and n[campo]["en"].strip(), (clave, n["id"], campo)


def test_aristas_entre_nodos_existentes_y_sin_nodos_sueltos():
    for clave, s in _datos()["sitios"].items():
        ids = {n["id"] for n in s["nodos"]}
        usados = set()
        for a, b in s["aristas"]:
            assert a in ids and b in ids, (clave, a, b)
            usados |= {a, b}
        assert ids == usados, f"{clave}: nodos sin aristas {ids - usados}"
        # cada sitio arranca en una fuente y termina en algo que publica
        cols = {n["col"] for n in s["nodos"]}
        assert {"fuente", "salida"} <= cols, clave
