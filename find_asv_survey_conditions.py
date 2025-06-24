from getdatatestbed import getDataFRF
import datetime as dt
import numpy as np
from matplotlib import pyplot as plt

############### USER INPUTS ###############

ofname = 'all_yf_wave_conditions.png'  # name of figure to be printed
yf_date_file_name = 'all_yellowfin_dates.txt'  # Comment this line out if you don't want to include these dates
#jb_date_file_name = 'all_jaiabot_dates.txt'  # Comment this line out if you don't want to include these dates
sampling_hours = 1  # number of hours for each survey, assuming start time below (one datapoint will be plotted for each hour)
start_hour = 13  # assumed start hour in UTC (ie 1300 UTC)

###########################################
# load .txt file with list of dates, located in the same directory as this py file
# Only include dates from files that are given by the user above
yf_dates_list, jb_dates_list = [], []

if 'yf_date_file_name' in locals() and yf_date_file_name:
    with open(yf_date_file_name, 'r') as file:
        yf_dates_list = file.read().splitlines()

if 'jb_date_file_name' in locals() and jb_date_file_name:
    with open(jb_date_file_name, 'r') as file:
        jb_dates_list = file.read().splitlines()

# Combine all dates
all_dates = yf_dates_list + jb_dates_list

# Sort the combined list chronologically
sorted_dates = sorted(all_dates, key=lambda x: dt.datetime.strptime(x, '%Y%m%d'))

start = dt.datetime.strptime(sorted_dates[0], '%Y%m%d')
end = dt.datetime.strptime(sorted_dates[-1], '%Y%m%d') + dt.timedelta(days=1)

hs_window, tp_window = 0.5, 1  # window to search +/- for conditions in


############## function definitions

def bin_data(data_to_be_binned, bin_size=0.1):
    bins = np.arange(all_waves['Hs'].min(), np.ceil(all_waves['Hs'].max()), bin_size)
    return np.digitize(data_to_be_binned, bins=bins, right=False), bins


def conditions_operated_plot(ofname, all_waves, bins, tp_mean, tp_std,
                             yf_dates_list=None, jb_dates_list=None, sorted_dates=None,
                             sampling_hours=2, start_hour=13):
    plt.figure(figsize=(10, 6))
    plt.suptitle('Survey Conditions', fontweight='bold')

    # Panel 1: Vertical lines for survey dates
    ax1 = plt.subplot2grid((3, 2), (0, 0), colspan=2)
    ax1.set_title('FRF - 17m Waverider Wave Height')
    ax1.plot(all_waves['time'], all_waves['Hs'], label='Wave Height')
    ax1.set_ylabel('Wave Height [m]')
    ax1.set_xlabel('Date')
    # Panel 1: Vertical lines for survey dates
    ax1 = plt.subplot2grid((3, 2), (0, 0), colspan=2)
    ax1.set_title('FRF - 17m Waverider Wave Height')
    ax1.plot(all_waves['time'], all_waves['Hs'], label='Wave Height', color='#4d4d4d')
    ax1.set_ylabel('Wave Height [m]')
    ax1.set_xlabel('Date')

    if yf_dates_list:
        for d in yf_dates_list:
            ax1.axvline(dt.datetime.strptime(d, '%Y%m%d'), color='#ff7f0e', linestyle='--', linewidth=1,
                        label='Yellowfin')  #color='#FFDB58'

    if jb_dates_list:
        for d in jb_dates_list:
            ax1.axvline(dt.datetime.strptime(d, '%Y%m%d'), color='#1f77b4', linestyle='--', linewidth=1, label='JaiaBot')

    # Panel 2: Wave conditions during surveys
    ax2 = plt.subplot2grid((3, 2), (1, 0), colspan=2, rowspan=2)
    ax2.set_title('Wave Conditions During Collections')
    ax2.fill_between(bins, tp_mean + tp_std, tp_mean - tp_std, alpha=0.25, color='black', label='67%')
    ax2.fill_between(bins, tp_mean + 2 * tp_std, tp_mean - 2 * tp_std, alpha=0.25, color='black', label='95%')

    if yf_dates_list:
        yf_dates = [dt.datetime.strptime(date, '%Y%m%d') for date in yf_dates_list]
        yf_hs, yf_tp = [], []
        for d in yf_dates:
            min_yf = d + dt.timedelta(hours=start_hour)
            yf_times = [min_yf + dt.timedelta(hours=i) for i in range(sampling_hours)]
            mask = np.isin(all_wave_dates, yf_times)
            yf_hs.extend(all_waves['Hs'][mask])
            yf_tp.extend(1 / all_waves['peakf'][mask])
        ax2.scatter(yf_hs, yf_tp, marker='D', c='#ff7f0e', s=50, edgecolor='k', label='Yellowfin')  #c='#FFDB58'

    if jb_dates_list:
        jb_dates = [dt.datetime.strptime(date, '%Y%m%d') for date in jb_dates_list]
        jb_hs, jb_tp = [], []
        for d in jb_dates:
            jb_min = d + dt.timedelta(hours=start_hour)
            jb_times = [jb_min + dt.timedelta(hours=i) for i in range(sampling_hours)]
            mask = np.isin(all_wave_dates, jb_times)
            jb_hs.extend(all_waves['Hs'][mask])
            jb_tp.extend(1 / all_waves['peakf'][mask])
        ax2.scatter(jb_hs, jb_tp, marker='o', c='#1f77b4', s=50, edgecolor='k', label='JaiaBot')

    ax2.set_xlabel('Wave Height [m]')
    ax2.set_ylabel('Wave Period [s]')
    ax2.set_xlim([0.25, 2])
    ax2.legend(loc='upper right')
    plt.tight_layout(rect=[0.02, 0.02, 0.99, 0.98])
    plt.savefig(ofname)


###########################


# get wave data and store in array
gd = getDataFRF.getObs(start, end)
all_waves = gd.getWaveData('waverider-17m', spec=False)
# Convert to datetime.datetime
all_wave_dates = np.array(
    [dt.datetime(date.year, date.month, date.day, date.hour, date.minute) for date in all_waves['time']])

# now bin wave heights to find distributions of wave periods in each
idx_bins, bins = bin_data(all_waves['Hs'], bin_size=0.25)
tp_std, tp_mean = [], []
for ii in range(len(bins)):
    tp_std.append(np.std(1 / all_waves['peakf'][idx_bins == ii]))
    tp_mean.append(np.mean(1 / all_waves['peakf'][idx_bins == ii]))
tp_mean, tp_std = np.array(tp_mean), np.array(tp_std)

# plot wave conditions operated in and print figure to png
conditions_operated_plot(ofname, all_waves, bins, tp_mean, tp_std, yf_dates_list=yf_dates_list,
                         jb_dates_list=jb_dates_list, sorted_dates=sorted_dates, sampling_hours=sampling_hours,
                         start_hour=start_hour)

print('Done!')
