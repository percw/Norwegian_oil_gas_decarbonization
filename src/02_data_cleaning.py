# This script was automatically extracted from a Jupyter Notebook.

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import os

pd.set_option("display.max_columns", None)

def fetch_dataframe(url, sep=",", filetype="csv"):
    if filetype == "csv":
        df = pd.read_csv(url, sep=sep)
    elif filetype == "excel":
        df = pd.read_excel(url)
    return df


base_output_url = "https://github.com/percw/Norwegian_oil_gas_decarbonization/raw/main/data/output/emissions_and_production/"
datafile_names = [
    "production_monthly",
    "operators",
    "movable_facilities",
    "licensees",
    "investments",
    "future_investments",
    "fixed_facilities",
    "wellbores",
    "field_description",
    "field_status",
    "field_overview",
    "field_reserves",
]

# Creating a dictionary to store the dataframes
dataframes = {}

for name in datafile_names:
    url = base_output_url + name + ".csv"
    dataframes[name] = fetch_dataframe(url)


# Setting the name of the df's	as the keys in the dictionary with _df appended
for name, df in dataframes.items():
    globals()[name + "_df"] = df

emission_file_names = [
    "emissions_co2",
    "emissions_methane",
    "emissions_nox",
    "emissions_oil",
    "emissions_water",
]

# Fetching the emissions dataframes from GitHub
emission_dataframes = {}

for name in emission_file_names:
    url = base_output_url + name + ".csv"
    emission_dataframes[name] = fetch_dataframe(url)

    # Setting the name of the df's	as the keys in the dictionary with _df appended
for name, df in emission_dataframes.items():
    globals()[name + "_df"] = df

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

# Checking  all unique oerators in the emissions dataframes

for name, df in emission_dataframes.items():
    print(name, df["operator"].nunique())
    print("\n")

# Printing the unique operators in the emissions dataframes

for name, df in emission_dataframes.items():
    print(name, df["operator"].unique())
    print("\n")

# Checking for missing values in all emissions dfs

for name, df in emission_dataframes.items():
    print(name, df.isnull().sum())
    print("\n")

# Dropping yearly_subsea_water_emissions column from emissions_water_df

emissions_water_df = emissions_water_df.drop(columns="yearly_subsea_water_emissions")

# Checking for nunique fields in the emissions dataframes

for name, df in emission_dataframes.items():
    print(name, df["field"].nunique())
    print("\n")

emissions_co2_df.describe()

# Merging all the emissions dataframes into one

emissions_df = emissions_co2_df.merge(
    emissions_methane_df, on=["field", "year", "org_number", "operator"], how="left"
)
emissions_df = emissions_df.merge(
    emissions_nox_df, on=["field", "year", "org_number", "operator"], how="left"
)
emissions_df = emissions_df.merge(
    emissions_oil_df, on=["field", "year", "org_number", "operator"], how="left"
)
emissions_df = emissions_df.merge(
    emissions_water_df, on=["field", "year", "org_number", "operator"], how="left"
)

emissions_df

# removing tailing whitespace from the field column in the emissions_df

emissions_df["field"] = emissions_df["field"].str.strip()

emissions_df[emissions_df["field"] == "vale"]

len(emissions_df.field.unique())

# Checking datatypes for all dfs

for name, df in dataframes.items():
    print(name, df.dtypes)
    print("\n")

# Checking for missing values in all dfs
for name, df in dataframes.items():
    print(name, df.isnull().sum())
    print("\n")

# Renaming columns from Norwegian to English


def clean_production_df(df, names_dict):
    df = df.rename(columns=names_dict)
    return df


production_name_change = {
    "prfInformationCarrier": "field",
    "prfYear": "year",
    "prfMonth": "month",
    "prfPrdNGLNetMillSm3": "net_ngl_prod_monthly_sm3",
    "prfPrdOilNetMillSm3": "net_oil_prod_monthly_sm3",
    "prfPrdGasNetBillSm3": "net_gas_prod_monthly_sm3",
    "prfPrdCondensateNetMillSm3": "net_condensate_prod_monthly_sm3",
    "prfPrdOeNetMillSm3": "net_oil_eq_prod_monthly_sm3",
    "prfPrdProducedWaterInFieldMillSm3": "produced_water_in_field",
    "prfNpdidInformationCarrier": "field_id",
}

production_monthly_df = clean_production_df(
    production_monthly_df, production_name_change
)
display(production_monthly_df)

# Filtering out all data reported before 1990

production_monthly_full_df = production_monthly_df.copy()
production_monthly_df = production_monthly_df[production_monthly_df["year"] >= 1990]
production_monthly_df

# Make all field names lower case
production_monthly_df["field"] = production_monthly_df["field"].str.lower()

# Checking all field names containing æ,ø,å


def check_for_special_characters(df, column):
    special_char = ["æ", "ø", "å", "Æ", "Ø", "Å"]
    for char in special_char:
        print(df[df[column].str.contains(char, na=False)][column].unique())


check_for_special_characters(production_monthly_df, "field")

# Checking if field_id and field match across the dataframe

print(
    "Number of fields in the field_id column:",
    production_monthly_df["field_id"].nunique(),
)
print("Number of fields in the field column:", production_monthly_df["field"].nunique())

# Checking that field_id and field match across the dataframe
field_id_field_match = (
    production_monthly_df.groupby(["field_id", "field"])
    .size()
    .reset_index(name="count")
)
field_id_field_match = field_id_field_match[field_id_field_match["count"] > 1]
print(field_id_field_match)

# Creating a dict with field and field_id

field_field_id_dict = (
    production_monthly_df[["field", "field_id"]]
    .drop_duplicates()
    .set_index("field")
    .to_dict()["field_id"]
)

# Calculating yearly production for net_oil_prod_monthly_sm3, net_gas_prod_monthly_sm3,
# net_ngl_prod_monthly_sm3, net_condensate_prod_monthly_sm3, net_oil_eq_prod_monthly_sm3,
# produced_water_in_field, and adding it to a new df called production_yearly_df
production_yearly_df = (
    production_monthly_df.groupby(["field", "year"])
    .agg(
        {
            "net_oil_prod_monthly_sm3": "sum",
            "net_gas_prod_monthly_sm3": "sum",
            "net_ngl_prod_monthly_sm3": "sum",
            "net_condensate_prod_monthly_sm3": "sum",
            "net_oil_eq_prod_monthly_sm3": "sum",
            "produced_water_in_field": "sum",
        }
    )
    .reset_index()
)

# Renaming the columns in the production_yearly_df to reflect that they are yearly values
production_yearly_df = production_yearly_df.rename(
    columns={
        "net_oil_prod_monthly_sm3": "net_oil_prod_yearly_mill_sm3",
        "net_gas_prod_monthly_sm3": "net_gas_prod_yearly_bill_sm3",
        "net_ngl_prod_monthly_sm3": "net_ngl_prod_yearly_mill_sm3",
        "net_condensate_prod_monthly_sm3": "net_condensate_prod_yearly_mill_sm3",
        "net_oil_eq_prod_monthly_sm3": "net_oil_eq_prod_yearly_mill_sm3",
        "produced_water_in_field": "produced_water_yearly_mill_sm3",
    }
)

# Adding the field_id to the production_yearly_df from the field_field_id_dict
production_yearly_df["field_id"] = production_yearly_df["field"].map(
    field_field_id_dict
)

display(production_yearly_df)

# Function to compute monthly volatility and add it to the yearly DataFrame
def add_volatility_to_yearly(monthly_df, yearly_df, group_columns, value_columns):
    """
    Computes the monthly volatility for specified columns and adds them to the yearly DataFrame.

    Parameters:
    monthly_df (pd.DataFrame): DataFrame containing monthly production data.
    yearly_df (pd.DataFrame): DataFrame containing yearly aggregated data.
    group_columns (list of str): Columns to group by for calculating volatility.
    value_columns (list of str): Columns for which to compute volatility.

    Returns:
    pd.DataFrame: The yearly DataFrame with added volatility columns.
    """
    for col in value_columns:
        # Compute the standard deviation (volatility) for each group
        volatility = (
            monthly_df.groupby(group_columns)[col]
            .std()
            .reset_index(name=f"{col}_volatility")
        )
        # Replace NaN with 0
        volatility[f"{col}_volatility"].fillna(0, inplace=True)
        # Merge the volatility into the yearly DataFrame
        yearly_df = yearly_df.merge(volatility, on=group_columns, how="left")
    return yearly_df


# List of production columns
production_columns = [
    "net_oil_prod_monthly_sm3",
    "net_gas_prod_monthly_sm3",
    "net_ngl_prod_monthly_sm3",
    "net_condensate_prod_monthly_sm3",
    "net_oil_eq_prod_monthly_sm3",
    "produced_water_in_field",
]

# Compute and add volatility columns to the yearly DataFrame
production_yearly_df = add_volatility_to_yearly(
    production_monthly_df, production_yearly_df, ["field", "year"], production_columns
)

display(production_yearly_df.head())

production_yearly_df.describe()

yearly_production_columns = [
    "net_oil_prod_yearly_mill_sm3",
    "net_gas_prod_yearly_bill_sm3",
    "net_ngl_prod_yearly_mill_sm3",
    "net_condensate_prod_yearly_mill_sm3",
    "net_oil_eq_prod_yearly_mill_sm3",
    "produced_water_yearly_mill_sm3",
]

# Print all with negative values
for col in yearly_production_columns:
    print(
        f"Negative values in {col}: {production_yearly_df[production_yearly_df[col] < 0].shape[0]}"
    )
    # The negative number:
    print(production_yearly_df[production_yearly_df[col] < 0][col])

# Setting all the negative values to 0
for col in yearly_production_columns:
    production_yearly_df[col] = production_yearly_df[col].clip(lower=0)

production_yearly_df.describe()

# Printing out all fields with numbers in the name


def check_for_numbers(df, column):
    print(df[df[column].str.contains("\d", na=False)][column].unique())


discoveries = check_for_numbers(production_yearly_df, "field")

# Removing the fields with numbers in the name / these are discoveries not fields
production_yearly_df = production_yearly_df[
    ~production_yearly_df["field"].str.contains("\d", na=False)
]

field_status_df.head()

# Convert date columns to datetime
field_status_df["fldStatusFromDate"] = pd.to_datetime(
    field_status_df["fldStatusFromDate"], format="%d.%m.%Y"
)
field_status_df["fldStatusToDate"] = pd.to_datetime(
    field_status_df["fldStatusToDate"], format="%d.%m.%Y"
)
production_yearly_df["year"] = pd.to_datetime(production_yearly_df["year"], format="%Y")

# Ensure proper field name matching
field_status_df["fldName"] = field_status_df["fldName"].str.lower()


# Function to get status based on date range
def get_status(row, status_df):
    field = row["field"]
    year = row["year"]
    status_rows = status_df[
        (status_df["fldName"] == field)
        & (status_df["fldStatusFromDate"] <= year)
        & (
            (status_df["fldStatusToDate"].isna())
            | (status_df["fldStatusToDate"] >= year)
        )
    ]
    if not status_rows.empty:
        return status_rows.iloc[0]["fldStatus"]
    return None


# Apply function to get status for each row
production_yearly_df["status"] = production_yearly_df.apply(
    get_status, axis=1, status_df=field_status_df
)

# Convert the year to only show the year
production_yearly_df["year"] = production_yearly_df["year"].dt.year

# Display the updated DataFrame
production_yearly_df

production_yearly_df[production_yearly_df["status"].isna()]

# Remove balder 1991
production_yearly_df = production_yearly_df[
    ~(
        (production_yearly_df["field"] == "balder")
        & (production_yearly_df["year"] == 1991)
    )
]

# Set 'byrding' field 2017 to 'Producing'
production_yearly_df.loc[
    (production_yearly_df["field"] == "byrding")
    & (production_yearly_df["year"] == 2017),
    "status",
] = "Producing"

# Set gimle 2005 to Approved for production
production_yearly_df.loc[
    (production_yearly_df["field"] == "gimle") & (production_yearly_df["year"] == 2005),
    "status",
] = "Approved for production"

# Set gimle 2006 to Producing
production_yearly_df.loc[
    (production_yearly_df["field"] == "gimle") & (production_yearly_df["year"] == 2006),
    "status",
] = "Producing"

# Remove grane 1996
production_yearly_df = production_yearly_df[
    ~(
        (production_yearly_df["field"] == "grane")
        & (production_yearly_df["year"] == 1996)
    )
]

# Remove mime 1990 and 1991
production_yearly_df = production_yearly_df[
    ~(
        (production_yearly_df["field"] == "mime")
        & (production_yearly_df["year"].isin([1990, 1991]))
    )
]

# Set mime 1992 to Approved for production
production_yearly_df.loc[
    (production_yearly_df["field"] == "mime") & (production_yearly_df["year"] == 1992),
    "status",
] = "Approved for production"

# Set sindre 2017 to producing
production_yearly_df.loc[
    (production_yearly_df["field"] == "sindre")
    & (production_yearly_df["year"] == 2017),
    "status",
] = "Producing"

production_yearly_df

field_overview_df

# Setting the current status of the field in its own column using the field_overview_df

field_overview_df.fldName = field_overview_df.fldName.str.lower()
field_overview_df["current_status"] = field_overview_df["fldCurrentActivitySatus"]

# Merging the current status of the field to the production_yearly_df
production_yearly_df = production_yearly_df.merge(
    field_overview_df[["fldName", "current_status"]],
    left_on="field",
    right_on="fldName",
    how="left",
)


# removing fldName column
production_yearly_df = production_yearly_df.drop(columns="fldName")

display(production_yearly_df.current_status.isna().sum())
display(production_yearly_df)

field_overview_df[field_overview_df["current_status"] == "Approved for production"]

# This is a list of future fields that are not yet producing

production_yearly_df.current_status.isna().sum()

# Renaming fldNpdidOwner to field_owner and fldNpdidField to field_id in the field_overview_df

field_overview_df = field_overview_df.rename(
    columns={"fldNpdidOwner": "field_owner", "fldNpdidField": "field_id"}
)

# Populating the production_yearly_df with the field_id and field_owner from the field_overview_df without merging

production_yearly_df["field_id"] = production_yearly_df["field"].map(
    field_field_id_dict
)
production_yearly_df["field_owner"] = production_yearly_df["field"].map(
    field_overview_df.set_index("fldName")["field_owner"]
)

production_yearly_df

# Extracting rows where 'fldDescriptionHeading' is 'Transport'
field_description_transport = field_description_df[
    field_description_df["fldDescriptionHeading"] == "Transport"
]

# Displaying the number of unique 'fldName' entries
print(
    "Number of unique fields in field_description_transport:",
    field_description_transport["fldName"].nunique(),
)


# Function to perform lookup and add new column based on matching field names within fldDescriptionText
def find_field_names_in_description(
    df, lookup_df, lookup_column, description_column, new_column
):
    """
    Searches for field names within description text and adds the field name to a new column if found.

    Parameters:
    df (pd.DataFrame): DataFrame to add the lookup values to.
    lookup_df (pd.DataFrame): DataFrame containing the lookup values.
    lookup_column (str): Column containing the values to look for.
    description_column (str): Column containing the text to search within.
    new_column (str): Name of the new column to add.

    Returns:
    pd.DataFrame: The original DataFrame with added lookup values.
    """
    # Convert the lookup column to a list of unique values in uppercase
    lookup_values = lookup_df[lookup_column].str.upper().unique().tolist()

    # Initialize the new column with None
    df[new_column] = None

    # Iterate over each row and search for lookup values in the description text
    for index, row in df.iterrows():
        found_field_names = []
        if pd.notnull(row[description_column]):
            description_text = row[description_column].upper().split()
            for value in lookup_values:
                if value in description_text:
                    found_field_names.append(value)
        if found_field_names:
            df.at[index, new_column] = ", ".join(found_field_names)

    return df


# Adding field name information to 'field_description_transport'
field_description_transport = find_field_names_in_description(
    field_description_transport,
    field_description_transport,
    "fldName",
    "fldDescriptionText",
    "processing_field",
)


len(field_description_transport.processing_field.unique())
display(
    field_description_transport[
        field_description_transport["processing_field"].isnull()
    ].head()
)

# In field_description_transport, rename fldName to field and fldDescriptionText to transport
field_description_transport = field_description_transport.rename(
    columns={"fldName": "field", "fldDescriptionText": "transport"}
)

# Making all field names lower case
field_description_transport["field"] = field_description_transport["field"].str.lower()
field_description_transport["processing_field"] = field_description_transport[
    "processing_field"
].str.lower()

# Displaying these columns: 'field', 'transport', 'processing_field'
display(field_description_transport[["field", "transport", "processing_field"]].head())

# ------ Manual check done in Excel ------
# See the file 'field_processing_list_manual_check.xlsx' in the emissions_and_production/cleaned/ folder
# field_description_transport[['field', 'transport', 'processing_field', 'field_in_emissions']].to_excel('field_processing_list_manual_check.xlsx', index=False)
#

# Import the manually checked file

field_processing_list_cleaned_df = pd.read_excel(
    "../../data/output/emissions_and_production/cleaned/field_processing_list_manual_check.xlsx"
)
field_processing_list_cleaned_df.head()

production_yearly_df.head()

field_processing_list_cleaned_df.head()

# Perform the merge based on the 'field' column
merged_df = pd.merge(
    production_yearly_df,
    field_processing_list_cleaned_df[
        ["field", "processing_field", "field_in_emissions"]
    ],
    on="field",
    how="left",
)

# Display the resulting DataFrame
merged_df.head()

merged_df["field_in_emissions"].value_counts()

fields_yearly_df = merged_df.copy()

fixed_facilities_df.head()

fixed_facilities_df["fclPhase"].unique()

facilites_operators = fixed_facilities_df["fclCurrentOperatorName"].unique()
facilites_operators

facilites_name_change = {
    "fclName": "facility_name",
    "fclPhase": "facility_phase",
    "fclSurface": "facility_surface",
    "fclCurrentOperatorName": "facility_operator",
    "fclKind": "facility_kind",
    "fclBelongsToName": "facility_belongs_to_name",
    "fclBelongsToKind": "facility_belongs_to_kind",
    "fclBelongsToS": "facility_belongs_to_s",
    "fclFunctions": "facility_functions",
    "fclStartupDate": "facility_startup_date",
    "fclGeodeticDatum": "facility_geodetic_datum",
    "fclWaterDepth": "facility_water_depth",
    "fclDesignLifetime": "facility_design_lifetime",
    "fclNationName": "facility_nation_name",
    "fclNpdidFacility": "facility_id",
}


# Renaming columns in the fixed_facilities_df
fixed_facilities_df = fixed_facilities_df.rename(columns=facilites_name_change)

# Making facility_name lower case
fixed_facilities_df["facility_name"] = fixed_facilities_df["facility_name"].str.lower()

# Making facility_belongs_to_name lower case
fixed_facilities_df["facility_belongs_to_name"] = fixed_facilities_df[
    "facility_belongs_to_name"
].str.lower()

fixed_facilities_df.head()

fixed_facilities_df["facility_belongs_to_name"].unique()

# Checking all facilites : facility_nation_name = ~Norway

fixed_facilities_df[fixed_facilities_df["facility_nation_name"] != "Norway"]

# Remove all facilities not in Norway
fixed_facilities_df = fixed_facilities_df[
    fixed_facilities_df["facility_nation_name"] == "Norway"
]

# Finding instances where the operator is not the same for the same facility
facility_operator_mismatch = (
    fixed_facilities_df.groupby(["facility_name", "facility_operator"])
    .size()
    .reset_index(name="count")
)
facility_operator_mismatch = facility_operator_mismatch[
    facility_operator_mismatch["count"] > 1
]
print(facility_operator_mismatch)

facilities_df = fixed_facilities_df.copy()

# Only keeping the facilites where the facility_belongs_to_name is in the production_yearly_df
facilities_df = facilities_df[
    facilities_df["facility_belongs_to_name"].isin(production_yearly_df["field"])
]
facilities_df

# Convert the facility_startup_date to datetime and only displaying the year
facilities_df["facility_startup_date"] = pd.to_datetime(
    facilities_df["facility_startup_date"], format="%d.%m.%Y"
)
facilities_df["facility_startup_date"] = facilities_df[
    "facility_startup_date"
].dt.year.astype("Int64")

# Remove facilites where startup date is NaN
facilities_df = facilities_df[facilities_df["facility_startup_date"].notna()]

# Removing all facilities with startup date before 1990
facilities_df = facilities_df[facilities_df["facility_startup_date"] >= 1990]

# Calculate number of IN SERVICE facilities per year and field

facilities_in_service = facilities_df[facilities_df["facility_phase"] == "IN SERVICE"]
facilities_in_service_count = (
    facilities_in_service.groupby(["facility_belongs_to_name", "facility_startup_date"])
    .size()
    .reset_index(name="count")
)
facilities_in_service_count = facilities_in_service_count.rename(
    columns={"facility_belongs_to_name": "field", "facility_startup_date": "year"}
)

facilities_in_service_count

# For all the fields that have several years with facilities in service, we want to add cumulatively add the number of facilities in service
facilities_in_service_count["cumulative_facilities_in_service"] = (
    facilities_in_service_count.groupby("field")["count"].cumsum()
)

# Remove count column and rename cumulative_facilities_in_service to count
facilities_in_service_count = facilities_in_service_count.drop(columns="count")
facilities_in_service_count = facilities_in_service_count.rename(
    columns={"cumulative_facilities_in_service": "count"}
)
facilities_in_service_count

# Calculate number of SHUT DOWN facilities per year and field

facilities_shut_down = facilities_df[facilities_df["facility_phase"] == "SHUT DOWN"]

facilities_shut_down_count = (
    facilities_shut_down.groupby(["facility_belongs_to_name", "facility_startup_date"])
    .size()
    .reset_index(name="count")
)
facilities_shut_down_count = facilities_shut_down_count.rename(
    columns={"facility_belongs_to_name": "field", "facility_startup_date": "year"}
)

# Using apply, we can calculate the cumulative number of shut down facilities
facilities_shut_down_count["cumulative_facilities_shut_down"] = (
    facilities_shut_down_count.groupby("field")["count"].cumsum()
)

# Remove count column and rename cumulative_facilities_shut_down to count
facilities_shut_down_count = facilities_shut_down_count.drop(columns="count")
facilities_shut_down_count = facilities_shut_down_count.rename(
    columns={"cumulative_facilities_shut_down": "count"}
)
facilities_shut_down_count

# One hot encode the facility_kind column without the facility_kind_ prefix only keeping the one hot encoding columns
facility_kind_in_service_df = pd.get_dummies(
    facilities_in_service, columns=["facility_kind"], prefix="", prefix_sep=""
)

# creating a list of the encoded columns
encoded_columns = facilities_in_service["facility_kind"].unique().tolist()

# facility_kind_in_service_df[['facility_belongs_to_name']+['facility_startup_date']+encoded_columns]

# Group by field and year and sum the one hot encoded columns
facility_kind_in_service_df = (
    facility_kind_in_service_df.groupby(
        ["facility_belongs_to_name", "facility_startup_date"]
    )[encoded_columns]
    .sum()
    .reset_index()
)

facility_kind_in_service_df.columns = ["field", "year"] + [
    f"facility_kind_{col.lower()}" for col in facility_kind_in_service_df.columns[2:]
]

facility_kind_in_service_df

# One hot encode the facility_kind column without the facility_kind_ prefix only keeping the one hot encoding columns
facility_kind_shut_down_df = pd.get_dummies(
    facilities_shut_down, columns=["facility_kind"], prefix="", prefix_sep=""
)

# creating a list of the encoded columns
encoded_columns = facilities_shut_down["facility_kind"].unique().tolist()

# Group by field and year and sum the one hot encoded columns
facility_kind_shut_down_df = (
    facility_kind_shut_down_df.groupby(
        ["facility_belongs_to_name", "facility_startup_date"]
    )[encoded_columns]
    .sum()
    .reset_index()
)
facility_kind_shut_down_df

# One hot encoding the facility_surface column

facility_surface_in_service_df = pd.get_dummies(
    facilities_in_service, columns=["facility_surface"], prefix="", prefix_sep=""
)
encoded_columns = facilities_in_service["facility_surface"].unique().tolist()

facility_surface_in_service_df = (
    facility_surface_in_service_df.groupby(
        ["facility_belongs_to_name", "facility_startup_date"]
    )[encoded_columns]
    .sum()
    .reset_index()
)

# Cumulative sum of the one hot encoded columns
facility_surface_in_service_df[encoded_columns] = (
    facility_surface_in_service_df.groupby(
        "facility_belongs_to_name"
    )[encoded_columns].cumsum()
)
facility_surface_in_service_df

facility_surface_shut_down_df = pd.get_dummies(
    facilities_shut_down, columns=["facility_surface"], prefix="", prefix_sep=""
)
encoded_columns = facilities_shut_down["facility_surface"].unique().tolist()

facility_surface_shut_down_df = (
    facility_surface_shut_down_df.groupby(
        ["facility_belongs_to_name", "facility_startup_date"]
    )[encoded_columns]
    .sum()
    .reset_index()
)

# Cumulative sum of the one hot encoded columns
facility_surface_shut_down_df[encoded_columns] = facility_surface_shut_down_df.groupby(
    "facility_belongs_to_name"
)[encoded_columns].cumsum()
facility_surface_shut_down_df

# Calculate the mean and std water_depth for each facility_belongs_to_name and year combo

facility_water_depth_per_field = (
    facilities_in_service.groupby(["facility_belongs_to_name"])["facility_water_depth"]
    .agg(["mean", "std"])
    .reset_index()
)

# If std is NaN, set it to 0
facility_water_depth_per_field["std"].fillna(0, inplace=True)

facility_water_depth_per_field

# Calculate the mean and std facility_design_lifetime for each facility_belongs_to_name and year combo

facility_design_lifetime_per_field = (
    facilities_in_service.groupby(["facility_belongs_to_name"])[
        "facility_design_lifetime"
    ]
    .agg(["mean", "std"])
    .reset_index()
)

# If std is NaN, set it to 0
facility_design_lifetime_per_field["std"].fillna(0, inplace=True)

facility_design_lifetime_per_field

# Adding the facility_design_lifetime_per_field to the fields_yearly_df

fields_yearly_with_facilites_df = fields_yearly_df.merge(
    facility_design_lifetime_per_field,
    left_on=["field"],
    right_on=["facility_belongs_to_name"],
    how="left",
)

# Renaming the mean and std to lifetime_mean and lifetime_std
fields_yearly_with_facilites_df = fields_yearly_with_facilites_df.rename(
    columns={"mean": "facilities_lifetime_mean", "std": "facilities_lifetime_std"}
)

fields_yearly_with_facilites_df

# Adding the facility_water_depth_per_field to the fields_yearly_with_facilites_df

fields_yearly_with_facilites_df = fields_yearly_with_facilites_df.merge(
    facility_water_depth_per_field,
    left_on=["field"],
    right_on=["facility_belongs_to_name"],
    how="left",
)

# Renaming the mean and std to water_depth_mean and water_depth_std
fields_yearly_with_facilites_df = fields_yearly_with_facilites_df.rename(
    columns={"mean": "facilities_water_depth_mean", "std": "facilities_water_depth_std"}
)

# Renaming facility_belongs_to_name_y to facility_belongs_to_name and removing facility_belongs_to_name_y
fields_yearly_with_facilites_df = fields_yearly_with_facilites_df.rename(
    columns={"facility_belongs_to_name_y": "facility_belongs_to_name"}
)
fields_yearly_with_facilites_df = fields_yearly_with_facilites_df.drop(
    columns="facility_belongs_to_name_x"
)

fields_yearly_with_facilites_df

facility_surface_shut_down_df

fields_and_facilites_df = fields_yearly_with_facilites_df.copy()

# Adding facility_surface_shut_down_df, facility_surface_in_service_df, facility_kind_in_service_df, facility_kind_shut_down_df to fields_and_facilites_df
fields_and_facilites_df = fields_and_facilites_df.merge(
    facility_surface_shut_down_df,
    left_on=["field", "year"],
    right_on=["facility_belongs_to_name", "facility_startup_date"],
    how="left",
)
fields_and_facilites_df = fields_and_facilites_df.rename(
    columns={"Y": "surface_facilites_shut_down", "N": "subsea_facilites_shut_down"}
)

fields_and_facilites_df = fields_and_facilites_df.merge(
    facility_surface_in_service_df,
    left_on=["field", "year"],
    right_on=["facility_belongs_to_name", "facility_startup_date"],
    how="left",
)
fields_and_facilites_df = fields_and_facilites_df.rename(
    columns={"Y": "surface_facilites_in_service", "N": "subsea_facilites_in_service"}
)

# facility_kind_in_service_df
# Adding facility_kind_ to the names of the columns of facility_kind_in_service_df and making them lower case
fields_and_facilites_df = fields_and_facilites_df.merge(
    facility_kind_in_service_df,
    left_on=["field", "year"],
    right_on=["field", "year"],
    how="left",
)

# Cleaning by removing uneccessary columns: facility_startup_date_y, facility_belongs_to_name, facility_startup_date_x, facility_belongs_to_name_y, facility_belongs_to_name_x
fields_and_facilites_df = fields_and_facilites_df.drop(
    columns=[
        "facility_startup_date_y",
        "facility_belongs_to_name",
        "facility_startup_date_x",
        "facility_belongs_to_name_y",
        "facility_belongs_to_name_x",
    ]
)
fields_and_facilites_df

# Facility kinds
facility_kind_columns = [
    col for col in fields_and_facilites_df.columns if "facility_kind_" in col
]
cols_to_make_zero = [
    "subsea_facilites_shut_down",
    "surface_facilites_shut_down",
    "subsea_facilites_in_service",
    "surface_facilites_in_service",
]

# Filling NaNs
fields_and_facilites_df[facility_kind_columns] = fields_and_facilites_df[
    facility_kind_columns
].fillna(0)
fields_and_facilites_df[cols_to_make_zero] = fields_and_facilites_df[
    cols_to_make_zero
].fillna(0)

# Cumatively sum all the facility kinds per field

for column in facility_kind_columns:
    fields_and_facilites_df[column] = fields_and_facilites_df.groupby("field")[
        column
    ].cumsum()

# Cumatively sum subsea_facilites_in_service and surface_facilites_in_service
fields_and_facilites_df["surface_facilites_in_service"] = (
    fields_and_facilites_df.groupby("field")["surface_facilites_in_service"].cumsum()
)
fields_and_facilites_df["subsea_facilites_in_service"] = (
    fields_and_facilites_df.groupby("field")["subsea_facilites_in_service"].cumsum()
)


fields_and_facilites_df

# Checking the df
display(wellbores_df.head())

# Checking unique  wlbStatus, wlbPurpose, wlbSubSea, and the value counts for each

# wlbFinalVerticalDepth, wlbTotalDepth, wlbWaterDepth

display(wellbores_df["wlbStatus"].unique())
display(wellbores_df["wlbPurpose"].unique())
display(wellbores_df["wlbSubSea"].unique())

# Removing all rows where wlbPurpose = nan and 'NOT AVAILABLE'
wellbores_df = wellbores_df[wellbores_df["wlbStatus"].notna()]

# Removing all rows where
wellbores_df = wellbores_df[wellbores_df["wlbPurpose"].notna()]
wellbores_df = wellbores_df[wellbores_df["wlbPurpose"] != "NOT AVAILABLE"]

wellbores_df = wellbores_df[wellbores_df["wlbField"].notna()]

# Keeping only the following columns: wlbField, wlbStatus, wlbPurpose, wlbSubSea, wlbFinalVerticalDepth, wlbTotalDepth, wlbWaterDepth

wellbores_smaller_df = wellbores_df[
    [
        "wlbField",
        "wlbStatus",
        "wlbPurpose",
        "wlbSubSea",
        "wlbFinalVerticalDepth",
        "wlbWaterDepth",
        "wlbEntryYear",
        "wlbCompletionYear",
        "wlbPluggedAbandonDate",
        "wlbPluggedDate",
    ]
].copy()
wellbores_smaller_df

# Making field lower case
wellbores_smaller_df["wlbField"] = wellbores_smaller_df["wlbField"].str.lower()

# removing wlb from all column names
wellbores_smaller_df.columns = wellbores_smaller_df.columns.str.replace("wlb", "well_")

# making all column names lower case
wellbores_smaller_df.columns = wellbores_smaller_df.columns.str.lower()

# Filtering out well_entry_year before 1990 and after 2023
wellbores_smaller_df = wellbores_smaller_df[
    (wellbores_smaller_df["well_entryyear"] >= 1990)
    & (wellbores_smaller_df["well_entryyear"] <= 2023)
]

wellbores_smaller_df

# Removing trailing whitespace from the well_subsea column
wellbores_smaller_df["well_subsea"] = wellbores_smaller_df["well_subsea"].str.strip()

# Getting dummies for well_status, well_purpose, and well_subsea
wellbores_calc_df = wellbores_smaller_df.copy()

well_status_df = pd.get_dummies(wellbores_smaller_df, columns=["well_status"])
well_purpose_df = pd.get_dummies(wellbores_smaller_df, columns=["well_purpose"])
well_subsea_df = pd.get_dummies(wellbores_smaller_df, columns=["well_subsea"])

# Make all columns lower case
well_status_df.columns = well_status_df.columns.str.lower()
well_purpose_df.columns = well_purpose_df.columns.str.lower()
well_subsea_df.columns = well_subsea_df.columns.str.lower()

well_status_cols = [col for col in well_status_df.columns if "well_status" in col]
well_purpose_cols = [col for col in well_purpose_df.columns if "well_purpose" in col]
well_subsea_cols = [col for col in well_subsea_df.columns if "well_subsea" in col]

# Cumulative sum of the one hot encoded columns
well_status_df = (
    well_status_df.groupby(["well_field", "well_entryyear"])[well_status_cols]
    .sum()
    .reset_index()
)
well_purpose_df = (
    well_purpose_df.groupby(["well_field", "well_entryyear"])[well_purpose_cols]
    .sum()
    .reset_index()
)
well_subsea_df = (
    well_subsea_df.groupby(["well_field", "well_entryyear"])[well_subsea_cols]
    .sum()
    .reset_index()
)

# Cumalitve sum of all the three one hot encoded columns
for column in well_status_cols:
    well_status_df[column] = well_status_df.groupby("well_field")[column].cumsum()

for column in well_purpose_cols:
    well_purpose_df[column] = well_purpose_df.groupby("well_field")[column].cumsum()

for column in well_subsea_cols:
    well_subsea_df[column] = well_subsea_df.groupby("well_field")[column].cumsum()


display(well_status_df.head())
display(well_purpose_df.head())
display(well_subsea_df.head())

# Merging the well_status_df, well_purpose_df, well_subsea_df to the fields_and_facilites_df without adding the well_entryyear and well_field columns

fields_facilites_wells_df = fields_and_facilites_df.copy()

fields_facilites_wells_df = fields_facilites_wells_df.merge(
    well_status_df,
    left_on=["field", "year"],
    right_on=["well_field", "well_entryyear"],
    how="left",
)
fields_facilites_wells_df = fields_facilites_wells_df.drop(
    columns=["well_field", "well_entryyear"]
)

fields_facilites_wells_df = fields_facilites_wells_df.merge(
    well_purpose_df,
    left_on=["field", "year"],
    right_on=["well_field", "well_entryyear"],
    how="left",
)
fields_facilites_wells_df = fields_facilites_wells_df.drop(
    columns=["well_field", "well_entryyear"]
)

fields_facilites_wells_df = fields_facilites_wells_df.merge(
    well_subsea_df,
    left_on=["field", "year"],
    right_on=["well_field", "well_entryyear"],
    how="left",
)
fields_facilites_wells_df = fields_facilites_wells_df.drop(
    columns=["well_field", "well_entryyear"]
)

fields_facilites_wells_df

# Replacing NaNs with 0 for the new columns

fields_facilites_wells_df[well_status_cols] = fields_facilites_wells_df[
    well_status_cols
].fillna(0)
fields_facilites_wells_df[well_purpose_cols] = fields_facilites_wells_df[
    well_purpose_cols
].fillna(0)
fields_facilites_wells_df[well_subsea_cols] = fields_facilites_wells_df[
    well_subsea_cols
].fillna(0)

# Cumulatively sum the columns

for column in well_status_cols:
    fields_facilites_wells_df[column] = fields_facilites_wells_df.groupby("field")[
        column
    ].cumsum()

for column in well_purpose_cols:
    fields_facilites_wells_df[column] = fields_facilites_wells_df.groupby("field")[
        column
    ].cumsum()

for column in well_subsea_cols:
    fields_facilites_wells_df[column] = fields_facilites_wells_df.groupby("field")[
        column
    ].cumsum()

fields_facilites_wells_df

# Calculating the mean and std well_finalverticaldepth and well_waterdepth grouped by well_field and well_entryyear

well_finalverticaldepth_df = (
    wellbores_smaller_df.groupby(["well_field", "well_entryyear"])[
        "well_finalverticaldepth"
    ]
    .agg(["mean", "std"])
    .reset_index()
)
well_waterdepth_df = (
    wellbores_smaller_df.groupby(["well_field", "well_entryyear"])["well_waterdepth"]
    .agg(["mean", "std"])
    .reset_index()
)

# If std is NaN, set it to 0
well_finalverticaldepth_df["std"].fillna(0, inplace=True)
well_waterdepth_df["std"].fillna(0, inplace=True)

# Ranaming columns, adding well_final_vertical_depth_mean and well_final_vertical_depth_std to the well_finalverticaldepth_df
well_finalverticaldepth_df = well_finalverticaldepth_df.rename(
    columns={
        "mean": "well_final_vertical_depth_mean",
        "std": "well_final_vertical_depth_std",
    }
)

# Ranaming columns, adding well_water_depth_mean and well_water_depth_std to the well_waterdepth_df
well_waterdepth_df = well_waterdepth_df.rename(
    columns={"mean": "well_water_depth_mean", "std": "well_water_depth_std"}
)

display(well_finalverticaldepth_df)
display(well_waterdepth_df)

# Merging into fields_facilites_wells_df

fields_facilites_wells_df = fields_facilites_wells_df.merge(
    well_finalverticaldepth_df,
    left_on=["field", "year"],
    right_on=["well_field", "well_entryyear"],
    how="left",
)
fields_facilites_wells_df = fields_facilites_wells_df.drop(
    columns=["well_field", "well_entryyear"]
)

fields_facilites_wells_df = fields_facilites_wells_df.merge(
    well_waterdepth_df,
    left_on=["field", "year"],
    right_on=["well_field", "well_entryyear"],
    how="left",
)
fields_facilites_wells_df = fields_facilites_wells_df.drop(
    columns=["well_field", "well_entryyear"]
)

fields_facilites_wells_calc_df = fields_facilites_wells_df.copy()

well_data_cols = [
    "well_final_vertical_depth_mean",
    "well_final_vertical_depth_std",
    "well_water_depth_mean",
    "well_water_depth_std",
]

# Forward filling the NaNs in the new columns
fields_facilites_wells_calc_df[well_data_cols] = fields_facilites_wells_calc_df[
    well_data_cols
].ffill()

latest_merged = fields_facilites_wells_calc_df.copy()

investments_df = investments_df.rename(
    columns={
        "prfInformationCarrier": "field",
        "prfYear": "year",
        "prfInvestmentsMillNOK": "investments_mill_nok",
        "prfNpdidInformationCarrier": "field_id",
    }
)

# Removing investments with year before 1990 and after 2023
investments_df = investments_df[
    (investments_df["year"] >= 1990) & (investments_df["year"] <= 2023)
]

# converting field to lower case
investments_df["field"] = investments_df["field"].str.lower()
investments_df.head()

future_investments_df.head()

future_investments_df = future_investments_df.rename(
    columns={
        "fldName": "field",
        "prfYear": "year",
        "fldInvestmentExpected": "future_investments_mill_nok",
        "prfNpdidInformationCarrier": "field_id",
    }
)

# Convert field to lower case
future_investments_df["field"] = future_investments_df["field"].str.lower()

# dropping fldInvExpFixYear and fldNpdidField
future_investments_df.drop(columns=["fldInvExpFixYear", "fldNpdidField"], inplace=True)

future_investments_df.head()

# Adding the future_investments_mill_nok to the investments_df
investments_merged_df = investments_df.merge(
    future_investments_df[["field", "future_investments_mill_nok"]],
    on=["field"],
    how="left",
)
investments_merged_df

# Setting all NaN in future_investments_mill_nok to 0

investments_merged_df["future_investments_mill_nok"] = investments_merged_df[
    "future_investments_mill_nok"
].fillna(0)

# Dropping dateSyncNPD and field_id column
investments_merged_df.drop(columns=["dateSyncNPD", "field_id"], inplace=True)

investments_merged_df

# Merging investments_merged into latest_merged

field_facility_well_investment_df = latest_merged.merge(
    investments_merged_df, on=["field", "year"], how="left"
)

# Removing all rows after 2023
field_facility_well_investment_df = field_facility_well_investment_df[
    field_facility_well_investment_df["year"] <= 2023
]
field_facility_well_investment_df[
    field_facility_well_investment_df["future_investments_mill_nok"].isna()
]

field_facility_well_investment_df.head()

licensees_df.head()

# Renaming columns: fldName to field, cmpLongName to old_company_name, fldCompanyShare to company_share

licensees_df = licensees_df.rename(
    columns={
        "fldName": "field",
        "cmpLongName": "old_company_name",
        "fldCompanyShare": "company_share",
        "fldNpdidField": "field_id",
        "cmpNpdidCompany": "company_id",
    }
)

# Making field lower case
licensees_df["field"] = licensees_df["field"].str.lower()
display(licensees_df.shape)

# Only keeping the fields that are in field_facility_well_investment_df 1997-2023

field_facility_well_investment_df_1997_2023 = field_facility_well_investment_df[
    (field_facility_well_investment_df["year"] >= 1997)
    & (field_facility_well_investment_df["year"] <= 2023)
]
field_licensees_df = licensees_df[
    licensees_df["field"].isin(field_facility_well_investment_df_1997_2023["field"])
]
display(field_licensees_df.head())
display(field_licensees_df.shape)
display(field_licensees_df.old_company_name.nunique())

# Converting fldOwnerFrom and fldLicenseeFrom to datetime

field_licensees_df["fldOwnerFrom"] = pd.to_datetime(
    field_licensees_df["fldOwnerFrom"], format="%d.%m.%Y"
)
field_licensees_df["fldLicenseeFrom"] = pd.to_datetime(
    field_licensees_df["fldLicenseeFrom"], format="%d.%m.%Y"
)

# field_licensees_df between 1997-2023

field_licensees_df_1997_2023 = field_licensees_df[
    (field_licensees_df["fldLicenseeFrom"].dt.year >= 1997)
    & (field_licensees_df["fldLicenseeFrom"].dt.year <= 2023)
]
display(field_licensees_df_1997_2023.old_company_name.nunique())
display(field_licensees_df_1997_2023.shape)

# Checking all unique old_company_name

display(field_licensees_df_1997_2023.old_company_name.nunique())
display(field_licensees_df_1997_2023.old_company_name.unique())

# Creating a a copy of old_company_name and calling it new_company_name
field_licensees_df_1997_2023["new_company_name"] = field_licensees_df_1997_2023[
    "old_company_name"
]

# Define the replacement operator
def replace_operator(name, name_contains, replacement):
    if name_contains.lower() in name.lower():
        return replacement
    return name

# Define the replacements as a list of tuples (substring, replacement)
name_replacements = [
    # BP
    ("det norske oljeselskap", "Aker BP"),
    ("det norske exploration as", "Aker BP"),
    ("aker", "Aker BP"),
    ("bp norge", "Aker BP"),
    ("Marathon", "Aker BP"),
    ("Pertra ASA", "Aker BP"),
    ("Pertra AS", "Aker BP"),
    ("Hess", "Aker BP"),
    ("ABP Norway AS", "Aker BP"),
    ("bp", "Aker BP"),
    ("lundin", "Aker BP"),
    # Equinor
    ("statoil", "Equinor ASA"),
    ("equinor", "Equinor ASA"),
    ("den norske stats oljeselskap", "Equinor ASA"),
    ("Saga Petroleum ASA", "Equinor ASA"),
    # CapeOmega
    ("capeomega", "CapeOmega AS"),
    ("Norwegian Energy Company ASA", "CapeOmega AS"),
    # Concedo
    ("concedo", "Concedo ASA"),
    # ConocoPhillips
    ("conoco", "ConocoPhillips"),
    ("phillips", "ConocoPhillips"),
    ("Conoco Phillips", "ConocoPhillips"),
    # Kuwait Petroleum Company
    ("AEDC", "Kuwait Petroleum Company"),
    ("KUFPEC", "Kuwait Petroleum Company"),
    # DNO
    ("dno", "DNO ASA"),
    ("faroe petroleum", "DNO ASA"),
    # Harbour Energy
    ("chrysaor", "Harbour Energy"),
    # Lime Petroleum
    ("lime", "Lime Petroleum"),
    # Neptune
    ("VNG", "Neptune Energy Norge AS"),
    ("ENGIE E&P Norge AS", "Neptune Energy Norge AS"),
    ("GDF SUEZ E&P Norge AS", "Neptune Energy Norge AS"),
    ("neptune", "Neptune Energy Norge AS"),
    # Okea
    ("okea", "OKEA ASA"),
    # Pandion Energy
    ("one-dyas", "Pandion Energy"),
    ("tullow", "Pandion Energy"),
    # Petoro
    ("statens direkte økonomiske engasjement sdøe", "Petoro AS"),
    # PGniG
    ("PGNiG", "PGNiG"),
    ("Pelican", "PGNiG"),
    ("dong", "PGNiG"),
    ("ineos", "PGNiG"),
    # Shell
    ("enterprise oil norwegian as", "Shell"),
    ("BG Norge AS", "Shell"),
    ("Enterprise Oil Norge AS", "Shell"),
    # Repsol
    ("repsol", "Repsol"),
    ("talisman", "Repsol"),
    ("Oryx (UK) Energy Company", "Repsol"),
    ("paladin", "Repsol"),
    # Sval Energi
    ("sval", "Sval Energi AS"),
    ("capricorn", "Sval Energi AS"),
    ("bayern", "Sval Energi AS"),
    ("spirit", "Sval Energi AS"),
    ("centrica", "Sval Energi AS"),
    ("pa resources", "Sval Energi AS"),
    ("suncor", "Sval Energi AS"),
    ("petro canada", "Sval Energi AS"),
    ("petro-canada", "Sval Energi AS"),
    # TotalEnergies EP Norge
    ("Total", "TotalEnergies EP Norge"),
    ("Totalfinaelf", "TotalEnergies EP Norge"),
    ("Fina Production Licenses AS", "TotalEnergies EP Norge"),
    ("Fina", "TotalEnergies EP Norge"),
    ("Elf Rex Norge AS", "TotalEnergies EP Norge"),
    ("Elf", "TotalEnergies EP Norge"),
    ("Kerr Mc-Gee North Sea (UK) Ltd", "TotalEnergies EP Norge"),
    ("Maersk Oil UK Limited", "TotalEnergies EP Norge"),
    # Vår Energi
    ("vår energi", "Vår Energi AS"),
    ("eni", "Vår Energi AS"),
    ("exxon", "Vår Energi AS"),
    ("Norsk Agip AS", "Vår Energi AS"),
    # Wintershall Dea
    ("Wintershall Norge AS", "Wintershall Dea Norge AS"),
    ("RWE Dea Norge AS", "Wintershall Dea Norge AS"),
    ("Norske RWE-DEA AS", "Wintershall Dea Norge AS"),
    ("E.ON", "Wintershall Dea Norge AS"),
    ("Dea E&P Norge AS", "Wintershall Dea Norge AS"),
    ("DEA Norge AS", "Wintershall Dea Norge AS"),
    # Misc
    ("hydro", "Norsk Hydro ASA"),
    ("Chevron", "Chevron"),
    ("pgs", "PGS"),
    ("Revus", "Revus Energy AS"),
    ("Harbour", "Harbour Energy"),
]

# Apply the replacements
for name_contains, replacement in name_replacements:
    field_licensees_df_1997_2023["new_company_name"] = field_licensees_df_1997_2023[
        "new_company_name"
    ].apply(lambda name: replace_operator(name, name_contains, replacement))

# Check the unique values of new_company_name

display(field_licensees_df_1997_2023.new_company_name.nunique())
display(field_licensees_df_1997_2023.new_company_name.unique())

field_licensees_df_1997_2023.head()

# Group by year
field_licensees_grouped_old_names = (
    field_licensees_df_1997_2023.groupby(["field", "fldLicenseeFrom", "company_share"])[
        "old_company_name"
    ]
    .apply(list)
    .reset_index()
)
field_licensees_grouped_new_names = (
    field_licensees_df_1997_2023.groupby(["field", "fldLicenseeFrom", "company_share"])[
        "new_company_name"
    ]
    .apply(list)
    .reset_index()
)

display(field_licensees_grouped_old_names)
display(field_licensees_grouped_new_names)

# Get the latest licensee for each field
latest_licensee = field_licensees_grouped.groupby("field").last().reset_index()
latest_licensee

display(emissions_df.head())
display(len(emissions_df.field.unique()))
display(emissions_df.describe())

# Merging field_facility_well_investment_df with emissions_df

field_emissions_df = field_facility_well_investment_df.merge(
    emissions_df, on=["field", "year"], how="left"
)
field_emissions_df.head()

fields_prod_emissions_1997_2023_df = field_emissions_df[
    (field_emissions_df["year"] >= 1997) & (field_emissions_df["year"] <= 2023)
]

fields_prod_emissions_1997_2023_df.head()

field_overview_df

latest_licensee

field_licensees_df_1997_2023

from collections import defaultdict

# Convert to DataFrame
ownership_df = field_licensees_df_1997_2023.copy()
big_df = fields_prod_emissions_1997_2023_df.copy()

# Ensure date columns are in datetime format
ownership_df["fldLicenseeFrom"] = pd.to_datetime(ownership_df["fldLicenseeFrom"])
big_df["date"] = pd.to_datetime(big_df["year"].astype(str) + "-01-01")

# Create a dictionary to hold ownership information
ownership_dict = defaultdict(list)

for idx, row in ownership_df.iterrows():
    ownership_dict[(row["field"], row["fldLicenseeFrom"])].append(
        (row["old_company_name"], row["company_share"])
    )

# Create a new dataframe with the aggregated ownership information
aggregated_ownership = []

for (field, date), owners in ownership_dict.items():
    aggregated_ownership.append(
        {
            "field": field,
            "date": date,
            "ownership_original": {owner: share for owner, share in owners},
        }
    )

aggregated_ownership_df = pd.DataFrame(aggregated_ownership)

# Merge the aggregated ownership information with the main dataframe
merged_dict_df = pd.merge_asof(
    big_df.sort_values("date"),
    aggregated_ownership_df.sort_values("date"),
    by="field",
    left_on="date",
    right_on="date",
    direction="nearest",
)

# Drop the extra 'date' column used for merging
merged_dict_df.drop(columns=["date"], inplace=True)

# Display the merged dataframe
merged_dict_df

# Ensure date columns are in datetime format
ownership_df["fldLicenseeFrom"] = pd.to_datetime(ownership_df["fldLicenseeFrom"])
merged_dict_df["date"] = pd.to_datetime(merged_dict_df["year"].astype(str) + "-01-01")

# Create a dictionary to hold ownership information
ownership_dict = defaultdict(list)

for idx, row in ownership_df.iterrows():
    ownership_dict[(row["field"], row["fldLicenseeFrom"])].append(
        (row["new_company_name"], row["company_share"])
    )

# Create a new dataframe with the aggregated ownership information
aggregated_ownership = []

for (field, date), owners in ownership_dict.items():
    aggregated_ownership.append(
        {
            "field": field,
            "date": date,
            "ownership_new_name": {owner: share for owner, share in owners},
        }
    )

aggregated_ownership_df = pd.DataFrame(aggregated_ownership)

# Merge the aggregated ownership information with the main dataframe
merged_dict_df = pd.merge_asof(
    merged_dict_df.sort_values("date"),
    aggregated_ownership_df.sort_values("date"),
    by="field",
    left_on="date",
    right_on="date",
    direction="nearest",
)

# Drop the extra 'date' column used for merging
merged_dict_df.drop(columns=["date"], inplace=True)

# Display the merged dataframe
merged_dict_df

# Rename fldName to field, fldDateOffResEstDisplay to dt year showing year

field_reserves_original_df = field_reserves_df.copy()
field_reserves_df = field_reserves_df.rename(
    columns={"fldName": "field", "fldDateOffResEstDisplay": "dt_year"}
)

# Making fields lower case
field_reserves_df["field"] = field_reserves_df["field"].str.lower()

# Rename fldRecoverableOil, fldRecoverableGas, fldRecoverableNGL, fldRecoverableCondensate, fldRecoverableOE to original_recoverable_oil, original_recoverable_gas, original_recoverable_ngl, original_recoverable_condensate, original_recoverable_oe

field_reserves_df = field_reserves_df.rename(
    columns={
        "fldRecoverableOil": "original_recoverable_oil",
        "fldRecoverableGas": "original_recoverable_gas",
        "fldRecoverableNGL": "original_recoverable_ngl",
        "fldRecoverableCondensate": "original_recoverable_condensate",
        "fldRecoverableOE": "original_recoverable_oe",
    }
)

field_reserves_df.head()

# Convert dy_year to show only year

field_reserves_df["dt_year"] = pd.to_datetime(field_reserves_df["dt_year"]).dt.year

# Rename fldRemainingOil	fldRemainingGas	fldRemainingNGL	fldRemainingCondensate to remaining_recoverable_oil	remaining_recoverable_gas	remaining_recoverable_ngl	remaining_recoverable_condensate

field_reserves_df = field_reserves_df.rename(
    columns={
        "fldRemainingOil": "current_remaining_recoverable_oil",
        "fldRemainingGas": "current_remaining_recoverable_gas",
        "fldRemainingNGL": "current_remaining_recoverable_ngl",
        "fldRemainingCondensate": "current_remaining_recoverable_condensate",
        "fldRemainingOE": "current_remaining_recoverable_oe",
    }
)
field_reserves_df.head()

# rename fldRemainingOE to remaining_recoverable_oe

# Columns containing 'current' and 'original'
current_columns = [col for col in field_reserves_df.columns if "current" in col]
original_columns = [col for col in field_reserves_df.columns if "original" in col]


field_original_current_reserves_df = field_reserves_df[
    ["field"] + current_columns + original_columns
].copy()
field_original_current_reserves_df.head()

# Merging field_original_reserves_df with fields_prod_emissions_1997_2023_df

final_merged_df = merged_dict_df.merge(
    field_original_current_reserves_df, on=["field"], how="left"
)
final_merged_df.head()

# Checking if file ../../data/output/emissions_and_production/cleaned/fields_prod_emissions_1997_2023.csv exists

final_output = "../../data/output/emissions_and_production/cleaned/fields_prod_emissions_1997_2023.csv"

if not os.path.exists(final_output):
    final_merged_df.to_csv(final_output, index=False)
    print("Saved file")
else:
    print("File already exists")

# Inserting watermark of environment and package versions used

# %load_ext watermark

# %watermark -a "Per Christian Wessel" -d -u -v -m -p pandas,numpy,scipy,matplotlib

