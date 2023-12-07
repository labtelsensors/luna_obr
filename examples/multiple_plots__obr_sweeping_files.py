#python -m examples.multiple_plots__obr_sweeping_files
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import logging
from src.data_reader import *

def sweepPath(file_dir):
    txt_file_list = [f for f in os.listdir(file_dir) if os.path.isfile(os.path.join(file_dir, f)) and f.endswith(".txt")]
    txt_file_list = list(set([f.split('.txt')[0] for f in txt_file_list]))
    return txt_file_list

# Main path 
dir_name = "data/i29/strain/distributed_strain"

# Get all folders in path
dir_list =  getFolders(dir_name)

# OBR file sufix
file_sufix_list = []

# Create new plot
fig, ax = plt.subplots(3,figsize=(8,7), num=1)

# Read all files in each folder
for dir in dir_list:
    file_prefix_list = sweepPath(dir)

    if file_prefix_list:
        for i,file_name in enumerate(file_prefix_list):
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
    
# Add legend and save figure
plt.legend(loc='upper left', fontsize='8')
#plt.savefig("figures/i29/strain/resolution_test.png")
plt.show()

