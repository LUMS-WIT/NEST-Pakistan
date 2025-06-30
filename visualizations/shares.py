import pandas as pd

df_lc = pd.read_csv("../modelData/historicalData/ACT_ppl_low_carbon_v3.csv")
df_fossil = pd.read_csv("../modelData/historicalData/ACT_ppl_fossil_v3.csv")
df_hydro = pd.read_csv("../modelData/historicalData/ACT_ppl_hydro_v3.csv")

df_all = pd.concat([df_lc, df_fossil, df_hydro], ignore_index=True)

low_carbon_tecs = df_lc["tec"].unique()
fossil_tecs = df_fossil["tec"].unique()
hydro_tecs = df_hydro["tec"].unique()
nuc_tecs = ["nuc_lc", "nuc_hc"]

df_all['value'] = df_all['level']

total_by_year = df_all.groupby('year_all')["value"].sum()
lc_by_year = df_all[df_all["tec"].isin(low_carbon_tecs)].groupby('year_all')["value"].sum()
hydro_by_year = df_all[df_all["tec"].isin(hydro_tecs)].groupby('year_all')["value"].sum()
fossil_by_year = df_all[df_all["tec"].isin(fossil_tecs)].groupby('year_all')["value"].sum()
nuclear_by_year = df_all[df_all["tec"].isin(nuc_tecs)].groupby('year_all')["value"].sum()

shares_df = pd.DataFrame({
    "total": total_by_year,
    "low_carbon": lc_by_year,
    "hydro": hydro_by_year,
    "fossil": fossil_by_year,
    "nuclear": nuclear_by_year,
}).fillna(0)

shares_df["share_lc"] = shares_df["low_carbon"] / shares_df["total"] * 100
shares_df["share_hydro"] = shares_df["hydro"] / shares_df["total"] * 100
shares_df["share_fossil"] = shares_df["fossil"] / shares_df["total"] * 100
shares_df["share_nuclear"] = shares_df["nuclear"] / shares_df["total"] * 100

target_years = [2025, 2030, 2035, 2040, 2045, 2050, 2055, 2060, 2070]
shares_df_filtered = shares_df.loc[target_years]

print(shares_df_filtered[["share_lc", "share_fossil", "share_hydro", "share_nuclear"]])
