import pandas as pd
import matplotlib.pyplot as plt
import logging
import linecache

def fileReader(file_path):
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

def dropEmpty(df_list):
    """ Drop empty dataframes from list.
    Args:
        df_list - dataframe or list of dataframes
    Returns:
        df_clean - dataframe or list of dataframes
    """
    not_empty = [i for i, df in enumerate(df_list) if df is not None]    
    if not_empty:
        df_clean = [df_list[i] for i in not_empty]
        return df_clean
    else:
        return False

def plotData(df,figure_path):
    """ Save plot of dataframe.
    Args:
        df - dataframe or list of dataframes
    """    
    fig, ax = plt.subplots(len(df),figsize=(8,7))
    
    if len(df)>1:
        for i in range(len(ax)):
            ax[i].plot(df[i].iloc[:,0], df[i].iloc[:,1],linewidth=1)
            ax[i].set_xlabel(df[i].columns[0])
            ax[i].set_ylabel(df[i].columns[1])
            ax[i].grid(alpha=0.5,linestyle='--')
            ax[i].set_xlim([df[i].iloc[:,0].min(axis=0),df[i].iloc[:,0].max(axis=0)])
    else:
        ax.plot(df[0].iloc[:,0], df[0].iloc[:,1],linewidth=1)
        ax.set_xlabel(df[0].columns[0])
        ax.set_ylabel(df[0].columns[1])
        ax.grid(alpha=0.5,linestyle='--')
        ax.set_xlim([df[0].iloc[:,0].min(axis=0),df[0].iloc[:,0].max(axis=0)])

    try: 
        plt.savefig(figure_path)
    except:
        logging.error('Unable save figure to path: ' + figure_path)
    plt.close()

def readData(file_dir, file_prefix, file_sufix_list, save_figure=True, figure_dir='../figures/'):
    """ Plot dataframe.
    Args:
        df - dataframe or list of dataframes
    Returns:
        fig - figure
    """

    # Create paths
    file_name_list = ["{}_{}.txt".format(file_prefix,file_sufix) for file_sufix in file_sufix_list]
    path_list = ["".join((file_dir,file_name)) for file_name in file_name_list]
    figure_path = "{}{}.png".format(figure_dir,file_prefix)
    
    # Read file
    df = [fileReader(path) for path in path_list]
    df = dropEmpty(df)

    if df and save_figure:
        plotData(df,figure_path)    
        
    return df
