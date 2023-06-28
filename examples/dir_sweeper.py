import pandas as pd
import matplotlib.pyplot as plt
from src.data_reader import *

# Main path 
dir_name = "data/i29/strain/resolution_test"

# Get all folders in path
dir_list =  getFolders(dir_name)

# OBR file sufix
file_sufix_list = ["Upper","Lower"]

# Read all files in each folder
for dir in dir_list:
    file_prefix_list = getFiles(dir)

    if file_prefix_list:
        for i,file_name in enumerate(file_prefix_list):
            # Instantiate DataReader
            dfreader = LUNAOBRDataReader(dir, file_name, file_sufix_list)
            # Set figure path            
            fig_dir = 'figures/'+'/'.join(dir.split('/')[1:])
            # Read data and save figure the results in figure path            
            _ = dfreader.readData(save_figure=True,figure_dir=fig_dir)
