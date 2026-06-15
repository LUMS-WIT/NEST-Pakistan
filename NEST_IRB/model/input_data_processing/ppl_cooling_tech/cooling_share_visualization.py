import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

sns.set(style="whitegrid")

# ------------------------------------------------
# PATHS
# ------------------------------------------------
base_input = Path(r"C:\Users\User\Desktop\lums\3rd semester\Thesis\Thesis II\Input")

regional_file = (
    base_input /
    "ppl_cooling_tech" /
    "cool_techcost" /
    "cooltech_cost_and_shares_ssp_msg_IRB.csv"
)

country_file = (
    base_input /
    "ppl_cooling_tech" /
    "cool_techcost" /
    "cooltech_cost_and_shares_country.csv"
)

excel_file = base_input / "ppl_cooling_tech" / "PLATTS_3.7.xlsx"

# ------------------------------------------------
# LOAD DATA
# ------------------------------------------------
df_regions = pd.read_csv(regional_file)
df_country = pd.read_csv(country_file)
plants = pd.read_excel(excel_file)

print("Regional file shape:", df_regions.shape)
print("Country file shape:", df_country.shape)

# ------------------------------------------------
# FIND REGION COLUMNS
# ------------------------------------------------
region_cols = [c for c in df_regions.columns if c.startswith("mix_")]

# ------------------------------------------------
# PLOT 1 — Total Cooling Shares by Region
# ------------------------------------------------
region_totals = df_regions[region_cols].sum().reset_index()
region_totals.columns = ["region", "total_share"]

plt.figure(figsize=(8,5))
sns.barplot(data=region_totals, x="region", y="total_share")
plt.title("Total Cooling Technology Shares by IRB Region")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# ------------------------------------------------
# PLOT 2 — Technology vs Region Heatmap
# ------------------------------------------------
heatmap_data = df_regions.set_index("utype")[region_cols]

plt.figure(figsize=(12,8))
sns.heatmap(heatmap_data, cmap="viridis")
plt.title("Cooling Technology Share Heatmap (IRB)")
plt.xlabel("Region")
plt.ylabel("Power Plant Technology")
plt.tight_layout()
plt.show()

# ------------------------------------------------
# PLOT 3 — Cooling Technology Frequency
# ------------------------------------------------
cooling_counts = plants["cool_group_msg"].value_counts()

plt.figure(figsize=(8,5))
sns.barplot(x=cooling_counts.index, y=cooling_counts.values)
plt.title("Cooling Technology Frequency in Dataset")
plt.ylabel("Count")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# ------------------------------------------------
# PLOT 4 — Investment Cost Distribution
# ------------------------------------------------
cost_cols = [
    "investment_million_USD_per_MW_low",
    "investment_million_USD_per_MW_mid",
    "investment_million_USD_per_MW_high"
]

plt.figure(figsize=(8,5))
sns.boxplot(data=df_regions[cost_cols])
plt.title("Investment Cost Distribution")
plt.ylabel("Million USD per MW")
plt.tight_layout()
plt.show()

# ------------------------------------------------
# PLOT 5 — Country Share Distribution
# ------------------------------------------------
country_cols = [c for c in df_country.columns if c.startswith("mix_")]
country_totals = df_country[country_cols].sum().reset_index()
country_totals.columns = ["country", "share"]

plt.figure(figsize=(8,5))
sns.barplot(data=country_totals, x="country", y="share")
plt.title("Cooling Shares by Country")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

print("\nVisualization complete.")