#Program Name: Metar Plot
#Author: Kyle Roebling
#Date: 7/16/19
#Version 1.0

#Import in python libaries that are needed
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt
import pandas as pd

from metpy.calc import wind_components
from metpy.calc import reduce_point_density
from metpy.plots import current_weather, StationPlot, wx_code_map, sky_cover
from metpy.units import units

#Global variables
state = []
plotBounds = []
plotSize = []
plotDensity = []
plotData = []
shapefile = []


#Opens and reads StateNames.txt to get names
textfile = open('H:/MetarPython/Config/StateNames.txt','r')
for line in textfile:
    line.rstrip()
    state.append(line.strip())
textfile.close()
line = ''
textfile = ''

#Opens and reads PlotData.txt to get observation file data
textfile = open('H:/MetarPython/Config/PlotData.txt','r')
for line in textfile:
    line.rstrip()
    plotData.append(line.strip())
textfile.close()
line = ''
textfile = ''

#Opens and reads PlotDensity.txt to get density values for plots
textfile = open('H:/MetarPython/Config/plotDensity.txt','r')
for line in textfile:
    line.rstrip()
    plotDensity.append(int(line.strip()))
textfile.close()
line = ''
textfile = ''


#Opens and reads shapefile.txt to get shapefiles
textfile = open('H:/MetarPython/Config/shapefile.txt','r')
for line in textfile:
    line.rstrip()
    shapefile.append(line.strip())
textfile.close()
line = ''
textfile = ''


#Opens and reads plotBounds.txt into list of tuples
with open('H:/MetarPython/Config/plotBounds.txt','r') as textfile:
    for line in textfile.readlines():
        line = line.strip()
        tmp = line.split(",")
        plotBounds.append((float(tmp[0]), float(tmp[1]), float(tmp[2]), float(tmp[3])))
textfile.close()
line = ''
textfile = ''

      
#Opens and reads plotSize.txt into list of tuples
with open('H:/MetarPython/Config/plotSize.txt','r') as textfile:
    for line in textfile.readlines():
        line = line.strip()
        tmp = line.split(",")
        plotSize.append((int(tmp[0]), int(tmp[1])))
textfile.close()
line = ''
textfile = ''


#Loop through configuation varaibles file for each state
for (stateName,bounds,size,ObData,shapefile,density) in zip(state,plotBounds,plotSize,plotData,shapefile,plotDensity):    
    #Read weather data from metardata.txt
    f = ObData
    data = pd.read_csv(f,header=0,usecols=(1,2,3,4,5,6,7,8,9),
                       names=['stid', 'lat', 'lon', 'slp', 'air_temperature', 'cloud_fraction',
                             'dew_point_temperature', 'weather', 'wind_dir', 'wind_speed'],
                      na_values=-99999)

    #Drop observations that have missing winds
    data = data.dropna(how='any', subset=['wind_dir','wind_speed'])

    #Get u,v wind components from wind speed and direction
    #Get u,v wind components from wind speed and direction
    u, v = wind_components((data['wind_speed'].values * units('mph')).to('mph'),
                       data['wind_dir'].values * units.degree)

    data['eastward_wind'], data['northward_wind'] = u, v

    #Convert weather strings into WMO codes 
    wx = [wx_code_map[s.split()[0] if ' ' in s else s] for s in data['weather'].fillna('')]

    #Set up the map projection
    proj = ccrs.LambertConformal(central_longitude=-86.3939722,central_latitude=32.300638,
                             standard_parallels=[10])

    #Transform lat and long into the projected coordinate system
    point_locs = proj.transform_points(ccrs.PlateCarree(), data['lon'].values, data['lat'].values)

    #then refine the number of stations plotted by setting a 300km radius
    data = data[reduce_point_density(point_locs,density)]

    # Change the DPI of the resulting figure. Higher DPI drastically improves the
    # look of the text rendering.
    plt.rcParams['savefig.dpi'] = 300

    # Create the figure and an axes set to the projection.
    fig = plt.figure(figsize= size)
    #add_metpy_logo(fig, 29, 20, size='small')
    ax = fig.add_subplot(1, 1, 1, projection=proj)

    # Add a title to map
    plt.title(f'{stateName} Current Observations', fontsize=20)


    #If statement to select shapefiles for Regional vs State plots
    if stateName == 'South East':
        # Add States to plot.
        reader = shpreader.Reader('H:\\MetarPython\\Shapefiles\\States.shp')
        states = list(reader.geometries())
        STATES = cfeature.ShapelyFeature(states, ccrs.PlateCarree())
        ax.add_feature(STATES, facecolor='none', edgecolor='#DADADA', linewidth= 0.5)
    else:
        # Add counties to plot.
        reader = shpreader.Reader(shapefile)
        counties = list(reader.geometries())
        COUNTIES = cfeature.ShapelyFeature(counties, ccrs.PlateCarree())
        ax.add_feature(COUNTIES, facecolor='none', edgecolor='#DADADA', linewidth= 0.5)

        # Add States to plot.
        reader = shpreader.Reader('H:\\MetarPython\\Shapefiles\\States.shp')
        states = list(reader.geometries())
        STATES = cfeature.ShapelyFeature(states, ccrs.PlateCarree())
        ax.add_feature(STATES, facecolor='none', edgecolor='#DADADA', linewidth= 0.5)

    # Set plot bounds
    ax.set_extent(bounds)


    # Start the station plot by specifying the axes to draw on, as well as the
    # lon/lat of the stations (with transform). We also the fontsize to 12 pt.
    stationplot = StationPlot(ax, data['lon'].values, data['lat'].values, clip_on=True,
                              transform=ccrs.PlateCarree(), fontsize=10)

    # Plot the temperature and dew point to the upper and lower left, respectively, of
    # the center point. Each one uses a different color.
    stationplot.plot_parameter('NW', data['air_temperature'], color='red')
    stationplot.plot_parameter('SW', data['dew_point_temperature'], color='green')

    #Plot sea level pressure
    stationplot.plot_parameter('NE', data['slp'], formatter=lambda v: format(10 * v, '.0f')[-3:])

    #Plot sky cover
    stationplot.plot_symbol('C', data['cloud_fraction'], sky_cover,color='blue')

    # Add wind barbs
    stationplot.plot_barb(data['eastward_wind'],data['northward_wind'],color='blue',zorder=2)

    #Plot current weather conditions
    stationplot.plot_symbol('W', wx, current_weather)

    #Save plot to file
    plt.savefig(f'H:\\MetarPython\\Plots\\{stateName}.pdf',bbox_inches='tight')


print('Success')

