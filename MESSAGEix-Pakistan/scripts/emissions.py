import pandas as pd
import numpy as np


def bound_emissions(msgSc, nodeName, scen_name, trajectories):
    data = pd.read_excel(trajectories, sheet_name="GHG")
    type_year = data['Year'].tolist()
    value = np.array(data[scen_name]) * 12.0/44.0

    df = pd.DataFrame({
        'node': [nodeName] * len(type_year),
        'type_emission': ['TCE'] * len(type_year),
        'type_tec': ['all'] * len(type_year),
        'type_year': type_year,
        'value': value,
        'unit': ['tC'] * len(type_year)
    })

    msgSc.add_par('bound_emission', df)

def net_zero_emissions(msgSc):

    nz_all_co2 = pd.DataFrame({
            'node': ["R12_PAK"] * 8,
            'type_emission': ['CO2_TCE'] * 8,
            'type_tec': ['all'] * 8,
            'type_year': [2030, 2035, 2040, 2045, 2050, 2055, 2060, 2070],
            'value': [54.28, 49.64, 41.46, 30.28, 16.01, 33, 33, 33],
            'unit': ['tC'] * 8
        }
    )
    msgSc.add_par("bound_emission", nz_all_co2)

    nz_all_ghg = pd.DataFrame({
            'node': ["R12_PAK"] * 8,
            'type_emission': ['TCE'] * 8,
            'type_tec': ['all'] * 8,
            'type_year': [2030, 2035, 2040, 2045, 2050, 2055, 2060, 2070],
            'value': [66, 61.37, 53.46, 42.28, 28, 57, 57, 57],
            'unit': ['tC'] * 8
        }
    )
    msgSc.add_par("bound_emission", nz_all_ghg)

    nz_trp_co2 = pd.DataFrame({
            'node': ["R12_PAK"] * 6,
            'type_emission': ['TCE_CO2_trp'] * 6,
            'type_tec': ['all'] * 6,
            'type_year': [2040, 2045, 2050, 2055, 2060, 2070],
            'value': [7.5, 4.5, 2.1, 0.5, 0, 0],
            'unit': ['tC'] * 6
        }
    )
    msgSc.add_par("bound_emission", nz_trp_co2)

    nz_rc_co2 = pd.DataFrame({
            'node': ["R12_PAK"] * 6,
            'type_emission': ['TCE_CO2_r_c'] * 6,
            'type_tec': ['all'] * 6,
            'type_year': [2040, 2045, 2050, 2055, 2060, 2070],
            'value': [8.5, 5, 1.5, 0, 0, 0],
            'unit': ['tC'] * 6
        }
    )
    msgSc.add_par("bound_emission", nz_rc_co2)

    nz_ind_co2 = pd.DataFrame({
            'node': ["R12_PAK"] * 6,
            'type_emission': ['TCE_CO2_ind'] * 6,
            'type_tec': ['all'] * 6,
            'type_year': [2040, 2045, 2050, 2055, 2060, 2070],
            'value': [12, 12.3, 12.5, 13.5, 15.2, 21],
            'unit': ['tC'] * 6
        }
    )
    msgSc.add_par("bound_emission", nz_ind_co2)
