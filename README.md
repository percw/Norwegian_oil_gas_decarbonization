# Decarbonizing the Norwegian Continental Shelf
### *Algorithmic Policy Frameworks for the 2030 "Fit For 55" Mandate*

---

## Strategic Context: May 2026

As of **May 4, 2026**, the Norwegian Continental Shelf (NCS) has reached a pivotal stabilization point. Following a record gas production year in 2024 (124 billion Sm³) and total production holding steady at ~239 MSm³ o.e. through 2025, the industry is now primarily focused on the aggressive 2030 decarbonization milestones. 

With the Norwegian CO2 tax for gas combustion reaching **2,210 NOK/Sm³** in 2025, the economic imperative for surgical decarbonization has moved from theoretical to operational. This repository provides the analytical infrastructure to navigate this transition using high-resolution geospatial data and debiased causal inference.

## Key Analytical Insights

Our models utilize the latest **2024/2025 production baselines** and emission inventories (~10.9 MtCO2e in 2024) to evaluate two primary pathways for the NCS: **Targeted Electrification** versus **Strategic Production Phase-out**.

### 1. The Pareto Efficiency of Production
Our analysis reveals extreme heterogeneity across the shelf. A small cluster of tail-end, carbon-intensive fields—many of which are now reaching their absolute economic limit under current tax regimes—account for a disproportionate share of total emissions. 

<div align="center">
  <img src="assets/scatter_tradeoff.png" alt="Pareto Trade-off" width="80%">
</div>

### 2. Marginal Abatement Cost (MAC)
We derive the real economic cost of abatement. While the first 20% of emissions can be abated at near-zero marginal cost by retiring inefficient tail-end assets, deeper cuts beyond 30% face a sharp inflection point.

<div align="center">
  <img src="assets/mac_curve.png" alt="MAC Curve" width="80%">
</div>

### 3. Core Findings
- **Electrification Strategy:** Electrifying just **13 specific field hubs** is mathematically sufficient to meet the 55% reduction target without any loss in production.
- **Phase-out Strategy:** A targeted production cut of **28%**—focused exclusively on high-intensity fields—can yield a significant **68% reduction** in lifetime emissions.

---

## Project Structure

- **assets/**: High-resolution visualizations and cinematic media.
- **data/**: Curated production and emission datasets (NOD/NorskPetroleum).
- **paper/**: Full-length academic manuscript (Markdown/LaTeX pipeline).
- **src/**: Modular Python research pipeline (DML and Linear Optimization).

## Getting Started

### Prerequisites
- Python 3.9+
- [Pandoc](https://pandoc.org/) (for manuscript compilation)

### Quick Execution
```bash
# Run the full research pipeline
python main.py

# Compile the final manuscript
cd paper && python compile_paper.py
```

---

## Academic Framing

This research bridges the gap between top-down macroeconomic mandates and field-level operational realities. By utilizing **Double Machine Learning** to orthogonalize high-dimensional confounders, we provide an unbiased look at the causal drivers of offshore carbon intensity, rooted in actual 2025 operational metrics.

---
<div align="center">
  <sub>Analyzed with precision. Updated May 2026.</sub>
</div>
