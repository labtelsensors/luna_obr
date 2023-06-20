import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging
import linecache
from scipy import interpolate

class DataFrameReader:

    def __init__(self, file_dir, file_prefix, file_sufix_list):
        self.file_dir = file_dir
        self.file_prefix = file_prefix
        self.file_sufix_list = file_sufix_list

    def getDataFrame(self):
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
            logging.error('Unable to read file from path: ' + file_path)
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

    def readData(self, save_figure=True, figure_dir='../figures/'):
        """ Plot dataframe.
        Args:
            df - dataframe or list of dataframes
        Returns:
            fig - figure
        """

        # Create paths
        file_name_list = ["{}_{}.txt".format(self.file_prefix, file_sufix) for file_sufix in self.file_sufix_list]
        path_list = ["".join((self.file_dir,file_name)) for file_name in file_name_list]
        figure_path = "{}{}.png".format(figure_dir,self.file_prefix)
        
        # Read file
        self.df = [self.fileReader(path) for path in path_list]
        self.df = self._dropEmpty()

        if self.df and save_figure:
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
        not_empty = [i for i, df in enumerate(self.df) if df is not None]    
        if not_empty:
            df_clean = [self.df[i] for i in not_empty]
            return df_clean
        else:
            return False

    def plotFromDataFrame(self,figure_path):
        """ Save plot of dataframe.
        Args:
            df - dataframe or list of dataframes
        """    
        fig, ax = plt.subplots(len(self.df),figsize=(8,7))
        
        if len(self.df)>1:
            for i in range(len(ax)):
                ax[i].plot(self.df[i].iloc[:,0], self.df[i].iloc[:,1],linewidth=1)
                ax[i].set_xlabel(self.df[i].columns[0])
                ax[i].set_ylabel(self.df[i].columns[1])
                ax[i].grid(alpha=0.5,linestyle='--')
                ax[i].set_xlim([self.df[i].iloc[:,0].min(axis=0),self.df[i].iloc[:,0].max(axis=0)])
        else:
            ax.plot(self.df.iloc[:,0], self.df.iloc[:,1],linewidth=1)
            ax.set_xlabel(self.df.columns[0])
            ax.set_ylabel(self.df.columns[1])
            ax.grid(alpha=0.5,linestyle='--')
            ax.set_xlim([self.df.iloc[:,0].min(axis=0),self.df.iloc[:,0].max(axis=0)])

        try: 
            plt.savefig(figure_path)
        except:
            logging.error('Unable save figure to path: ' + figure_path)
        plt.close()

        return fig
    
    def plotFromFigure(self, ax, old_fig, label, x_lim=[], y_lim=[]):
        x_min_max = x_lim
        y_min_max = y_lim

        if len(ax) > 1:
            for i in range(len(ax)):        
                ax[i].plot(old_fig.get_axes()[i].lines[0].get_xdata(),old_fig.get_axes()[i].lines[0].get_ydata(), 
                        label=label)
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
        else:
                ax.plot(old_fig.get_axes().lines[0].get_xdata(),old_fig.get_axes().lines[0].get_ydata(), 
                        label=label)
                ax.grid(alpha=0.5,linestyle='--')
                ax.set_xlabel(old_fig.get_axes().get_xlabel())
                ax.set_ylabel(old_fig.get_axes().get_ylabel())

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