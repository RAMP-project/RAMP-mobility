# -*- coding: utf-8 -*-

#%% Initialisation of a model instance

import importlib
import datetime
import calendar
import pytz
import numpy as np 

from ramp_mobility import country_input_files

# Import holidays package 
import holidays 

#%% Initialise model

def yearly_pattern(country, year):
    '''
    Definition of a yearly pattern of weekends and weekdays, in case some appliances have specific wd/we behaviour
    ''' 
    # Number of days to add at the beginning and the end of the simulation to avoid special cases at the beginning and at the end
    dummy_days = 5

    #Yearly behaviour pattern
    first_day = datetime.date(year, 1, 1).strftime("%A")
    
    if calendar.isleap(year):
        year_len = 366
    else: 
        year_len = 365
        
    Year_behaviour = np.zeros(year_len)
    
    dict_year = {'Monday'   : [5, 6], 
                 'Tuesday'  : [4, 5], 
                 'Wednesday': [3, 4],
                 'Thursday' : [2, 3], 
                 'Friday'   : [1, 2], 
                 'Saturday' : [0, 1], 
                 'Sunday'   : [6, 0]}
      
    for d in dict_year.keys():
        if first_day == d:
            Year_behaviour[dict_year[d][0]:year_len:7] = 1
            Year_behaviour[dict_year[d][1]:year_len:7] = 2
    
    # Adding Vacation days to the Yearly pattern

    if country == 'EL': 
        country = 'GR'
    elif country == 'FR':
        country = 'FRA'
        
    try:
        holidays_country = list(holidays.CountryHoliday(country, years = year).keys())
    except KeyError: 
        c_error = {'LV':'LT', 'RO':'BG'}
        print(f"[WARNING] Due to a known issue, the version of the holidays package you automatically installed is the 0.10.2, not containing {country}. Please refer to 'https://github.com/dr-prodigy/python-holidays/issues/338' for an explanation on how to install holidays 0.10.3. Otherwise, holidays from {c_error[country]} will be used.")
        country = c_error[country]
        holidays_country = list(holidays.CountryHoliday(country, years = year).keys())

    for i in range(len(holidays_country)):
        day_of_year = holidays_country[i].timetuple().tm_yday
        Year_behaviour[day_of_year-1] = 2
    
    dummy_days_array = np.zeros(dummy_days) 
    
    Year_behaviour = np.hstack((dummy_days_array, Year_behaviour, dummy_days_array))
    
    return(Year_behaviour, dummy_days)

def user_defined_inputs(inputfile):
    '''
    Imports an input file and returns a processed User_list
    '''
    inputfile_module = inputfile.replace('/', '.')
    
    file_module = importlib.import_module(f'country_input_files.{inputfile_module}')
    

    User_list = file_module.User_list
        
    return(User_list)

def Initialise_model(dummy_days, full_year, year):
    '''
    The model is ready to be initialised
    '''
    # Simulating n days before and after the wished number of profiles
    if full_year: 
        if calendar.isleap(year): # In case several countries shall be simulated in a loop, use fixed number of days 
            num_profiles_user = 366 # leap full year
        else:
            num_profiles_user = 365  # normal full year
    else:
        num_profiles_user = int(input("Please indicate the number of profiles (days) to be generated: ")) #asks the user how many profiles (i.e. code runs) he wants

    num_profiles_sim = num_profiles_user + (2 * dummy_days)
    
    
    assert 1 <= num_profiles_user <= 366, '[CRITICAL] Incorrect number of profiles, please provide a number higher than 0, up to 366'
    print('Please wait...') 
    
    Profile = [] #creates empty lists to store the results of each code run, i.e. each stochastically generated profile
    Usage = []
    Profile_user = []
    Usage_user = []

    return (Profile, Usage, Profile_user, Usage_user, num_profiles_user, num_profiles_sim)
    
def Initialise_inputs(inputfile, country, year, full_year):
    
    Year_behaviour, dummy_days = yearly_pattern(country, year)
    User_list = user_defined_inputs(inputfile)
    (Profile, Usage, Profile_user, Usage_user, num_profiles_user,num_profiles_sim
     ) = Initialise_model(dummy_days, full_year, year)
    
    if calendar.isleap(year) and num_profiles_user == 365:
        print('[WARNING] A leap year is being simulated with 365 days, if you want to simulate the whole year please insert 366 as profiles number') 

    # Calibration parameters
    '''
    Calibration parameters. These can be changed in case the user has some real data against which the model can be calibrated
    They regulate the probabilities defining the largeness of the peak window and the probability of coincident switch-on within the peak window
    '''
    peak_enlarg = 0 #percentage random enlargement or reduction of peak time range length
    mu_peak = 0.5 #median value of gaussian distribution [0,1] by which the number of coincident switch_ons is randomly selected
    s_peak = 1 #standard deviation (as percentage of the median value) of the gaussian distribution [0,1] above mentioned
    
    return (peak_enlarg, mu_peak, s_peak, Year_behaviour, User_list, Profile, 
            Usage, Profile_user, Usage_user, num_profiles_user, num_profiles_sim, dummy_days)


