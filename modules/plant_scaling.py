from __future__ import print_function
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from scipy.optimize import curve_fit
import random
import pandasql as ps
import time
# --------------------------------------------------------

#class which contains the analysis of the plant-set data

class Plant_set():

    def __init__(self, datapath, geo_metadata_XPV_labeled, coords = (00.00, 00.00)):
        self.datapath = datapath
        self.plants_metadata = geo_metadata_XPV_labeled
        self.coords = coords
        #self.points = self.read_data(geo_data_XPV_labeled = self.plants_metadata)
        
    def read_data(self, geo_data_XPV_labeled = None, path = None, set_points = False):
        '''
        read_data(self, geo_data_XPV_labeled = None, path = None, set_points = False):

        Se leen los metadatos de algún grupo de plantas contenidos en el dataframe o csv indicado en
        geo_data_XPV_labeled o en path según sea el caso. Después se extrae la información de los 
        perfiles de generación, así como de la potencia de las respectivas plantas. 
        Se extraen los valores de generación de la planta al medio día y se devuelve en el array llamado 'points'.
        '''
        t0 = time.time()
        if path is not None:
            plants_metadata_df = pd.read_csv(path)
        else:
            plants_metadata_df = geo_data_XPV_labeled

        files = plants_metadata_df['File_name']
        power_plants_MW = plants_metadata_df['Power (MW)'].astype('float64')

        self.power_plants_MW = power_plants_MW
        points = []
        i = 0
        len_ = len(files)
        
        for file, MW in zip(files, power_plants_MW):
            plant = pd.read_csv('./data/Extracted/' + file, header=0, index_col=0)
            midday_data = MW*np.ones((365,2))
            q1 = ps.sqldf("select * from plant where LocalTime LIKE '%12:00%'")
            q1.columns = ['LocalTime', 'midday_power']
            midday_data[:,1] = q1['midday_power']
            points.append(midday_data)
            i = i + 1
            if i % 3 == 0:
                print('|{:.2f}% completed. Time elapsed: {:.1f}s '.format(i*100/len_, time.time() - t0), end="\r")
        print('|{:.2f}% completed. Time elapsed: {:.1f}s '.format(i*100/len_, time.time() - t0), end="\r")

        points = np.array(points) 

        if set_points:
            self.points = points

        return points 
    
    def midday_distributions(self, create_csv = False, plot = False, fit = False):
        '''
        midday_distributions(create_csv = False, plot = False)
        
        Regresa data frame con potencias de planta y valor diario al medio día durante el año.
        '''
        points_plot = self.points[0]
        for i in self.points[1:]:
            points_plot = np.concatenate((points_plot,i),axis=0)  
        df = pd.DataFrame(columns = ['MW','Power_Midday'], data = points_plot)
        if create_csv:
            df.to_csv(path_or_buf = 'potencia_mediodia.csv', index=False) 
        if plot:
            x = df.MW.values
            y = df.Power_Midday.values
            df.plot.scatter(x = 'MW', y = 'Power_Midday', xlim = [0,x.max()+10], ylim = [0,y.max()+10], s=0.005, c='blue')
        return df
    
    def yearly_max_value(self, create_csv = False, plot = False, fit = False):
        '''
        yearly_max_value(create_csv = False, plot = False, fit = False)
        
        Regresa dataframe con potencias de planta y valor máximo anual al medio día.
        '''
        data = []
        for i in self.points:
            data.append(np.array([np.max(i[:,0]), np.max(i[:,1])]))
        data = np.array(data)

        df = pd.DataFrame(columns = ['MW','Max_Power_Midday'], data = data)
        if create_csv:
            df.to_csv(path_or_buf = 'potencia_mediodia_max.csv', index=False)
        if plot:
            x = df.MW.values
            y = df.Max_Power_Midday.values
            df.plot.scatter(x = 'MW', y = 'Max_Power_Midday', xlim = [0,x.max()+10], ylim = [0,y.max()+10], s=7, c='blue')
            
        if fit:
            df = pd.DataFrame(columns = ['MW','Power_Midday'], data = data)
        return df
    
    def yearly_mean_value(self, create_csv = False, plot = False, fit = False):
        '''
        yearly_mean_value(create_csv = False, plot = False, fit = False)
        
        Regresa dataframe con potencias de planta y valor máximo anual al medio día.
        '''
        data = []
        for i in self.points:
            data.append(np.array([np.mean(i[:,0]), np.mean(i[:,1])]))
        data = np.array(data)

        df = pd.DataFrame(columns = ['MW','Mean_Power_Midday'], data = data)
        if create_csv:
            df.to_csv(path_or_buf = 'potencia_mediodia_mean.csv', index=False)
        if plot:
            x = df.MW.values
            y = df.Mean_Power_Midday.values
            df.plot.scatter(x = 'MW', y = 'Mean_Power_Midday', xlim = [0,x.max()+10], ylim = [0,y.max()+10], s=7, c='blue')
        if fit:
            df = pd.DataFrame(columns = ['MW','Power_Midday'], data = data)
        return df

    def fit_curve(self, degree = 2, data = 'max', plot = False, scale_factor = None):
        '''
        fit_curve(degree = 2, data = 'max', plot = False, scale_factor = None)
        
        Ajusta una curva de grado especificado tomando como conjunto de ajuste
        los datos que se indiquen. Se forza que el ajuste considere un desfase de 0.

        Inputs:

        points: arreglo de puntos a considerar.
        degree: grado de la curva a ajustar (default: 2). {1,2,3}
        data  : 'max', 'mean', 'all'.
                'max': ajusta la curva a los máximos anuales de la distribución.
                'mean': ajusta la curva al valor promedio anual.
                'all': ajusta la curva a la distribución de datos completa. 
        scale_factor: Si se especifica, se devuelve el valor que devuelve la curva ajustada
                      para ese valor.

        Output:

        y_factor: El valor que devuelvela función ajustada para x=scale_factor.
        params: Contiene los coeficientes del polinomio ajustado. No contiene el offset, pues de 
                considera como cero.

        '''

        def linear(x, a):
            return a*x
        def second(x, a, b):
            return a*x**2 + b*x**1
        def third(x, a, b, c):
            return a*x**3 + b*x**2 + c*x**1

        if data == 'all':
            df = self.midday_distributions()
            ms = 0.15
        elif data == 'max':
            df = self.yearly_max_value(fit = True)
            ms = 5
        elif data == 'mean':
            df = self.yearly_mean_value(fit = True)
            ms = 5
        else:
            return print('Invalid selectionf for "data". Must be in ("all", "max", "mean")')

        #grado
        j = degree
        #datos
        x = df.MW.values
        y = df.Power_Midday.values

        # Curve fitting. returns parameters.
        if degree == 1:
            params = curve_fit(linear, x, y)
            [a] = params[0]
            if scale_factor is not None:
                y_factor = linear(scale_factor,a)
        elif degree == 2:
            params = curve_fit(second, x, y)
            [a,b] = params[0]
            if scale_factor is not None:
                y_factor = second(scale_factor, a, b)
        elif degree == 3:
            params = curve_fit(third, x, y)
            [a,b,c] = params[0]
            if scale_factor is not None:
                y_factor = third(scale_factor, a, b, c)
        else:
            return print('Error: Degree not supported. Must be 1, 2 or 3.')

        if plot:
            x_fit = np.linspace(0, x.max() + 10, 100)
            if degree == 1:
                y_fit = a*x_fit
            elif degree == 2:
                y_fit =  a * x_fit**2 + b*x_fit
            elif degree == 3:
                y_fit = a * x_fit**3 + b * x_fit**2 + c*x_fit
                
            plt.ylim(0, y.max() + 10)
            plt.xlim(0, x.max() + 10)
            plt.plot(x, y, '.', ms=ms)         # Data
            plt.plot(x_fit, y_fit, 'orange')  # Fitted curve

        if scale_factor is not None:
            return y_factor
        else:
            return params[0]
        
    def scale_signal(self, degree, data, MW_out, write_csv = True, plot_hist = False):
        '''
        scale_signal(degree, data, MW_out, write_csv = True, plot_hist = False)
        
        Devuelve un arreglo de valores de generación equivalente a una planta de MW_out
        watts pico instalados. 
        '''

        y_factor = self.fit_curve(degree = degree , data = data, plot = False, scale_factor = MW_out)
        #print(y_factor)

        MW = random.choice(self.power_plants_MW)
        file_metadata = self.plants_metadata.loc[self.plants_metadata['Power (MW)'] == MW]
        file_metadata = file_metadata.reset_index(drop=True)
        index = random.randint(0, file_metadata.shape[0] - 1)

        plant = pd.read_csv( self.datapath + file_metadata['File_name'][index], header=0, index_col=0, parse_dates=True, squeeze=True)

        midday_data = MW*np.ones((364,2))
        for j in range(364):
            i=2*j+1
            midday_data[j][1] = plant[i*int(288/2):i*int(288/2) + 1]
        points = midday_data 

        if data == 'mean' or data == 'all':
            N = np.mean(points[:,1])
        elif data == 'max':
            N = np.max(points[:,1])

        df = y_factor*plant/N

        midday_data = MW_out*np.ones((364,2))
        for j in range(364):
            i=2*j+1
            midday_data[j][1] = df[i*int(288/2):i*int(288/2) + 1]
        scalated_points = midday_data 

        if write_csv:
            if not os.path.exists('./reescaled_series/'):
                os.makedirs('./reescaled_series/')
            df.to_csv(path_or_buf = './reescaled_series/Scaled_{0}_{1}_{2}_{3}_2006_{4}_{5}MW_5_Min_{6}deg_{7}_{8}MW.csv'.format(file_metadata['Latitude'][index], file_metadata['Longitude'][index],self.coords[1], self.coords[0], file_metadata['Technology'][index], int(file_metadata['Power (MW)'][index]), degree, data, int(MW_out)), index=False)

        if plot_hist:

            pre_plant = pd.DataFrame(columns = ['MW','Power_Midday'], data = points)
            #pre_plant.to_csv(path_or_buf = 'pre_plant.csv', index=False)

            scl_plant = pd.DataFrame(columns = ['MW','Power_Midday'], data = scalated_points)
            #scl_plant.to_csv(path_or_buf = 'scl_plant.csv', index=False)

            plt.figure(figsize=(20,8)) 

            ax1 = plt.subplot(2,4,1)
            ax2 = plt.subplot(2,4,2)

            ax2.hist(pre_plant.Power_Midday, bins=50, label = 'Parent plant', color='orange',edgecolor='purple', alpha=0.5)
            ax2.set_xlabel('{}MW'.format(int(MW)), size=15)

            ax1.hist(scl_plant.Power_Midday, bins=50, label = 'Scalated plant', color='green',edgecolor='purple', alpha=0.5)
            ax1.set_xlabel('{}MW'.format(MW_out), size=15)
            ax1.set_ylabel('Frequency', size=15)

        return df