import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import descartes
import geopandas as gpd
from shapely.geometry import Point, Polygon
import urllib.request
from sklearn.cluster import KMeans
import seaborn as sns; sns.set()
import warnings

#--------------------------------

#generación de dataframes con puntos geograficos, acotados según una ventana máxima de 

def geographic_data(data_XPV_meta ):
    '''
    geographic_data(data_XPV_meta )
    
    Returns a geographic dataframe corresponding with the points of the locations on the metadata.
    '''
    #Creación de puntos geográficos a partir del dataframe.
    geometry_XPV = [Point(xy) for xy in zip(data_XPV_meta.Longitude.values.astype('float64'),data_XPV_meta.Latitude.values.astype('float64'))]
    geo_data_XPV = gpd.GeoDataFrame(data_XPV_meta, crs = 'crs', geometry = geometry_XPV)
    return geo_data_XPV
    
#--------------------------------

#visualización de las plantas

def plants_visualization(geo_data_XPV, map_precision = 'states', BBox = (-125.00, -66.00, 24.20, 49.50), tech = 'UPV'):
    '''
    plants_visualisation(geo_data_XPV, map_precision = 'states', BBox = (-125.00, -66.00, 24.20, 49.50), tech = 'UPV')
    
    Creates a plot within the bounding box BBox which has coordinates.
    '''
    #Lectura de archivo shape para generación del mapa.
    if map_precision == 'nation':
        usa_map = gpd.read_file('./files/usa_shapes/usa_shape_nation/cb_2018_us_nation_5m.shp')
    if map_precision == 'states':
        usa_map = gpd.read_file('./files/usa_shapes/usa_shape_states/cb_2018_us_state_500k.shp')
    if map_precision == 'countys':
        usa_map = gpd.read_file('./files/usa_shapes/usa_shape_countys/cb_2018_us_county_500k.shp')
        
    if tech == 'UPV':
        colmap = 'YlOrBr'
    elif tech == 'DPV':
        colmap = 'Blues'
    
    fig,ax = plt.subplots(figsize = (40,15))
    usa_map.plot(ax = ax, alpha = 1, color='black')
    ax.set_title('Plant distribution on the USA')
    ax.set_xlim(BBox[0],BBox[1])
    ax.set_ylim(BBox[2],BBox[3])
    power = geo_data_XPV['Power (MW)'].astype('float64')
    geo_data_XPV.plot(ax = ax, markersize = 25, column = power, c = power, cmap= colmap ,marker='o', label = tech, alpha = 0.7 ,legend=True)
    plt.legend()
    plt.show()
    

    
#--------------------------------

def plant_cluster_plotting(geo_data_XPV, centers_df, map_precision = 'states', BBox = (-125.00, -66.00, 24.20, 49.50), tech = 'UPV', coords = None):
    '''
    plant_cluster_plotting(geo_data_XPV, centers_df, map_precision = 'states', BBox = (-125.00, -66.00, 24.20, 49.50), tech = 'UPV', coords = None)
    
    Plots the different resulting clusters from the segmentation process.
    '''
    
    #Lectura de archivo shape para generación del mapa.
    if map_precision == 'nation':
        usa_map = gpd.read_file('./files/usa_shapes/usa_shape_nation/cb_2018_us_nation_5m.shp')
    if map_precision == 'states':
        usa_map = gpd.read_file('./files/usa_shapes/usa_shape_states/cb_2018_us_state_500k.shp')
    if map_precision == 'nation':
        usa_map = gpd.read_file('./files/usa_shapes/usa_shape_countys/cb_2018_us_county_500k.shp')
        
    if tech == 'UPV':
        colmap = 'YlOrBr'
    elif tech == 'DPV':
        colmap = 'Blues'
        
    fig,ax = plt.subplots(figsize = (40,15))
    usa_map.plot(ax = ax, alpha = 1, color='gray')
    ax.set_title('Plant clusters on USA')
    ax.set_xlim(BBox[0],BBox[1])
    ax.set_ylim(BBox[2],BBox[3])
    power = geo_data_XPV['Power (MW)'].astype('float64')
    cluster = geo_data_XPV['cluster_label_kmeans'].astype('float64')
    geo_data_XPV.plot(ax = ax, markersize = 25, column = cluster, c = cluster, cmap= colmap ,marker='o', label = tech + ' groups', alpha = 0.75 )
    plt.scatter(centers_df.center_long, centers_df.center_lat, c='black', s=200, alpha=0.5)
    if coords is not None:
        coords = np.array(coords)
        coords = coords.reshape((1,2))
        coords_df = pd.DataFrame( data = coords, columns = ['long', 'lat'])
        plt.scatter(coords_df.long, coords_df.lat, c='lightgreen', s=175, alpha=0.7)
    plt.legend()
    plt.show()
    