from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pathlib import Path
import httpx
import os

app = FastAPI(title="Mapa de Transparencia del Estado Argentino", version="1.0.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

SERVICES = {
    "contratos":    os.getenv("CONTRATOS_API_URL",   "https://gobbocomprartgn-production.up.railway.app"),
    "contratos_v2": os.getenv("CONTRATOS_V2_API_URL","https://monitorcontratosv2-production-65d2.up.railway.app"),
    "ejecutivo":    os.getenv("EJECUTIVO_API_URL",   "https://jefaturagabinete-production.up.railway.app"),
    "justicia":     os.getenv("JUSTICIA_API_URL",    "https://justicia-production-6a54.up.railway.app"),
    "diputados":    os.getenv("LEGISTATIVO_API_URL", "https://monitorlegistativo-production.up.railway.app"),
    "senadores":    os.getenv("SENADORES_API_URL",   "https://monitorlegistativosenadores-production.up.railway.app"),
    "iri":          os.getenv("IRI_API_URL",         "https://monitor-production-f053.up.railway.app"),
}

HTML_CONTENT = """... (tu HTML español existente, sin cambios) ..."""


@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse(content=HTML_CONTENT)

@app.get("/en", response_class=HTMLResponse)
async def landing_en():
    path = Path("landing_en.html")
    return HTMLResponse(content=path.read_text(encoding="utf-8"))

@app.get("/health")
def health():
    return {"status": "healthy", "service": "Mapa Transparencia"}

@app.get("/servicios")
def servicios():
    return {"servicios": [{"id": k, "url": v} for k, v in SERVICES.items()]}

@app.get("/status")
async def status():
    resultados = {}
    async with httpx.AsyncClient(timeout=5) as client:
        for nombre, url in SERVICES.items():
            try:
                r = await client.get(url)
                resultados[nombre] = {"url": url, "status": r.status_code, "ok": r.status_code < 400}
            except Exception as e:
                resultados[nombre] = {"url": url, "status": None, "ok": False, "error": str(e)}
    return resultados

@app.get("/iri/datos")
async def iri_datos():
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{SERVICES['iri']}/datos")
        r.raise_for_status()
        return r.json()

@app.get("/iri/top-riesgo")
async def iri_top(n: int = 10):
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{SERVICES['iri']}/top-riesgo", params={"n": n})
        r.raise_for_status()
        return r.json()

@app.get("/iri/resumen")
async def iri_resumen():
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{SERVICES['iri']}/resumen")
        r.raise_for_status()
        return r.json()
