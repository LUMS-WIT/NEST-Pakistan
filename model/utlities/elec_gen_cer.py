import pandas as pd

def add_elec_gen_cer():
    #TODO improve the function to work with any model.
    """ Process electricity generation data from the Canadian Energy Regulator (CER)
      to add historical activity to the model."""
    data = pd.read_csv('data/elec_gen_cer.csv')
    # Define the region renaming map and desired region format
    region_rename_map = {
        'NEWFOUNDLAND AND LABRADOR': 'NewfoundlandandLabrador',
        'BRITISH COLUMBIA': 'BritishColumbia',
        'PRINCE EDWARD ISLAND': 'PrinceEdwardIsland',
        'NORTHWEST TERRITORIES': 'NorthwestTerritories',
        'YUKON': 'Yukon',
        'NOVA SCOTIA': 'NovaScotia',
        'NEW BRUNSWICK': 'NewBrunswick',
        'ONTARIO': 'Ontario',
        'QUEBEC': 'Quebec',
        'ALBERTA': 'Alberta',
        'SASKATCHEWAN': 'Saskatchewan',
        'MANITOBA': 'Manitoba',
        'NUNAVUT': 'Nunavut'
    }

    # Rename regions
    data['region'] = data['region'].str.upper().map(region_rename_map)


    # Define the region renaming map and desired region format
    tech_rename_map = {
        'OIL': 'oil_ppl',
        'NATURAL GAS': 'gas_ppl',
        'SOLAR (DISTRIBUTED)': 'solar_rc',
        'SOLAR (UTILITY SCALE)': 'solar_pv_ppl',
        'BIOENERGY': 'bio_ppl',
        'COAL & COKE': 'coal_ppl',
        'URANIUM': 'nuc_hc',
        'HYDRO': 'hydro',
        'COAL WITH CCUS': 'coal_adv_ccs',
        'ONSHORE WIND':'wind_ppl',
        'URANIUM SMR':'nuc_lc'
        
    }

    # Rename regions
    data['source'] = data['source'].str.upper().map(tech_rename_map)

    # Filter for 5-year timesteps starting at 2020
    # Replace 2023 with 2020 and exclude existing 2020 entries
    data = data[(data['year'] % 5 == 0) | (data['year'] == 2023)]
    data.loc[data['year'] == 2023, 'year'] = 2020
    # Exclude existing 2020 entries that weren't modified
    data = data.drop_duplicates(subset=['region', 'year', 'scenario', 'source'], keep='last')

    data.rename(columns={'source': 'technology', 'region': 'node_loc', 'year': 'year_act'}, inplace=True)
    data.drop(columns = ['scenario','dataset'], inplace=True)
    data['value'] = data['value'] / (8760)
    data['unit'] = 'GWa/a'
    data['mode'] ='M1'
    data['time'] = 'year'

    # Step 1: Filter the dataset for the year 2050 to get the reference values
    data_2050 = data[data['year_act'] == 2050]

    # Step 2: Create new rows for 2055 and 2060 using the 2050 values
    data_extended = pd.concat([
        data,
        data_2050.assign(year_act=2055),
        data_2050.assign(year_act=2060)
    ])

    # Step 3: Sort the extended dataset by `node_loc` and `year_act` for clarity
    data_extended = data_extended.sort_values(by=['node_loc', 'year_act']).reset_index(drop=True)

    return data_extended






