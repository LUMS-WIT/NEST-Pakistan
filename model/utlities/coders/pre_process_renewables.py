import pandas as pd
import requests
import os
import math

def pre_process_renewables(root, years):
    """
    Creates renewable_capacity_factor and renewable_potential csv files for wind and solar
    """
    print('Creating renewable potential/capacity factor data')
    wind_cf_raw = pd.read_csv('windcf.csv', index_col=0)
    solar_cf_raw = pd.read_csv('solarcf.csv', index_col=0)
    grid_cell_data = pd.read_csv('gridcells.csv', index_col=0)
    grade_data = pd.read_csv('renewable_grades.csv', index_col=0)

    ons_grades = grade_data[grade_data.index.str.contains('onshore_')]
    ofs_grades = grade_data[grade_data.index.str.contains('offshore_')]
    solar_grades = grade_data[grade_data.index.str.contains('solar_')]
    
    wind_cf_raw = wind_cf_raw.mean()
    solar_cf_raw = solar_cf_raw.mean()
    
    grid_cell_data['wind_capacity_factor'] = wind_cf_raw.values
    grid_cell_data['solar_capacity_factor'] = solar_cf_raw.values

    ons_cf = [0] + list(ons_grades.capacity_factor.values)
    #print(f'Onshore wind grades: {ons_cf}')
    grid_cell_data['ons_wind_grade'] = pd.cut(grid_cell_data.wind_capacity_factor, ons_cf, labels=list(ons_grades.index.values),include_lowest=True)

    ofs_cf = [0] + list(ofs_grades.capacity_factor.values)
    #print(f'Offshore wind grades: {ofs_cf}')
    grid_cell_data['ofs_wind_grade'] = pd.cut(grid_cell_data.wind_capacity_factor, ofs_cf, labels=list(ofs_grades.index.values),include_lowest=True)

    solar_cf = [0] + list(solar_grades.capacity_factor.values)
    #print(f'Solar grades: {solar_cf}')
    grid_cell_data['solar_grade'] = pd.cut(grid_cell_data.solar_capacity_factor, solar_cf, labels=list(solar_grades.index.values),include_lowest=True)

    area_grade_ons = {}
    area_grade_ons['Canada'] = 0
    area_grade_ofs = {}
    area_grade_ofs['Canada'] = 0
    area_grade_solar = {}
    area_grade_solar['Canada'] = 0

    for prov in grid_cell_data.pr.unique():
        prov_data = grid_cell_data[grid_cell_data.pr == prov].copy()
        area_grade_ons[prov] = prov_data.groupby('ons_wind_grade', observed=False)['surface_area_ons'].sum()
        area_grade_ons['Canada'] += area_grade_ons[prov]

        area_grade_ofs[prov] = prov_data.groupby('ofs_wind_grade', observed=False)['surface_area_ofs'].sum()
        area_grade_ofs['Canada'] += area_grade_ofs[prov]

        area_grade_solar[prov] = prov_data.groupby('solar_grade', observed=False)['surface_area_ons'].sum()
        area_grade_solar['Canada'] += area_grade_solar[prov]
    
    data_ons = pd.DataFrame.from_dict(area_grade_ons)
    data_ons = data_ons.divide(data_ons['Canada'].values,axis=0).multiply(ons_grades.potential_Gwa.values, axis=0).fillna(0)

    data_ofs = pd.DataFrame.from_dict(area_grade_ofs)
    data_ofs = data_ofs.divide(data_ofs['Canada'].values,axis=0).multiply(ofs_grades.potential_Gwa.values, axis=0).fillna(0)

    data_solar = pd.DataFrame.from_dict(area_grade_solar)
    data_solar = data_solar.divide(data_solar['Canada'].values,axis=0).multiply(solar_grades.potential_Gwa.values, axis=0).fillna(0)

    wind_ons_potential = {}
    wind_ofs_potential = {}
    solar_potential = {}

    wind_ons_cf = {}
    wind_ofs_cf = {}
    solar_cf = {}

    for year in years:
        for prov in grid_cell_data.pr.unique():
            for grade in data_ons.index:
                wind_ons_potential[f'{prov}_{year}_{grade}'] = data_ons.loc[grade, prov].copy()
                wind_ons_cf[f'{prov}_{year}_{grade}'] = grade_data.loc[grade, 'capacity_factor'].copy()
            for grade in data_ofs.index:
                wind_ofs_potential[f'{prov}_{year}_{grade}'] = data_ofs.loc[grade, prov].copy()
                wind_ofs_cf[f'{prov}_{year}_{grade}'] = grade_data.loc[grade, 'capacity_factor'].copy()
            for grade in data_solar.index:
                solar_potential[f'{prov}_{year}_{grade}'] = data_solar.loc[grade, prov].copy()
                solar_cf[f'{prov}_{year}_{grade}'] = grade_data.loc[grade, 'capacity_factor'].copy()
    

    data = pd.DataFrame.from_dict(wind_ons_potential, orient='index', columns=['value'])
    data = pd.concat([data, pd.DataFrame.from_dict(wind_ofs_potential, orient='index', columns=['value'])])
    data = pd.concat([data, pd.DataFrame.from_dict(solar_potential, orient='index', columns=['value'])]).reset_index()
    data[['node', 'year', 'commodity']] = data['index'].str.split('_', n=2, expand=True)
    data[['commodity', 'grade']] = data['commodity'].str.rsplit('_',n=1,expand=True)
    data['level'] = 'renewable'
    data['unit'] = 'MWa'
    data['value'] = data['value'] * 1000
    data = data[['node', 'commodity', 'grade', 'level', 'year', 'value', 'unit']]
    data.to_csv(f'{root}\\data\\CODERS_data\\renewable_potential.csv',index=False)


    data = pd.DataFrame.from_dict(wind_ons_cf, orient='index', columns=['value'])
    data = pd.concat([data, pd.DataFrame.from_dict(wind_ofs_cf, orient='index', columns=['value'])])
    data = pd.concat([data, pd.DataFrame.from_dict(solar_cf, orient='index', columns=['value'])]).reset_index()
    data[['node', 'year', 'commodity']] = data['index'].str.split('_', n=2, expand=True)
    data[['commodity', 'grade']] = data['commodity'].str.rsplit('_',n=1,expand=True)
    data['level'] = 'renewable'
    data['unit'] = '-'
    data = data[['node', 'commodity', 'grade', 'level', 'year', 'value', 'unit']]
    data.to_csv(f'{root}\\data\\CODERS_data\\renewable_capacity_factor.csv',index=False)

if __name__ == "__main__":
    years = range(2020, 2060+1, 5)
    root = os.path.dirname(os.path.dirname(os.getcwd()))
    data = pre_process_renewables(root, years)
    #pre_process_solar(root, cutoff_per=0.05)