# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 12:03:48 2020

@author: Andrea Mangipinto
"""

#%% Import required libraries
import numpy as np
import random 
import pandas as pd
import datetime as dt
from ramp_mobility import utils
import itertools
import math

# from initialise import (charge_prob, charge_prob_const, SOC_initial_f, 
# SOC_initial_f_const, charge_check_smart, charge_check_normal, pv_indexing, 
# tot_users_calc)

#%% Charging process calculation script

def Charging_Process(Profiles_user, User_list, country, year, dummy_days, residual_load, charging_mode = 'Uncontrolled', logistic = False, infr_prob = 0.5, Ch_stations = ([3.7, 11, 120], [0.6, 0.3, 0.1]), V2G = False):
    
    #SOC value at the beginning of the simulation, relevant only for
    # Perfect Foresight charging strategy, as is the maximum SOC that the car 
    # will always try to go back to
    SOC_initial = 0.8
    SOC_min_rand = 0.5 # Minimum SOC level with which the car can start the simulation

    # Definition of battery limits to avoid degradation
    SOC_max = 0.8 # Maximum SOC at which the battery is charged
    SOC_min = 0.25 # Minimum SOC level that forces the charging event
    
    eff = 0.90  # Charging/discharging efficiency
    
    P_ch_station_list = Ch_stations[0] # Nominal power of the charging station [kW]
    prob_ch_station = Ch_stations[1]    
    
    # Parameters for the piecewise infrastructure probability function
    prob_max = 0.9
    prob_min = 0.4
    t1 = '06:00'
    t2 = '19:00'
    
    # Calculate the number of users in simulation for screen update
    tot_users = utils.tot_users_calc(User_list)
         
    # Check that the charging mode is one of the expected ones
    charging_mode_types = ['Uncontrolled', 'Night Charge', 'Self-consumption', 'RES Integration', 'Perfect Foresight']
    assert charging_mode in charging_mode_types, f"[WARNING] Invalid Charging Mode. Expected one of: {charging_mode_types}"
    
    #
    if 'RES Integration' in charging_mode:
        if not residual_load.any(None):
            raise ValueError("[WARNING] RES Integration detected as charging strategy, but the residual load file is not found. Please provide a csv file containing the residual load curve.")                        
    
    # Check that the initial SOC is in the expected way
    if (SOC_initial != 'random' and 
        not isinstance(SOC_initial, (int, float))): 
            raise ValueError(f"[WARNING] Invalid SOC initial. Expected either 'random', or a value between {SOC_min} and 1")                    

    # Check that the infrastructure probability is in the expected way
    if (infr_prob != 'piecewise' and 
        not isinstance(infr_prob, (int, float))): 
            raise ValueError("[WARNING] Invalid Infrastructure probability. Expected etiher 'piecewise', or a value between 0 and 1")                        
    
    # Initialization of output variables
    Charging_profile_user = {}
    Charging_nom_profile_user = {}
    Charging_profile = np.zeros(len(Profiles_user['Working - Large car']))
    Charging_nom_profile = np.zeros(len(Profiles_user['Working - Large car']))
    Charging_limit_profile = np.zeros(len(Profiles_user['Working - Large car']))
    Plug_in_profile = np.zeros(len(Profiles_user['Working - Large car']))
    Plug_in_profile_cap = np.zeros(len(Profiles_user['Working - Large car']))
    Plug_in_v2g_profile_cap = np.zeros(len(Profiles_user['Working - Large car']))
    Charging_profile_cap = np.zeros(len(Profiles_user['Working - Large car']))

    en_sys_tot = np.zeros(len(Profiles_user['Working - Large car']))
    SOC_user = {}
    plug_in_user = {}
    plug_in_user_v2g = {}
    min_charge_user = {}
    max_charge_user = {}
    num_us = 0
    dummy_minutes = 1440 * dummy_days
    batt_cap_tot=0

    # Creation of date array 
    start_day = dt.datetime(year, 1, 1) - dt.timedelta(days=dummy_days)
    n_periods = len(Profiles_user['Working - Large car'])
    minutes = pd.date_range(start=start_day, periods = n_periods, freq='T')

    # Check if introducing the logistic function for behavioural modeling
    if logistic: # Probability of charging based on the SOC of the car 
        ch_prob = utils.charge_prob
    else: # The user will always try to charge (probability = 1 for every SOC)
        ch_prob = utils.charge_prob_const
    
    if V2G:
        con_prob = utils.connection_prob_dome
    else:
        con_prob = utils.connection_prob_const

    # Check which infrastructure probability function to use 
    if infr_prob == 'piecewise': # Use of piecewise function based on hour of the day 
        # Windows for piecewise infrastructure probability
        window_1 = minutes.indexer_between_time('0:00', t1, include_start=True, include_end=False)
        window_2 = minutes.indexer_between_time(t1, t2, include_start=True, include_end=False)
        window_3 = minutes.indexer_between_time(t2, '0:00', include_start=True, include_end=True)
        infr_pr = np.zeros(len(minutes))
        infr_pr[window_1] = prob_max
        infr_pr[window_2] = prob_min
        infr_pr[window_3] = prob_max
    elif isinstance(infr_prob, (int, float)): # Constant probability of finding infrastructure
        infr_pr = np.ones(len(minutes)) * infr_prob
        window_1 = 0
        window_2 = 0
        window_3 = 0

    # Definition of range in which the charging is shifted
    if charging_mode == 'Night Charge':
        charge_range = minutes.indexer_between_time('22:00', '7:00', include_start=True, include_end=False)
        charge_range_check = utils.charge_check_smart
    elif charging_mode == 'Self-consumption':
        charge_range = utils.pv_indexing(minutes, country, year, inputfile_pv = r"database\ninja_pv_europe_v1.1_merra2.csv")
        charge_range_check = utils.charge_check_smart
    elif charging_mode == "RES Integration":
        charge_range = utils.residual_load(minutes, residual_load, year, country)
        charge_range_check = utils.charge_check_smart
    else: 
        charge_range = 0
        charge_range_check = utils.charge_check_normal

    print('\nPlease wait for the charging profiles...')   

    for us_num, Us in enumerate(User_list): # Simulates for each user type
        
        #Initialise lists
        Charging_profile_user[Us.user_name] = []
        Charging_nom_profile_user[Us.user_name] = []
        SOC_user[Us.user_name] = []
        plug_in_user[Us.user_name] = []
        plug_in_user_v2g[Us.user_name] = []
        min_charge_user[Us.user_name] = []
        max_charge_user[Us.user_name] = []
        
        plug_in_Us = np.zeros((len(Profiles_user[Us.user_name]), Us.num_users), dtype = int) # Initialise plug-in array
        # Brings tha values put to 0.001 for the mask to 0
        Profiles_user[Us.user_name] = np.where(Profiles_user[Us.user_name] < 0.1, 0, Profiles_user[Us.user_name]) 
        # Sets to power consumed by the car to negative values
        power_Us = np.where(Profiles_user[Us.user_name] > 0, -Profiles_user[Us.user_name], 0) # requested power by the vehicle is negative
        power_Us = power_Us / 1000 #kW
        
        # Users who never take the car in the considered period are skipped
        power_Us = power_Us[:,np.where(power_Us.any(axis=0))[0]] 
        
        Battery_cap_Us_min = Us.App_list[0].Battery_cap * 60 # Capacity multiplied by 60 to evaluate the capacity in kWmin
        Battery_cap_Us_h = Us.App_list[0].Battery_cap

        for i in range(power_Us.shape[1]): # Simulates for each single user with at least one travel --> TO BE CHANGED since there is connection also
            
            # Filter power for the specific user            
            plug_in = np.copy(plug_in_Us[:,i])
            plug_in_cap = np.copy(plug_in_Us[:,i])
            plug_in_v2g = np.copy(plug_in_Us[:,i])

            power = np.copy(power_Us[:,i]) # charging power
            power_limit = np.copy(power_Us[:,i]) # max charging/discharging power
            power_nom = np.copy(power_Us[:,i]) # nominal charging station power
            discharge_depth = np.copy(power_Us[:,i])

            # Variation of SOC for each minute, 
            delta_soc = power / Battery_cap_Us_min 
            
            #Control rountine on the Initial SOC value
            if SOC_initial == 'random': #function to select random value
                SOC_init = utils.SOC_initial_f(SOC_max, SOC_min_rand, SOC_initial)           
            elif isinstance(SOC_initial, (int, float)): # If initial SOC is a number, that will be the initial SOC
                SOC_init = utils.SOC_initial_f_const(SOC_max, SOC_min_rand, SOC_initial)    
            
            # Calculation of the SOC array
            SOC = delta_soc
            SOC[0] = SOC_init
            SOC = np.cumsum(SOC)
            
            # Calculation of the indexes of each parking start and end 
            park_ind = np.where(power == 0)[0]
            park_ind = np.split(park_ind, np.where(np.diff(park_ind) != 1)[0]+1)
            park_ind = [[ind[0],ind[-1]+1] for ind in park_ind] #list of array of index of when there is a mobility travel
            
            en_to_charge = 0  # Initialise value for perfect foresight charging mode          
            
            # Iterates over all parkings (park = 0 corresponds to the period where no travel was made yet, so is not evaluated)
            for park in range(0, len(park_ind)): 

                # The iteration for park = 0 is needed only for Perfect Foresight strategy. For the other cases the first loop is skipped.
                if charging_mode != 'Perfect Foresight' and park == 0:
                    continue
                
                # SOC at the beginning of the parking
                SOC_park = SOC[park_ind[park][0]]
                
                if SOC_park >= SOC_max:
                    continue
                else:
                    pass
                
                # For the time based charging methods, the index of the parking period is calculated.
                # In the other cases is set to a dummy variable to avoid interection with "dummy" charge range
                if charging_mode in ['Night Charge', 'Self-consumption', 'RES Integration']:
                    # Index range of when the car is parked                
                    ind_park_range = np.arange(park_ind[park][0], park_ind[park][1])                    
                else:
                    ind_park_range = 1
                
                try:  # Energy used in the following travel
                    next_travel_ind_range = np.arange(park_ind[park][1], park_ind[park+1][0])
                    len_next_park =  park_ind[park+1][1] - park_ind[park+1][0]
                    if len_next_park < 10:
                        try:
                            next_travel_ind_range = np.arange(park_ind[park][1], park_ind[park+2][0])
                        except IndexError:
                            pass
                    en_next_travel = abs(np.sum(power[next_travel_ind_range]))                 
                except IndexError: # If there is an index error means we are in the last parking, special case
                    en_next_travel = 0

                if charging_mode != 'Perfect Foresight':  # If not perfect foresight set energy charge tot=0, will be calculated only if parking
                    en_charge_tot = 0
                else: # Calculating the energy consumed in the following travel   
                    en_charge_tot = (en_next_travel + en_to_charge)/eff
                
                if charging_mode == 'Perfect Foresight' and en_charge_tot < 0.1:
                    continue
                
                residual_energy = Battery_cap_Us_min*SOC_park  # Residual energy in the EV Battery

                # Control to check if the user can charge based on infrastructure 
                # availability, SOC, time of the day (Depending on the options activated)
                if (
                    (ch_prob(SOC_park) > np.random.rand() and                   # user behaviour - charging probability
                    infr_pr[park_ind[park][0]] > np.random.rand() and           # infrastructure availability
                    charge_range_check(ind_park_range, charge_range)            # check on charging window
                    ) or 
                    (np.around(SOC_park, 2) <= SOC_min) or                      # forced charging if SOC < SOC_min
                    (np.floor(residual_energy) <= np.ceil(en_next_travel/eff))  # forced charging if residual energy is not enough for next trip
                    ): 
                                        
                    # Calculates the parking time
                    t_park = park_ind[park][1] - park_ind[park][0]                 
                                        
                    # Samples the nominal power of the charging station
                    P_ch_nom = random.choices(P_ch_station_list, weights=prob_ch_station)[0]

                    # Fills the array of plug in (1 = plugged, 0 = not plugged)
                    plug_in[park_ind[park][0]:park_ind[park][1]] = 1                
                    power_limit[park_ind[park][0]:park_ind[park][1]] = min(P_ch_nom, Battery_cap_Us_h*(SOC_max-SOC_min))
                    power_nom[park_ind[park][0]:park_ind[park][1]] = P_ch_nom  
                    discharge_depth[park_ind[park][0]:park_ind[park][1]] = SOC_min

                    # In the case of perfect foresight the charging is shifted at the end of the parking, so a special routine is needed
                    if charging_mode == 'Perfect Foresight': # C'E' UN PORBLEMA -> SOC >1 manca un controllo !!!!!
                        t_ch_nom = min(en_charge_tot / P_ch_nom, t_park) # charging time with nominal power (float)
                        t_ch_tot = int(- (en_charge_tot // -P_ch_nom)) # Fast way to perform the operation:   int(math.ceil(en_charge_tot/P_ch_nom)) 
                        t_ch = min(t_ch_tot, t_park) # charge until SOC max, if parking time allows                   
                        P_charge = P_ch_nom*t_ch_nom/t_ch #charging for an integer number of minutes at the power equivalent to the one that would charge en_charge_tot without rounding
                        charge_end = park_ind[park][1]
                        charge_start = charge_end - t_ch
                        power[charge_start: charge_end] = P_charge
                        en_to_charge = en_charge_tot - (t_ch * P_charge)
                    else: # In the other charging modes a common routine is defined
                        en_charge_tot = Battery_cap_Us_min*(SOC_max - SOC_park)/eff
                        with np.errstate(divide='raise'):
                            try: # Charging strategy for time based modes (Night charge, RES integration, Self-consumption)
                                charge_ind_range = np.intersect1d(ind_park_range, charge_range)
                                # Minimum charging power (charging during night time)
                                P_ch_min = min(en_charge_tot/len(charge_ind_range), P_ch_nom)
                                np.put(power, charge_ind_range, P_ch_min)
                            # if intersection array is empty means that we are in forced charging 
                            # (SOC<0.2 / too low SOC residual), or in uncontrolled charging mode
                            except (FloatingPointError, ZeroDivisionError): 
                                t_ch_nom = min(en_charge_tot / P_ch_nom, t_park) # charging time with nominal power (float) [min]
                                t_ch_tot = int(- (en_charge_tot // -P_ch_nom)) # Fast way to perform the operation: int(math.ceil(en_charge_tot/P_ch_nom)) 
                                t_ch = min(t_ch_tot, t_park) # charge until SOC max, if parking time allows                   
                                P_charge = P_ch_nom*t_ch_nom/t_ch #charging for an integer number of minutes at the power equivalent to the one that would charge en_charge_tot without rounding
                                charge_start = park_ind[park][0]
                                charge_end = charge_start + t_ch
                                power[charge_start: charge_end] = P_charge
                                                  
                    delta_soc = power / Battery_cap_Us_min # charged power transleted into SOC increase [-]         
                    SOC = delta_soc
                    SOC[0] = SOC_init
                    SOC = np.cumsum(SOC)
                
                else: # if the user does not charge, then the energy consumed will be charged in a following parking                         
                    en_to_charge = en_charge_tot

                    # Connection to the grid driven by V2G
                    if (
                    con_prob(SOC_park) > np.random.rand() and                   # V2G connection probability
                    infr_pr[park_ind[park][0]] > np.random.rand() and           # infrastructure availability
                    charge_range_check(ind_park_range, charge_range)            # check on charging window
                    ):
                        plug_in_v2g[park_ind[park][0]:park_ind[park][1]] = 1
                        P_ch_nom = random.choices(P_ch_station_list, weights=prob_ch_station)[0]
                        
                        power_nom[park_ind[park][0]:park_ind[park][1]] = P_ch_nom
                        power_limit[park_ind[park][0]:park_ind[park][1]] = min(P_ch_nom, Battery_cap_Us_h*(SOC_max-SOC_min)) # The maximum theoretical charge limit is set by the minimum between the available battery capacity and the charging power         
                        discharge_depth[park_ind[park][0]:park_ind[park][1]] = SOC_min
                try:
                    discharge_depth[park_ind[park][1]] = en_next_travel / Battery_cap_Us_min + SOC_min
                except IndexError: # If there is an index error means we are in the last parking, special case
                    discharge_depth[park_ind[park][0]] = en_next_travel / Battery_cap_Us_min + SOC_min

            charging_limit_power = np.where(power_nom<0, 0, power_limit) # Filtering only the nominal charging power
            charging_nom_power = np.where(power_nom<0, 0, power_nom) # Filtering only the nominal charging power 
            charging_power = np.where(power<0, 0, power) # Filtering only the charging power 
            charging_cap = np.where(charging_power >= 0.00001, 1, 0) # 1 is placed when the vehicle is charging
            min_charge_en = np.where(discharge_depth < 0, 0, discharge_depth)
            min_charge_en = np.where(min_charge_en == 0, SOC_min, min_charge_en)
            max_charge_en = np.where(charging_nom_power>0, SOC_max, min_charge_en)

            # SOC_user[Us.user_name].append(SOC)
            # Charging_profile_user[Us.user_name].append(power_pos)
            # plug_in_user[Us.user_name].append(plug_in)
            # plug_in_user_v2g[Us.user_name].append(plug_in_v2g)
            
            Charging_profile = Charging_profile + charging_nom_power
            
            Charging_limit_profile = Charging_limit_profile + charging_limit_power
            Charging_nom_profile = Charging_nom_profile + charging_nom_power
            Plug_in_profile = Plug_in_profile + plug_in + plug_in_v2g
            Plug_in_profile_cap = Plug_in_profile_cap + (plug_in) * Battery_cap_Us_h * SOC_max    # plugged-in total capacities [kWh]
            Plug_in_v2g_profile_cap = Plug_in_v2g_profile_cap + plug_in_v2g * Battery_cap_Us_h    # plugged-in total capacities [kWh] due to V2G purposes
            Charging_profile_cap = Charging_profile_cap + charging_cap * Battery_cap_Us_h         # In-charging total capacities [kWh]


            SOC_f=SOC[dummy_minutes:-dummy_minutes]
            charging_power_f=charging_power[dummy_minutes:-dummy_minutes]
            charging_nom_power_f=charging_nom_power[dummy_minutes:-dummy_minutes]
            plug_in_f = plug_in[dummy_minutes:-dummy_minutes]
            plug_in_v2g_f = plug_in_v2g[dummy_minutes:-dummy_minutes]
            min_charge_en_f = min_charge_en[dummy_minutes:-dummy_minutes]
            max_charge_en_f = max_charge_en[dummy_minutes:-dummy_minutes]

            # print(plug_in_v2g)
            plug_in_user[Us.user_name].append(plug_in_f)
            plug_in_user_v2g[Us.user_name].append(plug_in_v2g_f)
            Charging_profile_user[Us.user_name].append(charging_power_f)
            Charging_nom_profile_user[Us.user_name].append(charging_nom_power_f)
            SOC_user[Us.user_name].append(SOC_f)
            min_charge_user[Us.user_name].append(min_charge_en_f)
            max_charge_user[Us.user_name].append(max_charge_en_f)

            batt_cap_tot=batt_cap_tot+Battery_cap_Us_h

            ### Calculate the part of battery capacity available to the TSO for V2G option (deactivated)
            # if charging_mode == 'Perfect Foresight':
            #     en_system = (Battery_cap_Us_min - charging_power) * plug_in
            #     en_sys_tot = en_sys_tot + en_system

            if all(SOC > 0): #Check that the car never has SOC < 0
                continue
            else: 
                SOC_user[Us.user_name].append(SOC)
                # Charging_profile_user[Us.user_name].append(charging_power)
                # plug_in_user[Us.user_name].append(plug_in_f)
                # plug_in_user_v2g[Us.user_name].append(plug_in_v2g_f)

                neg_soc_ind = np.where(SOC < 0)[0]
                neg_soc_ind = np.split(neg_soc_ind, np.where(np.diff(neg_soc_ind) != 1)[0]+1)
                neg_soc_ind = [[ind[0],ind[-1]+1] for ind in neg_soc_ind] # list of array of index of when there is a mobility travel
                print(f"[WARNING: Charging process User {i + 1} ({Us.user_name}) not properly constructed, SOC < 0 in time {neg_soc_ind}]") 
                # SOC_user[Us.user_name].append(SOC)
                # Charging_profile_user[Us.user_name].append(power_pos)
                # plug_in_user[Us.user_name].append(plug_in)
       
        num_us = num_us + Us.num_users
        print(f'Charging Profile of "{Us.user_name}" user completed ({num_us}/{tot_users})') #screen update about progress of computation
    
    Charging_profile = Charging_profile[dummy_minutes:-dummy_minutes]
    Charging_nom_profile = Charging_nom_profile[dummy_minutes:-dummy_minutes]
    Plug_in_profile = Plug_in_profile[dummy_minutes:-dummy_minutes]
    Plug_in_profile_cap = Plug_in_profile_cap[dummy_minutes:-dummy_minutes]/batt_cap_tot
    Plug_in_v2g_profile_cap = Plug_in_v2g_profile_cap[dummy_minutes:-dummy_minutes]/batt_cap_tot
    Charging_profile_cap = Charging_profile_cap[dummy_minutes:-dummy_minutes]/batt_cap_tot
    Charging_limit_profile = Charging_limit_profile[dummy_minutes:-dummy_minutes]

    # Charging_profile_user=dict(itertools.islice(Charging_profile_user.items(), dummy_days, n_periods/1440 - dummy_days))
    # en_sys_tot = en_sys_tot[dummy_minutes:-dummy_minutes]
    
    return (Charging_profile, Charging_profile_user, SOC_user, Plug_in_profile_cap, plug_in_user, Charging_profile_cap,
     Plug_in_v2g_profile_cap, plug_in_user_v2g, Plug_in_profile, Charging_nom_profile_user, Charging_limit_profile, min_charge_user, max_charge_user, Charging_nom_profile)

