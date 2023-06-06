import pandas as pd
import matplotlib.pyplot as plt
from data_reader import readData
from os import listdir
from os.path import isfile, join
from scipy import interpolate
import numpy as np

def getSingleMeasurement(df, xnew):
    """ Interpolate data to get measurement in a specific length.
    Args:
        df - dataframe
    Returns:
        ynew - numpy array - interpolated measurement
    """
    x = df.iloc[:,0].to_numpy()
    y = df.iloc[:,1].to_numpy()
    f = interpolate.interp1d(x, y)
    ynew = f(xnew)
    return ynew

def getMeanMeasurement(df, minlim, maxlim):
    """ Calculate the mean over an interval.
    Args:
        df - dataframe
    Returns:
        ymean - numpy array - mean measurement
    """
    x = df.iloc[:,0].to_numpy()
    y = df.iloc[:,1].to_numpy()
    idx_min = (np.abs(x - minlim)).argmin()
    idx_max = (np.abs(x - maxlim)).argmin()
    ymean = np.mean(y[idx_min:idx_max])
    return ymean

# Path 
file_dir = "../data/02_06_23/"
figure_path = "../figures/spectral_shift_versus_strain.png"

# Search for all txt files in dir
txt_file_list = [f for f in listdir(file_dir) if isfile(join(file_dir, f)) and f.endswith(".txt")]
# Remove sufix and sort by name
file_prefix_list = list(set([f.split('_')[0] for f in txt_file_list]))
file_prefix_list.sort()

# File sufix
file_sufix_list = ["Upper","Lower"]

# Strain parameters
name_separator = "me"
strain = [float(f.split(name_separator)[0]) for f in file_prefix_list]
strain = pd.Series(strain)/19e-2
s_shift_single = list()
s_shift_mean = list()


for i,file_name in enumerate(file_prefix_list):
    df = readData(file_dir,file_name,file_sufix_list,save_figure =True)
    
    # Change here for different functionalities
    # Here, data from "_Lower.txt" is processed at each iteration. 
    # A single measurement is extracted from data
    meas_single = getSingleMeasurement(df[1],2.30).item(0)
    s_shift_single.append(meas_single)
    
    # The mean calculated over an interval
    meas_mean = getMeanMeasurement(df[1],2.22,2.35).item(0)
    s_shift_mean.append(meas_mean) 

# Plot Figure
plt.plot(strain, s_shift_single,'-o',strain,s_shift_mean,'-s')
plt.xlabel(r'Microstrain [$\mu \epsilon$]')
plt.ylabel(df[1].columns[1])
plt.grid(alpha=0.5,linestyle='--')
plt.savefig(figure_path)
plt.show()

