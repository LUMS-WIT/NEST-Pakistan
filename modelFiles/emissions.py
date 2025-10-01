import pandas as pd
import numpy as np
from itertools import product
from message_ix import make_df

def expand_grid(dictionary):
   return pd.DataFrame([row for row in product(*dictionary.values())], 
                       columns=dictionary.keys())


def bound_emissions(msgSDG, nodeName, scen_name):
    if scen_name == "NDC-cond" or scen_name == "LTS" or scen_name == "NDC-uncond":
        data = pd.read_csv("D:/COMMITTED/Models/NEST-Pakistan/modelData/emissionAllocation/emissions-NDC-LTS.csv")
        type_year = data['Time'].tolist()
        value = np.array(data[scen_name]) * 12.0/44.0 # * 1000000

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
        data = pd.read_csv("D:/\COMMITTED/Models/NEST-Pakistan/modelData/emissionAllocation/EF_allocations_PC_edited.csv")

        # Step 1: Filter data for Region = 'PAK', Temperature = '2.0 deg at 67%' and 
        filtered_data = data[(data['Region'] == 'PAK') & (data['Temperature'] == '2.0 deg at 67%')]
        filtered_data = filtered_data[filtered_data['Time'].isin([2025, 2030, 2035, 2040, 2045, 2050, 2055, 2060, 2070])]

        # Step 2: Extract columns as lists
        type_year = filtered_data['Time'].tolist()
        value = np.array(filtered_data[scen_name]) * 12.0/44.0

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
        
        # Add parameter to msgSDG (this part is specific to MESSAGEix model)
    msgSDG.add_par('bound_emission', df)

def total_emiss_bound(msgSc):
    emiss_df = make_df("bound_emission", node="R12_PAK", type_emission="TCE", type_tec="all",
                       type_year="cumulative", value=78.5, unit="tC",)
    msgSc.add_par("bound_emission", emiss_df)
    nz_year_emiss = pd.DataFrame({
            'node': ["R12_PAK"] * 3,
            'type_emission': ['TCE'] * 3,
            'type_tec': ['all'] * 3,
            'type_year': [2050, 2060, 2070],
            'value': [50, 50, 46],
            'unit': ['tC'] * 3
        }
    )
    msgSc.add_par("bound_emission", nz_year_emiss)

    # nz_year_emiss = pd.DataFrame({
    #         'node': ["R12_PAK"],
    #         'type_emission': ['TCE'],
    #         'type_tec': ['all'],
    #         'type_year': ["2070"],
    #         'value': [46],
    #         'unit':[ 'tC']
    #     }
    # )
    # msgSc.add_par("bound_emission", nz_year_emiss)