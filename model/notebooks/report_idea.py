df1 = pd.read_excel('/Users/muhammadawais/Documents/GitHub/message-ix-canada/model/output/MESSAGEix-CA_baseline.xlsx')
df1['Scenario'] = 'BAU'
df2 = pd.read_excel('/Users/muhammadawais/Documents/GitHub/message-ix-canada/model/output/MESSAGEix-CA_netzero.xlsx')
df2['Scenario'] = 'NZ'
df3 = pd.read_excel('/Users/muhammadawais/Documents/GitHub/message-ix-canada/model/output/MESSAGEix-CA_netzero_opt.xlsx')
df3['Scenario'] = 'NZ-OPT'
df4 = pd.read_excel('/Users/muhammadawais/Documents/GitHub/message-ix-canada/model/output/MESSAGEix-CA_netzero_opt.xlsx')
df4['Scenario'] = 'NZ-PES'
df = pd.concat([df1,df2,df3,df4])


# Convert only the negative values in the 'value' column to their absolute values
# Select only the columns from 2020 to 2060 and apply the abs() function to make values positive
df.loc[:, 2020:2060] = df.loc[:, 2020:2060].abs()
df = df.dropna(subset=['Region'])
# df = df.drop_duplicates(subset=  ['Model',   'Region', 'Scenario',
#            'Unit', 'Variable'])
df = df[~df['Variable'].isin(var_lis)]
df_pyam = pyam.IamDataFrame(df)

var_lis = [
'Emissions|CO2',
'Emissions|CO2|AFOLU',
'Emissions|CO2|Energy',
'Emissions|CO2|Industrial Processes',
'Emissions|CO2|Natural',
'Emissions|CO2|Product Use',
'Emissions|CO2|Waste',
'Emissions|CO2|AFOLU|Agriculture and Biomass Burning',
'Emissions|CO2|AFOLU|Agriculture',
'Emissions|CO2|AFOLU|Biomass Burning',
'Emissions|CO2|Energy:',
'Emissions|CO2|Energy|Supply',
'Emissions|CO2|Energy|Demand',
'Emissions|CO2|Energy|Demand|Residential and Commercial and AFOFI'
'Emissions|CO2|Energy|Demand|AFOFI',
'Emissions|CO2|Energy|Demand|Residential and Commercial',
'Emissions|CO2|Energy|Demand|Transportation|Rail and Domestic Shipping',
'Emissions|CO2|Energy|Demand|Transportation|Rail',
'Emissions|CO2|Energy|Demand|Transportation|Shipping|Domestic',
'Emissions|CO2|Energy|Demand|Transportation|Road Rail and Domestic Shipping',
'Emissions|CO2|Energy|Demand|Transportation|Rail',
'Emissions|CO2|Energy|Demand|Transportation|Road',
'Emissions|CO2|Energy|Demand|Transportation|Shipping|Domestic',
'Emissions|CO2|Energy|Supply|Electricity and Heat',
'Emissions|CO2|Energy|Supply',
'Emissions|CO2|Energy|Supply|Solids',
'Emissions|CO2|Energy|Supply|Liquids',
'Emissions|CO2|Energy|Supply|Gases',
'Emissions|CO2|Energy|Supply|Liquids|Fugitive',
'Emissions|CO2|Energy|Supply|Liquids|Combustion',
'Emissions|CO2|Energy|Supply|Gases|Biomass|Combustion',
'Emissions|CO2|Energy|Supply|Gases|Coal|Combustion',
'Emissions|CO2|Energy|Supply|Gases|Extraction|Combustion',
'Emissions|CO2|Energy|Supply|Gases|Hydrogen|Combustion',
'Emissions|CO2|Energy|Supply|Gases|Natural Gas|Combustion',
'Emissions|CO2|Energy|Supply|Gases|Transportation|Combustion',
'Emissions|CO2|Energy|Supply|Gases|Fugitive',
'Emissions|CO2|Energy|Supply|Liquids|Biomass',
'Emissions|CO2|Energy|Supply|Liquids|Coal',
'Emissions|CO2|Energy|Supply|Liquids|Extraction',
'Emissions|CO2|Energy|Supply|Liquids|Natural Gas',
'Emissions|CO2|Energy|Supply|Liquids|Oil',
'Emissions|CO2|Energy|Supply|Liquids|Transportation',
'Emissions|CO2|Energy|Supply|Solids|Biomass',
'Emissions|CO2|Energy|Supply|Solids|Coal',
'Emissions|CO2|Energy|Supply|Solids|Extraction',
'Emissions|CO2|Energy|Supply|Solids|Transportation',
'Emissions|CO2|Energy|Supply|Solids and Other Fugitive:',
'Emissions|CO2|Energy|Supply|Solids|Fugitive',
'Emissions|CO2|Fossil Fuels and Industry',
'Emissions|CO2|Energy',
'Emissions|CO2|Industrial Processes',
'Emissions|CO2|Industrial Processes|Metals and Minerals',
'Emissions|CO2|Industrial Processes|Non-Ferrous Metals',
'Emissions|CO2|Industrial Processes|Non-Metallic Minerals',
'Emissions|CO2|Industrial Processes|Iron and Steel',
'Emissions|CO2|Energy|Supply|Solids|Combustion',
'Final Energy',
'Final Energy|Industry',
'Final Energy|Residential and Commercial',
'Final Energy|Transportation',
'Final Energy|Electricity|Solar',
'Final Energy|Residential and Commercial|Electricity|Solar',
'Final Energy|Industry|Electricity|Solar',
'Final Energy|Liquids',
'Final Energy|Liquids|Biomass',
'Final Energy|Liquids|Coal',
'Final Energy|Liquids|Gas',
'Final Energy|Liquids|Oil',
'Final Energy|Solar',
'Final Energy|Solids',
'Final Energy|Solids',
'Final Energy|Solids|Biomass',
'Final Energy|Solids|Coal',
'Final Energy|Solids|Biomass|Traditional',
'Investment|Energy Supply|Electricity|Non-Biomass Renewables',
'Primary Energy',
'Primary Energy|Biomass',
'Primary Energy|Coal',
'Primary Energy|Gas',
'Primary Energy|Biomass|Electricity',
'Primary Energy|Biomass|Electricity|w/ CCS',
'Primary Energy|Biomass|Electricity|w/o CCS',
'Primary Energy|Coal|Electricity',
'Primary Energy|Coal|Electricity|w/ CCS',
'Primary Energy|Coal|Electricity|w/o CCS',
'Primary Energy|Fossil',
'Primary Energy|Fossil|w/ CCS',
'Primary Energy|Fossil|w/ CCS',
'Primary Energy|Gas|Electricity',
'Primary Energy|Gas|Electricity|w/ CCS',
'Primary Energy|Gas|Electricity|w/o CCS',
'Primary Energy|Oil',
'Secondary Energy|Electricity|Fossil|w/ CCS',
'Secondary Energy|Electricity|Fossil|w/o CCS',
'Secondary Energy|Electricity|Non-Biomass Renewables',
'Secondary Energy|Electricity',
'Secondary Energy|Electricity|Biomass',
'Secondary Energy|Electricity|Coal',
'Secondary Energy|Electricity|Gas',
# 'Secondary Energy|Electricity|Geothermal',
# 'Secondary Energy|Electricity|Hydro',
'Secondary Energy|Electricity|Oil',
'Secondary Energy|Electricity|Fossil',
'Secondary Energy|Electricity|Coal',
'Secondary Energy|Electricity|Gas',
'Secondary Energy|Electricity|Oil',
'Secondary Energy|Hydrogen|Fossil',
'Secondary Energy|Hydrogen|Coal',
'Secondary Energy|Hydrogen|Gas',
'Secondary Energy|Hydrogen|Oil',
'Secondary Energy|Liquids|Fossil',
'Secondary Energy|Liquids|Coal',
'Secondary Energy|Liquids|Gas',
'Secondary Energy|Liquids|Oil',
'Resource|Extraction',
'Resource|Extraction|Coal',
'Resource|Extraction|Gas',
'Resource|Extraction|Oil',
'Investment|Energy Supply|Electricity|Non-fossil',
'Investment|Energy Supply|Extraction|Fossil',
'Secondary Energy|Hydrogen|Fossil|w/ CCS',
'Secondary Energy|Hydrogen|Fossil|w/o CCS',
'Carbon Sequestration|CCS|Fossil',
'Carbon Sequestration|CCS|Biomass',
'Secondary Energy|Liquids|Fossil|w/o CCS',
'Secondary Energy|Liquids|Fossil|w/ CCS',
'Secondary Energy|Hydrogen|Fossil|w/o CCS',
'Secondary Energy|Hydrogen|Fossil|w/ CCS',
'Primary Energy|Non-Biomass Renewables',
'Final Energy|Solids'
'Final Energy|Solids|Biomass'
'Final Energy|Solids|Coal',
'Carbon Sequestration|CCS',
'Final Energy|Liquids',
'Final Energy|Liquids|Biomass',
'Final Energy|Liquids|Coal',
'Final Energy|Liquids|Gas',
'Final Energy|Liquids|Oil',
'Final Energy',
'Final Energy|Solar',
'Final Energy|Non-Energy Use',
'Final Energy|Solids|Biomass|Traditional',
'Final Energy|Electricity',
 'Final Energy|Gases',
 'Final Energy|Heat',
 'Final Energy|Hydrogen',
 'Investment|Energy Supply|Electricity|Fossil'
'Resource|Extraction'
'Resource|Extraction|Coal',
'Resource|Extraction|Gas',
'Resource|Extraction|Oil',
'Final Energy|Residential and Commercial|Solids',
'Final Energy|Residential and Commercial|Liquids',
'Final Energy|Transportation|Liquids',
'Final Energy|Industry|Liquids',
'Final Energy|Industry|Solids',
'Primary Energy|Biomass|Gases',
'Primary Energy|Biomass|Hydrogen',
'Primary Energy|Biomass|Liquids',
'Primary Energy|Biomass|Solids',
'Primary Energy|Biomass|Traditional',
'Primary Energy|Coal|Gases',
'Primary Energy|Coal|Hydrogen',
'Primary Energy|Coal|Liquids',
'Primary Energy|Coal|Solids',
'Primary Energy|Gas|Gases',
'Primary Energy|Gas|Hydrogen',
'Primary Energy|Gas|Liquids',
'Primary Energy|Gas|Solids',
'Primary Energy|Oil|Electricity',
'Primary Energy|Oil|Electricity|w/ CCS',
'Primary Energy|Oil|Electricity|w/o CCS',
'Primary Energy|Oil|Gases',
'Primary Energy|Oil|Hydrogen',
'Primary Energy|Oil|Liquids',
'Primary Energy|Oil|Solids',
'Investment|Energy Supply',
'Investment',
'Capacity|Electricity',
'Capacity|Electricity|Biomass|w/ CCS|1',
'Capacity|Electricity|Biomass|w/ CCS|2',
'Capacity|Electricity|Biomass|w/o CCS|1',
'Capacity|Electricity|Biomass|w/o CCS|2',
"Capacity|Electricity|Coal|w/o CCS|1",
"Capacity|Electricity|Coal|w/o CCS|2",
"Capacity|Electricity|Coal|w/o CCS|3",
"Capacity|Electricity|Coal|w/o CCS|4",
"Capacity|Electricity|Gas|w/ CCS|1",
"Capacity|Electricity|Gas|w/ CCS|2",
"Capacity|Electricity|Gas|w/o CCS|1",
"Capacity|Electricity|Gas|w/o CCS|2",
"Capacity|Electricity|Gas|w/o CCS|3",
"Capacity|Electricity|Coal|w/ CCS|1",
"Capacity|Electricity|Coal|w/ CCS|2",
"Capacity|Electricity|Coal|w/ CCS|3",
"Capacity|Electricity|Oil|w/o CCS|1",
"Capacity|Electricity|Oil|w/o CCS|2",
"Capacity|Electricity|Oil|w/o CCS|3",
"Capacity|Electricity|Solar|CSP|1",
"Capacity|Electricity|Solar|CSP|2",
"Capacity|Hydrogen|Coal",
"Capacity|Liquids|Oil",
"Capacity|Liquids|Oil|w/o CCS|1",
"Capacity|Liquids|Oil|w/o CCS|2",
"Capacity|Liquids|Coal|w/ CCS|1",
"Capacity|Liquids|Coal|w/ CCS|2",
"Capacity|Liquids|Coal|w/o CCS|1",
"Capacity|Liquids|Coal|w/o CCS|2",
"Capacity|Gases|Biomass|w/o CCS",
"Capacity|Gases|Coal|w/o CCS",
"Capacity|Hydrogen|Gas",
"Capacity|Liquids|Biomass|w/ CCS|1",
"Capacity|Liquids|Biomass|w/ CCS|2",
"Capacity|Liquids|Biomass|w/o CCS|1",
"Capacity|Liquids|Biomass|w/o CCS|2",
'Investment|Energy Supply|Electricity|Fossil',
 'Investment|Energy Supply|Electricity',
 'Investment|Energy Supply|Hydrogen',
 'Investment|Energy Supply|Liquids',
 'Investment|Energy Supply|Other',
 'Capacity|Electricity|Biomass',
 'Capacity|Electricity|Coal',
 'Capacity|Electricity|Gas',
 'Capacity|Electricity|Hydro',
 'Capacity|Electricity|Nuclear',
 'Capacity|Electricity|Oil',
 'Capacity|Electricity|Solar',
 'Capacity|Electricity|Wind',
 'Capacity|Gases',
 'Capacity|Hydrogen',
 'Capacity|Liquids',
 'Capacity|Liquids|Coal',
 'Capacity|Liquids|Gas',
 "Investment|Energy Supply|Electricity|Fossil",
"Investment|Energy Supply|Electricity|Fossil|Coal",
"Investment|Energy Supply|Electricity|Fossil|Gas",
"Investment|Energy Supply|Electricity|Fossil|Oil",
"Investment|Energy Supply|Electricity|Non-fossil|Geothermal",
"Investment|Energy Supply|Electricity|Non-fossil|Hydro",
"Investment|Energy Supply|Electricity|Non-fossil|Solar",
"Investment|Energy Supply|Electricity|Non-fossil|Wind",
"Investment|Energy Supply|Electricity|Non-fossil|Nuclear",
"Investment|Energy Supply|Extraction|Fossil|Coal",
"Investment|Energy Supply|Extraction|Fossil|Gas",
"Investment|Energy Supply|Extraction|Fossil|Oil"
'Capacity Additions|Electricity',
'Capacity Additions|Electricity|Biomass|w/ CCS|1',
'Capacity Additions|Electricity|Biomass|w/ CCS|2',
'Capacity Additions|Electricity|Biomass|w/o CCS|1',
'Capacity Additions|Electricity|Biomass|w/o CCS|2',
'Capacity Additions|Electricity|Coal|w/ CCS|1',
'Capacity Additions|Electricity|Coal|w/ CCS|2',
'Capacity Additions|Electricity|Coal|w/ CCS|3',
'Capacity Additions|Hydrogen',
'Capacity Additions|Electricity|Coal|w/o CCS|1',
'Capacity Additions|Electricity|Coal|w/o CCS|2',
'Capacity Additions|Electricity|Coal|w/o CCS|3',
'Capacity Additions|Electricity|Coal|w/o CCS|4',
'Capacity Additions|Electricity|Gas|w/o CCS|1',
'Capacity Additions|Electricity|Gas|w/o CCS|2',
'Capacity Additions|Electricity|Gas|w/o CCS|3',
'Capacity Additions|Electricity|Gas|w/ CCS|1',
'Capacity Additions|Electricity|Gas|w/ CCS|2',
'Capacity Additions|Electricity|Oil|w/o CCS|1',
'Capacity Additions|Electricity|Oil|w/o CCS|2',
'Capacity Additions|Electricity|Oil|w/o CCS|3',
'Capacity Additions|Electricity|Solar|CSP|1',
'Capacity Additions|Electricity|Solar|CSP|2',
'Capacity Additions|Gases|Biomass|w/o CCS',
'Capacity Additions|Liquids|Biomass|w/ CCS|1',
'Capacity Additions|Liquids|Biomass|w/ CCS|2',
'Capacity Additions|Liquids|Biomass|w/o CCS|1',
'Capacity Additions|Liquids|Biomass|w/o CCS|2',
'Capacity Additions|Liquids|Coal|w/ CCS|1',
'Capacity Additions|Liquids|Coal|w/ CCS|2',
'Capacity Additions|Liquids|Coal|w/o CCS|1',
'Capacity Additions|Liquids|Coal|w/o CCS|2',
'Capacity Additions|Liquids|Oil|w/o CCS|1',
'Capacity Additions|Liquids|Oil|w/o CCS|2',
'Secondary Energy|Liquids|Fossil|w/ CCS',
'Secondary Energy|Liquids|Fossil|w/o CCS',
'Secondary Energy|Liquids|Biomass',
'Secondary Energy|Hydrogen|Fossil|w/ CCS',
'Secondary Energy|Hydrogen|Fossil|w/o CCS',
'Secondary Energy|Liquids',
 'Secondary Energy|Heat',
 'Secondary Energy|Hydrogen',
 'Secondary Energy|Solids',
 'Secondary Energy|Gases',
 'Capacity Additions|Electricity|Biomass',
 'Capacity Additions|Electricity|Coal',
 'Capacity Additions|Electricity|Gas',
 'Capacity Additions|Electricity|Hydro',
 'Capacity Additions|Electricity|Nuclear',
 'Capacity Additions|Electricity|Oil',
 'Capacity Additions|Electricity|Solar',
 'Capacity Additions|Electricity|Wind',
 'Capacity Additions|Gases',
 'Capacity Additions|Hydrogen|Gas',
 'Capacity Additions|Liquids',
 'Secondary Energy|Electricity|Wind|',
 'Secondary Energy|Electricity|Wind|Curtailment',
 'Carbon Sequestration|CCS|Fossil|Energy|Supply',
 'Primary Energy|Fossil|w/o CCS'
]


df_pyam = df_pyam.filter(variable = ['Water*',
                                      'Resource|Cumulative*', 'GDP*',
                                      'Population*','Commulative*','*Trade*','Useful Energy|Input*',
                                      'Primary Energy (substitution method)*'],keep = False )

df_pyam = df_pyam.filter(variable = var_lis, keep = False)


#TODO Commented out to check IDEA without this first
# from cycler import K
# import yaml
# import pandas as pd

# # Load the YAML file
# yaml_file_path = '/Users/muhammadawais/Documents/GitHub/message-ix-canada/model/output/iamc_structure.yaml'
# with open(yaml_file_path, 'r') as file:
#     vars_agg = yaml.safe_load(file)

# # List to keep track of problematic variables
# problematic_variables = []

# # Loop through each item in the aggregation dictionary
# for variable, components in vars_agg.items():
#     try:
#         # Attempt to aggregate each variable with its components
#         df_pyam.aggregate(variable=variable, components=components, append=True)
#     except ValueError as e:
#         # Print the variable causing the issue and the associated error
#         problematic_variables.append(variable)
#         print(f"Error aggregating {variable}: {e}")
        
df_pyam_baseline = df_pyam.filter(scenario='BAU')
df_pyam_netzero = df_pyam.filter(scenario = 'NZ')
df_pyam_netzero_opt = df_pyam.filter(scenario = 'NZ-OPT')
df_pyam_netzero_pes = df_pyam.filter(scenario = 'NZ-PES')

df =df_pyam_baseline.as_pandas()
df['value'] = df['value'].astype(float)
df['model'] = 'MESSAGEix-Canada'
df.rename(columns={'year':'time'}, inplace=True)
df.to_csv('/Users/muhammadawais/Documents/GitHub/message-ix-canada/model/output/output_pyam_baseline.csv')

df =df_pyam_netzero.as_pandas()
df['value'] = df['value'].astype(float)
df['model'] = 'MESSAGEix-Canada'
df.rename(columns={'year':'time'}, inplace=True)
df.to_csv('/Users/muhammadawais/Documents/GitHub/message-ix-canada/model/output/output_pyam_netzero.csv')

df =df_pyam_netzero_opt.as_pandas()
df['value'] = df['value'].astype(float)
df['model'] = 'MESSAGEix-Canada'
df.rename(columns={'year':'time'}, inplace=True)
df.to_csv('/Users/muhammadawais/Documents/GitHub/message-ix-canada/model/output/output_pyam_netzero_opt.csv')

df =df_pyam_netzero_pes.as_pandas()
df['value'] = df['value'].astype(float)
df['model'] = 'MESSAGEix-Canada'
df.rename(columns={'year':'time'}, inplace=True)
df.to_csv('/Users/muhammadawais/Documents/GitHub/message-ix-canada/model/output/output_pyam_netzero_pes.csv')