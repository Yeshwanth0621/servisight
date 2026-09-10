<div align="center">

# ServiSight

### AI-assisted CAD serviceability inspection and tool-access analysis

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-MVP-F59E0B?style=for-the-badge)](#roadmap)

**Detect inaccessible service points before expensive prototypes are built.**

[Overview](#overview) · [How it works](#how-it-works) · [Quick start](#quick-start) · [Roadmap](#roadmap)

</div>

---

## Overview

**ServiSight** is a geometry-driven Design for Serviceability (DFS) inspector for mechanical CAD assemblies. It tests whether repair tools can physically reach service targets—such as bolts, screws, covers, bearings, and filters—without colliding with surrounding components.

Instead of discovering poor maintenance access after a prototype is built, engineers can evaluate tool clearance directly from a 3D assembly and receive an explainable recommendation.

```text
CAD Assembly + Tool Library + Service Targets
                    ↓
      Collision & Clearance Analysis
                    ↓
      Feasible Tool Ranking + 3D Heat Map
```

## The problem

A component may be easy to manufacture but difficult, slow, or unsafe to repair. A bolt can be visible in CAD yet remain impossible to remove because a socket, wrench, ratchet, or screwdriver cannot enter the available space or rotate safely.

ServiSight makes those issues visible early.

| Traditional workflow | With ServiSight |
|---|---|
| Build a prototype, then discover a blocked fastener | Detect blocked access from the CAD assembly |
| Check serviceability manually | Simulate a tool envelope automatically |
| Know that access fails, but not why | Identify the exact collision and blocking part |
| Choose a tool by trial and error | Rank feasible tools from a tool library |

## Core capabilities

- **CAD assembly input** — Load multi-part STL assemblies; STEP support is planned after the MVP.
- **Tool library** — Import a CSV catalog of tools with dimensions, shape, capability, and safety metadata.
- **Tool-envelope simulation** — Represent tools as simple boxes, cylinders, or capsules for fast analysis.
- **Collision detection** — Test the swept tool volume against surrounding assembly components.
- **Clearance scoring** — Measure available space and classify access as accessible, constrained, or blocked.
- **Tool recommendation** — Filter incompatible tools and rank feasible choices using fit, clearance, reach, torque, safety, and history.
- **3D serviceability heat map** — Visualize target status in green, yellow, and red, with blockers highlighted.
- **Explainable results** — Show why a tool was recommended or rejected.

## How it works

### 1. Define the assembly

Export each CAD component as an STL mesh while preserving its assembly position.

```text
data/assembly/
├── gearbox_housing.stl
├── front_cover.stl
├── bearing_cover.stl
├── bolt_01.stl
├── bolt_02.stl
└── bolt_03.stl
```

### 2. Load the tool library

Tools are described in a transparent, editable CSV file.

```csv
tool_id,tool_name,tool_category,shape,width_mm,height_mm,length_mm,tip_size_mm,torque_capacity_nm
T001,10mm Socket,Socket,Cylinder,14,14,80,10,35
T002,10mm Deep Socket,Socket,Cylinder,14,14,110,10,35
T003,10mm Combination Spanner,Spanner,Box,14,8,150,10,45
T004,Large Ratchet,Ratchet,Box,35,28,160,10,70
```

### 3. Mark service targets

Each target supplies the operation, position, required tool size, torque, and permitted approach direction.

```csv
target_id,target_name,x_mm,y_mm,z_mm,approach_x,approach_y,approach_z,fastener_size_mm,required_torque_nm
B001,Top Cover Bolt,50,40,25,0,0,-1,10,22
B002,Recessed Cover Bolt,85,40,25,0,0,-1,10,22
```

### 4. Analyze access

For every compatible tool, ServiSight:

1. Creates a simplified tool envelope.
2. Adds a configurable safety-clearance margin.
3. Sweeps the tool from outside the assembly toward the target.
4. Detects mesh collisions and measures clearance.
5. Rejects inaccessible tools.
6. Ranks valid tools using explainable engineering rules.

### 5. Show the decision

```text
Target: B002 — Recessed Cover Bolt
Required: 10 mm tool, 22 Nm torque

✓ Recommended: 10 mm Deep Socket
  Score: 91 / 100
  Clearance: 12.0 mm
  Reach: adequate
  Status: ACCESSIBLE

✕ Rejected: 10 mm Combination Spanner
  Reason: body collides with gearbox housing

✕ Rejected: Large Ratchet
  Reason: handle sweep is blocked by bearing cover
```

## Serviceability score

The initial score is intentionally explainable. It is not a black-box decision.

\[
\text{Score} = w_fF + w_cC + w_rR + w_tT + w_sS + w_hH
\]

| Symbol | Meaning |
|---|---|
| \(F\) | Functional compatibility: fastener, tool type, and torque match |
| \(C\) | Clearance quality around the tool envelope |
| \(R\) | Reach and target alignment adequacy |
| \(T\) | Expected operational efficiency |
| \(S\) | Safety suitability |
| \(H\) | Historical success score, when maintenance data is available |

A collision automatically rejects the tool regardless of its ranking score.

| Score | Status | Meaning |
|---:|---|---|
| 80–100 | 🟢 Accessible | Tool reaches and operates with safe clearance |
| 50–79 | 🟡 Constrained | Reachable, but clearance or operation is limited |
| 0–49 | 🔴 Blocked | Tool cannot safely reach or operate on the target |

## Tech stack

| Layer | Technology | Purpose |
|---|---|---|
| Language | Python | Core analysis and application logic |
| Geometry | Trimesh + NumPy | STL loading, transforms, collision and clearance analysis |
| Collision backend | python-fcl | Robust mesh collision detection |
| Data | Pandas + CSV | Tool catalog, targets, BOM, and maintenance history |
| Visualization | PyVista | Interactive engineering 3D visualization |
| Dashboard | Streamlit | Fast browser-based interface |
| Future CAD support | OpenCASCADE | STEP geometry and assembly import |

## Project structure

```text
servisight/
├── app.py                       # Streamlit application entry point
├── requirements.txt             # Python dependencies
├── README.md
├── LICENSE
├── data/
│   ├── assembly/                # Multi-part STL assembly
│   ├── tools.csv                # Tool catalog
│   ├── targets.csv              # Service target definitions
│   └── history.csv              # Optional maintenance records
├── src/
│   ├── loader.py                # CAD / mesh loading and validation
│   ├── tool_geometry.py         # Box, cylinder, and capsule tool models
│   ├── collision.py             # Swept-volume and collision analysis
│   ├── clearance.py             # Clearance measurement
│   ├── compatibility.py         # Tool-task compatibility filters
│   ├── scoring.py               # Explainable ranking system
│   └── visualization.py         # PyVista scene helpers
└── tests/                       # Controlled accessible/blocked cases
```

## Quick start

### Prerequisites

- Python 3.11 or later
- A multi-part STL test assembly
- A tool-library CSV

### Installation

```bash
git clone https://github.com/<your-username>/servisight.git
cd servisight

python -m venv .venv
```

**Windows**

```bash
.venv\Scripts\activate
```

**macOS / Linux**

```bash
source .venv/bin/activate
```

```bash
pip install -r requirements.txt
```

### Run the dashboard

```bash
streamlit run app.py
```

Then open the local URL shown in your terminal.

## MVP scope

The MVP prioritizes reliable, demonstrable engineering analysis over broad CAD support.

### Included

- Multi-part STL input
- Manually defined bolt/service targets
- Simple tool geometry: box, cylinder, capsule
- Straight-line approach-path simulation
- Collision and clearance checking
- Tool compatibility filtering
- Explainable top-three tool recommendation
- 3D red/yellow/green access visualization

### Not included yet

- Native SolidWorks, CATIA, Creo, NX, or Fusion file import
- Automatic bolt/fastener recognition
- Full technician ergonomics or hand models
- Arbitrary-angle path planning
- Automatic disassembly-sequence generation
- High-fidelity tool meshes
- ML models trained on real maintenance datasets

## Roadmap

- [x] Define the Design for Serviceability use case
- [x] Define tool catalog and service-target data schemas
- [ ] Load and display a multi-part STL assembly
- [ ] Generate a cylindrical socket tool envelope
- [ ] Test one tool against one bolt target
- [ ] Detect and name collision blockers
- [ ] Add CSV-driven multi-tool analysis
- [ ] Implement clearance-aware serviceability scoring
- [ ] Build Streamlit + PyVista dashboard
- [ ] Validate accessible and deliberately obstructed gearbox targets
- [ ] Add simple maintenance-history ranking
- [ ] Support STEP import through OpenCASCADE
- [ ] Explore ML-assisted serviceability prediction

## Validation target

The first benchmark is a simple gearbox-style assembly containing both accessible and deliberately obstructed fasteners.

**Success means:**

> ServiSight correctly rejects tools that cannot physically reach or operate on a service target, recommends a feasible alternative when one exists, and visually explains the result before a physical prototype is produced.

## Example use cases

- Gearbox cover bolts hidden behind ribs or housings.
- Motor casing fasteners with limited socket clearance.
- Pump assemblies requiring tool access through service openings.
- Battery enclosures with safety-constrained service zones.
- Consumer products where repairability and maintenance time matter.
- Early Design for Serviceability reviews during product development.

## Design principles

- **Geometry first** — Physical reachability must be validated by collision and clearance analysis.
- **Explainable decisions** — Every recommendation should state its evidence and blockers.
- **Simple inputs** — CSV and STL keep the MVP accessible and reproducible.
- **Engineer-in-the-loop** — The tool supports design decisions; it does not replace engineering judgment.
- **Incremental intelligence** — Rules first, historical ranking second, trained ML only when real data exists.

## Contributing

This project is currently an academic MVP. Contributions, ideas, test assemblies, and serviceability rule suggestions are welcome.

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature`.
3. Commit your changes: `git commit -m "Add your feature"`.
4. Push the branch: `git push origin feature/your-feature`.
5. Open a pull request.

## License

This project is released under the [MIT License](LICENSE).

---

<div align="center">

Built for engineers who want products that can be repaired—not just manufactured.

**ServiSight · Serviceability by design**

</div>
