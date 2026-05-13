# onsset-pypsa-iep

**Soft-linking framework for integrated energy and electrification planning.**  
Couples [OnSSET](https://github.com/OnSSET) (geospatial electrification) with [PyPSA-Earth](https://github.com/pypsa-meets-earth/pypsa-earth) (power system optimisation) through an iterative cost-of-electricity feedback loop.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)

---

## Overview

This repository implements the **OnSSET–PyPSA-Earth Integrated Energy Planning (IEP)** procedure. The two models exchange information iteratively:

```
Initialise COE⁽⁰⁾
        │
┌───────▼──────────┐
│    OnSSET        │              ← COE_r  (nodal cost of electricity)
│ Electrification  │
│   masterplan     │
└───────┬──────────┘
        │  L_Y,r  (aggregated nodal peak demand)
┌───────▼────────┐
│  PyPSA-Earth   │
│  Generation    │
│  portfolio  +  │
│  transmission  │
└───────┬────────┘
        │  Updated COE_r
        ▼
  |COE⁽ⁱᵗ⁾ − COE⁽ⁱᵗ⁻¹⁾| < ε ?
        │              │
       NO             YES → Integrated Energy Plan ✓
  (next iteration)
```

The loop terminates when the absolute change in nodal COE between consecutive iterations falls below ε (Eq. 5.1 of the thesis). In the Uganda case study, convergence is typically reached in **3–5 iterations**.

---

## Repository structure

```
onsset-pypsa-iep/
│
├── master_v2.py                  # Main pipeline: soft-linking loop orchestrator
├── calculateCOE.py               # Extracts nodal COE from PyPSA-Earth results
│
├── onsset/                       # Extended OnSSET package
│   ├── onsset.py                 # Core electrification model
│   ├── footbridge.py             # Coupling layer: demand aggregation & COE injection
│   ├── hybrids.py                # Hybrid mini-grid (solar+battery) modelling
│   ├── hybrids_wind.py           # Hybrid mini-grid (solar+wind+battery) modelling
│   ├── configModifier.py         # Scenario parameter configuration
│   ├── detailed_tech_parameters.py  # Technology cost and performance assumptions
│   ├── build_country_input.py    # Country-level input preparation
│   ├── specs.py                  # Specification definitions
│   ├── runner.py                 # OnSSET run manager
│   ├── main_runner.py            # Entry point for standalone OnSSET runs
│   ├── gui_runner.py             # Optional GUI runner
│   ├── funcs.py                  # Shared utility functions
│   └── __init__.py
│
├── input/
│   ├── OnSSET_InputFile_Calibrated.csv   # Calibrated OnSSET community-level inputs
│   ├── UGA_specs.xlsx                    # Uganda PyPSA-Earth scenario specifications
│   ├── UGA_gis_inputs_updated.gz         # GIS inputs for PyPSA-Earth network build
│   ├── industrialDem.gpkg                # Industrial demand (geospatial)
│   ├── regionsUpgraded_GADM.gpkg         # Administrative regions (GADM)
│   ├── HGEF.csv                          # Hydropower generation and flow data
│   ├── ug-2-pv.csv                       # Solar PV capacity factor time series
│   ├── ug-2-wind.csv                     # Wind capacity factor time series
│   ├── ug-1/final_clusters.*             # Pre-computed population clusters (shapefile)
│   └── UGA/UGA/UGA_mv_lines.*            # Uganda MV network (shapefile)
│
├── output/                        # Generated at runtime — see Output format below
│
├── detailed_tech_parameters.ipynb # Technology parameter exploration notebook
├── funcs.ipynb                    # Utility function development notebook
│
├── CITATION.cff
├── LICENSE
└── README.md
```

---

## Case study: Uganda (2050)

Three scenarios are implemented, spanning alternative electrification targets and industrial demand trajectories.

| Scenario | Description | Total demand | COE | Grid connected |
|---|---|---|---|---|
| 1 — Policy-Aligned | 100% electrification, Tier 5/3, CO₂ constraint | 94.6 TWh/y | 0.228 €/kWh | 94.8% |
| 2 — Trend Continuation | 75% electrification, Tier 3/3, no CO₂ constraint | 57.1 TWh/y | 0.196 €/kWh | 72.9% |
| 3 — High Industrial | 100% electrification, Tier 5/5, CO₂ constraint, 150% industrial demand | 328.7 TWh/y | 0.251 €/kWh | 99.7% |

Key validated outputs:
- Mutually consistent generation portfolio and electrification masterplan per scenario
- Transmission expansion aligned with Uganda's planned UETCL corridors
- COE range: **0.196–0.251 €/kWh** across scenarios
- Renewable/conventional capacity ratio: **3.3 to 67.7** depending on CO₂ constraint

---

## Installation

> **Prerequisites:** Python ≥ 3.10. PyPSA-Earth must be installed and configured separately — see its [repository](https://github.com/pypsa-meets-earth/pypsa-earth) and [documentation](https://pypsa-meets-earth.github.io/pypsa-earth/).

```bash
# 1. Clone this repository
git clone https://github.com/<your-org>/onsset-pypsa-iep.git
cd onsset-pypsa-iep

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install the OnSSET package in editable mode
pip install -e ./onsset
```

---

## Usage

### Run the full soft-linking pipeline

```bash
python master_v2.py
```

Scenario parameters (electrification tier, demand assumptions, CO₂ constraints) are configured in `onsset/configModifier.py` and `input/UGA_specs.xlsx`.

### Run OnSSET standalone

```bash
python onsset/main_runner.py
```

### Extract COE from an existing PyPSA-Earth network solution

```bash
python calculateCOE.py
```

### Output format

Each iteration produces three files in `output/`:

| File | Contents |
|---|---|
| `{run}_{it}_Results.csv` | Community-level electrification technology allocation |
| `{run}_{it}_Summaries.csv` | Aggregated metrics per region and technology |
| `{run}_{it}_Variables.csv` | Intermediate variables for diagnostic purposes |

---

## Key modules explained

**`master_v2.py`** — implements Algorithm 1 of the thesis: initialises COE, calls OnSSET, aggregates demand, calls PyPSA-Earth, extracts updated COE, and checks the convergence criterion `|COE^(it) − COE^(it−1)| < ε`.

**`calculateCOE.py`** — reads the PyPSA-Earth optimised network and computes the nodal marginal cost of electricity (shadow price of the nodal energy balance constraint) that is fed back into OnSSET.

**`onsset/footbridge.py`** — the coupling layer. Handles (i) geospatial aggregation of grid-connected residential demand from OnSSET clusters to PyPSA-Earth nodes, and (ii) injection of the updated COE into OnSSET's LCOE comparisons.

**`onsset/hybrids.py` / `hybrids_wind.py`** — extended mini-grid modelling for solar+battery and solar+wind+battery configurations, beyond the standard OnSSET technology set.

**`onsset/configModifier.py`** — programmatic control of scenario parameters, enabling batch runs without manual edits to input files.

---

## Input data

Large geospatial and compressed files (`*.gz`, `*.gpkg`, `*.shp`, `*.csv` > 10 MB) are **not tracked by Git**. They are archived on Zenodo at (https://doi.org/10.5281/zenodo.XXXXXXX)](https://zenodo.org/records/20157076).

Download and place them in `input/` before running the pipeline.

| File | Source | Notes |
|---|---|---|
| `OnSSET_InputFile_Calibrated.csv` | Derived from [WorldPop](https://www.worldpop.org/) + [GADM](https://gadm.org/) | Calibrated to Uganda 2022 electrification rate |
| `UGA_gis_inputs_updated.gz` | PyPSA-Earth automated download | Uganda network and resource data |
| `UGA_specs.xlsx` | This work | Scenario-specific PyPSA-Earth configuration |
| `industrialDem.gpkg` | [IEA Uganda Energy Transition Plan](https://www.iea.org/reports/uganda-energy-transition-plan) | Geospatially distributed industrial demand |
| `ug-2-pv.csv`, `ug-2-wind.csv` | [renewables.ninja](https://www.renewables.ninja/) via PyPSA-Earth | Capacity factor time series |
| `HGEF.csv` | Uganda ERA / UETCL | Hydropower generation and flow data |

---

## Dependencies

| Package | Role |
|---|---|
| [PyPSA-Earth](https://github.com/pypsa-meets-earth/pypsa-earth) | Power system optimisation (run externally via Snakemake) |
| [PyPSA](https://github.com/PyPSA/PyPSA) | Network model underlying PyPSA-Earth |
| [pandas](https://pandas.pydata.org/) | Tabular data handling |
| [geopandas](https://geopandas.org/) | Spatial joins and GIS operations |
| [numpy](https://numpy.org/) | Numerical operations |
| [openpyxl](https://openpyxl.readthedocs.io/) | Reading `UGA_specs.xlsx` |

A LP/MILP solver compatible with PyPSA is required (e.g. [HiGHS](https://highs.dev/) — free, or [Gurobi](https://www.gurobi.com/) — commercial). Results in this repository were produced with Gurobi on a 12th-Gen Intel Core i7-1260P (16 cores, 32 GB RAM).

---

## Methodology reference

Full methodological detail is in Chapters 5–6 of the thesis:

- **Section 5.1.2** — soft-linking procedure and variable exchange (Table 5.2)
- **Algorithm 1** — pseudocode of the iterative loop
- **Section 5.2** — planned transmission corridor extension to PyPSA-Earth
- **Chapter 6** — Uganda scenario results and validation

---

## Citation

If you use this framework, please cite:

```bibtex
@phdthesis{caminiti2026system,
  author     = {Caminiti, Corrado Maria},
  title      = {System Optimization Planning},
  school     = {Politecnico di Milano},
  year       = {2026},
  department = {Department of Energy},
  note       = {Supervisor: Prof. Marco Merlo},
}
```

A machine-readable citation is in [`CITATION.cff`](CITATION.cff).

---

## License

MIT — see [`LICENSE`](LICENSE).  
OnSSET and PyPSA-Earth are independently licensed; consult their repositories before redistribution.

---

## Acknowledgements

Developed at the Department of Energy, Politecnico di Milano.  

