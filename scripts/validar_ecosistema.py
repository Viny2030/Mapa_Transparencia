"""
validar_ecosistema.py — validación cruzada de cifras entre sitios del
Ecosistema de Transparencia (Comprar, Contratos, Monitor, MEACI, Ajuste).

Sólo biblioteca estándar. Cada control termina en OK / ADVERTENCIA / FALLA.
Sale con código 1 si hay alguna FALLA.

Uso:
  python validar_ecosistema.py                 # reporte en consola
  python validar_ecosistema.py --dias 3 --reporte reporte.md
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta

DOM = "ecosistematransparencia.com.ar"
URL = {s: f"https://{s}.{DOM}" for s in ("comprar", "contratos", "monitor", "meaci", "ajuste")}
UA = {"User-Agent": "validar-ecosistema/1.0"}

RESULTADOS: list[tuple[str, str, str]] = []  # (nivel, control, detalle)


def get(url: str, timeout: int = 60):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def registrar(nivel: str, control: str, detalle: str) -> None:
    RESULTADOS.append((nivel, control, detalle))
    icono = {"OK": "✅", "ADVERTENCIA": "⚠️ ", "FALLA": "❌"}[nivel]
    print(f"{icono} [{control}] {detalle}")


def monto_ars(texto) -> float | None:
    """'$7.318.883,55' → 7318883.55 ; números pasan tal cual."""
    if texto is None or texto == "":
        return None
    if isinstance(texto, (int, float)):
        return float(texto)
    s = re.sub(r"[^\d,.\-]", "", str(texto))
    if not s:
        return None
    s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def solo_digitos(c) -> str:
    return re.sub(r"\D", "", str(c or ""))


def fmt(n: float) -> str:
    return f"$ {n:,.0f}".replace(",", ".")


# ── 1. Comprar ↔ Contratos: mismas adjudicaciones BORA por día ───────────────
def control_comprar_vs_contratos(dias: int) -> None:
    for i in range(dias):
        f = (date.today() - timedelta(days=i)).isoformat()
        try:
            a = get(f"{URL['comprar']}/api/licitaciones/datos?fecha={f}").get("flujo") or []
            b = get(f"{URL['contratos']}/api/licitaciones/datos?fecha={f}").get("flujo") or []
        except Exception as e:
            registrar("FALLA", "Comprar↔Contratos", f"{f}: no se pudo consultar ({e})")
            continue
        if not a and not b:
            registrar("OK", "Comprar↔Contratos", f"{f}: ninguno de los dos tiene adjudicaciones (fin de semana/feriado o sin BORA)")
            continue
        la = {x.get("link_bora"): monto_ars(x.get("monto_adjudicado_bora")) for x in a}
        lb = {x.get("link_bora"): monto_ars(x.get("monto")) for x in b}
        solo_a, solo_b = set(la) - set(lb), set(lb) - set(la)
        comunes = set(la) & set(lb)
        dif_monto = [k for k in comunes if la[k] is not None and lb[k] is not None and abs(la[k] - lb[k]) > 1]
        ta = sum(v for v in la.values() if v)
        tb = sum(v for v in lb.values() if v)
        det = (f"{f}: Comprar {len(la)} adj. ({fmt(ta)}) · Contratos {len(lb)} adj. ({fmt(tb)}) · "
               f"sólo en Comprar {len(solo_a)} · sólo en Contratos {len(solo_b)} · monto distinto {len(dif_monto)}")
        nivel = "OK" if not (solo_a or solo_b or dif_monto) else "ADVERTENCIA"
        registrar(nivel, "Comprar↔Contratos", det)


# ── 2. Contratos: coherencia interna resumen vs organismos ───────────────────
def control_contratos_interno() -> None:
    try:
        res = get(f"{URL['contratos']}/api/resumen")
        org = get(f"{URL['contratos']}/api/organismos").get("data") or []
    except Exception as e:
        registrar("FALLA", "Contratos interno", f"no se pudo consultar ({e})")
        return
    suma = sum(o.get("monto_total") or 0 for o in org)
    tot = res.get("monto_total_ars") or 0
    dif = abs(suma - tot) / tot if tot else 1
    nivel = "OK" if dif < 0.005 else "FALLA"
    registrar(nivel, "Contratos interno",
              f"monto_total_ars del resumen {fmt(tot)} vs suma por organismo {fmt(suma)} (dif. {dif:.2%}); "
              f"{len(org)} organismos en la tabla vs organismos_unicos={res.get('organismos_unicos')}")
    total, con_monto = res.get("total") or 0, res.get("con_monto") or 0
    if total:
        cob = con_monto / total
        registrar("ADVERTENCIA" if cob < 0.5 else "OK", "Contratos interno",
                  f"sólo {con_monto} de {total} adjudicaciones ({cob:.0%}) tienen monto: "
                  f"el total en ARS subestima lo adjudicado")


# ── 3. MEACI ↔ Contratos / Comprar ───────────────────────────────────────────
def control_meaci() -> None:
    try:
        emp = get(f"{URL['meaci']}/api/empresas")
        alertas = get(f"{URL['meaci']}/api/alertas")
        resumen = get(f"{URL['meaci']}/api/resumen")
    except Exception as e:
        registrar("FALLA", "MEACI", f"no se pudo consultar ({e})")
        return

    cuit_emp: dict[str, str] = {}
    for e in emp:
        cs = e.get("cuits_ar") or []
        if isinstance(cs, str):
            try:
                cs = json.loads(cs)
            except ValueError:
                cs = [cs]
        for c in cs:
            if solo_digitos(c):
                cuit_emp[solo_digitos(c)] = e.get("nombre_matriz")

    # 3a. resumen vs listados
    if resumen.get("total_empresas") != len(emp):
        registrar("FALLA", "MEACI interno", f"resumen dice {resumen.get('total_empresas')} empresas y /api/empresas trae {len(emp)}")
    else:
        registrar("OK", "MEACI interno", f"{len(emp)} empresas, {len(cuit_emp)} CUIT argentinos")
    if resumen.get("alertas_activas") is not None and resumen["alertas_activas"] != len(alertas):
        registrar("ADVERTENCIA", "MEACI interno", f"resumen dice {resumen['alertas_activas']} alertas activas y /api/alertas trae {len(alertas)}")

    # 3b. la lista de sancionadas es la misma en los tres sitios
    cuits = ",".join(cuit_emp)
    vistos = {}
    for s in ("meaci", "contratos", "comprar"):
        try:
            d = get(f"{URL[s]}/api/cruce-cuits-bulk?cuits={urllib.parse.quote(cuits)}")
            vistos[s] = {solo_digitos(k) for k, v in (d.get("alertas") or {}).items() if v.get("sancionada")}
        except Exception as e:
            registrar("FALLA", "MEACI↔sitios", f"{s}: cruce-cuits-bulk falló ({e})")
    for s, v in vistos.items():
        if s == "meaci":
            continue
        faltan = set(cuit_emp) - v
        if faltan:
            registrar("FALLA", "MEACI↔sitios", f"{s} no marca como sancionadas {len(faltan)} de {len(cuit_emp)} CUIT de MEACI: "
                      + ", ".join(sorted(f"{cuit_emp[c]} ({c})" for c in faltan)[:6]))
        else:
            registrar("OK", "MEACI↔sitios", f"{s} reconoce las {len(cuit_emp)} CUIT sancionadas de MEACI")

    # 3c. ¿las sancionadas aparecen de verdad como proveedoras en Contratos?
    def buscar(q: str):
        d = get(f"{URL['contratos']}/api/proveedores?busqueda={urllib.parse.quote(q)}&top=5")
        return (d.get("data") if isinstance(d, dict) else d) or []

    en_contratos = []
    for c, nombre in cuit_emp.items():
        try:
            filas = buscar(c)
            if filas:
                monto = sum(monto_ars(f.get("monto_adj")) or 0 for f in filas)
                en_contratos.append(f"{nombre} ({c}) {fmt(monto)}")
        except Exception:
            pass
    # Por nombre de filial: una sancionada puede contratar con otro CUIT.
    por_nombre = []
    for e in emp:
        fil = e.get("filiales_ar") or []
        if isinstance(fil, str):
            try:
                fil = json.loads(fil)
            except ValueError:
                fil = [fil]
        for nom in fil:
            clave = re.sub(r"\b(S\.?A\.?U?\.?|S\.?R\.?L\.?|ARGENTINA)\b", "", str(nom), flags=re.I).strip(" .,")
            if len(clave) < 4:
                continue
            try:
                for f in buscar(clave):
                    if solo_digitos(f.get("cuit")) not in cuit_emp:
                        por_nombre.append(f"{nom} ≈ {f.get('nombre')} ({f.get('cuit')}, {f.get('contratos')} contr.)")
            except Exception:
                pass
    if por_nombre:
        registrar("ADVERTENCIA", "MEACI↔Contratos",
                  f"posibles filiales con CUIT distinto al cargado en MEACI (revisar a mano): " + "; ".join(por_nombre[:8]))
    alerta_plat = sorted({a.get("plataforma") for a in alertas})
    registrar("ADVERTENCIA" if not en_contratos else "OK", "MEACI↔Contratos",
              f"{len(alertas)} alertas MEACI etiquetadas {alerta_plat}; de las {len(cuit_emp)} CUIT sancionadas, "
              f"{len(en_contratos)} figuran como proveedoras en Contratos"
              + (": " + "; ".join(en_contratos) if en_contratos else
                 " → las alertas reflejan presencia en Argentina, no contratos detectados"))


# ── 4. Monitor ↔ Contratos ───────────────────────────────────────────────────
def periodo_comprar(fuente: str) -> tuple[int, int] | None:
    """'… COMPR.AR 2016-2026: …' → (2016, 2026); 'COMPR.AR 2024' → (2024, 2024)."""
    m = re.search(r"COMPR\.AR\s+(\d{4})(?:\s*-\s*(\d{4}))?", fuente)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2) or m.group(1))


def control_monitor() -> None:
    try:
        d = get(f"{URL['monitor']}/datos")
    except Exception as e:
        registrar("FALLA", "Monitor", f"no se pudo consultar ({e})")
        return
    filas = d.get("datos") or []
    # Solo los renglones de contratación: el resto (justicia, legislativo…) no tiene ese riesgo.
    contr = [f for f in filas if "monitor_contratos" in str(f.get("Fuente", ""))]
    con_dato = [f for f in contr if str(f.get("Riesgo Contratación", "")).strip() not in ("", "None", "nan")]
    periodos = [p for p in (periodo_comprar(str(f.get("Fuente", ""))) for f in contr) if p]
    detalle = (f"{len(contr)} organismos usan monitor_contratos como fuente; "
               f"{len(con_dato)} tienen 'Riesgo Contratación' con dato")
    if not contr:
        registrar("ADVERTENCIA", "Monitor↔Contratos", "ningún organismo usa monitor_contratos como fuente")
        return
    if not periodos:
        registrar("ADVERTENCIA", "Monitor↔Contratos", detalle + "; la fuente no indica el período de COMPR.AR")
        return
    desde, hasta = min(p[0] for p in periodos), max(p[1] for p in periodos)
    viejo = hasta < date.today().year - 1
    registrar("ADVERTENCIA" if viejo or not con_dato else "OK", "Monitor↔Contratos",
              detalle + f"; datos COMPR.AR {desde}-{hasta}"
              + (" → período desactualizado" if viejo else ""))


# ── 5. Ajuste: auditoría diaria propia ───────────────────────────────────────
def control_ajuste() -> None:
    try:
        runs = get("https://api.github.com/repos/Viny2030/Ajuste/actions/workflows/verificar_cifras.yml/runs?per_page=1")
        r = (runs.get("workflow_runs") or [None])[0]
    except Exception as e:
        registrar("ADVERTENCIA", "Ajuste", f"no se pudo leer la auditoría diaria en GitHub ({e})")
        return
    if not r:
        registrar("ADVERTENCIA", "Ajuste", "verificar_cifras.yml no tiene corridas")
        return
    cuando = r.get("created_at", "")[:10]
    edad = (date.today() - date.fromisoformat(cuando)).days if cuando else 99
    ok = r.get("conclusion") == "success"
    registrar("OK" if ok and edad <= 2 else ("FALLA" if not ok else "ADVERTENCIA"), "Ajuste",
              f"auditoría diaria verificar_cifras (deflactor BCRA, frescura IPC, total presupuesto, normativa): "
              f"última corrida {cuando} → {r.get('conclusion')}")


# ── 6. Frescura ──────────────────────────────────────────────────────────────
def control_frescura() -> None:
    hoy = date.today()
    fechas = {}
    try:
        fechas["comprar"] = get(f"{URL['comprar']}/api/status").get("ultimo_reporte")
    except Exception:
        pass
    try:
        fechas["contratos"] = (get(f"{URL['contratos']}/api/resumen").get("timestamp") or "")[:10]
    except Exception:
        pass
    try:
        fechas["monitor"] = (get(f"{URL['monitor']}/info").get("datos_actualizados") or "")[:10]
    except Exception:
        pass
    try:
        fechas["meaci (novedades)"] = (get(f"{URL['meaci']}/api/novedades").get("ultima_revision") or "")[:10]
    except Exception:
        pass
    for s, f in fechas.items():
        try:
            edad = (hoy - date.fromisoformat(f)).days
        except (TypeError, ValueError):
            registrar("ADVERTENCIA", "Frescura", f"{s}: sin fecha legible ({f!r})")
            continue
        registrar("OK" if edad <= 2 else "ADVERTENCIA", "Frescura", f"{s}: datos del {f} (hace {edad} días)")


def main() -> int:
    try:  # consola de Windows (cp1252) no imprime emojis
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--dias", type=int, default=3, help="días hacia atrás para Comprar↔Contratos")
    ap.add_argument("--reporte", help="escribir reporte Markdown en esta ruta")
    a = ap.parse_args()

    print(f"Validación cruzada del ecosistema — {datetime.now():%Y-%m-%d %H:%M}\n")
    control_frescura()
    control_comprar_vs_contratos(a.dias)
    control_contratos_interno()
    control_meaci()
    control_monitor()
    control_ajuste()

    n = {k: sum(1 for r in RESULTADOS if r[0] == k) for k in ("OK", "ADVERTENCIA", "FALLA")}
    print(f"\nResumen: {n['OK']} OK · {n['ADVERTENCIA']} advertencias · {n['FALLA']} fallas")

    if a.reporte:
        with open(a.reporte, "w", encoding="utf-8") as fh:
            fh.write(f"# Validación cruzada del ecosistema — {date.today()}\n\n")
            fh.write(f"**{n['OK']} OK · {n['ADVERTENCIA']} advertencias · {n['FALLA']} fallas**\n\n")
            fh.write("| Nivel | Control | Detalle |\n|---|---|---|\n")
            for nivel, ctrl, det in RESULTADOS:
                fh.write(f"| {nivel} | {ctrl} | {det.replace('|', '/')} |\n")
    return 1 if n["FALLA"] else 0


if __name__ == "__main__":
    sys.exit(main())
