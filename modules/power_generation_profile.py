from modules import plant_scaling
from modules import geographical_analysis
from modules import geographical_plotting

#-----------------------------------------

def cluster_label_gdf(metadata_XPV, N_clusters = 75 ):
    '''
    cluster_label_gdf(metadata_XPV, N_clusters = 75 )
    
    This function takes all the plants metadata, segment it according to the inputed N_clusters and 
    returns a labeled dataframe with the cluster categories.
    '''
    geo_metadata_XPV_df = geographical_plotting.geographic_data(metadata_XPV)
    geo_data_XPV_labeled_df, centers_df = geographical_analysis.geographical_plant_clustering(geo_metadata_XPV_df, N_clusters)
    return geo_data_XPV_labeled_df, centers_df

#-----------------------------------------

def Get_PGP_TS( geo_data_XPV_labeled_df, centers_df, coordinates = (-125, 35), power = 10, datapath = './data/Extracted/', degree = 3, data = 'max', out_csv = False):
    '''
    Get_PGP_TS( geo_data_XPV_labeled_df, centers_df, coordinates = (-125, 35), power = 10, datapath = './data/Extracted/', degree = 3, data = 'max', write_csv = False)
    
    This function generates a time series which correponds to a reescalement of a existing plant power generation
    time series that is in a nearby cluster group.
    
    To get a clearer idea on choosing the most convenient parameters, please explore notebooks 1 and 2 to get a 
    visualisation of the dataset and an idea of how the reescaling is done.
    '''    
    index, center_long, center_lat = geographical_analysis.closest_centroid( geo_data_XPV_labeled_df, centers_df, coords = coordinates )
    
    cluster_group_metadata_df = geographical_analysis.cluster_group(index, geo_data_XPV_labeled_df)
    
    selected_plant_set_obj = plant_scaling.Plant_set(datapath, cluster_group_metadata_df, coords = coordinates)
    
    selected_plant_set_obj.points = selected_plant_set_obj.read_data(geo_data_XPV_labeled = selected_plant_set_obj.plants_metadata, set_points = True)
    
    scaled_time_serie = selected_plant_set_obj.scale_signal(degree, data, MW_out = power, write_csv = out_csv, plot_hist = False)
    
    return scaled_time_serie