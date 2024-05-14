# -*- coding: utf-8 -*-
"""
Created on Mon Feb 3 09:30:00 2020
This is the code for the open-source stochastic model for the generation of 
electric vehicles load profiles in Europe, called RAMP-mobility.

@authors:
- Andrea Mangipinto, Politecnico di Milano
- Francesco Lombardi, TU Delft
- Francesco Sanvito, Politecnico di Milano
- Sylvain Quoilin, KU Leuven
- Emanuela Colombo, Politecnico di Milano

Copyright 2020 RAMP, contributors listed above.
Licensed under the European Union Public Licence (EUPL), Version 1.2;
you may not use this file except in compliance with the License.

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations
under the License.
"""

#%% Import required modules

import sys,os
sys.path.append('../')
import ramp_mobility

from core_model.stochastic_process_mobility import Stochastic_Process_Mobility
from core_model.charging_process import Charging_Process
from post_process import post_process as pp

import pandas as pd
from datetime import datetime

from post_process import calliope_ready_output as call

# Set code starting time, to compute execution time
startTime = datetime.now()

'''
Calls the stochastic process and saves the result in a list of stochastic profiles [kW]
In this default example, the model runs for 1 input files ("IT"),
but single or multiple files can be run increasing the list of countries to be run
and naming further input files with corresponding country code
'''
#%% Inputs definition

charging = True         # True or False to select to activate the calculation of the charging profiles 
write_variables = True  # Choose to write variables to csv
full_year = False       # Choose if simulating the whole year (True) or not (False), if False, the console will ask how many days should be simulated.

# countries = ['AT', 'BE', 'BG', 'CH', 'CZ', 'DE', 'DK', 'EE', 'EL', 'ES', 'FI', 'FR', 'HR', 'HU',
#     'IE', 'IT','LT', 'LU','LV', 'NL', 'NO', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK', 'UK']
countries = ['DE']
             
for c in countries:
    # Define folder where results are saved, it will be:
    # "results/inputfile/simulation_name" leave simulation_name False (or "")
    # to avoid the creation of the additional folder
    inputfile = f'Europe/{c}'
    
    # Define country and year to be considered when generating profiles
    country = f'{c}'
    year = 2016
    
    # Define attributes for the charging profiles
    charging_mode = 'Uncontrolled' # Select charging mode ('Uncontrolled', 'Night Charge', 'RES Integration', 'Perfect Foresight')
    logistic = True # Select the use of a logistic curve to model the probability of charging based on the SOC of the car
    infr_prob = 0.8 # Probability of finding the infrastructure when parking ('piecewise', number between 0 and 1)
    Ch_stations = ([3.7, 11, 120], [0.6, 0.3, 0.1]) # Define nominal power of charging stations and their probability 
    V2G = True # Mode for which the probability to get connected is evaluated for V2G purposes and not only charging

    #inputfile for the temperature data: 
    inputfile_temp = os.path.join("..", "database", "temp_ninja_pop_1980-2019.csv")
    
    ## If simulating the RES Integration charging strategy, a file with the residual load curve should be included in the folder
    try:
        inputfile_residual_load = os.path.join("..", "database", "residual_load", f"residual_load_{c}.csv")
        residual_load = pd.read_csv(inputfile_residual_load, index_col = 0)
    except FileNotFoundError:      
        residual_load = pd.DataFrame(0, index=range(1), columns=range(1))
    
    
    #%% Call the functions for the simulation
    
    # Simulate the mobility profile 
    (Profiles_list, Usage_list, User_list, Profiles_user_list, dummy_days, Usage_user, Usage_tot, Usage_tt, Profile_tot
     ) = Stochastic_Process_Mobility(inputfile, country, year, full_year)
    
    # Post-processes the results and generates plots
    Profiles_avg, Profiles_list_kW, Profiles_series = pp.Profile_formatting(
        Profiles_list)
    Usage_avg, Usage_series = pp.Usage_formatting(Usage_list)
    Profiles_user = pp.Profiles_user_formatting(Profiles_user_list)
    
    # If more than one daily profile is generated, also cloud plots are shown
    if len(Profiles_list) > 1:
        pp.Profile_cloud_plot(Profiles_list, Profiles_avg)
    
    # Create a dataframe with the profile
    Profiles_df = pp.Profile_dataframe(Profiles_series, year) 
    Usage_df = pp.Usage_dataframe(Usage_series, year)
    
    # Time zone correction for profiles and usage
    Profiles_utc = pp.Time_correction(Profiles_df, country, year) 
    Usage_utc = pp.Time_correction(Usage_df, country, year)    
    
    # By default, profiles and usage are plotted as a DataFrame
    pp.Profile_df_plot(Profiles_df, start = '01-01 00:00:00', end = '12-31 23:59:00', year = year, country = country)
    pp.Usage_df_plot(Usage_utc, start = '01-01 00:00:00', end = '12-31 23:59:00', year = year, country = country, User_list = User_list)
    
    # Add temperature correction to the Power Profiles 
    # To be done after the UTC correction because the source data for Temperatures have time in UTC
    temp_profile = pp.temp_import(country, year, inputfile_temp) #Import temperature profiles, change the default path to the custom one
    Profiles_temp = pp.Profile_temp(Profiles_utc, year = year, temp_profile = temp_profile)
    
    # Resampling the UTC Profiles
    Profiles_temp_h = pp.Resample(Profiles_temp)
    
    #Exporting all the main quantities
    if write_variables:
        pp.export_csv('Mobility Profiles', Profiles_temp, inputfile, simulation_name)
        pp.export_csv('Mobility Profiles Hourly', Profiles_temp_h, inputfile, simulation_name)
        pp.export_csv('Usage', Usage_utc, inputfile, simulation_name)
    #   pp.export_pickle('Profiles_User', Profiles_user_temp, inputfile, simulation_name)
        
    if charging:
        
        Profiles_user_temp = pp.Profile_temp_users(Profiles_user, temp_profile,
                                                   year, dummy_days)
     
        # Charging process function: if no problem is detected, only the cumulative charging profile is calculated. Otherwise, also the user specific quantities are included. 
        (Charging_profile, Ch_profile_user, SOC_user, Plug_in_profile_cap, plug_in_user,
        Charging_profile_cap, Plug_in_v2g_profile_cap, plug_in_user_v2g, Plug_in_profile, 
        Charging_nom_profile_user, Charging_limit_profile, min_charge_user, max_charge_user, Charging_nom_profile) = Charging_Process(
            Profiles_user_temp, User_list, country, year,dummy_days, 
            residual_load, charging_mode, logistic, infr_prob, Ch_stations, V2G)        


        Charging_limit_profile = Charging_limit_profile/max(Charging_nom_profile)

        # Postprocess of charging profiles and plug-in profiles
        Charging_profiles_utc = pp.time_conversion(Charging_profile, country, year) 

        Plug_in_profile_utc = pp.time_conversion(Plug_in_profile, country, year)                                            
        
        Plug_in_profile_cap_utc = pp.time_conversion(Plug_in_profile_cap, country, year) 
        
        Plug_in_v2g_profile_cap_utc = pp.time_conversion(Plug_in_v2g_profile_cap, country, year)

        Charging_profile_cap_utc = pp.time_conversion(Charging_profile_cap, country, year) 

        Charging_limit_profile_utc = pp.time_conversion(Charging_limit_profile, country, year)
        
        Discharge_depth_profile_utc = pp.time_conversion(call.average_norm_profile(min_charge_user,'mean'), country, year)
        
        Charge_depth_profile_utc = pp.time_conversion(call.average_norm_profile(max_charge_user,'mean'), country, year)

        resume = pd.concat([Plug_in_profile_cap_utc,Plug_in_v2g_profile_cap_utc,Charging_profile_cap_utc,Charging_profiles_utc,Profiles_temp, Discharge_depth_profile_utc, Charge_depth_profile_utc],axis=1)
        resume = resume.set_axis(['Plug_in_profiles','Plug_in_v2g_profile','Charging_profile_cap','Charging_profile', 'Mobility_profile', 'Discharge_depth_profile', 'Charge_depth_profile'], axis=1, inplace=False)
        resume["Plug_in not-charging"]=resume['Plug_in_profiles']-resume['Charging_profile_cap']
        resume["Plug_in_tot"]=resume['Plug_in_profiles']+resume['Plug_in_v2g_profile']
        
        """Calliope input generation"""
        
        # (large_vehicles_prof, medium_vehicles_prof, small_vehicles_prof) = call.mobility_profiles(Profile_tot, country, year)

        # Calliope input export
        # pp.export_csv('Large vehicle profile', large_vehicles_prof, inputfile, simulation_name)
        # pp.export_csv('Medium vehicle profile', medium_vehicles_prof, inputfile, simulation_name)
        # pp.export_csv('Small vehicle profile', small_vehicles_prof, inputfile, simulation_name)
        pp.export_csv('Charging limit profile', Charging_limit_profile_utc, inputfile, simulation_name)

        # Export charging profiles in csv
        pp.export_csv('Charging Profiles', Charging_profiles_utc, inputfile, simulation_name)
        pp.export_csv('Plug-in Profiles', Plug_in_profile_utc, inputfile, simulation_name)
        pp.export_csv('Plug-in Profiles cap', Plug_in_profile_cap_utc, inputfile, simulation_name)
        pp.export_csv('Plug-in V2G Profiles', Plug_in_v2g_profile_cap_utc, inputfile, simulation_name)
        pp.export_csv('Charging_cap profile', Charging_profile_cap_utc, inputfile, simulation_name)
        pp.export_csv('Resume', resume, inputfile, simulation_name)

        pp.export_csv('charging_limit',pp.Resample(Charging_limit_profile_utc),inputfile, simulation_name)
        pp.export_csv('depth_of_discharge',pp.Resample(Discharge_depth_profile_utc),inputfile,simulation_name)
        pp.export_csv('depth_of_charge',pp.Resample(Charge_depth_profile_utc),inputfile,simulation_name)
    
        # Plot the charging profile
        pp.Charging_Profile_df_plot(Charging_profiles_utc, color = 'green', start = '01-01 00:00:00', end = '12-31 23:59:00', year = year, country = country)

        (SOC_large_profile_utc, SOC_medium_profile_utc, SOC_small_profile_utc)=call.depth_of_discharge(SOC_user, country, year)
        
        df=resume[["Charging_profile_cap","Plug_in not-charging","Plug_in_v2g_profile"]]
        df.plot.area()
        
    print('\nExecution Time:', datetime.now() - startTime)
