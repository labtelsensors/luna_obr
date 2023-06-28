import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import logging
from src.data_reader import *

# Main path 
dir_name = "data/i29/temp/2m"

# Get all folders in path
dir_list =  getFolders(dir_name)

# OBR file sufix
file_sufix_list = ["Upper","Lower"]

# Measurement data
strain_shift = list()
strain = [30,40,60,50,40,30]
order = ['30','40','60','50d','40d','30d']

# Create new plot
fig, ax = plt.subplots(len(file_sufix_list),figsize=(8,7), num=1)

# Read all files in each folder
for dir in dir_list:
    file_prefix_list = getFiles(dir, is_numeric=True, file_order=order)

    if file_prefix_list:
        for i,file_name in enumerate(file_prefix_list):
            # Instantiate DataReader
            dfreader = LUNAOBRDataReader(dir, file_name, file_sufix_list)
            # Set figure path 
            fig_dir = 'figures/'+'/'.join(dir.split('/')[1:])
            # Set figure label
            label = str(strain[i]) + '$^\circ$C'
            # Read data and save figure the results in figure path 
            figure = dfreader.readData(save_figure=True,figure_dir=fig_dir)
            # Get a point in curve using interpolation
            meas_single = dfreader.getSingleMeasurement(3.0, 1).item(0)
            strain_shift.append(meas_single)
            # To calculate the mean over an interval use dfreader.getMeanMeasurement() instead
            # Add each curve to plot
            ax, x_lim, y_lim = dfreader.plotFromFigure(ax, figure, label)

# Add legend and save figure
plt.legend(loc='upper left', fontsize='8')
plt.savefig("figures/i29/temp/2m/temp_test.png")

# Plot Figure
sf = plt.figure(2)
plt.plot(strain, strain_shift,'-o', label='Single Point') 
plt.xlabel(r'Temperature [$^\circ$C]')
plt.ylabel(dfreader.getColumns(1)[1])
plt.grid(alpha=0.5,linestyle='--')
plt.legend()
plt.savefig("figures/i29/temp/2m/temp_sensitivity.png")
plt.show()