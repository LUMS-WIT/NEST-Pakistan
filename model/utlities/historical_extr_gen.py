import os
import pandas as pd

# These ratios were calculated by hand from the following document in the SESIT sharepoint:
# MESSAGE\calibration\provincial_sources\data_CA_provincial
RATIOS = {
    "crude_1": 0.003680875,
    "crude_2": 0.024307664,
    "crude_3": 0.007339417,
    "crude_4": 0.048467849,
    "crude_5": 0.54793723,
    "crude_6": 0.147306786,
    "crude_7": 0.220960179,
    "gas_1": 0.16338333,
    "gas_2": 0.097206152,
    "gas_3": 0.024961342,
    "gas_4": 0.118807519,
    "gas_5": 0.001047987,
    "gas_6": 0.237837468,
    "gas_7": 0.356756202,
}

YEARS = [2015, 2020]
PROVINCES = ["Alberta", "BritishColumbia", "Manitoba", "Ontario", "NewBrunswick",
             "NewfoundlandandLabrador", "NovaScotia", "PrinceEdwardIsland", "Quebec", "Saskatchewan", "Yukon"]

# Define the paths, ensure that BC_historical_calibration.xlsx
# has been added from the MESSAGE folder in the SESIT Sharepoint
input_file_path = os.path.join("..", "..", "data", "BC_historical_calibration.xlsx")
output_file_path = os.path.join("..", "..", "data", "updated_data_with_extractions.xlsx")

data = pd.read_excel(input_file_path, "historical activity")
print(data['node_loc'].unique())

new_rows = []

for province in PROVINCES:
    if province not in data['node_loc'].unique():
        print(f"Skipping {province} as it is not found in the dataset.")
        continue

    for year in YEARS:
        oil_data = data[(data['node_loc'] == province) & (data['year_act'] == year) & (data['technology'] == 'oil_extr_mpen')]
        gas_data = data[(data['node_loc'] == province) & (data['year_act'] == year) & (data['technology'] == 'gas_extr_mpen')]

        for i in range(1, 8):
            if not oil_data.empty:
                oil_row = {
                    'node_loc': province,
                    'technology': f'oil_extr_{i}',
                    'year_act': year,
                    'mode': oil_data['mode'].iloc[0],
                    'time': oil_data['time'].iloc[0],
                    'value': oil_data['value'].iloc[0] * RATIOS[f'crude_{i}'],
                    'unit': oil_data['unit'].iloc[0]
                }
                new_rows.append(oil_row)
            if not gas_data.empty:
                gas_row = {
                    'node_loc': province,
                    'technology': f'gas_extr_{i}',
                    'year_act': year,
                    'mode': gas_data['mode'].iloc[0],
                    'time': gas_data['time'].iloc[0],
                    'value': gas_data['value'].iloc[0] * RATIOS[f'gas_{i}'],
                    'unit': gas_data['unit'].iloc[0]
                }
                new_rows.append(gas_row)

if new_rows:
    new_rows_df = pd.DataFrame(new_rows)
    data = pd.concat([data, new_rows_df], ignore_index=True)

data.to_excel(output_file_path, index=False)

print(f"Data processing complete and saved to {output_file_path}.")
