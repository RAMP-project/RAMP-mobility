<img src="https://github.com/RAMP-project/RAMP-mobility/blob/master/RAMP-mobility_logo.png" width="300">

*RAMP-mobility - Getting started.*

---

This short tutorial describes the main steps to get a practical example of RAMP-Mobility running.

## Prerequisites
Install Python, with full scientific stack. The [Anaconda distribution](https://www.anaconda.com/products/individual) is recommended since it comprises all the required packages. If Anaconda is not used, the following libraries and their dependencies should be installed manually:

- numpy>=1.10
- matplotlib>=1.5.1
- pandas>= 0.24.0
- convertdate
- holidays

## Step-by-step example of a RAMP-Mobility run

To get started, make sure that you have git installed and type the following in the Anaconda Prompt:

```bash
git clone https://github.com/RAMP-project/RAMP-mobility.git
cd RAMP-mobility
conda env create  # Automatically creates environment based on environment.yml
conda activate ramp-mobility # Activate the environment
```
The above commands create a dedicated environment so that your anaconda configuration remains clean from the required dependencies installed. 
Then, using your favourite IDE (the model is developed with [Spyder](https://www.spyder-ide.org/)) open the RAMP_run.py script.

### Inputs definition

The file is divided in different sections. After the preamble and the import of the required modules, the Inputs are defined: 

```python
#%% Inputs definition

charging = True         # True or False to select to activate the calculation of the charging profiles
write_variables = True # Choose to write variables to csv

countries = ['AT', 'BE', 'BG', 'CH', 'CZ', 'DE', 'DK', 'EE', 'EL', 'ES', 'FI', 'FR', 'HR', 'HU',
   'IE', 'IT','LT', 'LU','LV', 'NL', 'NO', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK', 'UK']
```
The first step is the definition of the control variables *charging*, which activates the calculation of the EV charging profile based on the mobility profile and *write_variables* which activates the writing of the variables in cvs files.

Then, for each of the selected countries (at the moment only EU27 plus United Kingdom, Norway and Switzerland minus Malta and Cyprus are supported) the model is simulated. 

```python
for c in countries:
    # Define folder where results are saved, it will be:
    # "results/inputfile/simulation_name" leave simulation_name False (or "")
    # to avoid the creation of the additional folder
    inputfile = f'Europe/{c}'
    simulation_name = ''
    
    # Define country and year to be considered when generating profiles
    country = f'{c}'
    year = 2016

    # Choose if simulating the whole year (True) or not (False)
    # if False, the console will ask how many days should be simulated. 
    full_year = False
```

The variables to be defined are:

- *simulation_name*: defines the folder where results are saved, it will be: “results/inputfile/simulation_name" leave it False (or "") to avoid the creation of the additional folder.
- *year*: defines the simulated year
- *full_year*: allows choosing if simulating the whole year (True) or not (False). If False, the console will ask how many days should be simulated. This is useful when simulating different countries within a for loop. 

### Charging process function parameters

Four variables have to be defined for the charging process function: 

```python
    # Define attributes for the charging profiles
    charging_mode = 'Uncontrolled' # Select charging mode (Uncontrolled', 'Night Charge', 'RES Integration', 'Perfect Foresight')
    logistic = False # Select the use of a logistic curve to model the probability of charging based on the SOC of the car
    infr_prob = 0.8 # Probability of finding the infrastructure when parking ('piecewise', number between 0 and 1)
    Ch_stations = ([3.7, 11, 120], [0.6, 0.3, 0.1]) # Define nominal power of charging stations and their probability 
```

*charging_mode*: defines the user charging strategy. Four charging strategies are implemented, to simulate different scenarios.
1.	Uncontrolled: the base case, where no control over the user behaviour is applied. If the charging point is available, the battery is charged immediately at the nominal power, until a user-defined value of SOCmax.
2.	Perfect Foresight: strategy aiming at quantifying the possibility to implement a Vehicle-to-grid solution. If the charging point is available, the car is charged right before the end of the parking, at the nominal power, until the SOC satisfies the needs of the following journey. This allows to compute the part of the vehicle's battery available to the system, without affecting the user driving range.
3.	Night Charge: first smart charging strategy. It aims at shifting the charging events to the night period. The car is charged only if the charging point is available and the parking happens during nighttime.
4.	RES Integration: second smart charging method. Has the goal of coupling the renewable power generation with the transport sector. The car is charged only if the charging point is available and the parking happens during periods when there is excess of renewable power production. As this condition is evaluated through the residual load curve, a file containing it should be provided in the folder "Input_data/Residual Load duration curve/residual load".

*logistic*: activates the use of a logistic curve to model the probability of charging based on the SOC of the car. This makes the probability of charging higher, the lower the car SOC. The shape of the curve is defined in the charge_prob(SOC) function, in the “initialise.py” file.

```python
def charge_prob(SOC):
    
    k = 15
    per_SOC = 0.5
    
    p = 1-1/(1+np.exp(-k*(SOC-per_SOC)))
       
    return p
```

*infr_prob*: probability of finding the charging infrastructure when parking. It can be set to either a number between 0-1 or to 'piecewise'. This activates a piecewise curve with higher probability of finding the charging infrastructure in the morning or in the evening. The shape of the piecewise function can be changed in the preamble of the Charging_process function in the charging_process.py file. 

```python
def Charging_Process(Profiles_user, User_list, country, year, ...):
    
    [...]
    
    # Parameters for the piecewise infrastructure probability function
    prob_max = 0.9
    prob_min = 0.4
    t1 = '06:00'
    t2 = '19:00'
```

*Ch_stations*: defines the nominal power of the available charging stations and their probability, respectively.

### External Input files

Next, the input file for the temperature data (automatically provided with data from 1980 to 2016) and the residual load (only needed when simulating the RES Integration charging strategy) curve should be defined. 

```python
#inputfile for the temperature data: 
inputfile_temp = r"Input_data\temp_ninja_pop.csv"

## If simulating the RES Integration charging strategy, a file with the residual load curve should be included in the folder
try:
    inputfile_residual_load = fr"Input_data\Residual Load duration curve\residual load\residual_load_{c}.csv"
    residual_load = pd.read_csv(inputfile_residual_load, index_col = 0)
except FileNotFoundError:      
    residual_load = pd.DataFrame(0, index=range(1), columns=range(1))
```

### Outputs

4 csv files are generated as output in the “/results” folder: 

- Mobility Profiles: a time series, with minute temporal detail, representing the power requested by the car to the battery in order to satisfy the transport needs of the users.
- Mobility Profiles Hourly: same as Mobility Profiles, but with hourly temporal detail.
- Usage Profiles:  a time series, with minute temporal detail, representing the number of cars driving in each time step.
- Charging Profiles: a time series, with minute temporal detail, representing the power requested to the grid from the car, to recharge the battery. 

## Input files

### User-defined inputs

28 input files are automatically provided in the “Input_files/Europe” folder, one for each of the included countries. 

```python
'''Common values used in the input data definition'''

#Define Country
country = 'AT'

#Total number of users to be simulated
tot_users = 2500
```

Each input file requires, first, the definition of the country and the total number of simulated users (*tot_users*).

```python
#Variabilities 
r_w = {}

P_var = 0.1 #random in power
r_d   = 0.3 #random in distance
r_v   = 0.3 #random in velocity

#Variabilites in functioning windows 
r_w['working'] = 0.25
r_w['student'] = 0.25
r_w['inactive'] = 0.2
r_w['free time'] = 0.2

#Occasional use 
occasional_use = {}

occasional_use['weekday'] = 1
occasional_use['saturday'] = 0.6
occasional_use['sunday'] = 0.5
occasional_use['free time'] = {'weekday': 0.15, 'weekend': 0.3} #1/7, meaning taking car for free time once a week
```

Hence, a number of default stochastic parameters can be modified, namely:
- *P_var*: percentage random variability applied to the power consumption of the EV during the travel.
- *r_d*: percentage random variability applied to each travel average distance.
- *r_v*: percentage random variability applied to each travel average velocity.
- *r_w*: functioning windows random variability parameter, that shifts their starting and ending time around the user-defined average value.
- *occasional_use*: determines the probability that the appliance will be used in the simulated day; so, if equal to 1, there will be at least one switch-on event per day.

If precise information around these parameters are not available, it is advised to keep default values.

```python
#Calibration parameters for the Velocity - Power Curve [kW]
Par_P_EV = {}

Par_P_EV['small']  = [0.26, -13, 546]
Par_P_EV['medium'] = [0.3, -14, 600]
Par_P_EV['large']  = [0.35, -15.2, 620]

#Battery capacity [kWh]
Battery_cap = {}

Battery_cap['small']  = 37
Battery_cap['medium'] = 60
Battery_cap['large']  = 100
```

Then, the calibration parameters for the velocity-power curve are defined, through the *Par_P_EV* dictionary. These are derived from a JRC study, and link the EV battery power consumption to the vehicle average velocity. Unless precise information about other relations are available, it is advised to keep default values.

The *Battery_cap* dictionary defines the size of the battery (in kWh) for the 3 different types of cars modelled in the default version.

### Data from “Input_data” folder

In the “input_data/” folder, some csv provide the additional data needed to run the model. 
- The share of different vehicles among the country population is provided by the *pop_share.csv* and *vehicle_share.csv* files. 
- The mobility data are provided by the *d_tot.csv* (total daily driven distance), *d_min.csv* (average travel distance by trip) and *t_func.csv* (average driven time by trip).
- The *windows.csv* file provides the functioning windows when the EV is switched on for each country during the day. 
- The *trips_by_time.csv* files for the weekday, Saturday and Sunday provide the distribution of the travels along the day in different countries. 
