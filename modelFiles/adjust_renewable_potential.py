from message_ix import make_df
import pandas as pd

def adjust_bioenergy(msgSC):
    rp_remove = msgSC.par("renewable_potential", {"commodity":"bioenergy"})
    msgSC.remove_par("renewable_potential", rp_remove)
    rp = make_df("renewable_potential", node = "R12_PAK", commodity = "bioenergy", grade="bioenergy_1", level="renewable", unit="GWa",
                                year=(list(range(1990, 2065, 5)) + [2070]), value = 20.709)
    msgSC.add_par("renewable_potential", rp)


    

def adjust_potential(msgSC):
    # adjust_hydro(msgSC)
    adjust_bioenergy(msgSC)
    # adjust_solar(msgSC)
    # adjust_transport(msgSC)
