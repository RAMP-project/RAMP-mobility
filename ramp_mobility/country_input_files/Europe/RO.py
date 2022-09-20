# -*- coding: utf-8 -*-

#%% Definition of the inputs
from country_input_files.input_functions import common_inputs, data_loading, data_processing, creating_users
'''
Input data definition 
'''
#Define Country and file location
country = 'RO'
inputfolder = r"../database/"

#Total number of users to be simulated
tot_users = 2500
User_list = []

# Load common inputs
(P_var, r_d, r_v, r_w, occasional_use, Par_P_EV, Battery_cap, country_equivalent) = common_inputs(country)
# Load country-dependent files from database
(pop_data, vehicle_data, d_tot_data, d_min_data, t_func_data, window_data, trips) = data_loading(inputfolder,country_equivalent)
# Process country-dependent data
(pop_sh, vehicle_sh, d_tot, d_min, t_func, window, perc_usage) = data_processing(country, country_equivalent, pop_data, vehicle_data, d_tot_data, d_min_data, t_func_data, window_data, trips)
# Create Users and Appliances
User_List = creating_users(User_list, tot_users, pop_sh, vehicle_sh, Par_P_EV, Battery_cap, P_var, d_tot, perc_usage, r_d, t_func, r_v, d_min, occasional_use, window, r_w)