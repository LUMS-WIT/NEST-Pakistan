import os
import pandas as pd

# Conversion factor from Petajoules to Gigawatt-years
PJ_TO_GWA = 277.778 / 8760

# Define the mapping of technologies to data source
TECHNOLOGIES = {
    "coal_fs": ("Industrial", "Coal, Coke & Coke Oven Gas"),
    "foil_fs": ("Industrial", "Still Gas & Petroleum Coke"),
    "foil_trp": ("Transportation", "Heavy Fuel Oil"),
    "loil_fs": ("Industrial", "LPG & Petroleum Feedstocks"),
    "loil_i": ("Industrial", "RPP"),
    "loil_rc": ("Residential and Commercial", "RPP"),
    "loil_trp": ("Transportation", ("Motor Gasoline", "Diesel", "Aviation Fuel")),
    "gas_fs": ("Industrial", "Natural_Gas"),
    "gas_rc": ("Residential and Commercial", "Natural_Gas"),
    "gas_trp": ("Transportation", "Natural_Gas")
}
SECTORS = ["Industrial", "Residential and Commercial", "Transportation"]
PROVINCES = ["Alberta", "British Columbia", "Manitoba", "Ontario", "New Brunswick",
             "Newfoundland and Labrador", "Nova Scotia", "Prince Edward Island", "Quebec", "Saskatchewan", "Yukon"]

YEARS = [2015, 2020]

results = []

base_dir = os.path.join("..", "..", "data", "End_Uses")

for province in PROVINCES:
    print(province)
    data = {}

    for sector in SECTORS:
        file_path = os.path.join(base_dir, f"end_use_demand_{province.replace(' ', '')}.xlsx")
        data[sector] = pd.read_excel(file_path, sheet_name=sector)

    for technology, (sector, rows) in TECHNOLOGIES.items():
        if isinstance(rows, tuple):
            rows = list(rows)
        elif isinstance(rows, str):
            rows = [rows]

        for year in YEARS:
            total_value_pj = sum(data[sector][data[sector]['_'].isin(rows)][str(year)])
            total_value_gwa = total_value_pj * PJ_TO_GWA
            results.append({
                "province": province,
                "technology": technology,
                "year": year,
                "value": total_value_gwa,
                "unit": "GWa"
            })

df = pd.DataFrame(results)

output_file_path = os.path.join(base_dir, "energy_usage_by_technology.csv")
df.to_csv(output_file_path, index=False)

print(f"Data processing complete and saved to {output_file_path}.")
