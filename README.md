# Geospatial Emission and Production Data for Oil and Gas Fields on the Norwegian Continental Shelf

## Overview

This repository contains data and analysis related to the oil and gas fields on the Norwegian Continental Shelf. The goal of this project is to analyze, manipulate, and visualize geospatial data for these fields using Python and various geospatial libraries. The aim of this project is to find the key drivers of the differences in carbon intensity between fields. These drivers will be used to optimize different decarbonization strategies for the fields.

## Table of Contents

1. [Introduction](#introduction)
2. [Data](#data)
3. [Setup](#setup)
4. [Usage](#usage)
5. [Contributing](#contributing)
6. [License](#license)

## Introduction

This project aims to provide a comprehensive analysis of the oil and gas fields located on the Norwegian Continental Shelf. The analysis includes data manipulation, visualization, and interpretation of the geospatial data for fields, pipes, rigs, and wells.

## Data

The data for this project includes:

- Shapefiles for geolocation of fields, pipes, rigs, and wells
- CSV files for information about production, emissions, and other relevant data for each field
- The data is provided by [norskpetroleum.no](https://norskpetroleum.no), [norskeutslipp.no](https://norskeutslipp.no), and [sokkeldirektoratet.no](https://sokkeldirektoratet.no)

## Setup

To get started, clone this repository and set up your environment. Or open the notebooks in Google Collab. Link under usage.

### Prerequisites

- Python 3.9
- Pandas
- Geopandas
- Matplotlib
- Numpy

### Usage

I recommend either cloning the repo or running the code in Google Collab. This project contains several jupyter notebooks. To run them in Google collab, use the following links below.

### 1. Geospatial data analysis

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/percw/Norwegian_oil_gas_decarbonization/blob/main/notebooks/01_data_building/01_production_and_emission_data_building.ipynb)

### 2. Production and emission analysis

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/percw/Norwegian_oil_gas_decarbonization/blob/main/notebooks/02_data_cleaning/02_production_and_emission_data_cleaning.ipynb)

### 3. Data Processing

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/percw/Norwegian_oil_gas_decarbonization/blob/main/notebooks/03_data_processing/03_production_and_emission_data_processing.ipynb)
