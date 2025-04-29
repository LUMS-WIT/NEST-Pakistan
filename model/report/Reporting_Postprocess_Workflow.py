import pandas as pd
import pyam
import yaml

from cycler import K

gdp = pd.read_csv('model/data/gdp/gdp_messageca_prov.csv', header=0, sep=',')
rep = pd.read_excel('model/output/reports/MESSAGEix-CA_baseline.xlsx',sheet_name="data", header=0)


# GDP Convertions ---
## 1 USD 2010 == 1.19 USD 2020 -- https://www.in2013dollars.com/us/inflation/2010?endYear=2020&amount=1
## 1 USD 2020 ==  1.34 CAD 2020 --  https://www.bankofcanada.ca/rates/exchange/annual-average-exchange-rates/

GDP2020 = gdp["GDP"] * 1.19 * 1.34

gdp["GDP"] = GDP2020

rep.drop_duplicates(inplace=True)
rep.dropna(inplace=True)


df_pyam = pyam.IamDataFrame(rep)




gdp['model'] = df_pyam.model[0]
gdp['scenario']= df_pyam.scenario[0]
gdp['unit'] = 'CAD'
gdp['variable'] = 'GDP'
gdp.rename(columns={"Province": "region", "GDP": "value", "Year": "year"}, inplace=True)

gdp = gdp[gdp["region"] != "Canada"]

rep_with_gdp = [rep["region"] != "Canada"]

df_gdp = pyam.IamDataFrame(gdp)
rep_with_gdp = pyam.concat([df_pyam,df_gdp])
rep_with_gdp.filter(variable ='Final Energy').convert_unit('PJ','MJ',factor = 1e-3)
rep_with_gdp.filter(variable ='Final Energy').convert_unit('CAD','Bi-CAD',factor = 1e-9)
# Probably need to convert emissions from C-equivalent to CO2-equivalent?
#### ----- #### ---- #### ----- #### ---- #### ----- #### ---- #### ----- #### ---- ####
rep_with_gdp.aggregate_region(variable=rep_with_gdp.variable, region="National", subregions=rep_with_gdp.region, append=True)
rep_with_gdp.aggregate_region(variable=rep_with_gdp.variable, region="Atlantic", subregions=["PrinceEdwardIsland", "NovaScotia", "NewfoundlandandLabrador", "NewBrunswick"], append=True)


fin_energy = rep_with_gdp.divide('Final Energy','GDP','Final Energy Intensity of GDP',ignore_units=True, axis = 'variable').timeseries()
carbon_intensity = rep_with_gdp.divide('Emissions|Kyoto Gases','GDP','Carbon Intensity',ignore_units=True, axis = 'variable').timeseries()
second_energy_dem = rep_with_gdp.aggregate(variable="Final Energy Demand (Secondary Energy)",components=['Secondary Energy|Electricity', 'Secondary Energy|Gases', 'Secondary Energy|Heat'
                    'Secondary Energy|Hydrogen', 'Secondary Energy|Liquids', 'Secondary Energy|Solids'], method="sum")
elec_supply = rep_with_gdp.aggregate(variable = "Electricity Supply", components=["Secondary Energy|Electricity"])
elec_supply.convert_unit("PJ", "TWh", factor=0.2778)
# shadow_co2 = 
ghg_emissions = rep_with_gdp.aggregate(variable="Total GHG Emissions", components=["Emissions"])
ghg_emissions.convert_unit("Mt C-equivalent", "Mt CO2 eq", 44/12) 



final_df = pyam.concat([rep_with_gdp, fin_energy, carbon_intensity, second_energy_dem, elec_supply, ghg_emissions])

final_df.to_csv("model/output/reports/Formatted_Report.csv")

# For searching up 
df_pyam.filter(variable = 'Emissions|*').variable
