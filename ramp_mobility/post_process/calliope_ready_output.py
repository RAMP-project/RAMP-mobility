# -*- coding: utf-8 -*-

#%% Import required libraries
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytz
import copy
import matplotlib.ticker as mtick
from pathlib import Path
import pickle
import utils
from ramp_mobility.utils import tot_users_calc, tot_battery_cap_calc
from ramp_mobility.post_process import post_process as pp

# from initialise import tot_users_calc, tot_battery_cap_calc
import datetime as dt
#import enlopy as el

#%% Post-processing Calliope ready outputs

def mobility_profiles(Profile_tot, country, year):

    (large_vehicles_prof, medium_vehicles_prof, small_vehicles_prof)=formatting_vehicle_categories(Profile_tot)

    large_vehicles_prof=large_vehicles_prof/sum(large_vehicles_prof)
    medium_vehicles_prof=medium_vehicles_prof/sum(medium_vehicles_prof)
    small_vehicles_prof=small_vehicles_prof/sum(small_vehicles_prof)

    large_vehicles_prof_utc=pp.time_conversion(large_vehicles_prof,country, year)
    medium_vehicles_prof_utc=pp.time_conversion(medium_vehicles_prof,country, year)
    small_vehicles_prof_utc=pp.time_conversion(small_vehicles_prof,country, year)

    return (large_vehicles_prof_utc, medium_vehicles_prof_utc, small_vehicles_prof_utc)

def depth_of_discharge(SOC_user, country, year):
    
    (SOC_large_profile, SOC_medium_profile, SOC_small_profile)=vehicle_category_split(SOC_user,'mean')

    SOC_large_profile_utc=pp.time_conversion(SOC_large_profile,country, year)
    SOC_medium_profile_utc=pp.time_conversion(SOC_medium_profile,country, year)
    SOC_small_profile_utc=pp.time_conversion(SOC_small_profile,country, year)

    return (SOC_large_profile_utc, SOC_medium_profile_utc, SOC_small_profile_utc)

def charging_limits(Charging_limit_profile, country, year):

    Charging_limit_profile = Charging_limit_profile/max(Charging_limit_profile) # dividere per Pnom max
    Charging_limit_profile_utc=pp.time_conversion(Charging_limit_profile,country, year)

    return (Charging_limit_profile_utc)


'''
General functions
'''
def formatting_vehicle_categories(Usage_tot):
    
    '''
    Current function formats dictionary of dictionaries in series - It is used to split the usage
    in each vehicle category in order to check if the values are lower than the overall car numbers in such country
    The attributes large, medium and small refer to the size of the vehicles

    Used to compute for each vehicle size the adimensional mobility profile - Usage_tot or Profile_tot
    '''
    large = {}
    medium = {}
    small = {}
    large_profile=([])
    medium_profile=([])
    small_profile=([])

    # tot_users=tot_users_calc(User_list)

    for day in Usage_tot.keys():
        large[day] = np.zeros(1440)
        medium[day] = np.zeros(1440)
        small[day] = np.zeros(1440)
        for user_type in Usage_tot[day].keys():
            y=sum(x for x in Usage_tot[day][user_type].values())
            if 'Large' in user_type:
                large[day]=large[day]+y
            elif 'Medium' in user_type:
                medium[day]=medium[day]+y
            else:
                small[day]=small[day]+y
    
    for item in large.items():
        large_profile.append(item[1])
    for item in medium.items():
        medium_profile.append(item[1])
    for item in small.items():
        small_profile.append(item[1])

    large_profile=np.hstack(large_profile)
    medium_profile=np.hstack(medium_profile)
    small_profile=np.hstack(small_profile)

    # large_profile=np.hstack(large_profile)/tot_users
    # medium_profile=np.hstack(medium_profile)/tot_users
    # small_profile=np.hstack(small_profile)/tot_users
    
    return (large_profile, medium_profile, small_profile)


def check_vehicles_driver(large_profile, medium_profile, small_profile, User_list, country):

    """
    The current function performs a check over the vehicles-per-driver ratio.

    Required input: dimensional usage of the vehicles grouped by size
    """

    size=(['small','medium','large'])
    vehicles_driver_sim=([max(small_profile)/utils.tot_users_calc(User_list),max(medium_profile)/utils.tot_users_calc(User_list),
        max(large_profile)/utils.tot_users_calc(User_list)])

    try:
        path = fr"..\database\vehicles_per_driver.csv"
        vehicle_driver_df = pd.read_csv(path, index_col = 0)
    except FileNotFoundError:      
        print('[WARNING]: The check on the vehicle usage can not be performed since the file -vehicles_per_driver- is missing')

    vehicles_driver_ratio=vehicle_driver_df.loc[country,:]
      
    for i in range(len(vehicles_driver_ratio)):
        if vehicles_driver_sim[i] > vehicles_driver_ratio[i]:
            print(f"[WARNING]: For country {country}, simulated {size[i]} vehicles have exceeded the vehicles-per-driver check-value ({vehicles_driver_sim[i]:.3f} > {vehicles_driver_ratio[i]}).")
        else:
            print(f"[CHECK PASSED]: For country {country}, sim : {vehicles_driver_sim[i]:.3f} < {vehicles_driver_ratio[i]} : check-value")

    return

def vehicle_category_split(_profile_user,operand): # operand: (['sum','mean'])

    """
    Used for Charging_nom_profile_user and Ch_profile_user ->
    """
    count_large = 0
    count_medium = 0
    count_small = 0

    large_profile = np.zeros(len(_profile_user['Inactive - Large car'][0]))
    medium_profile = np.zeros(len(_profile_user['Inactive - Large car'][0]))
    small_profile = np.zeros(len(_profile_user['Inactive - Large car'][0]))

    for user_type in _profile_user.keys():
        if (operand == 'sum' or operand == 'summation'):
            y = y=sum(x for x in _profile_user[user_type])
        elif (operand == 'mean' or operand == 'average'):
            y = np.mean(_profile_user[user_type], axis=0)
                          
        if 'Large' in user_type:
            large_profile = large_profile + y
            count_large += 1
        elif 'Medium' in user_type:
            medium_profile = medium_profile + y
            count_medium += 1
        else:
            small_profile = small_profile + y
            count_small += 1
    
    if operand == 'mean' or 'average':
        large_profile = large_profile/count_large
        medium_profile = medium_profile/count_medium
        small_profile = small_profile/count_small

    return (large_profile, medium_profile, small_profile)

def average_norm_profile(_profile_user,operand): # operand: (['sum','mean'])

    """
    Used for Charging_nom_profile_user and Ch_profile_user ->
    """
    count = 0

    profile = np.zeros(len(_profile_user['Inactive - Large car'][0]))

    for user_type in _profile_user.keys():
        if (operand == 'sum' or operand == 'summation'):
            y = y=sum(x for x in _profile_user[user_type])
        elif (operand == 'mean' or operand == 'average'):
            y = np.mean(_profile_user[user_type], axis=0)
                        
        profile = profile + y
        count += 1
    
    if operand == 'mean' or 'average':
        profile = profile/count

    return (profile)

