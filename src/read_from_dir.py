import pandas as pd
import matplotlib.pyplot as plt
from data_reader import DataFrameReader
from os import listdir
from os.path import isfile, join
from scipy import interpolate
import numpy as np
import logging

# Path 
file_dir = "../data/smf/strain/"
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
    dfreader = DataFrameReader(file_dir, file_name, file_sufix_list)
    figure = dfreader.readData(save_figure =True)
    label = f'{strain[i]:.2f} $\mu \epsilon$'
    
    # Change here for different functionalities
    # Here, data from "_Lower.txt" is processed at each iteration. 
    # A single measurement is extracted from data
    meas_single = dfreader.getSingleMeasurement(2.30, 1).item(0)
    s_shift_single.append(meas_single)
    
    # The mean calculated over an interval
    meas_mean = dfreader.getMeanMeasurement(2.22,2.35, 1).item(0)
    s_shift_mean.append(meas_mean) 

    # Create plot with all curves
    if i == 0: 
        fig, ax = plt.subplots(len(figure.axes),figsize=(8,7), num=1)
    ax, x_lim, y_lim = dfreader.plotFromFigure(ax, figure, label)

plt.legend(loc='upper right', fontsize='6.5')
plt.savefig("../figures/obr_strain.png")
fig.show()

# Plot Figure
sf = plt.figure(2)
plt.plot(strain, s_shift_single,'-o', label='Single Point') 
plt.plot(strain,s_shift_mean,'-s', label = 'Mean')
plt.xlabel(r'Microstrain [$\mu \epsilon$]')
plt.ylabel(dfreader.getColumns(1)[1])
plt.grid(alpha=0.5,linestyle='--')
plt.legend()
plt.savefig(figure_path)
sf.show()

# Temperature
file_dir = "../data/smf/temperature1/"
figure_path = "../figures/spectral_shift_versus_temperature.png"

# Search for all txt files in dir
txt_file_list = [f for f in listdir(file_dir) if isfile(join(file_dir, f)) and f.endswith(".txt")]
# Remove files whose name does not begin with a number
txt_file_list = [f for f in txt_file_list if f[0].isnumeric()]

# Remove sufix and sort by name
file_prefix_list = list(set([f.split('_')[0] for f in txt_file_list]))
file_prefix_list.sort()

# Temperature parameters
temperature = [*range(30,80,10)]+([*range(30,80,10)])
temperature = pd.Series(temperature,dtype='float64')
t_shift_single = list()

for i,file_name in enumerate(file_prefix_list):
    dfreader = DataFrameReader(file_dir, file_name, file_sufix_list)
    figure = dfreader.readData(save_figure = True, figure_dir='../figures/temperature/')
    label = '%d $^\circ$C' % temperature[i]
    
    # Change here for different functionalities
    # Here, data from "_Lower.txt" is processed at each iteration. 
    # A single measurement is extracted from data
    meas_single = dfreader.getSingleMeasurement(2.50, 1).item(0)
    t_shift_single.append(meas_single)

    # Create plot with all curves
    if i == 0: 
        fig, ax = plt.subplots(len(figure.axes),figsize=(8,7), num=3)
    ax, x_lim, y_lim = dfreader.plotFromFigure(ax, figure, label)

plt.legend(loc='upper right', fontsize='8')
plt.savefig("../figures/obr_temperature.png")
fig.show()

# Add the last measurement to list
t_shift_single.insert(len(t_shift_single), t_shift_single[4])

# Plot Figure
tf = plt.figure(4)
plt.plot(temperature[:5], t_shift_single[:5],'-o', label='Ascendant') 
plt.plot(temperature[5:], t_shift_single[5:],'-s', label='Descendant')
plt.xlabel(r'Temperature [$^\circ$C]')
plt.ylabel(dfreader.getColumns(1)[1])
plt.grid(alpha=0.5,linestyle='--')
plt.legend()
try: 
    plt.savefig(figure_path)
except:
    logging.error('Unable save figure to path: ' + figure_path)
tf.show()

# Read second temperature experiment
file_dir = "../data/smf/temperature2-peltier/"

# Search for all txt files in dir
txt_file_list = [f for f in listdir(file_dir) if isfile(join(file_dir, f)) and f.endswith(".txt")]
# Remove files whose name does not begin with a number
txt_file_list = [f for f in txt_file_list if f[0].isnumeric()]

# Remove sufix and sort by name
file_prefix_list = list(set([f.split('_')[0] for f in txt_file_list]))
file_prefix_list.sort()
temperature = [30,35,40,45,50,55,30,35,40,45,50]

for i,file_name in enumerate(file_prefix_list):
    dfreader = DataFrameReader(file_dir, file_name, file_sufix_list)
    figure = dfreader.readData(save_figure = True, figure_dir='../figures/temperature-peltier/')
    label = '%d $^\circ$C' % temperature[i]

    # Create plot with all curves
    if i == 0: 
        fig, ax = plt.subplots(len(figure.axes),figsize=(8,7), num=5)
    ax, x_lim, y_lim = dfreader.plotFromFigure(ax, figure, label)

plt.legend(loc='upper right', fontsize='8')
plt.savefig("../figures/obr_temperature_peltier.png")
fig.show()

input()
