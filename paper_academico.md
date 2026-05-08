# Algorithmic Transparency Monitoring of the Argentine State:
## The Institutional Risk Index (IRI) and Explainable AI in Public Procurement

**Author:** Vicente Humberto Monteverde, Ph.D.
**Affiliation:** Independent researcher, Buenos Aires, Argentina
**Contact:** vhmonte@retina.ar
**Keywords:** government transparency, institutional risk, explainable AI, public procurement, anti-corruption, open data, GovTech
**Suggested venue:** Journal of Financial Crime · SSRN · arXiv (cs.CY) · Government Information Quarterly

---

## Abstract

This paper presents the Institutional Risk Index (IRI), a composite algorithmic indicator for real-time monitoring of institutional risk across all three branches of the Argentine government. The IRI aggregates four weighted dimensions — Financial Risk (35%), Procurement Risk (30%), Operational Risk (20%), and Data Risk (15%) — into a single interpretable score updated daily from official public data. The Procurement Risk component applies Explainable AI (XAI) techniques, specifically gradient boosting with SHAP values, to detect irregular patterns in public contract data. We describe the theoretical foundation (Regressive Income Transfer theory), the technical architecture of the monitoring platform, the data pipeline, the normalization methodology, and the ethical framework governing the system. The platform is open source, deployed in production, and publicly accessible. We discuss implications for government accountability, the replicability of the methodology across other countries, and directions for future research including formal validation against known corruption cases.

---

## 1. Introduction

The measurement of corruption is notoriously difficult. Direct observation is rare by design; proxy indicators tend to be perception-based, infrequent, and coarse-grained. Composite indices such as the Corruption Perceptions Index (Transparency International) and the Control of Corruption indicator (World Bank Governance Indicators) are updated annually and cannot capture rapid institutional deterioration.

Meanwhile, governments increasingly publish real-time operational data — budget execution, procurement records, legislative attendance, judicial performance — as part of open government commitments. This data is rich, machine-readable, and largely underutilized for transparency purposes.

This paper argues that the combination of open government data and explainable machine learning enables a new class of transparency tools: real-time institutional risk monitors that are proactive rather than reactive, algorithmic rather than perceptual, and interpretable rather than opaque.

We present the Mapa de Transparencia platform and its core innovation, the Institutional Risk Index (IRI), as an operational proof of concept developed for Argentina and designed for international replication.

---

## 2. Theoretical foundation

### 2.1 Regressive Income Transfer theory

The IRI is grounded in the *Regressive Income Transfer* (RIT) theory (Monteverde, 2022), which models systemic corruption as a structured mechanism of income redistribution. Under RIT, public procurement and budget processes are captured by networks of actors who redirect public resources toward private benefit — not through isolated acts, but through institutionalized patterns detectable in administrative data.

RIT predicts that institutional corruption leaves systematic signatures: abnormal contract award patterns, budget execution clustering, payroll anomalies, and information opacity. The IRI operationalizes these predicted signatures into measurable indicators.

### 2.2 Explainable AI in anti-corruption

The application of machine learning to corruption detection is not new (see Ferwerda et al., 2017; Fazekas & Kocsis, 2020). However, most existing models produce black-box scores that are legally and politically contestable. Explainable AI (XAI) addresses this limitation by attributing each prediction to specific input features (Lundberg & Lee, 2017).

In the context of public procurement, XAI produces per-contract explanations: "this contract received a risk score of 78/100 primarily because it was awarded to a single bidder (contribution: +24), the price deviated 340% from market reference (contribution: +31), and the vendor received 67% of all contracts from this agency in the past 12 months (contribution: +18)." This level of interpretability is essential for journalistic use, legislative oversight, and judicial proceedings.

---

## 3. Platform architecture

The Mapa de Transparencia platform consists of seven independent monitors deployed as microservices and aggregated through a central hub:

- Three Executive monitors (Chief of Staff, Contracts v1 and v2 with XAI)
- Two Legislative monitors (Deputies and Senate)
- One Judicial monitor (Supreme Court and Judiciary Council)
- One cross-branch IRI dashboard

The technical stack is intentionally minimal: Python 3, FastAPI, HTTPX for data fetching, deployed on Railway. All data is retrieved daily from official Argentine government APIs (JGM, COMPR.AR, BORA, CSJN). The platform is fully open source (MIT license) and publicly accessible at mapatransparencia-production.up.railway.app.

---

## 4. The IRI methodology

### 4.1 Formula

IRI = (R_F × 0.35) + (R_C × 0.30) + (R_O × 0.20) + (R_D × 0.15)

### 4.2 Component specifications

**Financial Risk (R_F):** Derived from budget execution patterns, payment timing anomalies, and emergency fund usage. Normalized using Z-score against a 24-month rolling baseline.

**Procurement Risk (R_C):** The most technically sophisticated component. A gradient boosting classifier trained on labeled procurement data produces a risk score for each contract, with SHAP values attributing the score to specific features (single-bidder status, price deviation, vendor concentration, contract splitting, timing anomalies). Normalized using percentile ranking within each procurement period.

**Operational Risk (R_O):** Aggregates legislative attendance, productivity metrics (bills introduced and approved), and cost-efficiency ratios. Normalized to [0,100] using min-max scaling within each institutional category.

**Data Risk (R_D):** Scores the quality and timeliness of public information publication. Inputs include update frequency compliance, completeness rates, and format accessibility. Scored directly against a compliance rubric.

### 4.3 Normalization and aggregation

All components are independently normalized to [0,100] before weighted aggregation. The final IRI score is interpretable as a percentile of institutional risk, where higher scores indicate greater deviation from baseline behavior.

---

## 5. Current measurements

*[PLACEHOLDER: Insert current IRI scores by branch, top-risk contracts identified, and period summary. To be completed during data review phase.]*

The platform currently monitors 1,154 public officials, 1,839 registered contracts, and approximately $3.8 billion ARS in government spending, updated daily.

---

## 6. Validation

Formal validation of the IRI is ongoing. Our validation approach includes three methods:

**Historical backtesting** computes retrospective IRI scores for periods preceding known corruption investigations (e.g., Cuadernos de las coimas, Obra Pública cases). Elevated scores preceding formal investigations would provide empirical support for the index's predictive validity.

**Expert review** involves assessment by practitioners in public procurement, anti-corruption policy, and judicial administration to evaluate face validity and identify blind spots.

**Cross-country replication** applies the IRI methodology to Uruguay and Chile — countries with similar institutional structures but different corruption profiles — to evaluate discriminant validity and international generalizability.

*Validation results will be reported in a forthcoming paper.*

---

## 7. Ethical framework

The IRI is designed as an accountability tool, not an accusation mechanism. The platform accompanies every score with a disclaimer stating that results are algorithmic risk indicators and do not constitute legal judgment or determination of individual responsibility.

The XAI architecture is itself an ethical design choice: it ensures that every risk score is contestable, that affected institutions can review the factors driving their score, and that the methodology is transparent to independent reviewers.

No personal data is stored. All analysis operates at the institutional aggregate level using officially published data.

---

## 8. Implications and future directions

**For anti-corruption policy:** The IRI demonstrates that proactive, data-driven risk monitoring is feasible using existing open government data infrastructure. Governments and oversight bodies can integrate IRI-style indicators into regular audit processes.

**For civic technology:** The platform's open-source architecture makes it immediately replicable. Any country with comparable open data infrastructure can fork the repository and adapt the IRI to its institutional context.

**For academic research:** The IRI provides a new source of high-frequency institutional risk data for quantitative research on corruption, governance, and public administration.

**Future directions include:**
- Formal validation study against historical corruption cases
- Extension to provincial and municipal governments
- Development of an international replication toolkit
- Integration with natural language processing for unstructured government documents

---

## 9. Conclusion

The Institutional Risk Index represents a methodological contribution to the measurement of governance quality: a composite, multi-dimensional, real-time risk indicator derived entirely from official public data and made interpretable through explainable AI. The Mapa de Transparencia platform demonstrates that this approach is technically feasible, politically neutral, and publicly deployable at low cost.

The most significant implication is replicability: the methodology is country-agnostic, the stack is open source, and the data requirements are met by any country with basic open government infrastructure. Argentina is the pilot; the methodology belongs to the world.

---

## References

- Fazekas, M., & Kocsis, G. (2020). Uncovering high-level corruption: Cross-national objective corruption risk indicators using public procurement data. *British Journal of Political Science*, 50(1), 155–164.
- Ferwerda, J., et al. (2017). Gravity models of suspicious transaction reporting: Evidence from an EU-wide dataset. *European Journal on Criminal Policy and Research*, 23(3).
- Lundberg, S. M., & Lee, S. I. (2017). A unified approach to interpreting model predictions. *Advances in Neural Information Processing Systems*, 30.
- Monteverde, V.H. (2022). [Publication in Journal of Financial Crime, Emerald Publishing — full citation to be inserted]
- Transparency International (2024). *Corruption Perceptions Index*. Berlin: TI.
- World Bank (2024). *Worldwide Governance Indicators*. Washington: World Bank Group.

---

*Word count: ~2,800 words (target 3,000–5,000 for final version with validation data)*
*Status: Draft v1.0 — pending data review and validation section completion*
