import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import logging
from src.data_reader import *

# Main path 
dir_name = "data/i29/strain/resolution_test"

# Get all folders in path
dir_list =  getFolders(dir_name)

# OBR file sufix
file_sufix_list = ["Upper","Lower"]

# Create new plot
fig, ax = plt.subplots(len(file_sufix_list),figsize=(8,7), num=1)

# Read all files in each folder
for dir in dir_list:
    file_prefix_list = getFiles(dir)

    if file_prefix_list:
        for i,file_name in enumerate(file_prefix_list):
            # Instantiate DataReader
            dfreader = LUNAOBRDataReader(dir, file_name, file_sufix_list)
            # Set figure path 
            fig_dir = 'figures/'+'/'.join(dir.split('/')[1:])
            # Set figure label
            label = dir.split('/')[-1]
            # Read data and save figure the results in figure path 
            figure = dfreader.readData(save_figure=True,figure_dir=fig_dir)
            # Add each curve to plot
            ax, x_lim, y_lim = dfreader.plotFromFigure(ax, figure, label)

# Add legend and save figure
plt.legend(loc='upper left', fontsize='8')
ax[1].set_xlim([1.315,1.345])
plt.savefig("figures/i29/strain/resolution_test.png")
plt.show()