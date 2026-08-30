import asyncio
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pathlib import Path
import httpx
import os

app = FastAPI(title="Mapa de Transparencia del Estado Argentino", version="1.1.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

SERVICES = {
    "contratos":    os.getenv("CONTRATOS_API_URL",   "https://gobbocomprartgn-production.up.railway.app"),
    "contratos_v2": os.getenv("CONTRATOS_V2_API_URL","https://monitorcontratos-production.up.railway.app"),
    "ejecutivo":    os.getenv("EJECUTIVO_API_URL",   "https://jefaturagabinete-production.up.railway.app"),
    "justicia":     os.getenv("JUSTICIA_API_URL",    "https://justicia-production-6a54.up.railway.app"),
    "diputados":    os.getenv("LEGISTATIVO_API_URL", "https://monitorlegistativo-production.up.railway.app"),
    "senadores":    os.getenv("SENADORES_API_URL",   "https://monitorlegistativosenadores-production.up.railway.app"),
    "iri":          os.getenv("IRI_API_URL",         "https://monitor-production-f053.up.railway.app"),
    "ajuste":       os.getenv("AJUSTE_API_URL",      "https://ajuste-production.up.railway.app"),
    "corrupcion_estrategica": os.getenv("CORRUPCION_ESTRATEGICA_API_URL", "https://corrupcionestrategica-production.up.railway.app"),
    "meaci":        os.getenv("MEACI_API_URL",       "https://meaci-production.up.railway.app"),
    "ddjj":         os.getenv("DECLA_API_URL",       "https://decla-production.up.railway.app"),
}

HTML_CONTENT = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Mapa de Transparencia · Estado Argentino</title>

<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-HXN5QSTRS1"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-HXN5QSTRS1');
</script>

<style>
  :root { --azul:#003f8a; --gris:#f4f6f9; --verde:#27ae60; --amarillo:#f39c12; --rojo:#e74c3c; --texto:#1a1a2e; }
  *{box-sizing:border-box;margin:0;padding:0;}
  body{font-family:'Segoe UI',system-ui,sans-serif;background:var(--gris);color:var(--texto);}
  header{background:linear-gradient(135deg,#003f8a,#005bb5);color:white;padding:2rem 1.5rem;text-align:center;}
  header h1{font-size:1.9rem;font-weight:700;}
  header p{font-size:0.95rem;opacity:.85;margin-top:.4rem;}
  .badge{display:inline-block;background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.3);border-radius:20px;padding:.2rem .8rem;font-size:.78rem;margin-top:.6rem;}
  nav{background:#003f8a;display:flex;justify-content:center;gap:.5rem;padding:.6rem 1rem;flex-wrap:wrap;}
  nav a{color:rgba(255,255,255,.8);text-decoration:none;font-size:.82rem;padding:.3rem .7rem;border-radius:4px;transition:background .2s;}
  nav a:hover{background:rgba(255,255,255,.15);color:white;}
  nav a.nav-intl{background:rgba(231,76,60,.25);color:#ff9090;border:1px solid rgba(231,76,60,.4);}
  nav a.nav-intl:hover{background:rgba(231,76,60,.45);color:white;}
  .hero{max-width:900px;margin:2rem auto 0;padding:0 1rem;text-align:center;}
  .hero h2{font-size:1.3rem;color:var(--azul);margin-bottom:.5rem;}
  .hero p{color:#555;font-size:.93rem;line-height:1.6;}
  .stats{max-width:900px;margin:2rem auto;padding:0 1rem;display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:1rem;}
  .stat-card{background:white;border-radius:10px;padding:1rem;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,.06);}
  .stat-card .num{font-size:1.6rem;font-weight:700;color:var(--azul);}
  .stat-card .label{font-size:.75rem;color:#666;margin-top:.2rem;}
  .num.loading{color:#ccc;animation:pulse 1.2s infinite;}
  @keyframes pulse{0%,100%{opacity:1;}50%{opacity:.4;}}
  .poderes{max-width:1100px;margin:0 auto 2rem;padding:0 1rem;display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:1.5rem;}
  .poder{background:white;border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,.07);overflow:hidden;}
  .poder-header{padding:1rem 1.2rem;display:flex;align-items:center;gap:.7rem;}
  .poder-header .icon{font-size:1.8rem;}
  .poder-header h3{font-size:1rem;font-weight:700;}
  .poder-header p{font-size:.78rem;opacity:.8;}
  .poder-ejecutivo .poder-header{background:linear-gradient(135deg,#003f8a,#0062cc);color:white;}
  .poder-legislativo .poder-header{background:linear-gradient(135deg,#7b2d8b,#a855f7);color:white;}
  .poder-judicial .poder-header{background:linear-gradient(135deg,#b5451b,#e8622a);color:white;}
  .poder-iri .poder-header{background:linear-gradient(135deg,#1a1a2e,#16213e);color:white;}
  .poder-intl .poder-header{background:linear-gradient(135deg,#7b1a1a,#c0392b);color:white;}
  .poder-ddjj .poder-header{background:linear-gradient(135deg,#0d5c46,#149e78);color:white;}
  .monitor-list{padding:.8rem;}
  .monitor-item{display:flex;align-items:center;gap:.8rem;padding:.75rem .8rem;border-radius:8px;text-decoration:none;color:var(--texto);transition:background .18s;border-bottom:1px solid #f0f0f0;}
  .monitor-item:last-child{border-bottom:none;}
  .monitor-item:hover{background:var(--gris);}
  .mi-icon{font-size:1.3rem;width:2rem;text-align:center;}
  .mi-info{flex:1;}
  .mi-title{font-size:.88rem;font-weight:600;}
  .mi-desc{font-size:.76rem;color:#777;margin-top:.1rem;}
  .mi-status{font-size:.7rem;padding:.15rem .5rem;border-radius:10px;font-weight:600;}
  .status-live{background:#d4edda;color:#155724;}
  .status-down{background:#f8d7da;color:#721c24;}
  .meaci-stats-row{display:flex;gap:1rem;flex-wrap:wrap;padding:.5rem .8rem 1rem;border-top:1px solid #f0f0f0;}
  .meaci-kpi{text-align:center;flex:1;min-width:80px;}
  .meaci-kpi-num{font-size:1.2rem;font-weight:700;color:#c0392b;}
  .meaci-kpi-label{font-size:.68rem;color:#999;text-transform:uppercase;letter-spacing:.04em;}
  .disclaimer{max-width:1100px;margin:0 auto 2rem;padding:0 1rem;}
  .disclaimer-inner{background:#fff8e1;border-left:4px solid #f39c12;border-radius:6px;padding:1rem 1.2rem;font-size:.85rem;color:#555;line-height:1.7;}
  .autor-section{max-width:1100px;margin:0 auto 2rem;padding:0 1rem;}
  .autor-card{background:#1a1a2e;border-radius:12px;padding:2rem;display:grid;grid-template-columns:auto 1fr;gap:2rem;align-items:start;box-shadow:0 4px 20px rgba(0,0,0,.15);}
  .autor-foto{width:100px;height:100px;border-radius:50%;border:3px solid #74b2e2;object-fit:cover;display:block;}
  .autor-foto-fallback{width:100px;height:100px;border-radius:50%;background:linear-gradient(135deg,#003f8a,#005bb5);display:flex;align-items:center;justify-content:center;font-size:3rem;border:3px solid #74b2e2;}
  .autor-info h3{font-size:1.2rem;font-weight:800;color:#fff;margin-bottom:.5rem;}
  .autor-info p{font-size:.88rem;color:#94a3b8;line-height:1.7;margin-bottom:.4rem;}
  .autor-info p em{color:#74b2e2;font-style:italic;}
  .autor-mails{display:flex;gap:.7rem;flex-wrap:wrap;margin-top:1rem;}
  .mail-btn{display:inline-flex;align-items:center;gap:.4rem;background:rgba(116,178,226,.15);border:1px solid rgba(116,178,226,.3);color:#74b2e2;padding:.4rem 1rem;border-radius:8px;font-size:.83rem;text-decoration:none;transition:background .2s;}
  .mail-btn:hover{background:rgba(116,178,226,.3);color:#fff;}
  .donacion-section{max-width:1100px;margin:0 auto 2rem;padding:0 1rem;}
  .donacion-header{text-align:center;margin-bottom:1.5rem;}
  .donacion-header h2{font-size:1.2rem;font-weight:700;color:var(--azul);margin-bottom:.4rem;}
  .donacion-header p{font-size:.85rem;color:#666;}
  .donacion-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1rem;}
  .don-card{background:white;border-radius:10px;padding:1.2rem;box-shadow:0 2px 10px rgba(0,0,0,.07);border-top:3px solid var(--azul);}
  .don-card h4{font-size:.88rem;font-weight:700;color:var(--azul);margin-bottom:.8rem;}
  .don-row{margin-bottom:.5rem;}
  .don-label{font-size:.7rem;text-transform:uppercase;color:#999;letter-spacing:.05em;font-weight:600;}
  .don-value{font-size:.88rem;font-weight:600;color:var(--texto);font-family:monospace;}
  .don-highlight{color:#27ae60;}
  footer{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:.5rem;padding:1.5rem;font-size:.8rem;color:#888;border-top:1px solid #e0e0e0;background:white;text-align:left;}
  footer a{color:var(--azul);text-decoration:none;}
  @media(max-width:640px){footer{justify-content:center;text-align:center;}}
  @media(max-width:640px){.autor-card{grid-template-columns:1fr;text-align:center;}.autor-mails{justify-content:center;}header h1{font-size:1.4rem;}}
</style>
</head>
<body>

<header>
  <h1>🗺️ Mapa de Transparencia del Estado Argentino</h1>
  <p>Ph.D. Vicente Humberto Monteverde · Algoritmos contra la Corrupción</p>
  <span class="badge">v1.1 · Datos públicos oficiales · Actualización diaria</span>
</header>

<nav>
  <a href="#ejecutivo">⚡ Ejecutivo</a>
  <a href="#legislativo">🏛️ Legislativo</a>
  <a href="#judicial">⚖️ Judicial</a>
  <a href="#ddjj">📜 DDJJ</a>
  <a href="#iri">🚦 IRI</a>
  <a href="#meaci" class="nav-intl">🌍 Monitor Internacional</a>
  <a href="#autor">👤 Autor</a>
  <a href="#donacion">💛 Donar</a>
  <a href="/docs">🔧 API</a>
  <a href="/en">🇺🇸 English</a>
</nav>

<div class="hero">
  <h2>Monitoreo integral del Estado argentino en tiempo real</h2>
  <p>Este portal centraliza los monitores de transparencia de los tres poderes del Estado, el sistema de contrataciones públicas, el Índice de Riesgo Institucional (IRI) y el Monitor Internacional de Anticorrupción (MEACI). Todos los datos provienen de fuentes oficiales públicas.</p>
</div>

<div class="stats">
  <div class="stat-card"><div class="num loading" id="kpi-monitores">—</div><div class="label">Monitores activos</div></div>
  <div class="stat-card"><div class="num">3</div><div class="label">Poderes del Estado</div></div>
  <div class="stat-card"><div class="num loading" id="kpi-organismos">—</div><div class="label">Organismos monitoreados</div></div>
  <div class="stat-card"><div class="num loading" id="kpi-iri">—</div><div class="label">IRI promedio global</div></div>
  <div class="stat-card"><div class="num loading" id="kpi-riesgo">—</div><div class="label">En riesgo medio/alto</div></div>
  <div class="stat-card"><div class="num" style="color:#c0392b;">31</div><div class="label">Casos MJR internacionales</div></div>
</div>

<div class="poderes">
  <div class="poder poder-ejecutivo" id="ejecutivo">
    <div class="poder-header"><span class="icon">⚡</span><div><h3>Poder Ejecutivo Nacional</h3><p>JGM · SGP · Presidencia · Contratos</p></div></div>
    <div class="monitor-list">
      <a class="monitor-item" href="https://jefaturagabinete-production.up.railway.app" target="_blank" rel="noopener">
        <span class="mi-icon">🏛️</span><div class="mi-info"><div class="mi-title">Monitor Ejecutivo</div><div class="mi-desc">JGM · SGP · Presidencia · Contratos · Nómina · Alertas</div></div>
        <span class="mi-status status-live" id="st-ejecutivo">EN VIVO</span>
      </a>
      <a class="monitor-item" href="https://gobbocomprartgn-production.up.railway.app" target="_blank" rel="noopener">
        <span class="mi-icon">⚖️</span><div class="mi-info"><div class="mi-title">Monitor de Contratos v1</div><div class="mi-desc">COMPR.AR · TGN · Análisis de riesgo en tiempo real</div></div>
        <span class="mi-status status-live" id="st-contratos">EN VIVO</span>
      </a>
      <a class="monitor-item" href="https://monitorcontratos-production.up.railway.app" target="_blank" rel="noopener">
        <span class="mi-icon">📊</span><div class="mi-info"><div class="mi-title">Monitor de Contratos v2</div><div class="mi-desc">BORA + COMPR.AR · Detección de irregularidades XAI</div></div>
        <span class="mi-status status-live" id="st-contratos_v2">EN VIVO</span>
      </a>
    </div>
  </div>

  <div class="poder poder-legislativo" id="legislativo">
    <div class="poder-header"><span class="icon">🏛️</span><div><h3>Poder Legislativo Nacional</h3><p>Cámara de Diputados · Senado</p></div></div>
    <div class="monitor-list">
      <a class="monitor-item" href="https://monitorlegistativo-production.up.railway.app" target="_blank" rel="noopener">
        <span class="mi-icon">🗳️</span><div class="mi-info"><div class="mi-title">Monitor Legislativo · Diputados</div><div class="mi-desc">ICE · Asistencia · Productividad · Costo per cápita</div></div>
        <span class="mi-status status-live" id="st-diputados">EN VIVO</span>
      </a>
      <a class="monitor-item" href="https://monitorlegistativosenadores-production.up.railway.app" target="_blank" rel="noopener">
        <span class="mi-icon">🏅</span><div class="mi-info"><div class="mi-title">Monitor Legislativo · Senadores</div><div class="mi-desc">Participación · Reporte por partido · Indicadores</div></div>
        <span class="mi-status status-live" id="st-senadores">EN VIVO</span>
      </a>
    </div>
  </div>

  <div class="poder poder-judicial" id="judicial">
    <div class="poder-header"><span class="icon">⚖️</span><div><h3>Poder Judicial de la Nación</h3><p>CSJN · Magistratura · Juzgados federales</p></div></div>
    <div class="monitor-list">
      <a class="monitor-item" href="https://justicia-production-6a54.up.railway.app" target="_blank" rel="noopener">
        <span class="mi-icon">⚖️</span><div class="mi-info"><div class="mi-title">Monitor Judicial</div><div class="mi-desc">Corte Suprema · Magistratura · Cámaras · Juzgados · IRA</div></div>
        <span class="mi-status status-live" id="st-justicia">EN VIVO</span>
      </a>
    </div>
  </div>

  <div class="poder poder-ddjj" id="ddjj">
    <div class="poder-header"><span class="icon">📜</span><div><h3>Declaraciones Juradas Patrimoniales (DDJJ)</h3><p>Funcionarios · Legisladores · Jueces · Score de riesgo IVPI</p></div></div>
    <div class="monitor-list">
      <a class="monitor-item" href="https://decla-production.up.railway.app" target="_blank" rel="noopener">
        <span class="mi-icon">🏛️</span><div class="mi-info"><div class="mi-title">DDJJ · Funcionarios (Ejecutivo)</div><div class="mi-desc">Patrimonio 2022–2024 · IVPI · 12 indicadores internacionales</div></div>
        <span class="mi-status status-live" id="st-ddjj-eje">EN VIVO</span>
      </a>
      <a class="monitor-item" href="https://decla-production.up.railway.app" target="_blank" rel="noopener">
        <span class="mi-icon">📋</span><div class="mi-info"><div class="mi-title">DDJJ · Legisladores</div><div class="mi-desc">Diputados y senadores · Ranking por bloque y cámara</div></div>
        <span class="mi-status status-live" id="st-ddjj-leg">EN VIVO</span>
      </a>
      <a class="monitor-item" href="https://decla-production.up.railway.app" target="_blank" rel="noopener">
        <span class="mi-icon">⚖️</span><div class="mi-info"><div class="mi-title">DDJJ · Jueces</div><div class="mi-desc">Nómina judicial · Consulta directa al Consejo de la Magistratura</div></div>
        <span class="mi-status status-live" id="st-ddjj-jud">EN VIVO</span>
      </a>
    </div>
  </div>

  <div class="poder poder-iri" id="iri" style="grid-column:1/-1;">
    <div class="poder-header"><span class="icon">🚦</span><div><h3>Índice de Riesgo Institucional (IRI)</h3><p>Semáforo de integridad pública · Score compuesto</p></div></div>
    <div class="monitor-list">
      <a class="monitor-item" href="https://monitor-production-f053.up.railway.app" target="_blank" rel="noopener">
        <span class="mi-icon">🚦</span>
        <div class="mi-info"><div class="mi-title">Monitor IRI · Dashboard Central</div><div class="mi-desc">Score compuesto: R_Financiero×35% + R_Contratación×30% + R_Operativo×20% + R_Datos×15%</div></div>
        <span class="mi-status status-live" id="st-iri">EN VIVO</span>
      </a>
    </div>
  </div>
</div>

<div class="poderes" style="margin-bottom:0;">
  <div class="poder" id="ajuste" style="grid-column:1/-1;border-top:3px solid #5b2d8e;">
    <div class="poder-header" style="background:linear-gradient(135deg,#3d1e6e,#5b2d8e);color:white;">
      <span class="icon">📊</span>
      <div><h3>Monitor de Ajuste Presupuestario (MAP)</h3><p>Presupuesto 2023 → 2026 · Nominal · Real (IPC) · USD constantes</p></div>
    </div>
    <div class="monitor-list">
      <a class="monitor-item" href="https://ajuste-production.up.railway.app" target="_blank" rel="noopener">
        <span class="mi-icon">📉</span>
        <div class="mi-info"><div class="mi-title">Dashboard Principal · Ajuste por Sector</div><div class="mi-desc">Ranking de programas · Por inciso · Evolución real · Licuación vs recorte · Sectores sociales</div></div>
        <span class="mi-status status-live" id="st-ajuste">EN VIVO</span>
      </a>
    </div>
  </div>
</div>

<div class="poderes" style="margin-top:1.5rem;">
  <div class="poder" id="corrupcion_estrategica" style="grid-column:1/-1;border-top:3px solid #b5651d;">
    <div class="poder-header" style="background:linear-gradient(135deg,#5c3a00,#b5651d);color:white;">
      <span class="icon">🕸️</span>
      <div><h3>Vectores de Influencia Estatal Extranjera</h3><p>Framework NEST de corrupción estratégica · China · Rusia · 18 vectores investigados</p></div>
    </div>
    <div class="monitor-list">
      <a class="monitor-item" href="https://corrupcionestrategica-production.up.railway.app" target="_blank" rel="noopener">
        <span class="mi-icon">🕸️</span>
        <div class="mi-info"><div class="mi-title">Vectores de Influencia Estatal Extranjera</div><div class="mi-desc">Clasifica casos de influencia de China y Rusia sobre decisiones públicas argentinas (nuclear, litio, puertos, banca, defensa) bajo el framework NEST de corrupción estratégica</div></div>
        <span class="mi-status status-live" id="st-corrupcion_estrategica">EN VIVO</span>
      </a>
    </div>
  </div>
</div>

<div class="poderes" style="margin-top:1.5rem;">
  <div class="poder poder-intl" id="meaci" style="grid-column:1/-1;border-top:3px solid #c0392b;">
    <div class="poder-header">
      <span class="icon">🌍</span>
      <div><h3>Monitor Internacional de Anticorrupción (MEACI)</h3><p>OCDE · DOJ · SFO · PNF · Presencia Argentina · Actualización semanal</p></div>
    </div>
    <div class="monitor-list">
      <a class="monitor-item" href="https://meaci-production.up.railway.app" target="_blank" rel="noopener">
        <span class="mi-icon">🔍</span>
        <div class="mi-info">
          <div class="mi-title">MEACI · Monitor de Casos MJR Internacionales</div>
          <div class="mi-desc">Cruza casos de corrupción internacional (DOJ · SFO · PNF) con contrataciones públicas argentinas (COMPR.AR) y registro AFIP</div>
        </div>
        <span class="mi-status status-live" id="st-meaci">EN VIVO</span>
      </a>
    </div>
    <div class="meaci-stats-row">
      <div class="meaci-kpi"><div class="meaci-kpi-num">31</div><div class="meaci-kpi-label">Casos MJR (2008–2026)</div></div>
      <div class="meaci-kpi"><div class="meaci-kpi-num">73</div><div class="meaci-kpi-label">Resoluciones totales</div></div>
      <div class="meaci-kpi"><div class="meaci-kpi-num">15</div><div class="meaci-kpi-label">Con presencia en AR</div></div>
      <div class="meaci-kpi"><div class="meaci-kpi-num">USD 24.7B</div><div class="meaci-kpi-label">Sanciones totales 2024</div></div>
    </div>
  </div>
</div>

<div class="disclaimer">
  <div class="disclaimer-inner">
    ⚠️ <strong>Nota:</strong> Esta herramienta es de carácter <strong>experimental y académico</strong>.
    Los datos provienen de fuentes públicas oficiales del Estado argentino y organismos internacionales.
    Los resultados son <strong>indicadores algorítmicos de riesgo</strong> — no implican juicio de valor,
    acusación ni determinación de responsabilidad sobre ninguna empresa, organismo o persona.
    El objetivo es promover la <strong>transparencia y el debate informado</strong> sobre el gasto público.
  </div>
</div>

<div class="disclaimer" id="marco-legal">
  <div class="disclaimer-inner" style="background:#e8f4fd;border-left-color:#003f8a;font-size:.82rem;">
    <strong>⚖️ Marco Legal y Transparencia</strong><br><br>
    Los datos publicados en este portal provienen exclusivamente de fuentes oficiales del Estado argentino.
    Su reutilización está amparada por la <strong>Ley 27.275 de Acceso a la Información Pública</strong>,
    que obliga a los organismos públicos a publicar activamente la información que producen, obtienen, transforman o controlan,
    y por el <strong>Decreto 1172/2003</strong> sobre libre acceso a la información pública en el Poder Ejecutivo Nacional.<br><br>
    En relación con la <strong>Ley 25.326 de Protección de Datos Personales</strong>, este portal procesa únicamente
    información de funcionarios públicos en ejercicio de sus funciones, excluida del ámbito de protección individual
    conforme al art. 2 de dicha ley y a la doctrina consolidada de la <strong>Agencia de Acceso a la Información Pública (AAIP)</strong>.
    Los datos curriculares de magistrados corresponden a declaración obligatoria ante el Consejo de la Magistratura (Ley 27.275, art. 16).
    Los CUIT de personas jurídicas son datos fiscales públicos no alcanzados por la Ley 25.326.<br><br>
    Las sanciones internacionales exhibidas corresponden a resoluciones firmes de organismos judiciales o regulatorios extranjeros
    de acceso público (<strong>DOJ · SFO · PNF · OCDE · Banco Mundial</strong>). Su cruce con el registro COMPR.AR tiene
    exclusivamente fines de análisis de riesgo académico y no implica imputación de responsabilidad en jurisdicción argentina.<br><br>
    Los indicadores, índices y alertas son el resultado de <strong>análisis algorítmico sobre datos oficiales</strong> y no constituyen
    imputaciones, acusaciones ni determinaciones de responsabilidad penal, civil o administrativa.
    No reemplazan los mecanismos formales de control del Estado (AGN · SIGEN · Ministerio Público Fiscal).
    Para consultas sobre el tratamiento de datos: <a href="mailto:vhmonte@retina.ar" style="color:#003f8a;">vhmonte@retina.ar</a>
  </div>
</div>

<div class="autor-section" id="autor">
  <div class="autor-card">
    <div>
      <img src="https://raw.githubusercontent.com/Viny2030/Mapa_Transparencia/main/foto.jpg"
           alt="Ph.D. Vicente Humberto Monteverde" class="autor-foto"
           onerror="this.style.display='none';this.nextElementSibling.style.display='flex';"/>
      <div class="autor-foto-fallback" style="display:none;">👤</div>
    </div>
    <div class="autor-info">
      <h3>Ph.D. Vicente Humberto Monteverde</h3>
      <p>Investigador en economía política y fenómenos de corrupción. Doctor en Ciencias Económicas.
         Autor de la teoría de <em>Transferencia Regresiva de Ingresos</em> y desarrollador del
         algoritmo XAI aplicado al análisis de contrataciones públicas.</p>
      <p>Publicaciones en <em>Journal of Financial Crime</em> (Emerald Publishing).
         Asesor en transparencia y auditoría algorítmica del gasto público.</p>
      <div class="autor-mails">
        <a href="mailto:vhmonte@retina.ar" class="mail-btn">✉️ vhmonte@retina.ar</a>
        <a href="mailto:viny01958@gmail.com" class="mail-btn">✉️ viny01958@gmail.com</a>
      </div>
    </div>
  </div>
</div>

<div class="donacion-section" id="donacion">
  <div class="donacion-header">
    <h2>💛 Apoyar este proyecto — Donaciones voluntarias</h2>
    <p>Si este proyecto te resulta útil, podés apoyarlo con una donación voluntaria.</p>
  </div>
  <div class="donacion-grid">
    <div class="don-card" style="border-top-color:#003f8a;">
      <h4>🇦🇷 Argentina · Pesos (ARS)</h4>
      <div class="don-row"><div class="don-label">Tipo</div><div class="don-value">Caja de Ahorro</div></div>
      <div class="don-row"><div class="don-label">CBU</div><div class="don-value don-highlight">0140005203400552652310</div></div>
      <div class="don-row"><div class="don-label">Alias</div><div class="don-value don-highlight">ALGORIT.MONTE.PESOS</div></div>
      <div class="don-row"><div class="don-label">Titular</div><div class="don-value">Vicente Humberto Monteverde</div></div>
      <div class="don-row"><div class="don-label">CUIL/CUIT</div><div class="don-value">20-12034411-1</div></div>
    </div>
    <div class="don-card" style="border-top-color:#27ae60;">
      <h4>🇦🇷 Argentina · Dólares (USD)</h4>
      <div class="don-row"><div class="don-label">Tipo</div><div class="don-value">Caja de Ahorro Dólares</div></div>
      <div class="don-row"><div class="don-label">CBU</div><div class="don-value don-highlight">0140005204400550329709</div></div>
      <div class="don-row"><div class="don-label">Alias</div><div class="don-value don-highlight">ALGO.MONTE.DOLARES</div></div>
      <div class="don-row"><div class="don-label">Titular</div><div class="don-value">Vicente Humberto Monteverde</div></div>
      <div class="don-row"><div class="don-label">CUIL/CUIT</div><div class="don-value">20-12034411-1</div></div>
    </div>
    <div class="don-card" style="border-top-color:#e74c3c;">
      <h4>🌐 Desde el Exterior (USD Wire)</h4>
      <div class="don-row"><div class="don-label">Banco</div><div class="don-value">Banco Santander Rio</div></div>
      <div class="don-row"><div class="don-label">Beneficiario</div><div class="don-value">Vicente Humberto Monteverde</div></div>
      <div class="don-row"><div class="don-label">Dirección</div><div class="don-value">Av. Directorio 3024 PB DTO 04</div></div>
      <div class="don-row"><div class="don-label">Cuenta USD</div><div class="don-value don-highlight">005200183500</div></div>
      <div class="don-row"><div class="don-label">SWIFT / BIC</div><div class="don-value don-highlight">BSCHUYMM</div></div>
      <div class="don-row"><div class="don-label">CUIT</div><div class="don-value">20-12034411-1</div></div>
    </div>
  </div>
</div>

<footer>
  <span>&copy; 2026 Vicente H. Monteverde | Mapa de Transparencia del Estado Argentino. Todos los derechos reservados.</span>
  <span>
    Mapa de Transparencia ·
    <a href="https://github.com/Viny2030/Mapa_Transparencia" target="_blank">github.com/Viny2030</a> ·
    Ph.D. Vicente Humberto Monteverde ·
    <a href="mailto:vhmonte@retina.ar">vhmonte@retina.ar</a>
  </span>
</footer>

<script>
async function cargarKPIs() {
  try {
    const [status, resumen] = await Promise.all([
      fetch('/status').then(r => r.json()),
      fetch('/iri/resumen').then(r => r.json())
    ]);

    const servicios = Object.entries(status);
    const activos = servicios.filter(([, s]) => s.ok).length;
    document.getElementById('kpi-monitores').textContent = activos;
    document.getElementById('kpi-monitores').classList.remove('loading');

    servicios.forEach(([nombre, s]) => {
      const el = document.getElementById('st-' + nombre);
      if (el) {
        el.textContent = s.ok ? 'EN VIVO' : 'CAIDO';
        el.className = 'mi-status ' + (s.ok ? 'status-live' : 'status-down');
      }
      // El monitor DDJJ tiene 3 badges (eje/leg/jud) que comparten el mismo servicio
      if (nombre === 'ddjj') {
        ['st-ddjj-eje', 'st-ddjj-leg', 'st-ddjj-jud'].forEach(id => {
          const el2 = document.getElementById(id);
          if (el2) {
            el2.textContent = s.ok ? 'EN VIVO' : 'CAIDO';
            el2.className = 'mi-status ' + (s.ok ? 'status-live' : 'status-down');
          }
        });
      }
    });

    const g = resumen.global;
    document.getElementById('kpi-organismos').textContent = g.total_organismos;
    document.getElementById('kpi-organismos').classList.remove('loading');
    document.getElementById('kpi-iri').textContent = g.iri_promedio_global.toFixed(1);
    document.getElementById('kpi-iri').classList.remove('loading');
    const enRiesgo = (g.alto_riesgo || 0) + (g.medio_riesgo || 0);
    document.getElementById('kpi-riesgo').textContent = enRiesgo;
    document.getElementById('kpi-riesgo').classList.remove('loading');

  } catch(e) {
    console.warn('KPIs no disponibles:', e);
    ['kpi-monitores','kpi-organismos','kpi-iri','kpi-riesgo'].forEach(id => {
      const el = document.getElementById(id);
      if (el) { el.textContent = '—'; el.classList.remove('loading'); }
    });
  }
}
cargarKPIs();
</script>

</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse(content=HTML_CONTENT)


@app.get("/en", response_class=HTMLResponse)
async def landing_en():
    path = Path("landing_en.html")
    return HTMLResponse(content=path.read_text(encoding="utf-8"))


@app.get("/google2e07fafd6389e31a.html", response_class=HTMLResponse)
async def google_verification():
    path = Path("google2e07fafd6389e31a.html")
    return HTMLResponse(content=path.read_text(encoding="utf-8"))


@app.get("/health")
def health():
    return {"status": "healthy", "service": "Mapa Transparencia"}


@app.get("/servicios")
def servicios():
    return {"servicios": [{"id": k, "url": v} for k, v in SERVICES.items()]}


_STATUS_CACHE = {"data": None, "ts": 0.0}
_STATUS_CACHE_TTL = 30  # segundos — evita golpear a los 11 servicios en cada carga de pagina


async def _check_one(client: httpx.AsyncClient, nombre: str, url: str) -> tuple[str, dict]:
    try:
        r = await client.get(url)
        return nombre, {"url": url, "status": r.status_code, "ok": r.status_code < 400}
    except Exception as e:
        return nombre, {"url": url, "status": None, "ok": False, "error": str(e)}


@app.get("/status")
async def status():
    now = time.time()
    if _STATUS_CACHE["data"] is not None and (now - _STATUS_CACHE["ts"]) < _STATUS_CACHE_TTL:
        return _STATUS_CACHE["data"]

    async with httpx.AsyncClient(timeout=5) as client:
        pares = await asyncio.gather(
            *[_check_one(client, nombre, url) for nombre, url in SERVICES.items()]
        )
    resultados = dict(pares)

    _STATUS_CACHE["data"] = resultados
    _STATUS_CACHE["ts"] = now
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
