# Robeson County Groundwater Monitoring Program (RCGMP)

**Researcher:** Shraya Rajkarnikar | UNC Pembroke — IT / Data Analytics  
**Advisors:** Dr. Maharjan & Dr. Phillippi | UNC Pembroke  
**Timeline:** March 2025 – April 2026
**Stack:** Python · Pandas · NumPy · Matplotlib · Seaborn · SciPy · Geopy · ArcGIS Pro · Excel  
**Presented:** PURC Symposium 2026 — 50+ faculty and community stakeholders

---

## Overview

This research project analyzes the relationship between precipitation and groundwater recharge across 13 monitoring wells in Robeson County, NC using 6+ years of environmental sensor data (2018–2024). The core research question: **is groundwater recharge driven primarily by surface land use or subsurface geology?**

**Key Finding:** Subsurface geology — specifically the presence and thickness of the Black Creek Confining Unit (CU) — is the primary driver of groundwater recharge variability across sites, not surface land use/land cover. Sites where the CU is absent or breached show significantly higher precipitation-to-groundwater correlation, regardless of surface conditions.

---

## Study Area

13 monitoring wells across Robeson County, NC paired with precipitation data from 3 NOAA airport weather stations (KLBT, KMEB, KFAY). Each well is matched to its closest airport station using great-circle distance calculations.

| Well | Coordinates | Closest Airport |
|---|---|---|
| Alamac | 34.591°N, 79.008°W | KLBT |
| Ballard | 34.532°N, 79.291°W | KMEB |
| Bethel Hill | 34.752°N, 79.079°W | KLBT |
| Doc Henderson | 34.781°N, 79.287°W | KMEB |
| James Dial | 34.665°N, 79.281°W | KMEB |
| Knapdale | 34.891°N, 79.031°W | KLBT |
| Landfill | 34.790°N, 78.908°W | KLBT |
| MW1 | 34.693°N, 79.200°W | KMEB |
| MW2 | 34.692°N, 79.200°W | KMEB |
| Orum Water Tower | 34.488°N, 79.024°W | KLBT |
| Prospect | 34.731°N, 79.232°W | KMEB |
| Sam Nobel | 34.689°N, 78.972°W | KLBT |
| Sammy Cox | 34.649°N, 79.048°W | KLBT |

---

## Repository Structure

```
/
├── well_rainfall_analysis.py          # Daily Pearson correlation, 90-day lag sweep
├── rainfall_analysis_0_1.py           # Filtered analysis — rainfall ≥ 0.1 inches
├── significant_rainfall_analysis.py   # Filtered analysis — rainfall ≥ 0.2 inches
├── weekly_rainfall_analysis.py        # Weekly resampled correlation, 12-week lag sweep
├── master_correlation_comparison.py   # All 4 methods compared across all 13 wells
├── doc_henderson_regression.py        # Linear regression + scatter for Doc Henderson
├── make_aquifer_figures_fixed.py      # Hydrogeological aquifer layer profile figures
├── generate_graphs.py                 # Bar chart — max daily correlation across all wells
├── research_script.py                 # James Dial daily average preprocessing
└── maps/
    └── LULC.jpg                       # ArcGIS Pro Land Use Land Cover map — all 13 wells
```

---

## Analysis Methods

### 1. Daily Baseline (`well_rainfall_analysis.py`)
- Merges daily well potentiometric levels with daily precipitation from the nearest airport
- Tests lags from 0–90 days using Pearson correlation
- Outputs: optimal lag (days) + max correlation coefficient per well
- Results saved to `correlation_results.csv`

### 2. Filtered Analysis — 0.1" & 0.2" Thresholds
(`rainfall_analysis_0_1.py`, `significant_rainfall_analysis.py`)
- Runs same lag analysis but filters to only significant rainfall events
- Eliminates noise from trace precipitation that does not drive recharge
- 0.1" filter: removes negligible events | 0.2" filter: significant storm events only

### 3. Weekly Resampled Analysis (`weekly_rainfall_analysis.py`)
- Resamples data to weekly frequency — total rainfall, mean well level
- Tests lags from 0–12 weeks
- Smooths out daily noise for cleaner long-term recharge signal detection

### 4. Master Comparison (`master_correlation_comparison.py`)
- Runs all 4 methods across all 13 wells in one pass
- Uses `geopy` great-circle distance to auto-assign nearest airport per well
- Produces grouped bar chart comparing all 4 methods side by side

### 5. Regression Visualization (`doc_henderson_regression.py`)
- Deep dive into Doc Henderson well — linear regression scatter plot
- Finds optimal lag automatically, plots trend line with R², p-value, correlation

### 6. Aquifer Layer Profiles (`make_aquifer_figures_fixed.py`)
- Generates hydrogeological cross-section figures for 5 key wells
- Visualizes Black Creek Confining Unit thickness and breach status
- Two figures: all 5 wells panel + breach comparison (Doc Henderson vs Bethel Hill vs Alamac)

---

## Key Results

| Well | CU Status | Weekly r | Interpretation |
|---|---|---|---|
| Doc Henderson | **Absent** | 0.227 | High recharge — no barrier |
| Bethel Hill | **11 ft (breach)** | 0.157 | Elevated recharge — thin CU |
| MW1 | 35 ft (intact) | 0.075 | Low recharge — CU intact |
| Alamac | 26 ft (intact) | 0.184 | Moderate — partial CU |
| Orum Water Tower | 11 ft | 0.075 | Low despite thin CU |

**Conclusion:** Wells with absent or breached Black Creek Confining Units show consistently higher precipitation-to-groundwater correlation — demonstrating that geology, not land use, controls recharge at these sites. This has direct implications for Robeson County public health and water resource management.

---

## ArcGIS Pro Maps

The LULC map (`maps/LULC.jpg`) was produced in ArcGIS Pro using Esri, NOAA, U.S. Census Bureau, and NGS data sources. It shows land use classification (crops, trees, built area, water, flooded vegetation) across all 13 well sites — used to test the land use hypothesis and rule out surface conditions as the primary recharge driver.

---

## Data Sources

- **Groundwater data:** NCDEQ Division of Water Resources — [ncwater.org](https://www.ncwater.org)
- **Precipitation data:** NOAA airports KLBT (Lumberton), KMEB (Laurinburg/Maxton), KFAY (Fayetteville)
- **Study period:** 2018–2024
- **Raw data not included** — contact UNC Pembroke RCGMP team for access

---

## Dependencies

```bash
pip install pandas numpy matplotlib seaborn scipy geopy openpyxl
```

---

## Author

**Shraya Rajkarnikar**  
B.S. Information Technology — UNC Pembroke, Expected May 2026  
Research under Dr. Maharjan & Dr. Phillippi  
[LinkedIn](https://linkedin.com/in/shraya-rajkarnikar-510280214) | [GitHub](https://github.com/Shraya-tech)
