# This script was automatically extracted from a Jupyter Notebook.

# Required Libraries
import lime
import lime.lime_tabular
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
from doubleml import DoubleMLData, DoubleMLPLR
from doubleml.datasets import fetch_bonus
from linearmodels.panel import PanelOLS
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression, RidgeCV
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from statsmodels.formula.api import ols
from statsmodels.stats.outliers_influence import variance_inflation_factor
from xgboost import XGBRegressor

pd.set_option("display.max_columns", None)


# Define a function for calculating root mean squared error
def root_mean_squared_error(y_true, y_pred):
    return np.sqrt(mean_squared_error(y_true, y_pred))

# Importing the dataset from the csv file
filepath = "https://raw.githubusercontent.com/percw/Norwegian_oil_gas_decarbonization/main/data/output/emissions_and_production/cleaned/fields_prod_emissions_intensities_share_1997_2023.csv"

# Creating a check if import is successful
try:
    data = pd.read_csv(filepath, sep=",")
    print("Data import successful")
except:
    print("Data import failed")

data.head(5)

data[data["field"] == "troll"]

# Rename "kgco2e/toe_int_gwp100" to "emission_intensity" and "share_intensity_tco2e/toe_gwp100" to "emission_intensity_distributed"

data = data.rename(
    columns={
        "share_intensity_tco2e/toe_gwp100": "emission_intensity_distributed",
        "kgco2e/toe_int_gwp100": "emission_intensity",
    }
)

# Year is %Y datetime
data["year"] = pd.to_datetime(data["year"], format="%Y")

# Get emission tons
data["yearly_tco2_emissions"] = data["yearly_co2_emissions_1000_tonnes"] * 1000

# Remove nans, inf and -inf
# data = data.replace([np.inf, -np.inf], np.nan).dropna()

dependent_vars = [
    "emission_intensity",
    "emission_intensity_distributed",
    "yearly_tco2e_gwp100",
    "yearly_tco2e_prod_share_emissions",
]

# Define the control variables
control_vars = [
    "net_oil_eq_prod_yearly_mill_sm3",
    "share_reserve_of_original_reserve",
    # "net_oil_prod_yearly_mill_sm3",    # Removed: P-value increased
    # "net_gas_prod_yearly_bill_sm3",    # Removed: P-value increased
    # "share_peak_prod",                 # Removed: P-value increased
    # "original_recoverable_ngl",        # Removed: Fully absorbed
    # "original_recoverable_oe",         # Removed: Fully absorbed
]

# Step 1: Select only the necessary columns for the analysis
columns_needed = ["field_id", "year", "electrified"] + dependent_vars + control_vars
twfe_data = data[columns_needed].copy()

# Convert the 'year' column to a proper integer year if it contains timestamps
twfe_data["year"] = pd.to_datetime(twfe_data["year"], unit="ns").dt.year

# Ensure the 'year' column is of integer type
twfe_data["year"] = twfe_data["year"].astype(int)

# Step 2: Ensure no NaN values are present in the dependent variables or control variables
twfe_data = twfe_data.dropna(subset=dependent_vars + control_vars)

# Step 3: Create year dummies
year_dummies = pd.get_dummies(twfe_data["year"], prefix="year", drop_first=True)
twfe_data = pd.concat([twfe_data, year_dummies], axis=1)

# Step 4: Set the index to a MultiIndex (field_id, year) for panel data analysis
twfe_data = twfe_data.set_index(["field_id", "year"])


# Step 5: Function to perform Two Way Fixed Effects for a given dependent variable
def twfe_model(dependent_var, data, controls=None):
    year_cols = " + ".join(year_dummies.columns)
    formula = f"{dependent_var} ~ electrified + {year_cols} + EntityEffects"
    if controls:
        control_cols = " + ".join(controls)
        formula = f"{dependent_var} ~ electrified + {control_cols} + {year_cols} + EntityEffects"

    # Fit the Two Way Fixed Effects model
    model = PanelOLS.from_formula(formula, data, drop_absorbed=True).fit(
        cov_type="clustered", cluster_entity=True
    )

    return model


# Perform Two Way Fixed Effects model for each dependent variable without controls
results_no_controls = {}
for var in dependent_vars:
    model = twfe_model(var, twfe_data)
    if model is not None:
        non_treated_mean = twfe_data.loc[twfe_data["electrified"] == 0, var].mean()
        treatment_coefficient = model.params["electrified"]
        percentage_change = (treatment_coefficient / non_treated_mean) * 100

        results_no_controls[var] = {
            "model": model,
            "summary": model.summary,
            "coef": treatment_coefficient,
            "conf_int_lower": model.conf_int().loc["electrified"][0],
            "conf_int_upper": model.conf_int().loc["electrified"][1],
            "p_value": model.pvalues["electrified"],
            "non_treated_mean": non_treated_mean,
            "percentage_change": percentage_change,
        }

# Perform Two Way Fixed Effects model for each dependent variable with controls
results_with_controls = {}
for var in dependent_vars:
    model = twfe_model(var, twfe_data, controls=control_vars)
    if model is not None:
        non_treated_mean = twfe_data.loc[twfe_data["electrified"] == 0, var].mean()
        treatment_coefficient = model.params["electrified"]
        percentage_change = (treatment_coefficient / non_treated_mean) * 100

        results_with_controls[var] = {
            "model": model,
            "summary": model.summary,
            "coef": treatment_coefficient,
            "conf_int_lower": model.conf_int().loc["electrified"][0],
            "conf_int_upper": model.conf_int().loc["electrified"][1],
            "p_value": model.pvalues["electrified"],
            "non_treated_mean": non_treated_mean,
            "percentage_change": percentage_change,
        }

# Create summary tables for actual treatment effects
summary_table_no_controls = pd.DataFrame(results_no_controls).T
summary_table_no_controls = summary_table_no_controls[
    [
        "coef",
        "conf_int_lower",
        "conf_int_upper",
        "p_value",
        "non_treated_mean",
        "percentage_change",
    ]
]
summary_table_no_controls.columns = [
    "Coefficient",
    "CI Lower",
    "CI Upper",
    "P-value",
    "Non-treated Mean",
    "Percentage Change",
]

summary_table_with_controls = pd.DataFrame(results_with_controls).T
summary_table_with_controls = summary_table_with_controls[
    [
        "coef",
        "conf_int_lower",
        "conf_int_upper",
        "p_value",
        "non_treated_mean",
        "percentage_change",
    ]
]
summary_table_with_controls.columns = [
    "Coefficient",
    "CI Lower",
    "CI Upper",
    "P-value",
    "Non-treated Mean",
    "Percentage Change",
]

# Create a combined summary table
combined_summary = summary_table_no_controls.copy()
combined_summary["Coef (with controls)"] = summary_table_with_controls["Coefficient"]
combined_summary["CI Lower (with controls)"] = summary_table_with_controls["CI Lower"]
combined_summary["CI Upper (with controls)"] = summary_table_with_controls["CI Upper"]
combined_summary["P-value (with controls)"] = summary_table_with_controls["P-value"]
combined_summary["Percentage Change (with controls)"] = summary_table_with_controls[
    "Percentage Change"
]

print("\n\nComparison of TWFE Model Results without and with Controls:")
display(combined_summary)

# Get the summary for emission_intensity_distributed
results_with_controls["emission_intensity_distributed"]["summary"]

# Set random seeds for reproducibility
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import PolynomialFeatures


random_seed = 42

# Copy the data for DML
data_dml_1 = data.copy()

# Remove fields with negative share_reserve_of_original_reserve
data_dml_1 = data_dml_1[data_dml_1["share_reserve_of_original_reserve"] >= 0]

# Generate the required variables
data_dml_1["processing_field_bin"] = (
    data_dml_1["processing_field"] == data_dml_1["field"]
).astype(float)

# Create dummy variables for operator
field_owner_dummies = pd.get_dummies(data_dml_1["operator"], prefix="operator")
data_dml_1 = pd.concat([data_dml_1, field_owner_dummies], axis=1)

# Define the list of outcomes
outcomes = ["emission_intensity_distributed", "yearly_tco2e_prod_share_emissions"]

# Define the treatment and control variables
D = "share_reserve_of_original_reserve"
X = (
    ["investments_mill_nok", "electrified"]
    + [col for col in data_dml_1.columns if col.startswith("facilities")]
    + [col for col in data_dml_1.columns if col.startswith("subsea_facilites")]
    + [col for col in data_dml_1.columns if col.startswith("surface_")]
    + [col for col in data_dml_1.columns if col.startswith("facility_kind")]
    + [col for col in data_dml_1.columns if col.startswith("well_status")]
    + [col for col in data_dml_1.columns if col.startswith("well_purpose")]
)

# Initialize a dictionary to store the summary statistics
dml_summary_stats = {}

# Iterate over the list of outcomes
for Y in outcomes:
    # Drop rows with NaN values in the relevant columns
    data_dml_1_clean = data_dml_1.dropna(subset=[Y, D] + X)

    # Initialize DoubleMLData object
    dml_data = DoubleMLData(data_dml_1_clean, Y, D, X)

    # Initialize DoubleMLPLR model with different models
    dml_plr = DoubleMLPLR(
        dml_data,
        ml_g=GradientBoostingRegressor(random_state=random_seed),
        ml_m=XGBRegressor(random_state=random_seed),
        ml_l=LinearRegression(),
    )

    # Fit the model
    dml_plr.fit()

    # Extract the results
    coef = dml_plr.coef
    se = dml_plr.se
    t_stat = dml_plr.t_stat
    p_val = dml_plr.pval

    # Store the results in the dictionary
    dml_summary_stats[Y] = {
        "Coefficient": coef[0],
        "Standard Error": se[0],
        "T-Statistic": t_stat[0],
        "P-Value": p_val[0],
    }

# Convert the summary statistics dictionary to a DataFrame
dml_1_summary_df = pd.DataFrame(dml_summary_stats).T

# Display the summary DataFrame
print(f"Comparison of DML Model Results for Different Outcomes: \n(Treatment: {D})")
display(dml_1_summary_df)

# Fit a quadratic polynomial regression model to the total emissions
poly = PolynomialFeatures(degree=2)
X_poly = poly.fit_transform(data_dml_1[["share_reserve_of_original_reserve"]])
model = LinearRegression()
model.fit(X_poly, data_dml_1["yearly_tco2e_prod_share_emissions"])

# Extract the coefficients
a, b, c = model.coef_[2], model.coef_[1], model.intercept_

print(
    f"The quadratic equation for the total emissions is: y = {a:.4f}x^2 + {b:.4f}x + {c:.4f}"
)

# Scatter plot with quadratic fit line
plt.figure(figsize=(10, 6))
sns.scatterplot(
    x=data_dml_1["share_reserve_of_original_reserve"],
    y=data_dml_1["emission_intensity_distributed"],
    hue=data_dml_1["electrified"],
    s=10,  # Marker size
)

# Fit a quadratic polynomial regression model
poly = PolynomialFeatures(degree=2)
X_poly = poly.fit_transform(data_dml_1[["share_reserve_of_original_reserve"]])
model = LinearRegression()
model.fit(X_poly, data_dml_1["emission_intensity_distributed"])

# Extract the coefficients
a, b, c = model.coef_[2], model.coef_[1], model.intercept_

dml_1_equation = {"a": a, "b": b, "c": c}

# Generate points for the fitted quadratic line
x_range = np.linspace(
    data_dml_1["share_reserve_of_original_reserve"].min(),
    data_dml_1["share_reserve_of_original_reserve"].max(),
    100,
)
y_fit = model.predict(poly.transform(x_range.reshape(-1, 1)))

# Plot the fitted quadratic line
plt.plot(x_range, y_fit, color="red")

# Print the quadratic equation
print(
    f"The quadratic equation for emission intensity is: y = {a:.4f}x^2 + {b:.4f}x + {c:.4f}"
)

# Upper Y-axis limit : 500
plt.ylim(0, 500)

plt.xlabel("Share Reserve of Original Reserve (%)")
plt.ylabel("Emission Intensity (kgCO2e/TOE)")
plt.title("Remaining Reserve Percentage and Emission Intensity")
plt.gca().invert_xaxis()
plt.show()

data_dml_1


random_seed = 42

# Copy the data for DML
data_dml_2 = data.copy()

# Remove fields with negative share_reserve_of_original_reserve
data_dml_2 = data_dml_2[data_dml_2["share_peak_prod"] >= 0]

# Generate the required variables
data_dml_2["processing_field_bin"] = (
    data_dml_2["processing_field"] == data_dml_2["field"]
).astype(float)

# Create dummy variables for operator
field_owner_dummies = pd.get_dummies(data_dml_2["operator"], prefix="operator")
data_dml_2 = pd.concat([data_dml_2, field_owner_dummies], axis=1)

# Define the list of outcomes
outcomes = ["emission_intensity_distributed", "yearly_tco2e_prod_share_emissions"]

# Define the treatment and control variables
D = "share_peak_prod"
X = (
    ["investments_mill_nok", "electrified"]
    + [col for col in data_dml_2.columns if col.startswith("facilities")]
    + [col for col in data_dml_2.columns if col.startswith("subsea_facilites")]
    + [col for col in data_dml_2.columns if col.startswith("surface_")]
    + [col for col in data_dml_2.columns if col.startswith("facility_kind")]
    + [col for col in data_dml_2.columns if col.startswith("well_status")]
    + [col for col in data_dml_2.columns if col.startswith("well_purpose")]
)

# Initialize a dictionary to store the summary statistics
dml_summary_stats = {}

# Iterate over the list of outcomes
for Y in outcomes:
    # Drop rows with NaN values in the relevant columns
    data_dml_2_clean = data_dml_2.dropna(subset=[Y, D] + X)

    # Initialize DoubleMLData object
    dml_data = DoubleMLData(data_dml_2_clean, Y, D, X)

    # Initialize DoubleMLPLR model with different models
    dml_plr = DoubleMLPLR(
        dml_data,
        ml_g=GradientBoostingRegressor(random_state=random_seed),
        ml_m=XGBRegressor(random_state=random_seed),
        ml_l=LinearRegression(),
    )

    # Fit the model
    dml_plr.fit()

    # Extract the results
    coef = dml_plr.coef
    se = dml_plr.se
    t_stat = dml_plr.t_stat
    p_val = dml_plr.pval

    # Store the results in the dictionary
    dml_summary_stats[Y] = {
        "Coefficient": coef[0],
        "Standard Error": se[0],
        "T-Statistic": t_stat[0],
        "P-Value": p_val[0],
    }

# Convert the summary statistics dictionary to a DataFrame
dml_2_summary_df = pd.DataFrame(dml_summary_stats).T

# Display the summary DataFrame
print(f"Comparison of DML Model Results for Different Outcomes: \n(Treatment: {D})")
display(dml_2_summary_df)

# Fit a quadratic polynomial regression model to the total emissions
poly = PolynomialFeatures(degree=2)
X_poly = poly.fit_transform(data_dml_2[["share_peak_prod"]])
model = LinearRegression()
model.fit(X_poly, data_dml_2["yearly_tco2e_prod_share_emissions"])

# Extract the coefficients
a, b, c = model.coef_[2], model.coef_[1], model.intercept_

print(
    f"The quadratic equation for the total emissions is: y = {a:.4f}x^2 + {b:.4f}x + {c:.4f}"
)

# Scatter plot with quadratic fit line
plt.figure(figsize=(10, 6))
sns.scatterplot(
    x=data_dml_2["share_peak_prod"],
    y=data_dml_2["emission_intensity_distributed"],
    size=data_dml_2["original_recoverable_oe"],
    hue=data_dml_2["electrified"],
    s=10,  # Marker size
)

# Fit a quadratic polynomial regression model
poly = PolynomialFeatures(degree=2)
X_poly = poly.fit_transform(data_dml_2[["share_peak_prod"]])
model = LinearRegression()
model.fit(X_poly, data_dml_2["emission_intensity_distributed"])

# Extract the coefficients
a, b, c = model.coef_[2], model.coef_[1], model.intercept_

dml_2_equation = {"a": a, "b": b, "c": c}

# Generate points for the fitted quadratic line
x_range = np.linspace(
    data_dml_2["share_peak_prod"].min(), data_dml_2["share_peak_prod"].max(), 100
)
y_fit = model.predict(poly.transform(x_range.reshape(-1, 1)))

# Plot the fitted quadratic line
plt.plot(x_range, y_fit, color="red")

# Print the quadratic equation
print(
    f"The quadratic equation for emission intensity is: y = {a:.4f}x^2 + {b:.4f}x + {c:.4f}"
)


# Upper Y-axis limit : 500
plt.ylim(0, 500)

plt.xlabel("Share of Peak Production")
plt.ylabel("Emission Intensity (kgCO2e/TOE)")
plt.title("Share of Peak Production")

plt.show()

# Set random seeds for reproducibility
random_seed = 42

# Copy the data for DML
data_dml_3 = data.copy()

# Generate the required variables
data_dml_3["processing_field_bin"] = (
    data_dml_3["processing_field"] == data_dml_3["field"]
).astype(float)

# Create dummy variables for operator
field_owner_dummies = pd.get_dummies(data_dml_3["operator"], prefix="operator")
data_dml_3 = pd.concat([data_dml_3, field_owner_dummies], axis=1)

# Define the list of outcomes
outcomes = ["emission_intensity_distributed", "yearly_tco2e_prod_share_emissions"]

# Define the treatment and control variables
D = "net_oil_eq_prod_yearly_mill_sm3"
X = (
    ["investments_mill_nok", "electrified", "future_investments_mill_nok"]
    + [col for col in data_dml_3.columns if col.startswith("facilities")]
    + [col for col in data_dml_3.columns if col.startswith("subsea_facilites")]
    + [col for col in data_dml_3.columns if col.startswith("surface_")]
    + [col for col in data_dml_3.columns if col.startswith("facility_kind")]
    + [col for col in data_dml_3.columns if col.startswith("well_status")]
    + [col for col in data_dml_3.columns if col.startswith("well_purpose")]
)

# Initialize a dictionary to store the summary statistics
dml_summary_stats = {}

# Iterate over the list of outcomes
for Y in outcomes:
    # Drop rows with NaN values in the relevant columns
    data_dml_3_clean = data_dml_3.dropna(subset=[Y, D] + X)

    # Initialize DoubleMLData object
    dml_data = DoubleMLData(data_dml_3_clean, Y, D, X)

    # Initialize DoubleMLPLR model with different models
    dml_plr = DoubleMLPLR(
        dml_data,
        ml_g=GradientBoostingRegressor(random_state=random_seed),
        ml_m=XGBRegressor(random_state=random_seed),
        ml_l=LinearRegression(),
    )

    # Fit the model
    dml_plr.fit()

    # Extract the results
    coef = dml_plr.coef
    se = dml_plr.se
    t_stat = dml_plr.t_stat
    p_val = dml_plr.pval

    # Store the results in the dictionary
    dml_summary_stats[Y] = {
        "Coefficient": coef[0],
        "Standard Error": se[0],
        "T-Statistic": t_stat[0],
        "P-Value": p_val[0],
    }

# Convert the summary statistics dictionary to a DataFrame
dml_1_summary_df = pd.DataFrame(dml_summary_stats).T

# Display the summary DataFrame
print(f"Comparison of DML Model Results for Different Outcomes: \n(Treatment: {D})")
display(dml_1_summary_df)

# Scatter plot with quadratic fit line
plt.figure(figsize=(10, 6))
sns.scatterplot(
    x=data_dml_3["net_oil_eq_prod_yearly_mill_sm3"],
    y=data_dml_3["emission_intensity_distributed"],
    # Make the color of the "electrified" field different
    size=data_dml_3["original_recoverable_oe"],
    hue=data_dml_3["electrified"],
    # Set hue to be original_recoverable_oe
    s=15,  # Marker size
)

# Fit a quadratic polynomial regression model
poly = PolynomialFeatures(degree=2)
X_poly = poly.fit_transform(data_dml_3[["net_oil_eq_prod_yearly_mill_sm3"]])
model = LinearRegression()
model.fit(X_poly, data_dml_3["emission_intensity_distributed"])

# Extract the coefficients
a, b, c = model.coef_[2], model.coef_[1], model.intercept_

dml_3_equation = {"a": a, "b": b, "c": c}

# Generate points for the fitted quadratic line
x_range = np.linspace(
    data_dml_3["net_oil_eq_prod_yearly_mill_sm3"].min(),
    data_dml_3["net_oil_eq_prod_yearly_mill_sm3"].max(),
    100,
)
y_fit = model.predict(poly.transform(x_range.reshape(-1, 1)))

# Plot the fitted quadratic line
plt.plot(x_range, y_fit, color="red")

# Upper Y-axis limit : 500
plt.ylim(0, 500)


# Print the quadratic equation
print(
    f"The quadratic equation for emission intensity is: y = {a:.4f}x^2 + {b:.4f}x + {c:.4f}"
)
plt.xlabel("Oil Eq. Production (mill. Sm3)")
plt.ylabel("Emissions Intensity kgCO2e/TOE")
plt.title("Oil Eq. Production and Emission Intensity")
plt.show()

# Set random seeds for reproducibility
random_seed = 42

# Copy the data for DML
data_dml_4 = data.copy()

# Generate the required variables
data_dml_4["processing_field_bin"] = (
    data_dml_4["processing_field"] == data_dml_4["field"]
).astype(float)

# Create dummy variables for operator
field_owner_dummies = pd.get_dummies(data_dml_4["operator"], prefix="operator")
data_dml_4 = pd.concat([data_dml_4, field_owner_dummies], axis=1)

# Define the list of outcomes
outcomes = ["emission_intensity_distributed", "yearly_tco2e_prod_share_emissions"]

# Define the treatment and control variables
D = "original_recoverable_oe"
X = (
    ["investments_mill_nok", "electrified", "future_investments_mill_nok"]
    + [col for col in data_dml_4.columns if col.startswith("facilities")]
    + [col for col in data_dml_4.columns if col.startswith("subsea_facilites")]
    + [col for col in data_dml_4.columns if col.startswith("surface_")]
    + [col for col in data_dml_4.columns if col.startswith("facility_kind")]
    + [col for col in data_dml_4.columns if col.startswith("well_status")]
    + [col for col in data_dml_4.columns if col.startswith("well_purpose")]
)

# Initialize a dictionary to store the summary statistics
dml_summary_stats = {}

# Iterate over the list of outcomes
for Y in outcomes:
    # Drop rows with NaN values in the relevant columns
    data_dml_4_clean = data_dml_4.dropna(subset=[Y, D] + X)

    # Initialize DoubleMLData object
    dml_data = DoubleMLData(data_dml_4_clean, Y, D, X)

    # Initialize DoubleMLPLR model with different models
    dml_plr = DoubleMLPLR(
        dml_data,
        ml_g=GradientBoostingRegressor(random_state=random_seed),
        ml_m=XGBRegressor(random_state=random_seed),
        ml_l=LinearRegression(),
    )

    # Fit the model
    dml_plr.fit()

    # Extract the results
    coef = dml_plr.coef
    se = dml_plr.se
    t_stat = dml_plr.t_stat
    p_val = dml_plr.pval

    # Store the results in the dictionary
    dml_summary_stats[Y] = {
        "Coefficient": coef[0],
        "Standard Error": se[0],
        "T-Statistic": t_stat[0],
        "P-Value": p_val[0],
    }

# Convert the summary statistics dictionary to a DataFrame
dml_1_summary_df = pd.DataFrame(dml_summary_stats).T

# Display the summary DataFrame
print(f"Comparison of DML Model Results for Different Outcomes: \n(Treatment: {D})")
display(dml_1_summary_df)

# Scatter plot with quadratic fit line
plt.figure(figsize=(10, 6))
sns.scatterplot(
    x=data_dml_4["original_recoverable_oe"],
    y=data_dml_4["emission_intensity_distributed"],
    # Make the color of the "electrified" field different
    # size=data_dml_4["original_recoverable_oe"],
    hue=data_dml_4["electrified"],
    # Set hue to be original_recoverable_oe
    s=15,  # Marker size
)

# Fit a quadratic polynomial regression model
poly = PolynomialFeatures(degree=2)
X_poly = poly.fit_transform(data_dml_4[["original_recoverable_oe"]])
model = LinearRegression()
model.fit(X_poly, data_dml_4["emission_intensity_distributed"])

# Extract the coefficients
a, b, c = model.coef_[2], model.coef_[1], model.intercept_

dml_4_equation = {"a": a, "b": b, "c": c}

# Generate points for the fitted quadratic line
x_range = np.linspace(
    data_dml_4["original_recoverable_oe"].min(),
    data_dml_4["original_recoverable_oe"].max(),
    100,
)
y_fit = model.predict(poly.transform(x_range.reshape(-1, 1)))

# Plot the fitted quadratic line
plt.plot(x_range, y_fit, color="red")

# Upper Y-axis limit : 500
plt.ylim(0, 500)


# Print the quadratic equation
print(
    f"The quadratic equation for emission intensity is: y = {a:.4f}x^2 + {b:.4f}x + {c:.4f}"
)
plt.xlabel("Original Recoverable Oil Eq. (mill. Sm3)")
plt.ylabel("Emissions Intensity kgCO2e/TOE")
plt.title("Original Reserve Size and Emission Intensity")
plt.show()


data_dml_3


# Checking how many fields have more than 0 in current remaining recoverable oil eq.

data_producing = data[data["current_status"] == "Producing"]
data_producing[data_producing["current_remaining_recoverable_oe"] > 0][
    "field"
].nunique()

data.net_oil_eq_prod_yearly_mill_sm3.describe()

# Create a column called median_production for each field
data["median_production"] = data.groupby("field")[
    "net_oil_eq_prod_yearly_mill_sm3"
].transform("mean")

# Checking Nan values in the median_production column
data["median_production"].isna().sum()

producing_data["current_remaining_recoverable_oe"].aggregate("sum")

# Filter for producing fields and calculate median yearly production
producing_data = data.copy()
producing_data = producing_data[producing_data["current_remaining_recoverable_oe"] > 0]

# Define the ramp-down threshold
ramp_down_threshold = 0.1

# Print dataset information after preprocessing
print(f"Dataset shape after preprocessing: {producing_data.shape}")

# Simplified production forecast
future_years = list(range(2024, 2050))
fields = producing_data["field"].unique()

future_predictions = []

for field in fields:
    median_production = producing_data[producing_data["field"] == field][
        "median_production"
    ].iloc[0]
    current_reserve = producing_data[producing_data["field"] == field][
        "current_remaining_recoverable_oe"
    ].iloc[0]
    original_recoverable = producing_data[producing_data["field"] == field][
        "original_recoverable_oe"
    ].iloc[0]
    cumulative_production = 0
    year = 2024

    while current_reserve > 0 and year <= 2050:
        if current_reserve <= ramp_down_threshold * original_recoverable:
            production_for_year = max(
                median_production
                * (current_reserve / (ramp_down_threshold * original_recoverable)),
                0,
            )
        else:
            production_for_year = (
                median_production
                if current_reserve >= median_production
                else current_reserve
            )

        cumulative_production += production_for_year
        future_predictions.append(
            {
                "field": field,
                "year": year,
                "predicted_production": production_for_year,
                "cumulative_production": cumulative_production,
                "years_left": np.round(current_reserve / median_production, 0),
            }
        )
        current_reserve -= production_for_year
        year += 1

    if current_reserve <= 0:
        future_predictions.append(
            {
                "field": field,
                "year": year,
                "predicted_production": 0,
                "cumulative_production": cumulative_production,
                "years_left": 0,
            }
        )

# Create a DataFrame for future predictions
future_predictions_df = pd.DataFrame(future_predictions)

# Visualize the estimated production for each field
plt.figure(figsize=(15, 10))
for field in future_predictions_df["field"].unique():
    field_data = future_predictions_df[future_predictions_df["field"] == field]
    plt.plot(field_data["year"], field_data["predicted_production"], label=field)

plt.xlabel("Year")
plt.ylabel("Projected Production (Million Sm3)")
plt.title("Estimated Production Volume for Each Field")
plt.ylim(0, 45)  # Set the y-axis limit to better visualize the data
# plt.legend(title="Field", loc="upper right", bbox_to_anchor=(1.2, 1))
plt.show()

future_predictions_df.describe()

# Create a neat stacked bar chart with the total production for each year. Use future_predictions_df. Split color by field

# Create a pivot table for the future predictions
pivot_table = future_predictions_df.pivot(
    index="year", columns="field", values="predicted_production"
)

# Fill NaN values with 0
pivot_table = pivot_table.fillna(0)

# Sort after highest production field
pivot_table = pivot_table[pivot_table.sum().sort_values(ascending=False).index]
# Create a stacked bar chart
pivot_table.plot(kind="bar", stacked=True, figsize=(15, 10))
plt.xlabel("Year")
plt.ylabel("Projected Production (Million Sm3)")
plt.title("Estimated Production Volume for Each Field")
# plt.legend(title="Field", loc="upper right", bbox_to_anchor=(1.2, 1))

# Hide legend

# Show legend with top 10 highest producing fields

plt.legend(
    title="Top 10 Producing Fields",
    loc="upper right",
    bbox_to_anchor=(1.2, 1),
    labels=pivot_table.columns[:10],
)

# In the same graph, but on the right side, show show the total yearly emissions (not cumaltive) for each year - as a line plot
plt.twinx()
plt.plot(future_predictions_df.groupby("year")["total_emissions"].sum(), color="black")
plt.ylabel("Total Projected Production (Million Sm3)")

plt.ylabel("Projected Emissions (Million Tons)")

plt.show()


import matplotlib.pyplot as plt

# Create a neat stacked bar chart with the total production for each year. Use future_predictions_df. Split color by field

# Create a pivot table for the future predictions
pivot_table = future_predictions_df.pivot(
    index="year", columns="field", values="predicted_production"
)

# Fill NaN values with 0
pivot_table = pivot_table.fillna(0)

# Sort after highest production field
pivot_table = pivot_table[pivot_table.sum().sort_values(ascending=False).index]

# Create a figure and the first axis
fig, ax1 = plt.subplots(figsize=(15, 10))
# Create a second y-axis for the emissions plot
ax2 = ax1.twinx()
ax2.plot(
    future_predictions_df.groupby("year")["total_emissions"].sum(),
    color="black",
    linestyle="--",
    marker="o",
)
ax2.set_ylabel("Projected Emissions (Million Tons)")

# Create the stacked bar chart
pivot_table.plot(kind="bar", stacked=True, ax=ax1, legend=False)
ax1.set_xlabel("Year")
ax1.set_ylabel("Projected Production (Million Sm3)")
ax1.set_title("Estimated Production Volume for Each Field")


# Show the legend for the top 10 highest producing fields
handles, labels = ax1.get_legend_handles_labels()
ax1.legend(
    handles[:10],
    labels[:10],
    title="Top 10 Producing Fields",
    loc="upper right",
    bbox_to_anchor=(1.2, 1),
)

# Show the plot
plt.show()


future_predictions_df


future_predictions_df.years_left.describe()

future_predictions_df.head()

future_predictions_df[future_predictions_df["field"] == "troll"]

producing_data = data.copy()

# Filter for producing fields and calculate median yearly production
producing_data = producing_data[producing_data["current_remaining_recoverable_oe"] > 0]

# Calculate the mean emission intensity for each field
producing_data["mean_emission_intensity_distributed"] = producing_data.groupby("field")[
    "emission_intensity_distributed"
].transform("mean")


def emission_intensity_adjustment(eq, x):
    a, b, c = eq["a"], eq["b"], eq["c"]
    return a * x**2 + b * x + c


# Define the ramp-down threshold
ramp_down_threshold = 0.05

# Print dataset information after preprocessing
print(f"Dataset shape after preprocessing: {producing_data.shape}")

# Simplified production forecast
future_years = list(range(2024, 2050))
fields = producing_data["field"].unique()

future_predictions = []

for field in fields:
    median_production = producing_data[producing_data["field"] == field][
        "median_production"
    ].iloc[0]
    current_reserve = producing_data[producing_data["field"] == field][
        "current_remaining_recoverable_oe"
    ].iloc[0]
    original_recoverable = producing_data[producing_data["field"] == field][
        "original_recoverable_oe"
    ].iloc[0]
    current_emission_intensity = producing_data[producing_data["field"] == field][
        "mean_emission_intensity_distributed"
    ].iloc[0]
    cumulative_production = 0
    year = 2024

    while current_reserve > 0 and year <= 2050:
        if current_reserve <= ramp_down_threshold * original_recoverable:
            production_for_year = max(
                median_production
                * (current_reserve / (ramp_down_threshold * original_recoverable)),
                0,
            )
        else:
            production_for_year = (
                median_production
                if current_reserve >= median_production
                else current_reserve
            )

        cumulative_production += production_for_year

        share_of_peak_prod = production_for_year / original_recoverable
        remaining_reserve_percentage = current_reserve / original_recoverable

        adjustment_1 = emission_intensity_adjustment(
            dml_1_equation, remaining_reserve_percentage * 100
        )
        adjustment_2 = emission_intensity_adjustment(
            dml_2_equation, share_of_peak_prod * 100
        )
        adjustment_3 = emission_intensity_adjustment(
            dml_3_equation, production_for_year
        )

        adjustment_effect = (adjustment_1 + adjustment_2 + adjustment_3) / 3

        # Apply the adjustments with equal weighting
        # final_emission_intensity = current_emission_intensity * (1 + (adjustment_1 + adjustment_2 + adjustment_3) / 3)

        # Apply the adjustments with equal weighting
        # final_emission_intensity = current_emission_intensity * (1 + (adjustment_1 + adjustment_2 + adjustment_3) / 3)
        # total_emissions = production_for_year * final_emission_intensity

        # Define weights for the current emission intensity and adjustments
        weight_current_intensity = (
            0.1  # Less influence on the current emission intensity
        )
        weight_adjustments = 0.9  # More influence on the adjustments

        # final_emission_intensity = (weight_current_intensity * current_emission_intensity
        # + weight_adjustments * current_emission_intensity * (1 + adjustment_effect))

        final_emission_intensity = (
            weight_current_intensity * current_emission_intensity
            + weight_adjustments * current_emission_intensity * (1 + adjustment_effect)
        )

        total_emissions = production_for_year * final_emission_intensity

        future_predictions.append(
            {
                "field": field,
                "year": year,
                "predicted_production": production_for_year,
                "cumulative_production": cumulative_production,
                "total_emissions": total_emissions,
                "years_left": np.round(current_reserve / median_production, 0),
                "reserve": current_reserve,
                "mean_emission_intensity_distributed": current_emission_intensity,
            }
        )
        current_reserve -= production_for_year
        year += 1

    if current_reserve <= 0:
        future_predictions.append(
            {
                "field": field,
                "year": year,
                "predicted_production": 0,
                "cumulative_production": cumulative_production,
                "total_emissions": 0,
                "years_left": 0,
                "reserve": current_reserve,
                "mean_emission_intensity_distributed": current_emission_intensity,
            }
        )

# Create a DataFrame for future predictions
future_predictions_df = pd.DataFrame(future_predictions)

# Plot the estimated total emissions for each field
plt.figure(figsize=(15, 10))
for field in future_predictions_df["field"].unique():
    field_data = future_predictions_df[future_predictions_df["field"] == field]
    plt.plot(field_data["year"], field_data["total_emissions"], label=field)

plt.xlabel("Year")
plt.ylabel("Total Emissions (kgCO2e)")
plt.title("Estimated Total Emissions for Each Field")
plt.show()

future_predictions_df.describe()

# future_predictions_df
future_predictions_df[future_predictions_df["field"] == "troll"]

# Creating a table to show, top 5 producers in cumalitve, total emissions, and average emission intensities

# Calculate the cumulative production and total emissions for each field
cumulative_production = future_predictions_df.groupby("field")[
    "cumulative_production"
].max()

total_emissions = future_predictions_df.groupby("field")["total_emissions"].max()

average_emission_intensity = future_predictions_df.groupby("field")[
    "mean_emission_intensity_distributed"
].mean()

# Create a DataFrame for the top 5 producers in cumulative production
top_5_cumulative = (
    cumulative_production.sort_values(ascending=False).head(5).reset_index()
)
top_5_cumulative.columns = ["Field", "Cumulative Production"]

# Create a DataFrame for the top 5 producers in total emissions
top_5_emissions = total_emissions.sort_values(ascending=False).head(5).reset_index()
top_5_emissions.columns = ["Field", "Total Emissions"]

# Create a DataFrame for the top 5 producers in average emission intensity
top_5_intensity = (
    average_emission_intensity.sort_values(ascending=True).head(5).reset_index()
)
top_5_intensity.columns = ["Field", "Average Emission Intensity"]

# Display the top 5 producers in each category
print("Top 5 Producers in Cumulative Production:")

display(top_5_cumulative)

print("\nTop 5 Producers in Total Emissions:")
display(top_5_emissions)

print("\Lowest 5  Average Emission Intensity:")
display(top_5_intensity)


display(data[data["field"] == "troll"])

# yearly_tco2e_prod_share_emissions mean for statfjord nord

display(data[data["field"] == "troll"]["emission_intensity_distributed"].mean())
display(data[data["field"] == "troll"]["emission_intensity_distributed"].mean())

em_1 = data[data["year"] == "2021"]["yearly_tco2e_gwp100"].sum()
prod_1 = data[data["year"] == "2021"]["net_oil_eq_prod_yearly_mill_sm3"].sum()

display(em_1)

em_1 / (prod_1 * 100000 * 0.84)


em_1 = data[data["year"] == "2022"]["yearly_tco2e_gwp100"].sum()
prod_1 = data[data["year"] == "2022"]["net_oil_eq_prod_yearly_mill_sm3"].sum()

display(em_1)

em_1 / (prod_1 * 100000 * 0.84)


em_2 = data[data["year"] == "2021"]["yearly_tco2e_gwp100"].sum()
prod_2 = data[data["year"] == "2021"]["net_oil_eq_prod_yearly_mill_sm3"].sum()

em_2 * 1000 / (prod_2 * 840000)


display(data[data["field"] == "statfjord nord"])

# yearly_tco2e_prod_share_emissions mean for statfjord nord

display(
    data[data["field"] == "statfjord nord"]["emission_intensity_distributed"].mean()
)

# Adding the electrified label from data

# Extracting only the last observation for each field
last_observation = producing_data.groupby("field").last().reset_index()

future_predictions_df = future_predictions_df.merge(
    last_observation[["field", "electrified"]], on="field", how="left"
)
future_predictions_df

# Export the future predictions to a CSV file
import os

filename_path = (
    "../../data/output/emissions_and_production/cleaned/field_predictions.csv"
)

if not os.path.exists(filename_path):
    future_predictions_df.to_csv(filename_path, index=False)
    print("Saved file")
else:
    print("File already exists")


# Printing the names of the electrified fields

future_predictions_df[future_predictions_df["electrified"] == 1]["field"].unique()

# Preparing the data

data["well_water_depth_mean_20m"] = data["well_water_depth_mean"] * 20

#

# Preprocess the Data: Remove np.nan and inf values
ols_data = data.replace([np.inf, -np.inf], np.nan).dropna()

# Define the dependent and independent variables
Y1 = ols_data["emission_intensity"]
Y2 = ols_data["emission_intensity_distributed"]

X = ols_data[
    [
        "share_peak_prod",
        "well_water_depth_mean_20m",
        "well_final_vertical_depth_mean",
        "original_recoverable_oe",
        "share_reserve_of_original_reserve",
        "net_oil_eq_prod_monthly_sm3_volatility",
        "gas_reserve_ratio",
        "oil_gas_reserve_ratio",
    ]
]

# Perform OLS regression using statsmodels for detailed results
ols_Y1 = sm.OLS(Y1, X).fit()
ols_Y2 = sm.OLS(Y2, X).fit()

# Conduct the OLS using sklearn for consistency with provided code
reg = LinearRegression().fit(X, Y2)

# Second degree polynomial regression
X_poly2 = X.copy()
for col in X.columns:
    if col != "const":
        X_poly2[f"{col}^2"] = X[col] ** 2

ols_Y1_poly2 = sm.OLS(Y1, X_poly2).fit()
ols_Y2_poly2 = sm.OLS(Y2, X_poly2).fit()


# Define a function to display the results in a pretty format
def pretty_print_results(results, degree):
    print(f"OLS Regression Results (Degree {degree}):")
    print("========================================")
    print(results.summary())
    print("\n\n")


# Print the results
pretty_print_results(ols_Y1, 1)
pretty_print_results(ols_Y2, 1)
pretty_print_results(ols_Y1_poly2, 2)
pretty_print_results(ols_Y2_poly2, 2)

# ------------------------------------------------------------------
# Robustness Check: Two-Way Fixed Effects (TWFE) Baseline
# ------------------------------------------------------------------
print("\n--- Running TWFE Robustness Check ---")
try:
    # We attempt to run a simple TWFE model if 'field' and 'year' are in ols_data
    if 'field' in ols_data.columns and 'year' in ols_data.columns:
        import statsmodels.formula.api as smf
        # Make a copy for fixed effects
        twfe_data = ols_data.copy()
        
        # We need continuous outcome and independent vars
        # Using Y1 (total emissions or similar) as outcome if available, else skip
        # Assuming Y1 is kgco2e/toe_int_gwp100 or total_emissions
        
        # A simple string formula for TWFE using C() for categorical fixed effects
        # Example: Y ~ X1 + X2 + C(field) + C(year)
        # We build the formula dynamically from X columns
        x_cols = [c for c in X.columns if c != "const"]
        formula = "Y1 ~ " + " + ".join(x_cols) + " + C(field) + C(year)"
        
        twfe_data['Y1'] = Y1
        twfe_model = smf.ols(formula, data=twfe_data).fit()
        
        print("\nTWFE Baseline Results (Extract):")
        # Extracting just the main coefficients (ignoring the hundreds of field/year dummies for display)
        summary_df = twfe_model.summary2().tables[1]
        display_vars = ["Intercept"] + x_cols
        print(summary_df.loc[summary_df.index.isin(display_vars)])
        print("\nNote: TWFE model confirms the baseline directional effects prior to DML non-linear adjustments.")
    else:
        print("TWFE Skipped: 'field' or 'year' identifiers missing from ols_data.")
except Exception as e:
    print(f"TWFE Check encountered an error (likely due to missing fixed effect categoricals): {e}")

