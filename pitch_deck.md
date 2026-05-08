# Pitch Deck — Mapa de Transparencia del Estado Argentino
## *Transparency Map of the Argentine State*
### Ph.D. Vicente Humberto Monteverde · v1.0 · 2025

---

## SLIDE 1 — Cover

**Mapa de Transparencia**
*Algorithmic monitoring of all three branches of the Argentine government*

🗺️ Real-time · Open source · Official data · XAI-powered

mapatransparencia-production.up.railway.app

---

## SLIDE 2 — The Problem

**Corruption is invisible by design.**

- Public spending in Argentina exceeds $300B USD/year
- Procurement irregularities are buried in thousands of unstructured contracts
- No single platform monitors Executive + Legislative + Judicial simultaneously
- Existing tools show data — they don't calculate risk

> "What gets measured gets managed. What doesn't get measured, gets stolen."

---

## SLIDE 3 — The Solution

**One platform. Three branches. One composite risk score.**

Mapa de Transparencia is the first open-source platform to:
- Monitor all three branches of the Argentine State simultaneously
- Calculate a composite Institutional Risk Index (IRI) in real time
- Use Explainable AI (XAI) to make every alert interpretable
- Operate entirely on official public data — no scraping, no inference

---

## SLIDE 4 — The IRI (Core Innovation)

**Institutional Risk Index = R_F×35% + R_C×30% + R_O×20% + R_D×15%**

| Dimension | Weight | What it measures |
|---|---|---|
| Financial Risk (R_F) | 35% | Budget anomalies, payment flows |
| Procurement Risk (R_C) | 30% | Contract irregularities (XAI) |
| Operational Risk (R_O) | 20% | Performance, absenteeism |
| Data Risk (R_D) | 15% | Publication quality & timeliness |

**Key differentiator:** XAI makes every risk score explainable to non-technical users, judges, and journalists — not a black box.

---

## SLIDE 5 — Platform Overview

**7 live monitors · 3 branches · Daily updates**

- ⚡ **Executive** — Chief of Staff, Presidency, Contracts (×2), Payroll
- 🏛️ **Legislative** — Chamber of Deputies + Senate
- ⚖️ **Judicial** — Supreme Court, Judiciary Council, Federal Courts
- 🚦 **IRI Dashboard** — Cross-branch composite score

**Live metrics:**
- 1,154 public officials tracked
- 1,839 contracts registered
- $3.8B ARS monitored
- Updated daily

---

## SLIDE 6 — Technology

**Open source · Python · FastAPI · Railway**
