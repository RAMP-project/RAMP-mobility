# -*- coding: utf-8 -*-
"""
Created on Thu May 14 16:32:22 2020

@author: FLomb
"""


import pandas as pd
import numpy as np
import copy

#%%

def calliope_ready_processing(plug_in_user, year):
    
    hourly_year_range = pd.date_range('%s-01-01 00:00:00' %year, '%s-12-31 23:00:00' %year, freq='H')
    minute_year_range = pd.date_range('%s-01-01 00:00:00' %year, '%s-12-31 23:59:00' %year, freq='T')
    
    user_types = list(plug_in_user.keys())
    days = int(len(plug_in_user[user_types[0]][0])/1440)
    calliope_frame = pd.DataFrame(
                        index=hourly_year_range[0:(days*24)],
                        columns=[
                            'disconnections', 
                            '1h','2h','3h','4h','5h','6h','7h','8h','9h','10h','11h','12h',
                            '13h','14h','15h','16h','17h','18h','19h','20h','21h','22h','23h'
                            ]
                        ).astype(float).fillna(0)
    
    for ut in user_types:
        
        if len(plug_in_user[ut]) > 1:
            user_arrays = plug_in_user[ut]
        else:
            user_arrays = [plug_in_user[ut]]
        
        for us in range(len(user_arrays)):
            
            try:
                plug_in_frame = pd.DataFrame(plug_in_user[ut][us], index=minute_year_range[0:(days*1440)]).resample('H').mean()
                plug_in_frame[plug_in_frame != 0] = 1
                diff_frame = plug_in_frame.diff().fillna(0)
                diff_frame.columns = ['plug_unplug']
                
                if plug_in_frame.iloc[0][0] == 0:
                    diff_frame.iloc[0] = -1
                if plug_in_frame.iloc[-1][0] == 0:
                    diff_frame.iloc[-1] = 1
                    
                calliope_frame['disconnections'] += (diff_frame[diff_frame==-1]*(-1)).fillna(0).values[:,0]
                undated_diff_frame = copy.deepcopy(diff_frame)
                undated_diff_frame.index = (range(0,len(diff_frame)))
                reconnection_lag = undated_diff_frame.query('plug_unplug == 1').index.values - undated_diff_frame.query('plug_unplug == -1').index.values     
            
            except:
                print('User class "%s" has no user' %ut)
