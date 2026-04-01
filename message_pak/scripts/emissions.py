import pandas as pd
import numpy as np
from itertools import product
from message_ix import make_df

def expand_grid(dictionary):
   return pd.DataFrame([row for row in product(*dictionary.values())], 
                       columns=dictionary.keys())


def bound_emissions(msgSc, nodeName, scen_name, trajectories):
    if scen_name in [
        "NDC-U", "NDC-C",
        "NDC-U-17-SSP1", "NDC-C-50-SSP1",
        "NDC-U-17-SSP2", "NDC-C-50-SSP2", 
        "NDC-U-17-SSP5", "NDC-C-50-SSP5", 
        "NDC-U-17-Acc", "NDC-C-50-Acc",
    ]:
        data = pd.read_excel(trajectories, sheet_name="GHG")
        type_year = data['Year'].tolist()
        value = np.array(data[scen_name]) * 12.0/44.0 

        dic = {
            'node': [nodeName] * len(type_year),
            'type_emission': ['TCE'] * len(type_year),
            'type_tec': ['all'] * len(type_year),
            'type_year': type_year,
            'value': value,
            'unit': ['tC'] * len(type_year)
        }

        df = pd.DataFrame(dic)
    
    else:
        data = pd.read_excel(trajectories, sheet_name="GHG")


        type_year = data['Year'].tolist()
        value = np.array(data[scen_name]) * 12.0/44.0

        # Step 3: Create dictionary for DataFrame
        dic = {
            'node': [nodeName] * len(type_year),
            'type_emission': ['TCE'] * len(type_year),
            'type_tec': ['all'] * len(type_year),
            'type_year': type_year,
            'value': value,
            'unit': ['tC'] * len(type_year)
        }

        # Step 4: Create DataFrame
        df = pd.DataFrame(dic)
        
    msgSc.add_par('bound_emission', df)

def net_zero_emissions(msgSc):

    nz_year_co2 = pd.DataFrame({
            'node': ["R12_PAK"] * 2,
            'type_emission': ['CO2_TCE'] * 2,
            'type_tec': ['all'] * 2,
            'type_year': [2060, 2070],
            'value': [0, 0],
            'unit': ['tC'] * 2
        }
    )
    msgSc.add_par("bound_emission", nz_year_co2)

    nz_year_ghg = pd.DataFrame({
            'node': ["R12_PAK"] * 2,
            'type_emission': ['TCE'] * 2,
            'type_tec': ['all'] * 2,
            'type_year': [2060, 2070],
            'value': [60, 59],
            'unit': ['tC'] * 2
        }
    )
    msgSc.add_par("bound_emission", nz_year_ghg)

    # ghg_df = make_df("bound_emission", node="R12_PAK", type_emission="TCE", type_tec="all",
    #                    type_year="cumulative", value=65, unit="tC",)
    # msgSc.add_par("bound_emission", ghg_df)


