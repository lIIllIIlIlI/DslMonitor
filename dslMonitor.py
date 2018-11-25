import time
import speedtest
import plotly
import argparse

import plotly.plotly as py
import plotly.graph_objs as go
import plotly.figure_factory as FF
import numpy as np
import pandas as pd
from datetime import datetime

parser = argparse.ArgumentParser(description='Monitor Dsl uplaod- and downloadspeed as well as ping.')
parser.add_argument('--period',type=int, help='Pass the measurement period', action="store", default = False) 
argv = parser.parse_args()
try:
    if(argv.period):
        MEASUREPERIOD_SECONDS = argv.period
except NameError:
    MEASUREPERIOD_SECONDS = 60
    
FULLDAY_SECONDS = 86400 

def logMeasurement(bandwidthDown, bandwidthUp, Ping):
    """
    Writes measurement to cvs file
    """
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if((bandwidthDown > 100) and (bandwidthUp > 15) and (Ping < 25)):
        with open('logfile.csv', 'a') as logfile:
            logfile.write('{},    {:.0f},                {:.0f},               {:3.2f}\n'.format(date, bandwidthDown, bandwidthUp, Ping))
    else:
        with open('errorfile.csv', 'a') as errorfile:        
            errorfile.write('{},    {:.0f},                {:.0f},               {:3.2f}\n'.format(date, bandwidthDown, bandwidthUp, Ping))
        with open('logfile.csv', 'a') as logfile:
            logfile.write('{},    {:.0f},                {:.0f},               {:3.2f}\n'.format(date, bandwidthDown, bandwidthUp, Ping))

def triggerMeasurement():
    """
    Pings Servers to retreive Download/Uploadbandwidth and ping, returns those values
    """
    s = speedtest.Speedtest()
    s.get_servers()
    s.get_best_server()
    s.download()
    s.upload()
    res = s.results.dict()
    return res["download"], res["upload"], res["ping"]

def printMeasurement():
    """
    Prints all gathered data stored in cvs file
    """
    # Import data from cvs
    df = pd.read_csv('test.csv')
    logfileTable = FF.create_table(df.head())
    # py.iplot(sample_data_table, filename='sample-data-table')
    py.iplot(logfileTable, filename='logfileTable')

    # Store data in differen elements
    trace1 = go.Scatter(
                        time=df['AAPL_x'], downloadBandwidth=df['AAPL_y'], # Data
                        mode='lines', name='downloadBandwidth' # Additional options
                        )
   # trace2 = go.Scatter(x=df['Time'], y=df['uploadBandwidth'], mode='lines', name='uploadBandwidth' )
   # trace3 = go.Scatter(x=df['Time'], y=df['Ping'], mode='lines', name='Ping')

    layout = go.Layout(title='Simple Plot from csv data',
                   plot_bgcolor='rgb(230, 230,230)')

    # actual printing
    fig = go.Figure(data=[trace1], layout=layout)
    py.iplot(fig, filename='V-DSL Stats')
    
def BittoMbitConverter(bandwidthDown, bandwidthUp, Ping):
    """
    Converts Bit Input to MBit
    """
    bandwidthDown = bandwidthDown / (1024 * 1024)
    bandwidthUp = bandwidthUp / (1024 * 1024)
    return bandwidthDown, bandwidthUp, Ping
    
def driver():
    """
    Manages measurement, logging and output
    """
    print(MEASUREPERIOD_SECONDS)
    start = time.time()
    while True:
        time.sleep(MEASUREPERIOD_SECONDS)
        bandwidthDown, bandwidthUp, Ping = triggerMeasurement()
        bandwidthDown, bandwidthUp, Ping = BittoMbitConverter(bandwidthDown, bandwidthUp, Ping)
        logMeasurement(bandwidthDown, bandwidthUp, Ping)
        # Print once each day
        if((time.time() - start) > 60):
            printMeasurement()
         
with open('logfile.csv', 'w') as logfile:
    logfile.write('Time,                   Download (MBit),    Upload (MBit),    Ping (ms)   \n')
with open('errorfile.csv', 'w') as errorfile:
    errorfile.write('Time,                   Download (MBit),    Upload (MBit),    Ping (ms)   \n')
# Start execution
driver()
