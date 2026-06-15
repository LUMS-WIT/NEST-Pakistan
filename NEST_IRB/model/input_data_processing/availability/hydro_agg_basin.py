"""
This script aggregates the global gridded data to any scale. The following
script specifically aggregates global gridded hydrological data onto the basin
 mapping used in the nexus module.
"""

import os

import numpy as np
import pandas as pd

# variable, for detailed symbols, refer to ISIMIP2b documentation
variables = ["qtot", "dis", "qr"]  # total runoff  # discharge  # groundwater run


GCMs = ["mmean", "dry"]
GCM = "mmean"  # 'dry'choose driest GCM else 'mmean' for multi model mean
# else mmmean
iso3 = "IRB"
isimip = "3b"

# climate model
if isimip == "2b":
    climmodels = ["gfdl-esm2m", "hadgem2-es", "ipsl-cm5a-lr", "miroc5"]
    climmodel = "gfdl-esm2m"
    # climate forcing
    scenarios = ["rcp26", "rcp60"]
    scen = "rcp26"
    # This is an internal IIASA directory path
    wd1 = os.path.join("p:", "ene.model", "NEST", "hydrological_data_agg") + os.sep
    wd = os.path.join("p:", "watxene", "ISIMIP", "ISIMIP2b", "output", "LPJmL") + os.sep
    wd2 = os.path.join("p:", "ene.model", "NEST", "hydrology", "processed_nc4") + os.sep
else:
    climmodels = [
        "gfdl-esm4",
        "ipsl-cm6a-lr",
        "mpi-esm1-2-hr",
        "mri-esm2-0",
        "ukesm1-0-ll",
    ]
    cl = "gfdl-esm4"
    scenarios = ["ssp126", "ssp370", "ssp585"]
    scen = "ssp126"
    wd1 = os.path.join("p:", "ene.model", "NEST", "hydrological_data_agg") + os.sep
    # Override input/output directory to local CSV folder
    wd11 = (    
        r"C:\Users\User\Desktop\lums\3rd semester\Thesis\ISIMP Water Model\Output"
        + os.sep
    )


SCEN_LOW = "ssp126"
SCEN_HIGH = "ssp370"


def _load_scenario_csv(
    base_dir: str, variable: str, model: str, scenario: str
) -> pd.DataFrame:
    """Load scenario CSV from Output folder and drop optional metadata columns."""
    csv_path = os.path.join(base_dir, f"{variable}_{model}_{scenario}_output.csv")
    df = pd.read_csv(csv_path).drop(columns=["basin_id"], errors="ignore")

    try:
        parsed = pd.to_datetime(df.columns, errors="raise")
        # align columns to month-end timestamps to match downstream logic
        df.columns = parsed + pd.offsets.MonthEnd(0)
    except Exception:
        pass
    return df


def bias_correction(df, val_2020, val_2020_annual, delta60):
    """ias corrects the data such that 2020 value is same
    for both scenario and then apply
    Input
    ----------
    df : raw input monthly data
    Returns
    -------
    df : bias corrected monthly data with also replacing 5 year timestep average
    df_monthly: monthly bias corrected data
    df_5y_m: bias corrected 5 y monthly
    df_5y: bias corrected 5 y average
    """
    # Starting value of delat is 1
    # it will reduce to zero with each 5 year timestep
    # till 2045 with a difference of 0.2.
    # This means the bias correction will fade away till 2045
    delta_multiply = 1

    for year in np.arange(2020, 2105, 5):
        # for 2020 delta all scenario data frame will be same
        if year == 2020:
            target_cols_2020 = pd.date_range("2020-01-01", periods=12, freq="ME")
            df[target_cols_2020] = pd.DataFrame(
                val_2020.values, index=df.index, columns=target_cols_2020
            )

        else:
            # for delta years after 2020
            if delta_multiply > 0.1:
                for i in np.arange(4, -1, -1):
                    if i == 4:
                        delta60.columns = pd.date_range(
                            str(year - i) + "-01-01", periods=12, freq="ME"
                        )
                        final_temp = df[
                            pd.date_range(
                                str(year - i) + "-01-01", periods=12, freq="ME"
                            )
                        ] - (delta_multiply * delta60)

                    else:
                        delta60.columns = pd.date_range(
                            str(year - i) + "-01-01", periods=12, freq="ME"
                        )
                        temp = df[
                            pd.date_range(
                                str(year - i) + "-01-01", periods=12, freq="ME"
                            )
                        ] - (delta_multiply * delta60)

                        final_temp = pd.concat((final_temp, temp), axis=1)

                df_monthly = final_temp
                target_cols_year = pd.date_range(str(year) + "-01-01", periods=12, freq="ME")
                grouped_monthly = final_temp.groupby(
                    final_temp.columns.month, axis=1
                ).mean()
                df[target_cols_year] = pd.DataFrame(
                    grouped_monthly.values,
                    index=df.index,
                    columns=target_cols_year,
                )
                # 5 year monthly data
                df_5y_m = df[df.columns[df.columns.year.isin(years)]]
                # 5 year annual
                # 50th quantile - q50
                df_q50 = (
                    df_monthly.rolling(240, min_periods=1, axis=1)
                    .quantile(0.5, interpolation="linear")
                    .resample("5Y", axis=1)
                    .mean()
                )
                df_q50["2020-12-31"] = val_2020_annual
                # 70th quantile - q70
                df_q70 = (
                    df_monthly.rolling(240, min_periods=1, axis=1)
                    .quantile(0.3, interpolation="linear")
                    .resample("5Y", axis=1)
                    .mean()
                )
                df_q70["2020-12-31"] = val_2020_annual
                # 90th quantile - q90
                df_q90 = (
                    df_monthly.rolling(240, min_periods=1, axis=1)
                    .quantile(0.1, interpolation="linear")
                    .resample("5Y", axis=1)
                    .mean()
                )

                df_q90["2020-12-31"] = val_2020_annual

                delta_multiply -= 0.2

            else:
                # after detlta years
                temp_daterange = pd.date_range(
                    str(year - 4) + "-01-01", periods=60, freq="ME"
                )
                # Monthly Bias corrected data
                df_monthly = df

                target_cols_year = pd.date_range(str(year) + "-01-01", periods=12, freq="ME")
                grouped_monthly = (
                    df[temp_daterange]
                    .groupby(df[temp_daterange].columns.month, axis=1)
                    .mean()
                )
                df[target_cols_year] = pd.DataFrame(
                    grouped_monthly.values,
                    index=df.index,
                    columns=target_cols_year,
                )
                # 5 year monthly
                df_5y_m = df[df.columns[df.columns.year.isin(years)]]
                # 5 year annual
                # 50th quantile - q50
                df_q50 = (
                    df_monthly.rolling(240, min_periods=1, axis=1)
                    .quantile(0.5, interpolation="linear")
                    .resample("5Y", axis=1)
                    .mean()
                )
                df_q50["2020-12-31"] = val_2020_annual
                # 70th quantile - q70
                df_q70 = (
                    df_monthly.rolling(240, min_periods=1, axis=1)
                    .quantile(0.3, interpolation="linear")
                    .resample("5Y", axis=1)
                    .mean()
                )
                df_q70["2020-12-31"] = val_2020_annual
                # 90th quantile - q90
                df_q90 = (
                    df_monthly.rolling(240, min_periods=1, axis=1)
                    .quantile(0.1, interpolation="linear")
                    .resample("5Y", axis=1)
                    .mean()
                )

                df_q90["2020-12-31"] = val_2020_annual

    return df, df_monthly, df_5y_m, df_q50, df_q70, df_q90


years = np.arange(2015, 2105, 5)


def process_variable(var):
    qtot_7p0_gfdl = _load_scenario_csv(wd11, var, cl, SCEN_HIGH)
    qtot_2p6_gfdl = _load_scenario_csv(wd11, var, cl, SCEN_LOW)

    calendar_months = pd.date_range("2015-01-01", periods=192, freq="ME")
    qtot_2p6_gfdl_avg = qtot_2p6_gfdl[calendar_months]
    qtot_7p0_gfdl_avg = qtot_7p0_gfdl[calendar_months]

    monthly_7p0 = qtot_7p0_gfdl_avg.groupby(
        qtot_7p0_gfdl_avg.columns.to_series().dt.month, axis=1
    ).mean().sort_index(axis=1)
    monthly_2p6 = qtot_2p6_gfdl_avg.groupby(
        qtot_2p6_gfdl_avg.columns.to_series().dt.month, axis=1
    ).mean().sort_index(axis=1)


    val_2020 = (monthly_7p0 + monthly_2p6) / 2
    val_2020_annual = val_2020.mean(axis=1)
    delta60 = monthly_7p0 - val_2020

    df_26, df_monthly_26, df_5y_m_26, df_q50_26, df_q70_26, df_q90_26 = bias_correction(
        qtot_2p6_gfdl, val_2020, val_2020_annual, delta60
    )

    df_70, df_monthly_70, df_5y_m_70, df_q50_70, df_q70_70, df_q90_70 = bias_correction(
        qtot_7p0_gfdl, val_2020, val_2020_annual, delta60
    )

    df_monthly_26.to_csv(wd11 + f"/{var}_monthly_2p6_{iso3}.csv")
    df_5y_m_26.to_csv(wd11 + f"/{var}_5y_m_2p6_low_{iso3}.csv")
    df_q50_26.to_csv(wd11 + f"/{var}_5y_2p6_low_{iso3}.csv")
    df_q70_26.to_csv(wd11 + f"/{var}_5y_2p6_med_{iso3}.csv")
    df_q90_26.to_csv(wd11 + f"/{var}_5y_2p6_high_{iso3}.csv")

    df_monthly_70.to_csv(wd11 + f"/{var}_monthly_7p0_{iso3}.csv")
    df_5y_m_70.to_csv(wd11 + f"/{var}_5y_m_7p0_low_{iso3}.csv")
    df_q50_70.to_csv(wd11 + f"/{var}_5y_7p0_low_{iso3}.csv")
    df_q70_70.to_csv(wd11 + f"/{var}_5y_7p0_med_{iso3}.csv")
    df_q90_70.to_csv(wd11 + f"/{var}_5y_7p0_high_{iso3}.csv")

    # No climate scenarios
    df_q50_70.apply(lambda x: val_2020_annual)
    for y in years:
        target_cols = pd.date_range(f"{y}-01-01", periods=12, freq="ME")
        df_5y_m_70[target_cols] = pd.DataFrame(
            val_2020.values, index=df_5y_m_70.index, columns=target_cols
        )
    df_5y_m_70.to_csv(wd11 + f"/{var}_5y_m_no_climate_low_{iso3}.csv")
    df_q50_70.apply(lambda x: val_2020_annual).to_csv(
        wd11 + f"/{var}_5y_no_climate_low_{iso3}.csv"
    )
    df_q70_70.apply(lambda x: val_2020_annual).to_csv(
        wd11 + f"/{var}_5y_no_climate_med_{iso3}.csv"
    )
    df_q90_70.apply(lambda x: val_2020_annual).to_csv(
        wd11 + f"/{var}_5y_no_climate_high_{iso3}.csv"
    )

    def generate_eflow_outputs(df_env, scenario_label):
        col_end = None
        for z in range(len(df_env.columns) // 12):
            col_start = 0 if z == 0 else col_end
            col_end = (z + 1) * 12
            temp = df_env.iloc[:, col_start:col_end].copy()

            MAF = temp.mean(axis=1)

            for j in range(len(temp.columns)):
                temp.iloc[:, j] = np.where(
                    temp.iloc[:, j] > 0.8 * MAF,
                    temp.iloc[:, j] * 0.2,
                    np.where(
                        (temp.iloc[:, j] > 0.4 * MAF) & (temp.iloc[:, j] <= 0.8 * MAF),
                        temp.iloc[:, j] * 0.45,
                        temp.iloc[:, j] * 0.6,
                    ),
                )

            if z == 0:
                eflow = temp
            else:
                eflow = pd.concat((eflow, temp), axis=1)

            eflow = eflow.abs()

        eflow_5y = eflow.resample("5Y", axis=1).mean()
        eflow_5y.to_csv(wd11 + f"e-flow_{var}_{scenario_label}_{iso3}.csv")
        if var == "qtot":
            eflow_5y.to_csv(wd11 + f"e-flow_{scenario_label}_{iso3}.csv")

        for year in np.arange(2020, 2105, 5):
            for i in np.arange(4, -1, -1):
                final_temp = eflow[
                    pd.date_range(str(year - i) + "-01-01", periods=12, freq="ME")
                ]

            target_cols = pd.date_range(str(year) + "-01-01", periods=12, freq="ME")
            grouped_monthly = final_temp.groupby(final_temp.columns.month, axis=1).mean()
            eflow[target_cols] = pd.DataFrame(
                grouped_monthly.values, index=eflow.index, columns=target_cols
            )

            eflow_5y_m = eflow[eflow.columns[eflow.columns.year.isin(years)]].copy()

        eflow_5y_m.to_csv(wd11 + f"e-flow_{var}_5y_m_{scenario_label}_{iso3}.csv")
        return eflow_5y, eflow_5y_m

    eflow_5y_26, _ = generate_eflow_outputs(df_monthly_26, "2p6")
    eflow_5y_70, eflow_5y_m_70 = generate_eflow_outputs(df_monthly_70, "7p0")

    target_cols_2020_eflow = pd.date_range("2020-01-01", periods=12, freq="ME")
    val_2020_eflow = eflow_5y_m_70[target_cols_2020_eflow]
    val_2020_eflowy = eflow_5y_70["2020-12-31"]
    eflow_5y_70.apply(lambda x: val_2020_eflowy).to_csv(
        wd11 + f"e-flow_{var}_no_climate_{iso3}.csv"
    )

    for y in years:
        target_cols = pd.date_range(f"{y}-01-01", periods=12, freq="ME")
        eflow_5y_m_70[target_cols] = pd.DataFrame(
            val_2020_eflow.values, index=eflow_5y_m_70.index, columns=target_cols
        )

    eflow_5y_m_70.to_csv(wd11 + f"e-flow_{var}_5y_m_no_climate_{iso3}.csv")


available_variables = [
    variable
    for variable in variables
    if os.path.exists(os.path.join(wd11, f"{variable}_{cl}_{SCEN_LOW}_output.csv"))
    and os.path.exists(os.path.join(wd11, f"{variable}_{cl}_{SCEN_HIGH}_output.csv"))
]

for var in available_variables:
    process_variable(var)
