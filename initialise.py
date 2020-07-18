# -*- coding: utf-8 -*-

#%% Initialisation of a model instance

from core import np, pd
import importlib
import datetime
import calendar
import pytz

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
                 'Sunday'   : [0, 6]}
      
    for d in dict_year.keys():
        if first_day == d:
            Year_behaviour[dict_year[d][0]:year_len:7] = 1
            Year_behaviour[dict_year[d][1]:year_len:7] = 2
    
    # Adding Vacation days to the Yearly pattern
    
    if country == 'RO': 
        print("[WARNING] Due to a known issue, the automatically installed version of the holidays package is not the latest one containing Romania. Please refer to https://github.com/dr-prodigy/python-holidays/issues/338 for an explanation on how to install holidays' latest version. For the time being holidays from Bulgaria will be used.")
        country = 'BG'
    elif country == 'LV':
        print("[WARNING] Due to a known issue, the automatically installed version of the holidays package is not the latest one containing Latvia. Please refer to https://github.com/dr-prodigy/python-holidays/issues/338 for an explanation on how to install holidays' latest version. For the time being holidays from Lithuania will be used.")
        country = 'LT'
    elif country == 'EL': 
        country = 'GR'
    elif country == 'FR':
        country = 'FRA'
        
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
    User_list = getattr((importlib.import_module(f'Input_files.{inputfile_module}')), 'User_list')
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
        num_profiles_user = int(input("Please indicate the number of profiles to be generated: ")) #asks the user how many profiles (i.e. code runs) he wants

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

#%% Support functions for the charging process 
    
def charge_prob(SOC):
    
    k = 15
    per_SOC = 0.5
    
    p = 1-1/(1+np.exp(-k*(SOC-per_SOC)))
       
    return p

def charge_prob_const(SOC):        
    
    p = 1       
    
    return p

def SOC_initial_f(SOC_max, SOC_min, SOC_initial):
    
    SOC_i = np.random.rand()*(SOC_max-SOC_min) + SOC_min
    
    return SOC_i

def SOC_initial_f_const(SOC_max, SOC_min, SOC_initial):
    
    SOC_i = SOC_initial
        
    return SOC_i

def charge_check_smart(ind_park_range, charge_range):
    
    b = np.isin(ind_park_range, charge_range, assume_unique = True).any()

    return b

def charge_check_normal(ind_park_range, charge_range):
    
    b = True

    return b

def pv_indexing(minutes, country, year, inputfile_pv = r"Input_data\ninja_pv_europe_v1.1_merra2.csv"):
      
    pv_af = pd.read_csv(inputfile_pv, index_col = 0) #Read the input file
    pv_af = pd.DataFrame(pv_af[country]) #Filter only for needed country
    ind_init = pd.date_range(start=pv_af.index[0], end=pv_af.index[-1], freq='H', tz = 'UTC')
    pv_af.set_index(ind_init, inplace = True) #Set index to datetime
    pv_af_tz = pv_af.tz_convert(pytz.country_timezones[country][0]) # Convert to country timezone
    
    pv_af_loc = pv_af_tz.tz_localize(None, ambiguous = 'NaT') # Remove the timezone information (local time)
    pv_af_loc = pv_af_loc[~pv_af_loc.index.duplicated(keep='first')] # Remove duplicate hours arising from tz conversion

    pv_af_loc = pv_af_loc.loc[str(year)]
    pv_non_zero_mean = pv_af_loc[pv_af_loc != 0].mean().values #calculate mean of non zero values

    pv_af_tz_high = pv_af_loc[pv_af_loc > pv_non_zero_mean].fillna(0) # filter values higher than the mean
    
    pv_af = pv_af_tz_high.resample('T', closed='right').pad() #resample with minute time detail
    pv_af = pv_af.loc[minutes[0]:  minutes[-1]] #filter for the simulated period
    
    pv_ind = np.nonzero(pv_af.values)[0] #extract indexes 
        
    return pv_ind

def residual_load(minutes, residual_load, year, country):
        
    residual_load_temp = pd.DataFrame(residual_load.values)
    
    ind_init = pd.date_range(start= f'{year}-01-01', end=f'{year}-12-31 23:00', freq='H', tz = 'UTC')
    residual_load_temp.set_index(ind_init, inplace = True)
    
    residual_load_temp_tz = residual_load_temp.tz_convert(pytz.country_timezones[country][0])
    
    residual_load_temp = residual_load_temp_tz.tz_localize(None, ambiguous = 'NaT') # Remove the timezone information (local time)
    residual_load_temp = residual_load_temp[~residual_load_temp.index.duplicated(keep='first')] # Remove duplicate hours arising from tz conversion

    residual_load_temp = residual_load_temp.loc[minutes[0]: minutes[-1]] #filter for the simulated period

    res_load_neg = residual_load_temp[residual_load_temp < 0].fillna(0)
            
    res_load_neg_ind = np.nonzero(res_load_neg.values)[0]
    
    return res_load_neg_ind
    
def tot_users_calc(User_list):
    # Calculation of the total number of users
    num_users = {}
    for i in range(len(User_list)):
        num_users[User_list[i].user_name] = User_list[i].num_users
        tot_users = sum(num_users.values())
    
    return tot_users

def tot_battery_cap_calc(User_list):
    # Calculation of the total fleet battery capacity
    cap_users = {}
    for Us in User_list:
        cap_users[Us.user_name] = Us.num_users *  Us.App_list[0].Battery_cap
        tot_cap_users = sum(cap_users.values())
    
    return tot_cap_users
