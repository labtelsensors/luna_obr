#python -m examples.obr_sweeping_strain_sensing
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import logging
from src.data_reader import *

def sweepPath(file_dir, file_order=None):
    txt_file_list = [f for f in os.listdir(file_dir) if os.path.isfile(os.path.join(file_dir, f)) and f.endswith(".txt")]
    txt_file_list = list(set([f.split('.txt')[0] for f in txt_file_list]))
    if file_order is not None:
        txt_file_list = sortFiles(txt_file_list, file_order) 
    return txt_file_list

def isInsideInterval(x, lim):
    if (lim[0] >= x[0]) & (lim[1] <= x[1]):
        return True
    else:
        return False

def getMean(df, minlim, maxlim, dim=0):
    """ Calculate the mean over an interval.
    Args:
        df - dataframe
    Returns:
        ymean - numpy array - mean measurement
    """
    df = df.iloc[:,dim*2:dim*2+2].dropna(axis=0)
    x = df.iloc[:,0].to_numpy()
    y = df.iloc[:,1].to_numpy()
    idx_min = (np.abs(x[0:25] - minlim)).argmin()
    idx_max = (np.abs(x - maxlim)).argmin()
    ymean = np.mean(y[idx_min:idx_max])
    return ymean
    
# Main path 
dir_name = "data/smf/strain"

# Get all folders in path
dir_list =  getFolders(dir_name)

# OBR file sufix
file_sufix_list = []

# Measurement data
strain = [0,5,10,15,20,25,30,35,40,45,50,55,60]
order = ['0_Lower','5_Lower','10_Lower','15_Lower','20_Lower','25_Lower','30_Lower','35_Lower','40_Lower','45_Lower','50_Lower','55_Lower','60_Lower']
mean_lim = [[2.35,2.45]]
strain_shift = np.zeros((len(mean_lim), len(strain)))

# Create new plot
fig, ax = plt.subplots(3,figsize=(8,7), num=1)

# Read all files in each folder
for dir in dir_list:
    file_prefix_list = sweepPath(dir,file_order=order)

    if file_prefix_list:
        for i,file_name in enumerate(file_prefix_list):
            print(file_name)
            # Instantiate DataReader
            dfreader = LUNAOBRDataReader(dir, file_name, file_sufix_list, is_obr_file = False)
            # Set figure path 
            fig_dir = 'figures/'+'/'.join(dir.split('/')[1:])
            # Set figure label
            label = file_name
            print(label)
            # Read data and save figure the results in figure path 
            figure = dfreader.readData(save_figure=True,figure_dir=fig_dir,skip_rows=11)
            # Add each curve to plot
            ax, x_lim, y_lim = dfreader.plotFromFigure(ax, figure, label)
            # Get dataframe
            df = dfreader.getDataFrame()
            
            # Get a point in curve using interpolation
            inside_lim = [isInsideInterval(x_lim[2], lim) for lim in mean_lim]
            if any(inside_lim):
                n = np.where(inside_lim)[0].item(0)
                meas_mean = getMean(df[0], mean_lim[n][0],mean_lim[n][1], 2).item(0)
                strain_shift[n][i] = meas_mean
    
# Add legend and save figure
plt.legend(loc='upper left', fontsize='8')
#plt.savefig("figures/cao/distributed_strain/multiplot.png")
plt.show()

# Plot strain sensitivity
labels = ['1st Loop','2nd Loop']
fig, ax = plt.subplots(1,figsize=(8,7))
for i in range(len(mean_lim)):
    y_data = strain_shift[i][:]
    x_data = strain   
    ax.plot(x_data, y_data, label = labels[i], marker='o', linewidth=1)            
    ax.set_xlabel(r'Microstrain [$\mu \epsilon$]')
    ax.set_ylabel('Spectral Shift (GHz)')
    #ax.grid(alpha=0.5,linestyle='--')

ax.grid(alpha=0.5,linestyle='--')
#plt.savefig("figures/cao/distributed_strain/strain_sensitivity.png")
plt.legend(loc='upper right', fontsize='8')
plt.show()

file_path = os.path.join(dir_name,'characterization.txt')
save2pd = np.array(strain).reshape((-1,1))
label = ['Microstrain']
for i in range(len(mean_lim)):
    x = np.array(strain_shift[i][:]).reshape((-1,1))
    save2pd = np.concatenate((save2pd, x), axis=1)
    label.append('Spectral Shift (GHz)')

df = pd.DataFrame(save2pd,columns=label)
df.to_csv(file_path,sep='\t',index=False)