# 2. Methodology

Our empirical strategy is divided into three consecutive phases: 1) Data Aggregation and Engineering, 2) Causal Inference via Double Machine Learning (DML) and Two-Way Fixed Effects (TWFE), and 3) Constrained Optimization for Policy Evaluation.

## 2.1. Data and Geospatial Integration

We construct a highly granular panel dataset by merging monthly production data, platform infrastructure details, and environmental emission disclosures (CO2, CH4, NOx) from the Norwegian Petroleum Directorate (NPD). We enhance this with geospatial boundaries (shapefiles) to control for the physical characteristics and geographical depth of the offshore reservoirs. 

## 2.2. Causal Discovery and Double Machine Learning (DML)

To identify the true drivers of carbon intensity without the confounding effects of collinearity, we first employ the PC algorithm to establish a Directed Acyclic Graph (DAG) of the underlying physical and economic variables. Variables that act as direct parents to carbon intensity are then analyzed using Double Machine Learning (DML).

The DML framework isolates the causal effect of a treatment $D$ (e.g., field age or reservoir depth) on the outcome $Y$ (carbon emissions) by orthogonalizing both against a high-dimensional set of controls $X$. This is expressed via the partially linear model:

$$ Y_i = \theta D_i + g(X_i) + U_i, \quad E[U_i | X_i, D_i] = 0 $$
$$ D_i = m(X_i) + V_i, \quad E[V_i | X_i] = 0 $$

Where $\theta$ is the true causal parameter, and $g(X)$ and $m(X)$ are nuisance parameters estimated via random forests. By employing cross-fitting, we eliminate regularization bias, yielding a robust, unbiased estimate of $\theta$.

## 2.3. Two-Way Fixed Effects (TWFE) Baseline

To benchmark our non-linear DML findings, we estimate a standard TWFE panel regression:

$$ Y_{it} = \beta D_{it} + \gamma X_{it} + \alpha_i + \delta_t + \epsilon_{it} $$

Where $\alpha_i$ represents field-level fixed effects and $\delta_t$ represents temporal fixed effects. This provides a classical econometric validator for our primary machine learning approach.

## 2.4. Linear Optimization for Policy Scenarios

Using the causal parameters derived above, we formulate a linear programming problem to optimize decarbonization across the NCS. The objective function minimizes the total deviation from baseline economic production while strictly enforcing a regional emission constraint defined by the policy stringency parameter $\lambda \in [0, 1]$.

Let $P_i$ be the production of field $i$ and $E_i$ be its associated emissions. The optimization is defined as:

$$ \max \sum_{i \in F} P_i $$
$$ \text{subject to:} $$
$$ \sum_{i \in F} E_i \leq \lambda \sum_{i \in F} E_{i,\text{baseline}} $$
$$ P_i \leq P_{i,\text{baseline}} \quad \forall i \in F $$

This framework is executed under two distinct paradigms: strategic production phase-out (where older, high-intensity fields are closed) and targeted electrification (where capital expenditure is allocated to reduce specific $E_i$ coefficients). By applying $\lambda$, we map the optimal field closures at varying levels of emission constraint. We then calculate the lost revenue per Ton of Oil Equivalent (TOE) to generate a Marginal Abatement Cost (MAC) curve for the phase-out strategy.
