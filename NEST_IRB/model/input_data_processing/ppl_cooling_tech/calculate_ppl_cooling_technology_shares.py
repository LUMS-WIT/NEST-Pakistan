import pandas as pd
import numpy as np
import yaml
from pathlib import Path

pd.options.mode.chained_assignment = None

# ------------------------------------------------
# PATHS
# ------------------------------------------------
base_input = Path(r"C:\Users\User\Desktop\lums\3rd semester\Thesis\Thesis II\Input")

excel_path = base_input / "ppl_cooling_tech" / "PLATTS_3.7.xlsx"

cooltech_csv_path = (
    base_input /
    "ppl_cooling_tech" /
    "cool_techcost" /
    "cooltech_cost_and_shares_ssp_msg.csv"
)

# ------------------------------------------------
# LOAD POWER PLANT DATA
# ------------------------------------------------
all_units = pd.read_excel(excel_path)

all_units_df = all_units[
    [
        "UNIT",
        "STATUS",
        "ISO",
        "msgregion",
        "msg_combo2",
        "cool_group_msg",
        "MW_x",
        "WW",
        "WC",
        "lat",
        "long"
    ]
].copy()

# ------------------------------------------------
# LOOP FOR REGION
# ------------------------------------------------
for reg in ["IRB"]:

    print("\nProcessing region:", reg)

    # ----------------------------------------------
    # FILTER OPERATIONAL PLANTS
    # ----------------------------------------------
    cooling_plants = (
        all_units_df[
            (all_units_df["STATUS"] == "OPR") &
            (~all_units_df["cool_group_msg"].isin(["CHP", "NCN"])) &
            (all_units_df["cool_group_msg"].notna())
        ]
        .rename(columns={
            "msg_combo2": "utype",
            "cool_group_msg": "cooling"
        })
        .copy()
    )

    # ----------------------------------------------
    # LOAD YAML REGION FILE
    # ----------------------------------------------
    yaml_file = base_input / "node" / f"{reg}.yaml"

    if not yaml_file.exists():
        yaml_file = base_input / f"{reg}.yaml"

    print("Using YAML:", yaml_file)

    with open(yaml_file, "r", encoding="utf-8") as f:
        from_yaml = yaml.safe_load(f)

    # ----------------------------------------------
    # CREATE REGION → ISO MAPPING
    # ----------------------------------------------
    reg_map = []

    for region_name, data in from_yaml.items():

        if region_name == "World":
            continue

        children = data.get("child", [])

        for iso in children:
            reg_map.append({
                "msgregion": region_name,
                "ISO": iso
            })

    reg_map_df = pd.DataFrame(reg_map)

    print("Region mapping size:", reg_map_df.shape)

    # ----------------------------------------------
    # MERGE REGION INFORMATION
    # ----------------------------------------------
    cooling_plants = (
        cooling_plants
        .drop(columns=["msgregion"], errors="ignore")
        .merge(reg_map_df, on="ISO", how="left")
    )

    # ----------------------------------------------
    # FILTER TO IRB COUNTRIES ONLY
    # ----------------------------------------------
    unmapped = cooling_plants["msgregion"].isna().sum()
    print("Plants without region:", unmapped)

    cooling_plants = cooling_plants[~cooling_plants["msgregion"].isna()].copy()

    print("Plants used in IRB model:", len(cooling_plants))

    print("\nCountry distribution:")
    print(cooling_plants["ISO"].value_counts())

    # ------------------------------------------------
    # LOAD COST DATA
    # ------------------------------------------------
    cooltech_cost_shares = pd.read_csv(cooltech_csv_path)

    # ------------------------------------------------
    # CALCULATE SHARES BY REGION
    # ------------------------------------------------
    shares_msg = (
        cooling_plants
        .groupby(["utype", "cooling", "msgregion"])["MW_x"]
        .sum()
        .reset_index()
    )

    shares_msg["cap_reg_unit"] = (
        shares_msg
        .groupby(["utype", "msgregion"])["MW_x"]
        .transform("sum")
    )

    shares_msg["shares"] = (
        shares_msg["MW_x"] /
        shares_msg["cap_reg_unit"]
    )

    shares_msg = shares_msg[
        ["utype", "cooling", "msgregion", "shares"]
    ]

    shares_msg = shares_msg.pivot_table(
        index=["utype", "cooling"],
        columns="msgregion",
        values="shares",
        fill_value=0
    ).reset_index()

    # ----------------------------------------------
    # RENAME REGION COLUMNS
    # ----------------------------------------------
    region_cols = [
        c for c in shares_msg.columns
        if c not in ["utype", "cooling"]
    ]

    shares_msg.rename(
        columns={c: f"mix_{c}" for c in region_cols},
        inplace=True
    )

    shares_msg["utype_pl"] = shares_msg["utype"]

    # ------------------------------------------------
    # TECHNOLOGY MAPPING
    # ------------------------------------------------
    shares_msg["match"] = shares_msg["utype"].str.replace(
        r"_.*", "", regex=True
    )

    platts_types = (
        shares_msg[["utype", "match"]]
        .groupby("match")
        .first()
        .reset_index()
        .rename(columns={"utype": "utype_pl"})
    )

    map_all_types = (
        cooltech_cost_shares[["utype", "cooling"]]
        .copy()
    )

    map_all_types["match"] = map_all_types["utype"].str.replace(
        r"_.*", "", regex=True
    )

    map_all_types = (
        map_all_types
        .merge(platts_types, on="match", how="left")
        .drop(columns=["match"])
        .dropna()
        .drop_duplicates()
    )

    # ------------------------------------------------
    # CSP EXPANSION
    # ------------------------------------------------
    cool_tecs = map_all_types["cooling"].unique()

    csp_rows = []

    for csp in ["csp_sm1_res", "csp_sm3_res"]:

        for cool in cool_tecs:
            csp_rows.append({
                "utype": csp,
                "cooling": cool,
                "utype_pl": "solar_th_ppl"
            })

        for i in range(1, 8):
            for cool in cool_tecs:
                csp_rows.append({
                    "utype": f"{csp}{i}",
                    "cooling": cool,
                    "utype_pl": "solar_th_ppl"
                })

    csp_map = pd.DataFrame(csp_rows)

    map_all_types = pd.concat(
        [map_all_types, csp_map],
        ignore_index=True
    )

    # ------------------------------------------------
    # ADD MISSING SHARES
    # ------------------------------------------------
    missing = map_all_types[
        ~map_all_types["utype"].isin(shares_msg["utype"])
    ]

    missing = (
        missing
        .merge(
            shares_msg.drop(columns=["utype"]),
            on=["utype_pl", "cooling"],
            how="left"
        )
        .drop(columns=["utype_pl"])
    )

    all_shares = pd.concat(
        [shares_msg, missing],
        ignore_index=True
    ).fillna(0)

    # ------------------------------------------------
    # MERGE COSTS
    # ------------------------------------------------
    cost_cols = [
        "investment_million_USD_per_MW_low",
        "investment_million_USD_per_MW_mid",
        "investment_million_USD_per_MW_high"
    ]

    cooltech_final = (
        cooltech_cost_shares[
            ["utype", "cooling"] + cost_cols
        ]
        .merge(all_shares, on=["utype", "cooling"], how="left")
        .fillna(0)
    )

    # ------------------------------------------------
    # ENSURE SHARES NOT ALL ZERO
    # ------------------------------------------------
    mix_cols = [
        c for c in cooltech_final.columns
        if c.startswith("mix_")
    ]

    long_df = cooltech_final.melt(
        id_vars=["utype", "cooling"] + cost_cols,
        value_vars=mix_cols,
        var_name="msgregion",
        value_name="shares"
    )

    long_df["max_shares"] = (
        long_df
        .groupby(["utype", "msgregion"])["shares"]
        .transform("max")
    )

    idx = long_df.groupby("utype")["shares"].idxmax()

    main_tec = long_df.loc[idx][["utype", "cooling"]]

    main_tec.rename(
        columns={"cooling": "main_tec_gbl"},
        inplace=True
    )

    long_df = long_df.merge(main_tec, on="utype")

    long_df["shares"] = np.where(
        (long_df["max_shares"] == 0) &
        (long_df["cooling"] == long_df["main_tec_gbl"]),
        1,
        long_df["shares"]
    )

    final_df = (
        long_df
        .drop(columns=["max_shares", "main_tec_gbl"])
        .pivot_table(
            index=["utype", "cooling"] + cost_cols,
            columns="msgregion",
            values="shares",
            fill_value=0
        )
        .reset_index()
    )
# ------------------------------------------------
# CREATE MESSAGE-STYLE OUTPUT (REGION × TIME)
# ------------------------------------------------

    # Example time factors (replace with real MESSAGE data later)
    time_factors = pd.DataFrame({
        "year": ["2025s", "2050s", "2070s"],
        "factor": [1.0, 0.98, 0.95]
    })

    # ----------------------------------------------
    # GET REGION COLUMNS DYNAMICALLY
    # ----------------------------------------------
    region_cols = [c for c in final_df.columns if c.startswith("mix_")]

    # Map: mix_R11_AFR → R11_AFR
    region_map = {col: col.replace("mix_", "") for col in region_cols}

    # ----------------------------------------------
    # CALCULATE AGGREGATED VALUES
    # ----------------------------------------------
    results = []

    for col, region_name in region_map.items():

        for _, row in time_factors.iterrows():
            year = row["year"]
            factor = row["factor"]

            # weighted aggregation
            value = (final_df[col] * factor).sum()

            results.append({
                "node": region_name,
                "year": year,
                "value": value
            })

    result_df = pd.DataFrame(results)

    # ----------------------------------------------
    # PIVOT TO FINAL FORMAT
    # ----------------------------------------------
    final_message_output = (
        result_df
        .pivot(index="node", columns="year", values="value")
        .reset_index()
    )

    # Optional: sort regions nicely
    final_message_output = final_message_output.sort_values("node")

    # ----------------------------------------------
    # SAVE OUTPUT (IRB SPECIFIC)
    # ----------------------------------------------
    output_path = (
        base_input /
        "ppl_cooling_tech" /
        "cool_techcost" /
        f"power_plant_cooling_impact_MESSAGE_{reg}.csv"
    )

    final_message_output.to_csv(output_path, index=False)

    print("\nMESSAGE-style regional output created successfully!")
    print(final_message_output.head())



#     # ------------------------------------------------
#     # SAVE OUTPUT
#     # ------------------------------------------------
#     output_path = (
#         base_input /
#         "ppl_cooling_tech" /
#         "cool_techcost" /
#         f"cooltech_cost_and_shares_ssp_msg_{reg}.csv"
#     )

#     final_df.to_csv(output_path, index=False)

# # ------------------------------------------------
# # COUNTRY LEVEL SHARES
# # ------------------------------------------------
# shares_country = (
#     cooling_plants
#     .groupby(["utype", "cooling", "ISO"])["MW_x"]
#     .sum()
#     .reset_index()
# )

# shares_country["cap_reg_unit"] = (
#     shares_country
#     .groupby(["utype", "ISO"])["MW_x"]
#     .transform("sum")
# )

# shares_country["shares"] = (
#     shares_country["MW_x"] /
#     shares_country["cap_reg_unit"]
# )

# shares_country = shares_country.pivot_table(
#     index=["utype", "cooling"],
#     columns="ISO",
#     values="shares",
#     fill_value=0
# ).reset_index()

# shares_country.rename(
#     columns={
#         c: f"mix_{c}"
#         for c in shares_country.columns
#         if c not in ["utype", "cooling"]
#     },
#     inplace=True
# )

# country_output = (
#     base_input /
#     "ppl_cooling_tech" /
#     "cool_techcost" /
#     "cooltech_cost_and_shares_country.csv"
# )

# shares_country.to_csv(country_output, index=False)

# print("\nProcessing completed successfully.")