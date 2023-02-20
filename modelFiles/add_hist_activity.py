# -*- coding: utf-8 -*-
"""
This function loads the activity data from the IEA Database, restructures
it to form of the MESSAGE model, and assign it to parameter "historical_activity".

"""
import pandas as pd
import cx_Oracle
from itertools import product
from modelFiles.utilities.util1 import setdefaults
from modelFiles.utilities.util2 import reindexandadd
from colorama import Fore

def add_iea_activity(msgSC, ieaName, nodeName, path, suffix):

    #%% 1) Initialization and preprations

    # IEA specification
    xls_set = pd.ExcelFile(str(path + '\ModelSetup' + suffix + '.xlsx'))
    sheet_list = xls_set.parse('lists')
    iea_year = int(sheet_list['IEA_historical_year'].dropna().item())
    # iea_year = int(iea_year[0])        # TODO: fetch data for more years
    iea_rev = int(sheet_list['IEA_revision'].dropna().item())
    iea_scheme = "'MESSAGE_2016'"

    parlist = ['historical_activity']

    # Data from Excel file
    xls = pd.ExcelFile(str(path + '\ModelSetup' + suffix + '.xlsx'))
    sheet_tech = xls.parse('technology')
    technology_df = sheet_tech[sheet_tech['INCLUDE'] == 'y'].dropna(subset=['TECHNOLOGY'])

    print('> Importing historical activity data ...')
    msgSC.check_out()

    #%% 2) Retriving the mapping of technologies to the IEA energy flows and products

    technology_df['SQL'] = pd.Series(index=technology_df.index)
    technology_df['SQL'] = ['SQL' for i in range(0, len(technology_df))]
    technology_df['IEA_Output_Value'] = pd.Series(index=technology_df.index)
    technology_df['IEA_Output_Unit'] = pd.Series(index=technology_df.index)
    technology_df['IEA_Output_Unit'] = ['IEA_Output_Unit' for i in range(0, len(technology_df))]

    #%% 3) Retriving historic energy demand from IEA Database

    for i in technology_df.index:
        if (type(technology_df.IEA_DATABASE_QUEREY_fNAME[i]) is str and
            type(technology_df.IEA_DATABASE_QUEREY_pFUEL[i]) is str):
            SQL = "SELECT SUM(d.VALUE) SUM_VALUE, d.UNIT, d.REV_CODE, d.RYEAR "
            SQL += " FROM ((edb_flow f INNER JOIN edb_data d ON f.CODE = d.FLOW_CODE) "
            SQL += " INNER JOIN edb_fuel p ON d.PROD_CODE = p.PROD_CODE) "
            SQL += " INNER JOIN edb_country r ON d.COUNTRY_CODE = r.CODE "
            SQL += " WHERE p.scheme = " + iea_scheme + "and d.rev_code = "
            SQL += str(iea_rev) + " and r.name = " + ieaName
            SQL += " And d.ryear = " + str(iea_year) + " and f.name in "
            SQL += str(technology_df.IEA_DATABASE_QUEREY_fNAME[i])
            SQL += " and p.FUEL in "
            SQL += str(technology_df.IEA_DATABASE_QUEREY_pFUEL[i])
            SQL += " GROUP BY d.UNIT,d.REV_CODE,d.RYEAR"
            technology_df.loc[i, 'SQL'] = SQL
            # Establish connection to the database and create a cursor
            connection = cx_Oracle.connect("iea/iea@//gp3.iiasa.ac.at:1521/GP3")
            cursor = connection.cursor()
            cursor.execute(SQL)  # Query the SQL comand
            output = [row for row in cursor]
            if output != []:
                technology_df.at[i, 'IEA_Output_Value'] = abs(round(output[0][0], 4))
                technology_df.at[i, 'IEA_Output_Unit'] = output[0][1]
            cursor.close()
            connection.close()

    #%% 4) Converting all units into GWa

    for i in technology_df.index:
        if technology_df.IEA_Output_Unit[i] == 'TJ':
            technology_df.at[i, 'IEA_Output_Value'
                         ] = technology_df.IEA_Output_Value[i] * 0.277777778  # Conversion from TJ to GWh

        technology_df.at[i, 'IEA_Output_Value'
                         ] = technology_df.IEA_Output_Value[i] /8760  # Conversion from  GWh to GWa

        technology_df.loc[i, 'IEA_Output_Unit'] = 'GWa'

    # Conversion from input fixed activity to an output normed activity
    for tec in technology_df.index:
        if technology_df.out_or_input[tec] == 'input':
            technology_df.at[tec, 'IEA_activity'
                             ] = technology_df.loc[tec, 'IEA_Output_Value'] / technology_df.loc[tec, 'input']    #NOTICE: the modeler can divide this by the value of the MESSAGE "input", instead of the Excel table
        else:
            technology_df.loc[tec, 'IEA_activity'] = technology_df.loc[tec, 'IEA_Output_Value']

    #%% 5) Loading parameters

    for parname in parlist:
        iea = technology_df.dropna(subset=['IEA_activity'])
        iea = iea[['TECHNOLOGY', 'IEA_activity']].drop_duplicates()

        par = pd.DataFrame(columns=msgSC.par(parname).columns, index=product(iea.TECHNOLOGY, [iea_year]))
        par = setdefaults(par,nodeName)
        par['year_act'] = iea_year
        par['unit'] = 'GWa'
        par['technology'] = [par.index[i][0] for i in range(0, len(par.index))]
        par['value'] = [float(iea.loc[iea.TECHNOLOGY == par.technology[i],
                                      'IEA_activity']) for i in range(0, len(par.index))]
        par = par.dropna(axis=0, how='any', thresh=None, subset=['value'])
        par.index = range(0, len(par.index))
        if par.empty:
           print(Fore.RED +'> WARNING: IEA database has no data for historical activity for ' + str(ieaName) + ', please check the name format!!')
        else:
            par = reindexandadd(par, parname, msgSC)

    #%% 6) Commiting additions
            print('> Historical activity data of "{}" in {} imported from IEA Database!'.format(nodeName, str(iea_year)))
        msgSC.commit('copied activity bounds for 2010 from IEA Database')
