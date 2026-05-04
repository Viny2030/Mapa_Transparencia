from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import httpx
import os

app = FastAPI(
    title="Mapa de Transparencia del Estado Argentino",
    description="Portal central que integra todos los monitores de transparencia",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── URLs de los servicios integrados ────────────────────────────────────────
SERVICES = {
    "contratos":    os.getenv("CONTRATOS_API_URL",   "https://gobbocomprartgn-production.up.railway.app"),
    "contratos_v2": os.getenv("CONTRATOS_V2_API_URL","https://monitorcontratosv2-production.up.railway.app"),
    "ejecutivo":    os.getenv("EJECUTIVO_API_URL",   "https://jefaturagabinete-production.up.railway.app"),
    "justicia":     os.getenv("JUSTICIA_API_URL",    "https://justicia-production-6a54.up.railway.app"),
    "diputados":    os.getenv("LEGISTATIVO_API_URL", "https://monitorlegistativo-production.up.railway.app"),
    "senadores":    os.getenv("SENADORES_API_URL",   "https://monitorlegistativosenadores-production.up.railway.app"),
    "iri":          os.getenv("IRI_API_URL",         "https://monitor-production-f053.up.railway.app"),
}

HTML_CONTENT = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Mapa de Transparencia · Estado Argentino</title>
<style>
  :root {
    --azul:    #003f8a;
    --celeste: #74b2e2;
    --blanco:  #ffffff;
    --gris:    #f4f6f9;
    --verde:   #27ae60;
    --amarillo:#f39c12;
    --rojo:    #e74c3c;
    --texto:   #1a1a2e;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Segoe UI', system-ui, sans-serif;
    background: var(--gris);
    color: var(--texto);
  }
  header {
    background: linear-gradient(135deg, var(--azul) 0%, #005bb5 100%);
    color: white;
    padding: 2rem 1.5rem 1.5rem;
    text-align: center;
  }
  header h1 { font-size: 1.9rem; font-weight: 700; letter-spacing: -0.5px; }
  header p  { font-size: 0.95rem; opacity: 0.85; margin-top: 0.4rem; }
  .badge {
    display: inline-block;
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 20px;
    padding: 0.2rem 0.8rem;
    font-size: 0.78rem;
    margin-top: 0.6rem;
  }
  nav {
    background: var(--azul);
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    padding: 0.6rem 1rem;
    flex-wrap: wrap;
  }
  nav a {
    color: rgba(255,255,255,0.8);
    text-decoration: none;
    font-size: 0.82rem;
    padding: 0.3rem 0.7rem;
    border-radius: 4px;
    transition: background 0.2s;
  }
  nav a:hover { background: rgba(255,255,255,0.15); color: white; }

  .hero {
    max-width: 900px;
    margin: 2rem auto 0;
    padding: 0 1rem;
    text-align: center;
  }
  .hero h2 { font-size: 1.3rem; color: var(--azul); margin-bottom: 0.5rem; }
  .hero p  { color: #555; font-size: 0.93rem; line-height: 1.6; }

  /* ── Poderes ── */
  .poderes {
    max-width: 1100px;
    margin: 2.5rem auto;
    padding: 0 1rem;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
  }
  .poder {
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
    overflow: hidden;
  }
  .poder-header {
    padding: 1rem 1.2rem;
    display: flex;
    align-items: center;
    gap: 0.7rem;
  }
  .poder-header .icon { font-size: 1.8rem; }
  .poder-header h3   { font-size: 1rem; font-weight: 700; }
  .poder-header p    { font-size: 0.78rem; opacity: 0.8; }

  .poder-ejecutivo .poder-header  { background: linear-gradient(135deg,#003f8a,#0062cc); color:white; }
  .poder-legislativo .poder-header{ background: linear-gradient(135deg,#7b2d8b,#a855f7); color:white; }
  .poder-judicial .poder-header   { background: linear-gradient(135deg,#b5451b,#e8622a); color:white; }
  .poder-fiscal .poder-header     { background: linear-gradient(135deg,#1a7a4a,#27ae60); color:white; }
  .poder-iri .poder-header        { background: linear-gradient(135deg,#1a1a2e,#16213e); color:white; }

  .monitor-list { padding: 0.8rem; }
  .monitor-item {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    padding: 0.75rem 0.8rem;
    border-radius: 8px;
    text-decoration: none;
    color: var(--texto);
    transition: background 0.18s;
    border-bottom: 1px solid #f0f0f0;
  }
  .monitor-item:last-child { border-bottom: none; }
  .monitor-item:hover { background: var(--gris); }
  .monitor-item .mi-icon { font-size: 1.3rem; width: 2rem; text-align: center; }
  .monitor-item .mi-info { flex: 1; }
  .monitor-item .mi-title { font-size: 0.88rem; font-weight: 600; }
  .monitor-item .mi-desc  { font-size: 0.76rem; color: #777; margin-top: 0.1rem; }
  .mi-status {
    font-size: 0.7rem;
    padding: 0.15rem 0.5rem;
    border-radius: 10px;
    font-weight: 600;
  }
  .status-live    { background:#d4edda; color:#155724; }
  .status-demo    { background:#fff3cd; color:#856404; }
  .status-pronto  { background:#e2e3e5; color:#383d41; }

  /* ── Stats bar ── */
  .stats {
    max-width: 900px;
    margin: 0 auto 2rem;
    padding: 0 1rem;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 1rem;
  }
  .stat-card {
    background: white;
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  }
  .stat-card .num  { font-size: 1.6rem; font-weight: 700; color: var(--azul); }
  .stat-card .label{ font-size: 0.75rem; color: #666; margin-top: 0.2rem; }

  /* ── Disclaimer ── */
  .disclaimer {
    max-width: 900px;
    margin: 0 auto 2rem;
    padding: 1rem 1.5rem;
    background: #fff8e1;
    border-left: 4px solid var(--amarillo);
    border-radius: 6px;
    font-size: 0.82rem;
    color: #555;
    line-height: 1.5;
  }

  footer {
    text-align: center;
    padding: 1.5rem;
    font-size: 0.8rem;
    color: #888;
    border-top: 1px solid #e0e0e0;
    background: white;
  }
  footer a { color: var(--azul); text-decoration: none; }
</style>
</head>
<body>

<header>
  <h1>🗺️ Mapa de Transparencia del Estado Argentino</h1>
  <p>Ph.D. Vicente Humberto Monteverde · Algoritmos contra la Corrupción</p>
  <span class="badge">v1.0 · Datos públicos oficiales · Actualización diaria</span>
</header>

<nav>
  <a href="#ejecutivo">⚡ Ejecutivo</a>
  <a href="#legislativo">🏛️ Legislativo</a>
  <a href="#judicial">⚖️ Judicial</a>
  <a href="#fiscal">💰 Fiscal</a>
  <a href="#iri">🚦 Índice IRI</a>
  <a href="/docs">🔧 API</a>
</nav>

<div class="hero">
  <h2>Monitoreo integral del Estado argentino en tiempo real</h2>
  <p>Este portal centraliza los monitores de transparencia de los tres poderes del Estado,
     el sistema de contrataciones públicas y el Índice de Riesgo Institucional (IRI).
     Todos los datos provienen de fuentes oficiales públicas.</p>
</div>

<!-- Stats -->
<div class="stats">
  <div class="stat-card">
    <div class="num">7</div>
    <div class="label">Monitores activos</div>
  </div>
  <div class="stat-card">
    <div class="num">3</div>
    <div class="label">Poderes del Estado</div>
  </div>
  <div class="stat-card">
    <div class="num">$3.8B</div>
    <div class="label">ARS monitoreados</div>
  </div>
  <div class="stat-card">
    <div class="num">1.154</div>
    <div class="label">Autoridades</div>
  </div>
  <div class="stat-card">
    <div class="num">1.839</div>
    <div class="label">Contratos registrados</div>
  </div>
</div>

<!-- ── PODER EJECUTIVO ── -->
<div class="poderes">

  <div class="poder poder-ejecutivo" id="ejecutivo">
    <div class="poder-header">
      <span class="icon">⚡</span>
      <div>
        <h3>Poder Ejecutivo Nacional</h3>
        <p>JGM · SGP · Presidencia · Contratos</p>
      </div>
    </div>
    <div class="monitor-list">
      <a class="monitor-item" href="https://jefaturagabinete-production.up.railway.app" target="_blank" rel="noopener">
        <span class="mi-icon">🏛️</span>
        <div class="mi-info">
          <div class="mi-title">Monitor Ejecutivo</div>
          <div class="mi-desc">JGM · SGP · Presidencia · Contratos · Nómina · Alertas</div>
        </div>
        <span class="mi-status status-live">EN VIVO</span>
      </a>
      <a class="monitor-item" href="https://gobbocomprartgn-production.up.railway.app" target="_blank" rel="noopener">
        <span class="mi-icon">⚖️</span>
        <div class="mi-info">
          <div class="mi-title">Monitor de Contratos y Licitaciones v1</div>
          <div class="mi-desc">COMPR.AR · TGN · Análisis de riesgo en tiempo real</div>
        </div>
        <span class="mi-status status-live">EN VIVO</span>
      </a>
      <a class="monitor-item" href="https://monitorcontratosv2-production.up.railway.app" target="_blank" rel="noopener">
        <span class="mi-icon">📊</span>
        <div class="mi-info">
          <div class="mi-title">Monitor de Contratos v2</div>
          <div class="mi-desc">BORA + COMPR.AR · Detección de irregularidades XAI</div>
        </div>
        <span class="mi-status status-live">EN VIVO</span>
      </a>
    </div>
  </div>

  <!-- ── PODER LEGISLATIVO ── -->
  <div class="poder poder-legislativo" id="legislativo">
    <div class="poder-header">
      <span class="icon">🏛️</span>
      <div>
        <h3>Poder Legislativo Nacional</h3>
        <p>Cámara de Diputados · Senado</p>
      </div>
    </div>
    <div class="monitor-list">
      <a class="monitor-item" href="https://monitorlegistativo-production.up.railway.app" target="_blank" rel="noopener">
        <span class="mi-icon">🗳️</span>
        <div class="mi-info">
          <div class="mi-title">Monitor Legislativo · Diputados</div>
          <div class="mi-desc">ICE · Asistencia · Productividad · Costo per cápita</div>
        </div>
        <span class="mi-status status-live">EN VIVO</span>
      </a>
      <a class="monitor-item" href="https://monitorlegistativosenadores-production.up.railway.app" target="_blank" rel="noopener">
        <span class="mi-icon">🏅</span>
        <div class="mi-info">
          <div class="mi-title">Monitor Legislativo · Senadores</div>
          <div class="mi-desc">Participación · Reporte por partido · Indicadores</div>
        </div>
        <span class="mi-status status-live">EN VIVO</span>
      </a>
    </div>
  </div>

  <!-- ── PODER JUDICIAL ── -->
  <div class="poder poder-judicial" id="judicial">
    <div class="poder-header">
      <span class="icon">⚖️</span>
      <div>
        <h3>Poder Judicial de la Nación</h3>
        <p>CSJN · Magistratura · Juzgados federales</p>
      </div>
    </div>
    <div class="monitor-list">
      <a class="monitor-item" href="https://justicia-production-6a54.up.railway.app" target="_blank" rel="noopener">
        <span class="mi-icon">⚖️</span>
        <div class="mi-info">
          <div class="mi-title">Monitor Judicial</div>
          <div class="mi-desc">Corte Suprema · Magistratura · Cámaras · Juzgados · IRA</div>
        </div>
        <span class="mi-status status-live">EN VIVO</span>
      </a>
    </div>
  </div>

  <!-- ── ÍNDICE IRI ── -->
  <div class="poder poder-iri" id="iri" style="grid-column: 1 / -1;">
    <div class="poder-header">
      <span class="icon">🚦</span>
      <div>
        <h3>Índice de Riesgo Institucional (IRI)</h3>
        <p>Semáforo de integridad pública · Todos los poderes · Score compuesto</p>
      </div>
    </div>
    <div class="monitor-list">
      <a class="monitor-item" href="https://monitor-production-f053.up.railway.app" target="_blank" rel="noopener">
        <span class="mi-icon">🚦</span>
        <div class="mi-info">
          <div class="mi-title">Monitor IRI · Dashboard Central</div>
          <div class="mi-desc">
            Score compuesto: R_Financiero×35% + R_Contratación×30% + R_Operativo×20% + R_Datos×15%
            · Integra todos los repositorios del sistema
          </div>
        </div>
        <span class="mi-status status-live">EN VIVO</span>
      </a>
    </div>
  </div>

</div>

<!-- Disclaimer -->
<div class="disclaimer" style="margin: 0 auto 2rem; max-width:1100px; padding: 0 1rem;">
  <div style="background:#fff8e1; border-left:4px solid #f39c12; border-radius:6px; padding:1rem 1.2rem; font-size:0.82rem; color:#555; line-height:1.6;">
    ⚠️ <strong>Aviso:</strong> Esta herramienta es de carácter experimental y académico.
    Los datos provienen de fuentes públicas oficiales del Estado argentino.
    Los resultados son indicadores algorítmicos de riesgo — no implican juicio de valor,
    acusación ni determinación de responsabilidad sobre ninguna empresa, organismo o persona.
    El objetivo es promover la transparencia y el debate informado sobre el gasto público.
  </div>
</div>

<footer>
  Mapa de Transparencia · <a href="https://github.com/Viny2030/Mapa_Transparencia" target="_blank">github.com/Viny2030</a> ·
  Ph.D. Vicente Humberto Monteverde ·
  <a href="mailto:vhmonte@retina.ar">vhmonte@retina.ar</a>
</footer>

</body>
</html>
"""

# ── Rutas ────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse(content=HTML_CONTENT)


@app.get("/health")
def health():
    return {"status": "healthy", "service": "Mapa Transparencia"}


@app.get("/servicios")
def servicios():
    """Lista todos los servicios integrados con sus URLs"""
    return {
        "servicios": [
            {"id": k, "url": v} for k, v in SERVICES.items()
        ]
    }


@app.get("/status")
async def status():
    """Verifica el estado de cada servicio integrado"""
    resultados = {}
    async with httpx.AsyncClient(timeout=5) as client:
        for nombre, url in SERVICES.items():
            try:
                r = await client.get(url)
                resultados[nombre] = {
                    "url": url,
                    "status": r.status_code,
                    "ok": r.status_code < 400
                }
            except Exception as e:
                resultados[nombre] = {
                    "url": url,
                    "status": None,
                    "ok": False,
                    "error": str(e)
                }
    return resultados


@app.get("/iri/datos")
async def iri_datos():
    """Proxy: datos del Monitor IRI"""
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{SERVICES['iri']}/datos")
        r.raise_for_status()
        return r.json()


@app.get("/iri/top-riesgo")
async def iri_top(n: int = 10):
    """Proxy: top N organismos de mayor riesgo IRI"""
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{SERVICES['iri']}/top-riesgo", params={"n": n})
        r.raise_for_status()
        return r.json()


@app.get("/iri/resumen")
async def iri_resumen():
    """Proxy: resumen estadístico global del IRI"""
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{SERVICES['iri']}/resumen")
        r.raise_for_status()
        return r.json()
