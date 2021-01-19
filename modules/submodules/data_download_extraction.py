import pandas as pd
import numpy as np
from zipfile import ZipFile
import urllib.request
from tqdm import tqdm
import os

#---------------------------------------------------------------------------------------------------
#class needed for progressbar on downloads
class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def download_url(url, output_path):
    with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=url.split('/')[-1]) as t:
        urllib.request.urlretrieve(url, filename=output_path, reporthook=t.update_to)
        
#---------------------------------------------------------------------------------------------------

def download_data(links_file_path, outpath):
    '''
    links_file_path: path and name of the file wich contains the entities and links for download.
    '''

    if not os.path.exists(outpath + 'data/'):
        os.mkdir(outpath + 'data/')
    state_links = pd.read_csv(links_file_path) 
    
    for state, url in state_links.values:
        if not os.path.exists(outpath + 'data/' + state + '.zip'):
            print('\n Downloading data for ', state)
            download_url(url, outpath + 'data/' + state + '.zip')
        else:
            print('Files from {} already exists.'.format(state))
            
def unzip_data(datapath):
    '''
    datapath: folder in which files are contained.
    '''
    files = [f for f in os.listdir(datapath) if os.path.isfile(os.path.join(datapath, f))]

    for file in files:
        with ZipFile(datapath+'/'+file, 'r') as zip_ref:
            for member in tqdm(zip_ref.infolist(), desc='Extracting {}'.format(file)):
                try:
                    zip_ref.extract(member, datapath + '/Extracted/')
                except zipfile.error as e:
                    pass
                                    
def info_df_from_data(datapath, tech='UPV'):
    '''
    datapath: folder in which files are contained.
    tech: technology of the simulated plant.
    '''
    files = [f for f in os.listdir(datapath) if os.path.isfile(os.path.join(datapath, f))]
    info_array = []

    for file in files:
        if (file.find('Actual') != -1) and (file.find(tech) != -1):
            aux = file.split('_',maxsplit=6)
            aux[5] = aux[5].replace('MW','')
            aux_ = np.append(np.array([aux[1],aux[2],aux[5],aux[4]]), np.array([file]), axis=0)
            info_array.append(aux_)
    
    df = pd.DataFrame(info_array, columns=['Latitude','Longitude','Power (MW)','Technology','File_name'])
    return df
                                    
               
