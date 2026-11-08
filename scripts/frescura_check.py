"""
frescura_check.py — alarma central de frescura de datos del ecosistema
======================================================================
Recorre los sitios de frescura/sitios.json y arma un informe con dos
listas separadas:

* Alarmas técnicas: el sitio no responde, o un dato no se cargó dentro
  del plazo esperado (falló el pipeline o la fuente no respondió).
  Se arreglan con código.
* Alarmas de contenido: la fuente oficial no publicó un dato nuevo (por
  ejemplo, el último recibo de dieta del Senado es de enero). Son trabajo
  de búsqueda, no de código. Van aparte para que no se vuelvan ruido.

Si un sitio publica /api/frescura (formato frescura/1) se usan sus datos;
si no, solo se controla que la página responda.

Uso:
    python scripts/frescura_check.py                 # imprime el informe
    python scripts/frescura_check.py --salida informe.md --json estado.json

El workflow .github/workflows/frescura.yml lo corre todos los días y abre,
actualiza o cierra un único issue con la etiqueta "frescura".
Solo usa la biblioteca estándar.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITIOS = os.path.join(RAIZ, "frescura", "sitios.json")
UA = "EcosistemaTransparencia-Frescura/1.0"
TIMEOUT = 45


def _get(url: str, timeout: int = TIMEOUT):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json, text/html"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.headers.get("Content-Type", ""), r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Content-Type", "") if e.headers else "", b""
    except Exception as e:  # timeout, DNS, TLS…
        return 0, str(e)[:120], b""


def revisar_sitio(sitio: dict, get=_get) -> dict:
    base = sitio["url"].rstrip("/")
    res = {"id": sitio["id"], "nombre": sitio["nombre"], "url": sitio["url"],
           "responde": False, "con_ficha": False, "tecnicas": [], "contenido": [], "al_dia": 0}

    status, ctype, cuerpo = get(base + "/api/frescura")
    if status == 200 and "json" in ctype:
        try:
            data = json.loads(cuerpo.decode("utf-8"))
        except ValueError:
            data = None
        if isinstance(data, dict) and str(data.get("formato", "")).startswith("frescura/"):
            res["responde"] = res["con_ficha"] = True
            res["datos"] = data.get("datos", [])
            for d in data.get("datos", []):
                fila = {"dato": d.get("dato") or d.get("id"), "periodo": d.get("periodo"),
                        "fuente": d.get("fuente"), "dias_desde_carga": d.get("dias_desde_carga"),
                        "dias_desde_periodo": d.get("dias_desde_periodo"), "nota": d.get("nota")}
                if d.get("estado") == "atrasado_tecnico":
                    res["tecnicas"].append(fila)
                elif d.get("estado") == "atrasado_contenido":
                    res["contenido"].append(fila)
                else:
                    res["al_dia"] += 1
            return res

    # Sin ficha: alcanza con que la página principal responda
    status, detalle, _ = get(sitio["url"])
    if 200 <= status < 400:
        res["responde"] = True
    else:
        res["tecnicas"].append({"dato": "Sitio", "periodo": None, "fuente": None,
                                "nota": f"no responde (HTTP {status or 'sin conexión'}{': ' + detalle if not status else ''})"})
    return res


def informe_md(resultados: list[dict], ahora: str) -> str:
    tec = [(r, f) for r in resultados for f in r["tecnicas"]]
    con = [(r, f) for r in resultados for f in r["contenido"]]
    lin = [f"Control diario de frescura — {ahora}", ""]
    lin.append(f"**{len(tec)} alarmas técnicas** · **{len(con)} alarmas de contenido** · "
               f"{sum(r['responde'] for r in resultados)}/{len(resultados)} sitios responden · "
               f"{sum(r['con_ficha'] for r in resultados)} con ficha de frescura")
    lin += ["", "## 🔴 Técnicas (se arreglan con código)", ""]
    if tec:
        lin.append("| Sitio | Dato | Detalle |")
        lin.append("|---|---|---|")
        for r, f in tec:
            det = f.get("nota") or (f"última carga hace {f['dias_desde_carga']} días" if f.get("dias_desde_carga") is not None else "sin fecha de carga")
            lin.append(f"| [{r['nombre']}]({r['url']}) | {f['dato']} | {det} |")
    else:
        lin.append("Ninguna.")
    lin += ["", "## 🟡 Contenido (dato viejo o pendiente de revisar: no se arregla con código)", ""]
    if con:
        lin.append("| Sitio | Dato | Período que cubre | Fuente | Nota |")
        lin.append("|---|---|---|---|---|")
        for r, f in con:
            per = f.get("periodo") or "—"
            if f.get("dias_desde_periodo") is not None:
                per += f" (hace {f['dias_desde_periodo']} días)"
            lin.append(f"| [{r['nombre']}]({r['url']}) | {f['dato']} | {per} | {f.get('fuente') or '—'} | {f.get('nota') or '—'} |")
    else:
        lin.append("Ninguna.")
    sin = [r["nombre"] for r in resultados if r["responde"] and not r["con_ficha"]]
    if sin:
        lin += ["", f"Sitios sin `/api/frescura` (solo se controla que respondan): {', '.join(sin)}."]
    lin += ["", "_Generado por `scripts/frescura_check.py` · formato `frescura/1`._"]
    return "\n".join(lin)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", help="archivo Markdown del informe")
    ap.add_argument("--json", help="archivo JSON con el estado")
    a = ap.parse_args(argv)
    with open(SITIOS, encoding="utf-8") as f:
        sitios = json.load(f)["sitios"]
    resultados = [revisar_sitio(s) for s in sitios]
    ahora = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    md = informe_md(resultados, ahora)
    print(md)
    estado = {"generado": ahora,
              "tecnicas": sum(len(r["tecnicas"]) for r in resultados),
              "contenido": sum(len(r["contenido"]) for r in resultados),
              "sitios": resultados}
    if a.salida:
        with open(a.salida, "w", encoding="utf-8") as f:
            f.write(md)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(estado, f, ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
