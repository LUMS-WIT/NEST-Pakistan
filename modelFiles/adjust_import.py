from message_ix import make_df
import pandas as pd

def adjust_oil(msgSC, path):
    imp_bau = pd.read_excel(path, sheet_name="imports")
    imp_bau = imp_bau[(imp_bau["technology"] == "oil_imp" ) | (imp_bau["technology"] == "loil_imp")]
    msgSC.add_par("bound_activity_up", imp_bau)

def adjust_coal(msgSC, path):
    imp_bau = pd.read_excel(path, sheet_name="imports")
    imp_bau = imp_bau[imp_bau["technology"] == "coal_imp"]
    msgSC.add_par("bound_activity_up", imp_bau)   

def adjust_imp(msgSC, path):
        # adjust_oil(msgSC, path)
        adjust_coal(msgSC, path)
