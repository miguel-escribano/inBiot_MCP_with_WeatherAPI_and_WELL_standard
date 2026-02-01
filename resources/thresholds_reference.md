# Unified Thresholds Reference – Indoor & Ambient Air Quality

> **Purpose**  
> This file defines all scientifically validated thresholds for indoor and outdoor air-quality and comfort analysis.
>  
> • **Section 1 – Indoor IAQ Standards** → used for WELL v2 and ASHRAE compliance scoring.  
> • **Section 2 – Outdoor (Ambient) Standards** → used only for environmental context and indoor–outdoor comparison.  
>  
> When several limits exist, the **strictest value** (lowest allowable concentration or narrowest comfort range) governs compliance.

---

## Section 1 — Indoor Air Quality Standards (WELL v2 + ASHRAE + WHO Indoor)

These limits apply **inside occupied buildings**.  
They consolidate requirements from:  
- **WELL Building Standard v2** (Features A01–A08 and T01–T07)  
- **ASHRAE 62.1 & 55** (ventilation & thermal comfort)  
- **WHO Indoor Air Quality Guidelines (2010 + 2021)**  

| Parameter | Unit | WELL v2 Limit | ASHRAE / ISO / WHO Indoor Limit | Typical Basis / Feature |
|-----------|------|---------------|--------------------------------|-------------------------|
| **PM2.5** | µg/m³ | ≤ 15 (24 h) · ≤ 8 (annual) | WHO Indoor ≤ 10 (annual) · ≤ 15 (24 h) | A01 – Fine Particulates |
| **PM10** | µg/m³ | ≤ 45 (24 h) · ≤ 20 (annual) | WHO Indoor ≤ 20 (annual) · ≤ 45 (24 h) | A01 – Coarse Particles |
| **CO2** | ppm | ≤ 800 | ASHRAE 62.1 recommends ≤ 1000 | A03 – Ventilation Effectiveness |
| **CO** | ppm | ≤ 9 (8 h) | WHO Indoor ≤ 7 (24 h) | A06 – Combustion Control |
| **NO2** | µg/m³ | ≤ 40 (annual) | WHO Indoor ≤ 10 (annual) | A05 – Combustion Sources |
| **O3** | µg/m³ | ≤ 100 (8 h) | WHO Indoor ≤ 100 (8 h) | A05 – Ozone Control |
| **SO2** | µg/m³ | ≤ 50 (24 h) | WHO Indoor ≤ 40 (24 h) | A05 – Combustion Residue |
| **Formaldehyde (HCHO)** | µg/m³ | ≤ 9 | WHO Indoor ≤ 100 (30 min) | A05 – Enhanced Air Quality |
| **Total VOCs (TVOC)** | µg/m³ | ≤ 500 | WHO Indoor ≤ 300 (recommended) | A05 – Volatile Organics |
| **Temperature** | °C | 20–24 (winter) · 23–26 (summer) | ASHRAE 55 operative 20–26 | T01 / T06 – Thermal Performance |
| **Relative Humidity** | % | 30–60 | ASHRAE 55 · WHO Indoor 40–60 | T07 – Humidity Control |
| **Air Speed** | m/s | ≤ 0.15 (cool) · ≤ 0.25 (warm) | ASHRAE 55 | Thermal Comfort Indicator |
| **Radon** | Bq/m³ | ≤ 100 | WHO Indoor ≤ 100 | A07 – Radon Control |
| **Mold / Bio-contaminants** | CFU/m³ | ≤ 500 | ISO 16000-17 guideline ≤ 500 | A08 – Microbial Control |
| **IAQ Index (0–100)** | – | ≥ 80 = Excellent | – | InBiot Composite Metric |
| **Ventilation Indicator (0–100)** | – | ≥ 80 = Excellent | – | InBiot Proxy for A03 |
| **Thermal Indicator (0–100)** | – | ≥ 80 = Comfortable | – | InBiot Proxy for T01 |
| **Virus Resistance Index (0–100)** | – | ≥ 80 = Ideal | – | InBiot Proxy for A08 |

> **Indoor Scoring Rule**  
> • Use only WELL v2, ASHRAE 62.1 / 55, ISO 16000 and WHO Indoor values.  
> • Ambient (Outdoor) standards must *never* be used for IAQ scoring.  
> • If no indoor limit exists, report as "Not Scored".  
> • Always apply the strictest (health-protective) limit.

---

## Section 2 — Outdoor / Ambient Air Quality Standards (Context Only)

Used solely for environmental reference, ventilation intake assessment, and indoor–outdoor comparisons.  
Values are from the **WHO Ambient Air Quality Guidelines (2021)**.

| Parameter | Unit | WHO Ambient 2021 Limit | Averaging Period | Context / Use |
|-----------|------|------------------------|------------------|---------------|
| **PM2.5** | µg/m³ | ≤ 15 (24 h) · ≤ 5 (annual) | 24 h / annual | Outdoor baseline for filtration comparison |
| **PM10** | µg/m³ | ≤ 45 (24 h) · ≤ 15 (annual) | 24 h / annual | Coarse ambient particles |
| **NO2** | µg/m³ | ≤ 25 (24 h) · ≤ 10 (annual) | 24 h / annual | Traffic / combustion marker |
| **O3** | µg/m³ | ≤ 100 (8 h) | 8 h | Photochemical oxidant |
| **CO** | ppm | ≤ 4 (24 h) | 24 h | Ambient carbon monoxide |
| **SO2** | µg/m³ | ≤ 40 (24 h) · ≤ 20 (annual) | 24 h / annual | Sulphur emissions context |

> **Context-Only Rule**  
> Ambient standards protect public health outdoors and serve only for contextual comparison (e.g., "Indoor PM2.5 = 4 µg/m³ vs Outdoor = 12 µg/m³ → effective filtration").  
> They are not used for WELL scoring.

---

## Section 3 — Thermal & Comfort Metrics (ASHRAE 55 + WELL T01–T07)

| Parameter | Typical Range | Standard Reference | Notes |
|-----------|---------------|-------------------|-------|
| **Operative Temperature** | 20–26 °C | ASHRAE 55 / WELL T01 | Core thermal comfort range |
| **Relative Humidity** | 30–60 % | ASHRAE 55 / WELL T07 | Comfort + Pathogen control |
| **Air Velocity** | ≤ 0.15 m/s | ASHRAE 55 | Draft avoidance |
| **PMV (–0.5 to +0.5)** | Neutral comfort | ASHRAE 55 / ISO 7730 | Optional comfort metric |

---

## Application Summary

| Analysis Type | Standards Applied | Scoring Logic |
|---------------|-------------------|---------------|
| **Indoor IAQ / WELL Compliance** | WELL v2 + ASHRAE 62.1/55 + WHO Indoor + ISO 16000 | Strictest limit applies |
| **Thermal Comfort** | WELL v2 + ASHRAE 55 | Use operative temp + RH band |
| **Outdoor Context / Comparison** | WHO Ambient 2021 | For informational context only |
| **Unmeasured Pollutants** | – | Mark as "Data Unavailable / Not Scored" |
