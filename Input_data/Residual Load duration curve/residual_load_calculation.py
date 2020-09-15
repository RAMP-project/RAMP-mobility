# -*- coding: utf-8 -*-
"""
Created on Tue May 26 14:56:07 2020

@author: Andrea Mangipinto
"""

import pandas as pd
import pytz

inputfile_pv = f"ninja_pv_europe_v1.1_merra2.csv"
inputfile_wind = f"ninja_wind_europe_v1.1_current_national.csv"
inputfile_cap = f"TIMES_Capacities_technology_2050.csv"
inputfile_load = f"time_series_60min_singleindex_filtered.csv"

def residual_load(country, year, load_multiplier, inputfile_load, inputfile_pv, inputfile_wind , inputfile_cap):
    
        
    if country == 'EL':
        country_tz = 'GR'
    elif country == 'UK':
        country_tz = 'GB'
    else:
        country_tz = country
    
    # Solar AF 
    pv_af = pd.read_csv(inputfile_pv, index_col = 0) #Read the input file
    pv_af.rename(columns={"GB": "UK", "GR": "EL"}, inplace = True)
    pv_af = pd.DataFrame(pv_af[country]) #Filter only for needed country
    ind_init = pd.date_range(start=pv_af.index[0], end=pv_af.index[-1], freq='H', tz = 'UTC')
    pv_af.set_index(ind_init, inplace = True) #Set index to datetime

    pv_af_tz = pv_af.tz_convert(pytz.country_timezones[country_tz][0]) # Convert to country timezone

    pv_af_loc = pv_af_tz.tz_localize(None, ambiguous = 'NaT') # Remove the timezone information (local time)
    pv_af_loc = pv_af_loc[~pv_af_loc.index.duplicated(keep='first')] # Remove duplicate hours arising from tz conversion

    # Wind AF 
    wind_af = pd.read_csv(inputfile_wind, index_col = 0) #Read the input file
    wind_af.rename(columns={"GB": "UK", "GR": "EL"}, inplace = True)

    wind_af = pd.DataFrame(wind_af[country]) #Filter only for needed country
    ind_init = pd.date_range(start=wind_af.index[0], end=wind_af.index[-1], freq='H', tz = 'UTC')
    wind_af.index = pd.to_datetime(wind_af.index, utc = True)
    wind_af = wind_af.reindex(ind_init) #Set index to datetime
    wind_af_tz = wind_af.tz_convert(pytz.country_timezones[country_tz][0]) # Convert to country timezone

    wind_af_loc = wind_af_tz.tz_localize(None, ambiguous = 'NaT') # Remove the timezone information (local time)
    wind_af_loc = wind_af_loc[~wind_af_loc.index.duplicated(keep='first')] # Remove duplicate hours arising from tz conversion

    # RES Capacities 
    res_cap_temp = pd.read_csv(inputfile_cap, index_col = 0)
    res_cap = pd.DataFrame(index = [country], columns = ['PV', 'WIND'])
    res_cap['PV'] = res_cap_temp.loc[country, res_cap_temp.columns.str.contains('PHOT|PV')].values
    res_cap['WIND'] = sum(res_cap_temp.loc[country, res_cap_temp.columns.str.contains('WIN|WIND')].values)

    wind_prod_local = wind_af_loc * res_cap['WIND']
    pv_prod_local = pv_af_loc * res_cap['PV']
    
    # Load Demand
    load = pd.read_csv(inputfile_load, index_col = 0)
    # pre-process the original file
    load.drop(columns = ['cet_cest_timestamp'], inplace = True)
    load.dropna(axis = 1, how = 'all',  inplace = True)
    c_old = list(load.columns)
    c_new = [w[0:2] for w in c_old]
    rename_dict = dict(zip(c_old,c_new))
    load.rename(columns = rename_dict, inplace = True)
    load.rename(columns={"GB": "UK", "GR": "EL"}, inplace = True)
    
    load = pd.DataFrame(load[country])
    ind_init = pd.date_range(start= load.index[0], end=load.index[-1], freq='H', tz = 'UTC')
    load.set_index(ind_init, inplace = True)
    load_tz = load.tz_convert(pytz.country_timezones[country_tz][0])
    
    load_loc = load_tz.tz_localize(None, ambiguous = 'NaT') # Remove the timezone information (local time)
    load_loc = load_loc[~load_loc.index.duplicated(keep='first')] # Remove duplicate hours arising from tz conversion

    load_multiplier = load_multiplier # Multiplier to account for higher load in the future 
    load_local_mult = load_loc * load_multiplier

    # Residual Load
    
    pv_prod_local = pv_prod_local.loc[f'{year}']
    pv_prod_local = pv_prod_local.resample('T', closed='right').pad() #resample with minute time detail

    wind_prod_local = wind_prod_local.loc[f'{year}']
    wind_prod_local = wind_prod_local.resample('T', closed='right').pad() #resample with minute time detail
    
    load_local_mult = load_local_mult.loc[f'{year}']
    load_local_mult = load_local_mult.resample('T', closed='right').pad() #resample with minute time detail

    res_load = load_local_mult - wind_prod_local - pv_prod_local
            
    return res_load

countries = ['AT', 'BE', 'BG', 'CH', 'CZ', 'DE', 'DK', 'EE', 'EL', 'ES', 'FI', 'FR', 'HR', 'HU',
  'IE', 'IT','LT', 'LU','LV', 'NL', 'NO', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK', 'UK']

for c in countries: 
    country = f'{c}'
    load_multiplier = 2.5
    year = 2016
    
    res_load = residual_load(country, year, load_multiplier, inputfile_load, inputfile_pv , inputfile_wind, inputfile_cap)
    
    res_load.to_csv(f'residual_load_{country}_{year}.csv')
