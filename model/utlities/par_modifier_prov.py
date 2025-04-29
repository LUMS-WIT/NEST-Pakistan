## This script needs to be cleaned up and converted into functions which a scenario can be then parameterized with 

df = pd.read_excel(DATA /'provincial_sources/historical_import_export.xlsx')

# Select columns up to 'unit'
df = df[['node_loc', 'technology', 'year_vtg', 'value', 'unit']].rename(columns={'year_vtg': 'year_act'})

# Add 'mode' column with all values set to 'M1'
df['mode'] = 'M1'
df['unit'] ='GWa'
# Add 'time' column with values from 'year_vtg'
df['time'] = 'year'
df['node_loc'] = df['node_loc'].str.replace(' ', '')['node_loc'] = df['node_loc'].str.replace(' ', '')
df['value'] = df['value'].fillna(0)


msg.add_par('historical_activity', df)



import pandas as pd

# Sample data to replicate across Canadian provinces
data = [
    ('R11_NAM', 'elec_t_d', 1990, 'M1', 'year', 346.902),
    ('R11_NAM', 'elec_t_d', 1995, 'M1', 'year', 414.603),
    ('R11_NAM', 'elec_t_d', 2000, 'M1', 'year', 455.097),
    ('R11_NAM', 'elec_t_d', 2005, 'M1', 'year', 482.681),
    ('R11_NAM', 'elec_t_d', 2010, 'M1', 'year', 484.257),
    ('R11_NAM', 'elec_t_d', 2015, 'M1', 'year', 485.843),
    ('R11_NAM', 'elec_t_d', 2020, 'M1', 'year', 521.053)
]

# Canadian provinces and territories with no spaces in names
provinces = [
    'Alberta', 'BritishColumbia', 'Manitoba', 'NewBrunswick', 
    'NewfoundlandandLabrador', 'NovaScotia', 'Ontario', 
    'PrinceEdwardIsland', 'Quebec', 'Saskatchewan', 
    'NorthwestTerritories', 'Nunavut', 'Yukon'
]

# Create a DataFrame for the sample data
df = pd.DataFrame(data, columns=['node_loc', 'technology', 'year_act', 'mode', 'time', 'value'])

# List to store DataFrames for each province
province_dfs = []

# Replicate the data for each Canadian province
for province in provinces:
    temp_df = df.copy()
    temp_df['node_loc'] = province
    province_dfs.append(temp_df)

# Concatenate all provincial DataFrames into one
final_df = pd.concat(province_dfs, ignore_index=True)

msg.add_par('historical_activity', final_df)


# Removing import, export bounds 

# msg.check_out()
df = msg.par('initial_activity_lo')
msg.remove_par('initial_activity_lo', df)
filtered_df = df[~df['technology'].isin(['elec_imp','elec_exp'])]
msg.add_par('initial_activity_lo',filtered_df) 
# msg.check_out()
df = msg.par('initial_activity_up')
msg.remove_par('initial_activity_up', df)
filtered_df = df[~df['technology'].isin(['elec_imp','elec_exp'])]
msg.add_par('initial_activity_up',filtered_df) 

# msg.check_out()
df = msg.par('growth_activity_lo')
msg.remove_par('growth_activity_lo', df)
filtered_df = df[~df['technology'].isin(['elec_imp','elec_exp'])]
msg.add_par('growth_activity_lo',filtered_df) 

# msg.check_out()
df = msg.par('growth_activity_up')
msg.remove_par('growth_activity_up', df)
filtered_df = df[~df['technology'].isin(['elec_imp','elec_exp'])]
msg.add_par('growth_activity_up',filtered_df)

nodes = msg.set('node').tolist()

# Assuming you want to pass all nodes except 'World' and 'R11_GLB'
all_nodes = msg.set('node')
nodes_to_pass = [node for node in all_nodes if node not in ['World', 'R11_GLB']]

model_calibrate(msg, nodes)

# Relations to be removed from copying
relation_remove = ["_min", "_max", "lim_", "_pot", "min-"]
# cleanup_rel_tec(msg, nodes= nodes_to_pass, relation_remove=relation_remove)
remove_accounting = False
# Ensure DataFrame operations use 'reg' correctly
exclusion = []
relations = msg.set('relation').tolist()

if remove_accounting:
    rel_par = pd.DataFrame()
    for par in ['relation_upper', 'relation_lower', 'relation_cost']:
        # Ensure that DataFrame filtering here is correct
        df = msg.par(par)
        df = df[df['node_rel'].isin(reg)][['node_rel', 'relation']]
        rel_par = pd.concat([rel_par, df], ignore_index=True)

    rel_par = rel_par.drop_duplicates()

    rel_act = pd.DataFrame()
    for par in ['relation_new_capacity', 'relation_total_capacity', 'relation_activity']:
        df = msg.par(par)
        df = df[df['node_rel'].isin(reg)][['node_rel', 'relation']]
        rel_act = pd.concat([rel_act, df], ignore_index=True)

    rel_act = rel_act.drop_duplicates()

    exclusion = pd.concat([rel_act, rel_par]).drop_duplicates(keep=False)['relation'].tolist()
    exclusion += [r for r in relations if r not in rel_act['relation'].tolist() and r not in rel_par['relation'].tolist()]

# Add manual exclusions and process them
exclusion += ['PE_domestic_total', 'PE_import_total', 'PE_import_share', 'PE_export_total',
                'demb_limit', 'demF_limit', 'demI_limit', 'demp_limit', 'demR_limit', 'demt_limit',
                'elec_coal', 'elec_gas', 'elec_hydro', 'elec_nuclear', 'ele_nuc', 'foil_prod',
                'oil_based_elec_gen', 'gas_export', 'SO2_red_ref', 'SO2_red_synf', 'SO2_ind',
                'SO2_elec', 'SO2_import', 'SO2_r_c'] + [x for x in relation_remove if x in msg.set("relation")]

msg.check_out()
for rel in set(exclusion):
    if rel in msg.set('relation'):
        msg.remove_set('relation', rel)
        print('Relation: {} - deleted'.format(rel))

msg.commit('Remove unused elements')




### adjust imports, exports based on extraction 



data = df

# Function to adjust the export values as per the given conditions
def adjust_export_values(df, tech_extr_mpen, tech_exp):
    for location in df['node_loc'].unique():
        # Extract rows for the current location and year 2015
        loc_data = df[(df['node_loc'] == location) & (df['year_act'] == 2015)]
        # Check if both required technologies exist in the location data
        if tech_extr_mpen in loc_data['technology'].values and tech_exp in loc_data['technology'].values:
            extr_mpen_val = loc_data.loc[loc_data['technology'] == tech_extr_mpen, 'value'].values[0]
            exp_val = loc_data.loc[loc_data['technology'] == tech_exp, 'value'].values[0]
            # Adjust export value if it's greater than extraction minus penalties value
            if exp_val > extr_mpen_val:
                df.loc[(df['node_loc'] == location) & (df['technology'] == tech_exp) & (df['year_act'] == 2015), 'value'] = 0.7 * extr_mpen_val
    return df

# Adjust the values for oil, gas, and coal
data = adjust_export_values(data, 'oil_extr_mpen', 'oil_exp')
data = adjust_export_values(data, 'gas_extr_mpen', 'gas_exp')
data = adjust_export_values(data, 'coal_extr_mpen', 'coal_exp')

# Function to add the '_imp' technologies based on the provided list for each 'node_loc'
def add_imp_technologies(df, tech_prefix, tech_list):
    df_tech = df[(df['year_act'] == 2015) & (df['technology'].isin(tech_list))]
    df_imp = df_tech.groupby('node_loc').agg({'value': 'sum'}).reset_index()
    df_imp['technology'] = tech_prefix + '_imp'
    df_imp['year_act'] = 2015
    df_imp['mode'] = 'M1'  # Assuming mode is 'M1' as per the structure of the existing data
    df_imp['time'] = 'year'  # Assuming time is 'year' as per the structure of the existing data
    df_imp['unit'] = 'GWa/a'  # Assuming unit is 'GWa/a' as per the structure of the existing data
    df_imp = df_imp[['node_loc', 'technology', 'year_act', 'mode', 'time', 'value', 'unit']]
    return pd.concat([df, df_imp], ignore_index=True)

# Lists of technologies for each category to sum their values
foil_techs = ['foil_fs', 'foil_i', 'foil_ppl', 'foil_rc', 'foil_t_d', 'foil_trp']
loil_techs = ['loil_fs', 'loil_i', 'loil_ppl', 'loil_rc', 'loil_t_d', 'loil_trp']
gas_techs = ['gas_cc', 'gas_ct', 'gas_fs', 'gas_i', 'gas_ppl', 'gas_rc', 'gas_t_d', 'gas_trp']

# Add the '_imp' technologies to the main dataframe
data = add_imp_technologies(data, 'foil', foil_techs)
data = add_imp_technologies(data, 'loil', loil_techs)
data = add_imp_technologies(data, 'gas', gas_techs)


## Updated 
import pandas as pd

data = df

# Function to adjust the export values as per the given conditions for years 2015 and 2020
def adjust_export_values(df, tech_extr_mpen, tech_exp, years):
    print(f"Adjusting export values for technologies {tech_extr_mpen} and {tech_exp} for years {years}")
    for location in df['node_loc'].unique():
        for year in years:
            # Extract rows for the current location and specified year
            loc_data = df[(df['node_loc'] == location) & (df['year_act'] == year)]
            # Check if the extraction technology with penalties exists
            if tech_extr_mpen in loc_data['technology'].values:
                if tech_exp in loc_data['technology'].values:
                    extr_mpen_val = loc_data.loc[loc_data['technology'] == tech_extr_mpen, 'value'].values[0]
                    exp_val = loc_data.loc[loc_data['technology'] == tech_exp, 'value'].values[0]
                    print(f"Location: {location}, Year: {year}, Extr. Value: {extr_mpen_val}, Exp. Value: {exp_val}")
                    # Adjust export value if it's greater than extraction minus penalties value
                    if exp_val > extr_mpen_val:
                        df.loc[(df['node_loc'] == location) & (df['technology'] == tech_exp) & (df['year_act'] == year), 'value'] = 0.7 * extr_mpen_val
            else:
                # If the extraction technology with penalties doesn't exist, set export technology value to zero
                if tech_exp in loc_data['technology'].values:
                    print(f"Setting export values to zero in {location} for year {year} as no extraction penalties technology found")
                    df.loc[(df['node_loc'] == location) & (df['technology'] == tech_exp) & (df['year_act'] == year), 'value'] = 0
    
    return df

# Adjust the values for oil, gas, and coal for both 2015 and 2020
years_to_adjust = [2015, 2020]
data = adjust_export_values(data, 'oil_extr_mpen', 'oil_exp', years_to_adjust)
data = adjust_export_values(data, 'gas_extr_mpen', 'gas_exp', years_to_adjust)
data = adjust_export_values(data, 'coal_extr_mpen', 'coal_exp', years_to_adjust)

# Function to add the '_imp' technologies based on the provided list for each 'node_loc'
def add_imp_technologies(df, tech_prefix, tech_list, years):
    df_tech = df[(df['year_act'].isin(years)) & (df['technology'].isin(tech_list))]
    df_imp = df_tech.groupby(['node_loc', 'year_act']).agg({'value': 'sum'}).reset_index()
    df_imp['technology'] = tech_prefix + '_imp'
    df_imp['mode'] = 'M1'
    df_imp['time'] = 'year'
    df_imp['unit'] = 'GWa/a'
    df_imp = df_imp[['node_loc', 'technology', 'year_act', 'mode', 'time', 'value', 'unit']]
    return pd.concat([df, df_imp], ignore_index=True)

# Add the '_imp' technologies to the main dataframe for both 2015 and 2020
data = add_imp_technologies(data, 'foil', foil_techs, years_to_adjust)
data = add_imp_technologies(data, 'loil', loil_techs, years_to_adjust)
data = add_imp_technologies(data, 'gas', gas_techs, years_to_adjust)

# List of technologies for each category to sum their values
foil_techs = ['foil_fs', 'foil_i', 'foil_ppl', 'foil_rc', 'foil_t_d', 'foil_trp']
loil_techs = ['loil_fs', 'loil_i', 'loil_ppl', 'loil_rc', 'loil_t_d', 'loil_trp']
gas_techs = ['gas_cc', 'gas_ct', 'gas_fs', 'gas_i', 'gas_ppl', 'gas_rc', 'gas_t_d', 'gas_trp']


import pandas as pd

data = df

# Function to add the oil_imp technology with the calculated value per each region
def add_oil_imp(df, foil_techs, loil_techs, years):
    for year in years:
        # Assuming that oil_imp is the sum of foil_techs and loil_techs for the same location and year
        tech_imp_list = foil_techs + loil_techs
        oil_imp_data = df[(df['year_act'] == year) & (df['technology'].isin(tech_imp_list))].copy()
        oil_imp_sum = oil_imp_data.groupby(['node_loc']).agg({'value': 'sum'}).reset_index()
        oil_imp_sum['technology'] = 'oil_imp'
        oil_imp_sum['year_act'] = year
        oil_imp_sum['mode'] = 'M1'  # Replace with actual mode if available
        oil_imp_sum['time'] = 'year'  # Replace with actual time if available
        oil_imp_sum['unit'] = 'GWa/a'  # Replace with actual unit if available
        
        # Ensure oil_imp is greater than the sum of foil and loil technologies
        oil_imp_sum['value'] *= (1 / (1 - 0.65))
        
        # Add oil_imp to the main dataframe
        df = pd.concat([df, oil_imp_sum], ignore_index=True)
    return df

# Function to adjust the import values as per the given conditions for specified years
def adjust_import_values(df, foil_techs, loil_techs, oil_imp_share, years):
    for year in years:
        for location in df['node_loc'].unique():
            # Calculate total import value for foil and loil technologies
            total_techs_value = df[(df['node_loc'] == location) & (df['year_act'] == year) & (df['technology'].isin(foil_techs + loil_techs))]['value'].sum()

            # Calculate the new oil_imp value ensuring it is greater than the sum of foil and loil technologies
            new_oil_imp_value = total_techs_value / (1 - oil_imp_share)
            df.loc[(df['node_loc'] == location) & (df['technology'] == 'oil_imp') & (df['year_act'] == year), 'value'] = new_oil_imp_value

            # Calculate and set the foil_imp and loil_imp values
            foil_loil_imp_each_share = (new_oil_imp_value * oil_imp_share) / 2  # Splitting the oil_imp share equally
            for tech_imp in ['foil_imp', 'loil_imp']:
                df.loc[(df['node_loc'] == location) & (df['technology'] == tech_imp) & (df['year_act'] == year), 'value'] = foil_loil_imp_each_share

    return df

# Lists of technologies for each category
foil_techs = ['foil_fs', 'foil_i', 'foil_ppl', 'foil_rc', 'foil_t_d', 'foil_trp']
loil_techs = ['loil_fs', 'loil_i', 'loil_ppl', 'loil_rc', 'loil_t_d', 'loil_trp']

# Add the oil_imp technology to the dataframe for both 2015 and 2020
years_to_adjust = [2015, 2020]
data = add_oil_imp(data, foil_techs, loil_techs, years_to_adjust)

# Share of oil_imp in total imports
oil_imp_share = 0.65

# Adjust the values for oil imports for both 2015 and 2020
data = adjust_import_values(data, foil_techs, loil_techs, oil_imp_share, years_to_adjust)


#### read in population data and resample it to 5 year
#TODO: Convert this into function and separate script
# Step 2: Rename 'Unnamed: 0' to 'Year' and convert 'Year' to datetime
data.rename(columns={'Unnamed: 0': 'Year'}, inplace=True)
data['Year'] = pd.to_datetime(data['Year'], format='%Y')

# Step 3: Pivot the dataframe to long format
pivoted_data = data.melt(id_vars=['Year'], var_name='Province', value_name='Population')

# Step 4: Set 'Year' as index and sort the index
pivoted_data.set_index('Year', inplace=True)
pivoted_data.sort_index(inplace=True)

# Step 5: Forward fill and backward fill to handle missing values
pivoted_data['Population'] = pivoted_data['Population'].ffill().bfill()

# Step 6: Resample and interpolate
resampled_data = pivoted_data.groupby('Province').resample('5A').mean().interpolate(method='linear')

# Step 7: Reset the index to have 'Year' as a column again
resampled_data = resampled_data.reset_index()

# Change the datetime format to the required format (e.g., 2020, 2025, etc.)

# Update the year values to the required format
resampled_data['Year'] = resampled_data['Year'].dt.year - 1

resampled_data.to_csv(DATA / 'pop_gdp_process/pop_messageca_prov.csv', index=False)


# Using pandas.concat instead of append to add new rows
def ensure_tech_existence(df, year_source, year_target):
    # Get unique combinations of node_loc and technology for the source year
    tech_combinations = df[df['year_act'] == year_source][['node_loc', 'technology']].drop_duplicates()
    new_rows = []
    
    for index, row in tech_combinations.iterrows():
        location = row['node_loc']
        technology = row['technology']
        
        # Check if this combination exists in the target year
        if not ((df['node_loc'] == location) & (df['technology'] == technology) & (df['year_act'] == year_target)).any():
            # Get the value from the source year
            value_2015 = df.loc[(df['node_loc'] == location) & (df['technology'] == technology) & (df['year_act'] == year_source), 'value'].values[0]
            # Add a new row with 1.1 times the value from 2015
            new_row = {
                'node_loc': location,
                'technology': technology,
                'year_act': year_target,
                'mode': 'M1',  # Assuming mode, time, and unit are the same
                'time': 'year',
                'value': 1.1 * value_2015,
                'unit': df.loc[(df['node_loc'] == location) & (df['technology'] == technology) & (df['year_act'] == year_source), 'unit'].values[0]
            }
            new_rows.append(new_row)
    
    new_df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
    
    return new_df

# Ensure all technologies in 2015 exist in 2020
data = ensure_tech_existence(data, 2015, 2020)

# Adjust the values for gas, oil, and coal for both 2015 and 2020
years_to_adjust = [2015, 2020]
data = adjust_values(data, 'gas_extr_mpen', 'gas_exp', 'gas_imp', gas_techs, years_to_adjust)
data = adjust_values(data, 'oil_extr_mpen', 'oil_exp', 'oil_imp', loil_techs, years_to_adjust)
data = adjust_values(data, 'coal_extr_mpen', 'coal_exp', 'coal_imp', coal_techs, years_to_adjust)

# Display the first few rows of the updated dataframe to verify the changes
data.head()
