# This script was automatically extracted from a Jupyter Notebook.

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import plotly.graph_objects as go

pd.set_option("display.max_columns", None)

# Importing the dataset from the csv file
url_path = (
    "https://raw.githubusercontent.com/percw/Norwegian_oil_gas_decarbonization/main/"
)
filename = (
    "/data/output/emissions_and_production/cleaned/fields_prod_emissions_1997_2023.csv"
)

# Creating a check if import is successful
try:
    fields_prod_emissions_1997_2023_df = pd.read_csv("".join([url_path, filename]))
    print("Data import successful")
except:
    print("Data import failed")

fields_prod_emissions_1997_2023_df.info()
fields_prod_emissions_1997_2023_df.head()

# Fields where emissions in NaN

field_without_emissions = fields_prod_emissions_1997_2023_df[
    fields_prod_emissions_1997_2023_df["field_in_emissions"] == False
].field.unique()

# Checking which of the fields without emissions have processing_field set

fields_without_emissions_and_processing_field = fields_prod_emissions_1997_2023_df[
    (fields_prod_emissions_1997_2023_df["field_in_emissions"] == False)
    & (fields_prod_emissions_1997_2023_df["processing_field"].isna())
].field.unique()
fields_without_emissions_and_processing_field

# Removing cod, edda and murchison from the the dataframe

fields_prod_emissions_1997_2023_df = fields_prod_emissions_1997_2023_df[
    ~fields_prod_emissions_1997_2023_df["field"].isin(["cod", "edda", "murchison"])
]

# Checking which fields are their own processing field and is not in the emission data

fields_own_processing_field = fields_prod_emissions_1997_2023_df[
    (
        fields_prod_emissions_1997_2023_df["field"]
        == fields_prod_emissions_1997_2023_df["processing_field"]
    )
    & (fields_prod_emissions_1997_2023_df["field_in_emissions"] == False)
]

fields_own_processing_field

# Removing frigg and albuskjell from the main df

fields_prod_emissions_1997_2023_df = fields_prod_emissions_1997_2023_df[
    ~fields_prod_emissions_1997_2023_df["field"].isin(["frigg", "albuskjell"])
]

fields_electricity_data = [
    {
        "field": "troll",
        "year_electrified": 1996,
        "power_capacity_MW": 200,
        "imported_power_2023_gwh/y": 1282,
    },
    {
        "field": "gullfaks",
        "year_electrified": 2023,
        "power_capacity_MW": None,
        "imported_power_2023_gwh/y": 108,
    },
    {
        "field": "snorre",
        "year_electrified": 2023,
        "power_capacity_MW": None,
        "imported_power_2023_gwh/y": 75,
    },
    {
        "field": "johan sverdrup",
        "year_electrified": 2019,
        "power_capacity_MW": 200,
        "imported_power_2023_gwh/y": 632,
    },
    {
        "field": "edvard grieg",
        "year_electrified": 2022,
        "power_capacity_MW": None,
        "imported_power_2023_gwh/y": 328,
    },
    {
        "field": "solveig",
        "year_electrified": 2022,
        "power_capacity_MW": None,
        "imported_power_2023_gwh/y": None,
    },
    {
        "field": "ivar aasen",
        "year_electrified": 2007,
        "power_capacity_MW": None,
        "imported_power_2023_gwh/y": 146,
    },
    {
        "field": "gina krog",
        "year_electrified": 2022,
        "power_capacity_MW": None,
        "imported_power_2023_gwh/y": 1.97,
    },
    {
        "field": "sleipner øst",
        "year_electrified": 2007,
        "power_capacity_MW": None,
        "imported_power_2023_gwh/y": 0,
    },
    {
        "field": "ormen lange",
        "year_electrified": 2007,
        "power_capacity_MW": None,
        "imported_power_2023_gwh/y": None,
    },
    {
        "field": "vega",
        "year_electrified": 2010,
        "power_capacity_MW": None,
        "imported_power_2023_gwh/y": None,
    },
    {
        "field": "duva",
        "year_electrified": 2021,
        "power_capacity_MW": None,
        "imported_power_2023_gwh/y": None,
    },
    {
        "field": "nova",
        "year_electrified": 2022,
        "power_capacity_MW": None,
        "imported_power_2023_gwh/y": None,
    },
    {
        "field": "gjøa",
        "year_electrified": 2010,
        "power_capacity_MW": 65,
        "imported_power_2023_gwh/y": 357,
    },
    {
        "field": "martin linge",
        "year_electrified": 2018,
        "power_capacity_MW": 55,
        "imported_power_2023_gwh/y": 224,
    },
    {
        "field": "goliat",
        "year_electrified": 2016,
        "power_capacity_MW": 70,
        "imported_power_2023_gwh/y": 414,
    },
    {
        "field": "valhall",
        "year_electrified": 2010,
        "power_capacity_MW": 78,
        "imported_power_2023_gwh/y": 388,
    },
    {
        "field": "hod",
        "year_electrified": 2010,
        "power_capacity_MW": 78,
        "imported_power_2023_gwh/y": None,
    },
]

# Valhall and Hod are the same field, but the electricity data is split between the two fields

# Adding electrification data to the fields_prod_emissions_1997_2023_df

# Add new columns with default values
fields_prod_emissions_1997_2023_df["electrified"] = 0
fields_prod_emissions_1997_2023_df["years_electrified"] = 0
fields_prod_emissions_1997_2023_df["electricity_mw"] = 0
fields_prod_emissions_1997_2023_df["imported_power_2023_gwh/y"] = 0

# Loop through fields_electricity_data and update the DataFrame
for field_data in fields_electricity_data:
    field_name = field_data["field"].lower()
    year_electrified = field_data["year_electrified"]
    power_capacity_MW = field_data["power_capacity_MW"]
    imported_power = field_data["imported_power_2023_gwh/y"]

    # Calculate the number of years electrified
    years_electrified = 2023 - year_electrified if year_electrified else 0

    # Update the DataFrame
    # Setting the electrified to 1 for the field from when it was electrified, not for all the years
    fields_prod_emissions_1997_2023_df.loc[
        (fields_prod_emissions_1997_2023_df["field"] == field_name)
        & (fields_prod_emissions_1997_2023_df["year"] >= year_electrified),
        "electrified",
    ] = 1

    fields_prod_emissions_1997_2023_df.loc[
        fields_prod_emissions_1997_2023_df["field"] == field_name, "years_electrified"
    ] = years_electrified

    fields_prod_emissions_1997_2023_df.loc[
        fields_prod_emissions_1997_2023_df["field"] == field_name, "electricity_mw"
    ] = power_capacity_MW if power_capacity_MW else 0

    fields_prod_emissions_1997_2023_df.loc[
        fields_prod_emissions_1997_2023_df["field"] == field_name,
        "imported_power_2023_gwh/y",
    ] = imported_power if imported_power else 0

    # Setting the year_electrified to a new column
    fields_prod_emissions_1997_2023_df.loc[
        fields_prod_emissions_1997_2023_df["field"] == field_name, "year_electrified"
    ] = year_electrified

# Display the updated DataFrame
fields_prod_emissions_1997_2023_df

display(fields_prod_emissions_1997_2023_df.electrified.unique())
display(fields_prod_emissions_1997_2023_df["imported_power_2023_gwh/y"].unique())
display(fields_prod_emissions_1997_2023_df.years_electrified.unique())

# Electrified fields to plot

electrified_fields_to_plot_df = fields_prod_emissions_1997_2023_df[
    fields_prod_emissions_1997_2023_df["electrified"] == 1
]

# Set up the plot
plt.figure(figsize=(14, 8))
sns.set(style="whitegrid")

fields_to_plot = [
    "troll",
    "gullfaks",
    "johan sverdrup",
    "snorre" "goliat",
    "valhall",
    "gjøa",
    "martin linge",
    "gina krog",
    "ormen lange",
]

# Plot each field's data
for field in fields_to_plot:
    field_data = electrified_fields_to_plot_df[
        electrified_fields_to_plot_df["field"] == field
    ]
    sns.lineplot(
        data=field_data,
        x="year",
        y="yearly_co2_emissions_1000_tonnes",
        label=field,
        marker="o",
    )


# Customize the plot
plt.title("Yearly CO2 Emissions for Selected Fields", fontsize=20)
plt.xlabel("Year", fontsize=14)
plt.ylabel("Yearly CO2 emissions (1000 tonnes)", fontsize=14)
plt.xticks(rotation=45)
plt.xticks(np.arange(1997, 2024, 1))
plt.legend(title="Field", bbox_to_anchor=(1.05, 1), loc="upper left", frameon=False)
plt.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()

# Show the plot
plt.show()

# Check the field_id of troll

fields_prod_emissions_1997_2023_df[
    fields_prod_emissions_1997_2023_df["field"] == "troll"
].field_id.unique()

# Fields to plot
fields_to_plot = [
    "troll",
    "gullfaks",
    "snorre",
    "johan sverdrup",
    "edvard grieg",
    "ivar aasen",
    "gina krog",
    "gjøa",
    "martin linge",
    "goliat",
    "valhall",
]

# Set up the plot grid
fig, axes = plt.subplots(nrows=4, ncols=3, figsize=(20, 20), constrained_layout=True)
axes = axes.flatten()

# Plot each field's data in its own subplot
for i, field in enumerate(fields_to_plot):
    ax = axes[i]
    field_data = electrified_fields_to_plot_df[
        electrified_fields_to_plot_df["field"] == field
    ]
    sns.lineplot(
        data=field_data,
        x="year",
        y="yearly_co2_emissions_1000_tonnes",
        ax=ax,
        marker="o",
    )

    # sns.lineplot(
    #    data=field_data,
    #    x="year",
    #    y="yearly_ch4_emissions_tons",
    #    ax=ax,
    #    marker=".",
    #    # color = navy blue
    #    color="#001f3f",
    # )

    # plot production data as a secondary y-axis
    ax2 = ax.twinx()
    sns.lineplot(
        data=field_data,
        x="year",
        y="net_oil_eq_prod_yearly_mill_sm3",
        ax=ax2,
        marker=".",
        color="red",
    )

    field_title = field.capitalize()
    ax.set_title(f"{field_title}", fontsize=16)
    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel("Emissions", fontsize=12)
    ax.grid(True)

    # Adding a legend
    ax.legend(["CO2 emissions (1000 tons)", "CH4 emissions (tons)"], loc="upper left")

    # Add a vertical line for the electrification year
    for field_data in fields_electricity_data:
        if field_data["field"] == field:
            year_electrified = field_data["year_electrified"]
            ax.axvline(x=year_electrified, color="black", linestyle=":", alpha=0.7)

# Hide any empty subplots
for j in range(i + 1, len(axes)):
    fig.delaxes(axes[j])

# Add a main title
plt.suptitle(
    "Yearly CO2 and CH4 Emissions for Selected Electrified Fields", fontsize=22
)
plt.show()

# Calculating average emission intensity for electrified fields

# Filter the DataFrame for electrified fields
electrified_fields_df = fields_prod_emissions_1997_2023_df[
    fields_prod_emissions_1997_2023_df["electrified"] == 1
]

# Calculate the average emission intensity for each field
electrified_fields_int = (
    electrified_fields_df["yearly_co2_emissions_1000_tonnes"].sum()
    / electrified_fields_df["net_oil_eq_prod_yearly_mill_sm3"].sum()
)

print(electrified_fields_int)

# Calculating average emission intensity for non-electrified fields

# Filter the DataFrame for non-electrified fields
non_electrified_fields_df = fields_prod_emissions_1997_2023_df[
    fields_prod_emissions_1997_2023_df["electrified"] == 0
]

# Calculate the average emission intensity for each field
non_electrified_fields_int = (
    non_electrified_fields_df["yearly_co2_emissions_1000_tonnes"].sum()
    / non_electrified_fields_df["net_oil_eq_prod_yearly_mill_sm3"].sum()
)

print(non_electrified_fields_int)

fields_prod_emissions_1997_2023_df[
    fields_prod_emissions_1997_2023_df["electrified"] == 1
]

# Calculating the average emission intensity for electrified fields only during the years they are electrified, and make sure that the year is greater than 2023-years_electrified

# Filter the DataFrame for electrified fields
electrified_intra_fields_df = fields_prod_emissions_1997_2023_df[
    (fields_prod_emissions_1997_2023_df["electrified"] == 1)
]

electrified_intra_fields_df.head(10)

# Calculate the average emission intensity for electrified_intra_fields_df

electrified_intra_fields_int = (
    electrified_intra_fields_df["yearly_co2_emissions_1000_tonnes"].sum()
    / electrified_intra_fields_df["net_oil_eq_prod_yearly_mill_sm3"].sum()
)

print(
    f"The average emission intensity for the elctrified fields during electrified years are: {electrified_intra_fields_int.round(2)}kgCO2/Sm3oe"
)

# printing the toe eq
print(
    f"The average emission intensity for the elctrified fields during electrified years are: {(electrified_intra_fields_int/0.84).round(2)}kgCO2/toe"
)

# in boe
print(
    f"The average emission intensity for the elctrified fields during electrified years are: {(electrified_intra_fields_int/6.2898).round(2)}kgCO2/boe"
)

# Calculating the average emission intensity for non-electrified

# Filter the DataFrame for non-electrified fields
non_electrified_intra_fields_df = fields_prod_emissions_1997_2023_df[
    (fields_prod_emissions_1997_2023_df["electrified"] == 0)
]

# Calculate the average emission intensity for non-electrified_intra_fields_df
non_electrified_intra_fields_int = (
    non_electrified_intra_fields_df["yearly_co2_emissions_1000_tonnes"].sum()
    / non_electrified_intra_fields_df["net_oil_eq_prod_yearly_mill_sm3"].sum()
)

print(
    f"The average emission intensity for the non-elctrified fields and electrified during non-electrified years are: {non_electrified_intra_fields_int.round(2)}kgCO2/Sm3oe"
)

# toe
print(
    f"The average emission intensity for the non-elctrified fields and electrified during non-electrified years are: {(non_electrified_intra_fields_int/0.84).round(2)}kgCO2/toe"
)

# boe
print(
    f"The average emission intensity for the non-elctrified fields and electrified during non-electrified years are: {(non_electrified_intra_fields_int/6.2898).round(2)}kgCO2/boe"
)

# Calc the % diff in emission intensity between electrified and non-electrified fields

diff_in_int = (
    (electrified_intra_fields_int - non_electrified_intra_fields_int)
    / non_electrified_intra_fields_int
    * 100
)

print(
    f"\nThe electrified fields have an average emission intensity that is {diff_in_int.round(2)}% lower than the non-electrified fields."
)

# The overall emission intensity for all fields in the dataset

# Calculate the average emission intensity for all fields
all_fields_int = (
    fields_prod_emissions_1997_2023_df["yearly_co2_emissions_1000_tonnes"].sum()
    / fields_prod_emissions_1997_2023_df["net_oil_eq_prod_yearly_mill_sm3"].sum()
)

all_fields_int

#
# Electrified fields
#
emissions_from_electrified_fields = electrified_intra_fields_df.groupby(["year"])[
    "yearly_co2_emissions_1000_tonnes"
].sum()

production_from_electrified_fields = electrified_intra_fields_df.groupby(["year"])[
    "net_oil_eq_prod_yearly_mill_sm3"
].sum()

#
# Non-electrified fields
#
emissions_from_non_electrified_fields = non_electrified_intra_fields_df.groupby(
    ["year"]
)["yearly_co2_emissions_1000_tonnes"].sum()

production_from_non_electrified_fields = non_electrified_intra_fields_df.groupby(
    ["year"]
)["net_oil_eq_prod_yearly_mill_sm3"].sum()

# Electrified intensity to get /toe
electrified_intensity = (
    emissions_from_electrified_fields / production_from_electrified_fields
) / 0.84


# Non-electrified intensity to get /toe
non_electrified_intensity = (
    emissions_from_non_electrified_fields / production_from_non_electrified_fields
) / 0.84

text_color = "black"
background_color = "#002244"
# Plot line colors
line_1_color = "#F68B1E"  # Orange
line_2_color = "#66B2FF"  # Light Blue
line_3_color = "#D49DB1"  # Light purple
line_4_color = "#FFD700"  # Gold
line_colors = [line_1_color, line_2_color, line_3_color, line_4_color]


def create_line_plot(x: [], y: [], title, y_label, x_label, legend=False, x_ticks=1):
    # Defining colors
    text_color = "black"
    background_color = "#002244"
    # Plot line colors
    line_1_color = "#F68B1E"  # Orange
    line_2_color = "#66B2FF"  # Light Blue
    line_3_color = "#D49DB1"  # Light purple
    line_4_color = "#FFD700"  # Gold

    line_colors = [line_1_color, line_2_color, line_3_color, line_4_color]

    # Defining max y to set y limit
    max_y = 0
    year_min = 1997
    year_max = 2023

    plt.figure(figsize=(6, 6))

    for i in range(len(x)):
        plt.plot(x[i], y[i], linewidth=2, color=line_colors[i])
        if max(y[i]) > max_y:
            max_y = max(y[i])
        if min(x[i]) < year_min:
            year_min = min(x[i])
        if max(x[i]) > year_max:
            year_max = max(x[i])

    # Titles and labels
    plt.title(
        title,
        fontsize=16,
        fontweight="bold",
        color=text_color,
    )

    # X axis show every year
    plt.xticks(np.arange(year_min, year_max, x_ticks))

    # Customizing ticks
    plt.xticks(fontsize=12, color=text_color, rotation=30)
    plt.yticks(fontsize=11, color=text_color)

    plt.xlabel(x_label, fontsize=10, color=text_color)
    plt.ylabel(y_label, fontsize=14, color=text_color)

    if legend:
        plt.legend(legend, loc="upper right")

    # Grid and layout
    plt.grid(True, which="both", linestyle=":", linewidth=0.25)
    plt.tight_layout()

    plt.ylim(0, int(max_y) * 1.2)

    # Dark blue background
    # plt.gca().patch.set_facecolor(background_color)
    # plt.gcf().patch.set_facecolor(background_color)

    return plt

# Plotting the Annual Carbon Emission Intensity for Norwegian Oil Eq. Production (kgCO2/toe):

title = "Emission Intensity for Norwegian Oil Eq. Production"
x_label = "Years"
y_label = "$kgCO_2/toe$"
legend = ["Electrified Fields", "Non-Electrified Fields"]

x = [electrified_intensity.index, non_electrified_intensity.index]
y = [electrified_intensity, non_electrified_intensity]

create_line_plot(x, y, title, y_label, x_label, legend, 2)
plt.show()

# Plotting the Annual Carbon Emission Intensity for Norwegian Oil Eq. Production (kgCO2/toe), but adding the LC GHG emissions:
# Only ~2% of emissions are from extraction, ~98% comes from burning the fossil fuel. Add that to the intensity
# sm3 to toe : 1 sm3 = 0.84 toe
# 5.80 mmbtu/barrel × 20.31 kg C/mmbtu × 44 kg CO2/12 kg C × 1 metric ton/1,000 kg = 0.43 metric tons CO2/barrel =  0.43 x 7.49 = 3.2 metric tons CO2/toe = 3200 kgCO2/toe

lifecycle_elect_intensities = (
    emissions_from_electrified_fields
    + (production_from_electrified_fields * 1000 * 3.2 * 0.84)
) / (production_from_electrified_fields * 0.84)

lifecycle_non_elect_intensities = (
    emissions_from_non_electrified_fields
    + (production_from_non_electrified_fields * 1000 * 3.2 * 0.84)
) / (production_from_non_electrified_fields * 0.84)

# Printing the Lifetime Emission Intensity for Electrified Fields

# toe
print(
    f"The average lifetime emission intensity for the electrified fields during electrified years are: {np.round(lifecycle_elect_intensities.mean(),2)}kgCO2/toe"
)
# boe
print(
    f"The average lifetime emission intensity for the electrified fields during electrified years are: {np.round(lifecycle_elect_intensities.mean()/6.2898, 2)}kgCO2/boe"
)

# Printing the Lifetime Emission Intensity for Non-Electrified Fields
# toe
print(
    "The average lifetime emission intensity for the non-electrified fields and electrified during non-electrified years are: ",
    round(np.round(lifecycle_non_elect_intensities.mean(), 2)),
    "kgCO2/toe",
)
# boe
print(
    "The average lifetime emission intensity for the non-electrified fields and electrified during non-electrified years are: ",
    round(np.round(lifecycle_non_elect_intensities.mean() / 6.2898, 2)),
    "kgCO2/boe",
)

# The percentage diff for /toe

percentage_diff = (
    (lifecycle_elect_intensities.mean() - lifecycle_non_elect_intensities.mean())
    / lifecycle_non_elect_intensities.mean()
) * 100

print(
    f"\nThe electrified fields have a {np.round(percentage_diff,2)}% lower lifetime emission intensity than the non-electrified fields"
)

# Plotting Lifetime Emission Intensity for Norwegian Oil Eq. Extraction $(kgCO_2/toe)$

title = "Lifetime Emission Intensity for Norwegian Oil Eq. Production"
x_label = "Years"
y_label = "$kgCO_2/toe$"
legend = ["Electrified Fields", "Non-Electrified Fields"]

x = [lifecycle_elect_intensities.index, lifecycle_non_elect_intensities.index]
y = [lifecycle_elect_intensities, lifecycle_non_elect_intensities]

create_line_plot(x, y, title, y_label, x_label, legend, 2)
plt.show()

# Computing the co2e per field
# GWP100
fields_prod_emissions_1997_2023_df["yearly_tco2e_gwp100"] = (
    fields_prod_emissions_1997_2023_df["yearly_co2_emissions_1000_tonnes"] * 1000
    + fields_prod_emissions_1997_2023_df["yearly_ch4_emissions_tons"] * 30
)

# GWP20
fields_prod_emissions_1997_2023_df["yearly_tco2e_gwp20"] = (
    fields_prod_emissions_1997_2023_df["yearly_co2_emissions_1000_tonnes"] * 1000
    + fields_prod_emissions_1997_2023_df["yearly_ch4_emissions_tons"] * 84
)

fields_prod_emissions_1997_2023_df.head(5)

non_electrified_intra_fields_df = fields_prod_emissions_1997_2023_df[
    (fields_prod_emissions_1997_2023_df["electrified"] == 0)
]

electrified_intra_fields_df = fields_prod_emissions_1997_2023_df[
    (fields_prod_emissions_1997_2023_df["electrified"] == 1)
]

#
# GWP100 intensity : electrified
#
emissions_from_electrified_fields_gwp100 = electrified_intra_fields_df.groupby(
    ["year"]
)["yearly_tco2e_gwp100"].sum()

production_from_electrified_fields = electrified_intra_fields_df.groupby(["year"])[
    "net_oil_eq_prod_yearly_mill_sm3"
].sum()

electrified_intensity_gwp_100 = (
    (emissions_from_electrified_fields_gwp100 / 1000)
    / (production_from_electrified_fields)
) / 0.84

#
# GWP 100 : non-electrified
#
emissions_from_non_electrified_fields_gwp100 = non_electrified_intra_fields_df.groupby(
    ["year"]
)["yearly_tco2e_gwp100"].sum()

production_from_non_electrified_fields = non_electrified_intra_fields_df.groupby(
    ["year"]
)["net_oil_eq_prod_yearly_mill_sm3"].sum()

non_electrified_intensity_gwp_100 = (
    (emissions_from_non_electrified_fields_gwp100 / 1000)
    / (production_from_non_electrified_fields)
) / 0.84

print("GWP100 - electrified")

# Printing the average CO2e intensity of electrified fields GWP100
print(
    f"The average CO2e intensity of electrified fields is: {np.round(electrified_intensity_gwp_100.mean(), 2)}kgCO2e/toe"
)

# boe
print(
    f"The average CO2e intensity of electrified fields is: {np.round(electrified_intensity_gwp_100.mean()/6.2898, 2)}kgCO2e/boe"
)

print("GWP100 - non-electrified")

# Printing the average CO2e intensity of non-electrified fields
print(
    f"The average CO2e intensity of non-electrified fields is: {np.round(non_electrified_intensity_gwp_100.mean(), 2)}kgCO2e/toe"
)

# boe
print(
    f"The average CO2e intensity of non-electrified fields is: {np.round(non_electrified_intensity_gwp_100.mean()/6.2898, 2)}kgCO2e/boe"
)

#
# GWP 20
#
# electrified
electrified_intensity_gwp_20 = (
    (electrified_intra_fields_df.groupby(["year"])["yearly_tco2e_gwp20"].sum() / 1000)
    / (
        electrified_intra_fields_df.groupby(["year"])[
            "net_oil_eq_prod_yearly_mill_sm3"
        ].sum()
    )
    / 0.84
)

# non-electrified
non_electrified_intensity_gwp_20 = (
    (
        non_electrified_intra_fields_df.groupby(["year"])["yearly_tco2e_gwp20"].sum()
        / 1000
    )
    / (
        non_electrified_intra_fields_df.groupby(["year"])[
            "net_oil_eq_prod_yearly_mill_sm3"
        ].sum()
    )
    / 0.84
)

# Printing the average CO2e intensity of electrified fields GWP20

print("GWP20 - electrified")
print(
    f"The average CO2e intensity of electrified fields is: {np.round(electrified_intensity_gwp_20.mean(), 2)}kgCO2e/toe"
)

# boe
print(
    f"The average CO2e intensity of electrified fields is: {np.round(electrified_intensity_gwp_20.mean()/6.2898, 2)}kgCO2e/boe"
)

print("GWP20 - non-electrified")

# Printing the average CO2e intensity of non-electrified fields
print(
    f"The average CO2e intensity of non-electrified fields is: {np.round(non_electrified_intensity_gwp_20.mean(), 2)}kgCO2e/toe"
)

# boe
print(
    f"The average CO2e intensity of non-electrified fields is: {np.round(non_electrified_intensity_gwp_20.mean()/6.2898, 2)}kgCO2e/boe"
)

# Plotting the annual CO2e intensity for elect and non-elect fields GWP100

title = "CO2e Intensity for Norwegian Oil Eq. Production"
x_label = "Years"
y_label = "$kgCO_2e/toe$"
legend = [
    "CO2e of Electrified Fields (GWP100)",
    "CO2e of Non-Electrified Fields (GWP100)",
    # "Elect. (GWP 20)",
    # "Non-Elect. (GWP 20)",
]

x = [
    electrified_intensity_gwp_100.index,
    non_electrified_intensity_gwp_100.index,
    # electrified_intensity_gwp_20.index,
    # non_electrified_intensity_gwp_20.index,
]
y = [
    electrified_intensity_gwp_100,
    non_electrified_intensity_gwp_100,
    # electrified_intensity_gwp_20,
    # non_electrified_intensity_gwp_20,
]

create_line_plot(x, y, title, y_label, x_label, legend, 2)
plt.show()

# Lifecyle intensity for electrified fields and non-electrified fields
# Calculating the lifecycle emission intensity for electrified and non-electrified fields
# Done as follows:
# lifecycle_emission  = (emissions_from_field + (production_from_field * 1000 * 3.200 * 0.84)) / (production_from_field * 0.84

lifecycle_elect_intensities_gwp100 = (
    emissions_from_electrified_fields_gwp100 / 1000
    + (production_from_electrified_fields * 1000 * 3.2 * 0.84)
) / (production_from_electrified_fields * 0.84)


lifecycle_non_elect_intensities_gwp100 = (
    emissions_from_non_electrified_fields_gwp100 / 1000
    + (production_from_non_electrified_fields * 1000 * 3.2 * 0.84)
) / (production_from_non_electrified_fields * 0.84)

# Printing the Lifetime Emission Intensity for Electrified Fields GWP100

# toe
print(
    f"The average lifetime emission intensity for the electrified fields during electrified years are: {np.round(lifecycle_elect_intensities_gwp100.mean(),2)}kgCO2e/toe"
)

# boe
print(
    f"The average lifetime emission intensity for the electrified fields during electrified years are: {np.round(lifecycle_elect_intensities_gwp100.mean()/6.2898, 2)}kgCO2e/boe"
)

# Printing the Lifetime Emission Intensity for Non-Electrified Fields GWP100

# toe
print(
    f"The average lifetime emission intensity for the non-electrified fields and electrified during non-electrified years are: {np.round(lifecycle_non_elect_intensities_gwp100.mean(),2)}kgCO2e/toe"
)

# boe
print(
    f"The average lifetime emission intensity for the non-electrified fields and electrified during non-electrified years are: {np.round(lifecycle_non_elect_intensities_gwp100.mean()/6.2898,2)}kgCO2e/boe"
)

# Titles and labels
title = "Lifecycle Emission Intensity for Norwegian Oil Eq. Production"
x_label = "Years"
y_label = "$kgCO_2e/toe$"
legend = [
    "CO2e of Electrified Fields (GWP100)",
    "CO2e of Non-Electrified Fields (GWP100)",
]

x = [
    lifecycle_elect_intensities_gwp100.index,
    lifecycle_non_elect_intensities_gwp100.index,
]
y = [lifecycle_elect_intensities_gwp100, lifecycle_non_elect_intensities_gwp100]

# Call plot function

plot = create_line_plot(
    x,
    y,
    title,
    y_label,
    x_label,
    legend,
    x_ticks=2,
)

plot.show()

# Setting a new column to hold the emission GWP100 intensity for each field for each year

fields_prod_emissions_1997_2023_df["kgco2e/toe_int_gwp100"] = (
    (fields_prod_emissions_1997_2023_df["yearly_tco2e_gwp100"])
    / 1000
    / fields_prod_emissions_1997_2023_df["net_oil_eq_prod_yearly_mill_sm3"]
) / 0.84

# Replacing inf with 0
fields_prod_emissions_1997_2023_df["kgco2e/toe_int_gwp100"] = (
    fields_prod_emissions_1997_2023_df["kgco2e/toe_int_gwp100"].replace(np.inf, 0)
)

fields_prod_emissions_1997_2023_df["kgco2e/toe_int_gwp100"] = (
    fields_prod_emissions_1997_2023_df["kgco2e/toe_int_gwp100"].replace(np.nan, 0)
)

# Counting number of 0s

fields_prod_emissions_1997_2023_df["kgco2e/toe_int_gwp100"].value_counts()

fields_prod_emissions_1997_2023_df["kgco2e/toe_int_gwp100"].describe()

# Create function to plot the distribution of a dataset


def plot_distribution(
    data,
    title,
    x_label,
    y_label,
    xmin,
    xmax,
    bins=50,
):
    plt.hist(
        data,
        bins=50,
        color=line_1_color,
    )

    plt.title(
        title,
        fontsize=16,
        color=text_color,
    )
    plt.xlabel(x_label, fontsize=16, color=text_color)
    plt.ylabel(y_label, fontsize=12, color=text_color)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.xlim(0, 500)

    # text color: white
    plt.xticks(fontsize=10, color=text_color)
    plt.yticks(fontsize=10, color=text_color)

    # background
    # plt.gca().patch.set_facecolor(background_color)
    # plt.gcf().patch.set_facecolor(background_color)

    return plt

# Plotting histofram for the kgco2e/toe_int_gwp100
# data = kgco2e/toe_int_gwp100 between 0 and 1000

data = fields_prod_emissions_1997_2023_df[
    (fields_prod_emissions_1997_2023_df["kgco2e/toe_int_gwp100"] > 0)
    & (fields_prod_emissions_1997_2023_df["kgco2e/toe_int_gwp100"] < 1000)
]

# Call hist function
plot = plot_distribution(
    data["kgco2e/toe_int_gwp100"],
    "Distribution of Emission Intensity for Norwegian Oil Eq. Production",
    "CO2e Intensity $(kgCO2_e/toe)$",
    "Number of Fields",
    0,
    1000,
)

plot.show()

fields_prod_emissions_1997_2023_df["net_oil_eq_prod_yearly_mill_sm3"].describe()

# Max production for each field

max_production = fields_prod_emissions_1997_2023_df.groupby(["field"])[
    "net_oil_eq_prod_yearly_mill_sm3"
].max()

fields_prod_emissions_1997_2023_df["share_peak_prod"] = (
    fields_prod_emissions_1997_2023_df["net_oil_eq_prod_yearly_mill_sm3"]
    / fields_prod_emissions_1997_2023_df["field"].map(max_production)
) * 100

# creating function to plot scatterplot


def plot_scatter(data, x, y, title, x_label, y_label, x_min=0, x_max=100):
    # Set up the plot
    plt.figure(figsize=(12, 8))

    # Plot the data
    plt.scatter(
        data=data,
        x=x,
        y=y,
        linewidth=0.2,
        s=40,
        color=line_1_color,
        edgecolor="black",
    )

    plt.title(title, fontsize=20, color=text_color)
    plt.xlabel(x_label, fontsize=14, color=text_color)
    plt.ylabel(y_label, fontsize=14, color=text_color)

    # white ticks
    plt.xticks(fontsize=12, color=text_color)
    plt.yticks(fontsize=12, color=text_color)

    # starting at 0
    plt.xlim(x_min, x_max)

    plt.gca().patch.set_facecolor(background_color)
    plt.gcf().patch.set_facecolor(background_color)

    return plt

# Creating scatter plot for the share of peak production and the CO2 intensity

plot = plot_scatter(
    data=fields_prod_emissions_1997_2023_df,
    x="share_peak_prod",
    y="yearly_tco2e_gwp100",
    title="Share of Peak Production vs CO2e Emissions",
    x_label="Share of Peak Production (%)",
    y_label="Yearly CO2 Emissions (tCO2e)",
)

plot.show()

# Creating scatter plot for the share of peak production and the CO2 intensity

data = fields_prod_emissions_1997_2023_df[
    (fields_prod_emissions_1997_2023_df["kgco2e/toe_int_gwp100"] > 0)
    & (fields_prod_emissions_1997_2023_df["kgco2e/toe_int_gwp100"] < 1000)
]

plot = plot_scatter(
    data=data,
    x="share_peak_prod",
    y="kgco2e/toe_int_gwp100",
    title="Share of Peak Production vs Emissions Intensity",
    x_label="Share of Peak Production (%)",
    y_label="CO2 Emissions Intensity (kgCO2e/toe)",
)

plot.show()

# Cum sum for the production for each field, subtracting that from the original reserve
fields_prod_emissions_1997_2023_df["oe_cum_sum_prod"] = (
    fields_prod_emissions_1997_2023_df.groupby(
        "field_id"
    )["net_oil_eq_prod_yearly_mill_sm3"].cumsum()
)

fields_prod_emissions_1997_2023_df["share_reserve_of_original_reserve"] = (
    100
    - (
        fields_prod_emissions_1997_2023_df["oe_cum_sum_prod"]
        / fields_prod_emissions_1997_2023_df["original_recoverable_oe"]
    )
    * 100
)

fields_prod_emissions_1997_2023_df["share_reserve_of_original_reserve"].describe()

# Creating scatter plot for the share of original reserve produced and the CO2 intensity

# Todo: add field_id as color hue
plot = plot_scatter(
    data=fields_prod_emissions_1997_2023_df,
    x="share_reserve_of_original_reserve",
    y="yearly_tco2e_gwp100",
    title=" Share of Original Reserve Produced vs CO2 Emissions",
    x_label="Share of Original Reserve Produced (%)",
    y_label="Yearly CO2 Emissions (tCO2e)",
)

plot.show()

# Creating scatter plot for the share of original reserve produced and the CO2 intensity

data = fields_prod_emissions_1997_2023_df[
    (fields_prod_emissions_1997_2023_df["kgco2e/toe_int_gwp100"] > 0)
    & (fields_prod_emissions_1997_2023_df["kgco2e/toe_int_gwp100"] < 1000)
]

plot = plot_scatter(
    data=data,
    x="share_reserve_of_original_reserve",
    y="kgco2e/toe_int_gwp100",
    title="Share of Original Reserve Produced vs Emission Intensity",
    x_label="Share of Original Reserve Produced (%)",
    y_label="Yearly Emissions Intensity (kgCO2e/toe)",
)

plot.show()

# describing the reserve columns

reserve_cols = [
    "current_remaining_recoverable_oil",
    "current_remaining_recoverable_gas",
    "current_remaining_recoverable_ngl",
    "current_remaining_recoverable_condensate",
    "current_remaining_recoverable_oe",
    "original_recoverable_oil",
    "original_recoverable_gas",
    "original_recoverable_ngl",
    "original_recoverable_condensate",
    "original_recoverable_oe",
]

fields_prod_emissions_1997_2023_df[reserve_cols].describe()

# Total yearly oe production in million sm3

total_oe_production = fields_prod_emissions_1997_2023_df.groupby("year")[
    "net_oil_eq_prod_yearly_mill_sm3"
].sum()

# Calculating the total original original_recoverable_oe by counting each field once
total_original_recoverable_oe = (
    fields_prod_emissions_1997_2023_df[["field", "original_recoverable_oe"]]
    .drop_duplicates()["original_recoverable_oe"]
    .sum()
)


display(total_oe_production)
display(total_original_recoverable_oe)

# Cumaulative sum the production from total_oe_production and for each year subtract it from the total_original_recoverable_oe
# to get the remaining recoverable oe for each year

remaining_recoverable_oe = total_original_recoverable_oe - total_oe_production.cumsum()
display(remaining_recoverable_oe)

# Sum of current remaining recoverable oe

# Calculating the total original original_recoverable_oe by counting each field once
total_remaining_recoverable_oe = (
    fields_prod_emissions_1997_2023_df[["field", "current_remaining_recoverable_oe"]]
    .drop_duplicates()["current_remaining_recoverable_oe"]
    .sum()
)

# sm3 to toe : 1 sm3 = 0.84 toe
print(
    f"Remaining Recoverable Oil Eq.: {np.round(total_remaining_recoverable_oe*0.84)} million toe"
)


# 5.80 mmbtu/barrel × 20.31 kg C/mmbtu × 44 kg CO2/12 kg C × 1 metric ton/1,000 kg = 0.43 metric tons CO2/barrel =  0.43 x 7.49 = 0.36 metric tons CO2/toe
# Using this conversion rate, calculate th amount of CO2 the remaining recoverable oe can produce

remaining_recoverable_oe_co2 = total_remaining_recoverable_oe * 1000000 * 0.36 * 0.84

print(
    f"CO2 Potential by burning remaining recoverable reserves: {(remaining_recoverable_oe_co2/1000000000).round(2)} GtCO2"
)

# Remaining recoverable gas
# Calculating the total original original_recoverable_gas by counting each field once
total_original_recoverable_gas = (
    fields_prod_emissions_1997_2023_df[["field", "original_recoverable_gas"]]
    .drop_duplicates()["original_recoverable_gas"]
    .sum()
)

# Calculating the total original original_recoverable_gas by counting each field once
total_remaining_recoverable_gas = (
    fields_prod_emissions_1997_2023_df[["field", "current_remaining_recoverable_gas"]]
    .drop_duplicates()["current_remaining_recoverable_gas"]
    .sum()
)

print("Remaining Recoverable Gas")
print(
    f"Original Recoverable Gas: {np.round(total_original_recoverable_gas, 2)} billion sm3"
)
print(
    f"Remaining Recoverable Gas: {np.round(total_remaining_recoverable_gas, 2)} billion sm3"
)

# Remaining recoverable NGL
# Calculating the total original original_recoverable_ngl by counting each field once
total_original_recoverable_ngl = (
    fields_prod_emissions_1997_2023_df[["field", "original_recoverable_ngl"]]
    .drop_duplicates()["original_recoverable_ngl"]
    .sum()
)

# Calculating the total original original_recoverable_ngl by counting each field once
total_remaining_recoverable_ngl = (
    fields_prod_emissions_1997_2023_df[["field", "current_remaining_recoverable_ngl"]]
    .drop_duplicates()["current_remaining_recoverable_ngl"]
    .sum()
)

print("Remaining Recoverable NGL")
print(
    f"Original Recoverable NGL: {np.round(total_original_recoverable_ngl, 2)} million sm3"
)
print(
    f"Remaining Recoverable NGL: {np.round(total_remaining_recoverable_ngl, 2)} million sm3"
)

# Remaining recoverable oil
# Calculating the total original original_recoverable_oil by counting each field once
total_original_recoverable_oil = (
    fields_prod_emissions_1997_2023_df[["field", "original_recoverable_oil"]]
    .drop_duplicates()["original_recoverable_oil"]
    .sum()
)

# Calculating the total original original_recoverable_oil by counting each field once
total_remaining_recoverable_oil = (
    fields_prod_emissions_1997_2023_df[["field", "current_remaining_recoverable_oil"]]
    .drop_duplicates()["current_remaining_recoverable_oil"]
    .sum()
)

print("Remaining Recoverable Oil")
print(
    f"Original Recoverable Oil: {np.round(total_original_recoverable_oil, 2)} million sm3"
)
print(
    f"Remaining Recoverable Oil: {np.round(total_remaining_recoverable_oil, 2)} million sm3"
)

# Plotting the remaining_recoverable_oe over time using plot func

title = "Remaining Oil, Gas and Condensate on the Norwegian Continental Shelf"
x_label = "Years"
y_label = "Million $sm^3$ oil eq."
legend = False
x = [remaining_recoverable_oe.index]
y = [remaining_recoverable_oe]

plot = create_line_plot(x, y, title, y_label, x_label, legend, 2)
plot.show()

# Pie chart showing the current remaining recoverable oe as of total original recoverable oe

# OE
remaining_recoverable_oe_percentage = (
    total_remaining_recoverable_oe / total_original_recoverable_oe
)

# Gas
remaining_recoverable_gas_percentage = (
    total_remaining_recoverable_gas / total_original_recoverable_gas
)

# Oil
remaining_recoverable_oil_percentage = (
    total_remaining_recoverable_oil / total_original_recoverable_oil
)

# NGL
remaining_recoverable_ngl_percentage = (
    total_remaining_recoverable_ngl / total_original_recoverable_ngl
)

pie_main = [
    remaining_recoverable_oe_percentage * 100,
    100 - 100 * remaining_recoverable_oe_percentage,
]

pie_oil = [
    remaining_recoverable_oil_percentage * 100,
    100 - 100 * remaining_recoverable_oil_percentage,
]
pie_gas = [
    remaining_recoverable_gas_percentage * 100,
    100 - 100 * remaining_recoverable_gas_percentage,
]
pie_ngl = [
    remaining_recoverable_ngl_percentage * 100,
    100 - 100 * remaining_recoverable_ngl_percentage,
]

# Data for the main pie chart
labels_main = ["Remaining", "Depleted"]
colors_main = ["#F68B1E", "#EBEBEB"]  # Professional color palette
explode_main = (0.1, 0)  # Explode the remaining slice

labels_smaller = ["Remaining", "Depleted"]
colors_smaller = ["#F68B1E", "#EBEBEB"]  # Professional color palette
explode_smaller = (0.1, 0)

# Plotting the main pie chart and the smaller ones
fig, axs = plt.subplots(
    1, 4, figsize=(20, 7), gridspec_kw={"width_ratios": [3, 1, 1, 1]}
)

fig.suptitle(
    "Norwegian Fossil Fuel Reserves (Current Open Fields)", fontsize=20, color="white"
)

# Main pie chart
axs[0].pie(
    pie_main,
    explode=explode_main,
    labels=labels_main,
    colors=colors_main,
    autopct="%1.0f%%",
    startangle=120,
    textprops={"color": "#EBEBEB", "fontsize": 14},
    wedgeprops=dict(edgecolor="#003366"),
)
axs[0].add_artist(plt.Circle((0, 0), 0.5, fc="#003366"))
axs[0].set_title("Overall in Oil Equivalents", fontsize=16, color="white", pad=20)
axs[0].axis("equal")

# Smaller pie chart 1
axs[1].pie(
    pie_oil,
    explode=explode_smaller,
    labels=labels_smaller,
    colors=colors_smaller,
    autopct="%1.0f%%",
    startangle=120,
    textprops={"color": "#EBEBEB", "fontsize": 14},
    wedgeprops=dict(edgecolor="#003366"),
)
axs[1].add_artist(plt.Circle((0, 0), 0.3, fc="#003366"))
axs[1].axis("equal")
axs[1].set_title("Oil ", fontsize=16, color="white")

# Smaller pie chart 2
axs[2].pie(
    pie_gas,
    explode=explode_smaller,
    labels=labels_smaller,
    colors=colors_smaller,
    autopct="%1.0f%%",
    startangle=120,
    textprops={"color": "#EBEBEB", "fontsize": 14},
    wedgeprops=dict(edgecolor="#003366"),
)
axs[2].add_artist(plt.Circle((0, 0), 0.3, fc="#003366"))
axs[2].axis("equal")
axs[2].set_title("Gas", fontsize=16, color="white")

# Smaller pie chart 3
axs[3].pie(
    pie_ngl,
    explode=explode_smaller,
    labels=labels_smaller,
    colors=colors_smaller,
    textprops={"color": "#EBEBEB", "fontsize": 14},
    autopct="%1.0f%%",
    startangle=120,
    wedgeprops=dict(edgecolor="#003366"),
)
axs[3].add_artist(plt.Circle((0, 0), 0.30, fc="#003366"))
axs[3].axis("equal")
axs[3].set_title("NGL", fontsize=16, color="white")

# set background for whole visual to dark blue
fig.patch.set_facecolor(background_color)

# Adjust layout
plt.tight_layout()

plt.show()

# mckinsey orange = #F68B1E

# Checking the dataframe for fields that does not have emissions and does not have a processing field
# fields_without_emissions_and_processing_field = (fields_prod_emissions_1997_2023_df[fields_prod_emissions_1997_2023_df['processing_field'].isna()])
display(
    fields_prod_emissions_1997_2023_df[
        fields_prod_emissions_1997_2023_df["processing_field"].isna()
    ].head()
)

# Setting the fields that does not have a processing field to be their own processing field

fields_prod_emissions_1997_2023_df.loc[
    fields_prod_emissions_1997_2023_df["processing_field"].isna(), "processing_field"
] = fields_prod_emissions_1997_2023_df.loc[
    fields_prod_emissions_1997_2023_df["processing_field"].isna(), "field"
]
display(
    fields_prod_emissions_1997_2023_df[
        fields_prod_emissions_1997_2023_df["processing_field"].isna()
    ].head()
)

# Host processing field production in oe, yearly_ch4_emissions_tons	yearly_nox_emissions_tons	yearly_oil_spill_emissions_tons	yearly_water_emissions_m3, grouped by year and processing field on the only the production columns

processing_production = fields_prod_emissions_1997_2023_df.groupby(
    ["year", "processing_field"]
)["net_oil_eq_prod_yearly_mill_sm3", "yearly_tco2e_gwp100"].sum()

# Rename columns to oil_fac_prod, gas_fac_prod, ngl_fac_prod, condensate_fac_prod, oil_eq_fac_prod, produced_water
processing_production = processing_production.rename(
    columns={
        "net_oil_eq_prod_yearly_mill_sm3": "oe_fac_prod_mill_sm3",
        "yearly_tco2e_gwp100": "yearly_fac_tco2e_gwp100",
    }
)

display(processing_production.head())
display(processing_production.describe())

# displaying year 1997

processing_production[processing_production.index.get_level_values("year") == 1997]

# Merging in the grouped emissions and set it on all the fields, but merge on processing field in main dataframe

fields_prod_emissions_1997_2023_df = fields_prod_emissions_1997_2023_df.merge(
    processing_production,
    how="left",
    left_on=["year", "processing_field"],
    right_on=["year", "processing_field"],
)

fields_prod_emissions_1997_2023_df.head()

# Calculating the share production for each field - production divided by processing field production

# oil eq share production
fields_prod_emissions_1997_2023_df["oe_share_prod"] = (
    fields_prod_emissions_1997_2023_df["net_oil_eq_prod_yearly_mill_sm3"]
    / fields_prod_emissions_1997_2023_df["oe_fac_prod_mill_sm3"]
)

# co2 share emissions = field emissions + processing field emissions * share production
fields_prod_emissions_1997_2023_df["yearly_tco2e_prod_share_emissions"] = (
    fields_prod_emissions_1997_2023_df["yearly_fac_tco2e_gwp100"]
    * fields_prod_emissions_1997_2023_df["oe_share_prod"]
)

fields_prod_emissions_1997_2023_df.head()

# Plotting the CO2 eq. emissions for each field

fields_prod_emissions_1997_2023_df["yearly_tco2e_prod_share_emissions"].describe()

# Printing the top 10 rows with the highest CO2 eq. emissions
fields_prod_emissions_1997_2023_df[
    [
        "field",
        "year",
        "yearly_tco2e_gwp100",
        "yearly_co2_emissions_1000_tonnes",
        "yearly_tco2e_prod_share_emissions",
    ]
].sort_values(by="yearly_tco2e_prod_share_emissions", ascending=False).head(10)

# CO2e emission - GWP 100
fields_prod_emissions_1997_2023_df["share_intensity_tco2e/toe_gwp100"] = (
    (fields_prod_emissions_1997_2023_df["yearly_tco2e_prod_share_emissions"] / 1000)
    / (fields_prod_emissions_1997_2023_df["net_oil_eq_prod_yearly_mill_sm3"])
) / 0.84

fields_prod_emissions_1997_2023_df["share_intensity_tco2e/toe_gwp100"].describe()

# Calculating the mean of tco2e/toe_gwp100 between 1997 and 2022 across fields

mean_share_co2_per_oe = (
    (
        (fields_prod_emissions_1997_2023_df["yearly_tco2e_prod_share_emissions"].sum())
        / 1000
    )
    / fields_prod_emissions_1997_2023_df["net_oil_eq_prod_yearly_mill_sm3"].sum()
) / 0.84

print(f"Mean tcCO2e/toe between 1997 and 2022: {np.round(mean_share_co2_per_oe)}")
# Calculating the mean of tco2e/toe_gwp100 between 1997 and 2022 across fields

mean_co2_per_oe = (
    ((fields_prod_emissions_1997_2023_df["yearly_tco2e_gwp100"].sum()) / 1000)
    / (fields_prod_emissions_1997_2023_df["net_oil_eq_prod_yearly_mill_sm3"].sum())
) / 0.84

print(f"Mean tCO2/toe between 1997 and 2022: {np.round(mean_co2_per_oe.mean(),2)}")

# Checking that the sums of emissions are correct
# the distributed emissions of co2e should be equal to the total emissions of co2e

distributed_co2e_total = fields_prod_emissions_1997_2023_df[
    "yearly_tco2e_prod_share_emissions"
].sum()

total_co2e = fields_prod_emissions_1997_2023_df["yearly_tco2e_gwp100"].sum()

print(
    f"Total distributed (share) CO2e emissions: {distributed_co2e_total.round(1)} - Total CO2 emissions: {total_co2e.round(1)}"
)

# Print the diff
print(f"Difference: {np.round(total_co2e - distributed_co2e_total, 1)}")

# % diff
print(
    f"Percentage difference: {np.round((total_co2e - distributed_co2e_total) / total_co2e * 100, 2)}%"
)

# Top 5 share_intensity_tco2e/toe_gwp100

fields_prod_emissions_1997_2023_df[
    [
        "field",
        "year",
        "yearly_tco2e_gwp100",
        "yearly_tco2e_prod_share_emissions",
        "yearly_co2_emissions_1000_tonnes",
        "share_intensity_tco2e/toe_gwp100",
        "oe_share_prod",
        "oe_fac_prod_mill_sm3",
        "net_oil_eq_prod_yearly_mill_sm3",
    ]
].sort_values(by="share_intensity_tco2e/toe_gwp100", ascending=False).head(5)

# Set a a limit for net_oil_eq_prod_yearly_mill_sm3 > 0.2

fields_prod_emissions_1997_2023_dist_df = fields_prod_emissions_1997_2023_df[
    (fields_prod_emissions_1997_2023_df["net_oil_eq_prod_yearly_mill_sm3"] > 0.2)
    & (fields_prod_emissions_1997_2023_df["share_intensity_tco2e/toe_gwp100"] < 2000)
]

# Top 10 share_intensity_tco2e/toe_gwp100

fields_prod_emissions_1997_2023_dist_df[
    [
        "field",
        "year",
        "oe_share_prod",
        "oe_fac_prod_mill_sm3",
        "yearly_tco2e_gwp100",
        "yearly_co2_emissions_1000_tonnes",
        "share_intensity_tco2e/toe_gwp100",
        "net_oil_eq_prod_yearly_mill_sm3",
    ]
].sort_values(by="share_intensity_tco2e/toe_gwp100", ascending=False).head(10)

# Plotting the distribution of the share_intensity_tco2e/toe_gwp100

data = fields_prod_emissions_1997_2023_dist_df[
    (fields_prod_emissions_1997_2023_dist_df["share_intensity_tco2e/toe_gwp100"] > 0)
    & (
        fields_prod_emissions_1997_2023_dist_df["share_intensity_tco2e/toe_gwp100"]
        < 2000
    )
]

# Call hist function

plot = plot_distribution(
    data["share_intensity_tco2e/toe_gwp100"],
    "Distributed Emission Intensity for Norwegian Oil Eq. Production",
    "CO2e Intensity $(kgCO2_e/toe)$",
    "Number of Fields",
    0,
    2000,
)

plot.show()

# Scatter plot of the share of production and the share CO2 intensity

plot = plot_scatter(
    fields_prod_emissions_1997_2023_dist_df,
    x="share_peak_prod",
    y="share_intensity_tco2e/toe_gwp100",
    title="Share of Peak Production vs Distributed Emission Intensity",
    x_label="Share of Peak Production (%)",
    y_label="CO2 Intensity (kgCO2e/toe)",
)

# Plotting the scatter of Share of Original Reserve Produced and the Share CO2 Intensity

plot = plot_scatter(
    data=data,
    x="share_reserve_of_original_reserve",
    y="share_intensity_tco2e/toe_gwp100",
    title="Share of Original Reserve Produced vs Distributed Emission Intensity",
    x_label="Share of Original Reserve Produced (%)",
    y_label="CO2 Intensity (kgCO2e/toe)",
)

# Ensure all production features are numeric, forcing non-numeric values to NaN
emission_features = [
    "yearly_co2_emissions_1000_tonnes",
    "yearly_tco2e_prod_share_emissions",
    "yearly_tco2e_gwp100",
]

production_features = [
    "net_oil_prod_yearly_mill_sm3",
    "net_gas_prod_yearly_bill_sm3",
    "net_ngl_prod_yearly_mill_sm3",
    "net_condensate_prod_yearly_mill_sm3",
    "net_oil_eq_prod_yearly_mill_sm3",
    "produced_water_yearly_mill_sm3",
]

production_features_volatility = [
    "net_oil_prod_monthly_sm3_volatility",
    "net_gas_prod_monthly_sm3_volatility",
    "net_ngl_prod_monthly_sm3_volatility",
    "net_condensate_prod_monthly_sm3_volatility",
    "net_oil_eq_prod_monthly_sm3_volatility",
    "produced_water_in_field_volatility",
]


# General statistics for production features
production_stats = fields_prod_emissions_1997_2023_df[production_features].describe()
production_stats_volatility = fields_prod_emissions_1997_2023_df[
    production_features_volatility
].describe()
display(production_stats)
display(production_stats_volatility)

# Function to create a grid of histograms
def plot_histograms(df, features, title, bins=30):
    plt.figure(figsize=(20, 15))
    for i, feature in enumerate(features, 1):
        # if under 3 features - 1 row, 3 columns
        # if under 6 features - 2 rows, 3 columns
        # if under 9 features - 3 rows, 3 columns
        # if under 12 features - 3 rows, 4 columns
        cols = 3
        rows = 3
        if len(features) < 3:
            rows = 1
            cols = 3
        elif len(features) < 6:
            rows = 2
            cols = 3
        elif len(features) < 9:
            rows = 3
            cols = 3
        else:
            rows = (len(features) + 3) // 4
            cols = 4
        plt.subplot(rows, cols, i)
        df[feature].hist(bins=bins, edgecolor="white", color=line_1_color)
        # Convert title to title case and remove underscores
        feature = feature.replace("_", " ").title()
        plt.title(feature)
        plt.xlabel("")
        plt.ylabel("")

    plt.suptitle(title, fontsize=20)
    plt.tight_layout(rect=[0, 0, 1, 0.96])

    plt.show()


# Plot histograms for production features
plot_histograms(
    fields_prod_emissions_1997_2023_df,
    production_features,
    "Production Data Histograms",
)

# Printing number of observations for each field
fields_prod_emissions_1997_2023_df["field_id"].value_counts().sum()

# Plot histograms for production features volatility

# Plot histograms for production features
plot_histograms(
    fields_prod_emissions_1997_2023_df,
    production_features_volatility,
    "Production Data Histograms",
)

# Drop rows with NaN values in production features
cleaned_production_df = fields_prod_emissions_1997_2023_df[
    production_features + emission_features
].dropna()


# Function to create scatter plot matrix
def plot_scatter_matrix(df, features, title):
    sns.pairplot(df[features], diag_kind="kde", plot_kws={"alpha": 0.5})
    plt.suptitle(title, fontsize=20)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()


# Plot scatter matrix for production features
plot_scatter_matrix(
    cleaned_production_df, production_features, "Production Data Scatter Matrix"
)

# Compute the correlation matrix for production features
correlation_matrix = cleaned_production_df.corr()


# Function to plot correlation matrix
def plot_correlation_matrix(corr_matrix, title):
    plt.figure(figsize=(12, 10))
    sns.heatmap(
        corr_matrix,
        annot=True,
        cmap="coolwarm",
        vmin=-1,
        vmax=1,
        square=True,
        linewidths=0.5,
        annot_kws={"size": 7},
        fmt=".2f",
    )
    plt.title(title, fontsize=20)
    plt.show()


# Plot the correlation matrix for production features
plot_correlation_matrix(correlation_matrix, "Correlation Matrix for Production Data")

# Plotting the scatter plot and correlation matrix for production features volatility

# Drop rows with NaN values in production features
cleaned_production_volatility_df = fields_prod_emissions_1997_2023_df[
    production_features_volatility + emission_features
].dropna()

# Plot scatter matrix for production features volatility
plot_scatter_matrix(
    cleaned_production_volatility_df,
    production_features_volatility,
    "Production Data Volatility Scatter Matrix",
)

# Compute the correlation matrix for production features volatility
correlation_matrix_volatility = cleaned_production_volatility_df.corr()

# Plot the correlation matrix for production features volatility
plot_correlation_matrix(
    correlation_matrix_volatility,
    "Correlation Matrix for Production Data Volatility",
)

# Define Emission Data features

emission_features = [
    "yearly_tco2e_gwp100",
    "yearly_co2_emissions_1000_tonnes",
    "yearly_tco2e_prod_share_emissions",
    "share_intensity_tco2e/toe_gwp100",
]


# General statistics for emission features
emission_stats = fields_prod_emissions_1997_2023_df[emission_features].describe()
emission_stats

# Drop rows with NaN values in emission features
cleaned_emission_df = fields_prod_emissions_1997_2023_df[emission_features].dropna()

# Compute the correlation matrix for emission features
emission_corr_matrix = cleaned_emission_df.corr()

# Plot the correlation matrix for emission features
plot_correlation_matrix(emission_corr_matrix, "Correlation Matrix for Emission Data")

def plot_fields_emissions_over_time(df, features, title="Fields Emissions Over Time"):
    """
    Plots line diagrams for multiple features over time.

    Parameters:
    - df: DataFrame containing the data
    - features: List of features to plot
    - title: Title of the plot
    """
    # Set up the color palette
    num_colors = len(df["field"].unique())
    palette = sns.color_palette("tab20", num_colors)

    num_features = len(features)
    cols = 1 if num_features == 1 else 2
    rows = (num_features + 1) // 2

    plt.figure(figsize=(cols * 10, rows * 6))

    for i, feature in enumerate(features, 1):
        plt.subplot(rows, cols, i)
        sns.lineplot(
            data=df,
            x="year",
            y=feature,
            hue="field",
            palette=palette,
            marker="o",
            alpha=0.7,
            legend=False,
        )
        # Convert title to title case and remove underscores
        feature = feature.replace("_", " ").title()
        plt.title(f"{feature} from 1997 to 2023", fontsize=15)
        # Show every year on the x-axis
        plt.xticks(df["year"].unique())
        plt.xticks(rotation=45, ha="right")
        plt.xlabel("Year", fontsize=12)
        # remove underscore from the feature y label
        plt.ylabel(feature.replace("_", " ").title(), fontsize=12)
        # plt.ylabel("Emissions (1000 tonnes)", fontsize=12)
        plt.grid(True)

    plt.suptitle(title, fontsize=20)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()


plot_fields_emissions_over_time(
    fields_prod_emissions_1997_2023_df,
    emission_features,
    title="Yearly Emissions of Fields Over Time",
)

# Define Facility and Field Characteristics features
facility_features = [
    "facilities_lifetime_mean",
    "facilities_water_depth_mean",
    "subsea_facilites_shut_down",
    "surface_facilites_shut_down",
    "subsea_facilites_in_service",
    "surface_facilites_in_service",
    "well_final_vertical_depth_mean",
    "well_water_depth_mean",
    "electrified",
    "years_electrified",
    "electricity_mw",
]

cols_with_well_status = [
    col for col in fields_prod_emissions_1997_2023_df if "well_status_" in col
]

cols_with_well_purpose = [
    col for col in fields_prod_emissions_1997_2023_df if "well_purpose_" in col
]

cols_with_facility_kind = [
    col for col in fields_prod_emissions_1997_2023_df if "kind" in col
]

# General statistics for facility features
facility_stats = fields_prod_emissions_1997_2023_df[facility_features].describe()
facility_stats

# Printing cols_with_well_status, cols_with_well_purpose, cols_with_facility_kind, facility_features and the list constituents

print("Well Status Columns:")
print(cols_with_well_status)
print("\nWell Purpose Columns:")
print(cols_with_well_purpose)
print("\nFacility Kind Columns:")
print(cols_with_facility_kind)

# Drop rows with NaN values in facility features
cleaned_facility_with_emissions_df = fields_prod_emissions_1997_2023_df[
    facility_features + emission_features
].dropna()

# Plot scatter matrix for facility features
plot_scatter_matrix(
    cleaned_facility_with_emissions_df,
    facility_features,
    "Facility and Field Characteristics Scatter Matrix",
)

# Plot correlation matrix for facility kind features

corr_df = fields_prod_emissions_1997_2023_df[
    cols_with_facility_kind + emission_features
].dropna()

plot_correlation_matrix(corr_df.corr(), "Correlation Matrix for Facility Kind Features")

# Plotting well status


corr_df = fields_prod_emissions_1997_2023_df[
    cols_with_well_status + emission_features
].dropna()

plot_correlation_matrix(corr_df.corr(), "Correlation Matrix for Well Status")

# Plotting well purpose

corr_df = fields_prod_emissions_1997_2023_df[
    cols_with_well_purpose + emission_features
].dropna()

plot_correlation_matrix(corr_df.corr(), "Correlation Matrix for Facility Purposes")

# Plotting corr matrix for facility_features

corr_df = fields_prod_emissions_1997_2023_df[
    facility_features + emission_features
].dropna()

plot_correlation_matrix(corr_df.corr(), "Correlation Matrix, Facility Features")

# Define Investments and Recoverables features
investment_features = [
    "investments_mill_nok",
    "future_investments_mill_nok",
    "current_remaining_recoverable_oil",
    "current_remaining_recoverable_gas",
    "current_remaining_recoverable_ngl",
    "current_remaining_recoverable_condensate",
    "current_remaining_recoverable_oe",
    "original_recoverable_oil",
    "original_recoverable_gas",
    "original_recoverable_ngl",
    "original_recoverable_condensate",
    "original_recoverable_oe",
]

# General statistics for investment features
investment_stats = fields_prod_emissions_1997_2023_df[investment_features].describe()
investment_stats

# Plot histograms for investment features
plot_histograms(
    fields_prod_emissions_1997_2023_df,
    investment_features,
    "Investments and Recoverables Histograms",
)

# Drop rows with NaN values in investment features
cleaned_investment_df = fields_prod_emissions_1997_2023_df[
    investment_features + emission_features
].dropna()


# Plot scatter matrix for investment features
plot_scatter_matrix(
    cleaned_investment_df,
    investment_features,
    "Investments and Recoverables Scatter Matrix",
)

# Compute the correlation matrix for investment features
investment_corr_matrix = cleaned_investment_df.corr()

# Plot the correlation matrix for investment features
plot_correlation_matrix(
    investment_corr_matrix,
    "Correlation Matrix for Investments and Recoverables",
)

# Calculate gas/oil ratio of reserve for each observation

fields_prod_emissions_1997_2023_dist_df["gas_reserve_ratio"] = (
    fields_prod_emissions_1997_2023_dist_df["original_recoverable_gas"] / 1000
) / fields_prod_emissions_1997_2023_dist_df["original_recoverable_oe"]

# Calculate oil reserve ratio


fields_prod_emissions_1997_2023_dist_df["oil_reserve_ratio"] = (
    fields_prod_emissions_1997_2023_dist_df["original_recoverable_oil"]
    / fields_prod_emissions_1997_2023_dist_df["original_recoverable_oe"]
)

# Calculate oil/gas reserve ration

fields_prod_emissions_1997_2023_dist_df["oil_gas_reserve_ratio"] = (
    fields_prod_emissions_1997_2023_dist_df["original_recoverable_oil"]
    / fields_prod_emissions_1997_2023_dist_df["original_recoverable_gas"]
)

fields_prod_emissions_1997_2023_dist_df.head()

data = fields_prod_emissions_1997_2023_dist_df.copy()

data_filtered = data.groupby("field").last().reset_index()

# Sort by biggest used %

# Calculate percentages
data_filtered["used_oe"] = np.round(
    data_filtered["original_recoverable_oe"]
    - data_filtered["current_remaining_recoverable_oe"],
    0,
)
data_filtered["remaining_percentage"] = np.round(
    (
        data_filtered["current_remaining_recoverable_oe"]
        / data_filtered["original_recoverable_oe"]
    )
    * 100,
    0,
)
data_filtered["used_percentage"] = np.round(
    (data_filtered["used_oe"] / data_filtered["original_recoverable_oe"]) * 100, 0
)

data_filtered = data_filtered.sort_values(by="remaining_percentage", ascending=False)

# Prepare data for plotting
plot_data = pd.melt(
    data_filtered,
    id_vars=["field"],
    value_vars=["remaining_percentage", "used_percentage"],
    var_name="Type",
    value_name="Percentage",
)

# Create a grouped bar chart
fig = go.Figure()

# Add bars for each type (used and remaining)
fig.add_trace(
    go.Bar(
        x=plot_data["field"][plot_data["Type"] == "remaining_percentage"],
        y=plot_data["Percentage"][plot_data["Type"] == "remaining_percentage"],
        name="Remaining OE",
        marker_color="rgba(0, 47, 95, 0.85)",
        text=[
            f"{val}%"
            for val in plot_data["Percentage"][
                plot_data["Type"] == "remaining_percentage"
            ]
        ],
        textposition="inside",
    )
)

fig.add_trace(
    go.Bar(
        x=plot_data["field"][plot_data["Type"] == "used_percentage"],
        y=plot_data["Percentage"][plot_data["Type"] == "used_percentage"],
        name="Used OE",
        marker_color="rgba(255, 99, 71, 0.7)",  # semi-transparent red
        text=[
            f"{val}%"
            for val in plot_data["Percentage"][plot_data["Type"] == "used_percentage"]
        ],
        textposition="inside",
    )
)

# Update layout for better visualization
fig.update_layout(
    title="Percentage of Original Recoverable Oil Equivalent Used and Remaining by Field",
    xaxis_title="Field",
    yaxis_title="Percentage of Recoverable Oil Equivalent (OE)",
    barmode="stack",
    legend_title="Type",
    yaxis=dict(
        tickformat=".2f%", range=[0, 100]
    ),  # Format y-axis as percentage and set range from 0 to 100
)

# Show the figure
fig.show()

# Filter to get only one entry per field (taking the last entry for simplicity)
data_filtered = data.groupby("field").last().reset_index()

# Calculate used OE
data_filtered["used_oe"] = np.round(
    data_filtered["original_recoverable_oe"]
    - data_filtered["current_remaining_recoverable_oe"],
    0,
)

# Sort by biggest used OE
data_filtered = data_filtered.sort_values(by="original_recoverable_oe", ascending=False)

# Prepare data for plotting
plot_data = pd.melt(
    data_filtered,
    id_vars=["field"],
    value_vars=["current_remaining_recoverable_oe", "used_oe"],
    var_name="Type",
    value_name="OE",
)

# Create a grouped bar chart
fig = go.Figure()

# Add bars for each type (used and remaining)
fig.add_trace(
    go.Bar(
        x=plot_data["field"][plot_data["Type"] == "current_remaining_recoverable_oe"],
        y=plot_data["OE"][plot_data["Type"] == "current_remaining_recoverable_oe"],
        name="Remaining OE",
        marker_color="rgba(0, 47, 95, 0.85)",  # McKinsey dark blue
        text=[
            f"{val:.0f}"
            for val in plot_data["OE"][
                plot_data["Type"] == "current_remaining_recoverable_oe"
            ]
        ],
        textposition="inside",
    )
)

fig.add_trace(
    go.Bar(
        x=plot_data["field"][plot_data["Type"] == "used_oe"],
        y=plot_data["OE"][plot_data["Type"] == "used_oe"],
        name="Used OE",
        marker_color="rgba(255, 99, 71, 0.7)",  # semi-transparent red
        text=[f"{val:.0f}" for val in plot_data["OE"][plot_data["Type"] == "used_oe"]],
        textposition="inside",
    )
)

# Update layout for better visualization
fig.update_layout(
    title="Original Recoverable Oil Equivalent Used and Remaining by Field",
    xaxis_title="Field",
    yaxis_title="Million SM3 Oil Equivalent (OE)",
    barmode="stack",  # Use 'group' for grouped bars
    legend_title="Type",
)

# Show the figure
fig.show()

# Get the unique field ids

# Extraxt 10 bigges by original recoverable oe
fields = (
    data.groupby("field")
    .last()
    .sort_values(by="original_recoverable_oe", ascending=False)
    .head(10)
    .index
)


# Create a plot for each field
fig = go.Figure()

for field in fields:
    field_data = data[data["field"] == field]
    max_production = field_data["net_oil_eq_prod_yearly_mill_sm3"].max()
    field_data["production_percentage"] = (
        field_data["net_oil_eq_prod_yearly_mill_sm3"] / max_production
    ) * 100

    fig.add_trace(
        go.Scatter(
            x=field_data["year"],
            y=field_data["production_percentage"],
            mode="lines+markers",
            name=f"{field} OE Production",
            text=[f"{val:.2f}%" for val in field_data["production_percentage"]],
            textposition="top center",
        )
    )

# Update layout for better visualization
fig.update_layout(
    title="Oil Equivalent Production Over Time (as % of Maximum Production)",
    xaxis_title="Year",
    yaxis_title="Production (% of Maximum)",
    showlegend=True,
)

# Show the figure
fig.show()

# Exporting the dataframe to a csv file unless the file exists, check if the export is successful

filename_path = "../../data/output/emissions_and_production/cleaned/fields_prod_emissions_intensities_share_1997_2023.csv"

if not os.path.exists(filename_path):
    fields_prod_emissions_1997_2023_dist_df.to_csv(filename_path, index=False)
    print("Saved file")
else:
    print("File already exists")

fields_prod_emissions_1997_2023_dist_df

# Sum of total OE reserves left on the NCS

total_remaining_recoverable_oe = fields_prod_emissions_1997_2023_dist_df[
    "current_remaining_recoverable_oe"
].sum()

total_remaining_recoverable_oe

