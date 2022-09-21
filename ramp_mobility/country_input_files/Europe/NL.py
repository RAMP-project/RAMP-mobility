# -*- coding: utf-8 -*-

#%% Definition of the inputs
from country_input_files.input_functions import common_inputs, data_loading, data_processing, creating_users
'''
Input data definition 
'''
#Define Country and file location
country = 'NL'
inputfolder = r"../database/"

#Total number of users to be simulated
tot_users = 2500
User_list = []

# Load common inputs
(P_var, r_d, r_v, r_w, occasional_use, Par_P_EV, Battery_cap, country_equivalent) = common_inputs(country)
# Optional section to set country specific variabilities and EV fleet characteristics
'''
#Variabilities 
P_var = 0.1 #random in power
r_d   = 0.3 #random in distance
r_v   = 0.3 #random in velocity
#Variabilites in functioning windows 
r_w = {}; r_w['working'] = 0.25; r_w['student'] = 0.25; r_w['inactive'] = 0.2; r_w['free time'] = 0.2
#Occasional use 
occasional_use = {}
occasional_use['weekday'] = 1; occasional_use['saturday'] = 0.6; occasional_use['sunday'] = 0.5
occasional_use['free time'] = {'weekday': 0.15, 'weekend': 0.3} #1/7, meaning taking car for free time once a week
#Calibration parameters for the Velocity - Power Curve [kW]
Par_P_EV = {}; Par_P_EV['small']  = [0.26, -13, 546]; Par_P_EV['medium'] = [0.3, -14, 600]; Par_P_EV['large']  = [0.35, -15.2, 620]
#Battery capacity [kWh]
Battery_cap = {}; Battery_cap['small']  = 37; Battery_cap['medium'] = 60; Battery_cap['large']  = 100
'''
# Load country-dependent files from database
(pop_data, vehicle_data, d_tot_data, d_min_data, t_func_data, window_data, trips) = data_loading(inputfolder,country_equivalent)
# Process country-dependent data
(pop_sh, vehicle_sh, d_tot, d_min, t_func, window, perc_usage) = data_processing(country, country_equivalent, pop_data, vehicle_data, d_tot_data, d_min_data, t_func_data, window_data, trips)
# Create Users and Appliances
User_List = creating_users(User_list, tot_users, pop_sh, vehicle_sh, Par_P_EV, Battery_cap, P_var, d_tot, perc_usage, r_d, t_func, r_v, d_min, occasional_use, window, r_w)