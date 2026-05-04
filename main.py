from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI(title="Mapa Transparencia")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok", "mensaje": "Mapa Transparencia API funcionando"}


@app.get("/health")
def health():
    return {"status": "healthy"}


# ── Endpoint principal: consulta datos de transparencia ──────────────────────
@app.get("/transparencia")
async def get_transparencia(provincia: str = None, anio: int = None):
    """
    Devuelve datos de transparencia presupuestaria.
    Parámetros opcionales: provincia, anio
    """
    params = {}
    if provincia:
        params["provincia"] = provincia
    if anio:
        params["anio"] = anio

    # URL base del portal de datos abiertos de Argentina
    url = "https://apis.datos.gob.ar/series/api/series/"

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        return {"error": str(e), "datos": []}


@app.get("/provincias")
def get_provincias():
    """Lista de provincias argentinas disponibles"""
    provincias = [
        "Buenos Aires", "CABA", "Catamarca", "Chaco", "Chubut",
        "Córdoba", "Corrientes", "Entre Ríos", "Formosa", "Jujuy",
        "La Pampa", "La Rioja", "Mendoza", "Misiones", "Neuquén",
        "Río Negro", "Salta", "San Juan", "San Luis", "Santa Cruz",
        "Santa Fe", "Santiago del Estero", "Tierra del Fuego", "Tucumán"
    ]
    return {"provincias": provincias}
