import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import descartes
import geopandas as gpd
from shapely.geometry import Point, Polygon
from sklearn.cluster import KMeans
import seaborn as sns; sns.set()
import warnings

#-----------------------------------

#generación de dataframes con puntos geograficos, acotados según una ventana máxima de 

def geographic_data(data_XPV_meta ):
    '''
    geographic_data(data_XPV_meta )
    
    Returns a geographic dataframe corresponding with the points of the locations on the metadata.
    '''
    #Creación de puntos geográficos a partir del dataframe.
    geometry_XPV = [Point(xy) for xy in zip(data_XPV_meta.Longitude.values.astype('float64'),data_XPV_meta.Latitude.values.astype('float64'))]
    geo_data_XPV = gpd.GeoDataFrame(data_XPV_meta, crs = 'crs', geometry = geometry_DPV)
    return geo_data_XPV
    
#-----------------------------------

# creación de arreglo de coordenadas a partir del dataframe

def coordinate_points(geo_data_XPV):
    '''
    coordinate_points(geo_data_XPV)
    
    Creates 2d array with points coordinates from the given geo_dataframe.
    '''
    geo_points = geo_data_XPV.geometry.values
    points = [ np.array((geom.xy[0][0], geom.xy[1][0])) for geom in geo_points ]
    return points

# ----------------------------------

#segmentation with kmeans

def geographical_plant_clustering(geo_data_XPV, N_clusters = 50 ):
    '''
    geographical_plant_clustering(geo_data_XPV, N_clusters = 50 )
    
    Clusters from the geographical coordinates of the plants. The funtion assigns a clustering class to each one of 
    the plants on the data frame and creates another data frame with the segmented centroids. In the second data 
    frame, it appends the nearest city with its own coordinates as well.
    '''
    #clustering
    points = coordinate_points(geo_data_XPV)
    kmeans = KMeans(n_clusters = N_clusters, init ='k-means++')
    kmeans.fit(points) # Compute k-means clustering.
    geo_data_XPV['cluster_label_kmeans'] = kmeans.fit_predict(points) # Labels of each point on geo_dataframe
    centers = kmeans.cluster_centers_ # Coordinates of cluster centers.
    centers_df = pd.DataFrame(centers, columns = ['center_long','center_lat'])

    #calling cities database
    us_cities = pd.read_csv('./files/uscities.csv')
    us_cities = us_cities.filter(['city','state_id','lat','lng'], axis=1)
    us_cities = us_cities.rename(columns={"lat": "Latitude", "lng": "Longitude"})
    us_cities.head()

    #appending nearest city from segmentation centers to centers dataframe
    cities = []
    states = []
    lat = []
    lng = []
    for x1,y1 in zip(centers_df.center_long.values, centers_df.center_lat.values):
        distances = []
        for x2,y2 in zip(us_cities.Longitude.values, us_cities.Latitude.values):
            a = np.array([x1,y1])
            b = np.array([x2,y2])
            distances.append(np.linalg.norm(a-b))

        ind = distances.index(min(distances))
        cities.append(us_cities.values[ind][0])
        states.append(us_cities.values[ind][1])
        lat.append(us_cities.values[ind][2])
        lng.append(us_cities.values[ind][3])

    #adds to dataframe data from nearest city to the centroid
    centers_df['Nearest_city'] = cities
    centers_df['State_near_city'] = states
    centers_df['city_long'] = lng
    centers_df['city_lat'] = lat
    
    geo_data_XPV_labeled = geo_data_XPV
    
    return geo_data_XPV_labeled, centers_df

# ------------------------------------

def closest_centroid(geo_data_XPV_labeled, centers_df, coords = (-120,25)):
    '''
    closest_centroid(geo_data_XPV_labeled, centers_df, coords = (-120,25))
    
    Calculates the nearest_centroid from a segmentation process given a coordinate position, 
    all of them given in centers_df. Returns the index of the nearest centroid, and its coordinates.
    '''
    long = coords[0]
    latit = coords[1]
    
    distances = []
    for x1,y1 in zip(centers_df.center_long.values, centers_df.center_lat.values):

        a = np.array([coords[0], coords[1]])
        b = np.array([x1,y1])
        distances.append(np.linalg.norm(a-b))
        
    min_ = min(distances)
    max_ = max(distances)

    index_min = distances.index(min_)
    index_max = distances.index(max_)

    center_lng = centers_df['center_long'][index_min]
    center_lat = centers_df['center_lat'][index_min]
    
    lng_max = centers_df['center_long'][index_max]
    lat_max = centers_df['center_lat'][index_max]

    b = np.array([lng_max,lat_max])
    dist = np.linalg.norm(a-b)
    
    if  dist > max_:
        warnings.warn("The selected coordinates are {0} times further than the furthest plant that belongs to the calculated centroid. Climatic variations may differ in a larger propportions to the ideal ones. Take it into account. Proceding...".format(dist/max_))
    

    return index_min, center_lng, center_lat

#--------------------------------------

def cluster_group(index, geo_data_XPV_labeled):
    '''
    cluster_group(index, geo_data_XPV_labeled)
    
    Returns the metadata of only the plants on geo_data_XPV_labeled which are on the cluster group marked with index-
    '''
    
    cluster_group_meta = geo_data_XPV_labeled.loc[geo_data_XPV_labeled['cluster_label_kmeans'] == index] 
    return cluster_group_meta.reset_index(drop=True)

# ------------------------------------