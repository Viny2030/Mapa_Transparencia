"""scripts/frescura_check.py — alarma central de frescura (sin red)."""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

import frescura_check as fc  # noqa: E402

FICHA = {
    "formato": "frescura/1", "sitio": "senadores",
    "datos": [
        {"id": "nomina", "dato": "Nómina", "estado": "al_dia"},
        {"id": "dieta", "dato": "Dieta (recibo oficial)", "estado": "atrasado_contenido",
         "periodo": "recibo de Enero 2026", "dias_desde_periodo": 279, "fuente": "senado.gob.ar"},
        {"id": "comisiones", "dato": "Comisiones", "estado": "atrasado_tecnico", "dias_desde_carga": 9},
    ],
}


def fake_get(respuestas):
    def get(url, timeout=None):
        return respuestas.get(url, (404, "text/html", b""))
    return get


def test_sitio_con_ficha_separa_tecnicas_y_contenido():
    get = fake_get({"https://s.example/api/frescura": (200, "application/json", json.dumps(FICHA).encode())})
    r = fc.revisar_sitio({"id": "s", "nombre": "S", "url": "https://s.example/"}, get=get)
    assert r["responde"] and r["con_ficha"]
    assert r["al_dia"] == 1
    assert [f["dato"] for f in r["contenido"]] == ["Dieta (recibo oficial)"]
    assert [f["dato"] for f in r["tecnicas"]] == ["Comisiones"]


def test_sitio_sin_ficha_solo_controla_que_responda():
    ok = fc.revisar_sitio({"id": "a", "nombre": "A", "url": "https://a.example/"},
                          get=fake_get({"https://a.example/": (200, "text/html", b"<html>")}))
    assert ok["responde"] and not ok["con_ficha"] and not ok["tecnicas"]
    caido = fc.revisar_sitio({"id": "b", "nombre": "B", "url": "https://b.example/"},
                             get=fake_get({"https://b.example/": (0, "timed out", b"")}))
    assert not caido["responde"]
    assert caido["tecnicas"][0]["dato"] == "Sitio" and "no responde" in caido["tecnicas"][0]["nota"]


def test_informe_lista_las_dos_alarmas_por_separado():
    get = fake_get({"https://s.example/api/frescura": (200, "application/json", json.dumps(FICHA).encode())})
    r = fc.revisar_sitio({"id": "s", "nombre": "SENADORES", "url": "https://s.example/"}, get=get)
    md = fc.informe_md([r], "2026-11-06 12:00 UTC")
    assert "**1 alarmas técnicas** · **1 alarmas de contenido**" in md
    tec, con = md.split("## 🟡")
    assert "Comisiones" in tec and "última carga hace 9 días" in tec
    assert "Dieta (recibo oficial)" in con and "hace 279 días" in con
