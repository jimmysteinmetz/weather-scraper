# -*- coding: utf-8 -*-
"""
Created on Wed Feb 25 09:57:27 2015

@author: JimmySteinmetz


"""

import pandas as pd
import numpy as np
import datetime
import requests
from bs4 import BeautifulSoup as bs
from bs4 import SoupStrainer as st
from time import time

start_time = time()

'''pulls weather data for dates. dates must be passed as timestamp'''
'''times are available by half hour'''
'''should edit to make datetime types able to be passed as well'''

def get_weather(date_timestamp):
    '''construct url'''
    head = 'http://www.weatheronline.co.uk/weather/maps/current?LANG=en&DATE='
    tail = '&CONT=namk&LAND=namk&KEY=namk&SORT=1&UD=9458034&INT=06&TYP=wetter&ART=tabelle&RUBRIK=akt&R=310&CEL=F&SI=mph'    
    url = head + str(date_timestamp) + tail
    
    '''pull data table'''
    f = requests.get(url)
    soup_strainer = st('table')
    soup = bs(f.text, parse_only=soup_strainer)    
    
    '''initialize datasets'''    
    stations = []
    temps = []
    cond = []
    locations = []
    states = []
    
    '''pull data'''
    '''first area for improvement'''
    count = 0
    for v in soup.find_all('td'):
        count += 1
        if ((count - 1) % 3) == 0:
            stations.append(v.get_text())
        if ((count - 2) % 3) == 0:
            temps.append(v.get_text())
        if (count % 3) == 0:
            cond.append(v.get_text())
    
    '''clean up station locations'''    
    for loc in stations:
        stop = loc.find("(")
        location = loc[:stop-1].lower()
        locations.append(location)
        start = loc.find(",", stop)
        states.append(loc[start + 1:-1])
    
    '''organize data into dataframe'''
    df = pd.DataFrame(np.vstack((stations,temps,cond, locations, states)).T)
    df.columns = ['stations', 'temps', 'weather', 'locations', 'states']
    
    '''append date as additional column'''    
    date = datetime.datetime.fromtimestamp(date_timestamp).strftime('%Y-%m-%d')
    df['date'] = date
    
    '''remove table headers'''    
    '''this could probably be tied in with the cleaned up data pull'''
    df = df.iloc[1::]
    
    '''convert temp to numeric'''
    df['temp_num'] = df['temps'].apply(lambda x: float(x[:(x.find(" °F"))-2]))
    
    '''write dataframe file to folder \data files'''
    filename = 'data files\\' + str(date) + '.csv'    
    df.to_csv(filename)

print 'run complete in %s seconds' % str(time() - start_time)
