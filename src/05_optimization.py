# This script was automatically extracted from a Jupyter Notebook.

import os
import sys
import urllib.request
from io import BytesIO
from zipfile import ZipFile

import folium
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from dbfread import DBF
from IPython.display import display

# Google OR tools
from ortools.linear_solver import pywraplp

pd.set_option("display.max_columns", None)

# Importing the field_dataset from the csv file
filepath = "https://raw.githubusercontent.com/percw/Norwegian_oil_gas_decarbonization/main/data/output/emissions_and_production/cleaned/fields_prod_emissions_1997_2023.csv"

# Creating a check if import is successful
try:
    field_data = pd.read_csv(filepath, sep=",")
    print("Data import successful")
    field_data = field_data.rename(
        columns={
            "share_intensity_tco2e/toe_gwp100": "emission_intensity_distributed",
            "kgco2e/toe_int_gwp100": "emission_intensity",
            "total_emissions": "predicted_emissions",
        }
    )

    # Year is %Y datetime
    field_data["year"] = pd.to_datetime(field_data["year"], format="%Y")
except:
    print("field_data import failed")


field_data

# Define the URLs for the shapefile components
base_url = "https://github.com/percw/Norwegian_oil_gas_decarbonization/tree/main/data/raw_data/geo/fields/"
shapefile_components = ["fldArea.shp", "fldArea.shx", "fldArea.dbf"]

# Local directory to save downloaded files
local_dir = "../../data/raw_data/geo/fields"


# Function to download a file from a URL to a local path
def download_file(url, local_path):
    urllib.request.urlretrieve(url, local_path)


# Download the shapefile components if they do not exist locally
if not os.path.exists(local_dir):
    os.makedirs(local_dir)
    for component in shapefile_components:
        local_path = os.path.join(local_dir, os.path.basename(component))
        download_file(base_url + component, local_path)
else:
    print("Field data already exists")


# Function to read shapefile into GeoPandas
def import_field_data():
    fields = gpd.read_file(os.path.join(local_dir, "fldArea.shp"))
    return fields


# Import field data
fields = gpd.read_file("../../data/raw_data/geo/fields/fldArea.shp")

# Now, `fields` contains the GeoDataFrame with the field data
print(fields.head())

# Convert fieldName to lowercase
fields["fieldName"] = fields["fieldName"].str.lower()
fields.head(3)

# Importing the field_dataset from the csv file
filepath_pred = "https://raw.githubusercontent.com/percw/Norwegian_oil_gas_decarbonization/main/data/output/emissions_and_production/cleaned/field_predictions.csv"

# Creating a check if import is successful
try:
    field_pred_data = pd.read_csv(filepath_pred, sep=",")
    print("Data import successful")
    field_pred_data = field_pred_data.rename(
        columns={"total_emissions": "predicted_emissions"}
    )
except:
    print("Data import failed")

field_pred_data.head(3)


# Showing all the fields that are electrified

already_electrified_fields = field_pred_data[field_pred_data["electrified"] == 1]
already_electrified_fields.field.unique()

field_pred_data["predicted_production"].aggregate("sum")

# Adding the geometry to the field_pred_data

field_pred_data = field_pred_data.merge(
    fields[["geometry", "fieldName"]], left_on="field", right_on="fieldName", how="left"
)
field_pred_data.head(3)

# Drop fieldName column
field_pred_data = field_pred_data.drop(columns=["fieldName"])
field_pred_data.head(3)

# Ensuring all fields have entries for every year from 2024 to 2050
fields_to_fill = field_pred_data["field"].unique()
years = list(range(2024, 2050))

# Create a DataFrame with all combinations of fields and years
all_combinations = pd.MultiIndex.from_product(
    [fields_to_fill, years], names=["field", "year"]
).to_frame(index=False)

# Merge with the original data to fill in missing combinations with zero production and zero emissions
field_pred_data_complete = all_combinations.merge(
    field_pred_data, on=["field", "year"], how="left"
)

# Forward fill the fields until reserves are exhausted
field_pred_data_complete["reserve"] = (
    field_pred_data_complete.groupby("field")["reserve"].ffill().fillna(0)
)
field_pred_data_complete["years_left"] = (
    field_pred_data_complete.groupby("field")["years_left"].ffill().fillna(0)
)
field_pred_data_complete["predicted_production"] = (
    field_pred_data_complete.groupby("field")["predicted_production"].ffill().fillna(0)
)
field_pred_data_complete["predicted_emissions"] = (
    field_pred_data_complete.groupby("field")["predicted_emissions"].ffill().fillna(0)
)
field_pred_data_complete["mean_emission_intensity_distributed"] = (
    field_pred_data_complete.groupby("field")["mean_emission_intensity_distributed"]
    .ffill()
    .fillna(0)
)
field_pred_data_complete["electrified"] = (
    field_pred_data_complete.groupby("field")["electrified"].ffill().fillna(0)
)
field_pred_data_complete["cumulative_production"] = (
    field_pred_data_complete.groupby("field")["cumulative_production"].ffill().fillna(0)
)
field_pred_data_complete["geometry"] = (
    field_pred_data_complete.groupby("field")["geometry"].ffill().fillna("")
)

# When reserves are zero, set production and emissions to zero
field_pred_data_complete.loc[
    field_pred_data_complete["reserve"] == 0,
    ["predicted_production", "predicted_emissions"],
] = 0

# Sort by field and year for readability
field_pred_data_complete = field_pred_data_complete.sort_values(
    by=["field", "year"]
).reset_index(drop=True)

# Display the first few rows to verify
display(field_pred_data_complete.head(30))

complete_already_electrified_fields = field_pred_data_complete[
    field_pred_data_complete["electrified"] == 1
]
complete_already_electrified_fields.field.unique()

# Create predicted emission

# Create a dataframe with the total lifetime emissions, production per field

# Group by field and sum the total emissions and production
field_lifetime_df = (
    field_pred_data_complete.groupby("field")
    .agg(
        total_emissions=("predicted_emissions", "sum"),
        predicted_production=("predicted_production", "sum"),
        years_left=("years_left", "max"),
        geometry=("geometry", "first"),
    )
    .reset_index()
)

# Scale the lifetime production and emissions using QuantileTransformer

from sklearn.preprocessing import QuantileTransformer

# Create a copy of the data
field_pred_data_lifetime = field_pred_data_complete.copy()


# Create a column for electrified emissions having 40% reduction in emission intensity
field_pred_data_lifetime["electrified_emissions"] = field_pred_data_lifetime.apply(
    lambda row: row["mean_emission_intensity_distributed"]
    * row["predicted_production"]
    * 0.6
    if row["electrified"] == 0
    else row["predicted_emissions"],
    axis=1,
)

# Calculate lifetime emissions and production
field_pred_data_lifetime["lifetime_production"] = field_pred_data_lifetime.groupby(
    "field"
)["predicted_production"].transform("sum")
field_pred_data_lifetime["lifetime_emissions"] = field_pred_data_lifetime.groupby(
    "field"
)["predicted_emissions"].transform("sum")
field_pred_data_lifetime["lifetime_electrified_emissions"] = (
    field_pred_data_lifetime.groupby("field")["electrified_emissions"].transform("sum")
)

# Initialize QuantileTransformer
quantile_transformer = QuantileTransformer(output_distribution="uniform")

# Apply QuantileTransformer
field_pred_data_lifetime[
    [
        "scaled_lifetime_production",
        "scaled_lifetime_emissions",
        "scaled_electrified_emissions",
    ]
] = quantile_transformer.fit_transform(
    field_pred_data_lifetime[
        ["lifetime_production", "lifetime_emissions", "lifetime_electrified_emissions"]
    ]
)

# Display the scaled values to check the distribution
display(
    field_pred_data_lifetime[
        [
            "scaled_lifetime_production",
            "scaled_lifetime_emissions",
            "scaled_electrified_emissions",
        ]
    ].describe()
)

field_pred_data_lifetime.head(3)

field_pred_data_lifetime[field_pred_data_lifetime["electrified"] == 1]

lifetime_pred_df = (
    field_pred_data_lifetime.groupby("field")
    .agg(
        total_lifetime_emissions=("lifetime_emissions", "first"),
        total_lifetime_production=("lifetime_production", "first"),
        total_lifetime_electrified_emissions=(
            "lifetime_electrified_emissions",
            "first",
        ),
        geometry=("geometry", "first"),
    )
    .reset_index()
    .copy()
)

lifetime_pred_df.head(5)


lifetime_pred_df.field.unique()

# Showing the field "e grieg"
lifetime_pred_df[lifetime_pred_df["field"] == "edvard grieg"]

# Apply scaler = MinMaxScaler()
from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler()
lifetime_pred_df[
    [
        "scaled_lifetime_production",
        "scaled_lifetime_emissions",
        "scaled_electrified_emissions",
    ]
] = scaler.fit_transform(
    lifetime_pred_df[
        [
            "total_lifetime_production",
            "total_lifetime_emissions",
            "total_lifetime_electrified_emissions",
        ]
    ]
)

lifetime_pred_df.head(3)

# Create a copy of the dataframe to work with
lifetime_pred_df_copy = lifetime_pred_df.copy()

# Fit the MinMaxScaler on the necessary columns

scaled_data = scaler.fit_transform(
    lifetime_pred_df_copy[["total_lifetime_production", "total_lifetime_emissions"]]
)

# Create new columns for normalized production and emissions
lifetime_pred_df_copy["normalized_production"] = scaled_data[:, 0]
lifetime_pred_df_copy["normalized_emissions"] = scaled_data[:, 1]

# Create the OR-Tools solver
solver = pywraplp.Solver.CreateSolver("SCIP")
if not solver:
    raise Exception("Solver not created.")

# Number of fields
num_fields = len(lifetime_pred_df_copy)

# Create binary decision variables for each field
x = [solver.BoolVar(f"x_{i}") for i in range(num_fields)]

# Set lambda (tradeoff parameter)
lambda_ = 0.8

# Objective function: Maximize production and minimize emissions
objective = solver.Objective()
for i in range(num_fields):
    objective.SetCoefficient(
        x[i],
        lambda_ * lifetime_pred_df_copy["normalized_production"][i]
        - (1 - lambda_) * lifetime_pred_df_copy["normalized_emissions"][i],
    )
objective.SetMaximization()

# Solve the problem
status = solver.Solve()

# Check if a solution has been found
if status == pywraplp.Solver.OPTIMAL:
    print("Optimal solution found.")
elif status == pywraplp.Solver.FEASIBLE:
    print("A potentially suboptimal solution was found.")
else:
    print("No solution found.")

# Get the results
decision_variables = [x[i].solution_value() for i in range(num_fields)]

# Calculate optimized production and emissions
optimized_production = (
    np.array(decision_variables) * lifetime_pred_df_copy["total_lifetime_production"]
)
optimized_emissions = (
    np.array(decision_variables) * lifetime_pred_df_copy["total_lifetime_emissions"]
)

# Add optimized production and emissions to the copied dataframe for review
lifetime_pred_df_copy["optimized_production"] = optimized_production
lifetime_pred_df_copy["optimized_emissions"] = optimized_emissions

# Calculate total and average values
total_production = optimized_production.sum()
total_emissions = optimized_emissions.sum()
average_emission_intensity = (
    total_emissions / total_production if total_production != 0 else 0
)

# Identify fields open and closed
fields_open = lifetime_pred_df_copy[lifetime_pred_df_copy["optimized_production"] > 0][
    "field"
].unique()
fields_closed = lifetime_pred_df_copy[
    lifetime_pred_df_copy["optimized_production"] == 0
]["field"].unique()
num_fields_open = len(fields_open)
num_fields_closed = len(fields_closed)

# Summary prints
print(f"Optimization completed with status: {status}")
print(f"Lambda: {lambda_}")
print(f"Total production: {total_production}")
print(f"Total emissions: {total_emissions}")
print(f"Average emission intensity: {average_emission_intensity}")
print(f"Number of fields open: {num_fields_open}")
print(f"Fields open: {fields_open}")
print(f"Number of fields closed: {num_fields_closed}")
print(f"Fields closed: {fields_closed}")


def optimize_field_allocations(df, lambdas):
    # Create a copy of the dataframe to work with
    df = df.copy()

    # Fit the MinMaxScaler on the necessary columns
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(
        df[["total_lifetime_production", "total_lifetime_emissions"]]
    )

    # Create new columns for normalized production and emissions
    df["normalized_production"] = scaled_data[:, 0]
    df["normalized_emissions"] = scaled_data[:, 1]

    results = {}

    for lambda_ in lambdas:
        # Create the OR-Tools solver
        solver = pywraplp.Solver.CreateSolver("SCIP")
        if not solver:
            raise Exception("Solver not created.")

        # Number of fields
        num_fields = len(df)

        # Create binary decision variables for each field
        x = [solver.BoolVar(f"x_{i}") for i in range(num_fields)]

        # Objective function: Maximize production and minimize emissions
        objective = solver.Objective()
        for i in range(num_fields):
            objective.SetCoefficient(
                x[i],
                lambda_ * df["normalized_production"][i]
                - (1 - lambda_) * df["normalized_emissions"][i],
            )
        objective.SetMaximization()

        # Solve the problem
        status = solver.Solve()

        # Check if a solution has been found
        if status == pywraplp.Solver.OPTIMAL:
            print(f"Optimal solution found for lambda = {lambda_}.")
        elif status == pywraplp.Solver.FEASIBLE:
            print(
                f"A potentially suboptimal solution was found for lambda = {lambda_}."
            )
        else:
            print(f"No solution found for lambda = {lambda_}.")
            continue

        # Get the results
        decision_variables = [x[i].solution_value() for i in range(num_fields)]

        # Calculate optimized production and emissions
        optimized_production = (
            np.array(decision_variables) * df["total_lifetime_production"]
        )
        optimized_emissions = (
            np.array(decision_variables) * df["total_lifetime_emissions"]
        )

        # Create a result DataFrame for the current lambda
        result_df = df.copy()
        result_df["optimized_production"] = optimized_production
        result_df["optimized_emissions"] = optimized_emissions

        # Add the result DataFrame to the results dictionary
        results[lambda_] = result_df

    return results


lambdas = [0.8, 0.85, 0.875, 0.9, 1]

df = lifetime_pred_df.copy()

results = optimize_field_allocations(df, lambdas)

for lambda_, df in results.items():
    print(f"\nResults for lambda = {lambda_}")
    print(df)

def print_fields_to_close(results, lambdas):
    for lambda_ in lambdas:
        df = results[lambda_]
        fields_closed = df[df["optimized_production"] == 0]["field"].unique()
        num_fields_closed = len(fields_closed)

        print(f"Lambda = {lambda_}:")
        print(f"Number of fields closed: {num_fields_closed}")
        print(f"Fields closed: {fields_closed}")
        print("\n")


print_fields_to_close(results, lambdas)

field_pred_data_lifetime

field_pred_data_lifetime["predicted_emissions"].sum()

field_pred_data_lifetime["predicted_production"].sum()


import matplotlib.pyplot as plt
import math


def plot_yearly_production_emissions(results, lambdas, field_pred_data_lifetime):
    # Calculate baseline emissions (all fields open)
    baseline_yearly_emissions = field_pred_data_lifetime.groupby("year")[
        "predicted_emissions"
    ].sum()
    baseline_total_emissions = baseline_yearly_emissions.sum() * 0.84

    # Calculate baseline production (all fields open)
    baseline_yearly_production = field_pred_data_lifetime.groupby("year")[
        "predicted_production"
    ].sum()
    baseline_total_production = baseline_yearly_production.sum()

    # Calculate baseline production (all fields open)
    baseline_yearly_production = field_pred_data_lifetime.groupby("year")[
        "predicted_production"
    ].sum()

    plt.figure(figsize=(14, 8))

    # Iterate over the results for each lambda
    for lambda_ in lambdas:
        df = results[lambda_]
        fields_open = df[df["optimized_production"] > 0]["field"].unique()

        # Extract yearly data for open fields
        yearly_data = field_pred_data_lifetime[
            field_pred_data_lifetime["field"].isin(fields_open)
        ]

        # Sum the production and emissions for each year
        yearly_production = yearly_data.groupby("year")["predicted_production"].sum()
        yearly_emissions = (
            yearly_data.groupby("year")["predicted_emissions"].sum() * 0.84
        )

        # Calculate total emissions for the current lambda
        total_emissions = yearly_emissions.sum()
        total_production = yearly_production.sum()

        # Calculate emission reduction
        emission_reduction = np.round(
            ((baseline_total_emissions - total_emissions) / baseline_total_emissions)
            * 100,
            1,
        )

        # Calculate production reduction
        production_reduction = np.round(
            ((baseline_total_production - total_production) / baseline_total_production)
            * 100,
            1,
        )

        # Calculate the emission intensity
        emission_intensity = np.round(
            total_emissions / (total_production * 100) if total_production != 0 else 0,
            1,
        )

        # Plot production volumes
        plt.plot(
            yearly_production.index,
            yearly_production.values,
            label=f"Lambda: {lambda_}\nProduction Reduction: {math.trunc(production_reduction)}%,\nEmission Reduction: {math.trunc(emission_reduction)}%,\nEstimated Emission intensity: {math.trunc(emission_intensity)} kgCO2e/toe.",
            linestyle="--",
        )

        # Plot emissions
        # plt.plot(yearly_emissions.index, yearly_emissions.values, label=f'Emissions (λ={lambda_}, Reduction: {emission_reduction:.2f}%)', linestyle='--')

    # Add labels and legend
    plt.xlabel("Year")
    plt.ylabel("Million SM3 Oil Equivalent")
    plt.title("Production Ramp-down Scenarios and Emission Reductions")
    plt.legend()
    plt.grid(True)
    plt.show()


plot_yearly_production_emissions(results, lambdas, field_pred_data_lifetime)

# Printing the Fields to shut down for the different lambda values


def print_fields_to_close(results, lambdas):
    for lambda_ in lambdas:
        df = results[lambda_]
        fields_closed = df[df["optimized_production"] == 0]["field"].unique()
        num_fields_closed = len(fields_closed)
        print(f"Lambda = {lambda_}:")
        print(f"Number of fields closed: {num_fields_closed}")
        print(f"Fields closed: {fields_closed}")
        print("\n")


print_fields_to_close(results, lambdas)


def plot_yearly_production_emissions(results, lambdas, field_pred_data_lifetime):
    # Calculate baseline emissions (all fields open)
    baseline_yearly_emissions = field_pred_data_lifetime.groupby("year")[
        "predicted_emissions"
    ].sum()
    baseline_total_emissions = baseline_yearly_emissions.sum()

    # Calculate baseline production (all fields open)
    baseline_yearly_production = field_pred_data_lifetime.groupby("year")[
        "predicted_production"
    ].sum()
    baseline_total_production = baseline_yearly_production.sum()

    # Calculate baseline production (all fields open)
    baseline_yearly_production = field_pred_data_lifetime.groupby("year")[
        "predicted_production"
    ].sum()

    plt.figure(figsize=(14, 8))

    # Iterate over the results for each lambda
    for lambda_ in lambdas:
        df = results[lambda_]
        fields_open = df[df["optimized_production"] > 0]["field"].unique()

        # Extract yearly data for open fields
        yearly_data = field_pred_data_lifetime[
            field_pred_data_lifetime["field"].isin(fields_open)
        ]

        # Sum the production and emissions for each year
        yearly_production = yearly_data.groupby("year")["predicted_production"].sum()
        yearly_emissions = (
            yearly_data.groupby("year")["predicted_emissions"].sum() * 0.84
        )

        # Calculate total emissions for the current lambda
        total_emissions = yearly_emissions.sum()
        total_production = yearly_production.sum()

        # Calculate emission reduction
        emission_reduction = np.round(
            ((baseline_total_emissions - total_emissions) / baseline_total_emissions)
            * 100,
            1,
        )

        # Calculate production reduction
        production_reduction = np.round(
            ((baseline_total_production - total_production) / baseline_total_production)
            * 100,
            1,
        )

        # Calculate the emission intensity
        emission_intensity = np.round(
            total_emissions / (total_production * 100) if total_production != 0 else 0,
            1,
        )

        # Plot emissions
        plt.plot(
            yearly_emissions.index,
            yearly_emissions.values,
            label=f"λ={lambda_} - Emission Reduction: {math.trunc(emission_reduction)}%),\nProduction Reduction: {math.trunc(production_reduction)}%,\nEstimated Emission intensity: {math.trunc(emission_intensity)} kgCO2e/toe.",
            linestyle="-",
        )

    # Add labels and legend
    plt.xlabel("Year")
    plt.ylabel("Emissions tCO2e")
    plt.title("Yearly Emissions")
    plt.legend()
    plt.grid(True, which="both", linestyle="--", linewidth=0.25)

    plt.show()


plot_yearly_production_emissions(results, lambdas, field_pred_data_lifetime)

# Plotting the annual emission intensity for the fields


def plot_annual_emission_intensity(results, lambdas, field_pred_data_lifetime):
    constant = 0
    for lambda_ in lambdas:
        df = results[lambda_]
        fields_open = df[df["optimized_production"] > 0]["field"].unique()

        # Extract yearly data for open fields
        yearly_data = field_pred_data_lifetime[
            field_pred_data_lifetime["field"].isin(fields_open)
        ]

        # Sum the production and emissions for each year
        yearly_production = yearly_data.groupby("year")["predicted_production"].sum()
        yearly_emissions = (
            yearly_data.groupby("year")["predicted_emissions"].sum() * 0.84
        )

        # Calculate emission intensity
        emission_intensity = yearly_emissions / (yearly_production * 100)

        if emission_intensity.iloc[0] > constant:
            constant = emission_intensity.iloc[0]

        # Plot emission intensity
        plt.plot(
            emission_intensity.index,
            emission_intensity.values,
            label=f"λ={lambda_}",
            linestyle="--",
        )

    # Add labels and legend
    plt.xlabel("Year")
    plt.ylabel("Emission Intensity (kgCO2e/TOE)")
    plt.title("Annual Emission Intensity")
    plt.legend()
    plt.grid(True)
    plt.show()


plot_annual_emission_intensity(results, lambdas, field_pred_data_lifetime)


def plot_scatter_tradeoff(results, lambdas, field_pred_data_lifetime):
    data_points = []

    for lambda_ in lambdas:
        df = results[lambda_]
        fields_open = df[df["optimized_production"] > 0]["field"].unique()

        # Extract yearly data for open fields
        yearly_data = field_pred_data_lifetime[
            field_pred_data_lifetime["field"].isin(fields_open)
        ]

        # Sum the production and emissions for each year
        yearly_production = yearly_data.groupby("year")["predicted_production"].sum()
        yearly_emissions = yearly_data.groupby("year")["predicted_emissions"].sum()

        for year in yearly_production.index:
            data_points.append(
                (year, yearly_production[year], yearly_emissions[year], lambda_)
            )

    # Convert to DataFrame for plotting
    plot_df = pd.DataFrame(
        data_points, columns=["Year", "Production", "Emissions", "Lambda"]
    )

    plt.figure(figsize=(14, 8))
    scatter = plt.scatter(
        plot_df["Production"],
        plot_df["Emissions"],
        c=plot_df["Lambda"],
        cmap="viridis",
        alpha=0.6,
        edgecolors="w",
    )
    plt.xlabel("Production Volume")
    plt.ylabel("Emissions")
    plt.title("Trade-off between Production Volume and Emissions")
    cbar = plt.colorbar(scatter)
    cbar.set_label("Lambda")
    plt.grid(True)
    plt.show()


plot_scatter_tradeoff(results, lambdas, field_pred_data_lifetime)

# Checking the total production volume in 2021

field_data[field_data["year"] == "2021"]["net_oil_eq_prod_yearly_mill_sm3"].sum()
field_data[field_data["year"] == "2021"]["net_oil_eq_prod_yearly_mill_sm3"].sum()

field_data

lifetime_pred_df

lifetime_pred_df

lambdas

def optimize_electrification(df, lambdas, electrification_levels):
    results = {}

    for electrification_level in electrification_levels:
        num_fields = len(df)
        print(len(df))
        num_electrified_fields = int(electrification_level * num_fields / 100)

        for lambda_ in lambdas:
            # Create the OR-Tools solver
            solver = pywraplp.Solver.CreateSolver("SCIP")
            if not solver:
                raise Exception("Solver not created.")

            # Create binary decision variables for electrification
            e = [solver.BoolVar(f"e_{i}") for i in range(num_fields)]

            # Objective function: Maximize production and minimize emissions
            objective = solver.Objective()
            for i in range(num_fields):
                # Adjusted emissions
                adjusted_emissions = (
                    e[i] * df["total_lifetime_electrified_emissions"][i]
                    + (1 - e[i]) * df["total_lifetime_emissions"][i]
                )
                # Set the coefficients for the objective
                objective.SetCoefficient(
                    e[i], lambda_ * df["total_lifetime_production"][i]
                )
                objective.SetCoefficient(
                    e[i], -(1 - lambda_) * df["total_lifetime_electrified_emissions"][i]
                )
                objective.SetCoefficient(
                    e[i], (1 - lambda_) * df["total_lifetime_emissions"][i]
                )
            objective.SetMaximization()

            # Constraint: Number of electrified fields should match the specified electrification level
            solver.Add(solver.Sum(e) == num_electrified_fields)

            # Solve the problem
            status = solver.Solve()

            # Check if a solution has been found
            if status == pywraplp.Solver.OPTIMAL:
                print(
                    f"Optimal solution found for lambda = {lambda_} and electrification level = {electrification_level}%."
                )
            elif status == pywraplp.Solver.FEASIBLE:
                print(
                    f"A potentially suboptimal solution was found for lambda = {lambda_} and electrification level = {electrification_level}%."
                )
            else:
                print(
                    f"No solution found for lambda = {lambda_} and electrification level = {electrification_level}%."
                )
                continue

            # Get the results
            electrification_decisions = [
                e[i].solution_value() for i in range(num_fields)
            ]

            # Calculate optimized emissions
            optimized_emissions = (
                np.array(electrification_decisions)
                * df["total_lifetime_electrified_emissions"]
                + (1 - np.array(electrification_decisions))
                * df["total_lifetime_emissions"]
            )

            # Calculate optimized production (should remain the same since electrification doesn't affect production directly)
            optimized_production = df["total_lifetime_production"]

            # Create a result DataFrame for the current lambda and electrification level
            result_df = df.copy()
            result_df["optimized_production"] = optimized_production
            result_df["optimized_emissions"] = optimized_emissions
            result_df["electrification_decision"] = electrification_decisions

            # Add the result DataFrame to the results dictionary
            results[(lambda_, electrification_level)] = result_df

    return results


electrification_levels = [0, 5, 10, 15, 20, 30, 40, 50]
lambdas = [0.8, 0.85, 0.875, 0.9, 1]

results_with_electrification = optimize_electrification(
    df, lambdas, electrification_levels
)


# Function to print fields to electrify for each combination of lambda and electrification level
def print_fields_to_electrify(results, lambdas, electrification_levels):
    for lambda_ in lambdas:
        for electrification_level in electrification_levels:
            df = results[(lambda_, electrification_level)]
            fields_electrified = df[df["electrification_decision"] == 1][
                "field"
            ].unique()
            num_fields_electrified = len(fields_electrified)

            print(
                f"Lambda = {lambda_}, Electrification Level = {electrification_level}%:"
            )
            print(f"Number of fields electrified: {num_fields_electrified}")
            print(f"Fields electrified: {fields_electrified}")
            print("\n")


print_fields_to_electrify(results_with_electrification, lambdas, electrification_levels)

df_2 = df.copy()

electrified_field_names = field_pred_data[field_pred_data["electrified"] == 1][
    "field"
].unique()
# adding a column for electrified from field_pred_data_lifetime

df_2["electrified"] = df_2["field"].apply(
    lambda x: 1 if x in electrified_field_names else 0
)

df_2


# Remove all fields that are already electrified

df_2 = df_2[df_2["electrified"] == 0]

# drop the electrified column

df_2 = df_2.drop(columns=["electrified"])

# reset index
df_2 = df_2.reset_index(drop=True)


def optimize_electrification_2(df, lambdas, electrification_levels):
    results = {}

    for electrification_level in electrification_levels:
        num_fields = len(df)
        print(len(df))
        num_electrified_fields = int(electrification_level * num_fields / 100)

        for lambda_ in lambdas:
            # Create the OR-Tools solver
            solver = pywraplp.Solver.CreateSolver("SCIP")
            if not solver:
                raise Exception("Solver not created.")

            # Create binary decision variables for electrification
            e = [solver.BoolVar(f"e_{i}") for i in range(num_fields)]

            # Objective function: Maximize production and minimize emissions
            objective = solver.Objective()
            for i in range(num_fields):
                # Adjusted emissions
                adjusted_emissions = (
                    e[i] * df["total_lifetime_electrified_emissions"][i]
                    + (1 - e[i]) * df["total_lifetime_emissions"][i]
                )
                # Set the coefficients for the objective
                objective.SetCoefficient(
                    e[i], lambda_ * df["total_lifetime_production"][i]
                )
                objective.SetCoefficient(
                    e[i], -(1 - lambda_) * df["total_lifetime_electrified_emissions"][i]
                )
                objective.SetCoefficient(
                    e[i], (1 - lambda_) * df["total_lifetime_emissions"][i]
                )
            objective.SetMaximization()

            # Constraint: Number of electrified fields should match the specified electrification level
            solver.Add(solver.Sum(e) == num_electrified_fields)

            # Solve the problem
            status = solver.Solve()

            # Check if a solution has been found
            if status == pywraplp.Solver.OPTIMAL:
                print(
                    f"Optimal solution found for lambda = {lambda_} and electrification level = {electrification_level}%."
                )
            elif status == pywraplp.Solver.FEASIBLE:
                print(
                    f"A potentially suboptimal solution was found for lambda = {lambda_} and electrification level = {electrification_level}%."
                )
            else:
                print(
                    f"No solution found for lambda = {lambda_} and electrification level = {electrification_level}%."
                )
                continue

            # Get the results
            electrification_decisions = [
                e[i].solution_value() for i in range(num_fields)
            ]

            # Calculate optimized emissions
            optimized_emissions = (
                np.array(electrification_decisions)
                * df["total_lifetime_electrified_emissions"]
                + (1 - np.array(electrification_decisions))
                * df["total_lifetime_emissions"]
            )

            # Calculate optimized production (should remain the same since electrification doesn't affect production directly)
            optimized_production = df["total_lifetime_production"]

            # Create a result DataFrame for the current lambda and electrification level
            result_df = df.copy()
            result_df["optimized_production"] = optimized_production
            result_df["optimized_emissions"] = optimized_emissions
            result_df["electrification_decision"] = electrification_decisions

            # Add the result DataFrame to the results dictionary
            results[(lambda_, electrification_level)] = result_df

    return results


electrification_levels = [0, 5, 10, 15, 20, 30, 40, 50]
lambdas = [0.1, 0.8, 0.85, 0.875, 1]

results_with_electrification_2 = optimize_electrification_2(
    df=df_2, lambdas=lambdas, electrification_levels=electrification_levels
)


# Function to print fields to electrify for each combination of lambda and electrification level
def print_fields_to_electrify(results, lambdas, electrification_levels):
    for lambda_ in lambdas:
        for electrification_level in electrification_levels:
            df = results[(lambda_, electrification_level)]
            fields_electrified = df[df["electrification_decision"] == 1][
                "field"
            ].unique()
            num_fields_electrified = len(fields_electrified)

            print(
                f"Lambda = {lambda_}, Electrification Level = {electrification_level}%:"
            )
            print(f"Number of fields electrified: {num_fields_electrified}")
            print(f"Fields electrified: {fields_electrified}")
            print("\n")


print_fields_to_electrify(
    results_with_electrification_2, lambdas, electrification_levels
)


field_pred_data

results_with_electrification

def check_electrified_fields_consistency(results, lambdas, electrification_levels):
    for electrification_level in electrification_levels:
        # Initialize a dictionary to store the electrified fields for each lambda
        electrified_fields_dict = {}

        for lambda_ in lambdas:
            df = results[(lambda_, electrification_level)]
            fields_electrified = set(
                df[df["electrification_decision"] == 1]["field"].unique()
            )
            electrified_fields_dict[lambda_] = fields_electrified

        # Compare the sets of electrified fields across different lambdas
        reference_lambda = lambdas[0]
        reference_fields = electrified_fields_dict[reference_lambda]

        consistency_flag = True

        # Printing the fields to electrify for each lambda
        print(
            f"Fields to electrify for electrification level {electrification_level}%:"
        )
        for lambda_, fields in electrified_fields_dict.items():
            print(f"Lambda {lambda_}: {fields}")

        for lambda_ in lambdas[1:]:
            if electrified_fields_dict[lambda_] != reference_fields:
                consistency_flag = False
                print(
                    f"Inconsistency found for electrification level {electrification_level}% between lambda {reference_lambda} and lambda {lambda_}."
                )
                print(f"Fields for lambda {reference_lambda}: {reference_fields}")
                print(
                    f"Fields for lambda {lambda_}: {electrified_fields_dict[lambda_]}\n"
                )

        if consistency_flag:
            print(
                f"Electrified fields are consistent across all lambdas for electrification level {electrification_level}%.\n"
            )


check_electrified_fields_consistency(
    results_with_electrification, lambdas, electrification_levels
)

def prepare_heatmap_data_single_lambda(results, lambda_, electrification_levels):
    fields = results[(lambda_, electrification_levels[0])]["field"].unique()
    heatmap_data = pd.DataFrame(index=fields)

    for electrification_level in electrification_levels:
        df = results[(lambda_, electrification_level)]
        electrified = df["electrification_decision"]
        num_fields_electrified = int(electrification_level * len(df) / 100)
        column_name = f"Elec={electrification_level}% (N={num_fields_electrified})"
        heatmap_data[column_name] = electrified.values

    return heatmap_data


def plot_heatmap(heatmap_data, lambda_):
    plt.figure(figsize=(16, 12))
    sns.heatmap(heatmap_data, cmap="Blues", cbar=False, linewidths=0.5)
    plt.title(
        f"Electrified Fields Across Different Electrification Levels",
        fontsize=16,
    )
    plt.xlabel("Electrification Level and Number of Fields Electrified", fontsize=14)
    plt.ylabel("Fields", fontsize=14)
    plt.xticks(rotation=45)
    plt.yticks(rotation=0)
    plt.show()


# Choose the lambda value to display
lambda_to_display = 0.8

# Prepare heatmap data for the chosen lambda
heatmap_data_single_lambda = prepare_heatmap_data_single_lambda(
    results_with_electrification, lambda_to_display, electrification_levels
)

# Plot the heatmap
plot_heatmap(heatmap_data_single_lambda, lambda_to_display)

import matplotlib.pyplot as plt


def prepare_bar_chart_data_single_lambda(results, lambda_, electrification_levels):
    fields = results[(lambda_, electrification_levels[0])]["field"].unique()
    bar_chart_data = pd.DataFrame(index=fields)

    for electrification_level in electrification_levels:
        df = results[(lambda_, electrification_level)]
        electrified = df["electrification_decision"]
        column_name = f"Elec={electrification_level}%"
        bar_chart_data[column_name] = electrified.values

    return bar_chart_data


def plot_stacked_bar_chart(bar_chart_data, lambda_):
    bar_chart_data.plot(kind="bar", stacked=True, figsize=(16, 12), colormap="Blues")
    plt.title(
        f"Electrification Decisions Across Different Electrification Levels (λ = {lambda_})",
        fontsize=16,
    )
    plt.xlabel("Fields", fontsize=14)
    plt.ylabel("Electrification Decision", fontsize=14)
    plt.xticks(rotation=45)
    plt.yticks(rotation=0)
    plt.legend(
        title="Electrification Level", bbox_to_anchor=(1.05, 1), loc="upper left"
    )
    plt.show()


# Prepare bar chart data for the chosen lambda
bar_chart_data_single_lambda = prepare_bar_chart_data_single_lambda(
    results_with_electrification, lambda_to_display, electrification_levels
)

# Plot the stacked bar chart
plot_stacked_bar_chart(bar_chart_data_single_lambda, lambda_to_display)


import matplotlib.pyplot as plt


def calculate_total_emissions(results, lambda_, electrification_levels):
    total_emissions = []

    for electrification_level in electrification_levels:
        df = results[(lambda_, electrification_level)]
        total_emissions.append(df["optimized_emissions"].sum())

    return total_emissions


def plot_total_emissions(total_emissions, electrification_levels, lambda_):
    plt.figure(figsize=(12, 6))
    plt.plot(
        electrification_levels, total_emissions, marker="o", linestyle="-", color="b"
    )
    plt.title(f"Total Emissions Across Different Electrification Levels", fontsize=16)
    plt.xlabel("Electrification Level (%)", fontsize=14)
    plt.ylabel("Total Emissions", fontsize=14)
    plt.ylim(0, max(total_emissions) * 1.1)
    plt.grid(True, which="both", linestyle="--", linewidth=0.25)
    plt.show()


# Calculate total emissions for the chosen lambda
lambda_to_display = 0.8
total_emissions = calculate_total_emissions(
    results_with_electrification, lambda_to_display, electrification_levels
)

# Plot the total emissions
plot_total_emissions(total_emissions, electrification_levels, lambda_to_display)

# Show the Y axis as Total Emissions in % reduction for each Eelectrification Level. Use the 0 % electrifitcation level as the baseline

# Calculate the baseline emissions
baseline_emissions = total_emissions[0]

# Calculate the percentage reduction in emissions for each electrification level
percent_reduction = [
    ((baseline_emissions - emissions) / baseline_emissions) * 100
    for emissions in total_emissions
]

# Plot the percentage reduction in emissions
plt.figure(figsize=(12, 6))
plt.plot(
    electrification_levels, percent_reduction, marker="o", linestyle="-", color="b"
)
plt.title(
    "Percentage Reduction in Total Emissions Across Different Electrification Levels",
    fontsize=16,
)
plt.xlabel("Electrification Level (%)", fontsize=14)
plt.ylabel("Percentage Reduction in Total Emissions (%)", fontsize=14)
plt.ylim(0, max(percent_reduction) * 1.1)
plt.grid(True, which="both", linestyle="--", linewidth=0.25)
plt.show()


percent_reduction


results_with_electrification[(0.5, 20)].optimized_emissions.sum()

# Adding the optimized_emissions column with the range of lambdas to the lifetime_pred_df as new columns for each lambda

lifetime_pred_optimized_df = lifetime_pred_df.copy()

for lambda_ in lambdas:
    lifetime_pred_optimized_df[f"optimized_emissions_{lambda_}"] = (
        results_with_electrification[(lambda_, 20)].optimized_emissions
    )

lifetime_pred_optimized_df.head(10)

lifetime_pred_optimized_df["optimized_emissions_0.7"].unique()

import folium
from folium.plugins import MarkerCluster

lifetime_pred_optimized_df["geometry"] = lifetime_pred_optimized_df["geometry"].apply(
    lambda x: x.centroid
)

# Create a map centered at a specific location
m = folium.Map(location=[60.472, 8.468], zoom_start=5)

# Create a MarkerCluster object
marker_cluster = MarkerCluster().add_to(m)

# Define lambda values
lambdas = [0.5, 0.6, 0.7, 0.8, 0.9]

# Add markers for each field
for idx, row in lifetime_pred_optimized_df.iterrows():
    if row["geometry"].geom_type == "Point":  # Ensure the geometry is a point
        lat, lon = row["geometry"].y, row["geometry"].x

        for lambda_ in lambdas:
            electrified_emission_key = f"optimized_emissions_{lambda_}"
            electrified = row[electrified_emission_key]

            if electrified > 0:  # Check if the field has emissions under this lambda
                folium.Marker(
                    location=[lat, lon],
                    popup=(
                        f"Field: {row['field']}<br>"
                        f"Lambda: {lambda_}<br>"
                        f"Optimized Emissions: {electrified:.2f}"
                    ),
                    icon=folium.Icon(color="green", icon="ok-sign"),
                ).add_to(marker_cluster)

# Display the map
m


lifetime_pred_optimized_df["geometry"] = lifetime_pred_optimized_df["geometry"].apply(
    lambda x: x.centroid
)


import geopandas as gpd

# If the dataframe is not a GeoDataFrame yet, convert it:
if not isinstance(lifetime_pred_optimized_df, gpd.GeoDataFrame):
    lifetime_pred_optimized_df = gpd.GeoDataFrame(
        lifetime_pred_optimized_df, geometry="geometry"
    )

# Make sure the CRS (Coordinate Reference System) is set
lifetime_pred_optimized_df.set_crs(
    epsg=4326, inplace=True
)  # assuming the coordinates are in WGS84


import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import geopandas as gpd


def plot_closed_fields_cartopy_adjusted(
    results, lambda_value, lifetime_pred_optimized_df
):
    # Filter the results for the given lambda value
    df = results[lambda_value]
    fields_closed = df[df["optimized_production"] == 0]["field"].unique()

    # Filter the lifetime_pred_optimized_df to get the geometries of the fields to be closed
    closed_fields_geometry = lifetime_pred_optimized_df[
        lifetime_pred_optimized_df["field"].isin(fields_closed)
    ]

    # Create a new plot with Cartopy
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={"projection": ccrs.Mercator()})

    # Add coastlines and borders for context
    ax.coastlines(resolution="10m", color="black", linewidth=1)
    ax.add_feature(cfeature.BORDERS, linestyle="-", linewidth=1)

    # Plot the base map using the geometries (in gray)
    lifetime_pred_optimized_df = lifetime_pred_optimized_df.to_crs(
        ccrs.Mercator().proj4_init
    )
    lifetime_pred_optimized_df.boundary.plot(
        ax=ax, edgecolor="lightgray", linewidth=0.5
    )

    # Plot the closed fields (in red)
    closed_fields_geometry = closed_fields_geometry.to_crs(ccrs.Mercator().proj4_init)
    closed_fields_geometry.plot(
        ax=ax, color="red", edgecolor="black", markersize=50, marker="o"
    )

    # Set title with professional styling
    plt.title(
        f"Oil and Gas Fields to be Closed for Lambda = {lambda_value}",
        fontsize=16,
        fontweight="bold",
        pad=20,
    )

    # Set extent to the area of interest
    ax.set_extent([0, 32, 55, 72], crs=ccrs.PlateCarree())

    # Show the plot
    plt.show()


plot_closed_fields_cartopy_adjusted(results, 0.9, lifetime_pred_optimized_df)


