from os import path
import pandas as pd
import argparse
import glob
from astropy.table import Table, Column
import matplotlib.pyplot as plt
from matplotlib.dates import (MONTHLY, DateFormatter,
                              rrulewrapper, RRuleLocator, drange)
from datetime import datetime

def plot_readthedocs_traffic(args):

    # Load traffic analysis data downloaded as CSV files from ReadTheDocs
    traffic_data = load_RTD_traffic_data(args)

    # Sum the traffic data by date; the CSV files have multiple entries
    # for each data, relating to the number of views per page of the documentation.
    # Since we want to plot the total number of views per day, we need to sum
    # over each date
    traffic_stats = sum_over_dates(traffic_data)
    print(traffic_stats)

    # Plot the traffic statistics as a function of time
    plot_stats_with_time(args, traffic_stats)

def plot_stats_with_time(args, traffic_stats):
    """
    Function to produce a plot of the traffic statistics as a function of time
    :param args:
    :param traffic_stats:
    :return:
    """

    # Plot formatting
    formatter = DateFormatter('%Y-%m-%d')
    rule = rrulewrapper(MONTHLY, interval=1)
    loc = RRuleLocator(rule)

    fig, ax = plt.subplots()
    plt.plot_date(traffic_stats['Date'], traffic_stats['Views'], marker='.', linestyle='-')
    ax.xaxis.set_major_locator(loc)
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_tick_params(rotation=30, labelsize=10)
    plt.grid()
    plt.title('TOM Toolkit ReadTheDocs visitors per day')
    plt.xlabel('Date')
    plt.ylabel('N total visits')

    plt.savefig(
        path.join(args.data_dir, 'tomtoolkit_RTD_visits_per_day.png'),
        bbox_inches='tight'
    )

def sum_over_dates(traffic_data):
    """
    Function to sum the traffic data by date; the CSV files have multiple entries
    for each data, relating to the number of views per page of the documentation.
    Since we want to plot the total number of views per day, we need to sum
    over each date

    :param traffic_data:
    :return:
    """

    dates = []
    total_views = []
    for i,date in enumerate(traffic_data['Date']):
        idx = traffic_data['Date'] == date
        clean_date = pd.to_datetime(date, format='%Y-%m-%d %H:%M:%S')
        dates.append(clean_date)
        total_views.append(traffic_data['Views'][idx].sum())

    traffic_stats = Table([
        Column(name='Date', data=dates),
        Column(name='Views', data=total_views)
    ])
    return traffic_stats

def load_RTD_traffic_data(args):
    """
    Function to load traffic analysis data from ReadTheDocs in CSV
    format files into a Pandas dataframe
    """

    # ReadTheDocs allows users to download segments of ~3 months worth
    # of traffic analysis at a time, so the input data comes in the form
    # of a set of files whose data should be concatenated
    file_list = glob.glob(path.join(args.data_dir, args.file_rootname + '*.csv'))

    for i,f in enumerate(file_list):
        if i == 0:
            df = pd.read_csv(f)
            print('Read ' + path.basename(f) + ' with ' + str(len(df)) + ' entries')
        else:
            new_data = pd.read_csv(f)
            df = pd.concat([df, new_data])
            print('Read concat ' + path.basename(f) + ' with ' + str(len(new_data)) + ' entries')

    traffic_data = Table.from_pandas(df.sort_values('Date'))

    return traffic_data

def get_args():

    parser = argparse.ArgumentParser()
    parser.add_argument('data_dir', help='Path to input data directory')
    parser.add_argument('file_rootname', help='Rootname of the CSV input files')
    args = parser.parse_args()

    return args


if __name__ == '__main__':
    args = get_args()
    plot_readthedocs_traffic(args)