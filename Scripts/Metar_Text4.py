#Program Name: Metar Decoder
#Author: Kyle Roebling
#Date: 7/25/19
#Version 3.0

#Import python libaries 
from metar import Metar
import urllib.request
import csv
from datetime import datetime

#Global Variables
file = []
state = []
se_plot_data = []


#Get timestamp for observations
now = datetime.now()
timestamp = datetime(now.year,now.month,now.day,now.hour,now.minute)

#Get today's date and month and year to check to see if metar is valid for today
date_check = str(now.date())

#Function that writes the formatted metar text data 
def metar_text(stateName,text_data):
    #Create file to write out text data
    file = open(f"H:\\MetarPython\\Metar_Text_Output\\{stateName}_Observations.txt","w")
    #Script Progress to User
    print(f'Writing {stateName} Data to file...')
    
    #Write out line to text files
    for lines in text_data:
        file.write(lines)
    
    #Close Text File        
    file.close()
    
#Function that writes the plot metar data for each state
def state_metar_plot(stateName,plot_data):
    #Create file to write out text data
    file = open(f"H:\\MetarPython\\Metar_Text_Output\\{stateName}_plot.txt","w")
    
    #Write out line to text files
    for lines in plot_data:
        file.write(lines)
    
    #Close Text File        
    file.close()
    
#Function that writes the plot metar data for all of the Southeast
def se_metar_plot(plot_data):
    #Create file to write out text data
    file = open(f"H:\\MetarPython\\Metar_Text_Output\\SE_plot.txt","w")
    
    #Write out line to text files
    for lines in plot_data:
        file.write(lines)
    
    #Close Text File        
    file.close()


#Function converts wind degrees into cardinal direction
def wind_deg_cardinal(deg):
    if deg == 'VRB':
        return 'VRB'
    else:
        deg = int(deg)
        arr = ['NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW', 'N']
        return arr[int(abs((deg - 11.25) % 360)/ 22.5)]

#Function converts knots to mph
def knots_mph(kts):
    mph = int(kts * 1.15)
    return mph

#Function that takes in cloud conditions and converts into a cloud fraction code
def cloud_cover(sky):
    if 'clear' in sky:
        return 0
    elif 'few' in sky :
        return 2
    elif 'scattered' in sky:
        return 4
    elif 'broken' in sky:
        return 7
    elif 'overcast' in sky:
        return 8
    else:
        return 10
    
#Funcion that find weather condtions 
def current_weather(current):
    if 'thunderstorm' in current:
        return 'TS'
    elif 'light rain' in current:
        return '-RA'
    elif 'heavy rain' in current:
        return '+RA'
    elif 'rain' in current:
        return 'RA'
    else:
        return ''

#Opens and reads StateFiles.txt to get files 
textfile = open('H:/MetarPython/Config/StateFiles.txt','r')
for line in textfile:
    file.append(line.strip()) 
textfile.close()
line = ''
textfile = ''

#Opens and reads StateNames.txt to get names
textfile = open('H:/MetarPython/Config/StateNames.txt','r')
for line in textfile:
    line.rstrip()
    state.append(line.strip())
textfile.close()
line = ''
textfile = ''

#Loop through the station file for each state
for (stateFile,stateName) in zip(file,state):
    
    #Create Lists to store metar station information
    station_id = []
    city = []
    lat = []
    long = []
    text_data = []
    state_plot_data = []

    
    #Opens and reads the MetarStation text file that contains the metar locations
    with open (stateFile,'r') as csvfile:
        readCSV = csv.reader(csvfile, delimiter = ',')
        for row in readCSV:
            station_id.append(row[0])
            city.append(row[1])
            lat.append(float(row[2]))
            long.append(float(row[3]))
        

    #Create header for text observation files
    text_data.append((f'{stateName} Current Weather Observations\n'))
    text_data.append((f'{timestamp}\n'))
    text_data.append((f'================================================================================================================\n'))       
    text_data.append((f'City                   Temp     Dewpt    Dir  MPH  Gusts  VIS    SLP      Precip  Conditions\n'))
    text_data.append((f'================================================================================================================\n'))

    #Create header for plot data files
    state_plot_data.append((f'id,lat,lon,slp,temp,cloud,dew_point,weather,wind_dir,wind_speed\n'))

    #Uses station id to download metar data from the url site
    for station,city,latitude,longitude in zip(station_id,city,lat,long):
        url = 'http://tgftp.nws.noaa.gov/data/observations/metar/stations/' + station + '.TXT'
        #Catch a bad url reading from NWS Server
        try:
            with urllib.request.urlopen(url) as response:
                data = response.readlines()
                data = data[1] #Reads second line of file
                data = data.decode('ASCII') #Converts the metar string from bytes to a string

                #Use a try except to catch bad metar data that can not be read
                try:
                    obs = Metar.Metar(data)
        
        
                    #Set weather data varibles
                    if obs.temp:
                        temp = str(obs.temp.string('F'))
                        temp_plot = float(temp[:-2])
                    else:
                        temp_plot = -99999
            
                    if obs.dewpt:
                        dewpt =  str(obs.dewpt.string('F'))
                        dewpt_plot = float(dewpt[:-2])
                    else:
                        dewpt_plot = -99999 
            
                    if obs.wind_dir:
                        wind_deg = str(obs.wind_dir)
                        wind_deg = int(wind_deg[:-8])
                        cardinal = wind_deg_cardinal(wind_deg)
                    else:
                        wind_deg = -99999
                        cardinal = "VRB"
            
                    if obs.wind_speed:
                        knots = str(obs.wind_speed)
                        knots = int(knots[:-6])
                        mph = knots_mph(knots)
                        mph_plot = knots_mph(knots)
                    else:
                        mph = 'UNK'
                        mph_plot = -99999
                
                    if obs.wind_gust:
                        knots = str(obs.wind_gust)
                        knots = int(knots[:-6])
                        gusts = knots_mph(knots)
                    else:
                        gusts = '  '
            
                    if obs.precip_1hr:
                       precip = str(obs.precip_1hr)
                    else:
                        precip = '  '
                
                    if obs.sky:
                        sky = str(obs.sky)
                        sky = sky[3:6]
                        sky_plot = str(obs.sky_conditions())
                        sky_plot = cloud_cover(sky_plot)
                    else:
                        sky = ' '
                    
                    
                    if obs.vis:
                        vis = str(obs.vis)
                        vis = vis[:-6]
                    else:
                        vis = ' '
        
                    if obs.press_sea_level:
                        slp = str(obs.press_sea_level)
                        slp = slp[:-3]
                        slp_plot = float(slp)
                    else:
                        slp = ' '
                        slp_plot = -99999
            
                    if obs.present_weather:
                       current = str(obs.present_weather())
                       current_plot = current_weather(current)
                 
                    #Get the date and month and year for metar for valid metar time
                    if obs.time:
                        metar_date_check = str(obs.time.date())
                    
            
            
                   #Check to see if metar has valid date for today
                    if  date_check == metar_date_check:
                        #Add formatted metar data for text file
                        text_data.append((f'{city:26}{temp:9}{dewpt:9}{cardinal:5}{mph:3}  {gusts:2}     {vis:5}  {slp:6}   {precip:6}  {sky:3}  {current:10}\n'))
                        state_plot_data.append((f'{station},{latitude},{longitude},{slp_plot},{temp_plot},{sky_plot},{dewpt_plot},{current_plot},{wind_deg},{mph_plot}\n'))
                        se_plot_data.append((f'{station},{latitude},{longitude},{slp_plot},{temp_plot},{sky_plot},{dewpt_plot},{current_plot},{wind_deg},{mph_plot}\n'))
                    else:
                        continue
            
                #If there is a bad metar input print our message to screen and continue script
                except:
                    continue
        #If there is a bad url read continue script without crashing
        except:
            continue
    #Call metar_text to write out formatted metar text       
    metar_text(stateName,text_data)
    #Call state_plot_text to write out plot formatted text
    state_metar_plot(stateName,state_plot_data)
#Call   
se_metar_plot(se_plot_data)
        

   
        
         