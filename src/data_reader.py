import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging
import linecache
from scipy import interpolate
import os

class LUNAOBRDataReader:
    
    def __init__(self, file_dir, file_prefix, file_sufix_list):
        self.file_dir = file_dir
        self.file_prefix = file_prefix
        self.file_sufix_list = file_sufix_list
        self.df = []

    def getDataFrame(self):
        """ Get dataframe.
        Returns:
            df - dataframe      
        """   
        return self.df    

    def getColumns(self, dim=0):
        """ Get columns from dataframe.
        Args:
            dim - integer - index of list of dataframes
        Returns:
            list - columns labels      
        """        
        try:
            df = self.df[dim]
        except Exception as e:
            logging.error('Failed to obtain DataFrame: ' + str(e))
            return
        return df.columns
    
    def fileReader(self, file_path):
        """ Read file from a specific path.
        Args:
            file_path - string
        Returns:
            df - dataframe
        """
        try:
            header_cmp = linecache.getline(file_path, 11, module_globals=None)
        except:
            logging.error('Unable to read header: ' + file_path)
            return    
        
        # Check line 11 of header to identify if sensing is enabled:
        # If so, header contains two additional rows
        skip_rows = 11
        if header_cmp.find("Gage length:") != -1:
            skip_rows = skip_rows+2

        try:      
            df = pd.read_csv(file_path, sep="\t", skiprows=skip_rows, header=1, index_col=False)
        except:
            logging.error('Unable to read file from path: ' + file_path)
            return 
        
        return df
    
    def _mkDir(self,dir_name):
        if not os.path.isdir(dir_name):
            os.makedirs(dir_name)  

    def readData(self, save_figure=True, figure_dir='../figures/'):
        """ Plot dataframe.
        Args:
            df - dataframe or list of dataframes
        Returns:
            fig - figure
        """
        # Create paths
        file_name_list = ["{}_{}.txt".format(self.file_prefix, file_sufix) for file_sufix in self.file_sufix_list]
        path_list = ["".join((self.file_dir,file_name)) if (self.file_dir[-1]=='/') else "/".join((self.file_dir,file_name))
                     for file_name in file_name_list]        
        figure_path = "".join((figure_dir,self.file_prefix)) if (figure_dir[-1]=='/') else "/".join((figure_dir,self.file_prefix))

        # Read file
        self.df = [self.fileReader(path) for path in path_list]
        self.df = self._dropEmpty()
        
        if self.df and save_figure:
            self._mkDir(figure_dir)
            figure = self.plotFromDataFrame(figure_path)    
        else:
            figure = None    
           
        return figure
    
    def _dropEmpty(self):
        """ Drop empty dataframes from list.
        Args:
            df_list - dataframe or list of dataframes
        Returns:
            df_clean - dataframe or list of dataframes
        """
        df_clean = [] 
        for dataframe in self.df:
            if dataframe is not None:   
                for col_name in dataframe.columns:
                    if (col_name.find('Unnamed') != -1):
                        dataframe.drop(col_name, axis=1)
                df_clean.append(dataframe) 

        return df_clean

    def plotFromDataFrame(self,figure_path):
        """ Save plot of dataframe.
        Args:
            df - dataframe or list of dataframes
        """    
        fig, ax = plt.subplots(len(self.df),figsize=(8,7))
        
        # Check if is instance of np.ndarray
        if not isinstance(ax, np.ndarray):
            ax = [ax]

        for i in range(len(ax)):
            for k in range(1, self.df[i].shape[1]-1):
                ax[i].plot(self.df[i].iloc[:,0], self.df[i].iloc[:,k],linewidth=1, label = self.df[i].columns[k])
            ax[i].set_xlabel(self.df[i].columns[0])
            ax[i].set_ylabel(self.df[i].columns[1])
            ax[i].grid(alpha=0.5,linestyle='--')
            ax[i].set_xlim([self.df[i].iloc[:,0].min(axis=0),self.df[i].iloc[:,0].max(axis=0)])
            ax[i].legend()
        
        try: 
            plt.savefig(figure_path)
        except:
            logging.error('Unable save figure to path: ' + figure_path)
        plt.close()

        return fig
    
    def plotFromFigure(self, ax, old_fig, label, x_lim=[], y_lim=[]):
        x_min_max = x_lim
        y_min_max = y_lim

        # Check if is instance of np.ndarray
        if not isinstance(ax, np.ndarray):
            ax = [ax]
        
        for i in range(len(ax)):        
            for k in range(1, self.df[i].shape[1]-1):
                ax[i].plot(self.df[i].iloc[:,0], self.df[i].iloc[:,k],linewidth=1, label = label)
            ax[i].grid(alpha=0.5,linestyle='--')
            ax[i].set_xlabel(old_fig.get_axes()[i].get_xlabel())
            ax[i].set_ylabel(old_fig.get_axes()[i].get_ylabel())    

            if x_min_max:                
                x_candidate = self._getMinMax(old_fig.get_axes()[i].lines[0].get_xdata())
                y_candidate = self._getMinMax(old_fig.get_axes()[i].lines[0].get_ydata())
                x_min_max = self._updateMinMax(x_min_max,x_candidate)
                y_min_max = self._updateMinMax(y_min_max,y_candidate)
        
            else:    
                x_min_max = self._getMinMax(old_fig.get_axes()[i].lines[0].get_xdata())
                y_min_max = self._getMinMax(old_fig.get_axes()[i].lines[0].get_ydata())

        return ax, x_min_max, y_min_max
    
    def getSingleMeasurement(self, xnew, dim=0):
        """ Interpolate data to get measurement in a specific length.
        Args:
            df - dataframe
        Returns:
            ynew - numpy array - interpolated measurement
        """
        try:
            df = self.df[dim]
        except Exception as e:
            logging.error('Failed to obtain DataFrame: ' + str(e))
            return
            
        x = df.iloc[:,0].to_numpy()
        y = df.iloc[:,1].to_numpy()
        f = interpolate.interp1d(x, y)
        ynew = f(xnew)
        return ynew

    def getMeanMeasurement(self, minlim, maxlim, dim=0):
        """ Calculate the mean over an interval.
        Args:
            df - dataframe
        Returns:
            ymean - numpy array - mean measurement
        """
        try:
            df = self.df[dim]
        except Exception as e:
            logging.error('Failed to obtain DataFrame: ' + str(e))
            return

        x = df.iloc[:,0].to_numpy()
        y = df.iloc[:,1].to_numpy()
        idx_min = (np.abs(x - minlim)).argmin()
        idx_max = (np.abs(x - maxlim)).argmin()
        ymean = np.mean(y[idx_min:idx_max])
        return ymean

    def _getMinMax(self, x):
        """ Calculate the mean over an interval.
        Args:
            x - list
        Returns:
            x_min_max - list
        """
        x_min_max = []
        x_min_max.append(min(x))
        x_min_max.append(max(x))
        return x_min_max

    def _updateMinMax(self, x,x_candidate):
        """ Calculate the mean over an interval.
        Args:
            x - list 
        Returns:
            x_candidate - list
        """
        if x_candidate[0] < x[0]:
            x[0] = x_candidate[0]
        if x_candidate[1] > x[1]:
            x[1] = x_candidate[0]
        return x    
    
def getFolders(dir_name):
# Search for all folders in dir
    try:
        folders_list = [f for f in os.listdir(dir_name) if os.path.isdir(os.path.join(dir_name, f))]
    except Exception as err:
        logging.error(f"Unexpected {err=}1, {type(err)=}")
        return 
    
    if folders_list:
        folders_path = ["".join((dir_name, folder)) if (dir_name[-1]=='/') else "/".join((dir_name, folder))
                        for folder in folders_list]
        return folders_path
    else:
        return [dir_name]

def getFiles(file_dir, is_numeric=False, file_order=None):        
    # Search for all txt files in dir
    try:
        txt_file_list = [f for f in os.listdir(file_dir) if os.path.isfile(os.path.join(file_dir, f)) and f.endswith(".txt")]
    except Exception as err:
        logging.error(f"Unexpected2 {err=}2, {type(err)=}")
        return 

    if is_numeric:
        # Remove files whose names do not begin with a number
        txt_file_list = [f for f in txt_file_list if f[0].isnumeric()]    

    # Remove sufix and sort by name
    file_prefix_list = list(set([f.split('_')[0] for f in txt_file_list]))
    
    if file_order is not None:
        file_prefix_list = _sortFiles(file_prefix_list, file_order)
    else:    
        file_prefix_list.sort()

    return file_prefix_list

def _sortFiles(file_list, file_order):
    order = list()
    
    for i, file_name in enumerate(file_order):
        if file_name in file_list:
            order.append(file_list.index(file_order[i]))

    new_file_list = [file_list[i] for i in order]
    return new_file_list