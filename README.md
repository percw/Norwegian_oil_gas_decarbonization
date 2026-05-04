<div align="center">
  <h1>Decarbonizing the Norwegian Continental Shelf</h1>
  <p><em>Geospatial Emission and Production Data Analysis for Oil and Gas Fields</em></p>
  
  [![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
  [![Jupyter Notebook](https://img.shields.io/badge/jupyter-%23FA0F00.svg?style=for-the-badge&logo=jupyter&logoColor=white)](https://jupyter.org/)
  [![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
</div>

## Overview

This repository contains data, analysis, and optimization models focused on the oil and gas fields of the Norwegian Continental Shelf (NCS). The primary objective is to analyze the key drivers of carbon intensity differences between fields and evaluate data-driven strategies to decarbonize the industry. 

Using Python, geospatial libraries, and machine learning techniques, this project processes data for fields, pipes, rigs, and wells to understand how Norway can meet its climate goals while managing energy output.

## Key Findings

Our analysis evaluates two primary decarbonization strategies: platform electrification and strategic field decommissioning. The findings demonstrate practical pathways for Norway to meet its "Fit For 55" commitments (a 55% reduction in emissions by 2030):

- **Electrification Strategy:** To achieve the required emission targets purely through electrification, **13 specific fields must be electrified**.
- **Production Optimization:** An alternative approach involves strategically decommissioning less efficient fields. Holding back overall production by **28%** (compared to depleting all currently active fields) can achieve a massive **68% reduction** in lifetime emissions from Norwegian oil and gas. 

These results highlight the disproportionate impact of certain fields on the overall carbon footprint, allowing for targeted, highly effective interventions.

## Data Sources

The project utilizes comprehensive datasets covering the NCS:
- **Geospatial Data:** Shapefiles detailing the geolocation of fields, pipelines, rigs, and wells.
- **Operational Data:** CSV records containing production volumes, emission metrics, and other relevant field-specific data.

*Sources:* [norskpetroleum.no](https://norskpetroleum.no) • [norskeutslipp.no](https://norskeutslipp.no) • [sokkeldirektoratet.no](https://sokkeldirektoratet.no)

## Setup & Usage

You can run the analysis either by setting up the project locally or directly in Google Colab (recommended for a quick start).

### Prerequisites
- Python 3.9
- Pandas, Geopandas, Matplotlib, Numpy

### Local Setup
```bash
git clone https://github.com/percw/Norwegian_oil_gas_decarbonization.git
cd Norwegian_oil_gas_decarbonization
# pip install -r requirements.txt # (if applicable)
```

### 🚀 Running the Python Pipeline

We have converted the interactive notebooks into a standalone, reproducible Python pipeline. To run the full end-to-end process (Data Building -> Cleaning -> Processing -> Modeling -> Optimization):

```bash
python main.py
```

This orchestrator script will sequentially execute the modules located in the `src/` directory.

### Interactive Notebooks (Google Colab)

Explore the data pipeline step-by-step:

1. **Geospatial Data Analysis**  
   [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/percw/Norwegian_oil_gas_decarbonization/blob/main/notebooks/01_data_building/01_production_and_emission_data_building.ipynb)

2. **Production and Emission Analysis**  
   [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/percw/Norwegian_oil_gas_decarbonization/blob/main/notebooks/02_data_cleaning/02_production_and_emission_data_cleaning.ipynb)

3. **Data Processing**  
   [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/percw/Norwegian_oil_gas_decarbonization/blob/main/notebooks/03_data_processing/03_production_and_emission_data_processing.ipynb)

## Contributing

Contributions, issues, and feature requests are welcome!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
