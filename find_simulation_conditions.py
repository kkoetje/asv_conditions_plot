# import sys
# import tqdm
## sys.path.append('/home/slug/repos')
from getdatatestbed import getDataFRF
# from testbedutils import sblib as sb
import datetime as dt
import numpy as np
# import pandas as pd
from matplotlib import pyplot as plt
# import netCDF4 as nc
# import glob
# import os

###############

ofname = 'yf_wave_conditions.png'
yf_date_file_name = 'all_yellowfin_dates.txt'
jb_date_file_name = 'all_jaiabot_dates.txt' # update this

###############
#load .txt file with list of dates, located in the same directory as this py file
with open(yf_date_file_name, 'r') as file:
    yf_dates_list = file.read().splitlines()
# # Print list of dates
# print(yf_dates_list)
with open(jb_date_file_name, 'r') as file:
    jb_dates_list = file.read().splitlines()

# Combine all dates
all_dates = yf_dates_list + jb_dates_list

# Sort the combined list chronologically
sorted_dates = sorted(all_dates, key=lambda x: dt.datetime.strptime(x, '%Y%m%d'))


start = dt.datetime.strptime(sorted_dates[0], '%Y%m%d')
end = dt.datetime.strptime(sorted_dates[-1], '%Y%m%d') + dt.timedelta(days=1)

# Convert list of strings to datetime
yf_dates = np.array([dt.datetime.strptime(date, '%Y%m%d') for date in yf_dates_list])

hs_window, tp_window = 0.5, 1  # window to search +/- for conditions in

#crawler_failure_time = dt.datetime(2021, 12, 14,20,00)
# y_frf_lower = 450
# y_frf_upper = 490
# bathy_url = "https://chldata.erdc.dren.mil/thredds/dodsC/frf/geomorphology/elevationTransects/survey/data/FRF_geomorphology_elevationTransects_survey_20211217.nc"

############## function Defs
def bin_data(data_to_be_binned,  bin_size=0.1):
    bins = np.arange(all_waves['Hs'].min(), np.ceil(all_waves['Hs'].max()), bin_size)
    return np.digitize(data_to_be_binned, bins=bins, right=False), bins

#def conditions_operated_plot(ofname, all_waves, hs_in_water, tp_in_water, bins, tp_mean, tp_std, color):
def conditions_operated_plot(ofname, all_waves, hs_in_water, tp_in_water, bins, tp_mean, tp_std):  #removed 'color' input arg

    # make plot of conditions we have YF data from
    plt.figure(figsize=(10,6))
    plt.suptitle('Yellowfin Survey Conditions',fontweight='bold')
    ax1 = plt.subplot2grid((3,2), (0,0), colspan=2)
    ax1.plot(all_waves['time'], all_waves['Hs'])
    ax1.set_ylabel('Wave Height [m]')
    ax1.set_xlabel('Date')
    for i in yf_dates:
        ax1.axvline(i, color='k', linestyle="--", linewidth=1)
    ax2 = plt.subplot2grid((3,2), (1,0), colspan=2, rowspan=2)
    ax2.set_title('Wave Conditions During Collections')
    ax2.scatter(hs_in_water, tp_in_water, c='yellow', s=50, label='Collected Conditions')
    # below was removed because it made a false assumption that wave heights were gaussian distributed.
    ax2.fill_between(bins, y1=tp_mean+tp_std, y2=tp_mean - tp_std, alpha=0.25, color='black', label='67%')
    ax2.fill_between(bins, y1=tp_mean+2*tp_std, y2=tp_mean - 2*tp_std, alpha=0.25, color='black', label="95%")
    # ax2.plot(waves['Hs'][idx_failure], 1/waves['peakf'][idx_failure], marker='X', color='c',
    #          markersize=20, markeredgecolor='k', label='Crawler Failure')
    ax2.set_xlabel('Wave Height [m]')
    ax2.set_ylabel('Wave Period [s]')
    ax2.legend(loc='upper right')
    # cbar = plt.colorbar(depth, ax=ax2)
    # cbar.set_label('elevation [m] NAVD88')
    plt.tight_layout(rect=[0.02, 0.02, 0.99, 0.98])
    # plt.subplots_adjust
    plt.xlim([0.25, 2])
    plt.savefig(ofname)

###########################

gd = getDataFRF.getObs(start, end)
all_waves = gd.getWaveData('waverider-17m', spec=False)
# Convert to datetime.datetime
all_wave_dates = np.array([dt.datetime(date.year, date.month, date.day, date.hour, date.minute) for date in all_waves['time']])


# now bin wave heights to find distributions of wave periods in each
idx_bins, bins = bin_data(all_waves['Hs'], bin_size=0.25)
tp_std, tp_mean = [], []
for ii in range(len(bins)):
    tp_std.append(np.std(1/all_waves['peakf'][idx_bins==ii]))
    tp_mean.append(np.mean(1/all_waves['peakf'][idx_bins==ii]) )
tp_mean, tp_std = np.array(tp_mean), np.array(tp_std)


# now find min/max waves per collection day
hs_in_water, tp_in_water, time_in_water = [], [], []
for d in range (0, len(yf_dates)):
    yf_in_water_time = yf_dates[d]

    # now convert to pydates to compare to all_waves
    min_yf_water = yf_in_water_time+dt.timedelta(hours=13) # assume YF is collected in UTC and that surveys are done between 8 and 11 am; add 4 hours for Edt and 5 hours of EST; Let's use 1300 UTC for simplicity (equal to 8am/9am EST/EDT)

    if yf_dates[d] == '20240930':
        max_yf_water = yf_in_water_time + dt.timedelta(hours=3)
    else:
        max_yf_water = yf_in_water_time+dt.timedelta(hours=6)

    yf_in_water_time_pydate = [min_yf_water + dt.timedelta(hours=i) for i in range(3)]

    # mask of what is together
    mask_waves_in_water = np.isin(all_wave_dates, yf_in_water_time_pydate)
    hs_in_water.extend(all_waves['Hs'][mask_waves_in_water])
    tp_in_water.extend(1/all_waves['peakf'][mask_waves_in_water])
    time_in_water.extend(all_waves['time'][mask_waves_in_water])



# plot wave conditions operated in and print figure to png

conditions_operated_plot(ofname, all_waves, hs_in_water, tp_in_water, bins, tp_mean, tp_std)


