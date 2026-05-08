# Mapa de Transparencia — Public API Specification
## OpenAPI 3.0 · v1.0

**Base URL:** `https://mapatransparencia-production.up.railway.app`
**Docs:** `/docs` (Swagger UI) · `/openapi.json` (machine-readable spec)
**Auth:** None required (public read-only API)
**Rate limit:** 100 requests/minute per IP

---

## Endpoints overview

### Hub

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Platform landing page |
| GET | `/docs` | Interactive Swagger UI |
| GET | `/openapi.json` | OpenAPI 3.0 specification |
| GET | `/health` | Platform health check |

### IRI — Institutional Risk Index

| Method | Endpoint | Description |
|---|---|---|
| GET | `/iri` | Current IRI score (all branches) |
| GET | `/iri/{branch}` | IRI score for a specific branch |
| GET | `/iri/history` | IRI score history (30-day rolling) |
| GET | `/iri/components` | Breakdown by component (R_F, R_C, R_O, R_D) |

**Branch values:** `executive` · `legislative` · `judicial`

**Example response — GET /iri:**
```json
{
  "timestamp": "2025-05-08T00:00:00Z",
  "iri_total": 42.7,
  "interpretation": "moderate_risk",
  "components": {
    "financial_risk": { "score": 38.2, "weight": 0.35 },
    "procurement_risk": { "score": 51.4, "weight": 0.30 },
    "operational_risk": { "score": 35.1, "weight": 0.20 },
    "data_risk": { "score": 44.8, "weight": 0.15 }
  },
  "by_branch": {
    "executive": 48.3,
    "legislative": 39.1,
    "judicial": 36.4
  },
  "data_date": "2025-05-07",
  "next_update": "2025-05-09T00:00:00Z"
}
```

### Contracts

| Method | Endpoint | Description |
|---|---|---|
| GET | `/contracts` | List of monitored contracts |
| GET | `/contracts/{id}` | Contract detail with XAI risk breakdown |
| GET | `/contracts/high-risk` | Contracts with risk score > 70 |
| GET | `/contracts/stats` | Aggregate contract statistics |

**Example response — GET /contracts/{id}:**
```json
{
  "contract_id": "COMPR-2025-00123",
  "organism": "Ministerio de Obras Públicas",
  "vendor": "[vendor name]",
  "amount_ars": 45000000,
  "award_date": "2025-04-15",
  "risk_score": 78.4,
  "risk_level": "high",
  "xai_explanation": {
    "top_factors": [
      { "feature": "single_bidder", "contribution": 24.1 },
      { "feature": "price_deviation_pct", "value": 340, "contribution": 31.2 },
      { "feature": "vendor_concentration_hhi", "value": 0.67, "contribution": 18.3 }
    ]
  },
  "source": "COMPR.AR",
  "disclaimer": "Algorithmic risk indicator only. Does not imply legal judgment."
}
```

### Officials

| Method | Endpoint | Description |
|---|---|---|
| GET | `/officials` | List of tracked public officials |
| GET | `/officials/stats` | Aggregate statistics (1,154 officials) |
| GET | `/officials/{branch}` | Officials by branch |

### Platform

| Method | Endpoint | Description |
|---|---|---|
| GET | `/monitors` | Status of all 7 monitors |
| GET | `/stats` | Platform-wide statistics |
| GET | `/sources` | Data sources and last update times |

---

## Data sources

All data is retrieved from official Argentine government sources. No proprietary or inferred data:

| Source | Description | Update freq. |
|---|---|---|
| JGM | Jefatura de Gabinete — budget, payroll | Daily |
| COMPR.AR | National procurement portal | Daily |
| BORA | Official Gazette — contracts & decrees | Daily |
| TGN | National Treasury — payments | Daily |
| Diputados | Chamber of Deputies — attendance, votes | Daily |
| Senado | Senate — attendance, votes | Daily |
| CSJN/Magistratura | Judiciary — performance data | Daily |

---

## Usage examples

```python
import httpx

# Get current IRI score
r = httpx.get("https://mapatransparencia-production.up.railway.app/iri")
iri = r.json()
print(f"IRI total: {iri['iri_total']} ({iri['interpretation']})")

# Get high-risk contracts
r = httpx.get("https://mapatransparencia-production.up.railway.app/contracts/high-risk")
contracts = r.json()
for c in contracts:
    print(f"{c['contract_id']}: {c['risk_score']}/100")
```

```bash
# Health check
curl https://mapatransparencia-production.up.railway.app/health

# IRI by branch
curl https://mapatransparencia-production.up.railway.app/iri/executive
```

---

## Disclaimer

This API provides algorithmic risk indicators derived from official public data. Results do not constitute legal judgment, accusation, or determination of responsibility. For research, journalism, and civic use only.

**License:** MIT · **Contact:** vhmonte@retina.ar
