from modules.submodules import data_download_extraction
import pandas as pd
import zipfile
import urllib.request
import os

# --------------------------------------------------------

#Descarga y extracción de archivos csv.

def data_download( Eastern = True, Western = True, Unzip = True):
    '''data_download( Eastern = True, Western = True, Unzip = True)
    
        This function downloads the 2006 simulated plants time series for fotovoltaic power generation. 
        It uses data provided by NREL. Downloads the files into a folder called 'data' where the extracted 
        files are also stored, if selected.
    '''
    if Eastern:
        print('Downloading eastern states data:')
        data_download_extraction.download_data('./links/eastern_states_links.csv', './')
        print('Download finished.')
    if Western:
        print('Downloading western states data:')
        data_download_extraction.download_data('./links/western_states_links.csv', './')
        print('Download finished.')
    if Unzip:
        print('Exracting data files:')
        data_download_extraction.unzip_data('./data/')
        print('Extraction finished.')
        
# --------------------------------------------------------

#Creación de los dataframes con los datos. Se generan archivos csv.

def get_plants_files_metadata( read = False, PATH = './data/Extracted/', UPV = True, DPV = True, to_csv = False):

    '''Function returns pandas dataframes with the metadata of the files which contain the time series.
       -UPV: solar plants with tracking technology.
       -DPV: solar plants without tracking technology.
    '''
    if read:
        #Si los archivos con datos geograficos ya están construidos solo se leen
        if UPV and DPV:
            data_UPV = pd.read_csv('./files/metadata_UPV.csv')
            data_DPV = pd.read_csv('./files/metadata_DPV.csv')
            return data_UPV, data_DPV
        if UPV and not DPV: 
            data_UPV = pd.read_csv('./files/metadata_UPV.csv')
            return data_UPV
        if DPV and not UPV: 
            data_DPV = pd.read_csv('./files/metadata_DPV.csv')
            return data_DPV
    else:
        if UPV and DPV:
            data_UPV = data_download_extraction.info_df_from_data( PATH , tech = 'UPV')
            data_DPV = data_download_extraction.info_df_from_data( PATH , tech = 'DPV')
            if to_csv: 
                data_UPV.to_csv('./files/metadata_UPV.csv', index = False)
                data_DPV.to_csv('./files/metadata_DPV.csv', index = False)
            return data_UPV, data_DPV
        if UPV and not DPV: 
            data_UPV = data_download_extraction.info_df_from_data( PATH , tech = 'UPV')
            if to_csv: 
                data_UPV.to_csv('./files/metadata_UPV.csv', index = False)
            return data_UPV
        if DPV and not UPV: 
            data_DPV = data_download_extraction.info_df_from_data( PATH , tech = 'DPV')
            if to_csv: 
                data_DPV.to_csv('./files/metadata_DPV.csv', index = False)
            return data_DPV
        
# --------------------------------------------------------

#Descarga y extracción de archivos shape del mapa de EEUU.

def get_usa_shapes():
    
    url = 'https://www2.census.gov/geo/tiger/GENZ2018/shp/cb_2018_us_nation_5m.zip'
    urllib.request.urlretrieve(url, './usa_shape.zip')
    url = 'https://www2.census.gov/geo/tiger/GENZ2018/shp/cb_2018_us_state_500k.zip'
    urllib.request.urlretrieve(url, './usa_shape_division.zip')
    url = 'https://www2.census.gov/geo/tiger/GENZ2018/shp/cb_2018_us_county_500k.zip'
    urllib.request.urlretrieve(url, './usa_shape_countys.zip')

    with zipfile.ZipFile('./usa_shape.zip', 'r') as zip_ref:
        zip_ref.extractall('./files/usa_shapes/usa_shape_nation/')
    with zipfile.ZipFile('./usa_shape_division.zip', 'r') as zip_ref:
        zip_ref.extractall('./files/usa_shapes/usa_shape_states/')
    with zipfile.ZipFile('./usa_shape_countys.zip', 'r') as zip_ref:
        zip_ref.extractall('./files/usa_shapes/usa_shape_countys/')
        
    os.remove('./usa_shape.zip')
    os.remove('./usa_shape_division.zip')
    os.remove('./usa_shape_countys.zip')
    
# --------------------------------------------------------

