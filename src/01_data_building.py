# This script was automatically extracted from a Jupyter Notebook.

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

pd.set_option("display.max_columns", None)

def fetch_dataframe(url, sep=";", filetype="csv"):
    # Difi hotell uses comma separated values
    if filetype == "csv":
        df = pd.read_csv(url, sep=sep)
    elif filetype == "excel":
        df = pd.read_excel(url)
    return df

# ------ Original Sources ------
# production_url = 'https://factpages.sodir.no/public?/Factpages/external/tableview/field_production_monthly&rs:Command=Render&rc:Toolbar=false&rc:Parameters=f&IpAddress=not_used&CultureCode=en&rs:Format=CSV&Top100=false'
#
# Exporting data
# production_monthly_df.to_csv('../../data/output/emissions_and_production/production_monthly.csv', index=False)
# production_monthly.csv', index=False)

# ------ Fetching data from GitHub repo ------
base_output_url = "https://github.com/percw/Norwegian_oil_gas_decarbonization/raw/main/data/output/emissions_and_production/"
production_url = "production_monthly.csv"

production_monthly_df = fetch_dataframe(base_output_url + production_url, sep=",")
production_monthly_df

production_monthly_df["prfInformationCarrier"].unique()

# ------ Original data source (accessed 21.05.2024) ------
# operators_url = 'https://factpages.sodir.no/public?/Factpages/external/tableview/field_operator_hst&rs:Command=Render&rc:Toolbar=false&rc:Parameters=f&IpAddress=not_used&CultureCode=en&rs:Format=CSV&Top100=false'
# operators_df = fetch_dataframe(operators_url, sep=',')
#
# Exporting the operators_df to a csv file in a folder called data/output
# operators_df.to_csv('../../data/output/emissions_and_production/operators.csv', index=False)

# ------ Fetching data from GitHub repo ------
operators_url = "operators.csv"
operators_df = fetch_dataframe(base_output_url + operators_url, sep=",")
display(operators_df.head())

# ------ Original data source (accessed 21.05.2024) ------
# licensees_url = 'https://factpages.sodir.no/public?/Factpages/external/tableview/field_licensee_hst&rs:Command=Render&rc:Toolbar=false&rc:Parameters=f&IpAddress=not_used&CultureCode=en&rs:Format=CSV&Top100=false'
# licensees_df = fetch_dataframe(licensees_url, sep=',')
#
# Exporting the licensees_df to a csv file in a folder called data/output
# licensees_df.to_csv('../../data/output/emissions_and_production/licensees.csv', index=False)
# licensees_df


# ------ Fetching data from GitHub repo ------
licensees_url = "licensees.csv"
licensees_df = fetch_dataframe(base_output_url + licensees_url, sep=",")
display(licensees_df.head())

display(licensees_df.head())

# ------ Original data source (accessed 21.05.2024) ------
# investments_url = 'https://factpages.sodir.no/public?/Factpages/external/tableview/field_investment_yearly&rs:Command=Render&rc:Toolbar=false&rc:Parameters=f&IpAddress=not_used&CultureCode=en&rs:Format=CSV&Top100=false'
# investments_df = fetch_dataframe(investments_url, sep=',')
#
# Exporting the investments_df to a csv file in a folder called data/output
# investments_df.to_csv('../../data/output/emissions_and_production/investments.csv', index=False)
# investments_df

# ------ Fetching data from GitHub repo ------
investments_url = "investments.csv"
investments_df = fetch_dataframe(base_output_url + investments_url, sep=",")
display(investments_df.head())

display(investments_df.head())

# ------ Original data source (accessed 21.05.2024) ------
# future_investments_url = 'https://factpages.sodir.no/public?/Factpages/external/tableview/field_investment_expected&rs:Command=Render&rc:Toolbar=false&rc:Parameters=f&IpAddress=not_used&CultureCode=en&rs:Format=CSV&Top100=false'
# future_investments_df = fetch_dataframe(future_investments_url, sep=',')
#
# Exporting the future_investments_df to a csv file in a folder called data/output
# future_investments_df.to_csv('../../data/output/emissions_and_production/future_investments.csv', index=False)
# future_investments_df

# ------ Fetching data from GitHub repo ------
future_investments_url = "future_investments.csv"
future_investments_df = fetch_dataframe(
    base_output_url + future_investments_url, sep=","
)
display(future_investments_df.head())

display(future_investments_df.head())

# ----- Experimental Code --------
# Code was used to see how many wells has been drilled in the Norwegian Continental Shelf with purpose of CCS
#
# wellbores_raw_data_url_path = 'https://raw.githubusercontent.com/percw/Norwegian_oil_gas_decarbonization/main/data/raw_data/emission_and_production/Wellbores.csv'

# wellbores_df = fetch_dataframe(wellbores_raw_data_url_path, sep=',')
# wellbores_df

# Print all cells where wlbPurpose contains CCS
# wellbores_df[wellbores_df['wlbPurpose'].str.contains('CCS', na=False)]

# ------ Original data source (accessed 21.05.2024) ------
# fixed_facilities_url = 'https://factpages.sodir.no/public?/Factpages/external/tableview/facility_fixed&rs:Command=Render&rc:Toolbar=false&rc:Parameters=f&IpAddress=not_used&CultureCode=en&rs:Format=CSV&Top100=false'
# fixed_facilities_df = fetch_dataframe(fixed_facilities_url, sep=',')
#
# Exporting the fixed_facilities_df to a csv file in a folder called data/output
# fixed_facilities_df.to_csv('../../data/output/emissions_and_production/fixed_facilities.csv', index=False)
# fixed_facilities_df

# ------ Fetching data from GitHub repo ------
fixed_facilities_url = "fixed_facilities.csv"
fixed_facilities_df = fetch_dataframe(base_output_url + fixed_facilities_url, sep=",")
display(fixed_facilities_df.head())

display(fixed_facilities_df.head())
display(fixed_facilities_df.fclKind.value_counts())

# ------ Original data source (accessed 21.05.2024) ------
# movable_facilities_url = 'https://factpages.sodir.no/public?/Factpages/external/tableview/facility_moveable&rs:Command=Render&rc:Toolbar=false&rc:Parameters=f&IpAddress=not_used&CultureCode=en&rs:Format=CSV&Top100=false'
# movable_facilities_df = fetch_dataframe(movable_facilities_url, sep=',')
#
# Exporting the movable_facilities_df to a csv file in a folder called data/output
# movable_facilities_df.to_csv('../../data/output/emissions_and_production/movable_facilities.csv', index=False)
# movable_facilities_df

# ------ Fetching data from GitHub repo ------
movable_facilities_url = "movable_facilities.csv"
movable_facilities_df = fetch_dataframe(
    base_output_url + movable_facilities_url, sep=","
)
display(movable_facilities_df.head())

display(movable_facilities_df.head())

base_url = "https://github.com/percw/Norwegian_oil_gas_decarbonization/raw/main/data/raw_data/emission_and_production/"

emissions_co2_url = base_url + "Emissions_CO2.xlsx"
emissions_co2_df = fetch_dataframe(emissions_co2_url, filetype="excel")

# Setting row 0 as column names
emissions_co2_df.columns = emissions_co2_df.iloc[1]
emissions_co2_df = emissions_co2_df[2:]

display(emissions_co2_df.head())

emissions_co2_df.isna().sum()

emissions_co2_df.Anleggsnavn.unique()

# Convert the 'field' column to strings, strip whitespace, and then to lowercase
emissions_co2_df["Anleggsnavn"] = emissions_co2_df["Anleggsnavn"].apply(
    lambda x: str(x).strip().lower() if pd.notnull(x) else x
)

# Printing all data about the 'svalin' field
lalala = emissions_co2_df[
    emissions_co2_df["Anleggsnavn"] == "svalin (equinor energy as)"
]
lalala

emissions_co2_df

emissions_ch4_url = base_url + "Emissions_methane.xlsx"
emissions_ch4_df = fetch_dataframe(emissions_ch4_url, filetype="excel")

# Setting row 0 as column names
emissions_ch4_df.columns = emissions_ch4_df.iloc[1]
emissions_ch4_df = emissions_ch4_df[2:]

display(emissions_ch4_df.head())

emissions_nox_url = base_url + "Emissions_NOX.xlsx"
emissions_nox_df = fetch_dataframe(emissions_nox_url, filetype="excel")

# Setting row 0 as column names
emissions_nox_df.columns = emissions_nox_df.iloc[1]
emissions_nox_df = emissions_nox_df[2:]

display(emissions_nox_df.head())

emissions_oil_spill = base_url + "Emissions_oil.xlsx"
emissions_oil_spill_df = fetch_dataframe(emissions_oil_spill, filetype="excel")

# Setting row 0 as column names
emissions_oil_spill_df.columns = emissions_oil_spill_df.iloc[1]
emissions_oil_spill_df = emissions_oil_spill_df[2:]

emissions_oil_spill_df

emissions_water = base_url + "Emissions_water.xlsx"
emissions_water_df = fetch_dataframe(emissions_water, filetype="excel")

# Setting row 0 as column names

emissions_water_df.columns = emissions_water_df.iloc[1]
emissions_water_df = emissions_water_df[2:]

emissions_water_df

# Renaming columns from Norwegian to English


def clean_emissions_df(df, emissions_type, unit, water_or_air="luft"):
    if water_or_air == "vann":
        df = df.rename(
            columns={
                "År": "year",
                "Anleggsnavn": "field",
                f"Årlig utslipp til {water_or_air}": f"yearly_{emissions_type}_emissions_{unit}",
                "Org.nr.": "org_number",
                "Årlig utslipp til undergrunn": f"yearly_subsea_{emissions_type}_emissions",
            }
        )
        df = df[
            [
                "field",
                "year",
                f"yearly_{emissions_type}_emissions_{unit}",
                "org_number",
                f"yearly_subsea_{emissions_type}_emissions",
            ]
        ]

    else:
        df = df.rename(
            columns={
                "År": "year",
                "Anleggsnavn": "field",
                f"Årlig utslipp til {water_or_air}": f"yearly_{emissions_type}_emissions_{unit}",
                "Org.nr.": "org_number",
            }
        )
        df = df[
            ["field", "year", f"yearly_{emissions_type}_emissions_{unit}", "org_number"]
        ]

    df[f"yearly_{emissions_type}_emissions_{unit}"] = pd.to_numeric(
        df[f"yearly_{emissions_type}_emissions_{unit}"], errors="coerce"
    )
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["operator"] = df["field"].str.extract(r"\((.*?)\)")
    df["field"] = df["field"].str.replace(r"\(.*\)", "")
    return df

emissions_co2_df = clean_emissions_df(emissions_co2_df, "co2", "1000_tonnes")

emissions_co2_df

emissions_ch4_df

# Methane emissions

emissions_ch4_df = clean_emissions_df(emissions_ch4_df, "ch4", "tons")

emissions_ch4_df

emissions_ch4_df["operator"].unique()

# NOX emissions

emissions_nox_df = clean_emissions_df(emissions_nox_df, "nox", "tons")
emissions_nox_df

# Emissions to water

emissions_water_df = clean_emissions_df(emissions_water_df, "water", "m3", "vann")
emissions_water_df

# Check for duplicate Year and field values
emissions_water_df.duplicated(subset=["year", "field"]).sum()

emissions_oil_spill_df = clean_emissions_df(
    emissions_oil_spill_df, "oil_spill", "tons", "vann"
)
emissions_oil_spill_df

emission_files_dict = {
    "emissions_co2": emissions_co2_df,
    "emissions_methane": emissions_ch4_df,
    "emissions_nox": emissions_nox_df,
    "emissions_oil": emissions_oil_spill_df,
    "emissions_water": emissions_water_df,
}

# Exporting the cleaned emissions dataframes to csv files in a folder called data/output

for key, df in emission_files_dict.items():
    df.to_csv(f"../../data/output/emissions_and_production/{key}.csv", index=False)

# Removing yearly_subsea_oil_spill_emissions column since it has only NaN values

emissions_oil_spill_df = emissions_oil_spill_df.drop(
    columns="yearly_subsea_oil_spill_emissions"
)

# Converting field and operator to lower case strings

emissions_dfs = [
    emissions_co2_df,
    emissions_ch4_df,
    emissions_nox_df,
    emissions_water_df,
    emissions_oil_spill_df,
]

for df in emissions_dfs:
    df["field"] = df["field"].astype(str).str.lower()
    df["operator"] = df["operator"].astype(str).str.lower()
    # orgnumber to int64
    df["org_number"] = pd.to_numeric(df["org_number"], errors="coerce")

# Changing all occurances of 'equinor asa' to 'equinor energy as'

for df in emissions_dfs:
    df["operator"] = df["operator"].replace("equinor asa", "equinor energy as")

# Removing entirely empty columns (NaN's)
for df in emissions_dfs:
    df = df.dropna(axis=1, how="all", inplace=True)

# Checking the shape of all emission dataframes

for df in emissions_dfs:
    print(df.shape)

# Checking the first and last years of all emission dataframes

for df in emissions_dfs:
    print(df.year.min(), df.year.max())

# Creating function to print all the missing years between 1997 and 2023 for all dfs


def print_missing_years(df):
    missing_years = set(range(1997, 2023)).difference(df.year)
    print(missing_years)


for df in emissions_dfs:
    print_missing_years(df)

# Checking for NaN values for all emissions dataframes
for df in emissions_dfs:
    print(df.isnull().sum())

# Checking for NA values for all emissions dataframes
for df in emissions_dfs:
    print(df.isna().sum())

def check_unique_org_number(df):
    """
    Checks if each combination of operator and field has a unique org_number.

    Parameters:
    df (pd.DataFrame): DataFrame containing the columns 'field', 'operator', and 'org_number'.

    Returns:
    bool: True if each combination of operator and field has a unique org_number, False otherwise.
    """
    # Check for missing values in 'operator' and 'org_number'
    if df[["operator", "org_number"]].isnull().any().any():
        print("Error: There are missing values in 'operator' or 'org_number'.")
        return False

    # Check for duplicate combinations of 'operator' and 'field' with different 'org_number'
    duplicates = df.groupby(["operator", "field"])["org_number"].nunique().reset_index()
    if any(duplicates["org_number"] > 1):
        print(
            "Error: There are duplicate combinations of 'operator' and 'field' with different 'org_number'."
        )
        return False

    return True

for df in (
    emissions_co2_df,
    emissions_ch4_df,
    emissions_nox_df,
    emissions_water_df,
    emissions_oil_spill_df,
):
    if check_unique_org_number(df):
        print("Each combination of operator and field has a unique org_number.")
    else:
        print("There are inconsistencies in the org_number assignment.")

display(emissions_ch4_df.head())

def check_operator_consistency(dfs, on_columns):
    """
    Checks if the same combination of field, year, and org_number corresponds to the same operator across all DataFrames.

    Parameters:
    dfs (list of pd.DataFrame): List of DataFrames to check.
    on_columns (list of str): List of column names to check for consistency.

    Returns:
    bool: True if the consistency check passes, False otherwise.
    """

    # Combine all unique combinations of on_columns and operator
    combined = pd.concat(
        [df[on_columns + ["operator"]].dropna().drop_duplicates() for df in dfs]
    )

    # Group by on_columns and check for unique operator values
    consistency_check = combined.groupby(on_columns)["operator"].nunique().reset_index()

    # If any group has more than one unique operator, consistency check fails
    if any(consistency_check["operator"] > 1):
        print("Inconsistency found in operator assignments:")

        print(consistency_check[consistency_check["operator"] > 1])
        return False
    return True

dfs_to_check_operator = [
    emissions_co2_df,
    emissions_nox_df,
    emissions_water_df,
    emissions_oil_spill_df,
]
on_columns = ["year", "field", "org_number"]

check_operator_consistency(dfs_to_check_operator, on_columns)

display(emissions_co2_df.head())

from functools import reduce

def merge_emission_data(dfs, on_columns, operator_df):
    """
    Merges a list of DataFrames on specified columns, keeping the operator from a specific DataFrame.

    Parameters:
    dfs (list of pd.DataFrame): List of DataFrames to merge.
    on_columns (list of str): List of column names to merge on.
    operator_df (pd.DataFrame): DataFrame to take the operator column from.

    Returns:
    pd.DataFrame: The merged DataFrame with the operator column from operator_df.
    """
    # Ensure the operator column is only in operator_df
    dfs_no_operator = [df.drop(columns=['operator'], errors='ignore') for df in dfs if not df.equals(operator_df)]

    # Merge the DataFrames sequentially
    merged_df = reduce(lambda left, right: pd.merge(left, right, on=on_columns, how='outer'), dfs_no_operator)
    
    # Merge with the operator_df to add the operator column
    merged_df = pd.merge(merged_df, operator_df, on=on_columns, how='left', suffixes=('', '_drop'))
    
    # Drop any duplicate columns that were suffixed with '_drop'
    merged_df = merged_df.loc[:, ~merged_df.columns.str.endswith('_drop')]

    return merged_df


# Merged DataFrame, keeping the operator from emissions_co2_df
emissions_df = merge_emission_data(emissions_dfs, on_columns, emissions_co2_df.head())

display(emissions_df.head())

# Checking number of NaNs in merged_df

emissions_df.isna().sum()

display(emissions_df.tail(30))

# Finding out which fields has the most NaN values and how many per column


# Group by 'field' and count NaN values in each column for each field
nan_counts_per_field = emissions_df.groupby("field").apply(lambda x: x.isna().sum())

# Remove the rows that have 0 for all columns
df = df.loc[~(df == 0).all(axis=1)]

print("NaN counts per field and column:")
(nan_counts_per_field)

# Removing yearly_subsea_water_emissions column from emissions_df
emissions_df = emissions_df.drop(columns=["yearly_subsea_water_emissions"])

# Checking the year 2013 for the field 'statfjord nord'

emissions_ch4_df[
    (emissions_ch4_df["year"] == 2013) & (emissions_ch4_df["field"] == "statfjord nord")
]

# Deleting the rows that has NaN values for the columns operator, yearly_nox_emissions_tons, and yearly_ch4_emissions_tons

emissions_df = emissions_df.dropna(
    subset=["operator", "yearly_nox_emissions_tons", "yearly_ch4_emissions_tons"]
)

emissions_df.isna().sum()

emissions_df["operator"].value_counts()

