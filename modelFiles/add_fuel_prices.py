import pandas as pd
import os 

def add_fuel_prices(msgSC, path):
    msgSC.add_set("relation", "fuel_price")
    msgSC.add_set("technology", ["elec_imp", "elec_exp"])
    file_path = os.path.join(path, "modelData", "Fuel_Price.xlsx")
    df = pd.read_excel(file_path)
    msgSC.add_par("relation_activity", df)